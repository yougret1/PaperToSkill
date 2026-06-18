# Model Response Output-Token Proxy

Evidence boundary: this report measures saved model-ablation response files only. Token counts and costs are local output-token proxies, not provider bills, live invoices, or success-per-dollar evidence. Pending rows are missing response files, not negative model-quality evidence.

- Total rows: 6
- Measured rows: 4
- Pending rows: 2
- Character proxy output tokens: 9420
- Tokenizer output tokens: 8710
- Price proxy: `1.0` dollars per million output tokens
- Tokenizer: `o200k_base`

| Model ID | Case ID | Actual alias | Status | Words | Character proxy output tokens | Tokenizer output tokens | Estimated output cost proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude_opus_4_8 | toolformer_curated_skill_usage | claude-opus-4-8 | measured | 1356 | 2438 | 2272 | 0.002272 |
| claude_opus_4_8 | aide_auto_skill_usage | claude-opus-4-8 | measured | 1181 | 2184 | 2108 | 0.002108 |
| gpt_5_5_or_gpt_family | toolformer_curated_skill_usage | gpt-5.4 | measured | 982 | 1741 | 1447 | 0.001447 |
| gpt_5_5_or_gpt_family | aide_auto_skill_usage | gpt-5.5 | measured | 1599 | 3057 | 2883 | 0.002883 |
| deepseek_followup_slot | toolformer_curated_skill_usage |  | pending | 0 | 0 |  |  |
| deepseek_followup_slot | aide_auto_skill_usage |  | pending | 0 | 0 |  |  |
