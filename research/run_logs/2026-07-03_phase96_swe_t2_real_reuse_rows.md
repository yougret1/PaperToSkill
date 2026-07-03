# Phase 96: SWE-T2 Live Real-Reuse Rows

Date: 2026-07-03

## Objective

Move one SWE-agent real-reuse task from fixture-pending to scored evidence by
materializing the locked SWE-T2 fixture against an external Astropy checkout and
running Summary vs PaperToSkill with GPT-family `gpt-5.5`.

## Actions

- Removed the accidental copied workspace under
  `benchmarks/real_reuse/assets/SWE-T2/workspace` after verifying the resolved
  path stayed inside the PaperToSkill workspace.
- Rematerialized SWE-T2 with `--workspace-mode external`, pointing
  `workspace_dir` to `D:/a_work/gitee/astropy__astropy`.
- Copied SWE-Bench Verified gold and test patches into
  `benchmarks/real_reuse/assets/SWE-T2/scorer_only/` so hidden scorer assets no
  longer point at temporary extraction paths.
- Fixed `scripts/score_real_reuse_swe.py` so candidate and hidden test patch
  paths are resolved before scoring in the temporary workspace.
- Added a regression test covering relative candidate/test patch paths.
- Validated the SWE-T2 scorer with the gold patch.
- Ran `scripts/run_real_reuse_swe.py` for SWE-T2 Summary and PaperToSkill with
  GPT-family `gpt-5.5`.
- Regenerated `results/real_reuse/main_results_plan.{csv,md,json}` and updated
  the AAAI real-reuse table and Results narrative.

## Commands

```powershell
python scripts\prepare_real_reuse_swe_fixture.py --task SWE-T2 --workspace-mode external --repo-source 'D:\a_work\gitee\astropy__astropy' --issue-file 'D:\a_work\gitee\PaperToSkill\tmp_real_reuse_swe\SWE-T2_problem_statement.md' --test-command "python -m pytest astropy/modeling/tests/test_separable.py::test_separable[compound_model6-result6] astropy/modeling/tests/test_separable.py::test_separable[compound_model9-result9]" --gold-patch 'D:\a_work\gitee\PaperToSkill\tmp_real_reuse_swe\SWE-T2_gold.patch' --test-patch 'D:\a_work\gitee\PaperToSkill\tmp_real_reuse_swe\SWE-T2_test.patch' --output-dir benchmarks\real_reuse\assets\SWE-T2
python -m unittest tests.test_prepare_real_reuse_swe_fixture tests.test_score_real_reuse_swe tests.test_run_real_reuse_swe -v
python scripts\score_real_reuse_swe.py --task SWE-T2 --patch benchmarks\real_reuse\assets\SWE-T2\scorer_only\gold.patch --workspace 'D:\a_work\gitee\astropy__astropy' --test-command-file benchmarks\real_reuse\assets\SWE-T2\target_test_command.txt --test-patch benchmarks\real_reuse\assets\SWE-T2\scorer_only\test.patch --timeout-seconds 180 --output-json results\real_reuse\swe_t2_gold_metric.json
python scripts\run_real_reuse_swe.py --task SWE-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --run-id phase96_gpt_swe_t2_real_reuse
python scripts\build_real_reuse_paper_tables.py
python scripts\check_paper_tables.py --strict
python scripts\check_paper_claims.py --strict
```

The GPT API key was loaded only into the local process environment from the
user-provided API documentation and was not written to tracked files.

## Results

- Gold scorer validation: `results/real_reuse/swe_t2_gold_metric.json` reports
  `task_score=1.0`, `success=true`, `test_patch_applied=true`, and 2/2 target
  Astropy tests passed.
- SWE-T2 Summary: score `0.000`, `success=false`, failure reason
  `patch_apply_failed`.
- SWE-T2 PaperToSkill: score `1.000`, `success=true`; the generated patch
  applied and passed both hidden target tests.
- `results/real_reuse/swe_run_report.md` reports `overall_status=complete`
  with two scored rows.
- `results/real_reuse/main_results_plan.md` now reads 10 raw scored rows and
  fills SWE-T2, REF-T1, REF-T2, SNAP-T1, and SNAP-T2.

## Evidence Boundary

- This phase is one locked SWE-Bench Verified-style Astropy instance, not a
  full SWE-agent reproduction and not the full eight-task benchmark.
- The positive PaperToSkill-vs-Summary result is valid for SWE-T2 under the
  current prompt, budget, hidden test patch, external Astropy checkout, and
  GPT-family `gpt-5.5` run.
- SWE-T1 remains fixture-pending. AIDE still awaits the real Kaggle
  Spaceship Titanic `train.csv`. SNAP-T1/T2 remain failure-boundary evidence
  because both scored rows are below the pre-registered success threshold.
