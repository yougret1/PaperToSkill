from __future__ import annotations

import json
import sys
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import format_conformance_successor as successor  # noqa: E402


def fg2_request(model_slot_id: str) -> tuple[dict[str, object], bytes]:
    root = successor.fg1.windows_extended_path(successor.DEFAULT_FG2)
    rows = successor.load_json(root / "global_remote_schedule.json")["rows"]
    row = next(item for item in rows if item["model_slot_id"] == model_slot_id)
    path = successor.fg2_request_path(root, row)
    return row, path.read_bytes()


def request_visible_text(value: dict[str, object]) -> str:
    if isinstance(value.get("input"), str):
        return value["input"]
    return value["messages"][0]["content"]


def test_format_transformation_only_prepends_uniform_instruction() -> None:
    for slot_id in successor.fg1.PROVIDER_SPECS:
        _, source = fg2_request(slot_id)
        before = json.loads(source)
        after = json.loads(successor.transformed_request_bytes(source))
        assert request_visible_text(after) == (
            successor.FORMAT_INSTRUCTION + request_visible_text(before)
        )
        if "input" in before:
            before["input"] = after["input"]
        else:
            before["messages"][0]["content"] = after["messages"][0]["content"]
        assert after == before


def test_format_pilot_is_marked_and_distinct() -> None:
    for slot_id in successor.fg1.PROVIDER_SPECS:
        _, source = fg2_request(slot_id)
        normal = successor.transformed_request_bytes(source)
        pilot = successor.transformed_request_bytes(source, pilot=True)
        assert pilot != normal
        visible = request_visible_text(json.loads(pilot))
        assert visible.startswith(
            successor.PILOT_MARKER + successor.FORMAT_INSTRUCTION
        )


def test_fg3_execution_ids_are_versioned_and_deterministic() -> None:
    parent_id = "fg2-exec-example"
    value = successor.execution_id(parent_id)
    assert value == successor.execution_id(parent_id)
    assert value.startswith("fg3-exec-")
    assert value != parent_id


def test_fg2_pilot_remains_unscored_and_invalid() -> None:
    summary = successor.load_json(
        FORWARD_ROOT / "remote_execution_v2_2026-07-23" / "pilot_summary.json"
    )
    assert summary["registered_experiment_rows_consumed"] == 0
    assert summary["all_slots_available"] is False
    assert summary["available_slot_count"] == 4


def test_frozen_fg3_bundle_verifies_when_present() -> None:
    if successor.DEFAULT_SUCCESSOR.exists():
        result = successor.verify_successor(
            successor.DEFAULT_PARENT,
            successor.DEFAULT_FG2,
            successor.DEFAULT_SUCCESSOR,
        )
        assert result["status"] == "passed"
        assert result["registered_rows"] == 1296
        assert result["pilot_rows"] == 6
