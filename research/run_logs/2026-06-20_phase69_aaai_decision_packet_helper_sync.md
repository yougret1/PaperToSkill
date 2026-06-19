# Phase 69: AAAI Decision Packet Helper Sync

## Objective

Make the `aaai_submission_decision` external-evidence execution packet point to
the validated AAAI decision-record helper, so the handoff no longer asks future
operators to infer or hand-write the final decision record.

## Changes

- Updated `scripts/check_external_evidence_packets.py` so the
  `aaai_submission_decision` packet lists
  `scripts/generate_aaai_submission_decision.py` and the current
  `results/aaai_submission_decision/decision.json` preflight as inputs.
- Reordered the packet commands into three explicit phases:
  pre-decision local gates, exactly one human-selected decision-record helper
  command, and final validation after the decision record exists.
- Added helper commands for both available options:
  `submit_now_deterministic_offline` and `wait_for_external_evidence`.
- Tightened completion criteria so `research/aaai_submission_decision.md` must
  exist and validate through `scripts/check_aaai_submission_decision.py --strict`.
- Added regression assertions in
  `tests/test_check_external_evidence_packets.py`.
- Regenerated `results/external_evidence_packets/packets.json` and
  `results/external_evidence_packets/packets.md`.
- Refreshed `results/aaai_submission_decision/decision.{json,md}`,
  `results/reproducibility/goal_completion_report.{json,md}`, and
  `results/reproducibility/package_report.{json,md}`.

## Commands Run

```powershell
python -m unittest tests.test_check_external_evidence_packets -v
python scripts\check_external_evidence_packets.py --strict
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Results

- `tests.test_check_external_evidence_packets`: 3 tests passed.
- `scripts/check_external_evidence_packets.py --strict`: passed and regenerated
  packet reports.
- `scripts/check_aaai_submission_decision.py --strict`: passed with
  `pending_human_decision`, 26 ready checks, 1 pending check, and 0 failed
  checks.
- `scripts/check_goal_completion.py --strict`: passed with
  `not_complete_pending_external_evidence`, 70 ready checks, 8 pending checks,
  and 0 failed checks.
- `scripts/check_reproducibility_package.py --strict`: passed with
  `ready_with_pending_external_evidence`, 283 ready checks, 8 pending checks,
  and 0 failed checks.

## Evidence Boundary

- This phase only improves the local handoff path for the final AAAI decision.
- No `research/aaai_submission_decision.md` decision record was generated.
- No AAAI submission option was selected.
- It does not complete DeepSeek, AI-Scientist-v2 smoke/full live run, human
  annotation, provider billing, or final AAAI submission readiness.
