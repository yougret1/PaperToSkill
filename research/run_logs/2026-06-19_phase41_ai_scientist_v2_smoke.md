# Phase 41: AI-Scientist-v2 LLM-Client Smoke

## Objective

Record bounded live evidence for the local AI-Scientist-v2 LLM client without
running BFTS or claiming research-task success.

## Commands

Run the smoke check with shell-only credentials:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

python scripts\run_ai_scientist_v2_smoke.py --strict
```

Regenerate the aggregate gates:

```powershell
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Results

- Added `scripts/run_ai_scientist_v2_smoke.py`, a bounded one-call smoke runner
  that imports the local `ai_scientist.llm` client and checks a tiny response
  marker contract.
- Added `tests/test_run_ai_scientist_v2_smoke.py` for successful contract
  responses and redacted provider-error reports.
- Generated `results/ai_scientist_v2_smoke/run_report.json` and
  `results/ai_scientist_v2_smoke/run_report.md`.
- The smoke report is
  `overall_status=blocked_by_provider_or_model_availability`, with 1 ready
  check, 2 pending checks, and 0 failed checks.
- The provider returned HTTP 403 with message `All available accounts
  exhausted`; no `response.md` was created.
- The goal report now records the smoke attempt as ready, but the smoke
  completion and full AI-Scientist-v2 live run as pending.

## Evidence Boundary

This phase proves only that the local PaperToSkill repository has a reproducible
AI-Scientist-v2 LLM-client smoke runner and a redacted provider-blocked attempt
report. It does not complete BFTS, prove research-task success, establish human
semantic fidelity, complete DeepSeek, collect provider billing, or make the
AAAI package submission-final.
