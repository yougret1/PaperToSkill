# Phase 37: GPT-Family Model-Ablation Retry

Date: 2026-06-19

## Objective

Re-run the prepared PaperToSkill GPT-family model-ablation prompt rows with the
separate GPT credential profile, save any successful responses, and score the
saved responses with the same deterministic response rubric used for Claude.

## Commands

Environment variables were set only in the local shell and were not written to
tracked files.

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\gpt_retry_run_report.json `
  --output-md results\model_ablation_prompts\v0\gpt_retry_run_report.md `
  --model-id gpt_5_5_or_gpt_family `
  --max-tokens 900
```

```powershell
python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md
```

## Results

- The GPT-family `/v1/models` catalog request succeeded with the separate GPT
  credential profile and listed 17 models, including `gpt-5.5`, `gpt-5.4`,
  `gpt-5.4-mini`, GPT 5.2 variants, and GPT 5.3 Codex variants.
- `toolformer_curated_skill_usage`: `gpt-5.5` timed out, then `gpt-5.4`
  succeeded with HTTP 200 and saved
  `results/model_ablation_prompts/v0/responses/gpt_5_5_or_gpt_family__toolformer_curated_skill_usage.md`.
- `aide_auto_skill_usage`: `gpt-5.5` succeeded with HTTP 200 and saved
  `results/model_ablation_prompts/v0/responses/gpt_5_5_or_gpt_family__aide_auto_skill_usage.md`.
- The saved-response scorer now reports 6 total rows, 4 scored rows, 2 pending
  rows, and 1.0 average normalized score over scored rows.
- Both GPT-family response rows score 6/6 under the deterministic response
  rubric.

## Evidence Boundary

This completes the GPT-family portion of the current two-case PaperToSkill
model-ablation protocol. It should be described as a GPT-family result because
one row used `gpt-5.4` after a `gpt-5.5` timeout. It does not complete the
DeepSeek follow-up slot, live cross-harness execution, human-fidelity
annotation, provider billing, output-token accounting, or success-per-dollar
evidence.

