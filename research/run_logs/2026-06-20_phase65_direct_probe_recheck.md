# Phase 65: Direct Provider Probe Recheck

Date: 2026-06-20

## Objective

Refresh the direct OpenAI-compatible provider diagnostics after remote-save
recovery and before attempting any AI-Scientist-v2 wrapper smoke retry.

## Commands

The credentials were set as shell-only environment variables and were not
written to tracked files.

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'

python scripts\run_openai_compatible_direct_probe.py --strict --require-complete --timeout-seconds 30 --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6 `
  --output-json results\openai_compatible_direct_probe\claude_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\claude_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\claude_family\response.md

python scripts\run_openai_compatible_direct_probe.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4 `
  --output-json results\openai_compatible_direct_probe\gpt_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\gpt_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\gpt_family\response.md
```

## Result

- Claude-family direct probe remains
  `blocked_by_provider_or_model_availability`.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` all returned HTTP 503
  `No available accounts: no available accounts`.
- GPT-family direct probe remains `blocked_by_provider_or_model_availability`.
- `gpt-5.5` and `gpt-5.4` both returned HTTP 502
  `Upstream access forbidden, please contact administrator`.
- No direct-probe marker-contract response files were saved.

## Evidence Boundary

This phase is a direct provider-availability diagnostic only. It does not
complete the AI-Scientist-v2 LLM-client smoke, BFTS/full live run, DeepSeek
rows, human annotation, provider billing, or the final AAAI submission
decision.
