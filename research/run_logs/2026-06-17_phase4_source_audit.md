# Run Log: 2026-06-17 Phase 4 Source-Map Audit

## Objective

Add a source-map-aware unsupported-instruction audit that can distinguish a real
paper-derived skill from a paper-like retained case and an abstract-only seed.

## Task

- Task spec: `benchmarks/tasks/skill_source_audit.json`
- Skills audited:
  - `generated_skills/ai_scientist_v2`
  - `generated_skills/papertoskill_paper_note`
  - `generated_skills/papertoskill_seed`

## Commands

```powershell
python scripts\audit_skill_source_map.py --task benchmarks\tasks\skill_source_audit.json --output results\evaluations\skill_source_audit_v0.json
python -m unittest discover -s tests -v
```

## Results

| Skill | Total bullets | Supported | Weak | Unsupported | Unsupported rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| AI Scientist-v2 real skill | 20 | 16 | 0 | 4 | 0.2 |
| Paper-like retained case | 18 | 0 | 14 | 4 | 0.222 |
| Abstract-only seed | 14 | 0 | 0 | 14 | 1.0 |

## Interpretation

The audit separates the real source-anchored skill from the abstract-only seed
and also shows that the paper-like retained case is weaker than the real paper
note. This is the first evidence in the project that unsupported-instruction
rate can be estimated from source-map-aware auditing instead of keyword coverage
alone.

## Failure And Fix

The first audit attempt mapped skill section names too literally and gave all
three skills an unsupported rate of 1.0. The fix was to map skill sections
(`workflow`, `validation`, `failure cases`, `transfer notes`) onto source-note
groups (`method`, `experiment`, `limitation`, `transfer notes`) before scoring.

## Evidence Boundary

This is still a heuristic audit, not a human annotation study. It can
under-credit valid paraphrases and over-credit noisy keyword overlap, but it is a
meaningful step toward unsupported-instruction scoring.

