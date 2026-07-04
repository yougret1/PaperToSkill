# SWE-T1 Source-Context Follow-Up

Evidence boundary: this paired follow-up exposes the same locked SQLFluff source slice to Summary and PaperToSkill. It is diagnostic follow-up evidence and does not replace the SWE-T1 first-pass main-table row.

- Raw scored rows read: 26
- Follow-up run id: phase107_gpt_swe_t1_source_context_followup

| Task ID | Condition | First-pass Run | First-pass Score | First-pass Failure | First-pass Patch Applied | Follow-up Run | Follow-up Score | Follow-up Patch Applied | Follow-up Test Passed | Follow-up Failure | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SWE-T1 | Summary | phase97_gpt_swe_t1_summary_retry | 0.000 | patch_apply_failed | No | phase107_gpt_swe_t1_source_context_followup | 0.000 | Yes | No | test_command_failed | Source context fixed patch application; hidden test still failed |
| SWE-T1 | PaperToSkill | phase97_gpt_swe_t1_real_reuse | 0.000 | patch_apply_failed | No | phase107_gpt_swe_t1_source_context_followup | 0.000 | Yes | No | test_command_failed | Source context fixed patch application; hidden test still failed |
