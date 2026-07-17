from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_protocol import ActionLimits  # noqa: E402
from effectslice.aci_runner import (  # noqa: E402
    DEFAULT_COMMON_SCAFFOLD,
    ACIRunResult,
    InteractiveACIRunner,
    ModelTurnResult,
)
from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from effectslice.swe_scorer_bridge import SWEScorerBridge  # noqa: E402
from run_model_ablation_prompts import request_json  # noqa: E402
from score_real_reuse_swe import score_patch  # noqa: E402


NO_SKILL_CONTEXT = (
    "No paper-derived procedural context is supplied for this condition. "
    "Use only the common bounded ACI contract, the locked task, and tool feedback."
)

PAIR_ROLE_BY_CONDITIONS = {
    ("B", "F"): "eligibility",
    ("B", "S"): "singleton_deletion_neighbor",
    ("F", "S"): "preservation",
    ("B", "F", "S"): "development_triage",
}


class RunnerInputError(ValueError):
    """Raised when a frozen SWE bundle input is invalid."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_condition_context(
    condition: str,
    *,
    full_skill_path: Path,
    slice_path: Path | None,
) -> str:
    if condition == "B":
        return NO_SKILL_CONTEXT
    if condition == "F":
        source = Path(full_skill_path)
    elif condition == "S":
        if slice_path is None:
            raise RunnerInputError("S condition requires slice_path")
        source = Path(slice_path)
    else:
        raise RunnerInputError(f"unsupported SWE EffectSlice condition: {condition}")
    if not source.is_file():
        raise RunnerInputError(f"condition context does not exist: {source}")
    context = source.read_text(encoding="utf-8").strip()
    if not context:
        raise RunnerInputError(f"condition context is empty: {source}")
    return context


def build_pair_manifest(
    *,
    pair_id: str,
    case_id: str,
    seed_block_id: str,
    model_family: str,
    model_alias: str,
    wire_api: str,
    source_commit: str,
    condition_contexts: dict[str, str],
    common_scaffold: str,
    task_prompt: str,
    full_skill_path: Path,
    atom_map_path: Path,
    scorer_path: Path,
    test_patch_path: Path,
    max_actions: int,
    maximum_transport_attempts: int,
    authorization_evidence: str,
) -> dict[str, Any]:
    for value, name in (
        (pair_id, "pair_id"),
        (case_id, "case_id"),
        (seed_block_id, "seed_block_id"),
        (model_family, "model_family"),
        (model_alias, "model_alias"),
        (wire_api, "wire_api"),
        (authorization_evidence, "authorization_evidence"),
    ):
        if not isinstance(value, str) or not value.strip():
            raise RunnerInputError(f"{name} must be non-empty")
    if wire_api not in {"openai_responses", "openai_chat_completions"}:
        raise RunnerInputError("unsupported wire_api")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", source_commit):
        raise RunnerInputError("source_commit must be a 40-character Git digest")
    conditions = tuple(sorted(condition_contexts))
    if conditions not in PAIR_ROLE_BY_CONDITIONS:
        raise RunnerInputError("conditions must be B/F, F/S, B/S, or B/F/S")
    for condition, context in condition_contexts.items():
        if condition not in {"B", "F", "S"}:
            raise RunnerInputError(f"unsupported condition: {condition}")
        if not isinstance(context, str) or not context.strip():
            raise RunnerInputError(f"empty context for condition {condition}")
    for path, name in (
        (full_skill_path, "full_skill_path"),
        (atom_map_path, "atom_map_path"),
        (scorer_path, "scorer_path"),
        (test_patch_path, "test_patch_path"),
    ):
        if not Path(path).is_file():
            raise RunnerInputError(f"{name} does not exist")
    for value, name in (
        (max_actions, "max_actions"),
        (maximum_transport_attempts, "maximum_transport_attempts"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise RunnerInputError(f"{name} must be a positive integer")
    if not common_scaffold.strip() or not task_prompt.strip():
        raise RunnerInputError("common scaffold and task prompt must be non-empty")

    return {
        "schema_version": "effectslice-swe-aci-pair.v1",
        "harness_protocol_version": "effectslice-swe-aci.v2",
        "action_budget_visible_to_model": True,
        "evidence_boundary": "development_only_not_confirmation",
        "pair_id": pair_id,
        "case_id": case_id,
        "seed_block_id": seed_block_id,
        "task_id": "SWE-T2",
        "model_family": model_family,
        "model_alias": model_alias,
        "wire_api": wire_api,
        "source_commit": source_commit.lower(),
        "comparison_role": PAIR_ROLE_BY_CONDITIONS[conditions],
        "same_aci_scaffold": True,
        "common_scaffold_sha256": sha256_text(common_scaffold.strip()),
        "task_prompt_sha256": sha256_text(task_prompt.strip()),
        "full_artifact_sha256": sha256_file(Path(full_skill_path)),
        "atom_map_sha256": sha256_file(Path(atom_map_path)),
        "scorer_sha256": sha256_file(Path(scorer_path)),
        "test_patch_sha256": sha256_file(Path(test_patch_path)),
        "maximum_transport_attempts": maximum_transport_attempts,
        "authorization_evidence": authorization_evidence,
        "conditions": {
            condition: {
                "context_sha256": sha256_text(condition_contexts[condition].strip()),
                "max_actions": max_actions,
                "retry_lineage_prefix": f"{pair_id}:{condition}",
            }
            for condition in conditions
        },
    }


class ProviderTransport:
    """Provider-neutral turn transport with bounded same-lineage retries."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model_alias: str,
        wire_api: str,
        max_tokens: int,
        timeout_seconds: float,
        max_attempts: int,
        retry_delay_seconds: float,
        request_function=request_json,
    ) -> None:
        for value, name in (
            (base_url, "base_url"),
            (api_key, "api_key"),
            (model_alias, "model_alias"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise RunnerInputError(f"{name} must be non-empty")
        if not base_url.lower().startswith("https://"):
            raise RunnerInputError("base_url must use HTTPS")
        if wire_api not in {"openai_responses", "openai_chat_completions"}:
            raise RunnerInputError("unsupported wire_api")
        for value, name in ((max_tokens, "max_tokens"), (max_attempts, "max_attempts")):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise RunnerInputError(f"{name} must be a positive integer")
        for value, name, allow_zero in (
            (timeout_seconds, "timeout_seconds", False),
            (retry_delay_seconds, "retry_delay_seconds", True),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or (value < 0 if allow_zero else value <= 0)
            ):
                qualifier = "nonnegative" if allow_zero else "positive"
                raise RunnerInputError(f"{name} must be finite and {qualifier}")
        if not callable(request_function):
            raise RunnerInputError("request_function must be callable")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model_alias = model_alias
        self._wire_api = wire_api
        self._max_tokens = max_tokens
        self._timeout_seconds = float(timeout_seconds)
        self._max_attempts = max_attempts
        self._retry_delay_seconds = float(retry_delay_seconds)
        self._request_function = request_function

    def public_config(self) -> dict[str, Any]:
        return {
            "base_url": self._base_url,
            "model_alias": self._model_alias,
            "wire_api": self._wire_api,
            "max_tokens": self._max_tokens,
            "timeout_seconds": self._timeout_seconds,
            "max_attempts": self._max_attempts,
            "retry_delay_seconds": self._retry_delay_seconds,
            "temperature": 0 if self._wire_api == "openai_chat_completions" else None,
        }

    def __call__(
        self,
        *,
        prompt: str,
        retry_lineage_id: str,
        turn_index: int,
    ) -> ModelTurnResult:
        del retry_lineage_id, turn_index
        body = self._request_body(prompt)
        endpoint = self._endpoint()
        last_error = "retryable_provider_error_exhausted"
        cumulative_input_tokens = 0
        cumulative_output_tokens = 0
        for attempt in range(1, self._max_attempts + 1):
            try:
                _, response = self._request_function(
                    endpoint,
                    self._api_key,
                    method="POST",
                    body=body,
                    extra_headers=None,
                    timeout_seconds=self._timeout_seconds,
                )
            except RuntimeError as error:
                if not _is_retryable_error(str(error)):
                    return ModelTurnResult(
                        status="error",
                        response_text=None,
                        attempts=attempt,
                        input_tokens=0,
                        output_tokens=0,
                        error_message="deterministic_provider_error",
                    )
                last_error = "retryable_provider_error_exhausted"
            except Exception:  # noqa: BLE001 - network error details are not persisted
                last_error = "retryable_provider_error_exhausted"
            else:
                attempt_input_tokens, attempt_output_tokens = _normalize_usage(response)
                cumulative_input_tokens += attempt_input_tokens
                cumulative_output_tokens += attempt_output_tokens
                content = _extract_content(response).strip()
                if content:
                    provider_model_id = response.get("model", "")
                    provider_response_id = response.get("id", "")
                    provider_created = response.get("created")
                    return ModelTurnResult(
                        status="success",
                        response_text=content,
                        attempts=attempt,
                        input_tokens=cumulative_input_tokens,
                        output_tokens=cumulative_output_tokens,
                        provider_model_id=(
                            provider_model_id if isinstance(provider_model_id, str) else ""
                        ),
                        provider_response_id=(
                            provider_response_id
                            if isinstance(provider_response_id, str)
                            else ""
                        ),
                        provider_created=(
                            provider_created
                            if isinstance(provider_created, int)
                            and not isinstance(provider_created, bool)
                            and provider_created >= 0
                            else None
                        ),
                    )
                last_error = "empty_response_content"
            if attempt < self._max_attempts and self._retry_delay_seconds:
                time.sleep(self._retry_delay_seconds)
        return ModelTurnResult(
            status="error",
            response_text=None,
            attempts=self._max_attempts,
            input_tokens=cumulative_input_tokens,
            output_tokens=cumulative_output_tokens,
            error_message=last_error,
        )

    def _endpoint(self) -> str:
        suffix = "responses" if self._wire_api == "openai_responses" else "chat/completions"
        if self._base_url.endswith(f"/{suffix}"):
            return self._base_url
        return f"{self._base_url}/{suffix}"

    def _request_body(self, prompt: str) -> dict[str, Any]:
        if self._wire_api == "openai_responses":
            return {
                "model": self._model_alias,
                "input": prompt,
                "max_output_tokens": self._max_tokens,
            }
        return {
            "model": self._model_alias,
            "messages": [
                {
                    "role": "system",
                    "content": "Follow the bounded ACI contract and return one JSON action only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": self._max_tokens,
        }


def _is_retryable_error(message: str) -> bool:
    match = re.search(r'"?http_error"?\s*:\s*(\d{3})', message)
    if not match:
        return True
    return int(match.group(1)) in {429, 502, 503, 504}


def _extract_content(response: dict[str, Any]) -> str:
    if not isinstance(response, dict):
        return ""
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    choices = response.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]
    output = response.get("output")
    if isinstance(output, list):
        parts = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        return "\n".join(parts)
    return ""


def _normalize_usage(response: dict[str, Any]) -> tuple[int, int]:
    usage = response.get("usage", {}) if isinstance(response, dict) else {}
    if not isinstance(usage, dict):
        return 0, 0
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))
    return _safe_token_count(input_tokens), _safe_token_count(output_tokens)


def _safe_token_count(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _asset_path(
    project_root: Path,
    manifest: dict[str, Any],
    slot: str,
) -> Path:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            path = Path(str(item["path"]))
            return path if path.is_absolute() else project_root / path
    raise RunnerInputError(f"asset manifest missing slot: {slot}")


def verify_locked_workspace(
    workspace: Path,
    *,
    expected_commit: str,
) -> dict[str, Any]:
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise RunnerInputError("locked workspace is missing")
    safe_directory = workspace.as_posix()
    base_command = [
        "git",
        "-c",
        f"safe.directory={safe_directory}",
        "-C",
        str(workspace),
    ]
    head = subprocess.run(
        [*base_command, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if head.returncode != 0:
        raise RunnerInputError("unable to verify locked workspace commit")
    actual_commit = head.stdout.strip().lower()
    if actual_commit != expected_commit.lower():
        raise RunnerInputError("locked workspace commit does not match manifest")
    status = subprocess.run(
        [*base_command, "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if status.returncode != 0:
        raise RunnerInputError("unable to verify locked workspace status")
    dirty_rows = [line for line in status.stdout.splitlines() if line.strip()]
    if dirty_rows:
        raise RunnerInputError("locked workspace has tracked or untracked modifications")
    return {
        "workspace": workspace.as_posix(),
        "expected_commit": expected_commit.lower(),
        "actual_commit": actual_commit,
        "tracked_and_untracked_worktree_clean": True,
        "scorer_copy_tree": workspace_tree_digest(workspace),
    }


def workspace_tree_digest(workspace: Path) -> dict[str, Any]:
    root = Path(workspace).resolve()
    if not root.is_dir():
        raise RunnerInputError("workspace tree does not exist")
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
            elif directory.is_symlink():
                raise RunnerInputError("workspace contains a directory symlink")
        directory_names.sort()
        for file_name in sorted(file_names):
            path = current / file_name
            relative = path.relative_to(root).as_posix()
            relative_bytes = relative.encode("utf-8")
            digest.update(len(relative_bytes).to_bytes(8, "big"))
            digest.update(relative_bytes)
            size = 0
            try:
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                        size += len(chunk)
            except OSError as error:
                raise RunnerInputError(f"unable to hash workspace file: {relative}") from error
            digest.update(size.to_bytes(8, "big"))
            file_count += 1
            total_bytes += size
    return {
        "sha256": digest.hexdigest(),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "excluded_directory_names": sorted(excluded),
    }


def serialize_run_result(result: ACIRunResult) -> dict[str, Any]:
    payload = dataclasses.asdict(result)
    return _json_safe(payload)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def run_condition(
    *,
    condition: str,
    context: str,
    task_prompt: str,
    workspace: Path,
    test_command: str,
    test_patch_path: Path,
    output_dir: Path,
    transport: ProviderTransport,
    retry_lineage_prefix: str,
    max_actions: int,
    scorer_timeout_seconds: float,
    action_limits: ActionLimits,
) -> tuple[ACIRunResult, dict[str, Any]]:
    condition_dir = Path(output_dir).resolve() / condition
    scorer_bridge = SWEScorerBridge(
        task_id="SWE-T2",
        workspace=workspace,
        test_command=test_command,
        test_patch_path=test_patch_path,
        output_dir=condition_dir / "scorer_calls",
        timeout_seconds=scorer_timeout_seconds,
        score_function=score_patch,
    )
    runner = InteractiveACIRunner(
        workspace=OverlayWorkspace(workspace),
        scorer_bridge=scorer_bridge,
        model_transport=transport,
        common_scaffold=DEFAULT_COMMON_SCAFFOLD,
        condition_context=context,
        task_prompt=task_prompt,
        action_limits=action_limits,
        max_actions=max_actions,
        max_response_chars=20_000,
        max_observation_chars=4_000,
    )
    result = runner.run(retry_lineage_prefix=retry_lineage_prefix)
    serialized = serialize_run_result(result)
    condition_dir.mkdir(parents=True, exist_ok=True)
    write_json(condition_dir / "run_result.json", serialized)
    write_json(
        condition_dir / "transcript.json",
        {
            "schema_version": "effectslice-aci-transcript.v1",
            "evidence_boundary": "development_only_not_confirmation",
            "condition": condition,
            "turns": serialized["turns"],
        },
    )
    (condition_dir / "candidate.patch").write_text(result.diff_text, encoding="utf-8")
    public_summary = {
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
    }
    return result, public_summary


def run_bundle(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.root).resolve()
    asset_manifest_path = (
        project_root / "benchmarks" / "real_reuse" / "assets" / "SWE-T2" / "asset_manifest.json"
    )
    manifest_asset = load_json(asset_manifest_path)
    locked_instance = manifest_asset["source_snapshot"]["locked_task_instance"]
    expected_commit = str(locked_instance["base_commit"])
    workspace_raw = Path(str(manifest_asset["workspace_dir"]))
    workspace = workspace_raw if workspace_raw.is_absolute() else project_root / workspace_raw
    workspace_state = verify_locked_workspace(workspace, expected_commit=expected_commit)
    task_prompt_path = _asset_path(project_root, manifest_asset, "task_prompt")
    test_command_path = _asset_path(project_root, manifest_asset, "target_test_command")
    test_patch_path = _asset_path(project_root, manifest_asset, "test_patch")
    task_prompt = task_prompt_path.read_text(encoding="utf-8").strip()
    test_command = test_command_path.read_text(encoding="utf-8").strip()
    full_skill_path = (
        project_root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md"
    )
    atom_map_path = RUN_ROOT / "artifacts" / "swe_t2" / "source_atom_map.json"
    scorer_path = project_root / "scripts" / "score_real_reuse_swe.py"
    conditions = tuple(sorted(set(args.condition)))
    if conditions not in PAIR_ROLE_BY_CONDITIONS:
        raise RunnerInputError("conditions must be B/F, F/S, B/S, or B/F/S")
    contexts = {
        condition: build_condition_context(
            condition,
            full_skill_path=full_skill_path,
            slice_path=args.slice_context,
        )
        for condition in conditions
    }
    output_dir = Path(args.output_dir).resolve()
    pair_manifest_path = output_dir / "pair_manifest.json"
    pair_manifest = build_pair_manifest(
        pair_id=args.pair_id,
        case_id=str(locked_instance["instance_id"]),
        seed_block_id=args.seed_block_id,
        model_family=args.model_family,
        model_alias=args.model_alias,
        wire_api=args.wire_api,
        source_commit=expected_commit,
        condition_contexts=contexts,
        common_scaffold=DEFAULT_COMMON_SCAFFOLD,
        task_prompt=task_prompt,
        full_skill_path=full_skill_path,
        atom_map_path=atom_map_path,
        scorer_path=scorer_path,
        test_patch_path=test_patch_path,
        max_actions=args.max_actions,
        maximum_transport_attempts=args.max_attempts,
        authorization_evidence=args.authorization_evidence,
    )
    pair_manifest["workspace_state"] = workspace_state
    pair_manifest["asset_manifest_sha256"] = sha256_file(asset_manifest_path)
    if "S" in conditions:
        pair_manifest["slice_artifact_sha256"] = sha256_file(args.slice_context)
        pair_manifest["slice_artifact_path"] = Path(args.slice_context).resolve().as_posix()
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
    pair_manifest["provider_config"] = transport.public_config()
    write_json(pair_manifest_path, pair_manifest)

    results = {}
    for condition in conditions:
        _, public_summary = run_condition(
            condition=condition,
            context=contexts[condition],
            task_prompt=task_prompt,
            workspace=workspace,
            test_command=test_command,
            test_patch_path=test_patch_path,
            output_dir=output_dir,
            transport=transport,
            retry_lineage_prefix=pair_manifest["conditions"][condition]["retry_lineage_prefix"],
            max_actions=args.max_actions,
            scorer_timeout_seconds=args.scorer_timeout_seconds,
            action_limits=ActionLimits(
                max_query_chars=200,
                max_path_chars=512,
                max_edit_chars=20_000,
                max_open_lines=200,
                max_search_results=20,
            ),
        )
        results[condition] = public_summary
    pair_manifest["results"] = results
    write_json(pair_manifest_path, pair_manifest)
    report = {
        "schema_version": "effectslice-swe-aci-run-report.v1",
        "evidence_boundary": "development_only_not_confirmation",
        "pair_id": args.pair_id,
        "comparison_role": pair_manifest["comparison_role"],
        "model_family": args.model_family,
        "model_alias": args.model_alias,
        "wire_api": args.wire_api,
        "conditions": list(conditions),
        "results": results,
        "pair_manifest_path": pair_manifest_path.as_posix(),
    }
    write_json(output_dir / "run_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run interactive SWE-T2 EffectSlice development bundles")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--condition", action="append", choices=("B", "F", "S"), default=[])
    parser.add_argument("--pair-id", required=True)
    parser.add_argument("--seed-block-id", default="development:aci:001")
    parser.add_argument("--model-family", default="GPT-family")
    parser.add_argument("--model-alias", default="gpt-5.6")
    parser.add_argument(
        "--wire-api",
        choices=("openai_responses", "openai_chat_completions"),
        default="openai_responses",
    )
    parser.add_argument("--base-url-env", default="EFFECTSLICE_GPT_BASE_URL")
    parser.add_argument("--api-key-env", default="EFFECTSLICE_GPT_API_KEY")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--timeout-seconds", type=float, default=240.0)
    parser.add_argument("--scorer-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--max-actions", type=int, default=8)
    parser.add_argument(
        "--slice-context",
        type=Path,
        default=RUN_ROOT / "artifacts" / "swe_t2" / "slice_v0.md",
    )
    parser.add_argument(
        "--authorization-evidence",
        default="user-confirmed trusted endpoint 2026-07-16",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "swe_t2_aci_bundle",
    )
    args = parser.parse_args()
    if not args.condition:
        args.condition = ["B", "F"]
    report = run_bundle(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
