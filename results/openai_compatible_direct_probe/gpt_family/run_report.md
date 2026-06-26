# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: blocked_by_provider_or_model_availability
- Wire API: openai_responses
- Model: gpt-5.5
- Attempted models: gpt-5.5, gpt-5.4
- Base URL env: AI_SCIENTIST_OPENAI_BASE_URL
- Auth env: AI_SCIENTIST_OPENAI_API_KEY
- Max tokens: 128
- Timeout seconds: 60.0
- Ready checks: 3
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | AI_SCIENTIST_OPENAI_BASE_URL; AI_SCIENTIST_OPENAI_API_KEY |
| direct_probe_response_saved | pending | response_chars=0 | results\openai_compatible_direct_probe\gpt_family\response.md |
| direct_probe_error | pending | gpt-5.5: {"error": {"message": "Upstream access forbidden, please contact administrator", "type": "upstream_error"}, "http_error": 502}; gpt-5.4: {"error": {"message": "Upstream access forbidden, please contact administrator", "type": "upstream_error"}, "http_error": 502} | provider/model availability |
| direct_probe_alias_attempt_1 | ready | gpt-5.5: blocked; {"error": {"message": "Upstream access forbidden, please contact administrator", "type": "upstream_error"}, "http_error": 502} | provider/model availability |
| direct_probe_alias_attempt_2 | ready | gpt-5.4: blocked; {"error": {"message": "Upstream access forbidden, please contact administrator", "type": "upstream_error"}, "http_error": 502} | provider/model availability |
