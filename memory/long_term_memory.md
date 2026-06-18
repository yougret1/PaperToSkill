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
- `scripts/papertoskill_note_from_text.py`: deterministic extracted-text-to-note
  scaffold that selects line-window evidence from `pdftotext` output and emits
  source-anchored Markdown notes.
- `scripts/evaluate_skill.py`: deterministic v0 evaluator for generated skills.
- `scripts/aggregate_results_tables.py`: paper-ready Markdown/CSV table
  aggregation over existing deterministic/offline evaluation JSON.
- `scripts/evaluate_context_costs.py`: deterministic context token/cost proxy
  evaluator over full papers, notes, skills, summaries, and abstracts.
- `scripts/build_human_fidelity_packets.py`: builds human-fidelity review
  packets and blank annotation template.
- `scripts/summarize_human_fidelity_annotations.py`: summarizes and validates
  human-fidelity annotation rows.
- `scripts/build_failure_case_archive.py`: builds a failure-case archive from
  paper source maps and project-level failure/fix records.
- `scripts/check_reproducibility_package.py`: checks local reproducibility
  package readiness and separates pending external evidence from local failures.
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
- `papers/notes/toolformer_note.md`: fourth curated real-paper note, focused on
  self-supervised tool use and API-call selection.
- `generated_skills/toolformer/SKILL.md`: fourth retained generated skill,
  focused on text-to-text API calls, sample/execute/filter data generation,
  fine-tuning, inference-time tool execution, and tool-use limitations.
- `results/evaluations/toolformer_rubric_v0.json`: Toolformer skill rubric
  score.
- `results/evaluations/toolformer_source_span_validation_v0.json`: Toolformer
  source-span support-rate summary.
- `results/evaluations/toolformer_context_baselines_v0.json`: Toolformer
  skill-vs-summary-vs-abstract deterministic comparison.
- `results/evaluations/toolformer_harness_transfer_v0.json`: Toolformer
  transfer-readiness ranking for full skill, skill without transfer notes, and
  generic summary.
- `results/live_transfer_prompts/toolformer_v0/`: Toolformer live prompt
  packets for later Codex/Claude execution.
- `papers/auto_notes/toolformer_auto_note.md`: first deterministic automatic
  note scaffold from extracted paper text.
- `generated_skills/toolformer_auto/SKILL.md`: first retained auto-note-derived
  skill, generated from `papers/extracted/toolformer.txt` via the automatic
  note scaffold.
- `results/evaluations/toolformer_auto_note_scaffold_v0.json`: line-window
  selection report for the Toolformer automatic note scaffold.
- `results/evaluations/toolformer_auto_rubric_v0.json`: Toolformer
  auto-note-derived skill rubric score.
- `results/evaluations/toolformer_auto_context_baselines_v0.json`: Toolformer
  auto-note-derived skill-vs-summary-vs-abstract deterministic comparison.
- `results/evaluations/toolformer_auto_harness_transfer_v0.json`: Toolformer
  auto-note-derived transfer-readiness ranking.
- `results/evaluations/toolformer_auto_source_span_validation_v0.json`:
  Toolformer auto-note-derived source-span validation summary.
- `papers/auto_notes/aide_auto_note.md`: second deterministic automatic note
  scaffold from extracted paper text, using the AIDE profile.
- `generated_skills/aide_auto/SKILL.md`: second retained auto-note-derived
  skill, generated from `papers/extracted/aide.txt` via the automatic note
  scaffold.
- `results/evaluations/aide_auto_note_scaffold_v0.json`: line-window selection
  report for the AIDE automatic note scaffold.
- `results/evaluations/aide_auto_rubric_v0.json`: AIDE auto-note-derived skill
  rubric score.
- `results/evaluations/aide_auto_context_baselines_v0.json`: AIDE
  auto-note-derived skill-vs-summary-vs-abstract deterministic comparison.
- `results/evaluations/aide_auto_harness_transfer_v0.json`: AIDE
  auto-note-derived transfer-readiness ranking.
- `results/evaluations/aide_auto_source_span_validation_v0.json`: AIDE
  auto-note-derived source-span validation summary.
- `results/tables/auto_note_comparison.md`: curated-vs-auto Toolformer and AIDE
  note comparison table.
- `results/tables/`: paper-ready main results, transfer ablation, compactness/
  source-grounding, context cost proxy, and combined summary tables.
- `results/human_fidelity_packets/`: prepared review packets and blank
  annotation template plus pending annotation summary for human source-fidelity
  review.
- `results/failure_cases/`: failure-case archive with 27 cases, including 21
  paper-reported limitations/failure branches and 6 project-level failure/fix
  records.
- `results/reproducibility/`: reproducibility package report. Current status is
  ready with pending external evidence, 105 ready checks, 5 pending checks, and
  0 failed checks.
- `research/review_report.md` and `research/rebuttal_bank.md`: internal
  review/rebuttal readiness artifacts that map likely reviewer objections to
  evidence and prohibited overclaims.
- `paper/outline.md`: section plan, contribution bullets, evidence boundary,
  and figure/table plan.
- `paper/draft.md`: first evidence-bounded paper draft.
- `paper/claim_checklist.md`: supported-vs-unsupported claim gate for drafting.
- `paper/limitations.md`: limitations and future-work text aligned to current
  deterministic/offline evidence.
- `paper/aaai/`: official AAAI-27 author kit, template provenance, and
  AAAI-formatted PaperToSkill LaTeX draft.
- `examples/usage/`: usage examples for Codex-style skill loading,
  extracted-text auto-note-to-skill conversion, and model-ablation execution.
- `benchmarks/model_ablation_v0.json`: Claude/GPT-family/DeepSeek model
  ablation prompt spec with response slots marked pending.
- `scripts/build_model_ablation_prompts.py`: prompt-grid builder for model
  ablations.
- `results/model_ablation_prompts/v0/`: generated model-ablation prompts for
  Claude Opus 4.8, GPT-family, and DeepSeek follow-up slots over Toolformer and
  AIDE auto-skill usage examples.

## Current Assumptions

- "Skill" means a natural-language operational guide for an agent, similar to
  Codex skills with a `SKILL.md` entry point and optional bundled resources.
- The paper should emphasize practical conversion, not only successful final
  outputs.
- Failure traces are valuable and should be recorded rather than hidden.
- Transfer evaluation should include moving skills between harnesses, especially
  Codex-to-Claude or another agent runtime.
- Paper writing must distinguish curated note-to-skill conversion from full
  arbitrary-PDF automation, and offline readiness from live agent success.
- Automatic note-scaffold writing must distinguish deterministic extracted-text
  line-window scaffolding from reliable arbitrary-PDF-to-skill automation.
- Cost writing must distinguish deterministic token/cost proxy from provider
  billing, tokenizer-exact accounting, and success-per-dollar evidence.
- Human-fidelity writing must distinguish prepared review packets from completed
  independent annotation.
- Reproducibility writing must distinguish local package readiness from
  completed external live responses or independent human validation.
- Rebuttal writing must answer objections from current evidence and explicitly
  avoid unsupported live, human-validation, and provider-billing claims.
- AAAI paper writing should use the `paper/aaai/` LaTeX package. The current
  official template is AAAI-27 because the author-kit endpoint available on
  2026-06-18 provides `aaai2027.sty`.
- Model-ablation writing must distinguish prompt packets from completed
  Claude/GPT/DeepSeek responses. GPT 5.5 is a requested GPT-family slot and
  must be verified at run time before claimed as available.

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
