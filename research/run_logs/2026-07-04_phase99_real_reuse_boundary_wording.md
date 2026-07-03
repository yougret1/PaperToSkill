# 2026-07-04 Phase 99 Real-Reuse Boundary Wording

## Purpose

Clean up generated real-reuse table boundary wording after the first
eight-row GPT-family `gpt-5.5` pass filled all planned real-reuse rows.

## Changes

- Updated `scripts/build_real_reuse_paper_tables.py` so generated Markdown and
  JSON evidence-boundary text says score cells are generated from raw rows when
  available and any future unfilled cells are planning placeholders.
- Regenerated:
  - `results/real_reuse/main_results_plan.md`
  - `results/real_reuse/main_results_plan.json`
- Added regression assertions in
  `tests/test_build_real_reuse_paper_tables.py` to prevent reintroducing the
  stale "pending cells" wording in newly generated table artifacts.

## Verification

- `python -m unittest tests.test_build_real_reuse_paper_tables -v`
- `python scripts\check_paper_tables.py --strict`
- `python scripts\check_paper_claims.py --strict`
- `python scripts\check_reproducibility_package.py --strict`

All listed checks passed before final phase verification.

## Evidence Boundary

This phase changes wording only. It does not change real-reuse scores, add new
rows, rerun models, complete human fidelity annotation, or support aggregate
downstream effectiveness claims.
