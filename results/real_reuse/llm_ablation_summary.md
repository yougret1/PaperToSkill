# Real-Reuse LLM Ablation Summary

Evidence boundary: Aggregates only rows whose run_id was pre-registered in the real-reuse LLM ablation plan. Pending rows are not negative evidence.

- Expected rows: 18

- Collected rows: 12

- Pending rows: 6

## Pair Status

| Task ID | Family | Alias | Summary | PaperToSkill | Status |
| --- | --- | --- | --- | --- | --- |
| AIDE-T2 | GPT-family | gpt-5.5 | 0.814 | 0.000 | complete |
| AIDE-T2 | Claude-family | claude-opus-4-8 |  |  | pending |
| AIDE-T2 | DeepSeek-family | deepseek-v4-flash | 0.500 | 0.500 | complete |
| SWE-T2 | GPT-family | gpt-5.5 | 0.000 | 0.000 | complete |
| SWE-T2 | Claude-family | claude-opus-4-8 |  |  | pending |
| SWE-T2 | DeepSeek-family | deepseek-v4-flash | 0.000 | 0.000 | complete |
| REF-T2 | GPT-family | gpt-5.5 | 1.000 | 1.000 | complete |
| REF-T2 | Claude-family | claude-opus-4-8 |  |  | pending |
| REF-T2 | DeepSeek-family | deepseek-v4-flash | 1.000 | 1.000 | complete |

## Collected Raw Rows

| Task ID | Family | Alias | Condition | Score | Success | Attempts |
| --- | --- | --- | --- | --- | --- | --- |
| AIDE-T2 | GPT-family | gpt-5.5 | summary | 0.814 | True | 2 |
| AIDE-T2 | GPT-family | gpt-5.5 | papertoskill | 0.000 | False | 1 |
| AIDE-T2 | DeepSeek-family | deepseek-v4-flash | summary | 0.500 | False | 1 |
| AIDE-T2 | DeepSeek-family | deepseek-v4-flash | papertoskill | 0.500 | False | 1 |
| SWE-T2 | GPT-family | gpt-5.5 | summary | 0.000 | False | 1 |
| SWE-T2 | GPT-family | gpt-5.5 | papertoskill | 0.000 | False | 1 |
| SWE-T2 | DeepSeek-family | deepseek-v4-flash | summary | 0.000 | False | 1 |
| SWE-T2 | DeepSeek-family | deepseek-v4-flash | papertoskill | 0.000 | False | 1 |
| REF-T2 | GPT-family | gpt-5.5 | summary | 1.000 | True | 1 |
| REF-T2 | GPT-family | gpt-5.5 | papertoskill | 1.000 | True | 1 |
| REF-T2 | DeepSeek-family | deepseek-v4-flash | summary | 1.000 | True | 1 |
| REF-T2 | DeepSeek-family | deepseek-v4-flash | papertoskill | 1.000 | True | 1 |
