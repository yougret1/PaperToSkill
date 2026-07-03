#!/usr/bin/env python
"""Materialize fixture manifests for real-reuse task contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROFILE_BY_TASK_KIND = {
    "tabular_ml_submission": {
        "fixture_kind": "local_or_public_tabular_ml_benchmark",
        "required_assets": ["dataset_manifest", "train_split", "validation_split", "starter_workspace"],
        "scoring_command": "to_be_defined_after_dataset_selection",
        "metric_inputs": ["submission_file", "validation_labels_or_metric_server"],
        "license_review": "required_before_download_or_commit",
    },
    "ml_debug_and_search": {
        "fixture_kind": "local_or_public_ml_debug_workspace",
        "required_assets": ["weak_script", "error_or_score_feedback", "validation_split", "starter_workspace"],
        "scoring_command": "to_be_defined_after_workspace_selection",
        "metric_inputs": ["candidate_script", "validation_feedback"],
        "license_review": "required_before_download_or_commit",
    },
    "issue_to_patch": {
        "fixture_kind": "repository_issue_to_patch",
        "required_assets": ["repository_snapshot", "issue_description", "target_test_command"],
        "scoring_command": "to_be_defined_after_repository_selection",
        "metric_inputs": ["patch_file", "test_log"],
        "license_review": "required_before_clone_or_patch_release",
    },
    "failing_test_to_patch": {
        "fixture_kind": "repository_failing_test_to_patch",
        "required_assets": ["repository_snapshot", "failing_test", "target_test_command"],
        "scoring_command": "to_be_defined_after_repository_selection",
        "metric_inputs": ["patch_file", "test_log"],
        "license_review": "required_before_clone_or_patch_release",
    },
    "multi_hop_qa_with_reflection": {
        "fixture_kind": "objective_qa_retry_case",
        "required_assets": ["question", "retrieval_context_or_tool_stub", "answer_key", "feedback_protocol"],
        "scoring_command": "to_be_defined_after_qa_fixture_selection",
        "metric_inputs": ["final_answer", "answer_key"],
        "license_review": "required_before_dataset_use",
    },
    "failed_attempt_retry": {
        "fixture_kind": "objective_retry_case",
        "required_assets": ["initial_task", "failed_first_attempt", "environment_feedback", "objective_checker"],
        "scoring_command": "to_be_defined_after_checker_selection",
        "metric_inputs": ["second_attempt_output", "checker_log"],
        "license_review": "required_before_dataset_or_repo_use",
    },
    "single_cell_embedding_pipeline": {
        "fixture_kind": "small_single_cell_analysis_dataset",
        "required_assets": ["dataset_manifest", "preprocessing_notes", "resource_budget", "expected_artifact_schema"],
        "scoring_command": "to_be_defined_after_dataset_selection",
        "metric_inputs": ["embedding_or_cluster_output", "runtime_log", "memory_log"],
        "license_review": "required_before_dataset_use",
    },
    "single_cell_clustering_or_marker_analysis": {
        "fixture_kind": "small_single_cell_cluster_or_marker_dataset",
        "required_assets": ["dataset_manifest", "reference_labels_or_proxy", "resource_budget", "expected_artifact_schema"],
        "scoring_command": "to_be_defined_after_dataset_selection",
        "metric_inputs": ["cluster_or_marker_output", "quality_metric_log", "runtime_log", "memory_log"],
        "license_review": "required_before_dataset_use",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_fixture_manifest(task_spec: dict[str, Any]) -> dict[str, Any]:
    task_kind = str(task_spec["task_kind"])
    profile = PROFILE_BY_TASK_KIND[task_kind]
    task_id = str(task_spec["id"])
    required_assets = [
        {
            "id": asset_id,
            "status": "pending_selection",
            "path_or_uri": None,
            "sha256": None,
            "notes": "Select a concrete, license-compatible asset before execution.",
        }
        for asset_id in profile["required_assets"]
    ]
    return {
        "schema_version": "0.1",
        "benchmark_id": task_spec["benchmark_id"],
        "task_id": task_id,
        "task_spec": task_spec["artifact_paths"]["task_spec"],
        "source_paper_id": task_spec["source_paper_id"],
        "domain": task_spec["domain"],
        "fixture_kind": profile["fixture_kind"],
        "status": "fixture_manifest_ready_assets_pending",
        "evidence_boundary": (
            "This manifest records fixture requirements and asset slots only. "
            "It does not contain selected datasets, repositories, task outputs, "
            "scores, or downstream success evidence."
        ),
        "source_alignment": {
            "original_style_input": task_spec["input_contract"]["original_style_input"],
            "required_output": task_spec["output_contract"]["required_output"],
            "metric_name": task_spec["metric_contract"]["name"],
            "metric_family": task_spec["metric_contract"]["family"],
            "reference_score_policy": task_spec["reference_score_policy"]["policy"],
        },
        "asset_slots": required_assets,
        "context_assets": [
            {
                "condition": condition["id"],
                "context_path": condition["context_path"],
                "asset_status": condition["asset_status"],
            }
            for condition in task_spec.get("conditions", [])
        ],
        "execution_budget": {
            "max_attempts": task_spec["run_controls"]["max_attempts"],
            "same_run_budget_across_conditions": task_spec["run_controls"]["same_run_budget_across_conditions"],
            "first_pass_human_intervention": task_spec["run_controls"]["first_pass_human_intervention"],
            "time_limit_seconds": "to_be_defined_before_execution",
            "token_limit": "to_be_defined_before_execution",
        },
        "scoring_contract": {
            "automated": task_spec["metric_contract"]["automated"],
            "metric_name": task_spec["metric_contract"]["name"],
            "direction": task_spec["metric_contract"]["direction"],
            "success_criterion": task_spec["metric_contract"]["success_criterion"],
            "scoring_command": profile["scoring_command"],
            "metric_inputs": profile["metric_inputs"],
        },
        "provenance_and_license": {
            "license_review": profile["license_review"],
            "download_or_clone_status": "not_started",
            "external_project_root_policy": "Place newly downloaded projects under D:/a_work/gitee.",
            "secret_policy": "Do not store API keys, private tokens, or credential-bearing logs in this manifest.",
        },
        "planned_outputs": {
            "run_dir": task_spec["artifact_paths"]["run_dir"],
            "metric_log": task_spec["artifact_paths"]["metric_log"],
            "execution_log": task_spec["artifact_paths"]["execution_log"],
            "raw_rows": task_spec["artifact_paths"]["raw_rows"],
        },
        "next_action": "Select concrete fixture assets and fill path_or_uri plus license/provenance before runner execution.",
    }


def materialize(task_dir: Path, output_dir: Path) -> list[Path]:
    output_paths: list[Path] = []
    for task_path in sorted(task_dir.glob("*.json")):
        task_spec = load_json(task_path)
        manifest = build_fixture_manifest(task_spec)
        output_path = output_dir / task_path.name
        write_json(output_path, manifest)
        output_paths.append(output_path)
    return output_paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build real-reuse fixture manifests from task specs.")
    parser.add_argument("--task-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "tasks")
    parser.add_argument("--output-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "fixtures")
    args = parser.parse_args()

    paths = materialize(args.task_dir, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
