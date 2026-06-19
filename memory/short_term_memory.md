# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-06-19.

## Current Phase

Phase 44 is complete and pushed to `origin/main` as
`1f7ceeb Add submission review handoff gate`: refreshed submission-review
handoff artifacts and added a checker so review/rebuttal/submission-checklist
files cannot drift behind the current evidence state.

Latest pushed commit after Phase 44: `1f7ceeb Add submission review handoff gate`.

Phase 44 added:

- Updated `research/review_report.md` and `research/rebuttal_bank.md` to remove
  stale Phase 17 live-transfer pending/HTTP 503 wording.
- Added `research/submission_checklist.md`.
- Added `scripts/check_submission_review.py`.
- Added `tests/test_check_submission_review.py`.
- Generated `results/reproducibility/submission_review_report.{json,md}`.
- Wired submission-review handoff into package and goal gates while keeping
  `aaai_final_submission_ready` pending.

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
- Human-fidelity annotation handoff:
  `results/human_fidelity_packets/annotation_guide.md` is present, the template
  has 24 blank rows, and `annotation_summary.md` reports
  `annotation_status=pending`, 0 scored rows, 24 pending rows, average
  confidence `n/a`, and 0 validation errors.
- Provider-billing evidence handoff:
  `results/provider_billing_evidence/billing_summary.md` reports
  `billing_status=pending`, 6 total rows, 0 measured rows, 6 pending rows, 0
  errors, total billed USD 0, and success per dollar `n/a`.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md` reports
  `overall_status=ready`, 15 ready checks, and 0 failed checks.
- Goal report now shows `not_complete_pending_external_evidence`, 53 ready
  checks, 8 pending checks, and 0 failed checks before Phase 44 regeneration;
  current Phase 44 regenerated report shows 55 ready checks, 8 pending checks,
  and 0 failed checks.
- Package report now shows `ready_with_pending_external_evidence`, 221 ready
  checks, 7 pending checks, and 0 failed checks before Phase 44 regeneration;
  current Phase 44 regenerated report shows 227 ready checks, 7 pending checks,
  and 0 failed checks.

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

Supported after Phase 43:

- AI-Scientist-v2 LLM-client smoke was attempted and provider-blocked with a
  redacted, reproducible report.
- Human-fidelity annotation handoff is ready and strictly validated, but blank
  rows remain pending.
- Provider-billing evidence handoff is ready and strictly validated, but all
  six billing rows remain pending.
- Submission-review handoff is ready and checks that review/rebuttal/checklist
  files match current evidence, but final AAAI submission remains pending.
- Package and goal gates separate provider/model availability pending evidence
  from local failures.
- All Phase 40 live-transfer saved-response evidence remains complete.

## Latest Verification

Phase 43 passed:

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

`git diff --check` reported only Windows LF-to-CRLF warnings, and `rg` exited
1 because no raw API-key-like strings were found.

Phase 44 full verification passed:

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

Full unittest count is 58 tests. `git diff --check` reported only Windows
LF-to-CRLF warnings, and `rg` exited 1 because no raw API-key-like strings were
found.

## Persistent Blockers

- DeepSeek follow-up remains pending user-provided alias/env profile.
- AI-Scientist-v2 LLM-client smoke remains provider-blocked until the endpoint
  can return a chat completion.
- AI-Scientist-v2 full live LLM/BFTS run remains pending and separate from
  dry-run, smoke, and live-transfer saved responses.
- Human-fidelity annotation remains pending.
- Provider billing and success-per-dollar evidence remain pending.
- Final AAAI submission readiness remains pending.
