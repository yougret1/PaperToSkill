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

## Current Model Slots

- `claude_opus_4_8`: use `claude-opus-4-8` if the provider still advertises the
  dashed alias.
- `gpt_5_5_or_gpt_family`: verify the exact GPT-family alias at `/v1/models`
  before running; record the actual alias used.
- `deepseek_followup_slot`: replace the placeholder alias and endpoint with the
  user's DeepSeek configuration, then run the same prompt grid.

## Evidence Boundary

The current repository contains prompt packets only. A model ablation is not
complete until responses are collected, scored with the same rubric, and
provider/model aliases are recorded without committing raw keys.
