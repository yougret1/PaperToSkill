# Section 03 Run Log

Date: 2026-07-25

## Frozen Inputs

- Terminal overlay: 1,296 unique rows, indices 1..1,296.
- Control schedule: 144 rows across four tasks and three controls.
- Raw terminal sources: 144 of 144 SHA-256 verified during extraction.
- Frozen FG3/FG4/FG5 artifacts were read only.

## Commands

```powershell
python .\extract_control_evidence.py
python .\analyze_controls.py
python .\verify_controls.py --require-source-extraction
```

## Verification

- PASS: semantic assertions for all twelve task-control states.
- PASS: analysis outputs reproduced byte for byte in a temporary directory.
- PASS: all 144 source rows re-extracted and evidence files reproduced byte for
  byte in a temporary directory.
- PASS: generated task-state table matches the prior scratch audit semantically.

## Decision

Section 03 is ready for repository backup. It supports exact control-state and
repeatability-risk claims only. Destructive controls remain `Invalid`, and a
confusion matrix is prohibited by the registered interpretation.
