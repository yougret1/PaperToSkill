from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
DEFAULT_V4 = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
DEFAULT_V5_ANALYSIS = RUN_ROOT / "derived" / "confirmation_v5r2" / "analysis.json"
DEFAULT_V5_CROSSCHECK = (
    RUN_ROOT / "derived" / "confirmation_v5r2" / "independent_crosscheck.json"
)
DEFAULT_OUTPUT_DIR = RUN_ROOT / "logs"
V4_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
V5_ANALYSIS_SCHEMA = "effectslice-confirmation-v5r2-analysis.v1"
V5_CROSSCHECK_SCHEMA = "effectslice-confirmation-v5r2-independent-crosscheck.v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path: Path, schema: str, label: str) -> tuple[Path, dict[str, Any]]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    return source, payload


def _artifact(path: Path) -> dict[str, str]:
    resolved = Path(path).resolve()
    return {"path": resolved.as_posix(), "sha256": _sha256(resolved)}


def _write(path: Path, payload: dict[str, Any]) -> None:
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _candidate_row(
    family: dict[str, Any], *, candidate_id: str, schedule: str, selected_after_v4: bool
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "schedule": schedule,
        "selected_after_v4": selected_after_v4,
        "registered_blocks": int(family["registered_blocks"]),
        "operational_success_counts": family["operational_success_counts"],
        "mean_task_score": family["mean_task_score"],
        "paired_success_status": family["paired_success_status"],
        "admission_decision": family["admission_decision"],
    }


def build_summaries(
    v4_path: Path,
    v5_analysis_path: Path,
    v5_crosscheck_path: Path,
    output_dir: Path,
) -> dict[str, str]:
    v4_source, v4 = _load(v4_path, V4_SCHEMA, "V4 summary")
    v5_source, v5 = _load(v5_analysis_path, V5_ANALYSIS_SCHEMA, "V5 analysis")
    cross_source, cross = _load(
        v5_crosscheck_path, V5_CROSSCHECK_SCHEMA, "V5 crosscheck"
    )
    if not cross["expected_analysis"]["all_compared_fields_match"]:
        raise ValueError("V5 crosscheck differs from analysis")
    if cross["expected_analysis"]["sha256"] != _sha256(v5_source):
        raise ValueError("V5 analysis digest differs from crosscheck")
    if not cross["validation"]["all_outputs_complete"]:
        raise ValueError("V5 outputs are incomplete")

    v4_families = {row["family_key"]: row for row in v4["families"]}
    expected_v4 = {
        "snap_mfse",
        "toolformer_negative",
        "toolformer_positive",
        "toolformer_identity",
    }
    if set(v4_families) != expected_v4:
        raise ValueError("unexpected V4 family set")
    natural = cross["families"]["toolformer_natural"]
    candidates = [
        _candidate_row(
            v4_families["snap_mfse"],
            candidate_id="snap_prefix_03",
            schedule="confirmation_v4",
            selected_after_v4=False,
        ),
        _candidate_row(
            v4_families["toolformer_negative"],
            candidate_id="toolformer_prefix_01",
            schedule="confirmation_v4",
            selected_after_v4=False,
        ),
        _candidate_row(
            natural,
            candidate_id="toolformer_prefix_04_v5",
            schedule="confirmation_v5_attempt_2",
            selected_after_v4=True,
        ),
    ]
    full_successes = sum(row["operational_success_counts"]["F"] for row in candidates)
    baseline_successes = sum(row["operational_success_counts"]["B"] for row in candidates)
    denominator = sum(row["registered_blocks"] for row in candidates)
    source_files = [v4_source.as_posix(), v5_source.as_posix(), cross_source.as_posix()]

    baseline = {
        "schema_version": "effectslice-stage2-baseline-summary.v5",
        "overall_plan": (
            "Describe no-artifact and full-artifact operational success over the "
            "complete registered V4 and V5 schedules used by non-planted candidates."
        ),
        "analysis": (
            f"B succeeds in {baseline_successes}/{denominator} condition runs and F "
            f"in {full_successes}/{denominator}. Counts are descriptive across "
            "sequential finite schedules; tasks and sessions are not pooled for inference."
        ),
        "statistical_unit": "complete_registered_finite_schedule",
        "metric": {
            "name": "full_artifact_operational_successes",
            "value": full_successes,
            "direction": "higher_is_better",
            "descriptive_denominator": denominator,
        },
        "baseline_operational_successes": baseline_successes,
        "candidate_schedule_rows": candidates,
        "population_inference_used": False,
        "code": "analyze_confirmation_v4.py and analyze_confirmation_v5_role_repair.py",
        "plot_code": "build_stage2_figures_v5.py",
        "plot_analyses": [],
        "exp_results_data_files": source_files,
    }

    admissions = sum(int(row["admission_decision"]["passed"]) for row in candidates)
    research = {
        "schema_version": "effectslice-stage2-research-summary.v5",
        "overall_plan": (
            "Admit a frozen paper-derived strict subset only when the complete "
            "registered count-level SLA, output, and integrity checks pass."
        ),
        "analysis": (
            f"{admissions}/{len(candidates)} non-planted candidates are admitted. "
            "V4 rejects SNAP prefix 03 and Toolformer prefix 01; a separately "
            "registered V5 schedule admits pre-existing Toolformer prefix 04. "
            "The V5 candidate was selected after V4 and uses new private cases."
        ),
        "statistical_unit": "complete_registered_finite_schedule",
        "metric": {
            "name": "non_planted_candidate_admissions",
            "value": admissions,
            "direction": "descriptive",
            "descriptive_denominator": len(candidates),
        },
        "candidate_rows": candidates,
        "general_effectslice_claim_ready": False,
        "cross_paper_claim_ready": False,
        "human_benefit_claim_ready": False,
        "population_inference_used": False,
        "code": (
            "analyze_confirmation_v4_role_repair.py, "
            "analyze_confirmation_v5_role_repair.py, and independent crosschecks"
        ),
        "plot_code": "build_stage2_figures_v5.py",
        "plot_analyses": [],
        "exp_results_data_files": source_files,
    }

    strict_subset_rows = candidates + [
        _candidate_row(
            v4_families["toolformer_positive"],
            candidate_id="toolformer_planted_positive",
            schedule="confirmation_v4",
            selected_after_v4=False,
        )
    ]
    ablation = {
        "schema_version": "effectslice-stage2-ablation-summary.v5",
        "overall_plan": (
            "Compare registered strict-subset boundaries and calibrate the harness "
            "with planted redundancy plus byte-identical identity instrumentation."
        ),
        "analysis": (
            "SNAP prefix 03 and Toolformer prefix 01 fail; non-planted Toolformer "
            "prefix 04 and planted T01-T05 pass. Identity instrumentation passes "
            "with 5/6 paired success matches. These are sequential task-local "
            "comparisons, not a causal atom ablation or reducer benchmark."
        ),
        "statistical_unit": "complete_registered_finite_schedule",
        "metric": {
            "name": "non_planted_candidate_admissions",
            "value": admissions,
            "direction": "descriptive",
            "descriptive_denominator": len(candidates),
        },
        "strict_subset_rows": strict_subset_rows,
        "identity_instrumentation": v4_families["toolformer_identity"],
        "v4_calibration": v4["calibration"],
        "causal_ablation_claim_ready": False,
        "population_inference_used": False,
        "code": "build_stage2_summaries_v5.py",
        "plot_code": "build_stage2_figures_v5.py",
        "plot_analyses": [],
        "exp_results_data_files": source_files,
    }

    v5_summary = {
        "schema_version": "effectslice-stage2-confirmation-summary.v5",
        "analysis_status": v5["analysis_status"],
        "evidence_boundary": v5["evidence_boundary"],
        "preregistration": cross["preregistration"],
        "analysis": cross["expected_analysis"],
        "independent_outcome_count_crosscheck": _artifact(cross_source),
        "family": natural,
        "registered_blocks": cross["registered_blocks"],
        "registered_condition_runs": cross["registered_condition_runs"],
        "resource_summary": cross["resource_summary"],
        "resource_by_family_condition": cross["resource_by_family_condition"],
        "validation": cross["validation"],
        "raw_evidence_digest": cross["raw_evidence_digest"],
        "raw_file_count": cross["raw_file_count"],
        "scope_guards": v5["scope_guards"],
        "inference_scope": v5["inference_scope"],
        "selection_disclosure": {
            "candidate_preexisted_v4": True,
            "selected_after_v4_analysis": True,
            "v5_private_results_used_for_selection": False,
            "new_nonoverlapping_private_block": True,
        },
    }

    destination = Path(output_dir).resolve()
    outputs = {
        "baseline": destination / "baseline_summary.json",
        "research": destination / "research_summary.json",
        "ablation": destination / "ablation_summary.json",
        "confirmation_v5": destination / "confirmation_v5_summary.json",
    }
    for key, payload in (
        ("baseline", baseline),
        ("research", research),
        ("ablation", ablation),
        ("confirmation_v5", v5_summary),
    ):
        _write(outputs[key], payload)
    return {key: path.as_posix() for key, path in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final V4+V5 Stage 2 summaries")
    parser.add_argument("--v4", type=Path, default=DEFAULT_V4)
    parser.add_argument("--v5-analysis", type=Path, default=DEFAULT_V5_ANALYSIS)
    parser.add_argument("--v5-crosscheck", type=Path, default=DEFAULT_V5_CROSSCHECK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    print(
        json.dumps(
            build_summaries(
                args.v4, args.v5_analysis, args.v5_crosscheck, args.output_dir
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
