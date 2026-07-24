from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analyze_fg5_output_contract as analysis  # noqa: E402


def test_replacements_prefer_full_artifacts_and_do_not_repeat_ids() -> None:
    inconclusive = [{"task_id": "T1"}, {"task_id": "T2"}]
    all_rows = [
        {"task_id": "T1", "execution_id": "old", "condition": "F", "model_slot_id": "m"},
        {"task_id": "T1", "execution_id": "s1", "condition": "S", "model_slot_id": "m"},
        {"task_id": "T1", "execution_id": "f1", "condition": "F", "model_slot_id": "z"},
        {"task_id": "T2", "execution_id": "b2", "condition": "B", "model_slot_id": "a"},
        {"task_id": "T2", "execution_id": "s2", "condition": "S", "model_slot_id": "z"},
    ]
    replacements = analysis.choose_replacements(inconclusive, {"old"}, all_rows)
    assert [row["execution_id"] for row in replacements] == ["f1", "s2"]


def test_replacements_allow_exhausted_task_candidates() -> None:
    replacements = analysis.choose_replacements(
        [{"task_id": "T1"}],
        {"only"},
        [
            {
                "task_id": "T1",
                "execution_id": "only",
                "condition": "F",
                "model_slot_id": "m",
            }
        ],
    )
    assert replacements == []


def test_audit_output_shapes_checks_inner_output_values() -> None:
    scoring = {
        "outputs": [
            {"case_id": "a", "output": {"value": 1}},
            {"case_id": "b", "output": {"wrong": 2}},
        ]
    }
    shape = {
        "type": "object",
        "required": ["value"],
        "properties": {"value": {"type": "integer"}},
        "additionalProperties": False,
    }
    count, mismatches, first = analysis.audit_output_shapes(scoring, shape)
    assert count == 2
    assert mismatches == 1
    assert first is not None and "missing required key" in first


def test_final_report_keeps_candidate_errors_explicit() -> None:
    value = {
        "selected_rows": 684,
        "selected_tasks": 24,
        "shape_evaluable_rows": 646,
        "output_values_checked": 646 * 64,
        "shape_mismatch_output_count": 0,
        "output_contract_mismatch_rows": 0,
        "operational_success_rows": 224,
        "technical_classifications": {
            "experimental_outcome_not_technical_error": 424,
            "integrity_or_digest": 9,
            "operational_success": 224,
            "response_format": 27,
        },
        "records": [
            {
                "fg5_execution_id": "fg5",
                "fg3_execution_id": "fg3",
                "task_id": "T",
                "condition": "F",
                "model_slot_id": "m",
                "worker_error_count": 64,
                "worker_status": "completed",
                "worker_output_count": 0,
                "technical_classification": "experimental_outcome_not_technical_error",
            }
        ],
    }
    report = analysis.final_report(
        value, analysis_sha256="a" * 64, selection_sha256="b" * 64
    )
    assert report["class_validation_passed"] is True
    assert report["shape_conforming_output_values"] == 646 * 64
    assert len(report["candidate_worker_error_rows"]) == 1
    assert len(report["non_evaluable_experimental_rows"]) == 1
