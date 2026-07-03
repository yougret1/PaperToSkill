# Real-Reuse Main Results Table

Evidence boundary: this table defines the main real-reuse experiment rows for the paper. Filled scores come from local raw rows; pending cells are not downstream task-success evidence.

- Raw scored rows read: 4

| Task ID | Source Paper | Domain | Original-style Input | Required Output | Metric | Reference | Summary Score | PaperToSkill Score | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | ML engineering | Kaggle-style dataset + metric | Runnable solution/submission | validation_score | Reported AIDE ref. | Pending | Pending | Awaiting dataset |
| AIDE-T2 | AIDE | ML engineering | Weak ML script + feedback | Improved script + trajectory | best_node_score | Reported AIDE ref. | Pending | Pending | Awaiting dataset |
| SWE-T1 | SWE-agent | Software engineering | Repo issue + tests | Patch + test log | resolved | Reported SWE-agent ref. | Pending | Pending | Fixture pending |
| SWE-T2 | SWE-agent | Software engineering | Failing test + repo | Focused patch + verification | tests_passed | Reported SWE-agent ref. | Pending | Pending | Fixture pending |
| REF-T1 | Reflexion | Reasoning / QA | Multi-hop QA + feedback | Final answer + reflection trace | exact_match_or_f1 | Reported Reflexion ref. | 1.000 | 1.000 | Scored (GPT-family) |
| REF-T2 | Reflexion | Decision / programming | Failed attempt + checker feedback | Corrected second attempt | second_attempt_success | Reported Reflexion ref. | 1.000 | 1.000 | Scored (GPT-family) |
| SNAP-T1 | SnapATAC2 | Single-cell omics | Small single-cell dataset | Pipeline + embedding artifacts | runtime_memory_quality | Reported SnapATAC2 ref. | Pending | Pending | Runner pending |
| SNAP-T2 | SnapATAC2 | Single-cell omics | Single-cell labels/proxy task | Clustering/marker artifacts | ari_nmi_runtime_memory | Reported SnapATAC2 ref. | Pending | Pending | Runner pending |
