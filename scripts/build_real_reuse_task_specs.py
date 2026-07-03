#!/usr/bin/env python
"""Materialize per-task specs for the planned real-reuse benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_RAW_ROW_FIELDS = [
    "run_id",
    "task_id",
    "source_paper_id",
    "domain",
    "condition",
    "model_family",
    "model_alias",
    "task_score",
    "success",
    "workflow_score",
    "unsupported_errors",
    "tokens",
    "time_seconds",
    "interventions",
    "failure_reason",
    "output_path",
]

EXISTING_SKILL_PATHS = {
    "aide": "generated_skills/aide/SKILL.md",
    "reflexion": "generated_skills/reflexion/SKILL.md",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def condition_specs(task: dict[str, Any]) -> list[dict[str, Any]]:
    task_id = str(task["id"])
    paper_id = str(task["source_paper_id"])
    skill_path = EXISTING_SKILL_PATHS.get(paper_id, f"generated_skills/real_reuse/{paper_id}/SKILL.md")
    return [
        {
            "id": "summary",
            "context_kind": "method_summary_baseline",
            "context_path": f"baselines/real_reuse/{task_id}_summary.md",
            "asset_status": "to_be_created_before_execution",
        },
        {
            "id": "papertoskill",
            "context_kind": "generated_skill",
            "context_path": skill_path,
            "asset_status": "existing_or_to_be_verified_before_execution",
        },
    ]


def build_task_spec(master: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    controls = master.get("execution_controls", {})
    artifacts = task.get("planned_artifacts", {})
    task_id = str(task["id"])
    return {
        "schema_version": "0.1",
        "benchmark_id": "papertoskill_real_reuse_v0",
        "master_spec": "benchmarks/real_reuse/real_reuse_v0.json",
        "id": task_id,
        "source_paper_id": task["source_paper_id"],
        "domain": task["domain"],
        "task_kind": task["task_kind"],
        "status": "spec_ready_assets_pending",
        "evidence_boundary": (
            "This per-task spec defines execution contracts only. It does not "
            "contain task outputs, scores, or downstream success evidence."
        ),
        "input_contract": {
            "original_style_input": task["original_style_input"],
            "required_fixture_manifest": f"benchmarks/real_reuse/fixtures/{task_id}.json",
            "fixture_status": "to_be_created_or_selected_before_execution",
        },
        "output_contract": {
            "required_output": task["required_output"],
            "output_dir": f"results/real_reuse/runs/{task_id}/outputs/",
            "must_log_command": True,
            "must_log_metric": True,
            "must_preserve_raw_output": True,
        },
        "conditions": condition_specs(task),
        "metric_contract": {
            **task["metric"],
            "score_field": "task_score",
            "success_field": "success",
            "metric_source_policy": "Use the original task metric family where practical; document any local proxy.",
        },
        "reference_score_policy": {
            **task["paper_reference"],
            "policy": controls.get("reference_score_policy", ""),
        },
        "run_controls": {
            "first_pass_human_intervention": controls.get("first_pass_human_intervention"),
            "human_review": controls.get("human_review"),
            "same_prompt_template_across_conditions": controls.get("same_prompt_template_across_conditions"),
            "same_task_metric_across_conditions": controls.get("same_task_metric_across_conditions"),
            "same_run_budget_across_conditions": controls.get("same_run_budget_across_conditions"),
            "max_attempts": "to_be_declared_in_fixture_or_runner_config",
            "random_seed_policy": "record seed when the task harness uses randomness",
        },
        "workflow_checklist": task["workflow_checklist"],
        "unsupported_error_policy": [
            "Count invented method claims that are not supported by the source paper or task fixture.",
            "Count steps that contradict the declared input, output, metric, or run budget.",
            "Count claims of completed results that are not present in the raw output log.",
        ],
        "raw_row_schema": DEFAULT_RAW_ROW_FIELDS,
        "artifact_paths": {
            "task_spec": artifacts["task_spec"],
            "run_dir": artifacts["run_dir"],
            "raw_rows": artifacts["raw_rows"],
            "metric_log": f"results/real_reuse/runs/{task_id}/metric.json",
            "execution_log": f"results/real_reuse/runs/{task_id}/run_log.md",
        },
        "next_action": "Create or select the fixture manifest and implement runner/scorer support before execution.",
    }


def materialize(master_path: Path, output_dir: Path) -> list[Path]:
    master = load_json(master_path)
    output_paths: list[Path] = []
    for task in master.get("tasks", []):
        task_spec = build_task_spec(master, task)
        output_path = output_dir / f"{task['id']}.json"
        write_json(output_path, task_spec)
        output_paths.append(output_path)
    return output_paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build per-task real-reuse specs from the master spec.")
    parser.add_argument("--master", type=Path, default=root / "benchmarks" / "real_reuse" / "real_reuse_v0.json")
    parser.add_argument("--output-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "tasks")
    args = parser.parse_args()

    paths = materialize(args.master, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
