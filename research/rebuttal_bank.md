# PaperToSkill Rebuttal Bank

Date: 2026-07-06

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
guards, and the completed 24-cell human-fidelity annotation provides bounded
semantic-fidelity and reviewability evidence rather than broad human validation.

Evidence to cite:

- `generated_skills/*/references/source_map.json`
- `results/tables/compactness_source_grounding.md`
- Source-span support rates: 0.938, 1.0, 1.0, and 1.0 with zero invalid ranges.
- `results/human_fidelity_packets/annotation_summary.md`:
  annotation_status=complete, 24 scored paper-by-criterion cells, 0 pending
  cells, mean score 4.75/5, and average confidence 0.946.

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
- `results/reproducibility/package_report.md`: 484 ready checks, 0 pending
  checks, and 0 failed checks.
- `results/human_fidelity_packets/annotation_summary.md`: completed bounded
  24-cell annotation summary.

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
output-contract evidence only. The separate real-reuse LLM ablation is a
different auxiliary protocol: it uses locked real-reuse tasks, has 12/18 scored
rows, and keeps the six Claude-family rows provider-pending after HTTP 502
availability failures.

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
- `results/real_reuse/llm_ablation_summary.md`: 18 expected real-reuse
  auxiliary rows, 12 collected scored rows, and 6 Claude-family rows pending
  after provider HTTP 502 availability failures.
- `results/real_reuse/llm_ablation_family_summary.csv`: GPT-family `gpt-5.5`
  is 6/6 scored with Summary/PaperToSkill averages 0.605/0.333; DeepSeek-family
  `deepseek-v4-flash` is 6/6 scored with 0.500/0.500; Claude-family
  `claude-opus-4-8` is 0/6 scored and provider-pending.

Do not say:

- "Saved-response model-ablation scoring proves live task success."
- "The provider failures are negative model-quality evidence."
- "The real-reuse LLM ablation replaces the locked main rows."
- "The 12/18 auxiliary slice proves aggregate PaperToSkill advantage."

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

## Q8.6: Do the real-reuse results prove downstream effectiveness?

Short answer: No. The first eight-row GPT-family pass is a stress test with
mixed and failure-heavy outcomes. Its value is that it exposes concrete
boundary modes under original-style tasks, while the paper avoids an aggregate
effectiveness claim.

Evidence to cite:

- `results/real_reuse/main_results_plan.md`: all eight Summary-vs-PaperToSkill
  rows are scored for the first GPT-family pass.
- `results/real_reuse/failure_analysis.md`: row-level boundary modes include
  budget timeout, patch application, PaperToSkill-only success, solved-by-both
  ceiling, and artifact completion.
- `results/real_reuse/swe_t1_source_context_followup.md`: SWE-T1 phase107
  shared-source-context follow-up where both patches applied but both failed
  the hidden test, clarifying a task-contract / hidden-objective boundary.
- `results/real_reuse/swe_t1_issue_aligned_followup.md`: SWE-T1 phase110
  issue-aligned follow-up where both Summary and PaperToSkill score 1.000
  under the revised scorer, showing contract closure for both conditions but
  no PaperToSkill advantage.
- `results/real_reuse/snapatac2_artifact_followup.md`: SNAP artifact-execution
  diagnosis showing that current SNAP rows are plan/JSON outputs under a
  non-executing runner, while the scorer requires completed artifacts plus
  runtime/memory records.
- `results/real_reuse/snapatac2_executable_artifact_followup.md`: SNAP
  phase108 controlled executable-artifact follow-up where both Summary and
  PaperToSkill score 1.000 on SNAP-T1/T2, validating the artifact/runtime/memory
  contract path without replacing the main rows.
- `paper/aaai/papertoskill_tables.tex`: the AAAI draft includes both the main
  real-reuse table, the derived failure-boundary table, the SWE-T1 diagnostic
  follow-up tables, the SNAP executable-artifact diagnostic table, and the
  phase112 SNAP executable-candidate diagnostic table.

Do not say:

- "PaperToSkill is broadly effective on real downstream tasks."
- "PaperToSkill has aggregate advantage over Summary."
- "Failure-boundary analysis is a new positive task-success result."

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

Short answer: Resolve the one pending-external-evidence item or submit
explicitly as a deterministic/offline system paper with the remaining
limitations prominent. The local closure queue and execution packets are ready
handoffs, but `pending_external_evidence` remains the active status until the
AAAI final decision is closed. Human-fidelity annotation_status=complete with
24 scored rows and 0 pending rows.

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

## Q11: Why include a Full Excerpt table if it is not a main baseline?

Short answer: It is a small sanity check for reviewer questions about context
length, not a main effectiveness baseline.

Evidence to cite:

- `results/real_reuse/full_excerpt_sanity.md`: AIDE-T1, SWE-T1, and SNAP-T1
  rows with Summary, PaperToSkill, and matched Full Excerpt scores plus local
  whitespace token proxies. Full Excerpt scores are 0.000, 0.000, and 0.250.
- `paper/aaai/papertoskill_tables.tex`: `tab:full-excerpt-sanity` is labeled
  as auxiliary.

Do not say:

- "Full Excerpt has been beaten by PaperToSkill in general."
- "The three-row sanity subset is a main baseline."
- "The token columns are provider billing or output-token cost."
