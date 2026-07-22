# EffectSlice Forward Generalization Preregistration

## Scope

This is a forward-only Stage 2.2 registration. It does not edit, reopen, pool
into, or supersede V4 or V5. The V4 and V5 preregistration hashes are bound in
`experiment_plan.json`. No forward provider conversation may begin until this
bundle passes its verifier, is committed, and is pushed.

The study asks whether one fixed admission protocol can issue auditable local
decisions across heterogeneous paper-derived procedures. It does not claim that
the registered papers are a random sample, that EffectSlice finds a globally
minimal core, or that an admission transfers to users, other tasks, or an entire
paper.

## Registered Sampling Frame

The primary frame contains 12 formally identified papers, three in each of four
domains, and two distinct bounded tasks per paper.

| Domain | Papers | Registered tasks |
|---|---|---:|
| NLP | LLMLingua; LLMLingua-2; Context-Aware Sentence Compression | 6 |
| Software engineering | Delta Debugging; C-Reduce; Perses | 6 |
| Data analysis | SnapATAC2; Leiden; HDBSCAN | 6 |
| Agent/tool use | Toolformer; Reflexion; ReAct | 6 |

The 24 paper-task clusters, mechanism boundaries, deterministic scorer
contracts, reserves, and rejection reasons are frozen in `paper_registry.json`.
Every selected task excludes foundation-model training and live external data.
Model scores, embeddings, tool outputs, compiler outcomes, and oracles are
supplied as deterministic fixtures when the task would otherwise depend on an
external service.

Before a Stage 2.3 pilot, each cluster must bind a legal local full text, exact
source spans, a 5-16 atom DAG, F and S digests, disjoint public/private fixture
digests, scorer code, and a task-specific adapter. Clean-room implementation is
the default. External code is not copied until its revision and license are
recorded.

## Primary B/F/S Design

Each paper-task cluster receives six matched private blocks. Each block runs B,
F, and S in a fresh provider conversation. The six permutations `BFS`, `BSF`,
`FBS`, `FSB`, `SBF`, and `SFB` occur exactly once per cluster. The global
schedule is deterministically interleaved across domains and hash-bound before
the first provider call.

- B: task and common action scaffold, with no paper-derived artifact.
- F: complete source-grounded task artifact.
- S: one frozen dependency-closed strict subset.

The primary reducer is outcome independent. It removes the last canonical
dependency-maximal atom that is not a hard contract, guardrail, or scorer
interface, then restores dependency closure. A cluster with no eligible strict
subset fails its static gate before provider execution. Private results can
never choose a paper, task, atom, scorer, or candidate.

The primary design contains `24 x 6 x 3 = 432` provider conversations. The
paper-task cluster is the independent unit; 432 conversations are not 432
independent scientific units.

## Frozen Admission Rule

Operational success requires every hard contract and private score at least
0.90. A natural S is admitted only when all of the following hold:

1. B succeeds in at most 1 of 6 blocks.
2. F succeeds in at least 5 of 6 blocks.
3. S succeeds in at least 5 of 6 blocks.
4. In at least 5 of 6 matched blocks, `score(S) >= score(F) - 0.05`.
5. Every required output and integrity check is complete.

Complete runs that fail one or more sufficiency fields are Reject. Missing or
corrupt terminal evidence after the retry policy is Invalid. Invalid is
orthogonal to F/S sufficiency and remains visible in every registered
denominator.

The forward claim passes its preregistered benchmark target only if at least
three of four positive controls are admitted, all four destructive negative
controls are rejected, at least 20 of 24 natural clusters yield valid decisions,
at least 8 natural S candidates are admitted, and admissions cover at least
three domains. Failure is reported; thresholds and tasks are not edited.

## Registered Secondary Experiments

Four clusters, one per domain (`NLP-LLM-01`, `SE-PE-01`, `DATA-HDB-01`, and
`AGENT-TF-01`), support all secondary experiments.

Controls add a redundant source-addressed atom for the positive S and delete a
core or hard-contract atom for the negative S. They reuse the matched primary B
and F but use 48 fresh S conversations. Four controls per class are too few for
a calibrated confusion matrix, so only exact task-level counts and intervals
are reported.

The atom ladder contains four nested dependency-closed levels, from `drop_4` to
the primary `drop_1`. Three levels beyond primary add 72 fresh S conversations.
These rows produce the restore/drop and compression-reliability Pareto analyses
but cannot select or rescue the primary S.

The closed-model robustness panel adds GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra, and
Claude Opus 4.7: 72 conversations each, 288 total. The primary DeepSeek rows are
reused. GPT-5.6 Luna and Claude Opus 4.6 are optional separate conditions after
all required runs; they are not silent fallbacks. A local
`Qwen/Qwen2.5-Coder-7B-Instruct` slot supplies the fixed-seed reproducibility
anchor after its exact weights, tokenizer, quantization, runtime, and hashes are
bound in Stage 2.3.

Closed endpoints run at temperature zero, but no closed model is claimed to be
seed deterministic. Returned seed/fingerprint fields are recorded when present.

## Statistics and Figures

The main report shows exact Admit/Reject/Invalid counts and all six paired block
outcomes per cluster. Aggregate sensitivity intervals use 10,000 bootstrap
replicates with seed 20260721, resampling papers within domain and carrying both
tasks and all blocks together. They describe this registered benchmark and do
not establish a population guarantee.

Four figure groups are preregistered:

1. Protocol audit: real source span, atom DAG, F/S boundary, freeze timeline,
   information flow, and admission state machine.
2. Cross-paper effects: paper-task forest/dot-whisker plot and faceted
   Admit/Reject/Invalid heatmap.
3. Compression and mechanism: reliability/cost Pareto and atom restore/drop
   trajectories.
4. Robustness: SLA and leave-one-block-out sensitivity plus failure-mode
   decomposition with recovered transport retries separated from semantic
   failures.

No empirical figure is generated from placeholders. A control confusion matrix
is explicitly prohibited with the current four independent controls per class.

## Compute, Retry, and Failure Policy

The required provider cap is 840 conversations: 432 primary, 288 required model
ablation, 72 atom ladder, and 48 controls. At the V4 observed mean of 127.2
seconds per conversation this is 29.7 nominal provider-hours; the planning band
is 36-48 hours with queue and network retries. The two optional closed models
add at most 144 conversations after required work.

Transport failures, HTTP 408/429/5xx, and timeouts receive at most five attempts
with 2/4/8/16-second delays. Authentication rejection, absent model aliases,
malformed frozen requests, and deterministic scorer failures are not retried as
network failures. A completed semantic result is never rerun because its score
is low. Every attempt and recovery is preserved.

## Stage 2.3 Gate

Stage 2.3 cannot start until:

- every file in this registration bundle passes `verify_forward_preregistration.py`;
- the bundle is committed and pushed;
- selected full texts, source spans, atom DAGs, F/S artifacts, fixtures,
  scorers, adapters, and the global schedule have immutable hashes; and
- exact provider aliases pass non-private format preflight without fallback.

No page-count optimization is applied during evidence construction. Main-paper
and appendix placement is decided only after real plots and review evidence
exist.
