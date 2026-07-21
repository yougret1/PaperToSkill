from __future__ import annotations

import json
import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_summaries_v3 import build_summaries  # noqa: E402
from test_build_stage2_summaries_v2 import task_summary  # noqa: E402


def calibration_analysis() -> dict:
    blocks = []
    order = 0
    for index in range(18):
        order += 1
        event = index != 14
        blocks.append(
            {
                "label": "positive",
                "replicate_id": f"p{index + 1:03d}",
                "global_order_index": order,
                "stratum": index + 1,
                "registered_status": "completed",
                "integrity_passed": True,
                "integrity_violations": [],
                "joint_substitution_event": event,
                "condition_results": {
                    "B": {
                        "success": False,
                        "hard_constraints_passed": True,
                        "task_score": 0.0,
                    },
                    "F": {
                        "success": True,
                        "hard_constraints_passed": True,
                        "task_score": 1.0,
                    },
                    "S": {
                        "success": event,
                        "hard_constraints_passed": True,
                        "task_score": 1.0 if event else 0.0,
                    },
                },
            }
        )
    for index in range(18):
        order += 1
        blocks.append(
            {
                "label": "negative",
                "replicate_id": f"n{index + 1:03d}",
                "global_order_index": order,
                "stratum": index + 1,
                "registered_status": "completed",
                "integrity_passed": True,
                "integrity_violations": [],
                "joint_substitution_event": False,
                "condition_results": {},
            }
        )
    for index in range(6):
        order += 1
        blocks.append(
            {
                "label": "identity",
                "replicate_id": f"i{index + 1:03d}",
                "global_order_index": order,
                "stratum": 1 + 3 * index,
                "registered_status": "completed",
                "integrity_passed": True,
                "integrity_violations": [],
                "joint_substitution_event": index < 5,
                "condition_results": {},
            }
        )
    return {
        "schema_version": "effectslice-v3-interleaved-calibration-analysis.v1",
        "analysis_role": "fresh_registered_calibration_replication",
        "primary_event": "candidate_centered_substitution_event",
        "decision_basis": "finite_registered_schedule",
        "registered_schedule_length": 42,
        "full_integrity_passed": True,
        "independence_verified": False,
        "provider_response_id_count": 100,
        "status_counts": {
            "completed": 42,
            "failed": 0,
            "pending": 0,
            "preserved": 0,
            "running": 0,
        },
        "registration_audit": {
            "valid": True,
            "anchor_verified": True,
            "control_interleaved": True,
            "provider_execution_started": True,
            "registered_block_count": 42,
            "registered_condition_run_count": 126,
            "preregistration_sha256": "a" * 64,
        },
        "calibration_decision": {
            "instrument_passed": False,
            "positive_requirement_passed": False,
            "negative_requirement_passed": True,
            "preregistered": True,
        },
        "labels": {
            "positive": {
                "primary_event_count": 17,
                "registered_blocks": 18,
                "integrity_passed_blocks": 18,
                "selected_success_count": 17,
                "legacy_joint_event_count": 17,
                "reference_failure_only_count": 0,
                "required_candidate_centered_events": 18,
            },
            "negative": {
                "primary_event_count": 0,
                "registered_blocks": 18,
                "integrity_passed_blocks": 18,
                "selected_success_count": 0,
                "legacy_joint_event_count": 0,
                "reference_failure_only_count": 0,
                "required_candidate_centered_events": (
                    "strictly_less_than_registered_blocks"
                ),
            },
            "identity": {
                "primary_event_count": 5,
                "registered_blocks": 6,
                "integrity_passed_blocks": 6,
                "selected_success_count": 5,
                "legacy_joint_event_count": 5,
                "reference_failure_only_count": 0,
                "required_candidate_centered_events": None,
            },
        },
        "blocks": blocks,
        "scope_guards": {
            "iid_inference_used": False,
            "population_guarantee": False,
            "cross_paper_claim_ready": False,
            "human_benefit_claim_ready": False,
        },
    }


def _write_task_summaries(root: Path) -> list[Path]:
    rows = [
        task_summary(
            "snap_mfse",
            baseline_successes=0,
            full_successes=13,
            slice_successes=5,
            full_benefit=13,
            preservation=3,
            slice_benefit=5,
            admitted=False,
        ),
        task_summary(
            "toolformer_filter",
            baseline_successes=0,
            full_successes=18,
            slice_successes=6,
            full_benefit=18,
            preservation=6,
            slice_benefit=6,
            admitted=False,
        ),
    ]
    paths = []
    for row in rows:
        path = root / f"{row['task_key']}.json"
        path.write_text(json.dumps(row), encoding="utf-8")
        paths.append(path)
    return paths


def test_builds_v3_summaries_with_failed_strict_calibration(tmp_path):
    task_paths = _write_task_summaries(tmp_path)
    calibration_path = tmp_path / "calibration.json"
    calibration_path.write_text(
        json.dumps(calibration_analysis()), encoding="utf-8"
    )

    paths = build_summaries(task_paths, calibration_path, tmp_path / "logs")

    baseline = json.loads(Path(paths["baseline"]).read_text(encoding="utf-8"))
    research = json.loads(Path(paths["research"]).read_text(encoding="utf-8"))
    ablation = json.loads(Path(paths["ablation"]).read_text(encoding="utf-8"))
    calibration = research["calibration_replication"]

    assert baseline["schema_version"] == "effectslice-stage2-baseline-summary.v3"
    assert research["schema_version"] == "effectslice-stage2-research-summary.v3"
    assert ablation["schema_version"] == "effectslice-stage2-ablation-summary.v3"
    assert research["metric"] == {
        "name": "task_local_admissions",
        "value": 0,
        "direction": "higher_is_better",
        "descriptive_denominator": 2,
    }
    assert calibration["instrument_passed"] is False
    assert calibration["positive_requirement_passed"] is False
    assert calibration["negative_requirement_passed"] is True
    assert calibration["registered_condition_run_count"] == 126
    assert [row["primary_event_count"] for row in calibration["label_rows"]] == [
        17,
        0,
        5,
    ]
    assert calibration["false_negative_blocks"][0]["replicate_id"] == "p015"
    assert calibration["false_negative_blocks"][0]["condition_results"]["S"][
        "success"
    ] is False
    assert research["diagnostic_event_admission_ready"] is False
    assert research["cross_paper_claim_ready"] is False
    assert research["human_benefit_claim_ready"] is False
    assert ablation["calibration_replication"] == calibration
    assert len(research["exp_results_data_files"]) == 3


def test_rejects_incomplete_calibration(tmp_path):
    task_paths = _write_task_summaries(tmp_path)
    payload = calibration_analysis()
    payload["status_counts"]["completed"] = 41
    calibration_path = tmp_path / "calibration.json"
    calibration_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        build_summaries(task_paths, calibration_path, tmp_path / "logs")
    except ValueError as error:
        assert "incomplete" in str(error)
    else:
        raise AssertionError("incomplete calibration should be rejected")
