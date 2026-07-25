# Section 07: Four-Domain Atom Restore/Drop Intervention

This forward successor tests atom-level necessity and rescue without changing
FG3, FG4, FG5, or Sections 01-06. It uses one representative task from each of
four domains, registries A and B, and six arms per task-registry unit.

The critical atom is the common no-input-mutation and stable-order operational
rule at atom index 10. It maps directly to registered hard contracts. The
noncritical comparator is the no-external-resource boundary at atom index 8;
it remains a legitimate registered constraint but does not name a scorer hard
contract.

## Registered Contrasts

- `F` versus `F_drop_critical`: critical-atom necessity.
- `F` versus `F_drop_noncritical`: lower-directness necessity comparator.
- `S_restore_critical` versus `S`: critical-atom rescue.
- `S_restore_noncritical` versus `S`: lower-directness rescue comparator.

All four DAGs are 12-atom chains. Therefore, a singleton deletion or a
non-prefix singleton restore can break dependency closure. The registration
marks those arms explicitly as causal interventions rather than reducer
outputs. Frozen `F` and `S` remain dependency-closed baselines.

## Execution Order

```powershell
python -B .\intervention_successor.py build
python -B .\intervention_successor.py verify
# Commit and privately push the frozen registration before the next command.
python -B .\run_intervention_successor.py --docs-dir <local-api-document-directory>
python -B .\verify_run_artifacts.py
python -B .\analyze_intervention_successor.py
python -B .\verify_intervention_results.py
```

The runner allows at most five transport attempts and never replays a completed
semantic response. The registered DeepSeek route has no API seed field;
temperature is 0 and top-p is 1. This is a focused intervention, not FG6 or a
comprehensive multi-seed experiment.
