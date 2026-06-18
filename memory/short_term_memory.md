# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-18.

## Current User Update

The user asked to continue the active goal, but added a new priority:

- First, reorganize memory because it has become too long.
- Memory should preserve file-change descriptions, where fixes live, and how
  important errors were solved.
- Remove old material that does not affect the current or future agent.
- Keep helpful summaries only after merging/shortening them.
- New Claude requested aliases: `claude-opus-4.8`, `claude-opus-4-6`,
  `claude-opus-4-7`.
- New GPT-family credential profile is available; user says its model list is
  requestable and includes at least `gpt-5.5` and `gpt-5.4`.

Do not commit raw keys. Use shell environment variables for live checks.

## Current Worktree State

Phase 31/32 work has been locally verified. On resume, check `git status` and
`git log -1 --oneline` to see whether the verified changes are already saved to
`origin/main`.

Implemented locally:

- `scripts/check_goal_completion.py`
- `tests/test_check_goal_completion.py`
- `results/reproducibility/goal_completion_report.json`
- `results/reproducibility/goal_completion_report.md`
- `research/run_logs/2026-06-18_phase31_goal_completion_gate.md`
- integration of goal-completion checks into
  `scripts/check_reproducibility_package.py`
- model-ablation alias/env support for separate Claude and GPT profiles
- usage-example checks for Claude aliases and GPT credential profile
- regenerated model-ablation prompt packets under
  `results/model_ablation_prompts/v0/`
- documentation/report updates for Phase 31/32
- memory compaction in this file and `memory/long_term_memory.md`
- AAAI PDF/log rebuilt after TeX edits so `check_aaai_package.py --strict`
  reports ready again

Current generated report status:

- AAAI package:
  ready, 17 ready, 0 failed.
- Goal-completion report:
  `not_complete_pending_external_evidence`, 34 ready, 10 pending, 0 failed.
- Reproducibility package:
  `ready_with_pending_external_evidence`, 164 ready, 7 pending, 0 failed.
- Usage examples:
  ready, 36 ready, 0 failed.
- Paper claims and tables:
  ready, 20/76 ready respectively, 0 failed.

Latest verification before commit:

- `python -m unittest discover -s tests -v`: 44 tests passed.
- `python scripts\check_aaai_package.py --strict`: passed.
- `python scripts\check_goal_completion.py --strict`: passed.
- `python scripts\check_reproducibility_package.py --strict`: passed.
- `python scripts\check_paper_claims.py --strict`: passed.
- `python scripts\check_paper_tables.py --strict`: passed.
- `python scripts\check_usage_examples.py --strict`: passed.
- `git diff --check`: passed with only Windows LF/CRLF warnings.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

Stable evidence retained from earlier phases:

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.

## Current Blockers

- Claude/GPT/DeepSeek model ablations are not complete until response files are
  saved and scored.
- Latest local live attempt with separate Claude/GPT credentials:
  - Claude catalog via `AI_SCIENTIST_OPENAI_API_KEY` listed 8 Claude-family
    models, including `claude-opus-4-8`, `claude-opus-4-7`, and
    `claude-opus-4-6`; both Claude prompt rows selected `claude-opus-4-8` and
    failed HTTP 503 `No available accounts: no available accounts`.
  - GPT catalog via `PAPERTOSKILL_GPT_OPENAI_API_KEY` listed 17 models,
    including `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, and GPT 5.2/5.3 variants;
    both GPT prompt rows selected `gpt-5.5` and failed HTTP 502
    `Upstream access forbidden, please contact administrator`.
  - No response files were saved; response evaluation remains 6 total rows, 0
    scored rows, and 6 pending rows.
- Human-fidelity annotation remains pending.
- Provider billing, output-token accounting, live invoices, and
  success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending until evidence decisions are
  made.

## Next Actions

1. Check whether Phase 31/32 is already committed/pushed; if not, commit and
   push the verified changes.
2. If Claude/GPT chat completions later work, run the prepared model-ablation prompts,
   save responses, score them, and update paper/reports.
3. If live calls still fail, record the exact provider/model availability
   result in run logs and keep model-quality claims pending.
4. After the user supplies a concrete DeepSeek alias/env profile, follow the
   same catalog, live-run, saved-response, scoring, and claim-boundary process.

## Important Current Files

- Memory: `memory/long_term_memory.md`, `memory/short_term_memory.md`.
- Active goal gate: `scripts/check_goal_completion.py`,
  `results/reproducibility/goal_completion_report.md`.
- Reproducibility gate: `scripts/check_reproducibility_package.py`,
  `results/reproducibility/package_report.md`.
- Model ablation: `benchmarks/model_ablation_v0.json`,
  `scripts/run_model_ablation_prompts.py`,
  `scripts/evaluate_model_ablation_responses.py`,
  `examples/usage/model_ablation_usage.md`.
- AAAI paper: `paper/aaai/papertoskill_aaai2027.tex`,
  `paper/aaai/papertoskill_tables.tex`,
  `paper/aaai/papertoskill_refs.bib`.
- Runbook: `research/runbook.md`.
