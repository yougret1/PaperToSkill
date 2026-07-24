from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_SUCCESSOR = ROOT / "format_conformance_successor_2026-07-23"
DEFAULT_RUN_DIR = ROOT / "remote_execution_v3_2026-07-23"
DEFAULT_MATERIALIZATION = ROOT / "materialization_remote_only_2026-07-23"
DEFAULT_OUTPUT_DIR = ROOT / "analysis_v1_2026-07-24"
PAYLOAD_SUBSCRIPT = re.compile(r"\bcase\s*\[\s*(['\"])payload\1\s*\]")
PAYLOAD_GET = re.compile(r"\bcase\s*\.\s*get\s*\(\s*(['\"])payload\1")


class InterfaceAnalysisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InterfaceAnalysisError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> Any:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_bytes(value) + b"\n")
    temporary.replace(path)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def classify_implementation(source: str | None) -> dict[str, bool]:
    source = source or ""
    subscript = PAYLOAD_SUBSCRIPT.search(source) is not None
    get_call = PAYLOAD_GET.search(source) is not None
    return {
        "case_payload_subscript": subscript,
        "case_payload_get": get_call,
        "case_payload_access": subscript or get_call,
    }


def normalized_payload_key_error(error: object) -> bool:
    if not isinstance(error, dict) or error.get("error_type") != "KeyError":
        return False
    message = str(error.get("message", "")).strip()
    return message in {"'payload'", '"payload"', "payload"}


def canonical_implementation(row: dict[str, Any], run_dir: Path) -> str | None:
    relative = row.get("canonical_output_path")
    if not relative:
        return None
    path = run_dir / str(relative)
    require(path.is_file(), f"missing canonical output: {relative}")
    try:
        document = load_json(path)
    except json.JSONDecodeError:
        return None
    if not isinstance(document, dict):
        return None
    implementation = document.get("implementation")
    return implementation if isinstance(implementation, str) else None


def group_summary(
    rows: list[dict[str, Any]], keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row.get(key) or "__none__") for key in keys)].append(row)
    output: list[dict[str, Any]] = []
    for values, members in sorted(groups.items()):
        output.append(
            {
                **dict(zip(keys, values)),
                "registered_rows": len(members),
                "scoring_rows": sum(row["scoring_available"] for row in members),
                "rows_with_any_worker_error": sum(
                    row["worker_error_cases"] > 0 for row in members
                ),
                "worker_error_cases": sum(row["worker_error_cases"] for row in members),
                "payload_key_error_rows": sum(
                    row["payload_key_error_cases"] > 0 for row in members
                ),
                "payload_key_error_cases": sum(
                    row["payload_key_error_cases"] for row in members
                ),
                "case_payload_access_rows": sum(
                    row["case_payload_access"] for row in members
                ),
                "operational_success_rows": sum(
                    row["terminal_outcome"] == "operational_success" for row in members
                ),
            }
        )
    return output


def audit_interface(materialization: Path) -> dict[str, Any]:
    tasks_dir = materialization / "tasks"
    task_dirs = sorted(path for path in tasks_dir.iterdir() if path.is_dir())
    require(len(task_dirs) == 24, "materialized task count changed")
    ambiguous_tasks: list[str] = []
    fixture_cases = 0
    payload_wrapped_cases = 0
    for task_dir in task_dirs:
        scaffold = (task_dir / "task_scaffold.md").read_text(encoding="utf-8")
        exposes_wrapper = "`payload` field" in scaffold or "inner payload" in scaffold
        if (
            "defining `solve(case)`" in scaffold
            and "public fixtures define input shapes" in scaffold
            and not exposes_wrapper
        ):
            ambiguous_tasks.append(task_dir.name)
        for registry in ("A", "B"):
            fixture = load_json(task_dir / "fixtures" / f"{registry}.json")
            for case in fixture["cases"]:
                fixture_cases += 1
                payload_wrapped_cases += (
                    isinstance(case, dict)
                    and "case_id" in case
                    and "payload" in case
                    and isinstance(case["payload"], dict)
                )

    worker_path = ROOT / "remote_execution_worker.py"
    worker_lines = worker_path.read_text(encoding="utf-8").splitlines()
    original_line = next(
        index
        for index, line in enumerate(worker_lines, start=1)
        if 'original = copy.deepcopy(item.get("payload"))' in line
    )
    solve_line = next(
        index
        for index, line in enumerate(worker_lines, start=1)
        if "output = solve(case)" in line
    )
    return {
        "materialized_tasks": len(task_dirs),
        "ambiguous_scaffold_tasks": len(ambiguous_tasks),
        "ambiguous_task_ids": ambiguous_tasks,
        "public_fixture_cases": fixture_cases,
        "outer_payload_wrapped_cases": payload_wrapped_cases,
        "worker_source_sha256": sha256_path(worker_path),
        "worker_extracts_inner_payload_line": original_line,
        "worker_calls_solve_with_inner_payload_line": solve_line,
        "worker_passes_inner_payload": True,
    }


def analyze(
    successor: Path, run_dir: Path, materialization: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    schedule_path = successor / "global_remote_schedule.json"
    schedule = load_json(schedule_path)["rows"]
    require(len(schedule) == 1296, "registered schedule row count changed")
    schedule_by_id = {str(row["execution_id"]): row for row in schedule}
    require(len(schedule_by_id) == 1296, "duplicate registered execution ID")

    result_files = {path.stem: path for path in (run_dir / "rows").glob("*.json")}
    require(set(result_files) == set(schedule_by_id), "terminal rows do not bind to schedule")
    scoring_files = {
        path.name.removesuffix(".json.gz"): path
        for path in (run_dir / "scoring").glob("*.json.gz")
    }
    require(set(scoring_files) <= set(schedule_by_id), "unknown scoring execution ID")

    row_records: list[dict[str, Any]] = []
    for schedule_row in schedule:
        execution_id = str(schedule_row["execution_id"])
        terminal = load_json(result_files[execution_id])
        require(terminal.get("execution_id") == execution_id, "terminal ID mismatch")
        scoring_path = scoring_files.get(execution_id)
        errors: list[object] = []
        if scoring_path is not None:
            scoring = load_gzip_json(scoring_path)
            require(scoring.get("execution_id") == execution_id, "scoring ID mismatch")
            raw_errors = scoring.get("errors", [])
            require(isinstance(raw_errors, list), "scoring errors are not a list")
            errors = raw_errors
        implementation = canonical_implementation(terminal, run_dir)
        patterns = classify_implementation(implementation)
        payload_errors = sum(normalized_payload_key_error(error) for error in errors)
        row_records.append(
            {
                "execution_id": execution_id,
                "domain": schedule_row["domain"],
                "paper_id": schedule_row["paper_id"],
                "task_id": schedule_row["task_id"],
                "execution_family": schedule_row["execution_family"],
                "condition": schedule_row["condition"],
                "model_slot_id": schedule_row["model_slot_id"],
                "variant_id": schedule_row.get("variant_id"),
                "candidate_id": schedule_row["candidate_id"],
                "terminal_outcome": terminal["terminal_outcome"],
                "scoring_available": scoring_path is not None,
                "worker_error_cases": len(errors),
                "payload_key_error_cases": payload_errors,
                "implementation_available": implementation is not None,
                **patterns,
            }
        )

    payload_rows = [row for row in row_records if row["payload_key_error_cases"]]
    access_rows = [row for row in row_records if row["case_payload_access"]]
    access_scoring_rows = [row for row in access_rows if row["scoring_available"]]
    interface_audit = audit_interface(materialization)
    result = {
        "schema_version": "effectslice-fg3-interface-failure-analysis.v1",
        "registered_rows": len(row_records),
        "scoring_documents": sum(row["scoring_available"] for row in row_records),
        "worker_error_cases": sum(row["worker_error_cases"] for row in row_records),
        "payload_key_error_cases": sum(
            row["payload_key_error_cases"] for row in row_records
        ),
        "payload_key_error_rows": len(payload_rows),
        "payload_error_case_count_distribution": dict(
            sorted(Counter(str(row["payload_key_error_cases"]) for row in payload_rows).items())
        ),
        "affected_rows_cover_all_64_private_cases": all(
            row["payload_key_error_cases"] == 64 for row in payload_rows
        ),
        "implementation_available_rows": sum(
            row["implementation_available"] for row in row_records
        ),
        "case_payload_access_rows": len(access_rows),
        "case_payload_access_scoring_rows": len(access_scoring_rows),
        "payload_error_rows_with_detected_access": sum(
            row["case_payload_access"] for row in payload_rows
        ),
        "detected_access_rows_without_payload_error": sum(
            not row["payload_key_error_cases"] for row in access_rows
        ),
        "interface_audit": interface_audit,
        "grouped": {
            "by_task": group_summary(row_records, ("domain", "paper_id", "task_id")),
            "by_family": group_summary(row_records, ("execution_family",)),
            "by_condition": group_summary(row_records, ("condition",)),
            "by_model": group_summary(row_records, ("model_slot_id",)),
            "by_variant": group_summary(row_records, ("execution_family", "variant_id")),
            "by_family_condition": group_summary(
                row_records, ("execution_family", "condition")
            ),
        },
        "interpretation": {
            "fact": (
                "All 24 scaffolds expose wrapped fixture rows as the input shape, while "
                "the frozen worker passes only each row's inner payload to solve(case)."
            ),
            "diagnostic_evidence": (
                "Payload KeyError counts and generated case-payload access are bound to "
                "the frozen schedule and terminal scoring artifacts."
            ),
            "causal_limit": (
                "This post-run audit diagnoses a plausible systematic task-interface "
                "failure; it does not reinterpret, repair, or rescue any FG3 outcome."
            ),
            "forward_action": (
                "Any corrected wording or rerun must be a separately registered, "
                "committed forward successor."
            ),
        },
        "credential_values_recorded": False,
    }
    return result, row_records


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--materialization", type=Path, default=DEFAULT_MATERIALIZATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result, rows = analyze(
        args.successor.resolve(),
        args.run_dir.resolve(),
        args.materialization.resolve(),
    )
    output_dir = args.output_dir.resolve()
    json_path = output_dir / "interface_failure_analysis.json"
    row_path = output_dir / "interface_failure_rows.csv"
    group_path = output_dir / "interface_failure_groups.csv"
    atomic_json(json_path, result)
    write_csv(
        row_path,
        rows,
        [
            "execution_id",
            "domain",
            "paper_id",
            "task_id",
            "execution_family",
            "condition",
            "model_slot_id",
            "variant_id",
            "candidate_id",
            "terminal_outcome",
            "scoring_available",
            "worker_error_cases",
            "payload_key_error_cases",
            "implementation_available",
            "case_payload_subscript",
            "case_payload_get",
            "case_payload_access",
        ],
    )
    flat_groups: list[dict[str, Any]] = []
    for grouping, values in result["grouped"].items():
        flat_groups.extend({"grouping": grouping, **value} for value in values)
    write_csv(
        group_path,
        flat_groups,
        [
            "grouping",
            "domain",
            "paper_id",
            "task_id",
            "execution_family",
            "condition",
            "model_slot_id",
            "variant_id",
            "registered_rows",
            "scoring_rows",
            "rows_with_any_worker_error",
            "worker_error_cases",
            "payload_key_error_rows",
            "payload_key_error_cases",
            "case_payload_access_rows",
            "operational_success_rows",
        ],
    )
    hashes = {
        path.name: sha256_path(path) for path in (json_path, row_path, group_path)
    }
    atomic_json(output_dir / "interface_failure_output_hashes.json", hashes)
    print(
        json.dumps(
            {
                "status": "passed",
                "registered_rows": result["registered_rows"],
                "payload_key_error_cases": result["payload_key_error_cases"],
                "payload_key_error_rows": result["payload_key_error_rows"],
                "case_payload_access_rows": result["case_payload_access_rows"],
                "output_dir": str(output_dir),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InterfaceAnalysisError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
