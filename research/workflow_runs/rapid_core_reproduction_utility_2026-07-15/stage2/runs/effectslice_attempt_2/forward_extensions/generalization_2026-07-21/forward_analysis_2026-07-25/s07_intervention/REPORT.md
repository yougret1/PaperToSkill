# Section 07 Report: Focused Atom Restore/Drop Intervention

## Question and Frozen Design

This successor asks whether a registered atom that directly describes the hard
contract is locally necessary for success and whether restoring it to the slice
rescues failure. It does not modify FG3, FG4, FG5, or Sections 01-06.

The frozen grid contains four representative tasks, one per domain, registries
A and B, and six arms: `F`, `S`, `F_drop_critical`,
`F_drop_noncritical`, `S_restore_critical`, and
`S_restore_noncritical`. This produces 48 cells. The critical intervention uses
atom index 10 (no input mutation and stable ordering); the comparator uses atom
index 8 (no external resources). Singleton intervention arms may break DAG
closure and therefore are causal probes, not reducer outputs.

All calls used `deepseek-v4-flash`, temperature 0, top-p 1, an 8,192 output-token
cap, and no provider seed. The registration was committed and privately pushed
before dispatch. A completed provider response was never replayed.

## Run Integrity

All 48 registered cells reached one terminal result on the first transport
attempt. There were 23 operational successes, 23 semantic hard-contract
failures, and two malformed/no-submission results. No credential value was
recorded and no dispatch is incomplete.

Both malformed rows are `SE-PE-01`, registry B: `F` and
`F_drop_critical`. In each case the provider consumed all 8,192 output tokens in
reasoning, returned finish reason `length`, and emitted zero canonical-output
bytes. These are completed provider responses with no final submission. The
frozen no-replay rule therefore prohibits rerunning them.

## Arm Results

| Arm | Success | Semantic hard failure | Invalid | Success rate on fixed grid |
|---|---:|---:|---:|---:|
| `F` | 4 | 3 | 1 | 0.500 |
| `S` | 5 | 3 | 0 | 0.625 |
| `F_drop_critical` | 3 | 4 | 1 | 0.375 |
| `F_drop_noncritical` | 4 | 4 | 0 | 0.500 |
| `S_restore_critical` | 2 | 6 | 0 | 0.250 |
| `S_restore_noncritical` | 5 | 3 | 0 | 0.625 |

## Paired Contrasts

The fixed-grid ITT estimate retains every registered unit and counts a
malformed/no-submission endpoint as non-success. The valid-pair estimate excludes
a task-registry pair whenever either contrast endpoint is not an operational
success, semantic hard-contract failure, or score shortfall.

| Contrast | ITT units | ITT success delta | Valid units | Valid-pair success delta | Exact sign-test p (valid) |
|---|---:|---:|---:|---:|---:|
| Critical necessity: `F - F_drop_critical` | 8 | +0.125 | 7 | +0.143 | 1.000 |
| Comparator necessity: `F - F_drop_noncritical` | 8 | 0.000 | 7 | +0.143 | 1.000 |
| Critical rescue: `S_restore_critical - S` | 8 | -0.375 | 8 | -0.375 | 0.250 |
| Comparator rescue: `S_restore_noncritical - S` | 8 | 0.000 | 8 | 0.000 | 1.000 |

The apparent ITT selectivity for critical deletion is created by the invalid
`SE-PE-01` registry-B endpoints. On valid pairs, critical and comparator deletion
have the same mean effect, each driven by the single `AGENT-TF-01` registry-A
pair. Across seven units with all four contrasts valid, the necessity
delta-of-deltas is 0.000.

Restoring the selected critical atom does not rescue the slice in this probe.
It changes three of eight valid units from success to semantic hard-contract
failure (`AGENT-TF-01` A and B; `SE-PE-01` B), for a mean success delta of
-0.375. The comparator restore has one improvement and one worsening, giving a
net delta of 0.000. The critical rescue sign test is not significant at this
sample size (`p = 0.250`).

## Claim Boundary and Use

This experiment supplies local intervention evidence, not broad causal proof.
It does not support the claim that the selected critical atom is selectively
necessary, nor that singleton restoration reliably repairs a reduced prompt.
It instead shows that adding one apparently important atom can interact
negatively with the remaining slice, and that atom importance cannot be inferred
from direct hard-contract wording alone.

Only four tasks, two registries, one model route, and one terminal provider
response per cell were tested. There is no provider seed and no multi-seed
replication. The paper may report this as a focused negative ablation with both
ITT and valid-pair estimates, but must not present it as a general restore
mechanism or as evidence of repeatability.

## Verification

- `verify_run_artifacts.py`: PASS; 48 terminal rows, zero incomplete dispatches,
  one transport attempt per row, and no credential value recorded.
- `verify_intervention_results.py`: PASS; eight outputs reproduced byte for
  byte, invalid endpoints checked, and ITT/valid-pair contracts checked.
- Machine-readable sources: `outputs/analysis.json`, `outputs/row_results.csv`,
  `outputs/contrast_units.csv`, and `outputs/contrast_summary.csv`.
