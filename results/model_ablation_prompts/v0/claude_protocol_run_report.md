# Model Ablation Run Report

- Overall status: blocked_by_provider_or_model_availability
- Started at unix time: 1782902742
- Completed at unix time: 1782902900
- Successes: 0
- Errors: 2
- Skipped: 0
- Max attempts per alias: 5
- Retry delay seconds: 2.0

Evidence boundary: credentials are read from environment variables and errors are redacted. A model ablation is complete only for rows with saved response files and subsequent scoring.

| Model | Case | Status | Alias Used | Detail |
| --- | --- | --- | --- | --- |
| claude_opus_4_8 | toolformer_curated_skill_usage | error | claude-opus-4-6 | claude-opus-4-8=error; claude-opus-4-7=error; claude-opus-4-6=error |
| claude_opus_4_8 | aide_auto_skill_usage | error | claude-opus-4-6 | claude-opus-4-8=error; claude-opus-4-7=error; claude-opus-4-6=error |
