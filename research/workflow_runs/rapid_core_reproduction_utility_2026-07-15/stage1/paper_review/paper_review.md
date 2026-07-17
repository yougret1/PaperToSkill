# Paper Reading and Reviewer Note

## 1. Bibliographic Information

- Title: PaperToSkill: Turning Research Papers into Portable Agent Skills
- Target: AAAI 2027
- Field: LLM agents, scientific-method operationalization, agent skill artifacts
- Paper type: artifact/compiler paper with deterministic artifact evaluation and exploratory downstream stress tests
- Canonical source: `paper/aaai/main.tex`
- Reviewed flat source/PDF: `paper/aaai/papertoskill_aaai2027.tex` and `papertoskill_aaai2027.pdf`
- Review date: 2026-07-15

## 2. One-Sentence Summary

PaperToSkill deterministically converts curated, source-anchored paper notes into compact `SKILL.md` artifacts with provenance, validation, failure, and transfer fields; the current evidence establishes artifact conformance and proxy compression, but not independent semantic fidelity, broad portability, ordinary-user benefit, or stable downstream advantage.

## 3. Problem and Motivation

The paper addresses a real gap: papers describe search policies, memory loops, validation stages, and interface contracts for human reading, but applying them requires manual procedural translation. A summary usually explains an idea but omits when to use it, required inputs, execution order, validation checks, failure handling, and adaptation rules (`papertoskill_aaai2027.tex:59-74`).

This is important for agent systems because procedural omissions often fail before model quality matters: patches do not apply, scorers and tasks disagree, required artifacts are missing, or runtime budgets are exceeded. The manuscript's failure analysis captures these boundaries well.

The ordinary-user motivation is currently aspirational. No user study measures whether non-experts complete tasks faster, make fewer errors, understand limitations better, or calibrate trust more accurately.

## 4. Claimed Gap in Prior Work

The manuscript claims a lightweight layer between paper reading and runnable paper agents: a human-editable natural-language skill with source and failure boundaries, without requiring an MCP server or runnable codebase. It positions primarily against Paper2Agent (`papertoskill_aaai2027.tex:92-114`).

That positioning is now incomplete. The run-scoped literature contains direct neighbors that occupy broad resource-to-skill, compact-grounded-context, dependency retrieval, skill reduction, and skill-utility claims:

- SkillFoundry and Anything2Skill cover scientific/external-resource-to-skill compilation.
- Paper2Agent covers paper activation through MCP artifacts.
- ClawTrace covers cost-aware preserve/prune/repair skill distillation.
- Graph-of-Skills covers dependency-complete compact skill retrieval.
- SkillRAE covers compact grounded execution context.
- A Framework for Evaluating Agentic Skills at Scale covers marginal skill utility.

Therefore, “paper to skill,” “compact,” “grounded,” “portable,” and “useful” are not available as broad novelty claims. The potentially defensible delta is narrower: deterministic, human-editable note-to-`SKILL.md` compilation with explicit line-span provenance, inferred-guidance labels, failure branches, and transfer boundaries.

## 5. Core Claim and Hypothesis

The paper's narrow hypothesis is that a structured paper-note-to-skill pipeline can retain more operational information than short summaries while producing a compact, auditable artifact (`papertoskill_aaai2027.tex:66-90`, `371-376`).

The manuscript explicitly does not claim robust arbitrary-PDF understanding, aggregate downstream superiority, independent human fidelity, provider cost savings, or broad cross-model success. This claim discipline is a strength.

However, the title and conclusion still use “portable,” “source-grounded,” and “reproducible” more broadly than the completed evidence supports.

## 6. Method

The method has three functional stages:

1. Prepare a curated source-anchored note, or an earlier extracted-text audit scaffold with line anchors.
2. Normalize sections/list items, collect candidates from abstract, method, experiment, limitation, and transfer regions, apply candidate limits, and emit `SKILL.md`.
3. Write `references/source_map.json` linking generated instructions to note sections and line spans; then evaluate schema, coverage, source spans, readiness, compactness, and downstream reuse.

The main technical defect is specification. The paper does not formally define region detection, candidate representation, scoring/ranking, deduplication, conflict handling, exact caps, ordering, inferred-guidance policy, or behavior when a required field lacks support (`papertoskill_aaai2027.tex:118-138`). The curation operator is also missing: who creates the notes, under what instructions, at what time/cost, with what agreement or variability?

Because curated notes may already contain most of the operationalization, the current design cannot separate curator value from extractor value.

## 7. Evidence Chain

| Claim | Reported evidence | What it supports | What it does not support |
|---|---|---|---|
| Structural validity | Four skills score 20/20 | Schema conformance on four cases | Semantic correctness or usability |
| Operational coverage | Skills score much higher than Summary/Abstract | More rubric keywords/fields in longer structured contexts | Advantage over token-matched or strong procedural baselines |
| Source grounding | Support 0.938-1.0, zero invalid ranges | Valid line-span bookkeeping and lexical support | Entailment, non-hallucination, or correct source use |
| Compactness | 479-943 words; 2.39%-9.65% of full-paper token proxy | Real size reduction versus full extracted text | Lower end-to-end cost, curation effort, or success per dollar |
| Transfer Notes | 10/10 full versus 7.6/10 removed | The readiness rubric rewards the present field | Live transfer improvement or paper-specific information value |
| Saved responses | 24/24 and 6/6 perfect contract scores | Output-format compliance on saved files | Human fidelity, live execution, or model quality |
| Real reuse | Eight single GPT-family rows, mixed | Feasibility and concrete failure boundaries | Stable treatment effect or aggregate benefit |
| Model robustness | Auxiliary GPT favors Summary; DeepSeek ties; Claude pending | Strong model/run sensitivity | Cross-model portability |
| Paper2Agent positioning | Seven artifact/workflow criteria | A plausible design-point distinction | Competitive performance or setup-cost advantage |

The strongest empirical result is therefore not “PaperToSkill helps.” It is: “the current pipeline can emit compact, schema-compliant, line-linked artifacts and expose downstream contract failures on selected cases.”

## 8. Figure and Table Walkthrough

### Figure 1

The source-paper -> note -> skill -> evaluation pipeline is visually clear and appropriately separates local deterministic checks from external evidence. The conceptual split is useful, but the external layer is still a plan rather than evidence.

### Main real-reuse and failure tables

The eight-row table reports mixed outcomes honestly. AIDE-T2 and SWE-T2 favor PaperToSkill in one run; AIDE-T1 and both Reflexion rows are tied/near-tied; SWE-T1 fails for both; SnapATAC2 remains below success thresholds. Follow-ups show that changing source context, scorer alignment, or executable contracts can make both conditions pass, which is valuable boundary analysis but weakens causal row-level “PaperToSkill-only” language.

### Deterministic artifact tables

The 20/20 and 10/10 scores saturate. Perfect or identical results are useful gates but poor discriminative scientific endpoints. The transfer-note ablation's identical 2.4-point drop is consistent with a fixed rubric penalty.

### External evidence tables

All cells are pending. This is a completion issue, but also an evidence-chain issue: the missing human/source-entailment and repeated cross-model measurements are the validators required for the central claims.

### Visual layout

The nine-page PDF has no clipping, overlap, missing figures, or broken glyphs. However, several wide tables on pages 3-5 are too small to audit efficiently. Non-reference content reaches page 8 despite the stated seven-page limit. Float placement leaves large unused regions on pages 6-9. Pending tables consume space that should be used for method specification and novelty positioning.

## 9. Original Innovation and Contributions

The original paper's strongest defensible contributions are:

1. A lightweight, human-editable `SKILL.md` artifact for operational paper knowledge rather than an MCP server or full runnable reproduction.
2. A deterministic curated-note-to-skill compiler that preserves line-span provenance, source/inference boundaries, validation checks, failure branches, and transfer notes.
3. An artifact-first audit pipeline that preserves negative outcomes and converts them into explicit execution-contract requirements.

The current six-item contribution list (`papertoskill_aaai2027.tex:82-90`) is too diffuse. Schema, extractor, auto-note scaffold, benchmark, metrics, and stress-test completion are project components, not six research innovations.

Reviewer judgment: the broad category is not novel. The narrow deterministic source/failure-boundary compiler may be publishable only if a direct comparison shows that these choices improve traceability, stability, editing, semantic fidelity, or downstream decisions.

## 10. Three-Reviewer Critique

### Reviewer 1: Technical Correctness and Methodology

Verdict: Reject, 3/10, confidence 0.88.

Main concerns:

- The algorithm and note-curation protocol are not independently implementable.
- Deterministic metrics measure schema compliance more directly than semantic fidelity.
- Context amount, representation, and prompt objective all change between baselines.
- One stochastic downstream sample under mutable contracts cannot establish row-level causal wins.

Strengths: disciplined scope, source-boundary-aware design, honest failure reporting, internally consistent headline arithmetic, and useful contract feedback.

### Reviewer 2: Empirical Evidence and Reproducibility

Verdict: Weak Reject, 4/10.

Main concerns:

- The main metrics are self-aligned lexical/structural gates without independent construct validation.
- Baselines are weak and length-confounded; strong adjacent systems are not run.
- The eight downstream rows have no repeated seeds, variance, confidence intervals, or confirmatory statistics.
- Development, scorer repair, and evaluation use the same small artifact/task pool; there is no untouched confirmation set.
- The paper package lacks a clean independent reproduction recipe and complete model/environment disclosure.

Strengths: unusually strong artifact lineage, fixed main-row bindings, preserved negative diagnostics, at least one well-hashed data path, and machine-checked table lineage.

### Reviewer 3: Novelty, Positioning, and Impact

Verdict: Reject, 3/10, confidence 4/5.

Main concerns:

- Related Work omits the systems that now define the contribution boundary.
- The six contributions do not resolve to one load-bearing mechanism or finding.
- Portable, grounded, and reusable are outcome claims supported mainly by self-defined artifact scores.
- No strong adjacent-system baseline tests practical advantage.
- Ordinary-user impact is claimed in motivation but unmeasured.

Novelty conclusion: the only plausible original delta is the narrow deterministic, editable, source/failure-boundary-aware compiler. EffectSlice is more defensible, but it is a separate-paper-scale pivot.

### Coordinator Synthesis

Consensus strengths:

- The problem is real and timely.
- Scope and negative-result reporting are unusually honest.
- Source/inference boundaries and failure branches are useful artifact design choices.
- The repository appears to preserve better evidence lineage than the manuscript communicates.

Consensus weaknesses:

- The paper does not isolate the value of its compiler from curated-note quality, context length, or evaluator design.
- Its best numbers are gates designed around its own schema.
- Its downstream evidence is exploratory, single-run, and mixed.
- Its novelty positioning is outdated relative to direct 2026 work.

Reviewer disagreement is small. R2 is slightly less negative because the artifact lineage and negative-result discipline are strong; R1 and R3 regard the method/novelty defects as rejection-level. All three require redesigned evidence, not wording-only revision.

Likely AAAI outcome: Reject / Weak Reject, with a credible resubmission path.

## 11. Limitations and Open Questions

- What portion of artifact quality comes from note curation versus deterministic extraction?
- Does a valid source span semantically entail each generated instruction?
- Does PaperToSkill beat a same-token structured procedural summary, expert-authored skill, or adjacent compiler?
- Which component actually helps: validation checks, failure cases, source anchors, transfer notes, or simply more context?
- Are AIDE/SWE wins stable across repeated seeds and model families?
- How often does the pipeline abstain or require human correction on unseen PDFs and paper types?
- Do ordinary users apply methods faster or more correctly, and do they understand failure boundaries better?
- What is the full conversion cost including curation, editing, retries, latency, and execution?

The blank reproducibility checklist and pending evidence tables are completion defects, but they are not the main scientific critique. The main critique remains construct validity, comparator fairness, causal identification, and novelty.

## 12. Concrete Improvement Priorities

1. Choose one paper thesis. For the current paper, use “deterministic source/failure-boundary-aware note-to-skill compilation.”
2. Specify the full transformation and curation protocol with pseudocode, exact caps, tie-breaking, schemas, and complexity/cost.
3. Add token/source/model-matched baselines: structured summary, generic LLM proceduralization, expert skill, source retrieval, and executable adjacent systems where applicable.
4. Validate the metrics with adversarial corruptions and blinded multi-rater semantic/source-entailment judgments.
5. Freeze tasks, prompts, scorer contracts, model versions, budgets, and a held-out paper-task set before confirmatory runs.
6. Run repeated paired samples and report task-level effects, uncertainty, win/tie/loss, false-admission, and abstention rather than incompatible raw-score averages.
7. Either remove ordinary-user language or run a preregistered user study covering time, correctness, edits, comprehension, trust calibration, and cognitive load.
8. Rewrite Related Work around direct 2025-2026 neighbors and a mechanism-by-mechanism comparison table.
9. Remove pending tables from the review PDF, make core tables readable, and fix page-limit/float placement.

## 13. Reusable Ideas for This Project

- Keep source-backed and inferred guidance distinct; this is one of the paper's strongest design choices.
- Preserve failure codes and negative rows instead of reporting only repaired outcomes.
- Separate artifact validity from effect validity. A structurally good skill is not necessarily helpful.
- Keep immutable task/scorer/selection manifests and table-generation lineage.
- Use current eight rows as development and failure-discovery data, not as future confirmatory evidence.

## 14. Writing Patterns Worth Reusing

Useful patterns:

- Explicit “what this result does not show” sentences.
- Separate local artifact evidence from external effect evidence.
- Turn failed rows into concrete contract implications.
- State diagnostic follow-ups as diagnostics rather than wins.

Patterns to change:

- Six contributions dilute the central research story.
- Repeated disclaimers cannot substitute for a strong positive claim and experiment.
- Too many diagnostic tables interrupt the argument and shrink the readable evidence.
- The title and conclusion remain broader than the most defensible claim.

## 15. Relationship to EffectSlice

EffectSlice should not be inserted as a late extra contribution into the current paper. It changes the question from “can curated paper notes become auditable skill artifacts?” to “after the complete artifact is proven beneficial, can a strict nonempty source-grounded subset preserve its task-local net effect under one sealed admission family?”

PaperToSkill can supply source maps, complete skills, eight development tasks, runners, scorers, and failure taxonomies. But EffectSlice requires a new title, abstract, related work, method, baselines, primary endpoint, statistical protocol, and at least four genuinely new held-out paper-task pairs. It is a follow-on methods paper, not a small revision.
