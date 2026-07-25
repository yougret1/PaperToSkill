# Section 07 Run Log

## 2026-07-25: Pre-Call Design

- Scope: four tasks (`NLP-LLM-01`, `SE-PE-01`, `DATA-HDB-01`, and
  `AGENT-TF-01`), two registries, six arms, 48 registered DeepSeek calls.
- Critical atom: index 10, covering no input mutation and deterministic
  ranking/traversal ties; direct hard-contract mappings are task-specific and
  frozen in the registry.
- Noncritical comparator: index 8, covering external-resource exclusion with no
  direct scorer hard-contract identifier.
- Protocol: corrected FG5 explicit case interface, exact output contract, and
  strict JSON submission envelope; `deepseek-v4-flash`, temperature 0, top-p 1,
  8,192 output-token cap, no API seed.
- Order: deterministic SHA-256 ordering over task, registry, and arm.
- Retry policy: at most five transport attempts; completed semantic responses
  are never replayed.
- Frozen predecessors: FG3, FG4, FG5, and Sections 01-06 are read-only inputs.

## Deferred By Time Constraint And Not Executed In This Goal

These items remain at the bottom of `CHECKLIST.md`, in priority order, with the
note "准备时间多的话再去做":

1. Additional compression points and Pareto analysis.
2. Additional publication-figure implementation and visual polishing.
3. FG6 comprehensive multi-seed experiment.

## 2026-07-25: Execution

- The frozen registration was committed as `ab4cbc13` and privately pushed
  before provider dispatch.
- All 48 registered DeepSeek cells reached a terminal result on their first
  transport attempt; no completed response was replayed.
- Terminal outcomes: 23 operational successes, 23 semantic hard-contract
  failures, and two malformed/no-submission results.
- The two malformed rows were `SE-PE-01` registry-B `F` and
  `F_drop_critical`. Both ended with provider finish reason `length` after 8,192
  output tokens and emitted an empty canonical submission. They remain frozen
  terminal results under the no-replay policy.
- No credential value was recorded; all 48 dispatches are complete.

## 2026-07-25: Analysis and Claim Decision

- Analysis reports both fixed-grid ITT and valid-pair estimates. ITT retains
  malformed/no-submission endpoints as non-success; valid-pair analysis excludes
  a contrast whenever either endpoint is not a semantic experimental outcome.
- Critical necessity: ITT `+0.125` over 8 units; valid-pair `+0.142857` over 7.
- Noncritical-comparator necessity: ITT `0.000` over 8 units; valid-pair
  `+0.142857` over 7. The valid necessity delta-of-deltas is therefore `0.000`.
- Critical rescue: `-0.375` over all 8 valid pairs, with 0 improvements and 3
  worsenings (two-sided exact sign `p=0.250`).
- Noncritical-comparator rescue: `0.000` over all 8 valid pairs, with one
  improvement and one worsening.
- Claim decision: do not claim selective necessity or reliable singleton rescue.
  Report the result as a focused negative intervention showing contextual atom
  interaction. Scope remains four tasks, two registries, one model route, no API
  seed, and no multi-seed replication.

## 2026-07-25: Verification

- `verify_run_artifacts.py`: PASS; 48 terminal rows, zero incomplete dispatches,
  all transport-attempt counts equal 1, and no credential value recorded.
- `verify_intervention_results.py`: PASS; eight outputs reproduced byte for
  byte, two invalid endpoints verified as length-exhausted empty submissions,
  and ITT/valid-pair unit contracts verified.
- Full interpretation and manuscript boundary: `REPORT.md`.
