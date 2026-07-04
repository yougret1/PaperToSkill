# Real-Reuse Core Stabilization Queue

Date: 2026-07-04

Evidence boundary: this is a planning and triage artifact. It does not add
new task-success evidence, does not change paper-facing main rows, and does
not promote any follow-up row. Main rows remain pinned by
`results/real_reuse/main_run_selection.json`.

## Inputs Reviewed

- `results/real_reuse/failure_analysis.md`
- `results/real_reuse/swe_t1_source_context_followup.md`
- `results/real_reuse/snapatac2_artifact_followup.md`
- `results/real_reuse/snapatac2_executable_artifact_followup.md`
- `results/real_reuse/main_results_plan.md`

## Stabilization Priorities

| Priority | Area | Current Evidence | Next Local Action | Main-Row Policy |
| --- | --- | --- | --- | --- |
| P1 | SNAP executable artifact contract | Main SNAP rows are plan/JSON outputs below threshold; phase108 controlled scaffold closes the artifact/runtime/memory scorer for both conditions. The executable-candidate contract is now pre-registered in `benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json` and summarized in `research/snapatac2_executable_candidate_contract.md`; strict preflight checks pass locally. | Implement a future executable SNAP rerun only against this contract: runner executes candidate code, records runtime/memory, writes artifact manifest, calls the existing scorer, and keeps rows diagnostic unless explicitly promoted. | Do not replace main SNAP rows unless a paired Summary/PaperToSkill rerun uses the same locked fixture, scorer, resource budget, and no-mid-run-human rule and updates `results/real_reuse/main_run_selection.json` by explicit promotion. |
| P2 | SWE-T1 hidden-objective mismatch | First pass failed at patch apply; phase107 shared-source-context follow-up applies both patches but both fail hidden test. The decision is now pre-registered in `benchmarks/real_reuse/swe_t1_task_contract_decision_v0.json` and summarized in `research/swe_t1_task_contract_decision.md`. | Freeze current SWE-T1 as boundary evidence. Do not spend more model calls under the current hidden-test contract; implement an issue-aligned revised test/scorer contract first if a stronger SWE-T1 row is needed later. | Preserve first-pass SWE-T1 as the main row unless an explicitly promoted paired rerun is pre-registered before execution. |
| P3 | AIDE-T1 and REF ceiling rows | AIDE-T1 and REF-T1/T2 are solved by both Summary and PaperToSkill. | Treat as ceiling/control rows unless the paper needs harder slices later. Do not spend model calls here before failure-heavy rows are stabilized. | Keep current main rows. |
| P4 | LLM ablation pending Claude rows | GPT-family and DeepSeek-family slices are collected; Claude-family rows are provider-502 availability metadata. | Retry opportunistically only after provider availability recovers; keep timeout/retry budget generous. | Auxiliary only; never replace main rows. |

## Immediate Non-Network Work

1. If a stronger SWE-T1 row is needed, pre-register an issue-aligned revised
   hidden test/scorer contract before any further SWE-T1 model calls.
2. If SNAP is rerun later, use the pre-registered executable-candidate contract
   rather than the old plan/JSON-only runner path.
3. Keep all future reruns paired: Summary and PaperToSkill must share task,
   fixture, scorer, resource budget, model family unless an ablation is
   explicitly being run, and no-mid-run-human-intervention policy.
