# Real Reuse Experiment Plan

Date: 2026-07-03

Status: planned. This file records the next-stage experiment design. It is not
evidence that the experiments have been run.

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

- Main evidence should use original task metrics where possible, such as
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
- No mid-run human intervention in the first pass. If human usability is tested
  later, use blind review or a separately logged human-study protocol.

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

| Task ID | Source Paper | Domain | Original-style Input | Required Output | Paper Reference / Baseline | Reference Score | Summary Score | PaperToSkill Score | Reproducibility / Fidelity | Metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | ML engineering | Dataset, objective metric, and starter workspace | Improved ML solution script or submission | Paper baseline or reported reference | TBD | TBD | TBD | TBD | Validation score / Kaggle-style metric |
| AIDE-T2 | AIDE | ML engineering | Weak or failed ML script plus score/error feedback | Improved debug/search trajectory and final solution | Paper baseline or reported reference | TBD | TBD | TBD | TBD | Validation score / best-node score |
| SWE-T1 | SWE-agent | Software engineering | GitHub issue, repository, and tests | Patch that passes tests | SWE-bench-style baseline/reference | TBD | TBD | TBD | TBD | Tests passed / resolved |
| SWE-T2 | SWE-agent | Software engineering | Repository bug plus failing test | Minimal patch and verification log | SWE-bench-style baseline/reference | TBD | TBD | TBD | TBD | Tests passed / resolved |
| REF-T1 | Reflexion | Reasoning QA | HotPotQA-style question with retrieval context/tools | Final answer after reflection loop | No-reflection or ReAct baseline | TBD | TBD | TBD | TBD | Exact match / F1 / success |
| REF-T2 | Reflexion | Decision or programming | Failed first attempt plus environment feedback | Corrected second attempt using reflection | No-reflection baseline | TBD | TBD | TBD | TBD | Success / pass rate |
| SNAP-T1 | SnapATAC2 | Single-cell omics | Small scATAC/scRNA dataset and analysis objective | Runnable analysis pipeline | Scanpy, Seurat, or LSI-style reference | TBD | TBD | TBD | TBD | Runtime, memory, clustering/embedding metric |
| SNAP-T2 | SnapATAC2 | Single-cell omics | Single-cell dataset and target cell groups | Dimensionality reduction, clustering, or marker output | Paper reference/baseline | TBD | TBD | TBD | TBD | ARI/NMI/runtime/memory |

Column definitions:

- `Reference Score`: the original paper's reported score or a locally
  reproduced baseline. Mark the source explicitly.
- `Summary Score`: score when the agent receives a concise method summary
  instead of a PaperToSkill skill.
- `PaperToSkill Score`: score when the agent receives the generated skill.
- `Reproducibility / Fidelity`: whether the run followed the source-paper
  method without unsupported extra steps. This can be binary plus a short note.
- `Metric`: the task's original metric family wherever possible.

## Table 2: Full Excerpt Sanity Check

Purpose: small sanity check only. It asks whether full excerpts dominate the
main setting enough to threaten the interpretation, while also recording context
cost.

| Task ID | Source Paper | Summary Score | PaperToSkill Score | Full Excerpt Score | Summary Tokens | PaperToSkill Tokens | Full Excerpt Tokens | Metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | TBD | TBD | TBD | TBD | TBD | TBD | Validation score |
| SWE-T1 | SWE-agent | TBD | TBD | TBD | TBD | TBD | TBD | Tests passed |
| SNAP-T1 | SnapATAC2 | TBD | TBD | TBD | TBD | TBD | TBD | Runtime/memory/quality |

## Table 3: Component Ablation

Purpose: optional/appendix unless the main experiment is strong enough. It tests
which skill components matter, not whether the overall approach works.

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
  argues about context cost. Prefer Table 6 for cost.

## Table 4: Domain Robustness Aggregate

Purpose: summarize whether results are confined to one domain.

| Domain | Papers | Tasks | Reuse Success | Avg PaperToSkill Score | Avg Reference Score | Main Failure Mode |
| --- | --- | --- | --- | --- | --- | --- |
| ML engineering | AIDE | 2 | TBD | TBD | TBD | TBD |
| Software engineering | SWE-agent | 2 | TBD | TBD | TBD | TBD |
| Reasoning / decision-making | Reflexion | 2 | TBD | TBD | TBD | TBD |
| Single-cell data analysis | SnapATAC2 | 2 | TBD | TBD | TBD | TBD |

## Table 5: Domain Robustness Raw Rows

Purpose: preserve raw evidence so small-sample aggregates do not overstate the
result.

| Task ID | Source Paper | Domain | PaperToSkill Score | Reference Score | Summary Score | Success | Failure Mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | ML engineering | TBD | TBD | TBD | TBD | TBD |
| AIDE-T2 | AIDE | ML engineering | TBD | TBD | TBD | TBD | TBD |
| SWE-T1 | SWE-agent | Software engineering | TBD | TBD | TBD | TBD | TBD |
| SWE-T2 | SWE-agent | Software engineering | TBD | TBD | TBD | TBD | TBD |
| REF-T1 | Reflexion | Reasoning / QA | TBD | TBD | TBD | TBD | TBD |
| REF-T2 | Reflexion | Decision / programming | TBD | TBD | TBD | TBD | TBD |
| SNAP-T1 | SnapATAC2 | Single-cell data analysis | TBD | TBD | TBD | TBD | TBD |
| SNAP-T2 | SnapATAC2 | Single-cell data analysis | TBD | TBD | TBD | TBD | TBD |

## Table 6: Agent / User Cost

Purpose: measure whether PaperToSkill reduces practical cost in a real-use
workflow.

| Condition | Users / Runs | Success Rate | Avg Task Score | Time to Completion | Interventions | Expert Fidelity Score | Token Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Summary | 8 tasks x N runs | TBD | TBD | TBD | TBD | TBD | TBD |
| PaperToSkill | 8 tasks x N runs | TBD | TBD | TBD | TBD | TBD | TBD |
| Full Excerpt sanity | 3 tasks x N runs | TBD | TBD | TBD | TBD | TBD | TBD |

First-pass rule: use agent-only execution with no mid-run human intervention.
Human work, if used, should be blind review after the run.

## Table 7: LLM Ablation Aggregate

Purpose: test whether the PaperToSkill benefit depends on a single model
family. It is not a broad model ranking.

| Model Family | Model Alias | Tasks | Summary Avg Score | PaperToSkill Avg Score | Reuse Success | Unsupported Errors / Task | Token Cost / Task | Availability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude-family | TBD | 8 | TBD | TBD | TBD | TBD | TBD | TBD |
| GPT-family | TBD | 8 | TBD | TBD | TBD | TBD | TBD | TBD |
| DeepSeek-family | TBD | 8 | TBD | TBD | TBD | TBD | TBD | TBD |

## Table 8: LLM Ablation Raw Rows

Purpose: raw `task x model x condition` table for audit and appendix.

| Task ID | Source Paper | Model Family | Model Alias | Condition | Task Score | Success | Unsupported Errors | Tokens | Failure Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AIDE-T1 | AIDE | Claude-family | TBD | Summary | TBD | TBD | TBD | TBD | TBD |
| AIDE-T1 | AIDE | Claude-family | TBD | PaperToSkill | TBD | TBD | TBD | TBD | TBD |
| AIDE-T1 | AIDE | GPT-family | TBD | Summary | TBD | TBD | TBD | TBD | TBD |
| AIDE-T1 | AIDE | GPT-family | TBD | PaperToSkill | TBD | TBD | TBD | TBD | TBD |
| AIDE-T1 | AIDE | DeepSeek-family | TBD | Summary | TBD | TBD | TBD | TBD | TBD |
| AIDE-T1 | AIDE | DeepSeek-family | TBD | PaperToSkill | TBD | TBD | TBD | TBD | TBD |
| ... | Repeat for all eight tasks | ... | ... | ... | ... | ... | ... | ... | ... |

## Table 9: Quality / Grounding Gate

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

## Execution Dependencies

1. Verify paper source, license, code availability, and benchmark setup for each
   selected paper.
2. Create task specs under `benchmarks/real_reuse/` (complete for eight tasks).
3. Create fixture requirement manifests, candidate manifests, and asset locks
   under `benchmarks/real_reuse/fixtures/`,
   `benchmarks/real_reuse/fixture_candidates/`, and
   `benchmarks/real_reuse/asset_locks/` (complete for eight tasks).
4. Create or record context conditions under `baselines/real_reuse/` and
   `generated_skills/` (complete for REF-T1/REF-T2).
5. Implement task-specific preparers and scorers that consume the asset locks
   without exposing hidden scorer assets to model-visible context (complete for
   REF-T1/REF-T2).
6. Implement a runner that logs command, model family, condition, task output,
   metric, tokens, time, and failure reason (complete for REF-T1/REF-T2).
7. Implement a scorer/aggregator that emits raw rows and table-ready CSV/MD
   files under `results/real_reuse/` (partially complete: REF rows fill the
   main table; remaining task families are pending).
8. After broader raw results exist, revise the AAAI Abstract, Contributions,
   Results, Discussion, Limitations, and Conclusion. Current AAAI text has only
   a cautious REF partial-result update.

## Evidence Boundaries

- This plan is now partially executed for REF-T1/REF-T2 only.
- The REF rows have one GPT-family Summary-vs-PaperToSkill run and both
  conditions score 1.000 on both locked tasks. This validates the execution
  path but does not show aggregate PaperToSkill advantage over Summary.
- Current AIDE, SWE-agent, and SnapATAC2 asset locks fix source revisions,
  concrete task instances, local materialization targets, hidden scorer assets,
  and scorer/preparer contracts, but they do not yet materialize data or
  produce scores.
- Existing deterministic/offline results remain useful as quality, grounding,
  and cost gates.
- The older saved-response model ablation remains a usage-plan/output-contract
  result; it does not prove live downstream task success.
- AI-Scientist-v2 evidence remains bounded integration/synthetic sensitivity
  evidence.
- Do not claim that PaperToSkill beats an original paper method unless the same
  experimental setting is reproduced or the claim is explicitly framed as a
  reported-reference comparison.
