# toolformer_filter Confirmation V2

- Classification: task_local_admission_rejected
- Statistical sample: 18 independent API agent runs
- Within-run evaluation: 64 clustered hidden checks per run
- Schedule complete: True
- Integrity passed: True
- Hard constraints passed: True
- Task-local admission ready: False

| Hypothesis | Successes | Total | One-sided CP lower | Threshold |
|---|---:|---:|---:|---:|
| H_full_benefit_run_level | 18 | 18 | 0.804661 | 0.800000 |
| H_slice_preservation_run_level | 6 | 18 | 0.127037 | 0.800000 |
| H_slice_benefit_run_level | 6 | 18 | 0.127037 | 0.800000 |

Cases are clustered checks inside a run and are not treated as independent Bernoulli observations.
