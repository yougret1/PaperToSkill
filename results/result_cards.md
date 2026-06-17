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
