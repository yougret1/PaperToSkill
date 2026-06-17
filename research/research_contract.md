# Research Contract

## Project

PaperToSkill.

## Paper Type

System and evaluation paper with an accompanying reusable artifact.

## Audience

- Agent builders who want to reuse recent research methods.
- Researchers who want their papers to become executable agent workflows.
- Non-expert users who can edit natural-language skills more easily than code.

## Problem Statement

Many useful LLM/agent research ideas are locked inside papers. Non-experts can
read summaries, but they often cannot turn a method section into a reliable
agent workflow. PaperToSkill investigates whether a paper can be converted into a
compact, editable skill that preserves enough procedural knowledge for an agent
to apply, reproduce, or adapt the contribution.

## Core Hypothesis

Paper-derived skills can improve agent task performance and transferability over
generic paper summaries while remaining compact enough for practical context
budgets.

## Required Artifacts

- PaperToSkill extraction workflow.
- A first PaperToSkill skill artifact.
- Benchmark paper set and generated skills.
- Evaluation scripts and result cards.
- Paper draft outline and claim-evidence matrix.
- Failure-case archive.

## Available Resources

- Local project repo: `D:\a_work\gitee\PaperToSkill`.
- AI-Scientist-v2 repo: `D:\a_work\gitee\ai-scientist-v2`.
- OpenAI-compatible LLM endpoint supplied by the user.
- Codex skill format examples from local skills.

## Constraints

- Do not lose state across context compaction; keep memory files current.
- Do not revert unrelated local modifications in `ai-scientist-v2`.
- Do not commit raw API keys to tracked files.
- Keep claims separate from evidence until experiments support them.

## Initial Acceptance Criteria

The first research milestone is worth keeping if it produces:

- a clear extraction specification for converting papers into skills;
- at least one valid generated `SKILL.md` from a paper or paper-like input;
- a dry-run or smoke-test path through AI-Scientist-v2 using PaperToSkill inputs;
- an experiment plan with measurable metrics for fidelity, compactness,
  transferability, and cost.

