# DeepSeek Follow-Up Handoff

Evidence boundary: this is a local handoff/preflight report. It does not call DeepSeek and does not complete the DeepSeek ablation.

- Overall status: responses_present
- Model alias: deepseek-v4-flash
- Auth env: DEEPSEEK_API_KEY
- Base URL env: DEEPSEEK_BASE_URL
- Ready checks: 7
- Pending checks: 0
- Failed checks: 0

## Configuration Helper

`scripts/configure_deepseek_followup.py` updates only non-secret slot metadata: model alias, auth environment-variable name, base-URL environment-variable name, and provider status. Keep raw keys in local environment variables and never commit them.

## Prompt Rows

| Case | Prompt | Expected Response |
| --- | --- | --- |
| toolformer_curated_skill_usage | results\model_ablation_prompts\v0\deepseek_followup_slot__toolformer_curated_skill_usage.md | results\model_ablation_prompts\v0\responses\deepseek_followup_slot__toolformer_curated_skill_usage.md |
| aide_auto_skill_usage | results\model_ablation_prompts\v0\deepseek_followup_slot__aide_auto_skill_usage.md | results\model_ablation_prompts\v0\responses\deepseek_followup_slot__aide_auto_skill_usage.md |

## Next Commands

```powershell
python scripts\configure_deepseek_followup.py `
  --task benchmarks\model_ablation_v0.json `
  --model-alias <deepseek-model-alias> `
  --auth-env DEEPSEEK_API_KEY `
  --base-url-env DEEPSEEK_BASE_URL

python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0

python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\deepseek_run_report.json `
  --output-md results\model_ablation_prompts\v0\deepseek_run_report.md `
  --model-id deepseek_followup_slot

python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md

python scripts\check_deepseek_followup.py --strict
```

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| deepseek_followup_slot_present | ready | present | benchmarks\model_ablation_v0.json |
| deepseek_followup_index_rows | ready | rows=2; expected_cases=2 | results\model_ablation_prompts\v0\index.json |
| deepseek_followup_prompt_files | ready | present | results\model_ablation_prompts\v0\index.json |
| deepseek_followup_response_paths_declared | ready | response_paths=2 | results\model_ablation_prompts\v0\index.json |
| deepseek_followup_env_names_declared | ready | auth_env=DEEPSEEK_API_KEY; base_url_env=DEEPSEEK_BASE_URL | benchmarks\model_ablation_v0.json |
| deepseek_followup_alias_configured | ready | alias=deepseek-v4-flash | benchmarks\model_ablation_v0.json |
| deepseek_followup_responses_saved | ready | saved=2; expected=2 | results\model_ablation_prompts\v0\responses\deepseek_followup_slot__toolformer_curated_skill_usage.md; results\model_ablation_prompts\v0\responses\deepseek_followup_slot__aide_auto_skill_usage.md |
