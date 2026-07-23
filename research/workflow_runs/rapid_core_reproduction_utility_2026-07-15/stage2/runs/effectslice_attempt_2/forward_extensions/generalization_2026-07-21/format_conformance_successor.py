from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

import output_budget_successor as fg2
import remote_execution_runner as fg1


FORWARD_ROOT = Path(__file__).resolve().parent
DEFAULT_PARENT = FORWARD_ROOT / "materialization_remote_only_2026-07-23"
DEFAULT_FG2 = FORWARD_ROOT / "output_budget_successor_2026-07-23"
DEFAULT_SUCCESSOR = FORWARD_ROOT / "format_conformance_successor_2026-07-23"
DEFAULT_RUN_DIR = FORWARD_ROOT / "remote_execution_v3_2026-07-23"
INVALID_FG2_REPORT = FORWARD_ROOT / "stage_report_2_3_fg2_budget_pilot_2026_07_23.json"
EXPECTED_FG2_BUNDLE = (
    "917fa2d4a722e3b05b3b2fc5d97ebe9f6ee36b888a03844f2a1334e326045411"
)
INVALID_FG2_COMMIT = "13d027ce"
FORMAT_VERSION = "fg3-bare-json-envelope-v1"
PILOT_MARKER = (
    "[FORMAT-CONFORMANCE PILOT - NOT SCORED]\n"
    "This request is excluded from every experiment estimate.\n\n"
)
FORMAT_INSTRUCTION = (
    "[STRICT SUBMISSION ENVELOPE]\n"
    "Your entire response must be exactly one valid JSON object with the single "
    "key \"implementation\". The first non-whitespace character must be { and "
    "the last non-whitespace character must be }. Do not use Markdown code "
    "fences. Do not add a preamble, explanation, or trailing text. Encode the "
    "Python source as a JSON string, escaping newlines, backslashes, and quotes "
    "as required by JSON.\n\n"
)


class FormatSuccessorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FormatSuccessorError(message)


def load_json(path: Path) -> Any:
    return fg1.load_json(path)


def canonical_json(value: object) -> bytes:
    return fg1.canonical_json(value)


def sha256_bytes(value: bytes) -> str:
    return fg1.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(path)


def write_json(path: Path, value: object) -> None:
    fg1.atomic_json(path, value)


def visible_request_text(value: dict[str, Any]) -> tuple[str, Any]:
    if isinstance(value.get("input"), str):
        return "input", value["input"]
    messages = value.get("messages")
    require(
        isinstance(messages, list) and len(messages) == 1,
        "request must contain one message or one input string",
    )
    message = messages[0]
    require(
        isinstance(message, dict) and isinstance(message.get("content"), str),
        "message content is not a string",
    )
    return "message", message


def transformed_request_bytes(
    fg2_request_bytes: bytes, *, pilot: bool = False
) -> bytes:
    value = json.loads(fg2_request_bytes.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), "FG2 request must be a JSON object")
    budget_key = fg2.output_budget_key(value)
    require(
        value[budget_key] == fg2.NEW_OUTPUT_BUDGET,
        "FG2 output budget changed",
    )
    kind, target = visible_request_text(value)
    prefix = (PILOT_MARKER if pilot else "") + FORMAT_INSTRUCTION
    if kind == "input":
        value["input"] = prefix + str(target)
    else:
        target["content"] = prefix + target["content"]
    return canonical_json(value)


def execution_id(fg2_execution_id: str) -> str:
    value = f"{FORMAT_VERSION}|{fg2_execution_id}".encode("utf-8")
    return "fg3-exec-" + hashlib.sha256(value).hexdigest()[:24]


def pilot_execution_id(slot_id: str) -> str:
    value = f"{FORMAT_VERSION}|pilot|{slot_id}".encode("utf-8")
    return "fg3-pilot-" + hashlib.sha256(value).hexdigest()[:20]


def fg2_request_path(fg2_root: Path, row: dict[str, Any]) -> Path:
    return fg2_root / "requests" / f"{row['execution_id']}.json"


def manifest_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name == "successor_manifest.json":
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def bundle_sha(files: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        canonical_json(
            {
                "schema_version": "effectslice-fg3-successor-binding.v1",
                "fg2_successor_bundle_sha256": EXPECTED_FG2_BUNDLE,
                "format_contract_version": FORMAT_VERSION,
                "files": files,
            }
        )
    )


def freeze_successor(
    parent: Path,
    fg2_root: Path,
    successor: Path,
) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    successor = fg1.windows_extended_path(successor)
    invalid_report = fg1.windows_extended_path(INVALID_FG2_REPORT)
    fg2_verification = fg2.verify_successor(parent, fg2_root)
    require(
        fg2_verification["bundle_sha256"] == EXPECTED_FG2_BUNDLE,
        "FG2 bundle binding changed",
    )
    require(invalid_report.is_file(), "invalid FG2 pilot report is missing")
    report = load_json(invalid_report)
    require(report.get("status") == "invalid", "FG2 pilot is not invalid")
    require(
        report.get("pilot", {}).get("strict_submission_fail_count") == 2,
        "FG2 pilot failure count changed",
    )
    require(not successor.exists(), "FG3 successor directory already exists")
    temporary = successor.with_name(successor.name + ".tmp")
    require(not temporary.exists(), "FG3 temporary directory already exists")
    temporary.mkdir(parents=True)
    try:
        fg2_rows = load_json(fg2_root / "global_remote_schedule.json")["rows"]
        require(len(fg2_rows) == 1296, "FG2 schedule row count changed")
        rows: list[dict[str, Any]] = []
        first_by_slot: dict[str, dict[str, Any]] = {}
        for fg2_row in fg2_rows:
            fg2_id = str(fg2_row["execution_id"])
            request_path = fg2_request_path(fg2_root, fg2_row)
            require(
                sha256_file(request_path)
                == fg2_row["serialized_wire_request_sha256"],
                f"FG2 request SHA changed: {fg2_id}",
            )
            new_id = execution_id(fg2_id)
            request_bytes = transformed_request_bytes(request_path.read_bytes())
            path = temporary / "requests" / f"{new_id}.json"
            fg1.atomic_write(path, request_bytes)
            row = copy.deepcopy(fg2_row)
            row["fg1_execution_id"] = fg2_row["parent_execution_id"]
            row["parent_execution_id"] = fg2_id
            row["execution_id"] = new_id
            row["format_contract_version"] = FORMAT_VERSION
            row["serialized_wire_request_sha256"] = sha256_bytes(request_bytes)
            rows.append(row)
            first_by_slot.setdefault(str(row["model_slot_id"]), fg2_row)
        require(
            len({row["execution_id"] for row in rows}) == 1296,
            "FG3 execution IDs are not unique",
        )
        write_json(
            temporary / "global_remote_schedule.json",
            {
                "schema_version": "effectslice-fg3-remote-schedule.v1",
                "fg2_successor_bundle_sha256": EXPECTED_FG2_BUNDLE,
                "format_contract_version": FORMAT_VERSION,
                "registered_rows": 1296,
                "rows": rows,
            },
        )

        pilot_rows: list[dict[str, Any]] = []
        for slot_id in sorted(fg1.PROVIDER_SPECS):
            source = first_by_slot[slot_id]
            source_path = fg2_request_path(fg2_root, source)
            request_bytes = transformed_request_bytes(
                source_path.read_bytes(), pilot=True
            )
            path = temporary / "pilot" / "requests" / f"{slot_id}.json"
            fg1.atomic_write(path, request_bytes)
            pilot_rows.append(
                {
                    "pilot_execution_id": pilot_execution_id(slot_id),
                    "model_slot_id": slot_id,
                    "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias,
                    "source_fg2_execution_id": source["execution_id"],
                    "request_path": f"pilot/requests/{slot_id}.json",
                    "serialized_wire_request_sha256": sha256_bytes(request_bytes),
                    "registered_experiment_row": False,
                    "scored": False,
                }
            )
        write_json(
            temporary / "pilot_manifest.json",
            {
                "schema_version": "effectslice-fg3-format-pilot.v1",
                "output_budget": fg2.NEW_OUTPUT_BUDGET,
                "format_contract_version": FORMAT_VERSION,
                "format_instruction": FORMAT_INSTRUCTION,
                "pilot_marker": PILOT_MARKER,
                "pass_rule": (
                    "All six exact aliases must return a non-truncated bare JSON "
                    "object containing exactly one nonempty implementation string."
                ),
                "registered_experiment_rows_consumed": 0,
                "rows": pilot_rows,
            },
        )
        write_json(
            temporary / "registration.json",
            {
                "schema_version": "effectslice-fg3-format-successor.v1",
                "created_at_utc": fg1.utc_now(),
                "fg2_successor_bundle_sha256": EXPECTED_FG2_BUNDLE,
                "invalid_fg2_pilot_report": INVALID_FG2_REPORT.name,
                "invalid_fg2_pilot_report_sha256": sha256_file(invalid_report),
                "invalid_fg2_pilot_commit": INVALID_FG2_COMMIT,
                "fg1_or_fg2_rows_pooled_with_fg3": False,
                "output_budget": fg2.NEW_OUTPUT_BUDGET,
                "format_contract_version": FORMAT_VERSION,
                "allowed_request_mutation": "prepend uniform format-only instruction",
                "task_candidate_registry_scorer_mutation": False,
                "model_alias_or_endpoint_mutation": False,
                "registered_rows": 1296,
                "pilot_required_before_registered_execution": True,
            },
        )
        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-fg3-successor-manifest.v1",
            "fg2_successor_bundle_sha256": EXPECTED_FG2_BUNDLE,
            "format_contract_version": FORMAT_VERSION,
            "files": files,
            "file_count": len(files),
            "bundle_sha256": bundle_sha(files),
            "provider_calls_started": False,
        }
        write_json(temporary / "successor_manifest.json", manifest)
        os.replace(temporary, successor)
        return manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_successor(
    parent: Path,
    fg2_root: Path,
    successor: Path,
) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    successor = fg1.windows_extended_path(successor)
    invalid_report = fg1.windows_extended_path(INVALID_FG2_REPORT)
    fg2_result = fg2.verify_successor(parent, fg2_root)
    require(
        fg2_result["bundle_sha256"] == EXPECTED_FG2_BUNDLE,
        "FG2 bundle changed",
    )
    manifest = load_json(successor / "successor_manifest.json")
    files = manifest_files(successor)
    require(files == manifest["files"], "FG3 file manifest changed")
    require(bundle_sha(files) == manifest["bundle_sha256"], "FG3 bundle SHA changed")
    registration = load_json(successor / "registration.json")
    require(
        registration["invalid_fg2_pilot_report_sha256"]
        == sha256_file(invalid_report),
        "invalid FG2 pilot report changed",
    )
    fg2_rows = load_json(fg2_root / "global_remote_schedule.json")["rows"]
    rows = load_json(successor / "global_remote_schedule.json")["rows"]
    require(len(fg2_rows) == len(rows) == 1296, "FG3 row count changed")
    fg2_by_id = {str(row["execution_id"]): row for row in fg2_rows}
    seen: set[str] = set()
    for row in rows:
        parent_id = str(row["parent_execution_id"])
        require(parent_id in fg2_by_id, "unknown FG2 parent row")
        fg2_row = fg2_by_id[parent_id]
        new_id = execution_id(parent_id)
        require(row["execution_id"] == new_id, "FG3 execution ID changed")
        require(new_id not in seen, "duplicate FG3 execution ID")
        seen.add(new_id)
        source = fg2_request_path(fg2_root, fg2_row)
        expected_bytes = transformed_request_bytes(source.read_bytes())
        request_path = successor / "requests" / f"{new_id}.json"
        require(request_path.read_bytes() == expected_bytes, "FG3 request changed")
        require(
            row["serialized_wire_request_sha256"] == sha256_bytes(expected_bytes),
            "FG3 request SHA changed",
        )
        expected_row = copy.deepcopy(fg2_row)
        expected_row["fg1_execution_id"] = fg2_row["parent_execution_id"]
        expected_row["parent_execution_id"] = parent_id
        expected_row["execution_id"] = new_id
        expected_row["format_contract_version"] = FORMAT_VERSION
        expected_row["serialized_wire_request_sha256"] = sha256_bytes(expected_bytes)
        require(row == expected_row, "FG3 row changed outside allowed fields")

    pilot = load_json(successor / "pilot_manifest.json")
    require(len(pilot["rows"]) == 6, "FG3 pilot row count changed")
    for item in pilot["rows"]:
        slot_id = str(item["model_slot_id"])
        path = successor / str(item["request_path"])
        require(
            sha256_file(path) == item["serialized_wire_request_sha256"],
            "FG3 pilot request SHA changed",
        )
        value = json.loads(path.read_text(encoding="utf-8"))
        budget_key = fg2.output_budget_key(value)
        require(value[budget_key] == fg2.NEW_OUTPUT_BUDGET, "FG3 budget changed")
        kind, target = visible_request_text(value)
        visible = target if kind == "input" else target["content"]
        require(
            visible.startswith(PILOT_MARKER + FORMAT_INSTRUCTION),
            "FG3 pilot prefix changed",
        )
        require(
            value["model"] == fg1.PROVIDER_SPECS[slot_id].exact_alias,
            "FG3 pilot alias changed",
        )
    return {
        "status": "passed",
        "bundle_sha256": manifest["bundle_sha256"],
        "registered_rows": 1296,
        "pilot_rows": 6,
        "output_budget": fg2.NEW_OUTPUT_BUDGET,
        "format_contract_version": FORMAT_VERSION,
    }


def initialize_run_manifest(
    run_dir: Path,
    successor: Path,
    credential_metadata: dict[str, Any],
) -> dict[str, Any]:
    successor_manifest = load_json(successor / "successor_manifest.json")
    path = run_dir / "run_manifest.json"
    expected = {
        "schema_version": "effectslice-fg3-remote-run.v1",
        "successor_bundle_sha256": successor_manifest["bundle_sha256"],
        "fg2_successor_bundle_sha256": EXPECTED_FG2_BUNDLE,
        "registered_rows": 1296,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
    }
    if path.exists():
        current = load_json(path)
        for key, value in expected.items():
            require(current.get(key) == value, f"FG3 run manifest {key} changed")
        return current
    value = {
        **expected,
        "created_at_utc": fg1.utc_now(),
        "provider_calls_started": False,
    }
    write_json(path, value)
    return value


def run_pilot(
    parent: Path,
    fg2_root: Path,
    successor: Path,
    run_dir: Path,
    docs_dir: Path,
) -> dict[str, Any]:
    verify_successor(parent, fg2_root, successor)
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    credentials, metadata = fg1.load_credentials(docs_dir)
    initialize_run_manifest(run_dir, successor, metadata)
    pilot = load_json(successor / "pilot_manifest.json")
    results: list[dict[str, Any]] = []
    for item in pilot["rows"]:
        slot_id = str(item["model_slot_id"])
        pilot_id = str(item["pilot_execution_id"])
        result_path = run_dir / "pilot" / f"{slot_id}.json"
        started_path = run_dir / "pilot" / f"{slot_id}.started.json"
        if result_path.exists():
            value = load_json(result_path)
            require(value["pilot_execution_id"] == pilot_id, "FG3 pilot ID changed")
            results.append(value)
            continue
        require(
            not started_path.exists(),
            f"ambiguous FG3 pilot dispatch lacks terminal result: {slot_id}",
        )
        write_json(
            started_path,
            {
                "schema_version": "effectslice-fg3-pilot-start.v1",
                "pilot_execution_id": pilot_id,
                "model_slot_id": slot_id,
                "started_at_utc": fg1.utc_now(),
                "semantic_rerun_allowed": False,
            },
        )
        request_bytes = (successor / str(item["request_path"])).read_bytes()
        require(
            sha256_bytes(request_bytes) == item["serialized_wire_request_sha256"],
            "FG3 pilot request changed before dispatch",
        )
        dispatch = fg1.dispatch_request(
            fg1.PROVIDER_SPECS[slot_id],
            credentials[slot_id],
            pilot_id,
            request_bytes,
        )
        fg1.persist_attempts(
            run_dir / "pilot",
            pilot_id,
            dispatch,
            (credentials[slot_id],),
        )
        raw_path: str | None = None
        raw_sha: str | None = None
        if dispatch.terminal_body is not None:
            raw = run_dir / "pilot" / "raw" / f"{slot_id}.json"
            fg1.atomic_write(raw, dispatch.terminal_body)
            raw_path = f"pilot/raw/{slot_id}.json"
            raw_sha = sha256_bytes(dispatch.terminal_body)
        status, reason, finish, termination = fg2.pilot_status(
            parent, slot_id, dispatch
        )
        value = {
            "schema_version": "effectslice-fg3-format-pilot-result.v1",
            "pilot_execution_id": pilot_id,
            "model_slot_id": slot_id,
            "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias,
            "status": status,
            "reason": reason,
            "provider_finish_reason": finish,
            "termination_reason": termination,
            "logical_request_count": 1,
            "transport_attempt_count": len(dispatch.attempts),
            "raw_response_path": raw_path,
            "raw_response_sha256": raw_sha,
            "credential_value_recorded": False,
            "completed_at_utc": fg1.utc_now(),
        }
        write_json(result_path, value)
        results.append(value)
    summary = {
        "schema_version": "effectslice-fg3-format-pilot-summary.v1",
        "format_contract_version": FORMAT_VERSION,
        "output_budget": fg2.NEW_OUTPUT_BUDGET,
        "slots": results,
        "available_slot_count": sum(
            item["status"] == "available" for item in results
        ),
        "all_slots_available": all(
            item["status"] == "available" for item in results
        ),
        "credential_values_recorded": False,
        "registered_experiment_rows_consumed": 0,
        "completed_at_utc": fg1.utc_now(),
    }
    write_json(run_dir / "pilot_summary.json", summary)
    manifest = load_json(run_dir / "run_manifest.json")
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    return summary


class OverlayResolver:
    def __init__(self, parent: Path, fg2_root: Path, successor: Path):
        self.parent = fg1.windows_extended_path(parent)
        self.fg2_root = fg1.windows_extended_path(fg2_root)
        self.successor = fg1.windows_extended_path(successor)
        self.fg2_rows = {
            str(row["execution_id"]): row
            for row in load_json(
                self.fg2_root / "global_remote_schedule.json"
            )["rows"]
        }
        self.fg2_resolver = fg2.OverlayResolver(self.parent, self.fg2_root)

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        parent_id = str(row["parent_execution_id"])
        require(parent_id in self.fg2_rows, "unknown FG3 parent row")
        parent_inputs = self.fg2_resolver.resolve(self.fg2_rows[parent_id])
        request_path = self.successor / "requests" / f"{row['execution_id']}.json"
        request_bytes = request_path.read_bytes()
        require(
            sha256_bytes(request_bytes) == row["serialized_wire_request_sha256"],
            "FG3 request SHA changed",
        )
        return fg1.RowInputs(
            task_dir=parent_inputs.task_dir,
            request_path=request_path,
            request_bytes=request_bytes,
            payload_path=parent_inputs.payload_path,
            fixture_path=parent_inputs.fixture_path,
            scorer_path=parent_inputs.scorer_path,
            candidate_path=parent_inputs.candidate_path,
            candidate_tokens=parent_inputs.candidate_tokens,
        )


def progress_summary(
    run_dir: Path, schedule: list[dict[str, Any]]
) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    by_slot: dict[str, int] = {}
    completed = 0
    for row in schedule:
        path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not path.exists():
            continue
        value = load_json(path)
        completed += 1
        outcome = str(value["terminal_outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        slot_id = str(row["model_slot_id"])
        by_slot[slot_id] = by_slot.get(slot_id, 0) + 1
    return {
        "schema_version": "effectslice-fg3-remote-progress.v1",
        "updated_at_utc": fg1.utc_now(),
        "registered_rows": len(schedule),
        "terminal_rows": completed,
        "remaining_rows": len(schedule) - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def run_schedule(
    parent: Path,
    fg2_root: Path,
    successor: Path,
    run_dir: Path,
    docs_dir: Path,
    max_new_rows: int | None,
) -> dict[str, Any]:
    verify_successor(parent, fg2_root, successor)
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    pilot = load_json(run_dir / "pilot_summary.json")
    require(pilot.get("all_slots_available") is True, "FG3 pilot did not pass")
    credentials, metadata = fg1.load_credentials(docs_dir)
    manifest = initialize_run_manifest(run_dir, successor, metadata)
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    schedule = load_json(successor / "global_remote_schedule.json")["rows"]
    resolver = OverlayResolver(parent, fg2_root, successor)
    new_rows = 0
    for row in schedule:
        execution = str(row["execution_id"])
        row_path = run_dir / "rows" / f"{execution}.json"
        started = run_dir / "dispatch" / f"{execution}.started.json"
        terminal = run_dir / "dispatch" / f"{execution}.terminal.json"
        if row_path.exists():
            fg1.validate_existing_row(parent, row_path, row)
            continue
        if max_new_rows is not None and new_rows >= max_new_rows:
            break
        require(
            not started.exists(),
            f"ambiguous FG3 dispatch lacks terminal result: {execution}",
        )
        inputs = resolver.resolve(row)
        write_json(
            started,
            {
                "schema_version": "effectslice-fg3-dispatch-start.v1",
                "execution_id": execution,
                "parent_execution_id": row["parent_execution_id"],
                "model_slot_id": row["model_slot_id"],
                "serialized_wire_request_sha256": row[
                    "serialized_wire_request_sha256"
                ],
                "started_at_utc": fg1.utc_now(),
                "semantic_rerun_allowed": False,
                "fg3_is_new_versioned_execution": True,
            },
        )
        result = fg1.execute_row(
            parent,
            run_dir,
            row,
            inputs,
            credentials[str(row["model_slot_id"])],
        )
        fg1.write_row(run_dir, row, result, parent)
        write_json(
            terminal,
            {
                "schema_version": "effectslice-fg3-dispatch-terminal.v1",
                "execution_id": execution,
                "terminal_outcome": result["terminal_outcome"],
                "result_row_sha256": sha256_file(row_path),
                "recovered_from_terminal_row": False,
            },
        )
        new_rows += 1
        if new_rows % 5 == 0:
            progress = progress_summary(run_dir, schedule)
            write_json(run_dir / "progress.json", progress)
            print(f"terminal_rows={progress['terminal_rows']}/1296", flush=True)
    progress = progress_summary(run_dir, schedule)
    write_json(run_dir / "progress.json", progress)
    return progress


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "verify", "pilot", "run"))
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--fg2", type=Path, default=DEFAULT_FG2)
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "freeze":
        manifest = freeze_successor(args.parent, args.fg2, args.successor)
        value = {
            "status": "passed",
            "bundle_sha256": manifest["bundle_sha256"],
            "file_count": manifest["file_count"],
            "provider_calls_started": manifest["provider_calls_started"],
        }
    elif args.command == "verify":
        value = verify_successor(args.parent, args.fg2, args.successor)
    elif args.command == "pilot":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = run_pilot(
            args.parent,
            args.fg2,
            args.successor,
            args.run_dir,
            args.docs_dir.resolve(),
        )
    else:
        require(args.docs_dir is not None, "--docs-dir is required")
        require(
            args.max_new_rows is None or args.max_new_rows > 0,
            "--max-new-rows must be positive",
        )
        value = run_schedule(
            args.parent,
            args.fg2,
            args.successor,
            args.run_dir,
            args.docs_dir.resolve(),
            args.max_new_rows,
        )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        FormatSuccessorError,
        fg2.SuccessorError,
        fg1.ExecutionError,
        fg1.IntegrityError,
    ) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
