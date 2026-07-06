# Real-Reuse Core Stabilization Queue

Date: 2026-07-06

Evidence boundary: this is a planning and triage artifact. It does not add
new task-success evidence, does not change paper-facing main rows, and does
not promote any follow-up row. Main rows remain pinned by
`results/real_reuse/main_run_selection.json`.

## Inputs Reviewed

- `results/real_reuse/failure_analysis.md`
- `results/real_reuse/swe_t1_source_context_followup.md`
- `results/real_reuse/snapatac2_artifact_followup.md`
- `results/real_reuse/snapatac2_executable_artifact_followup.md`
- `results/real_reuse/snapatac2_executable_candidate_script_generation_report.md`
- `results/real_reuse/snapatac2_executable_candidate_script_generation_phase118_t2_compact.md`
- `results/real_reuse/snapatac2_executable_candidate_run_report.md`
- `results/real_reuse/swe_t1_issue_aligned_followup.md`
- `results/real_reuse/main_results_plan.md`

## Stabilization Priorities

| Priority | Area | Current Evidence | Next Local Action | Main-Row Policy |
| --- | --- | --- | --- | --- |
| P1 | SNAP executable artifact contract | Main SNAP rows are plan/JSON outputs below threshold; phase108 controlled scaffold closes the artifact/runtime/memory scorer for both conditions. The executable-candidate contract is pre-registered in `benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json` and summarized in `research/snapatac2_executable_candidate_contract.md`. The executable-candidate runner is implemented in `scripts/run_real_reuse_snapatac2_executable_candidate.py`, guarded by strict preflight, and covered by `tests/test_run_real_reuse_snapatac2_executable_candidate.py`. Phase112 generated paired revised SNAP-T1 Summary/PaperToSkill candidate scripts and the executable-candidate runner scored both rows 1.000 under `phase112_gpt_snapatac2_executable_candidate_t1`. Phase113, phase115, and phase116 SNAP-T2 Summary generation attempts returned provider HTTP 524 after five, seven, and ten attempts, respectively, with no T2 script produced. Compact prompt packets are generated at `results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.{md,json}` and `results/real_reuse/snapatac2_executable_candidate_compact_prompts/`; they reduce SNAP-T2 Summary from 7,111 bytes to 5,150 bytes and SNAP-T2 PaperToSkill from 14,122 bytes to 5,553 bytes while preserving the runner interface, required artifacts, and scorer-only boundary. Phase118 attempted the compact SNAP-T2 Summary/PaperToSkill generation path with GPT-family `gpt-5.5`, a 600-second timeout, 6 attempts, 10-second retry delay, and `max_tokens=2200`; Summary still returned provider HTTP 524 after six attempts, no script or response was saved, and PaperToSkill was stopped because paired execution could not proceed. These are availability metadata only. | Keep phase112 as diagnostic contract-closure evidence: it shows model-generated scripts can satisfy the artifact/runtime/memory scorer for both conditions, not PaperToSkill advantage. Do not retry SNAP-T2 executable-candidate generation again by simply increasing attempts or shortening prompts. Wait for healthier provider behavior, then if rerun, keep the paired Summary/PaperToSkill compact prompt contract under the same locked fixture/scorer/resource/no-human rule and separate report paths. | Do not replace main SNAP rows unless a paired Summary/PaperToSkill rerun uses the same locked fixture, scorer, resource budget, and no-mid-run-human rule and updates `results/real_reuse/main_run_selection.json` by explicit promotion. |
| P2 | SWE-T1 hidden-objective mismatch | First pass failed at patch apply; phase107 shared-source-context follow-up applies both patches but both fail hidden test. The task-contract decision is pre-registered in `benchmarks/real_reuse/swe_t1_task_contract_decision_v0.json`; the issue-aligned revised check is pre-registered in `benchmarks/real_reuse/swe_t1_issue_aligned_contract_v0.json`, implemented at `benchmarks/real_reuse/assets/SWE-T1/scorer_only/issue_aligned_check.py`, and validated in `results/real_reuse/swe_t1_issue_aligned_contract_validation.{md,json}`. Phase110 then ran a paired issue-aligned follow-up and scored Summary 1.000 and PaperToSkill 1.000 in `results/real_reuse/swe_t1_issue_aligned_run_report.{md,json}`; the dedicated diagnostic table is `results/real_reuse/swe_t1_issue_aligned_followup.{csv,md,json}` and is included in the paper-table checker path. | Freeze current SWE-T1 main row as boundary evidence. Keep phase110 as diagnostic issue-aligned contract closure for both conditions; do not claim PaperToSkill advantage because Summary also passes. Keep the dedicated table/report synchronized if the paper tables are regenerated. | Preserve first-pass SWE-T1 as the main row unless an explicitly promoted paired rerun is pre-registered before execution and `results/real_reuse/main_run_selection.json` is intentionally changed. |
| P3 | AIDE-T1 and REF ceiling rows | AIDE-T1 and REF-T1/T2 are solved by both Summary and PaperToSkill. | Treat as ceiling/control rows unless the paper needs harder slices later. Do not spend model calls here before failure-heavy rows are stabilized. | Keep current main rows. |
| P4 | LLM ablation pending Claude rows | GPT-family and DeepSeek-family slices are collected; Claude-family rows are provider-502 availability metadata. | Retry opportunistically only after provider availability recovers; keep timeout/retry budget generous. | Auxiliary only; never replace main rows. |

## Immediate Non-Network Work

1. Keep the phase110 SWE-T1 issue-aligned diagnostic table/report synchronized
   with paper-table and package checks. Keep it separate from the main table
   unless explicitly promoted.
2. Keep the phase112 SNAP-T1 executable-candidate report and paper diagnostic
   table synchronized. Phase113, phase115, and phase116 SNAP-T2 Summary
   script-generation attempts hit provider HTTP 524 after five, seven, and ten
   attempts, respectively, and phase118 compact SNAP-T2 Summary still hit HTTP
   524 after six attempts. Do not retry SNAP-T2 again by simply increasing
   attempts or shortening the prompt. If provider large-context behavior
   becomes healthier, generate paired Summary/PaperToSkill candidate scripts
   from the compact prompt packets into separate report paths and use the
   implemented runner/pre-registered contract rather than the old plan/JSON-only
   runner path.
3. Keep all future reruns paired: Summary and PaperToSkill must share task,
   fixture, scorer, resource budget, model family unless an ablation is
   explicitly being run, and no-mid-run-human-intervention policy.
