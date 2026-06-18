# Model Ablation Run Report

- Overall status: partial
- Started at unix time: 1781804424
- Completed at unix time: 1781804544
- Successes: 2
- Errors: 2
- Skipped: 0

Evidence boundary: credentials are read from environment variables and errors are redacted. A model ablation is complete only for rows with saved response files and subsequent scoring.

| Model | Case | Status | Alias Used | Detail |
| --- | --- | --- | --- | --- |
| claude_opus_4_8 | toolformer_curated_skill_usage | success | claude-opus-4-8 | claude-opus-4-8=success |
| claude_opus_4_8 | aide_auto_skill_usage | success | claude-opus-4-8 | claude-opus-4-8=success |
| gpt_5_5_or_gpt_family | toolformer_curated_skill_usage | error | gpt-5.4 | gpt-5.5=error; gpt-5.4=error |
| gpt_5_5_or_gpt_family | aide_auto_skill_usage | error | gpt-5.4 | gpt-5.5=error; gpt-5.4=error |
