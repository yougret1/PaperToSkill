# AAAI Submission Decision Preflight

Evidence boundary: this report distinguishes submission choices, but it does not submit the paper, accept a claim scope, or complete pending external evidence.

- Overall status: pending_human_decision
- Decision status: pending_user_decision
- Selected option: n/a
- Ready checks: 26
- Pending checks: 1
- Failed checks: 0

## Options

### submit_now_deterministic_offline

- Status: available_for_human_decision
- Decision owner: Research Lead
- When defensible: Use only if the human lead accepts a bounded deterministic/offline system paper whose claims are scoped to local gates, saved-response scoring, and handoff readiness.

Required claim scope:

- Paper-note-to-skill conversion over curated and bounded extracted-text cases.
- Deterministic local gates for coverage, source grounding, transfer readiness, and table/claim consistency.
- Explicit limitations for human fidelity, provider billing, DeepSeek, and AI-Scientist-v2 live-run evidence.

Must not claim:

- AAAI acceptance or submission-final status.
- Human-validated semantic fidelity.
- Completed provider billing or success per dollar.
- DeepSeek model-ablation completion.
- Completed AI-Scientist-v2 LLM-client smoke or full live/BFTS run.

Validation commands:

```powershell
python scripts\check_aaai_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_submission_review.py --strict
python scripts\check_aaai_submission_decision.py --strict
python scripts\generate_aaai_submission_decision.py --selected-option submit_now_deterministic_offline --decision-owner "<name or role>" --decision-date YYYY-MM-DD --claim-boundary "<accepted bounded claim scope>" --evidence-policy "submit with explicit pending-evidence limitations"
```

### wait_for_external_evidence

- Status: available_for_human_decision
- Decision owner: Research Lead
- When defensible: Use if the intended paper claims require semantic fidelity, live AI-Scientist-v2 execution, DeepSeek comparison, or realized provider economics.

Required claim scope:

- Complete AI-Scientist-v2 smoke before any full live/BFTS run claim.
- Collect and score DeepSeek follow-up rows.
- Complete independent human-fidelity annotations.
- Fill provider billing rows before success-per-dollar claims.

Must not claim:

- That the local preflight itself completes any external evidence.
- That saved-response output-contract scoring proves live task success.

Validation commands:

```powershell
python scripts\check_external_evidence_packets.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\generate_aaai_submission_decision.py --selected-option wait_for_external_evidence --decision-owner "<name or role>" --decision-date YYYY-MM-DD --claim-boundary "<claims deferred until named evidence is complete>" --evidence-policy "wait for named external evidence rows"
```

## Decision Record Template

Create `research/aaai_submission_decision.md` only after the human lead makes the decision:

Recommended helper:

```powershell
python scripts\generate_aaai_submission_decision.py --selected-option submit_now_deterministic_offline --decision-owner "<name or role>" --decision-date YYYY-MM-DD --claim-boundary "<accepted paper claim scope>" --evidence-policy "<submit now with limitations, or wait for named evidence>"
```

Manual schema:

```markdown
# AAAI Submission Decision

Selected option: submit_now_deterministic_offline
Decision owner: <name or role>
Decision date: YYYY-MM-DD
Claim boundary: <accepted paper claim scope>
Evidence policy: <submit now with limitations, or wait for named evidence>
```

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| aaai_submission_decision_input_aaai_package | ready | present | results/reproducibility/aaai_package_report.json |
| aaai_submission_decision_input_paper_claims | ready | present | results/reproducibility/paper_claim_report.json |
| aaai_submission_decision_input_paper_tables | ready | present | results/reproducibility/paper_table_report.json |
| aaai_submission_decision_input_usage_examples | ready | present | results/reproducibility/usage_example_report.json |
| aaai_submission_decision_input_submission_review | ready | present | results/reproducibility/submission_review_report.json |
| aaai_submission_decision_input_goal_completion | ready | present | results/reproducibility/goal_completion_report.json |
| aaai_submission_decision_input_reproducibility_package | ready | present | results/reproducibility/package_report.json |
| aaai_submission_decision_input_external_packets | ready | present | results/external_evidence_packets/packets.json |
| aaai_submission_decision_input_ai_scientist_smoke | ready | present | results/ai_scientist_v2_smoke/run_report.json |
| aaai_submission_decision_input_ai_scientist_live_handoff | ready | present | results/ai_scientist_v2_live_run_handoff/handoff.json |
| aaai_submission_decision_input_deepseek_handoff | ready | present | results/deepseek_followup_handoff/handoff.json |
| aaai_submission_decision_input_model_ablation_evaluation | ready | present | results/model_ablation_prompts/v0/evaluation.json |
| aaai_submission_decision_input_human_fidelity | ready | present | results/human_fidelity_packets/annotation_summary.json |
| aaai_submission_decision_input_provider_billing | ready | present | results/provider_billing_evidence/billing_summary.json |
| aaai_submission_decision_input_decision_generator | ready | present | scripts/generate_aaai_submission_decision.py |
| aaai_submission_decision_input_submission_checklist | ready | present | research/submission_checklist.md |
| aaai_submission_decision_input_review_report | ready | present | research/review_report.md |
| aaai_submission_decision_input_rebuttal_bank | ready | present | research/rebuttal_bank.md |
| aaai_submission_decision_input_aaai_tex | ready | present | paper/aaai/papertoskill_aaai2027.tex |
| aaai_submission_decision_local_gates_ready | ready | local submission gates ready | results/reproducibility/aaai_package_report.json; results/reproducibility/paper_claim_report.json; results/reproducibility/paper_table_report.json; results/reproducibility/submission_review_report.json; results/reproducibility/usage_example_report.json |
| aaai_submission_decision_pending_evidence_state_current | ready | goal=not_complete_pending_external_evidence; package=ready_with_pending_external_evidence; pending=7 | results/reproducibility/goal_completion_report.json; results/reproducibility/package_report.json |
| aaai_submission_decision_external_packet_ready | ready | packet_status=pending_decision; criteria=3 | results/external_evidence_packets/packets.json |
| aaai_submission_decision_boundaries_declared | ready | submission options and non-negotiable boundaries declared | research/submission_checklist.md; research/review_report.md; paper/aaai/papertoskill_aaai2027.tex |
| aaai_submission_decision_options_declared | ready | options=submit_now_deterministic_offline,wait_for_external_evidence | results/aaai_submission_decision/decision.json |
| aaai_submission_decision_no_default_selection | ready | no option selected by the preflight | research/aaai_submission_decision.md |
| aaai_submission_decision_human_decision_recorded | pending | no human decision record present | research/aaai_submission_decision.md |
| aaai_submission_decision_no_secret_material | ready | no raw API-key-like strings found | results/aaai_submission_decision/decision.json |
