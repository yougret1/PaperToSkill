from __future__ import annotations

import json
import sys
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

from verify_forward_preregistration import audit  # noqa: E402


def test_forward_preregistration_gate_passes() -> None:
    result = audit()
    assert result["status"] == "passed"
    assert result["selected_papers"] == 12
    assert result["paper_task_clusters"] == 24
    assert result["primary_provider_conversations"] == 432
    assert result["required_provider_conversation_cap"] == 840


def test_domain_balance_and_model_slots_are_frozen() -> None:
    result = audit()
    assert result["domains"] == {
        "agent_tool_use": 3,
        "data_analysis": 3,
        "nlp": 3,
        "software_engineering": 3,
    }
    assert result["required_closed_model_slots"] == 4
    assert result["optional_closed_model_slots"] == 2
    assert result["open_seed_anchor"] == "Qwen/Qwen2.5-Coder-7B-Instruct"


def test_controls_are_not_misreported_as_calibrated_confusion_matrix() -> None:
    plan = json.loads(
        (
            FORWARD_ROOT
            / "preregistration"
            / "figure_statistical_plan.json"
        ).read_text(encoding="utf-8")
    )
    conditional = plan["conditional_outputs"][0]
    assert conditional["name"] == "control_confusion_matrix"
    assert conditional["default"] == "do_not_render"
    assert conditional["current_independent_controls_per_class"] == 4


def test_closed_model_seed_is_not_overclaimed() -> None:
    registry = json.loads(
        (
            FORWARD_ROOT
            / "preregistration"
            / "model_ablation_registry.json"
        ).read_text(encoding="utf-8")
    )
    closed = [
        slot
        for slot in registry["model_slots"]
        if slot["provider_family"] not in {"local_open_weights"}
    ]
    assert all(slot["seed_support"] == "not_relied_upon" for slot in closed)
    open_anchor = next(
        slot for slot in registry["model_slots"] if slot["slot_id"] == "open_seed_anchor"
    )
    assert open_anchor["seed_support"] == "required"
    assert open_anchor["decoding"]["do_sample"] is False
