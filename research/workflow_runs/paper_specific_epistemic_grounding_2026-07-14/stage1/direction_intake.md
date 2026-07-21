# Stage 1.1 Direction Intake

## Working Direction

PaperToSkill should help non-expert researchers and agent builders extract,
verify, adapt, and re-validate a paper's core research workflow while keeping
the original evidence boundary visible.

The original user-facing wording is:

> 适用于普通人快速对一篇论文的核心研究进行提取，验证以及快速修改

Here, "ordinary users" is operationalized as users who have basic task or
domain context but are not experts in the paper's specific method. "Modify" is
interpreted as adapting the method to a new task, not changing the original
paper's facts or results.

## Technical Thesis

The differentiating mechanism is paper-specific epistemic grounding:

1. Align claims, method actions, assumptions, validation evidence, and failure
   boundaries.
2. Label generated content as supported, inferred, conflicted, or missing.
3. Keep source evidence immutable and record user adaptations as typed deltas.
4. Propagate each delta to the claims and assumptions it invalidates.
5. Produce explicit re-validation requirements before an adapted workflow is
   treated as trustworthy.

## Research Boundary

- The new run must evaluate direct paper inputs or measure every human curation
  step. A hidden curated note cannot carry the central claim.
- Source-line validity is not evidence entailment.
- Portability requires matched cross-harness evidence.
- Existing v1 deterministic and real-reuse results are historical inputs, not
  automatically accepted evidence for the new thesis.

## Stage 1 Routing

The direction is specific and literature-groundable. Route to `1.2` for real
retrieval and full-text verification, with Anything2Skill, Paper2Agent, SkCC,
and SkillWiki treated as named high-risk adjacent work.

