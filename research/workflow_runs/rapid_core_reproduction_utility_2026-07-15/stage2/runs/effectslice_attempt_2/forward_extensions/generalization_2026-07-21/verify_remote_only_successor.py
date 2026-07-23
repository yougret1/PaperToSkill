from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PARENT = ROOT / "preregistration"
SUCCESSOR = ROOT / "preregistration_remote_only_2026-07-22"
EXPECTED_PARENT_BUNDLE_SHA256 = (
    "277bab0fba66a4144346d472ef3deadc010168353d47f939dc812501a2eff9b4"
)
EXPECTED_BUNDLE_FILES = {
    "build_remote_only_successor.py",
    "materialization_verifier_v3.py",
    "preregistration_remote_only_2026-07-22/candidate_matrix.json",
    "preregistration_remote_only_2026-07-22/experiment_plan.json",
    "preregistration_remote_only_2026-07-22/figure_statistical_plan.json",
    "preregistration_remote_only_2026-07-22/materialization_contract.json",
    "preregistration_remote_only_2026-07-22/metadata_evidence_manifest.json",
    "preregistration_remote_only_2026-07-22/model_ablation_registry.json",
    "preregistration_remote_only_2026-07-22/paper_registry.json",
    "preregistration_remote_only_2026-07-22/sla_operating_characteristics.json",
    "preregistration_remote_only_2026-07-22/successor_registration.json",
    "tests/test_remote_materialization_semantics.py",
    "tests/test_remote_only_successor.py",
    "verify_remote_only_successor.py",
    "verify_stage_2_3_remote_materialization.py",
}
REQUIRED_MODEL_SLOTS = {
    "gpt_5_5",
    "gpt_5_6_sol",
    "gpt_5_6_terra",
    "claude_opus_4_7",
    "gpt_5_6_luna",
}
OPTIONAL_MODEL_SLOTS = {"claude_opus_4_6"}
MATERIALIZED_MODEL_SLOTS = {
    "deepseek_primary",
    *REQUIRED_MODEL_SLOTS,
}
FORBIDDEN_REMOTE_ONLY_TERMS = (
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "open_seed_anchor",
    "open_anchor_runtime_manifest",
    "open_deterministic_anchor",
    "generated_token_ids",
    "local_executions",
    "global_local_anchor_schedule",
)


class SuccessorVerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorVerificationError(message)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def bundle_path(relative: str) -> Path:
    successor_prefix = "preregistration_remote_only_2026-07-22/"
    if relative.startswith(successor_prefix):
        return SUCCESSOR / relative.removeprefix(successor_prefix)
    return ROOT / relative


def verify_bundle() -> str:
    parent_manifest = load(PARENT / "bundle_hash_manifest.json")
    require(
        parent_manifest["bundle_sha256"] == EXPECTED_PARENT_BUNDLE_SHA256,
        "frozen parent bundle hash changed",
    )

    manifest = load(SUCCESSOR / "bundle_hash_manifest.json")
    require(
        manifest["parent_bundle_sha256"] == EXPECTED_PARENT_BUNDLE_SHA256,
        "successor parent hash mismatch",
    )
    rows = manifest["files"]
    require(isinstance(rows, list), "bundle files must be a list")
    paths = [row["path"] for row in rows]
    require(paths == sorted(paths), "bundle files must be sorted")
    require(set(paths) == EXPECTED_BUNDLE_FILES, "bundle file set mismatch")
    for row in rows:
        path = bundle_path(row["path"])
        require(path.is_file(), f"missing bundle file: {row['path']}")
        require(row["sha256"] == sha256(path), f"sha256 mismatch: {row['path']}")
        require(row["bytes"] == path.stat().st_size, f"byte mismatch: {row['path']}")
    calculated = hashlib.sha256(
        canonical([{"path": row["path"], "sha256": row["sha256"]} for row in rows])
    ).hexdigest()
    require(calculated == manifest["bundle_sha256"], "bundle hash mismatch")
    return calculated


def verify_no_local_design() -> None:
    for path in sorted(SUCCESSOR.glob("*.json")):
        if path.name == "successor_registration.json":
            continue
        text = path.read_text(encoding="utf-8")
        leaked = [term for term in FORBIDDEN_REMOTE_ONLY_TERMS if term in text]
        require(not leaked, f"local-model design leaked into {path.name}: {leaked}")


def verify_registration() -> None:
    registration = load(SUCCESSOR / "successor_registration.json")
    require(
        registration["parent_bundle_sha256"] == EXPECTED_PARENT_BUNDLE_SHA256,
        "registration parent hash mismatch",
    )
    require(registration["forward_only"] is True, "successor must be forward-only")
    require(
        registration["provider_calls_started"] is False,
        "provider calls must not precede the successor anchor",
    )
    require(registration["required_remote_rows"] == 1296, "remote row count mismatch")
    require(registration["required_local_rows"] == 0, "local rows must be zero")
    require(
        registration["added_required_remote_slot"]
        == {"slot_id": "gpt_5_6_luna", "exact_alias": "gpt-5.6-luna", "rows": 96},
        "Luna replacement registration mismatch",
    )


def verify_models() -> None:
    models = load(SUCCESSOR / "model_ablation_registry.json")
    require(
        models["schema_version"] == "effectslice-fg1-model-registry.remote-only.v1",
        "model registry schema mismatch",
    )
    slots = models["model_slots"]
    required = {row["slot_id"] for row in slots if row["required"]}
    optional = {row["slot_id"] for row in slots if not row["required"]}
    require(required == REQUIRED_MODEL_SLOTS, "required model slots mismatch")
    require(optional == OPTIONAL_MODEL_SLOTS, "optional model slots mismatch")
    require(
        all(row["remote_conversations"] == 96 for row in slots),
        "each model slot must retain 96 remote conversations",
    )
    luna = next(row for row in slots if row["slot_id"] == "gpt_5_6_luna")
    require(luna["model_alias"] == "gpt-5.6-luna", "Luna exact alias mismatch")
    require(
        luna["role"] == "required_remote_repeatability_anchor",
        "Luna role mismatch",
    )
    design = models["design"]
    require(
        design["remote_repeatability_anchor_conversations"] == 96,
        "model design repeatability count mismatch",
    )


def verify_plan() -> None:
    plan = load(SUCCESSOR / "experiment_plan.json")
    require(
        plan["schema_version"] == "effectslice-fg1-experiment-plan.remote-only.v1",
        "experiment-plan schema mismatch",
    )
    successor = plan["forward_only_successor"]
    require(successor["provider_calls_started"] is False, "plan call-state mismatch")
    budget = plan["resource_budget"]
    require(budget["required_remote_conversation_cap"] == 1296, "remote cap mismatch")
    require(budget["required_execution_cap"] == 1296, "execution cap mismatch")
    require(
        budget["remote_repeatability_anchor_conversations"] == 96,
        "repeatability budget mismatch",
    )
    secondary = plan["secondary_experiments"]
    require(
        "remote_repeatability_anchor" in secondary,
        "remote repeatability experiment missing",
    )
    anchor = secondary["remote_repeatability_anchor"]
    require(anchor["model"] == "gpt-5.6-luna", "repeatability model mismatch")
    require(anchor["remote_conversations"] == 96, "repeatability row count mismatch")
    require(
        "deterministic_F_I_gate" not in anchor,
        "closed-model deterministic gate must be absent",
    )


def verify_contract() -> None:
    contract = load(SUCCESSOR / "materialization_contract.json")
    require(
        contract["schema_version"]
        == "effectslice-fg1-materialization-contract.remote-only.v1",
        "materialization-contract schema mismatch",
    )
    successor = contract["successor_registration"]
    require(successor["provider_calls_started"] is False, "contract call-state mismatch")
    counts = contract["schedule_counts"]
    require(
        counts
        == {
            "required_remote_rows": 1296,
            "required_local_rows": 0,
            "required_total_rows": 1296,
            "optional_remote_template_rows": 96,
        },
        "schedule counts mismatch",
    )
    products = contract["schedule_family_products"]
    require("remote_anchor" in products, "remote-anchor schedule family missing")
    require(products["remote_anchor"]["model_slot_ids"] == ["gpt_5_6_luna"], "remote-anchor slot mismatch")
    require(products["remote_anchor"]["rows"] == 96, "remote-anchor rows mismatch")
    require(
        contract["global_artifacts"].count("materialization/global_remote_schedule.json")
        == 1,
        "exactly one remote schedule must be registered",
    )
    request_schema = contract["global_artifact_schemas"]["request_template_manifest"]
    require(
        set(request_schema["required_model_slots"]) == MATERIALIZED_MODEL_SLOTS,
        "request-template model slots mismatch",
    )
    response_contracts = contract["result_canonicalization_contract"][
        "slot_response_contracts"
    ]
    require(
        {row["model_slot_id"] for row in response_contracts}
        == MATERIALIZED_MODEL_SLOTS,
        "response-contract model slots mismatch",
    )
    result_contract = contract["result_canonicalization_contract"]
    require(
        "generated_token_ids" not in result_contract["required_result_row_fields"],
        "remote result rows must not contain generated token IDs",
    )
    require(
        "generated_token_ids" not in result_contract["result_row_json_schema"]["properties"],
        "remote result schema must not define generated token IDs",
    )
    overlap = contract["parent_overlap_audit"]["source_registry"]
    require(
        overlap["execution_id"]["effectslice_fg1"]["expected_file_count"] == 1,
        "remote schedule overlap count mismatch",
    )
    require(
        overlap["private_case_id"]["effectslice_fg1"]["expected_file_count"] == 48,
        "private-registry overlap count changed",
    )


def verify_unchanged_evidence() -> None:
    for name in (
        "metadata_evidence_manifest.json",
        "paper_registry.json",
        "sla_operating_characteristics.json",
    ):
        require(load(SUCCESSOR / name) == load(PARENT / name), f"{name} changed")


def verify() -> dict[str, object]:
    bundle_sha256 = verify_bundle()
    verify_no_local_design()
    verify_registration()
    verify_models()
    verify_plan()
    verify_contract()
    verify_unchanged_evidence()
    return {
        "status": "remote_only_successor_verified",
        "bundle_sha256": bundle_sha256,
        "required_remote_rows": 1296,
        "required_local_rows": 0,
        "required_model_slots": sorted(REQUIRED_MODEL_SLOTS),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
