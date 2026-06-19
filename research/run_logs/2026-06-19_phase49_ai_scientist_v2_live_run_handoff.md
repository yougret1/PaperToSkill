# Phase 49: AI-Scientist-v2 Live Run Handoff

## Objective

Make the pending full AI-Scientist-v2 live/BFTS run reproducible and
machine-checkable without claiming that the run has completed.

## Actions

- Added `scripts/check_ai_scientist_v2_live_run_handoff.py`, a no-network
  handoff/preflight report generator for the full live-run path.
- Generated `results/ai_scientist_v2_live_run_handoff/handoff.json` and `.md`.
- Integrated the handoff into the active-goal and reproducibility package
  gates.
- Updated the runbook and evidence summaries so the full live run is tracked by
  a report rather than only by memory text.

## Results

- Current handoff status is `blocked_by_provider_smoke`.
- The report has 10 ready checks, 2 pending checks, and 0 failed checks.
- Ready checks cover the AI-Scientist-v2 root, launcher, dry-run/skip flags,
  laptop-profile config, PaperToSkill seed idea, prior dry-run artifacts,
  environment variable names, and the next full-run command.
- Pending checks cover the provider-blocked smoke and missing full-run
  completion artifacts.
- No BFTS run was started, no LLM call was made by this checker, and no full
  live-run completion artifact was created.

## Evidence Boundary

This phase improves local full-live-run readiness only. It does not complete
the AI-Scientist-v2 LLM-client smoke, does not run BFTS, does not prove live
research-task success, does not resolve DeepSeek, does not collect human
annotations, does not collect provider billing, and does not make the AAAI
package submission-final.
