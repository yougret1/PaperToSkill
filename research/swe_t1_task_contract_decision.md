# SWE-T1 Task-Contract Decision

Date: 2026-07-04

Evidence boundary: this is a pre-registered decision note for the SWE-T1
real-reuse row. It does not add task-success evidence, does not replace the
paper-facing main row, and does not authorize a rerun by itself.

Machine-readable source:
`benchmarks/real_reuse/swe_t1_task_contract_decision_v0.json`

## Decision

Freeze the current SWE-T1 paper-facing row as failure-boundary evidence.

Do not spend more model calls on SWE-T1 under the current hidden-test contract.
If a stronger SWE-T1 row is needed later, first pre-register a revised
issue-aligned scorer/test contract, then rerun Summary and PaperToSkill as a
paired comparison.

## Evidence Reviewed

| Artifact | Finding |
| --- | --- |
| `results/real_reuse/failure_analysis.md` | First-pass Summary and PaperToSkill both scored 0.000 because patches failed to apply. |
| `results/real_reuse/swe_t1_source_context_followup.md` | Phase107 shared-source-context follow-up made both candidate patches apply, but both still failed the hidden target test. |
| `benchmarks/real_reuse/assets/SWE-T1/issue_description.md` | The model-visible task asks for a TSQL no-join alias false-positive fix. |
| `benchmarks/real_reuse/assets/SWE-T1/scorer_only/test.patch` | The scorer-only hidden test patch checks a specific L031 warning-message text change rather than directly testing the no-join alias false-positive reproduction. |

## Diagnosis

SWE-T1 currently mixes two different failure boundaries:

| Stage | Summary | PaperToSkill | Boundary |
| --- | --- | --- | --- |
| First pass | patch apply failed | patch apply failed | Patch-format/apply boundary |
| Phase107 source-context follow-up | patch applied, hidden test failed | patch applied, hidden test failed | Task-contract/hidden-objective boundary |

The phase107 patches were issue-reasonable rule-logic fixes, but the hidden
test target is narrower: it asserts a specific L031 warning-message text
change. That means another rerun under the same hidden-test contract would
mostly test whether the model guesses a hidden message-text change, not whether
PaperToSkill helps reuse the SWE-agent-style issue-to-patch method.

## Current Main-Row Policy

- Preserve the first-pass SWE-T1 main-row scores: Summary 0.000 and
  PaperToSkill 0.000.
- Keep phase107 as diagnostic follow-up only.
- Do not update `results/real_reuse/main_run_selection.json` for SWE-T1 unless
  a future paired rerun is explicitly pre-registered and promoted.
- Do not expose scorer-only `gold.patch` or `test.patch` content in future
  model prompts.

## Future Revision Rule

A future SWE-T1 revision is allowed only if it is pre-registered before model
calls and satisfies all of the following:

- Summary and PaperToSkill remain paired.
- Both conditions use the same locked SQLFluff instance, source context,
  scorer, resource budget, model family, and no-mid-run-human rule.
- Hidden tests directly exercise the issue reproduction queries from the
  model-visible issue description.
- Message-text assertions may be retained only as secondary regression checks,
  not as the sole success criterion.
- Any replacement of the paper-facing main row requires explicit promotion
  through `results/real_reuse/main_run_selection.json`.
