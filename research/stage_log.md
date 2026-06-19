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
