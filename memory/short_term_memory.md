# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-02.

## Latest Resume/Completion Note

- 2026-07-02 Phase 77 final sync completed after reviewing the added papers and
  API docs.
- New-papers decision remains unchanged after verification:
  - Paper2Agent: closest competing work; cite and compare through the bounded
    artifact/workflow table.
  - AgenticSciML: adjacent related work; cite, no immediate experiment.
  - Reasoning Manifolds: future non-procedural stress case; no current main
    experiment.
- API docs at
  `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument` were re-read:
  GPT uses OpenAI Responses (`/v1/responses`), Claude uses Anthropic Messages
  (`/v1/messages`), and DeepSeek uses Chat Completions (`/chat/completions`).
- Corrected stale AAAI decision/claim wording so the project no longer waits
  for AI-Scientist-v2 smoke/full live evidence; that bounded evidence is
  complete but remains only integration/synthetic sensitivity evidence.
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf` after paper-facing wording
  changes and added LaTeX temporary build files to `.gitignore`.
- Verification passed:
  `python -m unittest discover -s tests -v` (96 tests),
  all strict local gates, `git diff --check`, and repository raw-key scan.
- Current reports:
  - Goal completion: 77 ready / 3 pending / 0 failed.
  - Reproducibility package: 305 ready / 1 pending / 0 failed.
  - External evidence queue: `human_fidelity_annotation` and
    `aaai_submission_decision`.
  - AAAI decision: ready, selected `wait_for_external_evidence`.
- `C:\Users\19351\Desktop\tem\toHuman\needHelp.md` currently asks only for
  human-fidelity annotation. No `ok.txt` was present in the latest check.

## Current Presentation Handoff

- Latest PPT for the doctoral progress report is saved at
  `C:\Users\19351\Desktop\tem\PaperToSkill_博士生阶段进展汇报.pptx`.
- The latest revision directly answers the user's workflow questions:
  - Slide 8 is the real operational workflow. It now states that left-to-right
    is only the main path and shows that failed gates, missing evidence, or
    provider failures return to earlier steps instead of silently passing.
  - Slide 10 is the engineering implementation map. It explains each Slide 8
    step in beginner-friendly language with the local script/action, output,
    and failure check.
- Keep the verbal distinction short in future responses: Slide 8 explains what
  happens to a paper in actual operation; Slide 10 explains which local scripts,
  files, and checks implement that operation.
- Do not describe the real workflow as a one-way pipeline.
- 2026-06-30 verification: both local interface docs in `C:\Users\19351\Desktop\tem`
  are runnable. GPT doc (`gpt-5.5`, `gpt-5.4`) returned HTTP 200 on the first
  attempt via `POST https://coderxiaoc.com/v1/responses`. Claude doc
  (`claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`) returned HTTP 200
  on the first attempt via `POST https://coderxiaoc.com/v1/messages`.
- 2026-07-01 re-test: GPT and DeepSeek docs are currently runnable, while the
  Claude doc did not succeed as direct HTTP this time.
  - GPT doc: `gpt-5.5` returned HTTP 200 on attempt 2 and `gpt-5.4` returned
    HTTP 200 on attempt 1 via `POST https://coderxiaoc.com/v1/responses`.
  - DeepSeek doc: `deepseek-v4-flash` and `deepseek-v4-pro` both returned
    HTTP 200 on attempt 1 via
    `POST https://api.deepseek.com/chat/completions`.
  - Claude doc: `claude-opus-4-8`, `claude-opus-4-7`, and
    `claude-opus-4-6` returned HTTP 502 after five attempts via
    `POST https://coderxiaoc.com/v1/messages` with both the regular doc key
    (`sk-c83d...cad7`) and Desktop token (`sk-6477...000e`). This indicates
    current upstream/direct-request unavailability, not a model-name proof.
- 2026-07-01 same-day Claude-only re-test:
  - Regular Claude doc key (`sk-c83d...cad7`) worked for `claude-opus-4-8`,
    `claude-opus-4-7`, and `claude-opus-4-6` via
    `POST https://coderxiaoc.com/v1/messages`; all returned HTTP 200 on
    attempt 1 and visible `ok`.
  - The same regular key also worked for all three models with the
    Claude Code/Desktop beta header.
  - Desktop token (`sk-6477...000e`) still returned HTTP 502 after five
    attempts for all three models.
  - Current answer: Claude doc is runnable with the regular API key; Desktop
    token is not currently runnable by naked direct HTTP.
- 2026-07-01 update after the latest handoff:
  - Local token accounting now replaces provider-billing evidence for the
    current project state.
  - `results/token_accounting/token_accounting_summary.md` reports 4,322
    generated-skill input tokens, 95,303 full-extracted input tokens, 9,594
    saved-response output tokens, and 13,916 composite local token proxy.
  - The AAAI submission decision has been recorded as
    `wait_for_external_evidence`.

## Current Phase

Phase 77 is the current local phase. Phase 68 was committed as
`5548070 Refresh memory anchors after remote save` and pushed to `origin/main`
on 2026-06-20. Phase 69 syncs the AAAI submission-decision execution packet
with the validated decision-record helper; no external evidence status is
promoted and no AAAI option is selected. Phase 70 updates the direct provider
diagnostic to match the current coderxiaoc API protocols: Claude uses
Anthropic Messages and GPT uses OpenAI Responses.

Phase 76/77 evidence:

- AI-Scientist-v2 bounded LLM-client smoke is complete:
  `results/ai_scientist_v2_smoke/run_report.md` reports `complete`, 6 ready
  checks, 0 pending checks, and 0 failed checks.
- AI-Scientist-v2 bounded full live run is complete:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`,
  16 ready checks, 0 pending checks, 0 failed checks, and one completion
  directory:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
- Stage 1/2 validated an offline synthetic benchmark: skill TSR 0.80, full
  excerpt TSR 0.80, abstract TSR 0.20, generic summary/no context 0.00; skill
  token cost 86.2 versus full excerpt 113.2.
- Stage 3 HF/semantic-data branch is a failed branch only: invalid dataset
  loading/synthetic padding and missing `sentence_transformers`. Do not promote
  those numbers to the main paper.
- Stage 4 retrieval-depth sensitivity reports skill TSR 0.80 for K=1/2/3/5 and
  1.00 for K=all. Treat this as synthetic sensitivity evidence, not a final
  main-paper component ablation.
- Stale external-evidence reports were refreshed in dependency order. Current
  closure queue has two items: `human_fidelity_annotation` and
  `aaai_submission_decision`. Execution packets also have two packets.
- Current generated reports after refresh:
  - Goal completion: 77 ready / 3 pending / 0 failed.
  - Reproducibility package: 305 ready / 1 pending / 0 failed.
  - External evidence closure queue: 2 items, 3 ready checks, 0 failed checks.
  - External evidence execution packets: 2 packets, 7 ready checks, 0 failed
    checks.
- `C:\Users\19351\Desktop\tem\toHuman\needHelp.md` no longer asks for
  AI-Scientist-v2 provider/live-run help. It keeps only human-fidelity
  annotation as the current human-side action.
- Run log:
  `research/run_logs/2026-07-02_phase76_ai_scientist_v2_full_live_run.md`.

Phase 73/74 evidence:

- User added three PDFs under `papers/raw`; extracted text exists under
  `papers/extracted_text`.
- 2026-07-01 human-help signal check: `C:\Users\19351\Desktop\tem\toHuman\ok.txt`
  was present, reviewed, and removed after confirming the handoff. `needHelp.md`
  remains the live escalation log.
- Triage decision:
  - Paper2Agent (`arXiv:2509.06917`) is core related/competing work. It
    converts papers plus codebases into MCP servers and interactive paper
    agents; cite it and use the current bounded artifact/workflow comparison
    for positioning.
  - AgenticSciML (`doi:10.1038/s44387-026-00102-5`, `arXiv:2511.07262`) is
    adjacent agentic-science workflow background; cite it, but do not add an
    immediate experiment.
  - Reasoning Manifolds (`arXiv:2605.08142`) is a future theory-heavy
    non-procedural stress case, not a main experiment now.
- Current citation state:
  - `paper/aaai/papertoskill_aaai2027.tex` already cites Paper2Agent and
    AgenticSciML in Related Work.
  - `paper/aaai/papertoskill_refs.bib` already includes Paper2Agent,
    AgenticSciML, and Reasoning Manifolds entries.
  - No additional main experiment is required for Reasoning Manifolds yet.
- Updated AAAI related work/bib, related-work gap map, claim-source map, and
  `research/new_paper_triage_2026-07-01.md`.
- API docs in `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument` confirm:
  GPT uses OpenAI Responses at `https://coderxiaoc.com/v1/responses`; Claude
  uses Anthropic Messages at `https://coderxiaoc.com/v1/messages`; DeepSeek
  uses Chat Completions at `https://api.deepseek.com/chat/completions`.
- Current model-ablation protocol state:
  - GPT protocol refresh completed both current rows with `gpt-5.5`.
  - DeepSeek completed both current rows with `deepseek-v4-flash`.
  - Latest Claude protocol refresh used Anthropic Messages but returned
    provider HTTP 502; scored Claude rows come from older saved response files.
  - `results/model_ablation_prompts/v0/evaluation.md` reports 6 total, 6
    scored, 0 pending, average normalized 1.0.
  - `results/tables/model_response_cost_proxy.md` reports 6 measured, 0
    pending, 9,594 `o200k_base` output tokens.
- Evidence boundary: saved-response scoring is not live downstream task
  success, human semantic fidelity, provider billing, success per dollar, or a
  broad model-quality comparison.
- Paper2Agent artifact/workflow comparison:
  - `results/tables/paper2agent_artifact_comparison.md` reports
    `overall_status=ready`, 7 ready criteria, and 0 failed criteria.
  - This is source-backed artifact/workflow positioning only. It does not run
    Paper2Agent, deploy an MCP server, or prove baseline performance.
- Phase 75 generated reports before the Phase 76 live-run refresh:
  - Goal completion: 75 ready / 5 pending / 0 failed.
  - Reproducibility package: 301 ready / 5 pending / 0 failed.
  - Submission review: 15 ready / 0 failed after the latest refresh.
  - AAAI submission decision: ready, recorded
    `selected_option=wait_for_external_evidence`, 27 ready / 0 pending /
    0 failed.
  - External evidence closure queue: 4 items after token-accounting removal
    from the pending-evidence queue.
  - External evidence execution packets: 4 packets, 7 ready / 0 pending /
    0 failed.
  - Superseded by Phase 76 reports: goal 77 ready / 3 pending / 0 failed,
    package 305 ready / 1 pending / 0 failed, closure queue 2 items, packets
    2 items.
- 2026-07-01 Phase 75 sync:
  - Updated tests and `scripts/check_submission_review.py` so current reports
    accept the recorded AAAI wait decision and completed local token accounting
    instead of stale pending-decision/provider-billing assumptions.
  - Re-ran the Claude direct provider probe with the documented Anthropic
    Messages protocol, regular key, `PAPERTOSKILL_CLAUDE_BASE_URL`, and
    `PAPERTOSKILL_CLAUDE_API_KEY`; `claude-opus-4-8`,
    `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 502. This was
    a Phase 75 provider-availability observation, not a model-quality failure;
    it is superseded for the bounded AI-Scientist-v2 evidence path by the
    Phase 76 smoke/full live-run completion artifacts.
  - `python -m unittest discover -s tests -v` passed: 96 tests.

Phase 62 objective:

- Make it easier for the user to add DeepSeek later without manually editing
  JSON or committing secrets.
- Preserve evidence boundaries: configuring a DeepSeek slot is not collecting
  responses, scoring DeepSeek rows, or completing model ablations.

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

Phase 62 evidence:

- Added `scripts/configure_deepseek_followup.py`, which configures only
  non-secret DeepSeek slot metadata: model alias, auth env name, base-url env
  name, and provider status.
- The helper rejects raw API-key-like strings and requires uppercase
  environment-variable names for credential locations.
- Added `tests/test_configure_deepseek_followup.py`.
- Updated `scripts/check_deepseek_followup.py`,
  `scripts/check_external_evidence_packets.py`,
  `examples/usage/model_ablation_usage.md`, `research/runbook.md`, and package
  gates so future DeepSeek setup uses the helper.
- Added
  `research/run_logs/2026-06-20_phase62_deepseek_configuration_helper.md`.
- Current refreshed reproducibility package report is
  `ready_with_pending_external_evidence`, 282 ready checks, 8 pending checks,
  and 0 failed checks.
- Phase 62 was committed locally as
  `0db90e2 Add DeepSeek followup configuration helper`, but push to
  `origin/main` is currently blocked by GitHub HTTPS connectivity. `git push`
  returned `Recv failure: Connection was reset`; `git ls-remote origin main`
  failed to connect to `github.com:443`; `Test-NetConnection github.com -Port
  443` reported ping success but `TcpTestSucceeded=False`. Current local state
  after the failed push is `main...origin/main [ahead 1]`.
- Phase 63 added a push-recovery section to `research/runbook.md` with the
  status, push, `ls-remote`, and GitHub 443 diagnostic commands to run on the
  next resume.

Phase 64 evidence:

- `git push origin main` succeeded and advanced GitHub from `92beb7f` to
  `ad8346b`, saving both local commits:
  `0db90e2 Add DeepSeek followup configuration helper` and
  `ad8346b Record GitHub push connectivity diagnostics`.
- `git status -sb` then reported `main...origin/main`, so local tracking state
  was clean and aligned after the push.
- A follow-up `git ls-remote --heads origin main` still failed with
  `Recv failure: Connection was reset`, so treat GitHub HTTPS access as
  intermittent; do not treat the old Phase 62/63 save as pending.

Phase 65 evidence:

- Re-ran direct OpenAI-compatible probes with shell-only credentials and the
  tiny marker contract.
- Claude-family aliases `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` still returned HTTP 503
  `No available accounts: no available accounts`.
- GPT-family aliases `gpt-5.5` and `gpt-5.4` still returned HTTP 502
  `Upstream access forbidden, please contact administrator`.
- Reports under `results/openai_compatible_direct_probe/` remain
  `blocked_by_provider_or_model_availability`; no direct-probe response files
  exist. This is diagnostic only and does not complete AI-Scientist-v2 smoke.

Phase 66 evidence:

- Added `scripts/generate_aaai_submission_decision.py`.
- Added `tests/test_generate_aaai_submission_decision.py`.
- Updated `scripts/check_aaai_submission_decision.py` so the preflight lists
  the helper as an input and shows validated helper commands for both decision
  options.
- Updated `research/runbook.md`, `research/artifact_map.md`, and
  reproducibility package checks to include the helper.
- No `research/aaai_submission_decision.md` decision record was generated; the
  final AAAI submission decision remains pending a human research-lead choice.
- Phase 66 was pushed to `origin/main` as
  `4c020132be895469441489371516e6d14af7d2ef`.

Phase 67 evidence:

- Phase 67 was pushed to `origin/main` as
  `a0d67bc8d64ee7b25f3319817634fbc426bf31e0`.
- `git status -sb` after the Phase 67 push reported `main...origin/main`.

Phase 68 evidence:

- Refreshed long-term memory report counts to match current generated reports:
  reproducibility package `283 ready / 8 pending / 0 failed`, AAAI decision
  preflight `26 ready / 1 pending / 0 failed`, and usage examples `55 ready /
  0 failed`.
- Added `scripts/generate_aaai_submission_decision.py` and the AAAI gate
  recursion fix to the long-term artifact/fix map.
- Current recovery anchor before Phase 68 commit:
  `a0d67bc8d64ee7b25f3319817634fbc426bf31e0`.

Phase 69 evidence:

- Updated `scripts/check_external_evidence_packets.py` so the
  `aaai_submission_decision` packet lists
  `scripts/generate_aaai_submission_decision.py` and
  `results/aaai_submission_decision/decision.json` as inputs.
- The AAAI decision packet now separates pre-decision local gates, exactly one
  human-selected helper command, and final validation after
  `research/aaai_submission_decision.md` exists.
- Added regression assertions in
  `tests/test_check_external_evidence_packets.py`.
- Regenerated `results/external_evidence_packets/packets.{json,md}` and
  refreshed dependent AAAI decision, goal-completion, and package reports.
- Current refreshed report anchors remain:
  - `results/external_evidence_packets/packets.md`: ready, 7 ready checks,
    0 pending checks, 0 failed checks.
  - `results/aaai_submission_decision/decision.md`: pending human decision,
    26 ready checks, 1 pending check, 0 failed checks.
  - `results/reproducibility/goal_completion_report.md`: not complete pending
    external evidence, 70 ready checks, 8 pending checks, 0 failed checks.
  - `results/reproducibility/package_report.md`: ready with pending external
    evidence, 283 ready checks, 8 pending checks, 0 failed checks.
- No `research/aaai_submission_decision.md` decision record was generated; the
  final AAAI submission decision remains pending a human research-lead choice.

Phase 70 evidence:

- Verified local Claude Desktop / CC Switch routing:
  - Claude Desktop config uses `inferenceGatewayBaseUrl=https://coderxiaoc.com`
    and bearer auth.
  - CC Switch current Claude Desktop provider sets
    `ANTHROPIC_BASE_URL=https://coderxiaoc.com` and
    `ANTHROPIC_AUTH_TOKEN` locally.
  - Normal Claude direct request shape is Anthropic Messages:
    `POST https://coderxiaoc.com/v1/messages` with `Authorization: Bearer ...`
    and `anthropic-version: 2023-06-01`.
- Updated `scripts/run_openai_compatible_direct_probe.py` from a fixed
  `/chat/completions` diagnostic into a protocol-aware direct provider probe
  with `--wire-api openai_chat_completions|openai_responses|anthropic_messages`.
- Updated external-evidence closure/packet commands so current direct probes
  use:
  - Claude: `--wire-api anthropic_messages`, base URL `https://coderxiaoc.com`,
    aliases `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`.
  - GPT: `--wire-api openai_responses`, base URL
    `https://coderxiaoc.com/v1`, aliases `gpt-5.5`, `gpt-5.4`.
- Refreshed direct probe reports with shell-only credentials:
  - Claude-family report now has `wire_api=anthropic_messages`, 4 ready checks,
    2 pending checks, 0 failed checks, and all three Claude aliases returned
    HTTP 502 `Upstream service temporarily unavailable`.
  - GPT-family report now has `wire_api=openai_responses`, 3 ready checks,
    2 pending checks, 0 failed checks, and both GPT aliases returned HTTP 502
    `Upstream access forbidden, please contact administrator`.
- Updated `research/runbook.md` and generated external-evidence packets to
  distinguish protocol-specific direct probes from the legacy
  AI-Scientist-v2 wrapper smoke path.
- Local Desktop docs remain outside the repo at:
  - `C:\Users\19351\Desktop\tem\GPT大模型接口说明文档.md`
  - `C:\Users\19351\Desktop\tem\Claude大模型接口说明文档.md`
- No direct-probe response file was produced; AI-Scientist-v2 LLM-client smoke
  and full live/BFTS run remain pending provider availability.

## Current Evidence

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- Claude Opus 4.8 and GPT-family model-ablation rows are saved and scored for
  the current two-case protocol. In the GPT-family retry, Toolformer timed out
  on `gpt-5.5` then succeeded with `gpt-5.4`, while AIDE succeeded with
  `gpt-5.5`; call this GPT-family evidence, not pure `gpt-5.5`.
- Status anchor for gates: Claude/GPT-family/DeepSeek rows are now saved and
  scored for the current two-case model-ablation protocol; latest Claude
  protocol refresh is provider-blocked and should not be read as a model-quality
  failure.
- DeepSeek follow-up now reports `responses_present`. `results/deepseek_followup_handoff/handoff.md`
  reports 7 ready checks, 0 pending checks, and 0 failed checks.
- All four live-transfer saved-response sets are complete and scored:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24
  scored rows, 0 pending rows, and average normalized score 1.0.
- AI-Scientist-v2 LLM-client smoke is complete for the bounded marker contract:
  `results/ai_scientist_v2_smoke/run_report.md` reports `complete`, and
  `results/ai_scientist_v2_smoke/response.md` exists.
- AI-Scientist-v2 bounded full live run is complete:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`
  with one completion directory under
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
  This is bounded integration/synthetic sensitivity evidence, not broad live
  task-success proof.
- Human-fidelity annotation remains pending:
  `results/human_fidelity_packets/annotation_summary.md` reports 0 scored rows
  and 24 pending rows.
- Provider billing and success-per-dollar evidence are outside the current
  claim set; local token accounting replaces them for the current package in
  `results/token_accounting/token_accounting_summary.md`.
- External evidence closure queue, execution packets, and AAAI
  submission-decision gate are local handoffs/preflights only, not completed
  external evidence. The AAAI decision record now says
  `wait_for_external_evidence`, but final submission readiness is still
  pending under that policy.

## Boundaries To Preserve

Do not claim:

- Broad BFTS or live research-task success beyond the bounded Phase 76
  AI-Scientist-v2 run.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence as current claims.
- Saved-response model-ablation scoring proves live task success, broad model
  quality, provider billing, or provider economics.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.
- Final AAAI submission readiness under the recorded wait-for-evidence policy.

Supported:

- The AAAI package, paper-claim, paper-table, usage-example, and
  submission-review gates are locally ready when their checkers pass.
- The AAAI submission-decision gate validates the recorded
  `wait_for_external_evidence` decision.
- `aaai_final_submission_ready` remains pending until the named external
  evidence rows clear under that policy.

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

- AI-Scientist-v2 bounded smoke/full live-run evidence is complete, but it is
  not human semantic fidelity, not a real-data result, and not a broad live
  research-task success claim.
- Human-fidelity annotation remains pending.
- Local token accounting is complete; provider billing and success-per-dollar
  evidence remain out of scope for the current claim set.
- Final AAAI submission readiness remains pending under the recorded
  `wait_for_external_evidence` policy.
