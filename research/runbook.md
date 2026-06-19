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

## AI-Scientist-v2 LLM-Client Smoke

From `D:\a_work\gitee\PaperToSkill`, run a bounded one-call smoke through the
local AI-Scientist-v2 LLM client:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

python scripts\run_ai_scientist_v2_smoke.py --strict
```

The command prints the generated report paths plus an `overall_status`
summary. Use `--require-complete` when a CI or handoff step should exit
non-zero unless the provider returns a response satisfying the smoke contract:

```powershell
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete
```

To try the known Claude alias variants in one bounded run:

```powershell
python scripts\run_ai_scientist_v2_smoke.py --strict --timeout-seconds 15 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

Current Phase 46 status:
`results/ai_scientist_v2_smoke/run_report.md` reports
`overall_status=blocked_by_provider_or_model_availability`, 5 ready checks, 2
pending checks, and 0 failed checks. The latest recheck tried
`claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and
`claude-opus-4-6`; all four aliases timed out after 15 seconds waiting for
provider response, so no response file was produced. This is a bounded
client-availability smoke attempt, not a BFTS run or live research-task
success.

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

Estimate local output-token proxies for saved model responses:

```powershell
python scripts\evaluate_model_response_costs.py
```

Current Phase 37 status: the two Claude Opus 4.8 rows and the two GPT-family
rows are saved and scored 6/6 for the current prompt protocol. In the latest
GPT-family retry, the Toolformer row timed out on `gpt-5.5` and succeeded with
`gpt-5.4`; the AIDE row succeeded with `gpt-5.5`. Record this as a
GPT-family result, not a pure `gpt-5.5` result. Phase 38 adds local output-token
proxy accounting over these four saved Claude/GPT-family responses: 8,710
`o200k_base` output tokens, with two DeepSeek rows still pending. This report is
not provider billing or success-per-dollar evidence.

## Provider Billing Evidence Handoff

Prepare or refresh the blank provider-billing evidence template and pending
summary:

```powershell
python scripts\summarize_provider_billing_evidence.py --init-template --strict
```

When real provider usage exports or invoices are available, fill
`results/provider_billing_evidence/billing_template.csv` and rerun:

```powershell
python scripts\summarize_provider_billing_evidence.py --strict
```

Current Phase 43 status:
`results/provider_billing_evidence/billing_summary.md` reports
`billing_status=pending`, 6 total rows, 0 measured rows, 6 pending rows, 0
errors, total billed USD 0, and success per dollar `n/a`. This is an auditable
handoff for future real billing rows, not provider billing evidence.

For DeepSeek follow-up, edit `deepseek_followup_slot` in
`benchmarks/model_ablation_v0.json`, replacing `deepseek-to-be-filled` with the
real model alias and setting concrete `auth_env` / `base_url_env` names. Rebuild
the prompt packets, set those environment variables locally, and run the same
runner with `--model-id deepseek_followup_slot`. The runner skips DeepSeek only
while the placeholder alias remains unchanged.

Before and after editing the DeepSeek slot, generate the local handoff/preflight
report:

```powershell
python scripts\check_deepseek_followup.py --strict
```

Current Phase 47 status:
`results/deepseek_followup_handoff/handoff.md` reports
`pending_user_configuration`, 5 ready checks, 2 pending checks, and 0 failed
checks. This report lists the two DeepSeek prompt rows, expected response paths,
and next commands. It does not call DeepSeek or complete the DeepSeek ablation.

## Live-Transfer Response Collection

Existing live-transfer prompt packets live under
`results/live_transfer_prompts/*_v0/index.json`. Save responses only under each
row's `expected_response_path`. Do not commit raw API keys.

Run one live-transfer packet with the Claude-family profile:

```powershell
python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\toolformer_v0\run_report.json `
  --output-md results\live_transfer_prompts\toolformer_v0\run_report.md `
  --max-tokens 900
```

Repeat the same command for the other paper packet indexes and output paths:

```powershell
python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\ai_scientist_v2_v0\index.json `
  --output-json results\live_transfer_prompts\ai_scientist_v2_v0\run_report.json `
  --output-md results\live_transfer_prompts\ai_scientist_v2_v0\run_report.md `
  --max-tokens 900

python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\reflexion_v0\index.json `
  --output-json results\live_transfer_prompts\reflexion_v0\run_report.json `
  --output-md results\live_transfer_prompts\reflexion_v0\run_report.md `
  --max-tokens 900

python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\aide_v0\index.json `
  --output-json results\live_transfer_prompts\aide_v0\run_report.json `
  --output-md results\live_transfer_prompts\aide_v0\run_report.md `
  --max-tokens 900
```

Score saved live-transfer responses across all four paper packets:

```powershell
python scripts\evaluate_live_transfer_responses.py `
  --index results\live_transfer_prompts\ai_scientist_v2_v0\index.json `
  --index results\live_transfer_prompts\reflexion_v0\index.json `
  --index results\live_transfer_prompts\aide_v0\index.json `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\evaluation.json `
  --output-md results\live_transfer_prompts\evaluation.md
```

Current live-transfer status: all four live-transfer response sets have saved
responses across both harness prompt styles and all three context variants.
`results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24 scored
rows, 0 pending rows, and average normalized score 1.0 under deterministic
output-contract scoring. AI Scientist-v2, Reflexion, and AIDE rows score 11/11;
Toolformer rows score 9/9. AIDE has one provider fallback row:
`claude-opus-4-8` closed the connection, then `claude-opus-4-7` succeeded. This
is saved-response evidence, not human semantic fidelity, real live task success,
provider billing, or DeepSeek completion.

## Usage Example Gate

Verify that paper-facing usage examples are locally executable where they do
not require additional live model calls:

```powershell
python scripts\check_usage_examples.py `
  --output-json results\reproducibility\usage_example_report.json `
  --output-md results\reproducibility\usage_example_report.md `
  --strict
```

This checker validates the Codex-style skill usage files, the scored Toolformer
Codex-style response slot, the full live-transfer response evaluation, the
model-ablation prompt grid and response slots, an offline AIDE
extracted-text-to-note-to-skill chain, and a PDF-input pipeline
smoke run in a temporary directory. It does not execute additional
Claude/GPT/DeepSeek calls.

## Human-Fidelity Annotation Handoff

Regenerate the independent-review packets, annotation guide, and blank
annotation template:

```powershell
python scripts\build_human_fidelity_packets.py
```

Before using reviewer-filled annotations in a claim, summarize them with strict
validation:

```powershell
python scripts\summarize_human_fidelity_annotations.py --strict
```

Current Phase 42 status:
`results/human_fidelity_packets/annotation_guide.md` provides the reviewer
handoff, `annotation_template.csv` has 24 blank paper-by-criterion rows, and
`annotation_summary.md` reports `annotation_status=pending`, 0 scored rows, 24
pending rows, average confidence `n/a`, and 0 validation errors. The package
gate marks `human_fidelity_annotation_handoff_ready` ready, while completed
human-fidelity annotation remains pending.

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

## Submission-Review Handoff Gate

Verify that internal review, rebuttal, and submission checklist handoff files
match current evidence rather than stale earlier-phase status:

```powershell
python scripts\check_submission_review.py `
  --output-json results\reproducibility\submission_review_report.json `
  --output-md results\reproducibility\submission_review_report.md `
  --strict
```

Current Phase 44 status:
`results/reproducibility/submission_review_report.md` reports ready, 15 ready
checks, and 0 failed checks. It verifies that review handoff files describe the
24 scored saved live-transfer response rows, 4 scored and 2 pending
model-ablation rows, 0 scored and 24 pending human-fidelity rows, 0 measured
and 6 pending provider-billing rows, and the current AI-Scientist-v2 smoke
blocker. Passing this gate does not mean the AAAI paper is submission-final.

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
`not_complete_pending_external_evidence` until the AI-Scientist-v2 LLM-client
smoke can complete, the full AI-Scientist-v2 live run decision is resolved, the
DeepSeek follow-up response rows, human-fidelity annotation, provider-billing or
success-per-dollar evidence, and final AAAI submission decisions are complete.
Passing `--strict` only fails on local requirement
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
