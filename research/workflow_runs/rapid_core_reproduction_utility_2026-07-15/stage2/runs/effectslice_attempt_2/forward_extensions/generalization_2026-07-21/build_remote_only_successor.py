from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PARENT = ROOT / "preregistration"
OUTPUT = ROOT / "preregistration_remote_only_2026-07-22"
PARENT_BUNDLE_SHA256 = "277bab0fba66a4144346d472ef3deadc010168353d47f939dc812501a2eff9b4"
CREATED_AT = "2026-07-22T00:00:00Z"


def load(name: str) -> dict[str, Any]:
    return json.loads((PARENT / name).read_text(encoding="utf-8"))


def write(name: str, value: object) -> None:
    path = OUTPUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_terms(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): replace_terms(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_terms(item) for item in value]
    if isinstance(value, str):
        replacements = (
            ("open_seed_anchor", "gpt_5_6_luna"),
            ("open_anchor", "remote_anchor"),
            ("Open-anchor", "Remote-anchor"),
            ("open-anchor", "remote-anchor"),
            ("open anchor", "remote anchor"),
            ("Qwen/Qwen2.5-Coder-7B-Instruct", "gpt-5.6-luna"),
            ("local deterministic generation", "remote repeat dispatch"),
            ("local seeded generation", "remote repeat dispatch"),
            ("local execution", "remote execution"),
            ("local anchor", "remote anchor"),
        )
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    return value


def build_model_registry() -> dict[str, Any]:
    models = load("model_ablation_registry.json")
    models["schema_version"] = "effectslice-fg1-model-registry.remote-only.v1"
    slots = []
    for row in models["model_slots"]:
        if row["slot_id"] == "open_seed_anchor":
            continue
        row = copy.deepcopy(row)
        if row["slot_id"] == "gpt_5_6_luna":
            row["required"] = True
            row["role"] = "required_remote_repeatability_anchor"
            row["interpretation"] = "Exact F/I repeated remote requests quantify observed repeatability; no deterministic-model or seed guarantee is claimed."
        slots.append(row)
    models["model_slots"] = slots
    design = models["design"]
    design["remote_repeatability_anchor_conversations"] = design.pop(
        "local_executions_for_open_anchor"
    )
    models["registration_status"] = "stage_2_2_1_remote_only_successor_registered_materialization_pending"
    models["successor_policy"] = {
        "parent_bundle_sha256": PARENT_BUNDLE_SHA256,
        "reason": "User scope forbids local-model experiment design; the local open-weight slot is removed before materialization and before any provider call.",
        "replacement": {"removed_slot_id": "open_seed_anchor", "required_remote_slot_id": "gpt_5_6_luna"},
        "no_parent_file_modified": True,
    }
    return replace_terms(models)


def _luna_response_contract(contract: dict[str, Any]) -> dict[str, Any]:
    source = next(row for row in contract["result_canonicalization_contract"]["slot_response_contracts"] if row["model_slot_id"] == "gpt_5_6_terra")
    row = copy.deepcopy(source)
    row["model_slot_id"] = "gpt_5_6_luna"
    row["exact_alias"] = "gpt-5.6-luna"
    return row


def build_contract() -> dict[str, Any]:
    contract = load("materialization_contract.json")
    contract["schema_version"] = "effectslice-fg1-materialization-contract.remote-only.v1"
    contract["registration_status"] = "stage_2_2_1_remote_only_successor_registered_materialization_pending"
    contract["stage"] = "2.3-remote-only"
    contract["verifier"] = "verify_stage_2_3_remote_materialization.py"
    contract["successor_registration"] = {
        "parent_bundle_sha256": PARENT_BUNDLE_SHA256,
        "created_at_utc": CREATED_AT,
        "scope_change": "No local-model experiment may be designed or executed.",
        "remote_replacement": "gpt_5_6_luna",
        "provider_calls_started": False,
    }

    candidate_schedule = contract["candidate_manifest"]["schedule_candidate_ids"]
    candidate_schedule["remote_anchor"] = candidate_schedule.pop("open_anchor")

    payload = contract["model_visible_payload_contract"]
    wire = payload["wire_request_composition"]
    wire["normalized_output_limit"]["provider_native_pointer_required_for_every_slot"] = True

    global_artifacts = contract["global_artifacts"]
    global_artifacts.remove("materialization/global_local_anchor_schedule.json")
    global_artifacts.remove("materialization/open_anchor_runtime_manifest.json")
    schemas = contract["global_artifact_schemas"]
    schemas.pop("open_anchor_runtime_manifest")
    request_schema = schemas["request_template_manifest"]
    request_schema["required_model_slots"] = ["gpt_5_6_luna" if value == "open_seed_anchor" else value for value in request_schema["required_model_slots"]]
    request_schema["output_limit_json_pointer_by_slot"].pop("open_seed_anchor")
    request_schema["output_limit_json_pointer_by_slot"]["gpt_5_6_luna"] = "/max_output_tokens"

    luna_contract = _luna_response_contract(contract)
    response_contracts = [row for row in contract["result_canonicalization_contract"]["slot_response_contracts"] if row["model_slot_id"] != "open_seed_anchor"]
    response_contracts.append(luna_contract)
    contract["result_canonicalization_contract"]["slot_response_contracts"] = response_contracts
    result_manifest_schema = schemas["result_canonicalization_manifest"]
    result_manifest_schema["slot_response_contracts"] = copy.deepcopy(response_contracts)
    golden = []
    for row in result_manifest_schema["golden_case_contracts"]:
        if row["model_slot_id"] != "open_seed_anchor":
            golden.append(row)
            continue
        if row["termination_reason"] == "eos":
            golden.append({"case_id": "gpt_5_6_luna_completed", "model_slot_id": "gpt_5_6_luna", "dispatch_state": "completed_body", "terminal_outcome": "operational_success", "termination_reason": "provider_stop", "provider_finish_reason": "completed"})
        else:
            golden.append({"case_id": "gpt_5_6_luna_length_scored", "model_slot_id": "gpt_5_6_luna", "dispatch_state": "completed_body", "terminal_outcome": "operational_success", "termination_reason": "length", "provider_finish_reason": "max_output_tokens"})
    result_manifest_schema["golden_case_contracts"] = golden

    result_contract = contract["result_canonicalization_contract"]
    result_contract.pop("generated_token_ids", None)
    result_contract["raw_response_bytes"] = (
        "Streaming is disabled. Persist exactly the complete response-body bytes "
        "delivered by the HTTP client after transfer/content decoding and before "
        "UTF-8 or JSON parsing; do not reserialize. raw_response_sha256 hashes "
        "those bytes."
    )
    result_contract["empty_and_failure_behavior"] = (
        "An extracted empty string is a valid canonical byte string but ordinarily "
        "maps to malformed_or_no_submission with private_score=0.0. JSON/parser "
        "failure never produces an empty substitute. Invalid rows use null for "
        "canonical output, hard-contract vector, and private_score."
    )
    cross_fields = result_contract["result_row_cross_field_contract"]
    cross_fields.pop("generated_token_ids", None)
    cross_fields["invalid_outcome_null_fields"] = [
        value
        for value in cross_fields["invalid_outcome_null_fields"]
        if value != "generated_token_ids"
    ]
    result_contract["required_result_row_fields"] = [
        value
        for value in result_contract["required_result_row_fields"]
        if value != "generated_token_ids"
    ]
    result_schema = result_contract["result_row_json_schema"]
    result_schema["required"] = [
        value for value in result_schema["required"] if value != "generated_token_ids"
    ]
    result_schema["properties"].pop("generated_token_ids", None)
    result_contract["parser_golden_case_contracts"] = copy.deepcopy(golden)

    audit_schema = schemas["implementation_source_audit_manifest"]
    audit_schema["required_component_ids"] = [value for value in audit_schema["required_component_ids"] if value != "open_anchor_preflight"]
    audit_schema["required_checks_by_component"].pop("open_anchor_preflight")

    contract["schedule_counts"] = {"required_remote_rows": 1296, "required_local_rows": 0, "required_total_rows": 1296, "optional_remote_template_rows": 96}
    products = contract["schedule_family_products"]
    remote = products.pop("open_anchor")
    remote["model_slot_ids"] = ["gpt_5_6_luna"]
    products["remote_anchor"] = remote
    order = contract["schedule_row_schema"]["global_sequence_order"]
    order["family_order"] = ["remote_anchor" if value == "open_anchor" else value for value in order["family_order"]]
    order["remote_anchor_model_order"] = ["gpt_5_6_luna"]
    contract["schedule_row_schema"]["derived_seed_semantics"]["remote_rows"] = "Deterministic orchestration/request seed recorded for every remote row; no closed-model determinism claim."
    contract["schedule_row_schema"]["derived_seed_semantics"].pop("open_anchor_rows", None)

    for field in contract["parent_overlap_audit"]["source_registry"].values():
        if field["effectslice_fg1"]["glob"] == "global_*_schedule.json":
            field["effectslice_fg1"]["expected_file_count"] = 1
    contract["final_anchor_gate"] = [replace_terms(value) for value in contract["final_anchor_gate"]]
    return replace_terms(contract)


def build_experiment_plan() -> dict[str, Any]:
    plan = replace_terms(load("experiment_plan.json"))
    assert isinstance(plan, dict)
    plan["schema_version"] = "effectslice-fg1-experiment-plan.remote-only.v1"
    plan["registration_status"] = "stage_2_2_1_remote_only_successor_registered_materialization_pending"
    plan["forward_only_successor"] = {
        "parent_bundle_sha256": PARENT_BUNDLE_SHA256,
        "change": "Remove all local-model design and use gpt-5.6-luna for the fifth required remote sentinel slot.",
        "inference": "F/I is an observed repeatability comparison only; it is not a seed or determinism guarantee.",
        "provider_calls_started": False,
    }
    budget = plan["resource_budget"]
    budget["remote_repeatability_anchor_conversations"] = 96
    budget.pop("open_anchor_local_execution_cap", None)
    budget["required_remote_conversation_cap"] = 1296
    budget["required_execution_cap"] = 1296
    budget["required_nominal_remote_hours"] = 45.8
    budget["required_realistic_remote_hours"] = [55, 76]
    budget["ideal_two_worker_remote_wall_clock_lower_bound_hours"] = [27.5, 38.0]
    budget["excluded_from_remote_hour_estimate"] = [
        value
        for value in budget["excluded_from_remote_hour_estimate"]
        if "local anchor" not in value and "local execution" not in value
    ]
    secondary = plan["secondary_experiments"]
    anchor = secondary.pop("open_deterministic_anchor")
    anchor["remote_conversations"] = anchor.pop("local_executions")
    anchor["model"] = "gpt-5.6-luna"
    anchor["purpose"] = (
        "Repeated identical F/I remote requests quantify observed repeatability; "
        "no seed or deterministic closed-model guarantee is claimed."
    )
    anchor.pop("deterministic_F_I_gate", None)
    secondary["remote_repeatability_anchor"] = anchor
    return plan


def build_figure_plan() -> dict[str, Any]:
    plan = replace_terms(load("figure_statistical_plan.json"))
    assert isinstance(plan, dict)
    plan["schema_version"] = "effectslice-fg1-figure-statistical-plan.remote-only.v1"
    plan["registration_status"] = "stage_2_2_1_remote_only_successor_registered_materialization_pending"
    for figure in plan["figures"]:
        for panel in figure["panels"]:
            if "generated token" in panel["content"].lower():
                panel["content"] = "Required remote model x four sentinel-task exact B/F/S states and F/I observed output, score, contract-vector, and resource agreement; unavailable exact aliases stay visible."
    return plan


def build_candidate_matrix() -> dict[str, Any]:
    matrix = replace_terms(load("candidate_matrix.json"))
    assert isinstance(matrix, dict)
    matrix["schema_version"] = "effectslice-fg1-candidate-matrix.remote-only.v1"
    matrix["registration_status"] = "stage_2_2_1_remote_only_successor_registered_materialization_pending"
    return matrix


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    expected_names = {
        "bundle_hash_manifest.json",
        "candidate_matrix.json",
        "experiment_plan.json",
        "figure_statistical_plan.json",
        "materialization_contract.json",
        "metadata_evidence_manifest.json",
        "model_ablation_registry.json",
        "paper_registry.json",
        "sla_operating_characteristics.json",
        "successor_registration.json",
    }
    unexpected_names = {
        path.name for path in OUTPUT.iterdir() if path.name not in expected_names
    }
    if unexpected_names:
        raise RuntimeError(
            f"unexpected files in successor output: {sorted(unexpected_names)}"
        )
    write("paper_registry.json", load("paper_registry.json"))
    write("metadata_evidence_manifest.json", load("metadata_evidence_manifest.json"))
    write("sla_operating_characteristics.json", load("sla_operating_characteristics.json"))
    write("candidate_matrix.json", build_candidate_matrix())
    write("experiment_plan.json", build_experiment_plan())
    write("model_ablation_registry.json", build_model_registry())
    write("materialization_contract.json", build_contract())
    write("figure_statistical_plan.json", build_figure_plan())
    write("successor_registration.json", {
        "schema_version": "effectslice-fg1-remote-only-successor.v1",
        "parent_bundle_sha256": PARENT_BUNDLE_SHA256,
        "created_at_utc": CREATED_AT,
        "reason": "User explicitly prohibited local-model experiment design before Stage 2.3 was anchored or any provider call occurred.",
        "removed": ["open_seed_anchor", "Qwen/Qwen2.5-Coder-7B-Instruct", "global_local_anchor_schedule.json", "open_anchor_runtime_manifest.json"],
        "added_required_remote_slot": {"slot_id": "gpt_5_6_luna", "exact_alias": "gpt-5.6-luna", "rows": 96},
        "required_remote_rows": 1296,
        "required_local_rows": 0,
        "provider_calls_started": False,
        "forward_only": True,
    })
    bundle_paths = [
        path
        for path in OUTPUT.glob("*.json")
        if path.name != "bundle_hash_manifest.json"
    ]
    bundle_paths.extend(
        ROOT / relative
        for relative in (
            "build_remote_only_successor.py",
            "materialization_verifier_v3.py",
            "tests/test_remote_materialization_semantics.py",
            "tests/test_remote_only_successor.py",
            "verify_remote_only_successor.py",
            "verify_stage_2_3_remote_materialization.py",
        )
    )
    files = []
    for path in sorted(bundle_paths, key=lambda value: value.relative_to(ROOT).as_posix()):
        files.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    bundle_sha = hashlib.sha256(canonical([{"path": row["path"], "sha256": row["sha256"]} for row in files])).hexdigest()
    write("bundle_hash_manifest.json", {"schema_version": "effectslice-fg1-remote-only-bundle-hashes.v1", "parent_bundle_sha256": PARENT_BUNDLE_SHA256, "files": files, "bundle_sha256": bundle_sha})
    forbidden = ("Qwen/Qwen2.5-Coder-7B-Instruct", "open_seed_anchor", "open_anchor_runtime_manifest", "open_deterministic_anchor", "generated_token_ids", "local_executions", "global_local_anchor_schedule")
    for path in OUTPUT.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        if path.name == "successor_registration.json":
            continue
        leaked = [value for value in forbidden if value in text]
        if leaked:
            raise RuntimeError(f"local-model design leaked into {path.name}: {leaked}")
    print(json.dumps({"status": "remote_only_successor_built", "bundle_sha256": bundle_sha, "files": len(files)}, sort_keys=True))


if __name__ == "__main__":
    main()
