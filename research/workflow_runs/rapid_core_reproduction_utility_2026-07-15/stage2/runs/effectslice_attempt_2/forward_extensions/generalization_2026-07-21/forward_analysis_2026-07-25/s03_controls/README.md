# Section 03: Registered Controls Audit

This section audits the 144 registered control rows without changing FG3, FG4,
FG5, or the 1,296-row terminal overlay.

## Reproduce

```powershell
python .\extract_control_evidence.py
python .\analyze_controls.py
python .\verify_controls.py --require-source-extraction
```

`extract_control_evidence.py` re-reads the frozen schedule, overlay, task
manifests, scorer implementations, and all 144 terminal row sources. It writes a
portable evidence snapshot under `inputs/`. `analyze_controls.py` applies the
registered gates. `verify_controls.py` performs semantic assertions and an
independent byte-for-byte rerun; the optional extraction flag additionally
requires the original terminal row sources to remain available.

The committed evidence snapshot is sufficient for future analysis reruns even
if temporary successor-source directories are later removed.

## Claim Boundary

- Control outcomes are `SanityPass`, `SanityFail`, or `Invalid`, never admission
  labels.
- The planted-positive arms are byte-identical full artifacts. They are an
  identity-like no-harm check, not a nonidentical redundancy intervention.
- The destructive target cannot be mapped to the aggregate two-element scorer
  vector. Its four registered task states are therefore `Invalid`.
- No confusion matrix, false-admit rate, or false-reject rate is estimable from
  these controls.
