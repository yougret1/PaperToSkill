# 2026-07-05 Phase 114 Claude Direct Availability Recheck

## Action

- Rechecked Claude-family provider availability before deciding whether to
  spend real-reuse LLM-ablation calls on the six pending Claude-family rows.
- Loaded the Claude base URL and API key from the local Desktop API document
  into shell-only environment variables.
- Ran `scripts\run_openai_compatible_direct_probe.py` with Anthropic Messages,
  aliases `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`,
  `--timeout-seconds 120`, and `--max-tokens 16`.

## Result

- Overall status remained `blocked_by_provider_or_model_availability`.
- All three aliases returned provider HTTP 502.
- No response file was saved.
- `results/openai_compatible_direct_probe/claude_family/run_report.json` now
  carries the latest probe timestamp; the Markdown report content remains the
  same blocked-by-provider summary.

## Evidence Boundary

- This is provider availability metadata only.
- It is not model-quality evidence, not a real-reuse task failure, and not a
  reason to score the pending Claude-family rows as negative.
- The six Claude-family real-reuse LLM-ablation rows should remain pending
  until a lightweight direct probe succeeds.
