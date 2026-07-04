# Stage Log

## 2026-06-17 Phase 0

Actions:

- Created long-term and short-term memory files.
- Created research contract, artifact map, decision log, idea cards,
  claim-evidence matrix, and experiment design.
- Created AI-Scientist-v2 workshop input and seed idea JSON.
- Inspected AI-Scientist-v2 README, launch script, BFTS config, LLM client, and
  OpenAI-compatible backend changes.
- Installed missing local Python dependencies needed for smoke tests.
- Tested the provided endpoint at `/v1/models` and direct chat completion.
- Ran AI-Scientist-v2 dry-run using
  `ai_scientist_inputs/papertoskill_seed_ideas.json`.
- Created first PaperToSkill skill prototype at `skill/SKILL.md`.

Findings:

- PaperToSkill repo is connected to `https://github.com/yougret1/PaperToSkill.git`.
- AI-Scientist-v2 already has local modifications that add
  OpenAI-compatible backend support and smaller local-laptop BFTS settings.
- `/v1/models` works and advertises `claude-opus-4-8`.
- Chat completion currently fails because the provider reports exhausted/no
  available accounts.
- Dry-run succeeded and created:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- The generated `idea.md` and `bfts_config.yaml` look structurally valid.
- Phase 0 artifacts are ready for validation and commit.

Risks:

- Global Python environment has dependency conflicts after installing the
  AI-Scientist-v2 requirements.
- Long AI-Scientist-v2 experiments should wait until the remote endpoint works
  and an isolated environment exists.

## 2026-06-17 Phase 1

Actions:

- Created a seed benchmark manifest with agent/LLM-method papers.
- Created a seed literature matrix, related-work gap map, and claim source map.
- Implemented `scripts/papertoskill_extract.py`, a deterministic local extractor
  that produces `SKILL.md` plus `references/source_map.json`.
- Added `tests/test_papertoskill_extract.py`.
- Added `examples/papertoskill_paper_note.md` as a paper-like retained case.
- Generated retained skills under `generated_skills/`.

Findings:

- The scaffold can progress without remote LLM availability.
- Method, experiment, and limitation sections can be mapped into workflow,
  validation, and failure-case sections.
- An abstract-only input falls back to a generic scaffold, which is useful but
  should not be treated as high-fidelity extraction.

Failure found and fixed:

- Initial extraction split multiline Markdown list items and inferred the title
  incorrectly as `Methods`.
- Fixed by merging continuation lines and inferring title from the first H1 or
  LaTeX title.

Verification:

- `python -m json.tool benchmarks\paper_manifest.json`
- `python -m unittest discover -s tests -v`
- `python scripts\papertoskill_extract.py --source examples\papertoskill_paper_note.md --output generated_skills\papertoskill_paper_note --name papertoskill-paper-note`
- `python scripts\papertoskill_extract.py --source ai_scientist_inputs\papertoskill.md --output generated_skills\papertoskill_seed --name papertoskill-seed --title "PaperToSkill Seed"`

## 2026-06-17 Phase 2

Actions:

- Downloaded the AI Scientist-v2 PDF from arXiv.
- Extracted PDF text with `pdftotext -layout`.
- Rendered page 1 with `pdftoppm` and visually inspected readability.
- Created `papers/notes/ai_scientist_v2_note.md`, a curated source-anchored
  note with abstract, methods, experiments, limitations, and transfer notes.
- Generated `generated_skills/ai_scientist_v2/SKILL.md`.
- Added `benchmarks/rubric_v0.json` and `scripts/evaluate_skill.py`.
- Added evaluator tests and saved rubric output under `results/evaluations/`.

Findings:

- The real-paper note preserves AI Scientist-v2's four-stage experiment manager,
  parallelized agentic tree search, debug/refine branching, specialized node
  types, replication/aggregation, VLM critique, and ethical limitations.
- The generated skill scored 20/20 on rubric v0.

Evidence boundary:

- Rubric v0 is deterministic and useful for smoke validation, but it is not
  evidence of downstream task improvement over summaries.

Verification:

- `pdfinfo papers\raw\ai_scientist_v2.pdf`
- `pdftotext -layout papers\raw\ai_scientist_v2.pdf papers\extracted\ai_scientist_v2.txt`
- `pdftoppm -f 1 -l 1 -png -r 120 papers\raw\ai_scientist_v2.pdf output\pdf\ai_scientist_v2\page`
- `python scripts\papertoskill_extract.py --source papers\notes\ai_scientist_v2_note.md --output generated_skills\ai_scientist_v2 --name ai-scientist-v2-paper-skill`
- `python scripts\evaluate_skill.py --skill generated_skills\ai_scientist_v2\SKILL.md --rubric benchmarks\rubric_v0.json --output results\evaluations\ai_scientist_v2_rubric_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 3

Actions:

- Created `benchmarks/tasks/ai_scientist_v2_research_run.json`.
- Created generic-summary and abstract-only baselines.
- Implemented `scripts/evaluate_context_baselines.py`.
- Added `tests/test_evaluate_context_baselines.py`.
- Ran deterministic skill-vs-summary-vs-abstract context coverage evaluation.

Results:

- PaperToSkill generated skill: 7.867/9, 782 words.
- Generic summary: 1.733/9, 154 words.
- Abstract-only context: 1.2/9, 99 words.

Evidence boundary:

- This is a deterministic coverage baseline, not proof of downstream agent task
  success. It is valid as an early reproducible signal that the generated skill
  preserves more operational components than short summaries for one task.

Verification:

- `python scripts\evaluate_context_baselines.py --task benchmarks\tasks\ai_scientist_v2_research_run.json --output results\evaluations\ai_scientist_v2_context_baselines_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 4

Actions:

- Created a source-map-aware unsupported-instruction audit task.
- Implemented `scripts/audit_skill_source_map.py`.
- Added `tests/test_audit_skill_source_map.py`.
- Audited the real AI Scientist-v2 skill, the paper-like retained case, and the
  abstract-only seed.

Results:

- AI Scientist-v2 real skill unsupported rate: 0.2
- Paper-like retained case unsupported rate: 0.222
- Abstract-only seed unsupported rate: 1.0

Failure and fix:

- The first audit run mis-mapped section groups and incorrectly yielded 1.0 for
  all skills.
- Fixed by mapping skill sections onto source-note section groups before scoring.

Evidence boundary:

- The audit is heuristic and source-map-aware, not a human annotation study.

Verification:

- `python scripts\audit_skill_source_map.py --task benchmarks\tasks\skill_source_audit.json --output results\evaluations\skill_source_audit_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 5

Actions:

- Created an offline Codex/Claude-style harness-transfer task.
- Implemented `scripts/evaluate_harness_transfer.py`.
- Added `tests/test_evaluate_harness_transfer.py`.
- Compared the full AI Scientist-v2 generated skill, the same skill with
  `Transfer Notes` removed, and a generic summary baseline.

Results:

- Full generated skill average readiness score: 10.0/10.
- Skill without transfer notes average readiness score: 7.6/10.
- Generic summary average readiness score: 1.2/10.

Evidence boundary:

- This is an offline deterministic transfer-readiness metric, not a live
  cross-harness agent task run.

Verification:

- `python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\ai_scientist_v2_harness_transfer.json --output results\evaluations\ai_scientist_v2_harness_transfer_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 6

Actions:

- Re-tested the OpenAI-compatible endpoint.
- Added live cross-harness prompt packet task and builder.
- Added source-span validation task and validator.
- Generated six prompt packets for Codex-style and Claude-style harnesses across
  full skill, no-transfer-notes, and generic-summary contexts.
- Fixed source-span line counting to use newline-delimited lines rather than
  Python `splitlines()` because `pdftotext` form-feed characters shifted
  anchors.

Results:

- `/v1/models` succeeded and listed `claude-opus-4-8`.
- `/v1/chat/completions` still failed with HTTP 502:
  `All available accounts exhausted`.
- Source-span validation: 15 supported claims, 1 weak claim, 0 invalid ranges,
  support rate 0.938.

Evidence boundary:

- Prompt packets are ready for later live execution but are not live agent run
  results.
- Source-span validation is lexical/line-based, not human factuality annotation.

Verification:

- `python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\ai_scientist_v2_live_transfer.json --output-dir results\live_transfer_prompts\ai_scientist_v2_v0`
- `python scripts\validate_source_spans.py --task benchmarks\tasks\ai_scientist_v2_source_span_validation.json --output results\evaluations\ai_scientist_v2_source_span_validation_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 7

Actions:

- Selected Reflexion as the second real paper benchmark because it directly
  supports PaperToSkill's memory and failure-branch themes.
- Downloaded the Reflexion PDF from arXiv.
- Extracted text with `pdftotext -layout`.
- Rendered page 1 with `pdftoppm`.
- Created `papers/notes/reflexion_note.md`.
- Generated `generated_skills/reflexion/SKILL.md`.
- Added a Reflexion-specific rubric and source-span validation task.

Results:

- Reflexion generated skill scored 20/20 on
  `benchmarks/rubric_reflexion_v0.json`.
- Reflexion source-span validation found 11 supported anchored claims, 0 weak or
  unsupported claims, 0 invalid ranges, and support rate 1.0.

Evidence boundary:

- This extends the benchmark to two curated real-paper notes, but does not yet
  evaluate Reflexion against summary baselines or live agents.

Verification:

- `pdfinfo papers\raw\reflexion.pdf`
- `pdftotext -layout papers\raw\reflexion.pdf papers\extracted\reflexion.txt`
- `pdftoppm -f 1 -l 1 -png -r 120 papers\raw\reflexion.pdf output\pdf\reflexion\page`
- `python scripts\papertoskill_extract.py --source papers\notes\reflexion_note.md --output generated_skills\reflexion --name reflexion-paper-skill`
- `python scripts\evaluate_skill.py --skill generated_skills\reflexion\SKILL.md --rubric benchmarks\rubric_reflexion_v0.json --output results\evaluations\reflexion_rubric_v0.json`
- `python scripts\validate_source_spans.py --task benchmarks\tasks\reflexion_source_span_validation.json --output results\evaluations\reflexion_source_span_validation_v0.json`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 8

Actions:

- Added Reflexion generic-summary and abstract-only baselines.
- Added Reflexion downstream context-coverage task.
- Added Reflexion offline harness-transfer readiness task.
- Added Reflexion live transfer prompt packet task.
- Generated Reflexion live prompt packets for Codex-style and Claude-style
  harnesses.

Results:

- Reflexion context baseline:
  - generated skill: 8.267/9
  - generic summary: 3.483/9
  - abstract-only context: 2.533/9
- Reflexion harness-transfer readiness:
  - full skill: 10.0/10
  - skill without transfer notes: 7.6/10
  - generic summary: 2.25/10

Evidence boundary:

- These are deterministic/offline evaluations, not live agent task success.
- Live prompt packets are execution-ready inputs but still need later model
  responses.

Verification:

- `python scripts\evaluate_context_baselines.py --task benchmarks\tasks\reflexion_research_run.json --output results\evaluations\reflexion_context_baselines_v0.json`
- `python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\reflexion_harness_transfer.json --output results\evaluations\reflexion_harness_transfer_v0.json`
- `python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\reflexion_live_transfer.json --output-dir results\live_transfer_prompts\reflexion_v0`
- `python -m unittest discover -s tests -v`

## 2026-06-17 Phase 9

Actions:

- Implemented `scripts/aggregate_results_tables.py` to aggregate existing
  deterministic/offline evaluation JSON into paper-ready Markdown and CSV
  tables.
- Added `tests/test_aggregate_results_tables.py`.
- Generated main results, transfer ablation, compactness/source-grounding, and
  combined summary tables under `results/tables/`.

Results:

- `results/tables/main_results.md` summarizes two real-paper cases:
  AI Scientist-v2 and Reflexion both score 20/20 on the deterministic skill
  rubric; generated skills score 7.867/9 and 8.267/9 on context coverage,
  respectively.
- `results/tables/transfer_ablation.md` shows the full skill at 10/10 offline
  readiness for both papers, dropping to 7.6/10 when `Transfer Notes` are
  removed.
- `results/tables/compactness_source_grounding.md` records 782 and 479 word
  skills, 2/2 compactness scores, support rates of 0.938 and 1.0, and no
  invalid source-span ranges.

Evidence boundary:

- The tables aggregate existing deterministic/offline evaluations. They do not
  add live cross-harness agent-task evidence.
- Reflexion does not yet have a source-map unsupported-instruction audit row, so
  that table cell is explicitly `n/a`.

Verification:

- `python scripts\aggregate_results_tables.py --output-dir results\tables`
- `python -m unittest tests.test_aggregate_results_tables -v`

## 2026-06-17 Phase 10

Actions:

- Re-tested the OpenAI-compatible endpoint. `/v1/models` worked and listed
  `claude-opus-4-8`; `/v1/chat/completions` returned HTTP 503 with an empty
  body.
- Added AIDE as the third real-paper case:
  - raw PDF, extracted text, and rendered page 1;
  - source-anchored note;
  - generated skill and source map;
  - generic-summary and abstract-only baselines;
  - rubric, context-coverage, harness-transfer, source-span, and live prompt
    packet tasks.
- Fixed an extractor truncation issue exposed by AIDE by increasing candidate
  limits from 6/5/5 to 8/7/6 for workflow/validation/failure bullets and adding
  a regression test.
- Regenerated paper-ready result tables.

Results:

- AIDE generated skill scored 20/20 on `benchmarks/rubric_aide_v0.json`.
- AIDE context baseline:
  - generated skill: 9.1/10
  - generic summary: 1.916/10
  - abstract-only context: 1.333/10
- AIDE harness-transfer readiness:
  - full skill: 10.0/10
  - skill without transfer notes: 7.6/10
  - generic summary: 1.5/10
- AIDE source-span validation found 21 supported anchored claims, 0 weak or
  unsupported claims, 0 invalid ranges, and support rate 1.0.
- `results/tables/main_results.md` now covers AI Scientist-v2, Reflexion, and
  AIDE.

Evidence boundary:

- These are deterministic/offline evaluations, not live cross-harness agent task
  success.
- The remote LLM endpoint remains unsuitable for live runs because chat
  completion returned HTTP 503.

Verification:

- `pdfinfo papers\raw\aide.pdf`
- `pdftotext -layout papers\raw\aide.pdf papers\extracted\aide.txt`
- `pdftoppm -f 1 -l 1 -png -r 120 papers\raw\aide.pdf output\pdf\aide\page`
- `python scripts\papertoskill_extract.py --source papers\notes\aide_note.md --output generated_skills\aide --name aide-paper-skill`
- `python scripts\evaluate_skill.py --skill generated_skills\aide\SKILL.md --rubric benchmarks\rubric_aide_v0.json --output results\evaluations\aide_rubric_v0.json`
- `python scripts\evaluate_context_baselines.py --task benchmarks\tasks\aide_research_run.json --output results\evaluations\aide_context_baselines_v0.json`
- `python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\aide_harness_transfer.json --output results\evaluations\aide_harness_transfer_v0.json`
- `python scripts\validate_source_spans.py --task benchmarks\tasks\aide_source_span_validation.json --output results\evaluations\aide_source_span_validation_v0.json`
- `python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\aide_live_transfer.json --output-dir results\live_transfer_prompts\aide_v0`
- `python scripts\aggregate_results_tables.py --output-dir results\tables`

## 2026-06-17 Phase 11

Actions:

- Created a paper draft package under `paper/`.
- Added an outline with contribution bullets, section plan, and figure/table
  plan.
- Added a claim checklist that separates supported deterministic/offline claims
  from unsupported live-agent or full-automation claims.
- Added a first evidence-bounded draft grounded in the three-paper benchmark.
- Added a limitations file focused on curated inputs, heuristic metrics, blocked
  live transfer, missing human fidelity annotation, benchmark diversity, and
  cost accounting.
- Updated README, artifact map, decision log, result cards, and memory.

Results:

- The paper narrative now matches the current evidence: PaperToSkill supports a
  curated paper-note-to-skill conversion claim over three real agent-method
  papers, with deterministic coverage, compactness, source-grounding, and
  offline transfer-readiness results.
- The draft explicitly avoids claiming live cross-harness success, fully
  automatic arbitrary-PDF conversion, human-validated fidelity, or realized
  economic savings.

Evidence boundary:

- Phase 11 is synthesis and writing, not a new empirical run.
- Empirical claims still depend on the Phase 2-10 deterministic/offline
  evaluations.

Verification:

- `python -m unittest discover -s tests -v`: passed, 10 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 12

Actions:

- Implemented `scripts/evaluate_context_costs.py`.
- Added `tests/test_evaluate_context_costs.py`.
- Generated context-size and coverage-efficiency proxy artifacts:
  - `results/tables/context_cost_proxy.md`
  - `results/tables/context_cost_proxy.csv`
  - `results/tables/coverage_cost_efficiency.csv`
  - `results/tables/context_cost_proxy.json`
- Updated `results/tables/paper_ready_summary.md`.
- Updated `paper/outline.md`, `paper/draft.md`, `paper/claim_checklist.md`,
  and `paper/limitations.md` with the token/cost proxy evidence boundary.
- Updated artifact map, decision log, result cards, and memory.

Results:

- Generated skills use 1,366 estimated input tokens vs 62,041 for the full
  extracted AI Scientist-v2 paper, 823 vs 18,559 for Reflexion, and 1,517 vs
  15,894 for AIDE.
- This corresponds to deterministic input-token proxy reductions of 97.8%,
  95.57%, and 90.46% relative to full extracted paper text.
- Summary and abstract contexts are smaller, but their deterministic coverage
  scores remain substantially lower than the generated skills.

Evidence boundary:

- Token counts are estimated as `ceil(characters / 4)`.
- Cost uses a configurable `$1.00 / 1M` input-token proxy.
- Results are not provider bills, tokenizer-exact measurements, or
  success-per-dollar evidence.

Verification:

- `python -m unittest discover -s tests -v`: passed, 11 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 13

Actions:

- Re-tested the OpenAI-compatible endpoint.
- Added `benchmarks/human_fidelity_review_v0.json`, a six-criterion human-
  fidelity review protocol.
- Added `scripts/build_human_fidelity_packets.py`.
- Added `tests/test_build_human_fidelity_packets.py`.
- Generated human-fidelity packet artifacts under
  `results/human_fidelity_packets/`.
- Updated paper limitations, claim checklist, outline, draft, claim-evidence
  matrix, artifact map, decision log, result cards, stage log, and memory.

Results:

- `/v1/models` worked and listed `claude-opus-4-8`.
- `/v1/chat/completions` returned HTTP 503 with an empty body, so live transfer
  remains blocked by the provider.
- Prepared three human-fidelity review packets:
  - `results/human_fidelity_packets/ai_scientist_v2_human_fidelity_packet.md`
  - `results/human_fidelity_packets/reflexion_human_fidelity_packet.md`
  - `results/human_fidelity_packets/aide_human_fidelity_packet.md`
- Prepared `results/human_fidelity_packets/annotation_template.csv` with 18
  blank annotation rows for 3 papers x 6 criteria.

Evidence boundary:

- Human-fidelity packets are prepared, but no independent annotation has been
  completed.
- The paper may claim "human-fidelity review protocol prepared" but not
  "human-validated".

Verification:

- `python -m unittest discover -s tests -v`: passed, 12 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 14

Actions:

- Added `scripts/summarize_human_fidelity_annotations.py`.
- Added `tests/test_summarize_human_fidelity_annotations.py`.
- Generated:
  - `results/human_fidelity_packets/annotation_summary.md`
  - `results/human_fidelity_packets/annotation_summary.json`
- Updated README, paper draft package, artifact map, decision log, result cards,
  stage log, and memory.

Results:

- Current annotation summary reports:
  - annotation status: `pending`
  - total rows: `18`
  - scored rows: `0`
  - pending rows: `18`
  - validation errors: `0`

Evidence boundary:

- Blank score rows are pending, not negative evidence.
- The summary is not human-validation evidence until independent reviewers fill
  rows and the summary reports complete with no errors.

Verification:

- `python -m unittest discover -s tests -v`: passed, 14 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 15

Actions:

- Added `benchmarks/failure_case_archive_v0.json`.
- Added `scripts/build_failure_case_archive.py`.
- Added `tests/test_build_failure_case_archive.py`.
- Generated:
  - `results/failure_cases/failure_case_archive.json`
  - `results/failure_cases/failure_case_archive.md`
  - `results/failure_cases/failure_case_archive.csv`
- Updated README, paper draft package, claim-evidence matrix, artifact map,
  decision log, result cards, stage log, and memory.

Results:

- The archive records 20 cases:
  - 14 paper-reported limitations or failure branches from the three source
    maps;
  - 6 project-level failure/fix records from PaperToSkill development.
- Categories include cost, ethics, evaluation validity, evaluator bug, external
  dependency, extraction recall bug, extractor bug, memory limit, missing
  evidence, paper limitation, quality limit, quality threshold, search failure,
  and source-span bug.

Evidence boundary:

- The failure archive is a provenance artifact and claim-discipline aid.
- It is not a controlled outcome study and does not show that failure recording
  improves final user outcomes or live reproduction success.

Verification:

- `python -m unittest tests.test_build_failure_case_archive -v`: passed, 1 test OK.
- `python -m unittest discover -s tests -v`: passed, 15 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 16

Actions:

- Re-tested the OpenAI-compatible endpoint.
- Added `scripts/check_reproducibility_package.py`.
- Added `tests/test_check_reproducibility_package.py`.
- Generated:
  - `results/reproducibility/package_report.json`
  - `results/reproducibility/package_report.md`
- Updated the failure-case archive with the Phase 16 endpoint retest.
- Updated README, paper draft package, claim-evidence matrix, artifact map,
  decision log, result cards, stage log, experiment queue, and memory.

Results:

- `/v1/models` worked and listed `claude-opus-4-8`.
- `/v1/chat/completions` returned HTTP 503 with an empty body.
- Reproducibility package report:
  - overall status: `ready_with_pending_external_evidence`
  - ready checks: `63`
  - pending checks: `4`
  - failed checks: `0`
- Pending checks correspond to the three live response sets and completed
  human-fidelity annotation.

Evidence boundary:

- The package is locally reviewable and has no failed local checks.
- It still does not support completed live cross-harness, human-validated, or
  provider-billing claims.

Verification:

- `python -m unittest tests.test_check_reproducibility_package -v`: passed, 2 tests OK.
- `python -m unittest discover -s tests -v`: passed, 17 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 17

Actions:

- Added `research/review_report.md`.
- Added `research/rebuttal_bank.md`.
- Updated README, paper draft pointers, paper outline appendix plan, artifact
  map, decision log, result cards, stage log, and memory.

Results:

- The review report identifies eight major risks around summarization,
  deterministic metrics, curated notes, benchmark diversity, offline-only
  transfer, pending human fidelity, cost proxy interpretation, and failure
  archive interpretation.
- The rebuttal bank maps likely reviewer questions to concrete evidence files
  and explicitly lists unsupported phrases to avoid.

Evidence boundary:

- Phase 17 is an internal review/readiness phase.
- It adds no new empirical result and does not complete live or human-fidelity
  evidence.

Verification:

- `python -m unittest discover -s tests -v`: passed, 17 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 18

Actions:

- Added Toolformer as a fourth curated real-paper stress case focused on
  self-supervised tool-use data generation, API-call filtering, and
  inference-time tool execution.
- Added Toolformer baselines, paper-specific rubric, context-coverage task,
  harness-transfer task, source-span validation task, and live prompt-packet
  task.
- Regenerated Toolformer deterministic evaluations and live prompt packets.
- Extended paper-ready result aggregation, context-cost proxy, human-fidelity
  packets, failure-case archive, and reproducibility package checks to cover
  Toolformer.
- Updated paper draft package, claim checklist, limitations, review/rebuttal
  artifacts, artifact map, decision log, result cards, experiment queue, stage
  log, and memory.

Results:

- Toolformer skill rubric: `20/20`.
- Toolformer context baseline:
  - generated skill: `8.9/10`
  - generic summary: `2.5/10`
  - abstract-only context: `1.534/10`
- Toolformer harness-transfer readiness:
  - full skill: `10.0/10`
  - skill without transfer notes: `7.6/10`
  - generic summary: `1.45/10`
- Toolformer source-span validation found 22 supported anchored claims, 0 weak
  or unsupported claims, 0 invalid ranges, and support rate `1.0`.
- Toolformer context cost proxy: generated skill `1,526` estimated input tokens
  versus `24,097` for full extracted paper text, a `93.67%` token-proxy
  reduction.
- Human-fidelity review packets now cover four papers and the blank annotation
  template contains 24 rows.
- Failure-case archive now records 27 cases: 21 paper-reported limitations or
  failure branches and 6 project-level failure/fix records.
- Reproducibility package report now shows `ready_with_pending_external_evidence`
  with 75 ready checks, 5 pending checks, and 0 failed checks.

Evidence boundary:

- Phase 18 adds deterministic/offline evidence for a fourth curated paper note.
- It does not complete live cross-harness execution, human-fidelity annotation,
  tokenizer-exact pricing, provider billing, or success-per-dollar evidence.

Verification:

- `python -m unittest discover -s tests -v`: passed, 17 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

## 2026-06-17 Phase 19

Actions:

- Added `scripts/papertoskill_note_from_text.py`, a deterministic scaffold that
  converts extracted paper text into a source-anchored Markdown note.
- Added `tests/test_papertoskill_note_from_text.py` with both synthetic and
  Toolformer extracted-text coverage.
- Updated `scripts/papertoskill_extract.py` to preserve a seventh limitation
  bullet, then added a regression test.
- Generated `papers/auto_notes/toolformer_auto_note.md` and
  `generated_skills/toolformer_auto/SKILL.md`.
- Added Toolformer auto-note context, transfer, and source-span task specs.
- Generated deterministic auto-note evaluations and an
  `results/tables/auto_note_comparison.md` table.

Results:

- Toolformer auto-note-derived skill rubric: `20/20`.
- Toolformer auto-note context baseline:
  - auto-note-derived skill: `9.3/10`
  - generic summary: `2.5/10`
  - abstract-only context: `1.534/10`
- Toolformer auto-note harness-transfer readiness:
  - full skill: `10.0/10`
  - no-transfer-notes variant: `7.6/10`
  - generic summary: `1.45/10`
- Toolformer auto-note source-span validation found 20 supported claims, 0 weak
  or unsupported claims, 0 invalid ranges, and support rate `1.0`.
- The auto-note-derived skill is 1,179 words, under the 1,200-word compactness
  budget.

Failure and fix:

- The first auto-note scaffold mixed two-column PDF text and references into
  selected snippets. The script was updated to preserve raw line spacing, split
  likely columns, and select the keyword-bearing column while keeping the
  original newline line anchors.
- The first auto-note skill exceeded the compactness budget and missed several
  exact rubric signals. The script shortened snippets and made source-backed
  prefixes more explicit without hand-editing the generated auto-note.
- Two limitation anchors were too weak despite passing lexical validation. The
  selector now prefers stronger exact phrases and later analysis sections for
  targeted limitation specs.

Evidence boundary:

- Phase 19 supports a deterministic extracted-text-to-note scaffold and a first
  retained auto-note-derived Toolformer skill.
- It does not prove reliable arbitrary-PDF-to-skill automation, human semantic
  fidelity, live agent success, or robustness across diverse PDF layouts.

Verification:

- `python -m unittest discover -s tests -p test_papertoskill_note_from_text.py -v`: passed, 2 tests OK.
- Toolformer auto-note generation, extraction, rubric, context, transfer, and
  source-span commands all completed.

## 2026-06-17 Phase 20

Actions:

- Extended `scripts/papertoskill_note_from_text.py` with source-selection
  profiles. The default `toolformer` profile is preserved and a new `aide`
  profile targets code/ML-engineering concepts such as solution space,
  solution trees, search policy, coding actions, summarization, data preview,
  Weco-Kaggle, MLE-Bench, RE-Bench, data contamination, local optima, larger
  codebases, and LLM inference cost.
- Fixed selection order so target-section matches are preferred before
  full-document fallback.
- Added an overlap exception for the AIDE live-competition caveat because it
  shares a source paragraph with data-contamination evidence.
- Fixed `scripts/papertoskill_extract.py` so indented numbered continuations
  inside wrapped bullets do not become separate Markdown bullets.
- Added regression tests for the AIDE auto-note profile and indented numbered
  continuation handling.
- Generated `papers/auto_notes/aide_auto_note.md` and
  `generated_skills/aide_auto/SKILL.md`.
- Added AIDE auto-note context, transfer, and source-span task specs.
- Generated deterministic AIDE auto-note evaluations and updated
  `results/tables/auto_note_comparison.md` to compare curated-vs-auto rows for
  both Toolformer and AIDE.
- Extended the reproducibility package checker to include AIDE auto-note
  artifacts and auto-note transfer-ablation gates.

Results:

- AIDE auto-note-derived skill rubric: `20/20`.
- AIDE auto-note context baseline:
  - auto-note-derived skill: `8.467/10`
  - generic summary: `1.916/10`
  - abstract-only context: `1.333/10`
- AIDE auto-note harness-transfer readiness:
  - full skill: `9.5/10`
  - no-transfer-notes variant: `7.1/10`
  - generic summary: `1.5/10`
- AIDE auto-note source-span validation found 17 supported claims, 0 weak or
  unsupported claims, 0 invalid ranges, and support rate `1.0`.
- The auto-note-derived AIDE skill is 998 words, under the 1,200-word
  compactness budget.
- Reproducibility package report now shows
  `ready_with_pending_external_evidence`, 105 ready checks, 5 pending checks,
  and 0 failed checks.

Failure and fix:

- A direct Toolformer-profile run on AIDE was semantically poor and scored only
  `11.62/20` before the AIDE profile was added.
- Early AIDE profile output pulled weak snippets from figure captions, related
  work, or baseline passages. The profile now uses tighter AIDE-specific
  keywords and target-section-first selection.
- Source-span validation caught a malformed validation bullet after
  `papertoskill_extract.py` split an indented `2. AutoGPT.` continuation into a
  separate bullet. The extractor now only treats unindented Markdown list
  markers as new bullets.

Evidence boundary:

- Phase 20 supports deterministic extracted-text-to-note scaffold evidence for
  two papers/profiles: Toolformer and AIDE.
- It does not prove reliable arbitrary-PDF automation, human semantic fidelity,
  live agent success, provider billing, or success-per-dollar.

Verification:

- `python -m unittest tests.test_papertoskill_extract tests.test_papertoskill_note_from_text -v`: passed, 7 tests OK.
- `python -m unittest tests.test_aggregate_results_tables tests.test_check_reproducibility_package -v`: passed, 3 tests OK.

## 2026-06-18 Phase 21

Actions:

- Downloaded the official AAAI-27 author kit from `https://aaai.org/authorkit27/`.
- Extracted the template under `paper/aaai/AuthorKit27/` and recorded
  provenance in `paper/aaai/README.md`.
- Added `paper/aaai/papertoskill_aaai2027.tex`,
  `paper/aaai/papertoskill_tables.tex`, and
  `paper/aaai/papertoskill_refs.bib`.
- Added usage examples under `examples/usage/` for Codex-style skill use,
  auto-note-to-skill conversion, and Claude/GPT-family/DeepSeek model
  ablations.
- Added `benchmarks/model_ablation_v0.json` and
  `scripts/build_model_ablation_prompts.py`.
- Generated six model-ablation prompt packets under
  `results/model_ablation_prompts/v0/`.
- Extended the reproducibility checker to include AAAI package files, usage
  examples, model-ablation prompt packets, model slots, and pending response
  files.

Results:

- AAAI author kit SHA256:
  `E28C6AC9BC6EB3B4E2D849547D2CEFB5162610EE39D0A12E0DC62D1126B44A7D`.
- Model slots:
  - `claude_opus_4_8`, using `claude-opus-4-8` if still advertised;
  - `gpt_5_5_or_gpt_family`, requiring live alias verification;
  - `deepseek_followup_slot`, reserved for the user's later DeepSeek addition.
- Prompt grid covers two context cases:
  Toolformer curated-skill usage and AIDE auto-note-derived skill usage.

Evidence boundary:

- The AAAI package is prepared but not submission-final.
- Usage examples and model-ablation prompts are execution protocols, not
  completed live results.
- GPT 5.5 remains a requested GPT-family alias until verified at `/v1/models`.
- DeepSeek remains a follow-up slot.

## 2026-06-18 Phase 22

Actions:

- Added `scripts/run_model_ablation_prompts.py`, a live runner for the prepared
  model-ablation prompt index.
- Added `scripts/evaluate_model_ablation_responses.py`, a scorer for saved
  model response files.
- Added `tests/test_model_ablation_execution.py`.
- Ran a baseline response evaluation over the current prompt index.
- Attempted live Claude Opus 4.8 and GPT-family rows using the provided
  OpenAI-compatible endpoint through environment variables.
- Extended the reproducibility checker to include the model-ablation runner,
  evaluator, run report, evaluation report, and completion gate.

Results:

- Baseline response evaluation:
  - total rows: `6`
  - scored rows: `0`
  - pending rows: `6`
- Live attempt:
  - overall status: `blocked_by_provider_or_model_availability`
  - Claude Opus 4.8 rows: `2` errors
  - GPT-family rows: `2` skipped
  - successful response files: `0`
- `/v1/models` succeeded and listed eight Claude-family model IDs including
  `claude-opus-4-8`.
- Both Claude prompt calls selected `claude-opus-4-8` exactly but failed with
  HTTP `503`, `No available accounts: no available accounts`.
- The endpoint did not list `gpt-5.5` or any GPT-family fallback model, so the
  GPT-family rows were skipped as unavailable.
- The DeepSeek follow-up slot was intentionally not attempted.

Evidence boundary:

- Phase 22 records a live attempt and provider/model availability evidence.
- It does not complete Claude/GPT/DeepSeek model ablations because no response
  files were saved and no rows were scored.

## 2026-06-18 Phase 23

Actions:

- Re-ran the model-ablation runner against the provided endpoint for Claude
  Opus 4.8 and the GPT-family slot.
- Updated `scripts/run_model_ablation_prompts.py` so the DeepSeek slot is
  skipped only while its alias remains `deepseek-to-be-filled`.
- Added tests for placeholder-vs-configured DeepSeek slot behavior.
- Updated `examples/usage/model_ablation_usage.md` and `research/runbook.md`
  with runner/scorer commands and concrete DeepSeek follow-up steps.

Results:

- `/v1/models` still succeeded and listed eight Claude-family model IDs,
  including `claude-opus-4-8`.
- Both Claude rows again failed with HTTP `503`,
  `No available accounts: no available accounts`.
- The endpoint still did not list `gpt-5.5` or any GPT-family fallback model.
- No response files were saved; response evaluation remains pending.
- DeepSeek follow-up is mechanically ready: once the placeholder alias is
  replaced with a concrete model ID and environment variables are set, the
  runner will attempt it without requiring `--include-placeholder-models`.

Evidence boundary:

- Phase 23 improves execution readiness and records another availability check.
- It does not complete any model-quality ablation.

## 2026-06-18 Phase 24

Actions:

- Added `research/goal_completion_audit.md`.
- Audited the active user goal requirement by requirement against current
  repository evidence.
- Updated README, artifact map, memory, and reproducibility checks to expose the
  audit as a first-class project artifact.

Results:

- The audit finds that durable memory, phase-level GitHub saving,
  deterministic/offline PaperToSkill development, AAAI package preparation,
  usage examples, failure-branch provenance, and local reproducibility readiness
  are satisfied for the current scoped artifact package.
- The audit also finds that the full active goal should not be marked complete:
  live Claude/GPT-family model responses remain blocked/unavailable, DeepSeek
  response collection is intentionally pending user configuration, human
  fidelity annotation is unscored, and provider-billing/success-per-dollar
  evidence is not collected.

Evidence boundary:

- Phase 24 is a completion audit and planning gate. It adds no new empirical
  model responses.

## 2026-06-18 Phase 25

Actions:

- Updated `scripts/evaluate_context_costs.py` so the Phase 12
  `ceil(characters / 4)` proxy remains available while local `tiktoken`
  tokenizer-aware outputs are generated when possible.
- Added `o200k_base` tokenizer-aware context-size and coverage-efficiency
  artifacts under `results/tables/`.
- Updated `tests/test_evaluate_context_costs.py` to verify tokenizer-aware
  outputs and the explicit tokenizer-skip path.
- Extended the reproducibility checker to require the tokenizer-aware Markdown
  and JSON reports.
- Updated the AAAI table, paper draft, claim checklist, limitations, README,
  artifact map, decision log, run log, and memory to distinguish local
  tokenizer-aware proxy evidence from provider billing.

Results:

- Under `o200k_base`, generated skills use:
  - AI Scientist-v2: `1,079` tokens vs `45,212` for full extracted paper text,
    a `97.61%` reduction.
  - Reflexion: `703` tokens vs `16,414`, a `95.72%` reduction.
  - AIDE: `1,285` tokens vs `13,312`, a `90.35%` reduction.
  - Toolformer: `1,255` tokens vs `20,365`, a `93.84%` reduction.
- The character proxy remains available as a sensitivity check in the original
  `context_cost_proxy.*` files.

Evidence boundary:

- Phase 25 supports local tokenizer-aware compactness and input-cost proxy
  claims.
- It does not support provider-specific prices, live invoices, output-token
  accounting, model-quality conclusions, or success-per-dollar claims.

## 2026-06-18 Phase 26

Actions:

- Reran `scripts/run_model_ablation_prompts.py` for `claude_opus_4_8` and
  `gpt_5_5_or_gpt_family` using the provided OpenAI-compatible endpoint through
  local environment variables.
- Reran `scripts/evaluate_model_ablation_responses.py` after the live attempt.
- Added `research/run_logs/2026-06-18_phase26_model_ablation_recheck.md`.
- Updated memory and artifact map with the latest provider/model availability
  state.

Results:

- `/v1/models` succeeded and listed eight Claude-family model IDs, including
  `claude-opus-4-8`.
- Both Claude rows selected `claude-opus-4-8` exactly but failed with HTTP
  `503`, `No available accounts: no available accounts`.
- The model catalog did not list `gpt-5.5` or any GPT-family fallback model, so
  both GPT-family rows were skipped as unavailable.
- No response files were saved.
- Response evaluation remains `6` total rows, `0` scored rows, and `6` pending
  rows.

Evidence boundary:

- Phase 26 is current provider/model availability evidence only.
- It does not complete Claude/GPT-family model-quality ablations, does not
  evaluate DeepSeek, and does not support negative model-quality conclusions.

## 2026-06-18 Phase 27

Actions:

- Added `scripts/check_aaai_package.py`, an automated gate for the local
  AAAI-27 paper package and generated build artifacts.
- Added `tests/test_check_aaai_package.py`.
- Generated `results/reproducibility/aaai_package_report.json` and
  `results/reproducibility/aaai_package_report.md`.
- Integrated the AAAI package report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, claim/evidence docs, result cards, goal audit, and memory to
  treat AAAI readiness as a local gate rather than only file presence.

Results:

- The AAAI package report is `ready` with 17 ready checks and 0 failed checks.
- The checker verifies required package files, the official author-kit SHA256,
  `aaai2027` declaration and log load marker, fresh PDF/log/BibTeX outputs, PDF
  output marker, and unresolved citation/reference/build-warning markers.
- The reproducibility package report now shows
  `ready_with_pending_external_evidence`, 140 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 27 supports local AAAI package/build-artifact readiness.
- It does not make the manuscript submission-final, accepted, or empirically
  stronger on live model, human-fidelity, or provider-billing claims.

## 2026-06-18 Phase 28

Actions:

- Added `scripts/check_usage_examples.py`, a local gate for paper-facing usage
  examples.
- Added `tests/test_check_usage_examples.py`.
- Generated `results/reproducibility/usage_example_report.json` and
  `results/reproducibility/usage_example_report.md`.
- Integrated the usage-example report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, claim/evidence docs, result cards, goal audit, and memory.

Results:

- The usage-example report is `ready` with 34 ready checks and 0 failed checks.
- The checker validates usage-example files, Codex-style Toolformer skill
  inputs, model-ablation prompt grid/model slots/response slots, and an offline
  AIDE extracted-text-to-note-to-skill chain.
- The offline example chain selected 6 method windows, 6 experiment windows,
  and 5 limitation windows, then produced a temporary generated skill scoring
  20/20 on the AIDE rubric.
- The reproducibility package report now shows
  `ready_with_pending_external_evidence`, 147 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 28 supports local usage-example executability and prompt-slot
  readiness.
- It does not complete live Claude/GPT/DeepSeek model ablations, live
  cross-harness success, human usability validation, or provider billing.

## 2026-06-18 Phase 29

Actions:

- Added `scripts/check_paper_tables.py`, a consistency gate for the AAAI result
  tables.
- Added `tests/test_check_paper_tables.py`.
- Generated `results/reproducibility/paper_table_report.json` and
  `results/reproducibility/paper_table_report.md`.
- Integrated the paper-table report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, artifact map, decision log, result cards, goal audit, and
  memory.

Results:

- The paper-table report is `ready` with 76 ready checks and 0 failed checks.
- The checker parses `paper/aaai/papertoskill_tables.tex` and compares it
  against generated CSV sources for main results, transfer ablation,
  tokenizer-aware cost proxy, and auto-note comparison.
- The reproducibility package report now shows
  `ready_with_pending_external_evidence`, 153 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 29 prevents AAAI manuscript-table drift.
- It does not add new empirical evidence and does not complete pending live
  model, human-fidelity, or provider-billing evidence.

## 2026-06-18 Phase 30

Actions:

- Reran the model-ablation live runner for `claude_opus_4_8` and
  `gpt_5_5_or_gpt_family` against the provided endpoint.
- Added `scripts/check_paper_claims.py`, a local claim-discipline gate for the
  AAAI manuscript and Markdown draft.
- Added `tests/test_check_paper_claims.py`.
- Generated `results/reproducibility/paper_claim_report.json` and
  `results/reproducibility/paper_claim_report.md`.
- Integrated the claim report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, artifact map, decision log, result cards, stage log, run
  log, goal audit, and memory.

Results:

- Endpoint recheck still shows `claude-opus-4-8` in `/v1/models`, but both
  Claude rows fail with HTTP 503, `No available accounts: no available
  accounts`.
- The same catalog still does not list `gpt-5.5` or a GPT-family fallback
  model, so GPT-family rows remain skipped.
- The paper-claim report is `ready` with 20 ready checks and 0 failed checks.
- The reproducibility package report now shows
  `ready_with_pending_external_evidence`, 159 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 30 records another provider/model availability recheck and prevents
  unsupported paper overclaims.
- It does not complete live Claude/GPT/DeepSeek model ablations, live
  cross-harness transfer, human-fidelity annotation, or provider-billing
  evidence.

## 2026-06-18 Phase 31

Actions:

- Added `scripts/check_goal_completion.py`, a machine-checkable audit for the
  active user goal.
- Added `tests/test_check_goal_completion.py`.
- Generated `results/reproducibility/goal_completion_report.json` and
  `results/reproducibility/goal_completion_report.md`.
- Integrated the goal-completion report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, artifact map, decision log, result cards, stage log, goal
  audit, and memory.

Results:

- Goal-completion report status:
  `not_complete_pending_external_evidence`.
- Goal-completion report counts: 34 ready checks, 10 pending checks, and 0
  failed checks.
- The report keeps `active_goal_complete` pending and exposes the remaining
  requirements: AI-Scientist-v2 live LLM run, provider billing/success-per-
  dollar evidence, final AAAI submission readiness, Claude/GPT-family saved and
  scored ablation responses, DeepSeek responses after user configuration, full
  model-ablation evaluation, live cross-harness responses, and human-fidelity
  annotation.
- The reproducibility package report now shows
  `ready_with_pending_external_evidence`, 164 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 31 makes the active-goal completion decision auditable and
  machine-readable.
- It does not add live model responses, human annotations, provider-billing
  evidence, or submission-final paper evidence.

## 2026-06-18 Phase 32

Actions:

- Compacted long-term and short-term memory into shorter action-oriented files
  that preserve stable project facts, fix history, current blockers, and next
  actions.
- Updated `benchmarks/model_ablation_v0.json` so the Claude slot records
  candidates `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- Updated the GPT-family slot to use separate `PAPERTOSKILL_GPT_OPENAI_*`
  environment variables and candidates `gpt-5.5` and `gpt-5.4`.
- Updated prompt builder and runner behavior so prompt packets include alias
  candidates and run reports preserve model catalogs per credential profile,
  even when profiles share the same base URL.
- Reran the Claude/GPT-family model-ablation live runner and response
  evaluator.

Results:

- Claude catalog via `AI_SCIENTIST_OPENAI_API_KEY` lists 8 Claude-family models,
  including `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`.
- Claude prompt rows selected `claude-opus-4-8` and both failed HTTP 503:
  `No available accounts: no available accounts`.
- GPT catalog via `PAPERTOSKILL_GPT_OPENAI_API_KEY` lists 17 models, including
  `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, GPT 5.2 variants, and GPT 5.3 Codex
  variants.
- GPT prompt rows selected `gpt-5.5` and both failed HTTP 502:
  `Upstream access forbidden, please contact administrator`.
- Response evaluation remains 6 total rows, 0 scored rows, and 6 pending rows.

Evidence boundary:

- Phase 32 improves model-profile accuracy and records a fresh availability
  attempt with the user's updated credentials.
- It does not complete model-quality ablations because no response files were
  saved or scored.

## 2026-06-19 Phase 33

Actions:

- Updated `scripts/run_model_ablation_prompts.py` so live runs retry later
  candidate aliases when an advertised first-choice alias fails at
  chat-completion time.
- Added `tests/test_model_ablation_execution.py` coverage for successful
  fallback from a failed first Claude alias to a later Claude alias.
- Reran the Claude/GPT-family model-ablation live runner and response
  evaluator.
- Updated `scripts/check_goal_completion.py` so "ablation attempted" is based
  on provider/model attempt evidence, while saved-and-scored responses remain
  the separate completion requirement.

Results:

- Claude catalog via `AI_SCIENTIST_OPENAI_API_KEY` lists 8 Claude-family models.
- The runner tried `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6` for both Claude prompt rows; all failed HTTP 503:
  `No available accounts`.
- GPT catalog via `PAPERTOSKILL_GPT_OPENAI_API_KEY` lists 17 models.
- The runner tried `gpt-5.5` and `gpt-5.4` for both GPT prompt rows; both
  failed HTTP 502: `Upstream access forbidden`.
- Response evaluation remains 6 total rows, 0 scored rows, and 6 pending rows.

Evidence boundary:

- Phase 33 strengthens the live-run protocol and current provider-availability
  evidence.
- It does not complete model-quality ablations because no response files were
  saved or scored.

## 2026-06-19 Phase 34

Actions:

- Added `scripts/papertoskill_pipeline.py`, a local one-command pipeline from
  extracted text to auto-note scaffold, generated skill, source map, rubric
  evaluation, and manifest.
- Added `tests/test_papertoskill_pipeline.py`.
- Updated the auto-note usage example and runbook with the one-command path.
- Updated `scripts/check_usage_examples.py` so the usage gate runs a temporary
  AIDE pipeline example.

Results:

- The temporary AIDE pipeline example creates a manifest and scores 20/20 on
  `benchmarks/rubric_aide_v0.json`.
- Usage-example report status remains `ready`, now with 39 ready checks and 0
  failed checks.

Evidence boundary:

- Phase 34 improves the local user-facing conversion workflow.
- It does not prove human semantic fidelity, live harness success, or reliable
  arbitrary-PDF automation.

## 2026-06-19 Phase 35

Actions:

- Extended `scripts/papertoskill_pipeline.py` so the local pipeline accepts a
  `.pdf` source when `pdftotext -layout` is available.
- Added manifest source metadata for PDF runs: original source, generated text
  source, and text extractor.
- Added PDF-source coverage to `tests/test_papertoskill_pipeline.py` using the
  local AAAI PDF package when available.
- Updated `scripts/check_usage_examples.py` so the usage gate runs a temporary
  PDF pipeline smoke example and checks manifest/text-extraction evidence.
- Updated the auto-note usage example, runbook, artifact map, claim boundary
  docs, result cards, and memory.

Results:

- The PDF smoke path extracts text from
  `paper/aaai/papertoskill_aaai2027.pdf`, records `pdftotext -layout` in the
  manifest, and creates the expected pipeline artifacts.
- Usage-example report status remains `ready`, now with 42 ready checks and 0
  failed checks.
- The full unittest suite now has 47 tests.

Evidence boundary:

- Phase 35 supports local direct-PDF pipeline smoke execution only. It does not
  prove reliable arbitrary-PDF automation, human semantic fidelity, live
  harness success, provider billing, or completed model ablations.

## 2026-06-19 Phase 36

Actions:

- Reran `scripts/run_model_ablation_prompts.py` for `claude_opus_4_8` and
  `gpt_5_5_or_gpt_family` with shell-only environment variables.
- Reran `scripts/evaluate_model_ablation_responses.py` over the prompt index.
- Added a Phase 36 run log and updated package/goal checks, claim boundaries,
  result cards, goal audit, and memory.

Results:

- Claude catalog succeeded and listed 14 Claude-family models.
- Both Claude Opus 4.8 prompt rows completed with HTTP 200 and saved response
  files under `results/model_ablation_prompts/v0/responses/`.
- The saved-response evaluator scored both Claude rows 6/6, producing
  2 scored rows, 4 pending rows, and average normalized score 1.0 over scored
  rows.
- GPT catalog still lists `gpt-5.5` and `gpt-5.4`, but both aliases still fail
  chat completion with HTTP 502 `Upstream access forbidden`.
- DeepSeek remains pending user configuration.

Evidence boundary:

- Phase 36 completes the Claude Opus 4.8 portion of the prepared model
  ablation. It does not complete the GPT-family ablation, DeepSeek follow-up,
  live cross-harness execution, human fidelity annotation, provider billing, or
  success-per-dollar evidence.

## 2026-06-19 Phase 37

Actions:

- Reran `scripts/run_model_ablation_prompts.py` for
  `gpt_5_5_or_gpt_family` only, using the separate GPT credential profile via
  shell-only environment variables.
- Wrote the retry report to
  `results/model_ablation_prompts/v0/gpt_retry_run_report.json` and `.md`.
- Reran `scripts/evaluate_model_ablation_responses.py` over the full prompt
  index.
- Updated paper-facing claim boundaries, result cards, runbook, goal audit,
  and memory.

Results:

- GPT catalog succeeded and listed 17 models, including `gpt-5.5`, `gpt-5.4`,
  `gpt-5.4-mini`, GPT 5.2 variants, and GPT 5.3 Codex variants.
- `toolformer_curated_skill_usage`: `gpt-5.5` timed out, then `gpt-5.4`
  succeeded with HTTP 200 and saved a response file.
- `aide_auto_skill_usage`: `gpt-5.5` succeeded with HTTP 200 and saved a
  response file.
- The saved-response evaluator now reports 6 total rows, 4 scored rows,
  2 pending rows, and average normalized score 1.0 over scored rows.
- Both GPT-family rows score 6/6 under the deterministic response rubric.
- DeepSeek remains pending user configuration.

Evidence boundary:

- Phase 37 completes the GPT-family portion of the current two-case model
  ablation protocol. It should be described as GPT-family evidence, not pure
  `gpt-5.5` evidence, because one row used `gpt-5.4` after a `gpt-5.5`
  timeout. It does not complete DeepSeek, live cross-harness execution, human
  fidelity annotation, provider billing, output-token accounting, or
  success-per-dollar evidence.

## 2026-06-19 Phase 38

Actions:

- Added `scripts/evaluate_model_response_costs.py` to estimate local
  output-token proxies over saved model-ablation response files.
- Added `tests/test_evaluate_model_response_costs.py`.
- Generated `results/tables/model_response_cost_proxy.md`, `.csv`, and
  `.json`.
- Integrated the new report into the reproducibility package and active-goal
  completion gates.
- Updated paper-facing text, claim boundaries, runbook, artifact map, result
  cards, goal audit, and memory to distinguish local output-token proxy
  evidence from provider billing.

Results:

- The report covers 6 model-ablation prompt rows: 4 measured saved
  Claude/GPT-family responses and 2 pending DeepSeek rows.
- Character proxy output tokens total 9,420 across measured rows.
- Local `o200k_base` output tokens total 8,710 across measured rows:
  - Claude Toolformer: 2,272.
  - Claude AIDE: 2,108.
  - GPT-family Toolformer: 1,447.
  - GPT-family AIDE: 2,883.

Evidence boundary:

- Phase 38 supports local saved-response output-token proxy accounting.
- It does not support provider billing, live invoices, realized output-token
  bills, success-per-dollar evidence, DeepSeek completion, live cross-harness
  execution, or human-fidelity annotation.

## 2026-06-19 Phase 39

Actions:

- Added `scripts/run_live_transfer_prompts.py`, a live runner for existing
  Codex-style and Claude-style live-transfer prompt packets.
- Added `scripts/evaluate_live_transfer_responses.py`, a saved-response scorer
  for live-transfer outputs.
- Added `tests/test_live_transfer_execution.py`.
- Ran the Toolformer live-transfer packet with the Claude-family endpoint using
  shell-only credentials.
- Saved six Toolformer response files under
  `results/live_transfer_prompts/toolformer_v0/responses/`.
- Generated `results/live_transfer_prompts/toolformer_v0/run_report.json` and
  `.md`.
- Reran the aggregate live-transfer response evaluator across AI Scientist-v2,
  Reflexion, AIDE, and Toolformer.
- Integrated live-transfer infrastructure and Toolformer response evidence into
  the reproducibility package, usage-example, and active-goal gates.
- Updated runbook, artifact map, result cards, goal audit, claim checklist,
  paper draft, AAAI TeX draft, limitations, README, and memory.

Results:

- The Toolformer run report is `overall_status=complete` with 6 successes, 0
  errors, 0 skipped rows, catalog status `success`, 14 listed models, and exact
  alias `claude-opus-4-8`.
- The aggregate live-transfer evaluation reports 24 total rows, 6 scored rows,
  18 pending rows, and 1.0 average normalized score over scored rows.
- All six Toolformer rows score 9/9.
- AI Scientist-v2, Reflexion, and AIDE live-transfer response sets remain
  pending.
- Usage-example report now shows `ready`, 47 ready checks, and 0 failed checks.
- Reproducibility package report now shows
  `ready_with_pending_external_evidence`, 191 ready checks, 7 pending checks,
  and 0 failed checks.
- Goal-completion report now shows
  `not_complete_pending_external_evidence`, 44 ready checks, 8 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 39 completes only the Toolformer live-transfer response set for the
  current prompt protocol.
- It does not complete the remaining live-transfer response sets, DeepSeek,
  human-fidelity annotation, provider billing, live invoices, realized
  success-per-dollar evidence, or final AAAI submission readiness.

## 2026-06-19 Phase 40

Actions:

- Ran the remaining AI Scientist-v2, Reflexion, and AIDE live-transfer prompt
  packets with the Claude-family endpoint using shell-only credentials.
- Saved six response files for each paper under
  `results/live_transfer_prompts/<paper>_v0/responses/`.
- Generated per-paper run reports for AI Scientist-v2, Reflexion, and AIDE.
- Reran the aggregate live-transfer saved-response evaluator across all four
  paper packets.
- Updated package and goal gates to check all four live-transfer run reports
  and all four scored saved-response sets.

Results:

- AI Scientist-v2: run report `overall_status=complete`, 6 successes, 0 errors,
  and all rows used `claude-opus-4-8`.
- Reflexion: run report `overall_status=complete`, 6 successes, 0 errors, and
  all rows used `claude-opus-4-8`.
- AIDE: run report `overall_status=complete`, 6 successes, 0 errors. The first
  row fell back from `claude-opus-4-8` after a remote connection closure to
  `claude-opus-4-7`; the remaining rows used `claude-opus-4-8`.
- Aggregate live-transfer evaluation now reports 24 total rows, 24 scored rows,
  0 pending rows, and 1.0 average normalized score.
- AI Scientist-v2, Reflexion, and AIDE rows score 11/11 each; Toolformer rows
  remain 9/9 each.

Evidence boundary:

- Phase 40 completes saved live-transfer response coverage for the current
  prompt-packet protocol.
- It does not establish human semantic fidelity, real live task success,
  DeepSeek completion, provider billing, success-per-dollar evidence, or final
  AAAI submission readiness.

## 2026-06-19 Phase 41

Actions:

- Added `scripts/run_ai_scientist_v2_smoke.py`, a bounded AI-Scientist-v2
  LLM-client smoke runner that imports the local `ai_scientist.llm` client and
  asks for a tiny marker-contract response.
- Added `tests/test_run_ai_scientist_v2_smoke.py` for successful response
  contracts and redacted provider-error reports.
- Ran the smoke check with shell-only Claude-family credentials.
- Generated `results/ai_scientist_v2_smoke/run_report.json` and `.md`.
- Integrated the smoke runner/report into the active-goal and reproducibility
  package gates.

Results:

- The smoke attempt reached the provider but returned HTTP 403 with message
  `All available accounts exhausted`.
- The smoke report is
  `overall_status=blocked_by_provider_or_model_availability`, with 1 ready
  check, 2 pending checks, and 0 failed checks.
- No `results/ai_scientist_v2_smoke/response.md` was created because the
  provider did not return a chat-completion response.
- The goal-completion report now shows 51 ready checks, 8 pending checks, and
  0 failed checks. It marks `ai_scientist_v2_live_llm_smoke_attempted` ready,
  but `ai_scientist_v2_live_llm_smoke_complete` and the full
  `ai_scientist_v2_live_llm_run_complete` pending.
- The reproducibility package report now shows 212 ready checks, 6 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 41 records provider-availability evidence for a bounded
  AI-Scientist-v2 LLM-client smoke check.
- It does not complete BFTS, prove research-task success, establish human
  semantic fidelity, complete DeepSeek, collect provider billing, or make the
  AAAI package submission-final.

## 2026-06-19 Phase 42

Actions:

- Added completion requirements to `benchmarks/human_fidelity_review_v0.json`.
- Updated `scripts/build_human_fidelity_packets.py` so packets include a
  completion-requirements section and the annotation template includes
  reviewer handoff metadata: `packet_path`, `evidence_locator`,
  `confidence_0_to_1`, and `needs_discussion`.
- Added `results/human_fidelity_packets/annotation_guide.md`.
- Updated `scripts/summarize_human_fidelity_annotations.py` to validate scored
  rows for evidence locator, evidence note, confidence, reviewer, review date,
  and discussion flags.
- Added package-gate coverage for `human_fidelity_annotation_handoff_ready`.

Results:

- The human-fidelity annotation handoff is ready with 24 expected annotation
  rows, 24 template rows, and 24 summary rows.
- The annotation summary remains `annotation_status=pending`, with 0 scored
  rows, 24 pending rows, average confidence `n/a`, and 0 validation errors.
- The reproducibility package report now shows 214 ready checks, 6 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 42 improves independent-review readiness only.
- It does not complete human semantic validation, create expert scores, resolve
  DeepSeek, prove live task success, collect provider billing, or make the AAAI
  package submission-final.

## 2026-06-19 Phase 43

Actions:

- Added `benchmarks/provider_billing_evidence_v0.json` with six evidence slots
  for Claude-family model ablation, GPT-family model ablation, DeepSeek
  follow-up, live transfer, AI-Scientist-v2 live-run billing, and context
  comparison billing.
- Added `scripts/summarize_provider_billing_evidence.py` and
  `tests/test_summarize_provider_billing_evidence.py`.
- Generated `results/provider_billing_evidence/billing_template.csv` and
  `billing_summary.{json,md}`.
- Added provider-billing handoff checks to
  `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py`.
- Updated the paper draft, AAAI TeX, limitations, claim checklist, result
  cards, runbook, artifact map, memory, and completion audit to state the
  billing evidence boundary.

Results:

- The provider-billing handoff is ready with 6 template rows, 6 summary rows,
  0 validation errors, and `billing_status=pending`.
- All 6 billing rows remain pending; there are 0 measured provider bills and
  no success-per-dollar value.
- The goal-completion report shows 53 ready checks, 8 pending checks, and
  0 failed checks.
- The reproducibility package report shows 221 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 43 makes provider billing and success-per-dollar evidence collection
  executable.
- It does not collect live invoices, realized provider bills, DeepSeek
  responses, AI-Scientist-v2 live-run completion, human validation, or a real
  success-per-dollar result.

## 2026-06-19 Phase 44

Actions:

- Refreshed `research/review_report.md` and `research/rebuttal_bank.md` to
  match Phase 40-43 evidence.
- Added `research/submission_checklist.md`.
- Added `scripts/check_submission_review.py` and
  `tests/test_check_submission_review.py`.
- Generated `results/reproducibility/submission_review_report.{json,md}`.
- Added submission-review handoff checks to active-goal and reproducibility
  package gates.

Results:

- Submission-review handoff is ready with 15 ready checks and 0 failed checks.
- The handoff now reflects 24 scored saved live-transfer response rows, 4
  scored and 2 pending model-ablation rows, 0 scored and 24 pending
  human-fidelity rows, 0 measured and 6 pending provider-billing rows, and the
  AI-Scientist-v2 HTTP 403 provider blocker.
- Goal-completion report now shows 55 ready checks, 8 pending checks, and
  0 failed checks.
- Reproducibility package report now shows 227 ready checks, 7 pending checks,
  and 0 failed checks.

Evidence boundary:

- Phase 44 makes submission-review handoff freshness machine-checkable.
- It does not complete final AAAI submission, human validation, DeepSeek,
  provider billing, success-per-dollar evidence, AI-Scientist-v2 smoke
  completion, or a full AI-Scientist-v2 live run.

## 2026-06-19 Phase 45

Actions:

- Re-ran the bounded AI-Scientist-v2 LLM-client smoke with the configured
  OpenAI-compatible endpoint and shell-only credential.
- Updated `scripts/run_ai_scientist_v2_smoke.py` to print an explicit
  `overall_status` summary after writing reports.
- Added script-level `--timeout-seconds` handling so provider hangs produce a
  redacted blocked report instead of only an outer-shell timeout.
- Added `--require-complete` to the smoke runner for future checks that should
  fail unless the provider returns a response satisfying the smoke contract.
- Added regression coverage for smoke runner status summaries, timeout
  handling, and completion exit semantics.
- Added a reproducibility-package check that verifies the smoke runner exposes
  the status summary, timeout handling, and `--require-complete` mode.

Results:

- The recheck reached the provider through `ai_scientist.llm`.
- The provider did not return a smoke response within 15 seconds.
- No `results/ai_scientist_v2_smoke/response.md` file was created.
- The AI-Scientist-v2 smoke report remains
  `blocked_by_provider_or_model_availability`, with 1 ready check, 2 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 45 records a fresh provider-blocked smoke recheck and improves command
  clarity.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live research
  task success, resolve DeepSeek, collect human annotations, collect provider
  billing, or make the AAAI package submission-final.

## 2026-06-19 Phase 46

Actions:

- Updated `scripts/run_ai_scientist_v2_smoke.py` so bounded smoke checks can
  try repeatable `--model-alias` values in order and record `attempted_models`
  in JSON/Markdown reports.
- Added smoke-runner tests for alias fallback succeeding after an earlier alias
  fails.
- Updated reproducibility and submission-review gates so the current
  AI-Scientist-v2 smoke evidence is aligned to multi-alias attempts rather than
  a single stale blocker string.
- Reran the bounded AI-Scientist-v2 smoke with shell-only credentials and four
  Claude aliases: `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6`.
- Added `research/run_logs/2026-06-19_phase46_ai_scientist_v2_smoke_alias_fallback.md`.

Results:

- All four Claude aliases timed out after 15 seconds waiting for provider
  response.
- `results/ai_scientist_v2_smoke/run_report.md` reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- No `results/ai_scientist_v2_smoke/response.md` file was created.

Evidence boundary:

- Phase 46 strengthens provider/model availability evidence for the bounded
  AI-Scientist-v2 LLM-client smoke path.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live research
  task success, resolve DeepSeek, collect human annotations, collect provider
  billing, or make the AAAI package submission-final.

## 2026-06-19 Phase 48

Actions:

- Re-ran the bounded AI-Scientist-v2 LLM-client smoke with shell-only
  credentials, four Claude aliases, and `--timeout-seconds 30`.
- Added
  `research/run_logs/2026-06-19_phase48_ai_scientist_v2_smoke_provider_recheck.md`.
- Updated review, checklist, runbook, memory, result-card, and freshness-gate
  references to the latest smoke blocker details.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8` returned HTTP 403 `All available accounts exhausted`.
- `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` each timed out
  after 30 seconds waiting for provider response.
- No `results/ai_scientist_v2_smoke/response.md` file was created.

Evidence boundary:

- Phase 48 refreshes provider/model availability evidence for the bounded
  AI-Scientist-v2 LLM-client smoke path.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live research
  task success, resolve DeepSeek, collect human annotations, collect provider
  billing, or make the AAAI package submission-final.

## 2026-06-19 Phase 49

Actions:

- Added `scripts/check_ai_scientist_v2_live_run_handoff.py`, a no-network
  local handoff/preflight report for the pending full AI-Scientist-v2
  live/BFTS run.
- Generated
  `results/ai_scientist_v2_live_run_handoff/handoff.{json,md}`.
- Integrated the handoff into the active-goal and reproducibility package
  gates.
- Updated runbook, artifact map, submission-review materials, memory, and
  result cards so the full live-run path is tracked by local evidence instead
  of memory-only text.
- Added
  `research/run_logs/2026-06-19_phase49_ai_scientist_v2_live_run_handoff.md`.

Results:

- `results/ai_scientist_v2_live_run_handoff/handoff.md` reports
  `overall_status=blocked_by_provider_smoke`, with 10 ready checks, 2 pending
  checks, and 0 failed checks.
- Ready checks cover the AI-Scientist-v2 root, launcher, dry-run/skip flags,
  laptop-profile config, PaperToSkill seed idea, prior dry-run artifacts,
  environment variable names, and next full-run command.
- Pending checks cover provider-smoke completion and full-run completion
  artifacts.
- The active-goal report now shows 61 ready checks, 8 pending checks, and 0
  failed checks.
- The reproducibility package report now shows 243 ready checks, 8 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 49 makes the full AI-Scientist-v2 live-run path locally
  machine-checkable.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, call an LLM, prove
  live research-task success, resolve DeepSeek, collect human annotations,
  collect provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 50

Actions:

- Re-ran the bounded AI-Scientist-v2 LLM-client smoke with shell-only
  credentials, four Claude aliases, and `--timeout-seconds 30`.
- Added
  `research/run_logs/2026-06-20_phase50_ai_scientist_v2_smoke_timeout_recheck.md`.
- Updated current-status evidence summaries to distinguish this latest timeout
  recheck from earlier historical HTTP 403 evidence.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file was created.

Evidence boundary:

- Phase 50 refreshes provider/model availability evidence for the bounded
  AI-Scientist-v2 LLM-client smoke path.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 51

Actions:

- Added `scripts/check_external_evidence_closure.py`.
- Added `tests/test_check_external_evidence_closure.py`.
- Generated `results/external_evidence_closure/closure.md` and
  `results/external_evidence_closure/closure.json`.
- Integrated the closure queue into the active-goal and reproducibility package
  gates.
- Added
  `research/run_logs/2026-06-20_phase51_external_evidence_closure_queue.md`.

Results:

- `results/external_evidence_closure/closure.md` reports
  `overall_status=pending_external_evidence`, with 3 ready checks, 0 pending
  checks, and 0 failed checks.
- The queue maps pending goal requirements to six next-action items:
  AI-Scientist-v2 smoke completion, AI-Scientist-v2 full live/BFTS run,
  DeepSeek response collection/model-ablation completion, human-fidelity
  annotation, provider billing/success-per-dollar evidence, and the AAAI
  submission decision.

Evidence boundary:

- Phase 51 makes the remaining external-evidence closure path local and
  auditable.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 52

Actions:

- Re-ran the bounded AI-Scientist-v2 LLM-client smoke with shell-only
  credentials, four Claude aliases, and `--timeout-seconds 30`.
- Added
  `research/run_logs/2026-06-20_phase52_ai_scientist_v2_smoke_retry.md`.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file was created.

Evidence boundary:

- Phase 52 refreshes provider/model availability evidence for the bounded
  AI-Scientist-v2 LLM-client smoke path.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 53

Actions:

- Added `scripts/check_external_evidence_packets.py`.
- Added `tests/test_check_external_evidence_packets.py`.
- Generated `results/external_evidence_packets/packets.md` and
  `results/external_evidence_packets/packets.json`.
- Integrated the execution packet report into the active-goal and
  reproducibility package gates.
- Added
  `research/run_logs/2026-06-20_phase53_external_evidence_packets.md`.

Results:

- `results/external_evidence_packets/packets.md` reports
  `overall_status=ready`, with 7 ready checks, 0 pending checks, and 0 failed
  checks.
- The six packets cover AI-Scientist-v2 smoke completion, AI-Scientist-v2 full
  live/BFTS run, DeepSeek response collection/model-ablation completion,
  human-fidelity annotation, provider billing/success-per-dollar evidence, and
  the AAAI submission decision.
- The active-goal report now shows 67 ready checks, 8 pending checks, and 0
  failed checks.
- The reproducibility package report now shows 259 ready checks, 8 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 53 makes each closure item runnable as a local handoff packet with
  inputs, setup notes, commands, validation commands, completion criteria,
  escalation rules, and evidence boundaries.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 54

Actions:

- Executed the Phase 53 AI-Scientist-v2 smoke-completion packet with
  shell-only credentials, four Claude aliases, `--timeout-seconds 30`, and
  `--require-complete`.
- Regenerated the external-evidence closure queue, execution packets,
  AI-Scientist-v2 live-run handoff, and active-goal report after the smoke
  retry.
- Added
  `research/run_logs/2026-06-20_phase54_ai_scientist_v2_smoke_packet_retry.md`.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- Because the smoke report is not complete, the full AI-Scientist-v2 live/BFTS
  run remains blocked by provider smoke.
- The reproducibility package report now shows 260 ready checks, 8 pending
  checks, and 0 failed checks after adding the Phase 54 run log to the package
  gate.

Evidence boundary:

- Phase 54 refreshes provider/model availability evidence for the bounded
  AI-Scientist-v2 LLM-client smoke path using the execution-packet command.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 55

Actions:

- Added `scripts/check_aaai_submission_decision.py`, a local AAAI
  submission-decision preflight.
- Added `tests/test_check_aaai_submission_decision.py`.
- Generated `results/aaai_submission_decision/decision.md` and
  `results/aaai_submission_decision/decision.json`.
- Integrated the preflight into `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py`.
- Updated the runbook, artifact map, result cards, submission-review handoff
  files, goal audit, and memory references.
- Added
  `research/run_logs/2026-06-20_phase55_aaai_submission_decision_preflight.md`.

Results:

- `results/aaai_submission_decision/decision.md` reports
  `overall_status=pending_human_decision`, with 25 ready checks, 1 pending
  check, and 0 failed checks.
- Both decision options are available for a human decision:
  `submit_now_deterministic_offline` and `wait_for_external_evidence`.
- No option is selected by the preflight.
- The active-goal report now shows 70 ready checks, 8 pending checks, and 0
  failed checks.
- The reproducibility package report now shows 267 ready checks, 8 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 55 makes the final AAAI decision auditable and machine-checkable.
- It does not submit the paper, select a claim scope, complete DeepSeek,
  complete AI-Scientist-v2 smoke or full live/BFTS evidence, collect human
  annotations, collect provider billing, or make the AAAI package
  submission-final.

## 2026-06-20 Phase 56

Actions:

- Confirmed GitHub connectivity recovered and pushed Phase 55 commits to
  `origin/main`.
- Re-ran the bounded AI-Scientist-v2 LLM-client smoke with shell-only
  credentials, four Claude aliases, `--timeout-seconds 30`, and
  `--require-complete`.
- Added
  `research/run_logs/2026-06-20_phase56_ai_scientist_v2_smoke_after_push_recovery.md`.

Results:

- `git push origin main` succeeded, moving `origin/main` from `d8639bc` to
  `3183ffe`.
- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 5 ready
  checks, 2 pending checks, and 0 failed checks.
- `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6` each timed out after 30 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

Evidence boundary:

- Phase 56 refreshes provider/model availability evidence after remote push
  recovery.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 57

Actions:

- Re-ran the bounded AI-Scientist-v2 LLM-client smoke using the GPT-family
  credential profile mapped into `AI_SCIENTIST_OPENAI_API_KEY`, with
  `--timeout-seconds 60`, `--require-complete`, and aliases `gpt-5.5` then
  `gpt-5.4`.
- Updated the external-evidence closure queue and execution-packet generators
  so the AI-Scientist-v2 smoke handoff now lists both Claude-family and
  GPT-family retry commands.
- Updated review, rebuttal, checklist, runbook, result-card, goal-audit,
  README, and memory wording to reflect the latest GPT-family smoke attempt.
- Added
  `research/run_logs/2026-06-20_phase57_ai_scientist_v2_gpt_smoke_retry.md`.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` still reports
  `overall_status=blocked_by_provider_or_model_availability`, with 3 ready
  checks, 2 pending checks, and 0 failed checks.
- `gpt-5.5` and `gpt-5.4` both timed out after 60 seconds waiting for provider
  response.
- No `results/ai_scientist_v2_smoke/response.md` file exists.
- The full AI-Scientist-v2 live/BFTS run remains blocked by smoke/provider
  availability and missing completion artifacts.

Evidence boundary:

- Phase 57 confirms that the AI-Scientist-v2 OpenAI-compatible client path can
  be exercised with the GPT-family credential profile, but the provider did not
  return a smoke response.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 58

Actions:

- Added `--max-tokens` to `scripts/run_ai_scientist_v2_smoke.py`, allowing the
  bounded smoke call to temporarily cap `ai_scientist.llm.MAX_NUM_TOKENS` and
  restore the previous value afterward.
- Added test coverage for the temporary token cap and restoration behavior.
- Retried the bounded AI-Scientist-v2 LLM-client smoke with `--max-tokens 128`
  for GPT-family aliases and Claude-family aliases.
- Updated external-evidence closure and execution-packet commands so future
  smoke retries use the 128-token marker-contract probe.
- Added
  `research/run_logs/2026-06-20_phase58_ai_scientist_v2_max_token_smoke.md`.

Results:

- GPT-family capped retry: `gpt-5.5` and `gpt-5.4` both timed out after 45
  seconds waiting for provider response.
- Claude-family capped retry: `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` all timed out after 30 seconds
  waiting for provider response.
- The latest `results/ai_scientist_v2_smoke/run_report.md` records the
  Claude-family capped retry, `max_tokens=128`,
  `overall_status=blocked_by_provider_or_model_availability`, 5 ready checks,
  2 pending checks, and 0 failed checks.
- No `results/ai_scientist_v2_smoke/response.md` file exists.

Evidence boundary:

- Phase 58 makes the smoke request smaller and more diagnostic, but the
  provider still did not return a marker-contract response.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 59

Actions:

- Added `scripts/run_openai_compatible_direct_probe.py`, a direct
  OpenAI-compatible `/chat/completions` marker-contract diagnostic that bypasses
  `ai_scientist.llm`.
- Added tests for direct-probe success, redacted errors, missing
  configuration, and alias fallback.
- Ran direct endpoint probes with shell-only Claude-family and GPT-family
  credentials.
- Added
  `research/run_logs/2026-06-20_phase59_openai_direct_probe.md`.
- Integrated the new diagnostic reports into the reproducibility package gate
  as provider-availability evidence only.

Results:

- Claude-family direct probe: `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 503
  `No available accounts: no available accounts`.
- GPT-family direct probe: `gpt-5.5` and `gpt-5.4` both returned HTTP 502
  `Upstream access forbidden, please contact administrator`.
- Both direct-probe reports are
  `blocked_by_provider_or_model_availability`; no direct-probe response files
  exist.

Evidence boundary:

- Phase 59 clarifies that the current provider blocker is visible outside the
  AI-Scientist-v2 wrapper.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 60

Actions:

- Confirmed Phase 59 commit `dc52b06 Add direct OpenAI-compatible provider
  probe` pushed successfully to `origin/main`.
- Re-ran the direct OpenAI-compatible provider probes for Claude-family and
  GPT-family credential profiles with the same tiny marker contract.
- Added
  `research/run_logs/2026-06-20_phase60_post_push_provider_recheck.md`.

Results:

- Claude-family direct probe still reports
  `blocked_by_provider_or_model_availability`: `claude-opus-4-8`,
  `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` all returned
  HTTP 503 `No available accounts: no available accounts`.
- GPT-family direct probe still reports
  `blocked_by_provider_or_model_availability`: `gpt-5.5` and `gpt-5.4` both
  returned HTTP 502 `Upstream access forbidden, please contact administrator`.
- No direct-probe response files exist for either profile.

Evidence boundary:

- Phase 60 confirms that the provider blocker persists after Phase 59 was
  saved to the remote repository.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 61

Actions:

- Updated `scripts/check_external_evidence_packets.py` so the
  `ai_scientist_v2_smoke_completion` packet runs direct OpenAI-compatible
  provider probes before AI-Scientist-v2 wrapper smoke commands.
- Added direct-probe inputs, completion criteria, and escalation wording to the
  smoke-completion packet.
- Expanded the packet secret scan to include closure-report content as well as
  generated packet content.
- Added regression tests in `tests/test_check_external_evidence_packets.py` for
  direct-probe-first ordering and alias coverage.
- Added
  `research/run_logs/2026-06-20_phase61_direct_probe_packet_preflight.md`.

Results:

- `results/external_evidence_packets/packets.md` now tells operators to run
  Claude-family and GPT-family direct endpoint probes before wrapper smoke.
- The packet says to keep wrapper smoke pending and escalate provider
  availability if direct probes remain blocked.
- Local packet, package, goal-completion, live-run handoff, and submission
  review checks pass.

Evidence boundary:

- Phase 61 improves the external-evidence handoff only.
- It does not complete the AI-Scientist-v2 smoke, run BFTS, prove live
  research-task success, resolve DeepSeek, collect human annotations, collect
  provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 62

Actions:

- Added `scripts/configure_deepseek_followup.py`, a no-secret helper for
  configuring `deepseek_followup_slot` with model alias and environment
  variable names.
- Added `tests/test_configure_deepseek_followup.py`.
- Updated `scripts/check_deepseek_followup.py` so the handoff report includes
  the configuration helper before prompt building, running, scoring, and
  rechecking.
- Updated `scripts/check_external_evidence_packets.py`,
  `examples/usage/model_ablation_usage.md`, `research/runbook.md`, and the
  usage/reproducibility gates to reference the helper.
- Added
  `research/run_logs/2026-06-20_phase62_deepseek_configuration_helper.md`.

Results:

- The DeepSeek handoff now tells users to run
  `scripts/configure_deepseek_followup.py` instead of manually editing JSON.
- The helper rejects raw API-key-like values and requires uppercase environment
  variable names for credential locations.
- The DeepSeek slot remains `pending_user_configuration` until the user supplies
  a concrete alias and local environment variables.

Evidence boundary:

- Phase 62 prepares DeepSeek configuration only.
- It does not call DeepSeek, save DeepSeek responses, complete model ablations,
  collect provider billing, or make the AAAI package submission-final.

## 2026-06-20 Phase 63

Actions:

- Retried pushing Phase 62 commit `0db90e2 Add DeepSeek followup configuration
  helper` to `origin/main`.
- Diagnosed GitHub connectivity after repeated push failures.
- Added a phase-save and push-recovery section to `research/runbook.md`.
- Added
  `research/run_logs/2026-06-20_phase63_push_connectivity_diagnostic.md`.

Results:

- Local branch remains `main...origin/main [ahead 1]`.
- `git push origin main` failed with `Recv failure: Connection was reset`.
- `git ls-remote --heads origin main` failed to connect to `github.com:443`.
- `Test-NetConnection github.com -Port 443` reported ping success but
  `TcpTestSucceeded=False`, indicating an HTTPS connectivity blocker rather
  than a repository-content issue.
- The runbook now records the retry and diagnostic commands for the next
  resume.

Evidence boundary:

- Phase 63 records remote-save diagnostics only.
- It does not complete DeepSeek, AI-Scientist-v2 smoke/full live run, human
  annotation, provider billing, or the final AAAI submission decision.

## 2026-06-20 Phase 64

Actions:

- Retried `git push origin main` after the Phase 63 connectivity diagnostic.
- Confirmed local tracking state after the push.
- Updated short-term memory and `research/runbook.md` so future resumes do not
  treat the Phase 62/63 commits as unsaved.
- Added
  `research/run_logs/2026-06-20_phase64_remote_save_recovered.md`.

Results:

- `git push origin main` succeeded:
  `92beb7f..ad8346b  main -> main`.
- The remote save includes both `0db90e2 Add DeepSeek followup configuration
  helper` and `ad8346b Record GitHub push connectivity diagnostics`.
- `git status -sb` reported `main...origin/main` after the push.
- A follow-up `git ls-remote --heads origin main` still failed with
  `Recv failure: Connection was reset`, so GitHub HTTPS access should be
  considered intermittent even though the remote save succeeded.

Evidence boundary:

- Phase 64 records remote-save recovery only.
- It does not complete DeepSeek, AI-Scientist-v2 smoke/full live run, human
  annotation, provider billing, or the final AAAI submission decision.

## 2026-06-20 Phase 65

Actions:

- Re-ran direct OpenAI-compatible endpoint probes after remote-save recovery.
- Used shell-only credentials for the Claude-family and GPT-family profiles.
- Updated the direct-probe JSON reports with fresh timestamps.
- Added
  `research/run_logs/2026-06-20_phase65_direct_probe_recheck.md`.

Results:

- Claude-family direct probe remains
  `blocked_by_provider_or_model_availability`; `claude-opus-4-8`,
  `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` all returned
  HTTP 503 `No available accounts: no available accounts`.
- GPT-family direct probe remains
  `blocked_by_provider_or_model_availability`; `gpt-5.5` and `gpt-5.4` both
  returned HTTP 502 `Upstream access forbidden, please contact administrator`.
- No direct-probe marker-contract response files were saved.

Evidence boundary:

- Phase 65 is a provider-availability diagnostic only.
- It does not complete the AI-Scientist-v2 LLM-client smoke, BFTS/full live
  run, DeepSeek rows, human annotation, provider billing, or the final AAAI
  submission decision.

## 2026-06-20 Phase 66

Actions:

- Added `scripts/generate_aaai_submission_decision.py`, a validated helper that
  writes `research/aaai_submission_decision.md` only when an explicit option,
  owner, date, claim boundary, and evidence policy are supplied.
- Added `tests/test_generate_aaai_submission_decision.py`.
- Updated the AAAI submission-decision preflight so it lists the helper as an
  input and includes helper commands for both decision options.
- Updated `research/runbook.md`, artifact map, and reproducibility package
  checks to include the helper.
- Added
  `research/run_logs/2026-06-20_phase66_aaai_decision_record_helper.md`.

Results:

- The helper validates the selected option against the current preflight,
  rejects raw API-key-like material, and refuses empty required fields.
- No human decision record was generated in this phase.
- `aaai_final_submission_ready` remains pending until the research lead
  explicitly records a selected option and evidence policy.

Evidence boundary:

- Phase 66 adds a local decision-record helper only.
- It does not select an AAAI submission decision, submit the paper, complete
  DeepSeek, complete AI-Scientist-v2 smoke/full live run, collect human
  annotation, or collect provider billing.

## 2026-06-20 Phase 67

Actions:

- Pushed Phase 66 commit `4c02013 Add AAAI decision record helper` to
  `origin/main`.
- Updated short-term memory and artifact map with the remote-save status.
- Added
  `research/run_logs/2026-06-20_phase67_remote_save_after_decision_helper.md`.

Results:

- `git push origin main` succeeded:
  `78c78ae..4c02013  main -> main`.
- `git status -sb` reported `main...origin/main` after the push.
- Latest pushed HEAD after Phase 66 was
  `4c020132be895469441489371516e6d14af7d2ef`.

Evidence boundary:

- Phase 67 records remote-save status only.
- It does not complete any pending external evidence or select the final AAAI
  submission decision.

## 2026-06-20 Phase 68

Actions:

- Refreshed stale long-term and short-term memory anchors after the Phase 67
  remote save.
- Added `scripts/generate_aaai_submission_decision.py` and the AAAI gate
  recursion fix to the long-term artifact/fix map.
- Updated current generated-report counts in memory and runbook:
  reproducibility package `283 ready / 8 pending / 0 failed`, AAAI decision
  preflight `26 ready / 1 pending / 0 failed`, and usage examples `55 ready /
  0 failed`.

Results:

- The current recovery anchor before this Phase 68 commit is
  `a0d67bc8d64ee7b25f3319817634fbc426bf31e0`.
- Memory now records Phase 67 as pushed to `origin/main` and avoids treating
  the older Phase 66 commit as the latest pushed HEAD.

Evidence boundary:

- Phase 68 refreshes memory/report anchors only.
- It does not complete any pending external evidence or select the final AAAI
  submission decision.

## 2026-06-20 Phase 69

Actions:

- Updated `scripts/check_external_evidence_packets.py` so the
  `aaai_submission_decision` execution packet lists
  `scripts/generate_aaai_submission_decision.py` and the current AAAI
  decision preflight report as inputs.
- Reordered the AAAI decision packet commands into pre-decision local gates,
  exactly one human-selected helper command, and final validation after the
  decision record exists.
- Added helper commands for both available decision options:
  `submit_now_deterministic_offline` and `wait_for_external_evidence`.
- Tightened completion criteria so `research/aaai_submission_decision.md` must
  exist and validate through `scripts/check_aaai_submission_decision.py --strict`.
- Added regression assertions in
  `tests/test_check_external_evidence_packets.py`.
- Regenerated the external-evidence packet reports and refreshed dependent
  AAAI decision, goal-completion, and reproducibility-package reports.
- Added
  `research/run_logs/2026-06-20_phase69_aaai_decision_packet_helper_sync.md`.

Results:

- `python -m unittest tests.test_check_external_evidence_packets -v`: 3 tests
  passed.
- `python scripts\check_external_evidence_packets.py --strict`: passed.
- `python scripts\check_aaai_submission_decision.py --strict`: passed and still
  reports `pending_human_decision`, 26 ready checks, 1 pending check, and 0
  failed checks.
- `python scripts\check_goal_completion.py --strict`: passed and still reports
  `not_complete_pending_external_evidence`, 70 ready checks, 8 pending checks,
  and 0 failed checks.
- `python scripts\check_reproducibility_package.py --strict`: passed and still
  reports `ready_with_pending_external_evidence`, 283 ready checks, 8 pending
  checks, and 0 failed checks.

Evidence boundary:

- Phase 69 improves the local final-decision handoff only.
- It does not generate `research/aaai_submission_decision.md`, select an AAAI
  submission option, submit the paper, or complete any pending external
  evidence.

## 2026-06-26 Phase 70

Actions:

- Inspected local Claude Desktop and CC Switch configuration to identify the
  normal Claude request shape.
- Updated `scripts/run_openai_compatible_direct_probe.py` from a fixed
  `/chat/completions` diagnostic into a protocol-aware direct provider probe.
  It now supports `openai_chat_completions`, `openai_responses`, and
  `anthropic_messages` wire APIs.
- Updated external-evidence closure and packet commands so current direct
  probes use Anthropic Messages for Claude-family models and OpenAI Responses
  for GPT-family models.
- Removed the older dotted Claude alias from current direct-probe and wrapper
  smoke handoff commands; historical reports still preserve the older attempts.
- Refreshed direct provider probe reports for Claude and GPT with shell-only
  credentials.
- Updated `research/runbook.md`, long-term memory, and short-term memory with
  the protocol-specific routing and current blocker state.
- Added
  `research/run_logs/2026-06-26_phase70_protocol_specific_direct_probe.md`.

Results:

- Claude Desktop / CC Switch evidence indicates Claude direct requests should
  use `POST https://coderxiaoc.com/v1/messages`, `Authorization: Bearer ...`,
  and `anthropic-version: 2023-06-01`.
- `results/openai_compatible_direct_probe/claude_family/run_report.md` now
  records `wire_api=anthropic_messages`; `claude-opus-4-8`,
  `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 502
  `Upstream service temporarily unavailable`.
- `results/openai_compatible_direct_probe/gpt_family/run_report.md` now records
  `wire_api=openai_responses`; `gpt-5.5` and `gpt-5.4` returned HTTP 502
  `Upstream access forbidden`.
- Focused tests for direct probe, external-evidence closure, external-evidence
  packets, and reproducibility package passed.

Evidence boundary:

- Phase 70 corrects the direct-provider diagnostic protocol and updates
  handoff commands.
- The refreshed direct probes still did not produce a marker-contract response.
- AI-Scientist-v2 LLM-client smoke, full live/BFTS run, DeepSeek follow-up,
  human annotation, provider billing, and final AAAI submission readiness remain
  pending.

Phase 71 evidence:

- Verified the two local interface documents in `C:\Users\19351\Desktop\tem`
  are runnable as written.
- `GPT大模型接口说明文档.md` returned HTTP 200 on the first attempt for
  `gpt-5.5` and `gpt-5.4` via `POST https://coderxiaoc.com/v1/responses`.
- `Claude大模型接口说明文档.md` returned HTTP 200 on the first attempt for
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` via
  `POST https://coderxiaoc.com/v1/messages`.
- Added `research/run_logs/2026-06-30_interface_docs_runnable.md` as the
  project record for this check.

Evidence boundary:

- This confirms the local document request shapes are runnable.
- It does not change the separate AI-Scientist-v2 smoke / live-run blockers or
  any AAAI submission state.

## 2026-07-01 Phase 72

Actions:

- Re-tested the three local API interface documents in
  `C:\Users\19351\Desktop\tem` from their current contents:
  `GPT大模型接口说明文档.md`, `Claude大模型接口说明文档.md`, and
  `DeepSeek大模型接口说明文档.md`.
- Used each document's protocol shape and a minimal prompt:
  `Reply with exactly one word: ok`.
- Applied the documented retry rule: up to five attempts with short interval
  retry before marking the current direct request path unavailable.
- Recorded only redacted credential hints in project files.

Results:

- GPT doc is currently runnable:
  - `gpt-5.5` via `POST https://coderxiaoc.com/v1/responses` returned HTTP 200
    on attempt 2 with visible `ok`.
  - `gpt-5.4` via `POST https://coderxiaoc.com/v1/responses` returned HTTP 200
    on attempt 1 with visible `ok`.
- DeepSeek doc is currently runnable:
  - `deepseek-v4-flash` via
    `POST https://api.deepseek.com/chat/completions` returned HTTP 200 on
    attempt 1 with visible `ok`.
  - `deepseek-v4-pro` via
    `POST https://api.deepseek.com/chat/completions` returned HTTP 200 on
    attempt 1 with visible `ok`.
- Claude doc did not succeed as a direct HTTP request in this run:
  - `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` via
    `POST https://coderxiaoc.com/v1/messages` returned HTTP 502 after five
    attempts with the regular doc key.
  - The same three models also returned HTTP 502 after five attempts with the
    Desktop direct provider token listed in the doc.

Evidence boundary:

- The latest direct-document availability answer is: GPT and DeepSeek are
  runnable now; Claude is not runnable via the documented naked HTTP request in
  this run.
- The Claude result is HTTP 502 gateway/upstream failure, not proof that the
  model aliases are invalid or that Claude Desktop/CC Switch cannot work
  through a richer client path.
- This phase does not complete AI-Scientist-v2 LLM-client smoke, full
  live/BFTS run, human annotation, provider billing, or AAAI submission
  readiness.

Phase 72 addendum:

- A same-day Claude-only re-test was run after the earlier 502s.
- The regular Claude doc key (`sk-c83d...cad7`) succeeded for
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` via
  `POST https://coderxiaoc.com/v1/messages`; all returned HTTP 200 on attempt 1
  with visible `ok`.
- The same regular key also succeeded for all three models with the observed
  Claude Code/Desktop beta header.
- The Desktop direct provider token (`sk-6477...000e`) still returned HTTP 502
  after five attempts for all three aliases.
- Updated interpretation: the Claude document is runnable with the regular API
  key; the earlier 502 result was transient upstream/direct-request
  unavailability. The Desktop token remains unavailable through naked direct
  HTTP in this test.

## 2026-07-01 Phase 73

Actions:

- Reviewed newly added PDFs under `papers/raw` and extracted text under
  `papers/extracted_text`.
- Added `research/new_paper_triage_2026-07-01.md`.
- Updated related-work framing, claim-source mapping, AAAI bibliography, and
  paper/review handoff text.
- Updated protocol-aware model-ablation evidence and local gates to reflect the
  current GPT and DeepSeek runs while preserving the Claude provider blocker.

New-paper decision:

- Paper2Agent is core related work and the closest competing system. It builds
  MCP servers and interactive paper agents from papers plus codebases. Add it
  as a main citation and plan a future skill-vs-MCP comparison.
- AgenticSciML is adjacent background for agentic scientific discovery. Cite it
  as workflow/multi-agent context, not as a paper-to-skill baseline.
- Reasoning Manifolds is a future theory-heavy/non-procedural stress case. Do
  not add it to the current main experiment.

Model/API evidence:

- GPT protocol refresh completed both current model-ablation rows with
  `gpt-5.5` through OpenAI Responses.
- DeepSeek completed both current model-ablation rows with
  `deepseek-v4-flash` through Chat Completions.
- Latest Claude protocol refresh used Anthropic Messages but was blocked by
  provider HTTP 502; scored Claude rows come from previously saved response
  files.
- `results/model_ablation_prompts/v0/evaluation.md` reports 6 total rows,
  6 scored rows, 0 pending rows, and average normalized score 1.0.
- `results/tables/model_response_cost_proxy.md` reports 6 measured rows,
  0 pending rows, and 9,594 `o200k_base` output tokens.

Evidence boundary:

- Saved-response model-ablation scoring is not live downstream task success,
  human semantic fidelity, provider billing, success per dollar, or a broad
  model-quality comparison.
- AI-Scientist-v2 LLM-client smoke/full live run, human fidelity annotation,
  provider billing, and final AAAI decision remain pending.

## 2026-07-01 Phase 74

Actions:

- Promoted the Paper2Agent work from a planned comparison to a completed
  bounded artifact/workflow comparison.
- Updated the AAAI draft, Markdown draft, outline, limitations, claim
  checklist, related-work gap map, experiment queue, claim-evidence matrix,
  review report, rebuttal bank, submission checklist, runbook, goal audit, and
  memory anchors so they no longer treat Paper2Agent comparison or DeepSeek
  saved-response rows as pending.
- Wrote the human-action handoff to
  `C:\Users\19351\Desktop\tem\toHuman\needHelp.md`.

Results:

- `results/tables/paper2agent_artifact_comparison.md` reports
  `overall_status=ready`, 7 ready criteria, and 0 failed criteria.
- `results/model_ablation_prompts/v0/evaluation.md` reports 6 total rows,
  6 scored rows, 0 pending rows, and average normalized score 1.0.
- `results/reproducibility/goal_completion_report.md` reports
  `not_complete_pending_external_evidence`, 74 ready checks, 6 pending checks,
  and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 296 ready checks, 6 pending checks,
  and 0 failed checks.
- `results/external_evidence_closure/closure.md` now has 5 queue items:
  AI-Scientist-v2 smoke completion, AI-Scientist-v2 full live/BFTS run,
  human-fidelity annotation, provider billing/success-per-dollar evidence, and
  AAAI submission decision.

Evidence boundary:

- Phase 74 completes a source-backed Paper2Agent artifact/workflow comparison
  only. It does not run Paper2Agent, deploy an MCP server, or claim executable
  baseline performance.
- DeepSeek is complete only for saved-response model-ablation scoring under the
  current two-case protocol.
- AI-Scientist-v2 LLM-client smoke/full live run, human-fidelity annotation,
  provider billing, and final AAAI decision remain pending.

## 2026-07-02 Phase 76

Actions:

- Closed the bounded AI-Scientist-v2 smoke/full live-run evidence path after the
  documented Claude-family route produced a marker-contract smoke response and
  a full AI-Scientist-v2 completion directory.
- Refreshed stale external-evidence closure and execution-packet reports so
  completed AI-Scientist-v2 evidence is no longer queued as pending.
- Updated the human-help handoff so only human-fidelity annotation remains a
  human-side action for the current evidence policy.
- Recorded the full run in
  `research/run_logs/2026-07-02_phase76_ai_scientist_v2_full_live_run.md`.

Results:

- `results/ai_scientist_v2_smoke/run_report.md` reports `complete`, 6 ready
  checks, 0 pending checks, and 0 failed checks.
- `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`,
  16 ready checks, 0 pending checks, 0 failed checks, and one completion
  directory:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
- The AI-Scientist-v2-generated synthetic result shows skill task-success rate
  0.80, full excerpt 0.80, abstract 0.20, generic summary 0.00, no context
  0.00, with skill token cost 86.2 versus 113.2 for full excerpt.
- The retrieval-depth sensitivity branch reports skill success 0.80 for
  K=1,2,3,5 and 1.00 for K=all.
- `results/external_evidence_closure/closure.md` now has two queue items:
  human-fidelity annotation and AAAI submission decision.
- `results/external_evidence_packets/packets.md` now has two packets matching
  those queue items.
- `results/reproducibility/goal_completion_report.md` reports
  `not_complete_pending_external_evidence`, 77 ready checks, 3 pending checks,
  and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 305 ready checks, 1 pending check,
  and 0 failed checks.

Evidence boundary:

- The Phase 76 AI-Scientist-v2 evidence is bounded integration/synthetic
  sensitivity evidence. It does not make the main PaperToSkill benchmark a
  human-validated live task-success study.
- The Stage 3 HF/semantic-data branch remains a failed branch only because of
  invalid dataset loading/synthetic padding and missing `sentence_transformers`.
- Human-fidelity annotation and final AAAI submission readiness remain pending
  under the recorded `wait_for_external_evidence` policy.

## 2026-07-03 Phase 79

Actions:

- Recorded the next-stage real-reuse experiment design in
  `research/real_reuse_experiment_plan.md`.
- Updated `paper/outline.md` so the current deterministic/offline results remain
  the completed evidence, while original-style paper-task reuse is explicitly a
  planned next-stage validity experiment.
- Updated `research/experiment_queue.md`,
  `research/claim_evidence_matrix.md`, `research/goal_completion_audit.md`,
  `research/runbook.md`, and `research/artifact_map.md` to track the eight-task
  plan across AIDE, SWE-agent, Reflexion, and SnapATAC2.
- Kept Toolformer and AI Scientist-v2 as sanity/auxiliary cases rather than
  main real-reuse evidence.

Planned task grid:

- AIDE-T1 and AIDE-T2 for ML engineering.
- SWE-T1 and SWE-T2 for software engineering.
- REF-T1 and REF-T2 for reasoning/QA or reflection-based retry.
- SNAP-T1 and SNAP-T2 for single-cell data analysis.

Evidence boundary:

- Phase 79 is planning/protocol evidence only. It does not complete any
  real-reuse run.
- The AAAI manuscript results must not be rewritten as if these tasks have been
  executed.
- Existing deterministic/offline evaluations remain quality, grounding, cost,
  and readiness evidence until real-reuse raw rows exist.

## 2026-07-03 Phase 80

Actions:

- Converted the Phase 79 real-reuse plan into a machine-checkable benchmark
  specification at `benchmarks/real_reuse/real_reuse_v0.json`.
- Added `scripts/check_real_reuse_benchmark.py` and regression tests so the
  planned benchmark gates the eight task IDs, main paper set, Summary vs
  PaperToSkill conditions, Full Excerpt sanity scope, reference-score boundary,
  source-link declarations, workflow checklists, and future output paths.
- Generated the local preflight reports under `results/real_reuse/` and wired
  them into the aggregate reproducibility package checker.
- Updated the runbook, artifact map, experiment queue, claim-evidence matrix,
  and goal-completion audit so the next work starts from per-task executable
  specs, runner, scorer, and raw rows.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 85 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 312 ready checks, 1 pending check,
  and 0 failed checks after adding the real-reuse preflight gate.

Evidence boundary:

- Phase 80 completes only the planned benchmark spec and preflight gate. It
  does not run any real-reuse task and does not create downstream task-success
  evidence.
- The next required implementation step is to create per-task executable specs
  under `benchmarks/real_reuse/tasks/`, then implement a runner and scorer that
  preserve raw rows under `results/real_reuse/`.

## 2026-07-03 Phase 81

Actions:

- Added `scripts/build_real_reuse_task_specs.py` to materialize the eight
  per-task real-reuse execution-contract specs from the master benchmark spec.
- Generated `benchmarks/real_reuse/tasks/*.json` for AIDE-T1/T2, SWE-T1/T2,
  REF-T1/T2, and SNAP-T1/T2.
- Extended `scripts/check_real_reuse_benchmark.py` so the preflight validates
  each per-task spec's identity, condition set, metric contract, raw-row schema,
  and no-mid-run-human-intervention rule.
- Added tests for the task-spec builder and expanded package-gate expectations.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 142 ready checks, and 0 failed checks after validating the per-task
  specs.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 321 ready checks, 1 pending check,
  and 0 failed checks after adding the task-spec builder and eight task specs.

Evidence boundary:

- Phase 81 makes the task contracts concrete but still does not select fixtures,
  run any task, or create downstream result rows.
- The next implementation step is fixture manifests under
  `benchmarks/real_reuse/fixtures/`, followed by the runner and scorer.

## 2026-07-03 Phase 82

Actions:

- Added `scripts/build_real_reuse_fixture_manifests.py` to materialize fixture
  requirement manifests from the eight per-task real-reuse contracts.
- Generated `benchmarks/real_reuse/fixtures/*.json` for all eight tasks.
- Extended `scripts/check_real_reuse_benchmark.py` so the preflight validates
  each fixture manifest's identity, status, asset slots, context conditions,
  metric alignment, no-mid-run-human rule, and license/provenance boundary.
- Added fixture-manifest tests and expanded package-gate expectations.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 207 ready checks, and 0 failed checks after validating fixture
  manifests.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 330 ready checks, 1 pending check,
  and 0 failed checks after adding the fixture builder and eight manifests.

Evidence boundary:

- Phase 82 creates fixture requirement manifests only. It does not select or
  download datasets/repositories, fill scoring commands, run any task, or
  produce downstream result rows.
- The next implementation step is concrete fixture-asset selection plus
  runner/scorer implementation.

## 2026-07-03 Phase 83

Actions:

- Added `scripts/build_real_reuse_fixture_candidates.py` to materialize
  candidate asset/preparation manifests from the eight task specs and fixture
  requirement manifests.
- Generated `benchmarks/real_reuse/fixture_candidates/*.json` for all eight
  real-reuse tasks.
- Selected preparation candidates: MLE-bench Spaceship Titanic for AIDE-T1/T2,
  SWE-bench Lite/Verified for SWE-T1/T2, HotPotQA and HumanEval for REF-T1/T2,
  and SnapATAC2 official tutorial/API-backed datasets for SNAP-T1/T2.
- Extended `scripts/check_real_reuse_benchmark.py` so the preflight validates
  candidate identity, selected-source status, official/source URLs, asset-slot
  coverage, not-downloaded/license-review boundaries, preparation commands,
  scoring entry points, no-mid-run-human controls, and evidence boundaries.
- Added candidate-builder tests and expanded package-gate expectations.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 296 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 339 ready checks, 1 pending check,
  and 0 failed checks.
- These are preparation checks only, not execution checks.

Evidence boundary:

- Phase 83 selects candidate assets and preparation/scoring entry points only.
  It does not download Kaggle/Hugging Face/SnapATAC2 data, clone external
  projects for execution, fix task instance IDs, implement the preparer/scorer
  scripts, run Summary or PaperToSkill conditions, or create downstream result
  rows.

## 2026-07-03 Phase 84

Actions:

- Added `scripts/build_real_reuse_paper_tables.py` to materialize the
  paper-facing main real-reuse table scaffold from
  `benchmarks/real_reuse/real_reuse_v0.json`.
- Generated `results/real_reuse/main_results_plan.csv` and
  `results/real_reuse/main_results_plan.md`.
- Inserted the real-reuse main experiment table into
  `paper/aaai/papertoskill_tables.tex` as
  `Table~\ref{tab:real-reuse-main}` with pending Summary/PaperToSkill score
  cells.
- Updated `paper/aaai/papertoskill_aaai2027.tex` so the Experimental Setup
  identifies the real-reuse table as the primary downstream experiment and the
  Results section explicitly treats current completed numbers as
  deterministic/offline evidence.
- Extended `scripts/check_paper_tables.py` so the AAAI table is checked against
  `results/real_reuse/main_results_plan.csv`.
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf`.

Results:

- `results/reproducibility/paper_table_report.md` reports `ready`, 156 ready
  checks, and 0 failed checks.
- `results/reproducibility/aaai_package_report.md` reports `ready`, 17 ready
  checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 342 ready checks, 1 pending check,
  and 0 failed checks.

Evidence boundary:

- Phase 84 updates the paper table structure only. Summary/PaperToSkill task
  scores remain pending execution and must be filled after the main real-reuse
  tasks run.

## 2026-07-03 Phase 85

Actions:

- Added `scripts/build_real_reuse_asset_locks.py` to materialize
  preparation-time asset locks from the task specs, fixture manifests, and
  candidate manifests.
- Generated `benchmarks/real_reuse/asset_locks/*.json` for all eight real-reuse
  tasks.
- Locked concrete task instances and preparation contracts: Spaceship Titanic
  split/weak-script seeds for AIDE-T1/T2, SWE-bench Lite
  `sqlfluff__sqlfluff-1625`, SWE-bench Verified `astropy__astropy-12907`,
  HotPotQA distractor validation example `5a8b57f25542995d1e6f1371`,
  HumanEval `HumanEval/0`, and SnapATAC2 `pbmc5k` / `pbmc10k_multiome`
  tutorial fixtures.
- Corrected the SnapATAC2 candidate API URL from the stale `api.html` path to
  the current official `api/index.html` path.
- Extended `scripts/check_real_reuse_benchmark.py` so the preflight validates
  asset-lock identity, selected candidate match, fixed task instance, observed
  source revisions, asset-slot coverage, local targets, preparation contract,
  hidden scorer assets, scoring contract, run controls, and evidence boundary.
- Added asset-lock builder tests and expanded package-gate expectations.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 401 ready checks, and 0 failed checks after validating asset locks.

Evidence boundary:

- Phase 85 locks source revisions, task instances, local materialization
  targets, and scorer/preparer contracts only. It does not materialize datasets
  or repositories for execution, implement the preparer/scorer scripts, run
  Summary or PaperToSkill, or create downstream result rows.

## 2026-07-03 Phase 86

Actions:

- Added `scripts/prepare_real_reuse_reflexion_fixture.py` for locked REF-T1
  and REF-T2 fixture preparation.
- Added `scripts/score_real_reuse_reflexion.py` for REF-T1 EM/F1 answer-key
  scoring and REF-T2 HumanEval checker scoring.
- Materialized REF-T1 assets under `benchmarks/real_reuse/assets/REF-T1/`:
  question, retrieval context/tool stub, feedback protocol, task prompt, hidden
  answer key, and `asset_manifest.json`.
- Materialized REF-T2 assets under `benchmarks/real_reuse/assets/REF-T2/`:
  initial task, failed first attempt, environment feedback, task prompt, hidden
  tests/canonical solution, and `asset_manifest.json`.
- Created task-specific Summary baseline contexts at
  `baselines/real_reuse/REF-T1_summary.md` and
  `baselines/real_reuse/REF-T2_summary.md`.
- Extended `scripts/check_real_reuse_benchmark.py` so the preflight validates
  REF prepared asset manifests, sha256 values, model-visible/scorer-only
  separation, condition contexts, and evidence boundaries.
- Extended the reproducibility package gate to include the REF preparer,
  scorer, prepared assets, and Summary contexts.
- Added tests for the REF preparer, REF scorer, prepared-asset preflight, and
  package-gate expectations.

Results:

- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 418 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 368 ready checks, 1 pending check,
  and 0 failed checks.
- Targeted tests for the new preparer/scorer and real-reuse/package checks
  passed before full-gate execution.

Evidence boundary:

- Phase 86 prepares REF fixture assets and objective scorers only. It does not
  run Summary or PaperToSkill model conditions, does not create real-reuse raw
  rows, and does not provide downstream task-success evidence. AIDE, SWE-agent,
  and SnapATAC2 fixture assets/runners remain pending.

## 2026-07-03 Phase 87

Actions:

- Added `scripts/run_real_reuse_reflexion.py` to run locked REF-T1/REF-T2
  Summary-vs-PaperToSkill conditions, save prompts/responses/metrics, append
  scored raw rows, and report provider/model errors as availability evidence.
- Added tests for fixture-response execution, missing-credential pending
  behavior, prompt/scorer-only separation, and table filling from raw rows.
- Fixed REF-T1 scoring so yes/no answers with explanatory final-answer text
  are counted by their leading yes/no label while preserving EM/F1 fields.
- Ran the locked REF-T1/REF-T2 tasks through the GPT-family Responses profile
  using local shell-only credentials from the API docs.
- Updated `scripts/build_real_reuse_paper_tables.py` so the paper-facing
  real-reuse table fills existing score cells from `results/real_reuse/raw_rows.jsonl`.
- Updated `paper/aaai/papertoskill_tables.tex` and the AAAI results wording so
  REF-T1/REF-T2 have filled scores while AIDE, SWE-agent, and SnapATAC2 remain
  pending.
- Extended the real-reuse preflight and reproducibility package gates to track
  the REF runner and generated table JSON.

Results:

- `results/real_reuse/reflexion_run_report.md` reports `complete` with 4
  scored rows for GPT-family `gpt-5.5`.
- `results/real_reuse/raw_rows.jsonl` contains REF-T1/REF-T2 Summary and
  PaperToSkill scored rows. All four rows score 1.000 with zero interventions.
- `results/real_reuse/main_results_plan.{csv,md,json}` now fill REF-T1 and
  REF-T2 Summary/PaperToSkill scores as 1.000 and leave the remaining six rows
  pending.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 420 ready checks, and 0 failed checks after adding runner checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 370 ready checks, 1 pending check,
  and 0 failed checks after adding the runner and generated table JSON.

Evidence boundary:

- Phase 87 is partial real-reuse execution evidence for the Reflexion slice
  only. It shows the REF runner/scorer/table path works and that both Summary
  and PaperToSkill solve the two locked REF tasks under one GPT-family run. It
  does not show aggregate PaperToSkill advantage over Summary and does not
  complete the eight-task main experiment.

## 2026-07-03 Phase 88

Actions:

- Added `scripts/prepare_real_reuse_aide_fixture.py` to prepare locked
  AIDE-T1/AIDE-T2 fixtures from a real Kaggle Spaceship Titanic `train.csv`.
  The preparer creates deterministic validation splits, task prompts, Summary
  contexts, baseline submissions, and scorer-only `validation_labels.csv`.
- Added `scripts/score_real_reuse_aide.py` to score AIDE submissions or
  candidate scripts in an isolated temporary workspace against hidden
  validation labels and baseline-score JSON.
- Added `scripts/run_real_reuse_aide.py` to run locked AIDE Summary and
  PaperToSkill conditions, save prompts/responses/metrics/raw rows, and record
  missing credentials or provider errors as availability state rather than
  model-quality failure.
- Added AIDE unit tests for fixture preparation, scorer-only label separation,
  isolated candidate execution, fixture-response runner execution,
  missing-credential pending behavior, and hidden-label prompt separation.
- Extended the real-reuse preflight and reproducibility package gates to track
  the AIDE preparer/scorer/runner contract.
- Updated the runbook, artifact map, and experiment queue so AIDE is described
  as execution-layer ready but still blocked on real Kaggle data for fixture
  materialization and paper scores.

Results:

- Targeted AIDE/preflight/package test set passed: 17 tests.
- Full unit discovery passed: 131 tests.
- All strict local gates passed, including submission review, AAAI decision,
  DeepSeek follow-up, usage examples, external-evidence closure/packets,
  AI-Scientist-v2 live-run handoff, goal completion, reproducibility package,
  paper claims, AAAI package, paper tables, and real-reuse benchmark.
- `git diff --check` returned only line-ending warnings, and the raw-key scan
  produced no matches.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`,
  8 tasks, 424 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 376 ready checks, 1 pending check,
  and 0 failed checks.
- Human handoff remains active at
  `C:\Users\19351\Desktop\tem\toHuman.md`; `ok.txt` and the real
  `spaceship-titanic/train.csv` were not present during this phase.

Evidence boundary:

- Phase 88 is AIDE execution-layer readiness only. It does not materialize real
  AIDE fixture assets, does not run Summary or PaperToSkill model conditions,
  does not append AIDE rows to `results/real_reuse/raw_rows.jsonl`, and does
  not update the AAAI table with AIDE scores. Synthetic CSVs used in unit tests
  are test fixtures, not paper evidence.

## 2026-07-03 Phase 89

Actions:

- Retried `git push origin main` after the earlier Phase 87 GitHub HTTPS
  connectivity blocker.
- Recorded the remote-save recovery in
  `research/run_logs/2026-07-03_phase89_remote_save_after_aide_execution_layer.md`.

Results:

- `git push origin main` succeeded for the Phase 87/88 stack; a follow-up
  remote-save memory/log synchronization was also pushed.
- The remote now contains the Phase 87 REF runner/raw rows, the Phase 87 push
  blocker note, and the Phase 88 AIDE execution-layer commit.

Evidence boundary:

- Phase 89 is remote-save evidence only. It does not add new task results,
  clear the missing Kaggle `train.csv` blocker, or complete the eight-task
  real-reuse benchmark.

## 2026-07-03 Phase 90

Actions:

- Added a SWE-agent profile to `scripts/papertoskill_note_from_text.py` so the
  deterministic auto-note scaffold targets the SWE-agent paper's
  agent-computer-interface method, SWE-bench evaluation setup, ablations, and
  limitations.
- Generated `papers/auto_notes/swe_agent_auto_note.md`,
  `generated_skills/real_reuse/swe_agent/SKILL.md`, and
  `generated_skills/real_reuse/swe_agent/references/source_map.json`.
- Added `benchmarks/rubric_swe_agent_v0.json` and
  `benchmarks/tasks/swe_agent_auto_source_span_validation.json`.
- Ran the SWE-agent deterministic rubric and source-span validation.
- Updated the real-reuse table builder so pending rows report accurate
  readiness states: AIDE awaiting dataset, SWE-agent runner pending, SnapATAC2
  skill pending, and Reflexion scored.
- Extended the real-reuse and reproducibility gates to track the SWE-agent
  skill/readiness artifacts.

Results:

- SWE-agent rubric score is 20/20.
- The generated SWE-agent skill is 1186 words under the 1200-word compactness
  budget.
- SWE-agent source-span validation reports 20/20 supported claims,
  `support_rate=1.0`, and 0 invalid ranges.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 430
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 377 ready checks, 1 pending check,
  and 0 failed checks.
- The AAAI PDF was rebuilt after the table status update, and
  `results/reproducibility/aaai_package_report.md` reports ready with 17 ready
  checks and 0 failed checks.
- Full unit discovery passed with 133 tests. All strict local gates passed.
  `git diff --check` reported no whitespace errors beyond Windows line-ending
  warnings, and the raw-key scan produced no matches.

Evidence boundary:

- Phase 90 is SWE-agent skill/readiness evidence only. It does not implement
  SWE-bench fixture preparation, scoring, or running; does not append SWE raw
  rows; and does not provide SWE-T1/T2 downstream task-success evidence.
- AIDE remains blocked on the missing real Kaggle Spaceship Titanic
  `train.csv`; the user-side `ok.txt` signal was not present.

## 2026-07-03 Phase 91

Actions:

- Added `scripts/prepare_real_reuse_swe_fixture.py` to prepare locked SWE-T1
  and SWE-T2 fixture assets from local repository snapshots, issue/failing-test
  context, and a locked test command.
- Added `scripts/score_real_reuse_swe.py` to score candidate unified diff
  patches by applying them in an isolated temporary copy of the prepared
  workspace and running the locked test command.
- Added `scripts/run_real_reuse_swe.py` to run Summary and PaperToSkill
  conditions, save prompts/responses/metrics/raw rows when rows are scorable,
  and treat missing fixture assets, missing credentials, or provider/model
  errors as availability state.
- Added focused SWE unit tests for fixture preparation, hidden gold-patch
  separation, patch scoring, fixture-response runner execution,
  missing-fixture and missing-credential pending behavior, and prompt
  separation.
- Updated the real-reuse table status logic and tests so SWE rows are
  `Fixture pending` once the SWE skill and runner exist but no
  `asset_manifest.json` has been prepared.
- Extended real-reuse/package gates and documentation to include the SWE
  execution-layer contract.

Results:

- Targeted SWE/table/preflight/package tests passed: 18 tests.
- `results/real_reuse/main_results_plan.{csv,md,json}` now reports SWE-T1/T2
  as `Fixture pending`, with score cells still `Pending`.
- `paper/aaai/papertoskill_tables.tex` now matches the generated real-reuse
  table, and `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 434
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 381 ready checks, 1 pending check,
  and 0 failed checks.
- Paper-facing gates passed: `check_paper_tables.py`, `check_paper_claims.py`,
  and `check_aaai_package.py`.

Evidence boundary:

- Phase 91 is SWE execution-layer readiness only. It does not materialize
  official SWE-bench assets, does not prepare SWE-T1/T2 `asset_manifest.json`
  files, does not run live Summary/PaperToSkill SWE rows, does not append SWE
  raw rows, and does not add SWE task scores to the paper.
- The current real-reuse effectiveness evidence is still only the partial
  REF-T1/REF-T2 GPT-family slice; AIDE, SWE-agent, and SnapATAC2 remain
  pending for downstream task scores.

## 2026-07-03 Phase 92

Actions:

- Added a `snapatac2` profile to `scripts/papertoskill_note_from_text.py` for
  extracting matrix-free spectral embedding workflow steps, validation metrics,
  transfer cases, and limitations from the SnapATAC2 paper.
- Normalized deterministic text extraction with Unicode decomposition before
  ASCII conversion so terms such as `Nyström` become `Nystrom` instead of
  losing letters in generated notes.
- Generated the SnapATAC2 real-reuse skill gate artifacts:
  `papers/auto_notes/snapatac2_auto_note.md`,
  `generated_skills/real_reuse/snapatac2/SKILL.md`, source map,
  `benchmarks/rubric_snapatac2_v0.json`,
  `benchmarks/tasks/snapatac2_auto_source_span_validation.json`, and
  evaluation reports.
- Extended `scripts/check_real_reuse_benchmark.py` and
  `scripts/check_reproducibility_package.py` so the real-reuse/package gates
  validate SnapATAC2 skill, rubric, and source-span readiness.
- Refreshed the real-reuse main table and AAAI table/PDF so SNAP-T1/T2 now
  show `Runner pending` instead of `Skill pending`.

Results:

- SnapATAC2 rubric score is 20/20.
- The generated SnapATAC2 skill is 1091 words under the 1200-word compactness
  budget.
- SnapATAC2 source-span validation reports 18/18 supported claims,
  `support_rate=1.0`, and 0 invalid ranges.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 440
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 392 ready checks, 1 pending check,
  and 0 failed checks.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after the table status
  update, and `results/reproducibility/aaai_package_report.md` reports ready
  with 17 ready checks and 0 failed checks.
- Full unit discovery passed with 143 tests. All strict local gates passed.
  `git diff --check` reported no whitespace errors beyond Windows line-ending
  warnings, and the raw-key scan produced no matches.

Evidence boundary:

- Phase 92 is SnapATAC2 skill/readiness evidence only. It does not implement
  a SnapATAC2 runner, does not materialize SNAP-T1/T2 fixture assets, does not
  run Summary/PaperToSkill rows, does not append SNAP raw rows, and does not
  add SNAP task scores to the paper.
- The current real-reuse effectiveness evidence is still only the partial
  REF-T1/REF-T2 GPT-family slice; AIDE, SWE-agent, and SnapATAC2 remain
  pending for downstream task scores.

## 2026-07-03 Phase 93

Actions:

- Added `scripts/prepare_real_reuse_snapatac2_fixture.py` to prepare locked
  SNAP-T1/T2 fixture assets from declared SnapATAC2 dataset manifests,
  expected artifact schemas, resource budgets, and scorer-only labels/proxies.
- Added `scripts/score_real_reuse_snapatac2.py` to score candidate
  `candidate_output.json` / `analysis_artifacts.json` files against runtime,
  memory, artifact-completion, and ARI/NMI-style contracts.
- Added `scripts/run_real_reuse_snapatac2.py` to run Summary and PaperToSkill
  conditions, save prompts/responses/metrics/raw rows when rows are scorable,
  and treat missing fixture assets, missing credentials, or provider/model
  errors as availability state.
- Added focused SnapATAC2 unit tests for fixture preparation, scorer behavior,
  runner fixture-response execution, pending availability states, and raw-row
  output.
- Extended real-reuse/package gates and table tests so SnapATAC2 now has a
  validated execution-layer contract and SNAP-T1/T2 table rows move to
  `Fixture pending`.

Results:

- `results/real_reuse/main_results_plan.{csv,md,json}` now reports SNAP-T1/T2
  as `Fixture pending`, with score cells still `Pending`.
- `paper/aaai/papertoskill_tables.tex` matches the generated real-reuse table,
  and `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 444
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 396 ready checks, 1 pending check,
  and 0 failed checks.
- Full unit discovery passed with 153 tests before documentation cleanup; all
  strict local gates passed. `git diff --check` reported no whitespace errors
  beyond Windows line-ending warnings, and the raw-key scan produced no
  matches.

Evidence boundary:

- Phase 93 is SnapATAC2 execution-layer readiness only. It does not materialize
  SNAP-T1/T2 fixture assets, does not run live Summary/PaperToSkill SNAP rows,
  does not append SNAP raw rows, and does not add SNAP task scores to the
  paper.
- The current real-reuse effectiveness evidence is still only the partial
  REF-T1/REF-T2 GPT-family slice; AIDE, SWE-agent, and SnapATAC2 remain
  pending for downstream task scores.

## 2026-07-03 Phase 94

Actions:

- Extended the SnapATAC2 preparer with `official_miniature_fixture`
  materialization mode.
- Materialized SNAP-T1/SNAP-T2 assets from the official local SnapATAC2
  checkout at revision `7be57442708694217e27c8654ecd38a0de194aa4`.
- Copied official repository miniature test fragments into
  `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz` and
  `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`.
- Wrote dataset manifests, scorer-only thresholds, SNAP-T2 proxy-label policy,
  task prompts, resource budgets, expected schemas, preprocessing notes, and
  Summary contexts.
- Updated SnapATAC2 scorer support for scorer-only success thresholds.
- Extended real-reuse/package gates so prepared SnapATAC2 assets are validated.
- Refreshed the real-reuse main table and AAAI table/PDF so SNAP-T1/T2 now
  show `Ready to run` with score cells still `Pending`.

Results:

- SNAP-T1 miniature fragment SHA256:
  `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`.
- SNAP-T2 miniature fragment SHA256:
  `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 462
  ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 415 ready checks, 1 pending check,
  and 0 failed checks.
- Full unit discovery passed with 155 tests. All strict local gates passed.

Evidence boundary:

- Phase 94 is SnapATAC2 fixture-readiness evidence only.
- The miniature assets are official repository smoke/test fixtures, not full
  pbmc5k or pbmc10k_multiome paper reproductions.
- No SNAP Summary/PaperToSkill rows were run, no SNAP raw rows were appended,
  and no SNAP task scores were added to the paper.

## 2026-07-03 Phase 95

Actions:

- Retried the Phase 94 remote save; `git push origin main` failed because
  GitHub port 443 was unreachable from the current environment.
- Ran `scripts/run_real_reuse_snapatac2.py` with GPT-family `gpt-5.5` for
  SNAP-T1/SNAP-T2 under Summary and PaperToSkill conditions.
- Appended four scored SNAP rows to `results/real_reuse/raw_rows.jsonl`.
- Regenerated `results/real_reuse/main_results_plan.{csv,md,json}`.
- Updated `paper/aaai/papertoskill_tables.tex` and
  `paper/aaai/papertoskill_aaai2027.tex` so the paper reports SNAP scores as
  failed dry-run evidence rather than pending cells or positive results.

Results:

- `results/real_reuse/snapatac2_run_report.md` reports `complete` with four
  scored rows.
- SNAP-T1 Summary/PaperToSkill: `0.000` / `0.500`; both failed the success
  threshold.
- SNAP-T2 Summary/PaperToSkill: `0.200` / `0.400`; both failed the success
  threshold.
- `results/real_reuse/main_results_plan.md` now reads 8 raw scored rows and
  fills REF-T1, REF-T2, SNAP-T1, and SNAP-T2.

Evidence boundary:

- Phase 95 is real GPT-family execution evidence for the locked SnapATAC2
  miniature-fixture tasks only.
- It is not a full SnapATAC2 paper reproduction and not evidence that
  PaperToSkill successfully completes non-agent omics tasks.
- It does provide an important failure boundary: PaperToSkill scored higher
  than Summary on both SNAP dry-run tasks, but no SNAP row succeeded because
  complete runtime, memory, and quality artifacts were missing.

## 2026-07-03 Phase 96

Actions:

- Removed the accidental copied SWE-T2 workspace from the PaperToSkill asset
  tree and rematerialized SWE-T2 in external-workspace mode against
  `D:\a_work\gitee\astropy__astropy`.
- Copied SWE-T2 gold/test patches into
  `benchmarks/real_reuse/assets/SWE-T2/scorer_only/` and updated the manifest
  so hidden scorer assets no longer point at temporary extraction paths.
- Fixed SWE patch scoring to resolve candidate and hidden test patch paths
  before running `git apply` inside the temporary scoring workspace.
- Ran focused SWE tests, validated the SWE-T2 gold scorer, and ran SWE-T2
  Summary/PaperToSkill with GPT-family `gpt-5.5`.
- Regenerated the real-reuse table data and updated the AAAI table/results
  narrative.

Results:

- Focused SWE tests passed: 8 tests.
- Gold scorer validation passed: `task_score=1.0`, `success=true`, hidden test
  patch applied, and both Astropy target tests passed.
- SWE-T2 Summary/PaperToSkill scored `0.000` / `1.000`.
- `results/real_reuse/swe_run_report.md` reports `complete` with two scored
  rows.
- `results/real_reuse/main_results_plan.md` now reads 10 raw scored rows and
  fills SWE-T2, REF-T1, REF-T2, SNAP-T1, and SNAP-T2.

Evidence boundary:

- This phase is one locked SWE-Bench Verified-style Astropy instance, not a
  full SWE-agent reproduction and not the full eight-task benchmark.
- SWE-T1 remains fixture-pending; AIDE still awaits the real Kaggle
  Spaceship Titanic `train.csv`; SNAP-T1/T2 remain failure-boundary evidence
  because both scored rows are below the success threshold.

## 2026-07-03 Phase 97

Actions:

- Processed the active AIDE handoff path first. `ok.txt` existed, but the
  official Kaggle Spaceship Titanic `train.csv`, Kaggle CLI/package, user
  `kaggle.json`, and Kaggle environment variables were still unavailable.
  Rewrote `C:\Users\19351\Desktop\tem\toHuman.md` to request the official
  dataset or local user-managed Kaggle setup, then removed `ok.txt`.
- Cloned and prepared the locked SQLFluff workspace for SWE-T1 at base commit
  `14e1a23a3166b9a645a16de96f694c77a5d4abb7`.
- Extended `scripts/prepare_real_reuse_swe_fixture.py` to materialize a SWE
  fixture from local SWE-bench parquet via `--swe-bench-parquet` and
  `--instance-id`, keeping gold/test patches under `scorer_only`.
- Extended `scripts/score_real_reuse_swe.py` to add `src/` to `PYTHONPATH`
  where present and to tolerate line-ending/space differences during
  `git apply`.
- Added a parquet-backed SWE preparer regression test.
- Materialized `benchmarks/real_reuse/assets/SWE-T1/`, validated the hidden
  gold scorer, and ran SWE-T1 Summary/PaperToSkill with GPT-family `gpt-5.5`.
- Regenerated the real-reuse main table data and updated the AAAI table/results
  narrative plus claim, queue, artifact, runbook, outline, and result-card
  evidence docs.

Results:

- `results/real_reuse/swe_t1_gold_metric.json` validates the SWE-T1 scorer with
  `task_score=1.0`.
- SWE-T1 Summary/PaperToSkill scored `0.000` / `0.000`; both generated patches
  failed to apply.
- `results/real_reuse/main_results_plan.md` now reads 12 raw scored rows and
  fills SWE-T1, SWE-T2, REF-T1, REF-T2, SNAP-T1, and SNAP-T2 while AIDE-T1/T2
  remain pending.

Evidence boundary:

- SWE-T1 is one locked SWE-Bench Lite-style SQLFluff instance, not a full
  SWE-agent reproduction and not a PaperToSkill success.
- The row is useful failure-boundary evidence: the scorer path works and the
  hidden gold patch passes, but both model-generated patches fail to apply.
- The full eight-task real-reuse benchmark remains incomplete because AIDE-T1
  and AIDE-T2 await the official Kaggle Spaceship Titanic `train.csv`.

## 2026-07-04 Phase 98

Actions:

- Materialized AIDE-T1 and AIDE-T2 from the official Kaggle Spaceship Titanic
  files supplied under
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\`.
- Validated the local AIDE scorer against baseline/weak-script checks.
- Ran AIDE-T1 and AIDE-T2 Summary/PaperToSkill once with the GPT-family
  `gpt-5.5` slot.
- Regenerated the real-reuse main table data and synchronized the AAAI
  manuscript, outline, draft, result cards, reports, and memory to the full
  eight-row first-pass state.

Results:

- The official `train.csv` has 8,693 rows and SHA256
  `17336D553F49EBDF6ECB266D2B5D3746E5DD308445F7C7864141C4F28D2A88D0`.
- AIDE-T1 Summary/PaperToSkill scored `0.000` / `0.000`.
- AIDE-T2 Summary/PaperToSkill scored `0.000` / `0.000`.
- Both AIDE rows failed because generated scripts exceeded the 60-second
  scorer budget.
- The first single-run GPT-family pass now covers all eight real-reuse task
  rows: AIDE-T1/T2, SWE-T1/T2, REF-T1/T2, and SNAP-T1/T2.

Evidence boundary:

- This phase completes the first eight-row real-reuse pass, but the outcome is
  mixed and failure-heavy: SWE-T2 is one positive PaperToSkill row, REF ties
  Summary, AIDE and SWE-T1 are scored failures, and SNAP rows remain below
  threshold.
- The result is downstream stress-test and failure-boundary evidence, not
  aggregate PaperToSkill advantage over Summary.
- Kaggle-derived AIDE CSV fixture files remain local and ignored by Git; only
  manifests, hashes, and derived scored rows are committed.

## 2026-07-04 Phase 99

Actions:

- Rechecked memory, the human-fidelity handoff state, and Git status after the
  discussion about whether other paper sections still needed modification.
- Updated `scripts/build_real_reuse_paper_tables.py` so generated Markdown and
  JSON evidence-boundary text no longer says "pending cells" after the first
  eight-row pass has scored all planned rows.
- Regenerated `results/real_reuse/main_results_plan.md` and
  `results/real_reuse/main_results_plan.json`.
- Added table-builder regression assertions that the generated evidence
  boundary uses "future unfilled cells are planning placeholders" and does not
  reintroduce "pending cells".

Results:

- The real-reuse score data is unchanged.
- Focused table-builder unit tests passed.
- Paper-table, paper-claim, and reproducibility-package strict checks passed
  before final phase verification.

Evidence boundary:

- This phase is status-wording hygiene only. It does not add new task rows,
  rerun models, or strengthen downstream effectiveness claims.

## 2026-07-04 Phase 100

Actions:

- Added `scripts/build_real_reuse_failure_analysis.py` to derive a row-level
  failure-boundary table from `results/real_reuse/raw_rows.jsonl`.
- Generated `results/real_reuse/failure_analysis.{csv,md,json}`.
- Added `tests/test_build_real_reuse_failure_analysis.py`.
- Added the failure-boundary table to `paper/aaai/papertoskill_tables.tex` and
  referenced it from the AAAI Results paragraph.
- Extended `scripts/check_paper_tables.py` so the new LaTeX table is checked
  against `results/real_reuse/failure_analysis.csv`.
- Added the new builder and result artifacts to
  `scripts/check_reproducibility_package.py`.
- Updated outline, artifact map, claim evidence matrix, runbook, rebuttal bank,
  result cards, and memory.
- Rebuilt the AAAI PDF.

Results:

- The derived table maps first-pass rows to boundary modes:
  AIDE-T1/T2 budget timeout; SWE-T1 patch application; SWE-T2
  PaperToSkill-only success; REF-T1/T2 solved by both; SNAP-T1/T2 artifact
  completion.
- Paper-table consistency now reports 196 ready checks and 0 failed checks.
- Reproducibility package now reports 419 ready checks, 1 pending check, and 0
  failed checks.

Evidence boundary:

- This phase does not rerun models or add new task-success evidence.
- The failure-boundary table is explanatory analysis over the existing
  first-pass raw rows and supports method-contract follow-up planning without
  claiming aggregate downstream effectiveness.

## 2026-07-04 Phase 101

Actions:

- Extended the existing human-fidelity packet builder so it also creates a
  reviewer-facing quickstart, checksum manifest, and shareable zip bundle:
  `results/human_fidelity_packets/human_fidelity_reviewer_bundle.zip`.
- The bundle contains the annotation guide, blank 24-row annotation template,
  and all four paper-specific review packets.
- Added package-gate checks for the reviewer bundle manifest and zip.
- Updated focused tests, the runbook, artifact map, memory, and the external
  `C:\Users\19351\Desktop\tem\toHuman.md` handoff.

Results:

- Focused human-fidelity/package tests passed.
- `scripts\summarize_human_fidelity_annotations.py --strict` still reports the
  blank annotation template as pending with no validation errors.
- `scripts\check_reproducibility_package.py --strict` reports
  `ready_with_pending_external_evidence`, 423 ready checks, 1 pending check,
  and 0 failed checks.

Evidence boundary:

- This phase improves reviewer handoff readiness only.
- It does not complete human annotation or strengthen paper claims.
- Human validation remains pending until all 24 annotation rows are scored by
  independent reviewers and validated by the strict summarizer.

## 2026-07-04 Phase 102

Actions:

- Re-read memory, checked `C:\Users\19351\Desktop\tem\ok.txt` and confirmed no
  human-fidelity completion signal was present.
- Re-ran the current goal/package/human-fidelity gates and confirmed the
  remaining pending items are still human-fidelity annotation and final AAAI
  submission readiness under the recorded wait-for-evidence policy.
- Updated `research/review_report.md` so the internal adversarial review now
  reflects the eight-row real-reuse first pass and derived failure-boundary
  table.
- Updated `research/submission_checklist.md` so the ready/not-ready evidence
  tables include real-reuse first-pass evidence and the boundary against broad
  downstream-effectiveness claims.
- Updated `research/rebuttal_bank.md` to refresh stale package counts.
- Regenerated `results/reproducibility/submission_review_report.{json,md}`.
- Added `research/run_logs/2026-07-04_phase102_submission_review_real_reuse_sync.md`.

Results:

- `scripts/check_submission_review.py --strict` passed with 16 ready checks and
  0 failed checks.
- `scripts/check_goal_completion.py --strict` still reports
  `not_complete_pending_external_evidence`, 77 ready checks, 3 pending checks,
  and 0 failed checks.
- `scripts/check_reproducibility_package.py --strict` still reports
  `ready_with_pending_external_evidence`, 423 ready checks, 1 pending check,
  and 0 failed checks.
- AAAI decision, external-evidence closure, external-evidence packets, and
  paper-claim strict checks passed.

Evidence boundary:

- This phase is review-handoff synchronization only.
- It does not add new real-reuse rows or task-success evidence.
- Human fidelity and final AAAI submission readiness remain pending.

## 2026-07-04 Phase 103

Actions:

- Audited the human-fidelity annotation path after confirming
  `C:\Users\19351\Desktop\tem\ok.txt` was absent.
- Found that the handoff allowed 1-2 independent reviewers, while the
  summarizer judged completion by raw CSV row count; appended second-reviewer
  rows could make a fully covered review look pending.
- Updated `scripts/summarize_human_fidelity_annotations.py` to judge
  completion by 24 paper-by-criterion cells, report `required_cells`,
  `scored_cells`, and `pending_cells`, allow distinct-reviewer duplicate rows,
  reject duplicate same-reviewer rows for the same cell, and require
  `needs_discussion` on scored rows.
- Updated packet-builder guidance, the human-fidelity protocol config,
  external-evidence packet wording, package/submission-review gates, runbook,
  artifact map, goal audit, memory, and external `toHuman.md` handoff.
- Regenerated the human-fidelity packet outputs, reviewer bundle, annotation
  summary, external-evidence packets, package report, goal-completion report,
  and submission-review report.

Results:

- Focused tests passed for the annotation summarizer, packet builder,
  reproducibility package gate, and submission-review gate.
- Strict checks passed for reproducibility package, goal completion,
  submission review, external evidence packets, external evidence closure,
  AAAI submission decision, and paper claims.
- Current human-fidelity summary remains pending with 24 required cells, 0
  scored cells, 24 pending cells, and 0 errors.

Evidence boundary:

- This phase improves the independent-review protocol and validator only.
- It does not complete human annotation or add task-success evidence.

## 2026-07-04 Phase 104

Actions:

- Added the auxiliary Full Excerpt sanity scaffold for AIDE-T1, SWE-T1, and
  SNAP-T1.
- Added `scripts/build_real_reuse_full_excerpt_sanity.py` and
  `tests/test_build_real_reuse_full_excerpt_sanity.py`.
- Generated `results/real_reuse/full_excerpt_sanity.{csv,md,json}`.
- Added `tab:full-excerpt-sanity` to the AAAI table file and a short setup
  paragraph in the AAAI draft.
- Extended paper-table and reproducibility-package gates for the new table and
  outputs.
- Updated research docs, result cards, review handoff files, and memory so the
  scaffold is not mistaken for completed Full Excerpt task-success evidence.
- Added `research/run_logs/2026-07-04_phase104_full_excerpt_sanity_scaffold.md`.

Results:

- Focused Full Excerpt/table/package tests passed: 6 tests.
- Full unit discovery passed: 164 tests.
- Strict paper table, paper claims, AAAI package, reproducibility package,
  goal completion, submission review, external evidence closure/packets, AAAI
  decision, usage examples, DeepSeek handoff, AI-Scientist-v2 live-run handoff,
  and real-reuse benchmark checks passed.
- `results/reproducibility/paper_table_report.md`: ready, 226 ready checks, 0
  failed checks.
- `results/reproducibility/package_report.md`:
  `ready_with_pending_external_evidence`, 427 ready checks, 1 pending check, 0
  failed checks.
- `git diff --check` passed with only Windows line-ending warnings.
- Raw-key scan found no matches.

Evidence boundary:

- This phase creates a reviewer-question/cost-context sanity scaffold only.
- Full Excerpt score cells remain pending; pending cells are not negative
  evidence.
- No task-success evidence or aggregate downstream-effectiveness claim is
  added.
