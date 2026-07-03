# Phase 84: Real-Reuse Main Table In Paper

- Run ID: phase84_real_reuse_paper_table
- Date: 2026-07-03
- Snapshot: before phase commit
- Objective: put the main real-reuse experiment table scaffold into the AAAI
  paper before task scores are available, while keeping pending-score boundaries
  explicit.

## Inputs

- `benchmarks/real_reuse/real_reuse_v0.json`
- `results/real_reuse/spec_preflight.md`
- `paper/aaai/papertoskill_aaai2027.tex`
- `paper/aaai/papertoskill_tables.tex`

## Outputs

- `scripts/build_real_reuse_paper_tables.py`
- `results/real_reuse/main_results_plan.csv`
- `results/real_reuse/main_results_plan.md`
- Updated `paper/aaai/papertoskill_tables.tex`
- Updated `paper/aaai/papertoskill_aaai2027.tex`
- Updated `scripts/check_paper_tables.py`
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf`

## Commands

```powershell
python scripts\build_real_reuse_paper_tables.py
python -m unittest tests.test_build_real_reuse_paper_tables tests.test_check_paper_tables -v
python scripts\check_paper_tables.py --strict
pdflatex -interaction=nonstopmode papertoskill_aaai2027.tex
bibtex papertoskill_aaai2027
pdflatex -interaction=nonstopmode papertoskill_aaai2027.tex
pdflatex -interaction=nonstopmode papertoskill_aaai2027.tex
python scripts\check_aaai_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Result

- Paper table consistency: `ready`, 156 ready checks, 0 failed checks.
- AAAI package: `ready`, 17 ready checks, 0 failed checks.
- Reproducibility package: `ready_with_pending_external_evidence`, 342 ready
  checks, 1 pending check, 0 failed checks.

## Evidence Boundary

The table has pending score cells. It is a main-experiment scaffold and paper
structure update, not task-success evidence. After real-reuse runs complete,
update `results/real_reuse/main_results_plan.csv`,
`paper/aaai/papertoskill_tables.tex`, and the relevant Results text with the
actual scores.
