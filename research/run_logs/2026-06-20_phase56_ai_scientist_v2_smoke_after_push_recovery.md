# Phase 56: AI-Scientist-v2 Smoke After Push Recovery

Date: 2026-06-20

## Objective

After GitHub connectivity recovered and Phase 55 was pushed, retry the bounded
AI-Scientist-v2 LLM-client smoke to check whether the provider blocker has
cleared.

## Command

Credentials were set only as shell environment variables and were not written
to tracked files.

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete `
  --timeout-seconds 30 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

## Result

- The command exited non-zero because `--require-complete` was set.
- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`.
- Ready checks: 5.
- Pending checks: 2.
- Failed checks: 0.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Evidence Boundary

This phase is provider/model availability evidence for a bounded
AI-Scientist-v2 LLM-client smoke. It does not complete the smoke contract, run
BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
