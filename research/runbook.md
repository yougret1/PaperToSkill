# Runbook

## Memory Rule

After any context compaction or session resume, read:

1. `memory/long_term_memory.md`
2. `memory/short_term_memory.md`

Then update short-term memory with the current phase, blockers, and next action.

## Phase Save And Push Recovery

Save phase-level progress to `origin/main` after verification when network
connectivity allows:

```powershell
git status -sb
git log -1 --oneline
git push origin main
```

If push fails with a GitHub HTTPS connectivity error, keep the local commit and
diagnose the transport separately from project correctness:

```powershell
git status -sb
git log -3 --oneline
git ls-remote --heads origin main
Test-NetConnection github.com -Port 443 | Format-List
```

Current Phase 64 status: `git push origin main` succeeded and saved the Phase
62/63 commits through `ad8346b Record GitHub push connectivity diagnostics` to
`origin/main`. A follow-up `git ls-remote --heads origin main` still failed
with `Recv failure: Connection was reset`, so treat GitHub HTTPS access as
intermittent. If future pushes fail, diagnose transport separately from project
correctness and keep local commits intact until the next successful push.

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

Use environment variables rather than tracked config files. Current
`coderxiaoc.com` routing is protocol-specific:

- Claude-family direct probes use Anthropic Messages at
  `https://coderxiaoc.com/v1/messages`.
- GPT-family direct probes use OpenAI Responses at
  `https://coderxiaoc.com/v1/responses`.
- The legacy AI-Scientist-v2 wrapper smoke still exercises the local
  `ai_scientist.llm` OpenAI-compatible client path, so keep its status separate
  from the protocol-specific direct probes.

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family token locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"

$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:PAPERTOSKILL_GPT_OPENAI_API_KEY = "<set locally>"
```

Current Claude Messages aliases:

```text
claude-opus-4-8
claude-opus-4-7
claude-opus-4-6
```

The dotted `claude-opus-4.8` spelling appeared in older attempts, but the
current direct-provider and handoff commands use the hyphenated model names
above. The GPT-family profile should be checked with the separate
`PAPERTOSKILL_GPT_*` environment variables and is expected by the user to use
aliases such as `gpt-5.5` and `gpt-5.4`.

## Connectivity Smoke Test

Claude Messages test:

```powershell
$headers = @{ Authorization = "Bearer $env:AI_SCIENTIST_OPENAI_API_KEY" }
$headers["anthropic-version"] = "2023-06-01"
$body = @{
  model = "claude-opus-4-8"
  messages = @(@{ role = "user"; content = "Reply exactly: PaperToSkill API OK" })
  max_tokens = 32
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "$env:AI_SCIENTIST_OPENAI_BASE_URL/v1/messages" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

GPT Responses test:

```powershell
$headers = @{ Authorization = "Bearer $env:PAPERTOSKILL_GPT_OPENAI_API_KEY" }
$body = @{
  model = "gpt-5.5"
  input = "Reply exactly: PaperToSkill API OK"
  max_output_tokens = 32
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "$env:PAPERTOSKILL_GPT_OPENAI_BASE_URL/responses" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Earlier OpenAI-compatible chat-completion checks reached the server but failed
due to exhausted or unavailable provider accounts. Recheck with the current
protocol-specific env profile before making any availability claim.

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

To try the known Claude alias variants in one bounded tiny-marker run:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family OpenAI-compatible key locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 30 --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
```

To try the GPT-family credential profile through the same AI-Scientist-v2
OpenAI-compatible client path, map the GPT key into
`AI_SCIENTIST_OPENAI_API_KEY` locally for this smoke only:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set GPT-family key locally>"
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE = "1"
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4
```

Current AI-Scientist-v2 smoke status:
`results/ai_scientist_v2_smoke/run_report.md` reports
`overall_status=blocked_by_provider_or_model_availability`, `max_tokens=128`,
5 ready checks, 2 pending checks, and 0 failed checks. The latest capped
Claude-family retry used the older OpenAI-compatible wrapper path and timed out
for its alias set; no response file was produced. The immediately preceding
capped GPT-family retry tried `gpt-5.5` and `gpt-5.4`; both timed out after 45
seconds. This is bounded client-availability smoke evidence, not a BFTS run or
live research-task success.

## Protocol-Specific Direct Provider Probe

If the AI-Scientist-v2 smoke remains blocked, run the direct endpoint probe to
distinguish provider availability from the local `ai_scientist.llm` wrapper:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set Claude-family token locally>"
python scripts\run_openai_compatible_direct_probe.py --wire-api anthropic_messages --strict --require-complete --timeout-seconds 30 --max-tokens 128 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6 `
  --output-json results\openai_compatible_direct_probe\claude_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\claude_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\claude_family\response.md
```

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set GPT-family key locally>"
python scripts\run_openai_compatible_direct_probe.py --wire-api openai_responses --strict --require-complete --timeout-seconds 60 --max-tokens 128 `
  --model-alias gpt-5.5 `
  --model-alias gpt-5.4 `
  --output-json results\openai_compatible_direct_probe\gpt_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\gpt_family\run_report.md `
  --response-output results\openai_compatible_direct_probe\gpt_family\response.md
```

Current Phase 70 direct-probe status:
`results/openai_compatible_direct_probe/claude_family/run_report.md` reports
`wire_api=anthropic_messages`, attempted `claude-opus-4-8`,
`claude-opus-4-7`, and `claude-opus-4-6`, and is still blocked by HTTP 502
`Upstream service temporarily unavailable`. The GPT-family report uses
`wire_api=openai_responses`, attempted `gpt-5.5` and `gpt-5.4`, and is still
blocked by HTTP 502 `Upstream access forbidden`. This diagnostic bypasses
`ai_scientist.llm`, so it clarifies the provider blocker but does not complete
the AI-Scientist-v2 smoke or any BFTS/live research run.

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

Current status: the current two-case model-ablation protocol has 6/6 saved and
scored rows. GPT-family was refreshed through OpenAI Responses and completed
both rows with `gpt-5.5`; DeepSeek was run through Chat Completions and
completed both rows with `deepseek-v4-flash`. The latest Claude protocol
refresh used Anthropic Messages but was blocked by provider HTTP 502, so the
scored Claude rows come from previously saved response files. Local output-token
proxy accounting over all six saved responses reports 9,594 `o200k_base`
output tokens. This report is not provider billing, live downstream task
success, broad model-quality evidence, or success-per-dollar evidence.

Current Paper2Agent comparison status:
`results/tables/paper2agent_artifact_comparison.md` reports 7/7 ready criteria
and 0 failed criteria for a bounded source-backed artifact/workflow comparison.
It compares Paper2Agent's reported MCP workflow with current PaperToSkill
artifacts. It does not run Paper2Agent, deploy an MCP server, or claim
end-to-end baseline performance.

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

For DeepSeek follow-up, configure `deepseek_followup_slot` with the helper
script so only non-secret metadata is written to
`benchmarks/model_ablation_v0.json`:

```powershell
python scripts\configure_deepseek_followup.py `
  --model-alias <deepseek-model-alias> `
  --auth-env DEEPSEEK_API_KEY `
  --base-url-env DEEPSEEK_BASE_URL
```

Then rebuild the prompt packets, set those environment variables locally, and
run the same runner with `--model-id deepseek_followup_slot`. The runner skips
DeepSeek only while the placeholder alias remains unchanged.

Before and after editing the DeepSeek slot, generate the local handoff/preflight
report:

```powershell
python scripts\check_deepseek_followup.py --strict
```

Current status:
`results/deepseek_followup_handoff/handoff.md` reports `responses_present`, 7
ready checks, 0 pending checks, and 0 failed checks. The checked-in DeepSeek
slot uses `deepseek-v4-flash`, both expected response files exist, and the
saved-response evaluator scores both rows 6/6. Keep this separate from
provider billing and live downstream task success.

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

Current status:
`results/reproducibility/submission_review_report.md` reports ready, 15 ready
checks, and 0 failed checks. It verifies that review handoff files describe the
24 scored saved live-transfer response rows, 6 scored and 0 pending
model-ablation rows, 0 scored and 24 pending human-fidelity rows, local token
accounting, and the bounded AI-Scientist-v2 smoke/full live-run completion.
Passing this gate does not mean the AAAI paper is submission-final.

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
`not_complete_pending_external_evidence` until human-fidelity annotation and
final AAAI submission readiness under the recorded wait policy are complete.
Passing `--strict` only fails on local requirement
failures; pending external evidence remains pending rather than a package
failure.

## External Evidence Closure Queue

Build the local closure queue that maps pending goal requirements to concrete
next actions:

```powershell
python scripts\check_external_evidence_closure.py --strict
```

Current status:
`results/external_evidence_closure/closure.md` reports
`overall_status=pending_external_evidence`, 3 ready checks, 0 pending checks,
and 0 failed checks. The queue covers human-fidelity annotation and the AAAI
submission decision.

This queue is a local planning and checking artifact. It does not complete any
of the external evidence items.

## External Evidence Execution Packets

Build executable handoff packets for each item in the external-evidence closure
queue:

```powershell
python scripts\check_external_evidence_packets.py --strict
```

Current status:
`results/external_evidence_packets/packets.md` reports
`overall_status=ready`, 7 ready checks, 0 pending checks, and 0 failed checks.
The two packets cover human-fidelity annotation and the AAAI submission
decision.

These packets list inputs, setup notes, run commands, validation commands,
completion criteria, escalation rules, and evidence boundaries. They do not
complete any external evidence by themselves.

The AAAI submission-decision packet now routes final-decision recording through
`scripts/generate_aaai_submission_decision.py`. After the human research lead
chooses exactly one option, run only the matching helper command, then rerun
`scripts/check_aaai_submission_decision.py --strict`,
`scripts/check_goal_completion.py --strict`, and
`scripts/check_reproducibility_package.py --strict`.

## AAAI Submission Decision Preflight

Build the local preflight for the final AAAI decision:

```powershell
python scripts\check_aaai_submission_decision.py --strict
```

Current Phase 55 status:
`results/aaai_submission_decision/decision.md` reports
`overall_status=pending_human_decision`, 26 ready checks, 1 pending check, and
0 failed checks. It exposes two options for the research lead:

- submit now as a deterministic/offline system paper with explicit limitations;
- wait for external evidence before making stronger live, human-fidelity,
  provider-economics, or AI-Scientist-v2 live-run claims.

The preflight does not select an option. Record a human decision only by adding
`research/aaai_submission_decision.md` with a selected option, decision owner,
decision date, claim boundary, and evidence policy.

Prefer the validated helper when the research lead has made the decision:

```powershell
python scripts\generate_aaai_submission_decision.py `
  --selected-option submit_now_deterministic_offline `
  --decision-owner "<name or role>" `
  --decision-date YYYY-MM-DD `
  --claim-boundary "<accepted paper claim scope>" `
  --evidence-policy "<submit now with limitations, or wait for named evidence>"
python scripts\check_aaai_submission_decision.py --strict
```

Use `--selected-option wait_for_external_evidence` instead if the accepted
policy is to wait for the named external evidence rows. Do not run either
command until the human research lead has selected a policy.

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

## AI-Scientist-v2 Full Live-Run Handoff

Before attempting the full live/BFTS run, generate the local handoff/preflight
report:

```powershell
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
```

Current Phase 76 status:
`results/ai_scientist_v2_live_run_handoff/handoff.md` reports
`complete`, 16 ready checks, 0 pending checks, 0 failed checks, and one
completion directory. It checks the AI-Scientist-v2 root, launcher, dry-run/skip
flags, laptop-profile config, PaperToSkill seed idea, prior dry-run artifacts,
environment variable names, the smoke-completion evidence, completion artifacts,
and non-buggy best-node consistency.

The completed run is bounded integration and synthetic sensitivity evidence. Do
not treat it as human fidelity, real-data validation, or broad live research
task success.
