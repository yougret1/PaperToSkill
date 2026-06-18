# Phase 26 Model-Ablation Endpoint Recheck

Date: 2026-06-18.

## Question

Has the user-provided OpenAI-compatible endpoint recovered enough to complete
the Claude Opus 4.8 and GPT-family model-ablation rows?

## Actions

- Re-ran the model-ablation live runner for:
  - `claude_opus_4_8`
  - `gpt_5_5_or_gpt_family`
- Used local environment variables for the provided endpoint and API key.
- Re-ran the saved-response evaluator after the live attempt.

## Results

- `/v1/models` succeeded for `https://coderxiaoc.com/v1`.
- The model catalog still lists eight Claude-family model IDs:
  `claude-fable-5`, `claude-haiku-4-5-20251001`,
  `claude-opus-4-5-20251101`, `claude-opus-4-6`,
  `claude-opus-4-7`, `claude-opus-4-8`,
  `claude-sonnet-4-5-20250929`, and `claude-sonnet-4-6`.
- Both Claude rows selected `claude-opus-4-8` exactly but failed with HTTP
  `503`, `No available accounts: no available accounts`.
- The catalog still does not list `gpt-5.5` or any GPT-family fallback model,
  so both GPT-family rows were skipped as unavailable.
- No response files were saved.
- Response evaluation remains `6` total rows, `0` scored rows, and `6` pending
  rows.

## Evidence Boundary

This phase records current provider/model availability evidence only. It does
not complete Claude/GPT-family model-quality ablations, does not evaluate
DeepSeek, and does not support negative model-quality conclusions.

## Commands

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
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
