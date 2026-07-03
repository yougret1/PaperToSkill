# Phase 87 Run Log: Reflexion Real-Reuse Runner

- Run ID: phase87_real_reuse_reflexion_runner
- Date: 2026-07-03
- Objective: move the prepared REF-T1/REF-T2 real-reuse fixtures from dry
  scoring into a runnable Summary-vs-PaperToSkill execution path.

## Inputs

- `benchmarks/real_reuse/tasks/REF-T1.json`
- `benchmarks/real_reuse/tasks/REF-T2.json`
- `benchmarks/real_reuse/assets/REF-T1/asset_manifest.json`
- `benchmarks/real_reuse/assets/REF-T2/asset_manifest.json`
- `baselines/real_reuse/REF-T1_summary.md`
- `baselines/real_reuse/REF-T2_summary.md`
- `generated_skills/reflexion/SKILL.md`
- Local GPT API documentation under
  `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument`

## Outputs

- `scripts/run_real_reuse_reflexion.py`
- `tests/test_run_real_reuse_reflexion.py`
- Updated `scripts/score_real_reuse_reflexion.py`
- Updated `tests/test_score_real_reuse_reflexion.py`
- Updated `scripts/build_real_reuse_paper_tables.py`
- Updated `tests/test_build_real_reuse_paper_tables.py`
- Updated `scripts/check_real_reuse_benchmark.py`
- Updated `scripts/check_reproducibility_package.py`
- `results/real_reuse/raw_rows.jsonl`
- `results/real_reuse/reflexion_run_report.json`
- `results/real_reuse/reflexion_run_report.md`
- `results/real_reuse/main_results_plan.json`
- Updated `results/real_reuse/main_results_plan.csv`
- Updated `results/real_reuse/main_results_plan.md`
- Updated `paper/aaai/papertoskill_tables.tex`
- Updated `paper/aaai/papertoskill_aaai2027.tex`

## Commands

```powershell
python -m unittest tests.test_run_real_reuse_reflexion -v
python scripts\run_real_reuse_reflexion.py --task REF-T1 --task REF-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --run-id phase87_gpt_reflexion_real_reuse --max-tokens 1400 --timeout-seconds 90 --max-attempts 2 --retry-delay-seconds 2
python -m unittest tests.test_score_real_reuse_reflexion tests.test_run_real_reuse_reflexion -v
python scripts\build_real_reuse_paper_tables.py
python scripts\check_paper_tables.py --strict
python scripts\check_paper_claims.py --strict
python -m unittest tests.test_build_real_reuse_paper_tables tests.test_score_real_reuse_reflexion tests.test_run_real_reuse_reflexion tests.test_check_reproducibility_package -v
python scripts\check_real_reuse_benchmark.py --strict
python scripts\check_reproducibility_package.py --strict
```

The live command used shell-only GPT credentials derived from local API docs;
no raw API key was written to tracked files.

## Result

- GPT-family `gpt-5.5` completed 4/4 REF real-reuse rows.
- REF-T1 Summary: 1.000.
- REF-T1 PaperToSkill: 1.000.
- REF-T2 Summary: 1.000.
- REF-T2 PaperToSkill: 1.000.
- All four rows recorded zero interventions.

## Evidence Boundary

This phase is partial real-reuse execution evidence for the Reflexion slice
only. It validates the runner, scorer, raw-row, and table-update path, but it
does not prove PaperToSkill is better than Summary and does not complete the
eight-task main experiment.
