# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: blocked_by_provider_or_model_availability
- Wire API: anthropic_messages
- Model: claude-opus-4-8
- Attempted models: claude-opus-4-8, claude-opus-4-7, claude-opus-4-6
- Base URL env: PAPERTOSKILL_CLAUDE_BASE_URL
- Auth env: PAPERTOSKILL_CLAUDE_API_KEY
- Max tokens: 128
- Timeout seconds: 60.0
- Ready checks: 4
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | PAPERTOSKILL_CLAUDE_BASE_URL; PAPERTOSKILL_CLAUDE_API_KEY |
| direct_probe_response_saved | pending | response_chars=0 | results\openai_compatible_direct_probe\claude_family\response.md |
| direct_probe_error | pending | claude-opus-4-8: {"raw_body": "error code: 502\n", "http_error": 502}; claude-opus-4-7: {"raw_body": "error code: 502\n", "http_error": 502}; claude-opus-4-6: {"raw_body": "error code: 502\n", "http_error": 502} | provider/model availability |
| direct_probe_alias_attempt_1 | ready | claude-opus-4-8: blocked; {"raw_body": "error code: 502\n", "http_error": 502} | provider/model availability |
| direct_probe_alias_attempt_2 | ready | claude-opus-4-7: blocked; {"raw_body": "error code: 502\n", "http_error": 502} | provider/model availability |
| direct_probe_alias_attempt_3 | ready | claude-opus-4-6: blocked; {"raw_body": "error code: 502\n", "http_error": 502} | provider/model availability |
