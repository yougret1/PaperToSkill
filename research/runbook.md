# Runbook

## Memory Rule

After any context compaction or session resume, read:

1. `memory/long_term_memory.md`
2. `memory/short_term_memory.md`

Then update short-term memory with the current phase, blockers, and next action.

## AI-Scientist-v2 Environment

Recommended for stable runs:

```powershell
conda create -n papertoskill-ai-scientist python=3.11
conda activate papertoskill-ai-scientist
python -m pip install -r D:\a_work\gitee\ai-scientist-v2\requirements.txt
```

The current active Anaconda Python has been used for smoke work, but
`pip install -r requirements.txt` produced dependency conflicts. Use an isolated
environment before long experiments.

## LLM Endpoint

Use environment variables rather than tracked config files:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
```

Advertised model ID from `/v1/models`:

```text
claude-opus-4-8
```

The dotted spelling `claude-opus-4.8` was requested by the user, but the server
currently advertises the dashed spelling.

## Connectivity Smoke Test

```powershell
$headers = @{ Authorization = "Bearer $env:AI_SCIENTIST_OPENAI_API_KEY" }
Invoke-RestMethod `
  -Uri "$env:AI_SCIENTIST_OPENAI_BASE_URL/models" `
  -Method Get `
  -Headers $headers
```

Chat completion test:

```powershell
$body = @{
  model = "claude-opus-4-8"
  messages = @(@{ role = "user"; content = "Reply exactly: PaperToSkill API OK" })
  max_tokens = 20
  temperature = 0
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "$env:AI_SCIENTIST_OPENAI_BASE_URL/chat/completions" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

As of 2026-06-17, chat completion reached the server but failed due to exhausted
provider accounts.

## Model-Ablation Prompt Packets

From `D:\a_work\gitee\PaperToSkill`:

```powershell
python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0
```

The current prompt grid includes:

- `claude_opus_4_8`, using `claude-opus-4-8` if the provider still advertises
  the dashed alias;
- `gpt_5_5_or_gpt_family`, which must verify the exact GPT-family alias before
  running;
- `deepseek_followup_slot`, intentionally left for the user's later DeepSeek
  endpoint/model configuration.

Save live responses only under the `expected_response_path` fields in
`results/model_ablation_prompts/v0/index.json`. Do not commit raw API keys.

## AAAI Paper Package

The official AAAI-27 author kit is stored under `paper/aaai/`.

Main draft:

```powershell
cd D:\a_work\gitee\PaperToSkill\paper\aaai
pdflatex papertoskill_aaai2027.tex
bibtex papertoskill_aaai2027
pdflatex papertoskill_aaai2027.tex
pdflatex papertoskill_aaai2027.tex
```

If `pdflatex` is unavailable in the local environment, treat the `.tex` package
as prepared but not rendered.

## AI-Scientist-v2 Dry Run

From `D:\a_work\gitee\ai-scientist-v2`:

```powershell
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --dry_run `
  --skip_writeup `
  --skip_review
```

This should create an `experiments/<timestamp>_papertoskill_extractor_attempt_0`
folder and exit before running the expensive agentic search.
