from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import classify_fg3_error_rows as classifier  # noqa: E402


ROW = {
    "execution_id": "fg3-exec-test",
    "task_id": "NLP-LLM-01",
    "condition": "F",
    "candidate_id": "F",
    "model_slot_id": "deepseek_primary",
    "registry_id": "A",
}
SHAPE = {
    "type": "object",
    "properties": {"total": {"type": "integer"}},
    "required": ["total"],
    "additionalProperties": False,
}


def test_classifies_payload_signature_before_other_hard_failures() -> None:
    scoring = {
        "errors": [
            {"error_type": "KeyError", "message": "'payload'"},
            {"error_type": "KeyError", "message": "'payload'"},
        ],
        "outputs": [],
    }
    value = classifier.classify_row(
        ROW, {"terminal_outcome": "hard_contract_failure"}, scoring, SHAPE
    )
    assert value["technical_classification"] == "payload_input_interface"
    assert value["worker_error_count"] == 2


def test_classifies_shape_mismatch_without_using_expected_values() -> None:
    scoring = {
        "errors": [],
        "outputs": [
            {"case_id": "c1", "output": {"wrong": 1}},
            {"case_id": "c2", "output": {"total": 2}},
        ],
    }
    value = classifier.classify_row(
        ROW, {"terminal_outcome": "hard_contract_failure"}, scoring, SHAPE
    )
    assert value["technical_classification"] == "exact_output_contract"
    assert value["shape_mismatch_output_count"] == 1
    assert value["first_shape_violation"].startswith("$")


def test_shape_conformant_score_failure_is_not_labeled_technical() -> None:
    scoring = {
        "errors": [],
        "outputs": [
            {"case_id": "c1", "output": {"total": 1}},
            {"case_id": "c2", "output": {"total": 2}},
        ],
    }
    value = classifier.classify_row(
        ROW, {"terminal_outcome": "hard_contract_failure"}, scoring, SHAPE
    )
    assert value["technical_classification"] == "experimental_outcome_not_technical_error"
    assert value["shape_mismatch_output_count"] == 0


def test_terminal_classes_are_preserved_without_scoring_evidence() -> None:
    expected = {
        "malformed_or_no_submission": "response_format",
        "integrity_or_digest_failure": "integrity_or_digest",
        "provider_or_model_unavailable": "provider_availability",
        "operational_success": "operational_success",
    }
    for outcome, label in expected.items():
        value = classifier.classify_row(ROW, {"terminal_outcome": outcome}, None, SHAPE)
        assert value["technical_classification"] == label
