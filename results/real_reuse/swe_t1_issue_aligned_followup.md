# SWE-T1 Issue-Aligned Follow-Up

Evidence boundary: this paired follow-up uses the pre-registered SWE-T1 issue-aligned scorer. It is diagnostic contract-closure evidence and does not replace the SWE-T1 first-pass main-table row. Because both Summary and PaperToSkill pass, it does not show a PaperToSkill advantage.

- Raw scored rows read: 40
- Source-context run id: phase107_gpt_swe_t1_source_context_followup
- Issue-aligned run id: phase110_gpt_swe_t1_issue_aligned_followup

| Task ID | Condition | Main Run | Main Score | Phase107 Run | Phase107 Score | Phase107 Test Passed | Issue-Aligned Run | Issue-Aligned Score | Issue-Aligned Test Passed | Issue-Aligned Test Patch | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SWE-T1 | Summary | phase97_gpt_swe_t1_summary_retry | 0.000 | phase107_gpt_swe_t1_source_context_followup | 0.000 | No | phase110_gpt_swe_t1_issue_aligned_followup | 1.000 | Yes | No | Issue-aligned scorer passes both conditions; no PaperToSkill advantage |
| SWE-T1 | PaperToSkill | phase97_gpt_swe_t1_real_reuse | 0.000 | phase107_gpt_swe_t1_source_context_followup | 0.000 | No | phase110_gpt_swe_t1_issue_aligned_followup | 1.000 | Yes | No | Issue-aligned scorer passes both conditions; no PaperToSkill advantage |
