# EffectSlice Confirmation V2 Design

## Status

Approved by the standing user instruction to continue autonomously until a
high-quality manuscript is produced. This design supersedes the contaminated
confirmation interpretation in `effectslice_attempt_2`; it does not delete or
rewrite the historical bundles.

## Problem

The first confirmation implementation exposed the private scorer after `test`
actions. The agent then edited the same patch after observing confirmation-case
pass counts. Consequently, those runs are adaptive development evidence, not an
untouched holdout. The same experiment also treated deterministic cases for one
generated patch as independent Bernoulli trials. That is pseudoreplication.

## Alternatives Considered

1. **Run-level randomized confirmation (selected).** Keep the current tasks and
   selected source-grounded slices, but generate fresh patches in independent
   API sessions. A hidden suite is scored exactly once after each patch is
   fixed. Statistical bounds use independent agent runs, not cases.
2. **Deterministic conformance only.** Score one fixed patch on a hidden suite
   and report exact coverage without probability claims. This is inexpensive
   but too weak for the intended admission claim.
3. **Immediate broad benchmark.** Add many papers, reducers, providers, and
   human users before repairing the protocol. This has better external validity
   but leaves the internal-validity bug unresolved and wastes prior work.

## Scientific Unit and Gate

The primary statistical unit is one fresh provider conversation that produces
one patch under one condition. Cases inside the private suite are clustered
checks defining that run's task score; they are not independent observations.

For each task and replicate `r`, conditions `B`, `F`, and `S` use the same
scaffold, task, workspace, action budget, and private suite:

- `B`: no paper-derived procedural artifact.
- `F`: complete paper-derived procedural artifact.
- `S`: the discovery-selected dependency-closed slice.

The order of `B/F/S` is independently permuted for each replicate and recorded.
The provider API exposes no supported seed, so the protocol claims fresh
sessions and randomized order, not seeded determinism.

Each run is successful when the hard contract passes and at least 95% of the
hidden cases pass. For replicate `r`:

- full-artifact benefit: `F_success and not B_success`;
- slice preservation: `S_success == F_success` and the absolute task-score gap
  is at most 0.05;
- slice benefit: `S_success and not B_success`.

There are 18 registered replicates per task. One-sided Clopper-Pearson bounds at
`alpha=0.02` are computed across replicate indicators. Eighteen successes out
of eighteen have a lower bound above 0.8. A task-local slice is admitted only
if all three lower bounds exceed 0.8 and every hard contract passes. Otherwise
the output is rejection or abstention. Thresholds are frozen before provider
execution and are not changed after results are observed.

## Private-Score Protocol

Confirmation uses a dedicated runner mode:

1. The model may `search`, `open`, and `edit` the public workspace.
2. `test` is unavailable and never calls the private scorer.
3. `submit` fixes the patch, runs the private scorer once, and terminates. The
   score is persisted but never returned to the model.
4. If the action budget expires with a nonempty patch, the final patch is scored
   once. If no patch exists, the run fails without a scorer call.
5. The result records `private_score_count`, `private_feedback_exposed=false`,
   and the transcript needed to verify both properties.

The old confirmation cases and results are labeled `contaminated_development`
and excluded from all v2 decisions.

## Fresh Hidden Suites

New `confirmation_v2` blocks use seeds and case IDs disjoint from every prior
block. SNAP-MFSE keeps varied clustered count matrices. TOOLFORMER-FILTER is
redesigned so candidate count, horizon, thresholds, counterfactual losses, and
expected keep patterns vary; it may not use a constant `[true,true,false,false]`
oracle pattern. Suite diversity is tested before sealing.

The hidden suites remain local scorer inputs and are never included in model
prompts or tool observations.

## Digest Binding and Write-Once Evidence

Before any v2 provider call, a family manifest binds by SHA-256:

- task prompt;
- workspace tree;
- full artifact and source map;
- slice artifact and slice registry;
- discovery summary;
- confirmation-v2 case registry;
- scorer and runner source;
- thresholds, replicate IDs, and condition permutations.

The runner recomputes every digest from the actual path and rejects any
mismatch. Output directories are write-once: a pre-existing nonempty replicate
directory causes a hard failure. The protocol and family manifest are committed
and pushed before execution, providing a remote pre-run record.

## Provider Identity and Retry Policy

The primary service is the user-supplied DeepSeek endpoint. Requests use the
exact alias `deepseek-v4-flash`; the manuscript describes DeepSeek V3.2 as the
provider/user label and discloses that the alias-to-deployment mapping is not
independently attested. Request date, alias, endpoint protocol, temperature,
token limit, retry lineage, and any response model field are persisted.

Connection errors, timeouts, HTTP 429, and HTTP 5xx responses are retried up to
five times within the same model turn. Exhaustion marks the run missing and
counts against its gate; it is never silently replaced. A fresh replicate may
be started only under its preregistered replicate ID.

## Outputs

- protocol and case-generator tests;
- sealed family manifests and pre-run Git revision;
- raw write-once replicate bundles;
- run-level baseline, research, and ablation summaries;
- figures derived from summaries rather than hard-coded counts;
- revised manuscript with old evidence explicitly excluded;
- three-reviewer audit and Stage 2 reports.

## Non-Claims

The experiment does not establish cross-paper, cross-provider, or human-user
benefit. It does not claim local model inference, GPU independence of every
possible reproduction, global minimality, or superiority over other reducers.
It tests a task-local substitution decision under an API-first workflow.
