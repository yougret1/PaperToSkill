# Result Cards

## AI Scientist-v2 Paper-To-Skill Scaffold

- Experiment: deterministic scaffold on `papers/notes/ai_scientist_v2_note.md`.
- Main result: generated `generated_skills/ai_scientist_v2/SKILL.md` with a
  source map and source-anchored workflow, validation, and failure cases.
- Compared baselines: no baseline run yet; this is the first retained real-paper
  scaffold case.
- Practical significance: demonstrates that PaperToSkill can ingest a real
  paper-derived note and preserve operational workflow elements without remote
  LLM availability.
- Deterministic rubric: `results/evaluations/ai_scientist_v2_rubric_v0.json`
  scored 20/20.
- Rubric interpretation: v0 confirms required sections, source anchors,
  workflow keyword coverage, failure keyword coverage, and compactness under
  1200 words. It does not measure downstream task success or human fidelity.
- Failure modes: depends on human-created paper note quality; source anchors are
  line-level references into extracted text, not PDF page-level citations yet.
- Limitations: not a full-paper automatic extractor; no LLM-assisted fidelity
  audit; no downstream task run yet.
- Claim impact: supports the claim that the local scaffold can produce a
  compact, source-anchored, structurally valid paper-derived skill from a
  curated real-paper note. It does not yet prove downstream task improvement
  over summaries.
- Figure/table: none.

## AI Scientist-v2 Context Baseline Coverage

- Experiment: deterministic context coverage evaluation for
  `benchmarks/tasks/ai_scientist_v2_research_run.json`.
- Main result: the PaperToSkill-generated skill scored 7.867/9, compared with
  1.733/9 for a generic summary and 1.2/9 for abstract-only context.
- Compared baselines: `baselines/ai_scientist_v2_generic_summary.md` and
  `baselines/ai_scientist_v2_abstract_only.md`.
- Practical significance: the generated skill preserves more task-relevant
  operational details for planning an AI Scientist-v2-like research run,
  including stage management, node lifecycle, debug/refine policy, limitations,
  and source grounding.
- Statistical evidence: none yet; this is one deterministic task and one paper.
- Failure modes: keyword-based scoring can over-credit shallow mentions and
  under-credit paraphrases; it does not evaluate actual agent behavior.
- Limitations: not a human or LLM execution study; not yet a multi-paper
  benchmark; generic summary quality is hand-authored and may not represent all
  summarizers.
- Claim impact: supports a narrow form of the compactness/fidelity claim: on one
  source-grounded task rubric, the generated skill preserves more operational
  capabilities than summaries while staying under the compactness budget.
- Figure/table: `results/evaluations/ai_scientist_v2_context_baselines_v0.json`.

## AI Scientist-v2 Source-Map Audit

- Experiment: source-map-aware unsupported-instruction audit across
  `generated_skills/ai_scientist_v2`, `generated_skills/papertoskill_paper_note`,
  and `generated_skills/papertoskill_seed`.
- Main result: unsupported rate ranked the real AI Scientist-v2 skill lowest at
  0.2, the paper-like retained case at 0.222, and the abstract-only seed at 1.0.
- Compared baselines: the same two retained generated skills plus the
  abstract-only seed.
- Practical significance: the real paper-derived skill preserves most
  source-supported workflow/validation/failure content, while the abstract-only
  seed collapses under source-map audit. This is stronger evidence than keyword
  coverage alone that source mapping matters.
- Statistical evidence: none yet; this is a deterministic audit of three skills.
- Failure modes: the audit still uses token overlap and section mapping, so it
  can under-credit paraphrase-heavy yet valid instructions.
- Limitations: transfer-note bullets are still the hardest to score because they
  are often intentionally generic and may be supported by broader paper
  limitations rather than one exact section.
- Claim impact: supports the claim that source-map-aware auditing can
  discriminate between a real paper-derived skill and an abstract-only seed on
  unsupported-instruction rate.
- Figure/table: `results/evaluations/skill_source_audit_v0.json`.

## AI Scientist-v2 Harness Transfer Readiness

- Experiment: offline Codex/Claude-style transfer-readiness evaluation across
  the full generated skill, the same skill with `Transfer Notes` removed, and a
  generic summary baseline.
- Main result: the full generated skill scored 10.0/10 average readiness, the
  no-transfer-notes variant scored 7.6/10, and the generic summary scored
  1.2/10.
- Compared baselines: skill without transfer notes and generic prose summary.
- Practical significance: transfer notes contribute measurable portability
  signals beyond method coverage alone, including target-harness checks,
  framework-command adaptation, source-backed/inferred separation, and failed
  branch recording.
- Statistical evidence: none yet; this is a deterministic offline gate for one
  paper-derived skill.
- Failure modes: the metric is keyword/section based and can over-credit text
  that names transfer concepts without proving actual agent behavior.
- Limitations: does not replace live Codex-to-Claude or Claude-to-Codex task
  execution after the remote provider recovers.
- Claim impact: partially supports the harness-transfer claim only at the
  artifact-readiness level.
- Figure/table: `results/evaluations/ai_scientist_v2_harness_transfer_v0.json`.

## AI Scientist-v2 Source-Span Validation

- Experiment: validate source anchors in the AI Scientist-v2 generated skill
  against extracted paper text line spans.
- Main result: 15 of 16 claims were supported and 1 was weak; no invalid line
  ranges were found.
- Compared baselines: none; this is an internal consistency audit.
- Practical significance: confirms that the source anchors in the retained
  skill mostly point to actual supporting spans, which makes later audit and
  transfer work more trustworthy.
- Statistical evidence: none; deterministic line-span audit only.
- Failure modes: one claim about citation inaccuracies scored weak because the
  extracted span was semantically supportive but lexically sparse.
- Limitations: still not a human fact-check and still sensitive to paraphrase or
  OCR noise.
- Claim impact: strengthens the source-grounding claim for the generated
  skill.
- Figure/table: `results/evaluations/ai_scientist_v2_source_span_validation_v0.json`.

## Reflexion Paper-To-Skill Scaffold

- Experiment: deterministic scaffold on `papers/notes/reflexion_note.md`.
- Main result: generated `generated_skills/reflexion/SKILL.md` with source-
  anchored workflow, validation, failure cases, and transfer notes.
- Compared baselines: no summary baseline yet; this is the second retained
  real-paper scaffold case.
- Practical significance: extends PaperToSkill beyond AI Scientist-v2 to a
  different agent-method paper centered on failure reflection, episodic memory,
  and verbal reinforcement.
- Deterministic rubric: `results/evaluations/reflexion_rubric_v0.json` scored
  20/20.
- Source-span validation: `results/evaluations/reflexion_source_span_validation_v0.json`
  found 11/11 supported anchored claims with 0 invalid ranges.
- Failure modes: relies on a curated note rather than full automatic PDF
  extraction; rubric is paper-specific.
- Limitations: still no downstream live agent run or summary baseline for
  Reflexion.
- Claim impact: supports the claim that PaperToSkill can convert more than one
  real agent-method paper into a compact, source-grounded skill.
- Figure/table: `results/evaluations/reflexion_rubric_v0.json`;
  `results/evaluations/reflexion_source_span_validation_v0.json`.

## Reflexion Context Baseline Coverage

- Experiment: deterministic context coverage evaluation for
  `benchmarks/tasks/reflexion_research_run.json`.
- Main result: the PaperToSkill-generated Reflexion skill scored 8.267/9,
  compared with 3.483/9 for a generic summary and 2.533/9 for abstract-only
  context.
- Compared baselines: `baselines/reflexion_generic_summary.md` and
  `baselines/reflexion_abstract_only.md`.
- Practical significance: the generated skill preserves the actor/evaluator/
  self-reflection role split, memory split, feedback sources, validation
  domains, limitations, and source grounding better than short summaries.
- Statistical evidence: none; this is a deterministic task for one paper.
- Failure modes: keyword scoring can still over-credit exact phrasing and
  under-credit paraphrases.
- Limitations: not live agent task success.
- Claim impact: strengthens the deterministic multi-paper coverage claim.
- Figure/table: `results/evaluations/reflexion_context_baselines_v0.json`.

## Reflexion Harness Transfer Readiness

- Experiment: offline Codex/Claude-style transfer-readiness evaluation across
  the full Reflexion skill, the same skill with `Transfer Notes` removed, and a
  generic summary baseline.
- Main result: the full generated skill scored 10.0/10 average readiness, the
  no-transfer-notes variant scored 7.6/10, and the generic summary scored
  2.25/10.
- Compared baselines: skill without transfer notes and generic prose summary.
- Practical significance: the same transfer-note ablation pattern seen on
  AI Scientist-v2 also appears for Reflexion, suggesting the portability signal
  is not limited to one paper.
- Statistical evidence: none; deterministic offline gate only.
- Failure modes: does not prove live Codex-to-Claude or Claude-to-Codex success.
- Limitations: prompt packets are ready, but live responses are still blocked by
  remote provider availability.
- Claim impact: partially supports the harness-transfer claim at the offline
  artifact-readiness level across two papers.
- Figure/table: `results/evaluations/reflexion_harness_transfer_v0.json`.

## Paper-Ready Result Table Aggregation

- Experiment: aggregate existing deterministic/offline JSON evaluations into
  Markdown and CSV tables for paper drafting.
- Main result: generated `results/tables/main_results.md`,
  `results/tables/transfer_ablation.md`,
  `results/tables/compactness_source_grounding.md`, and
  `results/tables/paper_ready_summary.md`.
- Compared baselines: none; this is an analysis artifact over previously run
  baselines and ablations.
- Practical significance: gives the paper draft stable result tables for main
  coverage, transfer-note ablation, compactness, and source-grounding claims
  without manual number copying.
- Statistical evidence: none; all source metrics are deterministic/offline.
- Failure modes: table quality depends on the upstream JSON schemas and current
  benchmark coverage. Reflexion lacks the older source-map unsupported-
  instruction audit, so that cell is `n/a`.
- Limitations: does not add live cross-harness execution evidence or human
  fidelity annotation.
- Claim impact: improves traceability from claims to results but does not
  strengthen the empirical claims beyond existing evidence.
- Figure/table: `results/tables/paper_ready_summary.md`.

## AIDE Paper-To-Skill Scaffold

- Experiment: deterministic scaffold on `papers/notes/aide_note.md`.
- Main result: generated `generated_skills/aide/SKILL.md` with source-anchored
  workflow, validation, failure cases, and transfer notes.
- Compared baselines: no separate scaffold baseline; downstream baselines are
  covered in the AIDE context baseline card.
- Practical significance: extends PaperToSkill to a code-space tree-search
  paper centered on solution trees, draft/debug/improve actions, performance
  records, context summarization, data previews, and cost/contamination limits.
- Deterministic rubric: `results/evaluations/aide_rubric_v0.json` scored
  20/20.
- Source-span validation: `results/evaluations/aide_source_span_validation_v0.json`
  found 21/21 supported anchored claims with 0 invalid ranges.
- Failure modes: the initial extraction capped method/failure bullets too low
  and dropped `data preview` plus LLM-cost content. The extractor limit was
  increased and a regression test was added.
- Limitations: still depends on a curated paper note and deterministic lexical
  checks.
- Claim impact: supports the claim that PaperToSkill can convert a third,
  structurally different agent-method paper into a compact source-grounded
  skill.
- Figure/table: `results/evaluations/aide_rubric_v0.json`;
  `results/evaluations/aide_source_span_validation_v0.json`.

## AIDE Context Baseline Coverage

- Experiment: deterministic context coverage evaluation for
  `benchmarks/tasks/aide_research_run.json`.
- Main result: the PaperToSkill-generated AIDE skill scored 9.1/10, compared
  with 1.916/10 for a generic summary and 1.333/10 for abstract-only context.
- Compared baselines: `baselines/aide_generic_summary.md` and
  `baselines/aide_abstract_only.md`.
- Practical significance: the generated skill preserves solution-tree search,
  objective-function framing, draft/debug/improve policy, summarization, data
  preview, benchmark evidence, limitations, and source grounding better than
  short summaries.
- Statistical evidence: none; deterministic task only.
- Failure modes: keyword scoring can under-credit equivalent paraphrases and
  does not evaluate actual coding-agent behavior.
- Limitations: not live agent task success.
- Claim impact: strengthened the deterministic multi-paper coverage claim
  before the Toolformer extension.
- Figure/table: `results/evaluations/aide_context_baselines_v0.json`.

## AIDE Harness Transfer Readiness

- Experiment: offline Codex/Claude-style transfer-readiness evaluation across
  the full AIDE skill, the same skill with `Transfer Notes` removed, and a
  generic summary baseline.
- Main result: the full generated skill scored 10.0/10 average readiness, the
  no-transfer-notes variant scored 7.6/10, and the generic summary scored
  1.5/10.
- Compared baselines: skill without transfer notes and generic prose summary.
- Practical significance: the same transfer-note ablation pattern now holds for
  a third paper and a coding/ML-engineering workflow.
- Statistical evidence: none; deterministic offline gate only.
- Failure modes: still artifact-readiness rather than live transfer success.
- Limitations: live prompt packets are ready but remote chat completion returned
  HTTP 503.
- Claim impact: partially supported the harness-transfer claim at the offline
  artifact-readiness level before the Toolformer extension.
- Figure/table: `results/evaluations/aide_harness_transfer_v0.json`.

## Toolformer Paper-To-Skill Scaffold

- Experiment: deterministic scaffold on `papers/notes/toolformer_note.md`.
- Main result: generated `generated_skills/toolformer/SKILL.md` with source-
  anchored workflow, validation, failure cases, and transfer notes for
  self-supervised tool-use data generation.
- Compared baselines: no separate scaffold baseline; downstream baselines are
  covered in the Toolformer context baseline card.
- Practical significance: extends PaperToSkill beyond research, reflection, and
  coding workflows to a tool-use/API-contract paper.
- Deterministic rubric: `results/evaluations/toolformer_rubric_v0.json` scored
  20/20.
- Source-span validation: `results/evaluations/toolformer_source_span_validation_v0.json`
  found 22/22 supported anchored claims with 0 invalid ranges.
- Failure modes: still depends on a curated paper note and deterministic
  lexical checks; Toolformer is procedural, so it does not resolve the
  theory-heavy benchmark gap.
- Limitations: not live tool execution and not a human fidelity annotation.
- Claim impact: strengthens benchmark diversity by adding a tool-use stress
  case while preserving the curated-note/offline evidence boundary.
- Figure/table: `results/evaluations/toolformer_rubric_v0.json`;
  `results/evaluations/toolformer_source_span_validation_v0.json`.

## Toolformer Context Baseline Coverage

- Experiment: deterministic context coverage evaluation for
  `benchmarks/tasks/toolformer_research_run.json`.
- Main result: the PaperToSkill-generated Toolformer skill scored 8.9/10,
  compared with 2.5/10 for a generic summary and 1.534/10 for abstract-only
  context.
- Compared baselines: `baselines/toolformer_generic_summary.md` and
  `baselines/toolformer_abstract_only.md`.
- Practical significance: the generated skill preserves API-call
  representation, few-demonstration prompting, sample/execute/filter data
  construction, fine-tuning, inference-time execution, tool-suite coverage, and
  limitations better than short summaries.
- Statistical evidence: none; deterministic task only.
- Failure modes: keyword scoring can under-credit equivalent paraphrases and
  does not evaluate actual tool execution.
- Limitations: not live agent task success.
- Claim impact: strengthens the deterministic multi-paper coverage claim across
  four real paper cases.
- Figure/table: `results/evaluations/toolformer_context_baselines_v0.json`.

## Toolformer Harness Transfer Readiness

- Experiment: offline Codex/Claude-style transfer-readiness evaluation across
  the full Toolformer skill, the same skill with `Transfer Notes` removed, and
  a generic summary baseline.
- Main result: the full generated skill scored 10.0/10 average readiness, the
  no-transfer-notes variant scored 7.6/10, and the generic summary scored
  1.45/10.
- Compared baselines: skill without transfer notes and generic prose summary.
- Practical significance: the transfer-note ablation pattern now also holds for
  a tool-use paper with explicit API contracts.
- Statistical evidence: none; deterministic offline gate only.
- Failure modes: offline readiness remains artifact-readiness rather than live
  outcome evidence.
- Limitations: the Toolformer live-transfer response set is now saved and
  scored separately, but this card's metric is still deterministic offline
  readiness.
- Claim impact: partially supports the harness-transfer claim at the offline
  artifact-readiness level across four papers.
- Figure/table: `results/evaluations/toolformer_harness_transfer_v0.json`.

## Toolformer Live-Transfer Responses

- Experiment: run the six Toolformer live-transfer prompt packets across
  Codex-style and Claude-style harness prompts and three context variants using
  the Claude-family OpenAI-compatible endpoint.
- Main result: `results/live_transfer_prompts/toolformer_v0/run_report.md`
  reports `overall_status=complete`, 6 successes, 0 errors, catalog status
  `success`, 14 listed models, and exact alias `claude-opus-4-8`.
- Response evaluation: all six Toolformer rows score 9/9 in
  `results/live_transfer_prompts/evaluation.md`.
- Compared baselines: full skill, skill without `Transfer Notes`, and generic
  summary contexts are all present in the current Toolformer live response set;
  this phase does not yet aggregate a live success-rate comparison.
- Practical significance: this was the first complete paper response set and
  established reusable live-transfer execution and saved-response scoring
  infrastructure.
- Statistical evidence: none; deterministic output-contract scoring over six
  saved responses.
- Failure modes: keyword-style output-contract scoring can over-credit text
  that names required concepts without independently proving task execution
  quality.
- Limitations: this is not human semantic fidelity, provider billing, or live
  task-success evidence.
- Claim impact: supports saying the Toolformer live-transfer response set is
  saved and scored under the deterministic output-contract evaluator.
- Figure/table: `scripts/run_live_transfer_prompts.py`;
  `scripts/evaluate_live_transfer_responses.py`;
  `research/run_logs/2026-06-19_phase39_toolformer_live_transfer.md`;
  `results/live_transfer_prompts/toolformer_v0/run_report.md`;
  `results/live_transfer_prompts/evaluation.md`.

## All Paper Live-Transfer Saved Responses

- Experiment: run the AI Scientist-v2, Reflexion, and AIDE live-transfer prompt
  packets after the earlier Toolformer run, then rescore all four paper packets.
- Main result: `results/live_transfer_prompts/evaluation.md` reports 24 total
  rows, 24 scored rows, 0 pending rows, and average normalized score 1.0.
- Per-paper results: AI Scientist-v2, Reflexion, and AIDE rows score 11/11
  each; Toolformer rows score 9/9 each.
- Run reports: AI Scientist-v2 and Reflexion each completed 6/6 rows with
  `claude-opus-4-8`; AIDE completed 6/6 rows with one fallback from
  `claude-opus-4-8` to `claude-opus-4-7` after a remote connection closure.
- Practical significance: the project now has complete saved-response coverage
  for the current live-transfer prompt-packet protocol across both harness
  prompt styles and all three context variants.
- Statistical evidence: deterministic output-contract scoring over 24 saved
  responses; no human semantic annotation or success-rate estimate.
- Failure modes: provider alias availability can affect the alias used for a
  saved response; the AIDE fallback is provider evidence, not model-quality
  failure evidence.
- Limitations: saved-response output-contract scoring is not human semantic
  fidelity, real live task success, provider billing, DeepSeek evidence, or
  final submission readiness.
- Claim impact: supports saying all four current live-transfer response sets
  are saved and scored, while preserving the boundary that stronger live task
  and human-fidelity evidence remain pending.
- Figure/table: `research/run_logs/2026-06-19_phase40_all_live_transfer_responses.md`;
  `results/live_transfer_prompts/ai_scientist_v2_v0/run_report.md`;
  `results/live_transfer_prompts/reflexion_v0/run_report.md`;
  `results/live_transfer_prompts/aide_v0/run_report.md`;
  `results/live_transfer_prompts/toolformer_v0/run_report.md`;
  `results/live_transfer_prompts/evaluation.md`.

## Paper Draft Package

- Experiment: convert the validated deterministic/offline evidence into
  paper-facing artifacts.
- Main result: created `paper/outline.md`, `paper/draft.md`,
  `paper/claim_checklist.md`, and `paper/limitations.md`.
- Compared baselines: none; this is a synthesis artifact over existing result
  tables, claim evidence, and result cards.
- Practical significance: gives the project a coherent paper narrative while
  preventing overclaiming. The claim checklist explicitly separates supported
  deterministic/offline statements from pending live-agent claims.
- Statistical evidence: none; no new experiment was run for this card.
- Failure modes: draft quality depends on the current benchmark scope and may
  need revision after live cross-harness runs or human fidelity annotation.
- Limitations: the draft is a working paper package, not a submission-ready
  manuscript.
- Claim impact: improves claim discipline and makes missing evidence visible
  without strengthening the empirical claims.
- Figure/table: `paper/outline.md`; `paper/claim_checklist.md`;
  `paper/draft.md`; `paper/limitations.md`.

## Context Cost Proxy

- Experiment: context-size and cost-proxy analysis over full extracted paper
  text, curated paper notes, generated skills, generic summaries, and
  abstract-only baselines for the real-paper cases.
- Main result: under `o200k_base`, generated skills use 1,079 input tokens vs
  45,212 for the full AI Scientist-v2 extracted paper, 703 vs 16,414 for
  Reflexion, 1,285 vs 13,312 for AIDE, and 1,255 vs 20,365 for Toolformer.
- Compared baselines: full extracted paper, curated note, generated skill,
  generic summary, and abstract-only context. Coverage-per-budget rows are
  limited to the already evaluated skill, generic summary, and abstract-only
  contexts.
- Practical significance: generated skills compress full extracted paper text by
  97.61%, 95.72%, 90.35%, and 93.84% under the tokenizer-aware proxy while
  preserving much higher deterministic coverage than generic summaries or
  abstract-only contexts. The original `ceil(characters / 4)` proxy remains as a
  reproducible sensitivity check.
- Statistical evidence: none; this is deterministic accounting.
- Failure modes: the tokenizer-aware proxy is exact for the local `o200k_base`
  tokenizer, but the configurable cost number is still a scaling proxy, not a
  provider invoice or success-per-dollar measurement. Output-token accounting
  for saved model responses is tracked separately in
  `results/tables/model_response_cost_proxy.md`.
- Limitations: summary and abstract contexts are smaller than generated skills
  but lose substantial deterministic coverage, so the supported claim is
  coverage-preserving compression relative to full paper context rather than
  shortest context overall.
- Claim impact: upgrades compactness from word-count-only evidence to
  character-proxy and tokenizer-aware token/cost proxy evidence while preserving
  the no-real-billing boundary.
- Figure/table: `results/tables/context_cost_proxy.md`;
  `results/tables/context_cost_proxy.csv`;
  `results/tables/coverage_cost_efficiency.csv`;
  `results/tables/context_cost_proxy.json`;
  `results/tables/context_cost_proxy_tokenizer.md`;
  `results/tables/context_cost_proxy_tokenizer.csv`;
  `results/tables/coverage_cost_efficiency_tokenizer.csv`;
  `results/tables/context_cost_proxy_tokenizer.json`.

## Human-Fidelity Review Readiness

- Experiment: prepare human-fidelity review packets for the generated
  real-paper skills after re-testing the remote LLM endpoint.
- Main result: `/v1/models` worked and listed `claude-opus-4-8`, but
  `/v1/chat/completions` returned HTTP 503 with an empty body. Because live
  transfer remains blocked, Phase 13 added `benchmarks/human_fidelity_review_v0.json`,
  `scripts/build_human_fidelity_packets.py`, and review packets under
  `results/human_fidelity_packets/`.
- Compared baselines: no empirical baseline; packets include generated skill,
  curated source note excerpt, source-span support rate, invalid ranges,
  deterministic coverage score, and six review criteria.
- Practical significance: human-fidelity review is now operationally ready
  without overstating evidence. The annotation template has 24 blank rows
  covering 4 papers x 6 criteria, and Phase 42 adds a reviewer handoff guide
  plus required `evidence_locator`, `confidence_0_to_1`, and
  `needs_discussion` fields.
- Statistical evidence: none; no annotation has been completed.
- Failure modes: packet quality depends on curated notes and source-map
  structure. Independent reviewers still need to fill the annotation template.
- Limitations: this is review readiness, not human-validated skill fidelity.
- Claim impact: upgrades the human-fidelity gap from an undefined future task
  to a prepared protocol with pending annotations.
- Figure/table: `benchmarks/human_fidelity_review_v0.json`;
  `results/human_fidelity_packets/README.md`;
  `results/human_fidelity_packets/annotation_guide.md`;
  `results/human_fidelity_packets/annotation_template.csv`.

## Human-Fidelity Annotation Summary

- Experiment: add a deterministic summarizer for the human-fidelity annotation
  template.
- Main result: `scripts/summarize_human_fidelity_annotations.py` reports
  `annotation_status=pending`, 24 total rows, 0 scored rows, 24 pending rows,
  average confidence `n/a`, 0 discussion rows, and 0 validation errors for the
  current blank template.
- Compared baselines: none; this is provenance and validation infrastructure for
  future human annotations.
- Practical significance: once independent reviewers fill the template, the same
  script can summarize per-paper and per-criterion scores and catch missing
  evidence locators, evidence notes, confidence values, reviewer IDs, review
  dates, and malformed discussion flags.
- Statistical evidence: none; no annotation has been completed.
- Failure modes: the summary is only as valid as the human-filled CSV; it does
  not judge fidelity by itself.
- Limitations: current output supports only the claim that human annotation is
  prepared and pending.
- Claim impact: makes the human-fidelity evidence boundary machine-readable and
  harder to accidentally overstate.
- Figure/table: `results/human_fidelity_packets/annotation_summary.md`;
  `results/human_fidelity_packets/annotation_summary.json`.

## Failure-Case Archive

- Experiment: aggregate paper-reported failure/limitation cases from the four
  source maps and project-level failure/fix records from the PaperToSkill
  development history.
- Main result: `results/failure_cases/failure_case_archive.md` records 27
  cases: 21 paper-reported cases and 6 project-level cases.
- Compared baselines: no empirical baseline; this is a provenance artifact
  against a success-only research narrative.
- Practical significance: the archive makes failed branches inspectable and
  keeps limitations, endpoint failures, evaluator bugs, extraction recall
  issues, and missing evidence visible to the paper draft.
- Statistical evidence: none; the counts are deterministic archive summaries.
- Failure modes: archive quality depends on source-map failure coverage and
  accurate project records.
- Limitations: this is not a controlled study showing that failure recording
  improves final user outcomes or live reproduction success.
- Claim impact: supports the claim that PaperToSkill treats failed branches as
  first-class provenance, while preserving the evidence boundary.
- Figure/table: `benchmarks/failure_case_archive_v0.json`;
  `results/failure_cases/failure_case_archive.md`;
  `results/failure_cases/failure_case_archive.json`.

## Reproducibility Package Gate

- Experiment: check local artifact package readiness across memory, paper
  draft files, result tables, generated skills, source maps, deterministic
  evaluations, prompt packets, human-fidelity packet status, failure archive,
  and secret scan.
- Main result: `results/reproducibility/package_report.md` should report
  `overall_status=ready_with_pending_external_evidence` after dependent gates
  are refreshed in order. The latest intended package state is 427 ready
  checks, 1 pending check, and 0 failed checks; stale failure states usually
  indicate report refresh ordering around the AAAI decision gate.
- Compared baselines: unchecked artifact bundle.
- Practical significance: the package is locally reviewable while making the
  remaining external gaps explicit. AI-Scientist-v2 bounded smoke/full-run
  evidence, DeepSeek saved-response rows, model-ablation scoring, and local
  token accounting are complete for their bounded roles. Human-fidelity
  annotation remains pending. Provider billing and success-per-dollar are
  outside the current claim set.
- Statistical evidence: none; this is a deterministic reproducibility gate.
- Failure modes: the checker verifies package presence and key consistency
  gates, but it does not replace running live agents or collecting independent
  human scores.
- Limitations: readiness does not mean submission-final evidence.
- Claim impact: supports local reproducibility readiness while preserving the
  live/human evidence boundary.
- Figure/table: `scripts/check_reproducibility_package.py`;
  `results/reproducibility/package_report.md`;
  `results/reproducibility/package_report.json`.

## AI-Scientist-v2 LLM-Client Smoke

- Experiment: run one bounded chat-completion smoke through the local
  AI-Scientist-v2 `ai_scientist.llm` client using OpenAI-compatible provider
  profiles, with an optional tiny-request max-token cap.
- Main result: `results/ai_scientist_v2_smoke/run_report.md` reports
  `overall_status=complete`, `model=claude-opus-4-8`, 6 ready checks, 0
  pending checks, and 0 failed checks. A saved marker response satisfies the
  tiny PaperToSkill smoke contract.
- Provider outcome: earlier provider 403/502/503 and timeout diagnostics remain
  historical availability evidence. The current bounded smoke path is complete;
  protocol-specific direct probes remain useful only for future provider
  diagnosis.
- Practical significance: records that the local AI-Scientist-v2 client path is
  wired into PaperToSkill with a reproducible smoke command and a saved
  contract-satisfying marker response.
- Failure modes: provider account exhaustion, model unavailability, endpoint
  errors, or endpoint timeouts can block the smoke independently of
  PaperToSkill logic.
- Limitations: this is not BFTS, not live research-task success, and not human
  semantic validation.
- Claim impact: supports saying the bounded AI-Scientist-v2 LLM-client smoke
  is complete for a tiny marker contract, while preserving that it is not broad
  task-success evidence.
- Figure/table: `scripts/run_ai_scientist_v2_smoke.py`;
  `results/ai_scientist_v2_smoke/run_report.md`;
  `results/ai_scientist_v2_smoke/run_report.json`;
  `results/openai_compatible_direct_probe/claude_family/run_report.md`;
  `results/openai_compatible_direct_probe/gpt_family/run_report.md`;
  `research/run_logs/2026-06-20_phase59_openai_direct_probe.md`.

## AI-Scientist-v2 Full Live-Run Handoff

- Experiment: check the bounded full AI-Scientist-v2 live/BFTS run handoff and
  completion artifacts.
- Main result: `results/ai_scientist_v2_live_run_handoff/handoff.md` reports
  `overall_status=complete`, 16 ready checks, 0 pending checks, 0 failed
  checks, and one completion directory.
- Checks: AI-Scientist-v2 root, launcher, dry-run/skip flags, laptop-profile
  config, PaperToSkill seed idea, prior dry-run artifacts, environment variable
  names, smoke-completion evidence, completion artifacts, and best-node
  consistency.
- Practical significance: records that AI-Scientist-v2 can run the bounded
  PaperToSkill integration path and produce synthetic sensitivity evidence.
- Failure modes: the real-data/HF semantic branch remains failed because of
  invalid dataset loading/synthetic padding and missing `sentence_transformers`;
  this limits the evidence to bounded integration/synthetic sensitivity.
- Limitations: this is not human semantic validation, not real-data validation,
  and not broad live research-task success.
- Claim impact: supports bounded AI-Scientist-v2 integration/synthetic evidence
  only.
- Figure/table: `scripts/check_ai_scientist_v2_live_run_handoff.py`;
  `results/ai_scientist_v2_live_run_handoff/handoff.md`;
  `results/ai_scientist_v2_live_run_handoff/handoff.json`.

## Usage Example Verification Gate

- Experiment: add a machine-checkable gate for paper-facing usage examples.
- Main result: `results/reproducibility/usage_example_report.md` reports
  `overall_status=ready`, 53 ready checks, and 0 failed checks.
- Checks: usage docs, Codex-style Toolformer skill inputs, model-ablation prompt
  grid, model slots, response slots, a scored Toolformer Codex-style
  live-transfer response slot, the aggregate live-transfer saved-response
  evaluation, DeepSeek handoff readiness, an offline AIDE
  extracted-text-to-note-to-skill chain, a one-command AIDE pipeline run, and a
  direct-PDF pipeline smoke run.
- Offline example: the temporary AIDE chain selected 6 method windows, 6
  experiment windows, and 5 limitation windows, then produced a generated skill
  scoring 20/20 on the AIDE deterministic rubric.
- Pipeline example: the temporary one-command AIDE pipeline manifest produced a
  note, source map, skill, and rubric report, also scoring 20/20.
- PDF pipeline smoke example: the temporary PDF pipeline run extracts text from
  `paper/aaai/papertoskill_aaai2027.pdf` with `pdftotext -layout` and records
  the extracted text path in the manifest.
- Practical significance: the experiments section now has examples that are not
  only described in Markdown but also locally checked for runnable inputs and
  output slots; the Toolformer Codex-style response slot is also checked
  against the saved live-transfer response evaluation.
- Failure modes: the checker does not make additional Claude/GPT/DeepSeek calls
  and does not prove model-response quality or human usability.
- Limitations: user-facing qualitative evaluation, human semantic fidelity,
  DeepSeek, and provider billing remain pending.
- Claim impact: strengthens the local usage-example readiness claim while
  preserving the live-model and arbitrary-PDF automation evidence boundaries.
- Figure/table: `scripts/check_usage_examples.py`;
  `results/reproducibility/usage_example_report.md`;
  `results/reproducibility/usage_example_report.json`.

## AAAI Package Verification Gate

- Experiment: add an automated local gate for the AAAI-27 paper package and
  generated build artifacts.
- Main result: `results/reproducibility/aaai_package_report.md` reports
  `overall_status=ready`, 17 ready checks, and 0 failed checks.
- Checks: required AAAI files, author-kit SHA256, `aaai2027` declaration and
  log load marker, fresh PDF/log/BibTeX outputs, PDF page/byte output marker,
  and unresolved citation/reference/build markers.
- Practical significance: the final-paper package is no longer only a set of
  files; it has a reproducible local verification gate that can fail on stale
  PDF artifacts or unresolved references.
- Failure modes: this does not judge paper quality, venue compliance beyond the
  checked package/build markers, or whether the manuscript is submission-final.
- Limitations: a passing check depends on local generated build artifacts and
  does not replace re-running the full LaTeX toolchain after future TeX edits.
- Claim impact: strengthens the claim that the requested AAAI TeX package is
  prepared and locally verifiable, while preserving the no-acceptance boundary.
- Figure/table: `scripts/check_aaai_package.py`;
  `results/reproducibility/aaai_package_report.md`;
  `results/reproducibility/aaai_package_report.json`.

## Paper Table Consistency Gate

- Experiment: add an automated local gate that compares AAAI LaTeX table values
  with the generated CSV result tables.
- Main result: `results/reproducibility/paper_table_report.md` reports
  `overall_status=ready`, 76 ready checks, and 0 failed checks.
- Checks: main deterministic/offline results, transfer-note ablation,
  tokenizer-aware cost proxy, and curated-vs-auto note comparison.
- Practical significance: the AAAI manuscript tables can now fail loudly if a
  displayed number drifts from the reproducible result tables.
- Failure modes: the checker parses the current table structure and should be
  updated if table labels, row order, or column layout are intentionally
  redesigned.
- Limitations: this is manuscript consistency evidence, not a new experiment,
  live model result, human-fidelity annotation, or provider-billing result.
- Claim impact: strengthens paper-package reliability while preserving the
  existing empirical evidence boundary.
- Figure/table: `scripts/check_paper_tables.py`;
  `results/reproducibility/paper_table_report.md`;
  `results/reproducibility/paper_table_report.json`.

## Paper Claim Discipline Gate

- Experiment: add an automated local gate that scans paper-facing text for
  unsupported overclaims and required evidence-boundary statements.
- Main result: `results/reproducibility/paper_claim_report.md` reports
  `overall_status=ready`, 30 ready checks, and 0 failed checks.
- Checks: absence of unsupported positive claims about arbitrary-PDF
  automation, live transfer success, human validation, provider billing,
  completed model ablations, and submission-final status; absence of
  paper-facing draft/planning language in the AAAI body, AAAI table file, and
  Markdown draft; presence of required boundaries for curated scope, PDF
  automation, live transfer, human fidelity, cost proxy, and model-ablation
  availability.
- Practical significance: the AAAI manuscript, AAAI table file, and Markdown
  draft can now fail a local gate if future edits accidentally claim evidence
  that has not been collected or reintroduce planning placeholders.
- Failure modes: this is pattern-based text checking and should be updated if
  the paper adopts new terminology for the same evidence boundaries.
- Limitations: this does not evaluate paper quality and does not add live
  model, human-fidelity, provider-billing, or arbitrary-PDF evidence.
- Claim impact: strengthens claim discipline while preserving all current
  empirical boundaries.
- Figure/table: `scripts/check_paper_claims.py`;
  `results/reproducibility/paper_claim_report.md`;
  `results/reproducibility/paper_claim_report.json`.

## Review And Rebuttal Package

- Experiment: run an internal adversarial review and prepare an evidence-bounded
  rebuttal bank for likely reviewer objections.
- Main result: `research/review_report.md` identifies eight major risks, and
  `research/rebuttal_bank.md` maps likely questions to evidence and prohibited
  overclaims.
- Compared baselines: no review package.
- Practical significance: converts known weaknesses into explicit claim
  boundaries and next experiments, especially around summarization, curated
  notes, heuristic metrics, live transfer, human fidelity, cost, and failure
  archive interpretation.
- Statistical evidence: none; this is a review/readiness artifact.
- Failure modes: the report depends on the current draft and artifact package;
  it should be refreshed after live or human evidence changes.
- Limitations: it does not add empirical evidence or remove the pending live
  and human-validation gaps.
- Claim impact: improves submission readiness and reduces overclaim risk.
- Figure/table: `research/review_report.md`; `research/rebuttal_bank.md`.

## Deterministic Auto-Note Scaffold

- Experiment: convert `papers/extracted/toolformer.txt` and
  `papers/extracted/aide.txt` directly into source-anchored Markdown notes, then
  convert those auto-notes into retained skills.
- Main result: generated `papers/auto_notes/toolformer_auto_note.md`,
  `generated_skills/toolformer_auto/SKILL.md`,
  `papers/auto_notes/aide_auto_note.md`, and
  `generated_skills/aide_auto/SKILL.md`.
- Compared baselines: curated Toolformer/AIDE note-derived skills, generic
  summaries, and abstract-only contexts.
- Practical significance: reduces the curated-note bottleneck by producing an
  auditable text-to-note scaffold with line anchors before skill extraction.
- Deterministic rubric: both `results/evaluations/toolformer_auto_rubric_v0.json`
  and `results/evaluations/aide_auto_rubric_v0.json` scored 20/20.
- Context baseline: Toolformer auto-note-derived skill scored 9.3/10, compared
  with 2.5/10 for generic summary and 1.534/10 for abstract-only context; AIDE
  auto-note-derived skill scored 8.467/10, compared with 1.916/10 and
  1.333/10.
- Transfer readiness: Toolformer full auto-note-derived skill scored 10/10 and
  dropped to 7.6/10 without `Transfer Notes`; AIDE scored 9.5/10 and dropped to
  7.1/10.
- Source-span validation: Toolformer found 20/20 supported anchored claims and
  AIDE found 17/17, both with 0 invalid ranges.
- Failure modes: initial snippets mixed two-column PDF text and references; the
  selector now preserves raw spacing, chooses keyword-bearing columns, shortens
  snippets, and prefers stronger anchors for targeted limitations.
- Limitations: this is deterministic scaffold evidence for two extracted-text
  papers and two profiles, not reliable arbitrary-PDF automation or human
  semantic validation.
- Claim impact: supports the new bounded claim that extracted paper text can be
  transformed into an auditable note scaffold that feeds the existing
  PaperToSkill extraction pipeline.
- Figure/table: `results/tables/auto_note_comparison.md`;
  `results/evaluations/toolformer_auto_note_scaffold_v0.json`.

## AAAI Paper Package And Usage Examples

- Experiment: prepare the paper in official AAAI LaTeX format and add
  executable usage examples for the experiments section.
- Main result: downloaded the official AAAI-27 author kit, recorded provenance
  and SHA256, and added `paper/aaai/papertoskill_aaai2027.tex` plus LaTeX table
  and bibliography files.
- Usage examples: added Codex-style skill usage, extracted-text auto-note usage,
  and model-ablation usage docs under `examples/usage/`.
- Model-ablation protocol: added `benchmarks/model_ablation_v0.json`,
  `scripts/build_model_ablation_prompts.py`, and six prompt packets under
  `results/model_ablation_prompts/v0/`.
- Compared baselines: no new empirical baseline; this phase prepares paper and
  live-ablation infrastructure.
- Practical significance: the paper can now be revised in the requested AAAI
  template, and the user's later DeepSeek addition can follow the same prompt
  and response-slot protocol as Claude and GPT-family models.
- Statistical evidence: none; prompt packets and usage examples are not scored
  model responses.
- Failure modes: local LaTeX rendering depends on whether a TeX distribution is
  available; DeepSeek model ablations remain blocked until the user provides a
  concrete alias and endpoint profile.
- Limitations: Claude and GPT-family are complete only for the current two-row
  prompt protocol; no completed DeepSeek ablation, no provider billing or
  success-per-dollar evidence.
- Claim impact: supports the claim that AAAI packaging and model-ablation
  protocols are prepared, while preserving the evidence boundary that live model
  results remain pending.
- Figure/table: `paper/aaai/papertoskill_aaai2027.tex`;
  `examples/usage/`; `results/model_ablation_prompts/v0/index.json`.

## Model-Ablation Live Attempt

- Experiment: run prepared model-ablation prompt packets through the live runner
  and score any saved responses.
- Main result: `results/model_ablation_prompts/v0/run_report.md` reports
  `overall_status=partial`, with 2 Claude successes and 2 GPT-family errors.
- Claude model catalog: `/v1/models` succeeded for
  `https://coderxiaoc.com/v1` with `AI_SCIENTIST_OPENAI_API_KEY` and listed
  14 Claude-family IDs, including `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- Claude result: both selected `claude-opus-4-8` exactly, completed with HTTP
  200, saved response files, and scored 6/6 under the saved-response rubric.
- GPT-family model catalog: `/v1/models` succeeded with
  `PAPERTOSKILL_GPT_OPENAI_API_KEY` and listed 17 models, including
  `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, GPT 5.2 variants, and GPT 5.3 Codex
  variants.
- GPT-family result: the Phase 36 attempt failed with HTTP 502 for
  `gpt-5.5`/`gpt-5.4`, but the Phase 37 retry completed both current prompt
  rows. The Toolformer row timed out on `gpt-5.5` and then succeeded with
  `gpt-5.4`; the AIDE row succeeded with `gpt-5.5`.
- DeepSeek result: not attempted; the follow-up slot remains ready for the
  user's later configuration.
- Response evaluation: `results/model_ablation_prompts/v0/evaluation.md`
  reports 6 total rows, 4 scored rows, 2 pending rows, and 1.0 average
  normalized score over scored rows.
- Output-token proxy: `results/tables/model_response_cost_proxy.md` reports
  four measured saved responses, two pending DeepSeek rows, and 8,710
  `o200k_base` output tokens across the measured Claude/GPT-family rows.
- Latest recheck: Phase 37 reran the GPT-family slot with the separate GPT
  credential profile and produced the current GPT-family saved responses.
- Practical significance: the project now has a reusable runner/evaluator path
  for Claude/GPT/DeepSeek model ablations, records provider availability
  without committing raw credentials, and has saved/scored live model response
  evidence for Claude and GPT-family rows.
- Statistical evidence: four Claude/GPT-family rows scored by a deterministic
  rubric; not a broad model comparison because DeepSeek rows remain pending.
- Failure modes: provider account pool and model catalog availability can block
  a live run independently of PaperToSkill prompt quality.
- Limitations: this completes only the Claude Opus 4.8 and GPT-family portions
  of the current two-case protocol; it is not a completed DeepSeek comparison.
- Claim impact: supports saying Claude Opus 4.8 and GPT-family completed the
  current PaperToSkill usage prompt protocol, while preserving the boundary
  that DeepSeek results remain pending.
- Figure/table: `scripts/run_model_ablation_prompts.py`;
  `scripts/evaluate_model_ablation_responses.py`;
  `scripts/evaluate_model_response_costs.py`;
  `research/run_logs/2026-06-19_phase36_claude_ablation_success_gpt_blocked.md`;
  `research/run_logs/2026-06-19_phase37_gpt_family_ablation_success.md`;
  `research/run_logs/2026-06-19_phase38_model_response_cost_proxy.md`;
  `results/model_ablation_prompts/v0/run_report.md`;
  `results/model_ablation_prompts/v0/gpt_retry_run_report.md`;
  `results/model_ablation_prompts/v0/evaluation.md`;
  `results/tables/model_response_cost_proxy.md`.

## Model-Response Output-Token Proxy

- Experiment: estimate local output-token proxies for saved model-ablation
  response files without claiming provider billing.
- Main result: `results/tables/model_response_cost_proxy.md` reports 6 prompt
  rows, 4 measured saved responses, 2 pending DeepSeek rows, 9,420
  character-proxy output tokens, and 8,710 `o200k_base` output tokens.
- Per-row tokenizer counts: Claude Toolformer 2,272, Claude AIDE 2,108,
  GPT-family Toolformer 1,447, and GPT-family AIDE 2,883.
- Compared baselines: none; this is accounting over saved response files.
- Practical significance: the project now has both local input-context and
  saved-response output-token proxy reports, which is enough to discuss
  compactness and response-size accounting without inventing provider bills.
- Statistical evidence: none; deterministic local token counting only.
- Failure modes: pending DeepSeek rows have no response files and should not be
  treated as negative model-quality or cost evidence.
- Limitations: the price proxy uses a configurable `$1 / 1M output tokens`
  scale and is not a provider invoice, live bill, or success-per-dollar result.
- Claim impact: upgrades the economic section from input-context proxies only
  to local input/output token proxies while preserving the no-real-billing
  boundary.
- Figure/table: `scripts/evaluate_model_response_costs.py`;
  `results/tables/model_response_cost_proxy.md`;
  `results/tables/model_response_cost_proxy.csv`;
  `results/tables/model_response_cost_proxy.json`.

## Provider Billing Evidence Handoff

- Experiment: prepare auditable provider-billing and success-per-dollar
  evidence slots without claiming realized bills.
- Main result: `results/provider_billing_evidence/billing_summary.md` reports
  `billing_status=pending`, 6 total rows, 0 measured rows, 6 pending rows, 0
  errors, total billed USD 0, and success per dollar `n/a`.
- Compared baselines: local input/output token proxies in
  `results/tables/context_cost_proxy_tokenizer.md` and
  `results/tables/model_response_cost_proxy.md`.
- Practical significance: the project now has a concrete handoff for replacing
  proxy economics with invoice-backed rows when provider exports are available.
- Statistical evidence: none; no billing rows are measured yet.
- Failure modes: a partially filled row fails validation unless provider,
  model alias, billing period, token counts, billed USD, invoice/usage
  evidence, success metric, success value, and reviewer ID are present.
- Limitations: this is a template and validator, not a provider invoice or real
  success-per-dollar result.
- Claim impact: supports saying provider-billing evidence collection is
  prepared, while preserving that provider billing remains pending.
- Figure/table: `benchmarks/provider_billing_evidence_v0.json`;
  `scripts/summarize_provider_billing_evidence.py`;
  `results/provider_billing_evidence/billing_template.csv`;
  `results/provider_billing_evidence/billing_summary.md`;
  `results/provider_billing_evidence/billing_summary.json`.

## DeepSeek Follow-Up Readiness

- Experiment: configure and execute the DeepSeek follow-up slot under the same
  saved-response model-ablation protocol as Claude/GPT-family rows.
- Main result: `results/deepseek_followup_handoff/handoff.md` reports
  `responses_present`, 7 ready checks, 0 pending checks, and 0 failed checks.
  DeepSeek completed both current prompt rows with `deepseek-v4-flash`, and the
  six-row saved-response evaluation reports 6 scored rows and 0 pending rows.
- Compared baselines: Claude, GPT-family, and DeepSeek rows share the same
  two-case usage-plan prompt protocol and deterministic response evaluator.
- Practical significance: the DeepSeek slot is no longer a configuration
  blocker for the saved-response model-ablation protocol.
- Statistical evidence: deterministic saved-response contract scoring only.
- Failure modes: future DeepSeek refreshes can still be blocked by credentials,
  endpoint availability, model catalog changes, or provider instability.
- Limitations: this does not prove live downstream task success, broad model
  quality, provider economics, or real-reuse task effectiveness.
- Claim impact: supports saying the current saved-response model-ablation
  protocol has Claude/GPT-family/DeepSeek response rows present and scored.
- Figure/table: `research/run_logs/2026-06-18_phase23_deepseek_followup_readiness.md`;
  `research/run_logs/2026-06-19_phase47_deepseek_followup_handoff.md`;
  `results/deepseek_followup_handoff/handoff.md`;
  `examples/usage/model_ablation_usage.md`; `research/runbook.md`.

## Goal Completion Audit

- Experiment: audit the active user goal against current repository evidence
  before deciding whether the overall goal is complete.
- Main result: `research/goal_completion_audit.md` classifies local memory,
  phase-level GitHub saving, deterministic/offline PaperToSkill development,
  AAAI package preparation, usage examples, model-ablation saved responses,
  bounded AI-Scientist-v2 integration, failure-branch provenance, and local
  reproducibility readiness as satisfied for the current artifact package.
- Remaining blockers: human-fidelity annotation is unscored and final AAAI
  submission readiness remains governed by the recorded
  `wait_for_external_evidence` policy. The current real-reuse first pass is
  complete as an execution milestone but mixed as effectiveness evidence, so
  core real-reuse stabilization remains the next experimental priority.
- Practical significance: prevents the project from accidentally declaring
  success simply because the local deterministic package is extensive and green.
- Statistical evidence: none; this is a requirements and evidence audit.
- Failure modes: the audit must be refreshed if the user changes the target
  paper venue, adds new model credentials, or decides that deterministic/offline
  evidence is sufficient for the first submission.
- Limitations: it does not resolve external model availability or collect human
  scores.
- Claim impact: supports keeping the active goal open while showing exactly
  what evidence is still missing.
- Figure/table: `research/goal_completion_audit.md`.

## Goal Completion Gate

- Experiment: make the active-goal completion audit machine-checkable.
- Main result: `results/reproducibility/goal_completion_report.md` reports
  `overall_status=not_complete_pending_external_evidence`, 77 ready checks, 3
  pending checks, and 0 failed checks.
- Checks: durable memory, AI-Scientist-v2 dry-run evidence, PaperToSkill
  prototype and benchmark readiness, bounded AI-Scientist-v2 LLM-client smoke
  attempt/completion status, full AI-Scientist-v2 live-run handoff/completion
  status, AAAI/usage/table/claim gates, Claude/GPT-family ablation attempts
  and completion status, DeepSeek saved responses, all four live-transfer
  saved-response sets, local token accounting, human-fidelity annotation,
  real-reuse first-pass evidence, Full Excerpt sanity evidence, and
  external-evidence execution packets.
- Practical significance: the project now has a reusable gate that prevents
  accidentally marking the full user goal complete while external evidence is
  still missing.
- Failure modes: the gate must be updated if the user changes the definition of
  completion, adds a new required model, or decides to submit an explicitly
  deterministic/offline paper without waiting for live/human/cost evidence.
- Limitations: the gate does not collect human scores, make provider billing
  claims, stabilize the real-reuse first pass, or make the paper
  submission-final.
- Claim impact: strengthens completion discipline and keeps the current goal
  open with explicit pending requirements.
- Figure/table: `scripts/check_goal_completion.py`;
  `results/reproducibility/goal_completion_report.md`;
  `results/reproducibility/goal_completion_report.json`.

## External Evidence Closure Queue

- Experiment: map every pending external-evidence goal requirement to a
  concrete local queue item and next action.
- Main result: `results/external_evidence_closure/closure.md` reports
  `overall_status=pending_external_evidence`, 3 ready checks, 0 pending checks,
  and 0 failed checks.
- Queue items: human-fidelity annotation and AAAI final submission readiness
  under the recorded wait policy.
- Practical significance: pending external work is now centrally mapped and
  machine-checkable, reducing the chance that one blocker disappears from the
  runbook or completion audit.
- Statistical evidence: none; this is a deterministic planning and gate
  artifact.
- Failure modes: the queue must be regenerated after any external evidence
  changes, and it cannot substitute for the missing external evidence itself.
- Limitations: it does not collect annotations or approve final submission.
  Completed bounded AI-Scientist-v2 artifacts are inputs, not pending closure
  items.
- Claim impact: supports saying the remaining closure path is auditable, not
  that the remaining evidence is complete.
- Figure/table: `scripts/check_external_evidence_closure.py`;
  `results/external_evidence_closure/closure.md`;
  `results/external_evidence_closure/closure.json`.

## External Evidence Execution Packets

- Experiment: turn each external-evidence closure queue item into a runnable
  handoff packet with inputs, setup notes, commands, validation commands,
  completion criteria, escalation rules, and evidence boundaries.
- Main result: `results/external_evidence_packets/packets.md` reports
  `overall_status=ready`, 8 ready checks, 0 pending checks, and 0 failed
  checks. The extra check makes the human-fidelity `toHuman.md` / `ok.txt`
  handoff and cleanup workflow explicit.
- Packet items: human-fidelity annotation and AAAI submission decision/final
  readiness.
- Practical significance: the remaining external work is now not only mapped
  but directly executable as a handoff checklist, reducing ambiguity after
  context compaction or agent handoff.
- Statistical evidence: none; this is a deterministic planning and gate
  artifact.
- Failure modes: packet commands can still be blocked by unavailable reviewers,
  ambiguous annotation criteria, insufficient evidence strength, or a pending
  final submission decision.
- Limitations: it does not collect annotations or approve final submission.
  Completed bounded AI-Scientist-v2 artifacts are inputs, not pending packet
  items.
- Claim impact: supports saying the external-evidence handoff is runnable and
  machine-checked, not that the remaining evidence is complete.
- Figure/table: `scripts/check_external_evidence_packets.py`;
  `results/external_evidence_packets/packets.md`;
  `results/external_evidence_packets/packets.json`.

## Submission Review Handoff Gate

- Experiment: keep internal review, rebuttal, and submission checklist handoff
  files synchronized with the current evidence state.
- Main result: `results/reproducibility/submission_review_report.md` reports
  `overall_status=ready`, 16 ready checks, and 0 failed checks.
- Checks: stale HTTP 503/live-transfer pending language is absent; review
  materials include the current 24 scored saved live-transfer response rows,
  6 scored and 0 pending model-ablation rows, 0 scored and 24 pending
  human-fidelity cells, local token-accounting evidence, bounded AI-Scientist-v2
  smoke/full-run completion, and current goal/package counts.
- Practical significance: prevents reviewer-facing handoff materials from
  lagging behind the evidence package while keeping final submission decisions
  explicit.
- Failure modes: the checker must be rerun after any future goal/package count
  change or after real-reuse, LLM-ablation, human-fidelity, or submission
  evidence is updated.
- Limitations: this is review-handoff freshness, not new empirical evidence or
  final AAAI submission readiness.
- Claim impact: supports saying the submission-review handoff is current and
  machine-checked, while final submission remains pending.
- Figure/table: `scripts/check_submission_review.py`;
  `research/submission_checklist.md`;
  `results/reproducibility/submission_review_report.md`.

## AAAI Submission Decision Preflight

- Experiment: make the final AAAI submission decision auditable without making
  the decision for the user.
- Main result: `results/aaai_submission_decision/decision.md` reports
  `overall_status=ready`, `decision_status=recorded`,
  `selected_option=wait_for_external_evidence`, 27 ready checks, 0 pending
  checks, and 0 failed checks.
- Options: the preflight still documents `submit_now_deterministic_offline` and
  `wait_for_external_evidence`, and the current recorded policy is to wait for
  named external evidence before stronger claims.
- Practical significance: the decision record prevents the project from
  drifting into final-submission language while human fidelity and the chosen
  evidence policy remain unresolved.
- Statistical evidence: none; this is a decision and claim-boundary preflight.
- Failure modes: a future changed decision record can still be invalid if it
  lacks a selected option, decision owner, decision date, claim boundary, or
  evidence policy.
- Limitations: it does not submit the paper, complete external evidence, or
  make the active goal complete.
- Claim impact: supports saying the final submission decision is locally
  preflighted and auditable, not that the paper is submission-final.
- Figure/table: `scripts/check_aaai_submission_decision.py`;
  `results/aaai_submission_decision/decision.md`;
  `research/run_logs/2026-06-20_phase55_aaai_submission_decision_preflight.md`.

## AIDE Real-Reuse Rows

- Experiment: locked Kaggle Spaceship Titanic validation split under Summary vs
  PaperToSkill with GPT-family `gpt-5.5`, followed by an extended local scorer
  rerun over the same saved AIDE outputs.
- Main result: with a 300-second local scorer budget, AIDE-T1
  Summary/PaperToSkill score 0.816/0.817 and is solved by both conditions;
  AIDE-T2 scores 0.000/0.826 and is a PaperToSkill-only success. The earlier
  60-second scoring pass timed out all four generated scripts and remains a
  budget-boundary historical row, not the current main-table value.
- Baseline scorer validation: the deterministic baseline/weak-script path
  scores 0.4997124784358827, so the validation labels, submission format, and
  scoring path are live.
- Compared baselines: Summary and PaperToSkill use the same official
  Kaggle-derived local split, task prompt, no-mid-run-human rule, and hidden
  validation-label scorer.
- Practical significance: this turns the AIDE rows from timeout-only evidence
  into one solved-by-both row and one PaperToSkill-only success, while still
  showing that scorer budget and runtime contracts materially affect
  interpretation.
- Statistical evidence: none; these are two locked local validation tasks, not
  a full AIDE or Kaggle benchmark reproduction.
- Failure modes: the Summary AIDE-T2 row still times out under the extended
  scorer, and the Full Excerpt AIDE-T1 sanity row remains 0.000 under its saved
  60-second scorer path. These are local scoring/runtime boundaries rather than
  provider/model availability failures.
- Limitations: the result is not a full AIDE or Kaggle benchmark reproduction
  and should not be used as aggregate AIDE effectiveness evidence.
- Claim impact: strengthens the first eight-row real-reuse table with one
  additional PaperToSkill-only success, but the overall table remains mixed and
  does not establish aggregate PaperToSkill advantage over Summary.
- Figure/table: `results/real_reuse/aide_run_report.md`;
  `results/real_reuse/aide_t1_baseline_metric.json`;
  `results/real_reuse/aide_t2_weak_script_metric.json`;
  `results/real_reuse/main_results_plan.md`;
  `paper/aaai/papertoskill_tables.tex`.

## SWE-T1 Real-Reuse Rows

- Experiment: locked SWE-Bench Lite SQLFluff instance
  `sqlfluff__sqlfluff-1625` under Summary vs PaperToSkill with GPT-family
  `gpt-5.5`.
- Main result: Summary scores 0.000 and PaperToSkill scores 0.000; both
  generated candidate patches fail to apply under the hidden target-test
  scoring setup.
- Gold scorer validation: `results/real_reuse/swe_t1_gold_metric.json` scores
  1.000 after applying the scorer-only hidden test patch and gold patch, so the
  local metric path is live.
- Compared baselines: Summary and PaperToSkill use the same task prompt,
  external SQLFluff workspace, hidden test patch, no-mid-run-human rule, venv
  test command, and scorer.
- Practical significance: this fills the second SWE-agent row and exposes a
  software-engineering failure boundary where PaperToSkill guidance alone did
  not make the generated patch apply to the locked codebase.
- Statistical evidence: none; this is one locked task instance, not an
  aggregate SWE-agent benchmark.
- Failure modes: the PaperToSkill output targeted a plausible rule location but
  used context that did not match the locked file; the Summary retry also
  produced an unapplied patch. The first Summary call timed out, then a
  one-attempt retry produced the scored row.
- Limitations: this result does not prove PaperToSkill is ineffective on
  software engineering tasks; it is a single failed SWE-Bench Lite-style row.
- Claim impact: strengthens the evidence boundary by adding a real failed task
  row alongside the positive AIDE-T2 and SWE-T2 rows; aggregate downstream
  advantage remains unsupported after the full first-pass table because
  AIDE-T1/REF are solved by both conditions, SWE-T1 fails, and SNAP remains
  below threshold.
- Figure/table: `results/real_reuse/raw_rows.jsonl`;
  `results/real_reuse/swe_t1_gold_metric.json`;
  `results/real_reuse/main_results_plan.md`;
  `paper/aaai/papertoskill_tables.tex`.

## SWE-T2 Real-Reuse Rows

- Experiment: locked SWE-Bench Verified-style Astropy instance
  `astropy__astropy-12907` under Summary vs PaperToSkill with GPT-family
  `gpt-5.5`.
- Main result: Summary scores 0.000 because the generated patch fails to apply;
  PaperToSkill scores 1.000 because the generated patch applies and passes both
  hidden target tests.
- Compared baselines: Summary and PaperToSkill use the same task prompt,
  external Astropy workspace, hidden test patch, no-mid-run-human rule, and
  scorer.
- Practical significance: this is the first SWE-agent real-reuse row showing a
  successful PaperToSkill outcome under the original-style issue-to-patch
  input/output contract.
- Statistical evidence: none; this is one locked task instance, not an
  aggregate SWE-agent benchmark.
- Failure modes: Summary produced an invalid patch for the target file after
  the hidden test patch was applied; the later SWE-T1 row failed for both
  Summary and PaperToSkill due patch-apply failures. The latest AIDE update
  adds one solved-by-both row and one PaperToSkill-only success under an
  extended local scorer.
- Limitations: the result does not reproduce the full SWE-agent paper and does
  not establish broad software-engineering effectiveness.
- Claim impact: strengthens the partial downstream evidence but keeps aggregate
  effectiveness unsupported after the eight-row first pass.
- Figure/table: `results/real_reuse/swe_run_report.md`;
  `results/real_reuse/swe_t2_gold_metric.json`;
  `results/real_reuse/main_results_plan.md`;
  `paper/aaai/papertoskill_tables.tex`.

## Real-Reuse Failure-Boundary Analysis

- Experiment: derived row-level analysis over the first eight-row GPT-family
  Summary-vs-PaperToSkill real-reuse pass.
- Main result: the table maps AIDE-T1 to solved-by-both, AIDE-T2 and SWE-T2 to
  PaperToSkill-only success, SWE-T1 to patch application failure, REF-T1/T2 to
  a solved-by-both ceiling, and SNAP-T1/T2 to artifact completion boundaries.
- Compared baselines: no new baseline; the analysis is derived from the same
  Summary and PaperToSkill raw rows as the main real-reuse table.
- Practical significance: the mixed results are now reviewable as concrete
  method-contract pressure points: scorer budget/fallback, patch-format/apply
  checks, harder task slices, and required artifact/metric manifests.
- Statistical evidence: none; this is explanatory analysis over a single
  GPT-family pass and does not add new task-success evidence.
- Failure modes: because unsupported errors remain not automatically judged,
  this table should not be read as semantic-fidelity annotation.
- Claim impact: strengthens the honesty and diagnosability of the real-reuse
  section without supporting aggregate downstream effectiveness.
- Figure/table: `results/real_reuse/failure_analysis.md`;
  `results/real_reuse/failure_analysis.json`;
  `paper/aaai/papertoskill_tables.tex`.

## Full Excerpt Sanity Check

- Experiment: auxiliary three-task Full Excerpt sanity check over AIDE-T1,
  SWE-T1, and SNAP-T1.
- Main result: Full Excerpt scores are now filled for the pre-registered
  subset: AIDE-T1 0.000, SWE-T1 0.000, and SNAP-T1 0.250. The same table now
  mirrors the latest Summary/PaperToSkill values for AIDE-T1 (0.816/0.817).
  These do not reverse the mixed real-reuse interpretation.
- Compared baselines: Summary and PaperToSkill cells come from the existing
  real-reuse raw rows; Full Excerpt cells come from the same raw-row path.
- Practical significance: the scaffold answers reviewer questions about
  context-length sanity without reintroducing Full Excerpt as a main baseline.
- Statistical evidence: three scored sanity rows only; no aggregate
  effectiveness claim.
- Failure modes: token counts are context proxies, not provider bills or output
  token costs. The AIDE-T1 Full Excerpt sanity row times out under its saved
  60-second scorer path, SWE-T1 fails patch application, and SNAP-T1 misses
  required artifacts or metrics.
- Claim impact: does not change the main real-reuse interpretation; it is
  auxiliary sanity evidence over the pre-registered subset.
- Figure/table: `results/real_reuse/full_excerpt_sanity.md`;
  `results/real_reuse/full_excerpt_sanity.json`;
  `paper/aaai/papertoskill_tables.tex`.
