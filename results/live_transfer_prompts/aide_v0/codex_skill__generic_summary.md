# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `codex_skill`
- Harness label: Codex-style coding-agent harness

## Harness Instructions

Act as a coding research agent using the provided context as a skill. Produce an executable local plan with file artifacts, commands, validation checks, logs, retry conditions, and stop conditions. Be explicit about what is source-backed versus adapted for the local Codex workspace.

## Context Variant

- Variant ID: `generic_summary`
- Variant label: Generic prose summary baseline
- Source path: `baselines/aide_generic_summary.md`
- Dropped sections: none

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

# AIDE Generic Summary

AIDE is an LLM-based agent for machine-learning engineering. It treats ML work
as iterative code optimization and searches over possible solutions using a
tree-like process. The system drafts code, fixes bugs, and improves models based
on evaluation feedback. It was tested on Kaggle-style benchmarks, MLE-Bench, and
RE-Bench, where it achieved competitive results compared with other automated
agents and some human baselines. Its limitations include possible benchmark
contamination, evaluation mismatch with private leaderboards, local optima, and
cost from repeated LLM calls.
