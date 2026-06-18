# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

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

Phase 36 Claude-ablation evidence work is in progress. On resume, check `git status` and
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
- documentation/report updates through Phase 34
- memory compaction in this file and `memory/long_term_memory.md`
- AAAI PDF/log rebuilt after TeX edits so `check_aaai_package.py --strict`
  reports ready again
- Phase 34 added `scripts/papertoskill_pipeline.py`, a one-command local
  extracted-text-to-note-to-skill-to-evaluation pipeline, plus a usage-gate
  temporary AIDE pipeline example.
- Phase 35 extends the pipeline to accept a local PDF source when
  `pdftotext -layout` is available, writes extracted text under the output
  directory, and records PDF source metadata in the manifest.
- Phase 36 reran Claude/GPT-family model ablations. Claude Opus 4.8 has two
  saved response files scored 6/6. Phase 37 reran GPT-family only; both
  GPT-family rows are now saved and scored 6/6.

Current generated report status:

- AAAI package:
  ready, 17 ready, 0 failed.
- Goal-completion report:
  `not_complete_pending_external_evidence`, 37 ready, 8 pending, 0 failed.
- Reproducibility package:
  `ready_with_pending_external_evidence`, 174 ready, 7 pending, 0 failed.
- Usage examples:
  ready, 42 ready, 0 failed.
- Paper claims and tables:
  ready, 20/76 ready respectively, 0 failed.

Latest verification before commit:

- `python -m unittest discover -s tests -v`: 47 tests passed after Phase 36.
- `python scripts\check_aaai_package.py --strict`: passed.
- `python scripts\check_goal_completion.py --strict`: passed.
- `python scripts\check_reproducibility_package.py --strict`: passed.
- `python scripts\check_paper_claims.py --strict`: passed.
- `python scripts\check_paper_tables.py --strict`: passed.
- `python scripts\check_usage_examples.py --strict`: passed.
- `python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md`: passed with 4 scored Claude/GPT-family rows and 2 pending DeepSeek rows.
- `git diff --check`: passed with only Windows LF/CRLF warnings.
- `rg -n "sk-[A-Za-z0-9]{20,}" .`: no matches.

Stable evidence retained from earlier phases:

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.

## Current Blockers

- DeepSeek model ablations are not complete until response files are saved and
  scored.
- Claude Opus 4.8 now has saved and scored responses for both current
  model-ablation prompt rows.
- Latest local live attempt with separate Claude/GPT credentials:
  - Claude catalog via `AI_SCIENTIST_OPENAI_API_KEY` listed 14 Claude-family
    models, including `claude-opus-4-8`, `claude-opus-4-7`, and
    `claude-opus-4-6`; `claude-opus-4-8` completed both current prompt rows
    with HTTP 200 and both rows score 6/6.
  - Phase 36 GPT catalog via `PAPERTOSKILL_GPT_OPENAI_API_KEY` listed 17
    models, including `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, and GPT 5.2/5.3
    variants, but both prompt rows failed HTTP 502 at that time.
  - Phase 37 GPT-family retry succeeded: Toolformer timed out on `gpt-5.5`
    then succeeded with `gpt-5.4`; AIDE succeeded with `gpt-5.5`; both rows are
    saved and scored 6/6.
  - Response evaluation is now 6 total rows, 4 scored rows, and 2 pending rows.
- Human-fidelity annotation remains pending.
- Provider billing, output-token accounting, live invoices, and
  success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending until evidence decisions are
  made.

## Next Actions

1. Check whether Phase 36 is already committed/pushed; if not, commit and
   push the verified changes.
2. After the user supplies a concrete DeepSeek alias/env profile, follow the
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
