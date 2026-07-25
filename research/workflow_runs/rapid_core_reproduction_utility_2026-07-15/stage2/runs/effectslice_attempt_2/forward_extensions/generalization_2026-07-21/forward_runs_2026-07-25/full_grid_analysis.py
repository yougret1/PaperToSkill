from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


EXPERIMENT_ROOT = Path(__file__).resolve().parent
FORWARD_ROOT = EXPERIMENT_ROOT.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))
if str(FORWARD_ROOT) not in sys.path:
    sys.path.insert(0, str(FORWARD_ROOT))

import aggregate_fg3_results as aggregate  # noqa: E402
import full_grid_registration as registration  # noqa: E402
import full_grid_runner as runner  # noqa: E402


DEFAULT_REGISTRATION = registration.DEFAULT_OUTPUT
DEFAULT_RUNS = runner.DEFAULT_RUNS
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "analysis" / "full_grid"
SCHEMA_VERSION = "effectslice-full-grid-three-repeat-analysis.v1"


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalysisError(message)


def load_json(path: Path) -> Any:
    return registration.load_json(path)


def atomic_json(path: Path, value: object) -> None:
    registration.atomic_json(path, value)


def stable_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def numeric_score(row: dict[str, Any]) -> float | None:
    score = row.get("private_score")
    if isinstance(score, (int, float)) and not isinstance(score, bool):
        value = float(score)
        if math.isfinite(value):
            return value
    return None


def approximate_mean_ci(values: list[float]) -> dict[str, Any]:
    require(bool(values), "cannot summarize an empty effect set")
    mean = statistics.fmean(values)
    if len(values) == 1:
        lower = upper = mean
    else:
        standard_error = statistics.stdev(values) / math.sqrt(len(values))
        lower = mean - 1.96 * standard_error
        upper = mean + 1.96 * standard_error
    return {
        "independent_units": len(values),
        "mean": mean,
        "approximate_95ci_lower": lower,
        "approximate_95ci_upper": upper,
        "ci_method": "normal approximation over paper-task units",
    }


def load_repeat_rows(
    registration_root: Path, runs_root: Path, repeat_id: str
) -> list[dict[str, Any]]:
    registration_root = registration.fg1.windows_extended_path(registration_root)
    runs_root = registration.fg1.windows_extended_path(runs_root)
    schedule = runner.repeat_schedule(registration_root, repeat_id)
    materialized: list[dict[str, Any]] = []
    for scheduled in schedule:
        result_path = runs_root / repeat_id / "rows" / f"{scheduled['execution_id']}.json"
        require(result_path.is_file(), f"missing terminal row: {repeat_id}:{scheduled['execution_id']}")
        result = load_json(result_path)
        runner.verify_existing_row(result_path, scheduled)
        record = dict(scheduled)
        record.update(result)
        record["repeat_id"] = repeat_id
        record["source_fg5_execution_id"] = scheduled["source_fg5_execution_id"]
        record["logical_cell_id"] = scheduled["logical_cell_id"]
        materialized.append(record)
    require(len(materialized) == registration.ROWS_PER_REPEAT, f"row count changed: {repeat_id}")
    return materialized


def grouped_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def repeat_summary(rows: list[dict[str, Any]], repeat_id: str) -> dict[str, Any]:
    valid = [row for row in rows if row.get("row_valid") is True]
    scores = [score for row in rows if (score := numeric_score(row)) is not None]
    return {
        "repeat_id": repeat_id,
        "registered_rows": len(rows),
        "valid_rows": len(valid),
        "technical_invalid_rows": len(rows) - len(valid),
        "operational_successes": sum(row.get("condition_success") is True for row in rows),
        "terminal_outcomes": grouped_counts(rows, "terminal_outcome"),
        "execution_families": grouped_counts(rows, "execution_family"),
        "model_slots": grouped_counts(rows, "model_slot_id"),
        "conditions": grouped_counts(rows, "condition"),
        "domains": grouped_counts(rows, "domain"),
        "mean_private_score_over_scored_rows": statistics.fmean(scores) if scores else None,
    }


def primary_decisions(rows: list[dict[str, Any]], repeat_id: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["execution_family"] == "primary":
            grouped[str(row["task_id"])].append(row)
    require(len(grouped) == 24, f"primary paper-task count changed: {repeat_id}")
    decisions: list[dict[str, Any]] = []
    for task_id, task_rows in sorted(grouped.items()):
        require(len(task_rows) == 18, f"primary row count changed: {repeat_id}:{task_id}")
        decision = aggregate.decision_state(task_rows)
        condition_scores: dict[str, float | None] = {}
        for condition in ("B", "F", "S"):
            values = [
                score
                for row in task_rows
                if row["condition"] == condition
                and (score := numeric_score(row)) is not None
            ]
            condition_scores[condition] = statistics.fmean(values) if len(values) == 6 else None
        decisions.append(
            {
                "repeat_id": repeat_id,
                "task_id": task_id,
                "paper_id": task_rows[0]["paper_id"],
                "domain": task_rows[0]["domain"],
                "state": decision["state"],
                "reasons": decision["reasons"],
                "successes": decision.get("successes"),
                "mean_private_score": condition_scores,
                "F_minus_B": (
                    condition_scores["F"] - condition_scores["B"]
                    if condition_scores["F"] is not None and condition_scores["B"] is not None
                    else None
                ),
                "S_minus_B": (
                    condition_scores["S"] - condition_scores["B"]
                    if condition_scores["S"] is not None and condition_scores["B"] is not None
                    else None
                ),
                "S_minus_F": (
                    condition_scores["S"] - condition_scores["F"]
                    if condition_scores["S"] is not None and condition_scores["F"] is not None
                    else None
                ),
            }
        )
    return decisions


def primary_effects(decisions: list[dict[str, Any]], repeat_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {"repeat_id": repeat_id}
    for contrast in ("F_minus_B", "S_minus_B", "S_minus_F"):
        values = [float(row[contrast]) for row in decisions if row[contrast] is not None]
        result[contrast] = approximate_mean_ci(values) if values else None
    result["decision_states"] = grouped_counts(decisions, "state")
    return result


def logical_cell_stability(all_rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        groups[str(row["logical_cell_id"])].append(row)
    require(len(groups) == registration.ROWS_PER_REPEAT, "logical-cell count changed")
    records: list[dict[str, Any]] = []
    for logical_cell_id, rows in sorted(groups.items()):
        require(len(rows) == len(registration.REPEAT_IDS), f"repeat coverage changed: {logical_cell_id}")
        require(
            {str(row["repeat_id"]) for row in rows} == set(registration.REPEAT_IDS),
            f"repeat IDs changed: {logical_cell_id}",
        )
        scores = [numeric_score(row) for row in rows]
        finite_scores = [score for score in scores if score is not None]
        records.append(
            {
                "logical_cell_id": logical_cell_id,
                "source_fg5_execution_id": rows[0]["source_fg5_execution_id"],
                "task_id": rows[0]["task_id"],
                "execution_family": rows[0]["execution_family"],
                "model_slot_id": rows[0]["model_slot_id"],
                "terminal_outcome_agreement": len({str(row["terminal_outcome"]) for row in rows}) == 1,
                "row_valid_agreement": len({stable_value(row.get("row_valid")) for row in rows}) == 1,
                "condition_success_agreement": len({stable_value(row.get("condition_success")) for row in rows}) == 1,
                "private_score_all_available": len(finite_scores) == len(rows),
                "private_score_range": (
                    max(finite_scores) - min(finite_scores)
                    if len(finite_scores) == len(rows)
                    else None
                ),
            }
        )
    count = len(records)
    return {
        "logical_cells": count,
        "terminal_outcome_agreement_count": sum(row["terminal_outcome_agreement"] for row in records),
        "terminal_outcome_agreement_rate": sum(row["terminal_outcome_agreement"] for row in records) / count,
        "condition_success_agreement_count": sum(row["condition_success_agreement"] for row in records),
        "condition_success_agreement_rate": sum(row["condition_success_agreement"] for row in records) / count,
        "all_scored_cell_count": sum(row["private_score_all_available"] for row in records),
        "records": records,
    }


def primary_decision_stability(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in decisions:
        groups[str(row["task_id"])].append(row)
    require(len(groups) == 24, "primary stability task count changed")
    records = []
    for task_id, rows in sorted(groups.items()):
        require(len(rows) == 3, f"primary repeat coverage changed: {task_id}")
        states = {str(row["repeat_id"]): str(row["state"]) for row in rows}
        records.append(
            {
                "task_id": task_id,
                "paper_id": rows[0]["paper_id"],
                "domain": rows[0]["domain"],
                "states": states,
                "all_three_states_equal": len(set(states.values())) == 1,
            }
        )
    return {
        "paper_task_units": len(records),
        "all_three_states_equal_count": sum(row["all_three_states_equal"] for row in records),
        "all_three_states_equal_rate": sum(row["all_three_states_equal"] for row in records) / len(records),
        "records": records,
    }


def render_report(value: dict[str, Any]) -> str:
    lines = [
        "# FG6-FG8 Exact-Protocol Repetition Report",
        "",
        f"Registration bundle: `{value['registration_bundle_sha256']}`",
        "",
        "Each repetition contains exactly 1,296 registered terminal rows. The three repetitions total 3,888 rows.",
        "",
        "## Repeat Completion",
        "",
        "| Repeat | Registered | Valid | Invalid | Operational success |",
        "|---|---:|---:|---:|---:|",
    ]
    for repeat_id in registration.REPEAT_IDS:
        row = value["repeat_summaries"][repeat_id]
        lines.append(
            f"| {repeat_id} | {row['registered_rows']} | {row['valid_rows']} | "
            f"{row['technical_invalid_rows']} | {row['operational_successes']} |"
        )
    cell = value["logical_cell_stability"]
    decision = value["primary_decision_stability"]
    lines.extend(
        [
            "",
            "## Stability",
            "",
            f"- Terminal-outcome agreement: {cell['terminal_outcome_agreement_count']}/{cell['logical_cells']}.",
            f"- Condition-success agreement: {cell['condition_success_agreement_count']}/{cell['logical_cells']}.",
            f"- Primary decision agreement: {decision['all_three_states_equal_count']}/{decision['paper_task_units']} paper-task units.",
            "",
            "Technical Invalid rows remain in every registered denominator. These are independent exact-protocol repetitions, not API random-seed runs.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze(registration_root: Path, runs_root: Path, output: Path) -> dict[str, Any]:
    registration_root = registration.fg1.windows_extended_path(registration_root)
    runs_root = registration.fg1.windows_extended_path(runs_root)
    output = registration.fg1.windows_extended_path(output)
    verified = runner.verify_runs(registration_root, runs_root, require_complete=True)
    repeat_rows = {
        repeat_id: load_repeat_rows(registration_root, runs_root, repeat_id)
        for repeat_id in registration.REPEAT_IDS
    }
    summaries = {
        repeat_id: repeat_summary(rows, repeat_id)
        for repeat_id, rows in repeat_rows.items()
    }
    decisions_by_repeat = {
        repeat_id: primary_decisions(rows, repeat_id)
        for repeat_id, rows in repeat_rows.items()
    }
    effects = {
        repeat_id: primary_effects(decisions_by_repeat[repeat_id], repeat_id)
        for repeat_id in registration.REPEAT_IDS
    }
    all_rows = [row for repeat_id in registration.REPEAT_IDS for row in repeat_rows[repeat_id]]
    all_decisions = [
        row
        for repeat_id in registration.REPEAT_IDS
        for row in decisions_by_repeat[repeat_id]
    ]
    value = {
        "schema_version": SCHEMA_VERSION,
        "registration_bundle_sha256": verified["registration_bundle_sha256"],
        "rows_per_repeat": registration.ROWS_PER_REPEAT,
        "total_registered_rows": registration.TOTAL_REPEAT_ROWS,
        "repetition_kind": "independent_exact_protocol_repetition",
        "api_random_seed_used": False,
        "repeat_summaries": summaries,
        "primary_effects": effects,
        "primary_decisions": decisions_by_repeat,
        "logical_cell_stability": logical_cell_stability(all_rows),
        "primary_decision_stability": primary_decision_stability(all_decisions),
    }
    atomic_json(output / "analysis.json", value)
    report_path = output / "REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(value), encoding="utf-8", newline="\n")
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, default=DEFAULT_REGISTRATION)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    value = analyze(args.registration, args.runs, args.output)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
