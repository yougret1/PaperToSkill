# 2026-07-03 Phase 94 SnapATAC2 Fixture Materialization

## Objective

Move SnapATAC2 from execution-layer readiness to fixture readiness for the main
real-reuse experiment, without claiming downstream task success.

## Actions

- Extended `scripts/prepare_real_reuse_snapatac2_fixture.py` with
  `official_miniature_fixture` materialization mode.
- Materialized SNAP-T1 and SNAP-T2 fixture assets from the official local
  SnapATAC2 checkout at `D:\a_work\gitee\SnapATAC2`.
- Copied official repository test fragments into:
  - `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`
  - `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`
- Wrote dataset manifests with source repository revision, MIT license
  provenance, official dataset references, tutorial LFS OIDs, copied-file
  checksums, and a boundary that the miniature fixtures are not full pbmc5k or
  pbmc10k_multiome reproductions.
- Added scorer-only `scorer_thresholds.json` assets and a SNAP-T2
  `reference_labels_or_proxy.json` policy while keeping hidden assets out of
  model-visible prompts.
- Updated `scripts/score_real_reuse_snapatac2.py` so scorer-only thresholds
  control local success判定.
- Updated `scripts/check_real_reuse_benchmark.py` and
  `scripts/check_reproducibility_package.py` so prepared SNAP assets are
  validated by local gates.
- Refreshed `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex`; SNAP-T1/T2 now show `Ready to run`
  with score cells still `Pending`.
- Updated `paper/aaai/papertoskill_aaai2027.tex` to state that AIDE awaits
  dataset, SWE remains fixture-pending, and SnapATAC2 has prepared miniature
  fixture assets but no scored rows.
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf`.

## Materialized Assets

- SNAP-T1 miniature source:
  `D:\a_work\gitee\SnapATAC2\tests\test_tools\test_single.tsv.gz`
  - SHA256: `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`
- SNAP-T2 miniature source:
  `D:\a_work\gitee\SnapATAC2\tests\test_tools\test_clean.tsv.gz`
  - SHA256: `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`
- SnapATAC2 source revision:
  `7be57442708694217e27c8654ecd38a0de194aa4`

## Results

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 462
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 415 ready checks, 1 pending check,
  and 0 failed checks.
- `results/reproducibility/paper_table_report.md` reports ready, 156 ready
  checks, and 0 failed checks.
- `results/reproducibility/aaai_package_report.md` reports ready, 17 ready
  checks, and 0 failed checks.
- Full unit discovery passed with 155 tests.
- All strict local gates passed before phase save.

## Evidence Boundary

- This phase is SnapATAC2 fixture-readiness evidence only.
- The official miniature fixtures are smoke/fixture assets from the SnapATAC2
  repository; they are not the full SnapATAC2 paper datasets and not reproduced
  paper scores.
- No SNAP Summary or PaperToSkill raw rows were appended.
- No SNAP task score was added to the paper.
- The current real-reuse effectiveness evidence remains the partial REF-T1 and
  REF-T2 GPT-family slice; it still does not establish aggregate PaperToSkill
  advantage over Summary.
