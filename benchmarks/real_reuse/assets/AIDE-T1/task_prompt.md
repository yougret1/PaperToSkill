# AIDE-T1 Locked Task Prompt

You are solving a Kaggle-style tabular ML task under a local validation split.
The workspace contains:

- `train.csv`: labeled training rows.
- `validation_features.csv`: validation rows without labels.
- `baseline_submission.csv`: a majority-class starter submission.
- `baseline_score.json`: the starter validation score (0.499712).

Write a complete Python script that reads `train.csv` and
`validation_features.csv`, trains or applies a measurable model, and writes
`submission.csv` with columns `PassengerId` and `Transported`.

Use an AIDE-style loop mentally: inspect the data columns, propose a candidate,
respect the objective metric, and prefer measured validation improvement over
unsupported claims. Do not request hidden labels.
