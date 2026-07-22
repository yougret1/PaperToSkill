from __future__ import annotations

import json
import sys
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

from analyze_sla_operating_characteristics import analyze  # noqa: E402
from verify_forward_preregistration import audit  # noqa: E402


def load(name: str) -> dict[str, object]:
    return json.loads(
        (FORWARD_ROOT / "preregistration" / name).read_text(encoding="utf-8")
    )


def test_forward_preregistration_gate_passes() -> None:
    result = audit()
    assert result["status"] == "passed"
    assert result["selected_papers"] == 12
    assert result["independent_papers"] == 12
    assert result["nested_task_decisions"] == 24
    assert result["primary_remote_conversations"] == 432
    assert result["required_remote_conversation_cap"] == 1200
    assert result["open_anchor_local_execution_cap"] == 96
    assert result["required_execution_cap"] == 1296
    assert result["optional_remote_conversation_cap"] == 192


def test_domain_balance_and_exact_candidate_mapping() -> None:
    result = audit()
    assert result["domains"] == {
        "agent_tool_use": 3,
        "data_analysis": 3,
        "nlp": 3,
        "software_engineering": 3,
    }
    registry = load("paper_registry.json")
    matrix = load("candidate_matrix.json")
    registered = {
        paper["paper_id"]: [task["task_id"] for task in paper["tasks"]]
        for paper in registry["papers"]
    }
    selected = {
        row["paper_id"]: row["task_ids"]
        for row in matrix["entries"]
        if row["status"] == "selected"
    }
    assert selected == registered


def test_secondary_experiments_use_fresh_pairs_and_exact_arithmetic() -> None:
    plan = load("experiment_plan.json")
    secondary = plan["secondary_experiments"]
    assert secondary["controls"]["remote_conversations"] == 144
    assert secondary["structural_restoration_ladder"]["remote_conversations"] == 144
    assert secondary["alternate_candidate_reducers"]["remote_conversations"] == 96
    assert secondary["model_robustness"]["required_remote_conversations"] == 384
    for key in (
        "controls",
        "structural_restoration_ladder",
        "alternate_candidate_reducers",
        "model_robustness",
    ):
        assert secondary[key]["reuse_primary_rows"] is False


def test_reducer_is_blind_and_ratio_bound() -> None:
    reducer = load("experiment_plan.json")["candidate_construction"]["primary_reducer"]
    assert reducer["id"] == "dag_ratio_60_v1"
    assert reducer["visible_fields"] == [
        "atom_id",
        "dependency_ids",
        "rendered_token_count",
    ]
    assert {"hard_contract_label", "guardrail_label", "scorer_interface_label"} <= set(
        reducer["forbidden_fields"]
    )
    assert reducer["target_token_retention"] == 0.60
    assert reducer["eligible_token_retention_interval"] == [0.45, 0.75]


def test_sla_operating_analysis_is_current() -> None:
    stored = load("sla_operating_characteristics.json")
    assert stored == analyze()
    assert stored["total_count_states"] == 65536
    assert stored["passing_count_states"] == 81
    assert stored["classification_counts"] == {
        "Admit": 81,
        "baseline-sensitive": 9984,
        "full-insufficient": 53248,
        "margin-shortfall": 351,
        "slice-insufficient": 1872,
    }


def test_statistics_do_not_promote_blocks_to_independent_units() -> None:
    figures = load("figure_statistical_plan.json")
    stats = figures["statistics"]
    assert stats["primary_unit"] == "paper"
    assert stats["independent_n"] == 12
    assert stats["valid_pair_reporting"] == "valid_pairs/registered_pairs"
    assert stats["invalid_partial_identification_bounds"] is True
    assert "per-task Clopper-Pearson interval" in stats["per_task_display"]["forbidden"]
    assert "six-block bootstrap interval" in stats["per_task_display"]["forbidden"]
    assert figures["conditional_outputs"][0]["default"] == "do_not_render"


def test_model_seed_claim_and_identity_pair_are_bounded() -> None:
    models = load("model_ablation_registry.json")
    required = [
        slot
        for slot in models["model_slots"]
        if slot["role"] == "required_closed_robustness"
    ]
    assert {slot["model_alias"] for slot in required} == {
        "gpt-5.5",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "claude-opus-4-7",
    }
    assert all(slot["remote_conversations"] == 96 for slot in required)
    assert all(
        slot["decoding"]["normalized_max_output_tokens"] == 1024
        for slot in required
    )
    assert all(
        slot["seed_support"] == "record_if_returned_not_relied_upon"
        for slot in required
    )
    anchor = next(
        slot for slot in models["model_slots"] if slot["slot_id"] == "open_seed_anchor"
    )
    assert anchor["local_executions"] == 96
    assert anchor["decoding"]["do_sample"] is False
    assert anchor["decoding"]["normalized_max_output_tokens"] == 1024
    assert anchor["seed_derivation"]["F_I_same_seed"] is True
    groups = anchor["seed_derivation"]["condition_seed_groups"]
    assert groups["F"] == groups["I"]


def test_materialization_contract_requires_independent_audit_and_hashes() -> None:
    contract = load("materialization_contract.json")
    audit_contract = contract["semantic_audit"]
    assert audit_contract["source_auditor_must_differ_from_candidate_builder"] is True
    assert len(audit_contract["required_identities"]) == 6
    assert contract["source_and_task_specificity"]["minimum_central_spans_per_task"] == 2
    assert contract["schedule_counts"] == {
        "required_remote_rows": 1200,
        "required_local_rows": 96,
        "required_total_rows": 1296,
        "optional_remote_template_rows": 192,
    }
    assert contract["hash_contract"]["post_anchor_mutation_forbidden"] is True
    source_audit = contract["global_artifact_schemas"][
        "implementation_source_audit_manifest"
    ]
    assert source_audit["auditor_must_differ_from_builder"] is True
    assert source_audit["required_component_ids"] == [
        "result_canonicalizer",
        "analysis_implementation",
        "open_anchor_preflight",
    ]


def test_runtime_verifiers_do_not_depend_on_optimized_away_asserts() -> None:
    wrapper = (FORWARD_ROOT / "verify_forward_preregistration.py").read_text(
        encoding="utf-8"
    )
    implementation = (
        FORWARD_ROOT / "verify_forward_preregistration_v2.py"
    ).read_text(encoding="utf-8")
    assert "assert " not in wrapper
    assert "assert " not in implementation
    assert "VerificationError" in implementation
