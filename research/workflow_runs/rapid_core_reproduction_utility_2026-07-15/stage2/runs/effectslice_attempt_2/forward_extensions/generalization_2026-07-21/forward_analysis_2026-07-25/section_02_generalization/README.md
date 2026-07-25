# Section 02: Generalization and Interactions

This section has two deliberately separate scopes:

1. The registered primary analysis covers 12 papers and 24 nested tasks with
   `deepseek_primary`.
2. Model and reducer robustness covers four shared anchor tasks, one per domain,
   with six paired blocks per task. It must never be described as 24-task model
   coverage.

Run:

```powershell
python .\analyze_generalization.py
python .\verify_generalization.py
```

The output includes a 432-cell paper-task-condition heatmap table, domain and
registry effects, model-task and reducer-task effects, and leave-one-paper,
leave-one-model, and leave-one-anchor-task sensitivity diagnostics.

Provider-family comparisons are descriptive because provider family is
confounded with model identity. The four-anchor model and reducer results are
sensitivity evidence, not population inference.
