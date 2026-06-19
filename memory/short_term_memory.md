# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-20.

## Current Phase

Phase 55 is in progress locally: added an AAAI submission-decision preflight so
the `aaai_submission_decision` closure item is auditable without selecting an
option for the user.

Phase 55 local changes:

- Added `scripts/check_aaai_submission_decision.py`.
- Added `tests/test_check_aaai_submission_decision.py`.
- Generated `results/aaai_submission_decision/decision.{json,md}`.
- Integrated the preflight into `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py`.
- Added
  `research/run_logs/2026-06-20_phase55_aaai_submission_decision_preflight.md`.
- Updated submission-review handoff files, runbook, artifact map, result cards,
  stage log, goal audit, README/memory references as needed.

Current Phase 55 reports:

- `results/aaai_submission_decision/decision.md`:
  `pending_human_decision`, 25 ready checks, 1 pending check, 0 failed checks.
  Both `submit_now_deterministic_offline` and `wait_for_external_evidence` are
  available for a human decision. No option is selected by the preflight.
- `results/reproducibility/goal_completion_report.md`:
  `not_complete_pending_external_evidence`, 70 ready checks, 8 pending checks,
  0 failed checks.
- `results/reproducibility/package_report.md`:
  `ready_with_pending_external_evidence`, 267 ready checks, 8 pending checks,
  0 failed checks.

Git state at the start of Phase 55 was clean:

- `HEAD == origin/main == d8639bcfa35bd77152dc9fe72c003233db9ce3f0`.
- Local commit: `3c6ab9e Add AAAI submission decision preflight`.
- Latest local memory-only commit records the Phase 55 push blocker.
- Push status: blocked. Two `git push origin main` attempts on 2026-06-20
  failed with `Recv failure: Connection was reset`. A follow-up
  `git ls-remote origin HEAD` failed to connect to `github.com` port 443.
  Current branch is ahead of `origin/main` by 2 commits; use `git status -sb`
  as authoritative before retrying.

## Current Evidence

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- Claude Opus 4.8 and GPT-family model-ablation rows are saved and scored for
  the current two-case protocol. In the GPT-family retry, Toolformer timed out
  on `gpt-5.5` then succeeded with `gpt-5.4`, while AIDE succeeded with
  `gpt-5.5`; call this GPT-family evidence, not pure `gpt-5.5`.
- Status anchor for gates: gpt-family rows are now saved and scored; DeepSeek
  remains pending.
- DeepSeek follow-up remains locally preflighted but pending user alias/env
  configuration. `results/deepseek_followup_handoff/handoff.md` reports
  `pending_user_configuration`, 5 ready checks, 2 pending checks, 0 failed
  checks.
- All four live-transfer saved-response sets are complete and scored:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24
  scored rows, 0 pending rows, and average normalized score 1.0.
- AI-Scientist-v2 LLM-client smoke remains provider/model blocked.
  `results/ai_scientist_v2_smoke/run_report.md` reports
  `blocked_by_provider_or_model_availability`; latest Phase 54 packet retry
  tried `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`, and all four aliases timed out after 30 seconds waiting
  for provider response. No `results/ai_scientist_v2_smoke/response.md` exists.
- AI-Scientist-v2 full live/BFTS run remains blocked by smoke.
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports
  `blocked_by_provider_smoke`, 10 ready checks, 2 pending checks, 0 failed
  checks.
- Human-fidelity annotation remains pending:
  `results/human_fidelity_packets/annotation_summary.md` reports 0 scored rows
  and 24 pending rows.
- Provider billing and success-per-dollar evidence remain pending:
  `results/provider_billing_evidence/billing_summary.md` reports 0 measured
  rows, 6 pending rows, total billed USD 0, and success per dollar `n/a`.
- External evidence closure queue and execution packets are ready as local
  handoffs, not evidence completion.

## Boundaries To Preserve

Do not claim:

- DeepSeek completed.
- AI-Scientist-v2 LLM-client smoke completed.
- AI-Scientist-v2 full live LLM/BFTS run completed.
- BFTS or live research-task success completed.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.
- A selected final AAAI submission decision.

Supported after Phase 55:

- The AAAI package, paper-claim, paper-table, usage-example, and
  submission-review gates are locally ready.
- The AAAI submission-decision preflight is locally ready: it exposes the two
  defensible paths and required claim boundaries, but keeps the human decision
  pending.
- `aaai_final_submission_ready` remains pending until a human decision and
  selected evidence policy are recorded.

## Verification To Run Before Phase 55 Commit

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_aaai_submission_decision.py --strict
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

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion satisfying the marker contract.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission decision and submission readiness remain pending.
