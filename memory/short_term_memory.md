# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 48 is in progress locally: rechecking the bounded AI-Scientist-v2
LLM-client smoke path with a longer per-alias timeout and synchronizing the
provider-blocked evidence.

Latest pushed commit before Phase 48: `f9a902c Refresh phase 47 memory status`.

Phase 48 evidence so far:

- Re-ran `scripts/run_ai_scientist_v2_smoke.py` with four Claude aliases and
  `--timeout-seconds 30`.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `blocked_by_provider_or_model_availability`: `claude-opus-4-8` returned HTTP
  403 `All available accounts exhausted`; `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` timed out after 30 seconds waiting
  for provider response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- Added `research/run_logs/2026-06-19_phase48_ai_scientist_v2_smoke_provider_recheck.md`.

Phase 47 completed:

- Added `scripts/check_deepseek_followup.py`, which writes
  `results/deepseek_followup_handoff/handoff.{json,md}` without making network
  calls or reading API keys.
- Current handoff status is `pending_user_configuration`: 5 ready checks, 2
  pending checks, and 0 failed checks.
- Added tests for the current placeholder state and a configured
  `ready_to_run` DeepSeek state.
- Integrated the handoff report into usage, goal, and package gates while
  keeping DeepSeek response completion pending.
- Full verification passed before the commit, and no raw API keys were found by
  the repository scan.

Latest smoke recheck:

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

Result: `claude-opus-4-8` returned HTTP 403
`All available accounts exhausted`; the other three aliases timed out after 30
seconds waiting for provider response. `results/ai_scientist_v2_smoke/run_report.md` reports
`blocked_by_provider_or_model_availability`, 5 ready checks, 2 pending checks,
and 0 failed checks. No `results/ai_scientist_v2_smoke/response.md` exists.

## Current Evidence

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- All four live-transfer saved-response sets are complete and scored:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24
  scored rows, 0 pending rows, and average normalized score 1.0.
- Claude Opus 4.8 and GPT-family model-ablation rows are saved and scored for
  the current two-case protocol. In the GPT-family retry, Toolformer timed out
  on `gpt-5.5` then succeeded with `gpt-5.4`, while AIDE succeeded with
  `gpt-5.5`; DeepSeek remains pending.
- Explicit status anchor for gates: gpt-family rows are now saved and scored;
  DeepSeek remains pending.
- DeepSeek follow-up handoff:
  `results/deepseek_followup_handoff/handoff.md` reports
  `pending_user_configuration`, 5 ready checks, 2 pending checks, and 0 failed
  checks. It lists the two DeepSeek prompt rows and expected response paths.
- Human-fidelity annotation handoff:
  `results/human_fidelity_packets/annotation_summary.md` reports
  `annotation_status=pending`, 0 scored rows, 24 pending rows, average
  confidence `n/a`, and 0 validation errors.
- Provider-billing evidence handoff:
  `results/provider_billing_evidence/billing_summary.md` reports
  `billing_status=pending`, 6 total rows, 0 measured rows, 6 pending rows, 0
  errors, total billed USD 0, and success per dollar `n/a`.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md` reports ready, 15 ready
  checks, and 0 failed checks.
- Goal report:
  `results/reproducibility/goal_completion_report.md` reports
  `not_complete_pending_external_evidence`, 58 ready checks, 8 pending checks,
  and 0 failed checks.
- Package report:
  `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 237 ready checks, 7 pending checks,
  and 0 failed checks.

## Boundaries To Preserve

Do not claim:

- DeepSeek completed.
- AI-Scientist-v2 LLM-client smoke completed.
- AI-Scientist-v2 full live LLM run completed.
- BFTS or live research-task success completed.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.

Supported after Phase 48:

- AI-Scientist-v2 LLM-client smoke was attempted through local
  `ai_scientist.llm` with four Claude aliases:
  `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- `claude-opus-4-8` returned HTTP 403 `All available accounts exhausted`; the
  other three aliases timed out after 30 seconds waiting for provider response,
  so provider/model availability remains blocked.
- The absence of `results/ai_scientist_v2_smoke/response.md` is intentional
  while no alias satisfies the smoke marker contract.
- Package and goal gates separate provider/model availability pending evidence
  from local failures.
- DeepSeek follow-up is locally preflighted: the slot, prompt rows, response
  paths, env names, and next commands are machine-checked, but alias
  configuration and response collection remain pending.

## Latest Verification

Latest Phase 47 verification before commit `1c467e9`:

```powershell
python -m unittest tests.test_check_deepseek_followup tests.test_check_usage_examples tests.test_check_goal_completion tests.test_check_reproducibility_package -v
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_deepseek_followup.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

All tests/checkers passed. `git diff --check` emitted only Windows LF-to-CRLF
warnings. The raw-key scan returned no matches.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion satisfying the marker contract.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
