# Phase 54: AI-Scientist-v2 Smoke Packet Retry

## Objective

Execute the Phase 53 AI-Scientist-v2 smoke-completion packet to see whether
the provider can now return a response satisfying the bounded smoke contract,
without running BFTS or claiming live-run success.

## Command

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 30 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

## Results

- The smoke runner used the local `ai_scientist.llm` client path.
- The command exited non-zero because `--require-complete` was set and the
  provider did not return a response satisfying the smoke contract.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `overall_status=blocked_by_provider_or_model_availability`.
- The report has 5 ready checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

## Follow-Up Commands

```powershell
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_goal_completion.py --strict
```

## Evidence Boundary

This phase refreshes provider/model availability evidence for the bounded
AI-Scientist-v2 LLM-client smoke path. It does not complete the smoke, unlock
the full live/BFTS run, prove live research-task success, resolve DeepSeek,
collect human annotations, collect provider billing, or make the AAAI package
submission-final.
