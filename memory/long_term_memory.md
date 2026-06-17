# PaperToSkill Long-Term Memory

Read this file after any context compaction or session resume before taking new
project actions.

## Project Identity

- Project name: PaperToSkill.
- Core idea: turn papers into reusable agent skills.
- Target outcome: a research-backed system and paper draft that show how paper
  contributions can be extracted, operationalized, compacted, evaluated, and
  transferred across agent harnesses.
- Local project repo: `D:\a_work\gitee\PaperToSkill`.
- Remote repo: `https://github.com/yougret1/PaperToSkill.git`.
- AI-Scientist-v2 workspace: `D:\a_work\gitee\ai-scientist-v2`.

## User Intent

- The user wants durable local memory so context compaction does not erase
  project state.
- Memory must include at least two files: long-term memory and short-term memory.
- Use `ai-scientist-v2` to refine the idea, run or prepare research automation,
  and convert the idea toward implementation.
- Save phase-level progress to the PaperToSkill GitHub repo when appropriate.

## Working Definition

PaperToSkill is a paper extractor and translation workflow. It reads a target
paper and produces a `SKILL.md`-style artifact that preserves:

- the paper's central contribution and assumptions;
- the reusable method or workflow;
- concrete procedures an agent can execute;
- required inputs, outputs, tools, and validation checks;
- negative cases, limitations, and failure branches;
- compactness constraints and transfer notes for other harnesses.

## Research Direction

Primary research question:

Can papers be converted into compact, human-editable agent skills that preserve
enough procedural knowledge to reproduce or reuse the paper's main contribution?

Initial target contribution categories:

- system: a paper-to-skill extraction pipeline;
- evaluation: compactness, fidelity, usability, transferability, and cost;
- artifact: the PaperToSkill skill that can improve itself and process papers;
- analysis: success and failure cases, including failed reproduction branches.

## Current System Components

- `skill/SKILL.md`: human-facing PaperToSkill skill prototype.
- `benchmarks/paper_manifest.json`: seed benchmark paper set.
- `scripts/papertoskill_extract.py`: deterministic non-LLM extraction scaffold.
- `scripts/evaluate_skill.py`: deterministic v0 evaluator for generated skills.
- `scripts/aggregate_results_tables.py`: paper-ready Markdown/CSV table
  aggregation over existing deterministic/offline evaluation JSON.
- `tests/test_papertoskill_extract.py`: extractor smoke test.
- `tests/test_evaluate_skill.py`: evaluator smoke test.
- `generated_skills/`: retained generated examples with source maps.
- `papers/notes/ai_scientist_v2_note.md`: first curated real-paper note.
- `results/evaluations/ai_scientist_v2_rubric_v0.json`: first scored
  real-paper generated skill.
- `benchmarks/tasks/ai_scientist_v2_research_run.json`: first downstream
  context baseline task.
- `results/evaluations/ai_scientist_v2_context_baselines_v0.json`: first
  skill-vs-summary-vs-abstract deterministic comparison.
- `benchmarks/tasks/skill_source_audit.json`: source-map-aware unsupported
  instruction audit task.
- `results/evaluations/skill_source_audit_v0.json`: unsupported-rate ranking
  across real skill, paper-like case, and abstract-only seed.
- `benchmarks/tasks/ai_scientist_v2_harness_transfer.json`: offline Codex/
  Claude-style harness-transfer readiness task.
- `results/evaluations/ai_scientist_v2_harness_transfer_v0.json`: readiness
  ranking for full skill, skill without transfer notes, and generic summary.
- `benchmarks/tasks/ai_scientist_v2_live_transfer.json`: live prompt packet
  spec for later Codex/Claude execution.
- `benchmarks/tasks/ai_scientist_v2_source_span_validation.json`: source-span
  audit task for line-anchored claims.
- `results/evaluations/ai_scientist_v2_source_span_validation_v0.json`: source-
  span support-rate summary for the AI Scientist-v2 skill.
- `papers/notes/reflexion_note.md`: second curated real-paper note.
- `generated_skills/reflexion/SKILL.md`: second retained generated skill,
  focused on verbal reinforcement, reflection loops, and memory.
- `results/evaluations/reflexion_rubric_v0.json`: Reflexion skill rubric score.
- `results/evaluations/reflexion_source_span_validation_v0.json`: Reflexion
  source-span support-rate summary.
- `results/evaluations/reflexion_context_baselines_v0.json`: Reflexion
  skill-vs-summary-vs-abstract deterministic comparison.
- `results/evaluations/reflexion_harness_transfer_v0.json`: Reflexion
  transfer-readiness ranking for full skill, skill without transfer notes, and
  generic summary.
- `results/live_transfer_prompts/reflexion_v0/`: Reflexion live prompt packets
  for later Codex/Claude execution.
- `papers/notes/aide_note.md`: third curated real-paper note.
- `generated_skills/aide/SKILL.md`: third retained generated skill, focused on
  code-space tree search, draft/debug/improve actions, and solution selection.
- `results/evaluations/aide_rubric_v0.json`: AIDE skill rubric score.
- `results/evaluations/aide_source_span_validation_v0.json`: AIDE source-span
  support-rate summary.
- `results/evaluations/aide_context_baselines_v0.json`: AIDE
  skill-vs-summary-vs-abstract deterministic comparison.
- `results/evaluations/aide_harness_transfer_v0.json`: AIDE transfer-readiness
  ranking for full skill, skill without transfer notes, and generic summary.
- `results/live_transfer_prompts/aide_v0/`: AIDE live prompt packets for later
  Codex/Claude execution.
- `results/tables/`: paper-ready main results, transfer ablation, compactness/
  source-grounding, and combined summary tables.

## Current Assumptions

- "Skill" means a natural-language operational guide for an agent, similar to
  Codex skills with a `SKILL.md` entry point and optional bundled resources.
- The paper should emphasize practical conversion, not only successful final
  outputs.
- Failure traces are valuable and should be recorded rather than hidden.
- Transfer evaluation should include moving skills between harnesses, especially
  Codex-to-Claude or another agent runtime.

## LLM/API Configuration

The user provided an OpenAI-compatible server and model for agent/LLM use:

- Server: `https://coderxiaoc.com`
- Requested model: `claude-opus-4.8`

Do not commit raw API keys to tracked repository files. Prefer environment
variables:

- `AI_SCIENTIST_OPENAI_BASE_URL`
- `AI_SCIENTIST_OPENAI_API_KEY`
- `AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE=1`

The current `ai-scientist-v2` working tree already appears to include local
support for OpenAI-compatible backends and local-laptop BFTS settings.

## Persistent Rules

- Keep exploratory ideas, active work, and validated claims separate.
- Promote an item to validated memory only when backed by source evidence,
  code, experiment logs, or explicit user decision.
- Record decisions in `research/decision_log.md`.
- Record active work and blockers in `memory/short_term_memory.md`.
- If context was compacted, read this file and
  `memory/short_term_memory.md` first.
