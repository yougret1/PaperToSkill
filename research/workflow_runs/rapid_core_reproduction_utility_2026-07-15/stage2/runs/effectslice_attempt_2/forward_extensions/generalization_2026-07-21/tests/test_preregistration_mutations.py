from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Callable

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

from preregistration_verifier_v3 import VerificationError, audit  # noqa: E402
from materialization_verifier_v2 import (  # noqa: E402
    MaterializationError,
    build_validation_fixture_rows,
    preregistrations,
    validate_schedule_rows,
)


JsonMutator = Callable[[dict[str, object]], None]
RowMutator = Callable[[list[dict[str, object]]], None]


def mutate_json(
    tmp_path: Path,
    filename: str,
    mutator: JsonMutator,
) -> Path:
    root = tmp_path / "preregistration"
    shutil.copytree(FORWARD_ROOT / "preregistration", root)
    path = root / filename
    value = json.loads(path.read_text(encoding="utf-8"))
    mutator(value)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return root


def expect_json_rejected(
    tmp_path: Path,
    filename: str,
    mutator: JsonMutator,
) -> None:
    root = mutate_json(tmp_path, filename, mutator)
    with pytest.raises(VerificationError):
        audit(root, verify_bundle=False)


def expect_schedule_rejected(mutator: RowMutator) -> None:
    rows = build_validation_fixture_rows()
    _, registry, models, contract = preregistrations()
    mutator(rows)
    with pytest.raises(MaterializationError):
        validate_schedule_rows(rows, registry, models, contract)


def test_duplicate_primary_order_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        schedule = value["schedule"]
        schedule["all_orders"][1] = schedule["all_orders"][0]

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_reducer_semantic_label_visibility_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        reducer = value["candidate_construction"]["primary_reducer"]
        reducer["visible_fields"].append("hard_contract_label")

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


@pytest.mark.parametrize("field", ["target_token_retention", "tie_break_order"])
def test_reducer_selection_mutation_is_rejected(tmp_path: Path, field: str) -> None:
    def mutate(value: dict[str, object]) -> None:
        reducer = value["candidate_construction"]["primary_reducer"]
        reducer[field] = 0.61 if field == "target_token_retention" else list(reversed(reducer[field]))

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_primary_model_cross_file_mismatch_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["primary_design"]["primary_model_slot_id"] = "gpt_5_5"

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_pair_state_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["scoring"]["two_arm_pair_rule"]["states"][0] = "Admit"

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_sanity_state_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["scoring"]["control_sanity_rules"]["states"][1] = "Reject"

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_terminal_truth_table_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        table = value["transport_and_failure_policy"]["terminal_truth_table"]
        table["hard_contract_failure"]["condition_success"] = True

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_terminal_private_score_rule_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        table = value["transport_and_failure_policy"]["terminal_truth_table"]
        table["malformed_or_no_submission"]["private_score_rule"] = "null"

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_cost_endpoint_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        del value["analysis_contract"]["cost_measurement"][
            "latency_endpoints_ms"
        ]["retry_overhead_ms"]

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_lobo_invalid_rule_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["analysis_contract"]["leave_one_block_out"] = (
            "Delete invalid blocks and replace the primary decision."
        )

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_seed_golden_vector_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        anchor = next(
            slot for slot in value["model_slots"] if slot["slot_id"] == "open_seed_anchor"
        )
        anchor["seed_derivation"]["golden_test_vectors"][0]["uint32_seed"] += 1

    expect_json_rejected(tmp_path, "model_ablation_registry.json", mutate)


def test_model_output_cap_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        slot = next(
            row for row in value["model_slots"] if row["slot_id"] == "gpt_5_5"
        )
        slot["decoding"]["normalized_max_output_tokens"] = 2048

    expect_json_rejected(tmp_path, "model_ablation_registry.json", mutate)


def test_estimator_formula_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["analysis_contract"]["registered_estimator"]["paper_identified_bounds"] = (
            "Pool both tasks."
        )

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_canonical_payload_composition_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["model_visible_payload_contract"]["canonical_payload_composition"][
            "field_order"
        ].reverse()

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_result_canonicalization_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["result_canonicalization_contract"]["required_result_row_fields"].remove(
            "raw_response_sha256"
        )

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_termination_compatibility_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["result_canonicalization_contract"]["termination_compatibility"][
            "operational_success"
        ] = ["not_dispatched"]

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_slot_response_pointer_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["result_canonicalization_contract"]["slot_response_contracts"][0][
            "canonical_output_selector"
        ]["pointer"] = "/choices/1/message/content"

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_provider_native_output_pointer_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["request_template_manifest"][
            "output_limit_json_pointer_by_slot"
        ]["gpt_5_5"] = "/max_tokens"

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_source_audit_independence_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["implementation_source_audit_manifest"][
            "auditor_must_differ_from_builder"
        ] = False

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_registered_result_schema_type_weakening_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["result_canonicalization_contract"]["result_row_json_schema"][
            "properties"
        ]["private_score"] = {}

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_alternate_audit_schema_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["candidate_manifest"]["alternate_reducer_audit_schema"][
            "selection_key"
        ].reverse()

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_overlap_source_registry_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["parent_overlap_audit"]["source_registry"]["execution_id"][
            "confirmation_v4"
        ]["glob"] = "**/*.json"

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_open_anchor_determinism_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["open_anchor_runtime_manifest"][
            "determinism_required"
        ]["cudnn_benchmark"] = True

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_open_anchor_termination_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["open_anchor_runtime_manifest"][
            "generation_config"
        ]["max_new_tokens"] = 2048

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_open_anchor_inventory_contract_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["open_anchor_runtime_manifest"][
            "file_inventory_contract"
        ]["shard_index_must_exactly_cover_weight_files"] = False

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_open_anchor_preflight_schema_weakening_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["open_anchor_runtime_manifest"][
            "preflight_result_schema"
        ]["additionalProperties"] = True

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_golden_execution_protocol_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["result_canonicalization_manifest"][
            "verifier_executes_golden_suite"
        ] = False

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_empty_replacement_contract_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["global_artifact_schemas"]["replacement_amendment_manifest"][
            "amendments_must_be_empty"
        ] = False

    expect_json_rejected(tmp_path, "materialization_contract.json", mutate)


def test_replacement_reason_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["sampling_frame"]["replacement_policy"]["reason_codes"].append(
            "low_model_score"
        )

    expect_json_rejected(tmp_path, "paper_registry.json", mutate)


def test_metadata_evidence_digest_mutation_is_rejected(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        value["entries"][0]["sha256"] = "0" * 64

    expect_json_rejected(tmp_path, "metadata_evidence_manifest.json", mutate)


def test_missing_required_key_raises_verification_error(tmp_path: Path) -> None:
    def mutate(value: dict[str, object]) -> None:
        del value["primary_design"]

    expect_json_rejected(tmp_path, "experiment_plan.json", mutate)


def test_missing_schedule_row_is_rejected() -> None:
    expect_schedule_rejected(lambda rows: rows.pop())


def test_duplicate_schedule_row_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        rows[-1] = copy.deepcopy(rows[0])

    expect_schedule_rejected(mutate)


def test_wrong_schedule_model_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        rows[0]["model_slot_id"] = "gpt_5_5"

    expect_schedule_rejected(mutate)


def test_wrong_schedule_registry_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        rows[0]["registry_id"] = "B"

    expect_schedule_rejected(mutate)


def test_wrong_global_schedule_order_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        rows[0], rows[1] = rows[1], rows[0]
        rows[0]["global_sequence_index"] = 1
        rows[1]["global_sequence_index"] = 2

    expect_schedule_rejected(mutate)


def test_pair_fixture_hash_mismatch_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        rows[1]["fixture_payload_sha256"] = "1" * 64

    expect_schedule_rejected(mutate)


def test_f_i_payload_mismatch_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        row = next(
            item
            for item in rows
            if item["execution_family"] == "required_closed_models"
            and item["condition"] == "I"
        )
        row["canonical_model_visible_payload_sha256"] = "2" * 64

    expect_schedule_rejected(mutate)


def test_cross_model_fixture_mismatch_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        for row in rows:
            if (
                row["execution_family"] == "required_closed_models"
                and row["task_id"] == "NLP-LLM-01"
                and row["model_slot_id"] == "gpt_5_5"
                and row["block_id"] == 1
            ):
                row["fixture_payload_sha256"] = "4" * 64

    expect_schedule_rejected(mutate)


def test_cross_model_canonical_payload_mismatch_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        for row in rows:
            if (
                row["execution_family"] == "required_closed_models"
                and row["task_id"] == "NLP-LLM-01"
                and row["model_slot_id"] == "gpt_5_5"
                and row["block_id"] == 1
            ):
                row["canonical_model_visible_payload_sha256"] = "5" * 64

    expect_schedule_rejected(mutate)


def test_f_i_seeds_changed_together_are_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        for row in rows:
            if (
                row["execution_family"] == "open_anchor"
                and row["task_id"] == "NLP-LLM-01"
                and row["block_id"] == 1
                and row["condition"] in {"F", "I"}
            ):
                row["derived_seed"] = 0

    expect_schedule_rejected(mutate)


def test_nonempty_baseline_artifact_is_rejected() -> None:
    def mutate(rows: list[dict[str, object]]) -> None:
        row = next(item for item in rows if item["condition"] == "B")
        row["candidate_artifact_sha256"] = "3" * 64

    expect_schedule_rejected(mutate)
