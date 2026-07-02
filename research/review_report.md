# PaperToSkill Review Report

Date: 2026-07-02

Evidence boundary: this is an internal adversarial review of the current
PaperToSkill draft and artifact package. It updates the review handoff to match
current local evidence, but it does not claim final submission readiness,
human validation, provider billing, or broad live task success.

## Overall Assessment

PaperToSkill now has a coherent deterministic/offline system-paper package:
curated note-to-skill conversion over four real papers, deterministic
extracted-text-to-note scaffolds for Toolformer and AIDE, source maps,
source-span validation, compactness and local token-proxy accounting, usage
examples, saved model-ablation responses for Claude Opus 4.8, GPT-family, and
DeepSeek slots, all four live-transfer saved-response sets, human-fidelity annotation
handoff, local token-accounting evidence, a local external-evidence closure
queue, external-evidence execution packets, a bounded Paper2Agent
artifact/workflow comparison, a bounded AI-Scientist-v2 marker smoke/full live
run, a recorded AAAI submission decision, and an AAAI-27 LaTeX package.

The strongest current framing remains:

> PaperToSkill turns source-anchored paper notes into compact, human-editable
> agent skills and provides deterministic gates that check operational
> coverage, source grounding, transfer-readiness structure, failure provenance,
> and evidence-boundary discipline.

The paper should not be positioned as a completed live-agent study,
human-validated semantic-fidelity study, provider-billing study, or reliable
arbitrary-PDF-to-skill system. The 24 live-transfer rows are saved-response
output-contract evidence, not proof of live task success.

## Major Risks

| ID | Risk | Severity | Current Evidence | Required Response |
| --- | --- | --- | --- | --- |
| R1 | Reviewers may call PaperToSkill "just summarization." | High | Generated skills beat generic-summary and abstract-only baselines on deterministic operational coverage across AI Scientist-v2, Reflexion, AIDE, and Toolformer. Transfer notes, source maps, validation checks, and failure branches are first-class artifacts. | Emphasize executable workflow structure, source anchoring, failure provenance, and transfer-boundary discipline; avoid claiming real task success. |
| R2 | Reviewers may reject deterministic metrics as too heuristic. | High | Rubric, context coverage, source-span validation, and transfer readiness are reproducible but not human semantic scoring. | Present metrics as auditable gates; keep human-fidelity annotation as prepared but pending. |
| R3 | Curated notes weaken automation claims. | High | Main benchmark uses curated source-anchored notes; Toolformer and AIDE have deterministic extracted-text scaffolds. | Keep the main claim as paper-note-to-skill conversion; describe extracted-text scaffolds as bounded automation, not arbitrary-PDF reliability. |
| R4 | Four papers may be too narrow and procedural. | Medium | Benchmark covers agent research automation, verbal reinforcement, ML-engineering agents, and tool-use data generation. | Describe this as a focused first benchmark; propose theory-heavy/interface-heavy stress cases as future work. |
| R5 | Saved live-transfer responses can be overread as real live success. | High | `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24 scored rows, 0 pending rows, and average normalized score 1.0 under deterministic output-contract scoring. | Say "saved live-transfer response files were scored"; do not say the system proves live task success, human semantics, or cross-harness outcome gains. |
| R6 | Human fidelity is prepared but unscored. | High | `results/human_fidelity_packets/annotation_summary.md` reports 0 scored rows, 24 pending rows, and 0 errors. | Say "human-fidelity handoff ready"; do not say "human-validated" or "expert-validated." |
| R7 | Cost/economic claims can be overread. | Medium | Context and response costs are local token proxies. `results/token_accounting/token_accounting_summary.md` reports 4,322 generated-skill input tokens, 95,303 full-extracted input tokens, and 9,594 saved-response output tokens. | Call these local input/output token proxies; they are not provider billing, invoices, or success-per-dollar claims. |
| R8 | AI-Scientist-v2 integration may be overread as broad live task success. | Medium | Bounded LLM-client smoke is `complete`, and the full live-run handoff is `complete` with one completion directory. The run's positive result is synthetic; the HF/semantic-data branch remains a failed branch due invalid dataset loading/synthetic padding and missing `sentence_transformers`. | Treat this as bounded integration and synthetic sensitivity evidence only; do not claim human fidelity, real-data validation, or broad live research-task success. |
| R9 | Paper2Agent positioning may be overread as a baseline win. | Medium | `results/tables/paper2agent_artifact_comparison.md` reports 7/7 ready source-backed criteria for artifact/workflow comparison. It does not run Paper2Agent or deploy an MCP server. | Use this as positioning evidence only; do not claim runtime superiority or baseline performance. |

## Claim Tightening Recommendations

| Location | Current Pressure | Safer Wording |
| --- | --- | --- |
| Abstract | "paper-to-skill conversion" may imply end-to-end PDF automation. | "workflow that turns source-anchored paper notes into compact, human-editable agent skills" |
| Introduction | "ordinary users can reuse research" can sound broad. | "ordinary users can inspect, edit, and reuse a paper-derived workflow artifact under explicit evidence boundaries" |
| Results | "live transfer" can sound like task success. | "saved live-transfer response files scored with a deterministic output-contract evaluator; not human semantic or live task success evidence" |
| Cost | "economic signal" can sound like real savings. | "local tokenizer-aware input/output token proxies; not provider billing, invoices, or success-per-dollar evidence" |
| Failure archive | "first-class evidence" can sound causal. | "first-class provenance artifact for limitations and negative branches" |

## Submission Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Claim-evidence consistency | Pass with caveats | `paper/claim_checklist.md`; `research/claim_evidence_matrix.md`; `results/reproducibility/paper_claim_report.md` |
| Local reproducibility package | Pass locally, external evidence pending | `results/reproducibility/package_report.md`: 305 ready, 1 pending, 0 failed |
| Active-goal completion | Not complete | `results/reproducibility/goal_completion_report.md`: 77 ready, 3 pending, 0 failed |
| External evidence closure queue | Ready as local queue | `results/external_evidence_closure/closure.md`: 3 ready, 0 pending, 0 failed |
| External evidence execution packets | Ready as local handoff | `results/external_evidence_packets/packets.md`: 7 ready, 0 pending, 0 failed |
| AAAI submission decision | Recorded wait decision | `results/aaai_submission_decision/decision.md`: `selected_option=wait_for_external_evidence`, 27 ready, 0 pending, 0 failed |
| AAAI local package | Pass locally, not submission-final | `results/reproducibility/aaai_package_report.md` |
| Live-transfer saved responses | Complete for saved-response scoring | `results/live_transfer_prompts/evaluation.md`: 24 scored, 0 pending |
| Real live task success | Pending | Saved-response scoring is not human semantic or real task-success evidence |
| Model ablation | Complete for saved-response scoring | `results/model_ablation_prompts/v0/evaluation.md`: 6 scored rows, 0 pending; `results/deepseek_followup_handoff/handoff.md`: `responses_present` |
| Paper2Agent artifact comparison | Complete for bounded positioning evidence | `results/tables/paper2agent_artifact_comparison.md`: 7 ready criteria, 0 failed |
| AI-Scientist-v2 LLM-client smoke | Complete for bounded marker contract | `results/ai_scientist_v2_smoke/run_report.md`: `complete`; marker response saved. |
| AI-Scientist-v2 full live run | Complete for bounded synthetic integration evidence | `results/ai_scientist_v2_live_run_handoff/handoff.md`: `complete`; one completion directory. |
| Human fidelity | Handoff ready, annotation pending | `results/human_fidelity_packets/annotation_summary.md`: 0 scored, 24 pending |
| Local token accounting | Complete as current cost evidence | `results/token_accounting/token_accounting_summary.md`: complete local input/output token accounting |

## Recommended Next Experiments

1. Fill and summarize the 24-row human-fidelity annotation template with
   independent reviewer scores.
2. Extend the bounded Paper2Agent comparison into a real executable MCP
   baseline only if the codebase/environment resources are available. Keep the
   current artifact/workflow table as source-backed positioning evidence.
3. Use the Phase 76 AI-Scientist-v2 run as bounded integration evidence only;
   keep the failed HF/semantic-data branch as a negative result, not a main
   benchmark result.
4. Keep provider billing, invoices, and success-per-dollar outside the current
   claim set unless a separate future evidence policy explicitly reopens them.
5. Follow the recorded AAAI decision: wait for the named human-fidelity and
   final-submission evidence before stronger claims.

## Decision

Do not mark the project or paper submission as complete. The current package is
ready for internal review and reviewer-question preparation, and the AAAI
submission-decision record selects `wait_for_external_evidence`, but it is not
a submission-final AAAI paper and it does not establish human validation, real
live task success, real-data AI-Scientist-v2 validation, or real provider
economics.
