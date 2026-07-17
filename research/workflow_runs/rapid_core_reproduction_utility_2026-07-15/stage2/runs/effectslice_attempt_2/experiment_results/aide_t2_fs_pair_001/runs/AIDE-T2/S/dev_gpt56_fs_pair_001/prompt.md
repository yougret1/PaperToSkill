You are running a locked EffectSlice development task. Use only the procedural context and task prompt below. Do not request or invent hidden validation labels.

# Procedural Context

# AIDE Task-Local Procedural Slice



1. Model the task as optimization over a solution space of Python scripts, with a stateless objective function such as validation accuracy or loss. Each candidate solution can be evaluated independently and compared. Source anchors: lines 91-102.

5. Implement the coding operator with three specialized actions: drafting a single-file program from scratch, debugging by inspecting error logs and traces while preserving the approach, and improving a valid solution with one atomic measurable change. Source anchors: lines 167-199.

7. Include a static data preview with dataset size, column names, or data splits so coding prompts can make validation and hyperparameter decisions without a full EDA pipeline. Source anchors: lines 213-217.

- The Kaggle protocol splits training data into train and holdout test sets, prompts AIDE to produce `submission.csv`, and reports Exceeds % of Human and Above Median metrics. Source anchors: lines 252-280.

- Check whether the target harness supports the tools assumed by the paper.

- Replace framework-specific commands with local equivalents before execution.

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
