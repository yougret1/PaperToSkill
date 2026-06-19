# Human Fidelity Review Packet: AI Scientist-v2

Evidence boundary: this packet is an input for human review. It is not a completed annotation.

## Review Instructions

- Review the generated skill against the curated source note and extracted paper text.
- Use source anchors where available, but judge semantic fidelity rather than lexical overlap alone.
- Record one score per criterion and cite the source span or skill section that justifies the score.
- Mark unsupported or inferred transfer guidance explicitly instead of folding it into source-backed fidelity.

## Score Scale

- 0: Missing or contradicts the paper.
- 1: Present but vague, materially incomplete, or weakly grounded.
- 2: Mostly faithful with minor omissions or wording issues.
- 3: Faithful, operationally useful, and source-supported.

## Completion Requirements

- All 24 paper-by-criterion rows must have a score from 0 to 3.
- Every scored row must include an evidence_locator and evidence_note.
- Every scored row must include reviewer_id, review_date, and confidence_0_to_1.
- Use needs_discussion=true when the score depends on ambiguous source support or inferred transfer guidance.
- Do not claim human validation until the summarizer reports annotation_status=complete and zero errors.

## Artifact Summary

- Generated skill: `generated_skills/ai_scientist_v2/SKILL.md`
- Curated source note: `papers/notes/ai_scientist_v2_note.md`
- Extracted paper text: `papers/extracted/ai_scientist_v2.txt`
- Source map: `generated_skills/ai_scientist_v2/references/source_map.json`
- Source-span report: `results/evaluations/ai_scientist_v2_source_span_validation_v0.json`
- Deterministic skill coverage: 7.867/9
- Source-span support rate: 0.938
- Invalid source-span ranges: 0
- Source-map entries: 16
- Skill words: 782
- Source note words: 820

## Criteria

| Criterion | Question | Score | Evidence note |
| --- | --- | --- | --- |
| Central contribution fidelity | Does the skill preserve the paper's central contribution without overclaiming? |  |  |
| Operational workflow fidelity | Does the skill preserve the executable workflow, roles, stages, or search policy needed to reuse the method? |  |  |
| Validation and evidence fidelity | Does the skill preserve the paper's validation protocol, evaluation domains, and reported evidence without distorting them? |  |  |
| Failure and limitation fidelity | Does the skill preserve important limitations, failure modes, and stop conditions? |  |  |
| Source grounding | Are source-backed instructions traceable to the cited note or extracted-paper spans? |  |  |
| Transfer boundary discipline | Does the skill separate paper-backed content from inferred transfer guidance and harness-specific adaptation? |  |  |

## Generated Skill

```markdown
---
name: ai-scientist-v2-paper-skill
description: Use when applying the paper-derived method from The AI Scientist-v2 Workshop-Level Automated Scientific Discovery via Agentic Tree Search as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/notes/ai_scientist_v2_note.md`

## Paper Snapshot

The AI Scientist-v2 is an end-to-end agentic system for automated scientific discovery.
It formulates hypotheses, designs and executes experiments, analyzes and visualizes
data, and writes scientific manuscripts. Compared with AI Scientist-v1, the paper says
v2 removes reliance on human-authored code templates, generalizes across machine-
learning domains, and uses progressive agentic tree search managed by an experiment
manager. The paper also adds a VLM-based review loop for improving figure, caption, and
text quality. The authors evaluated the system by submitting three autonomous
manuscripts to an ICLR workshop; one reached workshop acceptance-level scores. Source
anchors: extracted text lines 23-31, 49-58, 80-87.

## Central Contribution

The AI Scientist-v2 is an end-to-end agentic system for automated scientific discovery.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Start with generalized idea generation rather than code-conditioned template modification. The system begins from high-level research directions and can use literature-search tools to check novelty and identify prior work. Source anchors: lines 187-204.
2. Remove template dependency by turning the generated idea into an experimental process that does not require a hand-authored baseline code template. Source anchors: lines 204-216.
3. Use an Experiment Progress Manager with four stages: preliminary investigation, hyperparameter tuning, research agenda execution, and ablation studies. Each stage has stopping criteria and passes the selected best node to the next stage. Source anchors: lines 211-244.
4. Run parallelized agentic tree search within each stage. Each node contains an experiment plan, generated Python code, execution trace or error, runtime, metrics, LLM feedback, visualization code, generated figures, VLM feedback, and buggy/non-buggy status. Source anchors: lines 244-356.
5. For buggy nodes, record the error and attempt debugging. For non-buggy nodes, refine the experiment. Select nodes using a best-first strategy guided by performance metrics, training dynamics, and plot quality. Source anchors: lines 323-354.
6. Use specialized node types for hyperparameter search, ablations, replications with multiple random seeds, and aggregation of replicated results. Source anchors: lines 333-356.

## Validation

- The authors generated three complete manuscripts using only AI Scientist-v2 after initial broad topical prompts aligned with the ICBINB workshop scope. Source anchors: lines 420-424.
- The manuscripts were included among 43 workshop submissions; reviewers knew some submissions might be AI-generated but not which ones. Source anchors: lines 425-428.
- One of the three AI-generated manuscripts received scores 6, 6, and 7, averaging 6.33/10, and exceeded the workshop acceptance threshold. The other two were not accepted. Source anchors: lines 429-433.
- The authors conducted internal review for experimental rigor, clarity, methodological soundness, and novelty, concluding that none met typical top-tier main-track standards. Source anchors: lines 438-446.
- The accepted AI-generated paper reported negative results on compositional regularization, and reviewers valued the clear presentation of challenges and negative results while noting weaknesses such as insufficient justification, possible dataset overlap, and caption inaccuracies. Source anchors: lines 86-99 and 598-619.

## Failure Cases

- The acceptance was workshop-level rather than main-conference-level, and only one of three AI-generated submissions was accepted. Source anchors: lines 694-704.
- The system does not consistently reach workshop-level quality and is not yet at top-tier conference standards. Source anchors: lines 696-704.
- The paper identifies remaining challenges in producing genuinely novel, high-impact hypotheses, designing innovative experiments, and rigorously justifying choices with deep domain expertise. Source anchors: lines 704-708.
- The authors observed citation inaccuracies and insufficient methodological rigor in generated manuscripts. Source anchors: lines 448-452.
- Ethical handling required IRB approval, reviewer disclosure, organizer coordination, and withdrawal of the accepted AI-generated paper before publication. Source anchors: lines 457-466, 714-721.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
```

## Curated Source Note Excerpt

```markdown
# The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search

## Source

- Paper ID: `ai_scientist_v2`
- arXiv: `https://arxiv.org/abs/2504.08066`
- PDF: `papers/raw/ai_scientist_v2.pdf`
- Extracted text: `papers/extracted/ai_scientist_v2.txt`
- Render check: `output/pdf/ai_scientist_v2/page-01.png`
- Extraction notes: PDF has 69 pages. `pdftotext -layout` produced
  `papers/extracted/ai_scientist_v2.txt`. Page 1 was visually rendered and
  inspected.

## Abstract

The AI Scientist-v2 is an end-to-end agentic system for automated scientific
discovery. It formulates hypotheses, designs and executes experiments, analyzes
and visualizes data, and writes scientific manuscripts. Compared with AI
Scientist-v1, the paper says v2 removes reliance on human-authored code
templates, generalizes across machine-learning domains, and uses progressive
agentic tree search managed by an experiment manager. The paper also adds a
VLM-based review loop for improving figure, caption, and text quality. The
authors evaluated the system by submitting three autonomous manuscripts to an
ICLR workshop; one reached workshop acceptance-level scores.

Source anchors: extracted text lines 23-31, 49-58, 80-87.

## Methods

1. Start with generalized idea generation rather than code-conditioned template
   modification. The system begins from high-level research directions and can
   use literature-search tools to check novelty and identify prior work.
   Source anchors: lines 187-204.
2. Remove template dependency by turning the generated idea into an experimental
   process that does not require a hand-authored baseline code template.
   Source anchors: lines 204-216.
3. Use an Experiment Progress Manager with four stages: preliminary
   investigation, hyperparameter tuning, research agenda execution, and ablation
   studies. Each stage has stopping criteria and passes the selected best node
   to the next stage. Source anchors: lines 211-244.
4. Run parallelized agentic tree search within each stage. Each node contains an
   experiment plan, generated Python code, execution trace or error, runtime,
   metrics, LLM feedback, visualization code, generated figures, VLM feedback,
   and buggy/non-buggy status. Source anchors: lines 244-356.
5. For buggy nodes, record the error and attempt debugging. For non-buggy nodes,
   refine the experiment. Select nodes using a best-first strategy guided by
   performance metrics, training dynamics, and plot quality. Source anchors:
   lines 323-354.
6. Use specialized node types for hyperparameter search, ablations,
   replications with multiple random seeds, and aggregation of replicated
   results. Source anchors: lines 333-356.
7. Save experimental outputs into structured files and generate plots; pass
   figures through VLM critique to catch unclear labels, missing legends, or
   misleading visualizations. Source anchors: lines 259-269, 371-378.
8. Use a writing and review process after experiments to produce manuscripts,
   reflect on them, and refine visuals/captions/text. Source anchors: lines
   179-185, 371-378.

## Experiments

- The authors generated three complete manuscripts using only AI Scientist-v2
  after initial broad topical prompts aligned with the ICBINB workshop scope.
  Source anchors: lines 420-424.
- The manuscripts were included among 43 workshop submissions; reviewers knew
  some submissions might be AI-generated but not which ones. Source anchors:
  lines 425-428.
- One of the three AI-generated manuscripts received scores 6, 6, and 7,
  averaging 6.33/10, and exceeded the workshop acceptance threshold. The other
  two were not accepted. Source anchors: lines 429-433.
- The authors conducted internal review for experimental rigor, clarity,
  methodological soundness, and novelty, concluding that none met typical
  top-tier main-track standards. Source anchors: lines 438-446.
- The accepted AI-generated paper reported negative results on compositional
  regularization, and reviewers valued the clear presentation of challenges and
  negative results while noting weaknesses such as insufficient justification,
  possible dataset overlap, and caption inaccuracies. Source anchors: lines
  86-99 and 598-619.

## Limitations

- The acceptance was workshop-level rather than main-conference-level, and only
  one of three AI-generated submissions was accepted. Source anchors: lines
  694-704.
- The system does not consistently reach workshop-level quality and is not yet
  at top-tier conference standards. Source anchors: lines 696-704.
- The paper identifies remaining challenges in producing genuinely novel,
  high-impact hypotheses, designing innovative experiments, and rigorously
  justifying choices with deep domain expertise. Source anchors: lines 704-708.
- The authors observed citation inaccuracies and insufficient methodological
  rigor in generated manuscripts. Source anchors: lines 448-452.
- Ethical handling required IRB approval, reviewer disclosure, organizer
  coordination, and withdrawal of the accepted AI-generated paper before
  publication. Source anchors: lines 457-466, 714-721.
- The paper warns that community norms are needed so AI-generated science does
  not game peer review or inflate CVs. Source anchors: lines 721-733.

## Transfer Notes

- A skill derived from this paper should preserve the four-stage experiment
  manager, node status model, debug/refine branching, specialized node types,
  replication/aggregation, VLM review, and ethical disclosure requirements.
- The workflow assumes executable code sandboxes, dataset access, plotting,
  LLM/VLM calls, checkpointing, and logs. If a harness lacks these tools, the
  skill should stop or downgrade to planning mode.
- For small local runs, reduce workers, stages, and budgets before launching
  full tree search.
```
