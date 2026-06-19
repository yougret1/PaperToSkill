# Phase 59: OpenAI-Compatible Direct Provider Probe

Date: 2026-06-20

## Objective

Determine whether the AI-Scientist-v2 smoke blocker is specific to the local
`ai_scientist.llm` wrapper or also appears when calling the OpenAI-compatible
`/chat/completions` endpoint directly with the same tiny marker contract.

## Changes

- Added `scripts/run_openai_compatible_direct_probe.py`.
- The diagnostic bypasses `ai_scientist.llm`, calls `/chat/completions`
  directly, supports repeatable `--model-alias`, `--max-tokens`,
  `--timeout-seconds`, `--require-complete`, redacts API-key-like strings, and
  clears stale response files on blocked attempts.
- Added tests for success, redaction, missing configuration, and alias fallback.
- Added direct-probe reports for Claude-family and GPT-family credential
  profiles under `results/openai_compatible_direct_probe/`.

## Commands

Credentials were set only as shell environment variables and were not written
to tracked files.

Claude-family direct probe:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set Claude-family key locally>'
python scripts\run_openai_compatible_direct_probe.py --strict --require-complete `
  --timeout-seconds 30 `
  --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6 `
  --output-json results\openai_compatible_direct_probe\claude_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\claude_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\claude_family\response.md
```

GPT-family direct probe:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set GPT-family key locally>'
python scripts\run_openai_compatible_direct_probe.py --strict --require-complete `
  --timeout-seconds 60 `
  --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4 `
  --output-json results\openai_compatible_direct_probe\gpt_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\gpt_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\gpt_family\response.md
```

## Result

- Both direct probe commands exited non-zero because `--require-complete` was
  set and no marker-contract response was saved.
- Claude-family direct probe:
  `results/openai_compatible_direct_probe/claude_family/run_report.md`
  reports `blocked_by_provider_or_model_availability`, 5 ready checks, 2
  pending checks, and 0 failed checks. All four Claude aliases returned HTTP
  503 with `No available accounts: no available accounts`.
- GPT-family direct probe:
  `results/openai_compatible_direct_probe/gpt_family/run_report.md` reports
  `blocked_by_provider_or_model_availability`, 3 ready checks, 2 pending
  checks, and 0 failed checks. `gpt-5.5` and `gpt-5.4` returned HTTP 502 with
  `Upstream access forbidden, please contact administrator`.
- No direct-probe response files exist for either profile.

## Evidence Boundary

This phase clarifies that the current provider blocker is visible even when
calling the OpenAI-compatible endpoint directly, outside the `ai_scientist.llm`
wrapper. It does not complete the AI-Scientist-v2 LLM-client smoke contract,
run BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
