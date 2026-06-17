# Run Log: 2026-06-17 Phase 8 Reflexion Baselines And Transfer

## Objective

Bring the Reflexion second-paper case up to the same deterministic evaluation
surface as AI Scientist-v2: context baselines, transfer-readiness ablation, and
live prompt packets.

## Commands

```powershell
python scripts\evaluate_context_baselines.py --task benchmarks\tasks\reflexion_research_run.json --output results\evaluations\reflexion_context_baselines_v0.json
python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\reflexion_harness_transfer.json --output results\evaluations\reflexion_harness_transfer_v0.json
python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\reflexion_live_transfer.json --output-dir results\live_transfer_prompts\reflexion_v0
python -m unittest discover -s tests -v
```

## Context Baseline Results

| Variant | Score | Max score | Words |
| --- | ---: | ---: | ---: |
| PaperToSkill generated skill | 8.267 | 9 | 479 |
| Generic summary | 3.483 | 9 | 111 |
| Abstract-only context | 2.533 | 9 | 52 |

## Harness Transfer Readiness Results

| Variant | Average normalized score |
| --- | ---: |
| Full generated skill | 10.0 |
| Skill without transfer notes | 7.6 |
| Generic summary | 2.25 |

## Live Prompt Packets

Generated six prompt packets under
`results/live_transfer_prompts/reflexion_v0/`, covering two harness styles and
three context variants.

## Interpretation

Reflexion mirrors the earlier AI Scientist-v2 pattern: a paper-derived skill
preserves more operational task capabilities than summaries, and explicit
transfer notes contribute measurable offline portability signals. This supports
the paper's multi-paper deterministic evidence story while still keeping live
agent success as a separate pending experiment.

## Evidence Boundary

These are deterministic scoring tasks and generated prompt packets. They do not
prove live Codex or Claude execution success.

