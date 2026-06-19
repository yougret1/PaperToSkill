# External Evidence Closure Queue

Evidence boundary: this is a local closure queue. It does not collect DeepSeek responses, human annotations, provider bills, AI-Scientist-v2 live-run artifacts, or final submission approval.

- Overall status: pending_external_evidence
- Queue item statuses: {'pending_provider': 1, 'blocked_by_smoke': 1, 'pending_user_configuration': 1, 'pending_reviewers': 1, 'pending_billing_rows': 1, 'pending_decision': 1}
- Ready checks: 3
- Pending checks: 0
- Failed checks: 0

## Queue Items

| Item | Status | Goal Requirements | Detail | Next Action |
| --- | --- | --- | --- | --- |
| ai_scientist_v2_smoke_completion | pending_provider | ai_scientist_v2_live_llm_smoke_complete | overall=blocked_by_provider_or_model_availability; counts={'ready': 3, 'pending': 2, 'fail': 0}; attempted=gpt-5.5,gpt-5.4 | Provider must return a smoke response satisfying all marker checks. |
| ai_scientist_v2_full_live_run | blocked_by_smoke | ai_scientist_v2_live_llm_run_complete | handoff=blocked_by_provider_smoke; completion_dirs=0 | Run the bounded full AI-Scientist-v2 task only after the smoke report is complete. |
| deepseek_followup_responses | pending_user_configuration | deepseek_followup_response_complete,model_ablation_evaluation_complete | handoff=pending_user_configuration; scored_rows=4; pending_rows=2 | User supplies DeepSeek alias/env vars, then run and score the two DeepSeek response rows. |
| human_fidelity_annotation | pending_reviewers | human_fidelity_annotation_complete | status=pending; scored_rows=0; pending_rows=24 | Independent reviewers fill the annotation template, then rerun the strict summarizer. |
| provider_billing_success_per_dollar | pending_billing_rows | provider_billing_evidence_complete | status=pending; measured_rows=0; pending_rows=6; errors=0 | Fill usage-export or invoice rows, then rerun the strict billing summary. |
| aaai_submission_decision | pending_decision | aaai_final_submission_ready | aaai_package=ready; submission_review=ready | Choose whether to submit as a deterministic/offline system paper or wait for the external evidence rows. |

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| external_closure_required_reports_present | ready | present | results/reproducibility/goal_completion_report.json; results/ai_scientist_v2_smoke/run_report.json; results/ai_scientist_v2_live_run_handoff/handoff.json; results/deepseek_followup_handoff/handoff.json; results/model_ablation_prompts/v0/evaluation.json; results/human_fidelity_packets/annotation_summary.json; results/provider_billing_evidence/billing_summary.json; results/reproducibility/aaai_package_report.json; results/reproducibility/submission_review_report.json |
| external_closure_goal_pending_items_covered | ready | pending_goal_requirements=7; covered=7 | results/reproducibility/goal_completion_report.json |
| external_closure_queue_items_declared | ready | items=6 | results/external_evidence_closure/closure.json |
