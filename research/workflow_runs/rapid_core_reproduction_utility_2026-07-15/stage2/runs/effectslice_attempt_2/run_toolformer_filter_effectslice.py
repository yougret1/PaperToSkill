from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]

import sys

sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_protocol import ActionLimits  # noqa: E402
from effectslice.aci_runner import (  # noqa: E402
    DEFAULT_COMMON_SCAFFOLD,
    InteractiveACIRunner,
)
from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from effectslice.evidence_binding import (  # noqa: E402
    normalize_condition_order,
    require_new_output_dir,
    validate_file_bindings,
)
from effectslice.toolformer_filter_scorer import ToolformerFilterScorerBridge  # noqa: E402
from run_swe_effectslice import (  # noqa: E402
    PAIR_ROLE_BY_CONDITIONS,
    ProviderTransport,
    RunnerInputError,
    serialize_run_result,
    sha256_file,
    sha256_text,
    workspace_tree_digest,
    write_json,
)


NO_ARTIFACT_CONTEXT = (
    "No paper-derived method artifact is supplied for this condition. "
    "Use only the common bounded ACI contract, the locked task, and tool feedback."
)

EVIDENCE_BOUNDARY_BY_BLOCK = {
    "development": "development_only_not_confirmation",
    "eligibility": "eligibility_only_not_confirmation",
    "discovery": "discovery_only_not_confirmation",
    "confirmation": "contaminated_development",
    "confirmation_v2": "registered_final_only_confirmation",
}

FINAL_STATE_SCORING_BY_HARNESS = {
    "effectslice-toolformer-filter-aci.v1": False,
    "effectslice-toolformer-filter-aci.v2": True,
    "effectslice-toolformer-filter-aci.v3": True,
}


def evidence_boundary_for_block(case_block: str) -> str:
    try:
        return EVIDENCE_BOUNDARY_BY_BLOCK[case_block]
    except KeyError as exc:
        raise ValueError(f"unsupported TOOLFORMER-FILTER case block: {case_block}") from exc


def build_toolformer_context(
    condition: str,
    *,
    full_artifact_path: Path,
    slice_path: Path | None,
) -> str:
    if condition == "B":
        return NO_ARTIFACT_CONTEXT
    if condition == "F":
        path = Path(full_artifact_path)
    elif condition == "S":
        if slice_path is None:
            raise ValueError("S condition requires a slice artifact")
        path = Path(slice_path)
    else:
        raise ValueError(f"unsupported TOOLFORMER-FILTER condition: {condition}")
    if not path.is_file():
        raise ValueError(f"condition artifact is missing: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"condition artifact is empty: {path}")
    return text


def load_slice_binding(
    *,
    slice_path: Path,
    registry_path: Path,
    candidate_id: str,
) -> dict[str, Any]:
    artifact = Path(slice_path).resolve()
    registry_file = Path(registry_path).resolve()
    if not artifact.is_file():
        raise ValueError(f"slice artifact is missing: {artifact}")
    if not registry_file.is_file():
        raise ValueError(f"slice registry is missing: {registry_file}")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("slice candidate ID must be nonempty")
    registry = json.loads(registry_file.read_text(encoding="utf-8"))
    matches = [
        row
        for row in registry.get("candidates", [])
        if row.get("candidate_id") == candidate_id
    ]
    if len(matches) != 1:
        raise ValueError(f"slice candidate is not uniquely registered: {candidate_id}")
    candidate = matches[0]
    registered_artifact = (registry_file.parent / candidate["artifact_path"]).resolve()
    if registered_artifact != artifact:
        raise ValueError("slice path does not match the registered candidate")
    artifact_sha256 = sha256_file(artifact)
    if candidate.get("artifact_sha256") != artifact_sha256:
        raise ValueError("slice artifact digest does not match the registry")
    retained = candidate.get("retained_atom_ids")
    if not isinstance(retained, list) or not retained:
        raise ValueError("registered slice must retain at least one atom")
    return {
        "slice_candidate_id": candidate_id,
        "retained_atom_ids": retained,
        "retained_scc_count": candidate.get("retained_scc_count"),
        "slice_artifact_path": artifact.as_posix(),
        "slice_artifact_sha256": artifact_sha256,
        "slice_registry_path": registry_file.as_posix(),
        "slice_registry_sha256": sha256_file(registry_file),
    }


def load_confirmation_binding(
    *,
    family_path: Path,
    slice_binding: dict[str, Any],
    conditions: tuple[str, ...],
    case_block: str,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    family_file = Path(family_path).resolve()
    if not family_file.is_file():
        raise ValueError(f"confirmation family is missing: {family_file}")
    family = json.loads(family_file.read_text(encoding="utf-8"))
    verified_files = validate_file_bindings(family, root=RUN_ROOT)
    if family.get("confirmation_unsealed") is not False:
        raise ValueError("confirmation family must be frozen before unsealing")
    expected_workspace = family.get("workspace_tree_sha256")
    if case_block == "confirmation_v2":
        if not isinstance(workspace_state, dict) or not workspace_state.get("sha256"):
            raise ValueError("confirmation-v2 requires a verified workspace tree")
        if expected_workspace != workspace_state["sha256"]:
            raise ValueError("workspace tree does not match the frozen family")
    if family.get("case_block") != case_block or not case_block.startswith(
        "confirmation"
    ):
        raise ValueError("confirmation case block does not match the frozen family")
    if sorted(family.get("conditions", [])) != list(conditions):
        raise ValueError("confirmation conditions do not match the frozen family")
    if family.get("selected_candidate_id") != slice_binding.get("slice_candidate_id"):
        raise ValueError("confirmation candidate does not match the bound slice")
    if family.get("selected_artifact_sha256") != slice_binding.get(
        "slice_artifact_sha256"
    ):
        raise ValueError("confirmation artifact digest does not match the bound slice")
    if family.get("slice_registry_sha256") != slice_binding.get(
        "slice_registry_sha256"
    ):
        raise ValueError("confirmation slice registry does not match the bound slice")
    if family.get("retained_atom_ids") != slice_binding.get("retained_atom_ids"):
        raise ValueError("confirmation retained atoms do not match the bound slice")
    hypotheses = family.get("hypotheses")
    if not isinstance(hypotheses, list) or not hypotheses:
        raise ValueError("confirmation family must register hypotheses")
    case_binding = verified_files.get("case_registry")
    if case_binding is not None:
        case_registry = json.loads(
            Path(case_binding["path"]).read_text(encoding="utf-8")
        )
        cases = case_registry.get("blocks", {}).get(case_block)
        if not isinstance(cases, list) or len(cases) != family.get("case_count"):
            raise ValueError("confirmation case count does not match the bound registry")
    return {
        "confirmation_family_path": family_file.as_posix(),
        "confirmation_family_sha256": sha256_file(family_file),
        "confirmation_case_count": family.get("case_count"),
        "confirmation_hypothesis_ids": [
            hypothesis["hypothesis_id"] for hypothesis in hypotheses
        ],
        "verified_family_inputs": verified_files,
    }


def build_pair_manifest(
    *,
    pair_id: str,
    seed_block_id: str,
    model_family: str,
    model_alias: str,
    wire_api: str,
    case_block: str,
    condition_contexts: dict[str, str],
    task_prompt: str,
    full_artifact_path: Path,
    atom_map_path: Path,
    case_registry_path: Path,
    scorer_path: Path,
    workspace_state: dict[str, Any],
    max_actions: int,
    maximum_transport_attempts: int,
    harness_protocol_version: str,
    provider_protocol_version: str,
    authorization_evidence: str,
) -> dict[str, Any]:
    for value, label in (
        (pair_id, "pair_id"),
        (seed_block_id, "seed_block_id"),
        (model_family, "model_family"),
        (model_alias, "model_alias"),
        (wire_api, "wire_api"),
        (case_block, "case_block"),
        (task_prompt, "task_prompt"),
        (harness_protocol_version, "harness_protocol_version"),
        (provider_protocol_version, "provider_protocol_version"),
        (authorization_evidence, "authorization_evidence"),
    ):
        if not isinstance(value, str) or not value.strip():
            raise RunnerInputError(f"{label} must be nonempty")
    if wire_api not in {"openai_responses", "openai_chat_completions"}:
        raise RunnerInputError("unsupported wire API")
    if harness_protocol_version not in FINAL_STATE_SCORING_BY_HARNESS:
        raise RunnerInputError("unsupported TOOLFORMER-FILTER harness protocol")
    try:
        evidence_boundary = evidence_boundary_for_block(case_block)
    except ValueError as exc:
        raise RunnerInputError("unsupported TOOLFORMER-FILTER case block") from exc
    conditions = tuple(sorted(condition_contexts))
    if conditions not in PAIR_ROLE_BY_CONDITIONS:
        raise RunnerInputError("conditions must be B/F, F/S, B/S, or B/F/S")
    for path in (
        full_artifact_path,
        atom_map_path,
        case_registry_path,
        scorer_path,
    ):
        if not Path(path).is_file():
            raise RunnerInputError(f"manifest input is missing: {path}")
    for value, label in (
        (max_actions, "max_actions"),
        (maximum_transport_attempts, "maximum_transport_attempts"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise RunnerInputError(f"{label} must be a positive integer")
    if not isinstance(workspace_state, dict) or not workspace_state.get("sha256"):
        raise RunnerInputError("workspace state must contain a tree digest")
    return {
        "schema_version": "effectslice-toolformer-filter-pair.v2",
        "harness_protocol_version": harness_protocol_version,
        "provider_protocol_version": provider_protocol_version,
        "evidence_boundary": evidence_boundary,
        "pair_id": pair_id,
        "task_id": "TOOLFORMER-FILTER",
        "seed_block_id": seed_block_id,
        "model_family": model_family,
        "model_alias": model_alias,
        "wire_api": wire_api,
        "case_block": case_block,
        "comparison_role": PAIR_ROLE_BY_CONDITIONS[conditions],
        "same_aci_scaffold": True,
        "action_budget_visible_to_model": True,
        "common_scaffold_sha256": sha256_text(DEFAULT_COMMON_SCAFFOLD.strip()),
        "task_prompt_sha256": sha256_text(task_prompt.strip()),
        "full_artifact_sha256": sha256_file(Path(full_artifact_path)),
        "atom_map_sha256": sha256_file(Path(atom_map_path)),
        "case_registry_sha256": sha256_file(Path(case_registry_path)),
        "scorer_sha256": sha256_file(Path(scorer_path)),
        "workspace_state": workspace_state,
        "maximum_transport_attempts": maximum_transport_attempts,
        "authorization_evidence": authorization_evidence,
        "conditions": {
            condition: {
                "context_sha256": sha256_text(context.strip()),
                "max_actions": max_actions,
                "retry_lineage_prefix": f"{pair_id}:{condition}",
            }
            for condition, context in sorted(condition_contexts.items())
        },
    }


def run_condition(
    *,
    condition: str,
    context: str,
    task_prompt: str,
    workspace: Path,
    case_registry_path: Path,
    case_block: str,
    output_dir: Path,
    transport,
    retry_lineage_prefix: str,
    max_actions: int,
    score_final_state_on_exhaustion: bool = False,
    private_score_policy: str = "interactive",
) -> tuple[Any, dict[str, Any]]:
    condition_dir = Path(output_dir).resolve() / condition
    bridge = ToolformerFilterScorerBridge(
        workspace=workspace,
        case_registry_path=case_registry_path,
        block=case_block,
        output_dir=condition_dir / "scorer_calls",
    )
    runner = InteractiveACIRunner(
        workspace=OverlayWorkspace(workspace),
        scorer_bridge=bridge,
        model_transport=transport,
        common_scaffold=DEFAULT_COMMON_SCAFFOLD,
        condition_context=context,
        task_prompt=task_prompt,
        action_limits=ActionLimits(
            max_query_chars=200,
            max_path_chars=512,
            max_edit_chars=20_000,
            max_open_lines=200,
            max_search_results=20,
        ),
        max_actions=max_actions,
        max_response_chars=20_000,
        max_observation_chars=4_000,
        score_final_state_on_exhaustion=score_final_state_on_exhaustion,
        private_score_policy=private_score_policy,
    )
    result = runner.run(retry_lineage_prefix=retry_lineage_prefix)
    condition_dir.mkdir(parents=True, exist_ok=True)
    serialized = serialize_run_result(result)
    write_json(condition_dir / "run_result.json", serialized)
    write_json(
        condition_dir / "transcript.json",
        {
            "schema_version": "effectslice-toolformer-filter-transcript.v1",
            "evidence_boundary": evidence_boundary_for_block(case_block),
            "condition": condition,
            "turns": serialized["turns"],
        },
    )
    (condition_dir / "candidate.patch").write_text(
        result.diff_text,
        encoding="utf-8",
        newline="\n",
    )
    public = {
        "status": result.status,
        "terminal_reason": result.terminal_reason,
        "submitted": result.submitted,
        "task_score": result.task_score,
        "success": result.success,
        "actions_used": result.state.actions_used,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "transport_attempts": result.transport_attempts,
        "elapsed_seconds": result.elapsed_seconds,
        "candidate_patch_sha256": sha256_text(result.diff_text),
        "run_result_path": (condition_dir / "run_result.json").as_posix(),
        "transcript_path": (condition_dir / "transcript.json").as_posix(),
        "candidate_patch_path": (condition_dir / "candidate.patch").as_posix(),
        "private_score_policy": result.private_score_policy,
        "private_score_count": result.private_score_count,
        "private_feedback_exposed": result.private_feedback_exposed,
    }
    return result, public


def run_bundle(args: argparse.Namespace) -> dict[str, Any]:
    workspace = (RUN_ROOT / "task_workspaces" / "toolformer_filter_v1").resolve()
    full_artifact_path = RUN_ROOT / "artifacts" / "toolformer_filter" / "full_artifact.md"
    atom_map_path = RUN_ROOT / "artifacts" / "toolformer_filter" / "source_atom_map.json"
    case_registry_path = Path(args.case_registry).resolve()
    task_prompt_path = RUN_ROOT / "artifacts" / "toolformer_filter" / "task_prompt.md"
    scorer_path = RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py"
    task_prompt = task_prompt_path.read_text(encoding="utf-8").strip()
    execution_order, conditions = normalize_condition_order(args.condition)
    if conditions not in PAIR_ROLE_BY_CONDITIONS:
        raise RunnerInputError("conditions must be B/F, F/S, B/S, or B/F/S")
    contexts = {
        condition: build_toolformer_context(
            condition,
            full_artifact_path=full_artifact_path,
            slice_path=args.slice_context,
        )
        for condition in execution_order
    }
    workspace_state = workspace_tree_digest(workspace)
    workspace_state["workspace"] = workspace.as_posix()
    manifest = build_pair_manifest(
        pair_id=args.pair_id,
        seed_block_id=args.seed_block_id,
        model_family=args.model_family,
        model_alias=args.model_alias,
        wire_api=args.wire_api,
        case_block=args.case_block,
        condition_contexts=contexts,
        task_prompt=task_prompt,
        full_artifact_path=full_artifact_path,
        atom_map_path=atom_map_path,
        case_registry_path=case_registry_path,
        scorer_path=scorer_path,
        workspace_state=workspace_state,
        max_actions=args.max_actions,
        maximum_transport_attempts=args.max_attempts,
        harness_protocol_version=args.harness_protocol_version,
        provider_protocol_version=args.provider_protocol_version,
        authorization_evidence=args.authorization_evidence,
    )
    slice_binding: dict[str, Any] | None = None
    if "S" in conditions:
        try:
            slice_binding = load_slice_binding(
                slice_path=args.slice_context,
                registry_path=args.slice_registry,
                candidate_id=args.slice_candidate_id,
            )
            manifest.update(slice_binding)
        except (TypeError, ValueError) as exc:
            raise RunnerInputError(str(exc)) from exc
    if args.case_block.startswith("confirmation"):
        if slice_binding is None:
            raise RunnerInputError("confirmation requires a registered slice")
        try:
            manifest.update(
                load_confirmation_binding(
                    family_path=args.confirmation_family,
                    slice_binding=slice_binding,
                    conditions=conditions,
                    case_block=args.case_block,
                    workspace_state=workspace_state,
                )
            )
        except (TypeError, ValueError) as exc:
            raise RunnerInputError(str(exc)) from exc
    base_url = os.environ.get(args.base_url_env, "")
    api_key = os.environ.get(args.api_key_env, "")
    if not base_url or not api_key:
        raise RunnerInputError("provider base URL or API key environment variable is missing")
    transport = ProviderTransport(
        base_url=base_url,
        api_key=api_key,
        model_alias=args.model_alias,
        wire_api=args.wire_api,
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
        max_attempts=args.max_attempts,
        retry_delay_seconds=args.retry_delay_seconds,
    )
    manifest["provider_config"] = transport.public_config()
    private_score_policy = (
        "final_only" if args.case_block == "confirmation_v2" else "interactive"
    )
    manifest["private_score_policy"] = private_score_policy
    manifest["condition_execution_order"] = list(execution_order)
    output_dir = require_new_output_dir(args.output_dir)
    write_json(output_dir / "pair_manifest.json", manifest)
    results = {}
    for condition in execution_order:
        _, public = run_condition(
            condition=condition,
            context=contexts[condition],
            task_prompt=task_prompt,
            workspace=workspace,
            case_registry_path=case_registry_path,
            case_block=args.case_block,
            output_dir=output_dir,
            transport=transport,
            retry_lineage_prefix=manifest["conditions"][condition]["retry_lineage_prefix"],
            max_actions=args.max_actions,
            score_final_state_on_exhaustion=FINAL_STATE_SCORING_BY_HARNESS[
                args.harness_protocol_version
            ],
            private_score_policy=private_score_policy,
        )
        results[condition] = public
    manifest["results"] = results
    write_json(output_dir / "pair_manifest.json", manifest)
    report = {
        "schema_version": "effectslice-toolformer-filter-run-report.v1",
        "evidence_boundary": evidence_boundary_for_block(args.case_block),
        "pair_id": args.pair_id,
        "case_block": args.case_block,
        "comparison_role": manifest["comparison_role"],
        "model_family": args.model_family,
        "model_alias": args.model_alias,
        "wire_api": args.wire_api,
        "harness_protocol_version": args.harness_protocol_version,
        "provider_protocol_version": args.provider_protocol_version,
        "conditions": list(conditions),
        "condition_execution_order": list(execution_order),
        "results": results,
        "pair_manifest_path": (output_dir / "pair_manifest.json").as_posix(),
    }
    write_json(output_dir / "run_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TOOLFORMER-FILTER EffectSlice ACI bundles")
    parser.add_argument("--condition", action="append", choices=("B", "F", "S"), default=[])
    parser.add_argument("--pair-id", required=True)
    parser.add_argument("--seed-block-id", default="development:toolformer-filter:001")
    parser.add_argument("--model-family", default="DeepSeek-family")
    parser.add_argument("--model-alias", default="deepseek-v4-flash")
    parser.add_argument(
        "--wire-api",
        choices=("openai_responses", "openai_chat_completions"),
        default="openai_chat_completions",
    )
    parser.add_argument("--base-url-env", default="EFFECTSLICE_DEEPSEEK_BASE_URL")
    parser.add_argument("--api-key-env", default="EFFECTSLICE_DEEPSEEK_API_KEY")
    parser.add_argument(
        "--case-block",
        choices=(
            "development",
            "eligibility",
            "discovery",
            "confirmation",
            "confirmation_v2",
        ),
        default="development",
    )
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument(
        "--harness-protocol-version",
        choices=tuple(FINAL_STATE_SCORING_BY_HARNESS),
        default="effectslice-toolformer-filter-aci.v2",
    )
    parser.add_argument(
        "--provider-protocol-version",
        default="effectslice-deepseek-output-budget.v2",
    )
    parser.add_argument("--timeout-seconds", type=float, default=240.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-actions", type=int, default=16)
    parser.add_argument(
        "--case-registry",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry.json",
    )
    parser.add_argument("--slice-context", type=Path)
    parser.add_argument(
        "--slice-registry",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "slices" / "slice_registry.json",
    )
    parser.add_argument("--slice-candidate-id")
    parser.add_argument(
        "--confirmation-family",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "confirmation_family.json",
    )
    parser.add_argument(
        "--authorization-evidence",
        default="user-confirmed trusted endpoint 2026-07-16",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "toolformer_filter_bundle",
    )
    args = parser.parse_args()
    if not args.condition:
        args.condition = ["B", "F"]
    print(json.dumps(run_bundle(args), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
