from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent

EVIDENCE_FILES = [
    "derived/aide_t2_development_summary.json",
    "derived/swe_t2_development_summary.json",
    "derived/snap_mfse_development_summary.json",
    "derived/snap_mfse_eligibility_summary.json",
    "derived/snap_mfse_discovery_summary.json",
    "derived/snap_mfse_confirmation_summary.json",
    "derived/toolformer_filter_development_summary.json",
    "derived/toolformer_filter_eligibility_summary.json",
    "derived/toolformer_filter_discovery_summary.json",
    "derived/toolformer_filter_confirmation_summary.json",
]


def _load(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"required evidence summary is missing: {relative}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"evidence summary must be a JSON object: {relative}")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_summaries(run_root: Path, output_dir: Path) -> dict[str, str]:
    root = Path(run_root).resolve()
    evidence = {relative: _load(root, relative) for relative in EVIDENCE_FILES}
    snap_eligibility = evidence["derived/snap_mfse_eligibility_summary.json"]
    snap_discovery = evidence["derived/snap_mfse_discovery_summary.json"]
    snap_confirmation = evidence["derived/snap_mfse_confirmation_summary.json"]
    tool_eligibility = evidence["derived/toolformer_filter_eligibility_summary.json"]
    tool_discovery = evidence["derived/toolformer_filter_discovery_summary.json"]
    tool_confirmation = evidence[
        "derived/toolformer_filter_confirmation_summary.json"
    ]
    aide = evidence["derived/aide_t2_development_summary.json"]
    swe = evidence["derived/swe_t2_development_summary.json"]

    snap_eligibility_row = next(
        row
        for row in snap_eligibility["bundles"]
        if row["pair_id"] == snap_eligibility["selected_eligibility_pair_id"]
    )
    tool_eligibility_row = next(
        row
        for row in tool_eligibility["bundles"]
        if row["pair_id"] == tool_eligibility["selected_eligibility_pair_id"]
    )
    snap_result = snap_confirmation["result"]
    tool_result = tool_confirmation["result"]
    full_artifact_rows = [
        {
            "task_id": "SNAP-MFSE",
            "classification": snap_eligibility_row["classification"],
            "beneficial_cases": snap_eligibility_row["beneficial_cases"],
            "total_cases": snap_eligibility_row["total_cases"],
            "aggregate_effect": snap_eligibility_row["aggregate_effect"],
            "one_sided_cp_lower": snap_eligibility_row["one_sided_cp_lower"],
        },
        {
            "task_id": "TOOLFORMER-FILTER",
            "classification": tool_eligibility_row["classification"],
            "beneficial_cases": tool_eligibility_row["beneficial_cases"],
            "total_cases": tool_eligibility_row["total_cases"],
            "aggregate_effect": tool_eligibility_row["aggregate_effect"],
            "one_sided_cp_lower": tool_eligibility_row["one_sided_cp_lower"],
        },
    ]
    baseline = {
        "schema_version": "effectslice-stage2-baseline-summary.v1",
        "overall_plan": (
            "Require a positive paired full-artifact effect over the same-scaffold "
            "no-artifact baseline before any compact slice is searched."
        ),
        "analysis": (
            "SNAP-MFSE and TOOLFORMER-FILTER passed frozen full-artifact "
            "eligibility. SWE-T2 abstained because the full artifact was ineligible; "
            "AIDE-T2 remained adaptive development evidence only."
        ),
        "metric": {
            "name": "eligible_full_artifact_tasks",
            "value": 2,
            "direction": "descriptive",
        },
        "full_artifact_rows": full_artifact_rows,
        "excluded_or_abstained": [
            {
                "task_id": "AIDE-T2",
                "disposition": "development_only",
                "selected_candidate": aide.get("selected_development_candidate"),
            },
            {
                "task_id": "SWE-T2",
                "disposition": "abstain",
                "reason": swe.get("task_disposition"),
            },
        ],
        "code": "run_*_effectslice.py and src/effectslice/*_scorer.py",
        "plot_code": "build_stage2_figures.py",
        "plot_analyses": [],
        "exp_results_data_files": list(EVIDENCE_FILES),
    }

    task_rows = [
        {
            "task_id": "SNAP-MFSE",
            "disposition": "sealed_confirmation",
            "full_artifact_eligible": True,
            "selected_candidate_id": snap_discovery["selected_candidate_id"],
            "confirmation": "passed",
            "preservation_violations": snap_result["preservation_violations"],
            "beneficial_cases": snap_result["beneficial_cases"],
            "total_cases": snap_result["total_cases"],
            "task_local_confirmation_ready": True,
        },
        {
            "task_id": "TOOLFORMER-FILTER",
            "disposition": "sealed_confirmation",
            "full_artifact_eligible": True,
            "selected_candidate_id": tool_discovery["selected_candidate_id"],
            "confirmation": "failed",
            "preservation_violations": tool_result["preservation_violations"],
            "beneficial_cases": tool_result["beneficial_cases"],
            "total_cases": tool_result["total_cases"],
            "task_local_confirmation_ready": False,
        },
        {
            "task_id": "AIDE-T2",
            "disposition": "development_only",
            "full_artifact_eligible": None,
            "selected_candidate_id": None,
            "confirmation": "not_run",
            "task_local_confirmation_ready": False,
        },
        {
            "task_id": "SWE-T2",
            "disposition": "abstain",
            "full_artifact_eligible": False,
            "selected_candidate_id": None,
            "confirmation": "not_run",
            "task_local_confirmation_ready": False,
        },
    ]
    research = {
        "schema_version": "effectslice-stage2-research-summary.v1",
        "overall_plan": (
            "Search source-grounded strict subsets only after full-artifact "
            "eligibility, then admit a slice only after deletion audit and sealed "
            "task-local confirmation."
        ),
        "analysis": (
            "One task-local slice (SNAP-MFSE) passed sealed confirmation. The "
            "Toolformer prefix selected on discovery failed on untouched confirmation; "
            "the protocol correctly withheld admission. No cross-paper effectiveness "
            "claim is ready."
        ),
        "metric": {
            "name": "sealed_confirmed_task_local_slices",
            "value": 1,
            "direction": "higher_is_better",
        },
        "task_rows": task_rows,
        "general_effectslice_claim_ready": False,
        "scientific_claim_ready": False,
        "code": "build/analyze scripts and immutable experiment_results bundles",
        "plot_code": "build_stage2_figures.py",
        "plot_analyses": [],
        "exp_results_data_files": list(EVIDENCE_FILES),
    }

    ablation = {
        "schema_version": "effectslice-stage2-ablation-summary.v1",
        "overall_plan": (
            "Compare discovery selection with sealed confirmation to measure whether "
            "the confirmation gate rejects adaptive false discoveries."
        ),
        "analysis": (
            "Toolformer prefix_01 matched F on all 16 discovery cases but failed 15 "
            "of 59 preservation comparisons in the sealed family. The confirmation "
            "gate rejected this apparently perfect discovery result. SNAP prefix_03 "
            "remained equivalent on all 59 sealed cases."
        ),
        "metric": {
            "name": "sealed_false_discovery_rejections",
            "value": 1,
            "direction": "higher_is_better",
        },
        "rows": [
            {
                "task_id": "SNAP-MFSE",
                "candidate_id": snap_discovery["selected_candidate_id"],
                "discovery_mismatches": snap_discovery["candidate_rows"][-1][
                    "case_mismatches"
                ],
                "confirmation_mismatches": snap_result["preservation_violations"],
                "sealed_decision": "admit",
            },
            {
                "task_id": "TOOLFORMER-FILTER",
                "candidate_id": tool_discovery["selected_candidate_id"],
                "discovery_mismatches": tool_discovery["candidate_rows"][0][
                    "case_mismatches"
                ],
                "confirmation_mismatches": tool_result["preservation_violations"],
                "sealed_decision": "reject",
            },
        ],
        "code": "analyze_*_discovery.py and analyze_*_confirmation.py",
        "plot_code": "build_stage2_figures.py",
        "plot_analyses": [],
        "exp_results_data_files": list(EVIDENCE_FILES),
    }

    destination = Path(output_dir).resolve()
    paths = {
        "baseline": destination / "baseline_summary.json",
        "research": destination / "research_summary.json",
        "ablation": destination / "ablation_summary.json",
    }
    for name, payload in (
        ("baseline", baseline),
        ("research", research),
        ("ablation", ablation),
    ):
        _write(paths[name], payload)
    return {name: str(path) for name, path in paths.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build required Stage 2 summaries")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "logs")
    args = parser.parse_args()
    print(json.dumps(build_summaries(args.run_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
