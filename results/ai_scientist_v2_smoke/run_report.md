# AI-Scientist-v2 Live LLM Smoke Report

Evidence boundary: this is a bounded LLM-client smoke check. It does not run BFTS or prove research-task success.

- Overall status: blocked_by_provider_or_model_availability
- Model: claude-opus-4-8
- Attempted models: claude-opus-4-8, claude-opus-4.8, claude-opus-4-7, claude-opus-4-6
- Base URL env: AI_SCIENTIST_OPENAI_BASE_URL
- Auth env: AI_SCIENTIST_OPENAI_API_KEY
- Max tokens override: 128
- Ready checks: 5
- Pending checks: 2
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| ai_scientist_v2_root | ready | present | D:\a_work\gitee\ai-scientist-v2 |
| ai_scientist_v2_llm_response_saved | pending | response_chars=0 | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_llm_error | pending | claude-opus-4-8: Timed out after 30 seconds waiting for provider response; claude-opus-4.8: Timed out after 30 seconds waiting for provider response; claude-opus-4-7: Timed out after 30 seconds waiting for provider response; claude-opus-4-6: Timed out after 30 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_1 | ready | claude-opus-4-8: blocked; Timed out after 30 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_2 | ready | claude-opus-4.8: blocked; Timed out after 30 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_3 | ready | claude-opus-4-7: blocked; Timed out after 30 seconds waiting for provider response | provider/model availability |
| ai_scientist_v2_llm_alias_attempt_4 | ready | claude-opus-4-6: blocked; Timed out after 30 seconds waiting for provider response | provider/model availability |
