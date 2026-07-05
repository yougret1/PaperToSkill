# SNAP Executable-Candidate Prompt: SNAP-T1 / summary

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

Expected file name for this packet: `SNAP-T1_summary.py`.
Use the `--fragment` path for the locked miniature fixture. The current fixture path is `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`.
Create these required artifacts under `--artifact-dir`: embedding.csv, cell_features.csv, fragment_summary.json.
Write optional candidate-side notes and quality metrics to `--result-json` as JSON.
Do not set final task completion by yourself; the runner owns `completed=true` only after execution and artifact checks.

## Evidence Boundary

This prompt packet prepares a future paired diagnostic rerun.
It must not append to `results/real_reuse/raw_rows.jsonl`.
It must not replace paper-facing main rows unless a later explicit promotion updates `results/real_reuse/main_run_selection.json`.
Do not request scorer-only labels, scorer thresholds, or hidden metrics.

## Condition Context

# Real-Reuse Summary Baseline: SNAP-T1

SnapATAC2 is a scalable single-cell omics analysis workflow centered on
matrix-free spectral embedding. A source-consistent reuse attempt should load
the declared dataset, preserve preprocessing assumptions such as IDF scaling
and normalization when relevant, run embedding/clustering or multimodal
analysis, and report objective artifacts plus runtime and memory.

For this locked task, produce machine-readable analysis artifacts, log runtime
and memory, and avoid subjective biological interpretation as the main score.


## Model-Visible Locked Assets

## dataset_manifest
Path: `benchmarks/real_reuse/assets/SNAP-T1/dataset_manifest.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T1",
  "dataset_function": "snapatac2.datasets.pbmc5k",
  "tutorial_path": "docs/tutorials/pbmc.ipynb",
  "tutorial_lfs_oid": "sha256:7b58060a27e69637f01ad41ebcdadb86cf023d3a912307da6b094b2bdf32fa9b",
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
      "name": "atac_pbmc_5k.tsv.gz",
      "checksum": "sha256:5fe44c0f8f76ce1534c1ae418cf0707ca5ef712004eee77c3d98d2d4b35ceaec"
    },
    {
      "name": "atac_pbmc_5k.h5ad",
      "checksum": "sha256:92ae7f185cdec26517fd8d5acb60b2ce92c71e0ace824de35589c6d7942cab06"
    },
    {
      "name": "atac_pbmc_5k_annotated.h5ad",
      "checksum": "sha256:592f1551c27d0cfe4d81e7febad624d6b7d3ebf977b0c3ea64e06b3f3d76f078"
    }
  ],
  "miniature_fixture": {
    "source_path": "D:/a_work/gitee/SnapATAC2/tests/test_tools/test_single.tsv.gz",
    "copied_path": "benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz",
    "sha256": "c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612",
    "size_bytes": 315693
  },
  "evidence_boundary": "This materializes a small official SnapATAC2 repository fixture for smoke and fixture-readiness checks. It is not the full pbmc5k or pbmc10k_multiome dataset, not a reproduction of the SnapATAC2 paper scores, and not a PaperToSkill downstream result."
}
```

## preprocessing_notes
Path: `benchmarks/real_reuse/assets/SNAP-T1/preprocessing_notes.md`

```
# SNAP-T1 SnapATAC2 Preprocessing Notes

- Use a SnapATAC2-style path: load the declared single-cell data, preserve
  source-paper preprocessing assumptions, and run dimensionality reduction
  before downstream clustering or artifact reporting.
- Keep objective logs separate from interpretation. The scorer expects
  machine-readable artifacts and runtime/memory plus embedding artifact checks.
- Do not expose scorer-only labels, thresholds, or post-run metric files to the
  model condition context.

```

## resource_budget
Path: `benchmarks/real_reuse/assets/SNAP-T1/resource_budget.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T1",
  "max_runtime_seconds": 1800,
  "max_peak_memory_mb": 8192,
  "same_budget_across_conditions": true
}
```

## expected_artifact_schema
Path: `benchmarks/real_reuse/assets/SNAP-T1/expected_artifact_schema.json`

```
{
  "schema_version": "0.1",
  "task_id": "SNAP-T1",
  "candidate_output_file": "candidate_output.json",
  "required_fields": [
    "completed",
    "method_steps",
    "embedding_artifacts",
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
Path: `benchmarks/real_reuse/assets/SNAP-T1/task_prompt.md`

```
# SNAP-T1 Locked SnapATAC2 Task Prompt

Objective: Produce a runnable analysis plan and machine-readable embedding artifact record for the declared small single-cell dataset.

Metric: runtime_memory_quality

Return one JSON object only. Required top-level fields:

completed, method_steps, embedding_artifacts, runtime_seconds, peak_memory_mb

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.

```

## miniature_fragment
- Path: `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`
- SHA256: `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`
- Do not inline this gzip file; pass its path to the candidate script through `--fragment`.

## Output Requirements

Return valid Python code only.
The code should be deterministic on the provided miniature fixture.
Prefer lightweight standard-library or widely available scientific Python logic.
If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.
