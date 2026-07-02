# External Evidence Closure Queue

Evidence boundary: this is a local closure queue. It does not collect human annotations, AI-Scientist-v2 live-run artifacts, or final submission approval.

- Overall status: pending_external_evidence
- Queue item statuses: {'pending_reviewers': 1, 'pending_decision': 1}
- Ready checks: 3
- Pending checks: 0
- Failed checks: 0

## Queue Items

| Item | Status | Goal Requirements | Detail | Next Action |
| --- | --- | --- | --- | --- |
| human_fidelity_annotation | pending_reviewers | human_fidelity_annotation_complete | status=pending; scored_rows=0; pending_rows=24 | Independent reviewers fill the annotation template, then rerun the strict summarizer. |
| aaai_submission_decision | pending_decision | aaai_final_submission_ready | aaai_package=ready; submission_review=ready | Choose whether to submit as a deterministic/offline system paper or wait for the external evidence rows. |

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| external_closure_required_reports_present | ready | present | results/reproducibility/goal_completion_report.json; results/ai_scientist_v2_smoke/run_report.json; results/ai_scientist_v2_live_run_handoff/handoff.json; results/deepseek_followup_handoff/handoff.json; results/model_ablation_prompts/v0/evaluation.json; results/human_fidelity_packets/annotation_summary.json; results/token_accounting/token_accounting_summary.json; results/reproducibility/aaai_package_report.json; results/reproducibility/submission_review_report.json |
| external_closure_goal_pending_items_covered | ready | pending_goal_requirements=2; covered=2 | results/reproducibility/goal_completion_report.json |
| external_closure_queue_items_declared | ready | items=2 | results/external_evidence_closure/closure.json |
