# SnapATAC2 Artifact-Execution Follow-Up Plan

Evidence boundary: this is a diagnosis and pre-registered follow-up contract for SNAP artifact execution. It does not replace the main SNAP rows or add new task-success evidence.

- Follow-up ID: `snapatac2_artifact_execution_followup_v0`
- Overall status: `pre_registered_followup_needed`
- Selected SNAP rows inspected: 4
- `snapatac2` importable: False
- Local SnapATAC2 repo exists: True
- Local SnapATAC2 revision: `7be57442708694217e27c8654ecd38a0de194aa4`

## Current Rows

| Task | Condition | Run | Score | Success | Candidate Status | Execution Gap | Failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SNAP-T1 | summary | phase95_snapatac2_gpt55_live | 0.000 | False | invalid_json | True | Extra data: line 1 column 149 (char 148) |
| SNAP-T1 | papertoskill | phase95_snapatac2_gpt55_live | 0.500 | False | parsed | True | missing_required_artifacts_or_metrics |
| SNAP-T2 | summary | phase95_snapatac2_gpt55_live | 0.200 | False | parsed | True | missing_required_artifacts_or_metrics |
| SNAP-T2 | papertoskill | phase95_snapatac2_gpt55_live | 0.400 | False | parsed | True | missing_required_artifacts_or_metrics |

## Fixture Probe

| Task | Status | Path | Size Bytes | Sample Lines | Field Counts |
| --- | --- | --- | --- | --- | --- |
| SNAP-T1 | readable | benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz | 315693 | 3 | 6,6,6 |
| SNAP-T2 | readable | benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz | 309344 | 3 | 5,5,5 |

## Diagnosis

- Current SNAP rows ask the model for a JSON artifact record but the runner does not execute candidate scripts or commands.
- The scorer requires completed=true plus concrete artifacts and runtime/memory records, so plan-only outputs cannot reach the pre-registered success threshold.
- The local miniature fixtures are readable, but the Python package `snapatac2` is not importable in the current environment.

## Follow-Up Contract

- `main_rows_unchanged`: True
- `conditions`: ['summary', 'papertoskill']
- `paired_conditions_required`: True
- `base_model`: gpt-5.5 unless explicitly running LLM ablation
- `provider_policy`: Use longer timeout/retry budgets; record provider availability separately from task metrics.
- `execution_requirement`: A follow-up runner must execute a controlled candidate script or a pre-registered scaffold that materializes artifacts and measures runtime/memory before setting completed=true.
- `scoring_requirement`: Use the same locked fixture, resource budget, hidden labels/proxy policy, and scorer for Summary and PaperToSkill.
- `human_intervention`: none_mid_run
- `blocked_if`: SnapATAC2 installation or required data download fails; record the command, error, and blocked artifact in toHuman.md and continue other non-blocked work.
