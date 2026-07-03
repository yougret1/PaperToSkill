# Phase 83: Real-Reuse Fixture Candidates

- Run ID: phase83_real_reuse_fixture_candidates
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: select candidate fixture assets and preparation/scoring entry
  points for all eight real-reuse task contracts without claiming execution
  evidence.

## Inputs

- `benchmarks/real_reuse/tasks/*.json`
- `benchmarks/real_reuse/fixtures/*.json`
- Primary/official source URLs for AIDE, MLE-bench, SWE-agent, SWE-bench,
  Reflexion, HotPotQA, HumanEval, and SnapATAC2.

## Outputs

- `scripts/build_real_reuse_fixture_candidates.py`
- `benchmarks/real_reuse/fixture_candidates/AIDE-T1.json`
- `benchmarks/real_reuse/fixture_candidates/AIDE-T2.json`
- `benchmarks/real_reuse/fixture_candidates/SWE-T1.json`
- `benchmarks/real_reuse/fixture_candidates/SWE-T2.json`
- `benchmarks/real_reuse/fixture_candidates/REF-T1.json`
- `benchmarks/real_reuse/fixture_candidates/REF-T2.json`
- `benchmarks/real_reuse/fixture_candidates/SNAP-T1.json`
- `benchmarks/real_reuse/fixture_candidates/SNAP-T2.json`
- Expanded candidate validation in `scripts/check_real_reuse_benchmark.py`

## Candidate Decisions

| Task | Candidate source |
| --- | --- |
| AIDE-T1 | MLE-bench Spaceship Titanic Kaggle-style submission fixture |
| AIDE-T2 | MLE-bench Spaceship Titanic weak-script/debug fixture |
| SWE-T1 | SWE-bench Lite issue-to-patch fixture |
| SWE-T2 | SWE-bench Verified failing-test patch fixture |
| REF-T1 | HotPotQA distractor-style multi-hop QA retry fixture |
| REF-T2 | HumanEval failed-attempt retry fixture |
| SNAP-T1 | SnapATAC2 PBMC5k/tutorial embedding pipeline fixture |
| SNAP-T2 | SnapATAC2 tutorial multiome/clustering fixture with labels or proxy metric |

## Commands

```powershell
python scripts\build_real_reuse_fixture_candidates.py
python scripts\check_real_reuse_benchmark.py --strict
python scripts\check_reproducibility_package.py --strict
python -m unittest tests.test_build_real_reuse_fixture_candidates tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
```

## Evidence Boundary

This phase selects candidate asset sources and records preparation/scoring entry
points. It does not download or clone execution assets, accept external dataset
terms, choose final task instance IDs, implement the preparer/scorer scripts,
run any Summary/PaperToSkill task, or create downstream task-success evidence.

## Result

- Real-reuse preflight: `ready_to_implement`, 8 tasks, 296 ready checks, and 0
  failed checks.
- Reproducibility package: `ready_with_pending_external_evidence`, 339 ready
  checks, 1 pending check, and 0 failed checks.
