from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import build_fg5_output_contracts as contracts
import classify_fg3_error_rows as classifier
import remote_execution_runner as runner


FORWARD_ROOT = Path(__file__).resolve().parent
DEVELOPMENT_ROOT = FORWARD_ROOT / "fg5_development_2026-07-24"
DEFAULT_FG5 = FORWARD_ROOT / "output_contract_successor_2026-07-24"
DEFAULT_RUN = FORWARD_ROOT / "remote_execution_v5_development_2026-07-24"
DEFAULT_CONTRACTS = contracts.DEFAULT_OUTPUT
DEFAULT_SELECTION = DEVELOPMENT_ROOT / "exact_output_contract_task_sample.json"
DEFAULT_ALL_SELECTION = DEVELOPMENT_ROOT / "exact_output_contract_all_rows.json"
DEFAULT_OUTPUT = DEVELOPMENT_ROOT / "exact_output_contract_task_sample_analysis.json"
DEFAULT_REPLACEMENTS = DEVELOPMENT_ROOT / "exact_output_contract_replacement_sample.json"
DEFAULT_FINAL_REPORT = DEVELOPMENT_ROOT / "exact_output_contract_final_report.json"


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalysisError(message)


def load_json(path: Path) -> Any:
    return runner.load_json(path)


def write_json(path: Path, value: object) -> None:
    runner.atomic_json(path, value)


def choose_replacements(
    inconclusive: list[dict[str, Any]],
    selected_ids: set[str],
    all_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    replacements: list[dict[str, Any]] = []
    used = set(selected_ids)
    for item in inconclusive:
        task_id = str(item["task_id"])
        candidates = [
            row
            for row in all_rows
            if str(row["task_id"]) == task_id and str(row["execution_id"]) not in used
        ]
        candidates.sort(
            key=lambda row: (
                row["condition"] != "F",
                row["condition"] != "S",
                str(row["model_slot_id"]),
                str(row["execution_id"]),
            )
        )
        if not candidates:
            continue
        choice = candidates[0]
        used.add(str(choice["execution_id"]))
        replacements.append(choice)
    return replacements


def audit_output_shapes(
    scoring: dict[str, Any] | None,
    shape: dict[str, Any],
) -> tuple[int, int, str | None]:
    if scoring is None:
        return 0, 0, None
    outputs = scoring.get("outputs", [])
    require(isinstance(outputs, list), "scoring outputs must be an array")
    mismatch_count = 0
    first_violation: str | None = None
    for output_row in outputs:
        require(
            isinstance(output_row, dict)
            and isinstance(output_row.get("case_id"), str)
            and "output" in output_row,
            "scoring evidence output row has an unexpected shape",
        )
        issues = contracts.shape_violations(output_row["output"], shape)
        if issues:
            mismatch_count += 1
            if first_violation is None:
                first_violation = issues[0]
    return len(outputs), mismatch_count, first_violation


def final_report(
    analysis: dict[str, Any],
    *,
    analysis_sha256: str,
    selection_sha256: str,
) -> dict[str, Any]:
    technical = analysis["technical_classifications"]
    candidate_error_rows = [
        {
            "fg5_execution_id": item["fg5_execution_id"],
            "fg3_execution_id": item["fg3_execution_id"],
            "task_id": item["task_id"],
            "condition": item["condition"],
            "model_slot_id": item["model_slot_id"],
            "worker_error_count": item["worker_error_count"],
        }
        for item in analysis["records"]
        if item["worker_error_count"]
        and item["technical_classification"]
        == "experimental_outcome_not_technical_error"
    ]
    non_evaluable_experimental_rows = [
        {
            "fg5_execution_id": item["fg5_execution_id"],
            "fg3_execution_id": item["fg3_execution_id"],
            "task_id": item["task_id"],
            "condition": item["condition"],
            "model_slot_id": item["model_slot_id"],
            "worker_status": item["worker_status"],
            "worker_error_count": item["worker_error_count"],
        }
        for item in analysis["records"]
        if item["worker_output_count"] == 0
        and item["technical_classification"]
        == "experimental_outcome_not_technical_error"
    ]
    passed = (
        analysis["selected_rows"] == 684
        and analysis["selected_tasks"] == 24
        and analysis["shape_evaluable_rows"] > 0
        and analysis["shape_mismatch_output_count"] == 0
        and analysis["output_contract_mismatch_rows"] == 0
    )
    return {
        "schema_version": "effectslice-fg5-output-contract-final-report.v1",
        "class_name": "exact_output_contract",
        "status": "completed" if passed else "incomplete",
        "class_validation_passed": passed,
        "success_criterion": (
            "all returned case outputs from the 684 terminal FG5 rows conform "
            "to their frozen public structural output contract; response, "
            "integrity, and candidate-algorithm failures remain explicit"
        ),
        "selected_fg3_rows": analysis["selected_rows"],
        "terminal_fg5_rows": analysis["selected_rows"],
        "affected_tasks": analysis["selected_tasks"],
        "shape_evaluable_rows": analysis["shape_evaluable_rows"],
        "output_values_checked": analysis["output_values_checked"],
        "shape_conforming_output_values": (
            analysis["output_values_checked"]
            - analysis["shape_mismatch_output_count"]
        ),
        "shape_mismatch_output_values": analysis["shape_mismatch_output_count"],
        "operational_success_rows": analysis["operational_success_rows"],
        "experimental_outcome_rows": technical.get(
            "experimental_outcome_not_technical_error", 0
        ),
        "candidate_worker_error_rows": candidate_error_rows,
        "non_evaluable_experimental_rows": non_evaluable_experimental_rows,
        "deferred_response_format_rows": technical.get("response_format", 0),
        "deferred_integrity_or_digest_rows": technical.get(
            "integrity_or_digest", 0
        ),
        "deferred_provider_availability_rows": technical.get(
            "provider_availability", 0
        ),
        "analysis_sha256": analysis_sha256,
        "selection_sha256": selection_sha256,
    }


def analyze(
    fg5_root: Path,
    run_dir: Path,
    contract_path: Path,
    selection_path: Path,
    all_selection_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fg5_root = runner.windows_extended_path(fg5_root)
    run_dir = runner.windows_extended_path(run_dir)
    contract_path = runner.windows_extended_path(contract_path)
    selection_path = runner.windows_extended_path(selection_path)
    all_selection_path = runner.windows_extended_path(all_selection_path)
    shapes = {
        str(item["task_id"]): item["output_shape"]
        for item in load_json(contract_path)["tasks"]
    }
    schedule = load_json(fg5_root / "global_remote_schedule.json")["rows"]
    by_id = {str(row["execution_id"]): row for row in schedule}
    selection = load_json(selection_path)
    selected_ids = [str(item) for item in selection["execution_ids"]]
    require(len(selected_ids) == selection["row_count"], "selection row count changed")

    records: list[dict[str, Any]] = []
    for execution_id in selected_ids:
        require(execution_id in by_id, f"unknown selected FG5 row: {execution_id}")
        row = by_id[execution_id]
        result_path = run_dir / "rows" / f"{execution_id}.json"
        require(result_path.is_file(), f"selected FG5 row is not terminal: {execution_id}")
        result = load_json(result_path)
        scoring_path = run_dir / "scoring" / f"{execution_id}.json.gz"
        scoring = classifier.load_scoring(scoring_path) if scoring_path.is_file() else None
        output_count, audited_mismatches, audited_first_violation = audit_output_shapes(
            scoring, shapes[str(row["task_id"])]
        )
        classified = classifier.classify_row(
            row, result, scoring, shapes[str(row["task_id"])]
        )
        require(
            classified["shape_mismatch_output_count"] in {0, audited_mismatches},
            "classifier and independent output-shape audit disagree",
        )
        records.append(
            {
                "fg5_execution_id": execution_id,
                "fg3_execution_id": row["fg3_execution_id"],
                "task_id": row["task_id"],
                "condition": row["condition"],
                "model_slot_id": row["model_slot_id"],
                "terminal_outcome": result["terminal_outcome"],
                "private_score": result["private_score"],
                "technical_classification": classified["technical_classification"],
                "classification_detail": classified["classification_detail"],
                "worker_error_count": classified["worker_error_count"],
                "worker_status": scoring.get("worker_status") if scoring else None,
                "worker_output_count": output_count,
                "shape_mismatch_output_count": audited_mismatches,
                "first_shape_violation": audited_first_violation,
            }
        )

    counts = Counter(str(item["technical_classification"]) for item in records)
    mismatches = [
        item for item in records if item["shape_mismatch_output_count"] > 0
    ]
    inconclusive = [
        item
        for item in records
        if item["technical_classification"]
        in {"response_format", "integrity_or_digest", "provider_availability"}
    ]
    worker_error_rows = [
        item
        for item in records
        if item["worker_error_count"] and item["technical_classification"] != "exact_output_contract"
    ]
    shape_evaluable_rows = [item for item in records if item["worker_output_count"] > 0]
    output_values_checked = sum(item["worker_output_count"] for item in records)
    shape_mismatch_output_count = sum(
        item["shape_mismatch_output_count"] for item in records
    )
    analysis = {
        "schema_version": "effectslice-fg5-output-contract-sample-analysis.v1",
        "selection_name": selection["selection_name"],
        "selected_rows": len(records),
        "selected_tasks": len({item["task_id"] for item in records}),
        "terminal_outcomes": dict(sorted(Counter(item["terminal_outcome"] for item in records).items())),
        "technical_classifications": dict(sorted(counts.items())),
        "operational_success_rows": sum(
            item["terminal_outcome"] == "operational_success" for item in records
        ),
        "output_contract_mismatch_rows": len(mismatches),
        "shape_evaluable_rows": len(shape_evaluable_rows),
        "output_values_checked": output_values_checked,
        "shape_mismatch_output_count": shape_mismatch_output_count,
        "inconclusive_rows": len(inconclusive),
        "non_contract_worker_error_rows": len(worker_error_rows),
        "task_sample_passed": not mismatches and not worker_error_rows and not inconclusive,
        "records": records,
    }
    all_selection = load_json(all_selection_path)
    replacements = choose_replacements(
        inconclusive,
        set(selected_ids),
        list(all_selection["rows"]),
    )
    replacement_manifest = {
        "schema_version": "effectslice-fg5-selection.v1",
        "selection_name": "replacement_rows_for_inconclusive_output_contract_samples",
        "row_count": len(replacements),
        "execution_ids": [row["execution_id"] for row in replacements],
        "rows": replacements,
    }
    return analysis, replacement_manifest


def build_and_write(
    fg5_root: Path,
    run_dir: Path,
    contract_path: Path,
    selection_path: Path,
    all_selection_path: Path,
    output_path: Path,
    replacement_path: Path,
    final_report_path: Path,
) -> dict[str, Any]:
    analysis, replacements = analyze(
        fg5_root, run_dir, contract_path, selection_path, all_selection_path
    )
    write_json(output_path, analysis)
    write_json(replacement_path, replacements)
    report = final_report(
        analysis,
        analysis_sha256=runner.sha256_file(output_path),
        selection_sha256=runner.sha256_file(selection_path),
    )
    write_json(final_report_path, report)
    return {
        "status": "passed",
        "selected_rows": analysis["selected_rows"],
        "selected_tasks": analysis["selected_tasks"],
        "terminal_outcomes": analysis["terminal_outcomes"],
        "technical_classifications": analysis["technical_classifications"],
        "output_contract_mismatch_rows": analysis["output_contract_mismatch_rows"],
        "inconclusive_rows": analysis["inconclusive_rows"],
        "non_contract_worker_error_rows": analysis["non_contract_worker_error_rows"],
        "shape_evaluable_rows": analysis["shape_evaluable_rows"],
        "output_values_checked": analysis["output_values_checked"],
        "shape_mismatch_output_count": analysis["shape_mismatch_output_count"],
        "replacement_rows": replacements["row_count"],
        "replacement_shortfall_rows": max(
            0, analysis["inconclusive_rows"] - replacements["row_count"]
        ),
        "task_sample_passed": analysis["task_sample_passed"],
        "class_validation_passed": report["class_validation_passed"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build",))
    parser.add_argument("--fg5", type=Path, default=DEFAULT_FG5)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--all-selection", type=Path, default=DEFAULT_ALL_SELECTION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--replacements", type=Path, default=DEFAULT_REPLACEMENTS)
    parser.add_argument("--final-report", type=Path, default=DEFAULT_FINAL_REPORT)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    value = build_and_write(
        args.fg5,
        args.run_dir,
        args.contracts,
        args.selection,
        args.all_selection,
        args.output,
        args.replacements,
        args.final_report,
    )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
