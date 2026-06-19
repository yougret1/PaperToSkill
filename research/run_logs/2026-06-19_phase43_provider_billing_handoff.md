# Phase 43: Provider Billing Evidence Handoff

## Objective

Make the remaining provider-billing and success-per-dollar evidence gap
executable by adding a blank billing-evidence template and strict summarizer,
without claiming any realized provider bills.

## Commands

```powershell
python scripts\summarize_provider_billing_evidence.py --init-template --strict
cd paper\aaai
pdflatex papertoskill_aaai2027.tex
bibtex papertoskill_aaai2027
pdflatex papertoskill_aaai2027.tex
pdflatex papertoskill_aaai2027.tex
cd ..\..
python -m unittest discover -s tests -v
python scripts\check_paper_claims.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

## Results

- Added `benchmarks/provider_billing_evidence_v0.json`, defining six billing
  evidence slots for Claude-family, GPT-family, DeepSeek, live-transfer,
  AI-Scientist-v2, and context-comparison evidence.
- Added `scripts/summarize_provider_billing_evidence.py`, which writes a blank
  template if needed and summarizes measured provider-billing rows.
- Added `results/provider_billing_evidence/billing_template.csv`.
- Added `results/provider_billing_evidence/billing_summary.json` and `.md`.
- The current billing summary is `billing_status=pending`, 6 total rows, 0
  measured rows, 6 pending rows, 0 errors, and no success-per-dollar value.
- Added package and goal checks for provider-billing handoff readiness.
- Goal report now shows 53 ready checks, 8 pending checks, and 0 failed checks.
- Reproducibility package report now shows 221 ready checks, 7 pending checks,
  and 0 failed checks.

## Evidence Boundary

This phase prepares auditable provider-billing evidence collection only. It does
not provide live invoices, realized provider bills, DeepSeek responses,
AI-Scientist-v2 live-run completion, human validation, or a real
success-per-dollar result.
