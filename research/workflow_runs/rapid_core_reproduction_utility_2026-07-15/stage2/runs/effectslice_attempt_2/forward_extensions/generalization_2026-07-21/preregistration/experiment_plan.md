# EffectSlice-FG1 Forward Generalization Preregistration

## Scope and status

EffectSlice-FG1 is a new forward-only SLA instance after V4 and V5. It shares protocol structure but does not edit, reopen, pool into, supersede, or statistically reuse either accepted schedule. Stage 2.2 registers the design; task materialization and immutable hashes remain pending for Stage 2.3. No experimental model call may begin before the final Stage 2.3 anchor is verified, committed, and pushed.

The study asks whether one fixed admission protocol can issue auditable task-local decisions across heterogeneous paper-derived procedures. It does not claim random sampling, a globally minimal core, or transfer from one task to users, other tasks, or a whole paper.

## Research questions

- RQ1: Can the registered B/F/S protocol issue complete task-local decisions across 12 papers and four mechanism domains?
- RQ2: How heterogeneous are paired F-B, S-B, and S-F effects when tasks are nested within papers?
- RQ3: How do structural restoration, reducer choice, compression, reliability, and cost trade off on four frozen tasks?
- RQ4: What exact candidate-state agreement and F/I repeatability are observed across required models on four prespecified sentinel tasks?
- RQ5: How stable are primary task decisions and identified bounds under the registered SLA grid, leave-one-block-out, and leave-one-paper-out sensitivity analyses?

## Sampling frame and unit

The primary frame has 12 papers, three in each of NLP, software engineering, data analysis, and agent/tool use, with two bounded tasks per paper. The independent aggregate unit is the paper (`n=12`). Tasks are nested within papers, and six blocks are paired repeated measurements within tasks; neither 24 tasks nor 432 conversations are independent papers.

Before the final Stage 2.3 anchor, every task binds a legal full text, at least two central spans, a 5-16 atom DAG, F and candidate digests, disjoint public/private registries, scorer and adapter code, a reference differential test, and an independent semantic audit. A registered static-ineligibility reason blocks the current materialization before that anchor.

The only static-ineligibility reasons are unavailable full text, infeasible source-span atomization, infeasible deterministic private scoring, required proprietary data or retraining, no eligible primary subset, no three-level structural ladder, or no alternate-reducer candidate. Any such case blocks the current materialization with `amendments=[]`. A same-domain replacement may proceed only in a separately committed successor Stage 2.2 registration that rebinds every paper/task/sentinel foreign key and regenerates all schedules before materialization resumes. Outcome-driven replacement and in-place task rewriting are forbidden.

## Primary B/F/S design

Every task receives six matched blocks and fresh B, F, and S conversations on the exact `deepseek_primary` slot. Registry A uses `BFS`, `FSB`, and `SBF`; Registry B uses `BSF`, `FBS`, and `SFB`. Every order occurs once. The 2/3 registry checks are explicit materialization/reporting audits; at the registered 5/6 total threshold they do not add independent admission strength.

- B is the bounded task and common scaffold with a zero-length canonical artifact whose
  SHA-256 is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- F is the complete source-grounded artifact.
- S is the dependency-closed strict subset from `dag_ratio_60_v1`.

The reducer reads only opaque source-locator-derived atom IDs, dependency IDs, and rendered token counts. It cannot read paper-claim, hard-contract, guardrail, scorer-interface, outcome, or model-output labels. `effectslice_atom_renderer_v1` uses UTF-8/LF and a pinned `tiktoken==0.12.0` `cl100k_base` encoding; the ratio is artifact-only `tokens(S)/tokens(F)`. The reducer enumerates every nonempty dependency-closed strict subset, retains candidates at 45-75%, targets 60%, and breaks ties by absolute target error, fewer tokens, then canonical opaque IDs. DAG acyclicity, dependency references, renderer/tokenizer bytes, the enumeration log, and reducer input/output hashes are bound before the final anchor. No eligible subset is a pre-anchor static failure, never a post-outcome repair.

The primary design contains `12 * 2 * 6 * 3 = 432` remote conversations.

## Admission rule

Operational success requires every hard contract and private score at least 0.90. Across six blocks, B succeeds at most once, F and S each succeed at least five times, and at least five valid F/S pairs satisfy `score(S) >= score(F) - 0.05`. Within each three-block registry, B succeeds at most once, F and S each succeed at least twice, and at least two valid pairs satisfy the margin. Every row must be terminal and all integrity checks must pass.

Complete valid B/F/S runs that fail a gate are Reject. The primary reason follows `full-insufficient`, `baseline-sensitive`, `slice-insufficient`, `margin-shortfall`; all failed gates remain flags. Missing transport/integrity evidence is Invalid and stays in every denominator. A completed malformed/no-submission, budget-exhausted, hard-contract-failed, or score-short response is a valid condition failure. Block-level condition success is not candidate-level admission.

Every valid terminal row has exactly one finite private score in `[0,1]`: malformed/no-submission is exactly `0.0`; budget exhaustion is scored from the terminal workspace; hard-contract failure, score shortfall, and operational success retain the frozen scorer's assertion fraction. Invalid rows have a null score. Each task's differential test exercises all five valid terminal-score cases before the anchor.

## Secondary experiments

All secondary experiments use `NLP-LLM-01`, `SE-PE-01`, `DATA-HDB-01`, and `AGENT-TF-01`. Every two-arm candidate gets a fresh adjacent F/C pair, with `FC, CF, FC, CF, FC, CF` across blocks; primary rows are not reused. Ladder and alternate reducers use `PairPass/PairFail/Invalid`, never Admit/Reject. Controls use control-specific `SanityPass/SanityFail/Invalid`: positive requires F/C sufficiency and margin, negative requires sufficient F plus repeated targeted candidate failure, and identity requires input-digest equality plus operational/contract/score agreement.

| Component | Remote conversations |
|---|---:|
| Primary B/F/S | 432 |
| Positive, destructive, and identity controls | 144 |
| Three structural restoration levels | 144 |
| Two alternate blind reducers | 96 |
| GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra, Claude Opus 4.7 with B/F/S/I | 384 |
| **Required remote total** | **1200** |

Controls are sanity states, not calibration data; no confusion matrix or error-rate claim is allowed. Restoration levels are selected by a complete deterministic chain enumeration and require `S=L0` strict-subset `L1` strict-subset `L2` strict-subset `F` before the anchor. They provide structural response evidence, not causality. Alternate reducers and model slots cannot select or rescue primary S.

The alternate DAG-greedy reducer removes atoms in reverse canonical topological order together with their present transitive dependents and retains every unique eligible trajectory state. The source-window reducer enumerates every half-open contiguous source-order window, adds transitive dependency closure, and deduplicates the eligible states. Both select by distance to 60%, fewer rendered tokens, then lexicographic atom IDs; the verifier independently recomputes their complete enumerations and selections.

I is a fresh repeat with a model-visible payload byte-identical to F. B/F/S/I orders keep F/I adjacent, balance F-before-I and I-before-F three times each, and preserve all six B/F/S projections. B/F/S alone determines candidate state. F/I reports valid pairs, success and contract-vector agreement, score delta, canonical-output equality, and raw equality. Closed slots are descriptive; the frozen local `Qwen/Qwen2.5-Coder-7B-Instruct` anchor requires 6/6 input, token-ID, canonical-output, contract, and score equality under an exact big-endian seed derivation with golden vectors. GPT-5.6 Luna and Claude Opus 4.6 are optional after required work and add 192 conversations.

The final anchor binds the Qwen revision, absolute snapshot root, index-complete weight/tokenizer/config file inventory, dtype and quantization, software and hardware evidence, greedy generation settings, and deterministic Torch/cuDNN/cuBLAS/Python flags. Generation uses `max_new_tokens=1024`, EOS IDs `[151645,151643]`, pad ID `151643`, and stops on the first EOS inclusively or the length cap. The verifier runs a frozen offline load/tokenize/generate-twice preflight and requires repeat token and canonical-output equality. Generated token IDs exclude prompt and post-EOS padding and include the first EOS. This is the only seed-controlled model claim; closed API seed fields are recorded if returned but are not relied upon.

Canonical model-visible payloads use a length-prefixed byte format over the exact task scaffold, fixture payload, and candidate artifact. Per-slot request templates reconstruct canonical non-streaming JSON wire bytes from registered JSON pointers. Raw responses are the exact post-transfer body bytes before parsing. Canonical output is extracted by a frozen slot-specific selector from strict UTF-8 JSON, newline-normalized, NFC-normalized, and UTF-8 encoded without a trailing-newline edit. Parser and analysis implementations, schemas, and golden fixtures/results are hash-bound before calls. The verifier executes both implementations in isolated Python processes with frozen JSON on stdin, requires exact canonical JSON bytes on stdout, validates the registered schemas, and rejects timeouts, stderr, nonzero exits, or byte differences.

Every primary and required model uses the same normalized 1024-token output cap. The request template maps it to `/max_tokens` for DeepSeek Chat Completions and Claude Messages, `/max_output_tokens` for OpenAI Responses, and `/max_new_tokens` for the local Qwen adapter; provider defaults are forbidden. Slot response contracts freeze the standard protocol assumption, output selector, raw finish-reason selector and normalization, and usage selectors before calls. A format-only preflight validates both request and response shape for every available exact alias. The parser golden suite separately covers every required slot, EOS, length, provider stop, a null finish reason, malformed completion, terminal transport failure, and not-dispatched unavailability. Length-capped completions keep the same frozen scorer and terminal-outcome rule.

The result parser, analysis implementation, and open-anchor preflight each record a builder identity and receive an independent source audit by a different identity. The audit evidence and exact implementation hashes are bound by the final anchor; an implementation cannot self-certify only by shipping matching golden fixtures.

At the V4 mean of 127.2 seconds, required remote work is 42.4 nominal serial call-hours and 51-70 planned call-hours with queues and network retries. This excludes the local anchor, source/task materialization, audits, scoring, plots, writing, and review; two workers give only an ideal 25.5-35 hour lower bound. Optional models add about 8-14 call-hours.

Resource reporting is descriptive and never ranks models. Every execution records frozen candidate bytes and `cl100k_base` tokens, canonical payload bytes, provider-reported input/output/total/cached tokens when valid, final-attempt and total elapsed milliseconds, retry sleep, and retry overhead. Each task-model-candidate cell shows all six registered values plus non-null count, median, range, and sum; S-F deltas require both members. Monetary cost is appendix-only and is omitted unless a dated public price table and its hash are frozen before calls.

## Statistics and figures

State counts use registered denominators. For each F-B, S-B, and S-F contrast, block differences are averaged over valid blocks only as a descriptive task value, while fixed-denominator lower/upper endpoints assign missing bounded outcomes to their extrema and average all six blocks. The two task endpoints receive fixed 0.5/0.5 paper weights, three papers receive 1/3 domain weights, and four domains receive 1/4 overall weights. Every level reports `valid_pairs/registered_pairs`. Per-task displays show six raw points, counts, median, and range, with no per-task Clopper-Pearson or six-block bootstrap intervals. Bootstrap and leave-one-paper-out recompute this same estimator.

Aggregate analysis is paper-level. Exact domain counts, leave-one-paper-out results, an equal-domain summary, and a paper-within-domain bootstrap sensitivity analysis are mandatory. The bootstrap describes this registered benchmark, not a population guarantee.

Leave-one-block-out uses the registered five-block thresholds and never deletes remaining Invalid rows. If omitting the sole Invalid row yields a complete five-block state, that recovery is labeled only as sensitivity evidence and cannot replace the six-block decision.

The required figure groups are: (1) an end-to-end real example from source span through opaque atoms, dependency DAG, F/S retained boundary, rendered payload, and terminal admission fields, plus the freeze timeline and full B/F/S/margin/integrity admission gate; (2) paper-level effect forest and a primary-only state matrix; (3) separate primary compression and two-arm Pair/Sanity panels with structural missing cells; and (4) model-by-sentinel-task candidate/F-I results, SLA sensitivity, and terminal-failure decomposition. The primary, paired-secondary, and model designs are never shown as a nonexistent full factorial. Recovered retries are annotations, not semantic failures. Empirical panels cannot use placeholders.

## Retry and forward gates

Connection resets, DNS/TLS failures, HTTP 408/429/5xx, and read timeouts receive at most five attempts with 2/4/8/16-second delays; 429 honors a larger valid `Retry-After` and deterministic execution-ID jitter. Authentication failure, absent exact aliases, malformed frozen requests, and deterministic scorer failures are not network retries. Stable execution IDs and idempotency keys are used when available; the first cryptographically valid terminal response wins and all late duplicates remain annotations. A terminal response is never rerun because its score is low. Every attempt is preserved without credentials.

Stage 2.3 starts only after the design bundle, deterministic SLA analysis, verifier, and tests pass; the Stage 2.2 report and artifacts are committed and pushed; and no experimental provider call has started. The first experiment remains prohibited until every source, span, audit, DAG, candidate, registry, scorer, adapter, test, request template, and schedule is hash-bound, exact aliases pass format-only preflight, independent implementation source audits pass, identities are recorded, and the final anchor is committed and pushed. API credentials are injected only from the environment or a secret store and never enter source, logs, fixtures, manifests, hashes, or the manuscript.

The final anchor also binds the exact 1296-row family/task/variant/model/block/condition
sequence. A normalized, sorted-unique value manifest for execution IDs, pair IDs,
private case IDs, derived seeds, fixture payload hashes, and wire-request hashes is
recomputed from the complete registered FG1/V4/V5 glob expansions with fixed extractors;
the manifest cannot choose its own source set, and every registered intersection must be zero. Only the
ordered FG1 execution-ID allowlist may enter FG1 estimators.

No page-count optimization is applied while evidence is being built.
