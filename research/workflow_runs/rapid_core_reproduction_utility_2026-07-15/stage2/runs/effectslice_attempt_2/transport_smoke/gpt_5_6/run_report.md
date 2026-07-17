# Direct Provider Probe Report

Evidence boundary: this direct provider diagnostic bypasses `ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke or any BFTS/live research run.

- Overall status: complete
- Wire API: openai_responses
- Model: gpt-5.6
- Attempted models: gpt-5.6
- Base URL env: EFFECTSLICE_GPT_BASE_URL
- Auth env: EFFECTSLICE_GPT_API_KEY
- Max tokens: 256
- Timeout seconds: 60.0
- Ready checks: 6
- Pending checks: 0
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| direct_probe_configuration | ready | base_url_present=True; api_key_present=True | EFFECTSLICE_GPT_BASE_URL; EFFECTSLICE_GPT_API_KEY |
| direct_probe_response_saved | ready | response_chars=91 | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\gpt_5_6\response.md |
| direct_probe_marker_papertoskill_smoke_ok | ready | present | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\gpt_5_6\response.md |
| direct_probe_marker_ai_scientist_v2 | ready | present | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\gpt_5_6\response.md |
| direct_probe_marker_paper_to_skill | ready | present | research\workflow_runs\rapid_core_reproduction_utility_2026-07-15\stage2\runs\effectslice_attempt_2\transport_smoke\gpt_5_6\response.md |
| direct_probe_alias_attempt_1 | ready | gpt-5.6: success; response_chars=91; http_status=200 | provider/model availability |
