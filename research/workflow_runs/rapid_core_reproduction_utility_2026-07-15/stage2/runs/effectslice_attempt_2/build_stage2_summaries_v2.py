from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
HYPOTHESIS_IDS = (
    "H_full_benefit_run_level",
    "H_slice_preservation_run_level",
    "H_slice_benefit_run_level",
)


def _load_summary(path: Path) -> dict[str, Any]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "effectslice-confirmation-v2-task-summary.v1":
        raise ValueError(f"invalid confirmation-v2 summary: {source}")
    if payload.get("statistical_unit") != "independent_agent_run":
        raise ValueError("summary statistical unit must be independent_agent_run")
    if payload.get("schedule_complete") is not True:
        raise ValueError("confirmation-v2 summary schedule is incomplete")
    if payload.get("integrity_passed") is not True:
        raise ValueError("confirmation-v2 summary failed integrity audit")
    payload["_source_path"] = source.as_posix()
    payload["_source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    return payload


def _condition_successes(summary: dict[str, Any]) -> dict[str, int]:
    counts = {condition: 0 for condition in ("B", "F", "S")}
    for replicate in summary.get("replicates", []):
        conditions = replicate.get("conditions", {})
        for condition in counts:
            row = conditions.get(condition, {})
            counts[condition] += row.get("success") is True
    return counts


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_summaries(
    task_summary_paths: list[Path],
    output_dir: Path,
) -> dict[str, str]:
    if not task_summary_paths:
        raise ValueError("at least one confirmation-v2 task summary is required")
    tasks = [_load_summary(path) for path in task_summary_paths]
    denominators = {int(task["replicate_denominator"]) for task in tasks}
    cluster_sizes = {int(task["clustered_hidden_checks_per_run"]) for task in tasks}
    if len(denominators) != 1:
        raise ValueError("task summaries must share one replicate denominator")
    if len(cluster_sizes) != 1:
        raise ValueError("task summaries must share one hidden-check cluster size")
    denominator = denominators.pop()
    cluster_size = cluster_sizes.pop()

    baseline_rows = []
    research_rows = []
    ablation_rows = []
    for task in tasks:
        hypotheses = task["hypotheses"]
        full = hypotheses["H_full_benefit_run_level"]
        preservation = hypotheses["H_slice_preservation_run_level"]
        selected = hypotheses["H_slice_benefit_run_level"]
        source = {
            "path": task["_source_path"],
            "sha256": task["_source_sha256"],
        }
        baseline_rows.append(
            {
                "task_key": task["task_key"],
                "full_benefit_successes": full["successes"],
                "replicate_denominator": full["total"],
                "one_sided_cp_lower": full["one_sided_cp_lower"],
                "minimum_prevalence": full["minimum_prevalence"],
                "source_summary": source,
            }
        )
        research_rows.append(
            {
                "task_key": task["task_key"],
                "selected_candidate_id": task["selected_candidate_id"],
                "classification": task["classification"],
                "full_benefit": full,
                "slice_preservation": preservation,
                "slice_benefit": selected,
                "task_local_admission_ready": task[
                    "task_local_admission_ready"
                ],
                "confirmation_family_sha256": task[
                    "confirmation_family_sha256"
                ],
                "source_summary": source,
            }
        )
        ablation_rows.append(
            {
                "task_key": task["task_key"],
                "condition_successes": _condition_successes(task),
                "replicate_denominator": denominator,
                "full_benefit_indicator_successes": full["successes"],
                "slice_preservation_indicator_successes": preservation[
                    "successes"
                ],
                "slice_benefit_indicator_successes": selected["successes"],
                "prior_confirmation_status": task[
                    "prior_confirmation_status"
                ],
                "source_summary": source,
            }
        )

    full_benefit_total = sum(row["full_benefit_successes"] for row in baseline_rows)
    admitted_count = sum(row["task_local_admission_ready"] for row in research_rows)
    baseline = {
        "schema_version": "effectslice-stage2-baseline-summary.v2",
        "overall_plan": (
            "Measure whether the complete paper-derived artifact improves a fresh "
            "API agent run over the same-scaffold no-artifact condition."
        ),
        "analysis": (
            f"Across {len(tasks)} tasks, the registered full-benefit indicator held "
            f"in {full_benefit_total}/{len(tasks) * denominator} independent runs. "
            "Task-local exact bounds are reported without pooling cases or tasks."
        ),
        "statistical_unit": "independent_agent_run",
        "metric": {
            "name": "full_artifact_benefit_indicator_successes",
            "value": full_benefit_total,
            "direction": "higher_is_better",
            "descriptive_denominator": len(tasks) * denominator,
        },
        "task_rows": baseline_rows,
        "code": "run_confirmation_v2.py and analyze_confirmation_v2.py",
        "plot_code": "build_stage2_figures_v2.py",
        "plot_analyses": [],
        "exp_results_data_files": [task["_source_path"] for task in tasks],
    }
    research = {
        "schema_version": "effectslice-stage2-research-summary.v2",
        "overall_plan": (
            "Admit a discovery-selected source-grounded slice only when full "
            "benefit, slice preservation, and slice benefit each clear the frozen "
            "run-level prevalence gate under final-only private scoring."
        ),
        "analysis": (
            f"{admitted_count}/{len(tasks)} task-local slices passed all registered "
            "run-level gates. This is not a cross-paper effectiveness estimate."
        ),
        "statistical_unit": "independent_agent_run",
        "metric": {
            "name": "task_local_admissions",
            "value": admitted_count,
            "direction": "higher_is_better",
            "descriptive_denominator": len(tasks),
        },
        "task_rows": research_rows,
        "general_effectslice_claim_ready": False,
        "cross_paper_claim_ready": False,
        "human_benefit_claim_ready": False,
        "code": "analyze_confirmation_v2.py",
        "plot_code": "build_stage2_figures_v2.py",
        "plot_analyses": [],
        "exp_results_data_files": [task["_source_path"] for task in tasks],
    }
    ablation = {
        "schema_version": "effectslice-stage2-ablation-summary.v2",
        "overall_plan": (
            "Compare no-artifact, full-artifact, and selected-slice conditions "
            "over the same registered independent-run schedule."
        ),
        "analysis": (
            "Condition success counts and paired run-level indicators are reported "
            "separately. Prior case-level confirmation is retained only as "
            "contaminated development evidence."
        ),
        "statistical_unit": "independent_agent_run",
        "replicate_denominator_per_task": denominator,
        "clustered_hidden_checks_per_run": cluster_size,
        "metric": {
            "name": "registered_condition_success_counts",
            "value": sum(
                sum(row["condition_successes"].values()) for row in ablation_rows
            ),
            "direction": "descriptive",
        },
        "task_rows": ablation_rows,
        "code": "run_confirmation_v2.py and analyze_confirmation_v2.py",
        "plot_code": "build_stage2_figures_v2.py",
        "plot_analyses": [],
        "exp_results_data_files": [task["_source_path"] for task in tasks],
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
    parser = argparse.ArgumentParser(
        description="Build Stage 2 summaries from confirmation-v2 run-level audits"
    )
    parser.add_argument("--task-summary", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "logs")
    args = parser.parse_args()
    summaries = args.task_summary or [
        RUN_ROOT
        / "derived"
        / "confirmation_v2"
        / "snap_mfse_confirmation_v2_summary.json",
        RUN_ROOT
        / "derived"
        / "confirmation_v2"
        / "toolformer_filter_confirmation_v2_summary.json",
    ]
    print(json.dumps(build_summaries(summaries, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
