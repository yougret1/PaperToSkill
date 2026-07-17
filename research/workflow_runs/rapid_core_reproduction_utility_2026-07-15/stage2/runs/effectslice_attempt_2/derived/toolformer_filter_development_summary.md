# TOOLFORMER-FILTER Development Audit

Evidence boundary: development only; frozen eligibility is still required.

- Bundles: 3
- Primary model family: DeepSeek-family
- Task disposition: proceed_to_frozen_eligibility
- Selected model family: DeepSeek-family
- Robustness-only positive families: ['GPT-family']
- Scientific claim ready: False

| Pair | Model | Classification | F-B | Same patch |
| --- | --- | --- | ---: | --- |
| toolformer-filter:development:deepseek:bf:001 | deepseek-v4-flash | task_contract_failure | n/a | None |
| toolformer-filter:development:deepseek:bf:002 | deepseek-v4-flash | positive_development_signal | 1.000000 | False |
| toolformer-filter:development:gpt:bf:001 | gpt-5.6 | positive_development_signal | 1.000000 | False |
