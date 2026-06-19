# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-20.

## Current Phase

Phase 54 is in progress locally: executed the Phase 53 AI-Scientist-v2
smoke-completion packet with shell-only credentials. The provider still did not
return a smoke response; this phase does not run BFTS or claim live-run
success.

Phase 54 evidence so far:

- Ran `scripts/run_ai_scientist_v2_smoke.py` with `--require-complete`,
  `--timeout-seconds 30`, and four Claude aliases:
  `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- The command exited non-zero because `--require-complete` was set and the
  provider did not return a smoke response satisfying the marker contract.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `blocked_by_provider_or_model_availability`, with 5 ready checks, 2 pending
  checks, and 0 failed checks.
- All four aliases timed out after 30 seconds waiting for provider response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- Regenerated `results/external_evidence_closure/closure.{json,md}`,
  `results/external_evidence_packets/packets.{json,md}`,
  `results/ai_scientist_v2_live_run_handoff/handoff.{json,md}`, and
  `results/reproducibility/goal_completion_report.{json,md}`.
- Added `research/run_logs/2026-06-20_phase54_ai_scientist_v2_smoke_packet_retry.md`.
- Push status: pending for Phase 54. Commit and push after verification.

Phase 53 changes currently local:

- Added `scripts/check_external_evidence_packets.py`.
- Added `tests/test_check_external_evidence_packets.py`.
- Generated `results/external_evidence_packets/packets.{json,md}`.
- Integrated execution packets into `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py`.
- Added `research/run_logs/2026-06-20_phase53_external_evidence_packets.md`.
- Updated artifact map, runbook, stage log, result cards, review/checklist,
  goal audit, README, and memory references.
- Current reports:
  - `results/external_evidence_packets/packets.md`: `ready`, 7 ready checks,
    0 pending checks, 0 failed checks.
  - `results/reproducibility/goal_completion_report.md`:
    `not_complete_pending_external_evidence`, 67 ready checks, 8 pending
    checks, 0 failed checks.
  - `results/reproducibility/package_report.md`:
    `ready_with_pending_external_evidence`, 260 ready checks, 8 pending
    checks, 0 failed checks.
- Push status: resolved for Phase 51 through Phase 53. After committing
  `b6bd29b Add external evidence execution packets`, `git push origin main`
  succeeded on 2026-06-20. The follow-up memory-only commit
  `99b26b5 Mark phase 53 pushed in memory` was also pushed, leaving
  `origin/main` synchronized at `99b26b5`.

Phase 51 changes currently local:

- Added `scripts/check_external_evidence_closure.py`.
- Added `tests/test_check_external_evidence_closure.py`.
- Generated `results/external_evidence_closure/closure.{json,md}`.
- Integrated the closure queue into `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py`.
- Added `research/run_logs/2026-06-20_phase51_external_evidence_closure_queue.md`.
- Updated artifact map, runbook, stage log, result cards, review/checklist,
  goal audit, and memory references.
- Local commits:
  - `2031315 Add external evidence closure queue`.
  - `14caad7 Record phase 51 push blocker`.
  - `ce0a5a6 Record phase 51 GitHub connectivity blocker`.
- Push status: blocked. Multiple `git push origin main` attempts on 2026-06-20
  failed: first with `Recv failure: Connection was reset`, then with
  `Failed to connect to github.com port 443`. `git ls-remote origin HEAD` also
  failed on port 443. `Test-NetConnection github.com -Port 443` showed ping
  succeeds but TCP 443 fails. Current branch is ahead of `origin/main` by at
  least 4 local commits; use `git status -sb` as the authoritative count.
  Retry push after committing Phase 53; if it succeeds, record a memory-only
  pushed-status commit.

Phase 52 evidence so far:

- Re-ran `scripts/run_ai_scientist_v2_smoke.py` with shell-only credentials,
  four Claude aliases, and `--timeout-seconds 30`.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `blocked_by_provider_or_model_availability`, with 5 ready checks, 2 pending
  checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- Added `research/run_logs/2026-06-20_phase52_ai_scientist_v2_smoke_retry.md`.
- Local commit: `e35eb38 Refresh AI-Scientist-v2 smoke retry evidence`.
- Push status: blocked. A post-Phase-52 `git push origin main` attempt again
  failed with `Recv failure: Connection was reset`. Current branch is ahead of
  `origin/main` by at least 5 local commits; use `git status -sb` as the
  authoritative count. Retry push before starting Phase 53; if it succeeds,
  record a memory-only pushed-status commit.

Phase 51 current reports:

- External closure queue:
  `results/external_evidence_closure/closure.md` reports
  `pending_external_evidence`, 3 ready checks, 0 pending checks, and 0 failed
  checks. Item statuses: 1 `pending_provider`, 1 `blocked_by_smoke`, 1
  `pending_user_configuration`, 1 `pending_reviewers`, 1
  `pending_billing_rows`, and 1 `pending_decision`.
- External execution packets:
  `results/external_evidence_packets/packets.md` reports `ready`, 7 ready
  checks, 0 pending checks, and 0 failed checks.
- Goal report:
  `results/reproducibility/goal_completion_report.md` reports
  `not_complete_pending_external_evidence`, 67 ready checks, 8 pending checks,
  and 0 failed checks.
- Package report:
  `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 260 ready checks, 8 pending checks,
  and 0 failed checks.

Latest pushed Phase 50 commits: `da704bc Refresh AI-Scientist-v2 smoke timeout
evidence`, `1b98a84 Record phase 50 push pending`, and `6a1cbf8 Mark phase 50
pushed in memory`. Push status: resolved on 2026-06-20; `origin/main` points at
`6a1cbf8`.

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

Latest result: all four aliases timed out after 30 seconds waiting for provider
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
- External evidence closure queue:
  `results/external_evidence_closure/closure.md` reports
  `pending_external_evidence`, 3 ready checks, 0 pending checks, and 0 failed
  checks. It maps all current pending goal requirements to six queue items.
- External evidence execution packets:
  `results/external_evidence_packets/packets.md` reports `ready`, 7 ready
  checks, 0 pending checks, and 0 failed checks.
- AI-Scientist-v2 live-run handoff:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports
  `blocked_by_provider_smoke`, 10 ready checks, 2 pending checks, and 0 failed
  checks.
- Goal report:
  `results/reproducibility/goal_completion_report.md` reports
  `not_complete_pending_external_evidence`, 67 ready checks, 8 pending checks,
  and 0 failed checks.
- Package report:
  `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 260 ready checks, 8 pending checks,
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

Supported after Phase 51:

- AI-Scientist-v2 LLM-client smoke was attempted through local
  `ai_scientist.llm` with four Claude aliases:
  `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- All four aliases timed out after 30 seconds waiting for provider response in
  the latest recheck, so provider/model availability remains blocked.
- The absence of `results/ai_scientist_v2_smoke/response.md` is intentional
  while no alias satisfies the smoke marker contract.
- Package and goal gates separate provider/model availability pending evidence
  from local failures.
- DeepSeek follow-up is locally preflighted: the slot, prompt rows, response
  paths, env names, and next commands are machine-checked, but alias
  configuration and response collection remain pending.
- Remaining external evidence is now centrally mapped in a local closure queue:
  AI-Scientist-v2 smoke completion, AI-Scientist-v2 full live/BFTS run,
  DeepSeek response collection/model-ablation completion, human-fidelity
  annotation, provider billing/success-per-dollar evidence, and AAAI submission
  decision.

## Latest Verification

Latest Phase 54 verification:

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_deepseek_followup.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

Latest full unittest before Phase 54 passed with 70 tests. Re-run the full
suite before committing Phase 54 if more files change. The latest Phase 54
smoke packet retry remains provider-blocked; Phase 54 push is pending.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion satisfying the marker contract.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
