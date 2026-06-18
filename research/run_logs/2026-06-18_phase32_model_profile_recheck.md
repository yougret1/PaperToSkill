# Phase 32 Run Log: Claude/GPT Credential Profile Recheck

## Decision Question

Do the newly supplied Claude and GPT-family credential profiles make the
Claude/GPT-family model-ablation rows executable?

## Actions

- Compacted `memory/long_term_memory.md` and `memory/short_term_memory.md` into
  shorter action-oriented memory files.
- Updated `benchmarks/model_ablation_v0.json` with:
  - Claude alias candidates: `claude-opus-4-8`, `claude-opus-4.8`,
    `claude-opus-4-7`, and `claude-opus-4-6`;
  - separate GPT env vars: `PAPERTOSKILL_GPT_OPENAI_BASE_URL` and
    `PAPERTOSKILL_GPT_OPENAI_API_KEY`;
  - GPT alias candidates: `gpt-5.5` and `gpt-5.4`.
- Updated prompt builder/runner behavior so prompt packets record alias
  candidates and run reports preserve multiple model catalogs for the same base
  URL when different credential env vars are used.
- Reran the Claude/GPT-family model-ablation live runner with shell-only
  environment variables.
- Reran the saved-response evaluator.

## Results

- Claude catalog through `AI_SCIENTIST_OPENAI_API_KEY`:
  - status: success;
  - model count: 8;
  - includes `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`.
- Claude chat completions:
  - both prompt rows selected `claude-opus-4-8`;
  - both failed HTTP 503 with `No available accounts: no available accounts`.
- GPT-family catalog through `PAPERTOSKILL_GPT_OPENAI_API_KEY`:
  - status: success;
  - model count: 17;
  - includes `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, GPT 5.2 variants, and GPT
    5.3 Codex variants.
- GPT-family chat completions:
  - both prompt rows selected `gpt-5.5`;
  - both failed HTTP 502 with
    `Upstream access forbidden, please contact administrator`.
- Response evaluation remains 6 total rows, 0 scored rows, and 6 pending rows.

## Evidence Boundary

This phase verifies that the separate GPT credential profile exposes GPT-family
model aliases, and it records current chat-completion blockers for Claude and
GPT-family rows. It does not complete model-quality ablations because no
response files were saved or scored.

## Verification

- `python scripts\build_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --output-dir results\model_ablation_prompts\v0`
- `python scripts\run_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\run_report.json --output-md results\model_ablation_prompts\v0\run_report.md --model-id claude_opus_4_8 --model-id gpt_5_5_or_gpt_family`
- `python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md`
