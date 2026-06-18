# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 40 is in progress: AI Scientist-v2, Reflexion, and AIDE live-transfer
saved responses were collected, all four paper packets were rescored, and the
project is being integrated/verified before commit.

Latest pushed commit before this phase: `6a52e66 Add Toolformer live transfer
responses`.

Current uncommitted Phase 40 work includes:

- new saved responses and run reports under:
  - `results/live_transfer_prompts/ai_scientist_v2_v0/`
  - `results/live_transfer_prompts/reflexion_v0/`
  - `results/live_transfer_prompts/aide_v0/`
- updated aggregate live-transfer evaluation:
  `results/live_transfer_prompts/evaluation.{json,md}`
- updated package and goal reports:
  `results/reproducibility/package_report.{json,md}` and
  `results/reproducibility/goal_completion_report.{json,md}`
- updated gates/tests:
  `scripts/check_reproducibility_package.py`,
  `scripts/check_goal_completion.py`, `scripts/check_paper_claims.py`,
  `tests/test_check_reproducibility_package.py`,
  `tests/test_check_goal_completion.py`, and
  `tests/test_check_paper_claims.py`
- updated docs/paper/memory/run logs, including:
  `research/run_logs/2026-06-19_phase40_all_live_transfer_responses.md`

## Current Evidence

- AI Scientist-v2 live-transfer run report:
  `results/live_transfer_prompts/ai_scientist_v2_v0/run_report.md`
  reports `overall_status=complete`, 6 successes, and alias
  `claude-opus-4-8` for all rows.
- Reflexion live-transfer run report:
  `results/live_transfer_prompts/reflexion_v0/run_report.md`
  reports `overall_status=complete`, 6 successes, and alias
  `claude-opus-4-8` for all rows.
- AIDE live-transfer run report:
  `results/live_transfer_prompts/aide_v0/run_report.md`
  reports `overall_status=complete`, 6 successes, and one provider fallback:
  `claude-opus-4-8` remote connection closure followed by
  `claude-opus-4-7` success on the first row.
- Toolformer live-transfer run report from Phase 39 remains complete:
  6 successes with `claude-opus-4-8`.
- Aggregate live-transfer response evaluation:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows,
  24 scored rows, 0 pending rows, and average normalized score 1.0.
  AI Scientist-v2, Reflexion, and AIDE rows score 11/11; Toolformer rows
  score 9/9.
- gpt-family rows are now saved and scored for the current two-case
  model-ablation
  protocol: Toolformer timed out on `gpt-5.5` then succeeded with `gpt-5.4`,
  while AIDE succeeded with `gpt-5.5`.
- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.

## Boundaries To Preserve

Do not claim:

- DeepSeek completed.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.

Supported after Phase 40 if verification passes:

- All four live-transfer saved-response sets are complete for the current
  prompt-packet protocol and deterministically scored.
- Claude-family live-transfer coverage spans AI Scientist-v2, Reflexion, AIDE,
  and Toolformer across Codex-style and Claude-style harness prompts and three
  context variants.
- AIDE has one provider fallback row from `claude-opus-4-8` to
  `claude-opus-4-7`; record this as provider/alias evidence, not model-quality
  failure evidence.

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
before the AAAI package gate:

```powershell
cd paper\aaai
pdflatex papertoskill_aaai2027.tex
bibtex papertoskill_aaai2027
pdflatex papertoskill_aaai2027.tex
pdflatex papertoskill_aaai2027.tex
```

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI Scientist-v2 full live LLM run remains pending; this is separate from the
  completed AI Scientist-v2 live-transfer saved-response packet.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
