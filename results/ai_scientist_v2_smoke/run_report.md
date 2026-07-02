# AI-Scientist-v2 Live LLM Smoke Report

Evidence boundary: this is a bounded LLM-client smoke check. It does not run BFTS or prove research-task success.

- Overall status: complete
- Model: claude-opus-4-8
- Attempted models: claude-opus-4-8
- Base URL env: AI_SCIENTIST_OPENAI_BASE_URL
- Auth env: AI_SCIENTIST_OPENAI_API_KEY
- Max tokens override: 128
- Ready checks: 6
- Pending checks: 0
- Failed checks: 0

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| ai_scientist_v2_root | ready | present | D:\a_work\gitee\ai-scientist-v2 |
| ai_scientist_v2_llm_response_saved | ready | response_chars=143 | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_smoke_marker_papertoskill_smoke_ok | ready | present | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_smoke_marker_ai_scientist_v2 | ready | present | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_smoke_marker_paper_to_skill | ready | present | D:\a_work\gitee\PaperToSkill\results\ai_scientist_v2_smoke\response.md |
| ai_scientist_v2_llm_alias_attempt_1 | ready | claude-opus-4-8: success; response_chars=143 | provider/model availability |
