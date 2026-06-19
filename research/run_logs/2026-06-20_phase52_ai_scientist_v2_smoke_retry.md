# Phase 52: AI-Scientist-v2 Smoke Retry

## Objective

Recheck the bounded AI-Scientist-v2 LLM-client smoke path after Phase 51
created the external-evidence closure queue, without running BFTS or claiming
live-run success.

## Command

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --timeout-seconds 30 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

## Results

- The smoke runner used the local `ai_scientist.llm` client path.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `overall_status=blocked_by_provider_or_model_availability`.
- The report has 5 ready checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Evidence Boundary

This phase refreshes provider/model availability evidence for the bounded
AI-Scientist-v2 LLM-client smoke path. It does not complete the smoke, run
BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
