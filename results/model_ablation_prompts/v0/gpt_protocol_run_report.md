# Model Ablation Run Report

- Overall status: complete
- Started at unix time: 1782893121
- Completed at unix time: 1782893293
- Successes: 2
- Errors: 0
- Skipped: 0

Evidence boundary: credentials are read from environment variables and errors are redacted. A model ablation is complete only for rows with saved response files and subsequent scoring.

| Model | Case | Status | Alias Used | Detail |
| --- | --- | --- | --- | --- |
| gpt_5_5_or_gpt_family | toolformer_curated_skill_usage | success | gpt-5.5 | gpt-5.5=success |
| gpt_5_5_or_gpt_family | aide_auto_skill_usage | success | gpt-5.5 | gpt-5.5=success |
