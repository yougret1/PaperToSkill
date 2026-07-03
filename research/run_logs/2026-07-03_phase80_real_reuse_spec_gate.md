# Phase 80: Real-Reuse Spec Gate

- Run ID: phase80_real_reuse_spec_gate
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: convert the planned real-reuse experiment design into a
  machine-checkable benchmark spec and local preflight gate.

## Inputs

- `research/real_reuse_experiment_plan.md`
- User discussion recorded in `C:\Users\19351\Desktop\tem\nextStep.md`
- Source URL reachability checks recorded in
  `benchmarks/real_reuse/real_reuse_v0.json`

## Outputs

- `benchmarks/real_reuse/real_reuse_v0.json`
- `scripts/check_real_reuse_benchmark.py`
- `tests/test_check_real_reuse_benchmark.py`
- `results/real_reuse/spec_preflight.json`
- `results/real_reuse/spec_preflight.md`
- Aggregate package-gate integration in
  `scripts/check_reproducibility_package.py`

## Commands

```powershell
python scripts\check_real_reuse_benchmark.py --strict
python -m unittest tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
python scripts\check_reproducibility_package.py --strict
```

Full phase-save verification also reruns the broader unit suite and strict
claim/package checks before commit.

## Result

- Real-reuse spec preflight: `ready_to_implement`.
- Planned tasks: 8.
- Ready checks: 85.
- Failed checks: 0.
- Aggregate reproducibility package after integration:
  `ready_with_pending_external_evidence`, 312 ready checks, 1 pending check,
  0 failed checks.

## Evidence Boundary

This run log records a benchmark-spec gate only. No original-style paper-task
was executed, no raw rows were produced, and the AAAI Results section must not
claim real-reuse downstream success until future `results/real_reuse/` raw rows
exist.
