# Phase 105 Full Excerpt Sanity Execution

Date: 2026-07-04

## Purpose

Move the auxiliary Full Excerpt sanity check from a table scaffold to scored
rows for the pre-registered AIDE-T1, SWE-T1, and SNAP-T1 subset, without
promoting Full Excerpt to a main baseline.

## Code Changes

- `scripts/build_real_reuse_task_specs.py` now adds a
  `full_paper_excerpt_sanity` condition only for pre-registered sanity tasks.
- `scripts/check_real_reuse_benchmark.py` verifies that AIDE-T1, SWE-T1, and
  SNAP-T1 include `full_excerpt`, while non-sanity tasks do not.
- `scripts/run_real_reuse_aide.py`, `scripts/run_real_reuse_swe.py`, and
  `scripts/run_real_reuse_snapatac2.py` accept explicit
  `--condition full_excerpt` but still default to Summary/PaperToSkill.
- `scripts/score_real_reuse_aide.py` now terminates candidate process trees on
  timeout, so heavy AIDE scripts return a scored timeout metric instead of
  hanging the scorer.

## Runs

- AIDE-T1 Full Excerpt:
  - live GPT-family response was produced under
    `results/real_reuse/runs/AIDE-T1/full_excerpt/phase105_gpt_full_excerpt_sanity/`;
  - after the scorer timeout fix, the saved live response was scored through
    the AIDE runner fixture-response path with the 60-second AIDE budget;
  - score: 0.000; failure reason: `timeout after 60s`.
- SWE-T1 Full Excerpt:
  - first live attempt with two 120-second reads timed out;
  - retry with one 240-second read completed and scored;
  - score: 0.000; failure reason: `patch_apply_failed`.
- SNAP-T1 Full Excerpt:
  - live GPT-family `gpt-5.5` run completed on the first attempt;
  - score: 0.250; failure reason: `missing_required_artifacts_or_metrics`.

## Generated Artifacts

- `results/real_reuse/raw_rows.jsonl`
- `results/real_reuse/full_excerpt_sanity.csv`
- `results/real_reuse/full_excerpt_sanity.md`
- `results/real_reuse/full_excerpt_sanity.json`
- `paper/aaai/papertoskill_tables.tex`
- `paper/aaai/papertoskill_aaai2027.tex`

## Verification So Far

- `python -m unittest tests.test_build_real_reuse_task_specs tests.test_check_real_reuse_benchmark tests.test_run_real_reuse_aide tests.test_run_real_reuse_swe tests.test_run_real_reuse_snapatac2 -v`: passed, 23 tests.
- `python -m unittest tests.test_score_real_reuse_aide -v`: passed, 5 tests.
- `python scripts\check_real_reuse_benchmark.py --strict`: passed.
- `python scripts\check_paper_tables.py --strict`: passed.
- `python scripts\check_paper_claims.py --strict`: passed.

## Evidence Boundary

This is an auxiliary three-row sanity check. It answers whether a small
Full Excerpt condition changes interpretation on selected rows. It does not
make Full Excerpt a main baseline, does not produce a broad context-length
claim, and does not establish aggregate downstream effectiveness.
