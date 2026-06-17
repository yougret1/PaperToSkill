# Experiment Design

## Experiment 0: Infrastructure Smoke Test

- Question: Can the project call the configured LLM endpoint through
  AI-Scientist-v2?
- Hypothesis: the local OpenAI-compatible changes are sufficient once required
  dependencies are installed and the correct base URL/model alias are used.
- Dataset: none.
- Baselines: direct OpenAI-compatible chat completion.
- Metrics: request succeeds, response text matches instruction.
- Failure criteria: missing dependency, 401/404, unsupported model, incompatible
  tool calling.
- Commands: run a minimal `ai_scientist.llm.create_client` call with
  environment variables.
- Output files: update `memory/short_term_memory.md` and run log.

## Experiment 1: Paper-To-Skill Smoke Conversion

- Question: Can PaperToSkill produce a valid skill from one paper-like input?
- Hypothesis: a structured extraction workflow can produce a `SKILL.md` with
  triggers, workflow, validation checks, and transfer notes.
- Dataset: the user's PaperToSkill idea text as the initial paper-like source;
  later replace or supplement with a real agent paper.
- Baselines: generic paper summary.
- Method variants: with and without explicit failure-case extraction.
- Metrics: skill structural validity, instruction coverage, unsupported-step
  count, agent usability.
- Failure criteria: generated skill lacks actionable workflow, invents key
  unsupported claims, or cannot be used by another agent.
- Output files: `skill/SKILL.md`, validation notes, result card.

## Experiment 2: Compactness Cost

- Question: How much context can be saved while preserving task performance?
- Hypothesis: a skill keeps the operational core of a paper at lower token cost
  than full paper excerpts.
- Dataset: 3-5 papers or paper sections.
- Baselines: full paper excerpt, abstract, generic summary.
- Metrics: input tokens, output tokens, endpoint cost estimate, success per 1k
  tokens.
- Failure criteria: compact skill loses key method steps or performs worse than
  summaries.
- Output files: cost table and examples.

## Experiment 3: Harness Transfer

- Question: Does a PaperToSkill output transfer across agent harnesses?
- Hypothesis: including tool contracts, assumptions, and transfer notes improves
  portability.
- Dataset: at least two generated skills and paired tasks.
- Baselines: skill without transfer notes, generic summary.
- Metrics: task success, number of user interventions, error categories.
- Failure criteria: transfer notes do not change outcomes or create confusion.
- Output files: harness transfer table and transcript snippets.

## Experiment 4: Failure Branch Audit

- Question: Do documented failed branches improve the honesty and usefulness of
  the final paper/system?
- Hypothesis: explicitly recording failure cases prevents overclaiming and helps
  future users debug reproduction attempts.
- Dataset: failed conversions, failed task runs, failed transfer cases.
- Baselines: success-only reporting.
- Metrics: number of claim downgrades, number of reproducible failure cases,
  reviewer objection coverage.
- Failure criteria: failure logs are too vague to guide any decision.
- Output files: failure-case archive and limitations section notes.

