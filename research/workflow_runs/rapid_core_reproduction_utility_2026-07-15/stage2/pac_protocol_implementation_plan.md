# EffectSlice PAC Certificate Implementation Plan

**Goal:** Create `effectslice_attempt_2` with an exact-binomial, pair-traceable
eligibility and sealed-confirmation implementation while preserving attempt 1.

**Architecture:** Immutable pair-level observations feed standard-library exact
binomial functions. Admission computes all p-values internally, validates exact
registry and pair coverage, and returns reason-coded abstention plus audit-ready
hypothesis results.

**Tech Stack:** Python 3.12 standard library, `dataclasses`, `unittest`/`pytest`,
JSON/JSONL, and SHA-256 digests.

## Task 1: Attempt Isolation

- [ ] Copy attempt 1 to `effectslice_attempt_2` without modifying attempt 1.
- [ ] Remove or relabel copied derived outputs so none are mistaken for new evidence.
- [ ] Change run IDs, evidence boundary, design, plan, and manifest references.
- [ ] Save the fresh strict readiness audit as a new derived artifact.

## Task 2: Exact-Binomial Statistics (TDD)

- [ ] Add failing tests for exact lower-tail p-values at zero and nonzero violations.
- [ ] Add failing tests for one-sided Clopper-Pearson bounds, including `k=0`,
      `k=n`, invalid counts, invalid alpha, and monotonicity.
- [ ] Add a failing test that derives 21 eligibility pairs for
      `pi_F=0.80, alpha_F=0.01`.
- [ ] Add a failing test that derives 59 zero-violation confirmation pairs for
      `rho=0.10, alpha_C=0.02, m=10`.
- [ ] Implement the smallest standard-library functions and rerun the full suite.

## Task 3: Pair-Level Evidence Models (TDD)

- [ ] Add failing tests for duplicate pair IDs, wrong seed blocks, non-boolean
      outcomes, missing hypothesis IDs, and noncanonical order.
- [ ] Add immutable `BinaryObservation`, `ViolationHypothesisEvidence`, and
      hypothesis-result records.
- [ ] Replace eligibility range fields with `minimum_beneficial_prevalence`.
- [ ] Replace externally supplied confirmation p-values with registered raw binary
      outcomes and internally computed p-values.

## Task 4: Eligibility and Confirmation Admission (TDD)

- [ ] Add failing eligibility tests for insufficient evidence, non-beneficial
      prevalence, exact boundary behavior, contracts, guardrails, and success.
- [ ] Add failing confirmation tests for incomplete pair coverage, overlapping
      blocks, registry mismatch, digest mismatch, failed preservation, failed
      deletion witness, hard-constraint failure, and success.
- [ ] Implement exact eligibility and rename the public confirmation gate to make
      its sealed-confirmation scope explicit.
- [ ] Preserve deterministic reason precedence and backward-incompatible schema
      changes under a new version identifier.

## Task 5: AIDE-T2 Development Adapter

- [ ] Freeze same-scaffold `B` and `F` prompt construction, model parameters,
      maximum requests, bounded retry policy, retry lineage, scorer, and locked labels.
- [ ] Freeze score direction, `delta_min`, `pi_F`, `epsilon`, `delta_delete`,
      `rho`, contracts, guardrails, atom map, dependency graph, and `Q/N`.
- [ ] Hash every frozen input and save the discovery/eligibility/confirmation split.
- [ ] Run only development pairs until the adapter and transport smoke tests pass.

## Task 6: Evidence and Stage Gates

- [ ] Preserve raw request metadata, redacted responses, retries, scorer outputs,
      and failure classifications without storing credentials.
- [ ] Produce baseline, research, and ablation summaries from real scored rows.
- [ ] Write `stage_report_2_3.json` only after attempts are reproducible and
      failures are classified.
- [ ] Write `stage_report_2_4.json` only after all three summaries parse and their
      claims remain inside the evidence boundary.
- [ ] Keep Stage 2 active if the main scientific evidence remains insufficient.

