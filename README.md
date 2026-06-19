# PaperToSkill

PaperToSkill is a research-to-skill system idea: given a paper, extract the
paper's transferable method, workflow, assumptions, evaluation pattern, and
failure cases into a concise Codex/agent skill that ordinary users can inspect,
edit, and reuse.

This repository is the local working memory and artifact hub for developing the
idea with `ai-scientist-v2`.

## Current Phase

Phase 47: Claude Opus 4.8 and GPT-family ablation rows are saved and scored for
the current two-case protocol, saved model responses have a local output-token
proxy report, and all four live-transfer saved-response sets are collected and
scored for the current prompt-packet protocol. A bounded AI-Scientist-v2
LLM-client smoke runner is present, and the latest recheck tried
`claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
`claude-opus-4-6`; all four attempts reached the provider path but timed out
after 15 seconds waiting for provider response, not because of a local package
failure or model-quality result. The smoke runner now prints an explicit
`overall_status` summary, has a script-level `--timeout-seconds`, offers
repeatable `--model-alias`, and provides `--require-complete` for checks that
should fail unless a response satisfying the smoke contract is saved. The
human-fidelity review handoff now includes an annotation guide, stricter blank
template metadata, and summary validation, while completed human annotation
remains pending. Provider-billing evidence collection now has a blank
invoice/usage template and strict summary validation, while realized bills and
success-per-dollar evidence remain pending. The submission-review handoff now
includes updated adversarial review, rebuttal, and checklist files plus a
checker that prevents stale review claims from drifting behind current evidence.
The AAAI-27 paper package, usage examples, deterministic/offline experiments,
model-ablation runner, DeepSeek follow-up path, local DeepSeek
handoff/preflight report, local `o200k_base` input/output token proxies,
one-command extracted-text-to-skill pipeline, local
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
- `research/submission_checklist.md`
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
- DeepSeek follow-up handoff:
  `results/deepseek_followup_handoff/handoff.md`.
- AI-Scientist-v2 LLM-client smoke report:
  `results/ai_scientist_v2_smoke/run_report.md`.
- Provider-billing evidence handoff:
  `results/provider_billing_evidence/billing_summary.md`.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md`.
