# Phase 90: SWE-agent Real-Reuse Skill Gate

Date: 2026-07-03

## Objective

Prepare the SWE-agent source-paper skill layer for the main real-reuse
benchmark while preserving the evidence boundary between skill readiness and
downstream task execution.

## Actions

- Added a `swe_agent` profile to `scripts/papertoskill_note_from_text.py` so
  the deterministic extracted-text-to-note scaffold can target SWE-agent's
  agent-computer-interface method, SWE-bench evaluation setup, ablations, and
  limitations.
- Generated `papers/auto_notes/swe_agent_auto_note.md` from
  `papers/extracted/swe_agent.txt`.
- Generated the real-reuse SWE-agent skill at
  `generated_skills/real_reuse/swe_agent/SKILL.md` with source map
  `generated_skills/real_reuse/swe_agent/references/source_map.json`.
- Added `benchmarks/rubric_swe_agent_v0.json` and
  `benchmarks/tasks/swe_agent_auto_source_span_validation.json`.
- Ran the deterministic rubric and source-span validation for the SWE-agent
  skill.
- Updated the real-reuse table builder so pending rows report task-specific
  readiness states rather than a generic `Ready to run`.
- Extended the real-reuse and reproducibility gates to track the SWE-agent
  skill/readiness artifacts.

## Results

- SWE-agent rubric score: 20/20.
- SWE-agent generated skill compactness: 1186 words under the 1200-word budget.
- SWE-agent source-span validation: 20/20 supported claims,
  `support_rate=1.0`, `invalid_ranges=0`.
- `results/real_reuse/main_results_plan.{csv,md,json}` now reports:
  - AIDE-T1/T2: `Awaiting dataset`
  - SWE-T1/T2: `Runner pending`
  - REF-T1/T2: `Scored (GPT-family)`
  - SNAP-T1/T2: `Skill pending`
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 430
  ready checks, and 0 failed checks after adding the SWE-agent skill gate.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 377 ready checks, 1 pending check,
  and 0 failed checks.
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf` after the real-reuse table
  status update so the AAAI package freshness gate passes.
- Verification passed before phase save:
  - `python -m unittest discover -s tests -v`: 133 tests passed.
  - All strict local gates passed: submission review, AAAI decision, DeepSeek
    follow-up, usage examples, external-evidence closure/packets,
    AI-Scientist-v2 live-run handoff, goal completion, reproducibility package,
    paper claims, AAAI package, paper tables, and real-reuse benchmark.
  - `git diff --check`: no whitespace errors; only Windows line-ending
    warnings.
  - Raw-key scan: no matches.

## Evidence Boundary

This phase is SWE-agent skill/readiness evidence only. It does not prepare
SWE-bench assets, implement the SWE real-reuse runner/scorer, run Summary or
PaperToSkill on SWE-T1/T2, append SWE raw rows, or update paper score cells
with SWE task outcomes.

AIDE remains blocked on the human-provided real Kaggle Spaceship Titanic
`train.csv`; `C:\Users\19351\Desktop\tem\ok.txt` and the expected
`real_reuse_assets\spaceship-titanic\train.csv` were absent during this phase.

## Next Action

Implement the SWE-agent execution layer:

- `scripts/prepare_real_reuse_swe_fixture.py`
- `scripts/score_real_reuse_swe.py`
- `scripts/run_real_reuse_swe.py`
- focused tests and gate integration
