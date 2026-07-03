# Phase 91: SWE-agent Real-Reuse Execution Layer

Date: 2026-07-03

## Objective

Add the SWE-agent execution-layer contract for the main real-reuse benchmark
without claiming SWE downstream task success before fixture assets and raw rows
exist.

## Actions

- Added `scripts/prepare_real_reuse_swe_fixture.py`.
  - Prepares SWE-T1/SWE-T2 fixture directories from a local repository snapshot.
  - Writes model-visible issue/failing-test context, task prompt, test command,
    starter workspace README, and task-specific Summary context.
  - Records gold patches as scorer-only and hidden from model-visible context.
- Added `scripts/score_real_reuse_swe.py`.
  - Copies the prepared workspace to a temporary directory.
  - Applies a candidate unified diff with `git apply`.
  - Runs the locked test command and reports `task_score`, `success`,
    `patch_applied`, and `test_passed`.
- Added `scripts/run_real_reuse_swe.py`.
  - Builds prompts from Summary or PaperToSkill context plus the locked task
    prompt.
  - Supports fixture responses for dry tests and live API calls for later runs.
  - Appends raw rows only when model/fixture output is scored.
  - Records missing fixture assets, missing credentials, and provider/model
    errors as availability status, not model-quality failure.
- Added tests:
  - `tests/test_prepare_real_reuse_swe_fixture.py`
  - `tests/test_score_real_reuse_swe.py`
  - `tests/test_run_real_reuse_swe.py`
  - Missing-fixture and missing-credential branches produce pending reports
    without appending raw rows.
- Added a table-status regression in
  `tests/test_build_real_reuse_paper_tables.py` so SWE rows become
  `Fixture pending` when the skill and runner exist but fixture assets do not.
- Refreshed generated real-reuse reports, package reports, paper table reports,
  and the AAAI PDF.

## Results

- Targeted test command:

```powershell
python -m unittest tests.test_build_real_reuse_paper_tables tests.test_prepare_real_reuse_swe_fixture tests.test_score_real_reuse_swe tests.test_run_real_reuse_swe tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
```

- Targeted result: 18 tests passed.
- `results/real_reuse/main_results_plan.md` now reports:
  - AIDE-T1/T2: `Awaiting dataset`
  - SWE-T1/T2: `Fixture pending`
  - REF-T1/T2: `Scored (GPT-family)`
  - SNAP-T1/T2: `Skill pending`
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 434
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 381 ready checks, 1 pending check,
  and 0 failed checks.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after the real-reuse table
  status update.
- Paper-facing strict checks passed:
  - `python scripts\check_paper_tables.py --strict`
  - `python scripts\check_paper_claims.py --strict`
  - `python scripts\check_aaai_package.py --strict`

## Evidence Boundary

This phase is SWE execution-layer readiness evidence only. It does not download
or materialize official SWE-bench assets, prepare SWE-T1/T2 asset manifests,
run live Summary or PaperToSkill SWE rows, append SWE raw rows, or provide SWE
task-success evidence.

The main real-reuse benchmark remains incomplete. Only REF-T1 and REF-T2 have
one GPT-family Summary-vs-PaperToSkill run, and both conditions score 1.000.
That validates the REF execution path but does not establish aggregate
PaperToSkill advantage over Summary.

## Next Action

Prepare concrete SWE fixture assets from local repository snapshots or move to
SnapATAC2 skill/execution preparation. AIDE fixture materialization still waits
for the human-provided Kaggle Spaceship Titanic `train.csv`.
