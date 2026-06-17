# Phase 15 Failure-Case Archive Run Log

Date: 2026-06-17

## Purpose

Create a first-class archive for failed branches, paper-reported limitations,
and project-level failure/fix records so the paper can discuss negative paths
without overstating outcome evidence.

## Commands

```powershell
python -m unittest tests.test_build_failure_case_archive -v
python scripts\build_failure_case_archive.py --output-dir results\failure_cases
python -m unittest discover -s tests -v
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

## Outputs

- `benchmarks/failure_case_archive_v0.json`
- `scripts/build_failure_case_archive.py`
- `tests/test_build_failure_case_archive.py`
- `results/failure_cases/failure_case_archive.json`
- `results/failure_cases/failure_case_archive.md`
- `results/failure_cases/failure_case_archive.csv`

## Results

- Total archived cases: 20
- Paper-reported cases: 14
- Project-level cases: 6
- Category coverage includes cost, ethics, evaluation validity, evaluator bug,
  external dependency, extraction recall bug, extractor bug, memory limit,
  missing evidence, paper limitation, quality limit, quality threshold, search
  failure, and source-span bug.

## Evidence Boundary

This archive is provenance evidence and claim-discipline infrastructure. It is
not a live reproduction failure study and does not show that recording failures
improves final user outcomes.

## Verification

- `python -m unittest tests.test_build_failure_case_archive -v`: passed, 1 test OK.
- `python -m unittest discover -s tests -v`: passed, 15 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.
