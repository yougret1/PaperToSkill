# Phase 53: External Evidence Execution Packets

## Objective

Turn the Phase 51 external-evidence closure queue into runnable execution
packets, without calling providers, running BFTS, collecting DeepSeek
responses, collecting human rows, collecting provider bills, or claiming that
pending evidence is complete.

## Commands

```powershell
python scripts\check_external_evidence_packets.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Results

- Added `scripts/check_external_evidence_packets.py`.
- Added `tests/test_check_external_evidence_packets.py`.
- Generated `results/external_evidence_packets/packets.json` and
  `results/external_evidence_packets/packets.md`.
- Integrated the packet report into the active-goal and reproducibility package
  gates.
- The packet report covers the same six queue items as the closure queue:
  AI-Scientist-v2 smoke completion, AI-Scientist-v2 full live/BFTS run,
  DeepSeek response collection/model-ablation completion, human-fidelity
  annotation, provider billing/success-per-dollar evidence, and the AAAI
  submission decision.
- `results/external_evidence_packets/packets.md` reports
  `overall_status=ready`, with 7 ready checks, 0 pending checks, and 0 failed
  checks.

## Evidence Boundary

This phase creates a local execution handoff. It does not complete the
AI-Scientist-v2 smoke, run the full AI-Scientist-v2 live/BFTS task, collect
DeepSeek responses, collect human annotations, collect provider bills, compute
success per dollar from invoices, or make the AAAI paper submission-final.
