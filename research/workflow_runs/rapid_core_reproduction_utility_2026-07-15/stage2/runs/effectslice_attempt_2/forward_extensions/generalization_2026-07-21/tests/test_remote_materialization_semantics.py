from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import materialization_verifier_v3 as verifier  # noqa: E402


def registrations() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    _, papers, models, contract = verifier.preregistrations()
    return papers, models, contract


def test_remote_validation_fixture_has_registered_1296_rows() -> None:
    papers, models, contract = registrations()
    rows = verifier.build_validation_fixture_rows()
    result = verifier.validate_schedule_rows(rows, papers, models, contract)
    assert result == {
        "rows": 1296,
        "family_counts": {
            "primary": 432,
            "controls": 144,
            "structural_ladder": 144,
            "alternate_reducers": 96,
            "required_closed_models": 384,
            "remote_anchor": 96,
        },
    }


def test_every_schedule_row_is_remote_and_luna_owns_remote_anchor() -> None:
    rows = verifier.build_validation_fixture_rows()
    assert len(rows) == 1296
    assert Counter(row["execution_family"] for row in rows) == verifier.EXPECTED_FAMILY_COUNTS
    anchor_rows = [row for row in rows if row["execution_family"] == "remote_anchor"]
    assert len(anchor_rows) == 96
    assert {row["model_slot_id"] for row in anchor_rows} == {"gpt_5_6_luna"}


def test_remote_anchor_f_and_i_are_byte_identical_requests() -> None:
    rows = verifier.build_validation_fixture_rows()
    grouped: dict[tuple[str, int], dict[str, dict[str, object]]] = {}
    for row in rows:
        if row["execution_family"] != "remote_anchor":
            continue
        key = (str(row["task_id"]), int(row["block_id"]))
        grouped.setdefault(key, {})[str(row["condition"])] = row
    assert len(grouped) == 24
    for conditions in grouped.values():
        assert conditions["F"]["serialized_wire_request_sha256"] == conditions["I"][
            "serialized_wire_request_sha256"
        ]
        assert conditions["F"]["derived_seed"] == conditions["I"]["derived_seed"]


def test_remote_anchor_model_mutation_is_rejected() -> None:
    papers, models, contract = registrations()
    rows = copy.deepcopy(verifier.build_validation_fixture_rows())
    row = next(item for item in rows if item["execution_family"] == "remote_anchor")
    row["model_slot_id"] = "claude_opus_4_6"
    with pytest.raises(verifier.MaterializationError, match="global row order"):
        verifier.validate_schedule_rows(rows, papers, models, contract)


def test_schedule_row_deletion_is_rejected() -> None:
    papers, models, contract = registrations()
    rows = verifier.build_validation_fixture_rows()[:-1]
    with pytest.raises(verifier.MaterializationError, match="1296 rows"):
        verifier.validate_schedule_rows(rows, papers, models, contract)


def test_remote_result_schema_has_no_generated_token_field() -> None:
    _, _, contract = registrations()
    result = contract["result_canonicalization_contract"]
    assert "generated_token_ids" not in result["required_result_row_fields"]
    assert "generated_token_ids" not in result["result_row_json_schema"]["properties"]
    assert result["result_row_json_schema"]["additionalProperties"] is False


def test_source_audit_has_only_remote_implementation_components() -> None:
    _, _, contract = registrations()
    schema = contract["global_artifact_schemas"]["implementation_source_audit_manifest"]
    assert schema["required_component_ids"] == [
        "result_canonicalizer",
        "analysis_implementation",
    ]


def test_v3_source_contains_no_local_model_branch() -> None:
    source = (FORWARD_ROOT / "materialization_verifier_v3.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "open_seed_anchor",
        "open_anchor_runtime_manifest",
        "global_local_anchor_schedule",
        "generated_token_ids",
    )
    assert not {value for value in forbidden if value in source}


def test_successor_contract_points_to_v3_wrapper() -> None:
    _, _, contract = registrations()
    assert contract["verifier"] == "verify_stage_2_3_remote_materialization.py"
    wrapper = FORWARD_ROOT / contract["verifier"]
    assert wrapper.is_file()
    assert "materialization_verifier_v3" in wrapper.read_text(encoding="utf-8")
