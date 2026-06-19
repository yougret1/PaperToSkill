# PaperToSkill

PaperToSkill is a research-to-skill system idea: given a paper, extract the
paper's transferable method, workflow, assumptions, evaluation pattern, and
failure cases into a concise Codex/agent skill that ordinary users can inspect,
edit, and reuse.

This repository is the local working memory and artifact hub for developing the
idea with `ai-scientist-v2`.

## Current Phase

Phase 42: Claude Opus 4.8 and GPT-family ablation rows are saved and scored for
the current two-case protocol, saved model responses have a local output-token
proxy report, and all four live-transfer saved-response sets are collected and
scored for the current prompt-packet protocol. A bounded AI-Scientist-v2
LLM-client smoke runner is now present, and the latest attempt is recorded as
provider-blocked by HTTP 403 `All available accounts exhausted`, not as a model
quality failure. The human-fidelity review handoff now includes an annotation
guide, stricter blank template metadata, and summary validation, while completed
human annotation remains pending.
The AAAI-27 paper package, usage examples, deterministic/offline experiments,
model-ablation runner, DeepSeek follow-up path, local `o200k_base` input/output
token proxies, one-command extracted-text-to-skill pipeline, local
`pdftotext -layout` PDF smoke input path, result tables, and
machine-checkable package/goal gates are prepared. The active goal is not yet
complete because completed AI-Scientist-v2 LLM-client/full live-run evidence,
DeepSeek responses, human-fidelity annotation, provider-specific billing or
success-per-dollar evidence, and final submission decisions remain pending.

## Memory

- Long-term memory: `memory/long_term_memory.md`
- Short-term memory: `memory/short_term_memory.md`

After any context compaction or session resume, read both memory files before
continuing work.

## Research Artifacts

- `research/research_contract.md`
- `research/artifact_map.md`
- `research/decision_log.md`
- `research/literature_matrix.md`
- `research/related_work_gap_map.md`
- `research/claim_source_map.md`
- `research/idea_cards.md`
- `research/claim_evidence_matrix.md`
- `research/experiment_design.md`
- `research/experiment_queue.md`
- `research/review_report.md`
- `research/rebuttal_bank.md`
- `research/runbook.md`
- `research/goal_completion_audit.md`
- `research/stage_log.md`
- `research/run_logs/`

## Paper Draft Package

- `paper/outline.md`
- `paper/draft.md`
- `paper/claim_checklist.md`
- `paper/limitations.md`
- `paper/aaai/papertoskill_aaai2027.tex`
- `paper/aaai/papertoskill_tables.tex`

These files intentionally separate supported deterministic/offline claims from
pending live-agent claims.

## AI-Scientist-v2 Inputs

- `ai_scientist_inputs/papertoskill.md`
- `ai_scientist_inputs/papertoskill_seed_ideas.json`

## Skill Prototype

- `skill/SKILL.md`

## Phase 1 Scaffold

- Benchmark manifest: `benchmarks/paper_manifest.json`
- Extractor script: `scripts/papertoskill_extract.py`
- One-command local pipeline: `scripts/papertoskill_pipeline.py`
- Smoke tests: `tests/test_papertoskill_extract.py`
- Retained generated case: `generated_skills/papertoskill_paper_note/SKILL.md`

## Current Benchmark Snapshot

- Real-paper cases: AI Scientist-v2, Reflexion, AIDE, and Toolformer.
- Main result tables: `results/tables/`.
- Generated skills: `generated_skills/ai_scientist_v2/`,
  `generated_skills/reflexion/`, `generated_skills/aide/`, and
  `generated_skills/toolformer/`.
- Live transfer prompt packets, run reports, saved responses, and scoring:
  `results/live_transfer_prompts/`.
- Human-fidelity review packets and pending annotation summary:
  `results/human_fidelity_packets/`.
- Failure-case archive: `results/failure_cases/`.
- Reproducibility package report: `results/reproducibility/`.
- AAAI package report: `results/reproducibility/aaai_package_report.md`.
- Usage-example report: `results/reproducibility/usage_example_report.md`.
- Auto-note comparison: `results/tables/auto_note_comparison.md`.
- Usage examples: `examples/usage/`.
- Model-ablation prompt packets: `results/model_ablation_prompts/v0/`.
- Model-ablation run/evaluation reports:
  `results/model_ablation_prompts/v0/run_report.md` and
  `results/model_ablation_prompts/v0/evaluation.md`.
- Model-response output-token proxy:
  `results/tables/model_response_cost_proxy.md`.
- AI-Scientist-v2 LLM-client smoke report:
  `results/ai_scientist_v2_smoke/run_report.md`.
