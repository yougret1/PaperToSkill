# 2026-07-03 Phase 93: SnapATAC2 Real-Reuse Execution Layer

## Purpose

Advance the non-agent/data-analysis real-reuse task family from `Runner
pending` to a locally verified execution-layer contract, while preserving the
boundary that no SNAP fixture assets or downstream task scores exist yet.

## Actions

- Added `scripts/prepare_real_reuse_snapatac2_fixture.py` for locked SNAP-T1
  and SNAP-T2 fixture preparation.
- Added `scripts/score_real_reuse_snapatac2.py` for deterministic scoring of
  candidate analysis artifacts.
- Added `scripts/run_real_reuse_snapatac2.py` for Summary and PaperToSkill
  prompt execution, response capture, metric scoring, raw-row writing, and
  availability/error separation.
- Added focused unit tests:
  - `tests/test_prepare_real_reuse_snapatac2_fixture.py`
  - `tests/test_score_real_reuse_snapatac2.py`
  - `tests/test_run_real_reuse_snapatac2.py`
- Extended the real-reuse preflight and reproducibility package gates to
  validate the SnapATAC2 preparer/scorer/runner contract.
- Refreshed the paper-facing real-reuse table artifacts and AAAI table/PDF so
  SNAP-T1/T2 now show `Fixture pending`.

## Verification

- `python -m unittest tests.test_prepare_real_reuse_snapatac2_fixture tests.test_score_real_reuse_snapatac2 tests.test_run_real_reuse_snapatac2 tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package tests.test_build_real_reuse_paper_tables -v`: passed before documentation cleanup.
- `python -m unittest discover -s tests -v`: 153 tests passed before documentation cleanup.
- Strict gates passed before documentation cleanup:
  - `python scripts\check_submission_review.py --strict`
  - `python scripts\check_aaai_submission_decision.py --strict`
  - `python scripts\check_deepseek_followup.py --strict`
  - `python scripts\check_usage_examples.py --strict`
  - `python scripts\check_external_evidence_closure.py --strict`
  - `python scripts\check_external_evidence_packets.py --strict`
  - `python scripts\check_ai_scientist_v2_live_run_handoff.py --strict`
  - `python scripts\check_paper_claims.py --strict`
  - `python scripts\check_aaai_package.py --strict`
  - `python scripts\check_paper_tables.py --strict`
  - `python scripts\check_real_reuse_benchmark.py --strict`
  - `python scripts\check_goal_completion.py --strict`
  - `python scripts\check_reproducibility_package.py --strict`
- `git diff --check`: no whitespace errors; Windows line-ending warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## Results

- Real-reuse preflight: `ready_to_implement`, 8 tasks, 444 ready checks, 0
  failed checks.
- Reproducibility package: `ready_with_pending_external_evidence`, 396 ready
  checks, 1 pending check, 0 failed checks.
- Paper table report: ready after moving SNAP-T1/T2 to `Fixture pending`.
- AAAI package report: ready after rebuilding `paper/aaai/papertoskill_aaai2027.pdf`.

## Evidence Boundary

This phase is SnapATAC2 execution-layer readiness evidence only. It does not
materialize SNAP-T1/T2 fixture assets, run live Summary or PaperToSkill SNAP
rows, append SNAP raw rows, or provide downstream task-success evidence.
