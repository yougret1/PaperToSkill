from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

from materialization_verifier_v2 import (
    BFSI_ORDERS,
    EMPTY_SHA256,
    FAMILY_ORDER,
    NORMALIZED_MAX_OUTPUT_TOKENS,
    OVERLAP_FIELDS,
    OVERLAP_SCOPES,
    PAIR_ORDERS,
    PRIMARY_ORDERS,
    REQUIRED_CLOSED_MODELS,
    SECONDARY_TASKS,
    build_validation_fixture_rows,
)


FORWARD_ROOT = Path(__file__).resolve().parent
PREREG_ROOT = FORWARD_ROOT / "preregistration"
RUN_ROOT = FORWARD_ROOT.parents[1]
STATUS = "stage_2_2_design_registered_materialization_pending"
EXPECTED_DOMAINS = ["nlp", "software_engineering", "data_analysis", "agent_tool_use"]
EXPECTED_FIGURES = [
    "F1_protocol_audit",
    "F2_cross_paper_effects",
    "F3_compression_reliability",
    "F4_robustness_and_failures",
]
EXPECTED_PRIMARY_TASK_ORDER = [
    "NLP-LLM-01",
    "SE-DD-01",
    "DATA-SNAP-01",
    "AGENT-TF-01",
    "NLP-LLM-02",
    "SE-DD-02",
    "DATA-SNAP-02",
    "AGENT-TF-02",
    "NLP-LL2-01",
    "SE-CR-01",
    "DATA-LEI-01",
    "AGENT-RF-01",
    "NLP-LL2-02",
    "SE-CR-02",
    "DATA-LEI-02",
    "AGENT-RF-02",
    "NLP-CSE-01",
    "SE-PE-01",
    "DATA-HDB-01",
    "AGENT-RA-01",
    "NLP-CSE-02",
    "SE-PE-02",
    "DATA-HDB-02",
    "AGENT-RA-02",
]
EXPECTED_BUNDLE_PATHS = sorted(
    [
        "analyze_sla_operating_characteristics.py",
        "build_metadata_evidence_manifest.py",
        "build_preregistration_hash_manifest.py",
        "build_stage_2_2_registration.py",
        "materialization_verifier_v2.py",
        "preregistration/candidate_matrix.json",
        "preregistration/experiment_plan.json",
        "preregistration/experiment_plan.md",
        "preregistration/figure_statistical_plan.json",
        "preregistration/materialization_contract.json",
        "preregistration/metadata_evidence_manifest.json",
        "preregistration/model_ablation_registry.json",
        "preregistration/paper_registry.json",
        "preregistration/sla_operating_characteristics.json",
        "preregistration_verifier_v3.py",
        "tests/test_forward_preregistration.py",
        "tests/test_materialization_semantics.py",
        "tests/test_preregistration_mutations.py",
        "verify_forward_preregistration.py",
        "verify_forward_preregistration_v2.py",
        "verify_stage_2_3_materialization.py",
    ]
)
EXPECTED_TERMINAL_OUTCOMES = [
    "provider_or_model_unavailable",
    "transport_terminal_failure",
    "integrity_or_digest_failure",
    "malformed_or_no_submission",
    "action_budget_exhausted",
    "hard_contract_failure",
    "score_shortfall",
    "operational_success",
]
EXPECTED_TERMINAL_TRUTH_TABLE = {
    "provider_or_model_unavailable": {
        "row_valid": False,
        "condition_success": None,
        "pair_valid": False,
        "private_score_rule": "null",
    },
    "transport_terminal_failure": {
        "row_valid": False,
        "condition_success": None,
        "pair_valid": False,
        "private_score_rule": "null",
    },
    "integrity_or_digest_failure": {
        "row_valid": False,
        "condition_success": None,
        "pair_valid": False,
        "private_score_rule": "null",
    },
    "malformed_or_no_submission": {
        "row_valid": True,
        "condition_success": False,
        "pair_valid": True,
        "private_score_rule": "exactly 0.0",
    },
    "action_budget_exhausted": {
        "row_valid": True,
        "condition_success": False,
        "pair_valid": True,
        "private_score_rule": (
            "Run the frozen scorer on the terminal workspace and use its finite "
            "[0,1] assertion fraction; scorer inability is integrity_or_digest_failure."
        ),
    },
    "hard_contract_failure": {
        "row_valid": True,
        "condition_success": False,
        "pair_valid": True,
        "private_score_rule": "frozen scorer's finite [0,1] assertion fraction",
    },
    "score_shortfall": {
        "row_valid": True,
        "condition_success": False,
        "pair_valid": True,
        "private_score_rule": "frozen scorer's finite [0,1] assertion fraction",
    },
    "operational_success": {
        "row_valid": True,
        "condition_success": True,
        "pair_valid": True,
        "private_score_rule": "frozen scorer's finite [0,1] assertion fraction",
    },
}
EXPECTED_ROW_FIELDS = [
    "execution_id",
    "global_sequence_index",
    "study_id",
    "execution_family",
    "paper_id",
    "domain",
    "task_id",
    "variant_id",
    "model_slot_id",
    "registry_id",
    "block_id",
    "order_code",
    "order_position",
    "condition",
    "candidate_id",
    "pair_id",
    "task_scaffold_sha256",
    "fixture_manifest_sha256",
    "fixture_payload_sha256",
    "private_registry_manifest_sha256",
    "scorer_manifest_sha256",
    "candidate_artifact_sha256",
    "canonical_model_visible_payload_sha256",
    "serialized_wire_request_sha256",
    "decoding_config_sha256",
    "derived_seed",
    "seed_turn_id",
]
EXPECTED_CANDIDATE_IDS = {
    "primary": {"B": "B_empty_artifact", "F": "F", "S": "S_dag_ratio_60_v1"},
    "controls": {
        "planted_redundancy_positive": {
            "F": "control_positive_reference",
            "C": "F",
        },
        "destructive_core_negative": {"F": "F", "C": "control_negative"},
        "byte_identical_identity": {"F": "F", "C": "control_identity"},
    },
    "structural_ladder": {
        "L0_primary_slice": {"F": "F", "C": "ladder_L0"},
        "L1_mid_restore": {"F": "F", "C": "ladder_L1"},
        "L2_near_full_strict": {"F": "F", "C": "ladder_L2"},
    },
    "alternate_reducers": {
        "dag_greedy_ratio_60_v1": {"F": "F", "C": "alternate_dag_greedy"},
        "source_window_ratio_60_v1": {
            "F": "F",
            "C": "alternate_source_window",
        },
    },
    "required_closed_models": {
        "B": "B_empty_artifact",
        "F": "F",
        "S": "S_dag_ratio_60_v1",
        "I": "F",
    },
    "open_anchor": {
        "B": "B_empty_artifact",
        "F": "F",
        "S": "S_dag_ratio_60_v1",
        "I": "F",
    },
}
EXPECTED_SCHEDULE_PRODUCTS = {
    "primary": {
        "tasks": 24,
        "variants_or_models": 1,
        "blocks": 6,
        "conditions": ["B", "F", "S"],
        "rows": 432,
        "model_slot_ids": ["deepseek_primary"],
    },
    "controls": {
        "tasks": 4,
        "model_slot_ids": ["deepseek_primary"],
        "variants": [
            "planted_redundancy_positive",
            "destructive_core_negative",
            "byte_identical_identity",
        ],
        "blocks": 6,
        "conditions": ["F", "C"],
        "rows": 144,
    },
    "structural_ladder": {
        "tasks": 4,
        "model_slot_ids": ["deepseek_primary"],
        "variants": ["L0_primary_slice", "L1_mid_restore", "L2_near_full_strict"],
        "blocks": 6,
        "conditions": ["F", "C"],
        "rows": 144,
    },
    "alternate_reducers": {
        "tasks": 4,
        "model_slot_ids": ["deepseek_primary"],
        "variants": ["dag_greedy_ratio_60_v1", "source_window_ratio_60_v1"],
        "blocks": 6,
        "conditions": ["F", "C"],
        "rows": 96,
    },
    "required_closed_models": {
        "tasks": 4,
        "model_slot_ids": REQUIRED_CLOSED_MODELS,
        "blocks": 6,
        "conditions": ["B", "F", "S", "I"],
        "rows": 384,
    },
    "open_anchor": {
        "tasks": 4,
        "model_slot_ids": ["open_seed_anchor"],
        "blocks": 6,
        "conditions": ["B", "F", "S", "I"],
        "rows": 96,
    },
}
EXPECTED_GLOBAL_ARTIFACTS = [
    "materialization/global_remote_schedule.json",
    "materialization/global_local_anchor_schedule.json",
    "materialization/request_template_manifest.json",
    "materialization/model_preflight_manifest.json",
    "materialization/result_canonicalization_manifest.json",
    "materialization/open_anchor_runtime_manifest.json",
    "materialization/replacement_amendment_manifest.json",
    "materialization/analysis_implementation_manifest.json",
    "materialization/implementation_source_audit_manifest.json",
    "materialization/parent_overlap_value_manifest.json",
    "materialization/parent_overlap_audit.json",
    "materialization/analysis_source_allowlist.json",
    "materialization/immutable_file_manifest.json",
    "materialization/final_anchor_manifest.json",
]
EXPECTED_REPLACEMENT_REASON_CODES = [
    "full_text_unavailable",
    "source_span_atomization_infeasible",
    "deterministic_private_scorer_infeasible",
    "proprietary_data_or_retraining_required",
    "primary_reducer_no_eligible_subset",
    "structural_ladder_no_three_level_chain",
    "alternate_reducer_no_candidate",
]
EXPECTED_RESULT_ROW_FIELDS = [
    "execution_id",
    "terminal_outcome",
    "termination_reason",
    "provider_finish_reason",
    "row_valid",
    "condition_success",
    "private_score",
    "raw_response_path",
    "raw_response_sha256",
    "canonical_output_path",
    "canonical_output_sha256",
    "generated_token_ids",
    "hard_contract_vector",
    "attempts",
    "candidate_artifact_bytes",
    "candidate_artifact_cl100k_tokens",
    "canonical_model_visible_payload_bytes",
    "provider_reported_input_tokens",
    "provider_reported_output_tokens",
    "provider_reported_total_tokens",
    "provider_reported_cached_input_tokens",
    "provider_usage_missing_reason",
    "terminal_attempt_elapsed_ms",
    "total_execution_elapsed_ms",
    "retry_sleep_elapsed_ms",
    "retry_overhead_ms",
]


def expected_result_row_schema() -> dict[str, object]:
    nullable_hash = {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"}
    nullable_path = {"type": ["string", "null"], "minLength": 1}
    nullable_nonnegative_integer = {
        "type": ["integer", "null"],
        "minimum": 0,
    }
    properties: dict[str, object] = {
        "execution_id": {"type": "string", "minLength": 1},
        "terminal_outcome": {
            "type": "string",
            "enum": [
                "provider_or_model_unavailable",
                "transport_terminal_failure",
                "integrity_or_digest_failure",
                "malformed_or_no_submission",
                "action_budget_exhausted",
                "hard_contract_failure",
                "score_shortfall",
                "operational_success",
            ],
        },
        "termination_reason": {
            "type": "string",
            "enum": [
                "eos",
                "length",
                "provider_stop",
                "transport_failure",
                "not_dispatched",
            ],
        },
        "provider_finish_reason": {"type": ["string", "null"]},
        "row_valid": {"type": "boolean"},
        "condition_success": {"type": ["boolean", "null"]},
        "private_score": {
            "type": ["number", "null"],
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "raw_response_path": nullable_path,
        "raw_response_sha256": nullable_hash,
        "canonical_output_path": nullable_path,
        "canonical_output_sha256": nullable_hash,
        "generated_token_ids": {
            "type": ["array", "null"],
            "items": {"type": "integer", "minimum": 0},
        },
        "hard_contract_vector": {
            "type": ["array", "null"],
            "items": {"type": "boolean"},
        },
        "attempts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "attempt_index",
                    "attempt_status_class",
                    "attempt_elapsed_ms",
                    "retry_sleep_after_attempt_ms",
                ],
                "properties": {
                    "attempt_index": {"type": "integer", "minimum": 1},
                    "attempt_status_class": {"type": "string", "minLength": 1},
                    "attempt_elapsed_ms": {"type": "integer", "minimum": 0},
                    "retry_sleep_after_attempt_ms": {
                        "type": "integer",
                        "minimum": 0,
                    },
                },
                "additionalProperties": True,
            },
        },
        "candidate_artifact_bytes": {"type": "integer", "minimum": 0},
        "candidate_artifact_cl100k_tokens": {"type": "integer", "minimum": 0},
        "canonical_model_visible_payload_bytes": {
            "type": "integer",
            "minimum": 0,
        },
        "provider_reported_input_tokens": nullable_nonnegative_integer,
        "provider_reported_output_tokens": nullable_nonnegative_integer,
        "provider_reported_total_tokens": nullable_nonnegative_integer,
        "provider_reported_cached_input_tokens": nullable_nonnegative_integer,
        "provider_usage_missing_reason": {
            "type": ["string", "null"],
            "enum": [
                "not_dispatched",
                "transport_failure_no_usage",
                "provider_omitted_usage",
                "malformed_usage_tuple_or_integrity_failure",
                None,
            ],
        },
        "terminal_attempt_elapsed_ms": nullable_nonnegative_integer,
        "total_execution_elapsed_ms": nullable_nonnegative_integer,
        "retry_sleep_elapsed_ms": nullable_nonnegative_integer,
        "retry_overhead_ms": nullable_nonnegative_integer,
    }
    return {
        "type": "object",
        "required": list(properties),
        "properties": properties,
        "additionalProperties": False,
    }


def expected_result_row_cross_field_contract() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-result-row-cross-fields.v1",
        "not_dispatched": {
            "terminal_outcome": "provider_or_model_unavailable",
            "attempts": "empty",
            "timing_fields": "all_null",
            "raw_response_pair": "both_null",
        },
        "dispatched": {
            "attempts": "nonempty",
            "timing_fields": "all_nonnull",
            "attempt_indices": "strict_consecutive_1_through_n",
            "terminal_attempt_elapsed_ms": "equals_last_attempt_elapsed_ms",
            "terminal_retry_sleep_after_attempt_ms": 0,
        },
        "timing_arithmetic": {
            "retry_sleep_elapsed_ms": "sum_attempt_retry_sleep_after_attempt_ms",
            "total_execution_elapsed_ms": "gte_terminal_attempt_elapsed_ms",
            "retry_overhead_ms": "total_execution_elapsed_ms_minus_terminal_attempt_elapsed_ms",
            "retry_overhead_sleep_rounding_tolerance_ms": 1,
            "total_component_lower_bound": "sum_attempt_elapsed_ms_plus_retry_sleep_elapsed_ms",
            "total_component_rounding_tolerance_ms": "attempt_count_plus_1",
        },
        "provider_usage": {
            "core_fields": [
                "provider_reported_input_tokens",
                "provider_reported_output_tokens",
                "provider_reported_total_tokens",
            ],
            "allowed_missingness": ["all_nonnull", "all_null_with_nonempty_reason"],
            "missing_reason_codes": [
                "not_dispatched",
                "transport_failure_no_usage",
                "provider_omitted_usage",
                "malformed_usage_tuple_or_integrity_failure",
            ],
            "missing_reason_by_terminal_outcome": {
                "provider_or_model_unavailable": ["not_dispatched"],
                "transport_terminal_failure": ["transport_failure_no_usage"],
                "completed_body_outcomes": [
                    "provider_omitted_usage",
                    "malformed_usage_tuple_or_integrity_failure",
                ],
            },
            "reported_total": "input_plus_output",
            "reported_usage_requires_missing_reason_null": True,
            "cached_input_tokens_independently_nullable": True,
        },
        "generated_token_ids": {
            "invalid_outcomes": "null",
            "closed_model_slots": "null_because_no_exact_token_id_selector_is_registered",
            "open_seed_anchor_eos": "nonempty_at_most_1024_first_registered_eos_is_final",
            "open_seed_anchor_length": "exactly_1024_with_no_registered_eos",
            "other_open_seed_anchor_reasons": "forbidden",
        },
        "path_hash_pairs": [
            ["raw_response_path", "raw_response_sha256"],
            ["canonical_output_path", "canonical_output_sha256"],
        ],
        "completed_body": {
            "raw_response_pair": "both_nonnull",
            "scored_nonmalformed_canonical_pair": "both_nonnull",
            "scored_nonmalformed_hard_contract_vector": "nonnull_array",
            "malformed_canonical_pair": "both_null_or_both_nonnull",
        },
        "invalid_outcome_null_fields": [
            "canonical_output_path",
            "canonical_output_sha256",
            "generated_token_ids",
            "hard_contract_vector",
            "private_score",
        ],
        "always_present_nonnegative_artifact_fields": [
            "candidate_artifact_bytes",
            "candidate_artifact_cl100k_tokens",
            "canonical_model_visible_payload_bytes",
        ],
    }


def expected_slot_response_contracts() -> list[dict[str, object]]:
    dispatch = {
        "transport_terminal_failure": "transport_failure",
        "provider_or_model_unavailable": "not_dispatched",
    }
    protocols: dict[str, dict[str, object]] = {
        "chat": {
            "provider_protocol": "openai_chat_completions_v1",
            "canonical_output_selector": {
                "kind": "json_pointer",
                "pointer": "/choices/0/message/content",
                "required_type": "string",
            },
            "provider_finish_reason_selector": {
                "kind": "json_pointer_nullable",
                "pointer": "/choices/0/finish_reason",
                "accepted_types": ["string", "null"],
            },
            "usage_selectors": {
                "input_tokens": {"kind": "json_pointer", "pointer": "/usage/prompt_tokens"},
                "output_tokens": {
                    "kind": "json_pointer",
                    "pointer": "/usage/completion_tokens",
                },
                "total_tokens": {"kind": "json_pointer", "pointer": "/usage/total_tokens"},
                "cached_input_tokens": {
                    "kind": "json_pointer_nullable",
                    "pointer": "/usage/prompt_tokens_details/cached_tokens",
                },
            },
            "finish_reason_normalization": {
                "exact_string_map": {
                    "length": "length",
                    "stop": "provider_stop",
                    "content_filter": "provider_stop",
                    "function_call": "provider_stop",
                    "tool_calls": "provider_stop",
                },
                "unknown_string": "provider_stop",
                "null_or_missing": "provider_stop",
                "dispatch_state_map": dispatch,
            },
        },
        "responses": {
            "provider_protocol": "openai_responses_v1",
            "canonical_output_selector": {
                "kind": "first_matching_nested_array_value_v1",
                "outer_array_pointer": "/output",
                "outer_match": {"field": "type", "equals": "message"},
                "inner_array_field": "content",
                "inner_match": {"field": "type", "equals": "output_text"},
                "value_field": "text",
                "required_type": "string",
                "selection": "first_in_provider_order",
            },
            "provider_finish_reason_selector": {
                "kind": "first_non_null_json_pointer_v1",
                "pointers_in_precedence_order": [
                    "/incomplete_details/reason",
                    "/status",
                ],
                "accepted_types": ["string", "null"],
            },
            "usage_selectors": {
                "input_tokens": {"kind": "json_pointer", "pointer": "/usage/input_tokens"},
                "output_tokens": {"kind": "json_pointer", "pointer": "/usage/output_tokens"},
                "total_tokens": {"kind": "json_pointer", "pointer": "/usage/total_tokens"},
                "cached_input_tokens": {
                    "kind": "json_pointer_nullable",
                    "pointer": "/usage/input_tokens_details/cached_tokens",
                },
            },
            "finish_reason_normalization": {
                "exact_string_map": {
                    "completed": "provider_stop",
                    "max_output_tokens": "length",
                },
                "unknown_string": "provider_stop",
                "null_or_missing": "provider_stop",
                "dispatch_state_map": dispatch,
            },
        },
        "anthropic": {
            "provider_protocol": "anthropic_messages_v1",
            "canonical_output_selector": {
                "kind": "first_matching_array_value_v1",
                "array_pointer": "/content",
                "match": {"field": "type", "equals": "text"},
                "value_field": "text",
                "required_type": "string",
                "selection": "first_in_provider_order",
            },
            "provider_finish_reason_selector": {
                "kind": "json_pointer_nullable",
                "pointer": "/stop_reason",
                "accepted_types": ["string", "null"],
            },
            "usage_selectors": {
                "input_tokens": {"kind": "json_pointer", "pointer": "/usage/input_tokens"},
                "output_tokens": {"kind": "json_pointer", "pointer": "/usage/output_tokens"},
                "total_tokens": {
                    "kind": "sum_nonnegative_integer_json_pointers_v1",
                    "pointers": ["/usage/input_tokens", "/usage/output_tokens"],
                },
                "cached_input_tokens": {
                    "kind": "json_pointer_nullable",
                    "pointer": "/usage/cache_read_input_tokens",
                },
            },
            "finish_reason_normalization": {
                "exact_string_map": {
                    "max_tokens": "length",
                    "end_turn": "provider_stop",
                    "pause_turn": "provider_stop",
                    "refusal": "provider_stop",
                    "stop_sequence": "provider_stop",
                    "tool_use": "provider_stop",
                },
                "unknown_string": "provider_stop",
                "null_or_missing": "provider_stop",
                "dispatch_state_map": dispatch,
            },
        },
        "local": {
            "provider_protocol": "effectslice_local_generation_adapter_v1",
            "canonical_output_selector": {
                "kind": "json_pointer",
                "pointer": "/canonical_output",
                "required_type": "string",
            },
            "provider_finish_reason_selector": {
                "kind": "json_pointer",
                "pointer": "/finish_reason",
                "accepted_types": ["string"],
            },
            "usage_selectors": {
                "input_tokens": {"kind": "json_pointer", "pointer": "/prompt_token_count"},
                "output_tokens": {
                    "kind": "json_pointer",
                    "pointer": "/generated_token_count",
                },
                "total_tokens": {
                    "kind": "sum_nonnegative_integer_json_pointers_v1",
                    "pointers": ["/prompt_token_count", "/generated_token_count"],
                },
                "cached_input_tokens": {"kind": "constant", "value": None},
            },
            "finish_reason_normalization": {
                "exact_string_map": {"eos": "eos", "length": "length"},
                "unknown_string": "provider_stop",
                "null_or_missing": "provider_stop",
                "dispatch_state_map": dispatch,
            },
        },
    }

    def bind(slot: str, alias: str, protocol: str) -> dict[str, object]:
        return {"model_slot_id": slot, "exact_alias": alias, **protocols[protocol]}

    return [
        bind("deepseek_primary", "deepseek-v4-flash", "chat"),
        bind("gpt_5_5", "gpt-5.5", "responses"),
        bind("gpt_5_6_sol", "gpt-5.6-sol", "responses"),
        bind("gpt_5_6_terra", "gpt-5.6-terra", "responses"),
        bind("claude_opus_4_7", "claude-opus-4-7", "anthropic"),
        bind("open_seed_anchor", "Qwen/Qwen2.5-Coder-7B-Instruct", "local"),
    ]


def expected_parser_golden_case_contracts() -> list[dict[str, object]]:
    return [
        {
            "case_id": case_id,
            "model_slot_id": slot,
            "dispatch_state": dispatch,
            "terminal_outcome": outcome,
            "termination_reason": reason,
            "provider_finish_reason": finish,
        }
        for case_id, slot, dispatch, outcome, reason, finish in [
            ("deepseek_provider_stop", "deepseek_primary", "completed_body", "operational_success", "provider_stop", "stop"),
            ("deepseek_length_scored", "deepseek_primary", "completed_body", "operational_success", "length", "length"),
            ("gpt_5_5_completed", "gpt_5_5", "completed_body", "operational_success", "provider_stop", "completed"),
            ("gpt_5_6_sol_length_scored", "gpt_5_6_sol", "completed_body", "operational_success", "length", "max_output_tokens"),
            ("gpt_5_6_terra_null_finish", "gpt_5_6_terra", "completed_body", "operational_success", "provider_stop", None),
            ("claude_provider_stop", "claude_opus_4_7", "completed_body", "operational_success", "provider_stop", "end_turn"),
            ("claude_length_scored", "claude_opus_4_7", "completed_body", "operational_success", "length", "max_tokens"),
            ("qwen_eos", "open_seed_anchor", "completed_body", "operational_success", "eos", "eos"),
            ("qwen_length_scored", "open_seed_anchor", "completed_body", "operational_success", "length", "length"),
            ("completed_malformed_body", "deepseek_primary", "completed_body", "malformed_or_no_submission", "provider_stop", None),
            ("terminal_transport_failure", "deepseek_primary", "transport_terminal_failure", "transport_terminal_failure", "transport_failure", None),
            ("model_unavailable_not_dispatched", "gpt_5_5", "provider_or_model_unavailable", "provider_or_model_unavailable", "not_dispatched", None),
        ]
    ]


EXPECTED_IMPLEMENTATION_SOURCE_AUDIT_CHECKS = {
    "result_canonicalizer": [
        "slot_response_contracts_exact",
        "finish_reason_normalization_exact",
        "usage_extraction_exact",
        "terminal_truth_table_enforced",
        "no_network_or_secret_access",
    ],
    "analysis_implementation": [
        "analysis_allowlist_only",
        "registered_estimators_exact",
        "invalid_denominators_preserved",
        "figure_sources_traceable",
        "no_network_or_secret_access",
    ],
    "open_anchor_preflight": [
        "offline_exact_revision_load",
        "deterministic_runtime_flags_exact",
        "eos_and_length_semantics_exact",
        "repeat_generation_compared",
        "no_network_or_secret_access",
    ],
}


def _expected_overlap_source_registry() -> dict[str, object]:
    schedule_fields = {
        "execution_id": {"kind": "schedule_rows_field", "field": "execution_id"},
        "pair_id": {"kind": "schedule_rows_field", "field": "pair_id"},
        "derived_seed": {"kind": "schedule_rows_field", "field": "derived_seed"},
        "fixture_payload_sha256": {
            "kind": "schedule_rows_field",
            "field": "fixture_payload_sha256",
        },
        "serialized_wire_request_sha256": {
            "kind": "schedule_rows_field",
            "field": "serialized_wire_request_sha256",
        },
    }
    parent_extractors = {
        "execution_id": ("experiment_results", "**/transcript.json", "retry_lineage_id"),
        "pair_id": ("experiment_results", "**/pair_manifest.json", "pair_id"),
        "private_case_id": ("artifacts", "**/case_registry.json", "case_id"),
        "derived_seed": ("artifacts", "**/case_registry.json", "seed"),
        "fixture_payload_sha256": ("artifacts", "**/case_registry.json", None),
        "serialized_wire_request_sha256": (
            "experiment_results",
            "**/transcript.json",
            "prompt_sha256",
        ),
    }
    registry: dict[str, object] = {}
    for field in OVERLAP_FIELDS:
        fg1 = (
            {
                "path_base": "materialization_root",
                "root": "tasks",
                "glob": "*/private_registry_*_manifest.json",
                "expected_file_count": 48,
                "extractor": {"kind": "recursive_key", "key": "case_ids"},
            }
            if field == "private_case_id"
            else {
                "path_base": "materialization_root",
                "root": ".",
                "glob": "global_*_schedule.json",
                "expected_file_count": 2,
                "extractor": schedule_fields[field],
            }
        )
        parent_root_kind, parent_glob, parent_key = parent_extractors[field]
        scopes: dict[str, object] = {"effectslice_fg1": fg1}
        for scope, version, count in (
            (
                "confirmation_v4",
                "confirmation_v4",
                180 if "transcript" in parent_glob else 60 if "pair_manifest" in parent_glob else 2,
            ),
            (
                "confirmation_v5r2",
                "confirmation_v5r2",
                54 if "transcript" in parent_glob else 18 if "pair_manifest" in parent_glob else 1,
            ),
        ):
            scopes[scope] = {
                "path_base": "run_root",
                "root": f"{parent_root_kind}/{version}",
                "glob": parent_glob,
                "expected_file_count": count,
                "extractor": (
                    {"kind": "file_sha256"}
                    if parent_key is None
                    else {"kind": "recursive_key", "key": parent_key}
                ),
            }
        registry[field] = scopes
    return registry
EXPECTED_ESTIMATOR = {
    "block_value": (
        "For contrast X-Y and valid rows, d_ptb = outcome_X - outcome_Y, computed "
        "separately for binary success and [0,1] private score."
    ),
    "block_bounds": {
        "both_valid": "[x-y, x-y]",
        "X_valid_Y_invalid": "[x-1, x]",
        "X_invalid_Y_valid": "[-y, 1-y]",
        "both_invalid": "[-1, 1]",
    },
    "task_observed": (
        "Arithmetic mean of valid block differences; undefined if zero valid pairs, "
        "always accompanied by valid_pairs/6."
    ),
    "task_identified_bounds": (
        "Arithmetic mean of the six registered block lower endpoints and of the six "
        "upper endpoints, using denominator 6."
    ),
    "paper_observed": (
        "Equal 0.5/0.5 mean of the two task_observed values only when both are "
        "defined; otherwise undefined."
    ),
    "paper_identified_bounds": (
        "Equal 0.5/0.5 mean of the two task lower bounds and upper bounds."
    ),
    "domain_identified_bounds": (
        "Equal 1/3 mean of the three registered paper bounds in the domain."
    ),
    "overall_identified_bounds": "Equal 1/4 mean of the four domain bounds.",
    "observed_summary": (
        "Descriptive mean over defined paper_observed values with k/12 reported; it "
        "never replaces the registered identified bounds."
    ),
}
EXPECTED_REPEATABILITY_REDUCTION = {
    "unit": "task_model",
    "registered_pairs": 6,
    "boolean_endpoints": [
        "model_visible_input_sha256_agreement",
        "operational_success_agreement",
        "hard_contract_vector_agreement",
        "canonical_output_sha256_agreement",
        "raw_response_sha256_agreement",
    ],
    "boolean_summary": {
        "raw_values": "Six block-ordered values in {true,false,null}.",
        "valid_pair_count": "Count of non-null values in the six registered pairs.",
        "agreement_count": "Count of true values among valid pairs.",
        "agreement_rate_registered": "agreement_count / 6",
        "agreement_rate_valid": (
            "agreement_count / valid_pair_count; undefined when valid_pair_count is zero"
        ),
    },
    "score_delta_summary": {
        "raw_absolute_private_score_deltas": (
            "Six block-ordered values in [0,1] or null when the F/I pair is Invalid."
        ),
        "valid_pair_count": "Count of non-null score deltas.",
        "median_absolute_delta": (
            "Median of non-null absolute deltas; undefined when valid_pair_count is zero."
        ),
        "maximum_absolute_delta": (
            "Maximum of non-null absolute deltas; undefined when valid_pair_count is zero."
        ),
    },
    "missingness_rule": (
        "Invalid F/I pairs remain null and are counted in registered denominator 6; "
        "they are never imputed as agreements or disagreements."
    ),
    "aggregation_boundary": (
        "Never pool model slots or sentinel tasks. Cross-model displays retain one "
        "task-model cell per endpoint and show unavailable slots explicitly."
    ),
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _repo_root() -> Path:
    for candidate in (FORWARD_ROOT, *FORWARD_ROOT.parents):
        if (candidate / "paper" / "effectslice_aaai" / "main_v3.tex").is_file():
            return candidate
    raise VerificationError("repository root not found")


def _load(prereg_root: Path, name: str) -> dict[str, Any]:
    path = prereg_root / name
    require(path.is_file(), f"missing preregistration artifact: {name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot parse {name}: {exc}") from exc
    require(isinstance(value, dict), f"{name} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence_path(repo: Path, relative: str) -> Path:
    if relative.startswith(("paper/", "papers/", "research/")):
        return repo / relative
    return FORWARD_ROOT / relative


def _load_operating_analyzer():
    path = FORWARD_ROOT / "analyze_sla_operating_characteristics.py"
    spec = importlib.util.spec_from_file_location("fg1_sla_analysis", path)
    require(spec is not None and spec.loader is not None, "cannot load SLA analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_hash_manifest() -> str:
    manifest_path = PREREG_ROOT / "bundle_hash_manifest.json"
    require(manifest_path.is_file(), "missing preregistration bundle hash manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(
        manifest.get("schema_version") == "effectslice-fg1-bundle-hashes.v1",
        "unexpected hash-manifest schema",
    )
    entries = manifest.get("files")
    require(isinstance(entries, list), "hash manifest files must be a list")
    paths = [entry.get("path") for entry in entries if isinstance(entry, dict)]
    require(len(paths) == len(entries), "invalid hash-manifest entry")
    require(paths == EXPECTED_BUNDLE_PATHS, "hash manifest paths/order are incomplete")
    require(len(paths) == len(set(paths)), "duplicate hash-manifest path")
    canonical_pairs: list[str] = []
    for entry in entries:
        relative = entry["path"]
        path = FORWARD_ROOT / relative
        require(path.is_file(), f"hash-bound file missing: {relative}")
        actual = _sha256(path)
        require(actual == entry.get("sha256"), f"hash mismatch: {relative}")
        require(path.stat().st_size == entry.get("bytes"), f"size mismatch: {relative}")
        canonical_pairs.append(f"{relative}\0{actual}")
    bundle = hashlib.sha256("\n".join(canonical_pairs).encode("utf-8")).hexdigest()
    require(bundle == manifest.get("bundle_sha256"), "bundle digest mismatch")
    return bundle


def _verify_metadata_manifest(
    repo: Path,
    registry: dict[str, Any],
    manifest: dict[str, Any],
) -> int:
    require(
        manifest.get("schema_version") == "effectslice-fg1-metadata-evidence-hashes.v1",
        "unexpected metadata-evidence schema",
    )
    entries = manifest.get("entries")
    require(isinstance(entries, list), "metadata evidence entries must be a list")
    expected: dict[tuple[str, str], list[str]] = {}
    papers = registry["papers"]
    for paper in papers:
        for relative in paper["metadata_evidence"]:
            scope = (
                "repository"
                if relative.startswith(("paper/", "papers/", "research/"))
                else "forward_extension"
            )
            expected.setdefault((scope, relative), []).append(paper["paper_id"])
    expected[("forward_extension", "stage_report_2_6.json")] = []
    actual_keys = [(entry.get("scope"), entry.get("path")) for entry in entries]
    require(actual_keys == sorted(expected), "metadata evidence paths/order mismatch")
    require(len(actual_keys) == len(set(actual_keys)), "duplicate metadata evidence")
    for entry in entries:
        key = (entry["scope"], entry["path"])
        path = _evidence_path(repo, entry["path"])
        require(path.is_file(), f"missing metadata evidence: {entry['path']}")
        require(entry.get("paper_ids") == sorted(expected[key]), f"evidence paper mapping: {key}")
        require(entry.get("sha256") == _sha256(path), f"metadata evidence hash: {key}")
        require(entry.get("bytes") == path.stat().st_size, f"metadata evidence size: {key}")
    return len(entries)


def _seed(fields: list[str]) -> int:
    digest = hashlib.sha256(b"\0".join(field.encode("utf-8") for field in fields)).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def _audit(prereg_root: Path, verify_bundle: bool) -> dict[str, object]:
    repo = _repo_root()
    registry = _load(prereg_root, "paper_registry.json")
    candidates = _load(prereg_root, "candidate_matrix.json")
    experiment = _load(prereg_root, "experiment_plan.json")
    models = _load(prereg_root, "model_ablation_registry.json")
    figures = _load(prereg_root, "figure_statistical_plan.json")
    materialization = _load(prereg_root, "materialization_contract.json")
    operating = _load(prereg_root, "sla_operating_characteristics.json")
    metadata = _load(prereg_root, "metadata_evidence_manifest.json")

    for name, artifact in {
        "paper_registry": registry,
        "candidate_matrix": candidates,
        "experiment_plan": experiment,
        "model_registry": models,
        "figure_plan": figures,
        "materialization_contract": materialization,
    }.items():
        require(artifact.get("registration_status") == STATUS, f"{name} registration status")

    papers = registry.get("papers")
    require(isinstance(papers, list) and len(papers) == 12, "expected 12 papers")
    domains = Counter(paper.get("domain") for paper in papers)
    require(list(dict.fromkeys(paper.get("domain") for paper in papers)) == EXPECTED_DOMAINS, "domain order changed")
    require(domains == Counter({domain: 3 for domain in EXPECTED_DOMAINS}), "expected three papers per domain")
    paper_ids = [paper.get("paper_id") for paper in papers]
    persistent_ids = [paper.get("persistent_id") for paper in papers]
    require(len(paper_ids) == len(set(paper_ids)), "duplicate paper ID")
    require(len(persistent_ids) == len(set(persistent_ids)), "duplicate persistent ID")

    task_ids: list[str] = []
    registry_mapping: dict[str, list[str]] = {}
    task_to_domain: dict[str, str] = {}
    for paper in papers:
        require("arxiv" not in str(paper.get("venue", "")).lower(), f"non-formal venue: {paper['paper_id']}")
        tasks = paper.get("tasks")
        require(isinstance(tasks, list) and len(tasks) == 2, "paper must have two tasks")
        require(tasks[0].get("name") != tasks[1].get("name"), "duplicate task name")
        evidence_texts = [
            _evidence_path(repo, relative).read_text(encoding="utf-8").lower()
            for relative in paper.get("metadata_evidence", [])
        ]
        identifier = str(paper["persistent_id"]).split(":", 1)[1].lower()
        require(any(identifier in text for text in evidence_texts), f"persistent identifier absent: {paper['paper_id']}")
        registry_mapping[paper["paper_id"]] = []
        for task in tasks:
            task_id = task.get("task_id")
            require(isinstance(task_id, str) and task_id, "task ID missing")
            task_ids.append(task_id)
            registry_mapping[paper["paper_id"]].append(task_id)
            task_to_domain[task_id] = paper["domain"]
            for field in (
                "bounded_objective",
                "mechanism_boundary",
                "private_scorer",
                "primary_metric",
            ):
                require(bool(task.get(field)), f"{task_id} missing {field}")
            require(len(task.get("hard_contracts", [])) >= 4, f"{task_id} contracts")
    require(len(task_ids) == len(set(task_ids)) == 24, "expected 24 unique tasks")

    implementation = registry.get("implementation_policy", {})
    for field in (
        "independent_semantic_audit",
        "task_specificity_gate",
        "private_registry_gate",
        "canonical_reducer_runtime_gate",
    ):
        require(bool(implementation.get(field)), f"paper registry missing {field}")
    registry_replacement = registry.get("sampling_frame", {}).get(
        "replacement_policy", {}
    )
    require(
        registry_replacement.get("reason_codes")
        == EXPECTED_REPLACEMENT_REASON_CODES,
        "paper-registry replacement reasons",
    )
    require(
        "amendments=[]"
        in registry_replacement.get("procedure", "")
        and "lowest-ranked eligible reserve from the same domain"
        in registry_replacement.get("procedure", "")
        and "successor Stage 2.2 registration"
        in registry_replacement.get("procedure", "")
        and "regenerate and verify every schedule"
        in registry_replacement.get("procedure", "")
        and "No in-place task rewrite"
        in registry_replacement.get("forbidden", ""),
        "paper-registry replacement procedure",
    )

    entries = candidates.get("entries")
    require(isinstance(entries, list), "candidate entries missing")
    selected = [row for row in entries if row.get("status") == "selected"]
    require(len(selected) == 12, "candidate matrix must select 12 papers")
    selected_mapping = {row["paper_id"]: row.get("task_ids") for row in selected}
    require(selected_mapping == registry_mapping, "candidate/task mapping mismatch")
    require({row.get("status") for row in entries} == {"selected", "reserve", "rejected"}, "candidate statuses")
    audit_contract = candidates.get("audit_contract", {})
    require(audit_contract.get("source_auditor_must_differ_from_candidate_builder") is True, "candidate audit independence")
    require(
        audit_contract.get("current_registration_is_immutable") is True
        and audit_contract.get("replacement_requires_committed_successor_registration")
        is True,
        "candidate replacement immutability",
    )
    require(audit_contract.get("outcome_access_during_selection_or_replacement") == "forbidden", "selection outcome blindness")

    design = experiment.get("primary_design", {})
    require(
        {
            "papers": design.get("papers"),
            "independent_aggregate_unit": design.get("independent_aggregate_unit"),
            "independent_papers": design.get("independent_papers"),
            "tasks_per_paper": design.get("tasks_per_paper"),
            "nested_task_decisions": design.get("nested_task_decisions"),
            "blocks_per_task": design.get("blocks_per_task"),
            "conditions": design.get("conditions"),
            "remote_conversations": design.get("remote_conversations"),
        }
        == {
            "papers": 12,
            "independent_aggregate_unit": "paper",
            "independent_papers": 12,
            "tasks_per_paper": 2,
            "nested_task_decisions": 24,
            "blocks_per_task": 6,
            "conditions": ["B", "F", "S"],
            "remote_conversations": 432,
        },
        "primary design changed",
    )
    primary_reference = models.get("primary_model_reference", {})
    require(
        primary_reference
        == {
            "slot_id": "deepseek_primary",
            "role": "primary_24_task_BFS_only",
            "model_alias": "deepseek-v4-flash",
            "paper_label": "DeepSeek V3.2",
            "alias_label_mapping_status": (
                "The exact request alias is frozen; the provider/user-facing paper label "
                "is reported, but their deployment mapping is not independently attested."
            ),
            "required_for_primary_schedule": True,
            "conditions": ["B", "F", "S"],
            "remote_conversations": 432,
            "robustness_rows_reused": False,
            "decoding": {
                "temperature": 0,
                "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
            },
        },
        "primary model registry changed",
    )
    require(design.get("primary_model_slot_id") == primary_reference["slot_id"], "primary model cross-binding")
    research_questions = experiment.get("research_questions")
    require(isinstance(research_questions, list) and [row.get("id") for row in research_questions] == ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5"], "research-question order")
    require(
        research_questions[2].get("question")
        == (
            "How do structural restoration, reducer choice, compression, reliability, "
            "and cost trade off on four frozen tasks?"
        ),
        "RQ3 resource scope",
    )
    require(
        research_questions[3].get("question")
        == (
            "What exact candidate-state agreement and F/I repeatability are observed "
            "across required models on four prespecified sentinel tasks?"
        ),
        "RQ4 endpoint scope",
    )
    require(
        research_questions[4].get("question")
        == (
            "How stable are primary task decisions and identified bounds under the "
            "registered SLA grid, leave-one-block-out, and leave-one-paper-out "
            "sensitivity analyses?"
        ),
        "RQ5 sensitivity scope",
    )
    require(
        "not significance, power, or population-generalization criteria"
        in experiment.get("hypotheses", {}).get("benchmark_target_rationale", ""),
        "benchmark targets mischaracterized",
    )

    schedule = experiment.get("schedule", {})
    require(schedule.get("registry_A") == {"orders": PRIMARY_ORDERS[:3], "blocks": 3}, "registry A order")
    require(schedule.get("registry_B") == {"orders": PRIMARY_ORDERS[3:], "blocks": 3}, "registry B order")
    require(schedule.get("all_orders") == ["BFS", "BSF", "FBS", "FSB", "SBF", "SFB"], "BFS order list")
    require(schedule.get("secondary_pair_contemporaneity", {}).get("order_codes_by_block") == PAIR_ORDERS, "pair order")
    require(schedule.get("secondary_pair_contemporaneity", {}).get("adjacent_rows_required") is True, "pair adjacency")
    require(schedule.get("model_BFSI_orders_by_block") == BFSI_ORDERS, "BFSI order")

    construction = experiment.get("candidate_construction", {})
    identity = construction.get("canonical_atom_identity", {})
    require(identity.get("semantic_names_forbidden") is True, "opaque atom IDs")
    require(identity.get("unique_and_opaque_audit_required") is True, "atom-ID audit")
    require("document_sha256" in identity.get("formula", "") and "byte_start" in identity.get("formula", ""), "atom-ID formula")
    require(
        construction.get("canonical_renderer")
        == {
            "id": "effectslice_atom_renderer_v1",
            "encoding": "UTF-8 without BOM",
            "newline": "LF",
            "atom_separator": "two LF bytes",
            "artifact_only_ratio": True,
            "implementation_sha256_bound_at_materialization": True,
        },
        "renderer contract changed",
    )
    require(
        construction.get("canonical_tokenizer")
        == {
            "library": "tiktoken",
            "library_version": "0.12.0",
            "encoding_name": "cl100k_base",
            "tokenizer_asset_sha256_bound_at_materialization": True,
        },
        "tokenizer contract changed",
    )
    require(
        construction.get("dag_static_validation")
        == [
            "unique opaque atom IDs",
            "every dependency references a registered atom",
            "directed graph is acyclic",
            "registered canonical topological order is valid",
            "every retained candidate is nonempty, strict, and dependency closed",
        ],
        "DAG static gates changed",
    )
    reducer = construction.get("primary_reducer", {})
    require(reducer.get("id") == "dag_ratio_60_v1", "primary reducer ID")
    require(reducer.get("visible_fields") == ["atom_id", "dependency_ids", "rendered_token_count"], "reducer visible fields")
    require(
        reducer.get("forbidden_fields")
        == [
            "paper_claim_label",
            "hard_contract_label",
            "guardrail_label",
            "scorer_interface_label",
            "public_outcome",
            "private_outcome",
            "model_output",
        ],
        "reducer forbidden fields",
    )
    require(reducer.get("closure_definition") == "If retained atom a depends on atom b, b is retained.", "reducer closure")
    require(reducer.get("enumeration") == "Enumerate all nonempty dependency-closed strict subsets of F.", "reducer enumeration")
    require(reducer.get("target_token_retention") == 0.60, "target retention")
    require(reducer.get("eligible_token_retention_interval") == [0.45, 0.75], "retention interval")
    require(
        reducer.get("tie_break_order")
        == [
            "minimum_absolute_distance_to_0.60",
            "fewer_rendered_tokens",
            "lexicographic_canonical_atom_id_list",
        ],
        "reducer tie breaks",
    )
    require(reducer.get("outcome_access") == "forbidden", "reducer outcome blindness")
    for field in (
        "input_manifest_sha256_bound_at_materialization",
        "enumeration_log_sha256_bound_at_materialization",
        "selected_output_sha256_bound_at_materialization",
    ):
        require(reducer.get(field) is True, f"reducer hash binding: {field}")

    scoring = experiment.get("scoring", {})
    require(
        scoring.get("admission_sla")
        == {
            "total_six_blocks": {
                "maximum_B_successes": 1,
                "minimum_F_successes": 5,
                "minimum_S_successes": 5,
                "minimum_valid_paired_margin_blocks": 5,
            },
            "each_three_block_registry": {
                "maximum_B_successes": 1,
                "minimum_F_successes": 2,
                "minimum_S_successes": 2,
                "minimum_valid_paired_margin_blocks": 2,
            },
            "paired_margin_rule": "S private_score >= F private_score - 0.05 in the same block",
            "all_registered_rows_terminal": True,
            "all_outputs_complete": True,
            "all_integrity_checks_pass": True,
        },
        "admission SLA changed",
    )
    require(list(scoring.get("decision_states", {})) == ["Admit", "Reject", "Invalid"], "decision-state order")
    pair_rule = scoring.get("two_arm_pair_rule", {})
    require(pair_rule.get("states") == ["PairPass", "PairFail", "Invalid"], "pair states")
    require("never called Admit or Reject" in pair_rule.get("scope", ""), "pair/admission separation")
    require(
        pair_rule.get("total_six_blocks")
        == {
            "minimum_reference_F_successes": 5,
            "minimum_candidate_successes": 5,
            "minimum_valid_margin_pairs": 5,
        },
        "two-arm total rule",
    )
    require(
        pair_rule.get("each_three_block_registry")
        == {
            "minimum_reference_F_successes": 2,
            "minimum_candidate_successes": 2,
            "minimum_valid_margin_pairs": 2,
        },
        "two-arm registry rule",
    )
    require(
        [pair_rule.get(state) for state in ("PairPass", "PairFail", "Invalid")]
        == [
            "All total, registry, terminal, and integrity gates pass.",
            "Every row is valid but one or more pair gates fail.",
            "One or more required pair rows or bindings are invalid.",
        ],
        "two-arm state semantics",
    )
    controls_rule = scoring.get("control_sanity_rules", {})
    require(controls_rule.get("states") == ["SanityPass", "SanityFail", "Invalid"], "sanity states")
    require(
        controls_rule.get("destructive_core_negative", {}).get("total")
        == {
            "minimum_reference_F_successes": 5,
            "maximum_candidate_successes": 1,
            "minimum_targeted_hard_contract_failures": 5,
        },
        "negative-control total rule",
    )
    require(
        controls_rule.get("destructive_core_negative", {}).get("each_registry")
        == {
            "minimum_reference_F_successes": 2,
            "maximum_candidate_successes": 1,
            "minimum_targeted_hard_contract_failures": 2,
        },
        "negative-control registry rule",
    )
    identity_rule = controls_rule.get("byte_identical_identity", {})
    require(
        {
            key: identity_rule.get(key)
            for key in (
                "input_digest_matches_required",
                "minimum_valid_pairs",
                "minimum_operational_success_agreements",
                "minimum_hard_contract_vector_agreements",
                "minimum_score_delta_within_0.05",
            )
        }
        == {
            "input_digest_matches_required": 6,
            "minimum_valid_pairs": 5,
            "minimum_operational_success_agreements": 5,
            "minimum_hard_contract_vector_agreements": 5,
            "minimum_score_delta_within_0.05": 5,
        },
        "identity-control rule",
    )
    require(
        [controls_rule.get(state) for state in ("SanityPass", "SanityFail", "Invalid")]
        == [
            "The control-specific frozen rule passes.",
            "Rows are valid but the control-specific rule fails.",
            "A required row, digest, or binding is invalid.",
        ],
        "sanity state semantics",
    )
    require(scoring.get("admit_reject_reserved_for_complete_BFS") is True, "BFS state reservation")
    require(
        scoring.get("reject_reason_precedence")
        == ["full-insufficient", "baseline-sensitive", "slice-insufficient", "margin-shortfall"],
        "reject precedence",
    )

    secondary = experiment.get("secondary_experiments", {})
    require(secondary.get("paper_task_ids") == SECONDARY_TASKS, "secondary task order")
    require({task_to_domain[task_id] for task_id in SECONDARY_TASKS} == set(EXPECTED_DOMAINS), "secondary domain coverage")
    controls = secondary.get("controls", {})
    ladder = secondary.get("structural_restoration_ladder", {})
    alternates = secondary.get("alternate_candidate_reducers", {})
    robustness = secondary.get("model_robustness", {})
    require(controls.get("pair") == ["fresh_reference_F", "fresh_control_candidate"], "control pair")
    require(ladder.get("pair") == ["fresh_F", "fresh_ladder_candidate"], "ladder pair")
    require(alternates.get("pair") == ["fresh_F", "fresh_alternate_S"], "alternate pair")
    for item, count in ((controls, 144), (ladder, 144), (alternates, 96)):
        require(item.get("pair_orders_by_block") == PAIR_ORDERS, "secondary pair order")
        require(item.get("pair_rows_are_adjacent") is True, "secondary pair adjacency")
        require(item.get("reuse_primary_rows") is False, "secondary row reuse")
        require(item.get("remote_conversations") == count, "secondary arithmetic")
    require("strict-subset L1 strict-subset L2 strict-subset F" in ladder.get("construction", ""), "ladder chain")
    require("complete" not in ladder.get("construction", "").lower() or "Enumerate all chains" in ladder.get("construction", ""), "ladder enumeration")
    require(ladder.get("feasibility_gate", "").startswith("At least one such three-level strict chain"), "ladder feasibility")
    require([item.get("id") for item in alternates.get("reducers", [])] == ["dag_greedy_ratio_60_v1", "source_window_ratio_60_v1"], "alternate reducer IDs")
    require(alternates.get("semantic_label_access") == "forbidden", "alternate reducer blindness")
    alternate_rules = [item.get("rule", "") for item in alternates.get("reducers", [])]
    require(
        "reverse registered canonical topological order" in alternate_rules[0]
        and "every half-open nonempty contiguous [start,end) interval"
        in alternate_rules[1]
        and all("lexicographic atom IDs" in rule for rule in alternate_rules),
        "alternate reducer algorithms",
    )
    require(robustness.get("conditions") == ["B", "F", "S", "I"], "BFSI conditions")
    require(robustness.get("condition_orders_by_block") == BFSI_ORDERS, "robustness order")
    require(robustness.get("required_remote_conversations") == 384, "robustness arithmetic")
    require(robustness.get("reuse_primary_rows") is False, "robustness row reuse")
    require(
        robustness.get("repeatability_metrics")
        == [
            "model_visible_input_sha256_agreement",
            "valid_pairs/registered_pairs",
            "operational_success_agreement",
            "hard_contract_vector_agreement",
            "absolute_private_score_delta",
            "canonical_output_sha256_agreement",
            "raw_response_sha256_agreement",
        ],
        "F/I repeatability endpoints",
    )
    require(
        robustness.get("repeatability_reduction") == EXPECTED_REPEATABILITY_REDUCTION,
        "experiment F/I reduction",
    )

    budget = experiment.get("resource_budget", {})
    remote_total = sum(
        budget[key]
        for key in (
            "primary_remote_conversations",
            "control_remote_conversations",
            "structural_ladder_remote_conversations",
            "alternate_reducer_remote_conversations",
            "required_model_robustness_remote_conversations",
        )
    )
    require(remote_total == budget.get("required_remote_conversation_cap") == 1200, "remote total")
    require(budget.get("open_anchor_local_execution_cap") == 96, "local total")
    require(budget.get("required_execution_cap") == 1296, "required total")
    require(budget.get("optional_closed_model_remote_conversation_cap") == 192, "optional total")
    require(budget.get("required_realistic_remote_hours") == [51, 70], "time plan")

    model_design = models.get("design", {})
    require(models.get("paper_task_ids") == SECONDARY_TASKS, "model/experiment task mismatch")
    require(model_design.get("condition_orders_by_block") == BFSI_ORDERS, "model order")
    require(model_design.get("candidate_state_rule") == "B/F/S use the primary admission SLA; I is excluded.", "model candidate rule")
    require(
        model_design.get("repeatability_reduction") == EXPECTED_REPEATABILITY_REDUCTION,
        "model-registry F/I reduction",
    )
    require(
        model_design.get("normalized_max_output_tokens")
        == NORMALIZED_MAX_OUTPUT_TOKENS,
        "model-registry normalized output cap",
    )
    primary_model = models.get("primary_model_reference", {})
    require(
        primary_model.get("decoding", {}).get("normalized_max_output_tokens")
        == NORMALIZED_MAX_OUTPUT_TOKENS,
        "primary-model normalized output cap",
    )
    slots = models.get("model_slots")
    require(isinstance(slots, list), "model slots missing")
    slot_ids = [slot.get("slot_id") for slot in slots]
    require(len(slot_ids) == len(set(slot_ids)), "duplicate model slot")
    required_closed = [slot for slot in slots if slot.get("role") == "required_closed_robustness"]
    require([slot.get("slot_id") for slot in required_closed] == REQUIRED_CLOSED_MODELS, "required model slot order")
    require(
        [slot.get("model_alias") for slot in required_closed]
        == ["gpt-5.5", "gpt-5.6-sol", "gpt-5.6-terra", "claude-opus-4-7"],
        "required model aliases",
    )
    require(all(slot.get("remote_conversations") == 96 for slot in required_closed), "closed slot count")
    require(all(slot.get("seed_support") == "record_if_returned_not_relied_upon" for slot in required_closed), "closed seed claim")
    require(
        all(
            slot.get("decoding", {}).get("normalized_max_output_tokens")
            == NORMALIZED_MAX_OUTPUT_TOKENS
            for slot in slots
        ),
        "model-slot normalized output caps",
    )
    optional = [slot for slot in slots if slot.get("required") is False]
    require([slot.get("model_alias") for slot in optional] == ["gpt-5.6-luna", "claude-opus-4-6"], "optional models")
    anchor = next((slot for slot in slots if slot.get("slot_id") == "open_seed_anchor"), None)
    require(isinstance(anchor, dict), "open anchor missing")
    require(anchor.get("local_executions") == 96, "open anchor count")
    require(
        anchor.get("decoding")
        == {
            "do_sample": False,
            "temperature": 0,
            "top_p": 1.0,
            "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
        },
        "anchor decoding",
    )
    seed = anchor.get("seed_derivation", {})
    require(seed.get("formula") == "uint32_big_endian(sha256(preimage_bytes)[0:4])", "seed formula")
    require(
        seed.get("preimage_fields")
        == ["study_id", "task_id", "ascii_decimal_block_id", "condition_seed_group", "ascii_decimal_turn_id"],
        "seed preimage fields",
    )
    require(seed.get("preimage_encoding") == "UTF-8 without BOM, fields joined by one NUL byte, no trailing NUL", "seed encoding")
    require(seed.get("condition_seed_groups") == {"B": "baseline", "F": "full_identity_pair", "S": "slice", "I": "full_identity_pair"}, "seed groups")
    require(seed.get("F_I_same_seed") is True, "F/I seed pairing")
    vectors = seed.get("golden_test_vectors")
    require(isinstance(vectors, list) and len(vectors) == 2, "seed vectors")
    for vector in vectors:
        require(_seed(vector["fields"]) == vector["uint32_seed"], "seed golden vector mismatch")
    require(anchor.get("deterministic_F_I_gate") == {"required_valid_pairs": 6, "required_model_visible_input_matches": 6, "required_generated_token_id_matches": 6, "required_canonical_output_sha256_matches": 6, "required_score_and_contract_vector_matches": 6}, "anchor determinism gate")

    transport = experiment.get("transport_and_failure_policy", {})
    require(
        transport.get("normalized_max_output_tokens")
        == NORMALIZED_MAX_OUTPUT_TOKENS
        and "provider-native JSON pointer"
        in transport.get("output_limit_binding", ""),
        "transport normalized output cap",
    )
    require(transport.get("mutually_exclusive_terminal_outcomes_in_precedence_order") == EXPECTED_TERMINAL_OUTCOMES, "terminal outcome order")
    require(transport.get("terminal_truth_table") == EXPECTED_TERMINAL_TRUTH_TABLE, "terminal truth table")
    require(transport.get("transport_retry_recovered_is_annotation") is True, "retry annotation")
    termination = transport.get("termination_reason_contract", {})
    require(
        termination.get("required_values")
        == ["eos", "length", "provider_stop", "transport_failure", "not_dispatched"]
        and termination.get("length_is_reported_separately_from_terminal_outcome")
        is True,
        "termination reason contract",
    )
    require("never rerun" in transport.get("semantic_rerun", ""), "semantic rerun ban")
    require(
        "Every row_valid=true terminal row has exactly one finite [0,1] private_score"
        in transport.get("private_score_totality", "")
        and "all five valid terminal score rules"
        in transport.get("private_score_totality", ""),
        "private-score totality contract",
    )

    analysis = experiment.get("analysis_contract", {})
    require(analysis.get("registered_estimator") == EXPECTED_ESTIMATOR, "registered estimator changed")
    require(analysis.get("aggregate_unit") == "paper", "aggregate unit")
    require(
        analysis.get("paper_bootstrap_sensitivity", {}).get("estimator_reuse")
        == (
            "Recompute the same task, paper, domain, and overall lower/upper "
            "estimators in every resample; never resample tasks or blocks."
        ),
        "bootstrap estimator reuse",
    )
    require(
        analysis.get("leave_one_paper_out")
        == (
            "Repeat the same registered estimator after removing each paper, "
            "renormalizing only the remaining paper weights within its domain."
        ),
        "LOPO estimator reuse",
    )
    require("B<=1, F>=4, S>=4, and margin>=4" in analysis.get("leave_one_block_out", ""), "five-block rule")
    require(
        "Any remaining Invalid row makes the five-block state Invalid"
        in analysis.get("leave_one_block_out", "")
        and "cannot replace the six-block admission decision"
        in analysis.get("leave_one_block_out", ""),
        "leave-one-block Invalid handling",
    )
    cost = analysis.get("cost_measurement", {})
    require(
        list(cost.get("deterministic_artifact_endpoints", {}))
        == [
            "candidate_artifact_bytes",
            "candidate_artifact_cl100k_tokens",
            "canonical_model_visible_payload_bytes",
        ],
        "registered deterministic resource endpoints",
    )
    require(
        list(cost.get("provider_reported_token_endpoints", {}))
        == [
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cached_input_tokens",
            "validation",
        ],
        "registered provider-token endpoints",
    )
    require(
        list(cost.get("latency_endpoints_ms", {}))
        == [
            "terminal_attempt_elapsed_ms",
            "total_execution_elapsed_ms",
            "retry_sleep_elapsed_ms",
            "retry_overhead_ms",
            "clock",
        ]
        and cost.get("attempt_fields")
        == [
            "attempt_index",
            "attempt_status_class",
            "attempt_elapsed_ms",
            "retry_sleep_after_attempt_ms",
        ],
        "registered latency endpoints",
    )
    require(
        cost.get("task_level_reduction", {}).get("registered_blocks") == 6
        and "every frozen provider_usage_missing_reason code"
        in cost.get("task_level_reduction", {}).get("missing_usage_reason_counts", "")
        and "valid_pairs/6"
        in cost.get("missingness", {}).get("paired_comparison", "")
        and cost.get("monetary_cost", {}).get("default") == "not_reported"
        and "final materialization anchor before calls"
        in cost.get("monetary_cost", {}).get("conditional_rule", ""),
        "registered resource reduction and cost rule",
    )

    figure_rows = figures.get("figures")
    require(isinstance(figure_rows, list), "figure rows missing")
    require([row.get("figure_id") for row in figure_rows] == EXPECTED_FIGURES, "figure order")
    require(
        [row.get("priority") for row in figure_rows]
        == ["main_required", "main_required", "main_required", "appendix_required"],
        "figure priorities",
    )
    stats = figures.get("statistics", {})
    require(stats.get("primary_unit") == "paper" and stats.get("independent_n") == 12, "figure independent unit")
    require(stats.get("valid_pair_reporting") == "valid_pairs/registered_pairs", "pair denominators")
    require(stats.get("invalid_partial_identification_bounds") is True, "invalid bounds")
    require(stats.get("estimator_source") == "experiment_plan.json analysis_contract.registered_estimator", "figure estimator binding")
    figure_lobo = stats.get("sla_sensitivity_grid", {}).get("leave_one_block_out", "")
    require(
        "Any remaining Invalid row makes the five-block state Invalid" in figure_lobo
        and "recovered sensitivity only" in figure_lobo,
        "figure leave-one-block Invalid handling",
    )
    require(
        stats.get("secondary_resource_outcomes") == cost,
        "figure resource contract binding",
    )
    require(figures.get("conditional_outputs", [])[0].get("default") == "do_not_render", "confusion matrix ban")

    require(materialization.get("schema_version") == "effectslice-fg1-materialization-contract.v1", "materialization schema")
    require(materialization.get("verifier") == "verify_stage_2_3_materialization.py", "materialization verifier binding")
    task_artifacts = materialization.get("required_task_artifacts")
    require(
        task_artifacts
        == [
            "source_manifest.json",
            "task_to_span_matrix.json",
            "atom_registry.json",
            "atom_dag.json",
            "candidate_manifest.json",
            "model_visible_payload_manifest.json",
            "reducer_runtime_manifest.json",
            "reducer_input_manifest.json",
            "reducer_enumeration_manifest.json",
            "public_fixture_manifest.json",
            "private_registry_A_manifest.json",
            "private_registry_B_manifest.json",
            "adapter_manifest.json",
            "reference_implementation_manifest.json",
            "scorer_manifest.json",
            "differential_test_report.json",
            "semantic_audit.json",
        ],
        "task artifact contract",
    )
    candidate_manifest = materialization.get("candidate_manifest", {})
    require(candidate_manifest.get("B_contract") == {"candidate_id": "B_empty_artifact", "canonical_bytes": "zero-length byte string", "bytes_length": 0, "sha256": EMPTY_SHA256, "paper_atom_count": 0, "strict_subset_fields_exempt": True}, "baseline payload contract")
    require(candidate_manifest.get("schedule_candidate_ids") == EXPECTED_CANDIDATE_IDS, "candidate schedule mapping")
    require(
        candidate_manifest.get("atom_registry_document_schema", {}).get("opaque_atom_id_regex")
        == "^a_[0-9a-f]{16}$",
        "opaque atom materialization schema",
    )
    require(
        candidate_manifest.get("atom_registry_document_schema", {}).get(
            "opaque_atom_id_derivation"
        )
        == construction["canonical_atom_identity"]["formula"],
        "atom-ID derivation cross-binding",
    )
    require(
        candidate_manifest.get("reducer_input_document_schema", {}).get("exact_atom_fields")
        == ["atom_id", "dependency_ids", "rendered_token_count"],
        "reducer input schema",
    )
    require(
        candidate_manifest.get("reducer_enumeration_document_schema", {}).get(
            "retained_token_ratio_precision_decimals"
        )
        == 12,
        "reducer enumeration precision",
    )
    require(
        candidate_manifest.get("runtime_manifest_schema", {}).get("tokenizer")
        == {"package": "tiktoken", "version": "0.12.0", "encoding": "cl100k_base"},
        "materialized tokenizer schema",
    )
    require(
        "all_chains"
        in candidate_manifest.get("ladder_chain_audit_schema", {}).get("required_fields", []),
        "ladder complete-chain binding",
    )
    require(
        candidate_manifest.get("alternate_reducer_audit_schema")
        == {
            "required_on_secondary_tasks": True,
            "null_on_other_tasks": True,
            "reducers": {
                "dag_greedy_ratio_60_v1": {
                    "candidate_id": "alternate_dag_greedy",
                    "enumeration_field": "eligible_trajectory_states",
                },
                "source_window_ratio_60_v1": {
                    "candidate_id": "alternate_source_window",
                    "enumeration_field": "eligible_closed_windows",
                },
            },
            "required_fields_per_reducer": [
                "selection_rule_id",
                "enumeration",
                "complete_enumeration_sha256",
                "selected_candidate_id",
            ],
            "selection_key": [
                "minimum_absolute_distance_to_0.60",
                "fewer_rendered_tokens",
                "lexicographic_atom_ids",
            ],
            "verifier_recomputes_both_enumerations": True,
        },
        "alternate reducer audit schema",
    )
    support_schemas = materialization.get("support_artifact_schemas", {})
    require(
        "hard_contract_ids"
        in support_schemas.get("scorer_manifest.json", {}).get(
            "required_fields", []
        ),
        "scorer hard-contract ordering schema",
    )
    require(
        support_schemas.get("differential_test_report.json", {}).get(
            "terminal_score_semantics_passed"
        )
        is True
        and support_schemas.get("differential_test_report.json", {}).get(
            "minimum_terminal_score_case_count"
        )
        == 5,
        "terminal-score differential test schema",
    )
    payload = materialization.get("model_visible_payload_contract", {})
    require(
        payload.get("canonical_payload_composition")
        == {
            "magic_ascii_line": "EFFECTSLICE_MODEL_VISIBLE_PAYLOAD_V1",
            "field_order": [
                "task_scaffold",
                "fixture_payload",
                "candidate_artifact",
            ],
            "field_encoding": (
                "For each field append ASCII label, ':', ASCII decimal byte length, LF, "
                "the exact field bytes, and LF. Prefix the magic line plus LF. No Unicode, "
                "newline, whitespace, JSON, or empty-artifact normalization is permitted."
            ),
            "B_attachment": (
                "candidate_artifact has decimal length 0 and contributes no bytes"
            ),
            "verifier_reconstructs_bytes": True,
        },
        "canonical payload byte composition",
    )
    wire = payload.get("wire_request_composition", {})
    require(
        wire.get("request_template_schema")
        == "effectslice-fg1-request-template.v1"
        and wire.get("template_required_fields")
        == [
            "schema_version",
            "model_slot_id",
            "exact_alias",
            "base_request",
            "model_json_pointer",
            "payload_json_pointer",
            "decoding_field_json_pointers",
        ]
        and wire.get("streaming") is False
        and wire.get("verifier_reconstructs_bytes") is True
        and "Deep-copy base_request" in wire.get("construction", "")
        and "ensure_ascii=false, then one LF" in wire.get("construction", ""),
        "wire request reconstruction contract",
    )
    for field in (
        "F_I_canonical_payload_sha256_equal",
        "F_I_artifact_sha256_equal",
        "F_I_serialized_wire_request_sha256_equal",
    ):
        require(payload.get(field) is True, f"F/I payload binding: {field}")
    require(
        payload.get("cross_model_frozen_fields")
        == [
            "task_scaffold_sha256",
            "fixture_manifest_sha256",
            "fixture_payload_sha256",
            "scorer_manifest_sha256",
            "candidate_artifact_sha256",
            "canonical_model_visible_payload_sha256",
            "private_registry_manifest_sha256",
        ],
        "cross-model frozen-input binding",
    )
    require(
        set(payload.get("digest_path_fields", {}))
        == {
            "task_scaffold_sha256",
            "fixture_manifest_sha256",
            "fixture_payload_sha256",
            "scorer_manifest_sha256",
            "candidate_artifact_sha256",
            "canonical_model_visible_payload_sha256",
            "serialized_wire_request_sha256",
            "decoding_config_sha256",
            "private_registry_manifest_sha256",
        },
        "typed digest-path binding",
    )
    require(
        payload.get("typed_path_constraints")
        == {
            "task_scaffold_path": "task_scaffold.md",
            "fixture_manifest_path": "public_fixture_manifest.json",
            "fixture_payload_path": "fixtures/{registry_id}.json",
            "scorer_manifest_path": "scorer_manifest.json",
            "candidate_artifact_path": "candidate_manifest.artifact_path[candidate_id]",
            "canonical_model_visible_payload_path": "payloads/{execution_id}.txt",
            "serialized_wire_request_path": "requests/{execution_id}.json",
            "decoding_config_path": "decoding/{model_slot_id}.json",
            "private_registry_manifest_path": "private_registry_{registry_id}_manifest.json",
        },
        "typed payload paths",
    )
    require(
        payload.get("task_wide_frozen_fields")
        == [
            "task_scaffold_sha256",
            "fixture_manifest_sha256",
            "scorer_manifest_sha256",
        ]
        and payload.get("task_registry_frozen_fields")
        == ["fixture_payload_sha256", "private_registry_manifest_sha256"]
        and payload.get("model_slot_wide_frozen_fields")
        == ["decoding_config_sha256"],
        "frozen-input scopes",
    )
    result_contract = materialization.get("result_canonicalization_contract", {})
    require(
        result_contract.get("required_result_row_fields")
        == EXPECTED_RESULT_ROW_FIELDS,
        "result-row canonicalization fields",
    )
    require(
        result_contract.get("result_row_json_schema")
        == expected_result_row_schema(),
        "registered typed result-row schema",
    )
    expected_termination_compatibility = {
        "provider_or_model_unavailable": ["not_dispatched"],
        "transport_terminal_failure": ["transport_failure"],
        "completed_body_outcomes": [
            "integrity_or_digest_failure",
            "malformed_or_no_submission",
            "action_budget_exhausted",
            "hard_contract_failure",
            "score_shortfall",
            "operational_success",
        ],
        "completed_body_reasons": ["eos", "length", "provider_stop"],
        "length_does_not_override_scorer_or_terminal_outcome": True,
    }
    require(
        result_contract.get("termination_compatibility")
        == expected_termination_compatibility,
        "termination/outcome compatibility contract",
    )
    require(
        result_contract.get("result_row_cross_field_contract")
        == expected_result_row_cross_field_contract(),
        "result-row cross-field contract",
    )
    require(
        result_contract.get("slot_response_contracts")
        == expected_slot_response_contracts()
        and result_contract.get("slot_response_contract_binding")
        == {
            "manifest_must_deep_equal_registration": True,
            "canonical_json_sha256_required": True,
            "provider_default_or_runtime_pointer_selection_forbidden": True,
        },
        "slot response parsing contracts",
    )
    require(
        result_contract.get("parser_golden_case_contracts")
        == expected_parser_golden_case_contracts(),
        "parser golden case contracts",
    )
    require(
        "complete response-body bytes"
        in result_contract.get("raw_response_bytes", "")
        and "strict UTF-8 JSON"
        in result_contract.get("canonical_output_bytes", "")
        and "apply Unicode NFC"
        in result_contract.get("canonical_output_bytes", "")
        and "first EOS token inclusive"
        in result_contract.get("generated_token_ids", "")
        and "exact hard_contract_ids order"
        in result_contract.get("hard_contract_vector", "")
        and result_contract.get("parser_and_schema_hash_bound_before_calls")
        is True,
        "result byte and token canonicalization",
    )
    replacement_contract = materialization.get("replacement_policy_contract", {})
    require(
        replacement_contract.get("reason_codes")
        == EXPECTED_REPLACEMENT_REASON_CODES
        and replacement_contract.get("current_registration_is_immutable")
        is True
        and replacement_contract.get("amendments_must_be_empty")
        is True
        and replacement_contract.get("nonempty_amendment_requires_successor_registration")
        is True
        and replacement_contract.get("outcome_access") == "forbidden"
        and replacement_contract.get("no_in_place_task_rewrite") is True
        and "lowest-ranked eligible reserve"
        in replacement_contract.get("successor_registration_rule", ""),
        "materialization replacement policy",
    )
    require(materialization.get("schedule_counts") == {"required_remote_rows": 1200, "required_local_rows": 96, "required_total_rows": 1296, "optional_remote_template_rows": 192}, "materialization counts")
    require(
        materialization.get("schedule_family_products") == EXPECTED_SCHEDULE_PRODUCTS,
        "schedule family Cartesian products",
    )
    require(
        materialization.get("global_artifacts") == EXPECTED_GLOBAL_ARTIFACTS,
        "global materialization artifacts",
    )
    require(
        set(materialization.get("global_artifact_schemas", {}))
        == {
            "request_template_manifest",
            "model_preflight_manifest",
            "result_canonicalization_manifest",
            "open_anchor_runtime_manifest",
            "replacement_amendment_manifest",
            "analysis_implementation_manifest",
            "implementation_source_audit_manifest",
            "final_anchor_manifest",
        },
        "global artifact schemas",
    )
    global_schemas = materialization["global_artifact_schemas"]
    require(
        global_schemas["request_template_manifest"].get(
            "output_limit_json_pointer_by_slot"
        )
        == {
            "deepseek_primary": "/max_tokens",
            "gpt_5_5": "/max_output_tokens",
            "gpt_5_6_sol": "/max_output_tokens",
            "gpt_5_6_terra": "/max_output_tokens",
            "claude_opus_4_7": "/max_tokens",
            "open_seed_anchor": "/max_new_tokens",
        },
        "provider-native output limit pointers",
    )
    preflight_manifest_schema = global_schemas["model_preflight_manifest"]
    require(
        {
            "request_template_sha256",
            "response_contract_sha256",
            "request_format_valid",
            "response_format_valid",
        }
        <= set(preflight_manifest_schema.get("slot_required_fields", []))
        and preflight_manifest_schema.get("available_requires_both_format_valid")
        is True
        and preflight_manifest_schema.get(
            "credentials_must_be_environment_or_secret_store_only"
        )
        is True,
        "model format-only preflight contract",
    )
    result_manifest_schema = global_schemas["result_canonicalization_manifest"]
    require(
        result_manifest_schema["golden_tests_passed"]
        is True
        and result_manifest_schema.get("verifier_executes_golden_suite")
        is True
        and result_manifest_schema.get("golden_execution_protocol")
        == "python_isolated_json_stdin_stdout_canonical_v1"
        and result_manifest_schema.get("schema_version")
        == "effectslice-fg1-result-canonicalization.v2"
        and result_manifest_schema.get("slot_response_contracts")
        == expected_slot_response_contracts()
        and result_manifest_schema.get("golden_case_contracts")
        == expected_parser_golden_case_contracts()
        and {
            "implementation_builder_identity",
            "slot_response_contracts",
            "slot_response_contracts_sha256",
            "golden_cases",
        }
        <= set(result_manifest_schema["required_fields"])
        and global_schemas["analysis_implementation_manifest"][
            "golden_tests_passed"
        ]
        is True
        and global_schemas["analysis_implementation_manifest"].get(
            "verifier_executes_golden_suite"
        )
        is True
        and global_schemas["analysis_implementation_manifest"].get(
            "golden_execution_protocol"
        )
        == "python_isolated_json_stdin_stdout_canonical_v1"
        and {
            "analysis_result_schema_path",
            "analysis_result_schema_sha256",
            "implementation_builder_identity",
        }
        <= set(global_schemas["analysis_implementation_manifest"]["required_fields"]),
        "golden implementation gates",
    )
    source_audit_schema = global_schemas["implementation_source_audit_manifest"]
    require(
        source_audit_schema.get("schema_version")
        == "effectslice-fg1-implementation-source-audit.v1"
        and source_audit_schema.get("required_component_ids")
        == [
            "result_canonicalizer",
            "analysis_implementation",
            "open_anchor_preflight",
        ]
        and source_audit_schema.get("required_checks_by_component")
        == EXPECTED_IMPLEMENTATION_SOURCE_AUDIT_CHECKS
        and source_audit_schema.get("review_status") == "pass"
        and source_audit_schema.get("auditor_must_differ_from_builder") is True
        and source_audit_schema.get(
            "all_implementation_hashes_must_match_bound_manifests"
        )
        is True,
        "independent implementation source-audit gate",
    )
    qwen_schema = global_schemas["open_anchor_runtime_manifest"]
    require(
        qwen_schema.get("model_slot_id") == "open_seed_anchor"
        and qwen_schema.get("exact_alias") == "Qwen/Qwen2.5-Coder-7B-Instruct"
        and qwen_schema.get("generation_config")
        == {
            "do_sample": False,
            "temperature": None,
            "top_p": None,
            "top_k": None,
            "num_beams": 1,
            "max_new_tokens": 1024,
            "eos_token_id": [151645, 151643],
            "pad_token_id": 151643,
            "use_cache": True,
            "stop_strings": [],
            "stop_behavior": "first_eos_inclusive_or_max_new_tokens",
        }
        and qwen_schema.get("file_inventory_contract", {}).get(
            "shard_index_must_exactly_cover_weight_files"
        )
        is True
        and qwen_schema.get("file_inventory_contract", {}).get(
            "model_root_must_be_snapshot_revision_directory"
        )
        is True
        and qwen_schema.get("file_inventory_contract", {}).get(
            "unlisted_discovered_files_forbidden"
        )
        is True
        and qwen_schema.get("file_inventory_contract", {}).get(
            "tokenizer_discovery_globs"
        )
        == [
            "tokenizer*",
            "vocab.*",
            "merges.txt",
            "special_tokens_map.json",
            "added_tokens.json",
            "chat_template.jinja",
        ]
        and qwen_schema.get("file_inventory_contract", {}).get(
            "model_root_repository_directory"
        )
        == "models--Qwen--Qwen2.5-Coder-7B-Instruct"
        and qwen_schema.get("required_model_config")
        == {
            "model_type": "qwen2",
            "architecture": "Qwen2ForCausalLM",
            "hidden_size": 3584,
            "intermediate_size": 18944,
            "num_hidden_layers": 28,
            "num_attention_heads": 28,
            "num_key_value_heads": 4,
            "vocab_size": 152064,
            "max_position_embeddings": 131072,
        }
        and qwen_schema.get("allowed_dtype") == ["bfloat16"]
        and qwen_schema.get("allowed_quantization") == ["none"]
        and qwen_schema.get("preflight_execution_protocol")
        == "python_isolated_json_stdin_stdout_canonical_v1"
        and qwen_schema.get("preflight_timeout_seconds") == 1800
        and "implementation_builder_identity" in qwen_schema.get("required_fields", [])
        and qwen_schema.get("determinism_required")
        == {
            "torch_use_deterministic_algorithms": True,
            "cudnn_benchmark": False,
            "cudnn_deterministic": True,
            "cuda_matmul_allow_tf32": False,
            "cudnn_allow_tf32": False,
            "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
            "PYTHONHASHSEED": "0",
        },
        "open-anchor runtime schema",
    )
    preflight_schema = qwen_schema.get("preflight_result_schema", {})
    preflight_required = qwen_schema.get("preflight_required_result_fields")
    require(
        preflight_schema.get("type") == "object"
        and preflight_schema.get("required") == preflight_required
        and set(preflight_schema.get("properties", {})) == set(preflight_required)
        and preflight_schema.get("additionalProperties") is False
        and preflight_schema.get("properties", {})
        .get("exact_alias", {})
        .get("const")
        == "Qwen/Qwen2.5-Coder-7B-Instruct"
        and preflight_schema.get("properties", {})
        .get("model_loaded", {})
        .get("const")
        is True
        and preflight_schema.get("properties", {})
        .get("repeat_generated_token_ids_equal", {})
        .get("const")
        is True
        and preflight_schema.get("properties", {})
        .get("generated_token_ids", {})
        .get("maxItems")
        == 1024,
        "open-anchor preflight result schema",
    )
    require(
        global_schemas["replacement_amendment_manifest"].get(
            "amendments_must_be_empty"
        )
        is True
        and global_schemas["replacement_amendment_manifest"].get(
            "nonempty_rows_forbidden"
        )
        is True,
        "replacement amendment empty gate",
    )
    row_schema = materialization.get("schedule_row_schema", {})
    require(row_schema.get("unique_key") == ["execution_id"], "schedule unique key")
    require(
        row_schema.get("pair_or_block_key")
        == [
            "execution_family",
            "task_id",
            "variant_id",
            "model_slot_id",
            "block_id",
        ],
        "schedule pair key",
    )
    require(row_schema.get("required_fields") == EXPECTED_ROW_FIELDS, "schedule row schema")
    require(row_schema.get("primary_orders_by_block") == PRIMARY_ORDERS, "materialized primary order")
    require(row_schema.get("two_arm_orders_by_block") == PAIR_ORDERS, "materialized pair order")
    require(row_schema.get("BFSI_orders_by_block") == BFSI_ORDERS, "materialized BFSI order")
    sequence = row_schema.get("global_sequence_order", {})
    require(sequence.get("family_order") == FAMILY_ORDER, "global family order")
    require(sequence.get("secondary_task_order") == SECONDARY_TASKS, "global secondary task order")
    require(sequence.get("required_closed_model_order") == REQUIRED_CLOSED_MODELS, "global model order")
    primary_task_order = sequence.get("primary_task_order")
    require(primary_task_order == EXPECTED_PRIMARY_TASK_ORDER, "primary global task order")
    require(set(primary_task_order) == set(task_ids), "primary global task membership")
    overlap = materialization.get("parent_overlap_audit", {})
    require(overlap.get("parents") == ["confirmation_v4", "confirmation_v5r2"], "parent overlap targets")
    require(overlap.get("required_zero_intersections") == OVERLAP_FIELDS, "parent overlap fields")
    require(overlap.get("normalized_value_manifest_scopes") == OVERLAP_SCOPES, "parent overlap scopes")
    require(overlap.get("verifier_recomputes_intersections") is True, "parent overlap recomputation")
    require(
        overlap.get("source_path_bases")
        == ["materialization_root", "forward_root", "run_root"]
        and overlap.get("allowed_extractors")
        == [
            "schedule_rows_field",
            "recursive_key",
            "json_pointer_list",
            "file_sha256",
        ]
        and overlap.get("source_paths_must_equal_complete_registered_glob_expansion")
        is True
        and overlap.get("every_scope_field_value_list_must_be_nonempty") is True
        and overlap.get("declared_values_must_equal_values_reextracted_from_hashed_sources")
        is True,
        "parent overlap source recomputation",
    )
    require(
        overlap.get("source_registry") == _expected_overlap_source_registry(),
        "fixed overlap source registry",
    )
    hash_contract = materialization.get("hash_contract", {})
    require(
        {
            key: hash_contract.get(key)
            for key in (
                "algorithm",
                "all_materialized_inputs_listed",
                "manifest_self_hash_excluded",
                "bundle_hash_from_canonical_sorted_path_digest_pairs",
                "post_anchor_mutation_forbidden",
                "control_file_exclusions",
            )
        }
        == {
            "algorithm": "sha256",
            "all_materialized_inputs_listed": True,
            "manifest_self_hash_excluded": True,
            "bundle_hash_from_canonical_sorted_path_digest_pairs": True,
            "post_anchor_mutation_forbidden": True,
            "control_file_exclusions": [
                "immutable_file_manifest.json",
                "final_anchor_manifest.json",
            ],
        },
        "materialization hash contract",
    )

    fixture_rows = build_validation_fixture_rows(prereg_root)
    require(len(fixture_rows) == 1296, "local Cartesian-product fixture")

    analyzer = _load_operating_analyzer()
    if prereg_root.resolve() == PREREG_ROOT.resolve():
        require(operating == analyzer.analyze(), "stale SLA operating analysis")
    require(operating.get("total_count_states") == 4**8, "SLA state enumeration")
    require(operating.get("passing_count_states") == 81, "SLA passing state count")
    require("factorized_diagnostic_scenarios" not in operating, "factorized pseudo-probabilities remain")

    immutable_inputs = experiment.get("forward_only_scope", {}).get("immutable_inputs")
    require(isinstance(immutable_inputs, list) and len(immutable_inputs) == 3, "forward input bindings")
    for item in immutable_inputs[:2]:
        path = RUN_ROOT / item["path"]
        require(path.is_file(), f"missing frozen parent input: {path}")
        require(_sha256(path) == item["sha256"], f"frozen parent changed: {path}")

    metadata_count = _verify_metadata_manifest(repo, registry, metadata)
    if verify_bundle:
        require(prereg_root.resolve() == PREREG_ROOT.resolve(), "bundle verification requires canonical root")
        bundle_sha256 = _verify_hash_manifest()
    else:
        bundle_sha256 = "semantic-only"

    return {
        "status": "passed",
        "registration_status": STATUS,
        "selected_papers": len(papers),
        "independent_papers": 12,
        "nested_task_decisions": len(task_ids),
        "domains": dict(sorted(domains.items())),
        "primary_remote_conversations": design["remote_conversations"],
        "required_remote_conversation_cap": 1200,
        "open_anchor_local_execution_cap": 96,
        "required_execution_cap": 1296,
        "optional_remote_conversation_cap": 192,
        "required_closed_model_slots": len(required_closed),
        "optional_closed_model_slots": len(optional),
        "open_seed_anchor": anchor["model_alias"],
        "figure_contracts": EXPECTED_FIGURES,
        "frozen_parent_hashes_verified": 2,
        "metadata_evidence_files_verified": metadata_count,
        "materialization_fixture_rows_verified": len(fixture_rows),
        "bundle_sha256": bundle_sha256,
    }


def audit(
    prereg_root: Path | None = None,
    *,
    verify_bundle: bool = True,
) -> dict[str, object]:
    root = (prereg_root or PREREG_ROOT).resolve()
    try:
        return _audit(root, verify_bundle)
    except VerificationError:
        raise
    except (KeyError, IndexError, TypeError, ValueError, OSError, StopIteration) as exc:
        raise VerificationError(f"malformed preregistration artifact: {exc}") from exc
