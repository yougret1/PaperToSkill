# Phase 61: Direct-Probe-First Smoke Packet

Date: 2026-06-20

## Objective

Make the AI-Scientist-v2 smoke-completion execution packet use the Phase 59/60
direct OpenAI-compatible provider diagnostic as a preflight before running the
`ai_scientist.llm` wrapper smoke. This improves the handoff while keeping the
provider-blocked evidence boundary intact.

## Changes

- Updated `scripts/check_external_evidence_packets.py` so the
  `ai_scientist_v2_smoke_completion` packet lists the direct-probe runner and
  Claude/GPT-family direct-probe reports as inputs.
- Added direct-probe commands before wrapper-smoke commands in the generated
  smoke-completion packet.
- Added completion criteria requiring at least one direct probe to return a
  saved marker-contract response before the wrapper smoke can be considered
  resolved.
- Expanded the packet secret scan to include the closure report content, not
  only the generated packet text.
- Added regression assertions in `tests/test_check_external_evidence_packets.py`
  to preserve direct-probe-first ordering and alias coverage.
- Refreshed `results/external_evidence_packets/packets.{json,md}` and related
  aggregate reports.

## Commands

```powershell
python -m unittest tests.test_check_external_evidence_packets -v
python scripts\check_external_evidence_packets.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_submission_review.py --strict
```

## Result

- The smoke-completion packet now instructs future operators to run direct
  Claude-family and GPT-family endpoint probes before attempting the
  AI-Scientist-v2 wrapper smoke.
- If direct probes still report provider/account blockers, the packet now says
  to keep wrapper smoke pending and escalate provider availability rather than
  treating the wrapper as failed.
- This phase changes handoff quality only. It does not run new provider calls
  or complete any external evidence.

## Evidence Boundary

This phase does not complete the AI-Scientist-v2 LLM-client smoke contract, run
BFTS, prove live research-task success, resolve DeepSeek, collect human
annotations, collect provider billing, or make the AAAI package
submission-final.
