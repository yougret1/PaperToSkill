# PaperToSkill Rebuttal Bank

Date: 2026-07-01

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
- `results/reproducibility/package_report.md`: 301 ready checks, 5 pending
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
output-token proxy. This is local token accounting, not provider billing or
success-per-dollar evidence.

Evidence to cite:

- `results/tables/context_cost_proxy_tokenizer.md`
- `results/tables/model_response_cost_proxy.md`
- AI Scientist-v2 generated skill: 1,079 `o200k_base` tokens vs 45,212 for full
  extracted paper.
- Reflexion generated skill: 703 vs 16,414.
- AIDE generated skill: 1,285 vs 13,312.
- Toolformer generated skill: 1,255 vs 20,365.
- `results/token_accounting/token_accounting_summary.md`: composite local token
  proxy of 13,916 tokens over generated-skill input and saved-response output
  evidence.

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

Short answer: Claude Opus 4.8, GPT-family, and DeepSeek rows are saved and
scored for the current two-case protocol, but this is saved-response
output-contract evidence only.

Evidence to cite:

- `results/model_ablation_prompts/v0/evaluation.md`: 6 total rows, 6 scored
  rows, 0 pending rows, average normalized score 1.0.
- `results/model_ablation_prompts/v0/gpt_protocol_run_report.md`: GPT-family
  protocol refresh completed both rows with `gpt-5.5`.
- `results/model_ablation_prompts/v0/deepseek_run_report.md`: DeepSeek
  completed both rows with `deepseek-v4-flash`.
- `results/model_ablation_prompts/v0/claude_protocol_run_report.md`: latest
  Claude protocol refresh used Anthropic Messages but was blocked by provider
  HTTP 502; scored Claude rows come from earlier saved response files.

Do not say:

- "Saved-response model-ablation scoring proves live task success."
- "The provider failures are negative model-quality evidence."

## Q8.5: How does PaperToSkill compare with Paper2Agent?

Short answer: Paper2Agent is the closest competing artifact type, but the
current evidence is a bounded artifact/workflow comparison, not a runtime
baseline.

Evidence to cite:

- `results/tables/paper2agent_artifact_comparison.md`: 7/7 ready criteria and
  0 failed criteria.
- The comparison covers required inputs, generated artifact type, setup burden,
  validation checks, failure handling, source traceability, and runtime
  dependency.
- Paper2Agent produces MCP servers from papers plus codebases; PaperToSkill
  produces portable natural-language skills with source and failure boundaries.

Do not say:

- "PaperToSkill outperforms Paper2Agent."
- "PaperToSkill has run a Paper2Agent MCP baseline."

## Q9: What happened with AI-Scientist-v2 integration?

Short answer: The local dry run succeeded, the bounded LLM-client smoke is
complete, and one bounded full live run produced a completion directory. The
run is useful integration evidence for the PaperToSkill idea, but its positive
result is synthetic and should not be described as human fidelity, real-data
validation, or broad live research-task success. A separate HF/semantic-data
branch is retained as a failed branch because dataset loading was invalid and
`sentence_transformers` was missing.

Evidence to cite:

- `results/ai_scientist_v2_smoke/run_report.md`
- `results/ai_scientist_v2_live_run_handoff/handoff.md`
- `research/run_logs/2026-07-02_phase76_ai_scientist_v2_full_live_run.md`
- `memory/short_term_memory.md`
- AI-Scientist-v2 dry-run experiment path recorded in memory.

Do not say:

- "AI-Scientist-v2 proves real-data task success."
- "BFTS succeeded as a broad live research benchmark."

## Q10: What must be done before a stronger submission?

Short answer: Resolve the remaining external evidence decisions or submit
explicitly as a deterministic/offline system paper with those limitations
prominent.

Evidence to cite:

- `results/reproducibility/goal_completion_report.md`: current ready/pending
  counts after rerunning `scripts/check_goal_completion.py --strict`.
- `results/reproducibility/package_report.md`: current ready/pending counts
  after rerunning `scripts/check_reproducibility_package.py --strict`.
- `results/external_evidence_closure/closure.md`: local closure items for
  remaining external evidence.
- `results/external_evidence_packets/packets.md`: local execution packets for
  remaining external evidence.
- `results/aaai_submission_decision/decision.md`: the recorded option is
  `wait_for_external_evidence`.
- `research/submission_checklist.md`: submission-review handoff checklist.

Do not say:

- "The package is final."
- "All validation is complete."
