# Phase 47: DeepSeek Follow-Up Handoff

## Objective

Make the user's later DeepSeek addition easier to execute and review without
claiming any DeepSeek result before a concrete alias, endpoint, and response
files exist.

## Actions

- Added `scripts/check_deepseek_followup.py`, a local handoff/preflight report
  generator for `deepseek_followup_slot`.
- Added `tests/test_check_deepseek_followup.py` for the current placeholder
  state and a future configured-but-not-yet-run state.
- Generated `results/deepseek_followup_handoff/handoff.json` and `.md`.
- Integrated the handoff report into the usage-example, active-goal, and
  reproducibility package gates.
- Updated the model-ablation usage example and runbook to call the handoff
  checker before and after editing the DeepSeek slot.

## Results

- Current handoff status is `pending_user_configuration`.
- The report has 5 ready checks, 2 pending checks, and 0 failed checks.
- Ready checks cover slot presence, two prompt rows, prompt files, response
  paths, and environment variable names.
- Pending checks cover the placeholder alias and missing DeepSeek response
  files.
- No DeepSeek live request was made and no DeepSeek response file was saved.

## Evidence Boundary

This phase improves local DeepSeek follow-up readiness only. It does not
complete DeepSeek model ablations, does not collect provider billing, does not
prove live task success, and does not change the pending status of the active
goal.
