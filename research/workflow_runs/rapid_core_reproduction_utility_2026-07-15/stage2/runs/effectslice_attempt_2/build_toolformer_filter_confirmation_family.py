from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(RUN_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def build_confirmation_family(
    *,
    discovery_summary_path: Path,
    slice_registry_path: Path,
    case_registry_path: Path,
    config_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    discovery_path = Path(discovery_summary_path).resolve()
    slice_path = Path(slice_registry_path).resolve()
    case_path = Path(case_registry_path).resolve()
    config_file = Path(config_path).resolve()
    for path in (discovery_path, slice_path, case_path, config_file):
        if not path.is_file():
            raise ValueError(f"confirmation family input is missing: {path}")
    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    if discovery.get("task_disposition") != "candidate_locked_for_confirmation":
        raise ValueError("discovery has not locked a candidate for confirmation")
    if discovery.get("deletion_audit_complete") is not True:
        raise ValueError("deletion audit must be complete before confirmation")
    selected_id = discovery.get("selected_candidate_id")
    registry = json.loads(slice_path.read_text(encoding="utf-8"))
    matches = [
        row for row in registry.get("candidates", []) if row.get("candidate_id") == selected_id
    ]
    if len(matches) != 1:
        raise ValueError("selected candidate is not uniquely registered")
    selected = matches[0]
    selected_artifact = (slice_path.parent / selected["artifact_path"]).resolve()
    if not selected_artifact.is_file():
        raise ValueError("selected slice artifact is missing")
    if _sha256(selected_artifact) != selected.get("artifact_sha256"):
        raise ValueError("selected slice artifact digest mismatch")
    cases = json.loads(case_path.read_text(encoding="utf-8"))
    confirmation_cases = cases.get("blocks", {}).get("confirmation")
    if not isinstance(confirmation_cases, list) or not confirmation_cases:
        raise ValueError("confirmation case block is missing")
    config = json.loads(config_file.read_text(encoding="utf-8"))
    statistics = config["statistics"]
    expected_count = int(statistics["zero_violation_confirmation_pairs"])
    if len(confirmation_cases) != expected_count:
        raise ValueError("confirmation case count does not match the frozen statistics")

    family = {
        "schema_version": "effectslice-toolformer-filter-confirmation-family.v1",
        "task_id": "TOOLFORMER-FILTER",
        "selected_candidate_id": selected_id,
        "retained_atom_ids": selected["retained_atom_ids"],
        "retained_scc_count": selected["retained_scc_count"],
        "selected_artifact_path": _relative(selected_artifact),
        "selected_artifact_sha256": _sha256(selected_artifact),
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation",
        "case_count": expected_count,
        "alpha": float(statistics["alpha_C"]),
        "epsilon": float(statistics["epsilon"]),
        "minimum_beneficial_prevalence": float(
            statistics["minimum_beneficial_prevalence"]
        ),
        "maximum_violation_rate": float(statistics["maximum_violation_rate"]),
        "discovery_summary_path": _relative(discovery_path),
        "discovery_summary_sha256": _sha256(discovery_path),
        "slice_registry_path": _relative(slice_path),
        "slice_registry_sha256": _sha256(slice_path),
        "case_registry_path": _relative(case_path),
        "case_registry_sha256": _sha256(case_path),
        "hypotheses": [
            {
                "hypothesis_id": "H_preserve_F",
                "metric": "casewise_S_not_equal_F",
                "acceptance_rule": (
                    "zero observed mismatches and one-sided Clopper-Pearson upper "
                    "bound <= maximum_violation_rate"
                ),
            },
            {
                "hypothesis_id": "H_benefit_over_B",
                "metric": "casewise_S_minus_B_at_least_delta_min",
                "acceptance_rule": (
                    "one-sided Clopper-Pearson lower bound >= "
                    "minimum_beneficial_prevalence"
                ),
            },
            {
                "hypothesis_id": "H_hard_constraints",
                "metric": "S_contract_passed",
                "acceptance_rule": "candidate contract passes",
            },
        ],
        "confirmation_unsealed": False,
        "general_effectslice_claim_ready": False,
        "evidence_boundary": (
            "Frozen after discovery and before any confirmation provider run. "
            "Passing supports only a task-local confirmation claim."
        ),
    }
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(family, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return family


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze TOOLFORMER-FILTER confirmation family")
    parser.add_argument(
        "--discovery-summary",
        type=Path,
        default=RUN_ROOT / "derived" / "toolformer_filter_discovery_summary.json",
    )
    parser.add_argument(
        "--slice-registry",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "slices" / "slice_registry.json",
    )
    parser.add_argument(
        "--case-registry",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry.json",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=RUN_ROOT / "configs" / "experiment_config.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "confirmation_family.json",
    )
    args = parser.parse_args()
    family = build_confirmation_family(
        discovery_summary_path=args.discovery_summary,
        slice_registry_path=args.slice_registry,
        case_registry_path=args.case_registry,
        config_path=args.config,
        output_path=args.output,
    )
    print(
        json.dumps(
            {
                "selected_candidate_id": family["selected_candidate_id"],
                "case_count": family["case_count"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
