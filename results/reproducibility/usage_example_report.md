# Usage Example Report

Evidence boundary: this report checks local usage-example files and runs an offline auto-note-to-skill example chain. It does not execute live model calls or score model responses.

- Overall status: ready
- Ready checks: 36
- Failed checks: 0

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| usage_readme | ready | present | examples/usage/README.md |
| codex_skill_usage | ready | present | examples/usage/codex_skill_usage.md |
| auto_note_scaffold_usage | ready | present | examples/usage/auto_note_scaffold_usage.md |
| model_ablation_usage | ready | present | examples/usage/model_ablation_usage.md |
| codex_toolformer_skill | ready | present | generated_skills/toolformer/SKILL.md |
| codex_toolformer_source_map | ready | present | generated_skills/toolformer/references/source_map.json |
| codex_toolformer_prompt | ready | present | results/live_transfer_prompts/toolformer_v0/codex_skill__full_skill.md |
| auto_note_source_text | ready | present | papers/extracted/aide.txt |
| auto_note_rubric | ready | present | benchmarks/rubric_aide_v0.json |
| auto_note_script | ready | present | scripts/papertoskill_note_from_text.py |
| extract_script | ready | present | scripts/papertoskill_extract.py |
| evaluate_script | ready | present | scripts/evaluate_skill.py |
| model_ablation_task | ready | present | benchmarks/model_ablation_v0.json |
| model_ablation_prompt_index | ready | present | results/model_ablation_prompts/v0/index.json |
| model_ablation_builder | ready | present | scripts/build_model_ablation_prompts.py |
| model_ablation_runner | ready | present | scripts/run_model_ablation_prompts.py |
| model_ablation_evaluator | ready | present | scripts/evaluate_model_ablation_responses.py |
| usage_readme_mentions_codex | ready | mentions codex_skill_usage.md | examples/usage/README.md |
| usage_readme_mentions_auto_note | ready | mentions auto_note_scaffold_usage.md | examples/usage/README.md |
| usage_readme_mentions_model_ablation | ready | mentions model_ablation_usage.md | examples/usage/README.md |
| codex_usage_mentions_prompt | ready | mentions results/live_transfer_prompts/toolformer_v0/codex_skill__full_skill.md | examples/usage/codex_skill_usage.md |
| auto_note_usage_mentions_profile | ready | mentions --profile aide | examples/usage/auto_note_scaffold_usage.md |
| model_ablation_usage_mentions_deepseek | ready | mentions deepseek_followup_slot | examples/usage/model_ablation_usage.md |
| usage_model_ablation_prompt_grid | ready | prompt_packets=6 | results/model_ablation_prompts/v0/index.json |
| usage_model_ablation_model_slots | ready | models=claude_opus_4_8,deepseek_followup_slot,gpt_5_5_or_gpt_family | results/model_ablation_prompts/v0/index.json |
| usage_model_ablation_cases | ready | cases=aide_auto_skill_usage,toolformer_curated_skill_usage | results/model_ablation_prompts/v0/index.json |
| usage_model_ablation_prompts_exist | ready | missing_prompts=0 | results/model_ablation_prompts/v0/index.json |
| usage_model_ablation_response_slots | ready | response_slots=6 | results/model_ablation_prompts/v0/index.json |
| usage_model_ablation_gpt_profile | ready | auth_env=PAPERTOSKILL_GPT_OPENAI_API_KEY; aliases=gpt-5.4,gpt-5.5 | benchmarks/model_ablation_v0.json |
| usage_model_ablation_claude_alias_candidates | ready | aliases=claude-opus-4-6,claude-opus-4-7,claude-opus-4-8,claude-opus-4.8 | benchmarks/model_ablation_v0.json |
| usage_auto_note_example_note_created | ready | created in temporary directory | temporary/aide_auto_note.md |
| usage_auto_note_example_report_created | ready | created in temporary directory | temporary/aide_auto_note_report.json |
| usage_auto_note_example_skill_created | ready | created in temporary directory | temporary/aide_auto_skill/SKILL.md |
| usage_auto_note_example_source_map_created | ready | created in temporary directory | temporary/aide_auto_skill/references/source_map.json |
| usage_auto_note_example_selected_windows | ready | methods=6; experiments=6; limitations=5 | temporary/aide_auto_note_report.json |
| usage_auto_note_example_rubric_score | ready | 20/20 | temporary/aide_auto_rubric.json |

## Offline Example Sample

- Paper ID: aide_auto_usage_check
- Profile: aide
- Selected windows: methods=6, experiments=6, limitations=5
- Temporary skill rubric score: 20/20
