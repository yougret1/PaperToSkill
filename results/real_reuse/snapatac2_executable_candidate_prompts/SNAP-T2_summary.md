# SNAP Executable-Candidate Prompt: SNAP-T2 / summary

You are preparing a Python candidate script for a locked SnapATAC2 real-reuse diagnostic rerun.

Return one Python script only. Do not wrap it in Markdown fences.

The script must be executable by `scripts/run_real_reuse_snapatac2_executable_candidate.py`.

## Candidate Script Interface

Your script must accept these command-line arguments:
- `--task-id`
- `--condition`
- `--fragment`
- `--artifact-dir`
- `--result-json`

Expected file name for this packet: `SNAP-T2_summary.py`.
Use the `--fragment` path for the locked miniature fixture. The current fixture path is `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`.
Create these required artifacts under `--artifact-dir`: clusters.csv, marker_summary.json, embedding.csv.
Write optional candidate-side notes and quality metrics to `--result-json` as JSON.
Do not set final task completion by yourself; the runner owns `completed=true` only after execution and artifact checks.

## Evidence Boundary

This prompt packet prepares a future paired diagnostic rerun.
It must not append to `results/real_reuse/raw_rows.jsonl`.
It must not replace paper-facing main rows unless a later explicit promotion updates `results/real_reuse/main_run_selection.json`.
Do not request scorer-only labels, scorer thresholds, or hidden metrics.

## Condition Context

# Real-Reuse Summary Baseline: SNAP-T2

SnapATAC2 is a scalable single-cell omics analysis workflow centered on
matrix-free spectral embedding. A source-consistent reuse attempt should load
the declared dataset, preserve preprocessing assumptions such as IDF scaling
and normalization when relevant, run embedding/clustering or multimodal
analysis, and report objective artifacts plus runtime and memory.

For this locked task, produce machine-readable analysis artifacts, log runtime
and memory, and avoid subjective biological interpretation as the main score.


## Model-Visible Locked Assets

## dataset_manifest
Path: `benchmarks/real_reuse/assets/SNAP-T2/dataset_manifest.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T2",
  "dataset_function": "snapatac2.datasets.pbmc10k_multiome",
  "tutorial_path": "docs/tutorials/modality.ipynb",
  "tutorial_lfs_oid": "sha256:79c7640e3fc12e0f2a9b9aac4f834cc4822865c5cbc3600358bd63ff7b1c8c37",
  "materialization_mode": "official_miniature_fixture",
  "dataset_status": "official_repository_miniature_fixture_materialized",
  "source_repository": {
    "url": "https://github.com/scverse/SnapATAC2",
    "local_path": "D:/a_work/gitee/SnapATAC2",
    "revision": "7be57442708694217e27c8654ecd38a0de194aa4",
    "license": "MIT",
    "license_path": "D:/a_work/gitee/SnapATAC2/LICENSE",
    "license_sha256": "68fa1c3e3011303beb02a4333b2b0aa9f95601f1dbf818b887f9431fbdb74138"
  },
  "official_dataset_references": [
    {
      "name": "10x-Multiome-Pbmc10k-ATAC.h5ad",
      "checksum": "sha256:24d030fb7f90453a0303b71a1e3e4e7551857d1e70072752d7fff9c918f77217"
    },
    {
      "name": "10x-Multiome-Pbmc10k-RNA.h5ad",
      "checksum": "sha256:a25327acff48b20b295c12221a84fd00f8f3f486ff3e7bd090fdef241b996a22"
    },
    {
      "name": "pbmc_10k_atac.tsv.gz",
      "checksum": "md5:a959ef83dfb9cae6ff73ab0147d547d1"
    }
  ],
  "miniature_fixture": {
    "source_path": "D:/a_work/gitee/SnapATAC2/tests/test_tools/test_clean.tsv.gz",
    "copied_path": "benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz",
    "sha256": "95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251",
    "size_bytes": 309344
  },
  "evidence_boundary": "This materializes a small official SnapATAC2 repository fixture for smoke and fixture-readiness checks. It is not the full pbmc5k or pbmc10k_multiome dataset, not a reproduction of the SnapATAC2 paper scores, and not a PaperToSkill downstream result."
}
```

## preprocessing_notes
Path: `benchmarks/real_reuse/assets/SNAP-T2/preprocessing_notes.md`

```
# SNAP-T2 SnapATAC2 Preprocessing Notes

- Use a SnapATAC2-style path: load the declared single-cell data, preserve
  source-paper preprocessing assumptions, and run dimensionality reduction
  before downstream clustering or artifact reporting.
- Keep objective logs separate from interpretation. The scorer expects
  machine-readable artifacts and ARI/NMI or pre-registered proxy plus runtime/memory.
- Do not expose scorer-only labels, thresholds, or post-run metric files to the
  model condition context.

```

## resource_budget
Path: `benchmarks/real_reuse/assets/SNAP-T2/resource_budget.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T2",
  "max_runtime_seconds": 1800,
  "max_peak_memory_mb": 8192,
  "same_budget_across_conditions": true
}
```

## expected_artifact_schema
Path: `benchmarks/real_reuse/assets/SNAP-T2/expected_artifact_schema.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T2",
  "candidate_output_file": "candidate_output.json",
  "required_fields": [
    "completed",
    "method_steps",
    "clustering_artifacts",
    "quality_metrics",
    "runtime_seconds",
    "peak_memory_mb"
  ],
  "optional_fields": [
    "predicted_labels",
    "notes",
    "commands"
  ]
}
```

## task_prompt
Path: `benchmarks/real_reuse/assets/SNAP-T2/task_prompt.md`

```
# SNAP-T2 Locked SnapATAC2 Task Prompt

Objective: Produce dimensionality reduction plus clustering/marker artifacts and objective quality/resource metrics for the declared dataset.

Metric: ari_nmi_runtime_memory

Return one JSON object only. Required top-level fields:

completed, method_steps, clustering_artifacts, quality_metrics, runtime_seconds, peak_memory_mb

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.

```

## miniature_fragment
- Path: `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`
- SHA256: `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`
- Do not inline this gzip file; pass its path to the candidate script through `--fragment`.

## Output Requirements

Return valid Python code only.
The code should be deterministic on the provided miniature fixture.
Prefer lightweight standard-library or widely available scientific Python logic.
If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.
