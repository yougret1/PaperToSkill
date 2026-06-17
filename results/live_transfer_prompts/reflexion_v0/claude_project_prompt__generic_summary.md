# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `claude_project_prompt`
- Harness label: Claude-style project prompt harness

## Harness Instructions

Act as a project-level research assistant using the provided context as reusable project instructions. Produce a harness-neutral retry-and-reflection plan that a Claude-style agent could follow, including assumptions, unavailable tools, validation checks, and transfer-specific adaptations.

## Context Variant

- Variant ID: `generic_summary`
- Variant label: Generic prose summary baseline
- Source path: `baselines/reflexion_generic_summary.md`
- Dropped sections: none

## Task

Given the PaperToSkill idea, produce a small local retry-and-reflection agent run plan inspired by Reflexion. The plan must preserve Actor/Evaluator/Self-Reflection roles, short-term and long-term memory, feedback-to-reflection conversion, retry policy, validation metrics, limitations, and harness-transfer adaptations.

## Required Output Contract

- A concise run objective for the PaperToSkill retry-and-reflection experiment.
- A role table covering Actor, Evaluator, and Self-Reflection responsibilities.
- A memory schema distinguishing short-term trajectory history from long-term reflection memory.
- A trial loop with feedback collection, reflection generation, memory update, and retry/stop conditions.
- A feedback-source plan covering environment feedback, heuristics, self-generated tests, or evaluator scoring.
- A validation plan with measurable success criteria and failure recording.
- Limitations copied or adapted from the source-backed skill.
- A transfer-adaptation note explaining what changed for the target harness.

## Evaluation Notes

- Do not claim live experimental success unless an actual run was executed.
- Preserve source-backed claims separately from harness-specific adaptations.
- Record missing tools, unavailable feedback sources, or non-executable environments as limitations.

## Context

# Generic Summary: Reflexion

Reflexion is a framework for improving language agents through verbal
reinforcement instead of updating model weights. It lets an agent reflect on
feedback from failed attempts, store lessons in memory, and use those lessons in
later trials.

The paper describes an actor that performs actions, an evaluator that scores
outcomes, and a self-reflection model that converts feedback into natural
language advice. The approach is tested on decision-making, reasoning, and
programming tasks, where it improves over several baselines.

The paper also notes limitations: agents can still get stuck, memory is bounded
by a simple window, and some tasks require more creative behavior than the
method reliably discovers.
