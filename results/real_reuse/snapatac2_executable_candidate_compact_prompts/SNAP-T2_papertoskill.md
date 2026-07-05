# SNAP Executable-Candidate Compact Prompt: SNAP-T2 / papertoskill

Return exactly one Python script, no Markdown fences. It must run under `scripts/run_real_reuse_snapatac2_executable_candidate.py`.

This compact local-path/SHA packet prepares a future paired diagnostic rerun; it is not scored evidence.

## Interface

Accept: `--task-id`, `--condition`, `--fragment`, `--artifact-dir`, `--result-json`.
Expected file name for this packet: `SNAP-T2_papertoskill.py`.
Fixture path passed through `--fragment`: `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`.
Create under `--artifact-dir`: clusters.csv, marker_summary.json, embedding.csv.
Write candidate notes/quality metrics to `--result-json` as JSON.
Runner owns final `completed=true` after execution/artifact checks.

## Hard Boundaries

No raw-row append; no main-row replacement unless `results/real_reuse/main_run_selection.json` is explicitly promoted later.
No scorer-only labels, scorer thresholds, hidden metrics, or post-run scorer files.
No network, package installation, package-manager subprocesses, or writes outside `--artifact-dir` and `--result-json`.
Use cross-platform Python for Windows/Linux; do not import `resource` or other POSIX-only modules.

## Compact Condition Context

- Full context path: `generated_skills/real_reuse/snapatac2/SKILL.md`
- Deterministic compact summary:
- name: snapatac2-paper-skill
- description: Use when applying the paper-derived method from A fast, scalable and versatile tool for analysis of single-cell omics data as an agent skill. Extracts workflow step...
- # A fast, scalable and versatile tool for analysis of single-cell omics data
- ## Source
- - Source file: `papers/auto_notes/snapatac2_auto_note.md`
- ## Paper Snapshot
- ... addressing cellular diversity across varied molecular modalities. Here we introduce
- SnapATAC2, which not only achieves a more precise capture of single-cell omics data
- ## Central Contribution
- package SnapATAC2, which not only achieves a more precise capture of single-cell omics
- ## Inputs
- - Available tools, runtime constraints, and output format expectations.
- ## Workflow
- 1. Frame the method as matrix-free spectral embedding for scalable nonlinear dimensionality reduction: ... to project the high-dimensional data into low-dimensional space while...

## Compact Model-Visible Locked Assets

## dataset_manifest
- Path: `benchmarks/real_reuse/assets/SNAP-T2/dataset_manifest.json`
- SHA256: `9ab6dd8e3f56bc2f57c250b82aad4bd1fedce8975e7f175a7cd28ba6206e04f6`
- Compact summary:
- dataset_function: "snapatac2.datasets.pbmc10k_multiome"
- materialization_mode: "official_miniature_fixture"
- dataset_status: "official_repository_miniature_fixture_materialized"
- miniature_fixture.copied_path: "benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz"
- miniature_fixture.sha256: "95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251"
- miniature_fixture.size_bytes: 309344
- source_repository.revision: "7be57442708694217e27c8654ecd38a0de194aa4"
- source_repository.license: "MIT"

## preprocessing_notes
- Path: `benchmarks/real_reuse/assets/SNAP-T2/preprocessing_notes.md`
- SHA256: `d611a7c295646a10dcc27140ddf1275a9f6fb1d681a063e337ec9c156885ae4a`
- Compact summary:
- # SNAP-T2 SnapATAC2 Preprocessing Notes
- - Use a SnapATAC2-style path: load the declared single-cell data, preserve
- source-paper preprocessing assumptions, and run dimensionality reduction
- before downstream clustering or artifact reporting.
- machine-readable artifacts and ARI/NMI or pre-registered proxy plus runtime/memory.

## resource_budget
- Path: `benchmarks/real_reuse/assets/SNAP-T2/resource_budget.json`
- SHA256: `1b43f1c1fb32ab34641bdac3478adccad92cd9d5951cab6e19bad4602a6b6130`
- Compact summary:
- max_runtime_seconds: 1800
- max_peak_memory_mb: 8192
- same_budget_across_conditions: true

## expected_artifact_schema
- Path: `benchmarks/real_reuse/assets/SNAP-T2/expected_artifact_schema.json`
- SHA256: `24c5b4087cabbc8cbcaabdee53f711b5b081c189297d74743bfc03a32d44a225`
- Compact summary:
- required_fields: ["completed", "method_steps", "clustering_artifacts", "quality_metrics", "runtime_seconds", "peak_memory_mb"]
- optional_fields: ["predicted_labels", "notes", "commands"]

## task_prompt
- Path: `benchmarks/real_reuse/assets/SNAP-T2/task_prompt.md`
- SHA256: `94c77787748a9aad93c33336ab9a9f7788976c4ed8f3a56a6a8d7a86cf507271`
- Compact summary:
- # SNAP-T2 Locked SnapATAC2 Task Prompt
- Objective: Produce dimensionality reduction plus clustering/marker artifacts and objective quality/resource metrics for the declared dataset.
- Metric: ari_nmi_runtime_memory
- completed, method_steps, clustering_artifacts, quality_metrics, runtime_seconds, peak_memory_mb
- Include `predicted_labels` only if the task asks for clustering labels. Do not
- claim a completed run unless the output records concrete artifacts and runtime

## miniature_fragment
- Path: `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`
- SHA256: `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`
- Use this gzip file only through the candidate script `--fragment` argument.

## Output Requirements

Return valid Python code only.
The code should be deterministic on the provided miniature fixture.
If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.
