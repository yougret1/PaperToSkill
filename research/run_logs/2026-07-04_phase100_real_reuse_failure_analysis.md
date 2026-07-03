# 2026-07-04 Phase 100 Real-Reuse Failure Analysis

## Purpose

Make the mixed first-pass real-reuse results easier to review by deriving a
row-level failure-boundary table from the existing raw rows.

## Changes

- Added `scripts/build_real_reuse_failure_analysis.py`.
- Added `tests/test_build_real_reuse_failure_analysis.py`.
- Generated:
  - `results/real_reuse/failure_analysis.csv`
  - `results/real_reuse/failure_analysis.md`
  - `results/real_reuse/failure_analysis.json`
- Added `tab:real-reuse-failure-analysis` to
  `paper/aaai/papertoskill_tables.tex`.
- Added a Results sentence pointing to the new table.
- Extended `scripts/check_paper_tables.py` and its tests to validate the new
  table against `results/real_reuse/failure_analysis.csv`.
- Added the builder and output files to the reproducibility package gate.
- Updated outline, artifact map, claim matrix, runbook, rebuttal bank, result
  cards, and memory.

## Derived Table Summary

- AIDE-T1/T2: budget timeout.
- SWE-T1: patch application.
- SWE-T2: PaperToSkill-only success.
- REF-T1/T2: solved by both.
- SNAP-T1/T2: artifact completion.

## Verification

- `python -m unittest tests.test_build_real_reuse_failure_analysis tests.test_check_paper_tables tests.test_check_reproducibility_package -v`
- `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` over the AAAI draft.
- `python scripts\check_paper_tables.py --strict`
- `python scripts\check_paper_claims.py --strict`
- `python scripts\check_aaai_package.py --strict`
- `python scripts\check_reproducibility_package.py --strict`

All listed checks passed before final full verification.

## Evidence Boundary

The table is derived from existing scored raw rows. It does not add new task
success evidence, complete human fidelity annotation, or support aggregate
downstream effectiveness claims.
