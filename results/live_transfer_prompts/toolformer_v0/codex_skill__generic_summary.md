# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `codex_skill`
- Harness label: Codex-style SKILL.md harness

## Harness Instructions

Respond as if the context were loaded as a SKILL.md file in a coding-agent workspace. Prefer concrete files, commands, and validation gates.

## Context Variant

- Variant ID: `generic_summary`
- Variant label: Generic prose summary baseline
- Source path: `baselines/toolformer_generic_summary.md`
- Dropped sections: none

## Task

Use the provided context to plan a Toolformer-style tool-use experiment in a local agent harness. Produce a concise but executable plan that preserves API-call representation, candidate call generation, execution, loss-based filtering, augmented dataset construction, fine-tuning, inference-time tool execution, validation domains, and limitations.

## Required Output Contract

- State whether the context is sufficient for a Toolformer-style run.
- List required local tools or simulated APIs.
- Give a step-by-step run plan.
- Identify validation checks and stop conditions.
- Mark source-backed steps separately from inferred adaptations.
- Record at least one likely failed branch.

## Evaluation Notes

- This packet is for later live evaluation only.
- Do not score as live transfer until response files are collected.

## Context

# Toolformer Generic Summary

Toolformer is a language-model tool-use method. It trains a model to call APIs
such as question answering, calculator, search, translation, and calendar tools.
The method uses a small number of examples for each tool and then creates
self-supervised training data so the model can learn when tool calls help.
Toolformer improves zero-shot results on several tasks compared with similar
models, while some limitations remain around tool quality, interaction style,
and evaluation.
