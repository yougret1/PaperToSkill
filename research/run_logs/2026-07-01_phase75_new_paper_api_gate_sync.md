# Phase 75: New-Paper/API Gate Sync

Date: 2026-07-01

## Decision

The newly added papers have been triaged against PaperToSkill:

- Paper2Agent remains the closest competing/adjacent system and is already
  cited in the AAAI draft with a bounded artifact/workflow comparison.
- AgenticSciML remains adjacent agentic-science workflow background and is
  already cited.
- Reasoning Manifolds remains a future non-procedural stress-case candidate,
  not a current main experiment.

No new main experiment is required for these papers at this phase.

## API Recheck

Re-ran the Claude direct provider probe using the documented Anthropic Messages
protocol:

```powershell
python scripts\run_openai_compatible_direct_probe.py --wire-api anthropic_messages --strict --require-complete --timeout-seconds 60 --max-tokens 128 --model-alias claude-opus-4-8 --model-alias claude-opus-4-7 --model-alias claude-opus-4-6 --base-url-env PAPERTOSKILL_CLAUDE_BASE_URL --auth-env PAPERTOSKILL_CLAUDE_API_KEY --output-json results\openai_compatible_direct_probe\claude_family\run_report.json --output-md results\openai_compatible_direct_probe\claude_family\run_report.md --response-output results\openai_compatible_direct_probe\claude_family\response.md
```

Result: provider/upstream HTTP 502 for `claude-opus-4-8`,
`claude-opus-4-7`, and `claude-opus-4-6`. This confirms the request protocol
is correct but the current direct provider path is unavailable. It does not
complete the AI-Scientist-v2 smoke or full live/BFTS run.

## Gate Sync

- Updated stale tests for the recorded AAAI decision and completed local token
  accounting.
- Updated `scripts/check_submission_review.py` so the review handoff can remain
  current across regenerated aggregate report counts.
- Refreshed goal, package, decision, closure, packet, paper-claim, and
  submission-review reports.

## Verification

- `python -m unittest discover -s tests -v`: 96 tests passed.

## Evidence Boundary

This phase does not claim human-fidelity completion, provider billing, live
task success, AI-Scientist-v2 smoke completion, or full live/BFTS completion.
