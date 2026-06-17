---
name: papertoskill-paper-note
description: Use when applying the paper-derived method from PaperToSkill Turning Research Papers into Reusable Agent Skills as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# PaperToSkill: Turning Research Papers into Reusable Agent Skills

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `examples/papertoskill_paper_note.md`

## Paper Snapshot

We propose PaperToSkill, a system for converting research papers into compact, human-
editable agent skills. The system extracts a paper's operational contribution, source-
backed workflow, tool assumptions, validation checks, failure cases, and cross-harness
transfer notes. The resulting skill is intended to help non-expert users reuse frontier
research methods without reading or rewriting an entire paper.

## Central Contribution

We propose PaperToSkill, a system for converting research papers into compact, human-
editable agent skills.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Parse the source paper into sections and preserve source anchors for fragile claims.
2. Identify the central contribution and separate operational method steps from background motivation.
3. Translate source-backed method steps into an agent workflow with explicit inputs, outputs, tools, assumptions, and stop conditions.
4. Add validation checks that can detect unsupported instructions, missing assumptions, and failed reproduction branches.
5. Add compactness and transfer notes so the generated skill can move across Codex-like and Claude-like agent harnesses.
6. Store a source map and failure-case log so the skill can be audited and revised.

## Validation

- Compare agents using PaperToSkill outputs against agents using no paper context, abstract-only summaries, generic LLM summaries, and full paper excerpts.
- Measure downstream task success, workflow coverage, unsupported instruction rate, token cost, and success per 1k tokens.
- Run ablations that remove source mapping, validation checks, failure-case extraction, and transfer notes.
- Evaluate harness transfer by moving generated skills between Codex-style and Claude-style agent prompts.

## Failure Cases

- Stop when the paper lacks enough procedural detail to define a workflow.
- Warn when the generated skill requires unavailable tools, datasets, licenses, or execution privileges.
- Downgrade claims when validation results are missing, noisy, or only indirectly related to the intended skill behavior.
- Record failed conversions and failed downstream task runs as first-class evidence rather than hiding them from the final paper.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
