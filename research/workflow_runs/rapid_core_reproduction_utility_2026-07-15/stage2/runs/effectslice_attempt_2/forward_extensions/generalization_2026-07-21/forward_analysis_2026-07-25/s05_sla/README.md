# Section 05: SLA Sensitivity And Leave-One-Block-Out

This section computes the frozen six-block decision for each of the 24 DeepSeek
primary tasks, then keeps four descriptive sensitivity families separate from
that registered result.

## Reproduce

```powershell
python .\analyze_sla_sensitivity.py
python .\verify_sla_sensitivity.py
```

Outputs include the 24 registered decisions, an 81-profile total-gate grid, nine
per-registry one-at-a-time profiles, five margin-tolerance profiles, all 144
registered leave-one-block-out recomputations, and task-level stability data.

Only `registered_task_decisions.csv` contains registered decisions. Sensitivity
profiles cannot replace, select, or rescue those decisions.
