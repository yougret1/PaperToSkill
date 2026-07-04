# Real-Reuse LLM Ablation Plan

Purpose: Pre-register real-reuse LLM ablation rows on stabilized paper-task slices.

Evidence boundary: Protocol and command plan only. It does not add model responses, scored raw rows, or main-table replacements. Provider latency, timeout, and retry counts are availability metadata, not method-effectiveness metrics.

Expected scored raw rows if fully run: 18

## Selected Tasks

| Task ID | Source Paper | Role | Metric | Summary | PaperToSkill |
| --- | --- | --- | --- | --- | --- |
| AIDE-T2 | AIDE | positive_method_reuse | best_node_score | 0.000 | 0.826 |
| SWE-T2 | SWE-agent | positive_method_reuse | tests_passed | 0.000 | 1.000 |
| REF-T2 | Reflexion | ceiling_control | second_attempt_success | 1.000 | 1.000 |

## Model Slots

| Family | Alias | Wire API | Base URL Env | API Key Env | Timeout | Attempts |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-family | gpt-5.5 | openai_responses | PAPERTOSKILL_GPT_OPENAI_BASE_URL | PAPERTOSKILL_GPT_OPENAI_API_KEY | 300 | 5 |
| Claude-family | claude-opus-4-8 | anthropic_messages | PAPERTOSKILL_CLAUDE_BASE_URL | PAPERTOSKILL_CLAUDE_API_KEY | 300 | 5 |
| DeepSeek-family | deepseek-v4-flash | openai_chat_completions | DEEPSEEK_BASE_URL | DEEPSEEK_API_KEY | 300 | 5 |

## Command Matrix

| Task ID | Model Slot | Expected Raw Rows | Run ID |
| --- | --- | --- | --- |
| AIDE-T2 | gpt_5_5 | 2 | `phase109_llm_ablation_gpt_5_5_aide_t2` |
| AIDE-T2 | claude_opus_4_8 | 2 | `phase109_llm_ablation_claude_opus_4_8_aide_t2` |
| AIDE-T2 | deepseek_v4_flash | 2 | `phase109_llm_ablation_deepseek_v4_flash_aide_t2` |
| SWE-T2 | gpt_5_5 | 2 | `phase109_llm_ablation_gpt_5_5_swe_t2` |
| SWE-T2 | claude_opus_4_8 | 2 | `phase109_llm_ablation_claude_opus_4_8_swe_t2` |
| SWE-T2 | deepseek_v4_flash | 2 | `phase109_llm_ablation_deepseek_v4_flash_swe_t2` |
| REF-T2 | gpt_5_5 | 2 | `phase109_llm_ablation_gpt_5_5_ref_t2` |
| REF-T2 | claude_opus_4_8 | 2 | `phase109_llm_ablation_claude_opus_4_8_ref_t2` |
| REF-T2 | deepseek_v4_flash | 2 | `phase109_llm_ablation_deepseek_v4_flash_ref_t2` |

## Environment Status

| Env | Status |
| --- | --- |
| DEEPSEEK_API_KEY | missing |
| DEEPSEEK_BASE_URL | missing |
| PAPERTOSKILL_CLAUDE_API_KEY | missing |
| PAPERTOSKILL_CLAUDE_BASE_URL | missing |
| PAPERTOSKILL_GPT_OPENAI_API_KEY | missing |
| PAPERTOSKILL_GPT_OPENAI_BASE_URL | missing |

## Commands

```powershell
python scripts\run_real_reuse_aide.py --task AIDE-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --base-url-env PAPERTOSKILL_GPT_OPENAI_BASE_URL --api-key-env PAPERTOSKILL_GPT_OPENAI_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1800 --run-id phase109_llm_ablation_gpt_5_5_aide_t2 --score-timeout-seconds 300
```

```powershell
python scripts\run_real_reuse_aide.py --task AIDE-T2 --condition summary --condition papertoskill --model-family Claude-family --model-alias claude-opus-4-8 --wire-api anthropic_messages --base-url-env PAPERTOSKILL_CLAUDE_BASE_URL --api-key-env PAPERTOSKILL_CLAUDE_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1800 --run-id phase109_llm_ablation_claude_opus_4_8_aide_t2 --score-timeout-seconds 300
```

```powershell
python scripts\run_real_reuse_aide.py --task AIDE-T2 --condition summary --condition papertoskill --model-family DeepSeek-family --model-alias deepseek-v4-flash --wire-api openai_chat_completions --base-url-env DEEPSEEK_BASE_URL --api-key-env DEEPSEEK_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1800 --run-id phase109_llm_ablation_deepseek_v4_flash_aide_t2 --score-timeout-seconds 300
```

```powershell
python scripts\run_real_reuse_swe.py --task SWE-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --base-url-env PAPERTOSKILL_GPT_OPENAI_BASE_URL --api-key-env PAPERTOSKILL_GPT_OPENAI_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 2200 --run-id phase109_llm_ablation_gpt_5_5_swe_t2 --score-timeout-seconds 120
```

```powershell
python scripts\run_real_reuse_swe.py --task SWE-T2 --condition summary --condition papertoskill --model-family Claude-family --model-alias claude-opus-4-8 --wire-api anthropic_messages --base-url-env PAPERTOSKILL_CLAUDE_BASE_URL --api-key-env PAPERTOSKILL_CLAUDE_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 2200 --run-id phase109_llm_ablation_claude_opus_4_8_swe_t2 --score-timeout-seconds 120
```

```powershell
python scripts\run_real_reuse_swe.py --task SWE-T2 --condition summary --condition papertoskill --model-family DeepSeek-family --model-alias deepseek-v4-flash --wire-api openai_chat_completions --base-url-env DEEPSEEK_BASE_URL --api-key-env DEEPSEEK_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 2200 --run-id phase109_llm_ablation_deepseek_v4_flash_swe_t2 --score-timeout-seconds 120
```

```powershell
python scripts\run_real_reuse_reflexion.py --task REF-T2 --condition summary --condition papertoskill --model-family GPT-family --model-alias gpt-5.5 --wire-api openai_responses --base-url-env PAPERTOSKILL_GPT_OPENAI_BASE_URL --api-key-env PAPERTOSKILL_GPT_OPENAI_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1600 --run-id phase109_llm_ablation_gpt_5_5_ref_t2 --score-timeout-seconds 10
```

```powershell
python scripts\run_real_reuse_reflexion.py --task REF-T2 --condition summary --condition papertoskill --model-family Claude-family --model-alias claude-opus-4-8 --wire-api anthropic_messages --base-url-env PAPERTOSKILL_CLAUDE_BASE_URL --api-key-env PAPERTOSKILL_CLAUDE_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1600 --run-id phase109_llm_ablation_claude_opus_4_8_ref_t2 --score-timeout-seconds 10
```

```powershell
python scripts\run_real_reuse_reflexion.py --task REF-T2 --condition summary --condition papertoskill --model-family DeepSeek-family --model-alias deepseek-v4-flash --wire-api openai_chat_completions --base-url-env DEEPSEEK_BASE_URL --api-key-env DEEPSEEK_API_KEY --timeout-seconds 300 --max-attempts 5 --retry-delay-seconds 5 --max-tokens 1600 --run-id phase109_llm_ablation_deepseek_v4_flash_ref_t2 --score-timeout-seconds 10
```
