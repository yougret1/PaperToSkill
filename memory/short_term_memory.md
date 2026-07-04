# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-04.

## Current Task

- Latest user request: update the related current records, including
  `C:\Users\19351\Desktop\tem\toHuman.md`, but do not modify local logs.
- Local logs excluded from this sync: `research/run_logs/**` and
  `research/stage_log.md`.
- `C:\Users\19351\Desktop\tem\ok.txt` was absent at the latest check.

## Record Sync Completed This Turn

- Rewrote `C:\Users\19351\Desktop\tem\toHuman.md` so it no longer treats
  GitHub connectivity, AAAI final-submission advice, provider billing, or a
  user study as the current human action.
- Rewrote `C:\Users\19351\Desktop\tem\nextStep.md` into the current
  experiment plan: core real-reuse first, auxiliary evidence collected
  opportunistically and analyzed later, component ablation appendix-only, and
  user study last/optional.
- Current `toHuman.md` says to create
  `C:\Users\19351\Desktop\tem\ok.txt` only when human-fidelity annotation is
  complete or when a concrete core real-reuse asset has been placed.

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

1. Finish record sync by refreshing any non-log entry records that still
   contain stale current-state wording.
2. Regenerate dependent readiness reports in order so stale fail states from
   old report dependencies clear:
   `check_aaai_package`, `check_paper_tables`, `check_paper_claims`,
   `check_submission_review`, `check_usage_examples`,
   `check_aaai_submission_decision`, `check_reproducibility_package`,
   `check_goal_completion`.
3. Run targeted searches for stale current-state wording around old pending
   fixture states, stale AI-Scientist-v2 blocked status, and old GitHub-push
   human-action wording, excluding `research/run_logs/**` and
   `research/stage_log.md`.

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
