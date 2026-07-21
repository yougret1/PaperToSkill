# snap_mfse Confirmation V2

- Classification: task_local_admission_rejected
- Statistical sample: 18 independent API agent runs
- Within-run evaluation: 64 clustered hidden checks per run
- Schedule complete: True
- Integrity passed: True
- Hard constraints passed: False
- Task-local admission ready: False

| Hypothesis | Successes | Total | One-sided CP lower | Threshold |
|---|---:|---:|---:|---:|
| H_full_benefit_run_level | 13 | 18 | 0.454269 | 0.800000 |
| H_slice_preservation_run_level | 3 | 18 | 0.032857 | 0.800000 |
| H_slice_benefit_run_level | 5 | 18 | 0.091598 | 0.800000 |

Cases are clustered checks inside a run and are not treated as independent Bernoulli observations.
