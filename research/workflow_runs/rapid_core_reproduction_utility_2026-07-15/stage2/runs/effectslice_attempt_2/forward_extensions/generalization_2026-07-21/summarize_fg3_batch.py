from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import format_conformance_successor as fg3
import remote_execution_runner as runner


KEY_ERROR_PATTERN = re.compile(r"^['\"]([A-Za-z_][A-Za-z0-9_]{0,63})['\"]$")


class SummaryError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SummaryError(message)


def load_evidence(path: Path) -> Any:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return runner.load_json(path)


def scoring_path(run_dir: Path, execution_id: str) -> Path | None:
    for name in (f"{execution_id}.json", f"{execution_id}.json.gz"):
        path = run_dir / "scoring" / name
        if path.is_file():
            return path
    return None


def increment(counter: Counter[str], value: object) -> None:
    counter[str(value)] += 1


def sorted_counts(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def numeric_summary(values: list[int | float]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None, "sum": 0}
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
        "sum": sum(values),
    }


def safe_error_signature(error: dict[str, Any]) -> str:
    error_type = str(error.get("error_type", "unknown"))
    message = str(error.get("message", ""))
    if error_type == "KeyError":
        match = KEY_ERROR_PATTERN.fullmatch(message)
        if match:
            return f"KeyError:{match.group(1)}"
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]
    return f"{error_type}:sha256-{digest}"


def summarize(successor: Path, run_dir: Path) -> dict[str, Any]:
    successor = runner.windows_extended_path(successor)
    run_dir = runner.windows_extended_path(run_dir)
    schedule = runner.load_json(successor / "global_remote_schedule.json")["rows"]
    require(len(schedule) == 1296, "FG3 schedule row count changed")
    completed: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in schedule:
        row_path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not row_path.is_file():
            break
        completed.append((row, runner.load_json(row_path)))
    completed_ids = {str(row["execution_id"]) for row, _ in completed}
    all_row_files = list((run_dir / "rows").glob("*.json"))
    require(
        len(all_row_files) == len(completed),
        "completed rows are not an exact contiguous schedule prefix",
    )
    require(
        {path.stem for path in all_row_files} == completed_ids,
        "row directory contains an out-of-prefix execution",
    )

    outcomes: Counter[str] = Counter()
    model_slots: Counter[str] = Counter()
    hard_vectors: Counter[str] = Counter()
    worker_statuses: Counter[str] = Counter()
    error_types: Counter[str] = Counter()
    safe_error_signatures: Counter[str] = Counter()
    attempt_statuses: Counter[str] = Counter()
    output_tokens: list[int] = []
    input_tokens: list[int] = []
    elapsed_ms: list[int] = []
    private_scores: list[float] = []
    total_attempts = 0
    rows_with_errors = 0
    rows_with_zero_outputs = 0
    total_errors = 0
    groups: dict[tuple[str, ...], dict[str, Any]] = {}

    for row, result in completed:
        execution_id = str(row["execution_id"])
        require(result.get("execution_id") == execution_id, "row execution ID changed")
        outcome = str(result["terminal_outcome"])
        increment(outcomes, outcome)
        increment(model_slots, row["model_slot_id"])
        vector = result.get("hard_contract_vector")
        vector_key = "null" if vector is None else json.dumps(vector, separators=(",", ":"))
        increment(hard_vectors, vector_key)
        attempts = result.get("attempts", [])
        require(isinstance(attempts, list) and attempts, "row has no attempts")
        total_attempts += len(attempts)
        for attempt in attempts:
            increment(attempt_statuses, attempt.get("attempt_status_class"))
        for key, target in (
            ("provider_reported_output_tokens", output_tokens),
            ("provider_reported_input_tokens", input_tokens),
            ("total_execution_elapsed_ms", elapsed_ms),
        ):
            value = result.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                target.append(value)
        private_score = result.get("private_score")
        if isinstance(private_score, (int, float)) and not isinstance(private_score, bool):
            private_scores.append(float(private_score))

        worker_status = "not_scored"
        error_count = 0
        output_count = 0
        score_path = scoring_path(run_dir, execution_id)
        if score_path is not None:
            evidence = load_evidence(score_path)
            worker_status = str(evidence.get("worker_status", "unknown"))
            errors = evidence.get("errors", [])
            outputs = evidence.get("outputs", [])
            if not isinstance(errors, list):
                errors = []
            if not isinstance(outputs, list):
                outputs = []
            error_count = len(errors)
            output_count = len(outputs)
            total_errors += error_count
            rows_with_errors += int(error_count > 0)
            rows_with_zero_outputs += int(output_count == 0)
            for error in errors:
                if not isinstance(error, dict):
                    increment(error_types, "invalid_error_record")
                    continue
                increment(error_types, error.get("error_type", "unknown"))
                increment(safe_error_signatures, safe_error_signature(error))
        increment(worker_statuses, worker_status)

        group_key = (
            str(row["domain"]),
            str(row["paper_id"]),
            str(row["task_id"]),
            str(row["condition"]),
            str(row["variant_id"]),
        )
        group = groups.setdefault(
            group_key,
            {
                "rows": 0,
                "terminal_outcomes": Counter(),
                "hard_contract_vectors": Counter(),
                "worker_statuses": Counter(),
                "rows_with_errors": 0,
                "rows_with_zero_outputs": 0,
                "error_count": 0,
            },
        )
        group["rows"] += 1
        increment(group["terminal_outcomes"], outcome)
        increment(group["hard_contract_vectors"], vector_key)
        increment(group["worker_statuses"], worker_status)
        group["rows_with_errors"] += int(error_count > 0)
        group["rows_with_zero_outputs"] += int(output_count == 0)
        group["error_count"] += error_count

    group_rows: list[dict[str, Any]] = []
    for key in sorted(groups):
        domain, paper_id, task_id, condition, variant_id = key
        group = groups[key]
        group_rows.append(
            {
                "domain": domain,
                "paper_id": paper_id,
                "task_id": task_id,
                "condition": condition,
                "variant_id": variant_id,
                "rows": group["rows"],
                "terminal_outcomes": sorted_counts(group["terminal_outcomes"]),
                "hard_contract_vectors": sorted_counts(group["hard_contract_vectors"]),
                "worker_statuses": sorted_counts(group["worker_statuses"]),
                "rows_with_errors": group["rows_with_errors"],
                "rows_with_zero_outputs": group["rows_with_zero_outputs"],
                "error_count": group["error_count"],
            }
        )

    manifest = runner.load_json(run_dir / "run_manifest.json")
    pilot = runner.load_json(run_dir / "pilot_summary.json")
    return {
        "schema_version": "effectslice-fg3-batch-summary.v1",
        "successor_bundle_sha256": manifest["successor_bundle_sha256"],
        "format_contract_version": fg3.FORMAT_VERSION,
        "registered_rows": len(schedule),
        "terminal_rows": len(completed),
        "remaining_rows": len(schedule) - len(completed),
        "contiguous_schedule_prefix": True,
        "pilot_all_slots_available": pilot.get("all_slots_available") is True,
        "terminal_outcomes": sorted_counts(outcomes),
        "terminal_rows_by_model_slot": sorted_counts(model_slots),
        "hard_contract_vectors": sorted_counts(hard_vectors),
        "worker_statuses": sorted_counts(worker_statuses),
        "rows_with_errors": rows_with_errors,
        "rows_with_zero_outputs": rows_with_zero_outputs,
        "total_worker_errors": total_errors,
        "error_types": sorted_counts(error_types),
        "safe_error_signatures": sorted_counts(safe_error_signatures),
        "logical_request_count": len(completed),
        "transport_attempt_count": total_attempts,
        "transport_retry_count": total_attempts - len(completed),
        "attempt_status_classes": sorted_counts(attempt_statuses),
        "provider_reported_input_tokens": numeric_summary(input_tokens),
        "provider_reported_output_tokens": numeric_summary(output_tokens),
        "total_execution_elapsed_ms": numeric_summary(elapsed_ms),
        "private_score": numeric_summary(private_scores),
        "by_paper_task_condition_variant": group_rows,
        "registered_experiment_rows_consumed": len(completed),
        "credential_values_recorded": False,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--successor", type=Path, default=fg3.DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=fg3.DEFAULT_RUN_DIR)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    summary = summarize(args.successor, args.run_dir)
    if args.output is not None:
        output = runner.windows_extended_path(args.output)
        if output.exists():
            raise SummaryError(f"output already exists: {args.output}")
        runner.atomic_json(output, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SummaryError, fg3.FormatSuccessorError, runner.ExecutionError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
