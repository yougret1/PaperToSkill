# Phase 29 Run Log: Paper Table Consistency Gate

## Decision Question

Can the AAAI manuscript tables be checked against the generated result tables
so manual table edits do not drift from the reproducible evidence?

## Actions

- Added `scripts/check_paper_tables.py`.
- Added `tests/test_check_paper_tables.py`.
- Generated:
  - `results/reproducibility/paper_table_report.json`
  - `results/reproducibility/paper_table_report.md`
- Integrated the paper-table report into
  `scripts/check_reproducibility_package.py`.

## Checks

The checker parses the four LaTeX result tables in
`paper/aaai/papertoskill_tables.tex` and compares their displayed values
against:

- `results/tables/main_results.csv`
- `results/tables/transfer_ablation.csv`
- `results/tables/context_cost_proxy_tokenizer.csv`
- `results/tables/auto_note_comparison.csv`

It tolerates presentation differences such as `1` versus `1.000` and decimal
fractions versus percentages, but fails when a displayed number changes.

## Results

- Paper-table report status: `ready`.
- Ready checks: `76`.
- Failed checks: `0`.
- Reproducibility package report after integration:
  `ready_with_pending_external_evidence`, `153` ready checks, `7` pending
  checks, and `0` failed checks.

## Evidence Boundary

This phase prevents manuscript-table drift. It does not add new empirical
evidence and does not resolve the pending live model, human-fidelity, or
provider-billing evidence gaps.

## Verification

- `python scripts\check_paper_tables.py --strict`
- `python -m unittest tests.test_check_paper_tables -v`
- `python scripts\check_reproducibility_package.py --strict`
