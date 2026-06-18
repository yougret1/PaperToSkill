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
