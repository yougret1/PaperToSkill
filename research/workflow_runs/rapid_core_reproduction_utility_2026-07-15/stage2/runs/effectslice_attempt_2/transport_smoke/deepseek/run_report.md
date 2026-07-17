# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: blocked_by_provider_or_model_availability
- Wire API: openai_chat_completions
- Model: deepseek-v4-flash
- Attempted models: deepseek-v4-flash
- Base URL env: EFFECTSLICE_DEEPSEEK_BASE_URL
- Auth env: EFFECTSLICE_DEEPSEEK_API_KEY
- Max tokens: 64
- Timeout seconds: 60.0
- Ready checks: 2
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | EFFECTSLICE_DEEPSEEK_BASE_URL; EFFECTSLICE_DEEPSEEK_API_KEY |
| direct_probe_response_saved | pending | response_chars=0 | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\deepseek\response.md |
| direct_probe_error | pending | deepseek-v4-flash: empty response content | provider/model availability |
| direct_probe_alias_attempt_1 | ready | deepseek-v4-flash: blocked; empty response content | provider/model availability |
