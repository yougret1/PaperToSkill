# Run Log: 2026-06-17 Phase 5 Harness Transfer Readiness

## Objective

Add a reproducible offline transfer-readiness evaluation before live
Codex-to-Claude or Claude-to-Codex runs are available.

## Task

- Task spec: `benchmarks/tasks/ai_scientist_v2_harness_transfer.json`
- Context variants:
  - `full_skill`: generated AI Scientist-v2 skill with transfer notes.
  - `skill_without_transfer_notes`: same skill with `Transfer Notes` removed.
  - `generic_summary`: prose summary baseline.
- Target harness styles:
  - Codex-style `SKILL.md`
  - Claude-style project prompt

## Commands

```powershell
python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\ai_scientist_v2_harness_transfer.json --output results\evaluations\ai_scientist_v2_harness_transfer_v0.json
python -m unittest discover -s tests -v
```

## Results

| Variant | Average normalized score | Codex-style score | Claude-style score |
| --- | ---: | ---: | ---: |
| Full generated skill | 10.0 | 10.0 | 10.0 |
| Skill without transfer notes | 7.6 | 7.6 | 7.6 |
| Generic summary | 1.2 | 1.2 | 1.2 |

## Interpretation

The full generated skill keeps the operational method, validation evidence,
source anchors, compactness, and transfer instructions required by both target
harness styles. Removing `Transfer Notes` preserves the paper method but loses
the explicit transfer checks. The generic summary stays compact but lacks
structured sections, source anchors, and most transfer signals.

## Evidence Boundary

This is an offline deterministic readiness metric, not a live cross-harness
agent execution result. It supports the claim that transfer notes improve the
skill artifact's portability signals, but it does not yet prove that Claude or
Codex agents will complete downstream tasks more successfully.

