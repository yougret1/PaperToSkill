# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 39 is in progress: Toolformer live-transfer responses were collected,
scored, integrated into local gates/docs, and are being verified before commit.

Latest pushed commit before this phase: `99e4434 Add model response cost proxy`.

Current uncommitted Phase 39 work includes:

- `scripts/run_live_transfer_prompts.py`
- `scripts/evaluate_live_transfer_responses.py`
- `tests/test_live_transfer_execution.py`
- `results/live_transfer_prompts/evaluation.{json,md}`
- `results/live_transfer_prompts/toolformer_v0/run_report.{json,md}`
- `results/live_transfer_prompts/toolformer_v0/responses/*.md`
- updated package/usage/goal checkers and reports
- updated runbook, artifact map, result cards, goal audit, stage log, paper
  claim docs, AAAI/Markdown drafts, README, and memory
- new run log:
  `research/run_logs/2026-06-19_phase39_toolformer_live_transfer.md`

## Current Evidence

- Toolformer live-transfer run report:
  `results/live_transfer_prompts/toolformer_v0/run_report.md`
  reports `overall_status=complete`, 6 successes, 0 errors, 0 skipped rows,
  catalog status `success`, 14 models, and alias `claude-opus-4-8`.
- Live-transfer response evaluation:
  `results/live_transfer_prompts/evaluation.md`
  reports 24 total rows, 6 scored Toolformer rows, 18 pending rows, and 1.0
  average normalized score over scored rows.
- All six Toolformer rows score 9/9.
- Remaining live-transfer response sets are pending:
  AI Scientist-v2, Reflexion, and AIDE.
- GPT-family rows are now saved and scored for the current two-case
  model-ablation protocol: Toolformer timed out on `gpt-5.5` then succeeded
  with `gpt-5.4`, while AIDE succeeded with `gpt-5.5`.
- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- Latest generated reports after Phase 39 integration:
  - Usage examples: ready, 47 ready, 0 failed.
  - Reproducibility package: `ready_with_pending_external_evidence`, 191 ready,
    7 pending, 0 failed.
  - Active-goal completion: `not_complete_pending_external_evidence`, 44 ready,
    8 pending, 0 failed.

## Boundaries To Preserve

Do not claim:

- DeepSeek completed.
- All live cross-harness response sets completed.
- Human semantic fidelity.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence.
- Reliable arbitrary-PDF automation.
- Submission-final or accepted AAAI paper.

Supported after Phase 39 if verification passes:

- Toolformer live-transfer response set completed with Claude Opus 4.8 for both
  harness prompt styles and all three context variants.
- Live-transfer infrastructure exists: runner, saved-response evaluator,
  aggregate report, run report, tests, and docs.
- Full live-transfer goal remains pending because AI Scientist-v2, Reflexion,
  and AIDE response sets are missing.

## Verification Still Needed Before Commit

Run:

```powershell
python -m unittest discover -s tests -v
python scripts\check_paper_claims.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

Because `paper/aaai/papertoskill_aaai2027.tex` changed, rebuild the AAAI PDF
before the AAAI package gate if `check_aaai_package.py --strict` reports stale
PDF/log artifacts.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI Scientist-v2 live LLM run remains pending.
- AI Scientist-v2, Reflexion, and AIDE live-transfer response sets remain
  pending.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
