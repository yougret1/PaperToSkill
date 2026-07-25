# Section 02 Report: Generalization and Interactions

## Coverage

- All 1,296 terminal rows are represented in 432 heatmap cells.
- Primary inference: 12 papers, 24 tasks, four domains, DeepSeek primary.
- Cross-model robustness: four shared anchor papers/tasks, six models, six paired
  blocks per task.
- Reducer robustness: the same four anchors with DeepSeek primary.

## Cross-model results on four anchors

| Model | F - B success | S - F success |
|---|---:|---:|
| Claude Opus 4.7 | +0.2500 | +0.2083 |
| DeepSeek | +0.2500 | +0.0417 |
| GPT-5.5 | +0.5000 | 0.0000 |
| GPT-5.6 Luna | +0.4167 | -0.1250 |
| GPT-5.6 Sol | +0.3750 | +0.0833 |
| GPT-5.6 Terra | +0.3750 | +0.0417 |

F - B is positive for all six models, so that anchor result is not driven by one
model. S - F is positive for four models, zero for one, and negative for one; the
S-over-F conclusion is model-dependent.

## Domain and registry sensitivity

Primary F - B operational-success effects are positive in every domain:
agent/tool-use `+0.1389`, data analysis `+0.1667`, NLP `+0.3333`, and software
engineering `+0.1389`. S - B is also positive in every domain. S - F is zero in
agent/tool-use and data analysis, positive in NLP (`+0.1389`), and smaller in
software engineering (`+0.0556`).

F - B remains positive in registry A (`+0.1806`) and registry B (`+0.2083`). S - B
also remains positive in both registries. The primary F/S-over-B result is not a
single-registry artifact.

## Reducer sensitivity on four anchors

The within-family candidate-minus-F success differences are `+0.1667` for DAG
greedy, `+0.2083` for source-window, `+0.0417` for the primary slice, `+0.2083`
for L0, `+0.2083` for L1, and `+0.0833` for L2. These comparisons use each
family's co-scheduled F arm; they are descriptive and must not be treated as a
single common-F ranking.

## Single-driver diagnostics

Leaving out any one primary paper does not reverse F - B or S - B for either
endpoint. F - B operational success remains between `+0.1597` and `+0.2361`, and
S - B remains between `+0.1875` and `+0.3021`. Cross-model and anchor-task
leave-one-out tables are included in `outputs/summary.json`.

## Claim boundary

The evidence supports F/S-over-B across domains and, on the shared anchors,
across all six models. It does not support a general S-over-F claim. The six-model
result covers four anchor tasks, not all 24 paper-tasks, and provider effects are
confounded with model identity.
