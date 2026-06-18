# Phase 38 Model-Response Output-Token Proxy

Date: 2026-06-19

## Decision

Can the cost/compactness section include output-token accounting for saved live
model responses without claiming provider billing?

## Actions

- Added `scripts/evaluate_model_response_costs.py`.
- Added `tests/test_evaluate_model_response_costs.py`.
- Generated:
  - `results/tables/model_response_cost_proxy.md`
  - `results/tables/model_response_cost_proxy.csv`
  - `results/tables/model_response_cost_proxy.json`
- Integrated the report into:
  - `scripts/check_reproducibility_package.py`
  - `scripts/check_goal_completion.py`
  - paper claim-boundary checks and paper-facing documentation.

## Results

- Total model-ablation rows: 6.
- Measured saved-response rows: 4.
- Pending rows: 2 DeepSeek follow-up rows.
- Character proxy output tokens: 9,420.
- Local `o200k_base` output tokens: 8,710.
- Per measured row:
  - Claude Toolformer: 2,272 tokenizer output tokens.
  - Claude AIDE: 2,108 tokenizer output tokens.
  - GPT-family Toolformer: 1,447 tokenizer output tokens.
  - GPT-family AIDE: 2,883 tokenizer output tokens.

## Evidence Boundary

This phase supports local output-token proxy accounting over saved
Claude/GPT-family model-ablation responses. It does not support provider
billing, live invoices, realized provider output bills, success-per-dollar
evidence, DeepSeek completion, live cross-harness success, or human semantic
fidelity.

## Verification

- `python scripts\evaluate_model_response_costs.py`
- `python -m unittest tests.test_evaluate_model_response_costs -v`
- `python -m unittest discover -s tests -v`
- `pdflatex -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex`;
  `bibtex papertoskill_aaai2027`;
  `pdflatex -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex`;
  `pdflatex -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex`
  from `paper/aaai`.
- `python scripts\check_aaai_package.py --strict`
- `python scripts\check_paper_claims.py --strict`
- `python scripts\check_goal_completion.py --strict`
- `python scripts\check_reproducibility_package.py --strict`
- `python scripts\check_paper_tables.py --strict`
- `python scripts\check_usage_examples.py --strict`
- `git diff --check`
- `rg -n "sk-[A-Za-z0-9]{20,}" .` returned no matches.

Final reports after this phase:

- Reproducibility package:
  `ready_with_pending_external_evidence`, 180 ready, 7 pending, 0 failed.
- Active-goal completion:
  `not_complete_pending_external_evidence`, 40 ready, 8 pending, 0 failed.
- AAAI package:
  ready, 17 ready, 0 failed.
