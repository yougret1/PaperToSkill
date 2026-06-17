# Claim Evidence Matrix

| Claim | Evidence Needed | Experiment | Metric | Baseline | Status | Source/Run |
| --- | --- | --- | --- | --- | --- | --- |
| PaperToSkill can convert a paper into a usable skill. | At least one generated skill passes structural validation and is usable by an agent. | Smoke conversion on one paper-like input, then run a task using the skill. | Validation pass, task completion, human review. | Manual skill writing or generic summary. | Planned | TBD |
| Paper-derived skills improve downstream task success compared with summaries. | Controlled tasks where agents use skill vs summary. | Multi-paper task benchmark. | Success rate, rubric score. | Abstract-only summary, generic LLM summary, no context. | Planned | TBD |
| Skills are more context-efficient than full paper excerpts. | Token/cost comparison with comparable task outcomes. | Compactness/cost experiment. | Tokens, price estimate, success per 1k tokens. | Full paper excerpt. | Planned | TBD |
| Transfer notes improve cross-harness portability. | Codex-to-Claude or Claude-to-Codex task runs with and without transfer notes. | Harness transfer ablation. | Cross-harness success rate and intervention count. | Skill without transfer notes. | Planned | TBD |
| Recording failure branches improves reproducibility and honest paper claims. | Failure-case archive and reviewer-style analysis showing avoided overclaims. | Failure branch audit. | Number of documented failure modes, claim downgrades. | Success-only report. | Planned | TBD |

