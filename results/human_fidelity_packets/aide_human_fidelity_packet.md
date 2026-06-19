# Human Fidelity Review Packet: AIDE

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

- Generated skill: `generated_skills/aide/SKILL.md`
- Curated source note: `papers/notes/aide_note.md`
- Extracted paper text: `papers/extracted/aide.txt`
- Source map: `generated_skills/aide/references/source_map.json`
- Source-span report: `results/evaluations/aide_source_span_validation_v0.json`
- Deterministic skill coverage: 9.1/10
- Source-span support rate: 1.0
- Invalid source-span ranges: 0
- Source-map entries: 21
- Skill words: 927
- Source note words: 899

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
name: aide-paper-skill
description: Use when applying the paper-derived method from AIDE AI-Driven Exploration in the Space of Code as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# AIDE: AI-Driven Exploration in the Space of Code

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/notes/aide_note.md`

## Paper Snapshot

AIDE is an LLM-powered machine-learning engineering agent. It frames ML engineering as
code optimization and treats trial-and-error as tree search over candidate code
solutions. AIDE reuses and refines promising solutions, evaluates each candidate with an
objective function, and reports strong results across Kaggle, MLE-Bench, and RE-Bench.
Source anchors: extracted text lines 23-32.

## Central Contribution

AIDE is an LLM-powered machine-learning engineering agent.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Model the task as optimization over a solution space of Python scripts, with a stateless objective function such as validation accuracy or loss. Each candidate solution can be evaluated independently and compared. Source anchors: lines 91-102.
2. Run AI-Driven Exploration as iterative tree search: initialize a solution tree, propose a new solution, evaluate it, record the node and score, select the next base node, and return the best-scoring solution. Source anchors: lines 117-126.
3. Store every discovered solution in a solution tree. Nodes correspond to scripts, edges represent improvement attempts, a search policy selects the base solution, a summarization operator extracts relevant history, and a coding operator proposes new scripts. Source anchors: lines 132-144.
4. Use a hard-coded search policy that chooses drafting for initial solutions, debugging for buggy nodes within a debug-depth budget, and improving for the best non-buggy solution. Source anchors: lines 152-162.
5. Implement the coding operator with three specialized actions: drafting a single-file program from scratch, debugging by inspecting error logs and traces while preserving the approach, and improving a valid solution with one atomic measurable change. Source anchors: lines 167-199.
6. Keep prompts concise with a summarization operator that extracts performance metrics, hyperparameters, and debugging hints rather than appending all historical logs. Source anchors: lines 201-211.
7. Include a static data preview with dataset size, column names, or data splits so coding prompts can make validation and hyperparameter decisions without a full EDA pipeline. Source anchors: lines 213-217.
8. Combine search policy, coding operator, and summarization under a stateless optimization framework to search code solutions without ever-increasing prompt history. Source anchors: lines 221-227.

## Validation

- The paper reports AIDE's own Kaggle evaluation and aggregates independent MLE-Bench and RE-Bench results. Source anchors: lines 229-239.
- Weco-Kaggle contains 63 competitions; Weco-Kaggle Lite uses 16 lower- complexity tabular ML tasks with primarily CPU runtime requirements. Source anchors: lines 241-250.
- The Kaggle protocol splits training data into train and holdout test sets, prompts AIDE to produce `submission.csv`, and reports Exceeds % of Human and Above Median metrics. Source anchors: lines 252-280.
- On Weco-Kaggle Lite, AIDE with GPT-4 Turbo reached 51.38 Exceeds % of humans and 50.00 Above Median, outperforming H2O AutoML and AutoGPT in the table. Source anchors: lines 282-291, 337-345.
- In MLE-Bench pass@1, AIDE is compared with MLAB and OpenHands across valid submissions, above-median rate, gold medals, and any-medal rate. AIDE with o1-preview reports 82.8 valid submissions and 16.9 any medals. Source anchors: lines 379-392.
- AIDE's solution-tree strategy keeps node-level code concise, preserves a performance record for each node, refines partial solutions over a 24-hour timeframe, and improves pass@k success with additional attempts. Source anchors: lines 450-473.
- In RE-Bench, AIDE outperformed humans within six hours on average and found an Optimize a Kernel solution faster than the nine human experts, but humans later caught up. Source anchors: lines 488-498.

## Failure Cases

- Kaggle holdout sets may differ from official private test sets, so percentile scores may not always be directly comparable. Source anchors: lines 396-398.
- There is possible data contamination because models may have seen competition-related data; the paper says live competition submissions are the only way to fully ensure no contamination. Source anchors: lines 398-402.
- AIDE can adopt a simple greedy policy that may lead to local optima on challenging R&D tasks. Source anchors: lines 488-491.
- AIDE fell short in environments requiring larger codebases or single improvements with multiple steps of interaction; in Rust CodeContests it repeated local patches instead of discovering new strategies. Source anchors: lines 494-501.
- While AIDE was developed for tabular machine-learning tasks, third-party experiments suggest the approach can generalize to neural architecture search, Triton Kernel optimization, and other AI R&D tasks. Source anchors: lines 537-545.
- LLM inference cost can reach approximately 2.50 USD for some tasks, although most Weco-Kaggle tasks stay under 1.50 USD in the reported GPT-4 Turbo pricing setup. Source anchors: lines 744-752.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
```

## Curated Source Note Excerpt

```markdown
# AIDE: AI-Driven Exploration in the Space of Code

## Source

- Paper ID: `aide`
- arXiv: `https://arxiv.org/abs/2502.13138`
- PDF: `papers/raw/aide.pdf`
- Extracted text: `papers/extracted/aide.txt`
- Render check: `output/pdf/aide/page-01.png`
- Extraction notes: PDF has 17 pages. `pdftotext -layout` produced
  `papers/extracted/aide.txt`. Page 1 was visually rendered and inspected.

## Abstract

AIDE is an LLM-powered machine-learning engineering agent. It frames ML
engineering as code optimization and treats trial-and-error as tree search over
candidate code solutions. AIDE reuses and refines promising solutions, evaluates
each candidate with an objective function, and reports strong results across
Kaggle, MLE-Bench, and RE-Bench.

Source anchors: extracted text lines 23-32.

## Methods

1. Model the task as optimization over a solution space of Python scripts, with
   a stateless objective function such as validation accuracy or loss. Each
   candidate solution can be evaluated independently and compared. Source
   anchors: lines 91-102.
2. Run AI-Driven Exploration as iterative tree search: initialize a solution
   tree, propose a new solution, evaluate it, record the node and score, select
   the next base node, and return the best-scoring solution. Source anchors:
   lines 117-126.
3. Store every discovered solution in a solution tree. Nodes correspond to
   scripts, edges represent improvement attempts, a search policy selects the
   base solution, a summarization operator extracts relevant history, and a
   coding operator proposes new scripts. Source anchors: lines 132-144.
4. Use a hard-coded search policy that chooses drafting for initial solutions,
   debugging for buggy nodes within a debug-depth budget, and improving for the
   best non-buggy solution. Source anchors: lines 152-162.
5. Implement the coding operator with three specialized actions: drafting a
   single-file program from scratch, debugging by inspecting error logs and
   traces while preserving the approach, and improving a valid solution with
   one atomic measurable change. Source anchors: lines 167-199.
6. Keep prompts concise with a summarization operator that extracts performance
   metrics, hyperparameters, and debugging hints rather than appending all
   historical logs. Source anchors: lines 201-211.
7. Include a static data preview with dataset size, column names, or data splits
   so coding prompts can make validation and hyperparameter decisions without a
   full EDA pipeline. Source anchors: lines 213-217.
8. Combine search policy, coding operator, and summarization under a stateless
   optimization framework to search code solutions without ever-increasing
   prompt history. Source anchors: lines 221-227.

## Experiments

- The paper reports AIDE's own Kaggle evaluation and aggregates independent
  MLE-Bench and RE-Bench results. Source anchors: lines 229-239.
- Weco-Kaggle contains 63 competitions; Weco-Kaggle Lite uses 16 lower-
  complexity tabular ML tasks with primarily CPU runtime requirements. Source
  anchors: lines 241-250.
- The Kaggle protocol splits training data into train and holdout test sets,
  prompts AIDE to produce `submission.csv`, and reports Exceeds % of Human and
  Above Median metrics. Source anchors: lines 252-280.
- On Weco-Kaggle Lite, AIDE with GPT-4 Turbo reached 51.38 Exceeds % of humans
  and 50.00 Above Median, outperforming H2O AutoML and AutoGPT in the table.
  Source anchors: lines 282-291, 337-345.
- In MLE-Bench pass@1, AIDE is compared with MLAB and OpenHands across valid
  submissions, above-median rate, gold medals, and any-medal rate. AIDE with
  o1-preview reports 82.8 valid submissions and 16.9 any medals. Source anchors:
  lines 379-392.
- AIDE's solution-tree strategy keeps node-level code concise, preserves a
  performance record for each node, refines partial solutions over a 24-hour
  timeframe, and improves pass@k success with additional attempts. Source
  anchors: lines 450-473.
- In RE-Bench, AIDE outperformed humans within six hours on average and found an
  Optimize a Kernel solution faster than the nine human experts, but humans
  later caught up. Source anchors: lines 488-498.

## Limitations

- Kaggle holdout sets may differ from official private test sets, so percentile
  scores may not always be directly comparable. Source anchors: lines 396-398.
- There is possible data contamination because models may have seen
  competition-related data; the paper says live competition submissions are the
  only way to fully ensure no contamination. Source anchors: lines 398-402.
- AIDE can adopt a simple greedy policy that may lead to local optima on
  challenging R&D tasks. Source anchors: lines 488-491.
- AIDE fell short in environments requiring larger codebases or single
  improvements with multiple steps of interaction; in Rust CodeContests it
  repeated local patches instead of discovering new strategies. Source anchors:
  lines 494-501.
- While AIDE was developed for tabular machine-learning tasks, third-party
  experiments suggest the approach can generalize to neural architecture search,
  Triton Kernel optimization, and other AI R&D tasks. Source anchors: lines
  537-545.
- LLM inference cost can reach approximately 2.50 USD for some tasks, although
  most Weco-Kaggle tasks stay under 1.50 USD in the reported GPT-4 Turbo pricing
  setup. Source anchors: lines 744-752.

## Transfer Notes

- A skill derived from AIDE should preserve the solution tree, node scores,
  draft/debug/improve action split, debug-depth budget, best-node improvement
  policy, context summarization, data preview, and final best-solution
  selection.
- The workflow assumes executable Python code, a scoring function, dataset
  access, error logs, tracebacks, repeated attempts, and enough compute budget
  for iterative evaluation.
- If the target harness lacks code execution or reliable scoring, the skill
  should downgrade to planning mode and explicitly mark unverified

[Excerpt truncated for review packet. See source file for full text.]
```
