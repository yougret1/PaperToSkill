# Phase 104 Full Excerpt Sanity Scaffold

Date: 2026-07-04

## Objective

Add a bounded auxiliary Full Excerpt sanity scaffold for the real-reuse
experiment without changing the main effectiveness claim.

## Actions

- Added `scripts/build_real_reuse_full_excerpt_sanity.py`.
- Added `tests/test_build_real_reuse_full_excerpt_sanity.py`.
- Generated `results/real_reuse/full_excerpt_sanity.{csv,md,json}` for
  AIDE-T1, SWE-T1, and SNAP-T1.
- Added `tab:full-excerpt-sanity` to the AAAI table file and a short setup
  paragraph in the AAAI draft.
- Extended `scripts/check_paper_tables.py` so the AAAI table is checked
  against `results/real_reuse/full_excerpt_sanity.csv`.
- Extended `scripts/check_reproducibility_package.py` so the builder and three
  generated outputs are package-gated artifacts.
- Updated research docs, result cards, memory, and reviewer handoff materials
  to keep the scaffold separate from main real-reuse task-success evidence.

## Current Table

`results/real_reuse/full_excerpt_sanity.md` contains:

- AIDE-T1: Summary 0.000, PaperToSkill 0.000, Full Excerpt Pending.
- SWE-T1: Summary 0.000, PaperToSkill 0.000, Full Excerpt Pending.
- SNAP-T1: Summary 0.000, PaperToSkill 0.500, Full Excerpt Pending.

Token columns are local whitespace context proxies.

## Verification

- `python scripts\build_real_reuse_full_excerpt_sanity.py`: passed.
- `python -m unittest tests.test_build_real_reuse_full_excerpt_sanity tests.test_check_paper_tables tests.test_check_reproducibility_package -v`:
  6 tests passed.
- `python scripts\check_paper_tables.py --strict`: passed; paper-table report
  is ready with 226 ready checks and 0 failed checks.
- `python scripts\check_paper_claims.py --strict`: passed.
- `python scripts\check_aaai_package.py --strict`: passed.
- `python scripts\check_reproducibility_package.py --strict`: passed; package
  report is ready with pending external evidence, 427 ready checks, 1 pending
  check, and 0 failed checks.
- `python scripts\check_goal_completion.py --strict`: passed with expected
  pending external evidence; 77 ready checks, 3 pending checks, 0 failed
  checks.
- `python scripts\check_submission_review.py --strict`: passed; 16 ready
  checks, 0 failed checks.
- `python scripts\check_external_evidence_closure.py --strict`: passed.
- `python scripts\check_external_evidence_packets.py --strict`: passed.
- `python scripts\check_aaai_submission_decision.py --strict`: passed.
- `python scripts\check_usage_examples.py --strict`: passed.
- `python scripts\check_deepseek_followup.py --strict`: passed.
- `python scripts\check_ai_scientist_v2_live_run_handoff.py --strict`: passed.
- `python scripts\check_real_reuse_benchmark.py --strict`: passed.
- `python -m unittest discover -s tests -v`: 164 tests passed.
- `git diff --check`: passed with only expected Windows line-ending warnings.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## Evidence Boundary

This phase adds a table-ready scaffold only. It does not run the Full Excerpt
condition, does not add task-success evidence, and does not change the mixed
real-reuse first-pass interpretation. Pending Full Excerpt score cells are not
negative evidence.
