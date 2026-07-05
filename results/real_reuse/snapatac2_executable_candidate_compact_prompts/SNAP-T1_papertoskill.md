# SNAP Executable-Candidate Compact Prompt: SNAP-T1 / papertoskill

Return exactly one Python script, no Markdown fences. It must run under `scripts/run_real_reuse_snapatac2_executable_candidate.py`.

This compact local-path/SHA packet prepares a future paired diagnostic rerun; it is not scored evidence.

## Interface

Accept: `--task-id`, `--condition`, `--fragment`, `--artifact-dir`, `--result-json`.
Expected file name for this packet: `SNAP-T1_papertoskill.py`.
Fixture path passed through `--fragment`: `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`.
Create under `--artifact-dir`: embedding.csv, cell_features.csv, fragment_summary.json.
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
- Path: `benchmarks/real_reuse/assets/SNAP-T1/dataset_manifest.json`
- SHA256: `22ce79319f5059514cd6c203c0240d94ab55ca9cd4419660e21ba3873569016d`
- Compact summary:
- dataset_function: "snapatac2.datasets.pbmc5k"
- materialization_mode: "official_miniature_fixture"
- dataset_status: "official_repository_miniature_fixture_materialized"
- miniature_fixture.copied_path: "benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz"
- miniature_fixture.sha256: "c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612"
- miniature_fixture.size_bytes: 315693
- source_repository.revision: "7be57442708694217e27c8654ecd38a0de194aa4"
- source_repository.license: "MIT"

## preprocessing_notes
- Path: `benchmarks/real_reuse/assets/SNAP-T1/preprocessing_notes.md`
- SHA256: `b7525b47f43b57a4fed9de8126a451b5bc58ac88f36638b1ad9de4cc11f583df`
- Compact summary:
- # SNAP-T1 SnapATAC2 Preprocessing Notes
- - Use a SnapATAC2-style path: load the declared single-cell data, preserve
- source-paper preprocessing assumptions, and run dimensionality reduction
- before downstream clustering or artifact reporting.
- machine-readable artifacts and runtime/memory plus embedding artifact checks.

## resource_budget
- Path: `benchmarks/real_reuse/assets/SNAP-T1/resource_budget.json`
- SHA256: `3310e5ab1dc96688197f165971b4fb228706106f108e75a2e8bbc01bbaeb3095`
- Compact summary:
- max_runtime_seconds: 1800
- max_peak_memory_mb: 8192
- same_budget_across_conditions: true

## expected_artifact_schema
- Path: `benchmarks/real_reuse/assets/SNAP-T1/expected_artifact_schema.json`
- SHA256: `251d39a2b6f8ace388484fe14c1f3db9799f4c095497c3ffd4796d943ed4ef6c`
- Compact summary:
- required_fields: ["completed", "method_steps", "embedding_artifacts", "runtime_seconds", "peak_memory_mb"]
- optional_fields: ["predicted_labels", "notes", "commands"]

## task_prompt
- Path: `benchmarks/real_reuse/assets/SNAP-T1/task_prompt.md`
- SHA256: `0626f9e5960b81d854d5899f209060685e4f37a33815fda50615b1d7123d4737`
- Compact summary:
- # SNAP-T1 Locked SnapATAC2 Task Prompt
- Objective: Produce a runnable analysis plan and machine-readable embedding artifact record for the declared small single-cell dataset.
- Metric: runtime_memory_quality
- completed, method_steps, embedding_artifacts, runtime_seconds, peak_memory_mb
- Include `predicted_labels` only if the task asks for clustering labels. Do not
- claim a completed run unless the output records concrete artifacts and runtime

## miniature_fragment
- Path: `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`
- SHA256: `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`
- Use this gzip file only through the candidate script `--fragment` argument.

## Output Requirements

Return valid Python code only.
The code should be deterministic on the provided miniature fixture.
If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.
