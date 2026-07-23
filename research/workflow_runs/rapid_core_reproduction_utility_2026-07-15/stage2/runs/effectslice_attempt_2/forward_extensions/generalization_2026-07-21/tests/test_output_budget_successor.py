from __future__ import annotations

import json
import sys
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import output_budget_successor as successor  # noqa: E402


def parent_request(model_slot_id: str) -> tuple[dict[str, object], bytes]:
    root = successor.fg1.windows_extended_path(successor.DEFAULT_PARENT)
    rows = successor.load_json(root / "global_remote_schedule.json")["rows"]
    row = next(item for item in rows if item["model_slot_id"] == model_slot_id)
    path = successor.parent_request_path(root, row)
    return row, path.read_bytes()


def test_request_transformation_changes_only_output_budget() -> None:
    for slot_id in successor.fg1.PROVIDER_SPECS:
        _, source = parent_request(slot_id)
        before = json.loads(source)
        after = json.loads(successor.transformed_request_bytes(source))
        key = successor.output_budget_key(before)
        assert before[key] == 1024
        assert after[key] == 8192
        before[key] = 8192
        assert after == before


def test_pilot_transformation_is_distinct_and_marked() -> None:
    for slot_id in successor.fg1.PROVIDER_SPECS:
        _, source = parent_request(slot_id)
        normal = successor.transformed_request_bytes(source)
        pilot = successor.transformed_request_bytes(source, pilot=True)
        assert pilot != normal
        value = json.loads(pilot)
        visible = value.get("input")
        if visible is None:
            visible = value["messages"][0]["content"]
        assert visible.startswith(successor.PILOT_MARKER)


def test_successor_execution_ids_are_versioned_and_deterministic() -> None:
    parent_id = "fg1-exec-example"
    first = successor.successor_execution_id(parent_id)
    assert first == successor.successor_execution_id(parent_id)
    assert first.startswith("fg2-exec-")
    assert first != parent_id


def test_frozen_fg1_invalid_batch_remains_terminal() -> None:
    run_dir = FORWARD_ROOT / "remote_execution_2026-07-23"
    rows = [
        successor.load_json(path)
        for path in (run_dir / "rows").glob("*.json")
    ]
    assert len(rows) == 72
    assert {row["provider_finish_reason"] for row in rows} == {"length"}
    assert {row["provider_reported_output_tokens"] for row in rows} == {1024}
    assert {row["terminal_outcome"] for row in rows} == {
        "malformed_or_no_submission"
    }


def test_frozen_successor_bundle_verifies_when_present() -> None:
    if successor.DEFAULT_SUCCESSOR.exists():
        result = successor.verify_successor(
            successor.DEFAULT_PARENT,
            successor.DEFAULT_SUCCESSOR,
        )
        assert result["status"] == "passed"
        assert result["registered_rows"] == 1296
        assert result["pilot_rows"] == 6
