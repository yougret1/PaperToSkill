# EffectSlice PAC Confirmation Protocol

## Scope

This document replaces the infeasible mean-Hoeffding equivalence design for new
Stage 2 attempts. It does not reinterpret or overwrite `effectslice_attempt_1`.
That attempt remains a software-readiness record and is not effectiveness
evidence.

## Alternatives Considered

1. Bounded mean equivalence with Hoeffding intervals. This is distribution-free,
   but the frozen `[-1, 1]` range, `epsilon = 0.025`, and `alpha_C = 0.02`
   require about 14,737 confirmation pairs. Reject as operationally infeasible.
2. Exact-binomial PAC violation certificates with familywise correction. This
   directly matches the claim that a task-local slice rarely violates a frozen
   preservation or necessity condition. Select this route.
3. Bayesian or optional-stopping sequential inference. This can reduce expected
   sample count, but prior choice and stopping rules add avoidable reviewer risk.
   Defer to future work.

## Units and Conditions

For a frozen task adapter and paired case `i`:

- `B_i`: same model, scaffold, case, and budget without the paper skill.
- `F_i`: the complete paper-derived skill.
- `S_i`: a task-local candidate slice selected during discovery.
- `D_{a,i}`: `S_i` with retained atom `a` deleted.

Pair identifiers, case identifiers, seed-block identifiers, prompts, model
configuration, scorer digest, artifact digests, and retry lineage are registered
before scoring. A network retry replaces the failed transport attempt; it never
creates a new statistical unit.

## Stage E: Full-Artifact Eligibility

Eligibility uses a seed block disjoint from discovery and confirmation. A pair is
beneficial when `score(F_i) - score(B_i) >= delta_min` and all frozen contract and
guardrail predicates pass. Missing, malformed, or unscorable outcomes count as
non-beneficial.

Let `pi_F` be the minimum beneficial-case prevalence. The gate passes only when
the one-sided exact Clopper-Pearson lower confidence bound for beneficial
prevalence is at least `pi_F`. With `pi_F = 0.80`, `alpha_F = 0.01`, and no
non-beneficial cases, 21 untouched eligibility pairs are sufficient.

## Stage D: Adaptive Discovery

Discovery may adaptively inspect candidates under a frozen query budget `Q`.
It creates no scientific claim and spends no confirmatory alpha. Candidate order
is deterministic after each query. The confirmation block remains sealed until a
single candidate, its complete deletion-neighbor family, and all hypothesis IDs
are registered.

## Stage C: Sealed Confirmation

Each registered hypothesis supplies one binary violation outcome for every
confirmation pair. Missing output, scorer failure, malformed output, or exhausted
retry counts as a violation and stays in the denominator.

The preservation hypothesis records a violation when `F_i - S_i > epsilon`.
For every retained atom `a`, the necessity hypothesis records a violation when
deleting `a` neither breaks a frozen contract/guardrail nor reduces score by at
least `delta_delete`. Thus every retained atom has a complete deletion witness;
unregistered or missing neighbors force abstention.

For each hypothesis, test the boundary null `p_violation >= rho` against
`p_violation < rho` using the exact binomial lower-tail p-value. Apply Holm's
step-down procedure to the sealed family at `alpha_C`. Admission requires every
registered hypothesis to reject, exact equality between submitted and registered
hypothesis families, exact confirmation pair coverage, and matching SHA-256
registry/manifest/artifact digests.

With `rho = 0.10`, `alpha_C = 0.02`, ten hypotheses, and zero observed
violations, 59 confirmation pairs are sufficient because
`0.9^59 <= 0.02 / 10`.

## Separate Constraints

Token usage, latency, API cost, compute, contracts, and guardrails remain named
endpoints. They are not collapsed into an arbitrary weighted net-utility score.
Admission requires each frozen hard constraint to pass. Descriptive cost effects
are reported with their original units.

## Falsification and Claim Boundary

EffectSlice is falsified for a task when the full artifact is not eligible, the
search cannot produce a strict dependency-closed slice within `Q`, any registered
confirmation hypothesis fails Holm correction, or any deterministic constraint
fails. Abstentions remain in the denominator.

Passing certifies only the registered task, adapter, model/configuration, artifact
digests, and case distribution. It does not establish global minimality, universal
paper understanding, or transfer to unregistered tasks or models.

## Error and Retry Policy

Failures with a deterministic cause, such as invalid input or authentication, are
classified immediately and are not retried. Connection errors, timeouts, HTTP
429, and HTTP 502/503/504 may receive up to five bounded transport attempts, as
recommended by the supplied provider documents, because the user's network is
intermittently unstable. Every attempt shares one retry-lineage ID and one
statistical pair ID. Exhausting the retry budget is terminal for that execution
and is handled by the preregistered missing-value rule.
