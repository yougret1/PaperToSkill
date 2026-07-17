# Toolformer Loss-Filter Paper-Core Reproduction Design

## Decision

Build one locked numerical implementation task for Toolformer's self-supervised
API-call filtering rule. The task tests whether a source-grounded paper artifact
helps an API-hosted model reproduce the paper's weighted future-token loss,
counterfactual baseline, and threshold decision on an ordinary API-first
workstation.

This is the second objective paper-core task in the EffectSlice Stage 2 run. It
reuses the SNAP-MFSE experimental harness and statistical gates but has an
independent paper oracle, case registry, scorer, workspace, and source atom map.
The design is selected autonomously under the user's instruction to continue
until a high-quality manuscript exists. No Git commit or push is part of the
work.

## Alternatives Considered

1. Reproduce the complete Toolformer data-generation and GPT-J fine-tuning
   pipeline. This is closest to the full paper but requires a large corpus,
   pretrained model weights, multiple tool backends, and training compute. It
   would confound the core filtering equation with infrastructure and is not a
   low-cost paper-core reproduction.
2. Reproduce inference-time interruption when the model emits the API result
   token. This is inexpensive but mostly a state-machine integration task and
   does not test the paper's central self-supervised selection mechanism.
3. Reproduce the loss-filter core. This is selected because the paper gives an
   exact formula, counterfactual comparator, threshold, and time-weighting
   schedule. It supports an independent oracle and falsifiable hidden cases
   without claiming full model training results.

## Source Boundary

- Paper text: `papers/extracted/toolformer.txt`.
- API-call filtering equations and explanation: lines 134-171.
- Experimental normalized weight schedule: lines 268-272.
- Existing broad paper artifact: `generated_skills/toolformer/SKILL.md` and its
  source map.

The task target is the filtering method described by these paper spans. It does
not reproduce candidate-call sampling, external API execution, corpus
augmentation, GPT-J fine-tuning, or downstream benchmark results.

## Locked Task

The starter repository exposes one incomplete function:

```python
def filter_useful_api_calls(
    logp_with_result: numpy.ndarray,
    logp_call_only: numpy.ndarray,
    logp_no_call: numpy.ndarray,
    tau_filter: float,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    ...
```

Each matrix has shape `(n_candidates, horizon)` and contains finite token log
probabilities. The function returns a Boolean keep mask and one utility margin
per candidate. It rejects non-2D, empty, shape-mismatched, nonfinite, positive
log-probability inputs and a nonfinite or negative threshold. The task prompt
states the interface and validation contract but omits the paper equations.

## Paper Oracle

For future-token offset `t`, define and normalize the paper's experimental
weight schedule:

```text
raw_t = max(0, 1 - 0.2 t)
w_t = raw_t / sum_s raw_s
```

For each candidate, compute weighted negative log likelihood for:

- the API call with its result, `L_plus`;
- no API call, `L_empty`; and
- the API call without its result, `L_call_only`.

Then compute:

```text
L_minus = min(L_empty, L_call_only)
margin = L_minus - L_plus
keep = margin >= tau_filter
```

The inclusive threshold is frozen. Log probabilities after the weight support
becomes zero do not affect the result. The oracle is independent of candidate
code and never enters model-visible feedback.

## Source-Grounded Artifact

Create five dependency-ordered atoms:

1. `T01`: normalize the paper's decreasing finite-support weight schedule.
2. `T02`: compute weighted future-token negative log likelihood.
3. `T03`: use the minimum of no-call and call-only counterfactual losses.
4. `T04`: compute the improvement margin and apply the inclusive threshold.
5. `T05`: batch the rule, validate numerical inputs, and return mask plus
   margins without changing the paper decision.

Dependencies form `T01 -> T02 -> T03 -> T04 -> T05`. Strict dependency-closed
slices are the four nonempty prefixes below the complete artifact.

## Case Registry And Scoring

Freeze deterministic, disjoint blocks before provider calls:

- development: 4 cases;
- eligibility: 21 cases;
- discovery: 16 cases;
- confirmation: 59 cases.

Cases cover variable horizons, zero-weight tails, comparator reversals,
threshold ties, near-threshold margins, batched candidates, and invalid input
contracts. The scorer applies a candidate patch in an isolated workspace,
compares mask and margins with the independent oracle, and returns only
aggregate public feedback. Raw case vectors remain private evidence. No
self-reported metric is accepted.

## Experimental Conditions

- `B`: bounded ACI and locked task without a paper artifact.
- `F`: the same ACI and task with the complete Toolformer execution card.
- `S`: one frozen strict dependency-closed prefix.

DeepSeek-family (`deepseek-v4-flash`, user-facing service name DeepSeek V3.2)
is primary. GPT-family may be used only for development robustness. The local
computer performs orchestration, tool execution, scoring, and persistence;
model inference comes from the trusted vendor API. No local accelerator is
required.

Use 16 model-visible actions, provider output budget v2, and harness v2 terminal
scoring. Network retries remain in one lineage and are capped at five.

## Admission And Sealing

1. Development may authorize but never establish eligibility.
2. The primary model must show a positive B/F development signal.
3. Frozen eligibility uses 21 cases and the existing exact-binomial gate.
4. Discovery evaluates strict prefixes in retained-count order using the frozen
   equivalence margin and complete deletion-closure audit.
5. After one candidate is locked, a confirmation family binds B/F/S, the
   selected artifact, all digests, 59 sealed cases, and statistical hypotheses.
6. Confirmation requires zero S/F mismatches, beneficial S/B prevalence,
   contract success, and the registered exact confidence bounds.

Raw bundles are immutable. Provider, harness, or execution failures are
classified and cannot be converted into model failures or positive evidence.

## Claim Boundary

A passing task supports only this statement: on the registered Toolformer
loss-filter implementation task and case distribution, the source-grounded
artifact or a certified slice changed the probability of reproducing the
paper's filtering rule under the stated model and action budget.

It does not reproduce full Toolformer training, show downstream tool-use gains,
establish that the weighting schedule is optimal, or prove EffectSlice works
for arbitrary papers.

## Test Plan

Implementation follows TDD. Tests cover exact weights, losses, comparator and
tie semantics; invalid inputs; deterministic case blocks and digests; known
correct and deliberately wrong patches; hidden-feedback sanitization; runner
manifests and credential exclusion; development, eligibility, discovery, and
confirmation analyzer boundaries; and full-suite regression.

## Self-Review

- No placeholders or unresolved choices remain.
- Task scope, oracle, artifact atoms, cases, and claims use the same filtering
  definition.
- The task is one bounded subsystem and reuses existing provider/harness code.
- "Paper-core reproduction" explicitly excludes model training and downstream
  performance, preventing two interpretations of success.
