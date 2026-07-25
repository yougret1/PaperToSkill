# Section 06 Run Log

Date: 2026-07-25

## Frozen Design

- Scope: four same-protocol, byte-identical identity-control discordances.
- Repeats: two independent calls per case, eight calls total.
- Model: `deepseek-v4-flash`, temperature `0`, top-p `1.0`.
- API seed: absent, matching the source requests.
- Excluded: cross-protocol discordances and completed row 1156.
- Interpretation: supplementary repeatability evidence only.

## Status

Frozen registration constructed and verified before any provider call.

## Pre-Call Verification

- PASS: four registered cases and eight unique execution rows.
- PASS: both source requests in every pair are byte-identical.
- PASS: all four request, payload, candidate, fixture, and scorer bindings match.
- PASS: source outcomes are discordant within every selected pair.
- PASS: the official DeepSeek endpoint and five-attempt transport policy load.
- PASS: no API seed is present, matching the source requests.
- PASS: no provider call has been made by this successor.
