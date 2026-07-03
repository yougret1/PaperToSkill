# Phase 85: Real-Reuse Asset Locks

- Run ID: phase85_real_reuse_asset_locks
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: turn selected real-reuse fixture candidates into preparation-time
  asset locks with concrete task instances, observed external source revisions,
  local target paths, hidden scorer assets, and scorer/preparer contracts.

## Inputs

- `benchmarks/real_reuse/tasks/*.json`
- `benchmarks/real_reuse/fixtures/*.json`
- `benchmarks/real_reuse/fixture_candidates/*.json`
- Public lightweight source probes:
  - GitHub `git ls-remote` for AIDE, MLE-bench, SWE-agent, SWE-bench,
    Reflexion, HumanEval, and SnapATAC2 repositories.
  - Hugging Face dataset API metadata for SWE-bench Lite, SWE-bench Verified,
    HotPotQA, and OpenAI HumanEval.
  - SnapATAC2 official docs reachability for `api/index.html` and
    `tutorials/index.html`.

## Outputs

- `scripts/build_real_reuse_asset_locks.py`
- `benchmarks/real_reuse/asset_locks/*.json`
- Updated `scripts/check_real_reuse_benchmark.py`
- Updated `scripts/check_reproducibility_package.py`
- Updated tests:
  - `tests/test_build_real_reuse_asset_locks.py`
  - `tests/test_check_real_reuse_benchmark.py`
  - `tests/test_check_reproducibility_package.py`
- Updated real-reuse documentation and memory anchors.

## Locked Instances

| Task | Locked Instance |
| --- | --- |
| AIDE-T1 | Kaggle Spaceship Titanic local validation split seed `20260703` |
| AIDE-T2 | Kaggle Spaceship Titanic weak-script debug fixture seed `20260703` |
| SWE-T1 | SWE-bench Lite dev instance `sqlfluff__sqlfluff-1625` |
| SWE-T2 | SWE-bench Verified test instance `astropy__astropy-12907` |
| REF-T1 | HotPotQA distractor validation example `5a8b57f25542995d1e6f1371` |
| REF-T2 | HumanEval task `HumanEval/0` |
| SNAP-T1 | SnapATAC2 `snapatac2.datasets.pbmc5k` PBMC tutorial fixture |
| SNAP-T2 | SnapATAC2 `snapatac2.datasets.pbmc10k_multiome` modality fixture |

## Commands

```powershell
python scripts\build_real_reuse_fixture_candidates.py
python scripts\build_real_reuse_asset_locks.py
python scripts\check_real_reuse_benchmark.py --strict
python -m unittest tests.test_build_real_reuse_asset_locks tests.test_check_real_reuse_benchmark -v
```

## Result

- Real-reuse preflight reports `ready_to_implement`, 8 tasks, 401 ready
  checks, and 0 failed checks after validating asset locks.
- The asset locks make the next implementation step concrete: implement the
  named preparer/scorer scripts, materialize assets, and then run Summary vs
  PaperToSkill under the same locked task instances and budgets.

## Evidence Boundary

Phase 85 is still preparation evidence only. It does not download Kaggle,
Hugging Face, or SnapATAC2 assets for execution; it does not clone external
projects for runs; it does not run Summary or PaperToSkill conditions; and it
does not create downstream task-success rows.
