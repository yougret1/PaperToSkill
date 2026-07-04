# PaperToSkill

PaperToSkill is a research-to-skill system idea: given a paper, extract the
paper's transferable method, workflow, assumptions, evaluation pattern, and
failure cases into a concise Codex/agent skill that ordinary users can inspect,
edit, and reuse.

This repository is the local working memory and artifact hub for developing the
idea with `ai-scientist-v2`.

## Current Phase

Current status as of 2026-07-04: the strongest next evidence target is the
core real-reuse experiment, not a real-user study and not a submission-advice
loop. The first GPT-family Summary-vs-PaperToSkill pass now covers all eight
locked paper-task rows across AIDE, SWE-agent, Reflexion, and SnapATAC2, but
the result is mixed and failure-heavy rather than proof of aggregate
downstream effectiveness. The next priority is to stabilize or rerun the core
real-reuse tasks under the selected source papers' objective metrics while
keeping provider latency, API timeouts, and retry counts out of the core method
score.

The package also contains supporting evidence: deterministic/offline gates,
source maps and source-span validation, usage examples, saved live-transfer
response scoring, saved Claude/GPT-family/DeepSeek model-ablation response
scoring, local token-accounting proxies, bounded Paper2Agent positioning, and a
bounded AI-Scientist-v2 smoke/full live run. These are supporting or bounded
evidence, not substitutes for real-reuse task outcomes.

The active goal is still not complete because human-fidelity annotation is
pending and final AAAI submission readiness remains gated by the recorded
`wait_for_external_evidence` policy. Provider billing and success-per-dollar
claims are outside the current claim set unless a future evidence policy
explicitly reopens them.

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
- OpenAI-compatible direct provider probe reports:
  `results/openai_compatible_direct_probe/`.
- Provider-billing evidence handoff:
  `results/provider_billing_evidence/billing_summary.md`.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md`.
- External-evidence closure queue:
  `results/external_evidence_closure/closure.md`.
- External-evidence execution packets:
  `results/external_evidence_packets/packets.md`.
- AAAI submission-decision preflight:
  `results/aaai_submission_decision/decision.md`.
