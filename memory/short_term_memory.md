# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-20.

## Current Phase

Phase 61 is the current local phase. Phase 60 was committed as
`a9fdbad Record post-push provider recheck` and pushed to `origin/main` on
2026-06-20. Phase 61 improves the AI-Scientist-v2 smoke-completion execution
packet so direct provider probes run before wrapper smoke attempts; external
evidence remains pending.

Phase 61 objective:

- Make the smoke-completion execution packet use Phase 59/60 direct provider
  probes as a preflight before AI-Scientist-v2 wrapper smoke.
- Preserve evidence boundaries: provider diagnostics and execution handoffs are
  not smoke completion, BFTS completion, or live research-task evidence.

Phase 59 evidence:

- Added `scripts/run_openai_compatible_direct_probe.py`, a diagnostic that
  bypasses `ai_scientist.llm` and calls `/chat/completions` directly with the
  same tiny marker contract.
- Added tests for success, redaction, missing configuration, and alias fallback.
- Ran direct probes with shell-only credentials:
  - Claude-family: `claude-opus-4-8`, `claude-opus-4.8`,
    `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 503
    `No available accounts: no available accounts`.
  - GPT-family: `gpt-5.5` and `gpt-5.4` both returned HTTP 502
    `Upstream access forbidden, please contact administrator`.
- Reports are under `results/openai_compatible_direct_probe/`; no direct-probe
  response files exist.
- Added `research/run_logs/2026-06-20_phase59_openai_direct_probe.md`.
- Integrated the direct-probe reports into the reproducibility package gate as
  diagnostic readiness checks only.

Phase 60 evidence:

- `git push origin main` succeeded for Phase 59:
  `2488ade..dc52b06  main -> main`.
- Re-ran direct probes with shell-only credentials:
  - Claude-family remains HTTP 503 `No available accounts: no available accounts`.
  - GPT-family remains HTTP 502 `Upstream access forbidden, please contact
    administrator`.
- Added
  `research/run_logs/2026-06-20_phase60_post_push_provider_recheck.md`.
- Refreshed local gate reports. `results/reproducibility/package_report.md`
  still reports `ready_with_pending_external_evidence`, 281 ready checks, 8
  pending checks, and 0 failed checks. `results/reproducibility/goal_completion_report.md`
  still reports `not_complete_pending_external_evidence`, 70 ready checks, 8
  pending checks, and 0 failed checks.

Phase 61 evidence:

- Updated `scripts/check_external_evidence_packets.py` so
  `ai_scientist_v2_smoke_completion` lists the direct-probe runner and
  Claude/GPT-family reports as inputs and runs direct endpoint probes before
  wrapper smoke commands.
- Added completion criteria that at least one direct probe must return a saved
  marker-contract response before wrapper smoke can be considered resolved.
- Expanded the packet secret scan to include closure-report content as well as
  generated packet content.
- Added regression coverage in `tests/test_check_external_evidence_packets.py`
  for direct-probe-first ordering and alias coverage.
- Added
  `research/run_logs/2026-06-20_phase61_direct_probe_packet_preflight.md`.

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
  `claude-opus-4-7`, and `claude-opus-4-6`; Phase 57 GPT-family retry timed
  out for `gpt-5.5` and `gpt-5.4`; Phase 58 capped retries still timed out for
  both credential profiles. Phase 59 direct probes show direct endpoint calls
  are also blocked outside `ai_scientist.llm`.
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

## Phase 59 Verification Completed

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

Results:

- `python -m unittest discover -s tests -v`: 79 tests passed.
- All listed strict checkers passed after direct-probe report and
  submission-review refresh.
- `git diff --check`: no whitespace errors; only line-ending warnings.
- Raw key scan produced no matches.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion satisfying the marker contract.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission decision and submission readiness remain pending.
