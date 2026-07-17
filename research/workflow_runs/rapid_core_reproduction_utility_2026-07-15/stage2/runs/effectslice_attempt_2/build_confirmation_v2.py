from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Callable


RUN_ROOT = Path(__file__).resolve().parent

import sys

sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.snap_mfse_cases import (  # noqa: E402
    build_case_registry as build_snap_case_registry,
)
from effectslice.toolformer_filter_cases import (  # noqa: E402
    build_case_registry as build_toolformer_case_registry,
)
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


TASK_SPECS: dict[str, dict[str, Any]] = {
    "snap_mfse": {
        "task_id": "SNAP-MFSE",
        "selected_candidate_id": "prefix_03",
        "case_builder": build_snap_case_registry,
        "schedule_seed": 2026071701,
        "full_artifact": RUN_ROOT / "artifacts" / "snap_mfse" / "full_artifact.md",
        "source_map": RUN_ROOT / "artifacts" / "snap_mfse" / "source_atom_map.json",
        "slice_registry": RUN_ROOT
        / "artifacts"
        / "snap_mfse"
        / "slices"
        / "slice_registry.json",
        "discovery_summary": RUN_ROOT / "derived" / "snap_mfse_discovery_summary.json",
        "task_prompt": RUN_ROOT / "artifacts" / "snap_mfse" / "task_prompt.md",
        "scorer": RUN_ROOT / "src" / "effectslice" / "snap_mfse_scorer.py",
        "case_generator": RUN_ROOT / "src" / "effectslice" / "snap_mfse_cases.py",
        "runner": RUN_ROOT / "run_snap_mfse_effectslice.py",
        "workspace": RUN_ROOT / "task_workspaces" / "snap_mfse_v1",
    },
    "toolformer_filter": {
        "task_id": "TOOLFORMER-FILTER",
        "selected_candidate_id": "prefix_01",
        "case_builder": build_toolformer_case_registry,
        "schedule_seed": 2026071702,
        "full_artifact": RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "full_artifact.md",
        "source_map": RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "source_atom_map.json",
        "slice_registry": RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "slices"
        / "slice_registry.json",
        "discovery_summary": RUN_ROOT
        / "derived"
        / "toolformer_filter_discovery_summary.json",
        "task_prompt": RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "task_prompt.md",
        "scorer": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py",
        "case_generator": RUN_ROOT
        / "src"
        / "effectslice"
        / "toolformer_filter_cases.py",
        "runner": RUN_ROOT / "run_toolformer_filter_effectslice.py",
        "workspace": RUN_ROOT / "task_workspaces" / "toolformer_filter_v1",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _stored_path(path: Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(RUN_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _add_binding(family: dict[str, Any], prefix: str, path: Path) -> None:
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise ValueError(f"confirmation-v2 input is missing: {resolved}")
    family[f"{prefix}_path"] = _stored_path(resolved)
    family[f"{prefix}_sha256"] = _sha256(resolved)


def _schedule(seed: int) -> list[dict[str, Any]]:
    orders = list(itertools.permutations(("B", "F", "S"))) * 3
    random.Random(seed).shuffle(orders)
    return [
        {
            "replicate_id": f"r{index:03d}",
            "condition_order": list(order),
        }
        for index, order in enumerate(orders, start=1)
    ]


def build_family(
    *,
    task_key: str,
    case_registry_output: Path,
    family_output: Path,
) -> dict[str, Any]:
    if task_key not in TASK_SPECS:
        raise ValueError(f"unsupported confirmation-v2 task: {task_key}")
    case_path = Path(case_registry_output).resolve()
    family_path = Path(family_output).resolve()
    for output in (case_path, family_path):
        if output.exists():
            raise ValueError(f"confirmation-v2 output already exists: {output}")
    spec = TASK_SPECS[task_key]
    case_builder: Callable[[Path], dict[str, Any]] = spec["case_builder"]
    case_registry = case_builder(case_path)
    confirmation_cases = case_registry.get("blocks", {}).get("confirmation_v2")
    if not isinstance(confirmation_cases, list) or len(confirmation_cases) != 64:
        raise ValueError("confirmation-v2 registry must contain 64 hidden cases")

    slice_registry_path = Path(spec["slice_registry"]).resolve()
    slice_registry = json.loads(slice_registry_path.read_text(encoding="utf-8"))
    selected = [
        row
        for row in slice_registry.get("candidates", [])
        if row.get("candidate_id") == spec["selected_candidate_id"]
    ]
    if len(selected) != 1:
        raise ValueError("confirmation-v2 candidate is not uniquely registered")
    selected_row = selected[0]
    selected_artifact = (
        slice_registry_path.parent / selected_row["artifact_path"]
    ).resolve()

    family: dict[str, Any] = {
        "schema_version": "effectslice-confirmation-v2-family.v1",
        "task_key": task_key,
        "task_id": spec["task_id"],
        "selected_candidate_id": spec["selected_candidate_id"],
        "retained_atom_ids": selected_row["retained_atom_ids"],
        "retained_scc_count": selected_row["retained_scc_count"],
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v2",
        "case_count": 64,
        "case_role": "clustered_within_run_checks",
        "statistical_unit": "independent_agent_run",
        "replicate_count": 18,
        "replicate_schedule": _schedule(int(spec["schedule_seed"])),
        "schedule_seed": int(spec["schedule_seed"]),
        "run_success_threshold": 0.95,
        "maximum_score_gap": 0.05,
        "alpha": 0.02,
        "minimum_prevalence": 0.8,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2 (user/provider label)",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "prior_confirmation_status": "contaminated_development",
        "confirmation_unsealed": False,
        "hypotheses": [
            {
                "hypothesis_id": "H_full_benefit_run_level",
                "indicator": "F_success and not B_success",
            },
            {
                "hypothesis_id": "H_slice_preservation_run_level",
                "indicator": "S_success equals F_success and abs(S_score-F_score)<=0.05",
            },
            {
                "hypothesis_id": "H_slice_benefit_run_level",
                "indicator": "S_success and not B_success",
            },
        ],
        "evidence_boundary": (
            "Registered before provider execution. Cases are clustered checks; "
            "probability bounds use independent agent runs only."
        ),
    }
    bindings = {
        "selected_artifact": selected_artifact,
        "discovery_summary": Path(spec["discovery_summary"]),
        "slice_registry": slice_registry_path,
        "case_registry": case_path,
        "source_map": Path(spec["source_map"]),
        "task_prompt": Path(spec["task_prompt"]),
        "scorer": Path(spec["scorer"]),
        "runner": Path(spec["runner"]),
        "scheduler": RUN_ROOT / "run_confirmation_v2.py",
        "aci_runner": RUN_ROOT / "src" / "effectslice" / "aci_runner.py",
        "aci_protocol": RUN_ROOT / "src" / "effectslice" / "aci_protocol.py",
        "evidence_binding": RUN_ROOT / "src" / "effectslice" / "evidence_binding.py",
        "transport": RUN_ROOT / "run_swe_effectslice.py",
        "case_generator": Path(spec["case_generator"]),
        "family_builder": RUN_ROOT / "build_confirmation_v2.py",
        "full_artifact": Path(spec["full_artifact"]),
    }
    for prefix, path in bindings.items():
        _add_binding(family, prefix, path)
    workspace_state = workspace_tree_digest(Path(spec["workspace"]))
    family["workspace_path"] = _stored_path(Path(spec["workspace"]))
    family["workspace_tree_sha256"] = workspace_state["sha256"]
    family["workspace_file_count"] = workspace_state["file_count"]
    family["workspace_total_bytes"] = workspace_state["total_bytes"]

    family_path.parent.mkdir(parents=True, exist_ok=True)
    with family_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(family, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return family


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a confirmation-v2 family")
    parser.add_argument("--task-key", choices=tuple(TASK_SPECS), required=True)
    parser.add_argument("--case-registry-output", type=Path, required=True)
    parser.add_argument("--family-output", type=Path, required=True)
    args = parser.parse_args()
    family = build_family(
        task_key=args.task_key,
        case_registry_output=args.case_registry_output,
        family_output=args.family_output,
    )
    print(
        json.dumps(
            {
                "task_id": family["task_id"],
                "case_count": family["case_count"],
                "replicate_count": family["replicate_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
