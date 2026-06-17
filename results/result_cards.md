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
- Claim impact: strengthens the deterministic multi-paper coverage claim across
  three real paper cases.
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
- Claim impact: partially supports the harness-transfer claim at the offline
  artifact-readiness level across three papers.
- Figure/table: `results/evaluations/aide_harness_transfer_v0.json`.

## Paper Draft Package

- Experiment: convert the validated three-paper deterministic/offline evidence
  into paper-facing artifacts.
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

- Experiment: deterministic context-size and cost-proxy analysis over full
  extracted paper text, curated paper notes, generated skills, generic summaries,
  and abstract-only baselines for the three real-paper cases.
- Main result: generated skills use 1,366 estimated input tokens vs 62,041 for
  the full AI Scientist-v2 extracted paper, 823 vs 18,559 for Reflexion, and
  1,517 vs 15,894 for AIDE.
- Compared baselines: full extracted paper, curated note, generated skill,
  generic summary, and abstract-only context. Coverage-per-budget rows are
  limited to the already evaluated skill, generic summary, and abstract-only
  contexts.
- Practical significance: generated skills compress full extracted paper text by
  97.8%, 95.57%, and 90.46% under the deterministic input-token proxy while
  preserving much higher deterministic coverage than generic summaries or
  abstract-only contexts.
- Statistical evidence: none; this is deterministic accounting.
- Failure modes: proxy tokens are estimated as `ceil(characters / 4)`, so they
  are not tokenizer-exact for any provider. The configurable cost number is a
  scaling proxy, not a real invoice.
- Limitations: summary and abstract contexts are smaller than generated skills
  but lose substantial deterministic coverage, so the supported claim is
  coverage-preserving compression relative to full paper context rather than
  shortest context overall.
- Claim impact: upgrades compactness from word-count-only evidence to
  deterministic token/cost proxy evidence while preserving the no-real-billing
  boundary.
- Figure/table: `results/tables/context_cost_proxy.md`;
  `results/tables/context_cost_proxy.csv`;
  `results/tables/coverage_cost_efficiency.csv`;
  `results/tables/context_cost_proxy.json`.
