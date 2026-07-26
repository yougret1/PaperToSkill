from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import completion_verifier as completion
import full_grid_analysis as analysis
import single_repeat_analysis as single
import terminal_row_successor_v2 as successor


SCHEMA_VERSION = "effectslice-full-grid-three-repeat-successor-analysis.v1"


def verify_exact_sets(
    registration_root: Path,
    runs_root: Path,
    repeat_id: str,
) -> None:
    schedule = analysis.runner.repeat_schedule(registration_root, repeat_id)
    expected_ids = {str(row["execution_id"]) for row in schedule}
    analysis.require(
        len(expected_ids) == analysis.registration.ROWS_PER_REPEAT,
        f"registered execution IDs changed: {repeat_id}",
    )
    run_dir = runs_root / repeat_id
    actual_sets = {
        "result": completion.directory_ids(run_dir / "rows", ".json"),
        "metadata": completion.directory_ids(run_dir / "metadata", ".json"),
        "terminal": completion.directory_ids(
            run_dir / "dispatch", ".terminal.json"
        ),
    }
    for name, actual in actual_sets.items():
        analysis.require(
            actual == expected_ids,
            f"{name} set is not exact: {repeat_id}",
        )
    for execution_id in expected_ids:
        marker = analysis.load_json(
            run_dir / "dispatch" / f"{execution_id}.terminal.json"
        )
        analysis.require(
            marker["execution_id"] == execution_id,
            f"terminal marker binding changed: {execution_id}",
        )


def load_completion_report(repeat_id: str) -> dict[str, Any]:
    path = completion.DEFAULT_OUTPUT / f"{repeat_id.lower()}.json"
    report = analysis.load_json(path)
    analysis.require(report["status"] == "passed", f"verification failed: {repeat_id}")
    analysis.require(
        report["unique_terminal_result_rows"] == analysis.registration.ROWS_PER_REPEAT,
        f"verification row count changed: {repeat_id}",
    )
    analysis.require(
        report["network_states_recorded_as_final"] is False,
        f"network state recorded as final: {repeat_id}",
    )
    return report


def paper_task_averaged_effects(
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in decisions:
        grouped[str(row["task_id"])].append(row)
    analysis.require(len(grouped) == 24, "paper-task count changed")
    result: dict[str, Any] = {
        "independent_unit": "paper_task",
        "repeat_aggregation": "mean_within_paper_task_before_interval",
    }
    for contrast in ("F_minus_B", "S_minus_B", "S_minus_F"):
        values: list[float] = []
        for task_id, rows in grouped.items():
            analysis.require(
                len(rows) == len(analysis.registration.REPEAT_IDS),
                f"repeat coverage changed: {task_id}",
            )
            contrasts = [row[contrast] for row in rows]
            analysis.require(
                all(value is not None for value in contrasts),
                f"missing contrast: {task_id}:{contrast}",
            )
            values.append(statistics.fmean(float(value) for value in contrasts))
        result[contrast] = analysis.approximate_mean_ci(values)
    return result


def grouped_performance(
    rows: list[dict[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)
    result: dict[str, dict[str, Any]] = {}
    for name, group in sorted(groups.items()):
        scores = [
            score
            for row in group
            if (score := analysis.numeric_score(row)) is not None
        ]
        result[name] = {
            "registered_rows": len(group),
            "valid_rows": sum(row.get("row_valid") is True for row in group),
            "technical_invalid_rows": sum(
                row.get("row_valid") is not True for row in group
            ),
            "operational_successes": sum(
                row.get("condition_success") is True for row in group
            ),
            "operational_success_rate": sum(
                row.get("condition_success") is True for row in group
            )
            / len(group),
            "mean_private_score_over_scored_rows": (
                statistics.fmean(scores) if scores else None
            ),
        }
    return result


def grouped_stability(
    records: list[dict[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        groups[str(row[field])].append(row)
    result: dict[str, dict[str, Any]] = {}
    for name, group in sorted(groups.items()):
        result[name] = {
            "logical_cells": len(group),
            "terminal_outcome_agreement_count": sum(
                row["terminal_outcome_agreement"] for row in group
            ),
            "terminal_outcome_agreement_rate": sum(
                row["terminal_outcome_agreement"] for row in group
            )
            / len(group),
            "condition_success_agreement_count": sum(
                row["condition_success_agreement"] for row in group
            ),
            "condition_success_agreement_rate": sum(
                row["condition_success_agreement"] for row in group
            )
            / len(group),
        }
    return result


def render_report(value: dict[str, Any]) -> str:
    base = analysis.render_report(value).rstrip()
    pooled = value["paper_task_averaged_effects"]
    outcomes = value["aggregate_terminal_outcomes"]
    lines = [
        base,
        "",
        "## Paper-Task-Averaged Effects",
        "",
    ]
    for contrast in ("F_minus_B", "S_minus_B", "S_minus_F"):
        row = pooled[contrast]
        lines.append(
            f"- {contrast}: {row['mean']:.6f} "
            f"(approximate 95% CI [{row['approximate_95ci_lower']:.6f}, "
            f"{row['approximate_95ci_upper']:.6f}])."
        )
    lines.extend(
        [
            "",
            "## Aggregate Terminal Outcomes",
            "",
            *(f"- {name}: {count}." for name, count in outcomes.items()),
            "",
            "Effects average repetitions within each paper-task before the "
            "24-unit interval is computed. No API random-seed claim is made.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze_successor_grid(
    registration_root: Path,
    runs_root: Path,
    output: Path,
) -> dict[str, Any]:
    registration_root = analysis.registration.fg1.windows_extended_path(
        registration_root
    )
    runs_root = analysis.registration.fg1.windows_extended_path(runs_root)
    output = analysis.registration.fg1.windows_extended_path(output)
    verified = analysis.registration.verify(registration_root, require_frozen=True)
    successor.verify_freeze()

    completion_reports: dict[str, dict[str, Any]] = {}
    repeat_rows: dict[str, list[dict[str, Any]]] = {}
    for repeat_id in analysis.registration.REPEAT_IDS:
        verify_exact_sets(registration_root, runs_root, repeat_id)
        completion_reports[repeat_id] = load_completion_report(repeat_id)
        repeat_rows[repeat_id] = single.load_repeat_rows(
            registration_root,
            runs_root,
            repeat_id,
        )

    summaries = {
        repeat_id: analysis.repeat_summary(rows, repeat_id)
        for repeat_id, rows in repeat_rows.items()
    }
    decisions_by_repeat = {
        repeat_id: analysis.primary_decisions(rows, repeat_id)
        for repeat_id, rows in repeat_rows.items()
    }
    effects = {
        repeat_id: analysis.primary_effects(decisions_by_repeat[repeat_id], repeat_id)
        for repeat_id in analysis.registration.REPEAT_IDS
    }
    all_rows = [
        row
        for repeat_id in analysis.registration.REPEAT_IDS
        for row in repeat_rows[repeat_id]
    ]
    all_decisions = [
        row
        for repeat_id in analysis.registration.REPEAT_IDS
        for row in decisions_by_repeat[repeat_id]
    ]
    terminal_outcomes = Counter(
        str(row["terminal_outcome"])
        for row in all_rows
    )
    cell_stability = analysis.logical_cell_stability(all_rows)
    decision_stability = analysis.primary_decision_stability(all_decisions)
    value = {
        "schema_version": SCHEMA_VERSION,
        "analysis_timing": "posthoc_after_all_repeat_completion",
        "registration_bundle_sha256": verified["registration_bundle_sha256"],
        "rows_per_repeat": analysis.registration.ROWS_PER_REPEAT,
        "total_registered_rows": analysis.registration.TOTAL_REPEAT_ROWS,
        "repetition_kind": "independent_exact_protocol_repetition",
        "api_random_seed_used": False,
        "frozen_scoring_and_decision_functions_reused": True,
        "hash_bound_metadata_overlay_materialized_in_memory": True,
        "completion_reports": completion_reports,
        "repeat_summaries": summaries,
        "primary_effects": effects,
        "primary_decisions": decisions_by_repeat,
        "paper_task_averaged_effects": paper_task_averaged_effects(all_decisions),
        "aggregate_performance": {
            "by_model_slot": grouped_performance(all_rows, "model_slot_id"),
            "by_execution_family": grouped_performance(
                all_rows, "execution_family"
            ),
            "by_condition": grouped_performance(all_rows, "condition"),
            "by_domain": grouped_performance(all_rows, "domain"),
        },
        "logical_cell_stability": cell_stability,
        "logical_cell_stability_by_model_slot": grouped_stability(
            cell_stability["records"], "model_slot_id"
        ),
        "logical_cell_stability_by_execution_family": grouped_stability(
            cell_stability["records"], "execution_family"
        ),
        "primary_decision_stability": decision_stability,
        "aggregate_terminal_outcomes": dict(sorted(terminal_outcomes.items())),
    }
    analysis.atomic_json(output / "analysis.json", value)
    report_path = output / "REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(value), encoding="utf-8", newline="\n")
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=analysis.DEFAULT_REGISTRATION,
    )
    parser.add_argument("--runs", type=Path, default=analysis.DEFAULT_RUNS)
    parser.add_argument("--output", type=Path, default=analysis.DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    value = analyze_successor_grid(args.registration, args.runs, args.output)
    summary = {
        "schema_version": value["schema_version"],
        "total_registered_rows": value["total_registered_rows"],
        "aggregate_terminal_outcomes": value["aggregate_terminal_outcomes"],
        "paper_task_averaged_effects": value["paper_task_averaged_effects"],
        "logical_cell_stability": {
            key: item
            for key, item in value["logical_cell_stability"].items()
            if key != "records"
        },
        "primary_decision_stability": {
            key: item
            for key, item in value["primary_decision_stability"].items()
            if key != "records"
        },
    }
    print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except analysis.AnalysisError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
