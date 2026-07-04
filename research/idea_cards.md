# Idea Cards

## Idea Card 1: PaperToSkill Extractor

- Name: `papertoskill_extractor`
- Problem: papers contain reusable agent methods, but ordinary users and agents
  cannot reliably convert them into operational workflows.
- Target audience or scientific need: agent users, agent framework developers,
  and researchers who want paper contributions to become reusable artifacts.
- Core insight: a skill is a compact, editable middle layer between a paper and
  code; it can encode method, constraints, validation, and failure branches.
- Difference from prior work: unlike paper summarization, PaperToSkill targets
  executable procedural transfer and cross-harness reuse.
- Falsifiable claim: on selected original-style paper tasks, paper-derived
  skills can enable better method reuse than generic summaries, while current
  evidence must be reported as mixed until paired task rows are stable.
- Minimum viable experiment: convert the selected main-paper set into skills,
  run the locked eight `paper-task` Summary-vs-PaperToSkill grid under the
  same input/output/scorer contracts, and report task success plus
  failure-boundary modes before making any aggregate-effectiveness claim.
- Baselines: generic paper Summary for the main table; paper-reported reference
  scores where available; a small Full Excerpt sanity check only as auxiliary
  context/cost evidence.
- Ablations: remove failure cases, remove validation checks, remove transfer
  notes, vary compression level.
- Data and compute: locked AIDE, SWE-agent, Reflexion, and SnapATAC2
  paper-tasks; LLM-based task execution with generous timeout/retry budgets;
  task-specific automatic scorers plus bounded human-fidelity review as
  supporting evidence.
- Risks: novelty overlap with paper summarization, subjective evaluation,
  endpoint/tool instability, generated skills may overfit examples.
- Decision: primary idea.

## Idea Card 2: Skill Fidelity Judge

- Name: `skill_fidelity_judge`
- Problem: generated skills may be fluent but omit important paper assumptions or
  invent unsupported steps.
- Target audience or scientific need: anyone generating skills from papers.
- Core insight: extraction should be judged by traceable coverage of paper claims,
  not surface readability.
- Difference from prior work: focuses on skill-level operational fidelity rather
  than summary factuality alone.
- Falsifiable claim: a claim-step-evidence audit reduces unsupported skill
  instructions and improves reproduction reliability.
- Minimum viable experiment: compare generated skills before and after audit on
  coverage, hallucination, and downstream task success.
- Baselines: unverified generated skill, generic LLM critique.
- Ablations: no source map, no negative-case audit, no validation checklist.
- Data and compute: same paper set as primary idea.
- Risks: judge may be noisy, requires careful source mapping.
- Decision: supporting module.

## Idea Card 3: Harness Transfer Evaluation

- Name: `harness_transfer_eval`
- Problem: a skill useful in one agent harness may fail in another due to tool,
  context, or instruction differences.
- Target audience or scientific need: users sharing reusable skills across Codex,
  Claude, and other agent runtimes.
- Core insight: transfer notes and interface assumptions are first-class parts of
  a skill, not afterthoughts.
- Difference from prior work: evaluates portability of paper-derived procedural
  knowledge, not only task performance in one harness.
- Falsifiable claim: explicit transfer notes improve success when moving a skill
  between Codex and Claude-like harnesses.
- Minimum viable experiment: run equivalent paper-to-task workflows in two
  harnesses using skills with and without transfer notes.
- Baselines: skill without transfer notes, generic summary.
- Ablations: tool contract removed, output constraints removed, memory protocol
  removed.
- Data and compute: small tasks and cross-agent transcripts.
- Risks: access to equivalent harnesses, noisy comparisons.
- Decision: main ablation/experiment family.
