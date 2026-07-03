# Real-Reuse Benchmark Spec Preflight

Evidence boundary: this is a local preflight for the planned real-reuse benchmark. It does not run any paper-task and does not claim downstream task success.

- Overall status: ready_to_implement
- Spec path: benchmarks/real_reuse/real_reuse_v0.json
- Task count: 8
- Ready checks: 401
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
| aide_t1_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_identity | ready | id=AIDE-T1; source_paper_id=aide | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_metric_matches | ready | metric=validation_score | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t1_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/AIDE-T1.json |
| aide_t2_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_identity | ready | id=AIDE-T2; source_paper_id=aide | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_metric_matches | ready | metric=best_node_score | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/AIDE-T2.json |
| aide_t2_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/AIDE-T2.json |
| ref_t1_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_identity | ready | id=REF-T1; source_paper_id=reflexion | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_metric_matches | ready | metric=exact_match_or_f1 | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t1_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/REF-T1.json |
| ref_t2_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_identity | ready | id=REF-T2; source_paper_id=reflexion | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_metric_matches | ready | metric=second_attempt_success | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/REF-T2.json |
| ref_t2_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/REF-T2.json |
| snap_t1_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_identity | ready | id=SNAP-T1; source_paper_id=snapatac2 | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_metric_matches | ready | metric=runtime_memory_quality | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t1_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/SNAP-T1.json |
| snap_t2_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_identity | ready | id=SNAP-T2; source_paper_id=snapatac2 | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_metric_matches | ready | metric=ari_nmi_runtime_memory | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/SNAP-T2.json |
| snap_t2_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/SNAP-T2.json |
| swe_t1_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_identity | ready | id=SWE-T1; source_paper_id=swe_agent | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_metric_matches | ready | metric=resolved | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t1_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/SWE-T1.json |
| swe_t2_task_spec_file_present | ready | present | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_identity | ready | id=SWE-T2; source_paper_id=swe_agent | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_status | ready | status=spec_ready_assets_pending | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_metric_matches | ready | metric=tests_passed | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_raw_row_schema | ready | fields=condition,domain,failure_reason,interventions,model_alias,model_family,output_path,run_id,source_paper_id,success,task_id,task_score,time_seconds,tokens,unsupported_errors,workflow_score | benchmarks/real_reuse/tasks/SWE-T2.json |
| swe_t2_task_spec_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/tasks/SWE-T2.json |
| real_reuse_task_specs_materialized | ready | task_specs=AIDE-T1,AIDE-T2,REF-T1,REF-T2,SNAP-T1,SNAP-T2,SWE-T1,SWE-T2 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_identity | ready | task_id=AIDE-T1; source_paper_id=aide | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_metric_matches_task | ready | metric=validation_score | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t1_fixture_license_review_pending | ready | {'license_review': 'required_before_download_or_commit', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/AIDE-T1.json |
| aide_t2_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_identity | ready | task_id=AIDE-T2; source_paper_id=aide | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_metric_matches_task | ready | metric=best_node_score | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| aide_t2_fixture_license_review_pending | ready | {'license_review': 'required_before_download_or_commit', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/AIDE-T2.json |
| ref_t1_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_identity | ready | task_id=REF-T1; source_paper_id=reflexion | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_metric_matches_task | ready | metric=exact_match_or_f1 | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t1_fixture_license_review_pending | ready | {'license_review': 'required_before_dataset_use', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/REF-T1.json |
| ref_t2_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_identity | ready | task_id=REF-T2; source_paper_id=reflexion | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_metric_matches_task | ready | metric=second_attempt_success | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/REF-T2.json |
| ref_t2_fixture_license_review_pending | ready | {'license_review': 'required_before_dataset_or_repo_use', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/REF-T2.json |
| snap_t1_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_identity | ready | task_id=SNAP-T1; source_paper_id=snapatac2 | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_metric_matches_task | ready | metric=runtime_memory_quality | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t1_fixture_license_review_pending | ready | {'license_review': 'required_before_dataset_use', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/SNAP-T1.json |
| snap_t2_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_identity | ready | task_id=SNAP-T2; source_paper_id=snapatac2 | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_asset_slots_declared | ready | asset_slots=4 | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_metric_matches_task | ready | metric=ari_nmi_runtime_memory | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| snap_t2_fixture_license_review_pending | ready | {'license_review': 'required_before_dataset_use', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/SNAP-T2.json |
| swe_t1_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_identity | ready | task_id=SWE-T1; source_paper_id=swe_agent | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_asset_slots_declared | ready | asset_slots=3 | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_metric_matches_task | ready | metric=resolved | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t1_fixture_license_review_pending | ready | {'license_review': 'required_before_clone_or_patch_release', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/SWE-T1.json |
| swe_t2_fixture_manifest_present | ready | present | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_identity | ready | task_id=SWE-T2; source_paper_id=swe_agent | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_status | ready | status=fixture_manifest_ready_assets_pending | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_asset_slots_declared | ready | asset_slots=3 | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_context_conditions | ready | conditions=papertoskill,summary | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_metric_matches_task | ready | metric=tests_passed | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixtures/SWE-T2.json |
| swe_t2_fixture_license_review_pending | ready | {'license_review': 'required_before_clone_or_patch_release', 'download_or_clone_status': 'not_started', 'external_project_root_policy': 'Place newly downloaded projects under D:/a_work/gitee.', 'secret_policy': 'Do not store API keys, private tokens, or credential-bearing logs in this manifest.'} | benchmarks/real_reuse/fixtures/SWE-T2.json |
| real_reuse_fixture_manifests_materialized | ready | fixtures=AIDE-T1,AIDE-T2,REF-T1,REF-T2,SNAP-T1,SNAP-T2,SWE-T1,SWE-T2 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_identity | ready | task_id=AIDE-T1; source_paper_id=aide | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_selected | ready | mle_bench_spaceship_titanic_submission | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_assets_match_slots | ready | asset_slots=dataset_manifest,starter_workspace,train_split,validation_split | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_scoring_plan | ready | metric=validation_score; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t1_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/AIDE-T1.json |
| aide_t2_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_identity | ready | task_id=AIDE-T2; source_paper_id=aide | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_selected | ready | mle_bench_spaceship_titanic_debug_workspace | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_assets_match_slots | ready | asset_slots=error_or_score_feedback,starter_workspace,validation_split,weak_script | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_scoring_plan | ready | metric=best_node_score; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| aide_t2_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/AIDE-T2.json |
| ref_t1_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_identity | ready | task_id=REF-T1; source_paper_id=reflexion | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_selected | ready | hotpotqa_distractor_reflection_retry | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_assets_match_slots | ready | asset_slots=answer_key,feedback_protocol,question,retrieval_context_or_tool_stub | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_preparation_plan | ready | commands=2; status=not_started | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_scoring_plan | ready | metric=exact_match_or_f1; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t1_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/REF-T1.json |
| ref_t2_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_identity | ready | task_id=REF-T2; source_paper_id=reflexion | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_selected | ready | humaneval_failed_attempt_retry | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_assets_match_slots | ready | asset_slots=environment_feedback,failed_first_attempt,initial_task,objective_checker | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_scoring_plan | ready | metric=second_attempt_success; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| ref_t2_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/REF-T2.json |
| snap_t1_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_identity | ready | task_id=SNAP-T1; source_paper_id=snapatac2 | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_selected | ready | snapatac2_pbmc5k_embedding_pipeline | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_assets_match_slots | ready | asset_slots=dataset_manifest,expected_artifact_schema,preprocessing_notes,resource_budget | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_scoring_plan | ready | metric=runtime_memory_quality; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t1_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/SNAP-T1.json |
| snap_t2_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_identity | ready | task_id=SNAP-T2; source_paper_id=snapatac2 | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_selected | ready | snapatac2_multiome_or_cluster_labels | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_assets_match_slots | ready | asset_slots=dataset_manifest,expected_artifact_schema,reference_labels_or_proxy,resource_budget | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_assets_not_downloaded | ready | candidate_assets=4 | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_scoring_plan | ready | metric=ari_nmi_runtime_memory; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| snap_t2_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/SNAP-T2.json |
| swe_t1_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_identity | ready | task_id=SWE-T1; source_paper_id=swe_agent | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_selected | ready | swe_bench_lite_issue_to_patch | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_assets_match_slots | ready | asset_slots=issue_description,repository_snapshot,target_test_command | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_assets_not_downloaded | ready | candidate_assets=3 | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_scoring_plan | ready | metric=resolved; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t1_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/SWE-T1.json |
| swe_t2_fixture_candidate_present | ready | present | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_identity | ready | task_id=SWE-T2; source_paper_id=swe_agent | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_status | ready | status=candidate_assets_selected_preparation_pending | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_selected | ready | swe_bench_verified_failing_test_patch | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_source_urls | ready | source_urls=3 | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_assets_match_slots | ready | asset_slots=failing_test,repository_snapshot,target_test_command | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_assets_not_downloaded | ready | candidate_assets=3 | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_preparation_plan | ready | commands=3; status=not_started | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_scoring_plan | ready | metric=tests_passed; scorer_status=to_implement_next_phase | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| swe_t2_fixture_candidate_boundary | ready | This file records selected candidate assets and preparation commands only. It does not download data, clone repositories, execute tasks, score outputs, or provide downstream task-success results. | benchmarks/real_reuse/fixture_candidates/SWE-T2.json |
| real_reuse_fixture_candidates_materialized | ready | candidates=AIDE-T1,AIDE-T2,REF-T1,REF-T2,SNAP-T1,SNAP-T2,SWE-T1,SWE-T2 | benchmarks/real_reuse/real_reuse_v0.json |
| aide_t1_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_identity | ready | task_id=AIDE-T1; source_paper_id=aide | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_selected_candidate_matches | ready | mle_bench_spaceship_titanic_submission | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_instance_locked | ready | {'source_kind': 'kaggle_competition', 'competition_slug': 'spaceship-titanic', 'local_instance_id': 'spaceship-titanic-validation-seed-20260703', 'split_seed': 20260703, 'split_policy': 'Create a deterministic local validation split from Kaggle training data; labels are scorer-only and must not enter model context.', 'reference_boundary': 'Kaggle/AIDE paper scores remain reported references unless this exact local split and budget are reproduced.'} | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_source_revisions | ready | source_locks=3; observed=2 | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_slots_match_fixture | ready | asset_slots=dataset_manifest,starter_workspace,train_split,validation_split | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/AIDE-T1', 'prepared_manifest': 'benchmarks/real_reuse/assets/AIDE-T1/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/AIDE-T1/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'mle-bench', 'url': 'https://github.com/openai/mle-bench', 'local_path': 'D:/a_work/gitee/mle-bench'}]} | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_aide_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_hidden_assets | ready | validation_labels.csv,heldout split labels | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_scoring_contract | ready | metric=validation_score; scorer=scripts/score_real_reuse_aide.py | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t1_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/AIDE-T1.json |
| aide_t2_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_identity | ready | task_id=AIDE-T2; source_paper_id=aide | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_selected_candidate_matches | ready | mle_bench_spaceship_titanic_debug_workspace | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_instance_locked | ready | {'source_kind': 'kaggle_competition_debug_fixture', 'competition_slug': 'spaceship-titanic', 'local_instance_id': 'spaceship-titanic-debug-weak-script-seed-20260703', 'split_seed': 20260703, 'weak_script_seed': 20260703, 'split_policy': 'Use the same deterministic validation split as AIDE-T1 and generate one weak baseline script before model runs.', 'reference_boundary': 'Only Summary and PaperToSkill runs under the same weak script and budget are strict comparisons.'} | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_source_revisions | ready | source_locks=3; observed=2 | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_slots_match_fixture | ready | asset_slots=error_or_score_feedback,starter_workspace,validation_split,weak_script | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/AIDE-T2', 'prepared_manifest': 'benchmarks/real_reuse/assets/AIDE-T2/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/AIDE-T2/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'mle-bench', 'url': 'https://github.com/openai/mle-bench', 'local_path': 'D:/a_work/gitee/mle-bench'}]} | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_aide_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_hidden_assets | ready | validation_labels.csv,heldout split labels | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_scoring_contract | ready | metric=best_node_score; scorer=scripts/score_real_reuse_aide.py | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| aide_t2_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/AIDE-T2.json |
| ref_t1_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_identity | ready | task_id=REF-T1; source_paper_id=reflexion | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_selected_candidate_matches | ready | hotpotqa_distractor_reflection_retry | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_instance_locked | ready | {'source_kind': 'hotpotqa_distractor_validation_example', 'dataset_id': 'hotpotqa/hotpot_qa', 'dataset_sha': '1908d6afbbead072334abe2965f91bd2709910ab', 'config': 'distractor', 'split': 'validation', 'example_id': '5a8b57f25542995d1e6f1371', 'level': 'hard', 'type': 'comparison', 'question': 'Were Scott Derrickson and Ed Wood of the same nationality?', 'answer_key_policy': 'The gold answer is scorer-only; the model receives only the question, context/tool stub, and fixed feedback protocol.', 'reference_boundary': 'Reflexion paper scores are reported references unless this exact QA setup and retry budget are reproduced.'} | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_source_revisions | ready | source_locks=3; observed=2 | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_slots_match_fixture | ready | asset_slots=answer_key,feedback_protocol,question,retrieval_context_or_tool_stub | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/REF-T1', 'prepared_manifest': 'benchmarks/real_reuse/assets/REF-T1/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/REF-T1/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': []} | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_reflexion_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_hidden_assets | ready | gold answer,supporting-fact labels if not part of the allowed retrieval context | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_scoring_contract | ready | metric=exact_match_or_f1; scorer=scripts/score_real_reuse_reflexion.py | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t1_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/REF-T1.json |
| ref_t2_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_identity | ready | task_id=REF-T2; source_paper_id=reflexion | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_selected_candidate_matches | ready | humaneval_failed_attempt_retry | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_instance_locked | ready | {'source_kind': 'humaneval_second_attempt_retry', 'dataset_id': 'openai/openai_humaneval', 'dataset_sha': '7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544', 'split': 'test', 'task_id': 'HumanEval/0', 'entry_point': 'has_close_elements', 'failed_first_attempt_seed': 20260703, 'answer_key_policy': 'Canonical solution and tests are scorer/harness assets; model sees prompt plus fixed failed-attempt feedback only.', 'reference_boundary': 'Reflexion paper scores are references unless the same HumanEval task, feedback protocol, and budget are reproduced.'} | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_source_revisions | ready | source_locks=3; observed=2 | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_slots_match_fixture | ready | asset_slots=environment_feedback,failed_first_attempt,initial_task,objective_checker | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/REF-T2', 'prepared_manifest': 'benchmarks/real_reuse/assets/REF-T2/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/REF-T2/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'human-eval', 'url': 'https://github.com/openai/human-eval', 'local_path': 'D:/a_work/gitee/human-eval'}]} | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_reflexion_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_hidden_assets | ready | canonical solution,private test oracle beyond provided feedback | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_scoring_contract | ready | metric=second_attempt_success; scorer=scripts/score_real_reuse_reflexion.py | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/REF-T2.json |
| ref_t2_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/REF-T2.json |
| snap_t1_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_identity | ready | task_id=SNAP-T1; source_paper_id=snapatac2 | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_selected_candidate_matches | ready | snapatac2_pbmc5k_embedding_pipeline | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_instance_locked | ready | {'source_kind': 'snapatac2_builtin_dataset_pipeline', 'dataset_function': 'snapatac2.datasets.pbmc5k', 'tutorial_path': 'docs/tutorials/pbmc.ipynb', 'tutorial_lfs_oid': 'sha256:7b58060a27e69637f01ad41ebcdadb86cf023d3a912307da6b094b2bdf32fa9b', 'api_docs': 'https://scverse.org/SnapATAC2/api/index.html', 'resource_metric_policy': 'Score completion, expected artifact schema, runtime, and memory; do not score subjective biological interpretation.', 'reference_boundary': 'SnapATAC2 paper scores remain reported references unless the same dataset, environment, and resource measurement are reproduced.'} | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_source_revisions | ready | source_locks=3; observed=3 | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_slots_match_fixture | ready | asset_slots=dataset_manifest,expected_artifact_schema,preprocessing_notes,resource_budget | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/SNAP-T1', 'prepared_manifest': 'benchmarks/real_reuse/assets/SNAP-T1/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/SNAP-T1/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'SnapATAC2', 'url': 'https://github.com/scverse/SnapATAC2', 'local_path': 'D:/a_work/gitee/SnapATAC2'}]} | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_snapatac2_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_hidden_assets | ready | post-run metric file,resource scorer thresholds | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_scoring_contract | ready | metric=runtime_memory_quality; scorer=scripts/score_real_reuse_snapatac2.py | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t1_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/SNAP-T1.json |
| snap_t2_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_identity | ready | task_id=SNAP-T2; source_paper_id=snapatac2 | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_selected_candidate_matches | ready | snapatac2_multiome_or_cluster_labels | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_instance_locked | ready | {'source_kind': 'snapatac2_builtin_multiome_or_cluster_fixture', 'dataset_function': 'snapatac2.datasets.pbmc10k_multiome', 'tutorial_path': 'docs/tutorials/modality.ipynb', 'tutorial_lfs_oid': 'sha256:79c7640e3fc12e0f2a9b9aac4f834cc4822865c5cbc3600358bd63ff7b1c8c37', 'api_docs': 'https://scverse.org/SnapATAC2/api/index.html', 'resource_metric_policy': 'Pre-register ARI/NMI when labels are available; otherwise mark the metric as a proxy before execution.', 'reference_boundary': 'Do not compare to paper resource scores as strict evidence unless the same data and environment are reproduced.'} | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_source_revisions | ready | source_locks=3; observed=3 | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_slots_match_fixture | ready | asset_slots=dataset_manifest,expected_artifact_schema,reference_labels_or_proxy,resource_budget | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/SNAP-T2', 'prepared_manifest': 'benchmarks/real_reuse/assets/SNAP-T2/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/SNAP-T2/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'SnapATAC2', 'url': 'https://github.com/scverse/SnapATAC2', 'local_path': 'D:/a_work/gitee/SnapATAC2'}]} | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_snapatac2_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_hidden_assets | ready | reference labels if used only for scoring,post-run metric file | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_scoring_contract | ready | metric=ari_nmi_runtime_memory; scorer=scripts/score_real_reuse_snapatac2.py | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| snap_t2_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/SNAP-T2.json |
| swe_t1_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_identity | ready | task_id=SWE-T1; source_paper_id=swe_agent | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_selected_candidate_matches | ready | swe_bench_lite_issue_to_patch | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_instance_locked | ready | {'source_kind': 'swe_bench_lite_dev_instance', 'dataset_id': 'princeton-nlp/SWE-bench_Lite', 'dataset_sha': '6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2', 'split': 'dev', 'instance_id': 'sqlfluff__sqlfluff-1625', 'repo': 'sqlfluff/sqlfluff', 'base_commit': '14e1a23a3166b9a645a16de96f694c77a5d4abb7', 'fail_to_pass': ['test/cli/commands_test.py::test__cli__command_directed'], 'reference_boundary': 'SWE-agent/SWE-bench paper scores are reported references unless the same instance, tests, and budget are reproduced locally.'} | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_source_revisions | ready | source_locks=3; observed=3 | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_slots_match_fixture | ready | asset_slots=issue_description,repository_snapshot,target_test_command | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/SWE-T1', 'prepared_manifest': 'benchmarks/real_reuse/assets/SWE-T1/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/SWE-T1/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'SWE-bench', 'url': 'https://github.com/princeton-nlp/SWE-bench', 'local_path': 'D:/a_work/gitee/SWE-bench'}]} | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_swe_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_hidden_assets | ready | gold patch,test_patch beyond allowed failing-test context | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_scoring_contract | ready | metric=resolved; scorer=scripts/score_real_reuse_swe.py | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t1_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/SWE-T1.json |
| swe_t2_asset_lock_present | ready | present | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_identity | ready | task_id=SWE-T2; source_paper_id=swe_agent | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_status | ready | status=asset_lock_ready_preparation_pending | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_selected_candidate_matches | ready | swe_bench_verified_failing_test_patch | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_instance_locked | ready | {'source_kind': 'swe_bench_verified_test_instance', 'dataset_id': 'princeton-nlp/SWE-bench_Verified', 'dataset_sha': 'c104f840cc67f8b6eec6f759ebc8b2693d585d4a', 'split': 'test', 'instance_id': 'astropy__astropy-12907', 'repo': 'astropy/astropy', 'base_commit': 'd16bfe05a744909de4b27f5875fe0d4ed41ce607', 'fail_to_pass': ['astropy/modeling/tests/test_separable.py::test_separable[compound_model6-result6]', 'astropy/modeling/tests/test_separable.py::test_separable[compound_model9-result9]'], 'difficulty': '15 min - 1 hour', 'reference_boundary': 'Strict comparison is only Summary vs PaperToSkill on this same verified instance and run budget.'} | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_source_revisions | ready | source_locks=3; observed=3 | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_slots_match_fixture | ready | asset_slots=failing_test,repository_snapshot,target_test_command | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_local_targets | ready | {'asset_dir': 'benchmarks/real_reuse/assets/SWE-T2', 'prepared_manifest': 'benchmarks/real_reuse/assets/SWE-T2/asset_manifest.json', 'run_dir': 'results/real_reuse/runs/SWE-T2/', 'external_project_root': 'D:/a_work/gitee', 'external_projects': [{'name': 'SWE-bench', 'url': 'https://github.com/princeton-nlp/SWE-bench', 'local_path': 'D:/a_work/gitee/SWE-bench'}]} | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_preparation_contract | ready | preparer=scripts/prepare_real_reuse_swe_fixture.py; status=not_started | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_hidden_assets | ready | gold patch,test_patch beyond allowed failing-test context | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_scoring_contract | ready | metric=tests_passed; scorer=scripts/score_real_reuse_swe.py | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_no_mid_run_human | ready | first_pass_human_intervention=none_mid_run | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| swe_t2_asset_lock_boundary | ready | This lock fixes the selected external source revisions, task instance, local materialization targets, and scorer/preparer contracts for a future real-reuse run. It does not download assets, run models, score outputs, or provide downstream task-success evidence. | benchmarks/real_reuse/asset_locks/SWE-T2.json |
| real_reuse_asset_locks_materialized | ready | asset_locks=AIDE-T1,AIDE-T2,REF-T1,REF-T2,SNAP-T1,SNAP-T2,SWE-T1,SWE-T2 | benchmarks/real_reuse/real_reuse_v0.json |
