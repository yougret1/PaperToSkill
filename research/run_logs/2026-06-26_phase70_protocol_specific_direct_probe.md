# Phase 70: Protocol-Specific Direct Provider Probe

## Objective

Align the direct provider diagnostic with the current coderxiaoc API routing:
Claude-family requests use Anthropic Messages, while GPT-family requests use
OpenAI Responses. Keep the result diagnostic-only and do not promote
AI-Scientist-v2 smoke or live-run evidence unless a marker-contract response is
actually saved.

## Changes

- Confirmed local Claude Desktop / CC Switch routing from local configuration:
  `ANTHROPIC_BASE_URL=https://coderxiaoc.com`, bearer token auth, and Anthropic
  Messages request shape.
- Updated `scripts/run_openai_compatible_direct_probe.py` with `--wire-api`:
  `openai_chat_completions`, `openai_responses`, and `anthropic_messages`.
- Added Anthropic Messages request construction with
  `anthropic-version: 2023-06-01`.
- Added OpenAI Responses request construction with `input` and
  `max_output_tokens`.
- Updated direct-probe output extraction for Anthropic `content[].text` and
  Responses `output_text` / `output[].content[].text`.
- Updated external-evidence closure and packet commands to use the protocol-
  specific direct probes before wrapper smoke commands.
- Updated runbook and memory with the corrected protocol boundary.

## Direct Probe Commands

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

## Results

- Claude-family direct probe:
  - `wire_api=anthropic_messages`
  - attempted `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`
  - all attempts returned HTTP 502 `Upstream service temporarily unavailable`
  - no response file was produced
- GPT-family direct probe:
  - `wire_api=openai_responses`
  - attempted `gpt-5.5`, `gpt-5.4`
  - both attempts returned HTTP 502 `Upstream access forbidden`
  - no response file was produced

## Verification

```powershell
python -m unittest tests.test_run_openai_compatible_direct_probe tests.test_check_external_evidence_packets tests.test_check_external_evidence_closure tests.test_check_reproducibility_package -v
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Evidence Boundary

- This phase proves the direct diagnostic now uses the correct protocol family
  for Claude and GPT.
- It does not prove the provider can currently return a usable response.
- It does not complete AI-Scientist-v2 LLM-client smoke, full live/BFTS run,
  DeepSeek follow-up, human-fidelity annotation, provider billing, or AAAI
  submission readiness.
