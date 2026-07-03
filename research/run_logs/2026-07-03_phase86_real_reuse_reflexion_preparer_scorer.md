# Phase 86 Real-Reuse Reflexion Preparer/Scorer

- Run ID: phase86_real_reuse_reflexion_preparer_scorer
- Date: 2026-07-03
- Commit or snapshot: created before the Phase 86 commit
- Environment: local Windows PowerShell in `D:\a_work\gitee\PaperToSkill`

## Inputs

- `benchmarks/real_reuse/tasks/REF-T1.json`
- `benchmarks/real_reuse/tasks/REF-T2.json`
- `benchmarks/real_reuse/fixtures/REF-T1.json`
- `benchmarks/real_reuse/fixtures/REF-T2.json`
- `benchmarks/real_reuse/fixture_candidates/REF-T1.json`
- `benchmarks/real_reuse/fixture_candidates/REF-T2.json`
- `benchmarks/real_reuse/asset_locks/REF-T1.json`
- `benchmarks/real_reuse/asset_locks/REF-T2.json`
- `generated_skills/reflexion/SKILL.md`
- `baselines/reflexion_generic_summary.md`

## Outputs

- `scripts/prepare_real_reuse_reflexion_fixture.py`
- `scripts/score_real_reuse_reflexion.py`
- `benchmarks/real_reuse/assets/REF-T1/asset_manifest.json`
- `benchmarks/real_reuse/assets/REF-T1/question.json`
- `benchmarks/real_reuse/assets/REF-T1/retrieval_context_or_tool_stub.json`
- `benchmarks/real_reuse/assets/REF-T1/feedback_protocol.md`
- `benchmarks/real_reuse/assets/REF-T1/task_prompt.md`
- `benchmarks/real_reuse/assets/REF-T1/answer_key.json`
- `benchmarks/real_reuse/assets/REF-T2/asset_manifest.json`
- `benchmarks/real_reuse/assets/REF-T2/initial_task.json`
- `benchmarks/real_reuse/assets/REF-T2/failed_first_attempt.py`
- `benchmarks/real_reuse/assets/REF-T2/environment_feedback.md`
- `benchmarks/real_reuse/assets/REF-T2/task_prompt.md`
- `benchmarks/real_reuse/assets/REF-T2/tests.json`
- `benchmarks/real_reuse/assets/REF-T2/canonical_solution.py`
- `baselines/real_reuse/REF-T1_summary.md`
- `baselines/real_reuse/REF-T2_summary.md`
- `tests/test_prepare_real_reuse_reflexion_fixture.py`
- `tests/test_score_real_reuse_reflexion.py`
- Updated `scripts/check_real_reuse_benchmark.py`
- Updated `scripts/check_reproducibility_package.py`
- Refreshed `results/real_reuse/spec_preflight.{json,md}`
- Refreshed `results/reproducibility/package_report.{json,md}`

## Commands

```powershell
python scripts\prepare_real_reuse_reflexion_fixture.py --task REF-T1 --dataset hotpotqa --config distractor --output-dir benchmarks\real_reuse\assets\REF-T1
python scripts\prepare_real_reuse_reflexion_fixture.py --task REF-T2 --dataset humaneval --output-dir benchmarks\real_reuse\assets\REF-T2
python -m unittest tests.test_prepare_real_reuse_reflexion_fixture tests.test_score_real_reuse_reflexion -v
python scripts\check_real_reuse_benchmark.py --strict
python -m unittest tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
python scripts\check_reproducibility_package.py --strict
```

## Results

- REF-T1 and REF-T2 prepared asset manifests exist and include sha256 values.
- REF-T1 keeps `answer_key.json` scorer-only and out of the model-visible prompt.
- REF-T2 keeps `tests.json` and `canonical_solution.py` scorer-only and out of
  the model-visible prompt.
- REF-T1 dry scorer tests pass for correct and incorrect answers.
- REF-T2 dry scorer tests pass for a corrected candidate and score the fixed
  failed first attempt as unsuccessful without crashing.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  418 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 368 ready checks, 1 pending check,
  and 0 failed checks.

## Evidence Boundary

This phase prepares fixture assets and deterministic scorers only. It does not
run a Summary or PaperToSkill model condition, does not write raw real-reuse
rows, does not update the AAAI real-reuse score cells, and does not claim
downstream task success.
