from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import inspect
import json
import math
import os
import re
import sys
import threading
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
    sha256_file,
)
from effectslice.swe_scorer_bridge import ScorerEvaluation  # noqa: E402
from effectslice.toolformer_filter_scorer import (  # noqa: E402
    ToolformerFilterScorerError,
    score_toolformer_filter_patch,
)
from effectslice.toolformer_filter_cases import generate_case  # noqa: E402
from confirmation_transport_v3 import (  # noqa: E402
    ProviderTransport,
    REGISTERED_BASE_URL,
    REGISTERED_MAX_ATTEMPTS,
    REGISTERED_MAX_TOKENS,
    REGISTERED_MODEL_ALIAS,
    REGISTERED_PROXY_POLICY,
    REGISTERED_RETRY_DELAY_SECONDS,
    REGISTERED_TIMEOUT_SECONDS,
    REGISTERED_WIRE_API,
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
_ATOM_ID_PATTERN = re.compile(r"\(`(T\d+)`\)")
_PUBLIC_PROVIDER_FIELDS = (
    "base_url",
    "model_alias",
    "wire_api",
    "max_tokens",
    "timeout_seconds",
    "max_attempts",
    "retry_delay_seconds",
    "temperature",
    "direct_connection",
    "proxy_policy",
)


class RunnerInputError(ValueError):
    """Raised when a frozen confirmation-v3 bundle input is invalid."""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _decode_utf8(payload: bytes, label: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunnerInputError(f"{label} must be valid UTF-8") from exc


def _load_json_object(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(_decode_utf8(payload, label))
    except json.JSONDecodeError as exc:
        raise RunnerInputError(f"{label} must be valid JSON") from exc
    if not isinstance(value, dict):
        raise RunnerInputError(f"{label} JSON must be an object")
    return value


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


def _write_bytes_exclusive(path: Path, payload: bytes) -> None:
    with Path(path).open("xb") as handle:
        handle.write(payload)


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
    actual_runner = Path(__file__).resolve()
    if path.is_absolute():
        if path.resolve() != actual_runner or sha256_file(actual_runner).lower() != expected:
            raise RunnerInputError(
                "actual runner execution source does not match the bound path and SHA"
            )
        parents = family_path.resolve().parents
        if len(parents) <= 4:
            raise RunnerInputError("family path is too short to resolve the run root")
        conventional = parents[4]
        return conventional
    candidates = (family_path.resolve().parent, *family_path.resolve().parents)
    for candidate in candidates:
        bound_runner = (candidate / path).resolve()
        if (
            bound_runner == actual_runner
            and sha256_file(actual_runner).lower() == expected
        ):
            return candidate.resolve()
    raise RunnerInputError(
        "actual runner execution source does not match the bound path and SHA"
    )


def _resolve_bound_path(
    raw_path: Any, *, run_root: Path, label: str, allow_external: bool = False
) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise RunnerInputError(f"{label} binding path must be nonempty")
    path = Path(raw_path)
    resolved = path.resolve() if path.is_absolute() else (run_root / path).resolve()
    if not allow_external:
        try:
            resolved.relative_to(run_root)
        except ValueError as exc:
            raise RunnerInputError(
                f"{label} binding escapes the registered run root"
            ) from exc
    if not resolved.is_file():
        raise RunnerInputError(f"{label} binding file is missing: {resolved}")
    return resolved


def _verify_standard_binding(
    family: Mapping[str, Any],
    *,
    name: str,
    run_root: Path,
) -> dict[str, Any]:
    record = family["bindings"].get(name)
    if not isinstance(record, dict):
        raise RunnerInputError(f"required binding is missing: {name}")
    _require_exact(record.get("status"), "bound", f"{name} binding status")
    expected = _require_sha256(record.get("sha256"), f"{name} binding digest")
    path = _resolve_bound_path(
        record.get("path"),
        run_root=run_root,
        label=name,
        allow_external=name in _actual_execution_sources(),
    )
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RunnerInputError(f"unable to read {name} binding") from exc
    actual = _sha256_bytes(payload)
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
    return {
        "path": path.as_posix(),
        "sha256": actual,
        "status": "bound",
        "verified_bytes": payload,
    }


def _verify_task_prompt_binding(
    family: Mapping[str, Any], *, run_root: Path
) -> dict[str, Any]:
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
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RunnerInputError("unable to read task_prompt binding") from exc
    if _sha256_bytes(payload) != file_digest:
        raise RunnerInputError("task_prompt file digest does not match the registered file")
    text = _decode_utf8(payload, "task_prompt")
    if _sha256_text(_canonical_text(text)) != canonical_digest:
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
        "verified_bytes": payload,
        "verified_text": text,
    }


def _actual_execution_sources() -> dict[str, Path]:
    sources = {
        "runner": Path(__file__),
        "scorer": inspect.getsourcefile(score_toolformer_filter_patch),
        "aci_runner": inspect.getsourcefile(InteractiveACIRunner),
        "aci_protocol": inspect.getsourcefile(ActionLimits),
        "transport": inspect.getsourcefile(ProviderTransport),
        "case_generator": inspect.getsourcefile(generate_case),
    }
    if any(source is None for source in sources.values()):
        raise RunnerInputError("unable to identify an actual execution source")
    return {name: Path(source).resolve() for name, source in sources.items()}


def _verify_execution_sources(bindings: Mapping[str, Mapping[str, Any]]) -> None:
    for name, source in _actual_execution_sources().items():
        bound_path = Path(bindings[name]["path"]).resolve()
        if (
            bound_path != source
            or not source.is_file()
            or sha256_file(source).lower() != bindings[name]["sha256"]
        ):
            raise RunnerInputError(
                f"actual {name} execution source does not match the bound path and SHA"
            )


def _artifact_atom_ids(payload: bytes, label: str) -> list[str]:
    atom_ids = _ATOM_ID_PATTERN.findall(_decode_utf8(payload, f"{label} artifact"))
    if not atom_ids or len(atom_ids) != len(set(atom_ids)):
        raise RunnerInputError(
            f"{label} artifact atom IDs must be unique and nonempty"
        )
    return atom_ids


def _verify_artifact_truth(
    control: str,
    full_bytes: bytes,
    selected_bytes: bytes,
    source_map: Mapping[str, Any],
) -> None:
    full_ids = _artifact_atom_ids(full_bytes, "F")
    selected_ids = _artifact_atom_ids(selected_bytes, "S")
    full_atoms = set(full_ids)
    selected_atoms = set(selected_ids)
    strict_subset = selected_atoms < full_atoms
    if control == "identity":
        if full_bytes != selected_bytes or selected_atoms != full_atoms:
            raise RunnerInputError("identity F and S must be byte-identical")
    elif not strict_subset:
        raise RunnerInputError("planted S must be a strict subset of F")

    atoms = source_map.get("atoms")
    if not isinstance(atoms, list) or not all(isinstance(row, dict) for row in atoms):
        raise RunnerInputError("source_map atoms must be objects")
    map_ids = [row.get("atom_id") for row in atoms]
    if (
        any(not isinstance(atom_id, str) for atom_id in map_ids)
        or len(map_ids) != len(set(map_ids))
        or map_ids != full_ids
    ):
        raise RunnerInputError(
            "F artifact atom membership must exactly match the source_map"
        )

    raw_requires = source_map.get("requires")
    if not isinstance(raw_requires, dict) or set(raw_requires) != full_atoms:
        raise RunnerInputError(
            "source_map requires keys must exactly match its atoms"
        )
    requires_edges: set[tuple[str, str]] = set()
    for atom_id in full_ids:
        dependencies = raw_requires[atom_id]
        if (
            not isinstance(dependencies, list)
            or any(not isinstance(item, str) for item in dependencies)
            or len(dependencies) != len(set(dependencies))
        ):
            raise RunnerInputError(
                f"source_map dependencies for {atom_id} must be unique atom IDs"
            )
        for dependency in dependencies:
            if dependency not in full_atoms or dependency == atom_id:
                raise RunnerInputError(
                    f"source_map dependency for {atom_id} is invalid: {dependency}"
                )
            requires_edges.add((atom_id, dependency))
        missing = set(dependencies) - selected_atoms
        if atom_id in selected_atoms and missing:
            raise RunnerInputError(
                f"S artifact is not dependency-closed at {atom_id}: {sorted(missing)}"
            )

    raw_edges = source_map.get("dependency_edges")
    if not isinstance(raw_edges, list):
        raise RunnerInputError("source_map dependency_edges must be a list")
    declared_edges: set[tuple[str, str]] = set()
    for edge in raw_edges:
        if not isinstance(edge, dict):
            raise RunnerInputError("source_map dependency edges must be objects")
        pair = (edge.get("from"), edge.get("to"))
        if (
            pair[0] not in full_atoms
            or pair[1] not in full_atoms
            or pair[0] == pair[1]
            or pair in declared_edges
        ):
            raise RunnerInputError("source_map contains an invalid dependency edge")
        declared_edges.add(pair)
    if declared_edges != requires_edges:
        raise RunnerInputError(
            "source_map requires and dependency_edges disagree"
        )


def _capture_workspace_tree(workspace: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    root = Path(workspace).resolve()
    if not root.is_dir():
        raise RunnerInputError("workspace tree does not exist")
    excluded = {".git", "__pycache__", ".pytest_cache"}
    digest = hashlib.sha256()
    files: dict[str, bytes] = {}
    total_bytes = 0
    for current_root, directory_names, file_names in os.walk(
        root, followlinks=False
    ):
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
            if path.is_symlink():
                raise RunnerInputError(f"workspace contains a file symlink: {relative}")
            try:
                payload = path.read_bytes()
            except OSError as exc:
                raise RunnerInputError(
                    f"unable to capture workspace file: {relative}"
                ) from exc
            relative_bytes = relative.encode("utf-8")
            digest.update(len(relative_bytes).to_bytes(8, "big"))
            digest.update(relative_bytes)
            digest.update(payload)
            digest.update(len(payload).to_bytes(8, "big"))
            files[relative] = payload
            total_bytes += len(payload)
    return (
        {
            "sha256": digest.hexdigest(),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "excluded_directory_names": sorted(excluded),
        },
        files,
    )


def _verify_registered_metadata(family: Mapping[str, Any], control: str) -> None:
    _require_exact(family.get("case_count"), 64, "case_count")
    _require_exact(
        family.get("base_url"), REGISTERED_BASE_URL, "base_url"
    )
    _require_exact(
        family.get("timeout_seconds"),
        REGISTERED_TIMEOUT_SECONDS,
        "timeout_seconds",
    )
    _require_exact(
        family.get("retry_delay_seconds"),
        REGISTERED_RETRY_DELAY_SECONDS,
        "retry_delay_seconds",
    )
    _require_exact(
        family.get("direct_connection"), True, "direct_connection"
    )
    _require_exact(
        family.get("proxy_policy"), REGISTERED_PROXY_POLICY, "proxy_policy"
    )
    _require_exact(family.get("max_tokens"), REGISTERED_MAX_TOKENS, "max_tokens")
    _require_exact(family.get("strict_subset"), control == "planted", "strict_subset")
    _require_exact(
        family.get("run_success_threshold"), 0.95, "run_success_threshold"
    )
    _require_exact(family.get("maximum_shortfall"), 0.05, "maximum_shortfall")
    replicate_count = family.get("replicate_count")
    if type(replicate_count) is not int or replicate_count < 1:
        raise RunnerInputError("replicate_count must be a positive integer")
    required = family.get("required_joint_events_for_admission")
    if control == "identity":
        if required is not None:
            raise RunnerInputError(
                "identity required_joint_events_for_admission must be null"
            )
    elif type(required) is not int or not 1 <= required <= replicate_count:
        raise RunnerInputError(
            "planted required_joint_events_for_admission is out of range"
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
        "maximum_transport_attempts": REGISTERED_MAX_ATTEMPTS,
        "provider_label": "DeepSeek V3.2",
        "model_alias": REGISTERED_MODEL_ALIAS,
        "wire_api": REGISTERED_WIRE_API,
        "temperature": 0,
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
    }
    for label, expected in exact_fields.items():
        _require_exact(family.get(label), expected, label)
    control = family.get("control")
    if control not in {"identity", "planted"}:
        raise RunnerInputError("control must be identity or planted")
    _verify_registered_metadata(family, control)

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

    full_bytes = bindings["full_artifact"]["verified_bytes"]
    selected_bytes = bindings["selected_artifact"]["verified_bytes"]
    source_map = _load_json_object(
        bindings["source_map"]["verified_bytes"], "source_map"
    )
    _verify_artifact_truth(control, full_bytes, selected_bytes, source_map)

    case_registry = _load_json_object(
        bindings["case_registry"]["verified_bytes"], "case_registry"
    )
    blocks = case_registry.get("blocks")
    if not isinstance(blocks, dict):
        raise RunnerInputError("case_registry blocks must be a JSON object")
    cases = blocks.get("confirmation_v3")
    if not isinstance(cases, list) or len(cases) != 64:
        raise RunnerInputError("case registry does not match the registered case_count")
    seen_seeds: set[int] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise RunnerInputError("confirmation_v3 cases must be JSON objects")
        seed = case.get("seed")
        if type(seed) is not int or seed in seen_seeds:
            raise RunnerInputError("confirmation_v3 case seeds must be unique integers")
        seen_seeds.add(seed)
        if case != generate_case(seed):
            raise RunnerInputError(
                f"confirmation_v3 case does not match generate_case({seed})"
            )

    workspace_raw = family.get("workspace_path")
    if not isinstance(workspace_raw, str) or not workspace_raw.strip():
        raise RunnerInputError("workspace_path must be nonempty")
    workspace_path = (run_root / workspace_raw).resolve()
    try:
        workspace_path.relative_to(run_root)
    except ValueError as exc:
        raise RunnerInputError("workspace path escapes the registered run root") from exc
    actual_workspace, workspace_files = _capture_workspace_tree(workspace_path)
    expected_file_count = family.get("workspace_file_count")
    expected_total_bytes = family.get("workspace_total_bytes")
    if type(expected_file_count) is not int or expected_file_count < 0:
        raise RunnerInputError("workspace_file_count must be a nonnegative integer")
    if type(expected_total_bytes) is not int or expected_total_bytes < 0:
        raise RunnerInputError("workspace_total_bytes must be a nonnegative integer")
    expected_workspace = {
        "sha256": _require_sha256(
            family.get("workspace_tree_sha256"), "workspace_tree_sha256"
        ),
        "file_count": expected_file_count,
        "total_bytes": expected_total_bytes,
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
            "verified_workspace_files": workspace_files,
        }
    )
    return verified


def _build_contexts(verified_family: Mapping[str, Any]) -> dict[str, str]:
    bindings = verified_family["verified_bindings"]
    contexts = {
        "B": NO_ARTIFACT_CONTEXT,
        "F": _decode_utf8(
            bindings["full_artifact"]["verified_bytes"], "full_artifact"
        ).strip(),
        "S": _decode_utf8(
            bindings["selected_artifact"]["verified_bytes"], "selected_artifact"
        ).strip(),
    }
    for condition, context in contexts.items():
        if not context:
            raise RunnerInputError(f"condition {condition} context is empty")
    return contexts


def _public_provider_config(
    raw_config: Mapping[str, Any],
    *,
    provider_label: str,
    expected: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_config, Mapping):
        raise RunnerInputError("transport public_config must return an object")
    public: dict[str, Any] = {}
    for key in _PUBLIC_PROVIDER_FIELDS:
        if key not in raw_config:
            continue
        value = raw_config[key]
        if expected is not None:
            if key not in expected:
                raise RunnerInputError(f"unexpected provider config field: {key}")
            _require_exact(value, expected[key], f"provider config {key}")
            value = expected[key]
        public[key] = value
    if expected is not None and set(public) != set(expected):
        raise RunnerInputError("transport public_config is incomplete")
    public["provider_label"] = provider_label
    return public


def _materialize_verified_snapshots(
    output_dir: Path, verified_family: Mapping[str, Any]
) -> tuple[Path, Path]:
    bindings = verified_family["verified_bindings"]
    input_dir = output_dir / "verified_inputs"
    input_dir.mkdir(exist_ok=False)
    names = {
        "task_prompt": "task_prompt.md",
        "full_artifact": "full_artifact.md",
        "selected_artifact": "selected_artifact.md",
        "source_map": "source_atom_map.json",
        "case_registry": "case_registry.json",
    }
    for binding, filename in names.items():
        _write_bytes_exclusive(
            input_dir / filename, bindings[binding]["verified_bytes"]
        )

    workspace_dir = output_dir / "workspace_snapshot"
    workspace_dir.mkdir(exist_ok=False)
    for relative, payload in verified_family["verified_workspace_files"].items():
        destination = (workspace_dir / relative).resolve()
        try:
            destination.relative_to(workspace_dir.resolve())
        except ValueError as exc:
            raise RunnerInputError("captured workspace path escapes snapshot") from exc
        destination.parent.mkdir(parents=True, exist_ok=True)
        _write_bytes_exclusive(destination, payload)
    return workspace_dir, input_dir / names["case_registry"]


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
        timeout_seconds: float,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        self._case_registry_path = Path(case_registry_path).resolve()
        self._condition_dir = Path(condition_dir).resolve()
        self._timeout_seconds = timeout_seconds
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
        outcome: dict[str, Any] = {}
        completed = threading.Event()

        def invoke() -> None:
            try:
                outcome["metric"] = score_toolformer_filter_patch(
                    diff_text=diff_text,
                    workspace=self._workspace,
                    case_registry_path=self._case_registry_path,
                    block="confirmation_v3",
                )
            except BaseException as exc:  # propagated on the caller thread
                outcome["error"] = exc
            finally:
                completed.set()

        worker = threading.Thread(target=invoke, daemon=True)
        worker.start()
        if not completed.wait(self._timeout_seconds):
            raise RunnerInputError(
                f"scorer timed out after {self._timeout_seconds:g} seconds"
            )
        if "error" in outcome:
            raise outcome["error"]
        metric = outcome["metric"]
        feedback = json.dumps(
            metric["public_summary"], sort_keys=True, separators=(",", ":")
        )
        return ScorerEvaluation(feedback, metric, patch_path)


def _serialize_result(result: Any) -> dict[str, Any]:
    return dataclasses.asdict(result)


def _validate_provider_turn_identity(
    result: Mapping[str, Any],
    *,
    expected_model_alias: str,
    seen_response_ids: set[str],
) -> None:
    turns = result.get("turns")
    if not isinstance(turns, (list, tuple)) or not turns:
        raise RunnerInputError("successful condition must contain model turns")
    for turn in turns:
        if not isinstance(turn, dict):
            raise RunnerInputError("model turn must be an object")
        _require_exact(
            turn.get("provider_model_id"),
            expected_model_alias,
            "provider model identity",
        )
        response_id = turn.get("provider_response_id")
        if (
            not isinstance(response_id, str)
            or not response_id
            or response_id in seen_response_ids
        ):
            raise RunnerInputError(
                "provider response identity is missing or duplicate"
            )
        seen_response_ids.add(response_id)


def _run_condition(
    *,
    condition: str,
    context: str,
    task_prompt: str,
    verified_family: Mapping[str, Any],
    output_dir: Path,
    transport: Any,
    retry_lineage_prefix: str,
    scorer_timeout_seconds: float,
    seen_provider_response_ids: set[str],
) -> dict[str, Any]:
    condition_dir = output_dir / condition
    bindings = verified_family["verified_bindings"]
    bridge = _ExclusiveToolformerScorerBridge(
        workspace=Path(verified_family["workspace_state"]["path"]),
        case_registry_path=Path(bindings["case_registry"]["path"]),
        condition_dir=condition_dir,
        timeout_seconds=scorer_timeout_seconds,
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
        raise RuntimeError(f"condition {condition} failed") from None
    if not condition_dir.exists():
        condition_dir.mkdir(exist_ok=False)
    serialized = _serialize_result(result)
    _validate_provider_turn_identity(
        serialized,
        expected_model_alias=verified_family["model_alias"],
        seen_response_ids=seen_provider_response_ids,
    )
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
    _require_exact(args.model_alias, REGISTERED_MODEL_ALIAS, "model_alias")
    _require_exact(args.max_attempts, REGISTERED_MAX_ATTEMPTS, "max_attempts")
    _require_exact(args.max_tokens, family["max_tokens"], "max_tokens")
    for name in ("timeout_seconds", "scorer_timeout_seconds"):
        value = getattr(args, name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise RunnerInputError(f"{name} must be positive")
    _require_exact(
        float(args.timeout_seconds),
        REGISTERED_TIMEOUT_SECONDS,
        "timeout_seconds",
    )
    _require_exact(
        float(args.scorer_timeout_seconds), 300.0, "scorer_timeout_seconds"
    )
    delay = args.retry_delay_seconds
    if (
        isinstance(delay, bool)
        or not isinstance(delay, (int, float))
        or not math.isfinite(delay)
        or delay < 0
    ):
        raise RunnerInputError("retry_delay_seconds must be nonnegative")
    _require_exact(
        float(delay),
        REGISTERED_RETRY_DELAY_SECONDS,
        "retry_delay_seconds",
    )


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
    _require_exact(
        base_url.rstrip("/"), verified["base_url"], "provider base URL"
    )
    contexts = _build_contexts(verified)
    task_prompt = verified["verified_bindings"]["task_prompt"][
        "verified_text"
    ].strip()
    if not task_prompt:
        raise RunnerInputError("task_prompt is empty")
    expected_public_config = {
        "base_url": verified["base_url"],
        "model_alias": args.model_alias,
        "wire_api": verified["wire_api"],
        "max_tokens": args.max_tokens,
        "timeout_seconds": args.timeout_seconds,
        "max_attempts": args.max_attempts,
        "retry_delay_seconds": args.retry_delay_seconds,
        "temperature": 0,
        "direct_connection": True,
        "proxy_policy": verified["proxy_policy"],
    }
    try:
        transport = transport_factory(
            base_url=base_url,
            api_key=api_key,
            model_alias=args.model_alias,
            wire_api=verified["wire_api"],
            max_tokens=args.max_tokens,
            timeout_seconds=args.timeout_seconds,
            max_attempts=args.max_attempts,
            retry_delay_seconds=args.retry_delay_seconds,
        )
        public_config = _public_provider_config(
            transport.public_config(),
            provider_label=verified["provider_label"],
            expected=expected_public_config,
        )
    except Exception:
        raise RunnerInputError("provider preflight failed") from None

    manifest = build_pair_manifest(
        verified_family=verified,
        condition_contexts=contexts,
        provider_config=public_config,
    )
    manifest["workspace_snapshot_path"] = (
        output_dir / "workspace_snapshot"
    ).as_posix()
    manifest["verified_inputs_path"] = (output_dir / "verified_inputs").as_posix()

    output_dir.mkdir(parents=True, exist_ok=False)
    _write_json_exclusive(output_dir / "pair_manifest.pre_run.json", manifest)
    workspace_snapshot, case_registry_snapshot = _materialize_verified_snapshots(
        output_dir, verified
    )

    execution_family = copy.deepcopy(verified)
    execution_family["workspace_state"]["path"] = workspace_snapshot.as_posix()
    execution_family["verified_bindings"]["case_registry"][
        "path"
    ] = case_registry_snapshot.as_posix()
    results: dict[str, Any] = {}
    seen_provider_response_ids: set[str] = set()
    for condition in verified["registered_replicate"]["condition_order"]:
        results[condition] = _run_condition(
            condition=condition,
            context=contexts[condition],
            task_prompt=task_prompt,
            verified_family=execution_family,
            output_dir=output_dir,
            transport=transport,
            retry_lineage_prefix=manifest["conditions"][condition][
                "retry_lineage_prefix"
            ],
            scorer_timeout_seconds=args.scorer_timeout_seconds,
            seen_provider_response_ids=seen_provider_response_ids,
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
    parser.add_argument("--model-alias", default=REGISTERED_MODEL_ALIAS)
    parser.add_argument("--base-url-env", default="EFFECTSLICE_DEEPSEEK_BASE_URL")
    parser.add_argument("--api-key-env", default="EFFECTSLICE_DEEPSEEK_API_KEY")
    parser.add_argument(
        "--timeout-seconds", type=float, default=REGISTERED_TIMEOUT_SECONDS
    )
    parser.add_argument("--scorer-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--max-tokens", type=int, default=REGISTERED_MAX_TOKENS)
    parser.add_argument(
        "--max-attempts", type=int, default=REGISTERED_MAX_ATTEMPTS
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=float,
        default=REGISTERED_RETRY_DELAY_SECONDS,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(json.dumps(run_bundle(args), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
