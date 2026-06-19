# Phase 58: AI-Scientist-v2 Max-Token-Capped Smoke

Date: 2026-06-20

## Objective

Make the bounded AI-Scientist-v2 LLM-client smoke more diagnostic by capping
the tiny marker-contract request at 128 max tokens. This checks whether earlier
provider timeouts were caused by the default `ai_scientist.llm.MAX_NUM_TOKENS`
budget rather than endpoint/model availability.

## Changes

- Added `--max-tokens` to `scripts/run_ai_scientist_v2_smoke.py`.
- The runner temporarily overrides `ai_scientist.llm.MAX_NUM_TOKENS` for the
  smoke call and restores the previous value after the call.
- Added test coverage for the temporary token cap and restoration behavior.
- Updated external-evidence closure and packet commands to include
  `--max-tokens 128` for both Claude-family and GPT-family smoke retries.

## Commands

Credentials were set only as shell environment variables and were not written
to tracked files.

GPT-family capped retry:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set GPT-family key locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete `
  --timeout-seconds 45 `
  --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4
```

Claude-family capped retry:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set Claude-family key locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete `
  --timeout-seconds 30 `
  --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

## Result

- Both live smoke commands exited non-zero because `--require-complete` was
  set.
- GPT-family capped retry: `gpt-5.5` and `gpt-5.4` both timed out after 45
  seconds waiting for provider response.
- Claude-family capped retry: `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` all timed out after 30 seconds
  waiting for provider response.
- The latest `results/ai_scientist_v2_smoke/run_report.md` records the
  Claude-family capped retry, `max_tokens=128`,
  `overall_status=blocked_by_provider_or_model_availability`, 5 ready checks,
  2 pending checks, and 0 failed checks.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Evidence Boundary

This phase improves the precision of provider/model availability evidence for
the bounded AI-Scientist-v2 LLM-client smoke. It does not complete the smoke
contract, run BFTS, prove live research-task success, resolve DeepSeek, collect
human annotations, collect provider billing, or make the AAAI package
submission-final.
