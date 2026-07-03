# Real-Reuse Benchmark Spec Preflight

Evidence boundary: this is a local preflight for the planned real-reuse benchmark. It does not run any paper-task and does not claim downstream task success.

- Overall status: ready_to_implement
- Spec path: benchmarks/real_reuse/real_reuse_v0.json
- Task count: 8
- Ready checks: 296
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
