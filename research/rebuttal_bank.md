# PaperToSkill Rebuttal Bank

Date: 2026-06-20

Use this file to answer likely reviewer objections without exceeding the current
evidence boundary. This is a reviewer-response handoff, not new evidence.

## Q1: Is PaperToSkill just another summarizer?

Short answer: No, but current evidence is deterministic/offline rather than a
completed user outcome study.

Evidence to cite:

- `results/tables/main_results.md`: generated skills outperform
  generic-summary and abstract-only baselines on deterministic operational
  coverage across AI Scientist-v2, Reflexion, AIDE, and Toolformer.
- `generated_skills/*/SKILL.md`: generated artifacts include workflow,
  validation, failure cases, transfer notes, and source anchors.
- `results/tables/transfer_ablation.md`: removing `Transfer Notes` lowers
  offline readiness from 10/10 to 7.6/10 across all four cases.

Do not say:

- "Skills improve live agent success over summaries."
- "The generated skills are semantically complete."

## Q2: How do you prevent hallucinated instructions?

Short answer: PaperToSkill uses source maps and source-span validation as local
guards, while independent human semantic validation remains pending.

Evidence to cite:

- `generated_skills/*/references/source_map.json`
- `results/tables/compactness_source_grounding.md`
- Source-span support rates: 0.938, 1.0, 1.0, and 1.0 with zero invalid ranges.
- `results/human_fidelity_packets/annotation_summary.md`: 0 scored rows,
  24 pending rows, and 0 errors.

Do not say:

- "All instructions are human-verified."
- "Source-span support proves factual correctness."

## Q3: Why are the inputs curated notes instead of raw PDFs?

Short answer: This paper isolates the paper-note-to-skill conversion layer
before claiming full PDF automation. The Toolformer and AIDE extracted-text
scaffolds are bounded deterministic scaffolds, not a robust arbitrary-PDF
solution.

Evidence to cite:

- `papers/notes/` contains curated source-anchored notes used as benchmark
  input.
- `scripts/papertoskill_note_from_text.py` and
  `results/tables/auto_note_comparison.md` show Toolformer and AIDE
  extracted-text scaffold results.
- `paper/limitations.md` states the curated-note and PDF automation boundary.

Do not say:

- "PaperToSkill fully automatically converts arbitrary PDFs."
- "The Toolformer and AIDE auto-note results prove reliable PDF automation."

## Q4: Are the metrics too heuristic?

Short answer: They are intentionally deterministic gates, not substitutes for
human semantic review or real live-task success.

Evidence to cite:

- `paper/limitations.md`: heuristic metric limitation.
- `results/reproducibility/package_report.md`: 259 ready checks, 8 pending
  checks, and 0 failed checks.
- `results/human_fidelity_packets/`: prepared independent-review protocol.

Do not say:

- "The metrics replace human review."
- "The deterministic score proves real-world usability."

## Q5: Does transfer readiness prove Codex-to-Claude transfer?

Short answer: It proves the presence of transfer-oriented structure and that
saved response files satisfy deterministic output contracts. It does not prove
human semantic fidelity or real task success.

Evidence to cite:

- `results/tables/transfer_ablation.md`: offline transfer-readiness ablation.
- `results/live_transfer_prompts/evaluation.md`: 24 saved live-transfer
  response rows, 24 scored rows, 0 pending rows, average normalized score 1.0.
- `results/live_transfer_prompts/*_v0/run_report.md`: saved response run
  reports.

Do not say:

- "Codex-to-Claude transfer succeeded as a real task outcome."
- "Transfer notes improve live success rate."

## Q6: What is the economic claim?

Short answer: Generated skills compress full extracted paper context under a
local tokenizer-aware input-token proxy, and saved model responses have a local
output-token proxy. Provider bills and success-per-dollar remain pending.

Evidence to cite:

- `results/tables/context_cost_proxy_tokenizer.md`
- `results/tables/model_response_cost_proxy.md`
- AI Scientist-v2 generated skill: 1,079 `o200k_base` tokens vs 45,212 for full
  extracted paper.
- Reflexion generated skill: 703 vs 16,414.
- AIDE generated skill: 1,285 vs 13,312.
- Toolformer generated skill: 1,255 vs 20,365.
- `results/provider_billing_evidence/billing_summary.md`: 0 measured rows,
  6 pending rows, success per dollar `n/a`.

Do not say:

- "PaperToSkill guarantees lower provider bills."
- "The system improves success per dollar."

## Q7: Why archive failures?

Short answer: The archive preserves limitations and project-level failure/fix
records as provenance so the paper does not become a success-only narrative.

Evidence to cite:

- `results/failure_cases/failure_case_archive.md`: 27 cases, 21 paper-reported
  and 6 project-level.
- `paper/limitations.md`: failure archive is not an outcome study.

Do not say:

- "Failure recording has been shown to improve final user outcomes."

## Q8: What is complete in the model ablation?

Short answer: Claude Opus 4.8 and GPT-family rows are saved and scored for the
current two-case protocol; DeepSeek remains pending.

Evidence to cite:

- `results/model_ablation_prompts/v0/evaluation.md`: 6 total rows, 4 scored
  rows, 2 pending DeepSeek rows, average normalized score 1.0 over scored rows.
- `results/model_ablation_prompts/v0/run_report.md`: Claude Opus 4.8 saved
  response evidence.
- `results/model_ablation_prompts/v0/gpt_retry_run_report.md`: GPT-family retry
  evidence.
- `results/deepseek_followup_handoff/handoff.md`: local DeepSeek follow-up
  handoff is `pending_user_configuration` with 5 ready, 2 pending, and 0 failed
  checks.

Do not say:

- "All model ablations are complete."
- "DeepSeek has completed."

## Q9: What happened with AI-Scientist-v2 integration?

Short answer: The local dry run succeeded, and a bounded LLM-client smoke was
attempted through the local AI-Scientist-v2 client. The latest smoke report is
`blocked_by_provider_or_model_availability`: `claude-opus-4-8`,
`claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6` were all tried,
and all four aliases timed out after 30 seconds waiting for provider response.
Smoke completion and full live-run evidence remain pending.

Evidence to cite:

- `results/ai_scientist_v2_smoke/run_report.md`
- `memory/short_term_memory.md`
- AI-Scientist-v2 dry-run experiment path recorded in memory.

Do not say:

- "AI-Scientist-v2 live run completed."
- "BFTS succeeded."

## Q10: What must be done before a stronger submission?

Short answer: Resolve the remaining external evidence decisions or submit
explicitly as a deterministic/offline system paper with those limitations
prominent.

Evidence to cite:

- `results/reproducibility/goal_completion_report.md`: 67 ready checks,
  8 pending checks, 0 failed checks.
- `results/reproducibility/package_report.md`: 259 ready checks, 8 pending
  checks, 0 failed checks.
- `results/external_evidence_closure/closure.md`: six local closure items for
  the remaining external evidence.
- `results/external_evidence_packets/packets.md`: six local execution packets
  for the remaining external evidence.
- `research/submission_checklist.md`: submission-review handoff checklist.

Do not say:

- "The package is final."
- "All validation is complete."
