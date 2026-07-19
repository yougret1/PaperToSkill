from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


RUN_ROOT = Path(__file__).resolve().parent
PREREGISTRATION_PATH = RUN_ROOT / "artifacts" / "confirmation_v4" / "preregistration.json"
DEFAULT_OUTPUT_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v4"
DEFAULT_PROGRESS_PATH = DEFAULT_OUTPUT_ROOT / "confirmation_v4_progress.json"
DEFAULT_ANALYSIS_PATH = RUN_ROOT / "derived" / "confirmation_v4" / "analysis.json"
EVIDENCE_BOUNDARY = "registered_public_test_finite_schedule_confirmation_v4"
CONDITIONS = ("B", "F", "S")


import sys

sys.path.insert(0, str(RUN_ROOT / "src"))

from build_confirmation_v4 import (  # noqa: E402
    finite_schedule_decision,
    identity_instrumentation_decision,
)
from effectslice.evidence_binding import validate_file_bindings  # noqa: E402
from run_confirmation_v4 import (  # noqa: E402
    PROGRESS_SCHEMA,
    _atomic_write_json,
    _base_record,
    _load_json,
    _load_prior_records,
    _resolve_registered,
    _sha256_file,
    load_and_verify_registration,
)
from run_snap_mfse_effectslice import build_snap_context  # noqa: E402
from run_swe_effectslice import workspace_tree_digest  # noqa: E402
from run_toolformer_filter_effectslice import build_toolformer_context  # noqa: E402


class AnalysisInputError(ValueError):
    """A registered V4 evidence artifact failed deterministic audit."""


def _require_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise AnalysisInputError(f"{label} must be a bool")
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AnalysisInputError(f"{label} must be a nonnegative integer")
    return value


def _require_score(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AnalysisInputError(f"{label} must be numeric")
    converted = float(value)
    if not math.isfinite(converted) or not 0.0 <= converted <= 1.0:
        raise AnalysisInputError(f"{label} must be finite and in [0, 1]")
    return converted


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expected_case_ids(family: Mapping[str, Any]) -> list[str]:
    registry_path = _resolve_registered(
        family.get("case_registry_path"), "case registry"
    )
    registry = _load_json(registry_path, "case registry")
    cases = registry.get("blocks", {}).get("confirmation_v4")
    if not isinstance(cases, list) or len(cases) != 64:
        raise AnalysisInputError("registered V4 case block must contain 64 cases")
    case_ids = [case.get("case_id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        raise AnalysisInputError("registered V4 case IDs must be nonempty strings")
    if len(set(case_ids)) != 64:
        raise AnalysisInputError("registered V4 case IDs must be unique")
    return case_ids


def _audit_metric(
    metric: Mapping[str, Any],
    *,
    family: Mapping[str, Any],
    expected_case_ids: list[str],
) -> dict[str, Any]:
    if not isinstance(metric, Mapping):
        raise AnalysisInputError("private scorer metric must be an object")
    if metric.get("task_id") != family["task_id"]:
        raise AnalysisInputError("private scorer task ID changed")
    if metric.get("block") != "confirmation_v4":
        raise AnalysisInputError("private scorer block changed")
    score = _require_score(metric.get("task_score"), "private task score")
    exact_success = _require_bool(metric.get("success"), "private exact success")
    patch_applied = _require_bool(metric.get("patch_applied"), "patch applied")
    contract_passed = _require_bool(
        metric.get("contract_passed"), "hard contract passed"
    )
    case_scores = metric.get("case_scores")
    if (
        not isinstance(case_scores, list)
        or len(case_scores) != 64
        or any(type(value) is not int or value not in {0, 1} for value in case_scores)
    ):
        raise AnalysisInputError("private scorer must contain 64 binary case scores")
    expected_score = sum(case_scores) / 64 if contract_passed else 0.0
    if not math.isclose(score, expected_score, rel_tol=0.0, abs_tol=1e-12):
        raise AnalysisInputError("private task score does not match registered cases")
    if exact_success != bool(contract_passed and all(case_scores)):
        raise AnalysisInputError("private exact success does not match scorer cases")
    details = metric.get("case_details")
    if not isinstance(details, list):
        raise AnalysisInputError("private case details must be a list")
    if details:
        detail_ids = [detail.get("case_id") for detail in details if isinstance(detail, dict)]
        if len(details) != 64 or detail_ids != expected_case_ids:
            raise AnalysisInputError("private case details do not match registration")
        for detail, case_score in zip(details, case_scores):
            if _require_bool(detail.get("passed"), "private case passed") != bool(
                case_score
            ):
                raise AnalysisInputError("private case detail disagrees with case score")
    elif any(case_scores):
        raise AnalysisInputError("nonzero private cases require complete case details")
    operational_success = bool(
        patch_applied
        and contract_passed
        and score >= float(family["run_success_threshold"])
    )
    return {
        "task_score": score,
        "private_exact_success": exact_success,
        "operational_success": operational_success,
        "patch_applied": patch_applied,
        "hard_contract_passed": contract_passed,
        "passed_cases": sum(case_scores),
    }


def _audit_condition(
    *,
    condition: str,
    condition_dir: Path,
    family: Mapping[str, Any],
    manifest: Mapping[str, Any],
    public_result: Mapping[str, Any],
    expected_case_ids: list[str],
    expected_context_sha256: str,
    provider_response_ids: set[str],
) -> dict[str, Any]:
    run_result_path = condition_dir / "run_result.json"
    transcript_path = condition_dir / "transcript.json"
    run_result = _load_json(run_result_path, "run result")
    transcript = _load_json(transcript_path, "transcript")
    patch_path = condition_dir / "candidate.patch"
    if patch_path.is_symlink() or not patch_path.is_file():
        raise AnalysisInputError("candidate patch is missing or unsafe")
    patch_text = patch_path.read_text(encoding="utf-8")
    if run_result.get("diff_text") != patch_text:
        raise AnalysisInputError("candidate patch differs from serialized run result")
    if public_result.get("candidate_patch_sha256") != _sha256_text(patch_text):
        raise AnalysisInputError("candidate patch digest differs from pair manifest")
    scalar_fields = (
        "status",
        "terminal_reason",
        "submitted",
        "task_score",
        "success",
        "input_tokens",
        "output_tokens",
        "transport_attempts",
        "elapsed_seconds",
        "private_score_policy",
        "private_score_count",
        "private_feedback_exposed",
    )
    for field in scalar_fields:
        if public_result.get(field) != run_result.get(field):
            raise AnalysisInputError(f"public condition result differs on {field}")
    if run_result.get("private_score_policy") != "final_only":
        raise AnalysisInputError("condition did not use final-only private scoring")
    if run_result.get("private_score_count") != 1:
        raise AnalysisInputError("condition must invoke the private scorer exactly once")
    if run_result.get("private_feedback_exposed") is not False:
        raise AnalysisInputError("condition exposed private scorer feedback")
    metrics = run_result.get("scorer_metrics")
    if not isinstance(metrics, list) or len(metrics) != 1:
        raise AnalysisInputError("condition must contain one private scorer metric")
    metric = _audit_metric(
        metrics[0], family=family, expected_case_ids=expected_case_ids
    )
    if not math.isclose(
        metric["task_score"],
        _require_score(run_result.get("task_score"), "run task score"),
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise AnalysisInputError("run task score differs from private scorer")
    if run_result.get("success") != metric["private_exact_success"]:
        raise AnalysisInputError("run exact success differs from private scorer")
    turns = run_result.get("turns")
    if not isinstance(turns, list) or not turns:
        raise AnalysisInputError("condition transcript must contain provider turns")
    if transcript.get("condition") != condition or transcript.get("turns") != turns:
        raise AnalysisInputError("condition transcript differs from run result")
    if transcript.get("evidence_boundary") != EVIDENCE_BOUNDARY:
        raise AnalysisInputError("condition transcript evidence boundary changed")
    public_tests = 0
    public_test_passes = 0
    action_counts: Counter[str] = Counter()
    scored_turn_indexes: list[int] = []
    for index, turn in enumerate(turns):
        if not isinstance(turn, dict):
            raise AnalysisInputError("provider turn must be an object")
        action = turn.get("action")
        action_name = action.get("action") if isinstance(action, dict) else "invalid"
        action_counts[action_name] += 1
        response_id = turn.get("provider_response_id")
        if not isinstance(response_id, str) or not response_id:
            raise AnalysisInputError("provider response ID must be nonempty")
        if response_id in provider_response_ids:
            raise AnalysisInputError("provider response ID is duplicated")
        provider_response_ids.add(response_id)
        if turn.get("provider_model_id") != family["model_alias"]:
            raise AnalysisInputError("provider model ID differs from registration")
        _require_nonnegative_int(turn.get("transport_attempts"), "turn transport attempts")
        _require_nonnegative_int(turn.get("input_tokens"), "turn input tokens")
        _require_nonnegative_int(turn.get("output_tokens"), "turn output tokens")
        status = turn.get("observation_status")
        if action_name == "test":
            public_tests += 1
            if status != "public_tested":
                raise AnalysisInputError(
                    "test action did not use the locked public-test channel"
                )
            message = turn.get("observation_message")
            if not isinstance(message, str):
                raise AnalysisInputError("public-test feedback must be a string")
            if "passed" in message and "failed" not in message:
                public_test_passes += 1
        if status == "scored":
            scored_turn_indexes.append(index)
            if action_name != "submit":
                raise AnalysisInputError("nonterminal action accessed private scoring")
    if scored_turn_indexes and scored_turn_indexes != [len(turns) - 1]:
        raise AnalysisInputError("private score was not terminal in the conversation")
    state = run_result.get("state")
    if not isinstance(state, dict) or state.get("max_actions") != 16:
        raise AnalysisInputError("condition action budget changed")
    observations = state.get("observations")
    if not isinstance(observations, list) or len(observations) != len(turns):
        raise AnalysisInputError("ACI state and transcript length differ")
    manifest_condition = manifest.get("conditions", {}).get(condition)
    if not isinstance(manifest_condition, dict):
        raise AnalysisInputError("pair manifest condition binding is missing")
    if manifest_condition.get("context_sha256") != expected_context_sha256:
        raise AnalysisInputError("pair manifest condition context is not reproducible")
    if run_result.get("condition_context_sha256") != expected_context_sha256:
        raise AnalysisInputError("condition context digest differs from manifest")
    if run_result.get("task_prompt_sha256") != manifest.get("task_prompt_sha256"):
        raise AnalysisInputError("task prompt digest differs from manifest")
    input_tokens = _require_nonnegative_int(
        run_result.get("input_tokens"), "condition input tokens"
    )
    output_tokens = _require_nonnegative_int(
        run_result.get("output_tokens"), "condition output tokens"
    )
    transport_attempts = _require_nonnegative_int(
        run_result.get("transport_attempts"), "condition transport attempts"
    )
    elapsed = run_result.get("elapsed_seconds")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or elapsed < 0:
        raise AnalysisInputError("condition elapsed seconds must be nonnegative")
    return {
        **metric,
        "status": run_result.get("status"),
        "terminal_reason": run_result.get("terminal_reason"),
        "submitted": _require_bool(run_result.get("submitted"), "submitted"),
        "actions_used": len(turns),
        "action_counts": dict(action_counts),
        "public_test_requests": public_tests,
        "public_test_passes": public_test_passes,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "transport_attempts": transport_attempts,
        "elapsed_seconds": float(elapsed),
        "common_scaffold_sha256": run_result.get("common_scaffold_sha256"),
        "evidence_file_sha256": {
            "run_result.json": _sha256_file(run_result_path),
            "transcript.json": _sha256_file(transcript_path),
            "candidate.patch": _sha256_file(patch_path),
        },
    }


def _audit_block(
    *,
    base: Mapping[str, Any],
    family: Mapping[str, Any],
    provider_response_ids: set[str],
) -> dict[str, Any]:
    output_dir = Path(base["output_dir"])
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise AnalysisInputError("registered block output is missing or unsafe")
    manifest_path = output_dir / "pair_manifest.json"
    report_path = output_dir / "run_report.json"
    manifest = _load_json(manifest_path, "pair manifest")
    report = _load_json(report_path, "run report")
    pair_id = f"confirmation-v4:{base['family_key']}:{base['replicate_id']}"
    for payload, label in ((manifest, "pair manifest"), (report, "run report")):
        if payload.get("pair_id") != pair_id:
            raise AnalysisInputError(f"{label} pair ID changed")
        if payload.get("case_block") != "confirmation_v4":
            raise AnalysisInputError(f"{label} case block changed")
        if payload.get("condition_execution_order") != base["condition_execution_order"]:
            raise AnalysisInputError(f"{label} condition execution order changed")
        if payload.get("comparison_role") != EVIDENCE_BOUNDARY:
            raise AnalysisInputError(f"{label} evidence role changed")
        if set(payload.get("results", {})) != set(CONDITIONS):
            raise AnalysisInputError(f"{label} must contain B/F/S results")
    if report.get("results") != manifest.get("results"):
        raise AnalysisInputError("run report and pair manifest results differ")
    if manifest.get("private_score_policy") != "final_only":
        raise AnalysisInputError("pair manifest did not freeze final-only scoring")
    if manifest.get("confirmation_family_sha256") != base["family_sha256"]:
        raise AnalysisInputError("pair manifest family digest changed")
    if manifest.get("confirmation_case_count") != 64:
        raise AnalysisInputError("pair manifest case count changed")
    verified = validate_file_bindings(family, root=RUN_ROOT)
    if manifest.get("verified_family_inputs") != verified:
        raise AnalysisInputError("pair manifest verified inputs changed")
    binding_fields = {
        "full_artifact_sha256": "full_artifact",
        "atom_map_sha256": "source_map",
        "case_registry_sha256": "case_registry",
        "scorer_sha256": "scorer",
        "slice_artifact_sha256": "selected_artifact",
        "slice_registry_sha256": "slice_registry",
    }
    for manifest_field, binding_name in binding_fields.items():
        if manifest.get(manifest_field) != verified[binding_name]["sha256"]:
            raise AnalysisInputError(
                f"pair manifest {manifest_field} differs from registration"
            )
    if manifest.get("retained_atom_ids") != family["retained_atom_ids"]:
        raise AnalysisInputError("pair manifest retained atoms changed")
    task_prompt = Path(verified["task_prompt"]["path"]).read_text(
        encoding="utf-8"
    ).strip()
    expected_prompt_sha256 = _sha256_text(task_prompt)
    if manifest.get("task_prompt_sha256") != expected_prompt_sha256:
        raise AnalysisInputError("pair manifest task prompt is not reproducible")
    workspace = Path(family["workspace_path"]).resolve()
    workspace_state = workspace_tree_digest(workspace)
    manifest_workspace = manifest.get("workspace_state")
    if not isinstance(manifest_workspace, dict) or manifest_workspace.get(
        "sha256"
    ) != workspace_state["sha256"]:
        raise AnalysisInputError("pair manifest workspace state changed")
    if workspace_state["sha256"] != family["workspace_tree_sha256"]:
        raise AnalysisInputError("registered workspace state changed")
    full_artifact = Path(verified["full_artifact"]["path"])
    selected_artifact = Path(verified["selected_artifact"]["path"])
    context_builder = (
        build_snap_context
        if family["task_key"] == "snap_mfse"
        else build_toolformer_context
    )
    expected_context_sha256 = {
        condition: _sha256_text(
            context_builder(
                condition,
                full_artifact_path=full_artifact,
                slice_path=selected_artifact,
            )
        )
        for condition in CONDITIONS
    }
    expected_case_ids = _expected_case_ids(family)
    results = {
        condition: _audit_condition(
            condition=condition,
            condition_dir=output_dir / condition,
            family=family,
            manifest=manifest,
            public_result=manifest["results"][condition],
            expected_case_ids=expected_case_ids,
            expected_context_sha256=expected_context_sha256[condition],
            provider_response_ids=provider_response_ids,
        )
        for condition in CONDITIONS
    }
    scaffold_digests = {
        row["common_scaffold_sha256"] for row in results.values()
    }
    if len(scaffold_digests) != 1 or None in scaffold_digests:
        raise AnalysisInputError("common scaffold differs across block conditions")
    return {
        "global_order_index": base["global_order_index"],
        "stratum": base["stratum"],
        "family_key": base["family_key"],
        "task_key": base["task_key"],
        "replicate_id": base["replicate_id"],
        "condition_execution_order": base["condition_execution_order"],
        "condition_results": results,
        "evidence_file_sha256": {
            "pair_manifest.json": _sha256_file(manifest_path),
            "run_report.json": _sha256_file(report_path),
        },
    }


def analyze_schedule(
    *,
    preregistration_path: Path,
    expected_preregistration_sha256: str,
    output_root: Path | None = None,
    progress_path: Path | None = None,
    output_path: Path | None = None,
    allow_test_input: bool = False,
) -> dict[str, Any]:
    registration, families, preregistration_sha256 = load_and_verify_registration(
        preregistration_path,
        expected_preregistration_sha256,
        allow_test_registration=allow_test_input,
    )
    registered_root = _resolve_registered(
        registration["execution"]["output_root"], "execution output root"
    )
    registered_progress = _resolve_registered(
        registration["execution"]["progress_path"], "execution progress"
    )
    root = registered_root if output_root is None else Path(output_root).resolve()
    progress_file = (
        registered_progress if progress_path is None else Path(progress_path).resolve()
    )
    analysis_path = (
        DEFAULT_ANALYSIS_PATH if output_path is None else Path(output_path).resolve()
    )
    if not allow_test_input and (
        root != registered_root
        or progress_file != registered_progress
        or analysis_path != DEFAULT_ANALYSIS_PATH.resolve()
    ):
        raise AnalysisInputError("production analysis paths are fixed")
    schedule = registration["global_interleaved_schedule"]
    expected = {
        (row["family_key"], row["replicate_id"]): _base_record(
            row, families[row["family_key"]], root
        )
        for row in schedule
    }
    progress = _load_json(progress_file, "confirmation V4 progress")
    if progress.get("schema_version") != PROGRESS_SCHEMA:
        raise AnalysisInputError("confirmation V4 progress schema changed")
    terminal = _load_prior_records(
        progress_file,
        preregistration_sha256=preregistration_sha256,
        expected=expected,
    )
    if len(terminal) != 60 or any(
        row["status"] not in {"completed", "preserved"} for row in terminal.values()
    ):
        raise AnalysisInputError("all 60 registered blocks must complete before analysis")
    if progress.get("counts", {}).get("pending") != 0 or progress.get(
        "counts", {}
    ).get("failed") != 0:
        raise AnalysisInputError("progress reports pending or failed registered blocks")
    provider_response_ids: set[str] = set()
    blocks: list[dict[str, Any]] = []
    for row in schedule:
        key = (row["family_key"], row["replicate_id"])
        base = expected[key]
        if _sha256_file(Path(base["family_path"])) != base["family_sha256"]:
            raise AnalysisInputError("registered family changed before analysis")
        blocks.append(
            _audit_block(
                base=base,
                family=families[row["family_key"]]["family"],
                provider_response_ids=provider_response_ids,
            )
        )
    family_summaries: dict[str, Any] = {}
    for family_key in sorted(families):
        rows = [row for row in blocks if row["family_key"] == family_key]
        counts = {
            condition: sum(
                row["condition_results"][condition]["operational_success"]
                for row in rows
            )
            for condition in CONDITIONS
        }
        summary: dict[str, Any] = {
            "candidate_role": families[family_key]["family"]["candidate_role"],
            "registered_blocks": len(rows),
            "operational_success_counts": counts,
            "mean_task_score": {
                condition: sum(
                    row["condition_results"][condition]["task_score"] for row in rows
                )
                / len(rows)
                for condition in CONDITIONS
            },
        }
        if family_key == "toolformer_identity":
            summary["admission_decision"] = None
            summary["identity_instrumentation"] = identity_instrumentation_decision(
                full_successes=[
                    row["condition_results"]["F"]["operational_success"]
                    for row in rows
                ],
                slice_successes=[
                    row["condition_results"]["S"]["operational_success"]
                    for row in rows
                ],
            )
        else:
            summary["admission_decision"] = finite_schedule_decision(counts)
        family_summaries[family_key] = summary
    positive_passed = family_summaries["toolformer_positive"]["admission_decision"][
        "passed"
    ]
    negative_passed = family_summaries["toolformer_negative"]["admission_decision"][
        "passed"
    ]
    identity_passed = family_summaries["toolformer_identity"][
        "identity_instrumentation"
    ]["passed"]
    all_conditions = [
        condition_result
        for block in blocks
        for condition_result in block["condition_results"].values()
    ]
    scaffold_digests = {
        row["common_scaffold_sha256"] for row in all_conditions
    }
    if len(scaffold_digests) != 1 or None in scaffold_digests:
        raise AnalysisInputError(
            "common scaffold digest differs across the registered schedule"
        )
    action_counts: Counter[str] = Counter()
    for condition_result in all_conditions:
        action_counts.update(condition_result["action_counts"])
    analysis = {
        "schema_version": "effectslice-confirmation-v4-analysis.v1",
        "analysis_status": "passed",
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "preregistration_path": Path(preregistration_path).resolve().as_posix(),
        "preregistration_sha256": preregistration_sha256,
        "progress_path": progress_file.as_posix(),
        "registered_blocks": 60,
        "registered_condition_runs": 180,
        "registered_outputs_complete": True,
        "integrity_passed": True,
        "family_summaries": family_summaries,
        "calibration": {
            "positive_control_expected_admission": True,
            "positive_control_observed_admission": positive_passed,
            "negative_control_expected_admission": False,
            "negative_control_observed_admission": negative_passed,
            "identity_instrumentation_passed": identity_passed,
            "passed": bool(positive_passed and not negative_passed and identity_passed),
        },
        "real_candidate_decisions": {
            "snap_mfse": family_summaries["snap_mfse"]["admission_decision"],
            "toolformer_filter": family_summaries["toolformer_negative"][
                "admission_decision"
            ],
        },
        "resource_summary": {
            "provider_conversations": 180,
            "provider_turns": len(provider_response_ids),
            "input_tokens": sum(row["input_tokens"] for row in all_conditions),
            "output_tokens": sum(row["output_tokens"] for row in all_conditions),
            "transport_attempts": sum(
                row["transport_attempts"] for row in all_conditions
            ),
            "actions_used": sum(row["actions_used"] for row in all_conditions),
            "action_counts": dict(sorted(action_counts.items())),
            "public_test_requests": sum(
                row["public_test_requests"] for row in all_conditions
            ),
            "public_test_passes": sum(
                row["public_test_passes"] for row in all_conditions
            ),
            "elapsed_condition_seconds": sum(
                row["elapsed_seconds"] for row in all_conditions
            ),
            "common_scaffold_sha256": next(iter(scaffold_digests)),
        },
        "terminal_reason_counts": dict(
            sorted(Counter(row["terminal_reason"] for row in all_conditions).items())
        ),
        "scope_guards": registration["scope_guards"],
        "inference_scope": (
            "Finite registered schedule only; no IID, confidence-interval, population, "
            "cross-paper, or human-benefit guarantee."
        ),
        "blocks": blocks,
    }
    _atomic_write_json(analysis_path, analysis)
    return analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit and analyze the externally anchored EffectSlice V4 schedule"
    )
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION_PATH)
    parser.add_argument(
        "--expected-preregistration-sha256",
        default=os.environ.get("EFFECTSLICE_V4_PREREGISTRATION_SHA256", ""),
    )
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--progress-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.expected_preregistration_sha256:
        raise ValueError(
            "expected preregistration SHA-256 must come from the committed external anchor"
        )
    analysis = analyze_schedule(
        preregistration_path=args.preregistration,
        expected_preregistration_sha256=args.expected_preregistration_sha256,
        output_root=args.output_root,
        progress_path=args.progress_path,
        output_path=args.output_path,
    )
    print(
        json.dumps(
            {
                "analysis_status": analysis["analysis_status"],
                "calibration_passed": analysis["calibration"]["passed"],
                "real_candidate_decisions": analysis["real_candidate_decisions"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
