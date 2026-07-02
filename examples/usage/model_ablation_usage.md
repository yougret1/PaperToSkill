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

$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
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

- `claude_opus_4_8`: try the configured Claude alias candidates in order:
  `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
  `claude-opus-4-6`.
- `gpt_5_5_or_gpt_family`: use the separate GPT credential profile, verify the
  exact GPT-family alias at `/v1/models`, and prefer `gpt-5.5` then `gpt-5.4`
  when available; record the actual alias used.
- `deepseek_followup_slot`: currently configured as `deepseek-v4-flash` with
  both expected response files saved; refresh it with the same prompt grid if
  the DeepSeek alias or credential profile changes.

## Current DeepSeek Status

The current repository has the DeepSeek slot configured as
`deepseek-v4-flash`, with both expected response files saved and scored.
`check_deepseek_followup.py` reports `responses_present`. The steps below
remain the reuse path if the DeepSeek alias or credential profile changes
later.

## Adding Or Refreshing DeepSeek

Before editing the slot, inspect the local handoff/preflight report:

```powershell
python scripts\check_deepseek_followup.py --strict
```

The report is written to `results/deepseek_followup_handoff/handoff.md` and
lists the current alias status, the two DeepSeek prompt rows, expected response
paths, and the exact follow-up commands. A fresh unconfigured slot remains
`pending_user_configuration` while the alias is still `deepseek-to-be-filled`;
the current checked-in slot reports `responses_present` because both response
files are saved.

1. Configure only non-secret slot metadata. Do not put raw API keys in the
   benchmark file.

```powershell
python scripts\configure_deepseek_followup.py `
  --model-alias <deepseek-model-alias> `
  --auth-env DEEPSEEK_API_KEY `
  --base-url-env DEEPSEEK_BASE_URL
```

2. Rebuild prompt packets so the prompt index records the concrete alias.
3. Rerun `python scripts\check_deepseek_followup.py --strict`; the report
   should move from `pending_user_configuration` to `ready_to_run` until
   response files are saved.
4. Set the DeepSeek environment variables locally and run:

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\deepseek_run_report.json `
  --output-md results\model_ablation_prompts\v0\deepseek_run_report.md `
  --model-id deepseek_followup_slot
```

The runner skips the DeepSeek slot only while the alias remains
`deepseek-to-be-filled`. Once a concrete alias is configured, it follows the
same availability check, response-save, and scoring path as Claude/GPT-family
slots.

After a DeepSeek run, rerun the scorer and handoff check:

```powershell
python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md

python scripts\check_deepseek_followup.py --strict
```

## Evidence Boundary

The current repository contains prompt packets, runner/evaluator scripts,
DeepSeek handoff reports, redacted run reports, and 6/6 saved/scored rows for
the current model-ablation protocol. This is still saved-response scoring only;
it is not live downstream task success, provider billing, success per dollar,
or broad model-quality proof.
