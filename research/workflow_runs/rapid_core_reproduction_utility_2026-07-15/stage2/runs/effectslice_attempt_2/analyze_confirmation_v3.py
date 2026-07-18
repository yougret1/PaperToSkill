from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any

from scipy.stats import beta

from effectslice.confirmation_v3 import balanced_schedule, joint_substitution_event


RUN_ROOT = Path(__file__).resolve().parent
PROGRESS_SCHEMA = "effectslice-confirmation-v3-progress.v1"
PAIR_SCHEMA = "effectslice-confirmation-v3-pair.v1"
REGISTERED_V3 = "registered_final_only_confirmation_v3"
CONDITIONS = ("B", "F", "S")
NO_ARTIFACT_CONTEXT = (
    "No paper-derived method artifact is supplied for this condition. "
    "Use only the common bounded ACI contract, the locked task, and tool feedback."
)
RUN_RESULT_FIELDS = {
    "status",
    "terminal_reason",
    "submitted",
    "task_score",
    "success",
    "diff_text",
    "state",
    "turns",
    "scorer_metrics",
    "input_tokens",
    "output_tokens",
    "transport_attempts",
    "elapsed_seconds",
    "common_scaffold_sha256",
    "condition_context_sha256",
    "task_prompt_sha256",
    "private_score_policy",
    "private_score_count",
    "private_feedback_exposed",
    "public_error",
}
SUMMARY_FIELDS = {
    "status",
    "terminal_reason",
    "submitted",
    "task_score",
    "success",
    "actions_used",
    "input_tokens",
    "output_tokens",
    "transport_attempts",
    "candidate_patch_sha256",
    "private_score_policy",
    "private_score_count",
    "private_feedback_exposed",
    "run_result_path",
    "transcript_path",
    "candidate_patch_path",
}
TURN_FIELDS = {
    "step",
    "retry_lineage_id",
    "prompt_sha256",
    "response_sha256",
    "response_text",
    "action",
    "observation_status",
    "observation_message",
    "transport_attempts",
    "input_tokens",
    "output_tokens",
    "provider_model_id",
    "provider_response_id",
    "provider_created",
}
METRIC_FIELDS = {
    "schema_version",
    "task_id",
    "metric_name",
    "block",
    "evidence_boundary",
    "task_score",
    "success",
    "patch_applied",
    "contract_passed",
    "contract_failures",
    "case_scores",
    "case_details",
    "failure_reason",
    "private_apply_result",
    "public_summary",
}
FAMILY_FIELDS = {
    "schema_version",
    "registration_status",
    "control",
    "task_key",
    "task_id",
    "conditions",
    "strict_subset",
    "calibration_role",
    "retained_atom_ids",
    "retained_unit_count",
    "retained_scc_count",
    "case_block",
    "case_count",
    "case_role",
    "case_generator_config_id",
    "statistical_unit",
    "decision_basis",
    "primary_event",
    "independence_verified",
    "iid_conditional_reference",
    "replicate_count",
    "replicate_schedule",
    "schedule_seed",
    "run_success_threshold",
    "maximum_shortfall",
    "admission_rule",
    "required_joint_events_for_admission",
    "private_score_policy",
    "maximum_transport_attempts",
    "provider_label",
    "model_alias",
    "wire_api",
    "temperature",
    "max_tokens",
    "fresh_provider_conversation_per_condition",
    "comparison_role",
    "evidence_boundary",
    "bindings",
    "task_prompt_path",
    "task_prompt_status",
    "task_prompt_file_sha256",
    "task_prompt_canonical_text_sha256",
    "workspace_path",
    "workspace_tree_sha256",
    "workspace_file_count",
    "workspace_total_bytes",
    "workspace_excluded_directory_names",
}
PAIR_FIELDS = {
    "schema_version",
    "completion_status",
    "pair_id",
    "task_id",
    "control",
    "comparison_role",
    "evidence_boundary",
    "decision_basis",
    "primary_event",
    "independence_verified",
    "private_score_policy",
    "family_path",
    "family_sha256",
    "replicate_id",
    "condition_execution_order",
    "task_prompt_path",
    "task_prompt_file_sha256",
    "task_prompt_canonical_text_sha256",
    "full_artifact_path",
    "full_artifact_sha256",
    "selected_artifact_path",
    "selected_artifact_sha256",
    "source_map_sha256",
    "case_registry_sha256",
    "scorer_sha256",
    "runner_sha256",
    "scheduler_sha256",
    "analyzer_sha256",
    "aci_runner_sha256",
    "transport_sha256",
    "case_generator_sha256",
    "reference_registry_sha256",
    "provider_config",
    "workspace_state",
    "conditions",
    "retry_lineage",
    "workspace_snapshot_path",
    "verified_inputs_path",
    "results",
}
V2_PAIR_FIELDS = {
    "action_budget_visible_to_model",
    "atom_map_sha256",
    "authorization_evidence",
    "case_block",
    "case_registry_sha256",
    "common_scaffold_sha256",
    "comparison_role",
    "condition_execution_order",
    "conditions",
    "confirmation_case_count",
    "confirmation_family_path",
    "confirmation_family_sha256",
    "confirmation_hypothesis_ids",
    "evidence_boundary",
    "full_artifact_sha256",
    "harness_protocol_version",
    "maximum_transport_attempts",
    "model_alias",
    "model_family",
    "pair_id",
    "private_score_policy",
    "provider_config",
    "provider_protocol_version",
    "results",
    "retained_atom_ids",
    "retained_scc_count",
    "same_aci_scaffold",
    "schema_version",
    "scorer_sha256",
    "seed_block_id",
    "slice_artifact_path",
    "slice_artifact_sha256",
    "slice_candidate_id",
    "slice_registry_path",
    "slice_registry_sha256",
    "task_id",
    "task_prompt_sha256",
    "verified_family_inputs",
    "wire_api",
    "workspace_state",
}
CONTROL_SPECS = {
    "identity": {
        "schedule_seed": 2026071801,
        "replicate_count": 6,
        "strict_subset": False,
        "calibration_role": "identity_instrumentation_only",
        "admission_rule": "descriptive_only",
        "required_joint_events_for_admission": None,
    },
    "planted": {
        "schedule_seed": 2026071802,
        "replicate_count": 18,
        "strict_subset": True,
        "calibration_role": "planted_redundancy_positive_control",
        "admission_rule": "all_registered_joint_events",
        "required_joint_events_for_admission": 18,
    },
}
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class AnalysisInputError(ValueError):
    """Raised when registered evidence cannot be audited without ambiguity."""


def _is_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except (FileNotFoundError, NotADirectoryError):
        return False
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(getattr(metadata, "st_file_attributes", 0) & flag)


def _reject_unsafe_components(path: Path, label: str) -> None:
    supplied = Path(path)
    if ".." in supplied.parts:
        raise AnalysisInputError(f"{label} must not traverse parents")
    absolute = Path(os.path.abspath(os.fspath(supplied)))
    for component in (*reversed(absolute.parents), absolute):
        if component.is_symlink() or _is_reparse_point(component):
            raise AnalysisInputError(f"{label} must not use symlink or reparse paths")


def _json_object(path: Path, label: str) -> dict[str, Any]:
    supplied = Path(path)
    _reject_unsafe_components(supplied, label)
    resolved = supplied.resolve()
    if not resolved.is_file():
        raise AnalysisInputError(f"{label} is missing")
    try:
        snapshot = resolved.read_bytes()
        value = json.loads(snapshot.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisInputError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AnalysisInputError(f"{label} must be a JSON object")
    return value


def _registered_stored_path(raw: Any, expected: Path, label: str) -> None:
    if not isinstance(raw, str):
        raise AnalysisInputError(f"{label} is not registered")
    supplied = Path(raw)
    _reject_unsafe_components(supplied, label)
    if supplied.resolve() != Path(expected).resolve():
        raise AnalysisInputError(f"{label} is not registered")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise AnalysisInputError(f"{label} does not match the registered value")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise AnalysisInputError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _validate_family(path: Path, expected_sha256: str) -> dict[str, Any]:
    family = _json_object(path, "registered family")
    if _sha256_file(path.resolve()) != expected_sha256:
        raise AnalysisInputError("registered family digest mismatch")
    if set(family) != FAMILY_FIELDS:
        raise AnalysisInputError(
            "registered family fields do not match the family schema"
        )
    exact = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": "complete",
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v3",
        "case_count": 64,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "iid_conditional_reference": {"label": "iid_conditional_only"},
        "run_success_threshold": 0.95,
        "maximum_shortfall": 0.05,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "fresh_provider_conversation_per_condition": True,
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
    }
    for field, expected in exact.items():
        _require_exact(family.get(field), expected, f"family {field}")
    control = family.get("control")
    if control not in CONTROL_SPECS:
        raise AnalysisInputError("family control must be identity or planted")
    spec = CONTROL_SPECS[control]
    for field in (
        "schedule_seed",
        "replicate_count",
        "strict_subset",
        "calibration_role",
        "admission_rule",
        "required_joint_events_for_admission",
    ):
        _require_exact(family.get(field), spec[field], f"family {field}")
    expected_schedule = balanced_schedule(
        spec["schedule_seed"], spec["replicate_count"]
    )
    _require_exact(
        family.get("replicate_schedule"), expected_schedule, "family replicate_schedule"
    )
    return family


def _binding_digest(family: dict[str, Any], name: str) -> str:
    bindings = family.get("bindings")
    if not isinstance(bindings, dict) or not isinstance(bindings.get(name), dict):
        raise AnalysisInputError(f"family binding is missing: {name}")
    record = bindings[name]
    _require_exact(record.get("status"), "bound", f"{name} binding status")
    return _require_sha256(record.get("sha256"), f"{name} binding digest")


def _require_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise AnalysisInputError(f"{label} must be a bool")
    return value


def _require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise AnalysisInputError(f"{label} must be an integer >= {minimum}")
    return value


def _require_finite_number(value: Any, label: str, *, minimum: float = 0) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise AnalysisInputError(f"{label} must be finite and >= {minimum}")
    return float(value)


def _audit_result_scalars(result: dict[str, Any]) -> None:
    _require_bool(result.get("submitted"), "condition submitted")
    _require_bool(result.get("private_feedback_exposed"), "private feedback")
    for field in ("input_tokens", "output_tokens"):
        _require_int(result.get(field), f"condition {field}")
    _require_int(
        result.get("transport_attempts"), "condition transport_attempts", minimum=1
    )
    _require_int(result.get("private_score_count"), "private score count")
    _require_finite_number(result.get("elapsed_seconds"), "condition elapsed_seconds")
    for field in (
        "common_scaffold_sha256",
        "condition_context_sha256",
        "task_prompt_sha256",
    ):
        _require_sha256(result.get(field), f"condition {field}")
    if not isinstance(result.get("public_error"), str):
        raise AnalysisInputError("condition public_error must be a string")


def _audit_metric(
    metric: Any,
    *,
    expected_block: str = "confirmation_v3",
    expected_case_ids: list[str] | None = None,
) -> tuple[bool, float, bool]:
    if not isinstance(metric, dict):
        raise AnalysisInputError("private score must be an object")
    if set(metric) != METRIC_FIELDS:
        raise AnalysisInputError("private score fields do not match the scorer schema")
    for field, expected in {
        "schema_version": "effectslice-toolformer-filter-score.v1",
        "task_id": "TOOLFORMER-FILTER",
        "metric_name": "registered_case_pass_rate",
        "block": expected_block,
    }.items():
        _require_exact(metric.get(field), expected, f"private score {field}")
    if (
        not isinstance(metric.get("evidence_boundary"), str)
        or not metric["evidence_boundary"]
    ):
        raise AnalysisInputError("private score evidence boundary is invalid")
    score = metric.get("task_score")
    if (
        type(score) not in (int, float)
        or not math.isfinite(score)
        or not 0 <= score <= 1
    ):
        raise AnalysisInputError("private task_score must be finite and within [0, 1]")
    success = metric.get("success")
    contract = metric.get("contract_passed")
    _require_bool(success, "private score success")
    _require_bool(contract, "private score contract_passed")
    patch_applied = _require_bool(
        metric.get("patch_applied"), "private score patch_applied"
    )
    failures = metric.get("contract_failures")
    if not isinstance(failures, list) or any(
        not isinstance(item, str) for item in failures
    ):
        raise AnalysisInputError("private score contract failures are invalid")
    case_scores = metric.get("case_scores")
    if (
        not isinstance(case_scores, list)
        or len(case_scores) != 64
        or any(type(item) is not int or item not in (0, 1) for item in case_scores)
    ):
        raise AnalysisInputError("private score must contain exactly 64 binary cases")
    if not math.isclose(float(score), sum(case_scores) / 64, rel_tol=0, abs_tol=1e-15):
        raise AnalysisInputError("private task_score does not match its 64 cases")
    case_details = metric.get("case_details")
    if not isinstance(case_details, list) or len(case_details) not in {0, 64}:
        raise AnalysisInputError("private score case details are invalid")
    if not case_details and metric.get("patch_applied") is True and contract is True:
        raise AnalysisInputError("evaluated private score lacks its 64 case details")
    if not patch_applied and (
        success
        or float(score) != 0.0
        or contract
        or any(case_scores)
        or case_details
    ):
        raise AnalysisInputError(
            "unapplied private score must be a zero-valued failure without case details"
        )
    case_ids: set[str] = set()
    for detail, case_score in zip(case_details, case_scores):
        if not isinstance(detail, dict):
            raise AnalysisInputError("private case detail must be an object")
        case_id = detail.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise AnalysisInputError("private case IDs must be nonempty and unique")
        case_ids.add(case_id)
        passed = detail.get("passed")
        if type(passed) is not bool or passed is not bool(case_score):
            raise AnalysisInputError(
                "private case detail does not match its binary score"
            )
        if detail.get("error_type") is not None and not isinstance(
            detail.get("error_type"), str
        ):
            raise AnalysisInputError("private case error type is invalid")
        full_fields = {
            "case_id",
            "passed",
            "keep_match",
            "margin_match",
            "max_abs_margin_error",
            "error_type",
        }
        error_fields = {"case_id", "passed", "error_type"}
        if set(detail) == full_fields:
            keep_match = _require_bool(detail.get("keep_match"), "private keep_match")
            margin_match = _require_bool(
                detail.get("margin_match"), "private margin_match"
            )
            _require_finite_number(
                detail.get("max_abs_margin_error"), "private margin error"
            )
            if passed is not bool(keep_match and margin_match):
                raise AnalysisInputError(
                    "private case comparisons do not match passed"
                )
        elif set(detail) == error_fields:
            if passed is not False or not isinstance(detail.get("error_type"), str):
                raise AnalysisInputError("private case error detail is invalid")
        else:
            raise AnalysisInputError("private case detail fields are invalid")
    if case_details and expected_case_ids is not None:
        if [detail["case_id"] for detail in case_details] != expected_case_ids:
            raise AnalysisInputError("private case IDs/order do not match registration")
    if success and (expected_case_ids is None or len(case_details) != 64):
        raise AnalysisInputError(
            "successful private score lacks registered case details"
        )
    failure_reason = metric.get("failure_reason")
    if not isinstance(failure_reason, str):
        raise AnalysisInputError("private failure reason must be a string")
    if (success and failure_reason) or (not success and not failure_reason):
        raise AnalysisInputError("private failure reason does not match success")
    expected_summary = {
        "status": "passed" if success else "failed",
        "task_score": float(score),
        "passed_cases": sum(case_scores),
        "total_cases": 64,
        "contract_passed": contract,
        "failure_reason": failure_reason,
    }
    _require_exact(
        metric.get("public_summary"), expected_summary, "private public summary"
    )
    apply_result = metric.get("private_apply_result")
    if not isinstance(apply_result, dict):
        raise AnalysisInputError("private apply result is invalid")
    if apply_result:
        if set(apply_result) != {"returncode", "stdout", "stderr"}:
            raise AnalysisInputError("private apply result fields are invalid")
        _require_int(apply_result.get("returncode"), "private apply returncode")
        if not isinstance(apply_result.get("stdout"), str) or not isinstance(
            apply_result.get("stderr"), str
        ):
            raise AnalysisInputError("private apply output is invalid")
    if not patch_applied:
        if failure_reason != "patch_apply_failed" or failures:
            raise AnalysisInputError("unapplied private score failure shape is invalid")
        if apply_result and apply_result["returncode"] == 0:
            raise AnalysisInputError("unapplied private score has a successful apply")
    if success is not bool(patch_applied and score >= 0.95 and contract):
        raise AnalysisInputError(
            "private success does not match patch, score, and hard contract"
        )
    return success, float(score), contract


def _audit_final_score_terminal(
    result: dict[str, Any],
    turns: list[dict[str, Any]],
    scored_indices: list[int],
    label: str,
) -> None:
    terminal_reason = result.get("terminal_reason")
    if terminal_reason == "submitted":
        _require_exact(result.get("submitted"), True, f"{label} submitted")
        if scored_indices != [len(turns) - 1]:
            raise AnalysisInputError(
                f"{label} must have one terminal scored model turn"
            )
        final_action = turns[-1].get("action")
        if not isinstance(final_action, dict) or final_action.get("action") != "submit":
            raise AnalysisInputError(f"{label} lacks a terminal submit action")
        return
    if terminal_reason == "action_budget_exhausted_after_final_score":
        _require_exact(result.get("submitted"), False, f"{label} submitted")
        if scored_indices:
            raise AnalysisInputError(
                f"{label} has a model turn after or at its final score"
            )
        return
    raise AnalysisInputError(f"{label} terminal reason is not final-only")


def _snapshot_bytes(path: Path, expected_sha256: str, label: str) -> bytes:
    _reject_unsafe_components(path, label)
    if not path.is_file():
        raise AnalysisInputError(f"{label} is missing")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise AnalysisInputError(f"{label} cannot be read") from exc
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise AnalysisInputError(f"{label} digest mismatch")
    return payload


def _workspace_snapshot_state(path: Path) -> dict[str, Any]:
    root = Path(path)
    _reject_unsafe_components(root, "workspace snapshot")
    if not root.is_dir():
        raise AnalysisInputError("workspace snapshot is missing")
    excluded = {".git", "__pycache__", ".pytest_cache"}
    digest = hashlib.sha256()
    file_count = 0
    total_bytes = 0
    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_root)
        for directory_name in tuple(directory_names):
            directory = current / directory_name
            if directory_name in excluded:
                directory_names.remove(directory_name)
            elif directory.is_symlink() or _is_reparse_point(directory):
                raise AnalysisInputError("workspace snapshot contains a linked directory")
        directory_names.sort()
        for file_name in sorted(file_names):
            source = current / file_name
            if source.is_symlink() or _is_reparse_point(source):
                raise AnalysisInputError("workspace snapshot contains a linked file")
            relative = source.relative_to(root).as_posix()
            try:
                payload = source.read_bytes()
            except OSError as exc:
                raise AnalysisInputError("workspace snapshot file cannot be read") from exc
            relative_bytes = relative.encode("utf-8")
            digest.update(len(relative_bytes).to_bytes(8, "big"))
            digest.update(relative_bytes)
            digest.update(payload)
            digest.update(len(payload).to_bytes(8, "big"))
            file_count += 1
            total_bytes += len(payload)
    return {
        "sha256": digest.hexdigest(),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "excluded_directory_names": sorted(excluded),
    }


def _audit_registered_snapshots(
    output_dir: Path, manifest: dict[str, Any], family: dict[str, Any]
) -> tuple[dict[str, str], list[str]]:
    input_dir = output_dir / "verified_inputs"
    workspace_dir = output_dir / "workspace_snapshot"
    _registered_stored_path(
        manifest.get("verified_inputs_path"), input_dir, "verified inputs path"
    )
    _registered_stored_path(
        manifest.get("workspace_snapshot_path"),
        workspace_dir,
        "workspace snapshot path",
    )
    expected_files = {
        "task_prompt.md",
        "full_artifact.md",
        "selected_artifact.md",
        "source_atom_map.json",
        "case_registry.json",
    }
    _reject_unsafe_components(input_dir, "verified inputs")
    if not input_dir.is_dir():
        raise AnalysisInputError("verified inputs directory is missing")
    observed_files = set()
    for path in input_dir.rglob("*"):
        if path.is_symlink() or _is_reparse_point(path):
            raise AnalysisInputError("verified inputs contain a linked path")
        if path.is_file():
            observed_files.add(path.relative_to(input_dir).as_posix())
    if observed_files != expected_files:
        raise AnalysisInputError("verified input snapshot fields are incomplete")
    task_prompt = _snapshot_bytes(
        input_dir / "task_prompt.md",
        family["task_prompt_file_sha256"],
        "task prompt snapshot",
    )
    full_artifact = _snapshot_bytes(
        input_dir / "full_artifact.md",
        _binding_digest(family, "full_artifact"),
        "full artifact snapshot",
    )
    selected_artifact = _snapshot_bytes(
        input_dir / "selected_artifact.md",
        _binding_digest(family, "selected_artifact"),
        "selected artifact snapshot",
    )
    _snapshot_bytes(
        input_dir / "source_atom_map.json",
        _binding_digest(family, "source_map"),
        "source map snapshot",
    )
    registry_bytes = _snapshot_bytes(
        input_dir / "case_registry.json",
        _binding_digest(family, "case_registry"),
        "case registry snapshot",
    )
    try:
        task_text = task_prompt.decode("utf-8").strip()
        full_text = full_artifact.decode("utf-8").strip()
        selected_text = selected_artifact.decode("utf-8").strip()
        registry = json.loads(registry_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisInputError("registered input snapshots are not valid UTF-8") from exc
    if not task_text or hashlib.sha256(task_text.encode("utf-8")).hexdigest() != family[
        "task_prompt_canonical_text_sha256"
    ]:
        raise AnalysisInputError("canonical task prompt snapshot digest mismatch")
    blocks = registry.get("blocks") if isinstance(registry, dict) else None
    cases = blocks.get("confirmation_v3") if isinstance(blocks, dict) else None
    if not isinstance(cases, list) or len(cases) != 64:
        raise AnalysisInputError("case registry snapshot must contain 64 registered cases")
    case_ids = []
    for case in cases:
        case_id = case.get("case_id") if isinstance(case, dict) else None
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise AnalysisInputError("case registry IDs must be nonempty and unique")
        case_ids.append(case_id)
    expected_workspace = {
        "sha256": family["workspace_tree_sha256"],
        "file_count": family["workspace_file_count"],
        "total_bytes": family["workspace_total_bytes"],
        "excluded_directory_names": family["workspace_excluded_directory_names"],
    }
    _require_exact(
        _workspace_snapshot_state(workspace_dir),
        expected_workspace,
        "workspace snapshot state",
    )
    contexts = {"B": NO_ARTIFACT_CONTEXT, "F": full_text, "S": selected_text}
    if any(not value for value in contexts.values()):
        raise AnalysisInputError("registered condition context is empty")
    return (
        {
            condition: hashlib.sha256(value.encode("utf-8")).hexdigest()
            for condition, value in contexts.items()
        },
        case_ids,
    )


def _audit_condition(
    *,
    output_dir: Path,
    condition: str,
    pair_id: str,
    family: dict[str, Any],
    manifest: dict[str, Any],
    response_ids: set[str],
    expected_context_sha256: str,
    expected_case_ids: list[str],
) -> dict[str, Any]:
    summary = manifest["results"].get(condition)
    if not isinstance(summary, dict):
        raise AnalysisInputError("condition result summary is missing")
    if set(summary) != SUMMARY_FIELDS:
        raise AnalysisInputError(
            "condition summary fields do not match the runner schema"
        )
    expected_paths = {
        "run_result_path": output_dir / condition / "run_result.json",
        "transcript_path": output_dir / condition / "transcript.json",
        "candidate_patch_path": output_dir / condition / "candidate.patch",
    }
    for field, expected in expected_paths.items():
        _registered_stored_path(
            summary.get(field), expected, f"condition {field}"
        )
    result = _json_object(expected_paths["run_result_path"], "condition run result")
    if set(result) != RUN_RESULT_FIELDS:
        raise AnalysisInputError(
            "condition run result fields do not match the runner schema"
        )
    _audit_result_scalars(result)
    transcript = _json_object(expected_paths["transcript_path"], "condition transcript")
    if set(transcript) != {"schema_version", "evidence_boundary", "turns"}:
        raise AnalysisInputError(
            "condition transcript fields do not match the runner schema"
        )
    _reject_unsafe_components(expected_paths["candidate_patch_path"], "condition patch")
    try:
        patch = expected_paths["candidate_patch_path"].read_bytes()
    except OSError as exc:
        raise AnalysisInputError("condition candidate patch is missing") from exc
    if hashlib.sha256(patch).hexdigest() != summary.get("candidate_patch_sha256"):
        raise AnalysisInputError("condition candidate patch digest mismatch")
    if patch.decode("utf-8") != result.get("diff_text"):
        raise AnalysisInputError("condition candidate patch does not match run result")
    for field in (
        "status",
        "terminal_reason",
        "submitted",
        "task_score",
        "success",
        "input_tokens",
        "output_tokens",
        "transport_attempts",
        "private_score_policy",
        "private_score_count",
        "private_feedback_exposed",
    ):
        _require_exact(
            result.get(field), summary.get(field), f"condition summary {field}"
        )
    _require_exact(result.get("status"), "scored", "condition status")
    _require_exact(result.get("private_score_policy"), "final_only", "score policy")
    _require_exact(result.get("private_score_count"), 1, "private score count")
    _require_exact(result.get("private_feedback_exposed"), False, "private feedback")
    _require_int(summary.get("actions_used"), "condition actions_used", minimum=1)
    _require_sha256(summary.get("candidate_patch_sha256"), "candidate patch digest")
    metrics = result.get("scorer_metrics")
    if not isinstance(metrics, list) or len(metrics) != 1:
        raise AnalysisInputError("condition must contain exactly one private score")
    success, score, hard_constraints = _audit_metric(
        metrics[0], expected_case_ids=expected_case_ids
    )
    _require_exact(result.get("success"), success, "condition success")
    _require_exact(result.get("task_score"), score, "condition task_score")
    context = manifest["conditions"].get(condition)
    if not isinstance(context, dict):
        raise AnalysisInputError("condition manifest is missing")
    _require_exact(
        context.get("context_sha256"),
        expected_context_sha256,
        "registered condition context digest",
    )
    _require_exact(
        result.get("condition_context_sha256"),
        context.get("context_sha256"),
        "condition context digest",
    )
    _require_exact(
        result.get("task_prompt_sha256"),
        family.get("task_prompt_canonical_text_sha256"),
        "condition task prompt digest",
    )
    turns = result.get("turns")
    _require_exact(transcript.get("turns"), turns, "transcript turns")
    _require_exact(
        transcript.get("schema_version"),
        "effectslice-confirmation-v3-transcript.v1",
        "transcript schema",
    )
    _require_exact(
        transcript.get("evidence_boundary"), REGISTERED_V3, "transcript boundary"
    )
    if not isinstance(turns, list) or not turns:
        raise AnalysisInputError("condition must contain model turns")
    scored_turn_indices = []
    for index, turn in enumerate(turns):
        if not isinstance(turn, dict):
            raise AnalysisInputError("model turn must be an object")
        if set(turn) != TURN_FIELDS:
            raise AnalysisInputError("model turn fields do not match the runner schema")
        _require_exact(turn.get("step"), index + 1, "model turn step")
        _require_exact(
            turn.get("retry_lineage_id"),
            f"{pair_id}:{condition}:turn-{index + 1:03d}",
            "model turn retry lineage",
        )
        _require_exact(
            turn.get("provider_model_id"), family["model_alias"], "provider model"
        )
        for field in ("transport_attempts", "input_tokens", "output_tokens"):
            _require_int(
                turn.get(field),
                f"model turn {field}",
                minimum=1 if field == "transport_attempts" else 0,
            )
        created = turn.get("provider_created")
        if created is not None:
            _require_int(created, "model turn provider_created")
        _require_sha256(turn.get("prompt_sha256"), "model prompt digest")
        response_id = turn.get("provider_response_id")
        if (
            not isinstance(response_id, str)
            or not response_id
            or response_id in response_ids
        ):
            raise AnalysisInputError(
                "provider response identity is missing or duplicate"
            )
        response_ids.add(response_id)
        response_text = turn.get("response_text")
        if not isinstance(response_text, str) or hashlib.sha256(
            response_text.encode("utf-8")
        ).hexdigest() != turn.get("response_sha256"):
            raise AnalysisInputError("model response digest mismatch")
        action = turn.get("action")
        if (
            isinstance(action, dict)
            and action.get("action") == "test"
            and turn.get("observation_status") == "scored"
        ):
            raise AnalysisInputError("pre-turn private feedback was exposed")
        if turn.get("observation_status") == "scored":
            scored_turn_indices.append(index)
    _audit_final_score_terminal(result, turns, scored_turn_indices, "condition")
    return {
        "success": success,
        "task_score": score,
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "hard_constraints_passed": hard_constraints,
        "common_scaffold_sha256": result["common_scaffold_sha256"],
        "integrity_violations": [],
    }


def _audit_bundle(
    record: dict[str, Any],
    family: dict[str, Any],
    *,
    schedule_response_ids: set[str],
    schedule_scaffold_sha256: list[str],
) -> dict[str, Any]:
    output_dir = Path(record["output_dir"])
    _reject_unsafe_components(output_dir, "registered output directory")
    if output_dir.name != record["replicate_id"] or not output_dir.is_dir():
        raise AnalysisInputError("registered output directory is invalid")
    manifest = _json_object(output_dir / "pair_manifest.json", "final pair manifest")
    if set(manifest) != PAIR_FIELDS:
        raise AnalysisInputError(
            "pair manifest fields do not match the registered schema"
        )
    pair_id = f"confirmation-v3:{record['control']}:{record['replicate_id']}"
    expected = {
        "schema_version": PAIR_SCHEMA,
        "completion_status": "complete",
        "pair_id": pair_id,
        "task_id": "TOOLFORMER-FILTER",
        "control": record["control"],
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "private_score_policy": "final_only",
        "family_path": Path(record["family_path"]).resolve().as_posix(),
        "family_sha256": record["family_sha256"],
        "replicate_id": record["replicate_id"],
        "condition_execution_order": record["condition_execution_order"],
        "task_prompt_file_sha256": family["task_prompt_file_sha256"],
        "task_prompt_canonical_text_sha256": family[
            "task_prompt_canonical_text_sha256"
        ],
        "full_artifact_sha256": _binding_digest(family, "full_artifact"),
        "selected_artifact_sha256": _binding_digest(family, "selected_artifact"),
        "source_map_sha256": _binding_digest(family, "source_map"),
        "case_registry_sha256": _binding_digest(family, "case_registry"),
        "scorer_sha256": _binding_digest(family, "scorer"),
        "runner_sha256": _binding_digest(family, "runner"),
        "scheduler_sha256": _binding_digest(family, "scheduler"),
        "analyzer_sha256": _binding_digest(family, "analyzer"),
        "aci_runner_sha256": _binding_digest(family, "aci_runner"),
        "transport_sha256": _binding_digest(family, "transport"),
        "case_generator_sha256": _binding_digest(family, "case_generator"),
        "reference_registry_sha256": _binding_digest(family, "v2_case_registry"),
    }
    for field, value in expected.items():
        _require_exact(manifest.get(field), value, f"pair manifest {field}")
    provider = manifest.get("provider_config")
    expected_provider = {
        "model_alias": family["model_alias"],
        "wire_api": family["wire_api"],
        "max_tokens": family["max_tokens"],
        "timeout_seconds": 240.0,
        "max_attempts": family["maximum_transport_attempts"],
        "retry_delay_seconds": 2.0,
        "temperature": family["temperature"],
        "provider_label": family["provider_label"],
    }
    _require_exact(provider, expected_provider, "provider identity")
    workspace = manifest.get("workspace_state")
    expected_workspace = {
        "sha256": family["workspace_tree_sha256"],
        "file_count": family["workspace_file_count"],
        "total_bytes": family["workspace_total_bytes"],
        "excluded_directory_names": family["workspace_excluded_directory_names"],
    }
    if not isinstance(workspace, dict):
        raise AnalysisInputError("workspace state is missing")
    for field, value in expected_workspace.items():
        _require_exact(workspace.get(field), value, f"workspace {field}")
    if set(manifest.get("results", {})) != set(CONDITIONS):
        raise AnalysisInputError("pair results must contain exactly B/F/S")
    if set(manifest.get("conditions", {})) != set(CONDITIONS):
        raise AnalysisInputError("pair conditions must contain exactly B/F/S")
    expected_contexts, expected_case_ids = _audit_registered_snapshots(
        output_dir, manifest, family
    )
    response_ids: set[str] = set()
    rows = {
        condition: _audit_condition(
            output_dir=output_dir,
            condition=condition,
            pair_id=pair_id,
            family=family,
            manifest=manifest,
            response_ids=response_ids,
            expected_context_sha256=expected_contexts[condition],
            expected_case_ids=expected_case_ids,
        )
        for condition in CONDITIONS
    }
    scaffold_digests = {row["common_scaffold_sha256"] for row in rows.values()}
    if len(scaffold_digests) != 1:
        raise AnalysisInputError("common scaffold digest differs across conditions")
    scaffold_digest = next(iter(scaffold_digests))
    if schedule_scaffold_sha256 and schedule_scaffold_sha256[0] != scaffold_digest:
        raise AnalysisInputError("common scaffold digest differs across the schedule")
    if response_ids & schedule_response_ids:
        raise AnalysisInputError(
            "provider response identity is duplicated across blocks"
        )
    event = joint_substitution_event(
        rows["B"], rows["F"], rows["S"], family["maximum_shortfall"]
    )
    schedule_response_ids.update(response_ids)
    if not schedule_scaffold_sha256:
        schedule_scaffold_sha256.append(scaffold_digest)
    return {
        "condition_results": {
            condition: {
                "success": rows[condition]["success"],
                "task_score": rows[condition]["task_score"],
                "hard_constraints_passed": rows[condition]["hard_constraints_passed"],
            }
            for condition in CONDITIONS
        },
        "joint_substitution_event": event,
    }


def _load_registered_progress(
    progress_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    progress = _json_object(progress_path, "confirmation-v3 progress")
    if set(progress) != {
        "schema_version",
        "registered_schedule_length",
        "counts",
        "records",
    }:
        raise AnalysisInputError("progress fields do not match the scheduler schema")
    _require_exact(progress["schema_version"], PROGRESS_SCHEMA, "progress schema")
    records = progress.get("records")
    if not isinstance(records, list):
        raise AnalysisInputError("progress records must be a list")
    family_records: dict[str, tuple[Path, str]] = {}
    for row in records:
        if not isinstance(row, dict):
            raise AnalysisInputError("progress records must be objects")
        control = row.get("control")
        path = row.get("family_path")
        digest = row.get("family_sha256")
        if control not in CONTROL_SPECS or not isinstance(path, str):
            raise AnalysisInputError("progress references an invalid registered family")
        _require_sha256(digest, "progress family digest")
        value = (Path(path), digest)
        if control in family_records and family_records[control] != value:
            raise AnalysisInputError("progress replaces a registered family")
        family_records[control] = value
    if set(family_records) != set(CONTROL_SPECS):
        raise AnalysisInputError("progress must cover identity and planted families")
    families = {
        control: _validate_family(*family_records[control])
        for control in ("identity", "planted")
    }
    expected_rows = []
    for control in ("identity", "planted"):
        family_path, family_sha256 = family_records[control]
        for replicate in families[control]["replicate_schedule"]:
            expected_rows.append(
                {
                    "control": control,
                    "task_key": "toolformer_filter",
                    "replicate_id": replicate["replicate_id"],
                    "condition_execution_order": replicate["condition_order"],
                    "family_path": family_path.resolve().as_posix(),
                    "family_sha256": family_sha256,
                }
            )
    _require_exact(
        progress.get("registered_schedule_length"),
        len(expected_rows),
        "progress denominator",
    )
    if len(records) != len(expected_rows):
        raise AnalysisInputError("progress omits or duplicates a registered block")
    counts = progress.get("counts")
    if not isinstance(counts, dict) or set(counts) != {
        "completed",
        "failed",
        "preserved",
    }:
        raise AnalysisInputError("progress status counts are invalid")
    if any(type(value) is not int or value < 0 for value in counts.values()):
        raise AnalysisInputError("progress status counts must be nonnegative integers")
    observed_counts = {status: 0 for status in ("completed", "failed", "preserved")}
    for index, (row, expected) in enumerate(zip(records, expected_rows)):
        for field, value in expected.items():
            _require_exact(row.get(field), value, f"progress record {index} {field}")
        status = row.get("status")
        if status not in observed_counts:
            raise AnalysisInputError("progress status vocabulary is invalid")
        observed_counts[status] += 1
        required = set(expected) | {"output_dir", "status"}
        if status in {"completed", "preserved"}:
            required.add("pair_id")
            _require_exact(
                row.get("pair_id"),
                f"confirmation-v3:{row['control']}:{row['replicate_id']}",
                "progress pair_id",
            )
        else:
            required |= {"error_type", "error_message"}
            for field in ("error_type", "error_message"):
                if not isinstance(row.get(field), str) or not row[field]:
                    raise AnalysisInputError(
                        "failed progress metadata must be nonempty strings"
                    )
        if set(row) != required:
            raise AnalysisInputError(
                "progress record fields do not match its terminal status"
            )
        output_dir = row.get("output_dir")
        if (
            not isinstance(output_dir, str)
            or Path(output_dir).name != row["replicate_id"]
        ):
            raise AnalysisInputError(
                "progress output directory replaced a registered ID"
            )
        _reject_unsafe_components(
            Path(output_dir), f"progress record {index} output directory"
        )
    _require_exact(counts, observed_counts, "progress counts")
    return progress, families


def _v2_registered_case_ids(manifest: dict[str, Any]) -> list[str]:
    verified_inputs = manifest.get("verified_family_inputs")
    if not isinstance(verified_inputs, dict):
        raise AnalysisInputError("v2 verified family inputs are missing")
    binding = verified_inputs.get("case_registry")
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        raise AnalysisInputError("v2 case registry binding is invalid")
    digest = _require_sha256(binding.get("sha256"), "v2 case registry digest")
    _require_exact(
        manifest.get("case_registry_sha256"), digest, "v2 manifest case registry digest"
    )
    raw_path = binding.get("path")
    if not isinstance(raw_path, str) or not Path(raw_path).is_absolute():
        raise AnalysisInputError("v2 case registry path is invalid")
    payload = _snapshot_bytes(
        Path(raw_path), digest, "v2 registered case registry"
    )
    try:
        registry = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisInputError("v2 case registry must be valid UTF-8 JSON") from exc
    if not isinstance(registry, dict) or set(registry) != {
        "schema_version",
        "task_id",
        "evidence_boundary",
        "blocks",
    }:
        raise AnalysisInputError("v2 case registry fields are invalid")
    _require_exact(
        registry.get("schema_version"),
        "effectslice-toolformer-filter-case-registry.v1",
        "v2 case registry schema",
    )
    _require_exact(registry.get("task_id"), "TOOLFORMER-FILTER", "v2 registry task")
    if (
        not isinstance(registry.get("evidence_boundary"), str)
        or not registry["evidence_boundary"]
    ):
        raise AnalysisInputError("v2 case registry evidence boundary is invalid")
    blocks = registry.get("blocks")
    cases = blocks.get("confirmation_v2") if isinstance(blocks, dict) else None
    if not isinstance(cases, list) or len(cases) != 64:
        raise AnalysisInputError("v2 case registry must contain 64 confirmation cases")
    case_ids: list[str] = []
    for case in cases:
        case_id = case.get("case_id") if isinstance(case, dict) else None
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise AnalysisInputError("v2 registered case IDs must be nonempty and unique")
        case_ids.append(case_id)
    return case_ids


def _audit_v2_result(
    result: dict[str, Any],
    *,
    pair_id: str,
    condition: str,
    response_ids: set[str],
    expected_case_ids: list[str],
) -> dict[str, Any]:
    if set(result) != RUN_RESULT_FIELDS:
        raise AnalysisInputError("v2 run result fields do not match the runner schema")
    _audit_result_scalars(result)
    _require_exact(result.get("status"), "scored", "v2 condition status")
    _require_exact(result.get("private_score_policy"), "final_only", "v2 score policy")
    _require_exact(result.get("private_score_count"), 1, "v2 private score count")
    _require_exact(result.get("private_feedback_exposed"), False, "v2 private feedback")
    metrics = result.get("scorer_metrics")
    if not isinstance(metrics, list) or len(metrics) != 1:
        raise AnalysisInputError("v2 condition must contain exactly one private score")
    success, score, hard_constraints = _audit_metric(
        metrics[0],
        expected_block="confirmation_v2",
        expected_case_ids=expected_case_ids,
    )
    _require_exact(result.get("success"), success, "v2 condition success")
    _require_exact(result.get("task_score"), score, "v2 condition task_score")
    turns = result.get("turns")
    if not isinstance(turns, list) or not turns:
        raise AnalysisInputError("v2 condition must contain model turns")
    scored_indices = []
    for index, turn in enumerate(turns):
        if not isinstance(turn, dict) or set(turn) != TURN_FIELDS:
            raise AnalysisInputError(
                "v2 model turn fields do not match the runner schema"
            )
        _require_exact(turn.get("step"), index + 1, "v2 model turn step")
        _require_exact(
            turn.get("retry_lineage_id"),
            f"{pair_id}:{condition}:turn-{index + 1:03d}",
            "v2 model turn retry lineage",
        )
        _require_exact(turn.get("provider_model_id"), "deepseek-v4-flash", "v2 model")
        response_id = turn.get("provider_response_id")
        if (
            not isinstance(response_id, str)
            or not response_id
            or response_id in response_ids
        ):
            raise AnalysisInputError(
                "v2 provider response identity is missing or duplicate"
            )
        response_ids.add(response_id)
        response_text = turn.get("response_text")
        if not isinstance(response_text, str) or hashlib.sha256(
            response_text.encode("utf-8")
        ).hexdigest() != turn.get("response_sha256"):
            raise AnalysisInputError("v2 model response digest mismatch")
        if turn.get("observation_status") == "scored":
            scored_indices.append(index)
    _audit_final_score_terminal(result, turns, scored_indices, "v2 condition")
    return {
        "success": success,
        "task_score": score,
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "hard_constraints_passed": hard_constraints,
        "common_scaffold_sha256": result["common_scaffold_sha256"],
        "integrity_violations": [],
    }


def _audit_v2_bundle(record: dict[str, Any], response_ids: set[str]) -> dict[str, Any]:
    output_dir = Path(record["output_dir"])
    _reject_unsafe_components(output_dir, "v2 registered output directory")
    if (
        output_dir.name != record["replicate_id"]
        or output_dir.parent.name != "toolformer_filter"
        or not output_dir.is_dir()
    ):
        raise AnalysisInputError("v2 registered output directory is invalid")
    manifest = _json_object(output_dir / "pair_manifest.json", "v2 final pair manifest")
    if set(manifest) != V2_PAIR_FIELDS:
        raise AnalysisInputError("v2 pair manifest fields do not match its schema")
    pair_id = f"toolformer_filter:confirmation-v2:{record['replicate_id']}"
    for field, expected in {
        "schema_version": "effectslice-toolformer-filter-pair.v2",
        "provider_protocol_version": "effectslice-deepseek-final-only.v3",
        "evidence_boundary": "registered_final_only_confirmation",
        "pair_id": pair_id,
        "task_id": "TOOLFORMER-FILTER",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "case_block": "confirmation_v2",
        "comparison_role": "development_triage",
        "slice_candidate_id": "prefix_01",
        "confirmation_case_count": 64,
        "private_score_policy": "final_only",
    }.items():
        _require_exact(manifest.get(field), expected, f"v2 pair manifest {field}")
    summaries = manifest.get("results")
    if not isinstance(summaries, dict) or set(summaries) != set(CONDITIONS):
        raise AnalysisInputError("v2 pair results must contain exactly B/F/S")
    local_response_ids: set[str] = set()
    expected_case_ids = _v2_registered_case_ids(manifest)
    rows = {}
    for condition in CONDITIONS:
        summary = summaries[condition]
        if not isinstance(summary, dict):
            raise AnalysisInputError("v2 condition summary is missing")
        result_path = output_dir / condition / "run_result.json"
        _registered_stored_path(
            summary.get("run_result_path"), result_path, "v2 run result path"
        )
        result = _json_object(result_path, "v2 condition run result")
        for field in (
            "status",
            "terminal_reason",
            "submitted",
            "task_score",
            "success",
            "input_tokens",
            "output_tokens",
            "transport_attempts",
            "private_score_policy",
            "private_score_count",
            "private_feedback_exposed",
        ):
            _require_exact(result.get(field), summary.get(field), f"v2 summary {field}")
        rows[condition] = _audit_v2_result(
            result,
            pair_id=pair_id,
            condition=condition,
            response_ids=local_response_ids,
            expected_case_ids=expected_case_ids,
        )
    scaffolds = {row["common_scaffold_sha256"] for row in rows.values()}
    if len(scaffolds) != 1 or local_response_ids & response_ids:
        raise AnalysisInputError("v2 condition identity is inconsistent")
    response_ids.update(local_response_ids)
    return {
        "joint_substitution_event": joint_substitution_event(
            rows["B"], rows["F"], rows["S"], 0.05
        )
    }


def reanalyze_v2_negative_control(progress_path: Path) -> dict[str, Any]:
    progress = _json_object(Path(progress_path), "confirmation-v2 progress")
    if set(progress) != {"schema_version", "counts", "records"}:
        raise AnalysisInputError("v2 progress fields do not match the scheduler schema")
    _require_exact(
        progress.get("schema_version"),
        "effectslice-confirmation-v2-progress.v1",
        "v2 progress schema",
    )
    counts = progress.get("counts")
    records = progress.get("records")
    if (
        not isinstance(counts, dict)
        or set(counts) != {"completed", "failed", "preserved"}
        or any(type(value) is not int or value < 0 for value in counts.values())
        or not isinstance(records, list)
    ):
        raise AnalysisInputError("v2 progress status data is invalid")
    observed = {status: 0 for status in counts}
    for row in records:
        if not isinstance(row, dict) or row.get("status") not in observed:
            raise AnalysisInputError("v2 progress record is invalid")
        observed[row["status"]] += 1
    _require_exact(counts, observed, "v2 progress counts")
    toolformer = [row for row in records if row.get("task_key") == "toolformer_filter"]
    expected_ids = [f"r{index:03d}" for index in range(1, 19)]
    if [row.get("replicate_id") for row in toolformer] != expected_ids:
        raise AnalysisInputError("v2 negative control schedule is missing or replaced")
    blocks = []
    integrity = []
    response_ids: set[str] = set()
    for row in toolformer:
        status = row.get("status")
        expected_fields = {"task_key", "replicate_id", "status", "output_dir"}
        if status in {"completed", "preserved"}:
            expected_fields.add("pair_id")
            _require_exact(
                row.get("pair_id"),
                f"toolformer_filter:confirmation-v2:{row['replicate_id']}",
                "v2 progress pair_id",
            )
        else:
            expected_fields |= {"error_type", "error_message"}
        if set(row) != expected_fields:
            raise AnalysisInputError("v2 progress record fields are invalid")
        if status == "failed":
            blocks.append(False)
            integrity.append(False)
            continue
        try:
            block = _audit_v2_bundle(row, response_ids)
        except (AnalysisInputError, OSError, UnicodeError):
            blocks.append(False)
            integrity.append(False)
        else:
            blocks.append(block["joint_substitution_event"] is True)
            integrity.append(True)
    events = sum(blocks)
    full_integrity = len(blocks) == 18 and all(integrity)
    admitted = bool(full_integrity and events == 18)
    decision = "invalid" if not full_integrity else ("admit" if admitted else "reject")
    return {
        "source": "existing_v2_final_toolformer_prefix_01",
        "candidate_id": "prefix_01",
        "evidence_role": "real_unstable_negative_control",
        "registered_block_count": len(blocks),
        "joint_event_count": events,
        "full_integrity_passed": full_integrity,
        "decision": decision,
        "strict_subset_admitted": admitted,
    }


def analyze_registered_schedule(
    progress_path: Path,
    *,
    include_historical_negative_control: bool = True,
    historical_v2_progress_path: Path | None = None,
) -> dict[str, Any]:
    if type(include_historical_negative_control) is not bool:
        raise ValueError("include_historical_negative_control must be a bool")
    if (
        historical_v2_progress_path is not None
        and not include_historical_negative_control
    ):
        raise ValueError(
            "historical_v2_progress_path requires historical negative-control analysis"
        )
    progress, families = _load_registered_progress(Path(progress_path))
    blocks = []
    schedule_response_ids: set[str] = set()
    schedule_scaffold_sha256: list[str] = []
    for record in progress["records"]:
        base = {
            "control": record["control"],
            "replicate_id": record["replicate_id"],
            "registered_status": record["status"],
        }
        if record["status"] == "failed":
            blocks.append(
                {
                    **base,
                    "integrity_passed": False,
                    "integrity_violations": ["registered_runner_failed"],
                    "joint_substitution_event": False,
                    "condition_results": None,
                }
            )
            continue
        try:
            audited = _audit_bundle(
                record,
                families[record["control"]],
                schedule_response_ids=schedule_response_ids,
                schedule_scaffold_sha256=schedule_scaffold_sha256,
            )
        except (AnalysisInputError, OSError, UnicodeError):
            blocks.append(
                {
                    **base,
                    "integrity_passed": False,
                    "integrity_violations": ["registered_bundle_integrity_failure"],
                    "joint_substitution_event": False,
                    "condition_results": None,
                }
            )
        else:
            blocks.append(
                {
                    **base,
                    "integrity_passed": True,
                    "integrity_violations": [],
                    **audited,
                }
            )
    controls = {}
    for control in ("identity", "planted"):
        rows = [row for row in blocks if row["control"] == control]
        events = sum(row["joint_substitution_event"] is True for row in rows)
        full_integrity = all(row["integrity_passed"] is True for row in rows)
        if control == "identity":
            decision = "descriptive_only"
            admitted = False
        else:
            admitted = bool(full_integrity and len(rows) == 18 and events == 18)
            decision = "admit" if admitted else "reject"
        controls[control] = {
            "registered_block_count": len(rows),
            "joint_event_count": events,
            "full_integrity_passed": full_integrity,
            "decision": decision,
            "strict_subset_admitted": admitted,
        }
    result = {
        "schema_version": "effectslice-confirmation-v3-analysis.v1",
        "output_semantics": "derived_regenerable_non_raw",
        "primary_event": "joint_substitution_event",
        "decision_basis": "finite_registered_schedule",
        "independence_verified": False,
        "schedule_integrity_passed": True,
        "registered_schedule_length": progress["registered_schedule_length"],
        "status_counts": progress["counts"],
        "iid_conditional_reference": iid_conditional_lower_reference(
            controls["planted"]["joint_event_count"], 18
        ),
        "controls": controls,
        "blocks": blocks,
        "strict_subset_admitted": controls["planted"]["strict_subset_admitted"],
    }
    if include_historical_negative_control:
        v2_path = (
            Path(historical_v2_progress_path)
            if historical_v2_progress_path is not None
            else RUN_ROOT
            / "experiment_results"
            / "confirmation_v2"
            / "confirmation_v2_progress.json"
        )
        negative = reanalyze_v2_negative_control(v2_path)
        result["historical_negative_control"] = negative
        registered_decision = (
            "pass"
            if negative["full_integrity_passed"] is True
            and negative["registered_block_count"] == 18
            and negative["decision"] == "reject"
            and controls["planted"]["strict_subset_admitted"] is True
            else "fail"
        )
    else:
        registered_decision = "not_evaluated"
    result["rule_comparison"] = {
        "development_selection_only": {
            "status": "development_only",
            "decision": "accept",
            "included_in_confirmation": False,
        },
        "adaptive_case_level": {
            "status": "invalid",
            "contaminated": True,
            "included_in_confirmation": False,
        },
        "registered_joint_schedule": {
            "status": "valid",
            "decision": registered_decision,
            "decision_basis": "finite_registered_schedule",
            "preserves_registered_failures": True,
        },
    }
    return result


def iid_conditional_lower_reference(events: Any, total: Any) -> dict[str, Any]:
    if type(events) is not int or type(total) is not int:
        raise ValueError("events and total must be non-bool integers")
    if total < 1 or not 0 <= events <= total:
        raise ValueError("events must satisfy 0 <= events <= total with total >= 1")
    lower = 0.0 if events == 0 else float(beta.ppf(0.02, events, total - events + 1))
    if not math.isfinite(lower):
        raise ValueError("conditional reference is not finite")
    return {
        "label": "iid_conditional_only",
        "alpha": 0.02,
        "events": events,
        "registered_blocks": total,
        "lower": lower,
        "independence_verified": False,
        "population_guarantee": False,
    }


def _paths_overlap(first: Path, second: Path) -> bool:
    left = Path(first).resolve()
    right = Path(second).resolve()
    try:
        left.relative_to(right)
        return True
    except ValueError:
        pass
    try:
        right.relative_to(left)
        return True
    except ValueError:
        return False


def _analysis_input_boundaries(
    progress_path: Path, historical_v2_progress_path: Path | None
) -> tuple[set[Path], set[Path]]:
    protected_files: set[Path] = set()
    protected_roots: set[Path] = set()
    for path, label in (
        (Path(progress_path), "confirmation-v3 progress"),
        (
            Path(historical_v2_progress_path)
            if historical_v2_progress_path is not None
            else None,
            "confirmation-v2 progress",
        ),
    ):
        if path is None:
            continue
        progress = _json_object(path, label)
        resolved_progress = path.resolve()
        protected_files.add(resolved_progress)
        protected_roots.add(resolved_progress.parent)
        records = progress.get("records")
        if not isinstance(records, list):
            raise AnalysisInputError(f"{label} records are invalid")
        for row in records:
            if not isinstance(row, dict):
                raise AnalysisInputError(f"{label} record is invalid")
            output_dir = row.get("output_dir")
            if not isinstance(output_dir, str):
                raise AnalysisInputError(f"{label} output directory is invalid")
            _reject_unsafe_components(Path(output_dir), f"{label} output directory")
            protected_roots.add(Path(output_dir).resolve())
            family_path = row.get("family_path")
            if family_path is not None:
                if not isinstance(family_path, str):
                    raise AnalysisInputError(f"{label} family path is invalid")
                _reject_unsafe_components(Path(family_path), f"{label} family path")
                protected_files.add(Path(family_path).resolve())
    return protected_files, protected_roots


def _derived_destination(output_path: Path, derived_root: Path) -> Path:
    supplied_output = Path(output_path)
    supplied_root = Path(derived_root)
    _reject_unsafe_components(supplied_output, "analysis output")
    _reject_unsafe_components(supplied_root, "derived output root")
    destination = supplied_output.resolve()
    root = supplied_root.resolve()
    normalized_parts = {part.lower() for part in root.parts}
    if "derived" not in normalized_parts or normalized_parts & {
        "raw",
        "artifacts",
        "experiment_results",
    }:
        raise AnalysisInputError(
            "analysis output root must be a derived-only directory"
        )
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise AnalysisInputError("analysis output escapes its derived root") from exc
    if not relative.parts or destination.suffix.lower() != ".json":
        raise AnalysisInputError(
            "analysis output must be a JSON file below its derived root"
        )
    return destination


def write_analysis(
    progress_path: Path,
    output_path: Path,
    *,
    include_historical_negative_control: bool = True,
    historical_v2_progress_path: Path | None = None,
    derived_root: Path | None = None,
) -> dict[str, Any]:
    root = (
        Path(derived_root)
        if derived_root is not None
        else RUN_ROOT / "derived" / "confirmation_v3"
    )
    destination = _derived_destination(Path(output_path), root)
    effective_v2_path = (
        Path(historical_v2_progress_path)
        if historical_v2_progress_path is not None
        else (
            RUN_ROOT
            / "experiment_results"
            / "confirmation_v2"
            / "confirmation_v2_progress.json"
            if include_historical_negative_control
            else None
        )
    )
    protected_files, protected_roots = _analysis_input_boundaries(
        Path(progress_path), effective_v2_path
    )
    resolved_root = root.resolve()
    if destination in protected_files:
        raise AnalysisInputError("analysis output must not overwrite raw input")
    if any(_paths_overlap(resolved_root, raw_root) for raw_root in protected_roots):
        raise AnalysisInputError("derived output root overlaps registered raw evidence")
    result = analyze_registered_schedule(
        Path(progress_path),
        include_historical_negative_control=include_historical_negative_control,
        historical_v2_progress_path=historical_v2_progress_path,
    )
    try:
        payload = (
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AnalysisInputError("analysis result is not deterministic JSON") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    _reject_unsafe_components(destination.parent, "analysis output parent")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except OSError as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass
        raise AnalysisInputError("analysis output could not be written safely") from exc
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit finite-schedule EffectSlice confirmation-v3 evidence"
    )
    parser.add_argument(
        "--progress-path",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v3"
        / "confirmation_v3_progress.json",
    )
    parser.add_argument(
        "--historical-v2-progress-path",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v2"
        / "confirmation_v2_progress.json",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=RUN_ROOT / "derived" / "confirmation_v3" / "analysis.json",
    )
    parser.add_argument(
        "--no-historical-negative-control",
        action="store_false",
        dest="include_historical_negative_control",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    v2_path = (
        args.historical_v2_progress_path
        if args.include_historical_negative_control
        else None
    )
    result = write_analysis(
        args.progress_path,
        args.output_path,
        include_historical_negative_control=args.include_historical_negative_control,
        historical_v2_progress_path=v2_path,
    )
    print(
        json.dumps(
            {
                "registered_schedule_length": result["registered_schedule_length"],
                "strict_subset_admitted": result["strict_subset_admitted"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
