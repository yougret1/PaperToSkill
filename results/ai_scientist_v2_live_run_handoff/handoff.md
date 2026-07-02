# AI-Scientist-v2 Live Run Handoff

Evidence boundary: this is a local handoff/preflight report. It does not run BFTS, does not call an LLM, and does not prove live research-task success.

- Overall status: complete
- Selected idea: papertoskill_extractor
- Ready checks: 16
- Pending checks: 0
- Failed checks: 0

## Next Command

```powershell
cd D:\a_work\gitee\ai-scientist-v2
Remove-Item Env:\AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE -ErrorAction SilentlyContinue
Remove-Item Env:\AI_SCIENTIST_OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\OPENAI_BASE_URL -ErrorAction SilentlyContinue
$env:ANTHROPIC_BASE_URL='https://coderxiaoc.com'
$env:ANTHROPIC_API_KEY='<set Claude-family token locally>'
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --skip_writeup `
  --skip_review
```

## Partial Stage Attempts

| Stage | Status | Total Nodes | Good Nodes | Buggy Nodes | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1_initial_implementation_1_preliminary | has_good_nodes | 3 | 2 | 0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| 2_baseline_tuning_1_first_attempt | has_good_nodes | 4 | 3 | 0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\notes\stage_progress.json |
| 3_creative_research_1_first_attempt | has_good_nodes | 3 | 3 | 0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_3_creative_research_1_first_attempt\notes\stage_progress.json |
| 1_initial_implementation_1_preliminary | no_good_nodes | 1 | 0 | 1 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-05-00_papertoskill_extractor_deepseek_stage1_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| 1_initial_implementation_1_preliminary | no_good_nodes | 2 | 0 | 2 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-15-00_papertoskill_extractor_deepseek_stage1_debug_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| 1_initial_implementation_1_preliminary | has_good_nodes | 4 | 2 | 1 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| 2_baseline_tuning_1_first_attempt | has_good_nodes | 4 | 3 | 0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\notes\stage_progress.json |
| 3_creative_research_1_first_attempt | has_good_nodes | 4 | 2 | 1 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_3_creative_research_1_first_attempt\notes\stage_progress.json |
| 4_ablation_studies_1_first_attempt | has_good_nodes | 4 | 3 | 0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_4_ablation_studies_1_first_attempt\notes\stage_progress.json |

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| ai_scientist_v2_live_root_present | ready | present | D:\a_work\gitee\ai-scientist-v2 |
| ai_scientist_v2_live_launcher_present | ready | present | D:\a_work\gitee\ai-scientist-v2\launch_scientist_bfts.py |
| ai_scientist_v2_live_launcher_flags_ready | ready | dry_run/skip flags present | D:\a_work\gitee\ai-scientist-v2\launch_scientist_bfts.py |
| ai_scientist_v2_live_config_present | ready | present | D:\a_work\gitee\ai-scientist-v2\bfts_config.yaml |
| ai_scientist_v2_live_config_laptop_profile | ready | num_workers=1 and claude-opus-4-8 profile present | D:\a_work\gitee\ai-scientist-v2\bfts_config.yaml |
| ai_scientist_v2_live_seed_ideas_present | ready | present | D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json |
| ai_scientist_v2_live_seed_idea_selected | ready | idea_idx=0; name=papertoskill_extractor | D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json |
| ai_scientist_v2_live_dry_run_artifacts_present | ready | candidate_dirs=10 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_21-08-42_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_21-11-02_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_21-14-24_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_21-24-58_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_23-50-00_papertoskill_extractor_gpt_responses_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-05-00_papertoskill_extractor_deepseek_stage1_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-15-00_papertoskill_extractor_deepseek_stage1_debug_attempt_0; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0 |
| ai_scientist_v2_live_env_names_declared | ready | env_names=ANTHROPIC_BASE_URL,ANTHROPIC_API_KEY | local shell environment |
| ai_scientist_v2_live_next_commands_declared | ready | full live command declared | next_commands |
| ai_scientist_v2_live_smoke_complete | ready | smoke_overall=complete | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\run_report.json |
| ai_scientist_v2_live_completion_artifacts_present | ready | completion_dirs=1 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0 |
| ai_scientist_v2_live_partial_stage_attempts_present | ready | stage_attempts=9 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_3_creative_research_1_first_attempt\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-05-00_papertoskill_extractor_deepseek_stage1_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-15-00_papertoskill_extractor_deepseek_stage1_debug_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| ai_scientist_v2_live_successful_stage_attempt_present | ready | successful_stage_attempts=7 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-01_22-26-37_papertoskill_extractor_attempt_0\logs\0-run\stage_3_creative_research_1_first_attempt\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\notes\stage_progress.json |
| ai_scientist_v2_live_failed_stage_attempts_recorded | ready | failed_stage_attempts=2 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-05-00_papertoskill_extractor_deepseek_stage1_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_00-15-00_papertoskill_extractor_deepseek_stage1_debug_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\notes\stage_progress.json |
| ai_scientist_v2_live_best_nodes_not_buggy | ready | checked=4; issues=0 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_1_initial_implementation_1_preliminary\best_node_id.txt; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_2_baseline_tuning_1_first_attempt\best_node_id.txt; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_3_creative_research_1_first_attempt\best_node_id.txt; D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0\logs\0-run\stage_4_ablation_studies_1_first_attempt\best_node_id.txt |
