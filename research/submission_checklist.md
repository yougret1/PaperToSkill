# PaperToSkill Submission Checklist

Date: 2026-06-19

Evidence boundary: this checklist prepares an AAAI submission-review handoff. It
does not declare the paper submission-final, accepted, human-validated, or
complete with respect to pending external evidence.

## Current Local Gate Status

| Gate | Current Status | Evidence | Submission Meaning |
| --- | --- | --- | --- |
| AAAI local package | Ready | `results/reproducibility/aaai_package_report.md` | Local TeX/PDF package is internally consistent; not final submission approval. |
| Paper claims | Ready | `results/reproducibility/paper_claim_report.md` | Unsupported overclaim patterns are absent from paper-facing text. |
| Paper tables | Ready | `results/reproducibility/paper_table_report.md` | AAAI tables match generated CSV result tables. |
| Usage examples | Ready | `results/reproducibility/usage_example_report.md`: 53 ready, 0 failed | Local example files, DeepSeek handoff, and offline example chain are synchronized. |
| Reproducibility package | Ready with pending external evidence | `results/reproducibility/package_report.md`: 243 ready, 8 pending, 0 failed | Local package is coherent; external evidence remains pending. |
| Active goal completion | Not complete | `results/reproducibility/goal_completion_report.md`: 61 ready, 8 pending, 0 failed | The overall user goal remains open. |

## Evidence Ready To Use

| Evidence Area | Ready Evidence | Boundary |
| --- | --- | --- |
| Curated note-to-skill benchmark | Four paper cases: AI Scientist-v2, Reflexion, AIDE, Toolformer | Deterministic/offline benchmark only. |
| Main deterministic results | `results/tables/main_results.md` | Operational coverage, not live success. |
| Transfer readiness | `results/tables/transfer_ablation.md` | Offline readiness, not live outcome proof. |
| Saved live-transfer responses | `results/live_transfer_prompts/evaluation.md`: 24 total, 24 scored, 0 pending, average normalized score 1.0 | Saved-response output-contract scoring is not human semantic fidelity or real live task success. |
| Model ablation | `results/model_ablation_prompts/v0/evaluation.md`: 6 total, 4 scored, 2 pending | Claude Opus 4.8 and GPT-family are scored; DeepSeek remains pending. |
| DeepSeek handoff | `results/deepseek_followup_handoff/handoff.md`: `pending_user_configuration`, 5 ready, 2 pending, 0 failed | Preflight only; no DeepSeek response has been collected. |
| Context cost proxy | `results/tables/context_cost_proxy_tokenizer.md` | Local `o200k_base` input-token proxy, not provider bills. |
| Model response cost proxy | `results/tables/model_response_cost_proxy.md` | Local output-token proxy over saved responses, not invoices. |
| Failure archive | `results/failure_cases/failure_case_archive.md`: 27 cases | Provenance and limitation record, not an outcome study. |

## Evidence Not Yet Ready

| Pending Item | Current Evidence | Required Before Stronger Claim |
| --- | --- | --- |
| AI-Scientist-v2 LLM-client smoke completion | `results/ai_scientist_v2_smoke/run_report.md`: `blocked_by_provider_or_model_availability`; attempted aliases `claude-opus-4-8`, `claude-opus-4.8`, `claude-opus-4-7`, and `claude-opus-4-6`; latest details are HTTP 403 `All available accounts exhausted` for `claude-opus-4-8` and 30-second provider timeouts for the other three aliases | Provider must return a response satisfying the smoke contract. |
| Full AI-Scientist-v2 live/BFTS run | `results/ai_scientist_v2_live_run_handoff/handoff.md`: `blocked_by_provider_smoke`, 10 ready, 2 pending, 0 failed; no full live-run completion artifact | Run and log a bounded full live task separately from smoke checks after provider smoke is resolved. |
| DeepSeek ablation | `results/model_ablation_prompts/v0/evaluation.md`: 2 pending DeepSeek rows | User supplies DeepSeek alias/env vars, then responses are saved and scored. |
| Human fidelity | `results/human_fidelity_packets/annotation_summary.md`: 0 scored rows, 24 pending rows | Independent reviewers fill the template and strict summarizer reports complete with no errors. |
| Provider billing | `results/provider_billing_evidence/billing_summary.md`: 0 measured rows, 6 pending rows | Fill usage export or invoice rows and rerun strict billing summary. |
| Success per dollar | Provider billing summary has success per dollar `n/a` | Requires measured billing rows and agreed success metric. |
| Final AAAI submission decision | Local package is ready, but goal remains pending | Human decision to submit as deterministic/offline paper or wait for external evidence. |

## Pre-Submission Commands

Run these before any final package decision:

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

If the raw-key scan exits 1 with no matches, that means no raw API-key-like
strings were found.

## Submission Decision Options

| Option | When It Is Defensible | Required Wording |
| --- | --- | --- |
| Submit now as deterministic/offline system paper | Human accepts pending live/human/billing evidence as explicit limitations | Keep abstract, experiments, and limitations framed around deterministic gates and handoff readiness. |
| Wait for stronger evidence | Human wants claims about semantic fidelity, live success, or real economics | Complete human annotations, DeepSeek, provider billing, and AI-Scientist-v2 smoke/live evidence first. |

## Non-Negotiable Claim Boundaries

- Do not claim robust arbitrary-PDF automation.
- Do not claim live task success from saved-response output-contract scoring.
- Do not claim human validation while there are 0 scored and 24 pending
  annotation rows.
- Do not claim provider billing, invoices, or success per dollar while there are
  0 measured and 6 pending billing rows.
- Do not claim DeepSeek completion while two DeepSeek rows are pending.
- Do not claim AI-Scientist-v2 LLM-client smoke completion while the latest
  smoke report is `blocked_by_provider_or_model_availability`.
- Do not claim the AAAI paper is submission-final until the human submission
  decision is made and all selected evidence gates are intentionally accepted.
