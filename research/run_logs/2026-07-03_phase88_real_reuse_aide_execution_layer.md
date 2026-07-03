# Phase 88 Run Log: AIDE Real-Reuse Execution Layer

- Run ID: phase88_real_reuse_aide_execution_layer
- Date: 2026-07-03
- Objective: prepare the AIDE-T1/AIDE-T2 real-reuse path up to executable
  fixture preparation, objective scoring, and Summary-vs-PaperToSkill runner
  contracts without using synthetic data as paper evidence.

## Inputs

- `benchmarks/real_reuse/tasks/AIDE-T1.json`
- `benchmarks/real_reuse/tasks/AIDE-T2.json`
- `benchmarks/real_reuse/asset_locks/AIDE-T1.json`
- `benchmarks/real_reuse/asset_locks/AIDE-T2.json`
- `generated_skills/aide/SKILL.md`
- Human handoff file:
  `C:\Users\19351\Desktop\tem\toHuman.md`

## Outputs

- `scripts/prepare_real_reuse_aide_fixture.py`
- `scripts/score_real_reuse_aide.py`
- `scripts/run_real_reuse_aide.py`
- `tests/test_prepare_real_reuse_aide_fixture.py`
- `tests/test_score_real_reuse_aide.py`
- `tests/test_run_real_reuse_aide.py`
- Updated `scripts/check_real_reuse_benchmark.py`
- Updated `scripts/check_reproducibility_package.py`
- Updated `tests/test_check_real_reuse_benchmark.py`
- Updated `tests/test_check_reproducibility_package.py`
- Updated `research/runbook.md`
- Updated `research/artifact_map.md`
- Updated `research/experiment_queue.md`
- Updated `results/real_reuse/spec_preflight.json`
- Updated `results/real_reuse/spec_preflight.md`
- Updated `results/reproducibility/package_report.json`
- Updated `results/reproducibility/package_report.md`

## Commands

```powershell
python -m unittest tests.test_prepare_real_reuse_aide_fixture tests.test_score_real_reuse_aide tests.test_run_real_reuse_aide tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
python scripts\check_real_reuse_benchmark.py --strict
python scripts\check_reproducibility_package.py --strict
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_deepseek_followup.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_real_reuse_benchmark.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

## Result

- The targeted AIDE/preflight/package test set passed: 17 tests.
- Full unit discovery passed: 131 tests.
- All listed strict local gates passed.
- `git diff --check` returned only line-ending warnings.
- The raw-key scan produced no matches.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 424
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 376 ready checks, 1 pending check,
  and 0 failed checks.
- The human-provided Kaggle Spaceship Titanic `train.csv` was not present:
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\train.csv`
  is still missing, and `C:\Users\19351\Desktop\tem\ok.txt` was not present.

## Evidence Boundary

This phase is execution-layer readiness for AIDE only. It does not materialize
the real AIDE fixtures, run Summary or PaperToSkill model rows, append AIDE raw
rows, update paper table scores, or claim downstream AIDE task success. AIDE
scoring must wait for the real Kaggle `train.csv`; synthetic unit-test data is
test coverage only.
