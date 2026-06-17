# Phase 12 Run Log: Context Cost Proxy

## Purpose

Add a reproducible compactness/economic proxy experiment that does not depend on
the blocked remote LLM endpoint.

## Method

- Estimate input-token proxies as `ceil(characters / 4)`.
- Estimate input cost with a configurable `$1.00 / 1M` input-token proxy.
- Compare full extracted paper text, curated source notes, generated skills,
  generic summaries, and abstract-only contexts.
- Compute deterministic coverage per estimated context budget only for context
  variants that already have coverage evaluations.

## Actions

- Added `scripts/evaluate_context_costs.py`.
- Added `tests/test_evaluate_context_costs.py`.
- Ran `python scripts\evaluate_context_costs.py --output-dir results\tables`.
- Updated paper tables and draft artifacts with the new evidence boundary.
- Updated artifact map, decision log, result cards, stage log, and memory.

## Results

Generated skill token-proxy reductions relative to full extracted paper text:

| Paper | Skill tokens | Full paper tokens | Reduction |
| --- | --- | --- | --- |
| AI Scientist-v2 | 1366 | 62041 | 97.8% |
| Reflexion | 823 | 18559 | 95.57% |
| AIDE | 1517 | 15894 | 90.46% |

## Evidence Boundary

This phase supports deterministic context-size and cost-proxy claims. It does
not support provider-billing, tokenizer-exact, live task, or success-per-dollar
claims.

## Verification

- `python -m unittest tests.test_evaluate_context_costs -v`: passed.
- `python -m unittest discover -s tests -v`: passed, 11 tests OK.
- `git diff --check`: no whitespace errors; Windows LF/CRLF warnings only.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.
