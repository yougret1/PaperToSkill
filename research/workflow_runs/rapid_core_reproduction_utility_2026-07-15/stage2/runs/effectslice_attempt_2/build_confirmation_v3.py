from __future__ import annotations

import argparse
import copy
import json
import sys
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


CASE_SEEDS = tuple(range(36_000, 36_064))
CASE_CONFIG_ID = "toolformer_filter_confirmation_v3_seeds_36000_36063"
PLANNED_BINDING_STATUS = "planned_before_preregistration"
REGISTERED_EVIDENCE_BOUNDARY = "registered_final_only_confirmation_v3"
T06_MARKDOWN = (
    "6. **Restate the shared selection invariant** (`T06`)\n"
    "   Apply the same inclusive `margin >= tau_filter` rule independently to every\n"
    "   proposed call and preserve the proposals' original order in the returned\n"
    "   decisions. This restates the registered T04/T05 invariant and introduces no\n"
    "   new computation.\n"
)
CONTROL_SPECS: dict[str, dict[str, Any]] = {
    "identity": {
        "strict_subset": False,
        "calibration_role": "identity_instrumentation_only",
        "schedule_seed": 2026071801,
        "replicate_count": 6,
        "admission_rule": "descriptive_only",
        "required_joint_events_for_admission": None,
    },
    "planted": {
        "strict_subset": True,
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
) -> dict[str, Any]:
    resolved = Path(path).resolve()
    stored = _stored_path(resolved, run_root)
    if resolved.is_file():
        return {"path": stored, "sha256": sha256_file(resolved), "status": "bound"}
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
) -> None:
    record = _binding_record(path, run_root, allow_planned=allow_planned)
    family["bindings"][prefix] = record
    family[f"{prefix}_path"] = record["path"]
    family[f"{prefix}_status"] = record["status"]
    if "sha256" in record:
        family[f"{prefix}_sha256"] = record["sha256"]


def _build_case_registry() -> dict[str, Any]:
    cases = [generate_case(seed) for seed in CASE_SEEDS]
    if len(cases) != 64:
        raise ValueError("confirmation-v3 registry must contain 64 cases")
    return {
        "schema_version": "effectslice-toolformer-filter-case-registry.v3",
        "task_id": "TOOLFORMER-FILTER",
        "generator_api": "effectslice.toolformer_filter_cases.generate_case",
        "generator_config_id": CASE_CONFIG_ID,
        "generator_inputs": {
            "seeds": list(CASE_SEEDS),
            "seed_start_inclusive": CASE_SEEDS[0],
            "seed_stop_exclusive": CASE_SEEDS[-1] + 1,
        },
        "generation_mechanism": (
            "Call generate_case(seed) once for each declared integer seed in "
            "ascending order; no hidden case values are copied or hand-authored."
        ),
        "blocks": {"confirmation_v3": cases},
        "case_role": "clustered",
        "evidence_boundary": REGISTERED_EVIDENCE_BOUNDARY,
    }


def _build_source_map(
    original: dict[str, Any],
    control: str,
    full_artifact_path: Path,
    selected_artifact_path: Path,
) -> dict[str, Any]:
    source_map = copy.deepcopy(original)
    source_map["schema_version"] = "effectslice-toolformer-filter-source-atom-map.v3"
    source_map["control"] = control
    source_map["full_artifact_path"] = full_artifact_path.name
    source_map["full_artifact_sha256"] = sha256_file(full_artifact_path)
    source_map["selected_artifact_path"] = selected_artifact_path.name
    source_map["selected_artifact_sha256"] = sha256_file(selected_artifact_path)
    source_map["selected_artifact_atom_ids"] = [
        "T01",
        "T02",
        "T03",
        "T04",
        "T05",
    ]
    source_map["selected_artifact_dependency_closed"] = True
    source_map["selected_artifact_strict_subset"] = control == "planted"
    source_map["evidence_boundary"] = REGISTERED_EVIDENCE_BOUNDARY

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


def _is_registered_output(output_dir: Path, run_root: Path) -> bool:
    registered_root = (
        Path(run_root)
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
    ).resolve()
    try:
        Path(output_dir).resolve().relative_to(registered_root)
    except ValueError:
        return False
    return True


def build_family(
    control: str,
    output_dir: Path,
    *,
    run_root: Path = RUN_ROOT,
) -> dict[str, Any]:
    if control not in CONTROL_SPECS:
        raise ValueError(f"unsupported confirmation-v3 control: {control}")

    root = Path(run_root).resolve()
    destination = Path(output_dir).resolve()
    artifact_root = root / "artifacts" / "toolformer_filter"
    original_artifact = artifact_root / "full_artifact.md"
    original_source_map = artifact_root / "source_atom_map.json"
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
    allow_planned = not _is_registered_output(destination, root)
    if not allow_planned:
        for path in planned_paths.values():
            if not path.is_file():
                raise FileNotFoundError(
                    f"final confirmation-v3 preregistration binding is missing: {path}"
                )

    original_bytes = original_artifact.read_bytes()
    full_bytes = (
        original_bytes
        if control == "identity"
        else original_bytes + b"\n" + T06_MARKDOWN.encode("utf-8")
    )
    selected_bytes = original_bytes
    original_map = json.loads(original_source_map.read_text(encoding="utf-8"))
    case_registry = _build_case_registry()
    workspace_state = workspace_tree_digest(workspace)
    spec = CONTROL_SPECS[control]

    destination.mkdir(parents=True, exist_ok=True)
    full_artifact_output = destination / "full_artifact.md"
    selected_artifact_output = destination / "selected_artifact.md"
    source_map_output = destination / "source_atom_map.json"
    case_registry_output = destination / "case_registry.json"
    family_output = destination / "family.json"

    _write_bytes_exclusive(full_artifact_output, full_bytes)
    _write_bytes_exclusive(selected_artifact_output, selected_bytes)
    source_map = _build_source_map(
        original_map,
        control,
        full_artifact_output,
        selected_artifact_output,
    )
    _write_json_exclusive(source_map_output, source_map)
    _write_json_exclusive(case_registry_output, case_registry)

    family: dict[str, Any] = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "control": control,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "strict_subset": spec["strict_subset"],
        "calibration_role": spec["calibration_role"],
        "retained_atom_ids": ["T01", "T02", "T03", "T04", "T05"],
        "retained_scc_count": 5,
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
        "comparison_role": REGISTERED_EVIDENCE_BOUNDARY,
        "evidence_boundary": REGISTERED_EVIDENCE_BOUNDARY,
        "bindings": {},
    }
    binding_paths = {
        "full_artifact": full_artifact_output,
        "selected_artifact": selected_artifact_output,
        "source_map": source_map_output,
        "case_registry": case_registry_output,
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
            allow_planned=prefix in planned_paths and allow_planned,
        )

    prompt_path = _stored_path(task_prompt, root)
    family["task_prompt_path"] = prompt_path
    family["task_prompt_status"] = "bound"
    family["task_prompt_file_sha256"] = sha256_file(task_prompt)
    family["task_prompt_canonical_text_sha256"] = sha256_canonical_text(task_prompt)
    family["bindings"]["task_prompt"] = {
        "path": prompt_path,
        "file_sha256": family["task_prompt_file_sha256"],
        "canonical_text_sha256": family["task_prompt_canonical_text_sha256"],
        "status": "bound",
    }
    family["workspace_path"] = _stored_path(workspace, root)
    family["workspace_tree_sha256"] = workspace_state["sha256"]
    family["workspace_file_count"] = workspace_state["file_count"]
    family["workspace_total_bytes"] = workspace_state["total_bytes"]
    family["workspace_excluded_directory_names"] = workspace_state[
        "excluded_directory_names"
    ]

    _write_json_exclusive(family_output, family)
    return family


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a write-once EffectSlice confirmation-v3 family"
    )
    parser.add_argument("--control", choices=tuple(CONTROL_SPECS), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    family = build_family(args.control, args.output_dir)
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
