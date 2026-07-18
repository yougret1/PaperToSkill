from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping


RUN_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_protocol import ActionLimits  # noqa: E402
from effectslice.aci_runner import (  # noqa: E402
    DEFAULT_COMMON_SCAFFOLD,
    InteractiveACIRunner,
)
from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from effectslice.confirmation_v3 import (  # noqa: E402
    sha256_canonical_text,
    sha256_file,
)
from effectslice.swe_scorer_bridge import ScorerEvaluation  # noqa: E402
from effectslice.toolformer_filter_scorer import (  # noqa: E402
    ToolformerFilterScorerError,
    score_toolformer_filter_patch,
)
from run_swe_effectslice import (  # noqa: E402
    ProviderTransport,
    RunnerInputError,
    workspace_tree_digest,
)


REGISTERED_V3 = "registered_final_only_confirmation_v3"
PAIR_SCHEMA = "effectslice-confirmation-v3-pair.v1"
CONDITIONS = ("B", "F", "S")
MAX_ACTIONS = 16
NO_ARTIFACT_CONTEXT = (
    "No paper-derived method artifact is supplied for this condition. "
    "Use only the common bounded ACI contract, the locked task, and tool feedback."
)
REQUIRED_BINDINGS = (
    "full_artifact",
    "selected_artifact",
    "source_map",
    "case_registry",
    "v2_case_registry",
    "scorer",
    "runner",
    "scheduler",
    "analyzer",
    "aci_runner",
    "aci_protocol",
    "evidence_binding",
    "transport",
    "case_generator",
    "task_prompt",
)
_STANDARD_BINDINGS = tuple(
    binding for binding in REQUIRED_BINDINGS if binding != "task_prompt"
)
_SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")
_PUBLIC_PROVIDER_FIELDS = (
    "model_alias",
    "wire_api",
    "max_tokens",
    "timeout_seconds",
    "max_attempts",
    "retry_delay_seconds",
    "temperature",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise RunnerInputError(f"{label} must be {expected!r}")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise RunnerInputError(f"{label} must be a SHA-256 hex digest")
    return value.lower()


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _write_text_exclusive(path: Path, text: str) -> None:
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _resolve_run_root(family_path: Path, family: Mapping[str, Any]) -> Path:
    bindings = family.get("bindings")
    if not isinstance(bindings, dict):
        raise RunnerInputError("family bindings must be an object")
    runner = bindings.get("runner")
    if not isinstance(runner, dict):
        raise RunnerInputError("family runner binding is missing")
    raw_path = runner.get("path")
    expected = _require_sha256(runner.get("sha256"), "runner binding digest")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise RunnerInputError("runner binding path must be nonempty")
    path = Path(raw_path)
    if path.is_absolute():
        if not path.is_file() or sha256_file(path).lower() != expected:
            raise RunnerInputError("runner binding digest does not match the registered file")
        conventional = family_path.resolve().parents[4]
        return conventional
    candidates = (family_path.resolve().parent, *family_path.resolve().parents)
    for candidate in candidates:
        bound_runner = (candidate / path).resolve()
        if bound_runner.is_file() and sha256_file(bound_runner).lower() == expected:
            return candidate.resolve()
    raise RunnerInputError("unable to resolve the registered family run root")


def _resolve_bound_path(raw_path: Any, *, run_root: Path, label: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise RunnerInputError(f"{label} binding path must be nonempty")
    path = Path(raw_path)
    resolved = path.resolve() if path.is_absolute() else (run_root / path).resolve()
    try:
        resolved.relative_to(run_root)
    except ValueError as exc:
        raise RunnerInputError(f"{label} binding escapes the registered run root") from exc
    if not resolved.is_file():
        raise RunnerInputError(f"{label} binding file is missing: {resolved}")
    return resolved


def _verify_standard_binding(
    family: Mapping[str, Any],
    *,
    name: str,
    run_root: Path,
) -> dict[str, str]:
    record = family["bindings"].get(name)
    if not isinstance(record, dict):
        raise RunnerInputError(f"required binding is missing: {name}")
    _require_exact(record.get("status"), "bound", f"{name} binding status")
    expected = _require_sha256(record.get("sha256"), f"{name} binding digest")
    path = _resolve_bound_path(record.get("path"), run_root=run_root, label=name)
    actual = sha256_file(path).lower()
    if actual != expected:
        raise RunnerInputError(f"{name} binding digest does not match the registered file")
    for suffix, expected_value in (
        ("path", record["path"]),
        ("sha256", record["sha256"]),
        ("status", "bound"),
    ):
        top_level = family.get(f"{name}_{suffix}")
        if top_level != expected_value:
            raise RunnerInputError(f"{name} top-level binding metadata does not match")
    return {"path": path.as_posix(), "sha256": actual, "status": "bound"}


def _verify_task_prompt_binding(
    family: Mapping[str, Any], *, run_root: Path
) -> dict[str, str]:
    record = family["bindings"].get("task_prompt")
    if not isinstance(record, dict):
        raise RunnerInputError("required binding is missing: task_prompt")
    _require_exact(record.get("status"), "bound", "task_prompt binding status")
    path = _resolve_bound_path(
        record.get("path"), run_root=run_root, label="task_prompt"
    )
    file_digest = _require_sha256(
        record.get("file_sha256"), "task_prompt file digest"
    )
    canonical_digest = _require_sha256(
        record.get("canonical_text_sha256"), "task_prompt canonical text digest"
    )
    if sha256_file(path).lower() != file_digest:
        raise RunnerInputError("task_prompt file digest does not match the registered file")
    if sha256_canonical_text(path).lower() != canonical_digest:
        raise RunnerInputError(
            "task_prompt canonical text digest does not match the registered file"
        )
    mirrors = {
        "task_prompt_path": record["path"],
        "task_prompt_status": "bound",
        "task_prompt_file_sha256": record["file_sha256"],
        "task_prompt_canonical_text_sha256": record[
            "canonical_text_sha256"
        ],
    }
    for key, expected in mirrors.items():
        if family.get(key) != expected:
            raise RunnerInputError(f"{key} does not match the task_prompt binding")
    return {
        "path": path.as_posix(),
        "sha256": file_digest,
        "file_sha256": file_digest,
        "canonical_text_sha256": canonical_digest,
        "status": "bound",
    }


def _verify_execution_sources(bindings: Mapping[str, Mapping[str, str]]) -> None:
    actual_sources = {
        "runner": Path(__file__).resolve(),
        "scorer": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py",
        "aci_runner": RUN_ROOT / "src" / "effectslice" / "aci_runner.py",
        "aci_protocol": RUN_ROOT / "src" / "effectslice" / "aci_protocol.py",
        "evidence_binding": RUN_ROOT / "src" / "effectslice" / "evidence_binding.py",
        "transport": RUN_ROOT / "run_swe_effectslice.py",
        "case_generator": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_cases.py",
    }
    for name, source in actual_sources.items():
        if not source.is_file() or sha256_file(source) != bindings[name]["sha256"]:
            raise RunnerInputError(
                f"actual {name} execution source does not match the bound SHA"
            )


def _verify_schedule(
    family: Mapping[str, Any], replicate_id: str
) -> dict[str, Any]:
    if not isinstance(replicate_id, str) or not replicate_id.strip():
        raise RunnerInputError("replicate_id must be nonempty")
    schedule = family.get("replicate_schedule")
    count = family.get("replicate_count")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count < 1
        or not isinstance(schedule, list)
        or len(schedule) != count
    ):
        raise RunnerInputError("replicate schedule does not match replicate_count")
    matches = []
    seen: set[str] = set()
    for row in schedule:
        if not isinstance(row, dict):
            raise RunnerInputError("replicate schedule rows must be objects")
        row_id = row.get("replicate_id")
        order = row.get("condition_order")
        if not isinstance(row_id, str) or not row_id:
            raise RunnerInputError("replicate schedule row has an invalid replicate_id")
        if row_id in seen:
            raise RunnerInputError(f"replicate_id is not unique: {row_id}")
        seen.add(row_id)
        if (
            not isinstance(order, list)
            or len(order) != len(CONDITIONS)
            or set(order) != set(CONDITIONS)
        ):
            raise RunnerInputError(
                f"replicate {row_id} condition_order must contain B/F/S exactly once"
            )
        if row_id == replicate_id:
            matches.append(row)
    if len(matches) != 1:
        raise RunnerInputError(
            f"replicate_id must exist exactly once in the registered schedule: {replicate_id}"
        )
    return copy.deepcopy(matches[0])


def load_and_verify_family(
    family_path: Path, replicate_id: str
) -> dict[str, Any]:
    family_file = Path(family_path).resolve()
    if not family_file.is_file():
        raise RunnerInputError(f"confirmation-v3 family is missing: {family_file}")
    try:
        family = json.loads(family_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunnerInputError("confirmation-v3 family is not valid UTF-8 JSON") from exc
    if not isinstance(family, dict):
        raise RunnerInputError("confirmation-v3 family must be a JSON object")

    exact_fields = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": "complete",
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v3",
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
    }
    for label, expected in exact_fields.items():
        _require_exact(family.get(label), expected, label)
    control = family.get("control")
    if control not in {"identity", "planted"}:
        raise RunnerInputError("control must be identity or planted")

    run_root = _resolve_run_root(family_file, family)
    bindings = {
        name: _verify_standard_binding(family, name=name, run_root=run_root)
        for name in _STANDARD_BINDINGS
    }
    bindings["task_prompt"] = _verify_task_prompt_binding(
        family, run_root=run_root
    )
    if set(family["bindings"]) != set(REQUIRED_BINDINGS):
        raise RunnerInputError("family bindings must contain exactly the registered inputs")
    _verify_execution_sources(bindings)

    full_bytes = Path(bindings["full_artifact"]["path"]).read_bytes()
    selected_bytes = Path(bindings["selected_artifact"]["path"]).read_bytes()
    if control == "identity":
        if full_bytes != selected_bytes or family.get("strict_subset") is not False:
            raise RunnerInputError("identity F and S must be byte-identical")
    elif full_bytes == selected_bytes or family.get("strict_subset") is not True:
        raise RunnerInputError("planted F and S must differ")

    case_registry = json.loads(
        Path(bindings["case_registry"]["path"]).read_text(encoding="utf-8")
    )
    cases = case_registry.get("blocks", {}).get("confirmation_v3")
    if not isinstance(cases, list) or len(cases) != family.get("case_count"):
        raise RunnerInputError("case registry does not match the registered case_count")

    workspace_raw = family.get("workspace_path")
    if not isinstance(workspace_raw, str) or not workspace_raw.strip():
        raise RunnerInputError("workspace_path must be nonempty")
    workspace_path = (run_root / workspace_raw).resolve()
    try:
        workspace_path.relative_to(run_root)
    except ValueError as exc:
        raise RunnerInputError("workspace path escapes the registered run root") from exc
    actual_workspace = workspace_tree_digest(workspace_path)
    expected_workspace = {
        "sha256": family.get("workspace_tree_sha256"),
        "file_count": family.get("workspace_file_count"),
        "total_bytes": family.get("workspace_total_bytes"),
        "excluded_directory_names": family.get(
            "workspace_excluded_directory_names"
        ),
    }
    if actual_workspace != expected_workspace:
        raise RunnerInputError("workspace tree does not match the registered family")
    actual_workspace["path"] = workspace_path.as_posix()

    replicate = _verify_schedule(family, replicate_id)
    verified = copy.deepcopy(family)
    verified.update(
        {
            "family_path": family_file.as_posix(),
            "family_sha256": sha256_file(family_file),
            "run_root": run_root.as_posix(),
            "registered_replicate": replicate,
            "verified_bindings": bindings,
            "workspace_state": actual_workspace,
        }
    )
    return verified


def _build_contexts(verified_family: Mapping[str, Any]) -> dict[str, str]:
    bindings = verified_family["verified_bindings"]
    contexts = {
        "B": NO_ARTIFACT_CONTEXT,
        "F": Path(bindings["full_artifact"]["path"])
        .read_text(encoding="utf-8")
        .strip(),
        "S": Path(bindings["selected_artifact"]["path"])
        .read_text(encoding="utf-8")
        .strip(),
    }
    for condition, context in contexts.items():
        if not context:
            raise RunnerInputError(f"condition {condition} context is empty")
    return contexts


def _public_provider_config(
    raw_config: Mapping[str, Any], *, provider_label: str
) -> dict[str, Any]:
    if not isinstance(raw_config, Mapping):
        raise RunnerInputError("transport public_config must return an object")
    public = {
        key: raw_config[key]
        for key in _PUBLIC_PROVIDER_FIELDS
        if key in raw_config
    }
    public["provider_label"] = provider_label
    return public


def build_pair_manifest(
    *,
    verified_family: Mapping[str, Any],
    condition_contexts: Mapping[str, str],
    provider_config: Mapping[str, Any],
) -> dict[str, Any]:
    if set(condition_contexts) != set(CONDITIONS):
        raise RunnerInputError("condition contexts must contain exactly B/F/S")
    order = verified_family["registered_replicate"]["condition_order"]
    replicate_id = verified_family["registered_replicate"]["replicate_id"]
    bindings = verified_family["verified_bindings"]
    pair_id = f"confirmation-v3:{verified_family['control']}:{replicate_id}"
    conditions = {
        condition: {
            "context_sha256": _sha256_text(condition_contexts[condition].strip()),
            "max_actions": MAX_ACTIONS,
            "retry_lineage_prefix": f"{pair_id}:{condition}",
        }
        for condition in order
    }
    return {
        "schema_version": PAIR_SCHEMA,
        "completion_status": "pre_run",
        "pair_id": pair_id,
        "task_id": "TOOLFORMER-FILTER",
        "control": verified_family["control"],
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "private_score_policy": "final_only",
        "family_path": verified_family["family_path"],
        "family_sha256": verified_family["family_sha256"],
        "replicate_id": replicate_id,
        "condition_execution_order": list(order),
        "task_prompt_path": bindings["task_prompt"]["path"],
        "task_prompt_file_sha256": bindings["task_prompt"]["file_sha256"],
        "task_prompt_canonical_text_sha256": bindings["task_prompt"][
            "canonical_text_sha256"
        ],
        "full_artifact_path": bindings["full_artifact"]["path"],
        "full_artifact_sha256": bindings["full_artifact"]["sha256"],
        "selected_artifact_path": bindings["selected_artifact"]["path"],
        "selected_artifact_sha256": bindings["selected_artifact"]["sha256"],
        "source_map_sha256": bindings["source_map"]["sha256"],
        "case_registry_sha256": bindings["case_registry"]["sha256"],
        "scorer_sha256": bindings["scorer"]["sha256"],
        "runner_sha256": bindings["runner"]["sha256"],
        "scheduler_sha256": bindings["scheduler"]["sha256"],
        "analyzer_sha256": bindings["analyzer"]["sha256"],
        "aci_runner_sha256": bindings["aci_runner"]["sha256"],
        "transport_sha256": bindings["transport"]["sha256"],
        "case_generator_sha256": bindings["case_generator"]["sha256"],
        "reference_registry_sha256": bindings["v2_case_registry"]["sha256"],
        "provider_config": dict(provider_config),
        "workspace_state": copy.deepcopy(verified_family["workspace_state"]),
        "conditions": conditions,
        "retry_lineage": {
            condition: conditions[condition]["retry_lineage_prefix"]
            for condition in order
        },
    }


class _ExclusiveToolformerScorerBridge:
    def __init__(
        self,
        *,
        workspace: Path,
        case_registry_path: Path,
        condition_dir: Path,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        self._case_registry_path = Path(case_registry_path).resolve()
        self._condition_dir = Path(condition_dir).resolve()
        self._score_count = 0
        if not self._workspace.is_dir() or not self._case_registry_path.is_file():
            raise ToolformerFilterScorerError("scorer inputs are missing")

    def evaluate(self, diff_text: str, *, evaluation_id: str) -> ScorerEvaluation:
        if self._score_count:
            raise ToolformerFilterScorerError("final-only scorer can be called once")
        if not isinstance(diff_text, str) or not diff_text.strip():
            raise ToolformerFilterScorerError("candidate diff must be nonempty")
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise ToolformerFilterScorerError("evaluation_id must be nonempty")
        self._condition_dir.mkdir(parents=False, exist_ok=False)
        scorer_calls = self._condition_dir / "scorer_calls"
        scorer_calls.mkdir(exist_ok=False)
        evaluation_dir = scorer_calls / evaluation_id
        evaluation_dir.mkdir(exist_ok=False)
        patch_path = evaluation_dir / "candidate.patch"
        _write_text_exclusive(patch_path, diff_text)
        self._score_count += 1
        metric = score_toolformer_filter_patch(
            diff_text=diff_text,
            workspace=self._workspace,
            case_registry_path=self._case_registry_path,
            block="confirmation_v3",
        )
        feedback = json.dumps(
            metric["public_summary"], sort_keys=True, separators=(",", ":")
        )
        return ScorerEvaluation(feedback, metric, patch_path)


def _serialize_result(result: Any) -> dict[str, Any]:
    return dataclasses.asdict(result)


def _run_condition(
    *,
    condition: str,
    context: str,
    task_prompt: str,
    verified_family: Mapping[str, Any],
    output_dir: Path,
    transport: Any,
    retry_lineage_prefix: str,
) -> dict[str, Any]:
    condition_dir = output_dir / condition
    bindings = verified_family["verified_bindings"]
    bridge = _ExclusiveToolformerScorerBridge(
        workspace=Path(verified_family["workspace_state"]["path"]),
        case_registry_path=Path(bindings["case_registry"]["path"]),
        condition_dir=condition_dir,
    )
    runner = InteractiveACIRunner(
        workspace=OverlayWorkspace(Path(verified_family["workspace_state"]["path"])),
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
        max_actions=MAX_ACTIONS,
        max_response_chars=20_000,
        max_observation_chars=4_000,
        score_final_state_on_exhaustion=True,
        private_score_policy="final_only",
    )
    result = runner.run(retry_lineage_prefix=retry_lineage_prefix)
    if result.status == "error":
        raise RuntimeError(f"condition {condition} failed: {result.terminal_reason}")
    if not condition_dir.exists():
        condition_dir.mkdir(exist_ok=False)
    serialized = _serialize_result(result)
    _write_json_exclusive(condition_dir / "run_result.json", serialized)
    _write_json_exclusive(
        condition_dir / "transcript.json",
        {
            "schema_version": "effectslice-confirmation-v3-transcript.v1",
            "evidence_boundary": REGISTERED_V3,
            "turns": serialized["turns"],
        },
    )
    _write_text_exclusive(condition_dir / "candidate.patch", result.diff_text)
    return {
        "status": result.status,
        "terminal_reason": result.terminal_reason,
        "submitted": result.submitted,
        "task_score": result.task_score,
        "success": result.success,
        "actions_used": result.state.actions_used,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "transport_attempts": result.transport_attempts,
        "candidate_patch_sha256": _sha256_text(result.diff_text),
        "private_score_policy": result.private_score_policy,
        "private_score_count": result.private_score_count,
        "private_feedback_exposed": result.private_feedback_exposed,
        "run_result_path": (condition_dir / "run_result.json").as_posix(),
        "transcript_path": (condition_dir / "transcript.json").as_posix(),
        "candidate_patch_path": (condition_dir / "candidate.patch").as_posix(),
    }


def _validate_runtime_args(args: argparse.Namespace, family: Mapping[str, Any]) -> None:
    _require_exact(args.model_alias, "deepseek-v4-flash", "model_alias")
    _require_exact(args.max_attempts, 5, "max_attempts")
    _require_exact(args.max_tokens, family["max_tokens"], "max_tokens")
    for name in ("timeout_seconds", "scorer_timeout_seconds"):
        value = getattr(args, name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value <= 0
        ):
            raise RunnerInputError(f"{name} must be positive")
    delay = args.retry_delay_seconds
    if (
        isinstance(delay, bool)
        or not isinstance(delay, (int, float))
        or delay < 0
    ):
        raise RunnerInputError("retry_delay_seconds must be nonnegative")


def run_bundle(
    args: argparse.Namespace,
    transport_factory=ProviderTransport,
) -> dict[str, Any]:
    verified = load_and_verify_family(args.family, args.replicate_id)
    _validate_runtime_args(args, verified)
    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        raise RunnerInputError(f"output directory already exists: {output_dir}")
    base_url = os.environ.get(args.base_url_env, "")
    api_key = os.environ.get(args.api_key_env, "")
    if not base_url or not api_key:
        raise RunnerInputError(
            "provider base URL or API key environment variable is missing"
        )
    output_dir.mkdir(parents=True, exist_ok=False)
    transport = transport_factory(
        base_url=base_url,
        api_key=api_key,
        model_alias=args.model_alias,
        wire_api="openai_chat_completions",
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
        max_attempts=args.max_attempts,
        retry_delay_seconds=args.retry_delay_seconds,
    )
    public_config = _public_provider_config(
        transport.public_config(), provider_label=verified["provider_label"]
    )
    contexts = _build_contexts(verified)
    manifest = build_pair_manifest(
        verified_family=verified,
        condition_contexts=contexts,
        provider_config=public_config,
    )
    _write_json_exclusive(output_dir / "pair_manifest.pre_run.json", manifest)

    task_prompt = Path(
        verified["verified_bindings"]["task_prompt"]["path"]
    ).read_text(encoding="utf-8").strip()
    results: dict[str, Any] = {}
    for condition in verified["registered_replicate"]["condition_order"]:
        results[condition] = _run_condition(
            condition=condition,
            context=contexts[condition],
            task_prompt=task_prompt,
            verified_family=verified,
            output_dir=output_dir,
            transport=transport,
            retry_lineage_prefix=manifest["conditions"][condition][
                "retry_lineage_prefix"
            ],
        )

    final_manifest = copy.deepcopy(manifest)
    final_manifest["completion_status"] = "complete"
    final_manifest["results"] = results
    _write_json_exclusive(output_dir / "pair_manifest.json", final_manifest)
    return {
        "schema_version": "effectslice-confirmation-v3-run-report.v1",
        "pair_id": manifest["pair_id"],
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
        "replicate_id": args.replicate_id,
        "condition_execution_order": list(
            verified["registered_replicate"]["condition_order"]
        ),
        "results": results,
        "pair_manifest_path": (output_dir / "pair_manifest.json").as_posix(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a bound Toolformer EffectSlice confirmation-v3 replicate"
    )
    parser.add_argument("--family", type=Path, required=True)
    parser.add_argument("--replicate-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-alias", default="deepseek-v4-flash")
    parser.add_argument("--base-url-env", default="EFFECTSLICE_DEEPSEEK_BASE_URL")
    parser.add_argument("--api-key-env", default="EFFECTSLICE_DEEPSEEK_API_KEY")
    parser.add_argument("--timeout-seconds", type=float, default=240.0)
    parser.add_argument("--scorer-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(json.dumps(run_bundle(args), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
