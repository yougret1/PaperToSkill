# Phase 60: Post-Push Provider Recheck

Date: 2026-06-20

## Objective

Confirm that the Phase 59 direct provider diagnostic was saved to `origin/main`
and recheck whether the OpenAI-compatible provider endpoint can now satisfy the
tiny marker contract. Keep the result as provider-availability evidence only.

## Commands

Phase 59 remote save check:

```powershell
git status -sb
git log -1 --oneline
git push origin main
```

Credentials for the following probes were set only as shell environment
variables and were not written to tracked files.

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

- Phase 59 commit `dc52b06 Add direct OpenAI-compatible provider probe` was
  pushed successfully to `origin/main`.
- Both direct probe commands exited non-zero because `--require-complete` was
  set and no marker-contract response was saved.
- Claude-family direct probe remains
  `blocked_by_provider_or_model_availability`: `claude-opus-4-8`,
  `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` all returned
  HTTP 503 `No available accounts: no available accounts`.
- GPT-family direct probe remains
  `blocked_by_provider_or_model_availability`: `gpt-5.5` and `gpt-5.4` both
  returned HTTP 502 `Upstream access forbidden, please contact administrator`.
- No direct-probe response files exist for either profile.

## Evidence Boundary

This recheck confirms the provider blocker persists after the Phase 59 remote
save. It does not complete the AI-Scientist-v2 LLM-client smoke contract, run
BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
