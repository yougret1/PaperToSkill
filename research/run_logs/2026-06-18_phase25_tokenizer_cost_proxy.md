# Phase 25 Tokenizer-Aware Cost Proxy

Date: 2026-06-18.

## Question

Can the compactness/economic section move beyond the coarse
`ceil(characters / 4)` proxy while still avoiding unsupported provider-billing
claims?

## Actions

- Updated `scripts/evaluate_context_costs.py` to preserve the existing
  character proxy and add optional `tiktoken` tokenizer-aware outputs.
- Used the local `o200k_base` encoding as the default tokenizer-aware proxy.
- Generated:
  - `results/tables/context_cost_proxy_tokenizer.md`
  - `results/tables/context_cost_proxy_tokenizer.csv`
  - `results/tables/coverage_cost_efficiency_tokenizer.csv`
  - `results/tables/context_cost_proxy_tokenizer.json`
- Updated tests, reproducibility checks, paper text, AAAI table text, claim
  checklist, limitations, artifact map, decision log, stage log, and memory.

## Results

Under `o200k_base`, generated skills use:

- AI Scientist-v2: `1,079` tokens vs `45,212` for full extracted paper text,
  a `97.61%` reduction.
- Reflexion: `703` tokens vs `16,414`, a `95.72%` reduction.
- AIDE: `1,285` tokens vs `13,312`, a `90.35%` reduction.
- Toolformer: `1,255` tokens vs `20,365`, a `93.84%` reduction.

The Phase 12 character proxy remains available as a sensitivity check:
`results/tables/context_cost_proxy.md` and
`results/tables/context_cost_proxy.json`.

## Evidence Boundary

This phase supports local tokenizer-aware compactness and input-cost proxy
claims. It does not support provider-specific prices, live invoices, output
token accounting, model-quality conclusions, or success-per-dollar claims.

## Commands

- `python -m unittest tests.test_evaluate_context_costs -v`
- `python scripts\evaluate_context_costs.py --output-dir results\tables`
- `python scripts\check_reproducibility_package.py --output-json results\reproducibility\package_report.json --output-md results\reproducibility\package_report.md --strict`
- `python -m unittest discover -s tests -v`
- `git diff --check`
- `rg -n "sk-[A-Za-z0-9]{20,}" .`
- `pdflatex -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex`
- `bibtex papertoskill_aaai2027`
- `pdflatex -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex`

## Verification

- Full unit tests: `30` tests passed.
- Reproducibility package: `ready_with_pending_external_evidence`, `134` ready,
  `7` pending, `0` failed.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- Raw-key scan: no matches.
- AAAI LaTeX PDF: generated successfully after BibTeX and sequential LaTeX
  rerun; no unresolved citation or table-reference warnings remained. One
  underfull hbox warning remains in the compactness paragraph.
