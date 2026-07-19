from __future__ import annotations

import copy

from analyze_confirmation_v3_interleaved_calibration import analyze_blocks


def condition(success: bool, score: float) -> dict[str, object]:
    return {
        "success": success,
        "task_score": score,
        "hard_constraints_passed": True,
    }


def block(
    label: str,
    replicate_id: str,
    *,
    baseline: bool,
    full: bool,
    selected: bool,
) -> dict[str, object]:
    return {
        "label": label,
        "control": "identity" if label == "identity" else "planted",
        "replicate_id": replicate_id,
        "integrity_passed": True,
        "integrity_violations": [],
        "joint_substitution_event": bool(not baseline and full and selected),
        "condition_results": {
            "B": condition(baseline, float(baseline)),
            "F": condition(full, float(full)),
            "S": condition(selected, float(selected)),
        },
    }


def preregistration() -> dict:
    return {
        "registered_block_count": 5,
        "primary_event": "candidate_centered_substitution_event",
        "families": {
            "identity": {
                "replicate_count": 1,
                "required_candidate_centered_events": None,
            },
            "positive": {
                "replicate_count": 2,
                "required_candidate_centered_events": 2,
            },
            "negative": {
                "replicate_count": 2,
                "required_candidate_centered_events": (
                    "strictly_less_than_registered_blocks"
                ),
            },
        },
    }


def audited_blocks() -> list[dict]:
    return [
        block("identity", "i001", baseline=False, full=True, selected=True),
        block("positive", "p001", baseline=False, full=False, selected=True),
        block("positive", "p002", baseline=False, full=True, selected=True),
        block("negative", "n001", baseline=False, full=True, selected=False),
        block("negative", "n002", baseline=False, full=True, selected=True),
    ]


def test_candidate_centered_rule_passes_separating_controls():
    result = analyze_blocks(preregistration(), audited_blocks())

    assert result["labels"]["positive"]["primary_event_count"] == 2
    assert result["labels"]["positive"]["reference_failure_only_count"] == 1
    assert result["labels"]["negative"]["primary_event_count"] == 1
    assert result["calibration_decision"]["instrument_passed"] is True
    assert result["calibration_decision"]["preregistered"] is True
    assert result["scope_guards"]["population_guarantee"] is False


def test_negative_control_all_events_fails_specificity_requirement():
    rows = audited_blocks()
    rows[3] = block(
        "negative", "n001", baseline=False, full=True, selected=True
    )

    result = analyze_blocks(preregistration(), rows)

    assert result["labels"]["negative"]["primary_event_count"] == 2
    assert result["calibration_decision"]["negative_requirement_passed"] is False
    assert result["calibration_decision"]["instrument_passed"] is False


def test_integrity_failure_prevents_instrument_pass():
    rows = copy.deepcopy(audited_blocks())
    rows[0]["integrity_passed"] = False
    rows[0]["integrity_violations"] = ["registered_bundle_integrity_failure"]

    result = analyze_blocks(preregistration(), rows)

    assert result["full_integrity_passed"] is False
    assert result["calibration_decision"]["instrument_passed"] is False
