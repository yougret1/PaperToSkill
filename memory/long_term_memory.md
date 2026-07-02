# PaperToSkill Long-Term Memory

Read this file after any context compaction or session resume before taking new
project actions. Also read `memory/short_term_memory.md`.

This file is intentionally compact. Detailed chronological history lives in
`research/stage_log.md`, `research/run_logs/`, and `results/result_cards.md`.

## Project Identity

- Project: PaperToSkill.
- Goal: turn research papers into compact, human-editable agent skills that
  preserve the paper's reusable method, validation workflow, limitations,
  failure branches, and transfer notes.
- Local repo: `D:\a_work\gitee\PaperToSkill`.
- Remote repo: `https://github.com/yougret1/PaperToSkill.git`.
- Supporting workspace: `D:\a_work\gitee\ai-scientist-v2`.
- Active branch convention: save phase-level progress to `origin/main` unless
  the user asks for a different branch.

## Persistent User Requirements

- Maintain at least two memory files:
  - `memory/long_term_memory.md` for stable project facts.
  - `memory/short_term_memory.md` for current task state and blockers.
- Keep memory useful and short. Move old phase narration into stage logs and
  reports; preserve only facts needed for future action.
- Use `ai-scientist-v2` to refine and develop the idea where useful.
- Final paper artifacts must use an official AAAI TeX template downloaded from
  the web. Current package is AAAI-27 under `paper/aaai/`.
- Experiments must include usage examples.
- Claude Opus and GPT-family model ablations should be run before the user adds
  DeepSeek following the same process.
- Do not silently treat unavailable model endpoints as model-quality failures.
  Report provider/model availability problems.

## Evidence Boundary

Current supported claims:

- Curated note-to-skill conversion over four papers: AI Scientist-v2,
  Reflexion, AIDE, and Toolformer.
- Deterministic extracted-text-to-note scaffolds for Toolformer and AIDE.
- Offline deterministic evaluations: rubric, context coverage, source-span
  validation, harness-transfer readiness, compactness/token proxy, usage-example
  executability, AAAI package readiness, table consistency, paper claim
  discipline, and active-goal completion auditing.
- Failure-case archive with paper-reported and project-level cases.
- Human-fidelity annotation handoff is ready: review packets, annotation guide,
  stricter blank template metadata, and strict summarizer validation are present
  for 24 paper-by-criterion rows; completed human annotation remains pending.
- Local token accounting handoff is ready: input-token and saved-response
  output-token proxy summaries are present, and the composite local token
  proxy is ready for reuse.
- Claude Opus 4.8, GPT-family, and DeepSeek model-ablation prompt rows are
  saved and scored for the current two-case protocol. GPT-family protocol
  refresh completed both rows with `gpt-5.5`; DeepSeek completed both rows with
  `deepseek-v4-flash`. The latest Claude protocol refresh used Anthropic
  Messages but was blocked by provider HTTP 502, so scored Claude rows come
  from previously saved response files.
- DeepSeek follow-up handoff now reports `responses_present`: the slot, prompt
  rows, response paths, env names, and saved response files are checked for the
  current two-row protocol.
- Local output-token proxy over saved Claude/GPT-family/DeepSeek
  model-ablation responses: 6 measured rows, 0 pending rows, 9,594
  `o200k_base` output tokens.
- New-paper triage on 2026-07-01: cite Paper2Agent as the closest competing
  paper-to-agent/MCP system; cite AgenticSciML as adjacent agentic-science
  workflow background; keep Reasoning Manifolds as a future non-procedural
  stress-case candidate rather than a main experiment. Paper2Agent and
  AgenticSciML are already cited in the AAAI draft; Reasoning Manifolds is
  kept as a future stress-case citation only.
- Bounded Paper2Agent artifact/workflow comparison is complete in
  `results/tables/paper2agent_artifact_comparison.md`: 7/7 criteria are ready.
  It is source-backed positioning evidence only and does not run Paper2Agent,
  deploy an MCP server, or claim end-to-end baseline performance.
- All four live-transfer response sets are saved and scored for both harness
  prompt styles and all three context variants under the current prompt-packet
  protocol. AI Scientist-v2, Reflexion, and AIDE rows score 11/11; Toolformer
  rows score 9/9 in the saved-response output-contract evaluator.
- Bounded AI-Scientist-v2 LLM-client smoke is complete for the local marker
  contract: `results/ai_scientist_v2_smoke/run_report.md` reports `complete`
  and `results/ai_scientist_v2_smoke/response.md` exists. Earlier provider
  failures remain useful historical diagnostics, not current blockers.
- Bounded AI-Scientist-v2 full live run is complete for the current local gate:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`,
  16 ready checks, 0 pending checks, 0 failed checks, and one completion
  directory under
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
  The run produced synthetic benchmark/sensitivity evidence: skill TSR 0.80,
  full excerpt TSR 0.80, abstract TSR 0.20, generic summary/no context 0.00,
  and retrieval-depth skill TSR 1.00 only when K=all. The Stage 3 real-data/HF
  branch remains a failed branch due invalid dataset loading/synthetic padding
  and missing `sentence_transformers`.
- External evidence closure queue is ready as a local planning/checking
  artifact: it maps all current pending goal requirements to two next-action
  items, human-fidelity annotation and AAAI submission decision. Provider
  billing and AI-Scientist-v2 smoke/full live-run evidence are no longer pending
  queue items for the current policy.
- External evidence execution packets are ready as a local handoff artifact:
  each closure item has inputs, setup notes, commands, validation commands,
  completion criteria, escalation rules, and evidence boundaries without
  completing any external evidence. The AAAI submission-decision packet uses
  the validated decision-record helper and requires a validated
  `research/aaai_submission_decision.md` record before final goal/package
  checks can clear `aaai_final_submission_ready`.
- AAAI submission decision is recorded as `wait_for_external_evidence` in
  `research/aaai_submission_decision.md`. The local decision gate is ready, but
  final submission readiness remains pending until the named external evidence
  rows clear under that wait policy.
- Phase 77 final-gate sync verified the newly added papers and API docs. The
  decision remains: cite Paper2Agent and AgenticSciML, keep Reasoning Manifolds
  as a future stress case, and do not add a new main experiment yet. All local
  strict gates and 96 unit tests passed after refreshing the AAAI decision
  state and rebuilding the AAAI PDF.

Current unsupported claims:

- Saved-response model-ablation scoring as proof of live downstream task
  success, broad model quality, provider billing, or provider economics.
- Saved-response output-contract scoring as proof of real live task success.
- Human-validated semantic fidelity.
- Provider billing, realized output-token bills, live invoices, or
  success-per-dollar as current paper claims.
- Reliable arbitrary-PDF-to-skill automation.
- Treating the bounded AI-Scientist-v2 synthetic smoke/full live run as broad
  real-data or live research-task success.
- Submission-final or accepted AAAI paper.
- Final AAAI submission readiness under the recorded wait-for-evidence policy.

## Main Artifact Map

Use these as entry points instead of searching the whole repo first:

- `skill/SKILL.md`: PaperToSkill skill prototype.
- `scripts/papertoskill_extract.py`: source-note-to-skill extractor.
- `scripts/papertoskill_note_from_text.py`: extracted-text-to-note scaffold.
- `scripts/papertoskill_pipeline.py`: local extracted-text-to-note-to-skill
  pipeline manifest command.
- `scripts/run_model_ablation_prompts.py`: OpenAI-compatible live model runner.
- `scripts/evaluate_model_ablation_responses.py`: saved-response scorer.
- `scripts/evaluate_model_response_costs.py`: saved-response output-token proxy.
- `scripts/run_live_transfer_prompts.py`: OpenAI-compatible live-transfer runner.
- `scripts/evaluate_live_transfer_responses.py`: saved live-transfer response
  scorer.
- `scripts/run_ai_scientist_v2_smoke.py`: bounded AI-Scientist-v2 LLM-client
  smoke runner with status-summary output, repeatable `--model-alias`,
  `--timeout-seconds`, `--max-tokens`, and `--require-complete`.
- `scripts/run_openai_compatible_direct_probe.py`: direct provider diagnostic
  for the same tiny marker contract, bypassing `ai_scientist.llm`; this is
  provider-availability evidence only.
- `scripts/check_ai_scientist_v2_live_run_handoff.py`: local full
  AI-Scientist-v2 live/BFTS run handoff and preflight report generator; no
  network calls.
- `scripts/check_reproducibility_package.py`: aggregate local package gate.
- `scripts/check_aaai_package.py`: AAAI package/build gate.
- `scripts/check_usage_examples.py`: usage-example gate.
- `scripts/check_paper_tables.py`: AAAI result-table consistency gate.
- `scripts/check_paper_claims.py`: paper overclaim/boundary gate.
- `scripts/check_submission_review.py`: submission-review handoff freshness
  gate.
- `scripts/check_goal_completion.py`: active-goal completion gate.
- `scripts/check_external_evidence_closure.py`: no-network closure queue for
  pending external evidence and final-decision items.
- `scripts/check_external_evidence_packets.py`: no-network execution packet
  builder for each pending external-evidence item.
- `scripts/check_aaai_submission_decision.py`: no-network AAAI submission
  decision preflight; exposes decision options without selecting one.
- `scripts/generate_aaai_submission_decision.py`: validated helper for writing
  the human AAAI submission-decision record after an explicit option, owner,
  date, claim boundary, and evidence policy are provided.
- `benchmarks/model_ablation_v0.json`: Claude/GPT-family/DeepSeek prompt spec.
- `scripts/check_deepseek_followup.py`: local DeepSeek follow-up handoff and
  preflight report generator; no network calls.
- `research/new_paper_triage_2026-07-01.md`: triage of Paper2Agent,
  AgenticSciML, and Reasoning Manifolds against PaperToSkill.
- `benchmarks/provider_billing_evidence_v0.json`: provider-billing evidence
  slot protocol.
- `scripts/summarize_provider_billing_evidence.py`: billing handoff template
  and summary validator.
- `examples/usage/`: usage examples for skill use, auto-note, and ablations.
- `paper/aaai/`: official AAAI-27 author kit and LaTeX draft.
- `results/reproducibility/`: machine-readable and Markdown readiness reports.
- `research/goal_completion_audit.md`: human-readable requirement audit.
- `research/runbook.md`: reproducible commands.

## Current Reports

- Reproducibility package:
  `results/reproducibility/package_report.md`
  reports `ready_with_pending_external_evidence`, 305 ready checks, 1 pending
  check, and 0 failed checks.
- Active-goal completion:
  `results/reproducibility/goal_completion_report.md`
  reports `not_complete_pending_external_evidence`, 77 ready checks, 3 pending
  checks, and 0 failed checks.
- External evidence closure queue:
  `results/external_evidence_closure/closure.md`
  reports `pending_external_evidence`, 3 ready checks, 0 pending checks, and 0
  failed checks. The two queue items are human-fidelity annotation and AAAI
  final submission readiness under the recorded wait policy.
- External evidence execution packets:
  `results/external_evidence_packets/packets.md`
  reports `ready`, 7 ready checks, 0 pending checks, and 0 failed checks. The
  packets cover the same two queue items and are local handoffs, not completed
  evidence.
- AAAI submission-decision preflight:
  `results/aaai_submission_decision/decision.md`
  reports `ready`, `selected_option=wait_for_external_evidence`, 27 ready
  checks, 0 pending checks, and 0 failed checks. This records the decision to
  wait; it does not complete the external evidence rows.
- AI-Scientist-v2 LLM-client smoke:
  `results/ai_scientist_v2_smoke/run_report.md`
  reports `complete`, 6 ready checks, 0 pending checks, and 0 failed checks.
- Protocol-specific direct provider probes:
  `results/openai_compatible_direct_probe/claude_family/run_report.md` reports
  `wire_api=anthropic_messages`, 4 ready checks, 2 pending checks, and 0 failed
  checks; `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` returned
  HTTP 502 `Upstream service temporarily unavailable`. The GPT-family report
  uses `wire_api=openai_responses`, has 3 ready checks, 2 pending checks, and 0
  failed checks; `gpt-5.5` and `gpt-5.4` returned HTTP 502
  `Upstream access forbidden`.
- AI-Scientist-v2 live-run handoff:
  `results/ai_scientist_v2_live_run_handoff/handoff.md`
  reports `complete`, 16 ready checks, 0 pending checks, 0 failed checks, and
  one completion directory.
- AAAI package:
  `results/reproducibility/aaai_package_report.md`
  reports ready, 17 ready checks, 0 failed checks.
- Usage examples:
  `results/reproducibility/usage_example_report.md`
  reports ready, 55 ready checks, 0 failed checks.
- DeepSeek follow-up handoff:
  `results/deepseek_followup_handoff/handoff.md`
  reports `responses_present`, 7 ready checks, 0 pending checks, and 0 failed
  checks.
- Model ablation response evaluation:
  `results/model_ablation_prompts/v0/evaluation.md`
  reports 6 total rows, 6 scored rows, 0 pending rows, and 1.0 average
  normalized score.
- Model response output-token proxy:
  `results/tables/model_response_cost_proxy.md`
  reports 6 total rows, 6 measured rows, 0 pending rows, 10,381
  character-proxy output tokens, and 9,594 `o200k_base` output tokens.
- Local token accounting evidence:
  `results/token_accounting/token_accounting_summary.md`
  reports 4,322 generated-skill input tokens, 95,303 full-extracted input
  tokens, 9,594 saved-response output tokens, and a 13,916 composite local
  token proxy.
- Live-transfer response evaluation:
  `results/live_transfer_prompts/evaluation.md`
  reports 24 total rows, 24 scored rows, 0 pending rows, and 1.0 average
  normalized score. AI Scientist-v2, Reflexion, and AIDE rows score 11/11;
  Toolformer rows score 9/9.
- Paper tables:
  `results/reproducibility/paper_table_report.md`
  reports ready, 76 ready checks, 0 failed checks.
- Paper claims:
  `results/reproducibility/paper_claim_report.md`
  reports ready, 20 ready checks, 0 failed checks.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md`
  reports ready, 15 ready checks, 0 failed checks.

## Model/API Configuration

Never commit raw API keys to tracked files. Use environment variables or local
shell-only values.

Claude-family profile:

- Direct Claude diagnostics and local Claude Desktop/CC Switch routing use
  Anthropic Messages at base URL `https://coderxiaoc.com`, request path
  `/v1/messages`, and `anthropic-version: 2023-06-01`.
- Current direct-probe aliases: `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6`. The older dotted spelling `claude-opus-4.8` remains in
  historical reports only; do not use it in new direct-probe handoff commands.
- Key source: local environment variable, e.g.
  `AI_SCIENTIST_OPENAI_API_KEY`; never commit raw keys.
- Latest direct provider probe for the AI-Scientist-v2 evidence path used
  `PAPERTOSKILL_CLAUDE_BASE_URL=https://coderxiaoc.com`,
  `PAPERTOSKILL_CLAUDE_API_KEY`, Anthropic Messages, and aliases
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`; all returned
  HTTP 502, so no fresh direct-probe response file exists.
- Scored Claude model-ablation rows come from previously saved responses; do
  not describe the latest Claude protocol refresh as a fresh success.

GPT-family profile:

- Direct GPT diagnostics use OpenAI Responses at base URL
  `https://coderxiaoc.com/v1` and request path `/responses`.
- Key source: local environment variable, e.g.
  `PAPERTOSKILL_GPT_OPENAI_API_KEY`.
- Latest catalog evidence with the separate GPT key lists `gpt-5.5`,
  `gpt-5.4`, and other GPT-family models.
- Current protocol-refresh evidence: GPT-family completed both current prompt
  rows with `gpt-5.5` through OpenAI Responses and both saved responses score
  6/6. Older Phase 37 fallback evidence remains historical only.

DeepSeek:

- `deepseek_followup_slot` is currently configured as `deepseek-v4-flash`.
- Current DeepSeek run completed both two-case protocol rows through
  OpenAI-compatible Chat Completions; both saved responses score 6/6.
- The runner skips the slot only if its alias is reset to
  `deepseek-to-be-filled`.
- Use `scripts/check_deepseek_followup.py --strict` before and after future
  edits to verify prompt rows, response paths, env names, and saved responses.

## Engineering/Fix History To Preserve

| Area | Problem Found | Fix / Current Location |
| --- | --- | --- |
| Extractor parsing | Multiline list items split into fragments; title inferred as `Methods`. | Merge continuation lines and infer title from H1/LaTeX title in `scripts/papertoskill_extract.py`; covered by `tests/test_papertoskill_extract.py`. |
| Extractor recall | AIDE exposed truncation of workflow/validation/failure bullets. | Increased candidate limits in `scripts/papertoskill_extract.py`; regression test keeps richer bullets. |
| Numbered continuations | Indented numbered continuations inside wrapped bullets became new bullets. | Treat only unindented list markers as new bullets in `scripts/papertoskill_extract.py`. |
| Source-span anchors | `pdftotext` form-feed characters shifted line anchors. | Use newline-delimited counting in `scripts/validate_source_spans.py`; covered by tests. |
| Source-map audit | First source-map audit mis-mapped section groups and scored all cases badly. | Map skill sections to source-note section groups in `scripts/audit_skill_source_map.py`. |
| Auto-note scaffold | Toolformer auto-note initially mixed two-column PDF text/references and exceeded compactness. | Preserve raw line spacing, split likely columns, prefer keyword-bearing column, shorten snippets in `scripts/papertoskill_note_from_text.py`. |
| AIDE auto-note | Toolformer profile was semantically poor on AIDE; figure captions and related-work snippets leaked in. | Added `--profile aide`, target-section-first selection, overlap exception for shared AIDE caveat. |
| Pipeline ergonomics | The extracted-text-to-note-to-skill workflow required three manual commands. | Added `scripts/papertoskill_pipeline.py` to write note, skill, source map, rubric report, and manifest in one local command. |
| PDF pipeline input | Users needed a smoke-tested direct PDF entry point without claiming robust PDF understanding. | `scripts/papertoskill_pipeline.py` accepts `.pdf` sources through `pdftotext -layout`, records extracted text in the manifest, and remains bounded as local smoke support. |
| Human fidelity | Blank annotation rows could be mistaken for negative scores. | `scripts/summarize_human_fidelity_annotations.py` marks blanks as pending. |
| Reproducibility | Local package readiness was conflated with external live/human evidence. | `scripts/check_reproducibility_package.py` uses ready/pending/fail statuses. |
| AAAI package | File presence was weaker than checking the actual author kit/build state. | `scripts/check_aaai_package.py` checks SHA256, style use, fresh PDF/log/BibTeX, unresolved markers. |
| Usage examples | Markdown examples could drift from executable paths. | `scripts/check_usage_examples.py` validates files, prompt slots, and offline AIDE example chain. |
| Paper tables | LaTeX table values could drift from CSV results. | `scripts/check_paper_tables.py` compares `paper/aaai/papertoskill_tables.tex` with generated CSVs. |
| Paper claims | Draft/AAAI text could overclaim pending evidence. | `scripts/check_paper_claims.py` checks unsupported positive claims and required boundary statements. |
| Goal completion | Narrative completion audit could stale. | `scripts/check_goal_completion.py` makes the active-goal status machine-checkable. |
| External evidence closure | Pending requirements were spread across multiple reports and docs. | `scripts/check_external_evidence_closure.py` maps current pending goal requirements to concrete queue items without claiming evidence completion. |
| External evidence execution | Closure queue items still required manual interpretation before handoff. | `scripts/check_external_evidence_packets.py` turns each queue item into inputs, commands, completion criteria, and escalation boundaries without claiming evidence completion; the AAAI decision packet now routes final-decision recording through `scripts/generate_aaai_submission_decision.py`. |
| AAAI submission decision | The final submission item was only a checklist row. | `scripts/check_aaai_submission_decision.py` creates a preflight report with submit-now vs wait-for-evidence options while keeping the human decision pending. |
| AAAI decision record | A human decision record could be hand-written with drift, unavailable options, or secret-like fields. | `scripts/generate_aaai_submission_decision.py` writes the record only after an explicit option, owner, date, claim boundary, and evidence policy; it validates option availability and rejects raw API-key-like material. |
| AAAI gate recursion | The decision preflight and goal/package gates can read each other during report refreshes, causing self-referential intermediate failures. | `scripts/check_aaai_submission_decision.py` treats only the known self-referential failure set as pending during its own preflight; regression covered by `tests/test_check_aaai_submission_decision.py`. |
| Model evidence state | GPT retry evidence was saved separately from the older Phase 36 failure report. | `scripts/check_goal_completion.py` reads both `run_report.json` and `gpt_retry_run_report.json` so historical GPT 502 evidence and current GPT-family success both remain visible. |
| Output-token accounting | Cost section had input-token proxies but no saved-response output-token accounting. | `scripts/evaluate_model_response_costs.py` reports local output-token proxies for saved Claude/GPT-family responses while preserving the no-provider-billing boundary. |
| AI-Scientist-v2 smoke boundary | AI-Scientist-v2 dry-run and live-transfer saved responses could be confused with a full live run. | `scripts/run_ai_scientist_v2_smoke.py` records bounded client smoke attempts with alias fallback, script-level timeout, and a tiny-request `--max-tokens` cap; the current marker-contract smoke is complete, but it remains separate from human fidelity and broad live task success. |
| Direct provider diagnosis | AI-Scientist-v2 smoke timeouts could be misread as only a wrapper bug or as only a model-name issue. | `scripts/run_openai_compatible_direct_probe.py` is protocol-aware: Claude-family direct diagnostics use Anthropic Messages (`/v1/messages`) and GPT-family direct diagnostics use OpenAI Responses (`/v1/responses`) with the same marker contract. Historical provider blockers are diagnostics; the bounded smoke/full live-run evidence is now complete. |

## Persistent Rules

- On resume, read both memory files first.
- Use `rg`/`rg --files` for search.
- Use `apply_patch` for manual edits.
- Do not revert user/local changes, especially in `ai-scientist-v2`.
- Keep exploratory notes, active work, and validated claims separate.
- Promote claims only when backed by files, tests, logs, or explicit user
  decisions.
- Before phase saving, run relevant tests/checkers, `git diff --check`, and a
  raw-key scan.

## Model Interface Facts

- GPT provider style follows OpenAI Responses API.
- GPT BaseURL: `https://coderxiaoc.com/v1`.
- GPT models confirmed usable: `gpt-5.5`, `gpt-5.4`.
- Claude provider style follows Anthropic Messages API.
- Claude BaseURL: `https://coderxiaoc.com` with request path `/v1/messages`.
- Claude models confirmed usable: `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`.
- 2026-06-30 verification: the local Desktop docs in `C:\Users\19351\Desktop\tem`
  are runnable. GPT doc returned HTTP 200 on the first attempt for
  `gpt-5.5` and `gpt-5.4` via `POST /v1/responses`. Claude doc returned HTTP 200
  on the first attempt for `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6` via `POST /v1/messages`.
- DeepSeek temporary key verified on 2026-06-30:
  `GET https://api.deepseek.com/models` returned `deepseek-v4-flash` and
  `deepseek-v4-pro`; `POST https://api.deepseek.com/chat/completions`
  succeeded for both models; `deepseek-v4-flash` returned visible content `ok`
  on a slightly larger max-tokens probe.
- 2026-07-01 re-test of the three Desktop API docs: GPT doc still runnable
  (`gpt-5.5` HTTP 200 on attempt 2, `gpt-5.4` HTTP 200 on attempt 1, both
  returned `ok`); DeepSeek doc runnable (`deepseek-v4-flash` and
  `deepseek-v4-pro` both HTTP 200 on attempt 1, returned `ok`); Claude doc did
  not complete as a direct HTTP request in this run (`claude-opus-4-8`,
  `claude-opus-4-7`, and `claude-opus-4-6` returned HTTP 502 after five
  attempts with both the regular doc key and Desktop token). Treat this as
  current upstream/direct-request unavailability, not proof of bad model names.
- 2026-07-01 same-day Claude-only re-test: the regular Claude doc key worked
  for `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` via
  `POST https://coderxiaoc.com/v1/messages`; all returned HTTP 200 on attempt 1
  with visible `ok`. The same regular key also worked with the Claude
  Code/Desktop beta header. The Desktop direct provider token still returned
  HTTP 502 after five attempts for all three aliases.
