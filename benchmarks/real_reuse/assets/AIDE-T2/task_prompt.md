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
