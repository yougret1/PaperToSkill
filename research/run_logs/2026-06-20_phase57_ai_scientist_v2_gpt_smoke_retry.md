# Phase 57: AI-Scientist-v2 GPT-Family Smoke Retry

Date: 2026-06-20

## Objective

Check whether the bounded AI-Scientist-v2 LLM-client smoke can complete through
the GPT-family credential profile after repeated Claude-family provider
timeouts. This is an availability probe for the local AI-Scientist-v2 client
path, not a model-quality experiment.

## Command

Credentials were set only as shell environment variables and were not written
to tracked files. The GPT-family key was mapped into
`AI_SCIENTIST_OPENAI_API_KEY` for this smoke because
`ai_scientist.llm.create_client` reads the `AI_SCIENTIST_OPENAI_*` profile.

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set GPT-family key locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete `
  --timeout-seconds 60 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4
```

## Result

- The command exited non-zero because `--require-complete` was set.
- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`.
- Ready checks: 3.
- Pending checks: 2.
- Failed checks: 0.
- `gpt-5.5` and `gpt-5.4` both timed out after 60 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- `scripts/check_external_evidence_closure.py` and
  `scripts/check_external_evidence_packets.py` now list both the Claude-family
  and GPT-family smoke retry commands so future handoffs do not assume a
  Claude-only blocker.

## Evidence Boundary

This phase is provider/model availability evidence for a bounded
AI-Scientist-v2 LLM-client smoke. It does not complete the smoke contract, run
BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
