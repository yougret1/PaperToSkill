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
- Claude Opus 4.8 and GPT-family model-ablation prompt rows are saved and
  scored for the current two-case protocol.
- Local output-token proxy over saved Claude/GPT-family model-ablation responses:
  4 measured rows, 2 pending DeepSeek rows, 8,710 `o200k_base` output tokens.

Current unsupported claims:

- Completed live DeepSeek model ablations.
- Completed live cross-harness success.
- Human-validated semantic fidelity.
- Provider billing, realized output-token bills, live invoices, or
  success-per-dollar.
- Reliable arbitrary-PDF-to-skill automation.
- Submission-final or accepted AAAI paper.

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
- `scripts/check_reproducibility_package.py`: aggregate local package gate.
- `scripts/check_aaai_package.py`: AAAI package/build gate.
- `scripts/check_usage_examples.py`: usage-example gate.
- `scripts/check_paper_tables.py`: AAAI result-table consistency gate.
- `scripts/check_paper_claims.py`: paper overclaim/boundary gate.
- `scripts/check_goal_completion.py`: active-goal completion gate.
- `benchmarks/model_ablation_v0.json`: Claude/GPT-family/DeepSeek prompt spec.
- `examples/usage/`: usage examples for skill use, auto-note, and ablations.
- `paper/aaai/`: official AAAI-27 author kit and LaTeX draft.
- `results/reproducibility/`: machine-readable and Markdown readiness reports.
- `research/goal_completion_audit.md`: human-readable requirement audit.
- `research/runbook.md`: reproducible commands.

## Current Reports

- Reproducibility package:
  `results/reproducibility/package_report.md`
  reports `ready_with_pending_external_evidence`, 180 ready checks, 7 pending
  checks, and 0 failed checks.
- Active-goal completion:
  `results/reproducibility/goal_completion_report.md`
  reports `not_complete_pending_external_evidence`, 40 ready checks, 8 pending
  checks, and 0 failed checks.
- AAAI package:
  `results/reproducibility/aaai_package_report.md`
  reports ready, 17 ready checks, 0 failed checks.
- Usage examples:
  `results/reproducibility/usage_example_report.md`
  reports ready, 42 ready checks, 0 failed checks.
- Model ablation response evaluation:
  `results/model_ablation_prompts/v0/evaluation.md`
  reports 6 total rows, 4 scored Claude/GPT-family rows, 2 pending DeepSeek
  rows, and 1.0 average normalized score over scored rows.
- Model response output-token proxy:
  `results/tables/model_response_cost_proxy.md`
  reports 6 total rows, 4 measured rows, 2 pending rows, 9,420 character-proxy
  output tokens, and 8,710 `o200k_base` output tokens.
- Paper tables:
  `results/reproducibility/paper_table_report.md`
  reports ready, 76 ready checks, 0 failed checks.
- Paper claims:
  `results/reproducibility/paper_claim_report.md`
  reports ready, 20 ready checks, 0 failed checks.

## Model/API Configuration

Never commit raw API keys to tracked files. Use environment variables or local
shell-only values.

Claude-family profile:

- Base URL: `https://coderxiaoc.com/v1`.
- Key source: local environment variable, e.g.
  `AI_SCIENTIST_OPENAI_API_KEY`.
- User-requested aliases: `claude-opus-4.8`, `claude-opus-4-6`,
  `claude-opus-4-7`.
- Latest Phase 36 catalog evidence lists 14 Claude-family models, including
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`.
- `claude-opus-4-8` completed both current model-ablation prompt rows with
  HTTP 200; the saved-response scorer reports 2/2 Claude rows scored at 6/6.

GPT-family profile:

- Base URL: `https://coderxiaoc.com/v1`.
- Key source: local environment variable, e.g.
  `PAPERTOSKILL_GPT_OPENAI_API_KEY`.
- Latest catalog evidence with the separate GPT key lists `gpt-5.5`,
  `gpt-5.4`, and other GPT-family models.
- Phase 37 GPT-family retry completed both current prompt rows:
  Toolformer timed out on `gpt-5.5` then succeeded with `gpt-5.4`; AIDE
  succeeded with `gpt-5.5`; both saved responses score 6/6.
- Describe this as a GPT-family result, not a pure `gpt-5.5` result.

DeepSeek:

- Leave `deepseek_followup_slot` pending until the user supplies a concrete
  alias/env vars.
- The runner skips the slot only while its alias remains
  `deepseek-to-be-filled`.

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
| Model evidence state | GPT retry evidence was saved separately from the older Phase 36 failure report. | `scripts/check_goal_completion.py` reads both `run_report.json` and `gpt_retry_run_report.json` so historical GPT 502 evidence and current GPT-family success both remain visible. |
| Output-token accounting | Cost section had input-token proxies but no saved-response output-token accounting. | `scripts/evaluate_model_response_costs.py` reports local output-token proxies for saved Claude/GPT-family responses while preserving the no-provider-billing boundary. |

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
