# Research Workflow Runs

This directory is the canonical progress root for ResearchStudio Full Research
Workflow runs in this repository.

## Runs

- `legacy_papertoskill_v1/` records the pre-workflow PaperToSkill research run.
  Its raw artifacts remain at their original paths until hard-coded consumers
  are migrated and verified.
- `paper_specific_epistemic_grounding_2026-07-14/` is the active run for the
  evidence-grounded extraction, verification, and adaptation direction.

## Rules

- Number stages with the stable workflow IDs `1`, `2`, and `3` and their
  sub-stage IDs.
- Save a `stage_report_*.json` for every attempted, blocked, failed, skipped,
  or passed stage.
- Preserve raw experiment artifacts. Derived artifacts belong under the stage
  that produced them.
- Do not append new work to `research/run_logs/`; it is a legacy compatibility
  path for the v1 run.
- `memory/` summarizes current state. It is not a substitute for stage reports.

