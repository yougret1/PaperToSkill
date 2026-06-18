# Phase 39: Toolformer Live-Transfer Responses

Date: 2026-06-19

## Objective

Advance the pending live cross-harness evidence by adding live-transfer
response infrastructure and collecting the Toolformer response set with the
Claude-family endpoint.

## Commands

Run Toolformer live-transfer prompts with shell-only credentials:

```powershell
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
python scripts\run_live_transfer_prompts.py `
  --index results\live_transfer_prompts\toolformer_v0\index.json `
  --output-json results\live_transfer_prompts\toolformer_v0\run_report.json `
  --output-md results\live_transfer_prompts\toolformer_v0\run_report.md `
  --max-tokens 900
```

Score saved live-transfer responses:

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

- Added `scripts/run_live_transfer_prompts.py`, a live runner for existing
  Codex-style and Claude-style live-transfer prompt packets.
- Added `scripts/evaluate_live_transfer_responses.py`, a saved-response scorer
  that keeps missing response rows pending.
- Added `tests/test_live_transfer_execution.py`.
- `results/live_transfer_prompts/toolformer_v0/run_report.md` reports
  `overall_status=complete`, 6 successes, 0 errors, 0 skipped rows, catalog
  status `success`, 14 listed models, and exact alias `claude-opus-4-8`.
- Six Toolformer response files were saved under
  `results/live_transfer_prompts/toolformer_v0/responses/`.
- `results/live_transfer_prompts/evaluation.md` reports 24 total live-transfer
  rows, 6 scored Toolformer rows, 18 pending rows, and average normalized score
  1.0 over scored rows.

## Evidence Boundary

This phase completes only the Toolformer live-transfer response set for the
current prompt packet protocol. AI Scientist-v2, Reflexion, and AIDE
live-transfer response sets remain pending. The response scorer is a
deterministic output-contract check, not human semantic fidelity, provider
billing, or a broad live deployment success metric.

## Verification

- `python -m unittest tests.test_live_transfer_execution -v`: passed.
- `python scripts\evaluate_live_transfer_responses.py ...`: passed and wrote
  `results/live_transfer_prompts/evaluation.{json,md}`.
