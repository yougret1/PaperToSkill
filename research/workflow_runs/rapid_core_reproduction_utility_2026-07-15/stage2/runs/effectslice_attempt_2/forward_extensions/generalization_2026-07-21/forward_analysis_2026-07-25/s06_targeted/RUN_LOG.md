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

Frozen registration was constructed, verified, committed as `3ceb3e2f`, and
privately pushed before any provider call.

## Pre-Call Verification

- PASS: four registered cases and eight unique execution rows.
- PASS: both source requests in every pair are byte-identical.
- PASS: all four request, payload, candidate, fixture, and scorer bindings match.
- PASS: source outcomes are discordant within every selected pair.
- PASS: the official DeepSeek endpoint and five-attempt transport policy load.
- PASS: no API seed is present, matching the source requests.
- PASS: no provider call has been made by this successor.

## Execution

```powershell
python -B run_targeted_successor.py --docs-dir <local-api-document-directory>
python -B verify_run_artifacts.py
python -B analyze_targeted_successor.py
python -B verify_targeted_results.py
```

- PASS: 8/8 registered rows reached terminal outcomes.
- PASS: all eight completed on their first transport attempt.
- PASS: 3 operational successes and 5 hard-contract failures.
- PASS: no other terminal outcome and no incomplete dispatch.
- PASS: every raw response, canonical output, private-scoring artifact, and
  dispatch-terminal row is present and hash-bound.
- PASS: analysis independently reproduces byte for byte.

## Result

Two cases agree across both repeats. `NLP-LLM-01/B4` changes from failure to
success, while `SE-PE-01/A3` remains failed but changes hard-contract vector.
The successor therefore confirms a targeted semantic repeatability limitation;
it does not repair or replace the frozen controls.
