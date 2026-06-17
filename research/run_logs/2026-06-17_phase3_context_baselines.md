# Run Log: 2026-06-17 Phase 3 Context Baselines

## Objective

Create a deterministic downstream-task baseline comparing the generated
PaperToSkill skill against a generic summary and abstract-only context.

## Task

- Task spec: `benchmarks/tasks/ai_scientist_v2_research_run.json`
- Prompt: plan a small AI Scientist-v2-inspired automated research run while
  preserving stages, node lifecycle, debug/refine policy, replication,
  aggregation, visual review, and limitations/ethics.

## Context Variants

- Skill: `generated_skills/ai_scientist_v2/SKILL.md`
- Generic summary: `baselines/ai_scientist_v2_generic_summary.md`
- Abstract only: `baselines/ai_scientist_v2_abstract_only.md`

## Commands

```powershell
python scripts\evaluate_context_baselines.py --task benchmarks\tasks\ai_scientist_v2_research_run.json --output results\evaluations\ai_scientist_v2_context_baselines_v0.json
python -m unittest discover -s tests -v
```

## Results

| Context | Score | Max | Words |
| --- | ---: | ---: | ---: |
| PaperToSkill generated skill | 7.867 | 9 | 782 |
| Generic summary | 1.733 | 9 | 154 |
| Abstract-only context | 1.2 | 9 | 99 |

## Interpretation

The generated skill preserves substantially more task-relevant operational
details than both baselines under this deterministic coverage rubric. The result
supports only a narrow claim: source-anchored skills can retain more actionable
method components than short summaries for one paper and one planning task.

## Evidence Boundary

This is not an LLM execution benchmark and not a human evaluation. The scoring is
keyword-based and may miss paraphrases or over-credit superficial mentions. The
next step is a source-map-aware unsupported-instruction evaluator and, when the
remote LLM endpoint recovers, an actual task-execution comparison.

