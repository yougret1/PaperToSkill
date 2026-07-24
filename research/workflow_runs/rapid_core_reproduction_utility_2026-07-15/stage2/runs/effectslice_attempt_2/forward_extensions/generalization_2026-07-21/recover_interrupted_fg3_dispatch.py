from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import format_conformance_successor as fg3
import remote_execution_runner as fg1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register a non-replayed FG3 dispatch interrupted before any terminal evidence."
    )
    parser.add_argument("execution_id")
    args = parser.parse_args()

    parent = fg1.windows_extended_path(ROOT / "materialization_remote_only_2026-07-23")
    fg2_root = fg1.windows_extended_path(ROOT / "output_budget_successor_2026-07-23")
    successor = fg1.windows_extended_path(ROOT / "format_conformance_successor_2026-07-23")
    run_dir = fg1.windows_extended_path(ROOT / "remote_execution_v3_2026-07-23")
    schedule = fg3.load_json(successor / "global_remote_schedule.json")["rows"]
    matches = [row for row in schedule if str(row["execution_id"]) == args.execution_id]
    fg3.require(len(matches) == 1, "execution_id must identify exactly one registered row")
    row = matches[0]

    started = run_dir / "dispatch" / f"{args.execution_id}.started.json"
    terminal = run_dir / "dispatch" / f"{args.execution_id}.terminal.json"
    row_path = run_dir / "rows" / f"{args.execution_id}.json"
    fg3.require(started.exists(), "started marker is missing")
    fg3.require(not terminal.exists(), "terminal marker already exists")
    fg3.require(not row_path.exists(), "result row already exists")

    resolver = fg3.OverlayResolver(parent, fg2_root, successor)
    inputs = resolver.resolve(row)
    value = fg1.unavailable_row(row, inputs)
    fg1.validate_result_row(parent, value, str(row["model_slot_id"]))

    row_bytes = fg1.canonical_json(value)
    terminal_value = {
        "schema_version": "effectslice-fg3-dispatch-terminal.v1",
        "execution_id": args.execution_id,
        "terminal_outcome": value["terminal_outcome"],
        "result_row_sha256": fg1.sha256_bytes(row_bytes),
        "recovered_from_terminal_row": False,
    }
    recovery_value = {
        "schema_version": "effectslice-fg3-interrupted-dispatch-recovery.v1",
        "execution_id": args.execution_id,
        "classification": "provider_or_model_unavailable",
        "reason": "process_exit_after_started_marker_before_dispatch_result_persisted",
        "semantic_rerun_allowed": False,
        "started_marker_sha256": fg1.sha256_file(started),
        "terminal_response_observed": False,
        "transport_attempts_observed": 0,
        "result_row_sha256": fg1.sha256_bytes(row_bytes),
    }
    print("ROW_JSON=" + json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    print("TERMINAL_JSON=" + json.dumps(terminal_value, sort_keys=True, indent=2, ensure_ascii=False))
    print("RECOVERY_JSON=" + json.dumps(recovery_value, sort_keys=True, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
