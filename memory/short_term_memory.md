# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 41 is in progress: add bounded AI-Scientist-v2 live LLM-client smoke
evidence without claiming full BFTS or live research-task success.

Latest pushed commit before Phase 41: `4fc9e80 Add all live transfer
responses`.

Current Phase 41 work includes:

- Added `scripts/run_ai_scientist_v2_smoke.py`.
- Added `tests/test_run_ai_scientist_v2_smoke.py`.
- Updated `scripts/check_goal_completion.py` and
  `scripts/check_reproducibility_package.py` to include AI-Scientist-v2 smoke
  runner/report evidence.
- Updated `tests/test_check_goal_completion.py` and
  `tests/test_check_reproducibility_package.py` for smoke attempted/blocked
  boundaries.
- Generated `results/ai_scientist_v2_smoke/run_report.{json,md}`.
- Regenerated `results/reproducibility/goal_completion_report.{json,md}` and
  `results/reproducibility/package_report.{json,md}`.
- Added `research/run_logs/2026-06-19_phase41_ai_scientist_v2_smoke.md`.
- Updated stage log, runbook, artifact map, goal audit, result cards, README,
  and memory.

## Current Evidence

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- All four live-transfer saved-response sets are complete and scored:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24
  scored rows, 0 pending rows, and average normalized score 1.0.
- Claude Opus 4.8 and GPT-family model-ablation rows are saved and scored for
  the current two-case protocol; gpt-family rows are now saved and scored. In
  the GPT-family retry, Toolformer timed out on `gpt-5.5` then succeeded with
  `gpt-5.4`, while AIDE succeeded with `gpt-5.5`; DeepSeek remains pending.
- AI-Scientist-v2 LLM-client smoke attempt:
  `results/ai_scientist_v2_smoke/run_report.md` reports
  `overall_status=blocked_by_provider_or_model_availability`, 1 ready check, 2
  pending checks, and 0 failed checks.
- The smoke provider error was HTTP 403
  `All available accounts exhausted`; no
  `results/ai_scientist_v2_smoke/response.md` file was created.
- Goal report now shows `not_complete_pending_external_evidence`, 51 ready
  checks, 8 pending checks, and 0 failed checks.
- Package report now shows `ready_with_pending_external_evidence`, 212 ready
  checks, 6 pending checks, and 0 failed checks.

## Boundaries To Preserve

Do not claim:

- DeepSeek completed.
- AI-Scientist-v2 LLM-client smoke completed.
- AI-Scientist-v2 full live LLM run completed.
- BFTS or live research-task success completed.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.

Supported after Phase 41 if verification passes:

- AI-Scientist-v2 LLM-client smoke was attempted and provider-blocked with a
  redacted, reproducible report.
- Package and goal gates separate provider/model availability pending evidence
  from local failures.
- All Phase 40 live-transfer saved-response evidence remains complete.

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

`rg` exit code 1 means no raw API-key-like strings were found.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
