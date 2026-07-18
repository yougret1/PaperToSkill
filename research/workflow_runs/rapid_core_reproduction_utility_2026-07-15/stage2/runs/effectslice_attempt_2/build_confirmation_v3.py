from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.confirmation_v3 import (  # noqa: E402
    balanced_schedule,
    sha256_canonical_text,
    sha256_file,
)
from effectslice.toolformer_filter_cases import generate_case  # noqa: E402
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


CASE_SEEDS = tuple(
    seed for seed in range(36_000, 36_200) if seed % 7 in {4, 5, 6}
)[:64]
CASE_CONFIG_ID = (
    f"toolformer_filter_confirmation_v3_tail_noise_seeds_"
    f"{CASE_SEEDS[0]}_{CASE_SEEDS[-1]}"
)
PLANNED_BINDING_STATUS = "planned_before_preregistration"
REGISTERED_EVIDENCE_BOUNDARY = "registered_final_only_confirmation_v3"
DRAFT_COMPARISON_ROLE = "planned_confirmation_v3_draft"
DRAFT_EVIDENCE_BOUNDARY = "draft_incomplete_confirmation_v3"
ATOM_ID_PATTERN = re.compile(r"\(`(T\d+)`\)")
T06_MARKDOWN = (
    "6. **Restate the shared selection invariant** (`T06`)\n"
    "   Apply the same inclusive `margin >= tau_filter` rule independently to every\n"
    "   proposed call and preserve the proposals' original order in the returned\n"
    "   decisions. This restates the registered T04/T05 invariant and introduces no\n"
    "   new computation.\n"
)
CONTROL_SPECS: dict[str, dict[str, Any]] = {
    "identity": {
        "calibration_role": "identity_instrumentation_only",
        "schedule_seed": 2026071801,
        "replicate_count": 6,
        "admission_rule": "descriptive_only",
        "required_joint_events_for_admission": None,
    },
    "planted": {
        "calibration_role": "planted_redundancy_positive_control",
        "schedule_seed": 2026071802,
        "replicate_count": 18,
        "admission_rule": "all_registered_joint_events",
        "required_joint_events_for_admission": 18,
    },
}


def _stored_path(path: Path, run_root: Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(Path(run_root).resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _write_bytes_exclusive(path: Path, payload: bytes) -> None:
    with Path(path).open("xb") as handle:
        handle.write(payload)


def _write_json_exclusive(path: Path, payload: dict[str, Any]) -> None:
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _binding_record(
    path: Path,
    run_root: Path,
    *,
    allow_planned: bool,
    digest_path: Path | None = None,
) -> dict[str, Any]:
    resolved = Path(path).resolve()
    stored = _stored_path(resolved, run_root)
    digest_source = Path(digest_path).resolve() if digest_path else resolved
    if digest_source.is_file():
        return {
            "path": stored,
            "sha256": sha256_file(digest_source),
            "status": "bound",
        }
    if not allow_planned:
        raise FileNotFoundError(f"confirmation-v3 binding is missing: {resolved}")
    return {"path": stored, "status": PLANNED_BINDING_STATUS}


def _register_binding(
    family: dict[str, Any],
    prefix: str,
    path: Path,
    run_root: Path,
    *,
    allow_planned: bool = False,
    digest_path: Path | None = None,
) -> None:
    record = _binding_record(
        path,
        run_root,
        allow_planned=allow_planned,
        digest_path=digest_path,
    )
    family["bindings"][prefix] = record
    family[f"{prefix}_path"] = record["path"]
    family[f"{prefix}_status"] = record["status"]
    if "sha256" in record:
        family[f"{prefix}_sha256"] = record["sha256"]


def _canonical_case_payload_hash(case: dict[str, Any]) -> str:
    payload = {
        key: value for key, value in case.items() if key not in {"case_id", "seed"}
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _all_registry_cases(registry: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = registry.get("blocks")
    if not isinstance(blocks, dict):
        raise ValueError("case registry blocks must be an object")
    cases: list[dict[str, Any]] = []
    for block in blocks.values():
        if not isinstance(block, list) or not all(isinstance(case, dict) for case in block):
            raise ValueError("case registry blocks must contain case objects")
        cases.extend(block)
    return cases


def _validate_case_independence(
    registry: dict[str, Any],
    v2_registry_path: Path,
) -> None:
    cases = registry["blocks"]["confirmation_v3"]
    seeds = registry["generator_inputs"]["seeds"]
    if len(cases) != 64 or len(seeds) != 64:
        raise ValueError("confirmation-v3 registry must contain 64 cases")
    case_seeds = [case.get("seed") for case in cases]
    case_ids = [case.get("case_id") for case in cases]
    if case_seeds != seeds or len(set(case_seeds)) != 64:
        raise ValueError("confirmation-v3 case seed IDs must be unique and registered")
    if len(set(case_ids)) != 64:
        raise ValueError("confirmation-v3 case IDs must be unique")
    if not v2_registry_path.is_file():
        return

    v2_registry = json.loads(v2_registry_path.read_text(encoding="utf-8"))
    v2_cases = _all_registry_cases(v2_registry)
    v2_seeds = {case.get("seed") for case in v2_cases}
    overlap_seeds = set(case_seeds) & v2_seeds
    if overlap_seeds:
        raise ValueError(
            f"confirmation-v3 and v2 case seed overlap: {sorted(overlap_seeds)}"
        )
    v3_payloads = {_canonical_case_payload_hash(case) for case in cases}
    v2_payloads = {_canonical_case_payload_hash(case) for case in v2_cases}
    if v3_payloads & v2_payloads:
        raise ValueError("confirmation-v3 case payload overlap with v2")


def _build_case_registry(
    *,
    registration_status: str,
    evidence_boundary: str,
    v2_registry_path: Path,
) -> dict[str, Any]:
    cases = [generate_case(seed) for seed in CASE_SEEDS]
    registry = {
        "schema_version": "effectslice-toolformer-filter-case-registry.v3",
        "task_id": "TOOLFORMER-FILTER",
        "generator_api": "effectslice.toolformer_filter_cases.generate_case",
        "generator_config_id": CASE_CONFIG_ID,
        "generator_inputs": {
            "seeds": list(CASE_SEEDS),
            "candidate_seed_range_start_inclusive": 36_000,
            "candidate_seed_range_stop_exclusive": 36_200,
            "selection_predicate": "seed % 7 in {4, 5, 6}",
        },
        "generation_mechanism": (
            "Select the first 64 ascending seeds from [36000, 36200) satisfying "
            "seed % 7 in {4, 5, 6}, then call generate_case(seed) once for each; "
            "the supported generator's seeded tail-noise path makes the payloads "
            "distinct without copied or hand-authored hidden values."
        ),
        "blocks": {"confirmation_v3": cases},
        "case_role": "clustered",
        "registration_status": registration_status,
        "evidence_boundary": evidence_boundary,
    }
    _validate_case_independence(registry, v2_registry_path)
    return registry


def _artifact_atom_ids(payload: bytes, label: str) -> list[str]:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} artifact must be UTF-8") from exc
    atom_ids = ATOM_ID_PATTERN.findall(text)
    if not atom_ids or len(atom_ids) != len(set(atom_ids)):
        raise ValueError(f"{label} artifact atom IDs must be unique and nonempty")
    return atom_ids


def _scc_count(atom_ids: list[str], requires: dict[str, list[str]]) -> int:
    nodes = set(atom_ids)
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    count = 0

    def visit(atom_id: str) -> None:
        nonlocal count, index
        indices[atom_id] = index
        lowlinks[atom_id] = index
        index += 1
        stack.append(atom_id)
        on_stack.add(atom_id)
        for dependency in requires[atom_id]:
            if dependency not in nodes:
                continue
            if dependency not in indices:
                visit(dependency)
                lowlinks[atom_id] = min(lowlinks[atom_id], lowlinks[dependency])
            elif dependency in on_stack:
                lowlinks[atom_id] = min(lowlinks[atom_id], indices[dependency])
        if lowlinks[atom_id] != indices[atom_id]:
            return
        while True:
            member = stack.pop()
            on_stack.remove(member)
            if member == atom_id:
                break
        count += 1

    for atom_id in atom_ids:
        if atom_id not in indices:
            visit(atom_id)
    return count


def _validate_artifact_truth(
    control: str,
    full_bytes: bytes,
    selected_bytes: bytes,
    source_map: dict[str, Any],
) -> dict[str, Any]:
    full_atom_ids = _artifact_atom_ids(full_bytes, "F")
    selected_atom_ids = _artifact_atom_ids(selected_bytes, "S")
    full_atoms = set(full_atom_ids)
    selected_atoms = set(selected_atom_ids)
    strict_subset = selected_atoms < full_atoms
    if control == "planted" and not strict_subset:
        raise ValueError("planted S must be a strict subset of F")
    if control == "identity" and selected_atoms != full_atoms:
        raise ValueError("identity F and S must have identical atom membership")

    atoms = source_map.get("atoms")
    if not isinstance(atoms, list) or not all(isinstance(atom, dict) for atom in atoms):
        raise ValueError("source map atoms must be objects")
    map_atom_ids = [atom.get("atom_id") for atom in atoms]
    if any(not isinstance(atom_id, str) for atom_id in map_atom_ids):
        raise ValueError("source map atom IDs must be strings")
    if len(map_atom_ids) != len(set(map_atom_ids)):
        raise ValueError("source map atom IDs must be unique")
    if full_atom_ids != map_atom_ids:
        raise ValueError("F artifact atom membership must exactly match the source map")
    if not selected_atoms.issubset(full_atoms):
        raise ValueError("S artifact atoms must be contained in F")

    raw_requires = source_map.get("requires")
    if not isinstance(raw_requires, dict) or set(raw_requires) != full_atoms:
        raise ValueError("source map requires keys must exactly match its atoms")
    requires: dict[str, list[str]] = {}
    for atom_id in full_atom_ids:
        dependencies = raw_requires[atom_id]
        if not isinstance(dependencies, list) or not all(
            isinstance(dependency, str) for dependency in dependencies
        ):
            raise ValueError(f"dependencies for {atom_id} must be atom ID lists")
        for dependency in dependencies:
            if dependency not in full_atoms:
                raise ValueError(
                    f"source map dependency for {atom_id} refers to missing atom {dependency}"
                )
        requires[atom_id] = dependencies

    edges = source_map.get("dependency_edges")
    if not isinstance(edges, list):
        raise ValueError("source map dependency_edges must be a list")
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("source map dependency edges must be objects")
        for endpoint in (edge.get("from"), edge.get("to")):
            if endpoint not in full_atoms:
                raise ValueError(
                    f"source map dependency edge refers to missing atom {endpoint}"
                )

    for atom_id in selected_atom_ids:
        missing = set(requires[atom_id]) - selected_atoms
        if missing:
            raise ValueError(
                f"S artifact is not dependency-closed at {atom_id}: {sorted(missing)}"
            )
    return {
        "full_atom_ids": full_atom_ids,
        "selected_atom_ids": selected_atom_ids,
        "strict_subset": strict_subset,
        "full_scc_count": _scc_count(full_atom_ids, requires),
        "selected_scc_count": _scc_count(selected_atom_ids, requires),
    }


def _build_source_map(
    original: dict[str, Any],
    control: str,
    full_artifact_path: Path,
    selected_artifact_path: Path,
    *,
    registration_status: str,
    evidence_boundary: str,
) -> dict[str, Any]:
    source_map = copy.deepcopy(original)
    source_map["schema_version"] = "effectslice-toolformer-filter-source-atom-map.v3"
    source_map["control"] = control
    source_map["full_artifact_path"] = full_artifact_path.name
    source_map["full_artifact_sha256"] = sha256_file(full_artifact_path)
    source_map["selected_artifact_path"] = selected_artifact_path.name
    source_map["selected_artifact_sha256"] = sha256_file(selected_artifact_path)
    source_map["registration_status"] = registration_status
    source_map["evidence_boundary"] = evidence_boundary

    if control == "planted":
        atoms = {atom["atom_id"]: atom for atom in source_map["atoms"]}
        source_map["atoms"].append(
            {
                "atom_id": "T06",
                "title": "Restate the shared selection invariant",
                "instruction": (
                    "Apply the same inclusive margin >= tau_filter rule independently "
                    "to every proposed call and preserve the proposals' original order "
                    "in the returned decisions. This restates the registered T04/T05 "
                    "invariant and introduces no new computation."
                ),
                "contract_role": "redundant_inclusive_order_restatement",
                "novel": False,
                "redundancy_status": "registered_redundant",
                "redundant_with_atom_ids": ["T04", "T05"],
                "source_spans": copy.deepcopy(
                    atoms["T04"]["source_spans"] + atoms["T05"]["source_spans"]
                ),
            }
        )
        source_map["requires"]["T06"] = ["T04", "T05"]
        source_map["dependency_edges"].extend(
            [
                {"from": "T06", "to": "T04"},
                {"from": "T06", "to": "T05"},
            ]
        )
    return source_map


def _validate_output_path(control: str, output_dir: Path, run_root: Path) -> Path:
    expected = (
        Path(run_root)
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / control
    ).resolve()
    destination = Path(output_dir).resolve()
    if destination != expected:
        raise ValueError(
            f"output_dir must be the exact confirmation-v3 control directory: {expected}"
        )
    if destination.exists():
        raise FileExistsError(destination)
    return destination


def build_family(
    control: str,
    output_dir: Path,
    *,
    run_root: Path = RUN_ROOT,
    require_complete_bindings: bool = False,
) -> dict[str, Any]:
    if control not in CONTROL_SPECS:
        raise ValueError(f"unsupported confirmation-v3 control: {control}")

    root = Path(run_root).resolve()
    destination = _validate_output_path(control, output_dir, root)
    artifact_root = root / "artifacts" / "toolformer_filter"
    original_artifact = artifact_root / "full_artifact.md"
    original_source_map = artifact_root / "source_atom_map.json"
    v2_case_registry = artifact_root / "case_registry_v2_r2.json"
    task_prompt = artifact_root / "task_prompt.md"
    workspace = root / "task_workspaces" / "toolformer_filter_v1"
    required_inputs = (
        original_artifact,
        original_source_map,
        task_prompt,
        root / "src" / "effectslice" / "toolformer_filter_scorer.py",
        root / "src" / "effectslice" / "aci_runner.py",
        root / "src" / "effectslice" / "aci_protocol.py",
        root / "src" / "effectslice" / "evidence_binding.py",
        root / "run_swe_effectslice.py",
        root / "src" / "effectslice" / "toolformer_filter_cases.py",
    )
    for path in required_inputs:
        if not path.is_file():
            raise FileNotFoundError(f"confirmation-v3 input is missing: {path}")
    if not workspace.is_dir():
        raise FileNotFoundError(f"confirmation-v3 workspace is missing: {workspace}")

    planned_paths = {
        "runner": root / "run_toolformer_filter_confirmation_v3.py",
        "scheduler": root / "run_confirmation_v3.py",
        "analyzer": root / "analyze_confirmation_v3.py",
    }
    missing_executables = [
        (prefix, path) for prefix, path in planned_paths.items() if not path.is_file()
    ]
    if require_complete_bindings and missing_executables:
        missing = ", ".join(f"{prefix}={path}" for prefix, path in missing_executables)
        raise FileNotFoundError(
            f"confirmation-v3 complete binding is missing: {missing}"
        )
    registration_status = "draft_incomplete" if missing_executables else "complete"
    if registration_status == "complete":
        comparison_role = REGISTERED_EVIDENCE_BOUNDARY
        evidence_boundary = REGISTERED_EVIDENCE_BOUNDARY
    else:
        comparison_role = DRAFT_COMPARISON_ROLE
        evidence_boundary = DRAFT_EVIDENCE_BOUNDARY

    original_bytes = original_artifact.read_bytes()
    full_bytes = (
        original_bytes
        if control == "identity"
        else original_bytes + b"\n" + T06_MARKDOWN.encode("utf-8")
    )
    selected_bytes = original_bytes
    original_map = json.loads(original_source_map.read_text(encoding="utf-8"))
    case_registry = _build_case_registry(
        registration_status=registration_status,
        evidence_boundary=evidence_boundary,
        v2_registry_path=v2_case_registry,
    )
    workspace_state = workspace_tree_digest(workspace)
    spec = CONTROL_SPECS[control]

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{control}.staging-",
            dir=destination.parent,
        )
    ).resolve()
    try:
        full_artifact_staging = staging / "full_artifact.md"
        selected_artifact_staging = staging / "selected_artifact.md"
        source_map_staging = staging / "source_atom_map.json"
        case_registry_staging = staging / "case_registry.json"
        family_staging = staging / "family.json"

        _write_bytes_exclusive(full_artifact_staging, full_bytes)
        _write_bytes_exclusive(selected_artifact_staging, selected_bytes)
        source_map = _build_source_map(
            original_map,
            control,
            full_artifact_staging,
            selected_artifact_staging,
            registration_status=registration_status,
            evidence_boundary=evidence_boundary,
        )
        artifact_truth = _validate_artifact_truth(
            control,
            full_bytes,
            selected_bytes,
            source_map,
        )
        source_map["full_artifact_atom_ids"] = artifact_truth["full_atom_ids"]
        source_map["full_artifact_unit_count"] = len(artifact_truth["full_atom_ids"])
        source_map["full_artifact_scc_count"] = artifact_truth["full_scc_count"]
        source_map["selected_artifact_atom_ids"] = artifact_truth[
            "selected_atom_ids"
        ]
        source_map["selected_artifact_unit_count"] = len(
            artifact_truth["selected_atom_ids"]
        )
        source_map["selected_artifact_scc_count"] = artifact_truth[
            "selected_scc_count"
        ]
        source_map["selected_artifact_dependency_closed"] = True
        source_map["selected_artifact_strict_subset"] = artifact_truth[
            "strict_subset"
        ]
        _write_json_exclusive(source_map_staging, source_map)
        _write_json_exclusive(case_registry_staging, case_registry)

        family: dict[str, Any] = {
            "schema_version": "effectslice-confirmation-v3-family.v1",
            "registration_status": registration_status,
            "control": control,
            "task_key": "toolformer_filter",
            "task_id": "TOOLFORMER-FILTER",
            "conditions": ["B", "F", "S"],
            "strict_subset": artifact_truth["strict_subset"],
            "calibration_role": spec["calibration_role"],
            "retained_atom_ids": artifact_truth["selected_atom_ids"],
            "retained_unit_count": len(artifact_truth["selected_atom_ids"]),
            "retained_scc_count": artifact_truth["selected_scc_count"],
            "case_block": "confirmation_v3",
            "case_count": 64,
            "case_role": "clustered",
            "case_generator_config_id": CASE_CONFIG_ID,
            "statistical_unit": "registered_matched_block",
            "decision_basis": "finite_registered_schedule",
            "primary_event": "joint_substitution_event",
            "independence_verified": False,
            "iid_conditional_reference": {"label": "iid_conditional_only"},
            "replicate_count": spec["replicate_count"],
            "replicate_schedule": balanced_schedule(
                seed=spec["schedule_seed"],
                replicate_count=spec["replicate_count"],
            ),
            "schedule_seed": spec["schedule_seed"],
            "run_success_threshold": 0.95,
            "maximum_shortfall": 0.05,
            "admission_rule": spec["admission_rule"],
            "required_joint_events_for_admission": spec[
                "required_joint_events_for_admission"
            ],
            "private_score_policy": "final_only",
            "maximum_transport_attempts": 5,
            "provider_label": "DeepSeek V3.2",
            "model_alias": "deepseek-v4-flash",
            "wire_api": "openai_chat_completions",
            "temperature": 0,
            "max_tokens": 8192,
            "fresh_provider_conversation_per_condition": True,
            "comparison_role": comparison_role,
            "evidence_boundary": evidence_boundary,
            "bindings": {},
        }
        final_outputs = {
            "full_artifact": destination / "full_artifact.md",
            "selected_artifact": destination / "selected_artifact.md",
            "source_map": destination / "source_atom_map.json",
            "case_registry": destination / "case_registry.json",
        }
        staging_outputs = {
            "full_artifact": full_artifact_staging,
            "selected_artifact": selected_artifact_staging,
            "source_map": source_map_staging,
            "case_registry": case_registry_staging,
        }
        binding_paths = {
            **final_outputs,
            "scorer": root / "src" / "effectslice" / "toolformer_filter_scorer.py",
            **planned_paths,
            "aci_runner": root / "src" / "effectslice" / "aci_runner.py",
            "aci_protocol": root / "src" / "effectslice" / "aci_protocol.py",
            "evidence_binding": root / "src" / "effectslice" / "evidence_binding.py",
            "transport": root / "run_swe_effectslice.py",
            "case_generator": root / "src" / "effectslice" / "toolformer_filter_cases.py",
        }
        for prefix, path in binding_paths.items():
            _register_binding(
                family,
                prefix,
                path,
                root,
                allow_planned=prefix in planned_paths,
                digest_path=staging_outputs.get(prefix),
            )

        prompt_path = _stored_path(task_prompt, root)
        family["task_prompt_path"] = prompt_path
        family["task_prompt_status"] = "bound"
        family["task_prompt_file_sha256"] = sha256_file(task_prompt)
        family["task_prompt_canonical_text_sha256"] = sha256_canonical_text(
            task_prompt
        )
        family["bindings"]["task_prompt"] = {
            "path": prompt_path,
            "file_sha256": family["task_prompt_file_sha256"],
            "canonical_text_sha256": family[
                "task_prompt_canonical_text_sha256"
            ],
            "status": "bound",
        }
        family["workspace_path"] = _stored_path(workspace, root)
        family["workspace_tree_sha256"] = workspace_state["sha256"]
        family["workspace_file_count"] = workspace_state["file_count"]
        family["workspace_total_bytes"] = workspace_state["total_bytes"]
        family["workspace_excluded_directory_names"] = workspace_state[
            "excluded_directory_names"
        ]

        _write_json_exclusive(family_staging, family)
        staging.rename(destination)
        return family
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a write-once EffectSlice confirmation-v3 family"
    )
    parser.add_argument("--control", choices=tuple(CONTROL_SPECS), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--require-complete-bindings", action="store_true")
    args = parser.parse_args()
    family = build_family(
        args.control,
        args.output_dir,
        require_complete_bindings=args.require_complete_bindings,
    )
    print(
        json.dumps(
            {
                "control": family["control"],
                "case_count": family["case_count"],
                "replicate_count": family["replicate_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
