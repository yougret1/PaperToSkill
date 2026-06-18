# Runbook

## Memory Rule

After any context compaction or session resume, read:

1. `memory/long_term_memory.md`
2. `memory/short_term_memory.md`

Then update short-term memory with the current phase, blockers, and next action.

## Local Text-To-Skill Pipeline

Run the deterministic local pipeline from extracted paper text to note, skill,
source map, rubric evaluation, and manifest:

```powershell
python scripts\papertoskill_pipeline.py `
  --source papers\extracted\aide.txt `
  --output-dir results\pipeline_examples\aide_auto `
  --paper-id aide_auto `
  --title "AIDE: AI-Driven Exploration in the Space of Code" `
  --profile aide `
  --skill-name aide-auto-paper-skill `
  --rubric benchmarks\rubric_aide_v0.json
```

Evidence boundary: this command composes deterministic local scaffold steps. It
does not prove human semantic fidelity, live harness success, or reliable
arbitrary-PDF automation.

PDF input is supported when `pdftotext` is available on `PATH`; the manifest
records the generated extracted-text file:

```powershell
python scripts\papertoskill_pipeline.py `
  --source paper\aaai\papertoskill_aaai2027.pdf `
  --output-dir results\pipeline_examples\papertoskill_pdf `
  --paper-id papertoskill_pdf `
  --title "PaperToSkill" `
  --skill-name papertoskill-pdf-pipeline
```

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

$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
```

Previously advertised Claude model ID from `/v1/models`:

```text
claude-opus-4-8
```

The user also requested `claude-opus-4.8`, `claude-opus-4-7`, and
`claude-opus-4-6`. The GPT-family profile should be checked with the separate
`PAPERTOSKILL_GPT_*` environment variables and is expected by the user to list
aliases such as `gpt-5.5` and `gpt-5.4`.

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

Earlier chat completion checks reached the server but failed due to exhausted
provider accounts. Recheck with the current env profile before making any
availability claim.

## Model-Ablation Prompt Packets

From `D:\a_work\gitee\PaperToSkill`:

```powershell
python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0
```

The current prompt grid includes:

- `claude_opus_4_8`, trying candidate aliases `claude-opus-4-8`,
  `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6`;
- `gpt_5_5_or_gpt_family`, using the separate GPT credential profile and
  preferring `gpt-5.5` then `gpt-5.4` when listed;
- `deepseek_followup_slot`, intentionally left for the user's later DeepSeek
  endpoint/model configuration.

Save live responses only under the `expected_response_path` fields in
`results/model_ablation_prompts/v0/index.json`. Do not commit raw API keys.

Run Claude/GPT-family availability and response collection:

```powershell
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\run_report.json `
  --output-md results\model_ablation_prompts\v0\run_report.md `
  --model-id claude_opus_4_8 `
  --model-id gpt_5_5_or_gpt_family
```

Score any saved responses:

```powershell
python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md
```

Current Phase 36 status: the two Claude Opus 4.8 rows are saved and scored
6/6. The GPT-family rows still list `gpt-5.5` and `gpt-5.4`, but both aliases
return HTTP 502 upstream-access errors during chat completion.

For DeepSeek follow-up, edit `deepseek_followup_slot` in
`benchmarks/model_ablation_v0.json`, replacing `deepseek-to-be-filled` with the
real model alias and setting concrete `auth_env` / `base_url_env` names. Rebuild
the prompt packets, set those environment variables locally, and run the same
runner with `--model-id deepseek_followup_slot`. The runner skips DeepSeek only
while the placeholder alias remains unchanged.

## Usage Example Gate

Verify that paper-facing usage examples are locally executable where they do
not require live model calls:

```powershell
python scripts\check_usage_examples.py `
  --output-json results\reproducibility\usage_example_report.json `
  --output-md results\reproducibility\usage_example_report.md `
  --strict
```

This checker validates the Codex-style skill usage files, the model-ablation
prompt grid and response slots, an offline AIDE extracted-text-to-note-to-skill
chain, and a PDF-input pipeline smoke run in a temporary directory. It does not
execute Claude/GPT/DeepSeek calls or score model responses.

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

Verify the local AAAI package and generated PDF artifacts:

```powershell
python scripts\check_aaai_package.py `
  --output-json results\reproducibility\aaai_package_report.json `
  --output-md results\reproducibility\aaai_package_report.md `
  --strict
```

This checker verifies the author-kit SHA256, required package files, the
`aaai2027` style declaration/load marker, fresh PDF/log/bibliography artifacts,
and unresolved citation/reference/build-warning markers. Passing it does not
mean the paper is submission-final.

Verify that the AAAI result tables still match generated CSV result tables:

```powershell
python scripts\check_paper_tables.py `
  --output-json results\reproducibility\paper_table_report.json `
  --output-md results\reproducibility\paper_table_report.md `
  --strict
```

This checker compares `paper/aaai/papertoskill_tables.tex` against
`results/tables/main_results.csv`, `transfer_ablation.csv`,
`context_cost_proxy_tokenizer.csv`, and `auto_note_comparison.csv`. Passing it
prevents manuscript-table drift, but does not add new empirical evidence.

Verify that paper-facing text avoids unsupported overclaims and includes the
required evidence-boundary statements:

```powershell
python scripts\check_paper_claims.py `
  --output-json results\reproducibility\paper_claim_report.json `
  --output-md results\reproducibility\paper_claim_report.md `
  --strict
```

This checker scans the AAAI manuscript and Markdown draft, but not
`paper/claim_checklist.md` because that file intentionally stores unsupported
phrases as negative examples.

## Goal Completion Gate

Verify the active user goal against current local evidence before deciding
whether to close the goal:

```powershell
python scripts\check_goal_completion.py `
  --output-json results\reproducibility\goal_completion_report.json `
  --output-md results\reproducibility\goal_completion_report.md `
  --strict
```

This checker is expected to report
`not_complete_pending_external_evidence` until live Claude/GPT-family
responses, the DeepSeek follow-up response rows, human-fidelity annotation,
provider-billing or success-per-dollar evidence, and final AAAI submission
decisions are complete. Passing `--strict` only fails on local requirement
failures; pending external evidence remains pending rather than a package
failure.

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
