# Real Reuse Experiment Plan

Date: 2026-07-04

Status: first GPT-family pass scored; SWE-T1 source-context and SNAP
executable-artifact diagnostic follow-ups are complete. Next work is to
stabilize or rerun core real-reuse evidence before running remaining auxiliary
analyses.

## Research Question

The next-stage validity question is:

> Given an original-paper-style input/output task, can a user or agent rely on a
> PaperToSkill-generated skill to reuse the source paper's method and obtain an
> acceptable real task outcome?

This is stronger than the current deterministic/offline package. The current
package shows that skills are compact, source-grounded, structurally valid, and
better than summaries on offline coverage/readiness checks. The real-reuse
study is intended to test downstream usefulness.

## Design Principles

- Main evidence should use source-paper core objective metrics where possible, such as
  validation score, test pass rate, exact match/F1, ARI/NMI, runtime, or memory.
- Main rows are `paper-task` rows, not just paper rows.
- Keep the paper's input/output shape as close as practical: same task kind,
  same required output, same metric family, and comparable run constraints.
- Use the original paper's score only as a `reported reference` unless the same
  dataset, inputs, outputs, metric, model/tool budget, and runtime setting are
  reproduced locally.
- Use `Summary` as the main baseline because it reflects a realistic way users
  operationalize a paper before PaperToSkill.
- Do not include `Abstract` in the main table.
- Do not include `Full Excerpt` in the main table; keep a small sanity check for
  reviewer questions about context size and full-text access.
- Preserve raw rows for every task. Aggregates may be useful, but small samples
  should not hide failure modes.
- Do not keep a separate auxiliary breadth/coverage experiment. Breadth is
  represented by the selected main paper-tasks unless this design is reopened.
- No mid-run human intervention in the core task runs. Human usability is not a
  main-experiment requirement; if tested later, use a separately logged
  user-study protocol after the core experiment and necessary auxiliary
  analyses are stable.
- Third-party LLM service latency, provider timeouts, and retry counts are not
  core effectiveness metrics. Give model calls enough timeout/retry budget and
  record provider availability separately. Runtime/resource metrics count only
  when they are part of the source paper's own local task metric and are rerun
  in a comparable local setting.
- Execution order: stabilize the core real-reuse experiment first; collect
  auxiliary data opportunistically during core runs; aggregate remaining
  auxiliary analyses afterward; run any real-user/user-study work last.

## Candidate Papers

| Paper | Role | Domain | Venue / Source Status | Why Selected | Current Boundary |
| --- | --- | --- | --- | --- | --- |
| AIDE: AI-Driven Exploration in the Space of Code | Main | ML engineering | arXiv / open implementation | Existing PaperToSkill case; objective ML benchmark style; source notes already preserve method, baselines, and caveats. | Full benchmark reproduction may be expensive; use reported scores as references unless locally reproduced. |
| SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | Main | Software engineering | NeurIPS 2024 / open implementation | Strong automated software-engineering benchmark shape; objective patch/test outcomes. | Needs local task selection and repo/test harness setup. |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Main | Reasoning, QA, decision-making | NeurIPS 2023 / open implementation | Tests whether workflow/failure-memory instructions transfer into retry/reflection tasks. | Avoid subjective reflection-quality scoring; use objective task success where possible. |
| SnapATAC2 | Main non-agent case | Single-cell omics data analysis | Nature Methods / open implementation | Adds a non-agent scientific-data-analysis domain with objective runtime/memory/analysis metrics. | Requires dataset choice and bioinformatics environment smoke test. |
| Toolformer | Sanity / auxiliary | Tool use | NeurIPS 2023 / existing PaperToSkill case | Useful for source-grounding and small tool-use sanity checks. | Original training/data-generation replication is too heavy for main validity. |
| AI Scientist-v2 | Sanity / auxiliary | Automated research | Existing integration evidence | Useful for integration and synthetic sensitivity evidence. | Current evidence is bounded/synthetic, not broad real-task success. |

Primary source links to verify during execution:

- AIDE arXiv and code: `https://arxiv.org/abs/2502.13138`,
  `https://github.com/WecoAI/aideml`
- SWE-agent paper and code: `https://arxiv.org/abs/2405.15793`,
  `https://github.com/SWE-agent/SWE-agent`
- Reflexion paper and code: `https://arxiv.org/abs/2303.11366`,
  `https://github.com/noahshinn/reflexion`
- SnapATAC2 paper and code:
  `https://www.nature.com/articles/s41592-023-02139-9`,
  `https://github.com/kaizhang/SnapATAC2`

## Table 1: Real Reuse Main Results

Purpose: main validity table. It tests whether PaperToSkill helps reproduce or
reuse a paper method under original-style inputs and outputs.

Current source table: `results/real_reuse/main_results_plan.md`.

| Task ID | Source Paper | Domain | Original-style Input | Required Output | Metric | Reference | Summary Score | PaperToSkill Score | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | ML engineering | Kaggle-style dataset + metric | Runnable solution/submission | validation_score | Reported AIDE ref. | 0.816 | 0.817 | Scored; solved by both |
| AIDE-T2 | AIDE | ML engineering | Weak ML script + feedback | Improved script + trajectory | best_node_score | Reported AIDE ref. | 0.000 | 0.826 | Scored; PaperToSkill-only success |
| SWE-T1 | SWE-agent | Software engineering | Repo issue + tests | Patch + test log | resolved | Reported SWE-agent ref. | 0.000 | 0.000 | Scored; both patch apply failed |
| SWE-T2 | SWE-agent | Software engineering | Failing test + repo | Focused patch + verification | tests_passed | Reported SWE-agent ref. | 0.000 | 1.000 | Scored; PaperToSkill-only success |
| REF-T1 | Reflexion | Reasoning / QA | Multi-hop QA + feedback | Final answer + reflection trace | exact_match_or_f1 | Reported Reflexion ref. | 1.000 | 1.000 | Scored; solved by both |
| REF-T2 | Reflexion | Decision / programming | Failed attempt + checker feedback | Corrected second attempt | second_attempt_success | Reported Reflexion ref. | 1.000 | 1.000 | Scored; solved by both |
| SNAP-T1 | SnapATAC2 | Single-cell omics | Small single-cell dataset | Pipeline + embedding artifacts | runtime_memory_quality | Reported SnapATAC2 ref. | 0.000 | 0.500 | Scored; below success threshold |
| SNAP-T2 | SnapATAC2 | Single-cell omics | Single-cell labels/proxy task | Clustering/marker artifacts | ari_nmi_runtime_memory | Reported SnapATAC2 ref. | 0.200 | 0.400 | Scored; below success threshold |

Column definitions:

- `Reference`: the original paper's reported score/reference or a locally
  reproduced baseline. Mark the source explicitly and do not treat reported
  paper scores as a fair same-environment baseline unless the same dataset,
  input/output, metric, budget, and run setting are reproduced locally.
- `Summary Score`: score when the agent receives a concise method summary
  instead of a PaperToSkill skill.
- `PaperToSkill Score`: score when the agent receives the generated skill.
- `Status`: execution state and current evidence boundary for the row.
- `Metric`: the task's original metric family wherever possible.

### Completed Follow-Up: SWE-T1 Source Context

SWE-T1 remains a failure-boundary row. The paper-facing first-pass row scored
Summary 0.000 and PaperToSkill 0.000 because both generated patches failed to
apply. That row remains the main-table evidence.

The source-context follow-up has run locally as
`phase107_gpt_swe_t1_source_context_followup`. It exposed the same locked
SQLFluff `L031.py` source slice to Summary and PaperToSkill because the
first-pass prompt asked the agent to inspect the repository while the one-shot
runner did not provide an interactive inspection tool.

The follow-up result is Summary 0.000 and PaperToSkill 0.000. In contrast to
the first pass, both candidate patches applied and both hidden test patches
applied, but both candidates failed the target test. The diagnostic
interpretation is task-contract/hidden-objective mismatch: both models edited
rule logic while the hidden scorer expected the specific L031 warning-message
change. This follow-up must be reported separately and must not silently
replace the first-pass SWE-T1 main row. The paper-facing main row selection is
locked by `results/real_reuse/main_run_selection.json`.

### Completed Diagnosis: SNAP Artifact Execution

SNAP-T1 and SNAP-T2 remain below the pre-registered success threshold in the
main table. The SNAP artifact-execution diagnosis in
`results/real_reuse/snapatac2_artifact_followup.{md,json}` found that the
selected SNAP rows are plan/JSON outputs under a non-executing runner, while
the scorer requires completed artifacts plus runtime/memory records. The
miniature fixtures are readable, but `snapatac2` is not importable in the
current Python environment.

The paired executable-artifact follow-up has now run as
`phase108_snapatac2_executable_artifact_followup` and is reported in
`results/real_reuse/snapatac2_executable_artifact_followup.{csv,md,json}`. It
kept Summary and PaperToSkill under the same fixture, scorer, resource budget,
hidden labels/proxy policy, and no-mid-run-human rule, but used a
pre-registered controlled scaffold rather than an LLM response. All four rows
score 1.000 under the existing SNAP scorer. This validates that concrete
artifacts plus runtime/memory records can satisfy the SNAP contract, but it
does not replace the main SNAP rows and does not show a PaperToSkill advantage.

## Table 2: Full Excerpt Sanity Check

Purpose: small sanity check only. It asks whether full excerpts dominate the
main setting enough to threaten the interpretation, while also recording context
cost.

| Task ID | Source Paper | Summary Score | PaperToSkill Score | Full Excerpt Score | Summary Tokens | PaperToSkill Tokens | Full Excerpt Tokens | Metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | 0.816 | 0.817 | 0.000 | 121 | 878 | 7366 | Validation score |
| SWE-T1 | SWE-agent | 0.000 | 0.000 | 0.000 | 89 | 1173 | 42048 | Tests passed / resolved |
| SNAP-T1 | SnapATAC2 | 0.000 | 0.500 | 0.250 | 72 | 1069 | 10297 | Runtime/memory/quality |

Current status: `results/real_reuse/full_excerpt_sanity.md` is scored for the
pre-registered sanity subset. Full Excerpt remains auxiliary; token counts are
local whitespace context proxies.

## Table 3: Component Ablation (Appendix Candidate)

Purpose: appendix candidate only. It tests which skill components matter, not
whether the overall approach works. Do not prioritize this until the core
real-reuse results are stable.

| Variant | Tasks | Avg Task Success | Workflow Score | Transfer Success | Failure Recovery | Unsupported Errors / Task |
| --- | --- | --- | --- | --- | --- | --- |
| Full PaperToSkill | 8 | TBD | TBD | TBD | TBD | TBD |
| No Transfer Notes | 8 or subset | TBD | TBD | TBD | TBD | TBD |
| No Failure Cases | 8 or subset | TBD | TBD | TBD | TBD | TBD |
| No Source Anchors | Optional subset | TBD | TBD | TBD | TBD | TBD |

Scoring rules:

- `Workflow Score` must use a pre-registered checklist extracted from the
  source paper's method section before seeing model outputs.
- `Unsupported Errors / Task` counts unsupported method claims, invented
  evidence, ignored constraints, or steps that contradict the source paper.
- Token cost should not live in this table unless the ablation specifically
  argues about context cost. Prefer the Full Excerpt sanity table and LLM
  ablation raw rows for context/cost accounting.

## Table 4: LLM Ablation Aggregate

Purpose: test whether the PaperToSkill benefit depends on a single model
family. It is not a broad model ranking.

| Model Family | Model Alias | Tasks | Summary Avg Score | PaperToSkill Avg Score | Reuse Success | Unsupported Errors / Task | Token Cost / Task | Availability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-family | gpt-5.5 | AIDE-T2, SWE-T2, and REF-T2 collected | 0.605 over collected slices | 0.333 over collected slices | REF-T2 tie; AIDE-T2 unfavorable; SWE-T2 joint failure | Not automatically judged | Provider usage / local proxy | All collected rows returned provider output; AIDE summary required 2 attempts |
| Claude-family | claude-opus-4-8 | AIDE-T2, SWE-T2, and REF-T2 attempted; no scored rows | Pending | Pending | Pending | Not automatically judged | Provider usage / local proxy | Provider HTTP 502 after 5 attempts per condition for all six condition rows |
| DeepSeek-family | deepseek-v4-flash | AIDE-T2, SWE-T2, and REF-T2 collected | 0.500 over collected slices | 0.500 over collected slices | REF-T2 tie; AIDE-T2 score tie below success threshold; SWE-T2 joint failure | Not automatically judged | Provider usage / local proxy | All collected rows HTTP 200 on attempt 1 |

Current pre-registered pilot: `benchmarks/real_reuse/llm_ablation_v0.json` and
`results/real_reuse/llm_ablation_plan.md` select AIDE-T2 and SWE-T2 as
positive PaperToSkill-only slices plus REF-T2 as a ceiling/control slice. The
plan uses GPT-family `gpt-5.5`, Claude-family `claude-opus-4-8`, and
DeepSeek-family `deepseek-v4-flash`, with 300-second provider timeouts, five
attempts, and five-second retry delays. Phase109 has collected all GPT-family
and DeepSeek-family scored rows for REF-T2, AIDE-T2, and SWE-T2, and attempted
all Claude-family REF-T2/AIDE-T2/SWE-T2 Summary/PaperToSkill condition rows.
GPT-family: REF-T2 is a ceiling/control pair
with Summary 1.000 and PaperToSkill 1.000; AIDE-T2 is unfavorable
(0.814/0.000) because the PaperToSkill candidate timed out under the
300-second local scorer; SWE-T2 is a joint-failure signal (0.000/0.000) because
both candidate patches fail to apply. DeepSeek-family: REF-T2 is another
ceiling/control tie (1.000/1.000), AIDE-T2 ties below the success threshold
(0.500/0.500), and SWE-T2 is another joint-failure signal (0.000/0.000).
Claude-family REF-T2, AIDE-T2, and SWE-T2 are all blocked by provider HTTP 502
after five attempts per condition, so they remain availability metadata and do
not enter the scored aggregate. The aggregate currently has 12 collected scored
rows and 6 pending rows; this is auxiliary model/repetition evidence, not a
main-table replacement and not aggregate PaperToSkill advantage.

## Table 5: LLM Ablation Raw Rows

Purpose: raw `task x model x condition` table for audit and appendix.

| Task ID | Source Paper | Model Family | Model Alias | Condition | Task Score | Success | Unsupported Errors | Tokens | Failure Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T2 | AIDE | GPT-family | gpt-5.5 | Summary | 0.814 | True | Not automatically judged | 7788 |  |
| AIDE-T2 | AIDE | GPT-family | gpt-5.5 | PaperToSkill | 0.000 | False | Not automatically judged | 8714 | timeout after 300s |
| SWE-T2 | SWE-agent | GPT-family | gpt-5.5 | Summary | 0.000 | False | Not automatically judged | 5310 | patch_apply_failed |
| SWE-T2 | SWE-agent | GPT-family | gpt-5.5 | PaperToSkill | 0.000 | False | Not automatically judged | 8053 | patch_apply_failed |
| REF-T2 | Reflexion | GPT-family | gpt-5.5 | Summary | 1.000 | True | Not automatically judged | 5171 |  |
| REF-T2 | Reflexion | GPT-family | gpt-5.5 | PaperToSkill | 1.000 | True | Not automatically judged | 5655 |  |
| AIDE-T2 | AIDE | DeepSeek-family | deepseek-v4-flash | Summary | 0.500 | False | Not automatically judged | 1664 |  |
| AIDE-T2 | AIDE | DeepSeek-family | deepseek-v4-flash | PaperToSkill | 0.500 | False | Not automatically judged | 3350 |  |
| SWE-T2 | SWE-agent | DeepSeek-family | deepseek-v4-flash | Summary | 0.000 | False | Not automatically judged | 988 | patch_apply_failed |
| SWE-T2 | SWE-agent | DeepSeek-family | deepseek-v4-flash | PaperToSkill | 0.000 | False | Not automatically judged | 3210 | patch_apply_failed |
| REF-T2 | Reflexion | DeepSeek-family | deepseek-v4-flash | Summary | 1.000 | True | Not automatically judged | 1057 |  |
| REF-T2 | Reflexion | DeepSeek-family | deepseek-v4-flash | PaperToSkill | 1.000 | True | Not automatically judged | 1493 |  |
| REF-T2 | Reflexion | Claude-family | claude-opus-4-8 | Summary | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |
| REF-T2 | Reflexion | Claude-family | claude-opus-4-8 | PaperToSkill | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |
| AIDE-T2 | AIDE | Claude-family | claude-opus-4-8 | Summary | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |
| AIDE-T2 | AIDE | Claude-family | claude-opus-4-8 | PaperToSkill | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |
| SWE-T2 | SWE-agent | Claude-family | claude-opus-4-8 | Summary | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |
| SWE-T2 | SWE-agent | Claude-family | claude-opus-4-8 | PaperToSkill | Provider 502 | Pending | Not automatically judged |  | HTTP 502 after 5 attempts |

## Table 6: Quality / Grounding Gate

Purpose: keep existing deterministic/offline evidence in the paper, but in a
supporting role.

| Source Paper | Skill Rubric | Source Support Rate | Invalid Source Ranges | Human Fidelity Status | Package Gate |
| --- | --- | --- | --- | --- | --- |
| AIDE | Current package value | Current package value | Current package value | Pending unless annotated | Current package gate |
| SWE-agent | TBD | TBD | TBD | TBD | TBD |
| Reflexion | Current package value | Current package value | Current package value | Pending unless annotated | Current package gate |
| SnapATAC2 | TBD | TBD | TBD | TBD | TBD |
| Toolformer sanity | Current package value | Current package value | Current package value | Pending unless annotated | Current package gate |
| AI Scientist-v2 sanity | Current package value | Current package value | Current package value | Pending unless annotated | Current package gate |

## Table 7: User Study (Last / Optional)

Purpose: optional final-stage evidence only. It is needed only for claims about
user efficiency, user workflow improvement, usability, or reduced human
intervention. It is not part of the core real-reuse effectiveness table and
should not be started before the core experiment and remaining auxiliary
analyses are stable.

| Condition | Users / Runs | Success Rate | Avg Task Score | Time to Completion | Interventions | Expert Fidelity Score | Token Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Summary | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| PaperToSkill | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Execution Dependencies

1. Verify paper source, license, code availability, and benchmark setup for each
   selected paper.
2. Create task specs under `benchmarks/real_reuse/` (complete for eight tasks).
3. Create fixture requirement manifests, candidate manifests, and asset locks
   under `benchmarks/real_reuse/fixtures/`,
   `benchmarks/real_reuse/fixture_candidates/`, and
   `benchmarks/real_reuse/asset_locks/` (complete for eight tasks).
4. Create or record context conditions under `baselines/real_reuse/` and
   `generated_skills/` (complete for REF-T1/REF-T2 and SNAP-T1/T2; SWE-agent
   skill context is ready and task-specific SWE Summary contexts are generated
   during fixture preparation).
5. Implement task-specific preparers and scorers that consume the asset locks
   without exposing hidden scorer assets to model-visible context (complete for
   REF-T1/REF-T2, AIDE-T1/T2, SWE-T1/T2, and SNAP-T1/T2).
6. Implement a runner that logs command, model family, condition, task output,
   metric, tokens, time, and failure reason (complete for REF-T1/REF-T2,
   AIDE-T1/T2, SWE-T1/T2, and SNAP-T1/T2).
7. Implement a scorer/aggregator that emits raw rows and table-ready CSV/MD
   files under `results/real_reuse/` (complete for the first single-run pass:
   all eight rows are filled in the main table). Paper-facing main rows should
   be selected through `results/real_reuse/main_run_selection.json` so
   follow-up raw rows remain auditable without overwriting the main cells.
8. After broader raw results exist, revise the AAAI Abstract, Contributions,
   Results, Discussion, Limitations, and Conclusion (in progress for the
   first-pass mixed/failure-boundary evidence boundary).

## Evidence Boundaries

- This plan now has one GPT-family Summary-vs-PaperToSkill pass for all eight
  planned rows. The result is mixed and should be read as first-pass downstream
  evidence plus failure-boundary evidence, not aggregate effectiveness.
- After rerunning the same saved AIDE outputs with a 300-second local scorer
  budget, AIDE-T1 scores 0.816/0.817 and is solved by both conditions, while
  AIDE-T2 scores 0.000/0.826 and is a PaperToSkill-only success. SWE-T1 scores
  0.000/0.000 because generated patches fail to apply; SWE-T2 scores
  0.000/1.000; REF-T1/REF-T2 score 1.000/1.000; SNAP-T1/SNAP-T2 score
  0.000/0.500 and 0.200/0.400 but fail the local success threshold.
- SWE-T1 phase107 is a completed shared-source-context follow-up, not a main
  row replacement. It also scores Summary 0.000 and PaperToSkill 0.000, but
  both candidate patches apply and then fail the hidden test. It is now
  reported as dedicated diagnostic follow-up evidence in
  `results/real_reuse/swe_t1_source_context_followup.{csv,md,json}` and in the
  AAAI table set.
- The SNAP artifact-execution diagnosis and paired executable-artifact
  follow-up are complete diagnostic evidence, not main-row replacements. The
  phase108 follow-up scores 1.000 for Summary and PaperToSkill on SNAP-T1/T2
  using a controlled scaffold, so it validates the artifact/runtime/memory
  contract path but does not establish PaperToSkill advantage.
- Existing deterministic/offline results remain useful as quality, grounding,
  and cost gates.
- The older saved-response model ablation remains a usage-plan/output-contract
  result; it does not prove live downstream task success.
- The real-reuse LLM ablation pilot is pre-registered and partially collected.
  Current aggregate files report 12 collected scored rows out of 18 expected
  rows: all GPT-family and DeepSeek-family rows are collected; Claude-family
  rows remain pending because the attempted REF-T2 control pair returned HTTP
  502 after five attempts per condition. Pending rows and provider errors are
  not negative method evidence; they are availability metadata.
- AI-Scientist-v2 evidence remains bounded integration/synthetic sensitivity
  evidence.
- Do not claim that PaperToSkill beats an original paper method unless the same
  experimental setting is reproduced or the claim is explicitly framed as a
  reported-reference comparison.
