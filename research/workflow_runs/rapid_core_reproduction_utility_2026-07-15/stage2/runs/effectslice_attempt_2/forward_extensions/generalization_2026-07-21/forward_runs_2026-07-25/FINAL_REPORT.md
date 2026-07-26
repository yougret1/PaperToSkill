# Controls-v2 and FG6-FG8 Final Experimental Report

Date: 2026-07-26

Branch: `codex/effectslice-v3`

This report closes exactly four forward experiments: Controls-v2 and the FG6,
FG7, and FG8 independent exact-protocol repetitions. FG3-FG5 are immutable
inputs. No result was removed because it was unfavorable, and retryable
transport states were retried rather than recorded as experimental outcomes.

## Executive Findings

1. Controls-v2 passed all 40 deterministic boundary cells. Its confusion matrix
   contains only correct cells: 24 Admit, 8 Reject, and 8 Invalid.
2. The exact-contract-removal negative control produced 0/24 operational
   successes and matched its registered negative direction in 24/24 rows.
3. The identity control exactly matched the full-reference arm descriptively:
   both produced 8/24 operational successes and a valid-row mean private score
   of 0.532552.
4. FG6, FG7, and FG8 each contain exactly 1,296 registered terminal rows. The
   combined denominator is 3,888, with no retryable network state persisted as
   a terminal outcome.
5. After averaging repetitions within each of the 24 paper-task units, F-B is
   0.262297 (approximate 95% CI [0.142371, 0.382224]) and S-B is 0.297779
   ([0.160973, 0.434585]). Both contrasts are consistently positive.
6. S-F is 0.035482 (approximate 95% CI [-0.000777, 0.071741]). The interval
   crosses zero, so these experiments do not support a claim that S is better
   than F.
7. The frozen primary decision agrees in all three repetitions for 20/24
   paper-task units (83.33%). Four units cross the Admit/Reject boundary.

## Controls-v2

Controls-v2 has two distinct layers and should be interpreted accordingly.

The deterministic layer tests the frozen admission logic against known labels;
it is a protocol-correctness check, not an LLM performance experiment. All
40/40 registered cells passed.

The model-mediated layer contains 96 registered calls: four domain anchors,
two registries, four control arms, and three independent repetitions. All 96
registered rows are present and valid. The terminal outcomes are 23 operational
successes, 71 hard-contract failures, and 2 malformed/no-submission outcomes.

| Arm | Rows | Successes | Mean private score | Direction matches |
|---|---:|---:|---:|---:|
| F reference | 24 | 8 | 0.532552 | 8/24 |
| F identity | 24 | 8 | 0.532552 | 8/24 |
| Redundancy removed | 24 | 7 | 0.490885 | 7/24 |
| Exact contract removed | 24 | 0 | 0.000000 | 24/24 |

Across the 32 task-registry-arm cells, all three terminal states agree in
26/32 cells (81.25%). The six unstable cells are the redundancy-removal arm for
both NLP registries, the redundancy-removal arm for both SE registries, and the
F-reference and F-identity arms for the SE registry-B cell. This instability
must be reported alongside the favorable deterministic and destructive-control
results.

Recommended paper interpretation: the frozen admission boundary recognizes all
known deterministic labels, preserves an identity transformation, and detects
the preregistered destructive removal. Controls-v2 does not by itself establish
cross-paper utility or model generalization; those claims depend on the
paper-task experiments.

## Exact-Protocol Repetitions

| Repeat | Rows | Valid | Technical invalid | Success | Hard contract | Integrity/digest | Malformed |
|---|---:|---:|---:|---:|---:|---:|---:|
| FG6 | 1,296 | 1,136 | 160 | 388 | 668 | 160 | 80 |
| FG7 | 1,296 | 1,136 | 160 | 365 | 681 | 160 | 90 |
| FG8 | 1,296 | 1,228 | 68 | 405 | 725 | 68 | 98 |
| Total | 3,888 | 3,500 | 388 | 1,158 | 2,074 | 388 | 268 |

The counts above retain technical Invalid rows in every registered denominator.
An operational failure is not automatically a protocol failure: hard-contract,
integrity/digest, and malformed/no-submission outcomes identify different
terminal mechanisms and should be shown separately in the paper.

### Primary Effects

| Repeat | F-B | S-B | S-F | Decisions |
|---|---:|---:|---:|---:|
| FG6 | 0.263346 | 0.311198 | 0.047852 | 3 Admit / 21 Reject |
| FG7 | 0.270833 | 0.295356 | 0.024523 | 6 Admit / 18 Reject |
| FG8 | 0.252713 | 0.286784 | 0.034071 | 3 Admit / 21 Reject |
| Paper-task-averaged | 0.262297 | 0.297779 | 0.035482 | 20/24 stable |

The independent statistical unit is the paper-task, not an execution row.
Repetitions are averaged within each paper-task before the 24-unit interval is
computed. This prevents the 3,888 execution rows from being treated as 3,888
independent samples.

The four decision-unstable units are:

| Paper-task | FG6 | FG7 | FG8 |
|---|---|---|---|
| NLP-LL2-01 | Reject | Admit | Admit |
| NLP-LLM-01 | Reject | Admit | Reject |
| NLP-LLM-02 | Reject | Admit | Reject |
| SE-CR-01 | Admit | Admit | Reject |

Across all 1,296 logical grid cells, condition-success status agrees across all
three repetitions for 919 cells (70.91%), while the finer terminal-outcome class
agrees for 780 cells (60.19%). This is compatible with a stable aggregate effect
and a conservative frozen decision boundary, but it also shows material
row-level stochasticity.

## Model and Family Stability

Model groups are not balanced for performance comparison. DeepSeek covers 816
logical cells, while each other model covers 96; DeepSeek also spans more
execution families. The table below is therefore a within-cell repeatability
description, not a model leaderboard.

| Model slot | Logical cells | Success agreement | Terminal agreement |
|---|---:|---:|---:|
| Claude 4.7 | 96 | 58.33% | 57.29% |
| DeepSeek | 816 | 74.63% | 57.97% |
| GPT-5.5 | 96 | 73.96% | 73.96% |
| GPT-5.6 Luna | 96 | 64.58% | 62.50% |
| GPT-5.6 Sol | 96 | 61.46% | 61.46% |
| GPT-5.6 Terra | 96 | 64.58% | 64.58% |

The primary family has the highest condition-success agreement (85.19%). The
structural ladder has the lowest condition-success agreement (56.25%) and
terminal agreement (47.22%), making it the clearest target for later diagnostic
work rather than a basis for a strong positive claim.

## What the Evidence Supports

The strongest supported claim is that the frozen protocol repeatedly separates
both F and S from B at the paper-task level. The deterministic controls and the
exact-contract-removal negative support boundary correctness. The 20/24 primary
decision agreement supports a qualified stability claim.

The evidence does not support claiming that S significantly outperforms F,
that all paper-task units are stable, or that one provider is superior to
another. It also does not turn low admission rates into evidence of model
quality; low admission is consistent with a conservative protocol but must be
reported together with the failure decomposition.

## Limitations

- FG6-FG8 are independent exact-protocol repetitions, not API-controlled random
  seed runs. No random-seed reproducibility claim is made.
- Provider/model coverage is unequal, so aggregate model success rates are
  confounded by execution-family coverage.
- Four of 24 primary paper-task decisions are unstable across repetitions.
- Technical Invalid rates differ across repetitions, especially between FG6/7
  and FG8, although all Invalid rows remain in the registered denominators.
- Controls-v2 contains only four domain anchors and 32 repeated logical cells;
  its 81.25% terminal-state agreement is descriptive rather than a precision
  estimate for all future controls.
- The approximate intervals use a normal approximation over 24 paper-task units.

## Verification Closure

- Controls-v2, FG6, FG7, and FG8 completion verifiers were rerun after all
  terminal work finished. Each verifier passed exact registration/result/
  metadata/marker set equality, strict result binding, and the ban on retryable
  transport states as terminal outcomes.
- The joint analysis was regenerated after the completion verifiers and again
  returned exactly 3,888 rows and the effects reported above.
- All 7 focused artifact-safety tests passed.
- A final scoped safety audit enumerated 35,200 files across the four experiments,
  analyses, verification records, source, and reports. It found zero exact
  credential reflections, zero generic credential-pattern matches outside
  opaque ciphertext, and zero forbidden local-model-design markers.

## Paper-Facing Analysis Recommendation

1. Lead with the paper-task-averaged F-B and S-B effects and their intervals.
2. Report S-F with its zero-crossing interval to avoid an unsupported dominance
   claim.
3. Pair the 20/24 primary-decision agreement with the four unstable units.
4. Present the four-way terminal failure decomposition rather than a single
   success/failure bar.
5. Use Controls-v2 as boundary validation: deterministic confusion matrix,
   identity invariance, destructive-control detection, and 26/32 repeatability.
6. Put the model table in an appendix or label it explicitly as within-cell
   repeatability because coverage is unbalanced.

## Primary Artifacts

- Checklist: `CHECKLIST.md`
- Chronological log: `RUN_LOG.md`
- Controls-v2 verification: `verification/controls_v2.json`
- FG6-FG8 verification: `verification/fg6.json`, `verification/fg7.json`, and
  `verification/fg8.json`
- Controls-v2 analysis: `analysis/controls_v2/analysis.json`
- Per-repeat analyses: `analysis/full_grid/fg6.json`, `fg7.json`, and `fg8.json`
- Joint analysis: `analysis/full_grid/analysis.json`
- Joint concise report: `analysis/full_grid/REPORT.md`
- Joint analysis implementation: `successor_full_grid_analysis.py`

## Git Evidence

| Artifact stage | Evidence commit | Closure-log commit |
|---|---|---|
| Controls-v2 | `912edd61` | included in evidence commit |
| FG6 | `ac6228a5` | `396a8d08` |
| FG7 | `6904601e` | `2624e05a` |
| FG8 | `6be61703f` | `2e5747ae9` |
| Joint analysis and final report | `PENDING_FINAL_EVIDENCE_COMMIT` | current branch head after closure |

All listed commits are on the private `origin/codex/effectslice-v3` branch.
