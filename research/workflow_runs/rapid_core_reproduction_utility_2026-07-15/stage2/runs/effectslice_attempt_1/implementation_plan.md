# EffectSlice Stage 2 Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use test-driven-development and execute inline because this run forbids commits and shared-worktree integration.

**Goal:** Implement and run a deterministic readiness/certificate-core pilot without changing existing PaperToSkill artifacts.

**Architecture:** A small Python package separates immutable records, bounded statistics, admission policy, and repository-readiness audit. The CLI writes only run-scoped JSON summaries.

**Tech Stack:** Python 3.12 standard library, `unittest`, JSON/JSONL, `pathlib`.

---

### Task 1: Handoff and Configuration

**Files:**
- Create: `run_manifest.json`
- Create: `configs/experiment_config.json`
- Create: `configs/decision_register.json`
- Reuse read-only: `idea.json`, `idea.md`

- [ ] Verify the copied idea contains hypothesis, method, experiment plan, baseline expectation, and risk factors.
- [ ] Record actual RTX 4060 8GB hardware and prohibit full 80GB-class campaign claims.
- [ ] Freeze the development-only evidence boundary and stable reason codes.

### Task 2: Statistical Core

**Files:**
- Create: `tests/test_statistics.py`
- Create: `src/effectslice/statistics.py`

- [ ] Write a failing test for a bounded one-sided Hoeffding lower bound.
- [ ] Run `python -m unittest tests.test_statistics -v` and verify import failure.
- [ ] Implement `hoeffding_lower_bound(values, low, high, alpha)` and `hoeffding_interval(values, low, high, alpha)` with strict finite/range checks.
- [ ] Write failing tests for Holm all-rejected pass and fail boundaries.
- [ ] Implement `holm_all_rejected(p_values, alpha)` and rerun the statistical tests.

### Task 3: Admission Policy

**Files:**
- Create: `tests/test_admission.py`
- Create: `src/effectslice/models.py`
- Create: `src/effectslice/admission.py`

- [ ] Write failing tests for insufficient pairs, non-beneficial `F`, empty slice, non-strict subset, incomplete neighbor family, insufficient query budget, failed confirmation family, and successful admission.
- [ ] Verify tests fail because the package is absent.
- [ ] Implement immutable records and `evaluate_full_eligibility`.
- [ ] Implement `evaluate_slice_admission` with deterministic reason precedence.
- [ ] Rerun admission and statistics tests until all pass.

### Task 4: Existing-Asset Readiness Audit

**Files:**
- Create: `tests/test_readiness.py`
- Create: `src/effectslice/readiness.py`

- [ ] Write a failing temporary-repository test showing aggregate Summary/PaperToSkill rows are not mistaken for paired `B/F` certificate evidence.
- [ ] Implement discovery of the eight task specs, selected rows, raw rows, and paper source maps.
- [ ] Implement per-task missing-criterion lists and an aggregate readiness report.
- [ ] Run the readiness test and the complete test suite.

### Task 5: Pilot Runner and Summaries

**Files:**
- Create: `tests/test_run_pilot.py`
- Create: `run_pilot.py`
- Produce: `experiment_results/pilot/readiness_report.json`
- Produce: `logs/baseline_summary.json`
- Produce: `logs/research_summary.json`
- Produce: `logs/ablation_summary.json`

- [ ] Write a failing end-to-end test for the four JSON outputs and evidence-boundary labels.
- [ ] Implement the runner using the package APIs.
- [ ] Run the test against a temporary fixture repository.
- [ ] Run the pilot against the real project root.
- [ ] Parse all outputs and verify no effectiveness claim appears.

### Task 6: Stage Reports and Verification

**Files:**
- Create: workflow-root `stage_report_2_1.json`
- Create: workflow-root `stage_report_2_2.json`
- Create: workflow-root `stage_report_2_3.json`
- Create: workflow-root `stage_report_2_4.json`
- Update: workflow-root `run_manifest.json`

- [ ] Run all pilot tests from a clean process.
- [ ] Validate every run-scoped JSON file.
- [ ] Confirm baseline, research, and ablation summaries match the local pipeline contract.
- [ ] Record current-data blockers without starting held-out or external-baseline execution.
- [ ] Confirm Git status shows no new writes outside the Stage 2 run and workflow stage reports.

