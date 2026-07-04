# SWE-T1 Issue-Aligned Contract Validation

Evidence boundary: this validates the pre-registered issue-aligned check
against the base workspace and existing phase107 candidate patches. It does not
add new model calls, does not append raw rows, and does not replace the
paper-facing SWE-T1 main row.

- Contract: `benchmarks/real_reuse/swe_t1_issue_aligned_contract_v0.json`
- Check script: `benchmarks/real_reuse/assets/SWE-T1/scorer_only/issue_aligned_check.py`

| Case | Patch | Observed | Finding |
| --- | --- | --- | --- |
| Base workspace | none | fail | Alias no-join query still triggers L031. |
| Phase107 Summary patch | `results/real_reuse/runs/SWE-T1/summary/phase107_gpt_swe_t1_source_context_followup/candidate.patch` | pass | Passes the issue-aligned no-join and join-regression checks. |
| Phase107 PaperToSkill patch | `results/real_reuse/runs/SWE-T1/papertoskill/phase107_gpt_swe_t1_source_context_followup/candidate.patch` | fail | Fixes the no-join alias issue but fails the join-regression guard because L031 no longer fires on the join-alias query. |

Policy: keep the first-pass SWE-T1 main row unchanged unless a future paired
rerun is pre-registered and explicitly promoted through
`results/real_reuse/main_run_selection.json`.
