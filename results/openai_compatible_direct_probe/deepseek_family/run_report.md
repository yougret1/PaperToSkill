# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: complete
- Wire API: openai_chat_completions
- Model: deepseek-v4-flash
- Attempted models: deepseek-v4-flash
- Base URL env: PAPERTOSKILL_DEEPSEEK_BASE_URL
- Auth env: PAPERTOSKILL_DEEPSEEK_API_KEY
- Max tokens: 128
- Timeout seconds: 60.0
- Ready checks: 6
- Pending checks: 0
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | PAPERTOSKILL_DEEPSEEK_BASE_URL; PAPERTOSKILL_DEEPSEEK_API_KEY |
| direct_probe_response_saved | ready | response_chars=162 | results\openai_compatible_direct_probe\deepseek_family\response.md |
| direct_probe_marker_papertoskill_smoke_ok | ready | present | results\openai_compatible_direct_probe\deepseek_family\response.md |
| direct_probe_marker_ai_scientist_v2 | ready | present | results\openai_compatible_direct_probe\deepseek_family\response.md |
| direct_probe_marker_paper_to_skill | ready | present | results\openai_compatible_direct_probe\deepseek_family\response.md |
| direct_probe_alias_attempt_1 | ready | deepseek-v4-flash: success; response_chars=162; http_status=200 | provider/model availability |
