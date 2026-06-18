# Phase 22 Model-Ablation Live Attempt Run Log

Date: 2026-06-18

Evidence boundary: this phase records executable live-attempt infrastructure and
provider/model availability evidence. It does not complete Claude/GPT/DeepSeek
model ablations because no response files were saved and no rows were scored.

## Commands

```powershell
python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md
```

The live attempt used local environment variables for the provided
OpenAI-compatible endpoint and key:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
python scripts\run_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\run_report.json --output-md results\model_ablation_prompts\v0\run_report.md --model-id claude_opus_4_8 --model-id gpt_5_5_or_gpt_family
```

## Results

- Runner added: `scripts/run_model_ablation_prompts.py`.
- Evaluator added: `scripts/evaluate_model_ablation_responses.py`.
- Unit tests added: `tests/test_model_ablation_execution.py`.
- Baseline evaluation report:
  - total rows: `6`
  - scored rows: `0`
  - pending rows: `6`
- Live-attempt report:
  - overall status: `blocked_by_provider_or_model_availability`
  - Claude rows: `2` errors
  - GPT-family rows: `2` skipped
  - successful responses: `0`

## Provider And Model Findings

- `/v1/models` succeeded for `https://coderxiaoc.com/v1`.
- The model catalog listed eight Claude-family model IDs, including
  `claude-opus-4-8`.
- Both `claude_opus_4_8` prompt calls selected `claude-opus-4-8` exactly but
  failed with HTTP `503`: `No available accounts: no available accounts`.
- The requested GPT slot `gpt_5_5_or_gpt_family` could not run because the
  model catalog did not list `gpt-5.5` or any GPT-family fallback model.
- The `deepseek_followup_slot` was not attempted; it remains reserved for the
  user's later DeepSeek configuration.

## Claim Impact

Phase 22 supports saying that PaperToSkill has a reusable model-ablation runner,
response evaluator, prompt grid, and redacted provider-availability report. It
also supports the narrow operational finding that the current endpoint lists a
Claude Opus 4.8 alias but cannot currently serve chat completions, and that the
same endpoint currently exposes no GPT-family model aliases. It does not
support completed model-ablation comparisons, live cross-harness success,
provider billing, or success-per-dollar claims.
