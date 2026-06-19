# Phase 46: AI-Scientist-v2 Smoke Alias Fallback

## Objective

Strengthen the bounded AI-Scientist-v2 LLM-client smoke evidence by trying all
known user-requested Claude alias variants before preserving the provider/model
availability blocker.

## Commands

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

python scripts\run_ai_scientist_v2_smoke.py --strict --timeout-seconds 15 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

## Results

- The smoke runner now supports repeatable `--model-alias` arguments and stores
  `attempted_models` in the JSON/Markdown reports.
- The recheck tried `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6`.
- All four aliases timed out after 15 seconds waiting for provider response.
- `results/ai_scientist_v2_smoke/run_report.md` reports
  `overall_status=blocked_by_provider_or_model_availability`, 5 ready checks,
  2 pending checks, and 0 failed checks.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Evidence Boundary

This phase improves provider/model availability evidence for the bounded smoke
path. It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
research-task success, resolve DeepSeek, collect human annotations, collect
provider billing, or make the AAAI package submission-final.
