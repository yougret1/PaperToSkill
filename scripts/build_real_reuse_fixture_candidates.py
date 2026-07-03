#!/usr/bin/env python
"""Materialize candidate fixture-asset plans for real-reuse tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CHECKED_ON = "2026-07-03"
STATUS = "candidate_assets_selected_preparation_pending"


CANDIDATE_PROFILES: dict[str, dict[str, Any]] = {
    "AIDE-T1": {
        "candidate": {
            "id": "mle_bench_spaceship_titanic_submission",
            "label": "MLE-bench Spaceship Titanic Kaggle-style submission task",
            "reason": "Small, objective ML-engineering benchmark shape with a submission file and validation metric, matching the AIDE-style code-space optimization workflow.",
            "relation_to_source_paper": "AIDE reports ML-engineering benchmark results over Weco-Kaggle, MLE-Bench, and RE-Bench-style tasks; this candidate keeps the Kaggle-style input/output contract while staying small enough for fixture preparation.",
        },
        "source_urls": [
            {
                "id": "aide_code",
                "url": "https://github.com/WecoAI/aideml",
                "kind": "source_paper_code",
                "notes": "AIDE implementation source for the workflow being reused.",
            },
            {
                "id": "mle_bench_repo",
                "url": "https://github.com/openai/mle-bench",
                "kind": "benchmark_harness",
                "notes": "MLE-bench harness; README includes the spaceship-titanic sample workflow.",
            },
            {
                "id": "kaggle_competition",
                "url": "https://www.kaggle.com/competitions/spaceship-titanic",
                "kind": "dataset_and_metric",
                "notes": "Candidate competition data and metric; requires Kaggle terms/credential handling outside tracked files.",
            },
        ],
        "assets": [
            ["dataset_manifest", "kaggle_competition", "Kaggle competition metadata and metric description."],
            ["train_split", "kaggle_competition", "Training data after local download and validation split creation."],
            ["validation_split", "kaggle_competition", "Held-out validation labels created locally from the training data."],
            ["starter_workspace", "mle_bench_repo", "Local AIDE-style solution workspace and baseline script."],
        ],
        "commands": [
            "git clone https://github.com/openai/mle-bench D:/a_work/gitee/mle-bench",
            "kaggle competitions download -c spaceship-titanic -p benchmarks/real_reuse/assets/AIDE-T1/raw",
            "python scripts/prepare_real_reuse_aide_fixture.py --task AIDE-T1 --competition spaceship-titanic --raw-dir benchmarks/real_reuse/assets/AIDE-T1/raw --output-dir benchmarks/real_reuse/assets/AIDE-T1",
        ],
        "environment_notes": [
            "Kaggle API credentials and competition-rule acceptance must be handled locally and never committed.",
            "The local runner should use the same attempt/time/token budget for Summary and PaperToSkill.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_aide.py --task AIDE-T1 --submission {submission_file} --labels benchmarks/real_reuse/assets/AIDE-T1/validation_labels.csv",
    },
    "AIDE-T2": {
        "candidate": {
            "id": "mle_bench_spaceship_titanic_debug_workspace",
            "label": "MLE-bench Spaceship Titanic weak-script debug fixture",
            "reason": "Uses the same objective competition but turns it into a weak-script plus score/error-feedback search task, directly exercising AIDE-style iterative refinement.",
            "relation_to_source_paper": "AIDE's core method is iterative exploration and selection over candidate code nodes; this fixture makes the node-improvement objective explicit.",
        },
        "source_urls": [
            {
                "id": "aide_code",
                "url": "https://github.com/WecoAI/aideml",
                "kind": "source_paper_code",
                "notes": "AIDE implementation source for iterative code exploration.",
            },
            {
                "id": "mle_bench_repo",
                "url": "https://github.com/openai/mle-bench",
                "kind": "benchmark_harness",
                "notes": "MLE-bench harness and example competition workflow.",
            },
            {
                "id": "kaggle_competition",
                "url": "https://www.kaggle.com/competitions/spaceship-titanic",
                "kind": "dataset_and_metric",
                "notes": "Candidate data and validation metric; local terms review required before download.",
            },
        ],
        "assets": [
            ["weak_script", "mle_bench_repo", "Local intentionally weak baseline script to be generated before execution."],
            ["error_or_score_feedback", "kaggle_competition", "Objective validation feedback generated from the weak script."],
            ["validation_split", "kaggle_competition", "Held-out validation split for the debug loop."],
            ["starter_workspace", "mle_bench_repo", "Workspace containing baseline, task prompt, and scoring harness."],
        ],
        "commands": [
            "git clone https://github.com/openai/mle-bench D:/a_work/gitee/mle-bench",
            "kaggle competitions download -c spaceship-titanic -p benchmarks/real_reuse/assets/AIDE-T2/raw",
            "python scripts/prepare_real_reuse_aide_fixture.py --task AIDE-T2 --competition spaceship-titanic --make-weak-script --raw-dir benchmarks/real_reuse/assets/AIDE-T2/raw --output-dir benchmarks/real_reuse/assets/AIDE-T2",
        ],
        "environment_notes": [
            "Use the same weak script and initial feedback for all conditions.",
            "Do not let the model see validation labels directly; scoring is via the runner.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_aide.py --task AIDE-T2 --candidate-script {candidate_script} --labels benchmarks/real_reuse/assets/AIDE-T2/validation_labels.csv",
    },
    "SWE-T1": {
        "candidate": {
            "id": "swe_bench_lite_issue_to_patch",
            "label": "SWE-bench Lite issue-to-patch candidate",
            "reason": "SWE-bench Lite keeps the SWE-agent-style repository issue, patch, and test-pass contract while reducing setup burden.",
            "relation_to_source_paper": "SWE-agent evaluates issue resolution through repository interaction and automated tests; this candidate preserves that input/output shape.",
        },
        "source_urls": [
            {
                "id": "swe_agent_code",
                "url": "https://github.com/SWE-agent/SWE-agent",
                "kind": "source_paper_code",
                "notes": "SWE-agent implementation and agent-computer interface reference.",
            },
            {
                "id": "swe_bench_repo",
                "url": "https://github.com/princeton-nlp/SWE-bench",
                "kind": "benchmark_harness",
                "notes": "Official SWE-bench harness and evaluation scripts.",
            },
            {
                "id": "swe_bench_lite",
                "url": "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite",
                "kind": "dataset",
                "notes": "Candidate issue set for the first repository patch fixture.",
            },
        ],
        "assets": [
            ["repository_snapshot", "swe_bench_lite", "Repository commit selected from a Lite instance."],
            ["issue_description", "swe_bench_lite", "Issue text and metadata from the selected instance."],
            ["target_test_command", "swe_bench_repo", "Test command derived from FAIL_TO_PASS tests and harness metadata."],
        ],
        "commands": [
            "git clone https://github.com/princeton-nlp/SWE-bench D:/a_work/gitee/SWE-bench",
            "python scripts/prepare_real_reuse_swe_fixture.py --task SWE-T1 --dataset princeton-nlp/SWE-bench_Lite --output-dir benchmarks/real_reuse/assets/SWE-T1",
            "python scripts/score_real_reuse_swe.py --task SWE-T1 --patch {patch_file} --workspace benchmarks/real_reuse/assets/SWE-T1/workspace",
        ],
        "environment_notes": [
            "Select a single deterministic Lite instance before execution and record the instance id.",
            "Avoid subjective code-review scoring; success is automated test resolution.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_swe.py --task SWE-T1 --patch {patch_file} --workspace benchmarks/real_reuse/assets/SWE-T1/workspace",
    },
    "SWE-T2": {
        "candidate": {
            "id": "swe_bench_verified_failing_test_patch",
            "label": "SWE-bench Verified failing-test-to-patch candidate",
            "reason": "Verified instances provide cleaner repository/test metadata for a focused failing-test patch task.",
            "relation_to_source_paper": "This keeps the SWE-agent automated repair contract while emphasizing a concrete failing test rather than a broad issue narrative.",
        },
        "source_urls": [
            {
                "id": "swe_agent_code",
                "url": "https://github.com/SWE-agent/SWE-agent",
                "kind": "source_paper_code",
                "notes": "SWE-agent reference implementation.",
            },
            {
                "id": "swe_bench_repo",
                "url": "https://github.com/princeton-nlp/SWE-bench",
                "kind": "benchmark_harness",
                "notes": "Official SWE-bench harness and dockerized evaluation flow.",
            },
            {
                "id": "swe_bench_verified",
                "url": "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified",
                "kind": "dataset",
                "notes": "Candidate verified issue/test set for the focused patch fixture.",
            },
        ],
        "assets": [
            ["repository_snapshot", "swe_bench_verified", "Repository commit selected from a Verified instance."],
            ["failing_test", "swe_bench_verified", "FAIL_TO_PASS test target and failure reproduction metadata."],
            ["target_test_command", "swe_bench_repo", "Harness-derived command to verify the patch."],
        ],
        "commands": [
            "git clone https://github.com/princeton-nlp/SWE-bench D:/a_work/gitee/SWE-bench",
            "python scripts/prepare_real_reuse_swe_fixture.py --task SWE-T2 --dataset princeton-nlp/SWE-bench_Verified --output-dir benchmarks/real_reuse/assets/SWE-T2",
            "python scripts/score_real_reuse_swe.py --task SWE-T2 --patch {patch_file} --workspace benchmarks/real_reuse/assets/SWE-T2/workspace",
        ],
        "environment_notes": [
            "Record the selected instance id and exact base commit before running models.",
            "The same failing test and regression command must be used across conditions.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_swe.py --task SWE-T2 --patch {patch_file} --workspace benchmarks/real_reuse/assets/SWE-T2/workspace",
    },
    "REF-T1": {
        "candidate": {
            "id": "hotpotqa_distractor_reflection_retry",
            "label": "HotPotQA distractor-style multi-hop QA reflection retry",
            "reason": "HotPotQA gives objective answers and multi-hop context, allowing Reflexion-style feedback and retry without subjective reflection grading.",
            "relation_to_source_paper": "Reflexion reports gains on QA-style retry loops; this candidate preserves answer-key scoring and verbal feedback.",
        },
        "source_urls": [
            {
                "id": "reflexion_code",
                "url": "https://github.com/noahshinn/reflexion",
                "kind": "source_paper_code",
                "notes": "Reflexion reference implementation.",
            },
            {
                "id": "hotpotqa_home",
                "url": "https://hotpotqa.github.io/",
                "kind": "dataset_home",
                "notes": "Official HotPotQA dataset and evaluation information.",
            },
            {
                "id": "hotpotqa_hf",
                "url": "https://huggingface.co/datasets/hotpotqa/hotpot_qa",
                "kind": "dataset_mirror",
                "notes": "Convenient loader candidate; verify license/terms against the official dataset page before use.",
            },
        ],
        "assets": [
            ["question", "hotpotqa_home", "Selected multi-hop question."],
            ["retrieval_context_or_tool_stub", "hotpotqa_home", "Distractor context paragraphs or local retrieval stub."],
            ["answer_key", "hotpotqa_home", "Gold answer used for exact match/F1."],
            ["feedback_protocol", "reflexion_code", "Deterministic feedback-after-first-attempt protocol."],
        ],
        "commands": [
            "python scripts/prepare_real_reuse_reflexion_fixture.py --task REF-T1 --dataset hotpotqa --config distractor --output-dir benchmarks/real_reuse/assets/REF-T1",
            "python scripts/score_real_reuse_reflexion.py --task REF-T1 --prediction {prediction_file} --answer-key benchmarks/real_reuse/assets/REF-T1/answer_key.json",
        ],
        "environment_notes": [
            "Use objective EM/F1 scoring only; do not score reflection elegance.",
            "The first-attempt feedback must be generated by a fixed rule before the retry.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_reflexion.py --task REF-T1 --prediction {prediction_file} --answer-key benchmarks/real_reuse/assets/REF-T1/answer_key.json",
    },
    "REF-T2": {
        "candidate": {
            "id": "humaneval_failed_attempt_retry",
            "label": "HumanEval failed-attempt retry fixture",
            "reason": "HumanEval provides objective unit tests for a second-attempt recovery task, avoiding subjective reflection-quality judgments.",
            "relation_to_source_paper": "Reflexion uses programming tasks with environment feedback; this candidate focuses on failure recovery under a fixed test checker.",
        },
        "source_urls": [
            {
                "id": "reflexion_code",
                "url": "https://github.com/noahshinn/reflexion",
                "kind": "source_paper_code",
                "notes": "Reflexion reference implementation and task framing.",
            },
            {
                "id": "humaneval_repo",
                "url": "https://github.com/openai/human-eval",
                "kind": "dataset_and_checker",
                "notes": "HumanEval tasks and execution-based evaluation.",
            },
            {
                "id": "humaneval_paper",
                "url": "https://arxiv.org/abs/2107.03374",
                "kind": "benchmark_paper",
                "notes": "Benchmark paper for the coding-task metric context.",
            },
        ],
        "assets": [
            ["initial_task", "humaneval_repo", "Selected HumanEval prompt and tests."],
            ["failed_first_attempt", "humaneval_repo", "Deterministic intentionally failing first attempt generated before execution."],
            ["environment_feedback", "humaneval_repo", "Unit-test failure output from the fixed checker."],
            ["objective_checker", "humaneval_repo", "HumanEval execution-based test harness or local equivalent."],
        ],
        "commands": [
            "git clone https://github.com/openai/human-eval D:/a_work/gitee/human-eval",
            "python scripts/prepare_real_reuse_reflexion_fixture.py --task REF-T2 --dataset humaneval --output-dir benchmarks/real_reuse/assets/REF-T2",
            "python scripts/score_real_reuse_reflexion.py --task REF-T2 --candidate {candidate_file} --tests benchmarks/real_reuse/assets/REF-T2/tests.json",
        ],
        "environment_notes": [
            "Sandbox code execution before running candidate model outputs.",
            "Record failed first-attempt output and fixed feedback before model comparison.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_reflexion.py --task REF-T2 --candidate {candidate_file} --tests benchmarks/real_reuse/assets/REF-T2/tests.json",
    },
    "SNAP-T1": {
        "candidate": {
            "id": "snapatac2_pbmc5k_embedding_pipeline",
            "label": "SnapATAC2 PBMC5k clustering/embedding tutorial fixture",
            "reason": "The official SnapATAC2 tutorial dataset supports a small single-cell analysis pipeline with objective completion, runtime, memory, and output-artifact checks.",
            "relation_to_source_paper": "SnapATAC2's contribution is scalable single-cell omics analysis; this candidate keeps the same pipeline style at local scale.",
        },
        "source_urls": [
            {
                "id": "snapatac2_code",
                "url": "https://github.com/scverse/SnapATAC2",
                "kind": "source_paper_code",
                "notes": "Current SnapATAC2 implementation repository.",
            },
            {
                "id": "snapatac2_tutorials",
                "url": "https://scverse.org/SnapATAC2/tutorials/index.html",
                "kind": "official_docs",
                "notes": "Official tutorial index with dataset-backed analysis workflows.",
            },
            {
                "id": "snapatac2_api",
                "url": "https://scverse.org/SnapATAC2/api/index.html",
                "kind": "official_api_docs",
                "notes": "API reference for datasets, preprocessing, embedding, and clustering calls.",
            },
        ],
        "assets": [
            ["dataset_manifest", "snapatac2_tutorials", "PBMC5k tutorial dataset or equivalent documented small dataset."],
            ["preprocessing_notes", "snapatac2_api", "Source-consistent preprocessing call sequence."],
            ["resource_budget", "snapatac2_tutorials", "Local runtime and memory budget to define before execution."],
            ["expected_artifact_schema", "snapatac2_api", "Embedding/clustering output schema for the scorer."],
        ],
        "commands": [
            "git clone https://github.com/scverse/SnapATAC2 D:/a_work/gitee/SnapATAC2",
            "python scripts/prepare_real_reuse_snapatac2_fixture.py --task SNAP-T1 --dataset pbmc5k --output-dir benchmarks/real_reuse/assets/SNAP-T1",
            "python scripts/score_real_reuse_snapatac2.py --task SNAP-T1 --artifact-dir results/real_reuse/runs/SNAP-T1/{condition}",
        ],
        "environment_notes": [
            "Pin the SnapATAC2 version and Python environment before comparing conditions.",
            "Use completion plus machine-readable artifact checks; avoid subjective biological interpretation as the main score.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_snapatac2.py --task SNAP-T1 --artifact-dir {artifact_dir}",
    },
    "SNAP-T2": {
        "candidate": {
            "id": "snapatac2_multiome_or_cluster_labels",
            "label": "SnapATAC2 multiome/clustering tutorial fixture with labels or proxy metrics",
            "reason": "A labeled or proxy-labeled tutorial dataset allows objective ARI/NMI or resource-quality scoring for a non-agent scientific data-analysis reuse task.",
            "relation_to_source_paper": "This extends the main validity experiment beyond agents into source-paper-style scientific data-analysis reuse.",
        },
        "source_urls": [
            {
                "id": "snapatac2_code",
                "url": "https://github.com/scverse/SnapATAC2",
                "kind": "source_paper_code",
                "notes": "Current SnapATAC2 implementation repository.",
            },
            {
                "id": "snapatac2_tutorials",
                "url": "https://scverse.org/SnapATAC2/tutorials/index.html",
                "kind": "official_docs",
                "notes": "Official workflows for clustering, annotation, and multimodal analysis.",
            },
            {
                "id": "snapatac2_api",
                "url": "https://scverse.org/SnapATAC2/api/index.html",
                "kind": "official_api_docs",
                "notes": "API reference needed to define deterministic scorer inputs.",
            },
        ],
        "assets": [
            ["dataset_manifest", "snapatac2_tutorials", "Small SnapATAC2 tutorial dataset with labels or a proxy-label plan."],
            ["reference_labels_or_proxy", "snapatac2_tutorials", "Reference labels, cell groups, or pre-registered proxy metric."],
            ["resource_budget", "snapatac2_tutorials", "Runtime and memory budget to define before execution."],
            ["expected_artifact_schema", "snapatac2_api", "Clustering/marker output schema for the scorer."],
        ],
        "commands": [
            "git clone https://github.com/scverse/SnapATAC2 D:/a_work/gitee/SnapATAC2",
            "python scripts/prepare_real_reuse_snapatac2_fixture.py --task SNAP-T2 --dataset tutorial-multiome-or-clustered --output-dir benchmarks/real_reuse/assets/SNAP-T2",
            "python scripts/score_real_reuse_snapatac2.py --task SNAP-T2 --artifact-dir results/real_reuse/runs/SNAP-T2/{condition}",
        ],
        "environment_notes": [
            "Choose the exact tutorial dataset and label/proxy metric before any model run.",
            "If labels are unavailable, the proxy metric must be pre-registered and described as a proxy, not biological truth.",
        ],
        "scoring_command_template": "python scripts/score_real_reuse_snapatac2.py --task SNAP-T2 --artifact-dir {artifact_dir}",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_source_urls(profile: dict[str, Any]) -> list[dict[str, Any]]:
    urls = []
    for item in profile["source_urls"]:
        urls.append(
            {
                "id": item["id"],
                "url": item["url"],
                "kind": item["kind"],
                "source_type": "primary_source_or_official_distribution",
                "checked_on": CHECKED_ON,
                "reachability_status": "declared_for_preparation_recheck",
                "notes": item["notes"],
            }
        )
    return urls


def build_assets(profile: dict[str, Any], fixture: dict[str, Any]) -> list[dict[str, Any]]:
    expected_slots = {slot["id"] for slot in fixture.get("asset_slots", [])}
    assets = []
    for slot, source_url_id, notes in profile["assets"]:
        if slot not in expected_slots:
            raise ValueError(f"{fixture['task_id']} candidate slot {slot!r} not present in fixture manifest")
        assets.append(
            {
                "slot": slot,
                "source_url_id": source_url_id,
                "path_or_uri": None,
                "local_path_policy": "Fill after preparation under benchmarks/real_reuse/assets/ or D:/a_work/gitee for external projects.",
                "materialization_status": "not_downloaded",
                "license_status": "review_required_before_use",
                "required_for_execution": True,
                "notes": notes,
            }
        )
    return assets


def build_candidate(task_spec: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task_spec["id"])
    profile = CANDIDATE_PROFILES[task_id]
    candidate = dict(profile["candidate"])
    candidate["candidate_status"] = "selected_for_preparation"
    return {
        "schema_version": "0.1",
        "benchmark_id": task_spec["benchmark_id"],
        "task_id": task_id,
        "task_spec": fixture["task_spec"],
        "fixture_manifest": f"benchmarks/real_reuse/fixtures/{task_id}.json",
        "source_paper_id": task_spec["source_paper_id"],
        "domain": task_spec["domain"],
        "status": STATUS,
        "evidence_boundary": (
            "This file records selected candidate assets and preparation commands only. "
            "It does not download data, clone repositories, execute tasks, score outputs, "
            "or provide downstream task-success results."
        ),
        "selected_candidate": candidate,
        "source_urls": build_source_urls(profile),
        "candidate_assets": build_assets(profile, fixture),
        "preparation_plan": {
            "preparation_status": "not_started",
            "external_project_root": "D:/a_work/gitee",
            "commands": profile["commands"],
            "environment_notes": profile["environment_notes"],
            "credentials_policy": "Use local environment variables or user-managed credentials only; never commit API keys, Kaggle tokens, Hugging Face tokens, cookies, or credential-bearing logs.",
        },
        "scoring_plan": {
            "scorer_status": "to_implement_next_phase",
            "metric_name": task_spec["metric_contract"]["name"],
            "metric_family": task_spec["metric_contract"]["family"],
            "direction": task_spec["metric_contract"]["direction"],
            "success_criterion": task_spec["metric_contract"]["success_criterion"],
            "scoring_command_template": profile["scoring_command_template"],
            "required_outputs": fixture["scoring_contract"]["metric_inputs"],
            "reference_score_boundary": task_spec["reference_score_policy"]["policy"],
        },
        "run_controls": {
            "first_pass_human_intervention": task_spec["run_controls"]["first_pass_human_intervention"],
            "same_run_budget_across_conditions": task_spec["run_controls"]["same_run_budget_across_conditions"],
            "same_prompt_template_across_conditions": task_spec["run_controls"]["same_prompt_template_across_conditions"],
        },
        "next_action": "Implement the task-specific preparer/scorer and materialize local assets before any Summary vs PaperToSkill run.",
    }


def materialize(task_dir: Path, fixture_dir: Path, output_dir: Path) -> list[Path]:
    output_paths: list[Path] = []
    for task_path in sorted(task_dir.glob("*.json")):
        task_spec = load_json(task_path)
        task_id = str(task_spec["id"])
        if task_id not in CANDIDATE_PROFILES:
            raise ValueError(f"missing fixture candidate profile for {task_id}")
        fixture_path = fixture_dir / f"{task_id}.json"
        fixture = load_json(fixture_path)
        candidate = build_candidate(task_spec, fixture)
        output_path = output_dir / task_path.name
        write_json(output_path, candidate)
        output_paths.append(output_path)
    return output_paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build candidate fixture-asset manifests for real-reuse tasks.")
    parser.add_argument("--task-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "tasks")
    parser.add_argument("--fixture-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "fixtures")
    parser.add_argument("--output-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "fixture_candidates")
    args = parser.parse_args()

    paths = materialize(args.task_dir, args.fixture_dir, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
