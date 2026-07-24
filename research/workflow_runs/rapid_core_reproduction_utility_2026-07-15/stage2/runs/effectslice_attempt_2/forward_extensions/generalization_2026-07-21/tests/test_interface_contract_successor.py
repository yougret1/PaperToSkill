from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import interface_contract_successor as successor  # noqa: E402


FG3_ROOT = successor.fg1.windows_extended_path(
    ROOT / "format_conformance_successor_2026-07-23"
)


def _visible(value: dict[str, object]) -> str:
    if isinstance(value.get("input"), str):
        return str(value["input"])
    messages = value["messages"]
    assert isinstance(messages, list) and len(messages) == 1
    return str(messages[0]["content"])


def test_transformation_adds_only_explicit_inner_payload_contract() -> None:
    source_path = next((FG3_ROOT / "requests").glob("*.json"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    transformed = json.loads(successor.transformed_request_bytes(source_path.read_bytes()))
    before = _visible(source)
    after = _visible(transformed)
    assert after == successor.INTERFACE_INSTRUCTION + before
    assert transformed["model"] == source["model"]
    assert transformed[successor.fg2.output_budget_key(transformed)] == successor.fg2.NEW_OUTPUT_BUDGET


def test_pilot_transformation_preserves_fg3_pilot_and_format_contract() -> None:
    source_path = next((FG3_ROOT / "pilot" / "requests").glob("*.json"))
    transformed = json.loads(successor.transformed_request_bytes(source_path.read_bytes(), pilot=True))
    visible = _visible(transformed)
    assert visible.startswith(
        successor.PILOT_MARKER
        + successor.INTERFACE_INSTRUCTION
        + successor.fg3.PILOT_MARKER
        + successor.fg3.FORMAT_INSTRUCTION
    )


def test_execution_ids_are_versioned_and_deterministic() -> None:
    value = "fg3-exec-0123456789abcdef01234567"
    assert successor.execution_id(value) == successor.execution_id(value)
    assert successor.execution_id(value).startswith("fg4-exec-")
    assert successor.execution_id(value) != value
