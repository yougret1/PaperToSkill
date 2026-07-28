# SkillsBench B/F/S Experiment Plan

## Boundary

- Public behavior benchmark: SkillsBench v1.1 at commit
  `9a1f4dd5f7659f75707435da3ce854b6e48321d1`.
- Executor: GPT-5.6 Sol through the OpenAI Responses protocol and the pinned
  BenchFlow `codex-acp` agent.
- Conditions: `B` has no skill bundle, `F` has the official curated bundle,
  and `S` has an independently implemented SkillReducer heuristic candidate.
- The reducer is not the official SkillReducer artifact. Results must not be
  described as an official system-level head-to-head comparison.
- SkillsBench tests task behavior. It does not validate paper-to-source-span,
  atom, dependency, or semantic-gate correctness.

## Frozen Selection

The material builder creates all candidates before model execution. A task is
eligible only when `S` reduces eager `SKILL.md` tokens. The main set uses one
hard and two medium tasks in each of eight SkillsBench categories, selected by
a fixed SHA-256 seed after applying resource filters. Five disjoint tasks form
a pilot-only set.

## Execution

1. Run one pilot task through `B/F/S` to verify Responses-based terminal tool
   use, fresh Docker state, skill isolation, and official verifier output.
2. Complete all five pilot tasks once. Pilot outcomes do not enter the main
   estimates and do not change the frozen main roster.
3. If the pipeline gate passes, run the 24 main tasks for three fresh
   repetitions under balanced task-specific condition order.
4. Preserve raw result JSON, trajectories, environment/verifier logs, hashes,
   and terminal/invalid status under `research/workflow_runs/`.

## Interpretation

The primary endpoint is the official deterministic task reward. Report paired
`F-B`, `S-B`, and `S-F` effects over frozen public tasks with task-clustered
uncertainty. Infrastructure failures remain invalid rows and are never scored
as task failures. A high `B` rate is reported as a diagnostic limitation, not
used to cherry-pick replacement tasks.
