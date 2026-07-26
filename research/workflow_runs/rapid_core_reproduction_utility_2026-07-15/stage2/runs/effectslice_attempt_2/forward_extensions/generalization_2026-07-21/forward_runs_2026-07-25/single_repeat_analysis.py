from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import full_grid_analysis as analysis
import terminal_row_successor_v2 as successor


SCHEMA_VERSION = "effectslice-full-grid-single-repeat-posthoc-analysis.v1"


def load_repeat_rows(
    registration_root: Path,
    runs_root: Path,
    repeat_id: str,
) -> list[dict[str, Any]]:
    schedule = analysis.runner.repeat_schedule(registration_root, repeat_id)
    run_dir = runs_root / repeat_id
    materialized: list[dict[str, Any]] = []
    for scheduled in schedule:
        result = successor.v1.verify_result_binding(run_dir, scheduled)
        analysis.require(
            not successor.v1.retryable_result(result),
            f"retryable result became terminal: {scheduled['execution_id']}",
        )
        record = dict(scheduled)
        record.update(result)
        record["repeat_id"] = repeat_id
        materialized.append(record)
    analysis.require(
        len(materialized) == analysis.registration.ROWS_PER_REPEAT,
        f"row count changed: {repeat_id}",
    )
    return materialized


def analyze_repeat(
    registration_root: Path,
    runs_root: Path,
    repeat_id: str,
    output: Path,
) -> dict[str, Any]:
    registration_root = analysis.registration.fg1.windows_extended_path(
        registration_root
    )
    runs_root = analysis.registration.fg1.windows_extended_path(runs_root)
    output = analysis.registration.fg1.windows_extended_path(output)
    analysis.require(
        repeat_id in analysis.registration.REPEAT_IDS,
        f"unknown repeat: {repeat_id}",
    )
    verified = analysis.registration.verify(registration_root, require_frozen=True)
    successor.verify_freeze()
    rows = load_repeat_rows(registration_root, runs_root, repeat_id)
    decisions = analysis.primary_decisions(rows, repeat_id)
    value = {
        "schema_version": SCHEMA_VERSION,
        "analysis_timing": "posthoc_after_repeat_completion",
        "frozen_scoring_and_decision_functions_reused": True,
        "hash_bound_metadata_overlay_materialized_in_memory": True,
        "registration_bundle_sha256": verified["registration_bundle_sha256"],
        "repeat_id": repeat_id,
        "registered_rows": analysis.registration.ROWS_PER_REPEAT,
        "repetition_kind": "independent_exact_protocol_repetition",
        "api_random_seed_used": False,
        "repeat_summary": analysis.repeat_summary(rows, repeat_id),
        "primary_effects": analysis.primary_effects(decisions, repeat_id),
        "primary_decisions": decisions,
    }
    analysis.atomic_json(output / f"{repeat_id.lower()}.json", value)
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repeat", choices=analysis.registration.REPEAT_IDS)
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
    value = analyze_repeat(
        args.registration,
        args.runs,
        args.repeat,
        args.output,
    )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except analysis.AnalysisError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
