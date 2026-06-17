# Phase 16 Reproducibility Package Run Log

Date: 2026-06-17

## Purpose

Re-test the remote model endpoint and add a local reproducibility package gate
that separates ready local artifacts from pending external evidence.

## Endpoint Retest

- `/v1/models`: reachable and lists `claude-opus-4-8`.
- `/v1/chat/completions`: HTTP 503 with an empty body for
  `claude-opus-4-8`.

Evidence boundary: live cross-harness runs remain blocked by provider
availability, not by missing local prompt packets.

## Commands

```powershell
python -m unittest tests.test_check_reproducibility_package -v
python scripts\check_reproducibility_package.py --output-json results\reproducibility\package_report.json --output-md results\reproducibility\package_report.md --strict
python scripts\build_failure_case_archive.py --output-dir results\failure_cases
python -m unittest discover -s tests -v
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

## Outputs

- `scripts/check_reproducibility_package.py`
- `tests/test_check_reproducibility_package.py`
- `results/reproducibility/package_report.json`
- `results/reproducibility/package_report.md`

## Results

- Overall status: `ready_with_pending_external_evidence`
- Ready checks: 63
- Pending checks: 4
- Failed checks: 0

The pending checks are the three live response sets and completed
human-fidelity annotation.

## Evidence Boundary

The report supports local package readiness. It does not claim completed live
cross-harness execution, completed human validation, provider billing evidence,
or success-per-dollar evidence.

## Verification

- `python -m unittest tests.test_check_reproducibility_package -v`: passed, 2 tests OK.
- `python -m unittest discover -s tests -v`: passed, 17 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.
