# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `claude_project_prompt`
- Harness label: Claude-style project prompt harness

## Harness Instructions

Act as a project-level research assistant using the provided context as reusable project instructions. Produce a harness-neutral code-optimization plan that a Claude-style agent could follow, including assumptions, unavailable tools, validation checks, and transfer-specific adaptations.

## Context Variant

- Variant ID: `skill_without_transfer_notes`
- Variant label: Generated skill with Transfer Notes removed
- Source path: `generated_skills/aide/SKILL.md`
- Dropped sections: Transfer Notes

## Task

Given the PaperToSkill idea, produce a small local AIDE-style code optimization run plan. The plan must preserve a solution tree, stateless objective function, draft/debug/improve actions, context summarization, data preview, validation metrics, best-solution selection, limitations, and harness-transfer adaptations.

## Required Output Contract

- A concise run objective for an AIDE-style PaperToSkill code optimization experiment.
- A solution-tree schema covering node code, parent edge, score, buggy status, and selected base node.
- A draft/debug/improve loop with debug-depth budget and one atomic measurable change per improve step.
- A context summary schema covering performance metrics, hyperparameters, and debugging hints.
- A data-preview schema covering dataset size, column names, data splits, and target metric.
- A validation plan with objective function, local execution commands, final best-solution selection, and failure recording.
- Limitations copied or adapted from the source-backed skill.
- A transfer-adaptation note explaining what changed for the target harness.

## Evaluation Notes

- Do not claim live experimental success unless an actual run was executed.
- Preserve source-backed claims separately from harness-specific adaptations.
- Record missing code execution, missing datasets, unavailable scoring, or excessive cost as limitations.

## Context

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
