# Section 04 Run Log

Date: 2026-07-25

## Commands

```powershell
python .\extract_failure_evidence.py
python .\analyze_failure_decomposition.py
python .\verify_failure_decomposition.py --require-source-extraction
```

## Verification

- PASS: 1,296 of 1,296 terminal result sources passed SHA-256 and endpoint checks.
- PASS: scorer-vector counts are 383 `[true,true]`, 759 `[true,false]`, and 154
  `[false,false]`.
- PASS: all analysis outputs reproduced byte for byte in a temporary directory.
- PASS: all source evidence reproduced byte for byte in a separate temporary
  extraction.
- PASS: the 1,296-row classification is semantically identical to the prior
  scratch analysis.

## Decision

Section 04 is locally complete and ready for its own commit and private push.
The checklist must be marked only after that backup succeeds.
