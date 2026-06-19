# AI-Scientist-v2 Live LLM Smoke Report

Evidence boundary: this is a bounded LLM-client smoke check. It does not run BFTS or prove research-task success.

- Overall status: blocked_by_provider_or_model_availability
- Model: gpt-5.5
- Attempted models: gpt-5.5, gpt-5.4
- Base URL env: AI_SCIENTIST_OPENAI_BASE_URL
- Auth env: AI_SCIENTIST_OPENAI_API_KEY
- Ready checks: 3
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| ai_scientist_v2_root | ready | present | D:\a_work\gitee\ai-scientist-v2 |
| ai_scientist_v2_llm_response_saved | pending | response_chars=0 | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_llm_error | pending | gpt-5.5: Timed out after 60 seconds waiting for provider response; gpt-5.4: Timed out after 60 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_1 | ready | gpt-5.5: blocked; Timed out after 60 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_2 | ready | gpt-5.4: blocked; Timed out after 60 seconds waiting for provider response | provider/model availability |
