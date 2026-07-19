import copy
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from scipy.stats import beta


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

import analyze_confirmation_v3 as analyzer  # noqa: E402
from effectslice.confirmation_v3 import balanced_schedule  # noqa: E402


REGISTERED = "registered_final_only_confirmation_v3"
NO_ARTIFACT_CONTEXT = (
    "No paper-derived method artifact is supplied for this condition. "
    "Use only the common bounded ACI contract, the locked task, and tool feedback."
)
TASK_PROMPT_BYTES = b"synthetic registered task prompt\n"
FULL_ARTIFACT_BYTES = b"synthetic full artifact\n"
PLANTED_ARTIFACT_BYTES = b"synthetic strict subset artifact\n"
SOURCE_MAP_BYTES = b'{"schema_version":"synthetic-source-map.v1"}\n'
WORKSPACE_FILES = {
    "README.md": b"synthetic workspace\n",
    "task.py": b"VALUE = 1\n",
}
SHA = {
    name: hashlib.sha256(name.encode("ascii")).hexdigest()
    for name in (
        "prompt-file",
        "prompt-text",
        "full",
        "selected",
        "source-map",
        "case-registry",
        "scorer",
        "runner",
        "scheduler",
        "analyzer",
        "aci-runner",
        "transport",
        "case-generator",
        "reference-registry",
        "workspace",
        "common-scaffold",
    )
}


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(payload) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def case_registry_bytes() -> bytes:
    return json_bytes(
        {
            "schema_version": "effectslice-toolformer-filter-case-registry.v3",
            "blocks": {
                "confirmation_v3": [
                    {"case_id": f"case-{index:03d}"} for index in range(1, 65)
                ]
            },
        }
    )


def v2_case_registry_payload() -> dict:
    return {
        "schema_version": "effectslice-toolformer-filter-case-registry.v1",
        "task_id": "TOOLFORMER-FILTER",
        "evidence_boundary": "synthetic frozen private cases",
        "blocks": {
            "confirmation_v2": [
                {"case_id": f"case-{index:03d}"} for index in range(1, 65)
            ]
        },
    }


V2_VERIFIED_INPUT_NAMES = (
    "aci_protocol",
    "aci_runner",
    "case_generator",
    "case_registry",
    "discovery_summary",
    "evidence_binding",
    "family_builder",
    "full_artifact",
    "runner",
    "scheduler",
    "scorer",
    "selected_artifact",
    "slice_registry",
    "source_map",
    "task_prompt",
    "transport",
)


def write_v2_family_bundle(
    root: Path, registry_path: Path
) -> tuple[Path, str, dict, dict]:
    input_dir = root / "registered_inputs"
    special_paths = {
        "case_registry": registry_path,
        "selected_artifact": root / "synthetic-prefix-01.md",
        "slice_registry": root / "synthetic-slice-registry.json",
    }
    bindings = {}
    for name in V2_VERIFIED_INPUT_NAMES:
        path = special_paths.get(name, input_dir / f"{name}.bin")
        if name != "case_registry":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"synthetic frozen {name}\n".encode("ascii"))
        bindings[name] = {
            "path": path.resolve().as_posix(),
            "sha256": sha256_file(path),
        }

    workspace_root = root / "workspace"
    for relative, payload in WORKSPACE_FILES.items():
        path = workspace_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    workspace = {
        **workspace_state(),
        "workspace": workspace_root.resolve().as_posix(),
    }
    family = {
        "schema_version": "effectslice-confirmation-v2-family.v1",
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "selected_candidate_id": "prefix_01",
        "retained_atom_ids": ["T01"],
        "retained_scc_count": 1,
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v2",
        "case_count": 64,
        "replicate_count": 18,
        "replicate_schedule": [
            {
                "replicate_id": f"r{index:03d}",
                "condition_order": ["B", "F", "S"],
            }
            for index in range(1, 19)
        ],
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "confirmation_unsealed": False,
        "evidence_boundary": "synthetic registered family",
        "selected_artifact_sha256": bindings["selected_artifact"]["sha256"],
        "discovery_summary_sha256": bindings["discovery_summary"]["sha256"],
        "slice_registry_sha256": bindings["slice_registry"]["sha256"],
        "case_registry_sha256": bindings["case_registry"]["sha256"],
        "source_map_sha256": bindings["source_map"]["sha256"],
        "task_prompt_sha256": bindings["task_prompt"]["sha256"],
        "scorer_sha256": bindings["scorer"]["sha256"],
        "runner_sha256": bindings["runner"]["sha256"],
        "scheduler_sha256": bindings["scheduler"]["sha256"],
        "aci_runner_sha256": bindings["aci_runner"]["sha256"],
        "aci_protocol_sha256": bindings["aci_protocol"]["sha256"],
        "evidence_binding_sha256": bindings["evidence_binding"]["sha256"],
        "transport_sha256": bindings["transport"]["sha256"],
        "case_generator_sha256": bindings["case_generator"]["sha256"],
        "family_builder_sha256": bindings["family_builder"]["sha256"],
        "full_artifact_sha256": bindings["full_artifact"]["sha256"],
        "workspace_tree_sha256": workspace["sha256"],
        "workspace_file_count": workspace["file_count"],
        "workspace_total_bytes": workspace["total_bytes"],
    }
    family_path = root / "confirmation_v2_family.json"
    write_json(family_path, family)
    return family_path, sha256_file(family_path), bindings, workspace


def workspace_state() -> dict:
    digest = hashlib.sha256()
    total_bytes = 0
    for relative, payload in sorted(WORKSPACE_FILES.items()):
        relative_bytes = relative.encode("utf-8")
        digest.update(len(relative_bytes).to_bytes(8, "big"))
        digest.update(relative_bytes)
        digest.update(payload)
        digest.update(len(payload).to_bytes(8, "big"))
        total_bytes += len(payload)
    return {
        "sha256": digest.hexdigest(),
        "file_count": len(WORKSPACE_FILES),
        "total_bytes": total_bytes,
        "excluded_directory_names": [".git", ".pytest_cache", "__pycache__"],
    }


def registered_input_bytes(control: str) -> dict[str, bytes]:
    return {
        "task_prompt": TASK_PROMPT_BYTES,
        "full_artifact": FULL_ARTIFACT_BYTES,
        "selected_artifact": (
            PLANTED_ARTIFACT_BYTES if control == "planted" else FULL_ARTIFACT_BYTES
        ),
        "source_map": SOURCE_MAP_BYTES,
        "case_registry": case_registry_bytes(),
    }


def family_payload(control: str) -> dict:
    planted = control == "planted"
    seed = 2026071802 if planted else 2026071801
    count = 18 if planted else 6
    inputs = registered_input_bytes(control)
    workspace = workspace_state()
    bindings = {
        "full_artifact": {
            "path": "full.md",
            "sha256": hashlib.sha256(inputs["full_artifact"]).hexdigest(),
            "status": "bound",
        },
        "selected_artifact": {
            "path": "selected.md",
            "sha256": hashlib.sha256(inputs["selected_artifact"]).hexdigest(),
            "status": "bound",
        },
        "source_map": {
            "path": "source.json",
            "sha256": hashlib.sha256(inputs["source_map"]).hexdigest(),
            "status": "bound",
        },
        "case_registry": {
            "path": "cases.json",
            "sha256": hashlib.sha256(inputs["case_registry"]).hexdigest(),
            "status": "bound",
        },
        "scorer": {"path": "scorer.py", "sha256": SHA["scorer"], "status": "bound"},
        "runner": {"path": "runner.py", "sha256": SHA["runner"], "status": "bound"},
        "scheduler": {
            "path": "scheduler.py",
            "sha256": SHA["scheduler"],
            "status": "bound",
        },
        "analyzer": {
            "path": "analyzer.py",
            "sha256": SHA["analyzer"],
            "status": "bound",
        },
        "aci_runner": {
            "path": "aci_runner.py",
            "sha256": SHA["aci-runner"],
            "status": "bound",
        },
        "transport": {
            "path": "transport.py",
            "sha256": SHA["transport"],
            "status": "bound",
        },
        "case_generator": {
            "path": "cases.py",
            "sha256": SHA["case-generator"],
            "status": "bound",
        },
        "v2_case_registry": {
            "path": "v2_cases.json",
            "sha256": SHA["reference-registry"],
            "status": "bound",
        },
        "task_prompt": {
            "path": "task.md",
            "file_sha256": hashlib.sha256(inputs["task_prompt"]).hexdigest(),
            "canonical_text_sha256": hashlib.sha256(
                inputs["task_prompt"].decode("utf-8").strip().encode("utf-8")
            ).hexdigest(),
            "status": "bound",
        },
    }
    return {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": "complete",
        "control": control,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "strict_subset": planted,
        "calibration_role": (
            "planted_redundancy_positive_control"
            if planted
            else "identity_instrumentation_only"
        ),
        "retained_atom_ids": ["T01"],
        "retained_unit_count": 1,
        "retained_scc_count": 1,
        "case_block": "confirmation_v3",
        "case_count": 64,
        "case_role": "clustered",
        "case_generator_config_id": "synthetic-v3-cases",
        "statistical_unit": "registered_matched_block",
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "iid_conditional_reference": {"label": "iid_conditional_only"},
        "replicate_count": count,
        "replicate_schedule": balanced_schedule(seed, count),
        "schedule_seed": seed,
        "run_success_threshold": 0.95,
        "maximum_shortfall": 0.05,
        "admission_rule": (
            "all_registered_joint_events" if planted else "descriptive_only"
        ),
        "required_joint_events_for_admission": 18 if planted else None,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "fresh_provider_conversation_per_condition": True,
        "comparison_role": REGISTERED,
        "evidence_boundary": REGISTERED,
        "task_prompt_path": "task.md",
        "task_prompt_status": "bound",
        "task_prompt_file_sha256": bindings["task_prompt"]["file_sha256"],
        "task_prompt_canonical_text_sha256": bindings["task_prompt"][
            "canonical_text_sha256"
        ],
        "workspace_path": "workspace",
        "workspace_tree_sha256": workspace["sha256"],
        "workspace_file_count": workspace["file_count"],
        "workspace_total_bytes": workspace["total_bytes"],
        "workspace_excluded_directory_names": workspace[
            "excluded_directory_names"
        ],
        "bindings": bindings,
    }


def score_metric(*, success: bool, score: float) -> dict:
    passed = int(round(score * 64))
    case_scores = [1] * passed + [0] * (64 - passed)
    return {
        "schema_version": "effectslice-toolformer-filter-score.v1",
        "task_id": "TOOLFORMER-FILTER",
        "metric_name": "registered_case_pass_rate",
        "block": "confirmation_v3",
        "evidence_boundary": "synthetic private metric",
        "task_score": sum(case_scores) / 64,
        "success": success,
        "patch_applied": True,
        "contract_passed": True,
        "contract_failures": [],
        "case_scores": case_scores,
        "case_details": [
            {
                "case_id": f"case-{index:03d}",
                "passed": bool(value),
                "keep_match": bool(value),
                "margin_match": bool(value),
                "max_abs_margin_error": 0.0 if value else 1.0,
                "error_type": None,
            }
            for index, value in enumerate(case_scores, start=1)
        ],
        "failure_reason": "" if success else "numerical_case_failed",
        "private_apply_result": {"returncode": 0, "stdout": "", "stderr": ""},
        "public_summary": {
            "status": "passed" if success else "failed",
            "task_score": sum(case_scores) / 64,
            "passed_cases": sum(case_scores),
            "total_cases": 64,
            "contract_passed": True,
            "failure_reason": "" if success else "numerical_case_failed",
        },
    }


def condition_result(
    *, pair_id: str, condition: str, context_sha256: str, success: bool, score: float
) -> tuple[dict, dict, dict, str]:
    metric = score_metric(success=success, score=score)
    action = {
        "action": "submit",
        "query": None,
        "path": None,
        "max_results": None,
        "start_line": None,
        "end_line": None,
        "old_text": None,
        "new_text": None,
    }
    response_text = json.dumps({"action": "submit"}, separators=(",", ":"))
    turn = {
        "step": 1,
        "retry_lineage_id": f"{pair_id}:{condition}:turn-001",
        "prompt_sha256": hashlib.sha256(
            f"{pair_id}:{condition}:prompt".encode()
        ).hexdigest(),
        "response_sha256": hashlib.sha256(response_text.encode()).hexdigest(),
        "response_text": response_text,
        "action": action,
        "observation_status": "scored",
        "observation_message": "final score retained privately",
        "transport_attempts": 1,
        "input_tokens": 10,
        "output_tokens": 3,
        "provider_model_id": "deepseek-v4-flash",
        "provider_response_id": f"response:{pair_id}:{condition}",
        "provider_created": 1,
    }
    diff_text = f"--- a/task.py\n+++ b/task.py\n+{pair_id}:{condition}\n"
    patch_sha256 = hashlib.sha256(diff_text.encode()).hexdigest()
    result = {
        "status": "scored",
        "terminal_reason": "submitted",
        "submitted": True,
        "task_score": metric["task_score"],
        "success": success,
        "diff_text": diff_text,
        "state": {
            "max_actions": 16,
            "observations": [
                {"step": 1, "action": action, "status": "scored", "message": "private"}
            ],
        },
        "turns": [turn],
        "scorer_metrics": [metric],
        "input_tokens": 10,
        "output_tokens": 3,
        "transport_attempts": 1,
        "elapsed_seconds": 0.1,
        "common_scaffold_sha256": SHA["common-scaffold"],
        "condition_context_sha256": context_sha256,
        "task_prompt_sha256": hashlib.sha256(
            TASK_PROMPT_BYTES.decode("utf-8").strip().encode("utf-8")
        ).hexdigest(),
        "private_score_policy": "final_only",
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "public_error": "",
    }
    transcript = {
        "schema_version": "effectslice-confirmation-v3-transcript.v1",
        "evidence_boundary": REGISTERED,
        "turns": [turn],
    }
    summary = {
        "status": "scored",
        "terminal_reason": "submitted",
        "submitted": True,
        "task_score": metric["task_score"],
        "success": success,
        "actions_used": 1,
        "input_tokens": 10,
        "output_tokens": 3,
        "transport_attempts": 1,
        "candidate_patch_sha256": patch_sha256,
        "private_score_policy": "final_only",
        "private_score_count": 1,
        "private_feedback_exposed": False,
    }
    return result, transcript, summary, diff_text


def write_bundle(root: Path, family_path: Path, family: dict, row: dict) -> Path:
    control = family["control"]
    replicate_id = row["replicate_id"]
    pair_id = f"confirmation-v3:{control}:{replicate_id}"
    output = root / "raw" / control / replicate_id
    inputs = registered_input_bytes(control)
    verified_inputs = output / "verified_inputs"
    for name, payload in {
        "task_prompt.md": inputs["task_prompt"],
        "full_artifact.md": inputs["full_artifact"],
        "selected_artifact.md": inputs["selected_artifact"],
        "source_atom_map.json": inputs["source_map"],
        "case_registry.json": inputs["case_registry"],
    }.items():
        path = verified_inputs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    workspace_snapshot = output / "workspace_snapshot"
    for relative, payload in WORKSPACE_FILES.items():
        path = workspace_snapshot / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    context_text = {
        "B": NO_ARTIFACT_CONTEXT,
        "F": inputs["full_artifact"].decode("utf-8").strip(),
        "S": inputs["selected_artifact"].decode("utf-8").strip(),
    }
    contexts = {
        condition: hashlib.sha256(context.encode("utf-8")).hexdigest()
        for condition, context in context_text.items()
    }
    outcomes = {"B": (False, 0.0), "F": (True, 1.0), "S": (True, 1.0)}
    summaries = {}
    for condition in row["condition_order"]:
        success, score = outcomes[condition]
        result, transcript, summary, diff_text = condition_result(
            pair_id=pair_id,
            condition=condition,
            context_sha256=contexts[condition],
            success=success,
            score=score,
        )
        condition_dir = output / condition
        result_path = condition_dir / "run_result.json"
        transcript_path = condition_dir / "transcript.json"
        patch_path = condition_dir / "candidate.patch"
        write_json(result_path, result)
        write_json(transcript_path, transcript)
        patch_path.write_text(diff_text, encoding="utf-8", newline="")
        summary.update(
            {
                "run_result_path": result_path.as_posix(),
                "transcript_path": transcript_path.as_posix(),
                "candidate_patch_path": patch_path.as_posix(),
            }
        )
        summaries[condition] = summary

    bindings = family["bindings"]
    manifest = {
        "schema_version": "effectslice-confirmation-v3-pair.v1",
        "completion_status": "complete",
        "pair_id": pair_id,
        "task_id": "TOOLFORMER-FILTER",
        "control": control,
        "comparison_role": REGISTERED,
        "evidence_boundary": REGISTERED,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "private_score_policy": "final_only",
        "family_path": family_path.resolve().as_posix(),
        "family_sha256": sha256_file(family_path),
        "replicate_id": replicate_id,
        "condition_execution_order": row["condition_order"],
        "task_prompt_path": "task.md",
        "task_prompt_file_sha256": family["task_prompt_file_sha256"],
        "task_prompt_canonical_text_sha256": family[
            "task_prompt_canonical_text_sha256"
        ],
        "full_artifact_path": "full.md",
        "full_artifact_sha256": family["bindings"]["full_artifact"]["sha256"],
        "selected_artifact_path": "selected.md",
        "selected_artifact_sha256": family["bindings"]["selected_artifact"][
            "sha256"
        ],
        "source_map_sha256": family["bindings"]["source_map"]["sha256"],
        "case_registry_sha256": family["bindings"]["case_registry"]["sha256"],
        "scorer_sha256": SHA["scorer"],
        "runner_sha256": SHA["runner"],
        "scheduler_sha256": SHA["scheduler"],
        "analyzer_sha256": SHA["analyzer"],
        "aci_runner_sha256": SHA["aci-runner"],
        "transport_sha256": SHA["transport"],
        "case_generator_sha256": SHA["case-generator"],
        "reference_registry_sha256": SHA["reference-registry"],
        "provider_config": {
            "model_alias": "deepseek-v4-flash",
            "wire_api": "openai_chat_completions",
            "max_tokens": 8192,
            "timeout_seconds": 240.0,
            "max_attempts": 5,
            "retry_delay_seconds": 2.0,
            "temperature": 0,
            "provider_label": "DeepSeek V3.2",
        },
        "workspace_state": {
            **workspace_state(),
            "path": (root / "workspace").as_posix(),
        },
        "conditions": {
            condition: {
                "context_sha256": contexts[condition],
                "max_actions": 16,
                "retry_lineage_prefix": f"{pair_id}:{condition}",
            }
            for condition in row["condition_order"]
        },
        "retry_lineage": {
            condition: f"{pair_id}:{condition}" for condition in row["condition_order"]
        },
        "workspace_snapshot_path": workspace_snapshot.as_posix(),
        "verified_inputs_path": verified_inputs.as_posix(),
        "results": summaries,
    }
    write_json(output / "pair_manifest.json", manifest)
    return output


def write_complete_schedule(root: Path) -> tuple[Path, dict, dict[str, Path]]:
    records = []
    families = {}
    for control in ("identity", "planted"):
        family = family_payload(control)
        family_path = root / f"{control}_family.json"
        write_json(family_path, family)
        families[control] = family_path
        family_sha256 = sha256_file(family_path)
        for row in family["replicate_schedule"]:
            output = write_bundle(root, family_path, family, row)
            records.append(
                {
                    "control": control,
                    "task_key": "toolformer_filter",
                    "replicate_id": row["replicate_id"],
                    "condition_execution_order": row["condition_order"],
                    "family_path": family_path.resolve().as_posix(),
                    "family_sha256": family_sha256,
                    "output_dir": output.as_posix(),
                    "status": "completed",
                    "pair_id": f"confirmation-v3:{control}:{row['replicate_id']}",
                }
            )
    progress = {
        "schema_version": "effectslice-confirmation-v3-progress.v1",
        "registered_schedule_length": 24,
        "counts": {"completed": 24, "failed": 0, "preserved": 0},
        "records": records,
    }
    progress_path = root / "raw" / "confirmation_v3_progress.json"
    write_json(progress_path, progress)
    return progress_path, progress, families


def update_condition_outcome(
    progress: dict,
    *,
    control: str,
    replicate_id: str,
    condition: str,
    success: bool,
    score: float,
) -> Path:
    record = next(
        row
        for row in progress["records"]
        if row["control"] == control and row["replicate_id"] == replicate_id
    )
    output = Path(record["output_dir"])
    manifest_path = output / "pair_manifest.json"
    result_path = output / condition / "run_result.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    metric = score_metric(success=success, score=score)
    result["success"] = success
    result["task_score"] = metric["task_score"]
    result["scorer_metrics"] = [metric]
    manifest["results"][condition]["success"] = success
    manifest["results"][condition]["task_score"] = metric["task_score"]
    write_json(result_path, result)
    write_json(manifest_path, manifest)
    return manifest_path


def test_iid_conditional_lower_reference_uses_registered_beta_quantile():
    reference = analyzer.iid_conditional_lower_reference(18, 18)

    assert reference == {
        "label": "iid_conditional_only",
        "alpha": 0.02,
        "events": 18,
        "registered_blocks": 18,
        "lower": float(beta.ppf(0.02, 18, 1)),
        "independence_verified": False,
        "population_guarantee": False,
    }


@pytest.mark.parametrize(
    ("events", "total"),
    [(True, 18), (18, True), (-1, 18), (19, 18), (1, 0), (math.nan, 18)],
)
def test_iid_conditional_lower_reference_fails_closed(events, total):
    with pytest.raises(ValueError):
        analyzer.iid_conditional_lower_reference(events, total)


def test_complete_registered_schedule_admits_only_the_planted_control(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path)

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    assert result["primary_event"] == "joint_substitution_event"
    assert result["decision_basis"] == "finite_registered_schedule"
    assert result["independence_verified"] is False
    assert result["schedule_integrity_passed"] is True
    assert result["registered_schedule_length"] == 24
    assert len(result["blocks"]) == 24
    assert result["controls"]["planted"]["joint_event_count"] == 18
    assert result["controls"]["planted"]["strict_subset_admitted"] is True
    assert result["controls"]["identity"]["joint_event_count"] == 6
    assert result["controls"]["identity"]["strict_subset_admitted"] is False
    assert result["controls"]["identity"]["decision"] == "descriptive_only"
    assert result["iid_conditional_reference"]["label"] == "iid_conditional_only"
    assert result["iid_conditional_reference"]["population_guarantee"] is False


def test_failed_registered_block_stays_in_denominator_and_rejects_admission(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    failed = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    failed.pop("pair_id")
    failed.update(
        status="failed",
        error_type="RuntimeError",
        error_message="registered runner failed",
    )
    progress["counts"] = {"completed": 23, "failed": 1, "preserved": 0}
    write_json(progress_path, progress)

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    assert result["registered_schedule_length"] == 24
    assert len(result["blocks"]) == 24
    assert result["controls"]["planted"]["joint_event_count"] == 17
    assert result["controls"]["planted"]["strict_subset_admitted"] is False
    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["registered_status"] == "failed"
    assert block["joint_substitution_event"] is False


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "replaced"])
def test_duplicate_missing_or_replaced_registered_blocks_are_rejected(
    tmp_path, mutation
):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    if mutation == "duplicate":
        progress["records"][1] = copy.deepcopy(progress["records"][0])
    elif mutation == "missing":
        progress["records"].pop(1)
    else:
        progress["records"][0]["replicate_id"] = "r999"
        progress["records"][0]["output_dir"] = str(
            Path(progress["records"][0]["output_dir"]).with_name("r999")
        )
        progress["records"][0]["pair_id"] = "confirmation-v3:identity:r999"
    write_json(progress_path, progress)

    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.analyze_registered_schedule(
            progress_path,
            include_historical_negative_control=False,
        )


def test_common_full_and_slice_failure_is_not_a_joint_event(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    for condition in ("F", "S"):
        update_condition_outcome(
            progress,
            control="planted",
            replicate_id="r001",
            condition=condition,
            success=False,
            score=0.0,
        )

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is True
    assert block["joint_substitution_event"] is False
    assert result["controls"]["planted"]["strict_subset_admitted"] is False


def test_slice_better_than_full_remains_joint_event_eligible(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    update_condition_outcome(
        progress,
        control="planted",
        replicate_id="r001",
        condition="F",
        success=True,
        score=61 / 64,
    )

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["joint_substitution_event"] is True
    assert result["controls"]["planted"]["strict_subset_admitted"] is True


def test_stale_stored_event_flag_is_rejected_as_an_unregistered_pair_field(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    manifest_path = Path(record["output_dir"]) / "pair_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["joint_substitution_event"] = False
    write_json(manifest_path, manifest)

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False
    assert block["joint_substitution_event"] is False
    assert result["controls"]["planted"]["strict_subset_admitted"] is False


def test_self_consistent_unregistered_condition_context_is_rejected(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    output_dir = Path(record["output_dir"])
    manifest_path = output_dir / "pair_manifest.json"
    result_path = output_dir / "S" / "run_result.json"
    unregistered = hashlib.sha256(b"self-consistent unregistered context").hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["conditions"]["S"]["context_sha256"] = unregistered
    write_json(manifest_path, manifest)
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    run_result["condition_context_sha256"] = unregistered
    write_json(result_path, run_result)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False
    assert block["joint_substitution_event"] is False


@pytest.mark.parametrize("mutation", ["case_id", "public_summary"])
def test_private_metric_matches_registered_cases_and_derived_summary(
    tmp_path, mutation
):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    result_path = Path(record["output_dir"]) / "S" / "run_result.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    metric = run_result["scorer_metrics"][0]
    if mutation == "case_id":
        metric["case_details"][0]["case_id"] = "unregistered-case"
    else:
        metric["public_summary"]["passed_cases"] = 0
    write_json(result_path, run_result)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False


def test_stored_condition_path_with_parent_traversal_is_rejected(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = progress["records"][0]
    output_dir = Path(record["output_dir"])
    manifest_path = output_dir / "pair_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result_path = output_dir / "S" / "run_result.json"
    manifest["results"]["S"]["run_result_path"] = str(
        result_path.parent / ".." / "S" / "run_result.json"
    )
    write_json(manifest_path, manifest)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = result["blocks"][0]
    assert block["integrity_passed"] is False


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_authoritative_run_result_fields_fail_closed(tmp_path, mutation):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    result_path = Path(record["output_dir"]) / "S" / "run_result.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    if mutation == "extra":
        run_result["secret_provider_debug"] = "must-never-appear"
    else:
        run_result.pop("elapsed_seconds")
    write_json(result_path, run_result)

    result = analyzer.analyze_registered_schedule(
        progress_path,
        include_historical_negative_control=False,
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False
    assert block["joint_substitution_event"] is False
    assert result["controls"]["planted"]["strict_subset_admitted"] is False
    assert "must-never-appear" not in json.dumps(result)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("submitted", 1),
        ("input_tokens", True),
        ("transport_attempts", 1.0),
        ("elapsed_seconds", math.inf),
    ],
)
def test_run_result_scalars_use_strict_bool_int_and_finite_types(
    tmp_path, field, bad_value
):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    result_path = Path(record["output_dir"]) / "S" / "run_result.json"
    manifest_path = Path(record["output_dir"]) / "pair_manifest.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_result[field] = bad_value
    if field in manifest["results"]["S"]:
        manifest["results"]["S"][field] = bad_value
    write_json(result_path, run_result)
    write_json(manifest_path, manifest)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [("success", 1), ("contract_passed", 1), ("case_scores", [True] + [1] * 63)],
)
def test_private_metric_uses_strict_bool_and_binary_integer_types(
    tmp_path, field, bad_value
):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    result_path = Path(record["output_dir"]) / "S" / "run_result.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    run_result["scorer_metrics"][0][field] = bad_value
    write_json(result_path, run_result)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False


def test_successful_metric_requires_an_applied_patch_and_registered_details():
    metric = score_metric(success=True, score=1.0)
    metric["patch_applied"] = False
    metric["case_details"] = []

    with pytest.raises(analyzer.AnalysisInputError):
        analyzer._audit_metric(
            metric,
            expected_case_ids=[f"case-{index:03d}" for index in range(1, 65)],
        )


def test_no_patch_failure_is_a_valid_fail_closed_metric_shape():
    metric = score_metric(success=False, score=0.0)
    metric.update(
        patch_applied=False,
        contract_passed=False,
        case_details=[],
        failure_reason="patch_apply_failed",
        private_apply_result={"returncode": 1, "stdout": "", "stderr": "failed"},
    )
    metric["public_summary"].update(
        contract_passed=False,
        failure_reason="patch_apply_failed",
    )

    assert analyzer._audit_metric(
        metric,
        expected_case_ids=[f"case-{index:03d}" for index in range(1, 65)],
    ) == (False, 0.0, False)


@pytest.mark.parametrize(
    "mutation", ["failure_reason", "contract_failure", "zero_returncode"]
)
def test_no_patch_failure_rejects_non_scorer_shapes(mutation):
    metric = score_metric(success=False, score=0.0)
    metric.update(
        patch_applied=False,
        contract_passed=False,
        case_details=[],
        failure_reason="patch_apply_failed",
        private_apply_result={"returncode": 1, "stdout": "", "stderr": "failed"},
    )
    metric["public_summary"].update(
        contract_passed=False,
        failure_reason="patch_apply_failed",
    )
    if mutation == "failure_reason":
        metric["failure_reason"] = "numerical_case_failed"
        metric["public_summary"]["failure_reason"] = "numerical_case_failed"
    elif mutation == "contract_failure":
        metric["contract_failures"] = ["unexpected"]
    else:
        metric["private_apply_result"]["returncode"] = 0

    with pytest.raises(analyzer.AnalysisInputError):
        analyzer._audit_metric(
            metric,
            expected_case_ids=[f"case-{index:03d}" for index in range(1, 65)],
        )


def test_common_scaffold_and_response_ids_match_across_registered_schedule(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    first, second = [
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] in {"r001", "r002"}
    ]
    first_result = json.loads(
        (Path(first["output_dir"]) / "S" / "run_result.json").read_text(
            encoding="utf-8"
        )
    )
    second_result_path = Path(second["output_dir"]) / "S" / "run_result.json"
    second_result = json.loads(second_result_path.read_text(encoding="utf-8"))
    second_result["common_scaffold_sha256"] = SHA["selected"]
    second_result["turns"][0]["provider_response_id"] = first_result["turns"][0][
        "provider_response_id"
    ]
    write_json(second_result_path, second_result)
    transcript_path = Path(second["output_dir"]) / "S" / "transcript.json"
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    transcript["turns"] = second_result["turns"]
    write_json(transcript_path, transcript)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r002"
    )
    assert block["integrity_passed"] is False


def test_action_budget_final_score_has_zero_post_score_model_turns(tmp_path):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    output_dir = Path(record["output_dir"])
    result_path = output_dir / "B" / "run_result.json"
    transcript_path = output_dir / "B" / "transcript.json"
    manifest_path = output_dir / "pair_manifest.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    run_result["terminal_reason"] = "action_budget_exhausted_after_final_score"
    run_result["submitted"] = False
    run_result["turns"][-1]["action"]["action"] = "edit"
    run_result["turns"][-1]["observation_status"] = "ok"
    write_json(result_path, run_result)
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    transcript["turns"] = run_result["turns"]
    write_json(transcript_path, transcript)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["results"]["B"]["terminal_reason"] = run_result["terminal_reason"]
    manifest["results"]["B"]["submitted"] = False
    write_json(manifest_path, manifest)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )

    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is True
    assert block["joint_substitution_event"] is True


@pytest.mark.parametrize(
    ("object_name", "mutation"),
    [
        ("family", "extra"),
        ("family", "missing"),
        ("pair", "extra"),
        ("pair", "missing"),
    ],
)
def test_authoritative_v3_top_level_fields_are_exact(
    tmp_path, object_name, mutation
):
    progress_path, progress, families = write_complete_schedule(tmp_path)
    if object_name == "family":
        family_path = families["planted"]
        payload = json.loads(family_path.read_text(encoding="utf-8"))
        if mutation == "extra":
            payload["unregistered_field"] = "must be rejected"
        else:
            payload.pop("workspace_path")
        write_json(family_path, payload)
        family_sha256 = sha256_file(family_path)
        for record in progress["records"]:
            if record["control"] == "planted":
                record["family_sha256"] = family_sha256
        write_json(progress_path, progress)

        with pytest.raises(analyzer.AnalysisInputError):
            analyzer.analyze_registered_schedule(
                progress_path, include_historical_negative_control=False
            )
        return

    record = next(
        row
        for row in progress["records"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    manifest_path = Path(record["output_dir"]) / "pair_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if mutation == "extra":
        manifest["unregistered_field"] = "must be rejected"
    else:
        manifest.pop("retry_lineage")
    write_json(manifest_path, manifest)

    result = analyzer.analyze_registered_schedule(
        progress_path, include_historical_negative_control=False
    )
    block = next(
        row
        for row in result["blocks"]
        if row["control"] == "planted" and row["replicate_id"] == "r001"
    )
    assert block["integrity_passed"] is False


def write_v2_negative_control(root: Path) -> Path:
    registry_path = root / "case_registry_v2.json"
    write_json(registry_path, v2_case_registry_payload())
    registry_sha256 = sha256_file(registry_path)
    family_path, family_sha256, bindings, workspace = write_v2_family_bundle(
        root, registry_path
    )
    records = []
    for index in range(1, 19):
        replicate_id = f"r{index:03d}"
        output_dir = root / "toolformer_filter" / replicate_id
        pair_id = f"toolformer_filter:confirmation-v2:{replicate_id}"
        summaries = {}
        outcomes = {
            "B": (False, 0.0),
            "F": (True, 1.0),
            "S": (index <= 6, 1.0 if index <= 6 else 0.0),
        }
        for condition, (success, score) in outcomes.items():
            result, _, summary, _ = condition_result(
                pair_id=pair_id,
                condition=condition,
                context_sha256=SHA["prompt-text"],
                success=success,
                score=score,
            )
            result["scorer_metrics"][0]["block"] = "confirmation_v2"
            result_path = output_dir / condition / "run_result.json"
            write_json(result_path, result)
            summary["run_result_path"] = result_path.as_posix()
            summaries[condition] = summary
        write_json(
            output_dir / "pair_manifest.json",
            {
                "schema_version": "effectslice-toolformer-filter-pair.v2",
                "provider_protocol_version": "effectslice-deepseek-final-only.v3",
                "evidence_boundary": "registered_final_only_confirmation",
                "pair_id": pair_id,
                "task_id": "TOOLFORMER-FILTER",
                "action_budget_visible_to_model": True,
                "atom_map_sha256": bindings["source_map"]["sha256"],
                "authorization_evidence": "synthetic trusted endpoint",
                "model_alias": "deepseek-v4-flash",
                "model_family": "DeepSeek-family",
                "wire_api": "openai_chat_completions",
                "case_block": "confirmation_v2",
                "comparison_role": "development_triage",
                "slice_candidate_id": "prefix_01",
                "confirmation_case_count": 64,
                "private_score_policy": "final_only",
                "common_scaffold_sha256": SHA["common-scaffold"],
                "condition_execution_order": ["B", "F", "S"],
                "conditions": {condition: {} for condition in ("B", "F", "S")},
                "confirmation_family_path": family_path.resolve().as_posix(),
                "confirmation_family_sha256": family_sha256,
                "confirmation_hypothesis_ids": ["synthetic-joint-event"],
                "full_artifact_sha256": bindings["full_artifact"]["sha256"],
                "harness_protocol_version": "effectslice-toolformer-filter-aci.v3",
                "maximum_transport_attempts": 5,
                "provider_config": {},
                "retained_atom_ids": ["T01"],
                "retained_scc_count": 1,
                "same_aci_scaffold": True,
                "scorer_sha256": bindings["scorer"]["sha256"],
                "seed_block_id": f"confirmation-v2:toolformer_filter:{replicate_id}",
                "slice_artifact_path": bindings["selected_artifact"]["path"],
                "slice_artifact_sha256": bindings["selected_artifact"]["sha256"],
                "slice_registry_path": bindings["slice_registry"]["path"],
                "slice_registry_sha256": bindings["slice_registry"]["sha256"],
                "task_prompt_sha256": hashlib.sha256(
                    TASK_PROMPT_BYTES.decode("utf-8").strip().encode("utf-8")
                ).hexdigest(),
                "workspace_state": workspace,
                "case_registry_sha256": registry_sha256,
                "verified_family_inputs": bindings,
                "results": summaries,
            },
        )
        records.append(
            {
                "task_key": "toolformer_filter",
                "replicate_id": replicate_id,
                "status": "completed",
                "output_dir": output_dir.as_posix(),
                "pair_id": pair_id,
            }
        )
    progress_path = root / "confirmation_v2_progress.json"
    write_json(
        progress_path,
        {
            "schema_version": "effectslice-confirmation-v2-progress.v1",
            "counts": {"completed": 18, "failed": 0, "preserved": 0},
            "records": records,
        },
    )
    return progress_path


def rebind_v2_registry(
    progress_path: Path,
    registry_path: Path,
    *,
    replicate_id: str | None = None,
    rebind_family: bool = False,
) -> str:
    digest = sha256_file(registry_path)
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    alternate_family_path = registry_path.with_name(
        f"{registry_path.stem}_family.json"
    )
    alternate_family_digest = None
    for record in progress["records"]:
        if record.get("task_key") != "toolformer_filter":
            continue
        if replicate_id is not None and record["replicate_id"] != replicate_id:
            continue
        manifest_path = Path(record["output_dir"]) / "pair_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["case_registry_sha256"] = digest
        manifest["verified_family_inputs"]["case_registry"] = {
            "path": registry_path.resolve().as_posix(),
            "sha256": digest,
        }
        if rebind_family:
            if alternate_family_digest is None:
                family = json.loads(
                    Path(manifest["confirmation_family_path"]).read_text(
                        encoding="utf-8"
                    )
                )
                family["case_registry_sha256"] = digest
                write_json(alternate_family_path, family)
                alternate_family_digest = sha256_file(alternate_family_path)
            manifest["confirmation_family_path"] = (
                alternate_family_path.resolve().as_posix()
            )
            manifest["confirmation_family_sha256"] = alternate_family_digest
        write_json(manifest_path, manifest)
    return digest


def test_v2_negative_control_and_rule_comparison_are_reanalyzed_from_raw(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "v3")
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")

    result = analyzer.analyze_registered_schedule(
        progress_path,
        historical_v2_progress_path=v2_progress_path,
    )

    negative = result["historical_negative_control"]
    assert negative["source"] == "existing_v2_final_toolformer_prefix_01"
    assert negative["registered_block_count"] == 18
    assert negative["joint_event_count"] == 6
    assert negative["decision"] == "reject"
    assert negative["strict_subset_admitted"] is False
    assert result["strict_subset_admitted"] is True
    assert list(result["rule_comparison"]) == [
        "development_selection_only",
        "adaptive_case_level",
        "registered_joint_schedule",
    ]
    assert result["rule_comparison"]["adaptive_case_level"] == {
        "status": "invalid",
        "contaminated": True,
        "included_in_confirmation": False,
    }
    assert result["rule_comparison"]["registered_joint_schedule"]["decision"] == "pass"


def test_invalid_v2_negative_control_cannot_make_registered_rule_pass(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "v3")
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    v2_progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    first = v2_progress["records"][0]
    result_path = Path(first["output_dir"]) / "S" / "run_result.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    run_result["scorer_metrics"][0]["case_scores"][0] = True
    write_json(result_path, run_result)

    result = analyzer.analyze_registered_schedule(
        progress_path,
        historical_v2_progress_path=v2_progress_path,
    )

    negative = result["historical_negative_control"]
    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"
    assert negative["strict_subset_admitted"] is False
    assert result["rule_comparison"]["registered_joint_schedule"]["decision"] == "fail"


def test_v2_reanalysis_rejects_case_ids_outside_the_bound_registry(tmp_path):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    v2_progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    first = v2_progress["records"][0]
    result_path = Path(first["output_dir"]) / "S" / "run_result.json"
    run_result = json.loads(result_path.read_text(encoding="utf-8"))
    for index, detail in enumerate(
        run_result["scorer_metrics"][0]["case_details"], start=1
    ):
        detail["case_id"] = f"replacement-{index:03d}"
    write_json(result_path, run_result)

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["registered_block_count"] == 18
    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_v2_pair_manifest_top_level_fields_are_exact(tmp_path, mutation):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    v2_progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    first = v2_progress["records"][0]
    manifest_path = Path(first["output_dir"]) / "pair_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if mutation == "extra":
        manifest["unregistered_field"] = "must be rejected"
    else:
        manifest.pop("authorization_evidence")
    write_json(manifest_path, manifest)

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["registered_block_count"] == 18
    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


@pytest.mark.parametrize("mutation", ["missing", "digest", "binding"])
def test_v2_confirmation_family_is_read_hashed_and_cross_bound(tmp_path, mutation):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    v2_progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    manifests = [
        Path(record["output_dir"]) / "pair_manifest.json"
        for record in v2_progress["records"]
        if record["task_key"] == "toolformer_filter"
    ]
    first_manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    family_path = Path(first_manifest["confirmation_family_path"])

    if mutation == "missing":
        family_path.unlink()
    else:
        family = json.loads(family_path.read_text(encoding="utf-8"))
        if mutation == "digest":
            family["evidence_boundary"] = "mutated after registration"
        else:
            family["case_registry_sha256"] = hashlib.sha256(
                b"different registry"
            ).hexdigest()
        write_json(family_path, family)
        if mutation == "binding":
            family_sha256 = sha256_file(family_path)
            for manifest_path in manifests:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["confirmation_family_sha256"] = family_sha256
                write_json(manifest_path, manifest)

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["registered_block_count"] == 18
    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


def test_v2_workspace_state_is_recomputed_from_registered_files(tmp_path):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    manifest_path = Path(progress["records"][0]["output_dir"]) / "pair_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    workspace = Path(manifest["workspace_state"]["workspace"])
    (workspace / "README.md").write_text(
        "mutated after registration\n", encoding="utf-8"
    )

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


@pytest.mark.parametrize("bad_output_dir", [None, 7, {}, "relative/r001"])
def test_v2_output_directory_type_and_absolute_path_fail_closed(
    tmp_path, bad_output_dir
):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    progress["records"][0]["output_dir"] = bad_output_dir
    write_json(v2_progress_path, progress)

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


def test_write_analysis_rejects_relative_v2_output_directory(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "v3")
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    progress = json.loads(v2_progress_path.read_text(encoding="utf-8"))
    progress["records"][0]["output_dir"] = "relative/r001"
    write_json(v2_progress_path, progress)

    with pytest.raises(analyzer.AnalysisInputError, match="absolute"):
        analyzer.write_analysis(
            progress_path,
            tmp_path / "derived" / "analysis.json",
            historical_v2_progress_path=v2_progress_path,
            derived_root=tmp_path / "derived",
        )


@pytest.mark.parametrize("relationship", ["equal", "ancestor", "descendant"])
def test_write_analysis_protects_transitive_v2_registry_paths(tmp_path, relationship):
    progress_path, _, _ = write_complete_schedule(tmp_path / "v3")
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    derived_root = tmp_path / "derived"
    registry_path = derived_root / "registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    original_registry = Path(
        json.loads(v2_progress_path.read_text(encoding="utf-8"))["records"][0][
            "output_dir"
        ]
    ).parent.parent / "case_registry_v2.json"
    shutil.copyfile(original_registry, registry_path)
    rebind_v2_registry(v2_progress_path, registry_path, rebind_family=True)

    if relationship == "equal":
        output_path = registry_path
    elif relationship == "ancestor":
        output_path = derived_root / "analysis.json"
    elif relationship == "descendant":
        output_path = registry_path / "nested" / "analysis.json"
        derived_root = output_path.parents[1]
    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.write_analysis(
            progress_path,
            output_path,
            historical_v2_progress_path=v2_progress_path,
            derived_root=derived_root,
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows junction semantics")
def test_write_analysis_rejects_real_windows_junction_alias(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "v3")
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    raw_root = tmp_path / "registered_raw"
    raw_root.mkdir()
    registry_path = raw_root / "registry.json"
    original_registry = tmp_path / "v2" / "case_registry_v2.json"
    shutil.copyfile(original_registry, registry_path)
    rebind_v2_registry(v2_progress_path, registry_path, rebind_family=True)
    junction_root = tmp_path / "derived_junction"
    created = subprocess.run(
        [
            "cmd.exe",
            "/d",
            "/c",
            "mklink",
            "/J",
            str(junction_root),
            str(raw_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip(f"junction creation unavailable: {created.stderr.strip()}")
    try:
        assert junction_root != raw_root
        assert junction_root.resolve() == raw_root.resolve()
        assert os.path.samefile(junction_root, raw_root)
        with pytest.raises(analyzer.AnalysisInputError):
            analyzer.write_analysis(
                progress_path,
                junction_root / "analysis.json",
                historical_v2_progress_path=v2_progress_path,
                derived_root=junction_root,
            )
    finally:
        junction_root.rmdir()


def test_v2_schedule_rejects_mixed_complete_registry_identity(tmp_path):
    v2_progress_path = write_v2_negative_control(tmp_path / "v2")
    alternate_registry = tmp_path / "alternate_registry.json"
    alternate = v2_case_registry_payload()
    alternate["evidence_boundary"] = "synthetic alternate frozen private cases"
    write_json(alternate_registry, alternate)
    rebind_v2_registry(
        v2_progress_path,
        alternate_registry,
        replicate_id="r002",
        rebind_family=True,
    )

    negative = analyzer.reanalyze_v2_negative_control(v2_progress_path)

    assert negative["registered_block_count"] == 18
    assert negative["full_integrity_passed"] is False
    assert negative["decision"] == "invalid"


def test_write_analysis_is_deterministic_derived_only_and_preserves_raw(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "inputs")
    derived_root = tmp_path / "derived" / "confirmation_v3"
    output_path = derived_root / "analysis.json"
    raw_before = progress_path.read_bytes()

    analyzer.write_analysis(
        progress_path,
        output_path,
        include_historical_negative_control=False,
        derived_root=derived_root,
    )
    first = output_path.read_bytes()
    analyzer.write_analysis(
        progress_path,
        output_path,
        include_historical_negative_control=False,
        derived_root=derived_root,
    )

    assert output_path.read_bytes() == first
    assert progress_path.read_bytes() == raw_before
    assert first.endswith(b"\n")
    assert b"secret" not in first.lower()
    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.write_analysis(
            progress_path,
            progress_path,
            include_historical_negative_control=False,
            derived_root=derived_root,
        )
    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.write_analysis(
            progress_path,
            tmp_path / "escaped.json",
            include_historical_negative_control=False,
            derived_root=derived_root,
        )
    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.write_analysis(
            progress_path,
            derived_root / ".." / "escaped.json",
            include_historical_negative_control=False,
            derived_root=derived_root,
        )


def test_json_inputs_have_a_bounded_size(tmp_path, monkeypatch):
    oversized = tmp_path / "oversized.json"
    write_json(oversized, {"payload": "x" * 128})
    monkeypatch.setattr(analyzer, "MAX_JSON_BYTES", 64, raising=False)

    with pytest.raises(analyzer.AnalysisInputError, match="size limit"):
        analyzer._json_object(oversized, "oversized input")


def test_validated_payload_cache_rechecks_file_signature(tmp_path):
    registered = tmp_path / "registered.json"
    registered.write_bytes(b'{"value":1}\n')
    digest = sha256_file(registered)

    assert analyzer._snapshot_bytes(registered, digest, "registered input")
    registered.write_bytes(b'{"value":200}\n')

    with pytest.raises(analyzer.AnalysisInputError, match="digest mismatch"):
        analyzer._snapshot_bytes(registered, digest, "registered input")


def test_write_analysis_honors_existing_cooperative_root_lock(tmp_path):
    progress_path, _, _ = write_complete_schedule(tmp_path / "inputs")
    derived_root = tmp_path / "derived" / "confirmation_v3"
    derived_root.mkdir(parents=True)
    lock_path = derived_root / ".effectslice-analysis.lock"
    lock_path.write_text("another cooperative writer\n", encoding="utf-8")
    output_path = derived_root / "analysis.json"

    with pytest.raises(analyzer.AnalysisInputError, match="locked"):
        analyzer.write_analysis(
            progress_path,
            output_path,
            include_historical_negative_control=False,
            derived_root=derived_root,
        )

    assert lock_path.read_text(encoding="utf-8") == "another cooperative writer\n"
    assert not output_path.exists()


def test_write_analysis_revalidates_destination_parent_identity(
    tmp_path, monkeypatch
):
    progress_path, _, _ = write_complete_schedule(tmp_path / "inputs")
    derived_root = tmp_path / "derived" / "confirmation_v3"
    output_path = derived_root / "analysis.json"
    identities = iter([(1, 1), (2, 2)])
    monkeypatch.setattr(
        analyzer,
        "_path_identity",
        lambda path, label: next(identities),
        raising=False,
    )

    with pytest.raises(analyzer.AnalysisInputError, match="changed"):
        analyzer.write_analysis(
            progress_path,
            output_path,
            include_historical_negative_control=False,
            derived_root=derived_root,
        )

    assert not output_path.exists()
    assert not (derived_root / ".effectslice-analysis.lock").exists()


def test_write_analysis_cannot_overwrite_transitive_raw_input(tmp_path):
    progress_path, progress, _ = write_complete_schedule(
        tmp_path / "derived" / "raw_input"
    )
    raw_result = Path(progress["records"][0]["output_dir"]) / "S" / "run_result.json"
    before = raw_result.read_bytes()

    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.write_analysis(
            progress_path,
            raw_result,
            include_historical_negative_control=False,
            derived_root=tmp_path / "derived",
        )

    assert raw_result.read_bytes() == before


@pytest.mark.parametrize("mutation", ["bool_count", "invalid_error"])
def test_progress_counts_and_failure_metadata_use_strict_types(tmp_path, mutation):
    progress_path, progress, _ = write_complete_schedule(tmp_path)
    failed = progress["records"][0]
    failed.pop("pair_id")
    failed.update(
        status="failed",
        error_type="RuntimeError",
        error_message="registered runner failed",
    )
    progress["counts"] = {"completed": 23, "failed": 1, "preserved": 0}
    if mutation == "bool_count":
        progress["counts"]["failed"] = True
    else:
        failed["error_type"] = 1
    write_json(progress_path, progress)

    with pytest.raises(analyzer.AnalysisInputError):
        analyzer.analyze_registered_schedule(
            progress_path, include_historical_negative_control=False
        )
