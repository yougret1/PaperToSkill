# SnapATAC2 Real-Reuse Run Report

Evidence boundary: this report covers only prepared SnapATAC2 real-reuse tasks. Provider/model errors are availability evidence, not model-quality failures. Aggregate PaperToSkill claims require the broader real-reuse benchmark.

- Run ID: phase95_snapatac2_gpt55_live
- Overall status: complete
- Status counts: {'scored': 4}
- Model family: GPT-family
- Model alias: gpt-5.5
- Wire API: openai_responses
- Raw rows: D:\a_work\gitee\PaperToSkill\results\real_reuse\raw_rows.jsonl

| Task | Condition | Status | Score | Success | Failure | Output |
| --- | --- | --- | --- | --- | --- | --- |
| SNAP-T1 | summary | scored | 0.0 | False | Extra data: line 1 column 149 (char 148) | results/real_reuse/runs/SNAP-T1/summary/phase95_snapatac2_gpt55_live/candidate_output.json |
| SNAP-T1 | papertoskill | scored | 0.5 | False | missing_required_artifacts_or_metrics | results/real_reuse/runs/SNAP-T1/papertoskill/phase95_snapatac2_gpt55_live/candidate_output.json |
| SNAP-T2 | summary | scored | 0.2 | False | missing_required_artifacts_or_metrics | results/real_reuse/runs/SNAP-T2/summary/phase95_snapatac2_gpt55_live/candidate_output.json |
| SNAP-T2 | papertoskill | scored | 0.4 | False | missing_required_artifacts_or_metrics | results/real_reuse/runs/SNAP-T2/papertoskill/phase95_snapatac2_gpt55_live/candidate_output.json |
