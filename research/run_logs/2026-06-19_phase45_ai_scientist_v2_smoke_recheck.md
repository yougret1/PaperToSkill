# Phase 45: AI-Scientist-v2 Smoke Recheck UX

## Objective

Recheck the bounded AI-Scientist-v2 LLM-client smoke path and make its command
line output harder to misread when the provider path is reachable but still
blocked or slow.

## Commands

Run the smoke recheck with shell-only credentials:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

python scripts\run_ai_scientist_v2_smoke.py --strict --timeout-seconds 15
```

Regenerate aggregate gates:

```powershell
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Results

- The recheck again used the OpenAI-compatible backend through the local
  `ai_scientist.llm` client.
- The provider did not return a smoke response within 15 seconds.
- No `results/ai_scientist_v2_smoke/response.md` file was created.
- `results/ai_scientist_v2_smoke/run_report.json` was refreshed with the new
  attempt timestamp and still reports
  `overall_status=blocked_by_provider_or_model_availability`, 1 ready check,
  2 pending checks, and 0 failed checks.
- `scripts/run_ai_scientist_v2_smoke.py` now prints
  `overall_status=...; ready=...; pending=...; fail=...` after writing the
  reports.
- The runner now supports `--timeout-seconds`, which records a blocked report
  instead of leaving provider hangs to the outer shell timeout.
- The runner also supports `--require-complete`, which exits non-zero unless a
  provider response is saved and satisfies the marker contract.
- `scripts/check_reproducibility_package.py` now checks that the smoke runner
  exposes the status summary, timeout handling, and `--require-complete`
  completion mode.

## Evidence Boundary

This phase improves smoke recheck clarity and records a fresh provider-blocked
attempt. It does not complete the AI-Scientist-v2 smoke, does not run BFTS,
does not prove research-task success, and does not change DeepSeek, human
annotation, provider-billing, or final-submission status.
