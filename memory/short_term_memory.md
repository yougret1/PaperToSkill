# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 46 is complete and pushed to `origin/main` as
`23a9e09 Try AI Scientist smoke aliases`: the bounded AI-Scientist-v2
LLM-client smoke runner now tries repeated Claude aliases and records each
attempt in reports.

Latest pushed commit after Phase 46: `23a9e09 Try AI Scientist smoke aliases`.

Phase 46 changed:

- Updated `scripts/run_ai_scientist_v2_smoke.py` with repeatable
  `--model-alias`, per-alias fallback, and `attempted_models` in JSON/Markdown
  reports.
- Added alias-attempt checks such as `ai_scientist_v2_llm_alias_attempt_1`.
- Preserved stale-response cleanup when all aliases are blocked.
- Added tests for fallback success after an earlier alias fails.
- Extended `scripts/check_reproducibility_package.py` to require alias-fallback
  support in the smoke CLI.
- Updated `scripts/check_submission_review.py` so review handoff freshness is
  checked against structured alias attempts plus the timeout detail instead of
  a brittle full error string.
- Added
  `research/run_logs/2026-06-19_phase46_ai_scientist_v2_smoke_alias_fallback.md`.

Latest smoke recheck:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python scripts\run_ai_scientist_v2_smoke.py --strict --timeout-seconds 15 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

Result: all four aliases timed out after 15 seconds waiting for provider
response. `results/ai_scientist_v2_smoke/run_report.md` reports
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
  `not_complete_pending_external_evidence`, 55 ready checks, 8 pending checks,
  and 0 failed checks.
- Package report:
  `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 230 ready checks, 7 pending checks,
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

Supported after Phase 46:

- AI-Scientist-v2 LLM-client smoke was attempted through local
  `ai_scientist.llm` with four Claude aliases:
  `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- All four aliases timed out after 15 seconds waiting for provider response,
  so provider/model availability remains blocked.
- The absence of `results/ai_scientist_v2_smoke/response.md` is intentional
  while no alias satisfies the smoke marker contract.
- Package and goal gates separate provider/model availability pending evidence
  from local failures.

## Latest Verification

Phase 46 full verification passed:

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

Full unittest count is 60 tests. `git diff --check` reported only Windows
LF-to-CRLF warnings, and `rg` exited 1 because no raw API-key-like strings were
found.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion satisfying the marker contract.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
