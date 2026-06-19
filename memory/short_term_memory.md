# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-20.

## Current Phase

Phase 57 is in progress locally. Phase 56 was committed and pushed as
`f1cc165 Refresh AI-Scientist-v2 smoke after push recovery`; before Phase 57
edits, `HEAD == origin/main == f1cc165c0bfb290d0e8041b72a40cab89c15fb74`.

Phase 57 objective:

- Test whether the bounded AI-Scientist-v2 LLM-client smoke can complete with
  the GPT-family credential profile after repeated Claude-family provider
  blockers.
- Keep this as provider/model availability evidence only, not model-quality or
  live research-task evidence.

Phase 57 evidence so far:

- Used shell-only credentials:
  `AI_SCIENTIST_OPENAI_BASE_URL=https://coderxiaoc.com/v1`,
  `AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE=1`, and the GPT-family key mapped into
  `AI_SCIENTIST_OPENAI_API_KEY` for this smoke only.
- Ran:
  `python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 60 --model-alias gpt-5.5 --model-alias gpt-5.4`.
- The command exited non-zero because `--require-complete` was set.
- `results/ai_scientist_v2_smoke/run_report.md` remains
  `blocked_by_provider_or_model_availability`, with 3 ready checks, 2 pending
  checks, and 0 failed checks.
- `gpt-5.5` and `gpt-5.4` both timed out after 60 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- Added
  `research/run_logs/2026-06-20_phase57_ai_scientist_v2_gpt_smoke_retry.md`.
- Updated the external-evidence closure queue and execution-packet generators
  so the AI-Scientist-v2 smoke handoff lists both Claude-family and GPT-family
  retry commands.

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
  Earlier Claude-family attempts included HTTP 403 account exhaustion and
  repeated 30-second timeouts for `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6`; latest Phase 57 GPT-family retry
  timed out for `gpt-5.5` and `gpt-5.4` after 60 seconds each.
- AI-Scientist-v2 full live/BFTS run remains blocked by smoke.
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports
  `blocked_by_provider_smoke`, with no completion artifacts.
- Human-fidelity annotation remains pending:
  `results/human_fidelity_packets/annotation_summary.md` reports 0 scored rows
  and 24 pending rows.
- Provider billing and success-per-dollar evidence remain pending:
  `results/provider_billing_evidence/billing_summary.md` reports 0 measured
  rows, 6 pending rows, total billed USD 0, and success per dollar `n/a`.
- External evidence closure queue, execution packets, and AAAI
  submission-decision preflight are local handoffs/preflights only, not
  completed external evidence.

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

Supported:

- The AAAI package, paper-claim, paper-table, usage-example, and
  submission-review gates are locally ready when their checkers pass.
- The AAAI submission-decision preflight exposes two defensible paths and keeps
  the human decision pending.
- `aaai_final_submission_ready` remains pending until a human decision and
  selected evidence policy are recorded.

## Verification To Run Before Phase 57 Commit

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
