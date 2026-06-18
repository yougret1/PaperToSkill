# Phase 27 AAAI Package Verification Gate

Date: 2026-06-18.

## Question

Can the requested AAAI TeX paper package be checked as a local build artifact
rather than only verified by file presence and manual log inspection?

## Actions

- Added `scripts/check_aaai_package.py`.
- Added `tests/test_check_aaai_package.py`.
- Generated:
  - `results/reproducibility/aaai_package_report.json`
  - `results/reproducibility/aaai_package_report.md`
- Integrated the AAAI package report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, claim/evidence docs, result cards, goal audit, stage log,
  and memory.

## Results

- AAAI package report: `overall_status=ready`.
- Ready checks: `17`.
- Failed checks: `0`.
- The checker verifies:
  - required AAAI package files;
  - official author-kit SHA256;
  - `aaai2027` declaration in the main TeX file;
  - `aaai2027` load marker in the LaTeX log;
  - no unresolved citation/reference/build-error markers in the log;
  - PDF output marker, currently 4 pages and 133048 bytes;
  - PDF/log freshness relative to TeX/table/bibliography inputs;
  - BibTeX `.bbl` freshness relative to the bibliography.
- Reproducibility package report after integration:
  `ready_with_pending_external_evidence`, 140 ready checks, 7 pending checks,
  and 0 failed checks.

## Evidence Boundary

This phase supports local AAAI package/build-artifact readiness. It does not
make the paper submission-final or accepted, and it does not resolve pending
live model responses, DeepSeek response collection, human-fidelity annotation,
provider billing, or success-per-dollar evidence.

## Commands

```powershell
python scripts\check_aaai_package.py `
  --output-json results\reproducibility\aaai_package_report.json `
  --output-md results\reproducibility\aaai_package_report.md `
  --strict

python scripts\check_reproducibility_package.py `
  --output-json results\reproducibility\package_report.json `
  --output-md results\reproducibility\package_report.md `
  --strict

python -m unittest tests.test_check_aaai_package -v
```
