# Phase 40: All Live-Transfer Saved Responses

## Objective

Complete the remaining saved-response coverage for the current live-transfer
prompt-packet protocol by collecting AI Scientist-v2, Reflexion, and AIDE
responses with the Claude-family OpenAI-compatible profile, then rescore all
four paper packets.

## Commands

Run each remaining live-transfer packet with shell-only credentials:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL = "https://coderxiaoc.com/v1"
$env:AI_SCIENTIST_OPENAI_API_KEY = "<set locally>"

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

Rescore all four paper packets:

```powershell
python scripts\evaluate_live_transfer_responses.py `
  --index results\live_transfer_prompts\ai_scientist_v2_v0\index.json `
  --index results\live_transfer_prompts\reflexion_v0\index.json `
  --index results\live_transfer_prompts\aide_v0\index.json `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\evaluation.json `
  --output-md results\live_transfer_prompts\evaluation.md
```

## Results

- AI Scientist-v2 run report: `overall_status=complete`, 6 successes, 0 errors,
  0 skipped rows; all rows used `claude-opus-4-8`.
- Reflexion run report: `overall_status=complete`, 6 successes, 0 errors,
  0 skipped rows; all rows used `claude-opus-4-8`.
- AIDE run report: `overall_status=complete`, 6 successes, 0 errors, 0 skipped
  rows. The first row tried `claude-opus-4-8`, received a remote connection
  closure, and then succeeded with `claude-opus-4-7`; the remaining rows used
  `claude-opus-4-8`.
- The aggregate saved-response evaluator reports 24 total rows, 24 scored rows,
  0 pending rows, and average normalized score 1.0.
- AI Scientist-v2, Reflexion, and AIDE rows score 11/11 each; Toolformer rows
  remain 9/9 each.

## Evidence Boundary

This phase completes saved live-transfer response coverage and deterministic
output-contract scoring for the current prompt-packet protocol. It does not
claim human semantic fidelity, real live task success, provider billing,
DeepSeek completion, or final AAAI submission readiness.
