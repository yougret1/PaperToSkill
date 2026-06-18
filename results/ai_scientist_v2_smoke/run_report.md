# AI-Scientist-v2 Live LLM Smoke Report

Evidence boundary: this is a bounded LLM-client smoke check. It does not run BFTS or prove research-task success.

- Overall status: blocked_by_provider_or_model_availability
- Model: claude-opus-4-8
- Base URL env: AI_SCIENTIST_OPENAI_BASE_URL
- Auth env: AI_SCIENTIST_OPENAI_API_KEY
- Ready checks: 1
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| ai_scientist_v2_root | ready | present | D:\a_work\gitee\ai-scientist-v2 |
| ai_scientist_v2_llm_response_saved | pending | response_chars=0 | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_llm_error | pending | Error code: 403 - {'error': {'message': 'All available accounts exhausted', 'type': 'server_error'}} | provider/model availability |
