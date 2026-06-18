# Phase 36 Run Log: Claude Ablation Success, GPT Still Blocked

## Decision Question

Can the prepared Claude Opus 4.8 and GPT-family model-ablation prompts produce
saved, scored responses through the user-provided OpenAI-compatible endpoint?

## Actions

- Set the Claude and GPT-family API keys only as local PowerShell environment
  variables for the runner process.
- Ran `scripts/run_model_ablation_prompts.py` for:
  - `claude_opus_4_8`
  - `gpt_5_5_or_gpt_family`
- Ran `scripts/evaluate_model_ablation_responses.py` over the saved response
  slots.
- Updated the machine-checkable package and goal gates so Claude completion is
  recognized separately from the still-pending GPT-family and DeepSeek rows.

## Results

- Claude catalog succeeded and listed 14 Claude-family models, including
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`.
- Claude Opus 4.8 completed both prompt rows with HTTP 200:
  - `toolformer_curated_skill_usage`
  - `aide_auto_skill_usage`
- The two Claude response files were saved under
  `results/model_ablation_prompts/v0/responses/`.
- Response evaluation now reports 6 total rows, 2 scored rows, 4 pending rows,
  and average normalized score 1.0 over scored rows.
- Both Claude rows score 6/6 under the saved-response scorer.
- GPT catalog still succeeded and listed `gpt-5.5`, `gpt-5.4`, and other
  GPT-family aliases.
- Both GPT prompt rows still failed at chat completion: `gpt-5.5` and
  `gpt-5.4` returned HTTP 502 `Upstream access forbidden`.
- DeepSeek remains pending user configuration.

## Evidence Boundary

This phase supports completed, saved, and scored Claude Opus 4.8 prompt-row
evidence for the current model-ablation protocol. It does not complete the
GPT-family ablation, the DeepSeek follow-up, live cross-harness execution,
human fidelity annotation, provider billing, or success-per-dollar evidence.

## Verification

- `python scripts\run_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\run_report.json --output-md results\model_ablation_prompts\v0\run_report.md --model-id claude_opus_4_8 --model-id gpt_5_5_or_gpt_family`
- `python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md`
