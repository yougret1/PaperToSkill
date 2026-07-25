# Section 01: F/S/B Paper-Task Effects

This section analyzes the frozen 432-row primary subset only:

- 12 papers, with two nested tasks per paper;
- four domains, with three papers per domain;
- six paired blocks per task;
- B, F, and S conditions;
- the `deepseek_primary` model slot and `primary_dag_ratio_60_v1` variant.

The paper is the independent unit. Task effects average the six paired block
differences, paper effects average the two nested task effects, and the overall
effect weights the four domain means equally. The 10,000 paper-stratified
bootstrap replicates use seed `20260721`. Their intervals are registered-benchmark
sensitivity intervals, not population confidence intervals.

Run from this directory with the existing base Python environment:

```powershell
python .\analyze_primary_effects.py
python .\verify_primary_effects.py
```

The supported result is that both F and S outperform B on operational success and
private score. The current data do not support a reliable S-over-F success claim.
