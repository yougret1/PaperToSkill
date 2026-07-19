from __future__ import annotations

import copy

import pytest

from build_confirmation_v3_calibration_analysis import (
    CalibrationAnalysisError,
    analyze_calibration,
)


def condition(success: bool, score: float) -> dict[str, object]:
    return {
        "success": success,
        "task_score": score,
        "hard_constraints_passed": True,
    }


def v3_block(
    control: str,
    replicate_id: str,
    *,
    baseline: bool,
    full: bool,
    selected: bool,
) -> dict[str, object]:
    return {
        "control": control,
        "replicate_id": replicate_id,
        "integrity_passed": True,
        "joint_substitution_event": bool(not baseline and full and selected),
        "condition_results": {
            "B": condition(baseline, float(baseline)),
            "F": condition(full, float(full)),
            "S": condition(selected, float(selected)),
        },
    }


def historical_replicate(
    replicate_id: str, *, baseline: bool, full: bool, selected: bool
) -> dict[str, object]:
    return {
        "replicate_id": replicate_id,
        "classification": "audited",
        "execution_status": "completed",
        "hard_constraints_passed": True,
        "integrity_violations": [],
        "conditions": {
            "B": condition(baseline, float(baseline)),
            "F": condition(full, float(full)),
            "S": condition(selected, float(selected)),
        },
    }


def inputs() -> tuple[dict, dict, dict, dict, dict]:
    blocks = [
        v3_block(
            "identity", "r001", baseline=False, full=True, selected=False
        ),
        v3_block(
            "identity", "r002", baseline=False, full=True, selected=True
        ),
        v3_block(
            "planted", "r001", baseline=False, full=False, selected=True
        ),
        v3_block(
            "planted", "r002", baseline=False, full=True, selected=True
        ),
    ]
    analysis = {
        "schedule_integrity_passed": True,
        "registered_schedule_length": 4,
        "strict_subset_admitted": False,
        "controls": {
            "identity": {
                "joint_event_count": 1,
                "registered_block_count": 2,
                "full_integrity_passed": True,
                "decision": "descriptive_only",
            },
            "planted": {
                "joint_event_count": 1,
                "registered_block_count": 2,
                "full_integrity_passed": True,
                "decision": "reject",
            },
        },
        "blocks": blocks,
    }
    historical = {
        "task_key": "toolformer_filter",
        "selected_candidate_id": "prefix_01",
        "integrity_passed": True,
        "schedule_complete": True,
        "replicate_denominator": 2,
        "replicates": [
            historical_replicate(
                "r001", baseline=False, full=True, selected=False
            ),
            historical_replicate(
                "r002", baseline=False, full=True, selected=True
            ),
        ],
    }
    progress = {
        "registered_schedule_length": 4,
        "records": [
            {"control": "identity", "replicate_id": "r001"},
            {"control": "identity", "replicate_id": "r002"},
            {"control": "planted", "replicate_id": "r001"},
            {"control": "planted", "replicate_id": "r002"},
        ],
    }
    identity = {
        "control": "identity",
        "maximum_shortfall": 0.05,
        "bindings": {
            "selected_artifact": {"sha256": "a" * 64},
        },
    }
    planted = {
        "control": "planted",
        "maximum_shortfall": 0.05,
        "bindings": {
            "selected_artifact": {"sha256": "a" * 64},
        },
    }
    return analysis, historical, progress, identity, planted


def test_candidate_centered_event_exposes_reference_only_failure():
    analysis, historical, progress, identity, planted = inputs()

    result = analyze_calibration(
        analysis=analysis,
        historical_summary=historical,
        progress=progress,
        identity_family=identity,
        planted_family=planted,
    )

    assert result["preregistered_primary"]["planted"]["events"] == 1
    assert result["exploratory_candidate_centered"]["planted"]["events"] == 2
    assert (
        result["exploratory_candidate_centered"]["planted"][
            "reference_failure_only_count"
        ]
        == 1
    )
    assert result["exploratory_candidate_centered"]["identity"]["events"] == 1
    assert (
        result["exploratory_candidate_centered"]["historical_negative"][
            "events"
        ]
        == 1
    )
    assert result["calibration_verdict"]["candidate_centered_rule"] == (
        "posthoc_not_admissible_without_fresh_confirmation"
    )
    assert result["schedule_diagnostics"]["control_interleaved"] is False
    assert result["schedule_diagnostics"]["shared_selected_artifact"] is True


def test_rejects_failed_v3_block_integrity():
    analysis, historical, progress, identity, planted = inputs()
    broken = copy.deepcopy(analysis)
    broken["blocks"][0]["integrity_passed"] = False

    with pytest.raises(CalibrationAnalysisError, match="integrity"):
        analyze_calibration(
            analysis=broken,
            historical_summary=historical,
            progress=progress,
            identity_family=identity,
            planted_family=planted,
        )


def test_rejects_unbound_control_artifacts():
    analysis, historical, progress, identity, planted = inputs()
    planted["bindings"]["selected_artifact"]["sha256"] = "b" * 64

    with pytest.raises(CalibrationAnalysisError, match="selected artifact"):
        analyze_calibration(
            analysis=analysis,
            historical_summary=historical,
            progress=progress,
            identity_family=identity,
            planted_family=planted,
        )
