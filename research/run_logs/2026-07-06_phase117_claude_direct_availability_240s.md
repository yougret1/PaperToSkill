# 2026-07-06 Phase 117 Claude Direct Availability Recheck

## Action

- Re-read the local Claude API document and loaded the Claude base URL and API
  key into shell-only environment variables.
- Ran the protocol-aware direct provider probe with Anthropic Messages, aliases
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`, `max_tokens=16`,
  and a longer 240-second request timeout.
- Command shape:

```powershell
python scripts\run_openai_compatible_direct_probe.py `
  --wire-api anthropic_messages `
  --model claude-opus-4-8 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6 `
  --base-url-env PAPERTOSKILL_CLAUDE_BASE_URL `
  --auth-env PAPERTOSKILL_CLAUDE_API_KEY `
  --timeout-seconds 240 `
  --max-tokens 16 `
  --response-output results\openai_compatible_direct_probe\claude_family\response.md `
  --output-json results\openai_compatible_direct_probe\claude_family\run_report.json `
  --output-md results\openai_compatible_direct_probe\claude_family\run_report.md `
  --strict
```

## Result

- Overall status remains `blocked_by_provider_or_model_availability`.
- All three Claude aliases returned provider HTTP 502.
- No response file was saved.
- The direct-probe report now records `timeout_seconds=240.0`,
  4 ready checks, 2 pending checks, and 0 failed checks.

## Evidence Boundary

- This is provider availability metadata only.
- It is not model-quality evidence, not a real-reuse task failure, and not
  scored Claude-family LLM-ablation evidence.
- Do not run the full six Claude-family real-reuse LLM-ablation rows until a
  small direct probe returns a usable response.
