# Phase 97: SWE-T1 Live Real-Reuse Rows

Date: 2026-07-03

## Objective

Move the locked SWE-T1 real-reuse task from fixture-pending to scored evidence
without weakening the evidence boundary. Also process the active AIDE human
handoff signal before continuing other work.

## AIDE Handoff Processing

- `C:\Users\19351\Desktop\tem\ok.txt` was present.
- `C:\Users\19351\Desktop\tem\toHuman.md` said to download the Kaggle
  Spaceship Titanic data because network was available.
- The expected official local file
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\train.csv`
  was absent.
- No local Kaggle CLI, Python `kaggle` package, `kaggle.json`, or
  `KAGGLE_USERNAME` / `KAGGLE_KEY` environment variables were present.
- `toHuman.md` was rewritten to ask for official Kaggle `train.csv` or a local
  user-managed Kaggle setup. `ok.txt` was removed after processing.

Boundary: AIDE-T1/AIDE-T2 remain `Awaiting dataset`; no synthetic or mirror
data was used.

## Implementation Changes

- Extended `scripts/prepare_real_reuse_swe_fixture.py` with
  `--swe-bench-parquet` and `--instance-id` so locked SWE-bench rows can be
  materialized directly from local parquet files.
- Extended `scripts/score_real_reuse_swe.py` so scoring subprocesses add
  `src/` to `PYTHONPATH` when present and tolerate whitespace/line-ending
  differences during `git apply`.
- Added a regression test for parquet-backed SWE-bench fixture preparation.

## Fixture And Environment

- Cloned `https://github.com/sqlfluff/sqlfluff.git` to
  `D:\a_work\gitee\sqlfluff__sqlfluff`.
- Checked out locked base commit
  `14e1a23a3166b9a645a16de96f694c77a5d4abb7`.
- Used local SWE-bench Lite parquet:
  `D:\a_work\gitee\SWE-bench_Lite\data\dev-00000-of-00001.parquet`.
- Locked instance: `sqlfluff__sqlfluff-1625`.
- Created task-specific venv:
  `D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625`.
- Installed the old SQLFluff-compatible runtime stack in that venv, including
  `click==7.1.2`, `pytest==6.2.5`, `pluggy==0.13.1`, and the SQLFluff checkout
  in editable mode so plugin entry points are available.

## Commands

```powershell
git clone https://github.com/sqlfluff/sqlfluff.git 'D:\a_work\gitee\sqlfluff__sqlfluff'
git -C 'D:\a_work\gitee\sqlfluff__sqlfluff' checkout 14e1a23a3166b9a645a16de96f694c77a5d4abb7
python -m venv 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625'
& 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe' -m pip install "click==7.1.2" "colorama>=0.3" configparser oyaml Jinja2 "diff-cover>=2.5.0" pathspec appdirs cached-property pytest toml tblib chardet typing_extensions "setuptools<81" "pytest==6.2.5" "pluggy==0.13.1"
& 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe' -m pip install -e 'D:\a_work\gitee\sqlfluff__sqlfluff'
python scripts\prepare_real_reuse_swe_fixture.py --task SWE-T1 --workspace-mode external --repo-source 'D:\a_work\gitee\sqlfluff__sqlfluff' --swe-bench-parquet 'D:\a_work\gitee\SWE-bench_Lite\data\dev-00000-of-00001.parquet' --test-command 'D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625\Scripts\python.exe -m pytest test/cli/commands_test.py::test__cli__command_directed -q' --output-dir benchmarks\real_reuse\assets\SWE-T1
python scripts\score_real_reuse_swe.py --task SWE-T1 --patch benchmarks\real_reuse\assets\SWE-T1\scorer_only\gold.patch --workspace 'D:\a_work\gitee\sqlfluff__sqlfluff' --test-command-file benchmarks\real_reuse\assets\SWE-T1\target_test_command.txt --test-patch benchmarks\real_reuse\assets\SWE-T1\scorer_only\test.patch --timeout-seconds 120 --output-json results\real_reuse\swe_t1_gold_metric.json
python scripts\run_real_reuse_swe.py --task SWE-T1 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --run-id phase97_gpt_swe_t1_real_reuse --score-timeout-seconds 120
python scripts\run_real_reuse_swe.py --task SWE-T1 --condition summary --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --run-id phase97_gpt_swe_t1_summary_retry --timeout-seconds 180 --max-attempts 1 --score-timeout-seconds 120
python scripts\build_real_reuse_paper_tables.py
```

The GPT key was loaded only into the process environment from the local GPT API
document and was not written to tracked files.

## Results

- Gold scorer validation: `results/real_reuse/swe_t1_gold_metric.json` reports
  `task_score=1.0`, `success=true`, hidden test patch applied, gold patch
  applied, and target pytest passed.
- First live run:
  - Summary: provider read timeout after two attempts; no raw scored row
    appended.
  - PaperToSkill: scored row appended, `task_score=0.0`, `success=false`,
    `failure_reason=patch_apply_failed`.
- Summary retry:
  - Summary: scored row appended, `task_score=0.0`, `success=false`,
    `failure_reason=patch_apply_failed`.
- `results/real_reuse/main_results_plan.md` now reads 12 scored raw rows and
  fills SWE-T1 as Summary `0.000`, PaperToSkill `0.000`,
  `Scored (GPT-family)`.
- `paper/aaai/papertoskill_tables.tex` and
  `paper/aaai/papertoskill_aaai2027.tex` were updated with the SWE-T1 row and
  a cautious Results paragraph.

## Evidence Boundary

SWE-T1 is real GPT-family downstream failure-boundary evidence for one locked
SWE-Bench Lite-style instance. It does not show PaperToSkill advantage over
Summary. Together with SWE-T2, it demonstrates both a successful and a failed
software-engineering real-reuse row, but still does not establish aggregate
SWE-agent or eight-task benchmark effectiveness. AIDE remains blocked on the
official Kaggle `train.csv`.
