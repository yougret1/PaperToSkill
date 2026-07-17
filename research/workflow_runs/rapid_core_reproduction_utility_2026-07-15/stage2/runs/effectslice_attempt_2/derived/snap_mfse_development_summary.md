# SNAP-MFSE Development Audit

Evidence boundary: development only; frozen eligibility is still required.

- Bundles: 4
- Primary model family: DeepSeek-family
- Task disposition: proceed_to_frozen_eligibility
- Selected model family: DeepSeek-family
- Robustness-only positive families: ['GPT-family']
- Scientific claim ready: False

| Pair | Model | Classification | F-B | Same patch |
| --- | --- | --- | ---: | --- |
| snap-mfse:dev:deepseek:bf:001 | deepseek-v4-flash | provider_failure | n/a | None |
| snap-mfse:dev:deepseek:bf:002 | deepseek-v4-flash | provider_failure | n/a | None |
| snap-mfse:dev:deepseek:bf:003 | deepseek-v4-flash | positive_development_signal | 1.000000 | False |
| snap-mfse:dev:gpt56:bf:001 | gpt-5.6 | positive_development_signal | 1.000000 | False |
