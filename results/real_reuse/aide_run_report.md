# AIDE Real-Reuse Run Report

Evidence boundary: this report covers only prepared AIDE real-reuse tasks. Provider/model errors are availability evidence, not model-quality failures. Aggregate PaperToSkill claims require the broader real-reuse benchmark.

- Run ID: phase106_extended_score_300s
- Overall status: complete
- Status counts: {'scored': 4}
- Model family: GPT-family
- Model alias: gpt-5.5
- Wire API: openai_responses
- Raw rows: D:\a_work\gitee\PaperToSkill\results\real_reuse\raw_rows.jsonl

| Task | Condition | Status | Score | Success | Failure | Output |
| --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | summary | scored | 0.8159861989649224 | True |  | results/real_reuse/runs/AIDE-T1/summary/phase106_extended_score_300s/candidate_solution.py |
| AIDE-T1 | papertoskill | scored | 0.8171362852213916 | True |  | results/real_reuse/runs/AIDE-T1/papertoskill/phase106_extended_score_300s/candidate_solution.py |
| AIDE-T2 | summary | scored | 0.0 | False | timeout after 300s | results/real_reuse/runs/AIDE-T2/summary/phase106_extended_score_300s/candidate_solution.py |
| AIDE-T2 | papertoskill | scored | 0.8263369752731455 | True |  | results/real_reuse/runs/AIDE-T2/papertoskill/phase106_extended_score_300s/candidate_solution.py |
