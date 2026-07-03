# Real-Reuse Condition: summary

You are running a locked SnapATAC2 PaperToSkill real-reuse task. Use only the model-visible context and assets below. Do not request reference labels, scorer thresholds, post-run metrics, or other hidden scorer-only assets.

# Condition Context

# Real-Reuse Summary Baseline: SNAP-T2

SnapATAC2 is a scalable single-cell omics analysis workflow centered on
matrix-free spectral embedding. A source-consistent reuse attempt should load
the declared dataset, preserve preprocessing assumptions such as IDF scaling
and normalization when relevant, run embedding/clustering or multimodal
analysis, and report objective artifacts plus runtime and memory.

For this locked task, produce machine-readable analysis artifacts, log runtime
and memory, and avoid subjective biological interpretation as the main score.

# Model-Visible Fixture Assets

## dataset_manifest
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

## preprocessing_notes
# SNAP-T2 SnapATAC2 Preprocessing Notes

- Use a SnapATAC2-style path: load the declared single-cell data, preserve
  source-paper preprocessing assumptions, and run dimensionality reduction
  before downstream clustering or artifact reporting.
- Keep objective logs separate from interpretation. The scorer expects
  machine-readable artifacts and ARI/NMI or pre-registered proxy plus runtime/memory.
- Do not expose scorer-only labels, thresholds, or post-run metric files to the
  model condition context.

## resource_budget
{
  "schema_version": "0.1",
  "task_id": "SNAP-T2",
  "max_runtime_seconds": 1800,
  "max_peak_memory_mb": 8192,
  "same_budget_across_conditions": true
}

## expected_artifact_schema
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

# Locked Task Prompt

# SNAP-T2 Locked SnapATAC2 Task Prompt

Objective: Produce dimensionality reduction plus clustering/marker artifacts and objective quality/resource metrics for the declared dataset.

Metric: ari_nmi_runtime_memory

Return one JSON object only. Required top-level fields:

completed, method_steps, clustering_artifacts, quality_metrics, runtime_seconds, peak_memory_mb

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.

# Output Contract

Return exactly one JSON object. It must be parseable as `candidate_output.json` and include the required fields declared in the expected artifact schema.
