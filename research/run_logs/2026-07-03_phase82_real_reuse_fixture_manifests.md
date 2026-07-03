# Phase 82: Real-Reuse Fixture Manifests

- Run ID: phase82_real_reuse_fixture_manifests
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: materialize fixture requirement manifests for all eight
  real-reuse task contracts.

## Inputs

- `benchmarks/real_reuse/tasks/*.json`
- `benchmarks/real_reuse/real_reuse_v0.json`

## Outputs

- `scripts/build_real_reuse_fixture_manifests.py`
- `benchmarks/real_reuse/fixtures/AIDE-T1.json`
- `benchmarks/real_reuse/fixtures/AIDE-T2.json`
- `benchmarks/real_reuse/fixtures/SWE-T1.json`
- `benchmarks/real_reuse/fixtures/SWE-T2.json`
- `benchmarks/real_reuse/fixtures/REF-T1.json`
- `benchmarks/real_reuse/fixtures/REF-T2.json`
- `benchmarks/real_reuse/fixtures/SNAP-T1.json`
- `benchmarks/real_reuse/fixtures/SNAP-T2.json`
- Expanded validation in `scripts/check_real_reuse_benchmark.py`

## Commands

```powershell
python scripts\build_real_reuse_fixture_manifests.py
python scripts\check_real_reuse_benchmark.py --strict
python scripts\check_reproducibility_package.py --strict
python -m unittest tests.test_build_real_reuse_fixture_manifests tests.test_check_real_reuse_benchmark tests.test_check_reproducibility_package -v
```

## Result

- Eight fixture requirement manifests were generated.
- Real-reuse preflight reports `ready_to_implement`, 8 tasks, 207 ready checks,
  and 0 failed checks.
- Aggregate reproducibility package reports `ready_with_pending_external_evidence`,
  330 ready checks, 1 pending check, and 0 failed checks.

## Evidence Boundary

The fixture manifests define required assets, context assets, execution budget
slots, scoring contracts, provenance/license requirements, and planned output
paths. They do not select concrete datasets or repositories, do not download or
clone external projects, do not fill scoring commands, and do not contain task
outputs, scores, or downstream task-success evidence.
