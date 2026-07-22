from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREREG = ROOT / "preregistration"
STATUS = "stage_2_2_design_registered_materialization_pending"
SECONDARY_TASKS = ["NLP-LLM-01", "SE-PE-01", "DATA-HDB-01", "AGENT-TF-01"]
NORMALIZED_MAX_OUTPUT_TOKENS = 1024
REQUIRED_MODEL_SLOTS = [
    "deepseek_primary",
    "gpt_5_5",
    "gpt_5_6_sol",
    "gpt_5_6_terra",
    "claude_opus_4_7",
    "open_seed_anchor",
]


def slot_response_contracts() -> list[dict[str, object]]:
    common_dispatch = {
        "transport_terminal_failure": "transport_failure",
        "provider_or_model_unavailable": "not_dispatched",
    }
    chat_completion = {
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
            "dispatch_state_map": common_dispatch,
        },
    }
    responses = {
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
            "dispatch_state_map": common_dispatch,
        },
    }
    anthropic = {
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
            "dispatch_state_map": common_dispatch,
        },
    }
    local = {
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
            "dispatch_state_map": common_dispatch,
        },
    }

    def bind(slot_id: str, exact_alias: str, value: dict[str, object]) -> dict[str, object]:
        return {"model_slot_id": slot_id, "exact_alias": exact_alias, **value}

    return [
        bind("deepseek_primary", "deepseek-v4-flash", chat_completion),
        bind("gpt_5_5", "gpt-5.5", responses),
        bind("gpt_5_6_sol", "gpt-5.6-sol", responses),
        bind("gpt_5_6_terra", "gpt-5.6-terra", responses),
        bind("claude_opus_4_7", "claude-opus-4-7", anthropic),
        bind("open_seed_anchor", "Qwen/Qwen2.5-Coder-7B-Instruct", local),
    ]


def parser_golden_case_contracts() -> list[dict[str, object]]:
    return [
        {
            "case_id": "deepseek_provider_stop",
            "model_slot_id": "deepseek_primary",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "provider_stop",
            "provider_finish_reason": "stop",
        },
        {
            "case_id": "deepseek_length_scored",
            "model_slot_id": "deepseek_primary",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "length",
            "provider_finish_reason": "length",
        },
        {
            "case_id": "gpt_5_5_completed",
            "model_slot_id": "gpt_5_5",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "provider_stop",
            "provider_finish_reason": "completed",
        },
        {
            "case_id": "gpt_5_6_sol_length_scored",
            "model_slot_id": "gpt_5_6_sol",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "length",
            "provider_finish_reason": "max_output_tokens",
        },
        {
            "case_id": "gpt_5_6_terra_null_finish",
            "model_slot_id": "gpt_5_6_terra",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "provider_stop",
            "provider_finish_reason": None,
        },
        {
            "case_id": "claude_provider_stop",
            "model_slot_id": "claude_opus_4_7",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "provider_stop",
            "provider_finish_reason": "end_turn",
        },
        {
            "case_id": "claude_length_scored",
            "model_slot_id": "claude_opus_4_7",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "length",
            "provider_finish_reason": "max_tokens",
        },
        {
            "case_id": "qwen_eos",
            "model_slot_id": "open_seed_anchor",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "eos",
            "provider_finish_reason": "eos",
        },
        {
            "case_id": "qwen_length_scored",
            "model_slot_id": "open_seed_anchor",
            "dispatch_state": "completed_body",
            "terminal_outcome": "operational_success",
            "termination_reason": "length",
            "provider_finish_reason": "length",
        },
        {
            "case_id": "completed_malformed_body",
            "model_slot_id": "deepseek_primary",
            "dispatch_state": "completed_body",
            "terminal_outcome": "malformed_or_no_submission",
            "termination_reason": "provider_stop",
            "provider_finish_reason": None,
        },
        {
            "case_id": "terminal_transport_failure",
            "model_slot_id": "deepseek_primary",
            "dispatch_state": "transport_terminal_failure",
            "terminal_outcome": "transport_terminal_failure",
            "termination_reason": "transport_failure",
            "provider_finish_reason": None,
        },
        {
            "case_id": "model_unavailable_not_dispatched",
            "model_slot_id": "gpt_5_5",
            "dispatch_state": "provider_or_model_unavailable",
            "terminal_outcome": "provider_or_model_unavailable",
            "termination_reason": "not_dispatched",
            "provider_finish_reason": None,
        },
    ]


def implementation_source_audit_checks() -> dict[str, list[str]]:
    return {
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


def write_json(name: str, value: dict[str, object]) -> None:
    path = PREREG / name
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )


def repeatability_reduction() -> dict[str, object]:
    return {
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


def cost_measurement_contract() -> dict[str, object]:
    return {
        "scope": "descriptive registered-benchmark resource use; not a model ranking",
        "raw_unit": "one registered execution row",
        "deterministic_artifact_endpoints": {
            "candidate_artifact_bytes": "Exact byte length of the frozen candidate artifact.",
            "candidate_artifact_cl100k_tokens": (
                "Exact tiktoken==0.12.0 cl100k_base count of the canonical rendered "
                "candidate artifact; the common task scaffold is excluded."
            ),
            "canonical_model_visible_payload_bytes": (
                "Exact byte length of the frozen canonical model-visible payload."
            ),
        },
        "provider_reported_token_endpoints": {
            "input_tokens": "Provider-returned input-token usage for the terminal response.",
            "output_tokens": "Provider-returned output-token usage for the terminal response.",
            "total_tokens": "Provider-returned total-token usage for the terminal response.",
            "cached_input_tokens": (
                "Provider-returned cached-input count when separately exposed; otherwise null."
            ),
            "validation": (
                "Counts must be nonnegative integers. When input, output, and total are all "
                "reported, total must equal input plus output under the endpoint's frozen "
                "provider semantics. Otherwise input, output, and total are all null and "
                "provider_usage_missing_reason records why; partial-null tuples are invalid. "
                "Cached-input tokens are independently nullable."
            ),
        },
        "latency_endpoints_ms": {
            "terminal_attempt_elapsed_ms": (
                "Monotonic elapsed time from dispatch of the final attempted request to "
                "complete response-body receipt or terminal transport classification, "
                "rounded once to the nearest millisecond."
            ),
            "total_execution_elapsed_ms": (
                "Monotonic elapsed time from dispatch of the first attempted request to the "
                "terminal classification, including prior attempts and registered retry waits."
            ),
            "retry_sleep_elapsed_ms": (
                "Sum of measured registered backoff, Retry-After, and deterministic-jitter "
                "waits, rounded once to the nearest millisecond."
            ),
            "retry_overhead_ms": (
                "max(0, total_execution_elapsed_ms - terminal_attempt_elapsed_ms); this "
                "contains prior-attempt time plus retry waits and is never pooled with model "
                "latency. For dispatched rows total time must be at least terminal-attempt "
                "time. Because total, terminal, and sleep durations are independently rounded "
                "once, retry overhead must be at least retry sleep minus one millisecond."
            ),
            "clock": "one process-local monotonic_ns clock; UTC timestamps are audit metadata only",
        },
        "attempt_fields": [
            "attempt_index",
            "attempt_status_class",
            "attempt_elapsed_ms",
            "retry_sleep_after_attempt_ms",
        ],
        "missingness": {
            "artifact_endpoints": "Never missing after materialization; a mismatch is Invalid.",
            "provider_tokens": (
                "Null when the terminal response does not expose a valid usage tuple; never "
                "impute with cl100k_base or another model's tokenizer."
            ),
            "latency": (
                "Null only when no request was dispatched, such as preflight unavailability. "
                "Once any attempt is dispatched, attempt and total timings are mandatory even "
                "for terminal transport failure."
            ),
            "paired_comparison": (
                "A blockwise S-F resource delta is valid only when both endpoints are non-null; "
                "report valid_pairs/6 and do not impute missing members."
            ),
        },
        "task_level_reduction": {
            "cell": "task x model slot x candidate",
            "registered_blocks": 6,
            "raw_display": "Show all six block-ordered values including nulls.",
            "summary": (
                "For each endpoint report non-null count/6, median, minimum, maximum, and sum "
                "over non-null values; undefined statistics remain null at count zero."
            ),
            "paired_S_minus_F": (
                "For each resource endpoint report six block-ordered S-F deltas and the same "
                "valid-count, median, range, and sum reduction over valid pairs."
            ),
            "aggregation_boundary": (
                "Never pool model slots, tasks, or structurally unrun cells; cross-task panels "
                "retain task-model-candidate cells."
            ),
            "missing_usage_reason_counts": (
                "Report counts for every frozen provider_usage_missing_reason code in each "
                "task-model-candidate cell; null denotes a complete reported usage tuple."
            ),
        },
        "monetary_cost": {
            "default": "not_reported",
            "conditional_rule": (
                "Report estimated USD cost only if a dated public price table, currency, input "
                "and output rates, original billing units, normalized USD-per-token rates, and "
                "its content hash are frozen in the final materialization anchor before calls."
            ),
            "formula": (
                "input_tokens * input_rate_usd_per_token + "
                "output_tokens * output_rate_usd_per_token"
            ),
            "missingness": "Null when token usage or a frozen price input is absent.",
            "role": "appendix descriptive endpoint only; never a primary success criterion",
        },
    }


def result_row_cross_field_contract() -> dict[str, object]:
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


def open_anchor_preflight_result_schema() -> dict[str, object]:
    hex_digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    properties: dict[str, object] = {
        "schema_version": {
            "type": "string",
            "const": "effectslice-fg1-open-anchor-preflight.v1",
        },
        "model_slot_id": {"type": "string", "const": "open_seed_anchor"},
        "exact_alias": {
            "type": "string",
            "const": "Qwen/Qwen2.5-Coder-7B-Instruct",
        },
        "revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
        "model_file_inventory_sha256": hex_digest,
        "generation_config_sha256": hex_digest,
        "input_ids_sha256": hex_digest,
        "prompt_token_count": {"type": "integer", "minimum": 1},
        "generated_token_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 1024,
            "items": {"type": "integer", "minimum": 0},
        },
        "canonical_output_sha256": hex_digest,
        "model_loaded": {"type": "boolean", "const": True},
        "tokenizer_loaded": {"type": "boolean", "const": True},
        "offline_mode": {"type": "boolean", "const": True},
        "repeat_generated_token_ids_equal": {"type": "boolean", "const": True},
        "repeat_canonical_output_equal": {"type": "boolean", "const": True},
    }
    return {
        "type": "object",
        "required": list(properties),
        "properties": properties,
        "additionalProperties": False,
    }


def result_row_schema_contract() -> dict[str, object]:
    nullable_hash = {
        "type": ["string", "null"],
        "pattern": "^[0-9a-f]{64}$",
    }
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


def overlap_source_registry() -> dict[str, object]:
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
    registry: dict[str, object] = {}
    for field in (
        "execution_id",
        "pair_id",
        "private_case_id",
        "derived_seed",
        "fixture_payload_sha256",
        "serialized_wire_request_sha256",
    ):
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
        parent_root_kind, parent_glob, parent_key = parent_extractors[field]
        scopes: dict[str, object] = {"effectslice_fg1": fg1}
        for scope, version, count in (
            ("confirmation_v4", "confirmation_v4", 180 if "transcript" in parent_glob else 60 if "pair_manifest" in parent_glob else 2),
            ("confirmation_v5r2", "confirmation_v5r2", 54 if "transcript" in parent_glob else 18 if "pair_manifest" in parent_glob else 1),
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


def build_experiment_plan() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-experiment-plan.v2",
        "registration_status": STATUS,
        "stage": "2.2",
        "study_id": "EffectSlice-FG1",
        "forward_only_scope": {
            "statement": (
                "EffectSlice-FG1 is a new SLA instance after V4/V5. It shares "
                "protocol structure but does not rewrite, reopen, pool into, "
                "supersede, or statistically reuse either accepted schedule."
            ),
            "design_checkpoint_commit": (
                "aedd758e5e6ab1bac924a84e52e5d77550d7b208"
            ),
            "immutable_inputs": [
                {
                    "path": "artifacts/confirmation_v4/preregistration.json",
                    "sha256": (
                        "b5970f270d500fa526d478ba77774ab6095232f4573d092663"
                        "efb9061d816fbb"
                    ),
                },
                {
                    "path": "artifacts/confirmation_v5r2/preregistration.json",
                    "sha256": (
                        "6083729477053feeee328f79f9fddfcb83acdaae7410debdab"
                        "5218b4e18e24eb"
                    ),
                },
                {
                    "path": (
                        "forward_extensions/generalization_2026-07-21/"
                        "stage_report_2_6.json"
                    ),
                    "role": "passed literature and venue evidence",
                    "sha256": (
                        "eefa5d736c86ee451d2b2449a82ff8e98f5ec912bc42738d84"
                        "b44e8b0cf753d4"
                    ),
                },
            ],
            "no_provider_calls_before_final_anchor": True,
        },
        "research_questions": [
            {
                "id": "RQ1",
                "question": (
                    "Can the registered B/F/S protocol issue complete task-local "
                    "decisions across 12 papers and four mechanism domains?"
                ),
            },
            {
                "id": "RQ2",
                "question": (
                    "How heterogeneous are paired F-B, S-B, and S-F effects when "
                    "tasks are nested within papers?"
                ),
            },
            {
                "id": "RQ3",
                "question": (
                    "How do structural restoration, reducer choice, compression, "
                    "reliability, and cost trade off on four frozen tasks?"
                ),
            },
            {
                "id": "RQ4",
                "question": (
                    "What exact candidate-state agreement and F/I repeatability are "
                    "observed across required models on four prespecified sentinel tasks?"
                ),
            },
            {
                "id": "RQ5",
                "question": (
                    "How stable are primary task decisions and identified bounds under "
                    "the registered SLA grid, leave-one-block-out, and leave-one-paper-out "
                    "sensitivity analyses?"
                ),
            },
        ],
        "hypotheses": {
            "control_sanity": (
                "At least three of four planted-redundancy controls and all four "
                "byte-identical controls produce SanityPass; all four destructive-core "
                "controls produce SanityPass under their negative-control rule. "
                "Controls are sanity states, not admission or calibration data."
            ),
            "decision_coverage": (
                "At least 20 of 24 natural task decisions are valid Admit or "
                "Reject states rather than Invalid."
            ),
            "natural_admission": (
                "At least 8 of 24 natural strict subsets are admitted, with one "
                "or more admissions in at least three domains."
            ),
            "forward_boundary": (
                "Failure is reported and cannot trigger edits to frozen tasks, "
                "atoms, reducers, scorers, models, registries, or thresholds."
            ),
            "benchmark_target_rationale": (
                "The 20/24 valid and 8/24 primary-admission targets are finite-benchmark "
                "engineering stress targets (83.3% coverage and 33.3% candidate yield), "
                "not significance, power, or population-generalization criteria."
            ),
        },
        "primary_design": {
            "paper_registry": "preregistration/paper_registry.json",
            "papers": 12,
            "independent_aggregate_unit": "paper",
            "independent_papers": 12,
            "tasks_per_paper": 2,
            "nested_task_decisions": 24,
            "blocks_per_task": 6,
            "registries_per_task": 2,
            "blocks_per_registry": 3,
            "conditions": ["B", "F", "S"],
            "primary_model_slot_id": "deepseek_primary",
            "condition_payload_contract": {
                "shared": (
                    "Within a registered block, B/F/S use the same model slot, task "
                    "scaffold, fixture, scorer, action budget, and decoding settings."
                ),
                "B": (
                    "B uses the canonical empty paper-artifact bytes and differs from "
                    "F/S only in the registered artifact attachment."
                ),
                "F": "F attaches the complete rendered paper artifact.",
                "S": "S attaches the primary reducer output.",
                "hash_binding": (
                    "Hash both canonical model-visible payload and serialized wire "
                    "request for every row before execution."
                ),
            },
            "remote_conversations": 432,
            "arithmetic": "12 * 2 * 6 * 3 = 432",
            "fresh_conversation_per_condition": True,
            "private_cases_per_block": 64,
            "private_cases_are_scorer_fixtures_not_independent_observations": True,
            "public_private_overlap_allowed": False,
            "maximum_parallel_workers": 2,
            "nesting_statement": (
                "Paper is the independent aggregate unit (n=12); two tasks are "
                "nested within paper and six paired blocks repeat within task."
            ),
        },
        "candidate_construction": {
            "atom_count_range": [5, 16],
            "full_artifact": (
                "F contains every registered paper-claim, implementation-guardrail, "
                "and scorer-interface atom needed for the bounded task."
            ),
            "canonical_atom_identity": {
                "formula": (
                    "a_ + first_16_lower_hex(sha256(document_sha256 + NUL + "
                    "ascii_decimal(byte_start) + NUL + ascii_decimal(byte_end) + "
                    "NUL + ascii_decimal(split_index)))"
                ),
                "semantic_names_forbidden": True,
                "unique_and_opaque_audit_required": True,
                "canonical_order": (
                    "document_sha256, byte_start, byte_end, split_index, atom_id"
                ),
            },
            "canonical_renderer": {
                "id": "effectslice_atom_renderer_v1",
                "encoding": "UTF-8 without BOM",
                "newline": "LF",
                "atom_separator": "two LF bytes",
                "artifact_only_ratio": True,
                "implementation_sha256_bound_at_materialization": True,
            },
            "canonical_tokenizer": {
                "library": "tiktoken",
                "library_version": "0.12.0",
                "encoding_name": "cl100k_base",
                "tokenizer_asset_sha256_bound_at_materialization": True,
            },
            "token_ratio_definition": (
                "token_count(canonical_render(candidate)) / "
                "token_count(canonical_render(F)); common task scaffold is excluded"
            ),
            "dag_static_validation": [
                "unique opaque atom IDs",
                "every dependency references a registered atom",
                "directed graph is acyclic",
                "registered canonical topological order is valid",
                "every retained candidate is nonempty, strict, and dependency closed",
            ],
            "primary_reducer": {
                "id": "dag_ratio_60_v1",
                "visible_fields": [
                    "atom_id",
                    "dependency_ids",
                    "rendered_token_count",
                ],
                "forbidden_fields": [
                    "paper_claim_label",
                    "hard_contract_label",
                    "guardrail_label",
                    "scorer_interface_label",
                    "public_outcome",
                    "private_outcome",
                    "model_output",
                ],
                "closure_definition": (
                    "If retained atom a depends on atom b, b is retained."
                ),
                "enumeration": (
                    "Enumerate all nonempty dependency-closed strict subsets of F."
                ),
                "target_token_retention": 0.60,
                "eligible_token_retention_interval": [0.45, 0.75],
                "tie_break_order": [
                    "minimum_absolute_distance_to_0.60",
                    "fewer_rendered_tokens",
                    "lexicographic_canonical_atom_id_list",
                ],
                "outcome_access": "forbidden",
                "input_manifest_sha256_bound_at_materialization": True,
                "enumeration_log_sha256_bound_at_materialization": True,
                "selected_output_sha256_bound_at_materialization": True,
            },
            "static_ineligibility": (
                "No eligible subset blocks this materialization anchor. Any same-domain "
                "replacement requires a separately committed successor registration before "
                "materialization resumes; the current registry and schedules are never amended "
                "in place."
            ),
            "required_bindings_before_final_anchor": [
                "legal full-text source and sha256",
                "at least two central source spans per task with byte locators",
                "task-to-span matrix and task-specificity audit",
                "atom registry, dependency DAG, and topological order",
                "canonical renderer, tokenizer assets, and reducer manifests",
                "F and all candidate artifact sha256 values",
                "public and private registry A/B sha256 values",
                "adapter, reference implementation, scorer and config sha256 values",
                "builder/auditor identities and resolution ledger",
            ],
        },
        "schedule": {
            "registry_A": {"orders": ["BFS", "FSB", "SBF"], "blocks": 3},
            "registry_B": {"orders": ["BSF", "FBS", "SFB"], "blocks": 3},
            "all_orders": ["BFS", "BSF", "FBS", "FSB", "SBF", "SFB"],
            "rule": (
                "Every task uses each order exactly once; both total and "
                "per-registry sufficiency must pass."
            ),
            "block_seed_base": 2026072100,
            "global_interleave_seed": 20260721,
            "global_interleave": (
                "Use materialization_contract.schedule_row_schema.global_sequence_order "
                "exactly: family, registered task, variant, model slot, block, then "
                "within-block order position. The registered primary task order cycles "
                "domains between task rows."
            ),
            "secondary_pair_contemporaneity": {
                "adjacent_rows_required": True,
                "unrelated_row_between_pair_forbidden": True,
                "order_codes_by_block": ["FC", "CF", "FC", "CF", "FC", "CF"],
                "failure_resume": (
                    "Exhaust the first row's registered transport attempts before its "
                    "paired row. Run the paired row unless the model slot is unavailable; "
                    "a terminally missing member makes the pair Invalid."
                ),
            },
            "model_BFSI_orders_by_block": [
                "BFIS",
                "IFSB",
                "SBFI",
                "BSIF",
                "FIBS",
                "SIFB",
            ],
            "materialization": (
                "Stage 2.3 hash-binds complete required remote and local schedules "
                "before any experimental provider call."
            ),
        },
        "scoring": {
            "private_score_range": [0.0, 1.0],
            "operational_success": (
                "All hard contracts pass and private_score >= 0.90."
            ),
            "admission_sla": {
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
                "paired_margin_rule": (
                    "S private_score >= F private_score - 0.05 in the same block"
                ),
                "all_registered_rows_terminal": True,
                "all_outputs_complete": True,
                "all_integrity_checks_pass": True,
            },
            "decision_states": {
                "Admit": "All total, per-registry, margin, and integrity gates pass.",
                "Reject": "Rows are complete and valid but one or more SLA gates fail.",
                "Invalid": (
                    "A required input, output, digest, scorer call, schedule binding, "
                    "or terminal model result is missing or corrupt after retries."
                ),
            },
            "two_arm_pair_rule": {
                "states": ["PairPass", "PairFail", "Invalid"],
                "scope": (
                    "Structural ladder and alternate-reducer F/C pairs only; these "
                    "states are never called Admit or Reject."
                ),
                "total_six_blocks": {
                    "minimum_reference_F_successes": 5,
                    "minimum_candidate_successes": 5,
                    "minimum_valid_margin_pairs": 5,
                },
                "each_three_block_registry": {
                    "minimum_reference_F_successes": 2,
                    "minimum_candidate_successes": 2,
                    "minimum_valid_margin_pairs": 2,
                },
                "margin_rule": (
                    "candidate private_score >= reference_F private_score - 0.05"
                ),
                "PairPass": "All total, registry, terminal, and integrity gates pass.",
                "PairFail": "Every row is valid but one or more pair gates fail.",
                "Invalid": "One or more required pair rows or bindings are invalid.",
            },
            "control_sanity_rules": {
                "states": ["SanityPass", "SanityFail", "Invalid"],
                "planted_redundancy_positive": {
                    "reference": "F_plus_registered_restatement_atom",
                    "candidate": "primary_F_bytes_after_only_restatement_removal",
                    "rule": "Apply the registered two_arm_pair_rule.",
                },
                "destructive_core_negative": {
                    "reference": "primary_F",
                    "candidate": "F_without_registered_destructive_target_closure",
                    "total": {
                        "minimum_reference_F_successes": 5,
                        "maximum_candidate_successes": 1,
                        "minimum_targeted_hard_contract_failures": 5,
                    },
                    "each_registry": {
                        "minimum_reference_F_successes": 2,
                        "maximum_candidate_successes": 1,
                        "minimum_targeted_hard_contract_failures": 2,
                    },
                },
                "byte_identical_identity": {
                    "reference": "primary_F",
                    "candidate": "byte_identical_primary_F",
                    "input_digest_matches_required": 6,
                    "minimum_valid_pairs": 5,
                    "minimum_operational_success_agreements": 5,
                    "minimum_hard_contract_vector_agreements": 5,
                    "minimum_score_delta_within_0.05": 5,
                    "raw_or_canonical_output_equality": "reported_descriptively",
                },
                "SanityPass": "The control-specific frozen rule passes.",
                "SanityFail": "Rows are valid but the control-specific rule fails.",
                "Invalid": "A required row, digest, or binding is invalid.",
            },
            "reject_reason_precedence": [
                "full-insufficient",
                "baseline-sensitive",
                "slice-insufficient",
                "margin-shortfall",
            ],
            "reject_reason_rule": (
                "Use the first failed reason as primary_reject_reason and preserve "
                "all failed gates as secondary flags."
            ),
            "invalid_is_orthogonal": (
                "Invalid is outside the F-by-S state space and remains in every "
                "registered denominator."
            ),
            "condition_success_is_not_candidate_admission": True,
            "admit_reject_reserved_for_complete_BFS": True,
        },
        "secondary_experiments": {
            "paper_task_ids": SECONDARY_TASKS,
            "controls": {
                "conditions": [
                    "planted_redundancy_positive",
                    "destructive_core_negative",
                    "byte_identical_identity",
                ],
                "pair": ["fresh_reference_F", "fresh_control_candidate"],
                "pair_orders_by_block": ["FC", "CF", "FC", "CF", "FC", "CF"],
                "pair_rows_are_adjacent": True,
                "blocks_per_condition_task": 6,
                "remote_conversations": 144,
                "arithmetic": "4 * 3 * 6 * 2 = 144",
                "reuse_primary_rows": False,
                "interpretation": (
                    "Control-specific SanityPass/SanityFail/Invalid only; no admission, "
                    "confusion matrix, or calibration-rate claim."
                ),
            },
            "structural_restoration_ladder": {
                "levels": [
                    "L0_primary_slice",
                    "L1_mid_restore",
                    "L2_near_full_strict",
                ],
                "construction": (
                    "Enumerate all chains S=L0 strict-subset L1 strict-subset L2 "
                    "strict-subset F in which every level is dependency closed. Choose "
                    "the chain by maximum L2 tokens, then minimum L1 distance to the "
                    "S/L2 token midpoint, fewer L1 tokens, lexicographic L1 IDs, then "
                    "lexicographic L2 IDs."
                ),
                "feasibility_gate": (
                    "At least one such three-level strict chain must exist before the "
                    "final anchor; otherwise block this materialization and create an "
                    "outcome-blind successor registration. Never reduce the registered "
                    "three-level design."
                ),
                "pair": ["fresh_F", "fresh_ladder_candidate"],
                "pair_orders_by_block": ["FC", "CF", "FC", "CF", "FC", "CF"],
                "pair_rows_are_adjacent": True,
                "blocks_per_level_task": 6,
                "remote_conversations": 144,
                "arithmetic": "4 * 3 * 6 * 2 = 144",
                "reuse_primary_rows": False,
                "interpretation": (
                    "PairPass/PairFail/Invalid structural response, not admission, "
                    "causality, or primary-S selection."
                ),
            },
            "alternate_candidate_reducers": {
                "reducers": [
                    {
                        "id": "dag_greedy_ratio_60_v1",
                        "rule": (
                            "Start current=F. Visit atoms once in reverse registered canonical "
                            "topological order. At each visit remove that atom, if still present, "
                            "and every currently present transitive dependent; continue from the "
                            "result even when it is outside the ratio interval. Record every "
                            "unique nonempty strict dependency-closed state in the 0.45-0.75 "
                            "interval, then select by absolute 0.60 target error, fewer rendered "
                            "tokens, and lexicographic atom IDs."
                        ),
                    },
                    {
                        "id": "source_window_ratio_60_v1",
                        "rule": (
                            "Enumerate every half-open nonempty contiguous [start,end) interval "
                            "in registered canonical source order, add the complete transitive "
                            "dependency closure, deduplicate by canonical atom-ID tuple, discard "
                            "full or out-of-0.45-0.75 states, then select by absolute 0.60 target "
                            "error, fewer rendered tokens, and lexicographic atom IDs."
                        ),
                    },
                ],
                "semantic_label_access": "forbidden",
                "no_candidate_policy": (
                    "Static task ineligibility blocks this materialization before the final "
                    "anchor. Any replacement is registered only in a separately committed "
                    "successor; no post-anchor reducer edit."
                ),
                "pair": ["fresh_F", "fresh_alternate_S"],
                "pair_orders_by_block": ["FC", "CF", "FC", "CF", "FC", "CF"],
                "pair_rows_are_adjacent": True,
                "blocks_per_reducer_task": 6,
                "remote_conversations": 96,
                "arithmetic": "4 * 2 * 6 * 2 = 96",
                "reuse_primary_rows": False,
                "interpretation": "PairPass/PairFail/Invalid only, never admission.",
            },
            "model_robustness": {
                "registry": "preregistration/model_ablation_registry.json",
                "conditions": ["B", "F", "S", "I"],
                "I_meaning": (
                    "A fresh conversation whose model-visible payload is "
                    "byte-identical to F; only non-visible ledger metadata differs."
                ),
                "condition_orders_by_block": [
                    "BFIS",
                    "IFSB",
                    "SBFI",
                    "BSIF",
                    "FIBS",
                    "SIFB",
                ],
                "F_I_adjacent": True,
                "F_before_I_blocks": 3,
                "I_before_F_blocks": 3,
                "blocks_per_task_model": 6,
                "remote_conversations_per_required_model": 96,
                "required_closed_models": 4,
                "required_remote_conversations": 384,
                "arithmetic": "4 * 4 * 6 * 4 = 384",
                "reuse_primary_rows": False,
                "candidate_state": (
                    "B/F/S alone produces Admit/Reject/Invalid under the primary SLA; "
                    "I is excluded from admission."
                ),
                "repeatability_metrics": [
                    "model_visible_input_sha256_agreement",
                    "valid_pairs/registered_pairs",
                    "operational_success_agreement",
                    "hard_contract_vector_agreement",
                    "absolute_private_score_delta",
                    "canonical_output_sha256_agreement",
                    "raw_response_sha256_agreement",
                ],
                "repeatability_reduction": repeatability_reduction(),
                "cross_model_summary": (
                    "Exact candidate-state agreement count across four sentinel tasks; "
                    "no global stability pass threshold or model ranking."
                ),
            },
            "open_deterministic_anchor": {
                "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "conditions": ["B", "F", "S", "I"],
                "local_executions": 96,
                "arithmetic": "4 * 6 * 4 = 96",
                "purpose": (
                    "Repeated identical F/I reproducibility, not seed sensitivity."
                ),
                "deterministic_F_I_gate": {
                    "required_valid_pairs": 6,
                    "required_model_visible_input_matches": 6,
                    "required_generated_token_id_matches": 6,
                    "required_canonical_output_sha256_matches": 6,
                    "required_score_and_contract_vector_matches": 6,
                },
            },
        },
        "resource_budget": {
            "primary_remote_conversations": 432,
            "control_remote_conversations": 144,
            "structural_ladder_remote_conversations": 144,
            "alternate_reducer_remote_conversations": 96,
            "required_model_robustness_remote_conversations": 384,
            "required_remote_conversation_cap": 1200,
            "open_anchor_local_execution_cap": 96,
            "required_execution_cap": 1296,
            "optional_closed_model_remote_conversation_cap": 192,
            "observed_v4_seconds_per_conversation": 127.2,
            "required_nominal_remote_hours": 42.4,
            "required_realistic_remote_hours": [51, 70],
            "remote_hours_meaning": (
                "Serial-equivalent remote call-hours including queue/network allowance; "
                "not total project time and not guaranteed wall-clock time."
            ),
            "ideal_two_worker_remote_wall_clock_lower_bound_hours": [25.5, 35.0],
            "excluded_from_remote_hour_estimate": [
                "96 local anchor executions",
                "24-task source and semantic materialization",
                "independent audits and differential tests",
                "scoring, aggregation, figures, manuscript revision, and review",
            ],
            "optional_models_realistic_additional_hours": [8, 14],
            "budget_rule": (
                "Required conditions finish before optional models; budget "
                "exhaustion cannot change the registration."
            ),
        },
        "transport_and_failure_policy": {
            "timeout_seconds": 240,
            "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
            "output_limit_binding": (
                "Every decoding config contains normalized_max_output_tokens=1024. Each "
                "hash-bound request template maps that normalized key to the exact "
                "provider-native JSON pointer; no provider default is used."
            ),
            "maximum_transport_attempts": 5,
            "retry_delays_seconds": [2, 4, 8, 16],
            "retry_delay_rule": (
                "For HTTP 429 use max(registered_delay, Retry-After when valid); add "
                "deterministic 0-1000 ms jitter derived from execution_id and attempt."
            ),
            "retryable": [
                "connection reset",
                "DNS or TLS transport failure",
                "HTTP 408",
                "HTTP 429",
                "HTTP 500",
                "HTTP 502",
                "HTTP 503",
                "HTTP 504",
                "read timeout",
            ],
            "non_retryable": [
                "authentication rejected",
                "model alias absent from model registry",
                "malformed frozen request",
                "deterministic scorer or contract failure",
            ],
            "semantic_rerun": (
                "forbidden; a terminal model response is never rerun because its "
                "score is low"
            ),
            "attempt_logging": (
                "Persist every attempt, elapsed time, status class, request ID when "
                "available, and recovery state without credentials."
            ),
            "duplicate_response_rule": (
                "Use a stable client execution_id and provider idempotency key when "
                "supported. Preserve every late/duplicate response; the first received "
                "response that passes request-ID, schema, and digest validation is the "
                "only terminal row. Later responses are duplicate annotations."
            ),
            "transport_retry_recovered_is_annotation": True,
            "termination_reason_contract": {
                "required_values": [
                    "eos",
                    "length",
                    "provider_stop",
                    "transport_failure",
                    "not_dispatched",
                ],
                "provider_finish_reason": (
                    "Persist the exact provider-returned finish/stop reason string when "
                    "available, otherwise null."
                ),
                "normalization": {
                    "eos": "Local anchor generated a registered EOS token.",
                    "length": (
                        "The normalized 1024-token cap or a provider-native length/max-token "
                        "finish reason ended generation."
                    ),
                    "provider_stop": (
                        "A completed provider response stopped for any non-length provider "
                        "reason, including a provider stop sequence."
                    ),
                    "transport_failure": "A request was dispatched but no valid body completed.",
                    "not_dispatched": "Preflight/model unavailability prevented dispatch.",
                },
                "length_is_reported_separately_from_terminal_outcome": True,
            },
            "mutually_exclusive_terminal_outcomes_in_precedence_order": [
                "provider_or_model_unavailable",
                "transport_terminal_failure",
                "integrity_or_digest_failure",
                "malformed_or_no_submission",
                "action_budget_exhausted",
                "hard_contract_failure",
                "score_shortfall",
                "operational_success",
            ],
            "terminal_truth_table": {
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
            },
            "private_score_totality": (
                "Every row_valid=true terminal row has exactly one finite [0,1] private_score. "
                "Every row_valid=false row has private_score=null. Each task differential test "
                "must exercise all five valid terminal score rules before the final anchor."
            ),
        },
        "analysis_contract": {
            "registered_state_denominators": (
                "Report Admit/Reject/Invalid over all registered decisions; never "
                "delete Invalid."
            ),
            "paired_effects": [
                "F-B operational-success and private-score difference",
                "S-B operational-success and private-score difference",
                "S-F operational-success and private-score difference",
            ],
            "paired_denominator": (
                "Report valid_pairs/registered_pairs; a missing member makes the "
                "pair Invalid."
            ),
            "partial_identification": (
                "Report best/worst bounds for Invalid binary outcomes and bounded "
                "[0,1] scores."
            ),
            "contrast_orientation": {
                "F_minus_B": ["F", "B"],
                "S_minus_B": ["S", "B"],
                "S_minus_F": ["S", "F"],
            },
            "registered_estimator": {
                "block_value": (
                    "For contrast X-Y and valid rows, d_ptb = outcome_X - outcome_Y, "
                    "computed separately for binary success and [0,1] private score."
                ),
                "block_bounds": {
                    "both_valid": "[x-y, x-y]",
                    "X_valid_Y_invalid": "[x-1, x]",
                    "X_invalid_Y_valid": "[-y, 1-y]",
                    "both_invalid": "[-1, 1]",
                },
                "task_observed": (
                    "Arithmetic mean of valid block differences; undefined if zero "
                    "valid pairs, always accompanied by valid_pairs/6."
                ),
                "task_identified_bounds": (
                    "Arithmetic mean of the six registered block lower endpoints and "
                    "of the six upper endpoints, using denominator 6."
                ),
                "paper_observed": (
                    "Equal 0.5/0.5 mean of the two task_observed values only when both "
                    "are defined; otherwise undefined."
                ),
                "paper_identified_bounds": (
                    "Equal 0.5/0.5 mean of the two task lower bounds and upper bounds."
                ),
                "domain_identified_bounds": (
                    "Equal 1/3 mean of the three registered paper bounds in the domain."
                ),
                "overall_identified_bounds": (
                    "Equal 1/4 mean of the four domain bounds."
                ),
                "observed_summary": (
                    "Descriptive mean over defined paper_observed values with k/12 "
                    "reported; it never replaces the registered identified bounds."
                ),
            },
            "aggregate_unit": "paper",
            "domain_weighting": (
                "Report exact domain counts and an equal-domain-weighted summary; "
                "keep both tasks nested within a sampled paper."
            ),
            "paper_bootstrap_sensitivity": {
                "replicates": 10000,
                "seed": 20260721,
                "resampling_unit": (
                    "paper within domain, carrying both tasks and all paired blocks"
                ),
                "interpretation": (
                    "registered-benchmark sensitivity only, not a population CI"
                ),
                "estimator_reuse": (
                    "Recompute the same task, paper, domain, and overall lower/upper "
                    "estimators in every resample; never resample tasks or blocks."
                ),
            },
            "leave_one_paper_out": (
                "Repeat the same registered estimator after removing each paper, "
                "renormalizing only the remaining paper weights within its domain."
            ),
            "leave_one_block_out": (
                "Descriptive five-block recomputation uses B<=1, F>=4, S>=4, and "
                "margin>=4 over the remaining blocks; per-registry gates are not applied "
                "after an unbalanced omission. Any remaining Invalid row makes the five-block "
                "state Invalid. Omitting the sole Invalid row may yield a labeled recovered "
                "five-block state, but it cannot replace the six-block admission decision."
            ),
            "per_task_display": (
                "Show six raw paired points, valid/Invalid counts, median, and range; "
                "no per-task Clopper-Pearson or six-block bootstrap interval."
            ),
            "controls": (
                "Exact sanity outcomes only; no confusion matrix or calibration rate."
            ),
            "multiple_comparisons": (
                "Only dag_ratio_60_v1 supplies primary S; secondary analyses cannot "
                "select or rescue it."
            ),
            "cost_measurement": cost_measurement_contract(),
        },
        "success_conditions": {
            "protocol_integrity": (
                "Every materialization, audit, hash, schedule, terminal, and control "
                "sanity gate passes."
            ),
            "decision_coverage": "At least 20/24 primary decisions are valid.",
            "candidate_yield": (
                "At least 8/24 primary dag_ratio_60_v1 candidates are admitted across "
                "at least three domains; this is an engineering benchmark target."
            ),
            "reporting_rule": (
                "Report the three conclusions separately; one cannot rescue another."
            ),
        },
        "falsification_condition": (
            "Any sanity failure, fewer than 20 valid natural decisions, fewer than "
            "8 admissions, fewer than three admission domains, or post-anchor mutation."
        ),
        "stage_2_3_entry_gate": [
            "The Stage 2.2 bundle, SLA analysis, verifier, and tests pass.",
            "The Stage 2.2 report and artifacts are committed and pushed.",
            "No experimental provider call has started.",
        ],
        "stage_2_3_final_anchor_gate": [
            "All sources, spans, audits, DAGs, candidates, fixtures, scorers, adapters, tests, and schedules have immutable hashes.",
            "Builder/auditor identities and disagreement resolutions are recorded.",
            "Independent auditors pass source review of the result parser, analysis implementation, and open-anchor preflight implementation.",
            "Exact aliases pass format-only preflight without fallback.",
            "The final anchor is verified, committed, and pushed before experiments.",
        ],
    }


def closed_slot(
    slot_id: str,
    family: str,
    alias: str,
    required: bool,
    hours: list[float],
) -> dict[str, object]:
    return {
        "slot_id": slot_id,
        "role": "required_closed_robustness" if required else "optional_secondary",
        "required": required,
        "provider_family": family,
        "model_alias": alias,
        "seed_support": "record_if_returned_not_relied_upon",
        "conditions": ["B", "F", "S", "I"],
        "remote_conversations": 96,
        "planning_hours": hours,
        "decoding": {
            "temperature": 0,
            "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
        },
        "availability_gate": (
            "The exact alias must pass format-only preflight; no fallback alias is "
            "substituted or pooled."
        ),
    }


def build_model_registry() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-model-registry.v2",
        "registration_status": STATUS,
        "paper_task_ids": SECONDARY_TASKS,
        "design": {
            "blocks_per_task": 6,
            "conditions": ["B", "F", "S", "I"],
            "I_meaning": (
                "I is a fresh conversation with a model-visible payload "
                "byte-identical to F."
            ),
            "remote_conversations_per_closed_model": 96,
            "local_executions_for_open_anchor": 96,
            "condition_orders_by_block": [
                "BFIS",
                "IFSB",
                "SBFI",
                "BSIF",
                "FIBS",
                "SIFB",
            ],
            "F_I_adjacent_in_every_block": True,
            "fresh_conversation_per_condition": True,
            "same_frozen_inputs_across_models": True,
            "temperature": 0,
            "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
            "output_budget_scope": (
                "Every primary, required closed-model, and open-anchor execution uses the "
                "same 1024-token output cap through a provider-native request-field mapping."
            ),
            "closed_model_seed_claim": (
                "Closed slots are not claimed bitwise or seed deterministic; returned "
                "seed or fingerprint fields are logged but not relied upon."
            ),
            "comparison_scope": (
                "Secondary robustness only; no model ranking, primary-row reuse, or "
                "pooling with the 24-task result; conclusions are limited to the four "
                "prespecified sentinel tasks."
            ),
            "candidate_state_rule": "B/F/S use the primary admission SLA; I is excluded.",
            "repeatability_metrics": [
                "model_visible_input_sha256_agreement",
                "valid_pairs/registered_pairs",
                "operational_success_agreement",
                "hard_contract_vector_agreement",
                "absolute_private_score_delta",
                "canonical_output_sha256_agreement",
                "raw_response_sha256_agreement",
            ],
            "repeatability_reduction": repeatability_reduction(),
        },
        "primary_model_reference": {
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
        "model_slots": [
            closed_slot("gpt_5_5", "OpenAI", "gpt-5.5", True, [2.7, 4.7]),
            closed_slot(
                "gpt_5_6_sol", "OpenAI", "gpt-5.6-sol", True, [4.0, 7.3]
            ),
            closed_slot(
                "gpt_5_6_terra", "OpenAI", "gpt-5.6-terra", True, [2.7, 5.3]
            ),
            closed_slot(
                "claude_opus_4_7",
                "Anthropic",
                "claude-opus-4-7",
                True,
                [4.0, 9.3],
            ),
            {
                "slot_id": "open_seed_anchor",
                "role": "required_reproducibility_anchor",
                "required": True,
                "provider_family": "local_open_weights",
                "model_alias": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "seed_support": "required",
                "conditions": ["B", "F", "S", "I"],
                "local_executions": 96,
                "decoding": {
                    "do_sample": False,
                    "temperature": 0,
                    "top_p": 1.0,
                    "normalized_max_output_tokens": NORMALIZED_MAX_OUTPUT_TOKENS,
                },
                "seed_derivation": {
                    "formula": (
                        "uint32_big_endian(sha256(preimage_bytes)[0:4])"
                    ),
                    "preimage_fields": [
                        "study_id",
                        "task_id",
                        "ascii_decimal_block_id",
                        "condition_seed_group",
                        "ascii_decimal_turn_id",
                    ],
                    "preimage_encoding": (
                        "UTF-8 without BOM, fields joined by one NUL byte, no trailing NUL"
                    ),
                    "condition_seed_groups": {
                        "B": "baseline",
                        "F": "full_identity_pair",
                        "S": "slice",
                        "I": "full_identity_pair",
                    },
                    "F_I_same_seed": True,
                    "golden_test_vectors": [
                        {
                            "fields": [
                                "EffectSlice-FG1",
                                "NLP-LLM-01",
                                "1",
                                "full_identity_pair",
                                "0",
                            ],
                            "uint32_seed": 2490612457,
                        },
                        {
                            "fields": [
                                "EffectSlice-FG1",
                                "AGENT-TF-01",
                                "6",
                                "slice",
                                "1",
                            ],
                            "uint32_seed": 3699213122,
                        },
                    ],
                    "frameworks_seeded": [
                        "python_random",
                        "numpy",
                        "torch_cpu",
                        "torch_cuda_all",
                    ],
                },
                "revision_gate": (
                    "Bind weight revision and file hashes, tokenizer hash, quantization, "
                    "runtime, device, CUDA stack, deterministic algorithms, TF32 state, "
                    "and CUBLAS_WORKSPACE_CONFIG before execution."
                ),
                "interpretation": (
                    "Identical F/I reproducibility, not seed sensitivity or a "
                    "capability-matched closed-model substitute."
                ),
                "deterministic_F_I_gate": {
                    "required_valid_pairs": 6,
                    "required_model_visible_input_matches": 6,
                    "required_generated_token_id_matches": 6,
                    "required_canonical_output_sha256_matches": 6,
                    "required_score_and_contract_vector_matches": 6,
                },
            },
            closed_slot(
                "gpt_5_6_luna", "OpenAI", "gpt-5.6-luna", False, [2.7, 5.3]
            ),
            closed_slot(
                "claude_opus_4_6",
                "Anthropic",
                "claude-opus-4-6",
                False,
                [4.0, 8.0],
            ),
        ],
        "preflight_contract": {
            "registry_snapshot": (
                "Persist exact alias discovery or format-only preflight status without "
                "credentials or paper-task private payloads."
            ),
            "maximum_format_only_requests_per_alias": 1,
            "unavailable_required_slot": (
                "Record provider_or_model_unavailable and mark cross-model robustness "
                "incomplete without invalidating the primary FG1 design."
            ),
            "no_alias_fallback": True,
            "no_post_outcome_model_addition": True,
        },
    }


def build_figure_plan() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-figure-statistical-plan.v2",
        "registration_status": STATUS,
        "evidence_rule": (
            "Empirical panels use only hash-bound real outcomes and aggregation code; "
            "placeholder, simulated, hand-entered, or selectively filtered outcomes "
            "are forbidden."
        ),
        "figures": [
            {
                "figure_id": "F1_protocol_audit",
                "priority": "main_required",
                "panels": [
                    {
                        "id": "a",
                        "content": (
                            "One end-to-end real case: paper span, opaque atoms, dependency "
                            "edges, F/S retain/drop boundary, canonical rendered artifact, "
                            "model-visible payload digest, and terminal admission fields."
                        ),
                    },
                    {
                        "id": "b",
                        "content": (
                            "V3 development, V4 freeze/run, prefix-04 selection, V5 "
                            "freeze/run, and FG1 design/materialization/run timeline "
                            "with public/private visibility."
                        ),
                    },
                    {
                        "id": "c",
                        "content": (
                            "Complete admission gate showing B sensitivity, F/S "
                            "sufficiency, paired margin, integrity, ordered Reject "
                            "reasons, and orthogonal Invalid. Controls are outside it."
                        ),
                    },
                ],
                "claim": "Protocol transparency and leakage control, not efficacy.",
            },
            {
                "figure_id": "F2_cross_paper_effects",
                "priority": "main_required",
                "panels": [
                    {
                        "id": "a",
                        "content": (
                            "Twelve paper-level F-B, S-B, and S-F effect rows with "
                            "nested task/block points, valid/registered pairs, and "
                            "partial-identification bounds."
                        ),
                    },
                    {
                        "id": "b",
                        "content": (
                            "Primary 12-paper x 2-task Admit/Reject/Invalid matrix with "
                            "registry-stratified raw counts; no reducer/model cells are "
                            "implied for combinations that were not run."
                        ),
                    },
                ],
                "claim": (
                    "Registered-benchmark heterogeneity and coverage; no random-sample "
                    "population claim."
                ),
            },
            {
                "figure_id": "F3_compression_reliability",
                "priority": "main_required",
                "panels": [
                    {
                        "id": "a",
                        "content": (
                            "Primary S compression versus admission plus a separate "
                            "two-arm secondary panel using PairPass/PairFail/Invalid; "
                            "the two state types are never pooled."
                        ),
                    },
                    {
                        "id": "b",
                        "content": (
                            "All registered structural restoration levels on four tasks, "
                            "including Invalid levels."
                        ),
                    },
                    {
                        "id": "c",
                        "content": (
                            "Four-task matrix for control SanityPass/SanityFail/Invalid "
                            "and ladder/alternate PairPass/PairFail/Invalid. Structural "
                            "missing cells are hatched and never encoded as failure."
                        ),
                    },
                    {
                        "id": "d",
                        "content": (
                            "Separate task-model-candidate resource cells for frozen artifact "
                            "bytes/tokens, provider-reported input/output tokens, terminal-attempt "
                            "latency, and retry overhead, with six raw values and non-null/6. "
                            "Paired S-F deltas are shown only when both members exist; monetary "
                            "cost is appendix-only and conditional on a pre-anchor hashed price table."
                        ),
                    },
                ],
                "claim": (
                    "Secondary compression, reliability, and resource-use trade-off plus "
                    "structural dose response, not causality or model ranking."
                ),
            },
            {
                "figure_id": "F4_robustness_and_failures",
                "priority": "appendix_required",
                "panels": [
                    {
                        "id": "a",
                        "content": (
                            "Required model x four sentinel-task exact B/F/S candidate "
                            "states and F/I repeatability metrics; unavailable slots stay visible."
                        ),
                    },
                    {
                        "id": "b",
                        "content": (
                            "Registered SLA-grid task-state stability, fixed five-block "
                            "leave-one-out task-state stability, and leave-one-paper-out "
                            "identified-bound summaries."
                        ),
                    },
                    {
                        "id": "c",
                        "content": (
                            "Mutually exclusive terminal outcome decomposition; recovered "
                            "transport retries are annotations, not semantic failures. Show "
                            "normalized length-cap termination separately so truncation is not "
                            "confounded with malformed output or hard-contract failure."
                        ),
                    },
                ],
                "claim": "Robustness and operational diagnosis.",
            },
        ],
        "conditional_outputs": [
            {
                "name": "control_confusion_matrix",
                "default": "do_not_render",
                "reason": (
                    "Four tasks per sanity state cannot support calibrated error rates."
                ),
                "current_independent_controls_per_state": 4,
                "current_output": "Exact task-level sanity table only.",
            }
        ],
        "statistics": {
            "primary_unit": "paper",
            "independent_n": 12,
            "nesting": (
                "six paired blocks within task, two tasks within paper, three papers "
                "within each domain"
            ),
            "primary_outcomes": [
                "registered Admit/Reject/Invalid state",
                "paired F-B operational-success and private-score difference",
                "paired S-B operational-success and private-score difference",
                "paired S-F operational-success and private-score difference",
            ],
            "secondary_resource_outcomes": cost_measurement_contract(),
            "registered_denominators": True,
            "valid_pair_reporting": "valid_pairs/registered_pairs",
            "invalid_partial_identification_bounds": True,
            "estimator_source": "experiment_plan.json analysis_contract.registered_estimator",
            "per_task_display": {
                "required": [
                    "six raw paired points",
                    "valid and Invalid counts",
                    "median",
                    "range",
                ],
                "forbidden": [
                    "per-task Clopper-Pearson interval",
                    "six-block bootstrap interval",
                ],
            },
            "paper_bootstrap_sensitivity": {
                "seed": 20260721,
                "replicates": 10000,
                "resample": "papers within domain",
                "preserve": "both tasks and all matched blocks",
                "interval": "percentile 95%",
                "scope_label": "registered-benchmark sensitivity interval",
            },
            "mandatory_sensitivity": [
                "leave_one_paper_out",
                "exact_domain_counts",
                "equal_domain_weighted_summary",
            ],
            "sla_sensitivity_grid": {
                "maximum_B_successes": [0, 1, 2],
                "minimum_F_successes": [4, 5, 6],
                "minimum_S_successes": [4, 5, 6],
                "paired_margin": [0.00, 0.05, 0.10],
                "leave_one_block_out": (
                    "Over five remaining blocks use B<=1, F>=4, S>=4, margin>=4; "
                    "omit per-registry gates and never replace the six-block rule. Any "
                    "remaining Invalid row makes the five-block state Invalid; omitting the "
                    "sole Invalid row may be labeled recovered sensitivity only."
                ),
            },
            "controls": (
                "Sanity states only; no calibration, sensitivity, specificity, or "
                "confusion matrix."
            ),
            "model_analysis": (
                "Report every slot separately on four prespecified sentinel tasks, "
                "including exact candidate state and all registered F/I metrics; "
                "unavailable slots remain visible and are never replaced post hoc."
            ),
            "nonfactorial_display_rule": (
                "Primary, paired-secondary, and model subdesigns use separate matrices; "
                "unrun combinations are structural missing, never Reject or Invalid."
            ),
            "multiple_testing": (
                "One primary S per task; every other candidate/model/SLA analysis is "
                "secondary and cannot rescue the primary result."
            ),
        },
        "figure_precedent_map": [
            {
                "planned_element": "method pipeline and atom boundary",
                "adjacent_precedents": [
                    "Toolformer",
                    "Delta Debugging",
                    "C-Reduce",
                    "Perses",
                ],
                "positioning": "Procedural and reduction diagrams are standard adjacent practice.",
            },
            {
                "planned_element": "risk and SLA sensitivity",
                "adjacent_precedents": ["SelectiveNet", "Conformal Risk Control"],
                "positioning": (
                    "Threshold/reject-option precedent without inheriting "
                    "distribution-free guarantees."
                ),
            },
            {
                "planned_element": "heatmap and failure analysis",
                "adjacent_precedents": ["AgentBoard", "MCP-AgentBench", "PaperBench"],
                "positioning": "Benchmark-analysis precedent, not an identical design.",
            },
            {
                "planned_element": "compression-reliability Pareto",
                "adjacent_precedents": [
                    "LLMLingua",
                    "LLMLingua-2",
                    "Prompt Compression with Context-Aware Sentence Encoding",
                ],
                "positioning": "Compression/performance trade-off precedent.",
            },
        ],
    }


def build_materialization_contract() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-materialization-contract.v1",
        "registration_status": STATUS,
        "stage": "2.3",
        "verifier": "verify_stage_2_3_materialization.py",
        "purpose": (
            "Convert the passed Stage 2.2 design into immutable, audited, executable "
            "inputs before any experimental provider call."
        ),
        "task_path_template": "materialization/tasks/{task_id}",
        "required_task_artifacts": [
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
        "source_and_task_specificity": {
            "minimum_central_spans_per_task": 2,
            "required_span_fields": [
                "document_sha256",
                "page_or_section",
                "byte_start",
                "byte_end",
                "quoted_text_sha256",
                "atom_ids",
            ],
            "two_tasks_same_paper_must_have_distinct_central_boundaries": True,
            "paper_claim_guardrail_scorer_roles_separated": True,
            "reference_differential_test_required": True,
        },
        "support_artifact_schemas": {
            "source_manifest.json": {
                "schema_version": "effectslice-fg1-sources.v1",
                "required_fields": ["schema_version", "task_id", "sources"],
                "source_required_fields": ["path", "sha256", "license_or_access_note"],
            },
            "task_to_span_matrix.json": {
                "schema_version": "effectslice-fg1-task-spans.v1",
                "required_fields": ["schema_version", "task_id", "central_spans"],
            },
            "public_fixture_manifest.json": {
                "schema_version": "effectslice-fg1-public-fixture.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "fixture_path",
                    "fixture_sha256",
                ],
            },
            "adapter_manifest.json": {
                "schema_version": "effectslice-fg1-adapter.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "implementation_path",
                    "implementation_sha256",
                ],
            },
            "reference_implementation_manifest.json": {
                "schema_version": "effectslice-fg1-reference-implementation.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "implementation_path",
                    "implementation_sha256",
                ],
            },
            "scorer_manifest.json": {
                "schema_version": "effectslice-fg1-scorer.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "implementation_path",
                    "implementation_sha256",
                    "hard_contract_ids",
                ],
            },
            "differential_test_report.json": {
                "schema_version": "effectslice-fg1-differential-test.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "passed",
                    "comparison_count",
                    "failure_count",
                    "terminal_score_semantics_passed",
                    "terminal_score_case_count",
                ],
                "passed": True,
                "minimum_comparison_count": 1,
                "failure_count": 0,
                "terminal_score_semantics_passed": True,
                "minimum_terminal_score_case_count": 5,
            },
            "semantic_audit.json": {
                "schema_version": "effectslice-fg1-semantic-audit.v1",
                "required_fields": [
                    "schema_version",
                    "task_id",
                    "identities",
                    "reviews",
                    "disagreements_and_resolutions",
                    "passed",
                ],
                "passed": True,
            },
        },
        "candidate_manifest": {
            "required_primary_candidates": [
                "B_empty_artifact",
                "F",
                "S_dag_ratio_60_v1",
            ],
            "required_secondary_candidates": [
                "control_positive_reference",
                "control_negative",
                "control_identity",
                "ladder_L0",
                "ladder_L1",
                "ladder_L2",
                "alternate_dag_greedy",
                "alternate_source_window",
            ],
            "required_fields": [
                "candidate_id",
                "candidate_type",
                "atom_ids",
                "dependency_closed",
                "strict_subset",
                "rendered_token_count",
                "retained_token_ratio",
                "artifact_path",
                "artifact_sha256",
                "construction_log_path",
                "construction_log_sha256",
                "renderer_sha256",
                "tokenizer_asset_sha256",
                "reducer_input_manifest_sha256",
            ],
            "B_contract": {
                "candidate_id": "B_empty_artifact",
                "canonical_bytes": "zero-length byte string",
                "bytes_length": 0,
                "sha256": (
                    "e3b0c44298fc1c149afbf4c8996fb924"
                    "27ae41e4649b934ca495991b7852b855"
                ),
                "paper_atom_count": 0,
                "strict_subset_fields_exempt": True,
            },
            "schedule_candidate_ids": {
                "primary": {
                    "B": "B_empty_artifact",
                    "F": "F",
                    "S": "S_dag_ratio_60_v1",
                },
                "controls": {
                    "planted_redundancy_positive": {
                        "F": "control_positive_reference",
                        "C": "F",
                    },
                    "destructive_core_negative": {
                        "F": "F",
                        "C": "control_negative",
                    },
                    "byte_identical_identity": {
                        "F": "F",
                        "C": "control_identity",
                    },
                },
                "structural_ladder": {
                    "L0_primary_slice": {"F": "F", "C": "ladder_L0"},
                    "L1_mid_restore": {"F": "F", "C": "ladder_L1"},
                    "L2_near_full_strict": {"F": "F", "C": "ladder_L2"},
                },
                "alternate_reducers": {
                    "dag_greedy_ratio_60_v1": {
                        "F": "F",
                        "C": "alternate_dag_greedy",
                    },
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
            },
            "identity_control": (
                "F and identity model-visible artifact bytes must have the same sha256."
            ),
            "ladder_feasibility": (
                "Materialization proves at least one closed chain "
                "S=L0 strict-subset L1 strict-subset L2 strict-subset F and records "
                "the complete chain-enumeration digest before the final anchor."
            ),
            "atom_dag_document_schema": {
                "schema_version": "effectslice-fg1-atom-dag.v1",
                "required_top_level_fields": ["schema_version", "task_id", "atoms"],
                "required_atom_fields": [
                    "atom_id",
                    "dependency_ids",
                    "rendered_token_count",
                ],
                "atoms_in_registered_canonical_topological_order": True,
                "dependency_ids_must_precede_atom": True,
            },
            "candidate_document_schema": {
                "schema_version": "effectslice-fg1-candidates.v1",
                "required_top_level_fields": [
                    "schema_version",
                    "task_id",
                    "candidates",
                    "primary_reducer_audit",
                    "ladder_chain_audit",
                    "alternate_reducer_audit",
                ],
                "candidate_ids_unique": True,
                "atom_ids_in_registered_canonical_order": True,
            },
            "atom_registry_document_schema": {
                "schema_version": "effectslice-fg1-atom-registry.v1",
                "required_top_level_fields": ["schema_version", "task_id", "atoms"],
                "required_atom_fields": [
                    "atom_id",
                    "source_locator",
                    "rendered_text",
                    "rendered_text_sha256",
                ],
                "atom_order_matches_DAG": True,
                "opaque_atom_id_derivation": (
                    "a_ + first_16_lower_hex(sha256(document_sha256 + NUL + "
                    "ascii_decimal(byte_start) + NUL + ascii_decimal(byte_end) + "
                    "NUL + ascii_decimal(split_index)))"
                ),
                "opaque_atom_id_regex": "^a_[0-9a-f]{16}$",
                "semantic_role_fields_forbidden": [
                    "paper_claim_label",
                    "hard_contract_label",
                    "guardrail_label",
                    "scorer_interface_label",
                    "public_outcome",
                    "private_outcome",
                    "model_output",
                ],
            },
            "primary_reducer_audit_schema": {
                "selection_rule_id": "dag_ratio_60_v1",
                "required_fields": [
                    "selection_rule_id",
                    "all_closed_strict_subsets",
                    "complete_enumeration_sha256",
                    "eligible_subset_count",
                    "selected_candidate_id",
                ],
                "selected_candidate_id": "S_dag_ratio_60_v1",
                "verifier_reenumerates_dependency_closed_subsets": True,
                "verifier_rerenders_and_retokenizes_every_subset": True,
                "canonicalization": (
                    "Canonical JSON UTF-8 with sorted keys and separators ',' ':'; "
                    "subset rows sorted by canonical atom-ID tuples."
                ),
            },
            "reducer_input_document_schema": {
                "schema_version": "effectslice-fg1-reducer-input.v1",
                "required_top_level_fields": ["schema_version", "task_id", "atoms"],
                "exact_atom_fields": [
                    "atom_id",
                    "dependency_ids",
                    "rendered_token_count",
                ],
                "must_equal_atom_dag_projection": True,
            },
            "reducer_enumeration_document_schema": {
                "schema_version": "effectslice-fg1-reducer-enumeration.v1",
                "required_top_level_fields": [
                    "schema_version",
                    "task_id",
                    "all_closed_strict_subsets",
                    "complete_enumeration_sha256",
                    "eligible_subset_count",
                    "selected_candidate_id",
                ],
                "subset_row_exact_fields": [
                    "atom_ids",
                    "rendered_token_count",
                    "retained_token_ratio",
                ],
                "retained_token_ratio_precision_decimals": 12,
                "selected_candidate_id": "S_dag_ratio_60_v1",
            },
            "runtime_manifest_schema": {
                "schema_version": "effectslice-fg1-reducer-runtime.v1",
                "required_top_level_fields": [
                    "schema_version",
                    "task_id",
                    "renderer",
                    "tokenizer",
                    "reducer",
                ],
                "component_required_fields": ["id", "path", "sha256"],
                "renderer": {
                    "id": "effectslice_atom_renderer_v1",
                    "separator": "\\n\\n",
                    "encoding": "utf-8",
                    "newline": "LF",
                },
                "tokenizer": {
                    "package": "tiktoken",
                    "version": "0.12.0",
                    "encoding": "cl100k_base",
                },
                "reducer_id": "dag_ratio_60_v1",
            },
            "ladder_chain_audit_schema": {
                "required_on_secondary_tasks": True,
                "eligible_subset_definition": (
                    "Every dependency-closed T satisfying S strict-subset T "
                    "strict-subset F."
                ),
                "required_fields": [
                    "selection_rule_id",
                    "eligible_closed_subsets",
                    "complete_subset_enumeration_sha256",
                    "enumerated_chain_count",
                    "all_chains",
                    "complete_chain_enumeration_sha256",
                    "selected_chain_candidate_ids",
                ],
                "selection_rule_id": "complete_chain_enumeration_v1",
                "selected_chain_candidate_ids": [
                    "ladder_L0",
                    "ladder_L1",
                    "ladder_L2",
                    "F",
                ],
                "canonicalization": (
                    "Canonical JSON UTF-8 with sorted keys and separators ',' ':'; "
                    "subset and chain rows sorted by canonical atom-ID tuples."
                ),
                "selection_key": [
                    "maximum_L2_rendered_tokens",
                    "minimum_twice_L1_distance_to_S_L2_token_midpoint",
                    "fewer_L1_rendered_tokens",
                    "lexicographic_L1_atom_ids",
                    "lexicographic_L2_atom_ids",
                ],
                "verifier_reenumerates_closed_subsets_and_chains": True,
            },
            "alternate_reducer_audit_schema": {
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
        },
        "model_visible_payload_contract": {
            "schema_version": "effectslice-fg1-model-visible-payloads.v1",
            "canonical_payload_composition": {
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
                "B_attachment": "candidate_artifact has decimal length 0 and contributes no bytes",
                "verifier_reconstructs_bytes": True,
            },
            "wire_request_composition": {
                "request_template_schema": "effectslice-fg1-request-template.v1",
                "template_required_fields": [
                    "schema_version",
                    "model_slot_id",
                    "exact_alias",
                    "base_request",
                    "model_json_pointer",
                    "payload_json_pointer",
                    "decoding_field_json_pointers",
                ],
                "construction": (
                    "Deep-copy base_request; set exact_alias at model_json_pointer, the UTF-8 "
                    "decoded canonical payload at payload_json_pointer, and every exact decoding "
                    "config key at its registered JSON pointer. The map key set must equal the "
                    "decoding-config key set. Serialize as UTF-8 canonical JSON with sorted keys, "
                    "separators ',' and ':', ensure_ascii=false, then one LF."
                ),
                "normalized_output_limit": {
                    "decoding_key": "normalized_max_output_tokens",
                    "value": NORMALIZED_MAX_OUTPUT_TOKENS,
                    "provider_native_pointer_required_for_every_slot": True,
                    "provider_default_forbidden": True,
                },
                "streaming": False,
                "verifier_reconstructs_bytes": True,
            },
            "required_conditions": ["B", "F", "S", "I", "C"],
            "required_fields": [
                "task_scaffold_sha256",
                "fixture_manifest_sha256",
                "fixture_payload_sha256",
                "private_registry_manifest_sha256",
                "scorer_manifest_sha256",
                "candidate_artifact_sha256",
                "canonical_model_visible_payload_sha256",
                "serialized_wire_request_sha256",
                "model_slot_id",
                "decoding_config_sha256",
            ],
            "manifest_row_key": ["execution_id"],
            "manifest_row_must_equal_schedule_hash_fields": True,
            "digest_path_fields": {
                "task_scaffold_sha256": "task_scaffold_path",
                "fixture_manifest_sha256": "fixture_manifest_path",
                "fixture_payload_sha256": "fixture_payload_path",
                "scorer_manifest_sha256": "scorer_manifest_path",
                "candidate_artifact_sha256": "candidate_artifact_path",
                "canonical_model_visible_payload_sha256": (
                    "canonical_model_visible_payload_path"
                ),
                "serialized_wire_request_sha256": "serialized_wire_request_path",
                "decoding_config_sha256": "decoding_config_path",
                "private_registry_manifest_sha256": "private_registry_manifest_path",
            },
            "typed_path_constraints": {
                "task_scaffold_path": "task_scaffold.md",
                "fixture_manifest_path": "public_fixture_manifest.json",
                "fixture_payload_path": "fixtures/{registry_id}.json",
                "scorer_manifest_path": "scorer_manifest.json",
                "candidate_artifact_path": "candidate_manifest.artifact_path[candidate_id]",
                "canonical_model_visible_payload_path": "payloads/{execution_id}.txt",
                "serialized_wire_request_path": "requests/{execution_id}.json",
                "decoding_config_path": "decoding/{model_slot_id}.json",
                "private_registry_manifest_path": (
                    "private_registry_{registry_id}_manifest.json"
                ),
            },
            "same_block_invariants": [
                "same task scaffold",
                "same fixture payload",
                "same scorer",
                "same model slot and decoding settings",
                "conditions differ only by registered artifact attachment",
            ],
            "F_I_canonical_payload_sha256_equal": True,
            "F_I_artifact_sha256_equal": True,
            "F_I_serialized_wire_request_sha256_equal": True,
            "cross_model_frozen_fields": [
                "task_scaffold_sha256",
                "fixture_manifest_sha256",
                "fixture_payload_sha256",
                "scorer_manifest_sha256",
                "candidate_artifact_sha256",
                "canonical_model_visible_payload_sha256",
                "private_registry_manifest_sha256",
            ],
            "cross_model_scope": (
                "For the same sentinel task, block, and condition/candidate, all required "
                "closed slots and the open anchor share frozen inputs. Decoding settings, "
                "serialized wire formatting, and model-specific response envelopes may differ."
            ),
            "task_wide_frozen_fields": [
                "task_scaffold_sha256",
                "fixture_manifest_sha256",
                "scorer_manifest_sha256",
            ],
            "task_registry_frozen_fields": [
                "fixture_payload_sha256",
                "private_registry_manifest_sha256",
            ],
            "model_slot_wide_frozen_fields": ["decoding_config_sha256"],
        },
        "result_canonicalization_contract": {
            "raw_response_bytes": (
                "Streaming is disabled. Persist exactly the complete response-body bytes "
                "delivered by the HTTP client after transfer/content decoding and before UTF-8 "
                "or JSON parsing; do not reserialize. raw_response_sha256 hashes those bytes. "
                "The local anchor persists the exact UTF-8 JSON bytes emitted by its frozen "
                "adapter under the same rule."
            ),
            "canonical_output_bytes": (
                "Parse raw response bytes as strict UTF-8 JSON, extract one JSON string with the "
                "slot-specific frozen selector in the hash-bound response contract, replace "
                "CRLF and CR with LF, apply Unicode NFC, encode UTF-8 without a trailing-newline "
                "edit, and hash those bytes. A missing/non-string pointer or parse failure yields "
                "canonical_output_sha256=null and terminal malformed_or_no_submission."
            ),
            "generated_token_ids": (
                "For the local anchor only, slice generate() output after the unpadded prompt "
                "length, retain generated IDs through the first EOS token inclusive, exclude "
                "all prompt IDs and any pad IDs after EOS, and persist the decimal integer list "
                "in order. Every currently registered closed-model slot records null because no "
                "exact token-ID selector is frozen; only a successor preregistration may change "
                "that rule."
            ),
            "hard_contract_vector": (
                "Boolean values in the exact hard_contract_ids order frozen in the task scorer "
                "manifest; no sorting at result time. Missing scorer output makes the row Invalid."
            ),
            "empty_and_failure_behavior": (
                "An extracted empty string is a valid canonical byte string but ordinarily maps "
                "to malformed_or_no_submission with private_score=0.0. JSON/parser failure never "
                "produces an empty substitute. Invalid rows use null for canonical output, token "
                "IDs, hard-contract vector, and private_score."
            ),
            "termination_reason": (
                "Every result records one normalized termination reason from eos, length, "
                "provider_stop, transport_failure, or not_dispatched, plus the nullable exact "
                "provider finish reason. Length termination remains scored by the same frozen "
                "scorer and is reported separately rather than relabeled as malformed."
            ),
            "termination_compatibility": {
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
            },
            "result_row_cross_field_contract": result_row_cross_field_contract(),
            "slot_response_contracts": slot_response_contracts(),
            "slot_response_contract_binding": {
                "manifest_must_deep_equal_registration": True,
                "canonical_json_sha256_required": True,
                "provider_default_or_runtime_pointer_selection_forbidden": True,
            },
            "parser_golden_case_contracts": parser_golden_case_contracts(),
            "parser_golden_suite_rule": (
                "Each registered case has a separately hash-bound fixture and result. The "
                "same parser implementation must emit exact canonical JSON bytes for every "
                "case; the verifier validates the typed row, terminal cross-field semantics, "
                "and the registered result projection."
            ),
            "required_result_row_fields": [
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
            ],
            "result_row_json_schema": result_row_schema_contract(),
            "parser_and_schema_hash_bound_before_calls": True,
        },
        "dual_private_registry": {
            "registry_A_orders": ["BFS", "FSB", "SBF"],
            "registry_B_orders": ["BSF", "FBS", "SFB"],
            "blocks_each": 3,
            "required_fields": [
                "case_ids",
                "case_seeds",
                "payload_sha256_values",
                "expected_output_sha256",
                "builder_identity",
                "auditor_identity",
            ],
            "A_B_cases_seeds_payloads_disjoint": True,
            "registry_B_builder_or_auditor_differs_from_candidate_builder": True,
            "document_schema": {
                "schema_version": "effectslice-fg1-private-registry.v1",
                "required_top_level_fields": [
                    "schema_version",
                    "task_id",
                    "registry_id",
                    "case_ids",
                    "case_seeds",
                    "payload_sha256_values",
                    "expected_output_sha256",
                    "builder_identity",
                    "auditor_identity",
                ],
                "lists_sorted_unique": True,
                "case_count": 64,
            },
        },
        "semantic_audit": {
            "required_identities": [
                "candidate_builder_identity",
                "source_auditor_identity",
                "registry_A_builder_identity",
                "registry_A_auditor_identity",
                "registry_B_builder_identity",
                "registry_B_auditor_identity",
            ],
            "source_auditor_must_differ_from_candidate_builder": True,
            "required_reviews": [
                "task-to-span matrix",
                "atom roles and dependency edges",
                "F completeness",
                "primary reducer blindness",
                "S closure and retention",
                "scorer semantics",
                "task-specificity differential test",
            ],
            "disagreements_and_resolutions_required": True,
        },
        "replacement_policy_contract": {
            "reason_codes": [
                "full_text_unavailable",
                "source_span_atomization_infeasible",
                "deterministic_private_scorer_infeasible",
                "proprietary_data_or_retraining_required",
                "primary_reducer_no_eligible_subset",
                "structural_ladder_no_three_level_chain",
                "alternate_reducer_no_candidate",
            ],
            "current_registration_is_immutable": True,
            "amendments_must_be_empty": True,
            "nonempty_amendment_requires_successor_registration": True,
            "outcome_access": "forbidden",
            "amendment_manifest": "materialization/replacement_amendment_manifest.json",
            "successor_registration_rule": (
                "If a registered paper is statically ineligible, stop materialization before "
                "the final anchor and provider calls. Select the lowest-ranked eligible reserve "
                "from the same domain without outcome access, then commit a successor Stage 2.2 "
                "registration with complete paper/task/sentinel foreign keys and regenerated "
                "schedules. This materialization manifest remains amendments=[]."
            ),
            "no_in_place_task_rewrite": True,
        },
        "global_artifacts": [
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
        ],
        "global_artifact_schemas": {
            "request_template_manifest": {
                "schema_version": "effectslice-fg1-request-templates.v1",
                "required_top_level_fields": ["schema_version", "templates"],
                "template_required_fields": [
                    "model_slot_id",
                    "path",
                    "sha256",
                ],
                "required_model_slots": [
                    "deepseek_primary",
                    "gpt_5_5",
                    "gpt_5_6_sol",
                    "gpt_5_6_terra",
                    "claude_opus_4_7",
                    "open_seed_anchor",
                ],
                "output_limit_json_pointer_by_slot": {
                    "deepseek_primary": "/max_tokens",
                    "gpt_5_5": "/max_output_tokens",
                    "gpt_5_6_sol": "/max_output_tokens",
                    "gpt_5_6_terra": "/max_output_tokens",
                    "claude_opus_4_7": "/max_tokens",
                    "open_seed_anchor": "/max_new_tokens",
                },
            },
            "model_preflight_manifest": {
                "schema_version": "effectslice-fg1-model-preflight.v1",
                "required_top_level_fields": ["schema_version", "slots"],
                "slot_required_fields": [
                    "model_slot_id",
                    "exact_alias",
                    "status",
                    "checked_at_utc",
                    "evidence_path",
                    "evidence_sha256",
                    "request_template_sha256",
                    "response_contract_sha256",
                    "request_format_valid",
                    "response_format_valid",
                ],
                "allowed_status": ["available", "provider_or_model_unavailable"],
                "no_alias_fallback": True,
                "available_requires_both_format_valid": True,
                "credentials_must_be_environment_or_secret_store_only": True,
            },
            "result_canonicalization_manifest": {
                "schema_version": "effectslice-fg1-result-canonicalization.v2",
                "required_fields": [
                    "schema_version",
                    "parser_implementation_path",
                    "parser_implementation_sha256",
                    "implementation_builder_identity",
                    "result_row_schema_path",
                    "result_row_schema_sha256",
                    "slot_response_contracts",
                    "slot_response_contracts_sha256",
                    "golden_cases",
                    "golden_tests_passed",
                    "golden_execution_protocol",
                    "golden_timeout_seconds",
                ],
                "golden_case_required_fields": [
                    "case_id",
                    "model_slot_id",
                    "dispatch_state",
                    "terminal_outcome",
                    "termination_reason",
                    "provider_finish_reason",
                    "fixture_path",
                    "fixture_sha256",
                    "result_path",
                    "result_sha256",
                ],
                "slot_response_contracts": slot_response_contracts(),
                "golden_case_contracts": parser_golden_case_contracts(),
                "golden_tests_passed": True,
                "golden_execution_protocol": "python_isolated_json_stdin_stdout_canonical_v1",
                "golden_timeout_seconds": 120,
                "verifier_executes_golden_suite": True,
                "canonical_stdout_trailing_newline": False,
                "json_schema_validation": "registered_subset_v1",
            },
            "open_anchor_runtime_manifest": {
                "schema_version": "effectslice-fg1-open-anchor-runtime.v1",
                "required_fields": [
                    "schema_version",
                    "model_slot_id",
                    "exact_alias",
                    "revision",
                    "model_root",
                    "weight_files",
                    "tokenizer_files",
                    "config_files",
                    "dtype",
                    "quantization",
                    "generation_config",
                    "software",
                    "hardware",
                    "determinism",
                    "environment_evidence_path",
                    "environment_evidence_sha256",
                    "preflight_implementation_path",
                    "preflight_implementation_sha256",
                    "implementation_builder_identity",
                    "preflight_fixture_path",
                    "preflight_fixture_sha256",
                    "preflight_result_path",
                    "preflight_result_sha256",
                    "preflight_execution_protocol",
                    "preflight_timeout_seconds",
                ],
                "model_slot_id": "open_seed_anchor",
                "exact_alias": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "generation_config": {
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
                },
                "file_inventory_contract": {
                    "weight_globs": ["*.safetensors"],
                    "tokenizer_discovery_globs": [
                        "tokenizer*",
                        "vocab.*",
                        "merges.txt",
                        "special_tokens_map.json",
                        "added_tokens.json",
                        "chat_template.jinja",
                    ],
                    "tokenizer_names": [
                        "added_tokens.json",
                        "chat_template.jinja",
                        "merges.txt",
                        "special_tokens_map.json",
                        "tokenizer.json",
                        "tokenizer_config.json",
                        "tokenizer.model",
                        "vocab.json",
                        "vocab.txt",
                    ],
                    "required_tokenizer_names": ["tokenizer.json", "tokenizer_config.json"],
                    "config_names": [
                        "config.json",
                        "generation_config.json",
                        "model.safetensors.index.json",
                    ],
                    "config_discovery_globs": [
                        "config.json",
                        "generation_config.json",
                        "*.safetensors.index.json",
                    ],
                    "required_config_names": [
                        "config.json",
                        "generation_config.json",
                        "model.safetensors.index.json",
                    ],
                    "shard_index_must_exactly_cover_weight_files": True,
                    "unlisted_discovered_files_forbidden": True,
                    "revision_format": "40_lower_hex",
                    "model_root_must_be_snapshot_revision_directory": True,
                    "model_root_repository_directory": (
                        "models--Qwen--Qwen2.5-Coder-7B-Instruct"
                    ),
                },
                "required_model_config": {
                    "model_type": "qwen2",
                    "architecture": "Qwen2ForCausalLM",
                    "hidden_size": 3584,
                    "intermediate_size": 18944,
                    "num_hidden_layers": 28,
                    "num_attention_heads": 28,
                    "num_key_value_heads": 4,
                    "vocab_size": 152064,
                    "max_position_embeddings": 131072,
                },
                "allowed_dtype": ["bfloat16"],
                "allowed_quantization": ["none"],
                "software_required_fields": [
                    "python",
                    "torch",
                    "transformers",
                    "tokenizers",
                    "safetensors",
                    "accelerate",
                ],
                "hardware_required_fields": [
                    "platform",
                    "processor",
                    "cpu_count",
                    "cuda_available",
                    "cuda_device_name",
                    "cuda_capability",
                    "cuda_runtime",
                    "cudnn_version",
                    "gpu_count",
                ],
                "environment_evidence_required_fields": [
                    "schema_version",
                    "model_slot_id",
                    "exact_alias",
                    "revision",
                    "model_root",
                    "model_file_inventory_sha256",
                    "dtype",
                    "quantization",
                    "generation_config",
                    "software",
                    "hardware",
                    "determinism",
                    "preflight_result_sha256",
                ],
                "preflight_execution_protocol": "python_isolated_json_stdin_stdout_canonical_v1",
                "preflight_timeout_seconds": 1800,
                "preflight_required_result_fields": [
                    "schema_version",
                    "model_slot_id",
                    "exact_alias",
                    "revision",
                    "model_file_inventory_sha256",
                    "generation_config_sha256",
                    "input_ids_sha256",
                    "prompt_token_count",
                    "generated_token_ids",
                    "canonical_output_sha256",
                    "model_loaded",
                    "tokenizer_loaded",
                    "offline_mode",
                    "repeat_generated_token_ids_equal",
                    "repeat_canonical_output_equal",
                ],
                "preflight_result_schema": open_anchor_preflight_result_schema(),
                "determinism_required": {
                    "torch_use_deterministic_algorithms": True,
                    "cudnn_benchmark": False,
                    "cudnn_deterministic": True,
                    "cuda_matmul_allow_tf32": False,
                    "cudnn_allow_tf32": False,
                    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
                    "PYTHONHASHSEED": "0",
                },
            },
            "replacement_amendment_manifest": {
                "schema_version": "effectslice-fg1-replacement-amendments.v2",
                "required_fields": ["schema_version", "amendments"],
                "amendments_must_be_empty": True,
                "nonempty_rows_forbidden": True,
            },
            "analysis_implementation_manifest": {
                "schema_version": "effectslice-fg1-analysis-implementation.v1",
                "required_fields": [
                    "schema_version",
                    "implementation_path",
                    "implementation_sha256",
                    "implementation_builder_identity",
                    "golden_fixture_path",
                    "golden_fixture_sha256",
                    "golden_result_path",
                    "golden_result_sha256",
                    "analysis_result_schema_path",
                    "analysis_result_schema_sha256",
                    "golden_tests_passed",
                    "golden_execution_protocol",
                    "golden_timeout_seconds",
                ],
                "golden_tests_passed": True,
                "golden_execution_protocol": "python_isolated_json_stdin_stdout_canonical_v1",
                "golden_timeout_seconds": 120,
                "verifier_executes_golden_suite": True,
                "canonical_stdout_trailing_newline": False,
                "json_schema_validation": "registered_subset_v1",
            },
            "implementation_source_audit_manifest": {
                "schema_version": "effectslice-fg1-implementation-source-audit.v1",
                "required_fields": ["schema_version", "audits"],
                "audit_required_fields": [
                    "component_id",
                    "implementation_path",
                    "implementation_sha256",
                    "builder_identity",
                    "auditor_identity",
                    "review_status",
                    "checks",
                    "evidence_path",
                    "evidence_sha256",
                    "reviewed_at_utc",
                ],
                "required_component_ids": [
                    "result_canonicalizer",
                    "analysis_implementation",
                    "open_anchor_preflight",
                ],
                "required_checks_by_component": implementation_source_audit_checks(),
                "review_status": "pass",
                "auditor_must_differ_from_builder": True,
                "all_implementation_hashes_must_match_bound_manifests": True,
            },
            "final_anchor_manifest": {
                "schema_version": "effectslice-fg1-final-anchor.v1",
                "required_fields": [
                    "schema_version",
                    "immutable_file_manifest_sha256",
                    "bundle_sha256",
                    "verified_at_utc",
                    "provider_calls_started",
                ],
                "provider_calls_started": False,
            },
        },
        "schedule_counts": {
            "required_remote_rows": 1200,
            "required_local_rows": 96,
            "required_total_rows": 1296,
            "optional_remote_template_rows": 192,
        },
        "schedule_family_products": {
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
                "model_slot_ids": [
                    "gpt_5_5",
                    "gpt_5_6_sol",
                    "gpt_5_6_terra",
                    "claude_opus_4_7",
                ],
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
        },
        "schedule_row_schema": {
            "unique_key": ["execution_id"],
            "pair_or_block_key": [
                "execution_family",
                "task_id",
                "variant_id",
                "model_slot_id",
                "block_id",
            ],
            "required_fields": [
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
            ],
            "derived_seed_semantics": {
                "formula": "uint32_big_endian(sha256(NUL_joined_UTF8_fields)[0:4])",
                "fields": [
                    "study_id",
                    "task_id",
                    "ascii_decimal_block_id",
                    "condition_seed_group",
                    "ascii_decimal_seed_turn_id",
                ],
                "remote_rows": (
                    "Deterministic orchestration/request seed recorded but never used "
                    "to claim closed-model determinism."
                ),
                "open_anchor_rows": "Exact model-generation seed.",
                "identity_control_F_C_same_seed_group": True,
            },
            "registry_by_block": {
                "1": "A",
                "2": "A",
                "3": "A",
                "4": "B",
                "5": "B",
                "6": "B",
            },
            "primary_orders_by_block": ["BFS", "FSB", "SBF", "BSF", "FBS", "SFB"],
            "two_arm_orders_by_block": ["FC", "CF", "FC", "CF", "FC", "CF"],
            "BFSI_orders_by_block": ["BFIS", "IFSB", "SBFI", "BSIF", "FIBS", "SIFB"],
            "pair_adjacency_required_for_two_arm_and_FI": True,
            "global_sequence_order": {
                "family_order": [
                    "primary",
                    "controls",
                    "structural_ladder",
                    "alternate_reducers",
                    "required_closed_models",
                    "open_anchor",
                ],
                "primary_task_order": [
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
                ],
                "secondary_task_order": [
                    "NLP-LLM-01",
                    "SE-PE-01",
                    "DATA-HDB-01",
                    "AGENT-TF-01",
                ],
                "required_closed_model_order": [
                    "gpt_5_5",
                    "gpt_5_6_sol",
                    "gpt_5_6_terra",
                    "claude_opus_4_7",
                ],
                "within_family": [
                    "task_id",
                    "variant_id",
                    "model_slot_id",
                    "block_id",
                    "order_position",
                ],
            },
        },
        "schedule_foreign_key_invariants": [
            "paper_id/task_id/domain matches paper_registry",
            "model_slot_id matches model registry and execution family",
            "variant_id and condition match exact family Cartesian product",
            "registry, order code, order position, and condition match block mapping",
            "all digest foreign keys exist and match bytes",
            "same pair/block shares scaffold, fixture, scorer, model, and decoding hashes",
            "F/I artifact, model-visible payload, and serialized wire-request hashes are equal",
            "no duplicate or missing Cartesian-product row",
            "global row sequence exactly matches the registered family/task/variant/model/block order",
        ],
        "parent_overlap_audit": {
            "parents": ["confirmation_v4", "confirmation_v5r2"],
            "required_zero_intersections": [
                "execution_id",
                "pair_id",
                "private_case_id",
                "derived_seed",
                "fixture_payload_sha256",
                "serialized_wire_request_sha256",
            ],
            "normalized_value_manifest": "materialization/parent_overlap_value_manifest.json",
            "normalized_value_manifest_scopes": [
                "effectslice_fg1",
                "confirmation_v4",
                "confirmation_v5r2",
            ],
            "normalized_lists_must_be_sorted_unique": True,
            "verifier_recomputes_intersections": True,
            "source_paths_and_sha256_required_for_every_normalized_list": True,
            "source_paths_must_equal_complete_registered_glob_expansion": True,
            "every_scope_field_value_list_must_be_nonempty": True,
            "source_path_bases": ["materialization_root", "forward_root", "run_root"],
            "allowed_extractors": [
                "schedule_rows_field",
                "recursive_key",
                "json_pointer_list",
                "file_sha256",
            ],
            "source_registry": overlap_source_registry(),
            "declared_values_must_equal_values_reextracted_from_hashed_sources": True,
            "analysis_source_allowlist": (
                "Only FG1 required schedule execution IDs and their derived rows; V4/V5 "
                "paths and IDs are explicitly excluded from FG1 estimators."
            ),
        },
        "hash_contract": {
            "algorithm": "sha256",
            "all_materialized_inputs_listed": True,
            "manifest_self_hash_excluded": True,
            "bundle_hash_from_canonical_sorted_path_digest_pairs": True,
            "post_anchor_mutation_forbidden": True,
            "control_file_exclusions": [
                "immutable_file_manifest.json",
                "final_anchor_manifest.json",
            ],
            "control_file_exclusion_reason": (
                "The immutable manifest cannot hash itself, and the final anchor binds the "
                "immutable-manifest hash and bundle hash; both are verified structurally."
            ),
        },
        "final_anchor_gate": [
            "Every required task and global artifact exists and parses.",
            "Every recorded sha256 matches bytes on disk.",
            "All independent audit and task-specificity gates pass.",
            "The deterministic verifier and all focused tests pass.",
            "No credentials are present in tracked or materialized artifacts.",
            "The anchor is committed and pushed before the first experiment call.",
        ],
    }


PLAN_MD = """# EffectSlice-FG1 Forward Generalization Preregistration

## Scope and status

EffectSlice-FG1 is a new forward-only SLA instance after V4 and V5. It shares protocol structure but does not edit, reopen, pool into, supersede, or statistically reuse either accepted schedule. Stage 2.2 registers the design; task materialization and immutable hashes remain pending for Stage 2.3. No experimental model call may begin before the final Stage 2.3 anchor is verified, committed, and pushed.

The study asks whether one fixed admission protocol can issue auditable task-local decisions across heterogeneous paper-derived procedures. It does not claim random sampling, a globally minimal core, or transfer from one task to users, other tasks, or a whole paper.

## Research questions

- RQ1: Can the registered B/F/S protocol issue complete task-local decisions across 12 papers and four mechanism domains?
- RQ2: How heterogeneous are paired F-B, S-B, and S-F effects when tasks are nested within papers?
- RQ3: How do structural restoration, reducer choice, compression, reliability, and cost trade off on four frozen tasks?
- RQ4: What exact candidate-state agreement and F/I repeatability are observed across required models on four prespecified sentinel tasks?
- RQ5: How stable are primary task decisions and identified bounds under the registered SLA grid, leave-one-block-out, and leave-one-paper-out sensitivity analyses?

## Sampling frame and unit

The primary frame has 12 papers, three in each of NLP, software engineering, data analysis, and agent/tool use, with two bounded tasks per paper. The independent aggregate unit is the paper (`n=12`). Tasks are nested within papers, and six blocks are paired repeated measurements within tasks; neither 24 tasks nor 432 conversations are independent papers.

Before the final Stage 2.3 anchor, every task binds a legal full text, at least two central spans, a 5-16 atom DAG, F and candidate digests, disjoint public/private registries, scorer and adapter code, a reference differential test, and an independent semantic audit. A registered static-ineligibility reason blocks the current materialization before that anchor.

The only static-ineligibility reasons are unavailable full text, infeasible source-span atomization, infeasible deterministic private scoring, required proprietary data or retraining, no eligible primary subset, no three-level structural ladder, or no alternate-reducer candidate. Any such case blocks the current materialization with `amendments=[]`. A same-domain replacement may proceed only in a separately committed successor Stage 2.2 registration that rebinds every paper/task/sentinel foreign key and regenerates all schedules before materialization resumes. Outcome-driven replacement and in-place task rewriting are forbidden.

## Primary B/F/S design

Every task receives six matched blocks and fresh B, F, and S conversations on the exact `deepseek_primary` slot. Registry A uses `BFS`, `FSB`, and `SBF`; Registry B uses `BSF`, `FBS`, and `SFB`. Every order occurs once. The 2/3 registry checks are explicit materialization/reporting audits; at the registered 5/6 total threshold they do not add independent admission strength.

- B is the bounded task and common scaffold with a zero-length canonical artifact whose
  SHA-256 is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- F is the complete source-grounded artifact.
- S is the dependency-closed strict subset from `dag_ratio_60_v1`.

The reducer reads only opaque source-locator-derived atom IDs, dependency IDs, and rendered token counts. It cannot read paper-claim, hard-contract, guardrail, scorer-interface, outcome, or model-output labels. `effectslice_atom_renderer_v1` uses UTF-8/LF and a pinned `tiktoken==0.12.0` `cl100k_base` encoding; the ratio is artifact-only `tokens(S)/tokens(F)`. The reducer enumerates every nonempty dependency-closed strict subset, retains candidates at 45-75%, targets 60%, and breaks ties by absolute target error, fewer tokens, then canonical opaque IDs. DAG acyclicity, dependency references, renderer/tokenizer bytes, the enumeration log, and reducer input/output hashes are bound before the final anchor. No eligible subset is a pre-anchor static failure, never a post-outcome repair.

The primary design contains `12 * 2 * 6 * 3 = 432` remote conversations.

## Admission rule

Operational success requires every hard contract and private score at least 0.90. Across six blocks, B succeeds at most once, F and S each succeed at least five times, and at least five valid F/S pairs satisfy `score(S) >= score(F) - 0.05`. Within each three-block registry, B succeeds at most once, F and S each succeed at least twice, and at least two valid pairs satisfy the margin. Every row must be terminal and all integrity checks must pass.

Complete valid B/F/S runs that fail a gate are Reject. The primary reason follows `full-insufficient`, `baseline-sensitive`, `slice-insufficient`, `margin-shortfall`; all failed gates remain flags. Missing transport/integrity evidence is Invalid and stays in every denominator. A completed malformed/no-submission, budget-exhausted, hard-contract-failed, or score-short response is a valid condition failure. Block-level condition success is not candidate-level admission.

Every valid terminal row has exactly one finite private score in `[0,1]`: malformed/no-submission is exactly `0.0`; budget exhaustion is scored from the terminal workspace; hard-contract failure, score shortfall, and operational success retain the frozen scorer's assertion fraction. Invalid rows have a null score. Each task's differential test exercises all five valid terminal-score cases before the anchor.

## Secondary experiments

All secondary experiments use `NLP-LLM-01`, `SE-PE-01`, `DATA-HDB-01`, and `AGENT-TF-01`. Every two-arm candidate gets a fresh adjacent F/C pair, with `FC, CF, FC, CF, FC, CF` across blocks; primary rows are not reused. Ladder and alternate reducers use `PairPass/PairFail/Invalid`, never Admit/Reject. Controls use control-specific `SanityPass/SanityFail/Invalid`: positive requires F/C sufficiency and margin, negative requires sufficient F plus repeated targeted candidate failure, and identity requires input-digest equality plus operational/contract/score agreement.

| Component | Remote conversations |
|---|---:|
| Primary B/F/S | 432 |
| Positive, destructive, and identity controls | 144 |
| Three structural restoration levels | 144 |
| Two alternate blind reducers | 96 |
| GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra, Claude Opus 4.7 with B/F/S/I | 384 |
| **Required remote total** | **1200** |

Controls are sanity states, not calibration data; no confusion matrix or error-rate claim is allowed. Restoration levels are selected by a complete deterministic chain enumeration and require `S=L0` strict-subset `L1` strict-subset `L2` strict-subset `F` before the anchor. They provide structural response evidence, not causality. Alternate reducers and model slots cannot select or rescue primary S.

The alternate DAG-greedy reducer removes atoms in reverse canonical topological order together with their present transitive dependents and retains every unique eligible trajectory state. The source-window reducer enumerates every half-open contiguous source-order window, adds transitive dependency closure, and deduplicates the eligible states. Both select by distance to 60%, fewer rendered tokens, then lexicographic atom IDs; the verifier independently recomputes their complete enumerations and selections.

I is a fresh repeat with a model-visible payload byte-identical to F. B/F/S/I orders keep F/I adjacent, balance F-before-I and I-before-F three times each, and preserve all six B/F/S projections. B/F/S alone determines candidate state. F/I reports valid pairs, success and contract-vector agreement, score delta, canonical-output equality, and raw equality. Closed slots are descriptive; the frozen local `Qwen/Qwen2.5-Coder-7B-Instruct` anchor requires 6/6 input, token-ID, canonical-output, contract, and score equality under an exact big-endian seed derivation with golden vectors. GPT-5.6 Luna and Claude Opus 4.6 are optional after required work and add 192 conversations.

The final anchor binds the Qwen revision, absolute snapshot root, index-complete weight/tokenizer/config file inventory, dtype and quantization, software and hardware evidence, greedy generation settings, and deterministic Torch/cuDNN/cuBLAS/Python flags. Generation uses `max_new_tokens=1024`, EOS IDs `[151645,151643]`, pad ID `151643`, and stops on the first EOS inclusively or the length cap. The verifier runs a frozen offline load/tokenize/generate-twice preflight and requires repeat token and canonical-output equality. Generated token IDs exclude prompt and post-EOS padding and include the first EOS. This is the only seed-controlled model claim; closed API seed fields are recorded if returned but are not relied upon.

Canonical model-visible payloads use a length-prefixed byte format over the exact task scaffold, fixture payload, and candidate artifact. Per-slot request templates reconstruct canonical non-streaming JSON wire bytes from registered JSON pointers. Raw responses are the exact post-transfer body bytes before parsing. Canonical output is extracted by a frozen slot-specific selector from strict UTF-8 JSON, newline-normalized, NFC-normalized, and UTF-8 encoded without a trailing-newline edit. Parser and analysis implementations, schemas, and golden fixtures/results are hash-bound before calls. The verifier executes both implementations in isolated Python processes with frozen JSON on stdin, requires exact canonical JSON bytes on stdout, validates the registered schemas, and rejects timeouts, stderr, nonzero exits, or byte differences.

Every primary and required model uses the same normalized 1024-token output cap. The request template maps it to `/max_tokens` for DeepSeek Chat Completions and Claude Messages, `/max_output_tokens` for OpenAI Responses, and `/max_new_tokens` for the local Qwen adapter; provider defaults are forbidden. Slot response contracts freeze the standard protocol assumption, output selector, raw finish-reason selector and normalization, and usage selectors before calls. A format-only preflight validates both request and response shape for every available exact alias. The parser golden suite separately covers every required slot, EOS, length, provider stop, a null finish reason, malformed completion, terminal transport failure, and not-dispatched unavailability. Length-capped completions keep the same frozen scorer and terminal-outcome rule.

The result parser, analysis implementation, and open-anchor preflight each record a builder identity and receive an independent source audit by a different identity. The audit evidence and exact implementation hashes are bound by the final anchor; an implementation cannot self-certify only by shipping matching golden fixtures.

At the V4 mean of 127.2 seconds, required remote work is 42.4 nominal serial call-hours and 51-70 planned call-hours with queues and network retries. This excludes the local anchor, source/task materialization, audits, scoring, plots, writing, and review; two workers give only an ideal 25.5-35 hour lower bound. Optional models add about 8-14 call-hours.

Resource reporting is descriptive and never ranks models. Every execution records frozen candidate bytes and `cl100k_base` tokens, canonical payload bytes, provider-reported input/output/total/cached tokens when valid, final-attempt and total elapsed milliseconds, retry sleep, and retry overhead. Each task-model-candidate cell shows all six registered values plus non-null count, median, range, and sum; S-F deltas require both members. Monetary cost is appendix-only and is omitted unless a dated public price table and its hash are frozen before calls.

## Statistics and figures

State counts use registered denominators. For each F-B, S-B, and S-F contrast, block differences are averaged over valid blocks only as a descriptive task value, while fixed-denominator lower/upper endpoints assign missing bounded outcomes to their extrema and average all six blocks. The two task endpoints receive fixed 0.5/0.5 paper weights, three papers receive 1/3 domain weights, and four domains receive 1/4 overall weights. Every level reports `valid_pairs/registered_pairs`. Per-task displays show six raw points, counts, median, and range, with no per-task Clopper-Pearson or six-block bootstrap intervals. Bootstrap and leave-one-paper-out recompute this same estimator.

Aggregate analysis is paper-level. Exact domain counts, leave-one-paper-out results, an equal-domain summary, and a paper-within-domain bootstrap sensitivity analysis are mandatory. The bootstrap describes this registered benchmark, not a population guarantee.

Leave-one-block-out uses the registered five-block thresholds and never deletes remaining Invalid rows. If omitting the sole Invalid row yields a complete five-block state, that recovery is labeled only as sensitivity evidence and cannot replace the six-block decision.

The required figure groups are: (1) an end-to-end real example from source span through opaque atoms, dependency DAG, F/S retained boundary, rendered payload, and terminal admission fields, plus the freeze timeline and full B/F/S/margin/integrity admission gate; (2) paper-level effect forest and a primary-only state matrix; (3) separate primary compression and two-arm Pair/Sanity panels with structural missing cells; and (4) model-by-sentinel-task candidate/F-I results, SLA sensitivity, and terminal-failure decomposition. The primary, paired-secondary, and model designs are never shown as a nonexistent full factorial. Recovered retries are annotations, not semantic failures. Empirical panels cannot use placeholders.

## Retry and forward gates

Connection resets, DNS/TLS failures, HTTP 408/429/5xx, and read timeouts receive at most five attempts with 2/4/8/16-second delays; 429 honors a larger valid `Retry-After` and deterministic execution-ID jitter. Authentication failure, absent exact aliases, malformed frozen requests, and deterministic scorer failures are not network retries. Stable execution IDs and idempotency keys are used when available; the first cryptographically valid terminal response wins and all late duplicates remain annotations. A terminal response is never rerun because its score is low. Every attempt is preserved without credentials.

Stage 2.3 starts only after the design bundle, deterministic SLA analysis, verifier, and tests pass; the Stage 2.2 report and artifacts are committed and pushed; and no experimental provider call has started. The first experiment remains prohibited until every source, span, audit, DAG, candidate, registry, scorer, adapter, test, request template, and schedule is hash-bound, exact aliases pass format-only preflight, independent implementation source audits pass, identities are recorded, and the final anchor is committed and pushed. API credentials are injected only from the environment or a secret store and never enter source, logs, fixtures, manifests, hashes, or the manuscript.

The final anchor also binds the exact 1296-row family/task/variant/model/block/condition
sequence. A normalized, sorted-unique value manifest for execution IDs, pair IDs,
private case IDs, derived seeds, fixture payload hashes, and wire-request hashes is
recomputed from the complete registered FG1/V4/V5 glob expansions with fixed extractors;
the manifest cannot choose its own source set, and every registered intersection must be zero. Only the
ordered FG1 execution-ID allowlist may enter FG1 estimators.

No page-count optimization is applied while evidence is being built.
"""


VERIFIER_WRAPPER = """from __future__ import annotations

import json

from verify_forward_preregistration_v2 import VerificationError, audit

__all__ = ["VerificationError", "audit"]


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
"""


TEST_SOURCE = """from __future__ import annotations

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
"""


def update_candidate_matrix() -> dict[str, object]:
    path = PREREG / "candidate_matrix.json"
    matrix = json.loads(path.read_text(encoding="utf-8"))
    matrix["schema_version"] = "effectslice-fg1-candidate-matrix.v2"
    matrix["registration_status"] = STATUS
    matrix["decision_time"] = (
        "Stage 2.2 design selection; final materialization eligibility remains pending"
    )
    matrix["audit_contract"] = {
        "selected_rows_are_not_materialized": True,
        "required_before_final_anchor": [
            "legal full-text digest",
            "task-to-source-span matrix",
            "two distinct task boundaries per paper",
            "reference differential test",
            "candidate builder identity",
            "independent source auditor identity",
            "registry A/B builder and auditor identities",
            "disagreement and resolution ledger",
        ],
        "source_auditor_must_differ_from_candidate_builder": True,
        "current_registration_is_immutable": True,
        "replacement_requires_committed_successor_registration": True,
        "outcome_access_during_selection_or_replacement": "forbidden",
    }
    return matrix


def update_paper_registry() -> dict[str, object]:
    path = PREREG / "paper_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    for paper in registry["papers"]:
        if paper["paper_id"] == "agent_reflexion":
            paper["persistent_id"] = "neurips:1b44b878bb782e6954cd888628510e90"
            paper["formal_identity_note"] = (
                "The hash is the NeurIPS 2023 proceedings identifier present in the "
                "DBLP retrieval URL; the arXiv identifier is not the selected identity."
            )
    registry["implementation_policy"]["canonical_reducer_runtime_gate"] = (
        "Bind the opaque atom-ID derivation, DAG validator, EffectSlice renderer v1, "
        "tiktoken 0.12.0 cl100k_base assets, and complete reducer input/enumeration/output "
        "hashes before the Stage 2.3 final anchor."
    )
    registry["sampling_frame"]["replacement_policy"] = {
        "reason_codes": [
            "full_text_unavailable",
            "source_span_atomization_infeasible",
            "deterministic_private_scorer_infeasible",
            "proprietary_data_or_retraining_required",
            "primary_reducer_no_eligible_subset",
            "structural_ladder_no_three_level_chain",
            "alternate_reducer_no_candidate",
        ],
        "procedure": (
            "A static-ineligibility reason blocks this materialization with amendments=[]. "
            "Without outcome access, use the lowest-ranked eligible reserve from the same "
            "domain only in a separately committed successor Stage 2.2 registration. The "
            "successor must update complete paper/task/sentinel foreign keys, regenerate and "
            "verify every schedule, and be pushed before materialization resumes."
        ),
        "sentinel_task_update_rule": (
            "Any affected sentinel is rebound only in the successor registration; the current "
            "materialization amendment list remains empty."
        ),
        "forbidden": (
            "No in-place task rewrite, no nonempty materialization amendment, and no "
            "replacement after outcome access or the final anchor."
        ),
    }
    return registry


def main() -> None:
    write_json("paper_registry.json", update_paper_registry())
    write_json("experiment_plan.json", build_experiment_plan())
    write_json("model_ablation_registry.json", build_model_registry())
    write_json("figure_statistical_plan.json", build_figure_plan())
    write_json("materialization_contract.json", build_materialization_contract())
    write_json("candidate_matrix.json", update_candidate_matrix())
    (PREREG / "experiment_plan.md").write_text(PLAN_MD, encoding="utf-8")
    (ROOT / "verify_forward_preregistration.py").write_text(
        VERIFIER_WRAPPER, encoding="utf-8"
    )
    (ROOT / "tests" / "test_forward_preregistration.py").write_text(
        TEST_SOURCE, encoding="utf-8"
    )


if __name__ == "__main__":
    main()
