# SNAP-MFSE Paper-Core Reproduction Design

## Decision

Build one locked algorithm-reproduction task for the matrix-free spectral
embedding (MFSE) contribution in the SnapATAC2 paper. The task measures whether
a source-grounded paper artifact helps a model reproduce the paper's core
algorithm on an ordinary API-first workstation. It replaces the existing
SNAP-T1/SNAP-T2 self-reported JSON scorer for this claim; those older rows remain
historical development artifacts only.

This design was selected autonomously under the user's instruction to continue
without pausing for approval. No Git commit or push is part of the work.

## Alternatives Considered

1. Extend the AIDE tree-search task. This reuses an objective ML scorer, but the
   complete artifact has shown only weak and unstable development effects, and
   an interactive search tree would require many provider calls.
2. Create a task around a new algorithm paper. This could offer a clean
   information gap, but it would require a new paper download, source map, code
   checkout, and novelty audit before any experiment could run.
3. Repair the SnapATAC2 task into a numerical implementation benchmark. This is
   selected because the paper, extracted text, source map, official code, and
   MIT-licensed repository are already local, while the current scorer is too
   weak to support scientific claims.

## Source Boundary

- Paper text: `papers/extracted/snapatac2.txt`, especially lines 73-79.
- Existing paper artifact: `generated_skills/real_reuse/snapatac2/SKILL.md`.
- Existing source map:
  `generated_skills/real_reuse/snapatac2/references/source_map.json`.
- Official implementation cross-check: `D:/a_work/gitee/SnapATAC2` at commit
  `7be57442708694217e27c8654ecd38a0de194aa4`, MIT license,
  `src/embedding.rs`.

The experimental target is the algorithm described in the paper, not a claim
that the current repository commit is identical to paper version 2.3.1. Any
difference between the paper equation and current code is recorded rather than
silently reconciled. In particular, the target IDF is the paper's explicit
`log(n / (1 + df))` equation from line 74; the current repository's different
edge-case implementation is audit context, not the experimental oracle.

## Locked Task

The model receives a small read-only-overlay starter repository with an
incomplete function:

```python
def matrix_free_spectral_embedding(
    counts: numpy.ndarray,
    n_components: int,
    random_state: int = 0,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    ...
```

The function must accept a finite, nonnegative cell-by-feature count matrix and
return descending eigenvalues and corresponding cell embeddings. It must use a
matrix-free symmetric linear operator and must not materialize the full
cell-by-cell similarity or normalized similarity matrix.

The task prompt specifies the API, input validation contract, resource bound,
and verification command. It does not include the MFSE equations. The full
paper artifact supplies source-grounded algorithm details. The no-artifact
baseline receives only the common ACI contract and locked task.

## Full Artifact

Create a deterministic task-local execution card from the cited paper spans.
The complete card contains distinct source-mapped atoms for:

1. IDF feature scaling from the count matrix.
2. Row-wise L2 normalization to obtain cosine-ready `X`.
3. Zero-diagonal similarity `W = X X^T - I` and degree computation without
   materializing `W`.
4. Degree normalization and the matrix-vector product
   `X_tilde (X_tilde^T v) - D^-1 v`.
5. Lanczos/top-eigenpair ordering, output checks, and the matrix-free resource
   guardrail.

The card does not include reference code or hidden expected values. Every atom
stores exact source spans and a digest. Later EffectSlice candidates must be
strict, dependency-closed subsets of these atoms.

## Scoring

The scorer runs in an isolated copy and returns only public fields. It uses
pre-registered deterministic matrix cases in disjoint blocks:

- development: 4 cases;
- eligibility: 21 cases;
- discovery: 16 cases;
- confirmation: 59 cases.

For each case, the scorer checks:

- valid shape, finite output, and descending eigenvalues;
- eigenvalues against a dense reference implementation of the paper equation;
- sign- and basis-invariant agreement through the embedding projection matrix;
- residual norms of returned eigenpairs;
- rejection of invalid negative, nonfinite, all-zero-row, and invalid-component
  inputs;
- static and runtime guards against allocating an `n_cells x n_cells` dense
  similarity matrix.

The per-case task score is binary. A case passes only when every numerical,
contract, and resource check passes. Aggregate reports retain the full binary
case vector; no self-reported metrics are accepted.

## Experimental Conditions

- `B`: common bounded ACI plus the locked task, no paper artifact.
- `F`: the same ACI and task plus the complete source-grounded execution card.
- `S`: a strict dependency-closed artifact proposed only after `F` is eligible.
- `D_a`: `S` with retained atom `a` and all dependents removed.

DeepSeek-family (`deepseek-v4-flash`, user-identified service name DeepSeek
V3.2) is the primary inference backend. GPT-family (`gpt-5.6`) is a robustness
backend. The local device performs orchestration, tool execution, scoring, and
artifact persistence; no local accelerator is required.

The ACI uses 16 model-visible actions per condition. This limit is fixed before
the first SNAP-MFSE model run and is not changed after observing task outcomes.
Network retries remain within the same statistical unit and are capped at five.

### Provider Protocol Amendment

DeepSeek provider protocol v1 used a 4096 output-token cap. In two preserved
primary B runs, the failing turns each consumed exactly 4096 tokens on all five
transport attempts and returned no visible action, while matched F runs
completed. Those bundles remain provider-inconclusive.

Provider protocol v2 raises only the DeepSeek output-token cap to 8192. The
model alias, wire API, prompt, artifact, case registry, scorer, 16-action
horizon, retry policy, thresholds, and all task digests remain unchanged. New
bundles record `effectslice-deepseek-output-budget.v2` in a v2 pair manifest;
v1 raw bundles are not overwritten. This amendment addresses transport-visible
completion and does not authorize interpreting a partial v1 B score as a final
model outcome.

### Harness Protocol Amendment

The first 21-case eligibility bundle exposed a separate terminal-measurement
defect in harness v1: B used its last action to edit after an earlier failed
test, so the final patch was not scored. The raw bundle is preserved and
classified `unscored_final_state`; its stale intermediate score is excluded.

Harness v2 keeps the same 16 model-visible actions and all scientific inputs.
When the action budget ends with a nonempty diff, the scorer evaluates the
terminal workspace once as `budget-final`, after the model can no longer act or
receive feedback. This changes only terminal measurement, prevents stale-score
reuse, and is recorded as `effectslice-snap-mfse-aci.v2`. Eligibility is rerun
as a new immutable bundle; the excluded v1 bundle remains in the audit.

### Sealed Confirmation Family

Discovery locked `prefix_03`, retaining `A01` through `A03`. On the frozen
16-case discovery block it matched F on all cases, while B, `prefix_01`, and
`prefix_02` each failed all cases; these are the complete dependency-closed
deletion closures for the selected chain prefix.

Before opening the 59-case confirmation block, freeze one B/F/S family in
`artifacts/snap_mfse/confirmation_family.json`. Confirmation passes only when:

1. S and F have zero case-level mismatches, and the one-sided
   Clopper-Pearson upper bound at `alpha_C=0.02` is at most 0.1;
2. the one-sided lower bound for `S-B >= delta_min` is at least 0.8; and
3. S passes both the input/shape contract and matrix-free guard.

The runner binds the family, selected artifact, slice registry, case registry,
and hypothesis IDs by digest. A passing result supports only a task-local
SNAP-MFSE claim; it does not establish general EffectSlice effectiveness.

## Admission and Stopping

Development first runs one B/F pair per model family. If neither produces a
positive full-artifact signal, the task abstains and no slice budget is spent.
If at least the primary backend shows a development signal, run the frozen 21
case eligibility block. The full artifact must satisfy the existing
`delta_min` and exact-binomial eligibility gate before discovery begins.

Discovery and deletion audits cannot use eligibility or confirmation cases.
Confirmation remains sealed until one candidate and its complete hypothesis
family are registered. Any malformed, missing, or unscorable case is a
violation and remains in the denominator.

## Failure Classification

- Provider/network failures follow the bounded retry policy.
- Authentication and deterministic input errors fail immediately.
- Harness defects invalidate the affected bundle and require a new protocol
  version; raw artifacts are never overwritten.
- A passing hidden test at the final action retains its objective score even if
  no separate `submit` action fits.
- A full artifact with no positive effect returns an explicit eligibility
  abstention; thresholds, seeds, and task prompts are not changed to rescue it.

## Test Plan

Implementation follows TDD. Unit tests cover reference numerical behavior,
sign/basis-invariant comparison, case registry digests, invalid inputs, dense
allocation guards, scorer sanitization, ACI manifests, and analyzer
classification. Integration tests apply known passing and failing patches to
the locked workspace. The entire attempt-2 suite must pass before any provider
run is interpreted.

## Claim Boundary

A successful task supports only this statement: on the locked SNAP-MFSE coding
task and registered case distribution, the source-grounded paper artifact
changed the probability of producing an implementation that reproduces the
paper's numerical core under the stated API and action budget.

It does not reproduce the full SnapATAC2 biological benchmark, establish global
minimality, measure ordinary-user usability, or prove that every paper can be
converted into a helpful artifact.
