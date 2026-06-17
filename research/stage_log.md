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
