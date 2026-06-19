# Phase 66: AAAI Decision Record Helper

Date: 2026-06-20

## Objective

Make the final AAAI submission decision record easier to create safely after a
human research lead selects a policy, without selecting an option by default.

## Actions

- Added `scripts/generate_aaai_submission_decision.py`.
- Added `tests/test_generate_aaai_submission_decision.py`.
- Updated `scripts/check_aaai_submission_decision.py` so the preflight lists
  the generator as an input and shows helper commands for both options.
- Updated `research/runbook.md`, `research/artifact_map.md`, and
  `scripts/check_reproducibility_package.py`.

## Result

- The helper writes `research/aaai_submission_decision.md` only when an
  explicit selected option, decision owner, decision date, claim boundary, and
  evidence policy are supplied.
- The helper validates the selected option against the current decision
  preflight unless explicitly told to skip that check for isolated tests.
- The helper rejects raw API-key-like material and empty required fields.
- No human decision record was generated in this phase.

## Verification

```powershell
python -m unittest tests.test_generate_aaai_submission_decision tests.test_check_aaai_submission_decision -v
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_goal_completion.py --strict
```

## Evidence Boundary

This phase adds a local decision-record helper only. It does not select an AAAI
submission decision, submit the paper, complete DeepSeek, complete
AI-Scientist-v2 smoke/full live run, collect human annotation, or collect
provider billing.
