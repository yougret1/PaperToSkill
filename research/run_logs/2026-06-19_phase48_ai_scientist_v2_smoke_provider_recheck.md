# Phase 48: AI-Scientist-v2 Smoke Provider Recheck

## Objective

Refresh the bounded AI-Scientist-v2 LLM-client smoke evidence with a longer
per-alias timeout while preserving the distinction between provider/model
availability and PaperToSkill quality.

## Command

The API key was supplied only as a local shell environment variable.

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

- `results/ai_scientist_v2_smoke/run_report.md` reports
  `overall_status=blocked_by_provider_or_model_availability`.
- The report has 5 ready checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8` returned HTTP 403 with
  `All available accounts exhausted`.
- `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` each timed out
  after 30 seconds waiting for provider response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Evidence Boundary

This phase refreshes provider-blocked smoke evidence only. It does not complete
the AI-Scientist-v2 LLM-client smoke, does not run BFTS, does not prove live
research-task success, does not resolve DeepSeek, does not collect human
annotations, does not collect provider billing, and does not make the AAAI
package submission-final.
