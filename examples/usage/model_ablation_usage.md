# Usage Example: Claude/GPT/DeepSeek Model Ablation Protocol

## Build Prompt Packets

```powershell
python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0
```

## Run Model Slots

Use environment variables rather than tracked files:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
```

For each prompt listed in `results/model_ablation_prompts/v0/index.json`, send
the prompt text to the selected model alias and save the response to the
`expected_response_path`.

The repository also includes a runner/evaluator pair:

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\run_report.json `
  --output-md results\model_ablation_prompts\v0\run_report.md `
  --model-id claude_opus_4_8 `
  --model-id gpt_5_5_or_gpt_family

python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md
```

## Current Model Slots

- `claude_opus_4_8`: use `claude-opus-4-8` if the provider still advertises the
  dashed alias.
- `gpt_5_5_or_gpt_family`: verify the exact GPT-family alias at `/v1/models`
  before running; record the actual alias used.
- `deepseek_followup_slot`: replace the placeholder alias and endpoint with the
  user's DeepSeek configuration, then run the same prompt grid.

## Adding DeepSeek

1. Edit `benchmarks/model_ablation_v0.json`.
2. In `deepseek_followup_slot`, replace `deepseek-to-be-filled` with the exact
   provider model alias.
3. Set `auth_env` and `base_url_env` to the environment-variable names you will
   use locally.
4. Rebuild prompt packets so the prompt index records the concrete alias.
5. Set the DeepSeek environment variables locally and run:

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\run_report.json `
  --output-md results\model_ablation_prompts\v0\run_report.md `
  --model-id deepseek_followup_slot
```

The runner skips the DeepSeek slot only while the alias remains
`deepseek-to-be-filled`. Once a concrete alias is configured, it follows the
same availability check, response-save, and scoring path as Claude/GPT-family
slots.

## Evidence Boundary

The current repository contains prompt packets, runner/evaluator scripts, and
redacted availability reports. A model ablation is not complete until responses
are collected, scored with the same rubric, and provider/model aliases are
recorded without committing raw keys.
