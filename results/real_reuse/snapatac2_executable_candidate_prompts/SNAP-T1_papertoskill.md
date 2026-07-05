# SNAP Executable-Candidate Prompt: SNAP-T1 / papertoskill

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

Expected file name for this packet: `SNAP-T1_papertoskill.py`.
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

---
name: snapatac2-paper-skill
description: Use when applying the paper-derived method from A fast, scalable and versatile tool for analysis of single-cell omics data as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# A fast, scalable and versatile tool for analysis of single-cell omics data

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/auto_notes/snapatac2_auto_note.md`

## Paper Snapshot

... addressing cellular diversity across varied molecular modalities. Here we introduce
a nonlinear dimensionality reduction algorithm, embodied in the Python package
SnapATAC2, which not only achieves a more precise capture of single-cell omics data
heterogeneities but also ensures efficient ... Source anchors: lines 18-43.

## Central Contribution

Here we introduce a nonlinear dimensionality reduction algorithm, embodied in the Python
package SnapATAC2, which not only achieves a more precise capture of single-cell omics
data heterogeneities but also ensures efficient ...

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Frame the method as matrix-free spectral embedding for scalable nonlinear dimensionality reduction: ... to project the high-dimensional data into low-dimensional space while retaining the relative relationships between cells, a process known as dimensionality reduction. This step .... Source anchors: lines 23-27.
2. Use SnapATAC2's workflow modules for preprocessing, embedding/clustering, enrichment, and multimodal analysis: ... 14 . The SnapATAC2 package is made up of four main parts: preprocessing, embedding/clustering, functional enrichment analysis and multimodal omics analysis (Fig. 1a ). The .... Source anchors: lines 28-32.
3. Preserve the source preprocessing sequence for spectral embedding: IDF scaling, row-wise L2 normalization, degree normalization, and eigenvectors: ... scaling with inverse term frequency, row-wise L 2 norm normalization, normalization using the degree matrix and eigenvector calculation through the Lanczos algorithm 25 . .... Source anchors: lines 33-37.
4. Avoid constructing the full similarity matrix and compute eigenvectors with Lanczos matrix-vector products: ... we first compute the n n pairwise similarity matrix W such that \({W}_{{ij}}=\delta \left({C}_{i* },{C}_{j* }\right)\) , where \(\delta :{{\mathbb{R}}}^{p}\times .... Source anchors: lines 75-79.
5. Use out-of-sample Nystrom landmarks when the full cell-by-feature matrix is too large: Nystrom method for out-of-sample embedding The matrix-free method described above is very fast and memory efficient. However, for massive datasets with hundreds of millions of .... Source anchors: lines 80-84.
6. Extend the workflow to multi-view spectral embedding for paired ATAC/RNA or other multi-omics views: ... to single-cell multimodal omics data. Multi-view spectral embedding is an extension of spectral embedding, which enables the joint embedding of multiple data representation .... Source anchors: lines 61-65.
7. Select informative eigenvectors before downstream clustering instead of trusting every spectral component: ... is shown in Extended Data Fig. 10d . Eigenvector selection in spectral embedding Not all eigenvectors produced by spectral embedding are informative and relevant for .... Source anchors: lines 85-89.

## Validation

- Benchmark runtime and memory against LSI, LDA, PCA, classic spectral embedding, and neural models: ... scATAC-seq data. d , Line plots comparing memory usage of various dimensionality reduction algorithms for scATAC-seq data. Neural network-based methods were excluded from this .... Source anchors: lines 33-37.
- Report the paper's scalability references for 200,000 cells and the end-to-end ArchR comparison: ... SnapATAC2 stood out by requiring only 21 GB of memory to process 200,000 cells (Fig. 1d ). In contrast, the original SnapATAC package showed limitations, encountering .... Source anchors: lines 38-42.
- Evaluate robustness to sequencing depth, noise, and rare cell-type abundance with ARI or silhouette metrics: ... outperformed other methods across varying sequencing depths, achieving the highest ARI scores. For example, at a sequencing depth of 5,000 reads per cell, all tested algorithms .... Source anchors: lines 44-48.
- Use real scATAC-seq benchmarks with cell labels and bio-conservation metrics: ... the quality of cell embeddings produced by various methods, we used a range of metrics: ARI, AMI, cell-type ASW and graph cLISI 43 . For batch effect removal analysis .... Source anchors: lines 106-110.
- Test transfer across scHi-C, scRNA-seq, DNA methylation, batch correction, and single-cell multiome data: ... our analysis, we applied SnapATAC2 to scRNA-seq datasets and compared its performance to two other methods commonly used for dimensionality reduction in this domain: scVI .... Source anchors: lines 57-61.
- Score embedding quality with normalized bio-conservation and batch-correction metrics instead of subjective interpretation: ... (graph iLISI) and cell-type separation (graph cLISI). LISI scores were computed using neighborhood lists from integrated k -NN graphs. The metric leverages the inverse .... Source anchors: lines 111-115.

## Failure Cases

- Do not claim arbitrary similarity metrics because the matrix-free implementation is currently cosine-specific: ... limitation of the matrix-free spectral embedding algorithm is that it currently is implemented using only cosine function-based similarity. For some data types, researchers .... Source anchors: lines 70-74.
- Use Nystrom landmarks or other memory controls when the cell-by-feature matrix itself is too large: ... is shown in Extended Data Fig. 10a . Nystrom method for out-of-sample embedding The matrix-free method described above is very fast and memory efficient. However, for .... Source anchors: lines 77-81.
- Treat neural-network runtime and memory comparisons carefully because GPU feature limits and preprocessing exclusions affect comparability: ... SCALE, we conducted the experiments on an A100 GPU equipped with 40 GB of memory. Notably, the memory usage of these methods is influenced more by the number of features than .... Source anchors: lines 118-122.
- Preserve dataset and label provenance when scoring ARI, AMI, ASW, cLISI, iLISI, or kBET: ... with different dimensions of the latent variable: 5, 10, 15, 20, 25 and 30. We then used the evaluate_models function to select the best model for downstream analysis. .... Source anchors: lines 103-107.
- Use public data and official code availability records when reproducing benchmark-style tasks: Data availability We processed various public scATAC-seq datasets for our benchmarking analysis, with the datasets listed in Table 1 . These include: 10x Genomics scATAC-seq data .... Source anchors: lines 149-153.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.


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
