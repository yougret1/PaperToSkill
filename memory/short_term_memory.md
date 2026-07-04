# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-04.

## Current Task

- Latest user request / active goal: save the current phase with git, upload to
  GitHub, then continue the core real-reuse main experiment. Use generous
  timeout/retry budgets for LLM service calls, keep provider instability
  separate from method quality, and record network/download blockers in
  `C:\Users\19351\Desktop\tem\toHuman.md` before continuing other work.
- Local logs remain excluded unless explicitly doing a phase log:
  `research/run_logs/**` and `research/stage_log.md`.
- `C:\Users\19351\Desktop\tem\ok.txt` was absent at the latest check.
- Preserve the completed phase107 row-selection and follow-up-reporting changes
  already in the worktree. They include appended SWE-T1 follow-up raw rows and
  run outputs, row-selection support in
  `scripts/build_real_reuse_paper_tables.py` and
  `scripts/build_real_reuse_failure_analysis.py`,
  `results/real_reuse/main_run_selection.json`, and
  `results/real_reuse/swe_t1_source_context_followup.{csv,md,json}`. Do not
  revert them during this records-only sync.

## Record Sync Completed This Turn

- Rewrote `C:\Users\19351\Desktop\tem\toHuman.md` so it no longer treats
  GitHub connectivity, AAAI final-submission advice, provider billing,
  domain-robustness planning, component ablation, or a user study as the
  current human action.
- Added the record-sync boundary to `toHuman.md`: do not modify local logs,
  do not reopen a separate domain-robustness experiment, keep component
  ablation appendix-only, keep user-study work last/optional, and record
  only genuinely blocking network/download failures there.
- Rewrote `C:\Users\19351\Desktop\tem\nextStep.md` into the current
  experiment plan: core real-reuse first, auxiliary evidence collected
  opportunistically and analyzed later, component ablation appendix-only, and
  user study last/optional.
- Current `toHuman.md` says to create
  `C:\Users\19351\Desktop\tem\ok.txt` only when human-fidelity annotation is
  complete or when a concrete core real-reuse asset has been placed.
- Updated non-log repository entry records to match the same policy:
  `README.md`, `research/experiment_queue.md`,
  `research/real_reuse_experiment_plan.md`, `research/runbook.md`, and
  `memory/long_term_memory.md`.
- Local logs remain untouched: `research/run_logs/**` and
  `research/stage_log.md`.
- Runbook/queue/review records should point future execution back to the
  core real-reuse stabilization path and use generous model-call
  timeout/retry budgets because the third-party service is unstable.
- Current records should mention the completed SWE-T1 source-context follow-up
  boundary: phase107 exposed the same locked SQLFluff source slice to Summary
  and PaperToSkill; both calls succeeded; both patches applied; both hidden
  tests failed; both task scores remain 0.000. Preserve the original
  first-pass SWE-T1 rows as the paper-facing main rows and report phase107 only
  as shared-source-context follow-up evidence.
- Current records should mention that `results/real_reuse/main_run_selection.json`
  locks paper-facing main-table rows so follow-up raw rows do not silently
  replace the pre-registered main experiment cells.
- Current records should mention that the dedicated SWE-T1 source-context
  follow-up table/report has been generated and that
  `scripts/check_paper_tables.py --strict` passed with 250 ready checks and 0
  failed checks after adding the follow-up table consistency checks.

## Current Core Experiment State

- Main experiment: `Real-Reuse Main Results`, comparing `Summary` vs
  `PaperToSkill` under the same locked paper-task, input/output, scorer, and
  local run setting.
- This is not a real-user study. The main metrics are source-paper-style
  objective task metrics, not user-experience metrics.
- Provider latency, API timeout, retry count, and third-party service
  instability are not core effectiveness metrics. Give model calls more timeout
  and retry budget, and record provider availability separately.
- Current first GPT-family `gpt-5.5` pass has scored all eight rows:
  AIDE-T1 `0.816/0.817` solved by both; AIDE-T2 `0.000/0.826`
  PaperToSkill-only success; SWE-T1 `0.000/0.000` patch-apply failure;
  SWE-T2 `0.000/1.000` PaperToSkill-only success; REF-T1/T2 `1.000/1.000`;
  SNAP-T1/T2 `0.000/0.500` and `0.200/0.400` below success threshold.
- Evidence boundary: this is mixed first-pass downstream stress-test and
  failure-boundary evidence, not aggregate PaperToSkill superiority over
  Summary.
- SWE-T1 phase107 shared-source-context follow-up is complete locally with
  Summary/PaperToSkill both `0.000/0.000`. Unlike the first-pass row, both
  candidate patches applied; the failure reason is `test_command_failed`
  because the hidden test expected the specific L031 warning-message change
  while both candidates edited rule logic. This is diagnostic follow-up
  evidence, not a main-table replacement.

## Current Auxiliary Evidence Policy

- Full Excerpt sanity is scored for AIDE-T1, SWE-T1, and SNAP-T1, but it is
  auxiliary sanity/cost/context evidence only, not a main baseline.
- LLM ablation should be attached to the real-reuse task protocol after the
  core rows stabilize; it should not rely on the older saved-response
  usage-plan protocol as downstream task evidence.
- Human-fidelity annotation supports semantic fidelity and reviewability, not
  main task effectiveness. It remains pending: 0 scored rows and 24 pending
  paper-by-criterion cells.
- Quality/grounding gates remain supporting evidence: rubric, source-span,
  source-map, context coverage, usage examples, token accounting, paper-table
  gates, and claim gates.
- Do not keep a separate domain breadth/coverage auxiliary experiment; the
  selected main paper-tasks provide the current breadth.

## Model And External Evidence State

- GPT protocol refresh completed both current rows with `gpt-5.5`.
- DeepSeek completed both current rows with `deepseek-v4-flash`; the DeepSeek
  handoff reports `responses_present`.
- Latest Claude protocol refresh used Anthropic Messages but was blocked by
  provider HTTP 502, so scored Claude rows come from previously saved response
  files. Treat the 502 as provider availability, not model quality.
- Local token accounting is complete for the current evidence set and replaces
  provider billing/success-per-dollar claims in the current paper scope.
- AI-Scientist-v2 dry-run succeeded historically. The bounded
  AI-Scientist-v2 LLM-client smoke is now complete, and the bounded full
  live-run handoff is complete with one completion directory. This is bounded
  integration/synthetic sensitivity evidence, not human fidelity, real-data
  validation, or broad live research-task success.
- AAAI decision is recorded as `wait_for_external_evidence`; final submission
  readiness remains pending under that policy.

## Immediate Next Actions

1. Phase save and remote backup are complete: `git push origin main` advanced
   GitHub from `cf7b54e` to `4040f56`, so commits `8b50758` and `4040f56` are
   backed up remotely.
2. Continue SNAP artifact-completion/budget inspection or the next
   pre-registered failure-heavy real-reuse follow-up, keeping Summary and
   PaperToSkill paired under the same task/scorer contract.
3. During core reruns, collect auxiliary raw data where cheap: provider
   availability, failure reasons, context/token proxies, and raw rows needed
   for future real-reuse LLM ablation.
4. Run broader verification gates before the next phase save:
   `check_real_reuse_benchmark.py`, `check_paper_tables.py`,
   `check_reproducibility_package.py`, `check_goal_completion.py`,
   `check_paper_claims.py`, `git diff --check`, and a raw-key scan.
5. Save and push the next meaningful phase after new core-experiment progress.

## Boundaries

Do not claim:

- Aggregate downstream effectiveness or broad superiority over Summary.
- Human-validated semantic fidelity.
- Provider billing, live invoices, or success-per-dollar evidence.
- Saved-response scoring as proof of live downstream task success.
- Reliable arbitrary-PDF-to-skill automation.
- Final AAAI submission readiness.

Do not modify:

- `research/run_logs/**`
- `research/stage_log.md`
