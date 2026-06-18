# Model Ablation Run Report

- Overall status: blocked_by_provider_or_model_availability
- Started at unix time: 1781788205
- Completed at unix time: 1781788209
- Successes: 0
- Errors: 2
- Skipped: 2

Evidence boundary: credentials are read from environment variables and errors are redacted. A model ablation is complete only for rows with saved response files and subsequent scoring.

| Model | Case | Status | Alias Used | Detail |
| --- | --- | --- | --- | --- |
| claude_opus_4_8 | toolformer_curated_skill_usage | error | claude-opus-4-8 | {"error": {"message": "No available accounts: no available accounts", "type": "api_error"}, "http_error": 503} |
| claude_opus_4_8 | aide_auto_skill_usage | error | claude-opus-4-8 | {"error": {"message": "No available accounts: no available accounts", "type": "api_error"}, "http_error": 503} |
| gpt_5_5_or_gpt_family | toolformer_curated_skill_usage | skipped |  | unavailable_gpt-5.5 |
| gpt_5_5_or_gpt_family | aide_auto_skill_usage | skipped |  | unavailable_gpt-5.5 |
