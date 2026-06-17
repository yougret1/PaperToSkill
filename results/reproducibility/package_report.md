# Reproducibility Package Report

Evidence boundary: this report checks local package completeness and separates pending external evidence from local failures.

- Overall status: ready_with_pending_external_evidence
- Ready checks: 63
- Pending checks: 4
- Failed checks: 0

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| memory_long_term | ready | present | memory/long_term_memory.md |
| memory_short_term | ready | present | memory/short_term_memory.md |
| paper_draft | ready | present | paper/draft.md |
| paper_outline | ready | present | paper/outline.md |
| claim_checklist | ready | present | paper/claim_checklist.md |
| limitations | ready | present | paper/limitations.md |
| artifact_map | ready | present | research/artifact_map.md |
| claim_evidence_matrix | ready | present | research/claim_evidence_matrix.md |
| stage_log | ready | present | research/stage_log.md |
| result_cards | ready | present | results/result_cards.md |
| main_results_md | ready | present | results/tables/main_results.md |
| main_results_csv | ready | present | results/tables/main_results.csv |
| transfer_ablation_md | ready | present | results/tables/transfer_ablation.md |
| context_cost_proxy_md | ready | present | results/tables/context_cost_proxy.md |
| context_cost_proxy_json | ready | present | results/tables/context_cost_proxy.json |
| paper_ready_summary | ready | present | results/tables/paper_ready_summary.md |
| ai_scientist_v2_skill | ready | present | generated_skills/ai_scientist_v2/SKILL.md |
| ai_scientist_v2_source_map | ready | present | generated_skills/ai_scientist_v2/references/source_map.json |
| ai_scientist_v2_rubric | ready | present | results/evaluations/ai_scientist_v2_rubric_v0.json |
| ai_scientist_v2_context | ready | present | results/evaluations/ai_scientist_v2_context_baselines_v0.json |
| ai_scientist_v2_transfer | ready | present | results/evaluations/ai_scientist_v2_harness_transfer_v0.json |
| ai_scientist_v2_source_span | ready | present | results/evaluations/ai_scientist_v2_source_span_validation_v0.json |
| ai_scientist_v2_live_prompt_index | ready | present | results/live_transfer_prompts/ai_scientist_v2_v0/index.json |
| ai_scientist_v2_rubric_score | ready | 20/20 | results/evaluations/ai_scientist_v2_rubric_v0.json |
| ai_scientist_v2_context_baseline_order | ready | skill=7.867; generic=1.733; abstract=1.2 | results/evaluations/ai_scientist_v2_context_baselines_v0.json |
| ai_scientist_v2_transfer_ablation_order | ready | full=10.0; no_transfer=7.6 | results/evaluations/ai_scientist_v2_harness_transfer_v0.json |
| ai_scientist_v2_source_span_support | ready | support_rate=0.938; invalid_ranges=0 | results/evaluations/ai_scientist_v2_source_span_validation_v0.json |
| ai_scientist_v2_live_prompt_packets | ready | prompt_packets=6; missing_prompts=0 | results/live_transfer_prompts/ai_scientist_v2_v0/index.json |
| ai_scientist_v2_live_responses | pending | missing_response_files=6 | results/live_transfer_prompts/ai_scientist_v2_v0/index.json |
| reflexion_skill | ready | present | generated_skills/reflexion/SKILL.md |
| reflexion_source_map | ready | present | generated_skills/reflexion/references/source_map.json |
| reflexion_rubric | ready | present | results/evaluations/reflexion_rubric_v0.json |
| reflexion_context | ready | present | results/evaluations/reflexion_context_baselines_v0.json |
| reflexion_transfer | ready | present | results/evaluations/reflexion_harness_transfer_v0.json |
| reflexion_source_span | ready | present | results/evaluations/reflexion_source_span_validation_v0.json |
| reflexion_live_prompt_index | ready | present | results/live_transfer_prompts/reflexion_v0/index.json |
| reflexion_rubric_score | ready | 20/20 | results/evaluations/reflexion_rubric_v0.json |
| reflexion_context_baseline_order | ready | skill=8.267; generic=3.483; abstract=2.533 | results/evaluations/reflexion_context_baselines_v0.json |
| reflexion_transfer_ablation_order | ready | full=10.0; no_transfer=7.6 | results/evaluations/reflexion_harness_transfer_v0.json |
| reflexion_source_span_support | ready | support_rate=1; invalid_ranges=0 | results/evaluations/reflexion_source_span_validation_v0.json |
| reflexion_live_prompt_packets | ready | prompt_packets=6; missing_prompts=0 | results/live_transfer_prompts/reflexion_v0/index.json |
| reflexion_live_responses | pending | missing_response_files=6 | results/live_transfer_prompts/reflexion_v0/index.json |
| aide_skill | ready | present | generated_skills/aide/SKILL.md |
| aide_source_map | ready | present | generated_skills/aide/references/source_map.json |
| aide_rubric | ready | present | results/evaluations/aide_rubric_v0.json |
| aide_context | ready | present | results/evaluations/aide_context_baselines_v0.json |
| aide_transfer | ready | present | results/evaluations/aide_harness_transfer_v0.json |
| aide_source_span | ready | present | results/evaluations/aide_source_span_validation_v0.json |
| aide_live_prompt_index | ready | present | results/live_transfer_prompts/aide_v0/index.json |
| aide_rubric_score | ready | 20/20 | results/evaluations/aide_rubric_v0.json |
| aide_context_baseline_order | ready | skill=9.1; generic=1.916; abstract=1.333 | results/evaluations/aide_context_baselines_v0.json |
| aide_transfer_ablation_order | ready | full=10.0; no_transfer=7.6 | results/evaluations/aide_harness_transfer_v0.json |
| aide_source_span_support | ready | support_rate=1; invalid_ranges=0 | results/evaluations/aide_source_span_validation_v0.json |
| aide_live_prompt_packets | ready | prompt_packets=6; missing_prompts=0 | results/live_transfer_prompts/aide_v0/index.json |
| aide_live_responses | pending | missing_response_files=6 | results/live_transfer_prompts/aide_v0/index.json |
| human_fidelity_protocol | ready | present | benchmarks/human_fidelity_review_v0.json |
| human_fidelity_template | ready | present | results/human_fidelity_packets/annotation_template.csv |
| human_fidelity_summary_json | ready | present | results/human_fidelity_packets/annotation_summary.json |
| human_fidelity_summary_md | ready | present | results/human_fidelity_packets/annotation_summary.md |
| human_fidelity_summary_valid | ready | errors=0 | results\human_fidelity_packets\annotation_summary.json |
| human_fidelity_annotation_complete | pending | status=pending; scored_rows=0; pending_rows=18 | results\human_fidelity_packets\annotation_summary.json |
| failure_archive_config | ready | present | benchmarks/failure_case_archive_v0.json |
| failure_archive_json | ready | present | results/failure_cases/failure_case_archive.json |
| failure_archive_md | ready | present | results/failure_cases/failure_case_archive.md |
| failure_archive_csv | ready | present | results/failure_cases/failure_case_archive.csv |
| failure_archive_counts | ready | total=20; paper=14; project=6 | results\failure_cases\failure_case_archive.json |
| secret_scan | ready | no raw API-key-like strings found | repository text files |
