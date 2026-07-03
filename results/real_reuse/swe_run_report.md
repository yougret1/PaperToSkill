# SWE Real-Reuse Run Report

Evidence boundary: this report covers only prepared SWE real-reuse tasks. Provider/model errors are availability evidence, not model-quality failures. Aggregate PaperToSkill claims require the broader real-reuse benchmark.

- Run ID: phase96_gpt_swe_t2_real_reuse
- Overall status: complete
- Status counts: {'scored': 2}
- Model family: GPT-family
- Model alias: gpt-5.5
- Wire API: openai_responses
- Raw rows: D:\a_work\gitee\PaperToSkill\results\real_reuse\raw_rows.jsonl

| Task | Condition | Status | Score | Success | Failure | Output |
| --- | --- | --- | --- | --- | --- | --- |
| SWE-T2 | summary | scored | 0.0 | False | patch_apply_failed | results/real_reuse/runs/SWE-T2/summary/phase96_gpt_swe_t2_real_reuse/candidate.patch |
| SWE-T2 | papertoskill | scored | 1.0 | True |  | results/real_reuse/runs/SWE-T2/papertoskill/phase96_gpt_swe_t2_real_reuse/candidate.patch |
