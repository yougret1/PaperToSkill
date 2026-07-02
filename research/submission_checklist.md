# PaperToSkill Submission Checklist

Date: 2026-07-02

Evidence boundary: this checklist prepares an AAAI submission-review handoff. It
does not declare the paper submission-final, accepted, human-validated, or
complete with respect to pending external evidence.

## Current Local Gate Status

| Gate | Current Status | Evidence | Submission Meaning |
| --- | --- | --- | --- |
| AAAI local package | Ready | `results/reproducibility/aaai_package_report.md` | Local TeX/PDF package is internally consistent; not final submission approval. |
| Paper claims | Ready | `results/reproducibility/paper_claim_report.md` | Unsupported overclaim patterns are absent from paper-facing text. |
| Paper tables | Ready | `results/reproducibility/paper_table_report.md` | AAAI tables match generated CSV result tables. |
| Usage examples | Ready | `results/reproducibility/usage_example_report.md`: 55 ready, 0 failed | Local example files, DeepSeek handoff, and offline example chain are synchronized. |
| Reproducibility package | Ready with pending external evidence | `results/reproducibility/package_report.md`: 305 ready, 1 pending, 0 failed | Local package is coherent; external evidence remains pending. |
| Active goal completion | Not complete | `results/reproducibility/goal_completion_report.md`: 77 ready, 3 pending, 0 failed | The overall user goal remains open. |
| External evidence closure queue | Ready as local queue | `results/external_evidence_closure/closure.md`: 3 ready, 0 pending, 0 failed | Pending evidence is mapped to next actions; evidence itself remains pending. |
| External evidence execution packets | Ready as local handoff | `results/external_evidence_packets/packets.md`: 7 ready, 0 pending, 0 failed | Pending evidence has runnable handoff packets; evidence itself remains pending. |
| AAAI submission decision | Recorded wait decision | `results/aaai_submission_decision/decision.md`: `selected_option=wait_for_external_evidence`, 27 ready, 0 pending, 0 failed | The current decision is to wait for named external evidence before stronger claims. |

## Evidence Ready To Use

| Evidence Area | Ready Evidence | Boundary |
| --- | --- | --- |
| Curated note-to-skill benchmark | Four paper cases: AI Scientist-v2, Reflexion, AIDE, Toolformer | Deterministic/offline benchmark only. |
| Paper2Agent comparison | `results/tables/paper2agent_artifact_comparison.md`: 7/7 source-backed criteria ready | Positioning evidence only; not an executable MCP baseline. |
| Main deterministic results | `results/tables/main_results.md` | Operational coverage, not live success. |
| Transfer readiness | `results/tables/transfer_ablation.md` | Offline readiness, not live outcome proof. |
| Saved live-transfer responses | `results/live_transfer_prompts/evaluation.md`: 24 total, 24 scored, 0 pending, average normalized score 1.0 | Saved-response output-contract scoring is not human semantic fidelity or real live task success. |
| Model ablation | `results/model_ablation_prompts/v0/evaluation.md`: 6 total, 6 scored, 0 pending | Saved-response scoring is complete for the current two-case Claude/GPT-family/DeepSeek prompt protocol; this is not live downstream task success or provider economics. |
| DeepSeek handoff | `results/deepseek_followup_handoff/handoff.md`: `responses_present`, 7 ready, 0 pending, 0 failed | DeepSeek response files are saved for the current protocol; keep raw keys out of tracked files. |
| External closure queue | `results/external_evidence_closure/closure.md`: two pending-external-evidence items | Local queue only; not evidence completion. |
| External execution packets | `results/external_evidence_packets/packets.md`: two pending-external-evidence execution packets | Local handoff only; not evidence completion. |
| AI-Scientist-v2 bounded smoke/full live run | `results/ai_scientist_v2_smoke/run_report.md`: `complete`; `results/ai_scientist_v2_live_run_handoff/handoff.md`: `complete` with one completion directory | Bounded integration and synthetic sensitivity evidence only; not human fidelity, real-data validation, or broad live task success. |
| AAAI submission decision | `results/aaai_submission_decision/decision.md`: `selected_option=wait_for_external_evidence` | Recorded decision; not final submission readiness. |
| Local token accounting | `results/token_accounting/token_accounting_summary.md`: 4,322 generated-skill input tokens, 95,303 full-extracted input tokens, 9,594 saved-response output tokens | Current cost evidence; not provider bills or success-per-dollar. |
| Context cost proxy | `results/tables/context_cost_proxy_tokenizer.md` | Local `o200k_base` input-token proxy, not provider bills. |
| Model response cost proxy | `results/tables/model_response_cost_proxy.md` | Local output-token proxy over saved responses, not invoices. |
| Failure archive | `results/failure_cases/failure_case_archive.md`: 27 cases | Provenance and limitation record, not an outcome study. |

## Evidence Not Yet Ready

| Pending Item | Current Evidence | Required Before Stronger Claim |
| --- | --- | --- |
| Human fidelity | `results/human_fidelity_packets/annotation_summary.md`: 0 scored rows, 24 pending rows | Independent reviewers fill the template and strict summarizer reports complete with no errors. |
| Final AAAI submission readiness | Local package and decision record are ready, but the selected policy waits for external evidence | Complete the human-fidelity evidence and then revisit the final submission decision. |

## Pre-Submission Commands

Run these before any final package decision:

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_external_evidence_packets.py --strict
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
| Submit now as deterministic/offline system paper | Human accepts pending live/human/evidence limitations as explicit limitations | Keep abstract, experiments, and limitations framed around deterministic gates and handoff readiness. |
| Wait for stronger evidence | Human wants claims about semantic fidelity or live success | Complete human annotations and any separate downstream live-task evaluation first. |

Current selected option: `wait_for_external_evidence`.

## Non-Negotiable Claim Boundaries

- Do not claim robust arbitrary-PDF automation.
- Do not claim live task success from saved-response output-contract scoring.
- Do not claim human validation while there are 0 scored and 24 pending
  annotation rows.
- Do not claim provider billing, invoices, or success per dollar while the
  project uses local token accounting instead.
- Do not claim saved-response model-ablation scoring proves live task success,
  broad model quality, provider bills, or success per dollar.
- Do not claim the bounded AI-Scientist-v2 smoke/full live run proves human
  fidelity, real-data validation, or broad live task success.
- Do not claim the AAAI paper is submission-final while the recorded
  `wait_for_external_evidence` policy still has pending named evidence.
