# Real-Reuse Condition: summary

You are running a locked PaperToSkill real-reuse task. Use only the model-visible context and task prompt below. Do not request or invent hidden validation labels.

# Condition Context

# Real-Reuse Summary Baseline: AIDE-T2

This context is the Summary baseline for the locked AIDE real-reuse task. It
summarizes the source-paper method only. It does not include hidden validation
labels or scorer-only thresholds.

# Generic Summary: AIDE

AIDE frames machine-learning engineering as search over executable Python
solutions. It keeps a tree of candidate scripts, evaluates each candidate with
an objective metric, records feedback, and uses that feedback to draft, debug,
or improve the next candidate.

The method emphasizes concise task context, static data previews, measured
validation scores, and choosing the best solution based on the objective
function rather than narrative confidence.

Known limitations include local optima, repeated local patches, benchmark/data
contamination concerns, and dependence on the available runtime and objective
metric.

# Locked Task Prompt

# AIDE-T2 Locked Task Prompt

You are given a weak AIDE-style baseline for a Kaggle-style tabular ML task.
The workspace contains:

- `train.csv`: labeled training rows.
- `validation_features.csv`: validation rows without labels.
- `weak_script.py`: the weak starting script.
- `error_or_score_feedback.md`: objective feedback for the weak script.
- `baseline_score.json`: the weak-script validation score (0.499712).

Write an improved Python script that reads `train.csv` and
`validation_features.csv`, uses the feedback, and writes `submission.csv` with
columns `PassengerId` and `Transported`.

Keep the change focused, log assumptions in comments only when needed, and do
not request hidden labels.

# Output Contract

Return exactly one Python code block. The script must run from the provided starter workspace and create `submission.csv` with `PassengerId` and `Transported` columns.
