# Phase 79 Real-Reuse Planning Sync

Date: 2026-07-03

## Purpose

Align the project planning files with the user's revised validity target:
PaperToSkill should ultimately be evaluated by whether it helps agents or users
reuse a source paper's method on original-style input/output tasks.

## Actions

- Added `research/real_reuse_experiment_plan.md` as the next-stage source of
  truth for task rows, table layouts, candidate papers, metrics, baselines, and
  evidence boundaries.
- Updated `paper/outline.md` to distinguish current completed evidence from
  planned real-reuse validity evidence.
- Updated `research/experiment_queue.md` with the planned E5 real-reuse task
  grid and downstream runner/scorer/ablation work items.
- Updated `research/claim_evidence_matrix.md` with the new reuse claim marked
  as planned, not supported.
- Updated `research/goal_completion_audit.md` to keep the active goal open
  until real-reuse experiments, human fidelity, and final AAAI readiness are
  completed.
- Updated `research/runbook.md` and `research/artifact_map.md` with future
  artifact paths and execution boundaries.

## Planned Main Papers

| Paper | Domain | Role |
| --- | --- | --- |
| AIDE | ML engineering | Main |
| SWE-agent | Software engineering | Main |
| Reflexion | Reasoning / QA / decision-making | Main |
| SnapATAC2 | Single-cell omics data analysis | Main non-agent case |
| Toolformer | Tool use | Sanity / auxiliary |
| AI Scientist-v2 | Automated research | Sanity / auxiliary |

## Evidence Boundary

No new real-reuse experiment has been executed in this phase. The current AAAI
Results section should not be promoted beyond deterministic/offline evidence
until raw real-reuse rows exist under future `results/real_reuse/` artifacts.

The current completed evidence remains:

- deterministic/offline skill quality and coverage;
- source grounding and compactness/cost proxies;
- saved-response live-transfer and model-ablation output-contract scoring;
- bounded AI-Scientist-v2 integration/synthetic sensitivity evidence;
- bounded Paper2Agent artifact/workflow comparison.

The new planned evidence is:

- eight original-style `paper-task` rows comparing Summary and PaperToSkill;
- small Full Excerpt sanity check;
- optional component ablation;
- real-reuse LLM ablation across Claude-family, GPT-family, and
  DeepSeek-family slots.
