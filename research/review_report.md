# PaperToSkill Review Report

Date: 2026-06-20

Evidence boundary: this is an internal adversarial review of the current
PaperToSkill draft and artifact package. It updates the review handoff to match
Phase 59 evidence, but it does not add new successful empirical results or
claim final submission readiness.

## Overall Assessment

PaperToSkill now has a coherent deterministic/offline system-paper package:
curated note-to-skill conversion over four real papers, deterministic
extracted-text-to-note scaffolds for Toolformer and AIDE, source maps,
source-span validation, compactness and local token-proxy accounting, usage
examples, saved model-ablation responses for Claude Opus 4.8 and GPT-family
slots, all four live-transfer saved-response sets, human-fidelity annotation
handoff, provider-billing evidence handoff, a local external-evidence closure
queue, external-evidence execution packets, an AAAI submission-decision
preflight, and an AAAI-27 LaTeX package.

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
| R7 | Cost/economic claims can be overread. | Medium | Context and response costs are local token proxies. `results/provider_billing_evidence/billing_summary.md` reports 0 measured rows and 6 pending rows. | Call these local input/output token proxies and billing handoff readiness; avoid provider bills, invoices, or success-per-dollar claims. |
| R8 | AI-Scientist-v2 integration may look complete when it is only smoke-attempted. | Medium | Bounded LLM-client smoke remains `blocked_by_provider_or_model_availability`; the latest Phase 58 retry capped the smoke request at 128 max tokens and tried `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6`; all four aliases timed out after 30 seconds waiting for provider response. Phase 59 direct endpoint probes bypassed `ai_scientist.llm` and returned HTTP 503 `No available accounts` for Claude-family aliases plus HTTP 502 `Upstream access forbidden` for GPT-family aliases. | Treat this as provider/model availability evidence only; full AI-Scientist-v2 live/BFTS run remains pending. |

## Claim Tightening Recommendations

| Location | Current Pressure | Safer Wording |
| --- | --- | --- |
| Abstract | "paper-to-skill conversion" may imply end-to-end PDF automation. | "workflow that turns source-anchored paper notes into compact, human-editable agent skills" |
| Introduction | "ordinary users can reuse research" can sound broad. | "ordinary users can inspect, edit, and reuse a paper-derived workflow artifact under explicit evidence boundaries" |
| Results | "live transfer" can sound like task success. | "saved live-transfer response files scored with a deterministic output-contract evaluator; not human semantic or live task success evidence" |
| Cost | "economic signal" can sound like real savings. | "local tokenizer-aware input/output token proxies; provider billing remains pending" |
| Failure archive | "first-class evidence" can sound causal. | "first-class provenance artifact for limitations and negative branches" |

## Submission Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Claim-evidence consistency | Pass with caveats | `paper/claim_checklist.md`; `research/claim_evidence_matrix.md`; `results/reproducibility/paper_claim_report.md` |
| Local reproducibility package | Pass locally, external evidence pending | `results/reproducibility/package_report.md`: 281 ready, 8 pending, 0 failed |
| Active-goal completion | Not complete | `results/reproducibility/goal_completion_report.md`: 70 ready, 8 pending, 0 failed |
| External evidence closure queue | Ready as local queue | `results/external_evidence_closure/closure.md`: 3 ready, 0 pending, 0 failed |
| External evidence execution packets | Ready as local handoff | `results/external_evidence_packets/packets.md`: 7 ready, 0 pending, 0 failed |
| AAAI submission decision preflight | Pending human decision | `results/aaai_submission_decision/decision.md`: 25 ready, 1 pending, 0 failed |
| AAAI local package | Pass locally, not submission-final | `results/reproducibility/aaai_package_report.md` |
| Live-transfer saved responses | Complete for saved-response scoring | `results/live_transfer_prompts/evaluation.md`: 24 scored, 0 pending |
| Real live task success | Pending | Saved-response scoring is not human semantic or real task-success evidence |
| Model ablation | Partial | `results/model_ablation_prompts/v0/evaluation.md`: 4 scored rows, 2 pending DeepSeek rows; `results/deepseek_followup_handoff/handoff.md`: `pending_user_configuration` |
| AI-Scientist-v2 LLM-client smoke | Attempted, provider-blocked | `results/ai_scientist_v2_smoke/run_report.md`: `blocked_by_provider_or_model_availability`; latest smoke aliases are `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6`; all four timed out after 30 seconds waiting for provider response with `--max-tokens 128`. Direct endpoint probes report HTTP 503 `No available accounts` for Claude-family aliases and HTTP 502 `Upstream access forbidden` for GPT-family aliases. |
| Human fidelity | Handoff ready, annotation pending | `results/human_fidelity_packets/annotation_summary.md`: 0 scored, 24 pending |
| Provider billing | Handoff ready, billing pending | `results/provider_billing_evidence/billing_summary.md`: 0 measured, 6 pending |

## Recommended Next Experiments

1. Fill and summarize the 24-row human-fidelity annotation template with
   independent reviewer scores.
2. Run the DeepSeek follow-up rows after the user supplies a concrete alias and
   credential profile; use `scripts/check_deepseek_followup.py --strict`
   before and after editing the slot.
3. Retry the bounded AI-Scientist-v2 LLM-client smoke only after the provider
   can serve chat completions for either the Claude-family or GPT-family
   credential profile; keep any full BFTS/live run separate.
4. Fill provider usage or invoice rows before making billing or
   success-per-dollar claims.
5. Decide whether the first AAAI submission should remain explicitly
   deterministic/offline or wait for the pending human/model/billing/live-run
   evidence.

## Decision

Do not mark the project or paper submission as complete. The current package is
ready for internal review and reviewer-question preparation, and the AAAI
submission-decision preflight makes both options auditable, but it is not a
submission-final AAAI paper and it does not establish human validation, real
live task success, DeepSeek completion, AI-Scientist-v2 live-run completion, or
real provider economics.
