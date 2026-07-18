# EffectSlice Confirmation V3 Design

## Status and Authorization

This design continues the user-authorized Stage 2 iteration inside
`D:\a_work\gitee\PaperToSkill`. It uses the user-supplied endpoint labeled
DeepSeek V3.2, whose request alias is `deepseek-v4-flash`. A commodity PC runs
orchestration, code execution, scoring, integrity checks, and evidence storage;
model inference stays at the vendor endpoint. No local model or GPU inference is
part of the design.

Confirmation v2 raw artifacts are immutable. V3 writes to new artifact, raw,
derived, and report paths.

## Problem to Repair

Confirmation v2 established two defensible negative results, but the final
review identified four blockers:

1. Fresh provider conversations were described as statistically independent
   even though the provider does not attest independent sampling.
2. Three marginal prevalence criteria did not directly gate one joint
   substitution event.
3. Both real candidates were rejected, so the protocol had no positive
   calibration showing that it can admit a known valid strict subset.
4. The raw-to-derived integrity audit did not hash every final transcript,
   patch, run result, summary, and figure.

V3 is a calibration iteration, not a general effectiveness study. It must fix
these blockers before API budget is spent on broader paper-task coverage.

## Considered Approaches

### A. Minimal calibration first (selected)

Reuse the Toolformer task, scorer, runner, and complete artifact. Add an exact
artifact identity calibration and a planted-redundancy strict-subset control,
then reanalyze the v2 prefix-01 candidate as a negative control. This costs at
most 72 new provider conversations and directly tests whether the admission
rule can both accept and reject.

### B. Immediate broad benchmark expansion

Build four to six new paper-task families and optionally add a second vendor
API. This offers stronger external validity but risks multiplying an
uncalibrated protocol defect and substantially increases task-contract and API
cost.

### C. Audit-only manuscript

Run no new experiments and reframe the paper around scorer leakage and
case-level pseudoreplication. This preserves a valid negative-result paper but
does not address the reviewers' central concern that the gate may be
structurally unable to admit.

Approach A is the smallest experiment that carries the paper's central claim.

## Experimental Objects

### Negative control: existing unstable strict subset

- Task: Toolformer filtering.
- Complete artifact: current five-unit artifact `T01` through `T05`.
- Slice: frozen v2 `prefix_01`, containing only `T01`.
- Evidence: existing confirmation v2 bundles, with no new provider calls.
- Expected outcome: rejected by the v3 joint event.

### Identity calibration

- Task: Toolformer filtering.
- `F` and `S` inject byte-identical copies of the current complete artifact.
- `B` injects no paper-derived procedure.
- Six registered B/F/S blocks use all six condition orders once.
- This is descriptive instrumentation calibration, not a strict-subset
  admission claim and not a prevalence estimate.
- Expected outcome: F/S differences should expose only fresh-session
  variability, not an artifact difference or condition-label prompt change.

### Planted-redundancy positive control

- Task: Toolformer filtering.
- `F+` contains the current five source-grounded units plus one registered
  source-grounded redundant unit that restates an already required invariant.
- `S` is the original five-unit complete artifact and is therefore a strict,
  dependency-closed subset of `F+`.
- A new deterministic 64-case registry is generated and frozen before any v3
  provider call. It must vary the same contract dimensions without copying the
  v2 registry byte-for-byte.
- Eighteen registered B/F+/S blocks use all six condition orders three times in
  a frozen shuffled schedule.
- Expected outcome: admission. Failure is retained and triggers protocol
  recalibration or an audit-only paper; thresholds are not changed post hoc.

## Joint Admission Event

For registered block `r`, define one primary event:

```text
J_r = B fails
      AND F succeeds
      AND S succeeds
      AND q_S >= q_F - 0.05
      AND all required hard contracts pass
      AND the block integrity audit passes
```

This definition repairs three v2 problems:

- It gates one joint substitution event instead of conjoining three marginal
  prevalence statements.
- It does not call joint failure "preservation."
- A slice that outperforms F is not rejected merely because the absolute score
  gap exceeds 0.05.

The planted control is admitted only when all 18 registered `J_r` values are
one. This is first a deterministic decision on a finite registered schedule.
The one-sided Clopper-Pearson value for 18/18 may be reported only as an
`iid-conditional reference calibration`; it is not an unconditional provider
population guarantee. The manuscript must use `fresh provider conversation`
and `registered matched block`, never assert that independence was verified.

The previous full-benefit, concordance, and slice-benefit counts remain
diagnostics. They are not separate admission gates.

## Rule Comparison

The final analysis compares three decision rules without fabricating new data:

1. `development_selection_only`: accepts a candidate after its discovery run.
2. `adaptive_case_level`: records what the contaminated historical protocol
   would have concluded, labeled invalid and excluded from confirmation.
3. `registered_joint_schedule`: uses the v3 joint event and preserves every
   registered failure.

The comparison is successful only if the registered joint rule rejects the v2
negative control and admits the planted positive control. The identity
calibration must not be counted as a strict-subset admission.

## Provider and Failure Policy

- Provider/user label: DeepSeek V3.2.
- Exact request alias: `deepseek-v4-flash`.
- Wire API: the already validated OpenAI-compatible vendor endpoint.
- Temperature: zero; no provider seed is claimed.
- Maximum transport attempts: five per model turn.
- Exhausted turns, missing patches, hard-contract failures, and scheduler
  failures remain in the registered denominator and are never replaced.
- Every condition starts a fresh conversation, but fresh does not imply
  statistically independent.

## Artifact and Integrity Design

V3 uses new versioned paths under the existing run directory:

```text
artifacts/toolformer_filter/confirmation_v3/
experiment_results/confirmation_v3/
derived/confirmation_v3/
figures/confirmation_v3/
```

Each family manifest binds the task prompt file bytes, canonical prompt text,
workspace tree, F artifact, S artifact, source map, case registry, scorer,
runner, scheduler, analyzer, thresholds, schedule, provider label, and request
alias. File-byte and canonical-text prompt hashes use different field names.

Every completed bundle receives a derived hash ledger covering:

- pair manifest;
- each condition's transcript;
- candidate patch;
- run result;
- scorer call artifacts;
- task summary;
- final table data;
- final figure.

The legacy v2 `comparison_role=development_triage` metadata defect is documented
but never edited. V3 uses a confirmation-specific role and evidence boundary.

## Implementation Boundaries

- Add v3-specific builder, scheduler, analyzer, and ledger code rather than
  changing v2 raw files or their frozen family definitions.
- Reuse the existing ACI runner and Toolformer scorer when their registered
  bytes remain appropriate; any changed executable receives a new v3 digest.
- Use write-once creation for family manifests and raw bundles.
- Derived outputs may be regenerated into versioned directories.
- No project memory files are created or updated.

## Test Plan

Implementation is test-driven. Tests must cover:

1. the exact joint-event truth table, including common failure and S-better-than-F;
2. six-order balancing for identity calibration and 18-block balancing for the
   planted control;
3. distinct file-byte and canonical-text prompt hashes;
4. confirmation-specific metadata roles;
5. write-once raw output and failure preservation;
6. analyzer rejection of missing, duplicate, or replaced registered blocks;
7. ledger verification and tamper detection for transcript, patch, result,
   summary, and figure;
8. deterministic reanalysis of the existing v2 negative control.

## Decision Gate and Next Iteration

V3 calibration passes only when:

- all registered bundles are preserved or explicitly failed;
- every integrity and hash-ledger check passes;
- the existing prefix-01 negative control is rejected;
- the planted-redundancy strict subset is admitted; and
- the identity calibration is reported separately without being counted as a
  strict-subset success.

If calibration passes, the next design expands to additional paper-task
families and stronger candidate/rule baselines. If it fails, the paper is
reframed as an audit/negative-result study or the protocol is redesigned before
any broad benchmark run. No threshold is changed after viewing v3 outcomes.

## Non-Claims

V3 does not establish cross-paper effectiveness, human benefit, local-model
inference, provider independence, reducer superiority, cost savings, or broad
commodity-hardware coverage. Those require later experiments.
