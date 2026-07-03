#!/usr/bin/env python
"""Materialize preparation-time asset locks for real-reuse tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CHECKED_ON = "2026-07-03"
STATUS = "asset_lock_ready_preparation_pending"


OBSERVED_SOURCE_LOCKS: dict[str, dict[str, Any]] = {
    "https://github.com/WecoAI/aideml": {
        "lock_type": "git_head_observed",
        "observed_revision": "40dcf28fc3a39e93c7192acec0c9e2e9bffa973d",
        "verification_command": "git ls-remote https://github.com/WecoAI/aideml HEAD",
    },
    "https://github.com/openai/mle-bench": {
        "lock_type": "git_head_observed",
        "observed_revision": "507f92e1138bb6e40dac5c6ee7a6758e6424bf97",
        "verification_command": "git ls-remote https://github.com/openai/mle-bench HEAD",
    },
    "https://github.com/SWE-agent/SWE-agent": {
        "lock_type": "git_head_observed",
        "observed_revision": "5f40e63360d654adcd91e30ed11473389bc4909b",
        "verification_command": "git ls-remote https://github.com/SWE-agent/SWE-agent HEAD",
    },
    "https://github.com/princeton-nlp/SWE-bench": {
        "lock_type": "git_head_observed",
        "observed_revision": "f7bbbb2ccdf479001d6467c9e34af59e44a840f9",
        "verification_command": "git ls-remote https://github.com/princeton-nlp/SWE-bench HEAD",
    },
    "https://github.com/noahshinn/reflexion": {
        "lock_type": "git_head_observed",
        "observed_revision": "218cf0ef1df84b05ce379dd4a8e47f17766733a0",
        "verification_command": "git ls-remote https://github.com/noahshinn/reflexion HEAD",
    },
    "https://github.com/openai/human-eval": {
        "lock_type": "git_head_observed",
        "observed_revision": "6d43fb980f9fee3c892a914eda09951f772ad10d",
        "verification_command": "git ls-remote https://github.com/openai/human-eval HEAD",
    },
    "https://github.com/scverse/SnapATAC2": {
        "lock_type": "git_head_observed",
        "observed_revision": "7be57442708694217e27c8654ecd38a0de194aa4",
        "verification_command": "git ls-remote https://github.com/scverse/SnapATAC2 HEAD",
    },
    "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite": {
        "lock_type": "hf_dataset_sha_observed",
        "observed_revision": "6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2",
        "verification_command": "GET https://huggingface.co/api/datasets/princeton-nlp/SWE-bench_Lite",
        "split_summary": "dev=23 examples; test=300 examples",
    },
    "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified": {
        "lock_type": "hf_dataset_sha_observed",
        "observed_revision": "c104f840cc67f8b6eec6f759ebc8b2693d585d4a",
        "verification_command": "GET https://huggingface.co/api/datasets/princeton-nlp/SWE-bench_Verified",
        "split_summary": "test=500 examples",
    },
    "https://huggingface.co/datasets/hotpotqa/hotpot_qa": {
        "lock_type": "hf_dataset_sha_observed",
        "observed_revision": "1908d6afbbead072334abe2965f91bd2709910ab",
        "verification_command": "GET https://huggingface.co/api/datasets/hotpotqa/hotpot_qa",
        "split_summary": "distractor validation=7405 examples",
    },
    "https://huggingface.co/datasets/openai/openai_humaneval": {
        "lock_type": "hf_dataset_sha_observed",
        "observed_revision": "7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544",
        "verification_command": "GET https://huggingface.co/api/datasets/openai/openai_humaneval",
        "split_summary": "test=164 examples",
    },
    "https://scverse.org/SnapATAC2/tutorials/index.html": {
        "lock_type": "official_docs_reachable",
        "observed_revision": "http_200_on_2026-07-03",
        "verification_command": "GET https://scverse.org/SnapATAC2/tutorials/index.html",
    },
    "https://scverse.org/SnapATAC2/api/index.html": {
        "lock_type": "official_docs_reachable",
        "observed_revision": "http_200_on_2026-07-03",
        "verification_command": "GET https://scverse.org/SnapATAC2/api/index.html",
    },
}


LOCK_PROFILES: dict[str, dict[str, Any]] = {
    "AIDE-T1": {
        "locked_task_instance": {
            "source_kind": "kaggle_competition",
            "competition_slug": "spaceship-titanic",
            "local_instance_id": "spaceship-titanic-validation-seed-20260703",
            "split_seed": 20260703,
            "split_policy": "Create a deterministic local validation split from Kaggle training data; labels are scorer-only and must not enter model context.",
            "reference_boundary": "Kaggle/AIDE paper scores remain reported references unless this exact local split and budget are reproduced.",
        },
        "external_projects": [
            {
                "name": "mle-bench",
                "url": "https://github.com/openai/mle-bench",
                "local_path": "D:/a_work/gitee/mle-bench",
            }
        ],
        "hidden_from_model": ["validation_labels.csv", "heldout split labels"],
        "preparer": "scripts/prepare_real_reuse_aide_fixture.py",
        "scorer": "scripts/score_real_reuse_aide.py",
    },
    "AIDE-T2": {
        "locked_task_instance": {
            "source_kind": "kaggle_competition_debug_fixture",
            "competition_slug": "spaceship-titanic",
            "local_instance_id": "spaceship-titanic-debug-weak-script-seed-20260703",
            "split_seed": 20260703,
            "weak_script_seed": 20260703,
            "split_policy": "Use the same deterministic validation split as AIDE-T1 and generate one weak baseline script before model runs.",
            "reference_boundary": "Only Summary and PaperToSkill runs under the same weak script and budget are strict comparisons.",
        },
        "external_projects": [
            {
                "name": "mle-bench",
                "url": "https://github.com/openai/mle-bench",
                "local_path": "D:/a_work/gitee/mle-bench",
            }
        ],
        "hidden_from_model": ["validation_labels.csv", "heldout split labels"],
        "preparer": "scripts/prepare_real_reuse_aide_fixture.py",
        "scorer": "scripts/score_real_reuse_aide.py",
    },
    "SWE-T1": {
        "locked_task_instance": {
            "source_kind": "swe_bench_lite_dev_instance",
            "dataset_id": "princeton-nlp/SWE-bench_Lite",
            "dataset_sha": "6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2",
            "split": "dev",
            "instance_id": "sqlfluff__sqlfluff-1625",
            "repo": "sqlfluff/sqlfluff",
            "base_commit": "14e1a23a3166b9a645a16de96f694c77a5d4abb7",
            "fail_to_pass": ["test/cli/commands_test.py::test__cli__command_directed"],
            "reference_boundary": "SWE-agent/SWE-bench paper scores are reported references unless the same instance, tests, and budget are reproduced locally.",
        },
        "external_projects": [
            {
                "name": "SWE-bench",
                "url": "https://github.com/princeton-nlp/SWE-bench",
                "local_path": "D:/a_work/gitee/SWE-bench",
            }
        ],
        "hidden_from_model": ["gold patch", "test_patch beyond allowed failing-test context"],
        "preparer": "scripts/prepare_real_reuse_swe_fixture.py",
        "scorer": "scripts/score_real_reuse_swe.py",
    },
    "SWE-T2": {
        "locked_task_instance": {
            "source_kind": "swe_bench_verified_test_instance",
            "dataset_id": "princeton-nlp/SWE-bench_Verified",
            "dataset_sha": "c104f840cc67f8b6eec6f759ebc8b2693d585d4a",
            "split": "test",
            "instance_id": "astropy__astropy-12907",
            "repo": "astropy/astropy",
            "base_commit": "d16bfe05a744909de4b27f5875fe0d4ed41ce607",
            "fail_to_pass": [
                "astropy/modeling/tests/test_separable.py::test_separable[compound_model6-result6]",
                "astropy/modeling/tests/test_separable.py::test_separable[compound_model9-result9]",
            ],
            "difficulty": "15 min - 1 hour",
            "reference_boundary": "Strict comparison is only Summary vs PaperToSkill on this same verified instance and run budget.",
        },
        "external_projects": [
            {
                "name": "SWE-bench",
                "url": "https://github.com/princeton-nlp/SWE-bench",
                "local_path": "D:/a_work/gitee/SWE-bench",
            }
        ],
        "hidden_from_model": ["gold patch", "test_patch beyond allowed failing-test context"],
        "preparer": "scripts/prepare_real_reuse_swe_fixture.py",
        "scorer": "scripts/score_real_reuse_swe.py",
    },
    "REF-T1": {
        "locked_task_instance": {
            "source_kind": "hotpotqa_distractor_validation_example",
            "dataset_id": "hotpotqa/hotpot_qa",
            "dataset_sha": "1908d6afbbead072334abe2965f91bd2709910ab",
            "config": "distractor",
            "split": "validation",
            "example_id": "5a8b57f25542995d1e6f1371",
            "level": "hard",
            "type": "comparison",
            "question": "Were Scott Derrickson and Ed Wood of the same nationality?",
            "answer_key_policy": "The gold answer is scorer-only; the model receives only the question, context/tool stub, and fixed feedback protocol.",
            "reference_boundary": "Reflexion paper scores are reported references unless this exact QA setup and retry budget are reproduced.",
        },
        "external_projects": [],
        "hidden_from_model": ["gold answer", "supporting-fact labels if not part of the allowed retrieval context"],
        "preparer": "scripts/prepare_real_reuse_reflexion_fixture.py",
        "scorer": "scripts/score_real_reuse_reflexion.py",
    },
    "REF-T2": {
        "locked_task_instance": {
            "source_kind": "humaneval_second_attempt_retry",
            "dataset_id": "openai/openai_humaneval",
            "dataset_sha": "7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544",
            "split": "test",
            "task_id": "HumanEval/0",
            "entry_point": "has_close_elements",
            "failed_first_attempt_seed": 20260703,
            "answer_key_policy": "Canonical solution and tests are scorer/harness assets; model sees prompt plus fixed failed-attempt feedback only.",
            "reference_boundary": "Reflexion paper scores are references unless the same HumanEval task, feedback protocol, and budget are reproduced.",
        },
        "external_projects": [
            {
                "name": "human-eval",
                "url": "https://github.com/openai/human-eval",
                "local_path": "D:/a_work/gitee/human-eval",
            }
        ],
        "hidden_from_model": ["canonical solution", "private test oracle beyond provided feedback"],
        "preparer": "scripts/prepare_real_reuse_reflexion_fixture.py",
        "scorer": "scripts/score_real_reuse_reflexion.py",
    },
    "SNAP-T1": {
        "locked_task_instance": {
            "source_kind": "snapatac2_builtin_dataset_pipeline",
            "dataset_function": "snapatac2.datasets.pbmc5k",
            "tutorial_path": "docs/tutorials/pbmc.ipynb",
            "tutorial_lfs_oid": "sha256:7b58060a27e69637f01ad41ebcdadb86cf023d3a912307da6b094b2bdf32fa9b",
            "api_docs": "https://scverse.org/SnapATAC2/api/index.html",
            "resource_metric_policy": "Score completion, expected artifact schema, runtime, and memory; do not score subjective biological interpretation.",
            "reference_boundary": "SnapATAC2 paper scores remain reported references unless the same dataset, environment, and resource measurement are reproduced.",
        },
        "external_projects": [
            {
                "name": "SnapATAC2",
                "url": "https://github.com/scverse/SnapATAC2",
                "local_path": "D:/a_work/gitee/SnapATAC2",
            }
        ],
        "hidden_from_model": ["post-run metric file", "resource scorer thresholds"],
        "preparer": "scripts/prepare_real_reuse_snapatac2_fixture.py",
        "scorer": "scripts/score_real_reuse_snapatac2.py",
    },
    "SNAP-T2": {
        "locked_task_instance": {
            "source_kind": "snapatac2_builtin_multiome_or_cluster_fixture",
            "dataset_function": "snapatac2.datasets.pbmc10k_multiome",
            "tutorial_path": "docs/tutorials/modality.ipynb",
            "tutorial_lfs_oid": "sha256:79c7640e3fc12e0f2a9b9aac4f834cc4822865c5cbc3600358bd63ff7b1c8c37",
            "api_docs": "https://scverse.org/SnapATAC2/api/index.html",
            "resource_metric_policy": "Pre-register ARI/NMI when labels are available; otherwise mark the metric as a proxy before execution.",
            "reference_boundary": "Do not compare to paper resource scores as strict evidence unless the same data and environment are reproduced.",
        },
        "external_projects": [
            {
                "name": "SnapATAC2",
                "url": "https://github.com/scverse/SnapATAC2",
                "local_path": "D:/a_work/gitee/SnapATAC2",
            }
        ],
        "hidden_from_model": ["reference labels if used only for scoring", "post-run metric file"],
        "preparer": "scripts/prepare_real_reuse_snapatac2_fixture.py",
        "scorer": "scripts/score_real_reuse_snapatac2.py",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def source_locks(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    locks: list[dict[str, Any]] = []
    for source in candidate.get("source_urls", []):
        url = str(source.get("url", ""))
        observed = OBSERVED_SOURCE_LOCKS.get(url, {})
        locks.append(
            {
                "source_url_id": source.get("id"),
                "url": url,
                "kind": source.get("kind"),
                "lock_type": observed.get("lock_type", "declared_source_recheck_required"),
                "observed_revision": observed.get("observed_revision"),
                "observed_on": CHECKED_ON if observed else None,
                "verification_command": observed.get("verification_command"),
                "split_summary": observed.get("split_summary"),
                "must_reverify_before_materialization": True,
            }
        )
    return locks


def asset_slot_locks(task_id: str, candidate: dict[str, Any]) -> list[dict[str, Any]]:
    locks = []
    for asset in candidate.get("candidate_assets", []):
        slot = str(asset.get("slot", ""))
        locks.append(
            {
                "slot": slot,
                "source_url_id": asset.get("source_url_id"),
                "locked_path_after_prepare": f"benchmarks/real_reuse/assets/{task_id}/{slot}",
                "materialization_status": "not_materialized",
                "license_review_status": "pending",
                "sha256_after_prepare": None,
                "required_for_execution": asset.get("required_for_execution") is True,
                "notes": asset.get("notes"),
            }
        )
    return locks


def build_lock(task_spec: dict[str, Any], fixture: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task_spec["id"])
    profile = LOCK_PROFILES[task_id]
    metric = task_spec["metric_contract"]
    return {
        "schema_version": "0.1",
        "benchmark_id": task_spec["benchmark_id"],
        "task_id": task_id,
        "task_spec": f"benchmarks/real_reuse/tasks/{task_id}.json",
        "fixture_manifest": f"benchmarks/real_reuse/fixtures/{task_id}.json",
        "fixture_candidate": f"benchmarks/real_reuse/fixture_candidates/{task_id}.json",
        "source_paper_id": task_spec["source_paper_id"],
        "domain": task_spec["domain"],
        "status": STATUS,
        "evidence_boundary": (
            "This lock fixes the selected external source revisions, task instance, "
            "local materialization targets, and scorer/preparer contracts for a future "
            "real-reuse run. It does not download assets, run models, score outputs, "
            "or provide downstream task-success evidence."
        ),
        "source_probe": {
            "checked_on": CHECKED_ON,
            "method": "Lightweight git ls-remote, Hugging Face dataset API, and official documentation reachability probes.",
            "boundary": "Reachability and public metadata only; no large dataset download, clone, install, or task execution.",
        },
        "selected_candidate_id": candidate["selected_candidate"]["id"],
        "locked_task_instance": profile["locked_task_instance"],
        "source_revision_locks": source_locks(candidate),
        "asset_slot_locks": asset_slot_locks(task_id, candidate),
        "local_materialization_targets": {
            "asset_dir": f"benchmarks/real_reuse/assets/{task_id}",
            "prepared_manifest": f"benchmarks/real_reuse/assets/{task_id}/asset_manifest.json",
            "run_dir": task_spec["artifact_paths"]["run_dir"],
            "external_project_root": "D:/a_work/gitee",
            "external_projects": profile["external_projects"],
        },
        "preparation_contract": {
            "status": "not_started",
            "preparer": profile["preparer"],
            "must_complete_before_model_run": [
                "Reverify source revisions or explicitly record an updated revision lock.",
                "Complete license and terms review for every materialized asset.",
                "Write the prepared asset manifest with paths and sha256 values.",
                "Create condition contexts for Summary and PaperToSkill without exposing hidden scorer assets.",
                "Confirm the scorer command exists and can run on a dry fixture.",
            ],
            "hidden_from_model": profile["hidden_from_model"],
            "credential_policy": "Use user-managed credentials only. Never commit API keys, Kaggle tokens, Hugging Face tokens, cookies, or credential-bearing logs.",
        },
        "scoring_lock": {
            "scorer": profile["scorer"],
            "metric_name": metric["name"],
            "metric_family": metric["family"],
            "direction": metric["direction"],
            "success_criterion": metric["success_criterion"],
            "scoring_command_template": candidate["scoring_plan"]["scoring_command_template"],
            "required_metric_inputs": fixture["scoring_contract"]["metric_inputs"],
            "raw_row_schema": task_spec["raw_row_schema"],
            "answer_or_gold_policy": "Gold labels, answers, patches, canonical solutions, and scorer-only thresholds must stay out of model-visible context.",
        },
        "condition_lock": fixture["context_assets"],
        "run_control_lock": {
            "first_pass_human_intervention": task_spec["run_controls"]["first_pass_human_intervention"],
            "same_prompt_template_across_conditions": task_spec["run_controls"]["same_prompt_template_across_conditions"],
            "same_run_budget_across_conditions": task_spec["run_controls"]["same_run_budget_across_conditions"],
            "same_task_metric_across_conditions": task_spec["run_controls"]["same_task_metric_across_conditions"],
        },
        "next_action": "Implement the preparer/scorer named above, materialize assets, then run Summary and PaperToSkill under the same locked task instance and budget.",
    }


def materialize(task_dir: Path, fixture_dir: Path, candidate_dir: Path, output_dir: Path) -> list[Path]:
    output_paths: list[Path] = []
    for task_path in sorted(task_dir.glob("*.json")):
        task_spec = load_json(task_path)
        task_id = str(task_spec["id"])
        if task_id not in LOCK_PROFILES:
            raise ValueError(f"missing asset lock profile for {task_id}")
        fixture = load_json(fixture_dir / f"{task_id}.json")
        candidate = load_json(candidate_dir / f"{task_id}.json")
        output_path = output_dir / f"{task_id}.json"
        write_json(output_path, build_lock(task_spec, fixture, candidate))
        output_paths.append(output_path)
    return output_paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build preparation-time asset locks for real-reuse tasks.")
    parser.add_argument("--task-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "tasks")
    parser.add_argument("--fixture-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "fixtures")
    parser.add_argument("--candidate-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "fixture_candidates")
    parser.add_argument("--output-dir", type=Path, default=root / "benchmarks" / "real_reuse" / "asset_locks")
    args = parser.parse_args()

    paths = materialize(args.task_dir, args.fixture_dir, args.candidate_dir, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
