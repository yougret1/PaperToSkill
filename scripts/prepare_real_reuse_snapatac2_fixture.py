#!/usr/bin/env python
"""Prepare locked SnapATAC2 real-reuse fixture assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1"
PREPARED_ON = "2026-07-03"
STATUS = "prepared_assets_ready_for_dry_scoring"
TASK_IDS = ("SNAP-T1", "SNAP-T2")
MATERIALIZATION_MODES = ("metadata_only", "official_miniature_fixture")
DEFAULT_MINIATURE_SOURCES = {
    "SNAP-T1": Path("tests/test_tools/test_single.tsv.gz"),
    "SNAP-T2": Path("tests/test_tools/test_clean.tsv.gz"),
}
OFFICIAL_DATASET_REFERENCES = {
    "SNAP-T1": [
        {
            "name": "atac_pbmc_5k.tsv.gz",
            "checksum": "sha256:5fe44c0f8f76ce1534c1ae418cf0707ca5ef712004eee77c3d98d2d4b35ceaec",
        },
        {
            "name": "atac_pbmc_5k.h5ad",
            "checksum": "sha256:92ae7f185cdec26517fd8d5acb60b2ce92c71e0ace824de35589c6d7942cab06",
        },
        {
            "name": "atac_pbmc_5k_annotated.h5ad",
            "checksum": "sha256:592f1551c27d0cfe4d81e7febad624d6b7d3ebf977b0c3ea64e06b3f3d76f078",
        },
    ],
    "SNAP-T2": [
        {
            "name": "10x-Multiome-Pbmc10k-ATAC.h5ad",
            "checksum": "sha256:24d030fb7f90453a0303b71a1e3e4e7551857d1e70072752d7fff9c918f77217",
        },
        {
            "name": "10x-Multiome-Pbmc10k-RNA.h5ad",
            "checksum": "sha256:a25327acff48b20b295c12221a84fd00f8f3f486ff3e7bd090fdef241b996a22",
        },
        {
            "name": "pbmc_10k_atac.tsv.gz",
            "checksum": "md5:a959ef83dfb9cae6ff73ab0147d547d1",
        },
    ],
}


SNAP_SUMMARY_FALLBACK = """# Real-Reuse Summary Baseline: {task_id}

SnapATAC2 is a scalable single-cell omics analysis workflow centered on
matrix-free spectral embedding. A source-consistent reuse attempt should load
the declared dataset, preserve preprocessing assumptions such as IDF scaling
and normalization when relevant, run embedding/clustering or multimodal
analysis, and report objective artifacts plus runtime and memory.

For this locked task, produce machine-readable analysis artifacts, log runtime
and memory, and avoid subjective biological interpretation as the main score.
"""


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def resolve_against(base: Path, path: Path) -> Path:
    return path if path.is_absolute() else base / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_revision(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def file_entry(root: Path, path: Path, slot: str, visibility: str) -> dict[str, str]:
    return {
        "slot": slot,
        "path": relative(root, path),
        "sha256": sha256_file(path),
        "visibility": visibility,
    }


def copy_or_write_json(source: Path | None, target: Path, default_payload: dict[str, Any]) -> None:
    if source:
        shutil.copy2(source, target)
    else:
        write_json(target, default_payload)


def load_lock(root: Path, task_id: str) -> dict[str, Any]:
    return load_json(root / "benchmarks" / "real_reuse" / "asset_locks" / f"{task_id}.json")


def default_dataset_manifest(task_id: str, lock: dict[str, Any]) -> dict[str, Any]:
    instance = lock.get("locked_task_instance", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "dataset_function": instance.get("dataset_function"),
        "tutorial_path": instance.get("tutorial_path"),
        "dataset_status": "external_or_user_materialized_before_execution",
        "evidence_boundary": (
            "Model-visible dataset contract only. This file does not contain "
            "the full dataset or any scorer-only labels."
        ),
    }


def materialized_dataset_manifest(
    root: Path,
    task_id: str,
    lock: dict[str, Any],
    *,
    snapatac2_root: Path,
    source_path: Path,
    copied_path: Path,
) -> dict[str, Any]:
    instance = lock.get("locked_task_instance", {})
    license_path = snapatac2_root / "LICENSE"
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "dataset_function": instance.get("dataset_function"),
        "tutorial_path": instance.get("tutorial_path"),
        "tutorial_lfs_oid": instance.get("tutorial_lfs_oid"),
        "materialization_mode": "official_miniature_fixture",
        "dataset_status": "official_repository_miniature_fixture_materialized",
        "source_repository": {
            "url": "https://github.com/scverse/SnapATAC2",
            "local_path": snapatac2_root.as_posix(),
            "revision": git_revision(snapatac2_root),
            "license": "MIT",
            "license_path": license_path.as_posix() if license_path.exists() else "",
            "license_sha256": sha256_file(license_path) if license_path.exists() else "",
        },
        "official_dataset_references": OFFICIAL_DATASET_REFERENCES[task_id],
        "miniature_fixture": {
            "source_path": source_path.as_posix(),
            "copied_path": relative(root, copied_path),
            "sha256": sha256_file(copied_path),
            "size_bytes": copied_path.stat().st_size,
        },
        "evidence_boundary": (
            "This materializes a small official SnapATAC2 repository fixture for "
            "smoke and fixture-readiness checks. It is not the full pbmc5k or "
            "pbmc10k_multiome dataset, not a reproduction of the SnapATAC2 paper "
            "scores, and not a PaperToSkill downstream result."
        ),
    }


def default_budget(task_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "max_runtime_seconds": 1800,
        "max_peak_memory_mb": 8192,
        "same_budget_across_conditions": True,
    }


def default_scorer_thresholds(task_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "success_threshold": 0.8,
        "visibility": "scorer_only",
        "threshold_policy": (
            "Pre-registered local dry-scoring threshold for one locked "
            "SnapATAC2 output. Hidden from model condition contexts."
        ),
    }


def default_proxy_labels(task_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "proxy_status": "no_ground_truth_labels_materialized",
        "accepted_reported_quality_metric_keys": [
            "ari",
            "nmi",
            "proxy_quality_score",
            "silhouette",
            "embedding_quality",
        ],
        "evidence_boundary": (
            "This scorer-only proxy policy allows the local miniature fixture "
            "to dry-score reported objective quality metrics. It is not a "
            "biological gold-label annotation set."
        ),
    }


def expected_schema(task_id: str) -> dict[str, Any]:
    if task_id == "SNAP-T1":
        required = [
            "completed",
            "method_steps",
            "embedding_artifacts",
            "runtime_seconds",
            "peak_memory_mb",
        ]
    else:
        required = [
            "completed",
            "method_steps",
            "clustering_artifacts",
            "quality_metrics",
            "runtime_seconds",
            "peak_memory_mb",
        ]
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "candidate_output_file": "candidate_output.json",
        "required_fields": required,
        "optional_fields": ["predicted_labels", "notes", "commands"],
    }


def preprocessing_notes(task_id: str) -> str:
    metric = "runtime/memory plus embedding artifact checks" if task_id == "SNAP-T1" else "ARI/NMI or pre-registered proxy plus runtime/memory"
    return f"""# {task_id} SnapATAC2 Preprocessing Notes

- Use a SnapATAC2-style path: load the declared single-cell data, preserve
  source-paper preprocessing assumptions, and run dimensionality reduction
  before downstream clustering or artifact reporting.
- Keep objective logs separate from interpretation. The scorer expects
  machine-readable artifacts and {metric}.
- Do not expose scorer-only labels, thresholds, or post-run metric files to the
  model condition context.
"""


def make_task_prompt(task_id: str) -> str:
    if task_id == "SNAP-T1":
        objective = (
            "Produce a runnable analysis plan and machine-readable embedding "
            "artifact record for the declared small single-cell dataset."
        )
        metric = "runtime_memory_quality"
        fields = "completed, method_steps, embedding_artifacts, runtime_seconds, peak_memory_mb"
    else:
        objective = (
            "Produce dimensionality reduction plus clustering/marker artifacts "
            "and objective quality/resource metrics for the declared dataset."
        )
        metric = "ari_nmi_runtime_memory"
        fields = "completed, method_steps, clustering_artifacts, quality_metrics, runtime_seconds, peak_memory_mb"
    return f"""# {task_id} Locked SnapATAC2 Task Prompt

Objective: {objective}

Metric: {metric}

Return one JSON object only. Required top-level fields:

{fields}

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.
"""


def write_summary_context(task_id: str, condition_dir: Path) -> Path:
    path = condition_dir / f"{task_id}_summary.md"
    write_text(path, SNAP_SUMMARY_FALLBACK.format(task_id=task_id))
    return path


def prepare(args: argparse.Namespace) -> Path:
    root = args.root.resolve()
    task_id = args.task.upper()
    output_dir = resolve(root, args.output_dir)
    condition_dir = resolve(root, args.condition_dir)
    papertoskill_context = resolve(root, args.papertoskill_context)
    lock = load_lock(root, task_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_manifest_path = output_dir / "dataset_manifest.json"
    budget_path = output_dir / "resource_budget.json"
    schema_path = output_dir / "expected_artifact_schema.json"
    preprocessing_path = output_dir / "preprocessing_notes.md"
    task_prompt_path = output_dir / "task_prompt.md"
    summary_path = write_summary_context(task_id, condition_dir)
    miniature_path: Path | None = None
    miniature_source_path: Path | None = None
    scorer_thresholds_path: Path | None = None

    if args.materialization_mode == "official_miniature_fixture":
        if args.dataset_manifest:
            raise ValueError("--dataset-manifest cannot be combined with official_miniature_fixture mode")
        if not args.snapatac2_root:
            raise ValueError("--snapatac2-root is required for official_miniature_fixture mode")
        snapatac2_root = args.snapatac2_root.resolve()
        source_relative = args.mini_fragment_source or DEFAULT_MINIATURE_SOURCES[task_id]
        miniature_source_path = resolve_against(snapatac2_root, source_relative)
        if not miniature_source_path.exists():
            raise ValueError(f"missing miniature SnapATAC2 fixture source: {miniature_source_path}")
        miniature_path = output_dir / "miniature_fragment.tsv.gz"
        shutil.copy2(miniature_source_path, miniature_path)
        copy_or_write_json(
            None,
            dataset_manifest_path,
            materialized_dataset_manifest(
                root,
                task_id,
                lock,
                snapatac2_root=snapatac2_root,
                source_path=miniature_source_path,
                copied_path=miniature_path,
            ),
        )
        scorer_thresholds_path = output_dir / "scorer_thresholds.json"
        write_json(scorer_thresholds_path, default_scorer_thresholds(task_id))
    else:
        copy_or_write_json(args.dataset_manifest, dataset_manifest_path, default_dataset_manifest(task_id, lock))
    copy_or_write_json(args.resource_budget, budget_path, default_budget(task_id))
    write_json(schema_path, expected_schema(task_id))
    write_text(preprocessing_path, preprocessing_notes(task_id))
    write_text(task_prompt_path, make_task_prompt(task_id))

    files = [
        file_entry(root, dataset_manifest_path, "dataset_manifest", "model_visible"),
        file_entry(root, preprocessing_path, "preprocessing_notes", "model_visible"),
        file_entry(root, budget_path, "resource_budget", "model_visible"),
        file_entry(root, schema_path, "expected_artifact_schema", "model_visible"),
        file_entry(root, task_prompt_path, "task_prompt", "model_visible"),
        file_entry(root, summary_path, "summary_context", "condition_context"),
    ]
    if miniature_path:
        files.append(file_entry(root, miniature_path, "miniature_fragment", "model_visible"))
    hidden_from_model: list[str] = []
    if scorer_thresholds_path:
        files.append(file_entry(root, scorer_thresholds_path, "scorer_thresholds", "scorer_only"))
        hidden_from_model.append(relative(root, scorer_thresholds_path))
    if args.reference_labels:
        labels_path = output_dir / "reference_labels_or_proxy.json"
        shutil.copy2(resolve(root, args.reference_labels), labels_path)
        files.append(file_entry(root, labels_path, "reference_labels_or_proxy", "scorer_only"))
        hidden_from_model.append(relative(root, labels_path))
    elif args.materialization_mode == "official_miniature_fixture" and task_id == "SNAP-T2":
        labels_path = output_dir / "reference_labels_or_proxy.json"
        write_json(labels_path, default_proxy_labels(task_id))
        files.append(file_entry(root, labels_path, "reference_labels_or_proxy", "scorer_only"))
        hidden_from_model.append(relative(root, labels_path))

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "papertoskill_real_reuse_v0",
        "task_id": task_id,
        "source_paper_id": "snapatac2",
        "status": STATUS,
        "prepared_on": PREPARED_ON,
        "materialization_mode": args.materialization_mode,
        "evidence_boundary": (
            "Prepared SnapATAC2 fixture metadata and condition contexts for dry "
            "scoring. This manifest does not run a model, compare Summary "
            "against PaperToSkill, score downstream outputs, or claim task "
            "success. Official miniature fixture files, when present, are smoke "
            "assets only and are not full SnapATAC2 paper reproductions."
        ),
        "locked_task_instance": lock.get("locked_task_instance", {}),
        "condition_contexts": [
            {"condition": "summary", "path": relative(root, summary_path), "visibility": "model_visible"},
            {"condition": "papertoskill", "path": relative(root, papertoskill_context), "visibility": "model_visible"},
        ],
        "hidden_from_model": hidden_from_model,
        "asset_dir": relative(root, output_dir),
        "files": files,
    }
    manifest_path = output_dir / "asset_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare locked SnapATAC2 real-reuse fixture assets.")
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--materialization-mode", choices=MATERIALIZATION_MODES, default="metadata_only")
    parser.add_argument("--snapatac2-root", type=Path)
    parser.add_argument("--mini-fragment-source", type=Path)
    parser.add_argument("--dataset-manifest", type=Path)
    parser.add_argument("--resource-budget", type=Path)
    parser.add_argument("--reference-labels", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition-dir", type=Path, default=Path("baselines/real_reuse"))
    parser.add_argument(
        "--papertoskill-context",
        type=Path,
        default=Path("generated_skills/real_reuse/snapatac2/SKILL.md"),
    )
    args = parser.parse_args()

    try:
        manifest_path = prepare(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
