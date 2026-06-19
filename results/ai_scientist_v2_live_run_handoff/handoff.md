# AI-Scientist-v2 Live Run Handoff

Evidence boundary: this is a local handoff/preflight report. It does not run BFTS, does not call an LLM, and does not prove live research-task success.

- Overall status: blocked_by_provider_smoke
- Selected idea: papertoskill_extractor
- Ready checks: 10
- Pending checks: 2
- Failed checks: 0

## Next Command

```powershell
cd D:\a_work\gitee\ai-scientist-v2
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --skip_writeup `
  --skip_review
```

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
| ai_scientist_v2_live_dry_run_artifacts_present | ready | candidate_dirs=1 | D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0 |
| ai_scientist_v2_live_env_names_declared | ready | env_names=AI_SCIENTIST_OPENAI_BASE_URL,AI_SCIENTIST_OPENAI_API_KEY,AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE | local shell environment |
| ai_scientist_v2_live_next_commands_declared | ready | full live command declared | next_commands |
| ai_scientist_v2_live_smoke_complete | pending | smoke_overall=blocked_by_provider_or_model_availability | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\run_report.json |
| ai_scientist_v2_live_completion_artifacts_present | pending | completion_dirs=0 | D:\a_work\gitee\ai-scientist-v2\experiments |
