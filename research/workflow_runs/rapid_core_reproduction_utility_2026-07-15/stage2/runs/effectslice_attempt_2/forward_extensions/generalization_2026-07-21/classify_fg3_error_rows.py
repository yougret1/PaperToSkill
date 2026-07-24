from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import build_fg5_output_contracts as contracts
import remote_execution_runner as runner


FORWARD_ROOT = Path(__file__).resolve().parent
DEFAULT_FG3 = FORWARD_ROOT / "format_conformance_successor_2026-07-23"
DEFAULT_FG3_RUN = FORWARD_ROOT / "remote_execution_v3_2026-07-23"
DEFAULT_FG5 = FORWARD_ROOT / "output_contract_successor_2026-07-24"
DEFAULT_CONTRACTS = contracts.DEFAULT_OUTPUT
DEFAULT_OUTPUT = (
    FORWARD_ROOT
    / "fg5_development_2026-07-24"
    / "fg3_error_classification.json"
)
DEFAULT_ALL_SELECTION = (
    FORWARD_ROOT
    / "fg5_development_2026-07-24"
    / "exact_output_contract_all_rows.json"
)
DEFAULT_SAMPLE_SELECTION = (
    FORWARD_ROOT
    / "fg5_development_2026-07-24"
    / "exact_output_contract_task_sample.json"
)
MODEL_SLOTS = (
    "deepseek_primary",
    "gpt_5_5",
    "gpt_5_6_sol",
    "gpt_5_6_terra",
    "gpt_5_6_luna",
    "claude_opus_4_7",
)


class ClassificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClassificationError(message)


def load_json(path: Path) -> Any:
    return runner.load_json(path)


def write_json(path: Path, value: object) -> None:
    runner.atomic_json(path, value)


def load_scoring(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"invalid scoring evidence: {path.name}")
    return value


def _is_payload_interface_error(errors: list[dict[str, Any]]) -> bool:
    return bool(errors) and all(
        str(item.get("error_type")) == "KeyError"
        and "payload" in str(item.get("message", ""))
        for item in errors
    )


def classify_row(
    row: dict[str, Any],
    result: dict[str, Any],
    scoring: dict[str, Any] | None,
    shape: dict[str, Any],
) -> dict[str, Any]:
    outcome = str(result["terminal_outcome"])
    classification = "experimental_outcome_not_technical_error"
    detail = outcome
    shape_mismatch_count = 0
    first_shape_violation: str | None = None
    worker_error_count = 0

    if outcome == "operational_success":
        classification = "operational_success"
    elif outcome == "malformed_or_no_submission":
        classification = "response_format"
    elif outcome == "integrity_or_digest_failure":
        classification = "integrity_or_digest"
    elif outcome == "provider_or_model_unavailable":
        classification = "provider_availability"
    elif scoring is not None:
        errors = scoring.get("errors", [])
        outputs = scoring.get("outputs", [])
        errors = errors if isinstance(errors, list) else []
        outputs = outputs if isinstance(outputs, list) else []
        worker_error_count = len(errors)
        if _is_payload_interface_error(errors):
            classification = "payload_input_interface"
            detail = "all recorded worker errors are KeyError('payload')"
        elif not errors and outputs:
            for output_row in outputs:
                require(
                    isinstance(output_row, dict)
                    and isinstance(output_row.get("case_id"), str)
                    and "output" in output_row,
                    "scoring evidence output row has an unexpected shape",
                )
                issues = contracts.shape_violations(output_row["output"], shape)
                if issues:
                    shape_mismatch_count += 1
                    if first_shape_violation is None:
                        first_shape_violation = issues[0]
            if shape_mismatch_count:
                classification = "exact_output_contract"
                detail = "one or more inner output values violate the public structural contract"
            else:
                detail = "output structure conforms; failure is algorithmic or score-related"
        elif errors:
            detail = "worker errors are not the payload-interface signature"
        else:
            detail = "no scoreable outputs were recorded"

    return {
        "fg3_execution_id": row["execution_id"],
        "task_id": row["task_id"],
        "condition": row["condition"],
        "candidate_id": row["candidate_id"],
        "model_slot_id": row["model_slot_id"],
        "registry_id": row["registry_id"],
        "terminal_outcome": outcome,
        "technical_classification": classification,
        "classification_detail": detail,
        "worker_error_count": worker_error_count,
        "shape_mismatch_output_count": shape_mismatch_count,
        "first_shape_violation": first_shape_violation,
    }


def choose_task_sample(
    exact_rows: list[dict[str, Any]],
    fg5_by_fg3: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in exact_rows:
        by_task[str(item["task_id"])].append(item)
    selected: list[dict[str, Any]] = []
    for index, task_id in enumerate(sorted(by_task)):
        target_slot = MODEL_SLOTS[index % len(MODEL_SLOTS)]
        candidates = by_task[task_id]
        candidates.sort(
            key=lambda item: (
                item["condition"] != "F",
                item["model_slot_id"] != target_slot,
                item["condition"] != "S",
                str(item["fg3_execution_id"]),
            )
        )
        choice = candidates[0]
        fg5_row = fg5_by_fg3[str(choice["fg3_execution_id"])]
        selected.append(
            {
                "execution_id": fg5_row["execution_id"],
                "fg3_execution_id": choice["fg3_execution_id"],
                "task_id": task_id,
                "condition": choice["condition"],
                "model_slot_id": choice["model_slot_id"],
            }
        )
    return selected


def build_classification(
    fg3_root: Path,
    fg3_run: Path,
    fg5_root: Path,
    contract_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    fg3_root = runner.windows_extended_path(fg3_root)
    fg3_run = runner.windows_extended_path(fg3_run)
    fg5_root = runner.windows_extended_path(fg5_root)
    contract_path = runner.windows_extended_path(contract_path)
    contract_value = load_json(contract_path)
    shapes = {
        str(item["task_id"]): item["output_shape"] for item in contract_value["tasks"]
    }
    require(len(shapes) == 24, "output contract task count changed")
    fg3_rows = load_json(fg3_root / "global_remote_schedule.json")["rows"]
    fg5_rows = load_json(fg5_root / "global_remote_schedule.json")["rows"]
    require(len(fg3_rows) == len(fg5_rows) == 1296, "registered row count changed")
    fg5_by_fg3 = {str(row["fg3_execution_id"]): row for row in fg5_rows}
    require(len(fg5_by_fg3) == 1296, "FG5/FG3 lineage is not one-to-one")

    records: list[dict[str, Any]] = []
    for row in fg3_rows:
        execution_id = str(row["execution_id"])
        result_path = fg3_run / "rows" / f"{execution_id}.json"
        require(result_path.is_file(), f"missing FG3 terminal row: {execution_id}")
        result = load_json(result_path)
        scoring_path = fg3_run / "scoring" / f"{execution_id}.json.gz"
        scoring = load_scoring(scoring_path) if scoring_path.is_file() else None
        records.append(classify_row(row, result, scoring, shapes[str(row["task_id"]) ]))

    counts = Counter(str(item["technical_classification"]) for item in records)
    exact_rows = [
        item for item in records if item["technical_classification"] == "exact_output_contract"
    ]
    all_selection_rows = [
        {
            "execution_id": fg5_by_fg3[str(item["fg3_execution_id"])]["execution_id"],
            "fg3_execution_id": item["fg3_execution_id"],
            "task_id": item["task_id"],
            "condition": item["condition"],
            "model_slot_id": item["model_slot_id"],
        }
        for item in exact_rows
    ]
    sample_rows = choose_task_sample(exact_rows, fg5_by_fg3)
    classification = {
        "schema_version": "effectslice-fg5-fg3-error-classification.v1",
        "registered_rows": len(records),
        "classification_counts": dict(sorted(counts.items())),
        "exact_output_contract_rows": len(exact_rows),
        "exact_output_contract_tasks": len({item["task_id"] for item in exact_rows}),
        "records": records,
    }
    all_selection = {
        "schema_version": "effectslice-fg5-selection.v1",
        "selection_name": "all_fg3_exact_output_contract_rows",
        "row_count": len(all_selection_rows),
        "execution_ids": [item["execution_id"] for item in all_selection_rows],
        "rows": all_selection_rows,
    }
    sample_selection = {
        "schema_version": "effectslice-fg5-selection.v1",
        "selection_name": "one_exact_output_contract_row_per_affected_task",
        "row_count": len(sample_rows),
        "execution_ids": [item["execution_id"] for item in sample_rows],
        "rows": sample_rows,
    }
    return classification, all_selection, sample_selection


def build_and_write(
    fg3_root: Path,
    fg3_run: Path,
    fg5_root: Path,
    contract_path: Path,
    output: Path,
    all_selection_path: Path,
    sample_selection_path: Path,
) -> dict[str, Any]:
    classification, all_selection, sample_selection = build_classification(
        fg3_root, fg3_run, fg5_root, contract_path
    )
    write_json(output, classification)
    write_json(all_selection_path, all_selection)
    write_json(sample_selection_path, sample_selection)
    return {
        "status": "passed",
        "registered_rows": classification["registered_rows"],
        "classification_counts": classification["classification_counts"],
        "exact_output_contract_rows": classification["exact_output_contract_rows"],
        "exact_output_contract_tasks": classification["exact_output_contract_tasks"],
        "task_sample_rows": sample_selection["row_count"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build",))
    parser.add_argument("--fg3", type=Path, default=DEFAULT_FG3)
    parser.add_argument("--fg3-run", type=Path, default=DEFAULT_FG3_RUN)
    parser.add_argument("--fg5", type=Path, default=DEFAULT_FG5)
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--all-selection", type=Path, default=DEFAULT_ALL_SELECTION)
    parser.add_argument("--sample-selection", type=Path, default=DEFAULT_SAMPLE_SELECTION)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    value = build_and_write(
        args.fg3,
        args.fg3_run,
        args.fg5,
        args.contracts,
        args.output,
        args.all_selection,
        args.sample_selection,
    )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ClassificationError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
