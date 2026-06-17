---
name: papertoskill
description: Convert research papers, paper drafts, arXiv PDFs, method sections, or paper-like idea notes into reusable Codex/agent skills. Use when Codex needs to extract a paper's transferable method, assumptions, workflow, validation checks, limitations, failure cases, and cross-harness transfer notes into a concise SKILL.md artifact.
---

# PaperToSkill

Convert a paper into an agent skill, not a summary. Preserve the paper's
operational contribution, evidence boundaries, and failure cases in a compact
form another agent can use.

## Inputs

Accept any of:

- paper PDF, Markdown, LaTeX, HTML, or text;
- paper section plus supplementary material;
- research idea note that should become a skill prototype.

When the source is a PDF, extract text and figures before writing the skill. Keep
page or section references where possible.

## Output

Produce a skill folder with:

- `SKILL.md` as the required entry point;
- optional `references/` files for long source-grounded details;
- optional `scripts/` only when deterministic tooling is needed;
- optional `assets/` only for templates or media used by the skill.

Do not add README, changelog, installation guides, or extra documentation unless
the user explicitly asks for them.

## Extraction Workflow

1. Identify the paper's central contribution in one sentence.
2. Extract the target user, use case, and conditions where the method applies.
3. Separate source-backed facts from inferences.
4. Convert the method into an ordered agent workflow.
5. Extract required inputs, tools, data, and environment assumptions.
6. Add validation checks that would catch common wrong outputs.
7. Add failure cases, limitations, and situations where the skill should stop.
8. Add transfer notes for other agent harnesses when tool names, memory, browser,
   file access, or execution semantics may differ.
9. Compress the skill until only action-guiding context remains.
10. Run a structural review before finalizing.

## Skill Structure

Use this structure unless the paper clearly needs something else:

```markdown
---
name: <lowercase-hyphen-name>
description: <what it does and when to use it>
---

# <Skill Title>

<One paragraph describing the operational purpose.>

## Inputs

<Required source artifacts or task inputs.>

## Workflow

<Numbered steps an agent can execute.>

## Validation

<Checks before claiming success.>

## Failure Cases

<When to stop, warn, downgrade, or ask for help.>

## Transfer Notes

<Harness-specific assumptions and adaptations.>
```

## Fidelity Rules

- Do not invent a method step because it sounds plausible.
- Mark uncertain or inferred steps explicitly.
- If the paper lacks enough implementation detail, include a stop condition or
  a required clarification rather than filling the gap silently.
- Keep citations or section anchors for fragile claims.
- Preserve negative results and failed branches when the source reports them.

## Compactness Rules

- Keep `SKILL.md` focused on what the agent must do.
- Move long examples, paper quotes, tables, and source maps into `references/`.
- Remove background material that does not change agent behavior.
- Prefer concrete checks over broad advice.

## Validation

Before delivering the generated skill, check:

- frontmatter has only `name` and `description`;
- the description contains the trigger conditions;
- the workflow is executable by an agent without rereading the whole paper;
- unsupported claims are marked or removed;
- limitations and failure cases are present;
- transfer notes mention any harness-specific assumptions.

