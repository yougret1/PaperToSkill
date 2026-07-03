# Phase 81: Real-Reuse Per-Task Specs

- Run ID: phase81_real_reuse_task_specs
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: materialize the eight planned real-reuse paper-task rows into
  per-task execution-contract specs.

## Inputs

- `benchmarks/real_reuse/real_reuse_v0.json`
- `results/real_reuse/spec_preflight.md`

## Outputs

- `scripts/build_real_reuse_task_specs.py`
- `benchmarks/real_reuse/tasks/AIDE-T1.json`
- `benchmarks/real_reuse/tasks/AIDE-T2.json`
- `benchmarks/real_reuse/tasks/SWE-T1.json`
- `benchmarks/real_reuse/tasks/SWE-T2.json`
- `benchmarks/real_reuse/tasks/REF-T1.json`
- `benchmarks/real_reuse/tasks/REF-T2.json`
- `benchmarks/real_reuse/tasks/SNAP-T1.json`
- `benchmarks/real_reuse/tasks/SNAP-T2.json`
- Expanded validation in `scripts/check_real_reuse_benchmark.py`

## Commands

```powershell
python scripts\build_real_reuse_task_specs.py
python scripts\check_real_reuse_benchmark.py --strict
python -m unittest tests.test_build_real_reuse_task_specs tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
```

## Result

- Eight per-task execution-contract specs were generated.
- Real-reuse preflight reports `ready_to_implement`, 8 tasks, 142 ready checks,
  and 0 failed checks.
- Aggregate reproducibility package reports `ready_with_pending_external_evidence`,
  321 ready checks, 1 pending check, and 0 failed checks.

## Evidence Boundary

The per-task files define input contracts, output contracts, context
conditions, metric contracts, run controls, workflow checklists, unsupported
error policy, and raw-row schema. They do not contain fixtures, task outputs,
scores, or downstream task-success evidence.
