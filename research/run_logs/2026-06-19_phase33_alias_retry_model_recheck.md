# Phase 33 Run Log: Alias-Retry Model Recheck

## Decision Question

Can the Claude/GPT-family model-ablation runner recover when the first listed
model alias is advertised but unavailable at chat-completion time?

## Actions

- Updated `scripts/run_model_ablation_prompts.py` so each prompt row can try
  every listed candidate alias that appears in the provider model catalog.
- Added a regression test in `tests/test_model_ablation_execution.py` for the
  case where the first Claude alias fails but the next alias succeeds.
- Reran the Claude/GPT-family model-ablation live runner with shell-only
  environment variables.
- Reran `scripts/evaluate_model_ablation_responses.py`.
- Updated the goal-completion gate so "ablation attempted" means the runner has
  provider/model attempt evidence, not that the first alias succeeded.

## Results

- Claude catalog through `AI_SCIENTIST_OPENAI_API_KEY` still lists 8
  Claude-family models, including `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- For both Claude prompt rows, the runner tried:
  - `claude-opus-4-8`: HTTP 503, `No available accounts`;
  - `claude-opus-4-7`: HTTP 503, `No available accounts`;
  - `claude-opus-4-6`: HTTP 503, `No available accounts`.
- GPT-family catalog through `PAPERTOSKILL_GPT_OPENAI_API_KEY` still lists 17
  models, including `gpt-5.5`, `gpt-5.4`, and `gpt-5.4-mini`.
- For both GPT prompt rows, the runner tried:
  - `gpt-5.5`: HTTP 502, `Upstream access forbidden`;
  - `gpt-5.4`: HTTP 502, `Upstream access forbidden`.
- No response files were saved.
- Response evaluation remains 6 total rows, 0 scored rows, and 6 pending rows.

## Evidence Boundary

This phase improves the live-run protocol and records stronger provider/model
availability evidence. It does not complete model-quality ablations because no
Claude/GPT-family response files were saved or scored.

## Verification

- `python -m unittest tests.test_model_ablation_execution -v`
- `python scripts\run_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\run_report.json --output-md results\model_ablation_prompts\v0\run_report.md --model-id claude_opus_4_8 --model-id gpt_5_5_or_gpt_family`
- `python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md`
