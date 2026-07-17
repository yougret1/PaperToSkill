from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.readiness import audit_project  # noqa: E402


EVIDENCE_BOUNDARY = (
    "Read-only development readiness and software-contract output only; this is not EffectSlice effectiveness "
    "evidence. Aggregate task scores are not paired observations."
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _summary(
    summary_type: str,
    status: str,
    overall_plan: str,
    analysis: str,
    metric_name: str,
    metric_value: int | float,
    direction: str,
    data_files: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "local-research-summary.v1",
        "summary_type": summary_type,
        "status": status,
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "entries": [
            {
                "overall_plan": overall_plan,
                "analysis": analysis,
                "metric": {
                    "name": metric_name,
                    "value": metric_value,
                    "direction": direction,
                },
                "code": "run_pilot.py and src/effectslice/readiness.py",
                "plot_code": None,
                "plot_analyses": [],
                "exp_results_data_files": data_files,
            }
        ],
    }


def build_summaries(report: dict[str, Any], readiness_ref: str) -> dict[str, dict[str, Any]]:
    ready_count = report["ready_task_count"]
    baseline = _summary(
        "baseline",
        "completed_development_audit",
        "Measure how many existing real-reuse tasks satisfy every prerequisite for an EffectSlice certificate run.",
        (
            f"Audited {report['task_count']} development tasks; {ready_count} are currently "
            "certificate-ready. Missing requirements remain explicit per task."
        ),
        "certificate_ready_task_count",
        ready_count,
        "higher_is_better",
        [readiness_ref],
    )
    research = _summary(
        "research",
        "completed_software_pilot",
        "Implement reason-coded eligibility/admission gates and enumerate the distinct real-data blockers.",
        (
            f"The pilot reports {len(report['blocker_counts'])} distinct blocker types. Gate unit tests validate "
            "software behavior only; no candidate effect was estimated."
        ),
        "distinct_readiness_blocker_types",
        len(report["blocker_counts"]),
        "lower_is_better",
        [readiness_ref],
    )
    if ready_count:
        ablation_status = "not_run_route_a_scope"
        ablation_analysis = (
            f"{ready_count} development task(s) satisfy the readiness schema, but Route A does not execute "
            "empirical gate ablations. Readiness alone is not an EffectSlice result."
        )
    else:
        ablation_status = "not_run_missing_paired_evidence"
        ablation_analysis = (
            "No empirical ablation was run because no current task is certificate-ready. Synthetic unit fixtures "
            "are intentionally excluded from scientific summaries."
        )
    ablation = _summary(
        "ablation",
        ablation_status,
        "Run empirical gate ablations only after at least one task has frozen B/F pairs and complete atom metadata.",
        ablation_analysis,
        "empirical_ablation_task_count",
        0,
        "descriptive",
        [readiness_ref],
    )
    return {"baseline": baseline, "research": research, "ablation": ablation}


def run_pilot(project_root: Path, run_root: Path) -> dict[str, str]:
    project = Path(project_root).resolve()
    run = Path(run_root).resolve()
    config_path = run / "configs" / "experiment_config.json"
    try:
        report = audit_project(project, config_path)
    except Exception as error:
        if isinstance(error, FileNotFoundError):
            failure_class = "missing_input"
        elif isinstance(error, (ValueError, KeyError, TypeError, json.JSONDecodeError)):
            failure_class = "invalid_format"
        else:
            failure_class = "execution_failure"
        _write_json(
            run / "logs" / "execution_error.json",
            {
                "schema_version": "effectslice-execution-error.v1",
                "failure_class": failure_class,
                "error_type": type(error).__name__,
                "message": str(error),
                "config_path": config_path.relative_to(run).as_posix(),
                "evidence_boundary": EVIDENCE_BOUNDARY,
            },
        )
        raise
    readiness_path = run / "experiment_results" / "pilot" / "readiness_report.json"
    _write_json(readiness_path, report)

    readiness_ref = readiness_path.relative_to(run).as_posix()
    summaries = build_summaries(report, readiness_ref)

    outputs = {
        "readiness": readiness_path,
        "baseline": run / "logs" / "baseline_summary.json",
        "research": run / "logs" / "research_summary.json",
        "ablation": run / "logs" / "ablation_summary.json",
    }
    for summary_type in ("baseline", "research", "ablation"):
        _write_json(outputs[summary_type], summaries[summary_type])
    return {name: str(path) for name, path in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EffectSlice Stage 2 readiness pilot")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    args = parser.parse_args()
    print(json.dumps(run_pilot(args.project_root, args.run_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
