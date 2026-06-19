# Phase 51: External Evidence Closure Queue

## Objective

Make the remaining external evidence blockers machine-checkable as a local
closure queue, without calling providers, running BFTS, collecting human rows,
or claiming that pending evidence is complete.

## Commands

```powershell
python scripts\check_external_evidence_closure.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Results

- Added `scripts/check_external_evidence_closure.py`.
- Added `tests/test_check_external_evidence_closure.py`.
- Generated `results/external_evidence_closure/closure.json` and
  `results/external_evidence_closure/closure.md`.
- Integrated the closure report into the goal-completion and reproducibility
  package gates.
- The closure queue maps the current pending goal requirements to six concrete
  next-action items:
  - AI-Scientist-v2 smoke completion.
  - AI-Scientist-v2 full live/BFTS run.
  - DeepSeek response collection and model-ablation completion.
  - Human-fidelity annotation.
  - Provider billing and success-per-dollar evidence.
  - AAAI submission decision.

## Evidence Boundary

This phase creates a local planning and checking artifact. It does not complete
the AI-Scientist-v2 smoke, run the full AI-Scientist-v2 live/BFTS task, collect
DeepSeek responses, collect human annotations, collect provider bills, compute
success per dollar from invoices, or make the AAAI paper submission-final.
