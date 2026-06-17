---
name: papertoskill-seed
description: Use when applying the paper-derived method from PaperToSkill Seed as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# PaperToSkill Seed

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `ai_scientist_inputs/papertoskill.md`

## Paper Snapshot

Modern LLM and agent research produces many methods that could improve everyday
workflows, but most people cannot directly operationalize a paper's method section into
a reliable agent workflow. We propose PaperToSkill, a system that converts research
papers into reusable agent skills. A skill is a concise, natural-language artifact that
defines when it should be used, what inputs it requires, how an agent should execute the
method, how outputs should be validated, and which limitations or failure cases must be
respected. The central hypothesis is that paper-derived skills can preserve procedural
knowledge better than generic summaries while using less context than full paper
excerpts. PaperToSkill treats extraction as a structured process: identify the paper's
contribution, separate claims from evidence, extract the operational workflow, encode
assumptions and tool contracts, add validation checks, and record failure branches. The
resulting skill should be editable by non-experts and portable across agent harnesses.
Experiments should evaluate fidelity, downstream task success, compactness cost, and
cross-harness transfer. Baselines include no paper context, abstract-only summaries,
generic LLM summaries, and full paper excerpts. Ablations should remove failure-case
extraction, validation checks, source mapping, and transfer notes. The project should
also study negative results: successful applications alone are insufficient for a system
that claims to turn research into practice.

## Central Contribution

We propose PaperToSkill, a system that converts research papers into reusable agent
skills.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Read the source paper and identify the operational method behind: We propose PaperToSkill, a system that converts research papers into reusable agent skills.
2. Separate source-backed method steps from inferred implementation details.
3. Translate each method step into an agent action with required inputs and outputs.
4. Add validation checks and stop conditions before using the skill on a real task.

## Validation

- Check that every workflow step maps to a source section or is marked as an inference.
- Run the skill on a small task before claiming it captures the paper's method.
- Record task outcome, missing assumptions, and unsupported instructions.

## Failure Cases

- Stop if the paper does not provide enough procedural detail to define an agent workflow.
- Warn if the generated skill requires tools, data, or environment access not available to the current harness.
- Downgrade claims when validation evidence is absent or only indirectly related.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
