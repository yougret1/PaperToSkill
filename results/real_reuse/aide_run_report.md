# AIDE Real-Reuse Run Report

Evidence boundary: this report covers only prepared AIDE real-reuse tasks. Provider/model errors are availability evidence, not model-quality failures. Aggregate PaperToSkill claims require the broader real-reuse benchmark.

- Run ID: phase109_llm_ablation_claude_opus_4_8_aide_t2
- Overall status: blocked_by_provider_or_model_availability
- Status counts: {'error': 2}
- Model family: Claude-family
- Model alias: claude-opus-4-8
- Wire API: anthropic_messages
- Raw rows: D:\a_work\gitee\PaperToSkill\results\real_reuse\raw_rows.jsonl

| Task | Condition | Status | Score | Success | Failure | Output |
| --- | --- | --- | --- | --- | --- | --- |
| AIDE-T2 | summary | error |  |  | {"raw_body": "error code: 502\n", "http_error": 502} |  |
| AIDE-T2 | papertoskill | error |  |  | {"raw_body": "error code: 502\n", "http_error": 502} |  |
