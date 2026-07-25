# Section 05 Run Log

Date: 2026-07-25

## Frozen Rules

- Six-block total gates: `B<=1`, `F>=5`, `S>=5`, margin `>=5`.
- Three-block registry gates: `B<=1`, `F>=2`, `S>=2`, margin `>=2`.
- Paired margin: `S score >= F score - 0.05`.
- Five-block omission gates: `B<=1`, `F>=4`, `S>=4`, margin `>=4`, with no
  per-registry gates after the unbalanced omission.

## Commands

```powershell
python .\analyze_sla_sensitivity.py
python .\verify_sla_sensitivity.py
```

## Verification

- PASS: exactly 24 registered task decisions from 432 primary rows.
- PASS: registered states are 2 Admit, 22 Reject, and 0 Invalid.
- PASS: one and only one of 81 total-grid rows reproduces the registered profile.
- PASS: nine registry and five margin-tolerance profiles are complete.
- PASS: all 24 tasks times six omissions produce 144 five-block rows.
- PASS: independent analysis outputs reproduce byte for byte.

## Decision

Section 05 is complete and ready for repository backup. Its sensitivity outputs
are descriptive and cannot replace the frozen six-block decisions.
