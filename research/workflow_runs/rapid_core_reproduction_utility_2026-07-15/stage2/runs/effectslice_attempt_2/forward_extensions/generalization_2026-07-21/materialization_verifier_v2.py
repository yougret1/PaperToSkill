from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PREREG = ROOT / "preregistration"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
OPAQUE_ATOM_ID = re.compile(r"^a_[0-9a-f]{16}$")
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SECONDARY_TASKS = ["NLP-LLM-01", "SE-PE-01", "DATA-HDB-01", "AGENT-TF-01"]
NORMALIZED_MAX_OUTPUT_TOKENS = 1024
FAMILY_ORDER = [
    "primary",
    "controls",
    "structural_ladder",
    "alternate_reducers",
    "required_closed_models",
    "open_anchor",
]
PRIMARY_ORDERS = ["BFS", "FSB", "SBF", "BSF", "FBS", "SFB"]
PAIR_ORDERS = ["FC", "CF", "FC", "CF", "FC", "CF"]
BFSI_ORDERS = ["BFIS", "IFSB", "SBFI", "BSIF", "FIBS", "SIFB"]
REQUIRED_CLOSED_MODELS = [
    "gpt_5_5",
    "gpt_5_6_sol",
    "gpt_5_6_terra",
    "claude_opus_4_7",
]
REQUIRED_HASH_FIELDS = [
    "task_scaffold_sha256",
    "fixture_manifest_sha256",
    "fixture_payload_sha256",
    "private_registry_manifest_sha256",
    "scorer_manifest_sha256",
    "candidate_artifact_sha256",
    "canonical_model_visible_payload_sha256",
    "serialized_wire_request_sha256",
    "decoding_config_sha256",
]
EXPECTED_FAMILY_COUNTS = {
    "primary": 432,
    "controls": 144,
    "structural_ladder": 144,
    "alternate_reducers": 96,
    "required_closed_models": 384,
    "open_anchor": 96,
}
OVERLAP_FIELDS = [
    "execution_id",
    "pair_id",
    "private_case_id",
    "derived_seed",
    "fixture_payload_sha256",
    "serialized_wire_request_sha256",
]
OVERLAP_SCOPES = [
    "effectslice_fg1",
    "confirmation_v4",
    "confirmation_v5r2",
]
SEMANTIC_REDUCER_FIELDS = {
    "paper_claim_label",
    "hard_contract_label",
    "guardrail_label",
    "scorer_interface_label",
    "public_outcome",
    "private_outcome",
    "model_output",
}


class MaterializationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MaterializationError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing materialization file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"expected object in {path}")
    return value


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


_SCHEMA_KEYWORDS = {
    "$id",
    "$schema",
    "additionalProperties",
    "allOf",
    "anyOf",
    "const",
    "description",
    "enum",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "items",
    "maxItems",
    "maxLength",
    "maximum",
    "minItems",
    "minLength",
    "minimum",
    "oneOf",
    "pattern",
    "properties",
    "required",
    "title",
    "type",
}


def _json_type_matches(value: object, expected: str) -> bool:
    return {
        "array": isinstance(value, list),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "null": value is None,
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "object": isinstance(value, dict),
        "string": isinstance(value, str),
    }.get(expected, False)


def _validate_registered_schema(value: object, schema: object, label: str = "$") -> None:
    require(isinstance(schema, dict), f"JSON schema node must be an object: {label}")
    unknown = set(schema) - _SCHEMA_KEYWORDS
    require(not unknown, f"unsupported JSON schema keywords at {label}: {sorted(unknown)}")

    if "allOf" in schema:
        require(isinstance(schema["allOf"], list), f"allOf must be a list: {label}")
        for index, child in enumerate(schema["allOf"]):
            _validate_registered_schema(value, child, f"{label}.allOf[{index}]")
    for keyword, required_count in (("anyOf", 1), ("oneOf", 1)):
        if keyword not in schema:
            continue
        choices = schema[keyword]
        require(isinstance(choices, list) and choices, f"{keyword} must be nonempty: {label}")
        matches = 0
        for child in choices:
            try:
                _validate_registered_schema(value, child, label)
            except MaterializationError:
                continue
            matches += 1
        require(
            matches >= required_count if keyword == "anyOf" else matches == required_count,
            f"{keyword} mismatch: {label}",
        )

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = [expected_type] if isinstance(expected_type, str) else expected_type
        require(
            isinstance(expected_types, list)
            and expected_types
            and all(isinstance(item, str) for item in expected_types),
            f"invalid schema type declaration: {label}",
        )
        require(
            any(_json_type_matches(value, item) for item in expected_types),
            f"JSON schema type mismatch: {label}",
        )
    if "const" in schema:
        require(value == schema["const"], f"JSON schema const mismatch: {label}")
    if "enum" in schema:
        require(isinstance(schema["enum"], list) and value in schema["enum"], f"JSON schema enum mismatch: {label}")

    if isinstance(value, dict):
        required_fields = schema.get("required", [])
        require(isinstance(required_fields, list), f"schema required must be a list: {label}")
        require(set(required_fields) <= set(value), f"JSON schema required fields missing: {label}")
        properties = schema.get("properties", {})
        require(isinstance(properties, dict), f"schema properties must be an object: {label}")
        for key, child in properties.items():
            if key in value:
                _validate_registered_schema(value[key], child, f"{label}.{key}")
        extras = set(value) - set(properties)
        additional = schema.get("additionalProperties", True)
        if additional is False:
            require(not extras, f"JSON schema additional fields: {label}/{sorted(extras)}")
        elif isinstance(additional, dict):
            for key in extras:
                _validate_registered_schema(value[key], additional, f"{label}.{key}")
        else:
            require(additional is True, f"invalid additionalProperties: {label}")
    if isinstance(value, list):
        if "minItems" in schema:
            require(len(value) >= schema["minItems"], f"JSON schema minItems: {label}")
        if "maxItems" in schema:
            require(len(value) <= schema["maxItems"], f"JSON schema maxItems: {label}")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_registered_schema(item, schema["items"], f"{label}[{index}]")
    if isinstance(value, str):
        if "minLength" in schema:
            require(len(value) >= schema["minLength"], f"JSON schema minLength: {label}")
        if "maxLength" in schema:
            require(len(value) <= schema["maxLength"], f"JSON schema maxLength: {label}")
        if "pattern" in schema:
            require(re.search(str(schema["pattern"]), value) is not None, f"JSON schema pattern: {label}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema:
            require(value >= schema["minimum"], f"JSON schema minimum: {label}")
        if "maximum" in schema:
            require(value <= schema["maximum"], f"JSON schema maximum: {label}")
        if "exclusiveMinimum" in schema:
            require(value > schema["exclusiveMinimum"], f"JSON schema exclusiveMinimum: {label}")
        if "exclusiveMaximum" in schema:
            require(value < schema["exclusiveMaximum"], f"JSON schema exclusiveMaximum: {label}")


def _validate_result_row_semantics(
    row: dict[str, Any],
    label: str,
    model_slot_id: str | None = None,
    open_anchor_generation_config: dict[str, Any] | None = None,
) -> None:
    outcome = row.get("terminal_outcome")
    reason = row.get("termination_reason")
    finish = row.get("provider_finish_reason")
    for field in (
        "candidate_artifact_bytes",
        "candidate_artifact_cl100k_tokens",
        "canonical_model_visible_payload_bytes",
    ):
        value = row.get(field)
        require(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0,
            f"{label} artifact endpoint must be present: {field}",
        )
    for path_field, hash_field in (
        ("raw_response_path", "raw_response_sha256"),
        ("canonical_output_path", "canonical_output_sha256"),
    ):
        require(
            (row.get(path_field) is None) == (row.get(hash_field) is None),
            f"{label} path/hash pair mismatch: {path_field}",
        )
    completed_outcomes = {
        "integrity_or_digest_failure",
        "malformed_or_no_submission",
        "action_budget_exhausted",
        "hard_contract_failure",
        "score_shortfall",
        "operational_success",
    }
    if outcome == "provider_or_model_unavailable":
        require(reason == "not_dispatched", f"{label} unavailable termination mismatch")
        require(finish is None, f"{label} unavailable row has provider finish reason")
    elif outcome == "transport_terminal_failure":
        require(reason == "transport_failure", f"{label} transport termination mismatch")
        require(finish is None, f"{label} transport row has provider finish reason")
    else:
        require(outcome in completed_outcomes, f"{label} unknown completed outcome")
        require(
            reason in {"eos", "length", "provider_stop"},
            f"{label} completed-body termination mismatch",
        )

    invalid_outcomes = {
        "provider_or_model_unavailable",
        "transport_terminal_failure",
        "integrity_or_digest_failure",
    }
    if outcome in invalid_outcomes:
        require(row.get("row_valid") is False, f"{label} invalid outcome row_valid")
        require(row.get("condition_success") is None, f"{label} invalid outcome success")
        require(row.get("private_score") is None, f"{label} invalid outcome score")
        for field in (
            "canonical_output_path",
            "canonical_output_sha256",
            "generated_token_ids",
            "hard_contract_vector",
        ):
            require(row.get(field) is None, f"{label} invalid outcome field must be null: {field}")
    else:
        require(row.get("row_valid") is True, f"{label} valid outcome row_valid")
        expected_success = outcome == "operational_success"
        require(
            row.get("condition_success") is expected_success,
            f"{label} condition-success truth table",
        )
        score = row.get("private_score")
        require(
            isinstance(score, (int, float))
            and not isinstance(score, bool)
            and 0.0 <= float(score) <= 1.0,
            f"{label} valid outcome score",
        )
        if outcome == "malformed_or_no_submission":
            require(float(score) == 0.0, f"{label} malformed score must be zero")

    completed_body = reason in {"eos", "length", "provider_stop"}
    if completed_body:
        require(
            row.get("raw_response_path") is not None,
            f"{label} completed body requires raw response",
        )
    if outcome in {
        "action_budget_exhausted",
        "hard_contract_failure",
        "score_shortfall",
        "operational_success",
    }:
        require(
            row.get("canonical_output_path") is not None,
            f"{label} scored outcome requires canonical output",
        )
        require(
            isinstance(row.get("hard_contract_vector"), list),
            f"{label} scored outcome requires hard-contract vector",
        )

    if outcome == "provider_or_model_unavailable":
        require(
            row.get("raw_response_path") is None,
            f"{label} unavailable row cannot have raw response",
        )
        require(row.get("attempts") == [], f"{label} unavailable row must have no attempts")
        for field in (
            "terminal_attempt_elapsed_ms",
            "total_execution_elapsed_ms",
            "retry_sleep_elapsed_ms",
            "retry_overhead_ms",
        ):
            require(row.get(field) is None, f"{label} unavailable timing must be null: {field}")
    else:
        attempts = row.get("attempts")
        require(
            isinstance(attempts, list) and len(attempts) > 0,
            f"{label} dispatched row must have attempts",
        )
        for field in (
            "terminal_attempt_elapsed_ms",
            "total_execution_elapsed_ms",
            "retry_sleep_elapsed_ms",
            "retry_overhead_ms",
        ):
            require(
                row.get(field) is not None,
                f"{label} dispatched timing must be non-null: {field}",
            )
        require(
            row.get("retry_sleep_elapsed_ms")
            == sum(attempt["retry_sleep_after_attempt_ms"] for attempt in attempts),
            f"{label} retry sleep arithmetic",
        )
        require(
            [attempt["attempt_index"] for attempt in attempts]
            == list(range(1, len(attempts) + 1)),
            f"{label} attempt indices must be consecutive",
        )
        require(
            row.get("terminal_attempt_elapsed_ms") == attempts[-1]["attempt_elapsed_ms"],
            f"{label} terminal attempt timing mismatch",
        )
        require(
            attempts[-1]["retry_sleep_after_attempt_ms"] == 0,
            f"{label} terminal attempt cannot have retry sleep",
        )

    usage = [
        row.get("provider_reported_input_tokens"),
        row.get("provider_reported_output_tokens"),
        row.get("provider_reported_total_tokens"),
    ]
    usage_missing_reason = row.get("provider_usage_missing_reason")
    usage_all_present = all(value is not None for value in usage)
    usage_all_null = all(value is None for value in usage)
    require(
        usage_all_present or usage_all_null,
        f"{label} provider usage tuple must be complete or all null",
    )
    if usage_all_present:
        require(
            usage_missing_reason is None,
            f"{label} reported provider usage cannot have a missing reason",
        )
        require(usage[2] == usage[0] + usage[1], f"{label} provider usage total")
    else:
        require(
            usage_missing_reason
            in {
                "not_dispatched",
                "transport_failure_no_usage",
                "provider_omitted_usage",
                "malformed_usage_tuple_or_integrity_failure",
            },
            f"{label} null provider usage requires a missing reason",
        )
        if outcome == "provider_or_model_unavailable":
            allowed_usage_missing_reasons = {"not_dispatched"}
        elif outcome == "transport_terminal_failure":
            allowed_usage_missing_reasons = {"transport_failure_no_usage"}
        else:
            allowed_usage_missing_reasons = {
                "provider_omitted_usage",
                "malformed_usage_tuple_or_integrity_failure",
            }
        require(
            usage_missing_reason in allowed_usage_missing_reasons,
            f"{label} provider usage missing reason conflicts with terminal outcome",
        )
    total_ms = row.get("total_execution_elapsed_ms")
    terminal_ms = row.get("terminal_attempt_elapsed_ms")
    retry_overhead_ms = row.get("retry_overhead_ms")
    if total_ms is not None and terminal_ms is not None and retry_overhead_ms is not None:
        require(total_ms >= terminal_ms, f"{label} total timing precedes terminal attempt")
        require(
            retry_overhead_ms == total_ms - terminal_ms,
            f"{label} retry overhead arithmetic",
        )
        require(
            retry_overhead_ms + 1 >= row.get("retry_sleep_elapsed_ms"),
            f"{label} retry overhead excludes registered sleep",
        )
        attempt_component_ms = sum(
            attempt["attempt_elapsed_ms"] for attempt in row.get("attempts")
        ) + row.get("retry_sleep_elapsed_ms")
        require(
            total_ms + len(row.get("attempts")) + 1 >= attempt_component_ms,
            f"{label} total timing omits attempt components",
        )

    generated_token_ids = row.get("generated_token_ids")
    if outcome in invalid_outcomes:
        require(
            generated_token_ids is None,
            f"{label} invalid outcome generated token IDs must be null",
        )
    elif model_slot_id == "open_seed_anchor":
        require(
            isinstance(open_anchor_generation_config, dict),
            f"{label} open-anchor generation contract missing",
        )
        _validate_open_anchor_generated_token_ids(
            generated_token_ids,
            open_anchor_generation_config,
            label,
        )
        eos_token_ids = open_anchor_generation_config["eos_token_id"]
        max_new_tokens = open_anchor_generation_config["max_new_tokens"]
        if reason == "eos":
            require(
                generated_token_ids[-1] in eos_token_ids,
                f"{label} EOS termination must end in registered EOS",
            )
        elif reason == "length":
            require(
                len(generated_token_ids) == max_new_tokens
                and not any(token_id in eos_token_ids for token_id in generated_token_ids),
                f"{label} length termination token semantics",
            )
        else:
            require(False, f"{label} open-anchor termination reason")
    elif model_slot_id is not None:
        require(
            generated_token_ids is None,
            f"{label} closed-model token IDs must be null",
        )


def _validate_open_anchor_generated_token_ids(
    generated_token_ids: object,
    generation_config: dict[str, Any],
    label: str,
) -> None:
    max_new_tokens = generation_config.get("max_new_tokens")
    eos_token_ids = generation_config.get("eos_token_id")
    require(
        isinstance(max_new_tokens, int) and max_new_tokens >= 1,
        f"{label} max_new_tokens contract",
    )
    require(
        isinstance(eos_token_ids, list)
        and bool(eos_token_ids)
        and all(isinstance(token_id, int) for token_id in eos_token_ids),
        f"{label} EOS token contract",
    )
    require(
        isinstance(generated_token_ids, list)
        and bool(generated_token_ids)
        and len(generated_token_ids) <= max_new_tokens,
        f"{label} generated token length",
    )
    first_eos_index = next(
        (
            index
            for index, token_id in enumerate(generated_token_ids)
            if token_id in eos_token_ids
        ),
        None,
    )
    if first_eos_index is None:
        require(
            len(generated_token_ids) == max_new_tokens,
            f"{label} short generation must terminate with EOS",
        )
    else:
        require(
            first_eos_index == len(generated_token_ids) - 1,
            f"{label} first EOS must be the final generated token",
        )


def _validate_implementation_source_audit(
    materialization_root: Path,
    source_audit_schema: dict[str, Any],
    implementation_records: dict[str, dict[str, str]],
) -> set[str]:
    source_audit = load_json(
        materialization_root / "implementation_source_audit_manifest.json"
    )
    require(
        source_audit.get("schema_version") == source_audit_schema["schema_version"],
        "implementation source-audit schema",
    )
    require(
        set(source_audit_schema["required_fields"]) <= set(source_audit),
        "implementation source-audit fields",
    )
    audits = source_audit["audits"]
    required_components = source_audit_schema["required_component_ids"]
    require(
        isinstance(audits, list)
        and [row.get("component_id") for row in audits if isinstance(row, dict)]
        == required_components,
        "implementation source-audit component order",
    )
    audit_required_fields = set(source_audit_schema["audit_required_fields"])
    referenced: set[str] = set()
    for row in audits:
        require(
            isinstance(row, dict) and audit_required_fields <= set(row),
            "implementation source-audit row fields",
        )
        component_id = str(row["component_id"])
        expected = implementation_records[component_id]
        require(
            row["implementation_path"] == expected["implementation_path"]
            and row["implementation_sha256"] == expected["implementation_sha256"]
            and row["builder_identity"] == expected["builder_identity"],
            f"implementation source-audit binding: {component_id}",
        )
        require(
            isinstance(row["auditor_identity"], str)
            and row["auditor_identity"]
            and row["auditor_identity"] != row["builder_identity"],
            f"implementation source-audit independence: {component_id}",
        )
        require(
            row["review_status"] == source_audit_schema["review_status"]
            and row["checks"]
            == source_audit_schema["required_checks_by_component"][component_id],
            f"implementation source-audit verdict/checks: {component_id}",
        )
        require(
            isinstance(row["reviewed_at_utc"], str) and row["reviewed_at_utc"],
            f"implementation source-audit timestamp: {component_id}",
        )
        _require_hashed_file(
            materialization_root,
            row["evidence_path"],
            row["evidence_sha256"],
            f"implementation source-audit evidence: {component_id}",
        )
        referenced.add(str(row["evidence_path"]))
    return referenced


def _isolated_environment() -> dict[str, str]:
    blocked_fragments = ("API_KEY", "PASSWORD", "SECRET", "TOKEN", "CREDENTIAL")
    blocked_exact = {"ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY"}
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() not in blocked_exact
        and not any(fragment in key.upper() for fragment in blocked_fragments)
    }
    environment.update(
        {
            "HF_HUB_OFFLINE": "1",
            "NO_PROXY": "*",
            "PYTHONHASHSEED": "0",
            "PYTHONUTF8": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }
    )
    return environment


def _execute_golden_json_transform(
    implementation_path: Path,
    fixture_path: Path,
    golden_result_path: Path,
    result_schema_path: Path | dict[str, Any] | None,
    timeout_seconds: int,
    label: str,
) -> dict[str, Any]:
    require(implementation_path.suffix.lower() == ".py", f"{label} implementation must be Python")
    require(isinstance(timeout_seconds, int) and 1 <= timeout_seconds <= 1800, f"{label} timeout")
    fixture_bytes = fixture_path.read_bytes()
    try:
        json.loads(fixture_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"{label} fixture is not strict UTF-8 JSON: {exc}") from exc
    golden_bytes = golden_result_path.read_bytes()
    try:
        golden_value = json.loads(golden_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"{label} golden result is not strict UTF-8 JSON: {exc}") from exc
    require(golden_bytes == _canonical_json(golden_value), f"{label} golden result is not canonical JSON bytes")
    schema = (
        load_json(result_schema_path)
        if isinstance(result_schema_path, Path)
        else result_schema_path
    )
    if schema is not None:
        _validate_registered_schema(golden_value, schema, f"{label}.golden")
    try:
        with tempfile.TemporaryDirectory(prefix="effectslice-golden-") as temporary:
            completed = subprocess.run(
                [sys.executable, "-I", str(implementation_path.resolve())],
                input=fixture_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=temporary,
                env=_isolated_environment(),
                check=False,
                timeout=timeout_seconds,
            )
    except subprocess.TimeoutExpired as exc:
        raise MaterializationError(f"{label} golden execution timed out") from exc
    require(completed.returncode == 0, f"{label} golden execution failed: exit={completed.returncode}")
    require(completed.stderr == b"", f"{label} golden execution wrote stderr")
    require(completed.stdout == golden_bytes, f"{label} golden execution bytes differ")
    actual_value = json.loads(completed.stdout.decode("utf-8"))
    if schema is not None:
        _validate_registered_schema(actual_value, schema, f"{label}.actual")
    return actual_value


def _strict_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    require(set(value) == expected, f"{label} fields changed: {sorted(set(value) ^ expected)}")


def preregistrations(
    prereg_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = prereg_root or PREREG
    return (
        load_json(root / "experiment_plan.json"),
        load_json(root / "paper_registry.json"),
        load_json(root / "model_ablation_registry.json"),
        load_json(root / "materialization_contract.json"),
    )


def task_maps(registry: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    papers = registry.get("papers")
    require(isinstance(papers, list), "paper registry papers must be a list")
    task_to_paper: dict[str, str] = {}
    task_to_domain: dict[str, str] = {}
    for paper in papers:
        require(isinstance(paper, dict), "paper registry row must be an object")
        tasks = paper.get("tasks")
        require(isinstance(tasks, list), "paper tasks must be a list")
        for task in tasks:
            require(isinstance(task, dict), "task row must be an object")
            task_id = task.get("task_id")
            require(isinstance(task_id, str) and task_id, "task_id missing")
            require(task_id not in task_to_paper, f"duplicate task_id: {task_id}")
            task_to_paper[task_id] = str(paper.get("paper_id"))
            task_to_domain[task_id] = str(paper.get("domain"))
    return task_to_paper, task_to_domain


def _family_definition(
    family: str,
    primary_tasks: list[str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    if family == "primary":
        return primary_tasks, ["primary_dag_ratio_60_v1"], ["deepseek_primary"], PRIMARY_ORDERS
    if family == "controls":
        return (
            SECONDARY_TASKS,
            [
                "planted_redundancy_positive",
                "destructive_core_negative",
                "byte_identical_identity",
            ],
            ["deepseek_primary"],
            PAIR_ORDERS,
        )
    if family == "structural_ladder":
        return (
            SECONDARY_TASKS,
            ["L0_primary_slice", "L1_mid_restore", "L2_near_full_strict"],
            ["deepseek_primary"],
            PAIR_ORDERS,
        )
    if family == "alternate_reducers":
        return (
            SECONDARY_TASKS,
            ["dag_greedy_ratio_60_v1", "source_window_ratio_60_v1"],
            ["deepseek_primary"],
            PAIR_ORDERS,
        )
    if family == "required_closed_models":
        return (
            SECONDARY_TASKS,
            ["primary_dag_ratio_60_v1"],
            REQUIRED_CLOSED_MODELS,
            BFSI_ORDERS,
        )
    if family == "open_anchor":
        return (
            SECONDARY_TASKS,
            ["primary_dag_ratio_60_v1"],
            ["open_seed_anchor"],
            BFSI_ORDERS,
        )
    raise MaterializationError(f"unknown execution family: {family}")


def expected_row_specs(
    registry: dict[str, Any], contract: dict[str, Any]
) -> list[dict[str, Any]]:
    task_to_paper, _ = task_maps(registry)
    order_contract = contract.get("schedule_row_schema", {}).get(
        "global_sequence_order", {}
    )
    require(order_contract.get("family_order") == FAMILY_ORDER, "family order changed")
    primary_tasks = order_contract.get("primary_task_order")
    require(isinstance(primary_tasks, list), "primary task order missing")
    require(
        len(primary_tasks) == len(set(primary_tasks)) == 24,
        "primary task order must contain 24 unique tasks",
    )
    require(set(primary_tasks) == set(task_to_paper), "primary task order mismatch")
    require(
        order_contract.get("secondary_task_order") == SECONDARY_TASKS,
        "secondary task order changed",
    )
    require(
        order_contract.get("required_closed_model_order") == REQUIRED_CLOSED_MODELS,
        "required closed-model order changed",
    )

    specs: list[dict[str, Any]] = []
    for family in FAMILY_ORDER:
        tasks, variants, models, orders = _family_definition(family, primary_tasks)
        for task_id in tasks:
            for variant_id in variants:
                for model_slot_id in models:
                    for block_id, order_code in enumerate(orders, start=1):
                        for order_position, condition in enumerate(order_code, start=1):
                            specs.append(
                                {
                                    "execution_family": family,
                                    "task_id": task_id,
                                    "variant_id": variant_id,
                                    "model_slot_id": model_slot_id,
                                    "block_id": block_id,
                                    "order_code": order_code,
                                    "order_position": order_position,
                                    "condition": condition,
                                }
                            )
    require(len(specs) == 1296, "expected schedule arithmetic changed")
    return specs


def _candidate_id(family: str, variant: str, condition: str) -> str:
    if family == "primary":
        return {"B": "B_empty_artifact", "F": "F", "S": "S_dag_ratio_60_v1"}[
            condition
        ]
    if family in {"required_closed_models", "open_anchor"}:
        return {
            "B": "B_empty_artifact",
            "F": "F",
            "S": "S_dag_ratio_60_v1",
            "I": "F",
        }[condition]
    if family == "controls":
        return {
            "planted_redundancy_positive": {
                "F": "control_positive_reference",
                "C": "F",
            },
            "destructive_core_negative": {"F": "F", "C": "control_negative"},
            "byte_identical_identity": {"F": "F", "C": "control_identity"},
        }[variant][condition]
    if family == "structural_ladder":
        return {
            "L0_primary_slice": {"F": "F", "C": "ladder_L0"},
            "L1_mid_restore": {"F": "F", "C": "ladder_L1"},
            "L2_near_full_strict": {"F": "F", "C": "ladder_L2"},
        }[variant][condition]
    if family == "alternate_reducers":
        return {
            "dag_greedy_ratio_60_v1": {
                "F": "F",
                "C": "alternate_dag_greedy",
            },
            "source_window_ratio_60_v1": {
                "F": "F",
                "C": "alternate_source_window",
            },
        }[variant][condition]
    raise MaterializationError(f"candidate mapping missing: {family}/{variant}/{condition}")


def _seed(fields: list[str]) -> int:
    digest = hashlib.sha256(b"\0".join(field.encode("utf-8") for field in fields)).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def _seed_group(family: str, variant: str, condition: str) -> str:
    if condition == "B":
        return "baseline"
    if condition in {"F", "I"}:
        return "full_identity_pair"
    if condition == "S":
        return "slice"
    if family == "controls" and variant == "byte_identical_identity":
        return "full_identity_pair"
    return "candidate_" + variant


def validate_schedule_rows(
    rows: list[dict[str, Any]],
    registry: dict[str, Any],
    model_registry: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, object]:
    specs = expected_row_specs(registry, contract)
    slots = model_registry.get("model_slots")
    require(isinstance(slots, list), "model registry slots missing")
    known_slots = {str(slot.get("slot_id")) for slot in slots if isinstance(slot, dict)}
    known_slots.add(str(model_registry.get("primary_model_reference", {}).get("slot_id")))
    required_fields = contract.get("schedule_row_schema", {}).get("required_fields")
    require(isinstance(required_fields, list), "schedule required fields missing")
    require(len(required_fields) == len(set(required_fields)), "duplicate required field")
    required = set(required_fields)
    task_to_paper, task_to_domain = task_maps(registry)

    require(isinstance(rows, list), "schedule rows must be a list")
    require(len(rows) == len(specs) == 1296, "schedule must contain 1296 rows")
    require(all(isinstance(row, dict) for row in rows), "every schedule row must be an object")
    execution_ids = [row.get("execution_id") for row in rows]
    require(
        all(isinstance(value, str) and value for value in execution_ids),
        "execution_id must be a nonempty string",
    )
    require(len(execution_ids) == len(set(execution_ids)), "duplicate execution_id")
    require(
        [row.get("global_sequence_index") for row in rows]
        == list(range(1, len(rows) + 1)),
        "global sequence is not contiguous",
    )

    grouped: dict[tuple[str, str, str, str, int], list[dict[str, Any]]] = defaultdict(list)
    pair_to_group: dict[str, tuple[str, str, str, str, int]] = {}
    artifacts: dict[tuple[str, str], str] = {}
    for index, (row, spec) in enumerate(zip(rows, specs, strict=True), start=1):
        missing = required - set(row)
        require(not missing, f"row {index} missing fields: {sorted(missing)}")
        for field in (
            "execution_family",
            "task_id",
            "variant_id",
            "model_slot_id",
            "block_id",
            "order_code",
            "order_position",
            "condition",
        ):
            require(row[field] == spec[field], f"global row order mismatch at {index}: {field}")

        task_id = row["task_id"]
        require(row["study_id"] == "EffectSlice-FG1", f"wrong study at row {index}")
        require(row["paper_id"] == task_to_paper[task_id], f"wrong paper at row {index}")
        require(row["domain"] == task_to_domain[task_id], f"wrong domain at row {index}")
        require(
            row["registry_id"] == ("A" if row["block_id"] <= 3 else "B"),
            f"wrong registry at row {index}",
        )
        require(row["model_slot_id"] in known_slots, f"unknown model slot at row {index}")
        candidate_id = _candidate_id(
            row["execution_family"], row["variant_id"], row["condition"]
        )
        require(row["candidate_id"] == candidate_id, f"wrong candidate at row {index}")
        for field in REQUIRED_HASH_FIELDS:
            require(bool(HEX64.fullmatch(str(row[field]))), f"invalid {field} at row {index}")
        seed = row["derived_seed"]
        require(isinstance(seed, int) and 0 <= seed <= 0xFFFFFFFF, f"invalid seed at row {index}")
        turn_id = row["seed_turn_id"]
        require(isinstance(turn_id, int) and turn_id >= 0, f"invalid seed_turn_id at row {index}")
        expected_seed = _seed(
            [
                row["study_id"],
                task_id,
                str(row["block_id"]),
                _seed_group(row["execution_family"], row["variant_id"], row["condition"]),
                str(turn_id),
            ]
        )
        require(seed == expected_seed, f"derived seed mismatch at row {index}")

        group_key = (
            row["execution_family"],
            task_id,
            row["variant_id"],
            row["model_slot_id"],
            row["block_id"],
        )
        pair_id = row["pair_id"]
        require(isinstance(pair_id, str) and pair_id, f"invalid pair_id at row {index}")
        prior_group = pair_to_group.setdefault(pair_id, group_key)
        require(prior_group == group_key, f"pair_id reused across groups: {pair_id}")
        grouped[group_key].append(row)

        artifact_key = (task_id, candidate_id)
        prior_artifact = artifacts.setdefault(artifact_key, row["candidate_artifact_sha256"])
        require(prior_artifact == row["candidate_artifact_sha256"], f"candidate bytes drift: {artifact_key}")
        if candidate_id == "B_empty_artifact":
            require(
                row["candidate_artifact_sha256"] == EMPTY_SHA256,
                f"baseline is not the registered empty artifact at row {index}",
            )

    for group_key, group_rows in grouped.items():
        positions = [row["global_sequence_index"] for row in group_rows]
        require(
            positions == list(range(positions[0], positions[0] + len(positions))),
            f"non-adjacent block/pair rows: {group_key}",
        )
        require(len({row["pair_id"] for row in group_rows}) == 1, f"pair_id mismatch: {group_key}")
        for field in (
            "task_scaffold_sha256",
            "fixture_manifest_sha256",
            "fixture_payload_sha256",
            "scorer_manifest_sha256",
            "decoding_config_sha256",
        ):
            require(len({row[field] for row in group_rows}) == 1, f"pair {field} mismatch: {group_key}")
        by_condition = {row["condition"]: row for row in group_rows}
        if "F" in by_condition and "I" in by_condition:
            for field in (
                "candidate_artifact_sha256",
                "canonical_model_visible_payload_sha256",
                "serialized_wire_request_sha256",
            ):
                require(
                    by_condition["F"][field] == by_condition["I"][field],
                    f"F/I {field} mismatch: {group_key}",
                )
            if group_key[0] == "open_anchor":
                require(
                    by_condition["F"]["derived_seed"]
                    == by_condition["I"]["derived_seed"],
                    f"open-anchor F/I seed mismatch: {group_key}",
                )
        if group_key[0] == "controls" and group_key[2] == "byte_identical_identity":
            for field in (
                "candidate_artifact_sha256",
                "canonical_model_visible_payload_sha256",
                "serialized_wire_request_sha256",
            ):
                require(
                    by_condition["F"][field] == by_condition["C"][field],
                    f"identity control {field} mismatch: {group_key}",
                )
            require(
                by_condition["F"]["derived_seed"] == by_condition["C"]["derived_seed"],
                f"identity control seed mismatch: {group_key}",
            )

    cross_model_frozen = contract.get("model_visible_payload_contract", {}).get(
        "cross_model_frozen_fields"
    )
    require(isinstance(cross_model_frozen, list), "cross-model frozen fields missing")
    cross_rows: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["execution_family"] in {"required_closed_models", "open_anchor"}:
            cross_rows[(row["task_id"], row["block_id"], row["condition"])].append(row)
    for cross_key, model_rows in cross_rows.items():
        require(len(model_rows) == 5, f"cross-model cell incomplete: {cross_key}")
        require(
            {row["model_slot_id"] for row in model_rows}
            == set(REQUIRED_CLOSED_MODELS) | {"open_seed_anchor"},
            f"cross-model slot set changed: {cross_key}",
        )
        for field in cross_model_frozen:
            require(
                len({row[field] for row in model_rows}) == 1,
                f"cross-model frozen input mismatch {field}: {cross_key}",
            )

    payload_contract = contract.get("model_visible_payload_contract", {})
    for task_id in task_to_paper:
        task_rows = [row for row in rows if row["task_id"] == task_id]
        for field in payload_contract.get("task_wide_frozen_fields", []):
            require(
                len({row[field] for row in task_rows}) == 1,
                f"task-wide frozen input mismatch {field}: {task_id}",
            )
        for registry_id in ("A", "B"):
            registry_rows = [row for row in task_rows if row["registry_id"] == registry_id]
            for field in payload_contract.get("task_registry_frozen_fields", []):
                require(
                    len({row[field] for row in registry_rows}) == 1,
                    f"task-registry frozen input mismatch {field}: {task_id}/{registry_id}",
                )
    for model_slot_id in known_slots:
        model_rows = [row for row in rows if row["model_slot_id"] == model_slot_id]
        if not model_rows:
            continue
        for field in payload_contract.get("model_slot_wide_frozen_fields", []):
            require(
                len({row[field] for row in model_rows}) == 1,
                f"model-slot frozen input mismatch {field}: {model_slot_id}",
            )

    for task_id in task_to_paper:
        if (task_id, "ladder_L0") in artifacts:
            require(
                artifacts[(task_id, "ladder_L0")]
                == artifacts[(task_id, "S_dag_ratio_60_v1")],
                f"ladder L0 does not equal primary S: {task_id}",
            )
        if (task_id, "control_identity") in artifacts:
            require(
                artifacts[(task_id, "control_identity")] == artifacts[(task_id, "F")],
                f"identity control does not equal F: {task_id}",
            )

    family_counts = Counter(row["execution_family"] for row in rows)
    require(dict(family_counts) == EXPECTED_FAMILY_COUNTS, "family row counts changed")
    return {"rows": len(rows), "family_counts": dict(family_counts)}


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def build_validation_fixture_rows(
    prereg_root: Path | None = None,
) -> list[dict[str, Any]]:
    _, registry, models, contract = preregistrations(prereg_root)
    task_to_paper, task_to_domain = task_maps(registry)
    specs = expected_row_specs(registry, contract)
    rows: list[dict[str, Any]] = []
    for index, spec in enumerate(specs, start=1):
        family = spec["execution_family"]
        task_id = spec["task_id"]
        variant = spec["variant_id"]
        model_slot = spec["model_slot_id"]
        block_id = spec["block_id"]
        condition = spec["condition"]
        group_label = "|".join([family, task_id, variant, model_slot, str(block_id)])
        if family in {"required_closed_models", "open_anchor"}:
            frozen_label = "|".join([task_id, str(block_id)])
        else:
            frozen_label = group_label
        task_common = _digest("task-common|" + task_id)
        registry_id = "A" if block_id <= 3 else "B"
        fixture_payload = _digest("fixture-payload|" + task_id + "|" + registry_id)
        private_registry = _digest(
            "private-registry|" + task_id + "|" + registry_id
        )
        candidate_id = _candidate_id(family, variant, condition)
        artifact_identity = {
            "control_identity": "F",
            "ladder_L0": "S_dag_ratio_60_v1",
        }.get(candidate_id, candidate_id)
        artifact = (
            EMPTY_SHA256
            if candidate_id == "B_empty_artifact"
            else _digest("artifact|" + task_id + "|" + artifact_identity)
        )
        payload_condition = "F" if condition == "I" else condition
        if family == "controls" and variant == "byte_identical_identity" and condition == "C":
            payload_condition = "F"
        payload_label = frozen_label if family in {"required_closed_models", "open_anchor"} else group_label
        payload = _digest("payload|" + payload_label + "|" + payload_condition)
        wire = _digest("wire|" + group_label + "|" + payload_condition)
        seed_group = _seed_group(family, variant, condition)
        rows.append(
            {
                "execution_id": "exec-" + _digest("exec|" + str(index) + "|" + group_label)[:24],
                "global_sequence_index": index,
                "study_id": "EffectSlice-FG1",
                "execution_family": family,
                "paper_id": task_to_paper[task_id],
                "domain": task_to_domain[task_id],
                "task_id": task_id,
                "variant_id": variant,
                "model_slot_id": model_slot,
                "registry_id": "A" if block_id <= 3 else "B",
                "block_id": block_id,
                "order_code": spec["order_code"],
                "order_position": spec["order_position"],
                "condition": condition,
                "candidate_id": candidate_id,
                "pair_id": "pair-" + _digest("pair|" + group_label)[:24],
                "task_scaffold_sha256": task_common,
                "fixture_manifest_sha256": task_common,
                "fixture_payload_sha256": fixture_payload,
                "private_registry_manifest_sha256": private_registry,
                "scorer_manifest_sha256": task_common,
                "candidate_artifact_sha256": artifact,
                "canonical_model_visible_payload_sha256": payload,
                "serialized_wire_request_sha256": wire,
                "decoding_config_sha256": _digest("decoding|" + model_slot),
                "derived_seed": _seed(
                    ["EffectSlice-FG1", task_id, str(block_id), seed_group, "0"]
                ),
                "seed_turn_id": 0,
            }
        )
    validate_schedule_rows(rows, registry, models, contract)
    return rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_bound_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative, "bound path missing")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise MaterializationError(f"bound path escapes materialization root: {relative}") from exc
    return candidate


def _require_hashed_file(root: Path, relative: object, expected: object, label: str) -> Path:
    path = _safe_bound_path(root, str(relative))
    require(path.is_file(), f"missing {label}: {relative}")
    require(bool(HEX64.fullmatch(str(expected))), f"invalid {label} digest")
    require(_sha256(path) == expected, f"{label} digest mismatch: {relative}")
    return path


def _compose_model_visible_payload(
    task_root: Path, row: dict[str, Any], contract: dict[str, Any]
) -> bytes:
    composition = contract["model_visible_payload_contract"][
        "canonical_payload_composition"
    ]
    components = {
        "task_scaffold": _safe_bound_path(task_root, str(row["task_scaffold_path"])).read_bytes(),
        "fixture_payload": _safe_bound_path(task_root, str(row["fixture_payload_path"])).read_bytes(),
        "candidate_artifact": _safe_bound_path(
            task_root, str(row["candidate_artifact_path"])
        ).read_bytes(),
    }
    payload = (str(composition["magic_ascii_line"]) + "\n").encode("ascii")
    for label in composition["field_order"]:
        value = components[str(label)]
        payload += f"{label}:{len(value)}\n".encode("ascii") + value + b"\n"
    return payload


def _set_json_pointer(document: object, pointer: str, value: object) -> None:
    require(pointer.startswith("/") and pointer != "/", f"invalid JSON pointer: {pointer}")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
    current = document
    for part in parts[:-1]:
        if isinstance(current, dict):
            require(part in current, f"request pointer missing: {pointer}")
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            require(0 <= index < len(current), f"request pointer index: {pointer}")
            current = current[index]
        else:
            raise MaterializationError(f"request pointer type mismatch: {pointer}")
    leaf = parts[-1]
    if isinstance(current, dict):
        require(leaf in current, f"request pointer leaf missing: {pointer}")
        current[leaf] = value
    elif isinstance(current, list) and leaf.isdigit():
        index = int(leaf)
        require(0 <= index < len(current), f"request pointer leaf index: {pointer}")
        current[index] = value
    else:
        raise MaterializationError(f"request pointer leaf type mismatch: {pointer}")


def _render_wire_request(
    template: dict[str, Any], payload: bytes, decoding: dict[str, Any]
) -> bytes:
    require(template.get("schema_version") == "effectslice-fg1-request-template.v1", "request template schema")
    request = copy.deepcopy(template["base_request"])
    _set_json_pointer(request, str(template["model_json_pointer"]), template["exact_alias"])
    try:
        payload_text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise MaterializationError("canonical model-visible payload is not UTF-8") from exc
    _set_json_pointer(request, str(template["payload_json_pointer"]), payload_text)
    decoding_pointers = template["decoding_field_json_pointers"]
    require(isinstance(decoding_pointers, dict), "decoding pointer map missing")
    require(set(decoding_pointers) == set(decoding), "decoding pointer/config key mismatch")
    require(
        decoding.get("normalized_max_output_tokens") == NORMALIZED_MAX_OUTPUT_TOKENS
        and "normalized_max_output_tokens" in decoding_pointers,
        "normalized output-token cap missing or changed",
    )
    for key in sorted(decoding):
        _set_json_pointer(request, str(decoding_pointers[key]), decoding[key])
    return (
        json.dumps(
            request,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        if set(value) & SEMANTIC_REDUCER_FIELDS:
            return True
        return any(_contains_forbidden_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _token_encoder() -> Any:
    try:
        import importlib.metadata
        import tiktoken
    except ImportError as exc:
        raise MaterializationError("tiktoken==0.12.0 is required for materialization audit") from exc
    require(importlib.metadata.version("tiktoken") == "0.12.0", "tiktoken version drift")
    return tiktoken.get_encoding("cl100k_base")


def _tokenizer_fingerprint_document(encoder: Any) -> dict[str, object]:
    ranks = [
        [base64.b64encode(token).decode("ascii"), int(rank)]
        for token, rank in encoder._mergeable_ranks.items()
    ]
    ranks.sort(key=lambda row: (row[1], row[0]))
    specials = sorted(
        [[str(token), int(rank)] for token, rank in encoder._special_tokens.items()]
    )
    return {
        "schema_version": "effectslice-tiktoken-fingerprint.v1",
        "package": "tiktoken",
        "version": "0.12.0",
        "encoding": "cl100k_base",
        "mergeable_rank_count": len(ranks),
        "mergeable_ranks_sha256": hashlib.sha256(_canonical_json(ranks)).hexdigest(),
        "special_token_count": len(specials),
        "special_tokens_sha256": hashlib.sha256(_canonical_json(specials)).hexdigest(),
    }


def _render_subset(
    atom_ids: tuple[str, ...] | list[str],
    canonical_order: list[str],
    text_by_id: dict[str, str],
) -> bytes:
    selected = set(atom_ids)
    ordered = [text_by_id[atom_id] for atom_id in canonical_order if atom_id in selected]
    return "\n\n".join(ordered).encode("utf-8")


def _enumerate_closed_subsets(
    atom_order: list[str],
    dependencies: dict[str, set[str]],
    text_by_id: dict[str, str],
    encoder: Any,
) -> tuple[list[dict[str, Any]], dict[tuple[str, ...], int]]:
    rows: list[dict[str, Any]] = []
    token_counts: dict[tuple[str, ...], int] = {}
    full_tuple = tuple(atom_order)
    full_tokens = len(encoder.encode(_render_subset(full_tuple, atom_order, text_by_id).decode("utf-8")))
    require(full_tokens > 0, "F must contain at least one token")
    for mask in range(1, (1 << len(atom_order)) - 1):
        atom_tuple = tuple(
            atom_id for index, atom_id in enumerate(atom_order) if mask & (1 << index)
        )
        selected = set(atom_tuple)
        if any(not dependencies[atom_id].issubset(selected) for atom_id in atom_tuple):
            continue
        tokens = len(
            encoder.encode(_render_subset(atom_tuple, atom_order, text_by_id).decode("utf-8"))
        )
        token_counts[atom_tuple] = tokens
        rows.append(
            {
                "atom_ids": list(atom_tuple),
                "rendered_token_count": tokens,
                "retained_token_ratio": round(tokens / full_tokens, 12),
            }
        )
    rows.sort(key=lambda row: tuple(row["atom_ids"]))
    return rows, token_counts


def _subset_row(
    atom_ids: tuple[str, ...],
    atom_order: list[str],
    text_by_id: dict[str, str],
    encoder: Any,
    full_tokens: int,
) -> dict[str, Any]:
    tokens = len(encoder.encode(_render_subset(atom_ids, atom_order, text_by_id).decode("utf-8")))
    return {
        "atom_ids": list(atom_ids),
        "rendered_token_count": tokens,
        "retained_token_ratio": round(tokens / full_tokens, 12),
    }


def _alternate_reducer_enumerations(
    atom_order: list[str],
    dependencies: dict[str, set[str]],
    text_by_id: dict[str, str],
    encoder: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    full_tokens = len(encoder.encode(_render_subset(atom_order, atom_order, text_by_id).decode("utf-8")))

    current = set(atom_order)
    greedy_by_ids: dict[tuple[str, ...], dict[str, Any]] = {}
    for atom_id in reversed(atom_order):
        if atom_id not in current:
            continue
        removed = {atom_id}
        changed = True
        while changed:
            changed = False
            for candidate in atom_order:
                if candidate in current and candidate not in removed and dependencies[candidate] & removed:
                    removed.add(candidate)
                    changed = True
        current -= removed
        if not current:
            continue
        atom_tuple = tuple(atom_id for atom_id in atom_order if atom_id in current)
        require(
            all(dependencies[item].issubset(current) for item in current),
            "greedy reducer produced a nonclosed state",
        )
        row = _subset_row(atom_tuple, atom_order, text_by_id, encoder, full_tokens)
        if 0.45 <= row["retained_token_ratio"] <= 0.75:
            greedy_by_ids[atom_tuple] = row

    window_by_ids: dict[tuple[str, ...], dict[str, Any]] = {}
    for start in range(len(atom_order)):
        for end in range(start + 1, len(atom_order) + 1):
            selected = set(atom_order[start:end])
            changed = True
            while changed:
                expanded = selected | {
                    dependency
                    for atom_id in selected
                    for dependency in dependencies[atom_id]
                }
                changed = expanded != selected
                selected = expanded
            if selected == set(atom_order):
                continue
            atom_tuple = tuple(atom_id for atom_id in atom_order if atom_id in selected)
            row = _subset_row(atom_tuple, atom_order, text_by_id, encoder, full_tokens)
            if 0.45 <= row["retained_token_ratio"] <= 0.75:
                window_by_ids[atom_tuple] = row

    greedy = [greedy_by_ids[key] for key in sorted(greedy_by_ids)]
    windows = [window_by_ids[key] for key in sorted(window_by_ids)]
    require(greedy and windows, "alternate reducer has no registered candidate")
    return greedy, windows


def _select_ratio_candidate(rows: list[dict[str, Any]], full_tokens: int) -> dict[str, Any]:
    return min(
        rows,
        key=lambda row: (
            abs(5 * row["rendered_token_count"] - 3 * full_tokens),
            row["rendered_token_count"],
            tuple(row["atom_ids"]),
        ),
    )


def _validate_private_registry(
    task_root: Path, task_id: str, registry_id: str
) -> tuple[dict[str, Any], set[str], set[str], set[str]]:
    filename = f"private_registry_{registry_id}_manifest.json"
    doc = load_json(task_root / filename)
    required = {
        "schema_version",
        "task_id",
        "registry_id",
        "case_ids",
        "case_seeds",
        "payload_sha256_values",
        "expected_output_sha256",
        "builder_identity",
        "auditor_identity",
    }
    _strict_keys(doc, required, filename)
    require(doc["schema_version"] == "effectslice-fg1-private-registry.v1", f"{filename} schema")
    require(doc["task_id"] == task_id and doc["registry_id"] == registry_id, f"{filename} identity")
    collections: list[set[str]] = []
    for field in ("case_ids", "case_seeds", "payload_sha256_values"):
        values = doc[field]
        require(isinstance(values, list) and len(values) == 64, f"{filename} {field} count")
        normalized = [str(value) for value in values]
        require(normalized == sorted(set(normalized)), f"{filename} {field} not sorted unique")
        collections.append(set(normalized))
    require(all(HEX64.fullmatch(value) for value in collections[2]), f"{filename} payload digest")
    require(bool(HEX64.fullmatch(str(doc["expected_output_sha256"]))), f"{filename} expected output digest")
    require(bool(str(doc["builder_identity"])) and bool(str(doc["auditor_identity"])), f"{filename} identities")
    return doc, collections[0], collections[1], collections[2]


def validate_task_artifacts(
    task_root: Path,
    task_id: str,
    is_secondary: bool,
    request_templates: dict[str, dict[str, Any]] | None = None,
) -> dict[str, object]:
    _, _, _, contract = preregistrations()
    required_names = contract["required_task_artifacts"]
    require(isinstance(required_names, list), "required task artifact list missing")
    for name in required_names:
        require((task_root / name).is_file(), f"missing task artifact {task_id}/{name}")

    generic_docs: dict[str, dict[str, Any]] = {}
    semantic_names = {
        "atom_registry.json",
        "atom_dag.json",
        "candidate_manifest.json",
        "model_visible_payload_manifest.json",
        "reducer_runtime_manifest.json",
        "reducer_input_manifest.json",
        "reducer_enumeration_manifest.json",
        "private_registry_A_manifest.json",
        "private_registry_B_manifest.json",
    }
    for name in required_names:
        if name not in semantic_names:
            doc = load_json(task_root / name)
            require(doc.get("task_id") == task_id, f"task identity mismatch: {task_id}/{name}")
            generic_docs[name] = doc

    support_schemas = contract["support_artifact_schemas"]
    support_referenced_paths: set[str] = set()
    for name, schema in support_schemas.items():
        doc = generic_docs[name]
        required_fields = set(schema["required_fields"])
        require(required_fields <= set(doc), f"support fields missing: {task_id}/{name}")
        require(
            doc.get("schema_version") == schema["schema_version"],
            f"support schema mismatch: {task_id}/{name}",
        )

    source_doc = generic_docs["source_manifest.json"]
    sources = source_doc.get("sources")
    require(isinstance(sources, list) and sources, f"sources missing: {task_id}")
    source_digests: set[str] = set()
    source_bytes: dict[str, bytes] = {}
    source_fields = set(
        support_schemas["source_manifest.json"]["source_required_fields"]
    )
    for index, source in enumerate(sources):
        require(
            isinstance(source, dict) and source_fields <= set(source),
            f"source fields missing: {task_id}/{index}",
        )
        source_path = _require_hashed_file(
            task_root,
            source["path"],
            source["sha256"],
            f"source document {task_id}/{index}",
        )
        digest = str(source["sha256"])
        require(digest not in source_digests, f"duplicate source digest: {task_id}/{digest}")
        require(
            bool(str(source["license_or_access_note"]).strip()),
            f"source access note missing: {task_id}/{index}",
        )
        source_digests.add(digest)
        source_bytes[digest] = source_path.read_bytes()
        support_referenced_paths.add(str(source["path"]))

    span_doc = generic_docs["task_to_span_matrix.json"]
    central_spans = span_doc.get("central_spans")
    require(isinstance(central_spans, list) and len(central_spans) >= 2, f"insufficient central spans: {task_id}")
    span_fields = set(contract["source_and_task_specificity"]["required_span_fields"])
    for index, span in enumerate(central_spans):
        require(isinstance(span, dict) and span_fields <= set(span), f"invalid central span {task_id}/{index}")
        document_sha = str(span["document_sha256"])
        require(document_sha in source_digests, f"central span source missing: {task_id}/{index}")
        byte_start = span["byte_start"]
        byte_end = span["byte_end"]
        require(
            isinstance(byte_start, int)
            and isinstance(byte_end, int)
            and 0 <= byte_start < byte_end <= len(source_bytes[document_sha]),
            f"central span offsets invalid: {task_id}/{index}",
        )
        require(
            hashlib.sha256(source_bytes[document_sha][byte_start:byte_end]).hexdigest()
            == span["quoted_text_sha256"],
            f"central span quote digest mismatch: {task_id}/{index}",
        )
        require(
            isinstance(span["atom_ids"], list) and span["atom_ids"],
            f"central span atoms missing: {task_id}/{index}",
        )

    public_fixture = generic_docs["public_fixture_manifest.json"]
    _require_hashed_file(
        task_root,
        public_fixture["fixture_path"],
        public_fixture["fixture_sha256"],
        f"public fixture {task_id}",
    )
    support_referenced_paths.add(str(public_fixture["fixture_path"]))
    for name in (
        "adapter_manifest.json",
        "reference_implementation_manifest.json",
        "scorer_manifest.json",
    ):
        implementation = generic_docs[name]
        _require_hashed_file(
            task_root,
            implementation["implementation_path"],
            implementation["implementation_sha256"],
            f"support implementation {task_id}/{name}",
        )
        support_referenced_paths.add(str(implementation["implementation_path"]))
    hard_contract_ids = generic_docs["scorer_manifest.json"]["hard_contract_ids"]
    require(
        isinstance(hard_contract_ids, list)
        and hard_contract_ids
        and hard_contract_ids == sorted(set(hard_contract_ids))
        and all(isinstance(value, str) and value for value in hard_contract_ids),
        f"scorer hard-contract order invalid: {task_id}",
    )

    differential = generic_docs["differential_test_report.json"]
    differential_schema = support_schemas["differential_test_report.json"]
    require(
        differential["passed"] is differential_schema["passed"]
        and isinstance(differential["comparison_count"], int)
        and differential["comparison_count"]
        >= differential_schema["minimum_comparison_count"]
        and differential["failure_count"] == differential_schema["failure_count"],
        f"differential test did not pass: {task_id}",
    )
    require(
        differential["terminal_score_semantics_passed"]
        is differential_schema["terminal_score_semantics_passed"]
        and isinstance(differential["terminal_score_case_count"], int)
        and differential["terminal_score_case_count"]
        >= differential_schema["minimum_terminal_score_case_count"],
        f"terminal score semantics not differentially tested: {task_id}",
    )

    semantic = generic_docs["semantic_audit.json"]
    semantic_schema = support_schemas["semantic_audit.json"]
    require(semantic["passed"] is semantic_schema["passed"], f"semantic audit failed: {task_id}")
    reviews = semantic["reviews"]
    require(
        isinstance(reviews, list)
        and reviews == contract["semantic_audit"]["required_reviews"],
        f"semantic review set mismatch: {task_id}",
    )
    require(
        isinstance(semantic["disagreements_and_resolutions"], list),
        f"semantic resolution ledger missing: {task_id}",
    )


    atom_registry = load_json(task_root / "atom_registry.json")
    atom_dag = load_json(task_root / "atom_dag.json")
    for doc, schema, label in (
        (atom_registry, "effectslice-fg1-atom-registry.v1", "atom registry"),
        (atom_dag, "effectslice-fg1-atom-dag.v1", "atom DAG"),
    ):
        require(doc.get("schema_version") == schema and doc.get("task_id") == task_id, f"{label} identity")
        require(isinstance(doc.get("atoms"), list), f"{label} atoms missing")
    registry_atoms = atom_registry["atoms"]
    dag_atoms = atom_dag["atoms"]
    require(5 <= len(registry_atoms) <= 16, f"atom count outside registered range: {task_id}")
    require(len(registry_atoms) == len(dag_atoms), f"atom registry/DAG length mismatch: {task_id}")

    atom_order: list[str] = []
    text_by_id: dict[str, str] = {}
    dependencies: dict[str, set[str]] = {}
    encoder = _token_encoder()
    for index, (registry_atom, dag_atom) in enumerate(zip(registry_atoms, dag_atoms, strict=True)):
        require(isinstance(registry_atom, dict) and isinstance(dag_atom, dict), f"invalid atom row: {task_id}/{index}")
        require(not _contains_forbidden_key(registry_atom), f"semantic label leaked into atom registry: {task_id}/{index}")
        atom_id = str(registry_atom.get("atom_id"))
        require(bool(OPAQUE_ATOM_ID.fullmatch(atom_id)), f"nonopaque atom ID: {task_id}/{atom_id}")
        source_locator = registry_atom.get("source_locator")
        require(isinstance(source_locator, dict), f"source locator missing: {task_id}/{atom_id}")
        _strict_keys(
            source_locator,
            {"document_sha256", "byte_start", "byte_end", "split_index"},
            f"source locator {task_id}/{atom_id}",
        )
        require(bool(HEX64.fullmatch(str(source_locator["document_sha256"]))), f"source document digest: {task_id}/{atom_id}")
        locator_document_sha = str(source_locator["document_sha256"])
        require(
            locator_document_sha in source_bytes,
            f"atom source is not registered: {task_id}/{atom_id}",
        )
        require(
            all(
                isinstance(source_locator[field], int) and source_locator[field] >= 0
                for field in ("byte_start", "byte_end", "split_index")
            )
            and source_locator["byte_end"] > source_locator["byte_start"],
            f"source locator offsets: {task_id}/{atom_id}",
        )
        require(
            source_locator["byte_end"] <= len(source_bytes[locator_document_sha]),
            f"atom source locator exceeds document: {task_id}/{atom_id}",
        )
        atom_preimage = b"\0".join(
            str(source_locator[field]).encode("ascii")
            for field in ("document_sha256", "byte_start", "byte_end", "split_index")
        )
        expected_id = "a_" + hashlib.sha256(atom_preimage).hexdigest()[:16]
        require(atom_id == expected_id, f"atom ID is not source-locator-derived: {task_id}/{atom_id}")
        rendered_text = registry_atom.get("rendered_text")
        require(isinstance(rendered_text, str) and rendered_text, f"rendered atom text missing: {task_id}/{atom_id}")
        require(hashlib.sha256(rendered_text.encode("utf-8")).hexdigest() == registry_atom.get("rendered_text_sha256"), f"rendered atom digest mismatch: {task_id}/{atom_id}")
        require(dag_atom.get("atom_id") == atom_id, f"atom registry/DAG order mismatch: {task_id}/{atom_id}")
        deps = dag_atom.get("dependency_ids")
        require(isinstance(deps, list) and deps == sorted(set(deps)), f"dependency IDs not sorted unique: {task_id}/{atom_id}")
        require(set(deps).issubset(set(atom_order)), f"DAG is non-topological or has dangling dependency: {task_id}/{atom_id}")
        atom_tokens = len(encoder.encode(rendered_text))
        require(dag_atom.get("rendered_token_count") == atom_tokens, f"atom token count mismatch: {task_id}/{atom_id}")
        atom_order.append(atom_id)
        text_by_id[atom_id] = rendered_text
        dependencies[atom_id] = set(deps)
    require(len(atom_order) == len(set(atom_order)), f"duplicate atom ID: {task_id}")
    for index, span in enumerate(central_spans):
        require(
            set(span["atom_ids"]).issubset(set(atom_order))
            and len(span["atom_ids"]) == len(set(span["atom_ids"])),
            f"central span references unknown or duplicate atoms: {task_id}/{index}",
        )

    reducer_input = load_json(task_root / "reducer_input_manifest.json")
    _strict_keys(reducer_input, {"schema_version", "task_id", "atoms"}, "reducer input")
    require(reducer_input["schema_version"] == "effectslice-fg1-reducer-input.v1" and reducer_input["task_id"] == task_id, f"reducer input identity: {task_id}")
    require(not _contains_forbidden_key(reducer_input), f"semantic field leaked into reducer input: {task_id}")
    expected_reducer_atoms = [
        {
            "atom_id": atom["atom_id"],
            "dependency_ids": atom["dependency_ids"],
            "rendered_token_count": atom["rendered_token_count"],
        }
        for atom in dag_atoms
    ]
    for index, atom in enumerate(reducer_input["atoms"]):
        require(isinstance(atom, dict), f"invalid reducer input atom: {task_id}/{index}")
        _strict_keys(atom, {"atom_id", "dependency_ids", "rendered_token_count"}, f"reducer input atom {task_id}/{index}")
    require(reducer_input["atoms"] == expected_reducer_atoms, f"reducer input differs from DAG: {task_id}")
    reducer_input_sha = _sha256(task_root / "reducer_input_manifest.json")

    runtime = load_json(task_root / "reducer_runtime_manifest.json")
    runtime_schema = contract["candidate_manifest"]["runtime_manifest_schema"]
    require(runtime.get("schema_version") == runtime_schema["schema_version"] and runtime.get("task_id") == task_id, f"runtime identity: {task_id}")
    for component_name in ("renderer", "tokenizer", "reducer"):
        component = runtime.get(component_name)
        require(isinstance(component, dict), f"runtime component missing: {task_id}/{component_name}")
        require(set(runtime_schema["component_required_fields"]) <= set(component), f"runtime component fields: {task_id}/{component_name}")
        _require_hashed_file(task_root, component["path"], component["sha256"], f"{component_name} runtime")
    renderer = runtime["renderer"]
    tokenizer = runtime["tokenizer"]
    reducer = runtime["reducer"]
    require(renderer.get("id") == "effectslice_atom_renderer_v1" and renderer.get("separator") == "\n\n" and renderer.get("encoding") == "utf-8" and renderer.get("newline") == "LF", f"renderer contract drift: {task_id}")
    require(tokenizer.get("package") == "tiktoken" and tokenizer.get("version") == "0.12.0" and tokenizer.get("encoding") == "cl100k_base", f"tokenizer contract drift: {task_id}")
    tokenizer_asset = load_json(task_root / str(tokenizer["path"]))
    require(
        tokenizer_asset == _tokenizer_fingerprint_document(encoder),
        f"tokenizer fingerprint mismatch: {task_id}",
    )
    require(reducer.get("id") == "dag_ratio_60_v1", f"reducer contract drift: {task_id}")

    subset_rows, subset_token_counts = _enumerate_closed_subsets(
        atom_order, dependencies, text_by_id, encoder
    )
    enumeration_sha = hashlib.sha256(_canonical_json(subset_rows)).hexdigest()
    full_tokens = len(encoder.encode(_render_subset(atom_order, atom_order, text_by_id).decode("utf-8")))
    eligible = [
        row
        for row in subset_rows
        if 45 * full_tokens <= 100 * row["rendered_token_count"] <= 75 * full_tokens
    ]
    require(bool(eligible), f"no eligible primary subset: {task_id}")
    selected = min(
        eligible,
        key=lambda row: (
            abs(5 * row["rendered_token_count"] - 3 * full_tokens),
            row["rendered_token_count"],
            tuple(row["atom_ids"]),
        ),
    )

    candidate_doc = load_json(task_root / "candidate_manifest.json")
    require(candidate_doc.get("schema_version") == "effectslice-fg1-candidates.v1" and candidate_doc.get("task_id") == task_id, f"candidate manifest identity: {task_id}")
    candidates = candidate_doc.get("candidates")
    require(isinstance(candidates, list), f"candidate rows missing: {task_id}")
    candidate_by_id: dict[str, dict[str, Any]] = {}
    required_fields = set(contract["candidate_manifest"]["required_fields"])
    referenced_paths: set[str] = set(required_names) | support_referenced_paths
    candidate_hashes: dict[str, str] = {}
    for candidate in candidates:
        require(isinstance(candidate, dict) and required_fields <= set(candidate), f"candidate fields missing: {task_id}")
        candidate_id = str(candidate["candidate_id"])
        require(candidate_id not in candidate_by_id, f"duplicate candidate: {task_id}/{candidate_id}")
        ids = candidate["atom_ids"]
        require(isinstance(ids, list) and ids == [atom_id for atom_id in atom_order if atom_id in set(ids)] and len(ids) == len(set(ids)), f"candidate atom order invalid: {task_id}/{candidate_id}")
        selected_set = set(ids)
        require(selected_set.issubset(set(atom_order)), f"unknown candidate atom: {task_id}/{candidate_id}")
        closed = all(dependencies[atom_id].issubset(selected_set) for atom_id in ids)
        require(candidate["dependency_closed"] is closed, f"candidate closure flag mismatch: {task_id}/{candidate_id}")
        strict = bool(selected_set) and selected_set < set(atom_order)
        if candidate_id == "B_empty_artifact":
            strict = False
        require(candidate["strict_subset"] is strict, f"candidate strict-subset flag mismatch: {task_id}/{candidate_id}")
        artifact_bytes = b"" if candidate_id == "B_empty_artifact" else _render_subset(ids, atom_order, text_by_id)
        artifact_path = _require_hashed_file(task_root, candidate["artifact_path"], candidate["artifact_sha256"], f"candidate artifact {candidate_id}")
        require(artifact_path.read_bytes() == artifact_bytes, f"candidate rendering mismatch: {task_id}/{candidate_id}")
        tokens = 0 if not artifact_bytes else len(encoder.encode(artifact_bytes.decode("utf-8")))
        ratio = round(tokens / full_tokens, 12)
        require(candidate["rendered_token_count"] == tokens and candidate["retained_token_ratio"] == ratio, f"candidate token accounting mismatch: {task_id}/{candidate_id}")
        construction_path = _require_hashed_file(task_root, candidate["construction_log_path"], candidate["construction_log_sha256"], f"candidate construction log {candidate_id}")
        require(candidate["renderer_sha256"] == renderer["sha256"] and candidate["tokenizer_asset_sha256"] == tokenizer["sha256"] and candidate["reducer_input_manifest_sha256"] == reducer_input_sha, f"candidate runtime binding mismatch: {task_id}/{candidate_id}")
        referenced_paths.update((str(candidate["artifact_path"]), str(candidate["construction_log_path"]), str(runtime["renderer"]["path"]), str(runtime["tokenizer"]["path"]), str(runtime["reducer"]["path"])))
        candidate_by_id[candidate_id] = candidate
        candidate_hashes[candidate_id] = str(candidate["artifact_sha256"])

    required_candidates = set(contract["candidate_manifest"]["required_primary_candidates"])
    if is_secondary:
        required_candidates |= set(contract["candidate_manifest"]["required_secondary_candidates"])
    require(set(candidate_by_id) == required_candidates, f"candidate set mismatch: {task_id}")
    require(candidate_by_id["B_empty_artifact"]["artifact_sha256"] == EMPTY_SHA256, f"B bytes changed: {task_id}")
    require(candidate_by_id["F"]["atom_ids"] == atom_order, f"F is incomplete: {task_id}")
    require(candidate_by_id["S_dag_ratio_60_v1"]["atom_ids"] == selected["atom_ids"], f"primary reducer selection mismatch: {task_id}")

    primary_audit = candidate_doc.get("primary_reducer_audit")
    require(isinstance(primary_audit, dict), f"primary reducer audit missing: {task_id}")
    require(primary_audit.get("selection_rule_id") == "dag_ratio_60_v1", f"primary reducer ID: {task_id}")
    require(primary_audit.get("all_closed_strict_subsets") == subset_rows, f"primary subset enumeration mismatch: {task_id}")
    require(primary_audit.get("complete_enumeration_sha256") == enumeration_sha, f"primary enumeration digest mismatch: {task_id}")
    require(primary_audit.get("eligible_subset_count") == len(eligible) and primary_audit.get("selected_candidate_id") == "S_dag_ratio_60_v1", f"primary audit selection metadata: {task_id}")

    enumeration_doc = load_json(task_root / "reducer_enumeration_manifest.json")
    expected_enumeration = {
        "schema_version": "effectslice-fg1-reducer-enumeration.v1",
        "task_id": task_id,
        "all_closed_strict_subsets": subset_rows,
        "complete_enumeration_sha256": enumeration_sha,
        "eligible_subset_count": len(eligible),
        "selected_candidate_id": "S_dag_ratio_60_v1",
    }
    require(enumeration_doc == expected_enumeration, f"standalone reducer enumeration mismatch: {task_id}")

    if is_secondary:
        require(candidate_by_id["control_identity"]["artifact_sha256"] == candidate_by_id["F"]["artifact_sha256"], f"identity control differs from F: {task_id}")
        require(candidate_by_id["ladder_L0"]["artifact_sha256"] == candidate_by_id["S_dag_ratio_60_v1"]["artifact_sha256"], f"ladder L0 differs from S: {task_id}")
        s_tuple = tuple(selected["atom_ids"])
        s_set = set(s_tuple)
        ladder_subsets = [row for row in subset_rows if s_set < set(row["atom_ids"]) < set(atom_order)]
        chains = [
            {"L1_atom_ids": left["atom_ids"], "L2_atom_ids": right["atom_ids"]}
            for left in ladder_subsets
            for right in ladder_subsets
            if set(left["atom_ids"]) < set(right["atom_ids"])
        ]
        chains.sort(key=lambda row: (tuple(row["L1_atom_ids"]), tuple(row["L2_atom_ids"])))
        require(bool(chains), f"no strict S-L1-L2-F ladder: {task_id}")
        subset_sha = hashlib.sha256(_canonical_json(ladder_subsets)).hexdigest()
        chain_sha = hashlib.sha256(_canonical_json(chains)).hexdigest()
        selected_chain = min(
            chains,
            key=lambda row: (
                -subset_token_counts[tuple(row["L2_atom_ids"])],
                abs(
                    2 * subset_token_counts[tuple(row["L1_atom_ids"])]
                    - subset_token_counts[s_tuple]
                    - subset_token_counts[tuple(row["L2_atom_ids"])]
                ),
                subset_token_counts[tuple(row["L1_atom_ids"])],
                tuple(row["L1_atom_ids"]),
                tuple(row["L2_atom_ids"]),
            ),
        )
        ladder_audit = candidate_doc.get("ladder_chain_audit")
        require(isinstance(ladder_audit, dict), f"ladder audit missing: {task_id}")
        require(ladder_audit.get("selection_rule_id") == "complete_chain_enumeration_v1", f"ladder rule ID: {task_id}")
        require(ladder_audit.get("eligible_closed_subsets") == ladder_subsets and ladder_audit.get("complete_subset_enumeration_sha256") == subset_sha, f"ladder subset enumeration mismatch: {task_id}")
        require(ladder_audit.get("all_chains") == chains and ladder_audit.get("enumerated_chain_count") == len(chains) and ladder_audit.get("complete_chain_enumeration_sha256") == chain_sha, f"ladder chain enumeration mismatch: {task_id}")
        require(ladder_audit.get("selected_chain_candidate_ids") == ["ladder_L0", "ladder_L1", "ladder_L2", "F"], f"ladder selected IDs: {task_id}")
        require(candidate_by_id["ladder_L1"]["atom_ids"] == selected_chain["L1_atom_ids"] and candidate_by_id["ladder_L2"]["atom_ids"] == selected_chain["L2_atom_ids"], f"ladder selected chain mismatch: {task_id}")
    else:
        require(candidate_doc.get("ladder_chain_audit") is None, f"non-sentinel ladder audit must be null: {task_id}")

    alternate_audit = candidate_doc.get("alternate_reducer_audit")
    if is_secondary:
        require(isinstance(alternate_audit, dict), f"alternate reducer audit missing: {task_id}")
        greedy_rows, window_rows = _alternate_reducer_enumerations(
            atom_order, dependencies, text_by_id, encoder
        )
        alternate_specs = {
            "dag_greedy_ratio_60_v1": (
                greedy_rows,
                "alternate_dag_greedy",
            ),
            "source_window_ratio_60_v1": (
                window_rows,
                "alternate_source_window",
            ),
        }
        require(set(alternate_audit) == set(alternate_specs), f"alternate audit set: {task_id}")
        for reducer_id, (enumeration, candidate_id) in alternate_specs.items():
            selected_alternate = _select_ratio_candidate(enumeration, full_tokens)
            require(
                candidate_by_id[candidate_id]["atom_ids"] == selected_alternate["atom_ids"],
                f"alternate reducer selection mismatch: {task_id}/{reducer_id}",
            )
            audit_row = alternate_audit[reducer_id]
            require(isinstance(audit_row, dict), f"alternate audit row: {task_id}/{reducer_id}")
            expected_audit = {
                "selection_rule_id": reducer_id,
                "enumeration": enumeration,
                "complete_enumeration_sha256": hashlib.sha256(
                    _canonical_json(enumeration)
                ).hexdigest(),
                "selected_candidate_id": candidate_id,
            }
            require(
                audit_row == expected_audit,
                f"alternate reducer audit mismatch: {task_id}/{reducer_id}",
            )
    else:
        require(alternate_audit is None, f"non-sentinel alternate audit must be null: {task_id}")

    registry_a, a_cases, a_seeds, a_payloads = _validate_private_registry(task_root, task_id, "A")
    registry_b, b_cases, b_seeds, b_payloads = _validate_private_registry(task_root, task_id, "B")
    require(not (a_cases & b_cases or a_seeds & b_seeds or a_payloads & b_payloads), f"private registries overlap: {task_id}")

    payload_doc = load_json(task_root / "model_visible_payload_manifest.json")
    require(payload_doc.get("schema_version") == "effectslice-fg1-model-visible-payloads.v1" and payload_doc.get("task_id") == task_id, f"payload manifest identity: {task_id}")
    payload_rows = payload_doc.get("rows")
    require(isinstance(payload_rows, list), f"payload rows missing: {task_id}")
    payload_by_execution: dict[str, dict[str, Any]] = {}
    digest_paths = contract["model_visible_payload_contract"]["digest_path_fields"]
    typed_paths = contract["model_visible_payload_contract"]["typed_path_constraints"]
    for row in payload_rows:
        require(isinstance(row, dict) and isinstance(row.get("execution_id"), str), f"invalid payload row: {task_id}")
        execution_id = row["execution_id"]
        require(execution_id not in payload_by_execution, f"duplicate payload execution: {task_id}/{execution_id}")
        expected_paths = {
            "task_scaffold_path": typed_paths["task_scaffold_path"],
            "fixture_manifest_path": typed_paths["fixture_manifest_path"],
            "fixture_payload_path": f"fixtures/{row.get('registry_id')}.json",
            "scorer_manifest_path": typed_paths["scorer_manifest_path"],
            "candidate_artifact_path": candidate_by_id.get(
                str(row.get("candidate_id")), {}
            ).get("artifact_path"),
            "canonical_model_visible_payload_path": f"payloads/{execution_id}.txt",
            "serialized_wire_request_path": f"requests/{execution_id}.json",
            "decoding_config_path": f"decoding/{row.get('model_slot_id')}.json",
            "private_registry_manifest_path": (
                f"private_registry_{row.get('registry_id')}_manifest.json"
            ),
        }
        for path_field, expected_path in expected_paths.items():
            require(
                Path(str(row.get(path_field))).as_posix() == expected_path,
                f"typed payload path mismatch: {task_id}/{execution_id}/{path_field}",
            )
        for digest_field, path_field in digest_paths.items():
            require(digest_field in row and path_field in row, f"payload binding missing: {task_id}/{execution_id}/{digest_field}")
            _require_hashed_file(task_root, row[path_field], row[digest_field], f"payload binding {digest_field}")
            referenced_paths.add(str(row[path_field]))
        for json_path_field in (
            "fixture_payload_path",
            "serialized_wire_request_path",
            "decoding_config_path",
        ):
            load_json(task_root / str(row[json_path_field]))
        require(row["candidate_artifact_sha256"] == candidate_hashes.get(row.get("candidate_id")), f"payload candidate hash mismatch: {task_id}/{execution_id}")
        canonical_payload = _compose_model_visible_payload(task_root, row, contract)
        canonical_payload_path = _safe_bound_path(
            task_root, str(row["canonical_model_visible_payload_path"])
        )
        require(
            canonical_payload_path.read_bytes() == canonical_payload,
            f"canonical payload composition mismatch: {task_id}/{execution_id}",
        )
        if request_templates is not None:
            model_slot_id = str(row["model_slot_id"])
            require(model_slot_id in request_templates, f"request template missing: {model_slot_id}")
            decoding = load_json(task_root / str(row["decoding_config_path"]))
            expected_wire = _render_wire_request(
                request_templates[model_slot_id], canonical_payload, decoding
            )
            wire_path = _safe_bound_path(task_root, str(row["serialized_wire_request_path"]))
            require(
                wire_path.read_bytes() == expected_wire,
                f"wire request composition mismatch: {task_id}/{execution_id}",
            )
        payload_by_execution[execution_id] = row

    identities = semantic.get("identities")
    require(isinstance(identities, dict), f"semantic-audit identities missing: {task_id}")
    for identity in contract["semantic_audit"]["required_identities"]:
        require(bool(str(identities.get(identity, ""))), f"semantic-audit identity missing: {task_id}/{identity}")
    require(identities["source_auditor_identity"] != identities["candidate_builder_identity"], f"source auditor equals candidate builder: {task_id}")
    require(registry_b["builder_identity"] != identities["candidate_builder_identity"] or registry_b["auditor_identity"] != identities["candidate_builder_identity"], f"registry B lacks independent identity: {task_id}")

    return {
        "candidate_hashes": candidate_hashes,
        "private_case_ids": a_cases | b_cases,
        "payload_rows": payload_by_execution,
        "referenced_paths": referenced_paths,
    }


def _recursive_key_values(value: object, key: str) -> list[object]:
    found: list[object] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                if isinstance(item_value, list):
                    found.extend(item_value)
                else:
                    found.append(item_value)
            found.extend(_recursive_key_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(_recursive_key_values(item, key))
    return found


def _extract_overlap_values(path: Path, extractor: dict[str, Any]) -> list[str]:
    if extractor.get("kind") == "file_sha256":
        return [_sha256(path)]
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"cannot parse overlap source {path}: {exc}") from exc
    kind = extractor.get("kind")
    if kind == "schedule_rows_field":
        rows = document.get("rows") if isinstance(document, dict) else None
        require(isinstance(rows, list), f"overlap schedule rows missing: {path}")
        field = str(extractor.get("field"))
        values = [row[field] for row in rows if isinstance(row, dict) and field in row]
    elif kind == "recursive_key":
        values = _recursive_key_values(document, str(extractor.get("key")))
    elif kind == "json_pointer_list":
        pointer = extractor.get("pointer")
        require(isinstance(pointer, str) and pointer.startswith("/"), f"invalid overlap JSON pointer: {path}")
        current: object = document
        for raw_part in pointer.split("/")[1:]:
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict):
                require(part in current, f"overlap pointer missing: {path}#{pointer}")
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                require(0 <= index < len(current), f"overlap pointer index: {path}#{pointer}")
                current = current[index]
            else:
                raise MaterializationError(f"overlap pointer type mismatch: {path}#{pointer}")
        require(isinstance(current, list), f"overlap pointer is not a list: {path}#{pointer}")
        values = current
    else:
        raise MaterializationError(f"unsupported overlap extractor: {kind}")
    normalized: list[str] = []
    for value in values:
        require(isinstance(value, (str, int)) and not isinstance(value, bool), f"nonscalar overlap value: {path}")
        normalized.append(str(value))
    return normalized


def _overlap_source_path(
    materialization_root: Path, source: dict[str, Any]
) -> Path:
    base_name = source.get("path_base")
    if base_name == "materialization_root":
        base = materialization_root.resolve()
    elif base_name == "forward_root":
        base = ROOT.resolve()
    elif base_name == "run_root":
        base = ROOT.parents[1].resolve()
    else:
        raise MaterializationError(f"invalid overlap source path base: {base_name}")
    path = (base / str(source.get("path"))).resolve()
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise MaterializationError(f"overlap source escapes {base_name}: {source.get('path')}") from exc
    return path


def _verify_overlap(
    materialization_root: Path,
    rows: list[dict[str, Any]],
    contract: dict[str, Any],
    fg1_private_case_ids: set[str],
) -> None:
    overlap_contract = contract.get("parent_overlap_audit", {})
    require(overlap_contract.get("required_zero_intersections") == OVERLAP_FIELDS, "overlap fields changed")
    require(overlap_contract.get("normalized_value_manifest_scopes") == OVERLAP_SCOPES, "overlap scopes changed")
    values_doc = load_json(materialization_root / "parent_overlap_value_manifest.json")
    require(
        values_doc.get("schema_version") == "effectslice-fg1-parent-overlap-values.v1",
        "unexpected overlap-value schema",
    )
    fields = values_doc.get("fields")
    require(isinstance(fields, dict), "overlap value fields missing")
    source_registry = overlap_contract.get("source_registry")
    require(isinstance(source_registry, dict), "overlap source registry missing")
    recomputed_counts: dict[str, int] = {}
    for field in OVERLAP_FIELDS:
        scope_rows = fields.get(field)
        require(isinstance(scope_rows, dict), f"overlap values missing field: {field}")
        require(list(scope_rows) == OVERLAP_SCOPES, f"overlap scope order changed: {field}")
        values_by_scope: dict[str, list[str]] = {}
        for scope in OVERLAP_SCOPES:
            item = scope_rows.get(scope)
            require(isinstance(item, dict), f"overlap scope missing: {field}/{scope}")
            values = item.get("values")
            require(isinstance(values, list), f"overlap values must be a list: {field}/{scope}")
            normalized = [str(value) for value in values]
            require(normalized == sorted(set(normalized)), f"overlap values not sorted unique: {field}/{scope}")
            sources = item.get("sources")
            require(isinstance(sources, list) and sources, f"overlap sources missing: {field}/{scope}")
            source_spec = source_registry[field][scope]
            require(isinstance(source_spec, dict), f"overlap source spec missing: {field}/{scope}")
            base_probe = {"path_base": source_spec["path_base"], "path": "."}
            base = _overlap_source_path(materialization_root, base_probe)
            source_root = (base / str(source_spec["root"])).resolve()
            try:
                source_root.relative_to(base)
            except ValueError as exc:
                raise MaterializationError(
                    f"overlap source root escapes base: {field}/{scope}"
                ) from exc
            discovered = sorted(
                (path for path in source_root.glob(str(source_spec["glob"])) if path.is_file()),
                key=lambda path: path.relative_to(base).as_posix(),
            )
            require(
                len(discovered) == source_spec["expected_file_count"],
                f"overlap registered source count mismatch: {field}/{scope}",
            )
            expected_relative_paths = [path.relative_to(base).as_posix() for path in discovered]
            require(len(sources) == len(discovered), f"overlap source list incomplete: {field}/{scope}")
            require(
                [str(source.get("path")) for source in sources] == expected_relative_paths,
                f"overlap source paths differ from registered glob: {field}/{scope}",
            )
            extracted: set[str] = set()
            extractor = source_spec["extractor"]
            for source, source_path in zip(sources, discovered, strict=True):
                require(isinstance(source, dict), f"invalid overlap source: {field}/{scope}")
                _strict_keys(source, {"path_base", "path", "sha256"}, f"overlap source {field}/{scope}")
                require(
                    source["path_base"] == source_spec["path_base"],
                    f"overlap path base mismatch: {field}/{scope}",
                )
                require(bool(HEX64.fullmatch(str(source.get("sha256")))), f"invalid overlap source digest: {field}/{scope}")
                require(source_path.is_file(), f"overlap source missing: {field}/{scope}/{source.get('path')}")
                require(_sha256(source_path) == source["sha256"], f"overlap source hash mismatch: {field}/{scope}/{source.get('path')}")
                extracted.update(_extract_overlap_values(source_path, extractor))
            require(normalized == sorted(extracted), f"overlap values not reproduced from sources: {field}/{scope}")
            require(normalized, f"overlap source values unexpectedly empty: {field}/{scope}")
            values_by_scope[scope] = normalized
        fg1_values = set(values_by_scope["effectslice_fg1"])
        parent_values = set(values_by_scope["confirmation_v4"]) | set(
            values_by_scope["confirmation_v5r2"]
        )
        recomputed_counts[field] = len(fg1_values & parent_values)
        if field != "private_case_id":
            expected_values = sorted({str(row[field]) for row in rows})
            require(
                values_by_scope["effectslice_fg1"] == expected_values,
                f"FG1 normalized values do not match schedule: {field}",
            )
        else:
            require(
                values_by_scope["effectslice_fg1"] == sorted(fg1_private_case_ids),
                "FG1 private case IDs do not match registry manifests",
            )

    overlap = load_json(materialization_root / "parent_overlap_audit.json")
    require(overlap.get("intersection_counts") == recomputed_counts, "overlap report is not recomputed")
    require(all(value == 0 for value in recomputed_counts.values()), "parent overlap is nonzero")


def _materialization_relative(path_value: str) -> str:
    prefix = "materialization/"
    return path_value[len(prefix) :] if path_value.startswith(prefix) else path_value


def _validate_replacement_amendments(
    amendments: dict[str, Any], amendment_schema: dict[str, Any]
) -> None:
    require(
        amendments.get("schema_version") == amendment_schema["schema_version"],
        "replacement amendment schema",
    )
    amendment_rows = amendments.get("amendments")
    require(isinstance(amendment_rows, list), "replacement amendments missing")
    require(
        amendment_schema.get("amendments_must_be_empty") is True
        and amendment_schema.get("nonempty_rows_forbidden") is True,
        "replacement empty-amendment contract missing",
    )
    require(
        amendment_rows == [],
        "nonempty replacement amendment requires a separately committed successor registration",
    )


def _validate_result_row_schema_contract(
    result_schema: dict[str, Any], registered_schema: dict[str, Any]
) -> None:
    require(
        result_schema == registered_schema,
        "result-row schema differs from the registered typed contract",
    )
    required_fields = registered_schema.get("required")
    require(isinstance(required_fields, list), "registered result-row required fields")
    require(result_schema.get("type") == "object", "result-row schema top-level type")
    require(
        result_schema.get("required") == required_fields,
        "result-row schema required fields do not equal the registered contract",
    )
    properties = result_schema.get("properties")
    require(isinstance(properties, dict), "result-row schema properties")
    require(
        set(properties) == set(required_fields),
        "result-row schema properties do not equal the registered contract",
    )
    require(
        result_schema.get("additionalProperties") is False,
        "result-row schema must forbid additional properties",
    )


def _validate_open_anchor_file_inventory(
    model_root: Path,
    runtime: dict[str, Any],
    runtime_schema: dict[str, Any],
) -> tuple[str, set[Path]]:
    inventory_contract = runtime_schema.get("file_inventory_contract")
    require(isinstance(inventory_contract, dict), "open-anchor file inventory contract")
    revision = runtime.get("revision")
    require(
        isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision) is not None,
        "open-anchor revision must be 40 lowercase hex characters",
    )
    require(
        model_root.name == revision and model_root.parent.name == "snapshots",
        "open-anchor model root must be the exact snapshot revision directory",
    )
    require(
        model_root.parent.parent.name
        == inventory_contract["model_root_repository_directory"],
        "open-anchor repository cache directory does not match exact alias",
    )

    weight_names = sorted(
        path.name
        for pattern in inventory_contract["weight_globs"]
        for path in model_root.glob(pattern)
        if path.is_file()
    )
    tokenizer_names = sorted(
        {
            path.name
            for pattern in inventory_contract["tokenizer_discovery_globs"]
            for path in model_root.glob(pattern)
            if path.is_file()
        }
    )
    config_names = sorted(
        {
            path.name
            for pattern in inventory_contract["config_discovery_globs"]
            for path in model_root.glob(pattern)
            if path.is_file()
        }
    )
    require(
        set(tokenizer_names) <= set(inventory_contract["tokenizer_names"]),
        "open-anchor unregistered tokenizer file discovered",
    )
    require(
        set(config_names) <= set(inventory_contract["config_names"]),
        "open-anchor unregistered config file discovered",
    )
    discovered = {
        "weight_files": sorted(set(weight_names)),
        "tokenizer_files": tokenizer_names,
        "config_files": config_names,
    }
    require(discovered["weight_files"], "open-anchor weight inventory is empty")
    require(
        set(inventory_contract["required_tokenizer_names"]) <= set(tokenizer_names),
        "open-anchor required tokenizer files missing",
    )
    require(
        set(inventory_contract["required_config_names"]) <= set(config_names),
        "open-anchor required config files missing",
    )

    referenced: set[Path] = set()
    canonical_inventory: dict[str, list[dict[str, object]]] = {}
    group_paths: set[str] = set()
    for group_name, discovered_names in discovered.items():
        file_rows = runtime.get(group_name)
        require(isinstance(file_rows, list) and file_rows, f"open-anchor {group_name}")
        paths: list[str] = []
        canonical_rows: list[dict[str, object]] = []
        for row in file_rows:
            require(isinstance(row, dict), f"open-anchor {group_name} row")
            _strict_keys(row, {"path", "sha256", "size_bytes"}, f"open-anchor {group_name}")
            relative = str(row["path"]).replace("\\", "/")
            require("/" not in relative, f"open-anchor inventory path must be top-level: {relative}")
            path = _require_hashed_file(model_root, relative, row["sha256"], f"open-anchor {group_name}")
            require(path.stat().st_size == row["size_bytes"], f"open-anchor size mismatch: {relative}")
            paths.append(relative)
            canonical_rows.append(
                {"path": relative, "sha256": row["sha256"], "size_bytes": row["size_bytes"]}
            )
            referenced.add(path)
        require(paths == sorted(set(paths)), f"open-anchor {group_name} paths")
        require(paths == discovered_names, f"open-anchor {group_name} does not equal discovered inventory")
        require(not (group_paths & set(paths)), f"open-anchor file appears in multiple groups: {group_name}")
        group_paths.update(paths)
        canonical_inventory[group_name] = canonical_rows

    index = load_json(model_root / "model.safetensors.index.json")
    weight_map = index.get("weight_map")
    require(isinstance(weight_map, dict) and weight_map, "open-anchor shard index weight_map")
    indexed_shards = sorted(set(str(value) for value in weight_map.values()))
    require(
        indexed_shards == discovered["weight_files"],
        "open-anchor shard index does not exactly cover weight inventory",
    )

    model_config = load_json(model_root / "config.json")
    required_config = runtime_schema["required_model_config"]
    require(model_config.get("model_type") == required_config["model_type"], "open-anchor model_type")
    architectures = model_config.get("architectures")
    require(
        isinstance(architectures, list)
        and required_config["architecture"] in architectures,
        "open-anchor architecture",
    )
    for field in (
        "hidden_size",
        "intermediate_size",
        "num_hidden_layers",
        "num_attention_heads",
        "num_key_value_heads",
        "vocab_size",
        "max_position_embeddings",
    ):
        require(
            model_config.get(field) == required_config[field],
            f"open-anchor exact model identity mismatch: {field}",
        )
    require(runtime.get("dtype") in runtime_schema["allowed_dtype"], "open-anchor dtype")
    require(
        runtime.get("quantization") in runtime_schema["allowed_quantization"],
        "open-anchor quantization",
    )
    if model_config.get("torch_dtype") is not None:
        require(model_config["torch_dtype"] == runtime["dtype"], "open-anchor config dtype mismatch")
    generation_defaults = load_json(model_root / "generation_config.json")
    generation = runtime_schema["generation_config"]
    require(generation_defaults.get("eos_token_id") == generation["eos_token_id"], "open-anchor EOS IDs")
    require(generation_defaults.get("pad_token_id") == generation["pad_token_id"], "open-anchor pad token ID")
    inventory_sha256 = hashlib.sha256(_canonical_json(canonical_inventory)).hexdigest()
    return inventory_sha256, referenced


def _validate_global_artifacts(
    materialization_root: Path,
    models: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, object]:
    global_paths = [_materialization_relative(str(path)) for path in contract["global_artifacts"]]
    for relative in global_paths:
        load_json(materialization_root / relative)

    schemas = contract["global_artifact_schemas"]
    registered_response_contracts = contract["result_canonicalization_contract"][
        "slot_response_contracts"
    ]
    require(isinstance(registered_response_contracts, list), "slot response contracts")
    response_contract_by_slot = {
        str(row["model_slot_id"]): row for row in registered_response_contracts
    }
    require(
        len(response_contract_by_slot) == len(registered_response_contracts),
        "duplicate slot response contract",
    )
    request_doc = load_json(materialization_root / "request_template_manifest.json")
    request_schema = schemas["request_template_manifest"]
    require(request_doc.get("schema_version") == request_schema["schema_version"], "request-template schema")
    templates = request_doc.get("templates")
    require(isinstance(templates, list), "request templates missing")
    referenced: set[str] = set()
    request_templates: dict[str, dict[str, Any]] = {}
    request_template_hashes: dict[str, str] = {}
    slots: list[str] = []
    primary = models["primary_model_reference"]
    expected_aliases = {str(primary["slot_id"]): str(primary["model_alias"])}
    for slot in models["model_slots"]:
        if slot.get("required") is True:
            expected_aliases[str(slot["slot_id"])] = str(slot["model_alias"])
    for row in templates:
        require(isinstance(row, dict) and set(request_schema["template_required_fields"]) <= set(row), "request-template fields")
        slots.append(str(row["model_slot_id"]))
        template_path = _require_hashed_file(
            materialization_root, row["path"], row["sha256"], "request template"
        )
        template = load_json(template_path)
        template_fields = set(
            contract["model_visible_payload_contract"]["wire_request_composition"][
                "template_required_fields"
            ]
        )
        require(template_fields <= set(template), f"request template document fields: {row['model_slot_id']}")
        slot_id = str(row["model_slot_id"])
        require(slot_id in expected_aliases, f"unexpected request template slot: {slot_id}")
        require(
            template["model_slot_id"] == slot_id
            and template["exact_alias"] == expected_aliases[slot_id],
            f"request template identity: {slot_id}",
        )
        require(
            isinstance(template["base_request"], dict)
            and template["base_request"].get("stream") is False,
            f"request template must disable streaming: {slot_id}",
        )
        request_templates[slot_id] = template
        request_template_hashes[slot_id] = str(row["sha256"])
        expected_limit_pointer = request_schema["output_limit_json_pointer_by_slot"][
            slot_id
        ]
        require(
            template["decoding_field_json_pointers"].get(
                "normalized_max_output_tokens"
            )
            == expected_limit_pointer,
            f"provider-native output-limit pointer: {slot_id}",
        )
        referenced.add(str(row["path"]))
    require(slots == request_schema["required_model_slots"], "request-template slot order")

    preflight = load_json(materialization_root / "model_preflight_manifest.json")
    preflight_schema = schemas["model_preflight_manifest"]
    require(preflight.get("schema_version") == preflight_schema["schema_version"], "model-preflight schema")
    preflight_rows = preflight.get("slots")
    require(isinstance(preflight_rows, list), "model preflight rows missing")
    require([row.get("model_slot_id") for row in preflight_rows] == list(expected_aliases), "model preflight slot order")
    for row in preflight_rows:
        require(isinstance(row, dict) and set(preflight_schema["slot_required_fields"]) <= set(row), "model preflight fields")
        slot_id = str(row["model_slot_id"])
        require(slot_id in expected_aliases, f"unexpected model preflight slot: {slot_id}")
        require(row["exact_alias"] == expected_aliases[slot_id], f"model preflight alias drift: {slot_id}")
        require(row["status"] in preflight_schema["allowed_status"], f"model preflight status: {slot_id}")
        require(isinstance(row["checked_at_utc"], str) and row["checked_at_utc"], f"model preflight timestamp: {slot_id}")
        require(
            row["request_template_sha256"] == request_template_hashes[slot_id],
            f"model preflight request-template binding: {slot_id}",
        )
        expected_response_hash = hashlib.sha256(
            _canonical_json(response_contract_by_slot[slot_id])
        ).hexdigest()
        require(
            row["response_contract_sha256"] == expected_response_hash,
            f"model preflight response-contract binding: {slot_id}",
        )
        require(
            isinstance(row["request_format_valid"], bool)
            and isinstance(row["response_format_valid"], bool),
            f"model preflight format flags: {slot_id}",
        )
        if row["status"] == "available":
            require(
                row["request_format_valid"] is True
                and row["response_format_valid"] is True,
                f"available model format preflight failed: {slot_id}",
            )
        _require_hashed_file(materialization_root, row["evidence_path"], row["evidence_sha256"], f"model preflight evidence {slot_id}")
        referenced.add(str(row["evidence_path"]))

    implementation_records: dict[str, dict[str, str]] = {}

    result_document = load_json(
        materialization_root / "result_canonicalization_manifest.json"
    )
    result_schema = schemas["result_canonicalization_manifest"]
    require(
        result_document.get("schema_version") == result_schema["schema_version"],
        "result_canonicalization_manifest schema",
    )
    require(
        set(result_schema["required_fields"]) <= set(result_document),
        "result_canonicalization_manifest fields",
    )
    require(
        result_document["golden_tests_passed"] is result_schema["golden_tests_passed"]
        and result_schema.get("verifier_executes_golden_suite") is True
        and result_document["golden_execution_protocol"]
        == result_schema["golden_execution_protocol"]
        and result_document["golden_timeout_seconds"]
        == result_schema["golden_timeout_seconds"],
        "result canonicalizer golden execution contract",
    )
    builder_identity = result_document["implementation_builder_identity"]
    require(
        isinstance(builder_identity, str) and builder_identity,
        "result canonicalizer builder identity",
    )
    require(
        result_document["slot_response_contracts"] == registered_response_contracts
        and result_schema["slot_response_contracts"] == registered_response_contracts,
        "slot response contracts changed during materialization",
    )
    response_contract_sha256 = hashlib.sha256(
        _canonical_json(registered_response_contracts)
    ).hexdigest()
    require(
        result_document["slot_response_contracts_sha256"]
        == response_contract_sha256,
        "slot response contract digest",
    )
    parser_path = _require_hashed_file(
        materialization_root,
        result_document["parser_implementation_path"],
        result_document["parser_implementation_sha256"],
        "result canonicalizer parser implementation",
    )
    result_row_schema_path = _require_hashed_file(
        materialization_root,
        result_document["result_row_schema_path"],
        result_document["result_row_schema_sha256"],
        "result canonicalizer row schema",
    )
    referenced.update(
        {
            str(result_document["parser_implementation_path"]),
            str(result_document["result_row_schema_path"]),
        }
    )
    registered_result_schema = contract["result_canonicalization_contract"][
        "result_row_json_schema"
    ]
    _validate_result_row_schema_contract(
        load_json(result_row_schema_path), registered_result_schema
    )
    golden_cases = result_document["golden_cases"]
    expected_cases = result_schema["golden_case_contracts"]
    require(
        isinstance(golden_cases, list) and len(golden_cases) == len(expected_cases),
        "result canonicalizer golden case count",
    )
    projection_fields = [
        "case_id",
        "model_slot_id",
        "dispatch_state",
        "terminal_outcome",
        "termination_reason",
        "provider_finish_reason",
    ]
    required_case_fields = set(result_schema["golden_case_required_fields"])
    for index, (case, expected) in enumerate(zip(golden_cases, expected_cases)):
        require(
            isinstance(case, dict) and required_case_fields <= set(case),
            f"result golden case fields: {index}",
        )
        require(
            {field: case[field] for field in projection_fields} == expected,
            f"result golden case registration drift: {index}",
        )
        fixture_path = _require_hashed_file(
            materialization_root,
            case["fixture_path"],
            case["fixture_sha256"],
            f"result golden fixture: {case['case_id']}",
        )
        golden_result_path = _require_hashed_file(
            materialization_root,
            case["result_path"],
            case["result_sha256"],
            f"result golden result: {case['case_id']}",
        )
        referenced.update({str(case["fixture_path"]), str(case["result_path"])})
        actual = _execute_golden_json_transform(
            parser_path,
            fixture_path,
            golden_result_path,
            registered_result_schema,
            int(result_document["golden_timeout_seconds"]),
            f"result_canonicalization_manifest/{case['case_id']}",
        )
        _validate_result_row_semantics(
            actual,
            f"golden/{case['case_id']}",
            str(case["model_slot_id"]),
            schemas["open_anchor_runtime_manifest"]["generation_config"],
        )
        for field in (
            "terminal_outcome",
            "termination_reason",
            "provider_finish_reason",
        ):
            require(
                actual[field] == expected[field],
                f"golden result projection mismatch: {case['case_id']}/{field}",
            )
    implementation_records["result_canonicalizer"] = {
        "implementation_path": str(result_document["parser_implementation_path"]),
        "implementation_sha256": str(result_document["parser_implementation_sha256"]),
        "builder_identity": builder_identity,
    }

    analysis_document = load_json(
        materialization_root / "analysis_implementation_manifest.json"
    )
    analysis_schema = schemas["analysis_implementation_manifest"]
    require(
        analysis_document.get("schema_version") == analysis_schema["schema_version"],
        "analysis_implementation_manifest schema",
    )
    require(
        set(analysis_schema["required_fields"]) <= set(analysis_document),
        "analysis_implementation_manifest fields",
    )
    require(
        analysis_document["golden_tests_passed"] is analysis_schema["golden_tests_passed"]
        and analysis_schema.get("verifier_executes_golden_suite") is True
        and analysis_document["golden_execution_protocol"]
        == analysis_schema["golden_execution_protocol"]
        and analysis_document["golden_timeout_seconds"]
        == analysis_schema["golden_timeout_seconds"],
        "analysis golden execution contract",
    )
    analysis_builder = analysis_document["implementation_builder_identity"]
    require(
        isinstance(analysis_builder, str) and analysis_builder,
        "analysis implementation builder identity",
    )
    analysis_paths: dict[str, Path] = {}
    for path_field, hash_field in (
        ("implementation_path", "implementation_sha256"),
        ("golden_fixture_path", "golden_fixture_sha256"),
        ("golden_result_path", "golden_result_sha256"),
        ("analysis_result_schema_path", "analysis_result_schema_sha256"),
    ):
        analysis_paths[path_field] = _require_hashed_file(
            materialization_root,
            analysis_document[path_field],
            analysis_document[hash_field],
            f"analysis implementation {path_field}",
        )
        referenced.add(str(analysis_document[path_field]))
    _execute_golden_json_transform(
        analysis_paths["implementation_path"],
        analysis_paths["golden_fixture_path"],
        analysis_paths["golden_result_path"],
        analysis_paths["analysis_result_schema_path"],
        int(analysis_document["golden_timeout_seconds"]),
        "analysis_implementation_manifest",
    )
    implementation_records["analysis_implementation"] = {
        "implementation_path": str(analysis_document["implementation_path"]),
        "implementation_sha256": str(analysis_document["implementation_sha256"]),
        "builder_identity": analysis_builder,
    }

    amendments = load_json(materialization_root / "replacement_amendment_manifest.json")
    amendment_schema = schemas["replacement_amendment_manifest"]
    require(
        contract["replacement_policy_contract"].get("current_registration_is_immutable")
        is True
        and contract["replacement_policy_contract"].get("amendments_must_be_empty")
        is True,
        "replacement immutability contract",
    )
    _validate_replacement_amendments(amendments, amendment_schema)

    runtime = load_json(materialization_root / "open_anchor_runtime_manifest.json")
    runtime_schema = schemas["open_anchor_runtime_manifest"]
    require(runtime.get("schema_version") == runtime_schema["schema_version"], "open-anchor runtime schema")
    require(set(runtime_schema["required_fields"]) <= set(runtime), "open-anchor runtime fields")
    require(
        runtime["model_slot_id"] == runtime_schema["model_slot_id"]
        and runtime["exact_alias"] == runtime_schema["exact_alias"]
        and isinstance(runtime["revision"], str)
        and runtime["revision"],
        "open-anchor runtime identity",
    )
    model_root_value = Path(str(runtime["model_root"]))
    require(model_root_value.is_absolute(), "open-anchor model root must be absolute")
    model_root = model_root_value.resolve()
    require(model_root.is_dir(), "open-anchor model root")
    inventory_sha256, _ = _validate_open_anchor_file_inventory(model_root, runtime, runtime_schema)
    require(runtime["generation_config"] == runtime_schema["generation_config"], "open-anchor generation config")
    require(
        isinstance(runtime["software"], dict)
        and set(runtime["software"]) == set(runtime_schema["software_required_fields"])
        and all(isinstance(value, str) and value for value in runtime["software"].values()),
        "open-anchor software",
    )
    require(
        isinstance(runtime["hardware"], dict)
        and set(runtime["hardware"]) == set(runtime_schema["hardware_required_fields"])
        and runtime["hardware"].get("cuda_available") is True
        and isinstance(runtime["hardware"].get("gpu_count"), int)
        and runtime["hardware"]["gpu_count"] >= 1,
        "open-anchor hardware",
    )
    determinism = runtime["determinism"]
    require(isinstance(determinism, dict), "open-anchor determinism")
    for key, value in runtime_schema["determinism_required"].items():
        require(determinism.get(key) == value, f"open-anchor determinism drift: {key}")
    evidence_path = _require_hashed_file(
        materialization_root,
        runtime["environment_evidence_path"],
        runtime["environment_evidence_sha256"],
        "open-anchor environment evidence",
    )
    referenced.add(str(runtime["environment_evidence_path"]))
    evidence = load_json(evidence_path)
    _strict_keys(
        evidence,
        set(runtime_schema["environment_evidence_required_fields"]),
        "open-anchor environment evidence",
    )
    evidence_expected = {
        "schema_version": "effectslice-fg1-open-anchor-environment.v1",
        "model_slot_id": runtime["model_slot_id"],
        "exact_alias": runtime["exact_alias"],
        "revision": runtime["revision"],
        "model_root": str(model_root),
        "model_file_inventory_sha256": inventory_sha256,
        "dtype": runtime["dtype"],
        "quantization": runtime["quantization"],
        "generation_config": runtime["generation_config"],
        "software": runtime["software"],
        "hardware": runtime["hardware"],
        "determinism": runtime["determinism"],
        "preflight_result_sha256": runtime["preflight_result_sha256"],
    }
    require(evidence == evidence_expected, "open-anchor environment evidence content mismatch")

    preflight_paths: dict[str, Path] = {}
    for path_field, hash_field in (
        ("preflight_implementation_path", "preflight_implementation_sha256"),
        ("preflight_fixture_path", "preflight_fixture_sha256"),
        ("preflight_result_path", "preflight_result_sha256"),
    ):
        preflight_paths[path_field] = _require_hashed_file(
            materialization_root,
            runtime[path_field],
            runtime[hash_field],
            f"open-anchor {path_field}",
        )
        referenced.add(str(runtime[path_field]))
    require(
        runtime["preflight_execution_protocol"]
        == runtime_schema["preflight_execution_protocol"]
        and runtime["preflight_timeout_seconds"]
        == runtime_schema["preflight_timeout_seconds"],
        "open-anchor preflight execution contract",
    )
    preflight_result = _execute_golden_json_transform(
        preflight_paths["preflight_implementation_path"],
        preflight_paths["preflight_fixture_path"],
        preflight_paths["preflight_result_path"],
        runtime_schema["preflight_result_schema"],
        int(runtime["preflight_timeout_seconds"]),
        "open-anchor preflight",
    )
    require(
        set(runtime_schema["preflight_required_result_fields"]) <= set(preflight_result),
        "open-anchor preflight result fields",
    )
    require(
        preflight_result["model_slot_id"] == runtime["model_slot_id"]
        and preflight_result["exact_alias"] == runtime["exact_alias"]
        and preflight_result["revision"] == runtime["revision"]
        and preflight_result["model_file_inventory_sha256"] == inventory_sha256
        and preflight_result["generation_config_sha256"]
        == hashlib.sha256(_canonical_json(runtime["generation_config"])).hexdigest()
        and isinstance(preflight_result["prompt_token_count"], int)
        and preflight_result["prompt_token_count"] >= 1
        and preflight_result["model_loaded"] is True
        and preflight_result["tokenizer_loaded"] is True
        and preflight_result["offline_mode"] is True
        and preflight_result["repeat_generated_token_ids_equal"] is True
        and preflight_result["repeat_canonical_output_equal"] is True
        and isinstance(preflight_result["generated_token_ids"], list)
        and preflight_result["generated_token_ids"],
        "open-anchor offline preflight semantics",
    )
    _validate_open_anchor_generated_token_ids(
        preflight_result["generated_token_ids"],
        runtime["generation_config"],
        "open-anchor offline preflight",
    )
    open_anchor_builder = runtime["implementation_builder_identity"]
    require(
        isinstance(open_anchor_builder, str) and open_anchor_builder,
        "open-anchor preflight builder identity",
    )
    implementation_records["open_anchor_preflight"] = {
        "implementation_path": str(runtime["preflight_implementation_path"]),
        "implementation_sha256": str(runtime["preflight_implementation_sha256"]),
        "builder_identity": open_anchor_builder,
    }

    source_audit_schema = schemas["implementation_source_audit_manifest"]
    referenced.update(
        _validate_implementation_source_audit(
            materialization_root, source_audit_schema, implementation_records
        )
    )
    return {"referenced": referenced, "request_templates": request_templates}


def audit_materialization(materialization_root: Path) -> dict[str, object]:
    try:
        _, registry, models, contract = preregistrations()
        task_to_paper, _ = task_maps(registry)
        global_context = _validate_global_artifacts(materialization_root, models, contract)
        global_referenced = global_context["referenced"]
        request_templates = global_context["request_templates"]
        require(isinstance(global_referenced, set), "global referenced paths invalid")
        require(isinstance(request_templates, dict), "request templates invalid")
        task_results: dict[str, dict[str, object]] = {}
        all_private_case_ids: set[str] = set()
        all_referenced: set[str] = set(global_referenced)
        for task_id in task_to_paper:
            task_root = materialization_root / "tasks" / task_id
            result = validate_task_artifacts(
                task_root,
                task_id,
                task_id in SECONDARY_TASKS,
                request_templates,
            )
            task_results[task_id] = result
            all_private_case_ids.update(result["private_case_ids"])
            all_referenced.update(
                f"tasks/{task_id}/{path}" for path in result["referenced_paths"]
            )

        remote = load_json(materialization_root / "global_remote_schedule.json").get("rows")
        local = load_json(materialization_root / "global_local_anchor_schedule.json").get("rows")
        require(isinstance(remote, list) and len(remote) == 1200, "remote schedule count")
        require(isinstance(local, list) and len(local) == 96, "local schedule count")
        require(
            all(row.get("execution_family") != "open_anchor" for row in remote),
            "open-anchor row in remote schedule",
        )
        require(
            all(row.get("execution_family") == "open_anchor" for row in local),
            "non-anchor row in local schedule",
        )
        rows = [*remote, *local]
        result = validate_schedule_rows(rows, registry, models, contract)

        schedule_by_execution = {row["execution_id"]: row for row in rows}
        payload_by_execution: dict[str, dict[str, Any]] = {}
        schedule_binding_fields = {
            "execution_id",
            "execution_family",
            "variant_id",
            "model_slot_id",
            "registry_id",
            "block_id",
            "condition",
            "candidate_id",
            *REQUIRED_HASH_FIELDS,
        }
        for task_id, task_result in task_results.items():
            task_payloads = task_result["payload_rows"]
            require(isinstance(task_payloads, dict), f"payload mapping invalid: {task_id}")
            for execution_id, payload_row in task_payloads.items():
                require(execution_id not in payload_by_execution, f"duplicate cross-task payload execution: {execution_id}")
                require(execution_id in schedule_by_execution, f"payload execution absent from schedule: {execution_id}")
                schedule_row = schedule_by_execution[execution_id]
                require(schedule_row["task_id"] == task_id, f"payload task mismatch: {execution_id}")
                for field in schedule_binding_fields:
                    require(payload_row.get(field) == schedule_row.get(field), f"payload/schedule mismatch {field}: {execution_id}")
                payload_by_execution[execution_id] = payload_row
        require(set(payload_by_execution) == set(schedule_by_execution), "payload manifests do not exactly cover schedule")

        immutable = load_json(materialization_root / "immutable_file_manifest.json")
        entries = immutable.get("files")
        require(isinstance(entries, list), "immutable file list missing")
        relative_paths = [entry.get("path") for entry in entries if isinstance(entry, dict)]
        require(len(relative_paths) == len(entries), "invalid immutable file row")
        require(len(relative_paths) == len(set(relative_paths)), "duplicate immutable file path")
        require(relative_paths == sorted(relative_paths), "immutable file paths not canonical sorted")
        bound_hashes: set[str] = set()
        bound_paths: set[str] = set()
        for entry in entries:
            path = _safe_bound_path(materialization_root, entry["path"])
            require(path.is_file(), f"bound materialized file missing: {entry['path']}")
            actual = _sha256(path)
            require(actual == entry.get("sha256"), f"materialized hash mismatch: {entry['path']}")
            require(path.stat().st_size == entry.get("bytes"), f"materialized size mismatch: {entry['path']}")
            bound_hashes.add(actual)
            bound_paths.add(str(entry["path"]).replace("\\", "/"))
        for row in rows:
            for field in REQUIRED_HASH_FIELDS:
                require(row[field] in bound_hashes, f"unbound row digest {field}: {row['execution_id']}")

        exclusions = set(contract["hash_contract"]["control_file_exclusions"])
        required_global_bound = {
            _materialization_relative(str(path))
            for path in contract["global_artifacts"]
            if _materialization_relative(str(path)) not in exclusions
        }
        required_task_bound = {
            f"tasks/{task_id}/{name}"
            for task_id in task_to_paper
            for name in contract["required_task_artifacts"]
        }
        required_bound_paths = required_global_bound | required_task_bound | {
            path.replace("\\", "/") for path in all_referenced
        }
        require(required_bound_paths <= bound_paths, f"required materialized files are unbound: {sorted(required_bound_paths - bound_paths)}")

        anchor = load_json(materialization_root / "final_anchor_manifest.json")
        anchor_schema = contract["global_artifact_schemas"]["final_anchor_manifest"]
        require(set(anchor_schema["required_fields"]) <= set(anchor), "final anchor fields")
        require(anchor.get("schema_version") == anchor_schema["schema_version"], "final anchor schema")
        require(anchor.get("provider_calls_started") is False, "provider calls started before anchor")
        immutable_sha = _sha256(materialization_root / "immutable_file_manifest.json")
        require(anchor.get("immutable_file_manifest_sha256") == immutable_sha, "final anchor immutable-manifest hash")
        bundle_rows = [{"path": entry["path"], "sha256": entry["sha256"]} for entry in entries]
        bundle_sha = hashlib.sha256(_canonical_json(bundle_rows)).hexdigest()
        require(anchor.get("bundle_sha256") == bundle_sha, "final anchor bundle hash")
        require(isinstance(anchor.get("verified_at_utc"), str) and anchor["verified_at_utc"], "final anchor timestamp")

        _verify_overlap(materialization_root, rows, contract, all_private_case_ids)
        allowlist = load_json(materialization_root / "analysis_source_allowlist.json")
        allowlisted = allowlist.get("execution_ids")
        require(
            isinstance(allowlisted, list)
            and allowlisted == [row["execution_id"] for row in rows],
            "analysis execution allowlist mismatch or reordering",
        )
        require(len(allowlisted) == len(set(allowlisted)), "duplicate analysis allowlist ID")
        require(
            allowlist.get("exclude_parent_runs")
            == ["confirmation_v4", "confirmation_v5r2"],
            "parent analysis exclusion changed",
        )
        return {"status": "passed", **result}
    except MaterializationError:
        raise
    except (KeyError, IndexError, TypeError, ValueError, OSError) as exc:
        raise MaterializationError(f"malformed materialization artifact: {exc}") from exc
