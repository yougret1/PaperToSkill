# Real-Reuse Benchmark Spec Preflight

Evidence boundary: this is a local preflight for the planned real-reuse benchmark. It does not run any paper-task and does not claim downstream task success.

- Overall status: ready_to_implement
- Spec path: benchmarks/real_reuse/real_reuse_v0.json
- Task count: 8
- Ready checks: 85
- Failed checks: 0

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| real_reuse_spec_file | ready | present | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_status_planned | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_main_task_count | ready | tasks=8 | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_expected_task_ids | ready | tasks=AIDE-T1,AIDE-T2,REF-T1,REF-T2,SNAP-T1,SNAP-T2,SWE-T1,SWE-T2 | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_main_papers | ready | main_papers=aide,reflexion,snapatac2,swe_agent | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_main_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_no_abstract_or_full_excerpt_main | ready | excluded=abstract,full_excerpt | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_full_excerpt_sanity_scope | ready | sanity_tasks=AIDE-T1,SNAP-T1,SWE-T1 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_source_paper_known | ready | source_paper_id=aide | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_automated_metric | ready | metric=validation_score; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/AIDE-T1.json results/real_reuse/runs/AIDE-T1/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_source_paper_known | ready | source_paper_id=aide | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_automated_metric | ready | metric=best_node_score; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/AIDE-T2.json results/real_reuse/runs/AIDE-T2/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t2_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_source_paper_known | ready | source_paper_id=reflexion | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_automated_metric | ready | metric=exact_match_or_f1; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/REF-T1.json results/real_reuse/runs/REF-T1/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t1_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_source_paper_known | ready | source_paper_id=reflexion | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_automated_metric | ready | metric=second_attempt_success; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/REF-T2.json results/real_reuse/runs/REF-T2/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| ref_t2_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_source_paper_known | ready | source_paper_id=snapatac2 | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_automated_metric | ready | metric=runtime_memory_quality; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/SNAP-T1.json results/real_reuse/runs/SNAP-T1/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t1_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_source_paper_known | ready | source_paper_id=snapatac2 | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_automated_metric | ready | metric=ari_nmi_runtime_memory; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/SNAP-T2.json results/real_reuse/runs/SNAP-T2/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| snap_t2_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_source_paper_known | ready | source_paper_id=swe_agent | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_automated_metric | ready | metric=resolved; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/SWE-T1.json results/real_reuse/runs/SWE-T1/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t1_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_source_paper_known | ready | source_paper_id=swe_agent | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_planned_status | ready | status=planned | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_conditions_are_primary_only | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_automated_metric | ready | metric=tests_passed; automated=True | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_reference_boundary | ready | reported_reference_only_until_local_reproduction | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_planned_artifacts_declared | ready | benchmarks/real_reuse/tasks/SWE-T2.json results/real_reuse/runs/SWE-T2/ results/real_reuse/raw_rows.jsonl | benchmarks/real_reuse/real_reuse_v0.json |
| swe_t2_workflow_checklist_preregistered | ready | items=4 | benchmarks/real_reuse/real_reuse_v0.json |
| ai_scientist_v2_paper_url_declared | ready | https://arxiv.org/abs/2504.08066 | benchmarks/real_reuse/real_reuse_v0.json |
| ai_scientist_v2_resource_status_declared | ready | existing_integration_case | benchmarks/real_reuse/real_reuse_v0.json |
| aide_paper_url_declared | ready | https://arxiv.org/abs/2502.13138 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_resource_status_declared | ready | paper_and_code_urls_reachable | benchmarks/real_reuse/real_reuse_v0.json |
| aide_code_url_declared | ready | https://github.com/WecoAI/aideml | benchmarks/real_reuse/real_reuse_v0.json |
| reflexion_paper_url_declared | ready | https://arxiv.org/abs/2303.11366 | benchmarks/real_reuse/real_reuse_v0.json |
| reflexion_resource_status_declared | ready | paper_and_code_urls_reachable | benchmarks/real_reuse/real_reuse_v0.json |
| reflexion_code_url_declared | ready | https://github.com/noahshinn/reflexion | benchmarks/real_reuse/real_reuse_v0.json |
| snapatac2_paper_url_declared | ready | https://www.nature.com/articles/s41592-023-02139-9 | benchmarks/real_reuse/real_reuse_v0.json |
| snapatac2_resource_status_declared | ready | paper_url_reachable_code_url_reaches_current_scverse_repo | benchmarks/real_reuse/real_reuse_v0.json |
| snapatac2_code_url_declared | ready | https://github.com/scverse/SnapATAC2 | benchmarks/real_reuse/real_reuse_v0.json |
| swe_agent_paper_url_declared | ready | https://arxiv.org/abs/2405.15793 | benchmarks/real_reuse/real_reuse_v0.json |
| swe_agent_resource_status_declared | ready | paper_and_code_urls_reachable | benchmarks/real_reuse/real_reuse_v0.json |
| swe_agent_code_url_declared | ready | https://github.com/SWE-agent/SWE-agent | benchmarks/real_reuse/real_reuse_v0.json |
| toolformer_paper_url_declared | ready | https://arxiv.org/abs/2302.04761 | benchmarks/real_reuse/real_reuse_v0.json |
| toolformer_resource_status_declared | ready | existing_papertoskill_case | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_llm_ablation_linked_to_tasks | ready | linked=True | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_llm_ablation_model_families | ready | families=Claude-family,DeepSeek-family,GPT-family | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_llm_ablation_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_planned_outputs_complete | ready | outputs=6 | benchmarks/real_reuse/real_reuse_v0.json |
| real_reuse_planned_outputs_under_results_real_reuse | ready | results_real_reuse_paths=6 | benchmarks/real_reuse/real_reuse_v0.json |
