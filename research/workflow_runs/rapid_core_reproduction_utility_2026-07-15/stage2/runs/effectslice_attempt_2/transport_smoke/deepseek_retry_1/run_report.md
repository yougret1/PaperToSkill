# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: fail
- Wire API: openai_chat_completions
- Model: deepseek-v4-flash
- Attempted models: deepseek-v4-flash
- Base URL env: EFFECTSLICE_DEEPSEEK_BASE_URL
- Auth env: EFFECTSLICE_DEEPSEEK_API_KEY
- Max tokens: 256
- Timeout seconds: 60.0
- Ready checks: 4
- Pending checks: 0
- Failed checks: 2

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | EFFECTSLICE_DEEPSEEK_BASE_URL; EFFECTSLICE_DEEPSEEK_API_KEY |
| direct_probe_response_saved | ready | response_chars=46 | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\deepseek_retry_1\response.md |
| direct_probe_marker_papertoskill_smoke_ok | ready | present | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\deepseek_retry_1\response.md |
| direct_probe_marker_ai_scientist_v2 | fail | missing | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\deepseek_retry_1\response.md |
| direct_probe_marker_paper_to_skill | fail | missing | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\deepseek_retry_1\response.md |
| direct_probe_alias_attempt_1 | ready | deepseek-v4-flash: success; response_chars=46; http_status=200 | provider/model availability |
