# External Evidence Execution Packets

Evidence boundary: these packets define how to finish pending external evidence. They do not collect human annotations, depend on provider bills, AI-Scientist-v2 live-run artifacts, or final submission approval by themselves.

- Overall status: ready
- Closure status: pending_external_evidence
- Ready checks: 7
- Pending checks: 0
- Failed checks: 0

## human_fidelity_annotation

- Status: pending_reviewers
- Owner: Human reviewers
- Goal requirements: human_fidelity_annotation_complete
- Source evidence: results/human_fidelity_packets/annotation_summary.json
- Current detail: status=pending; scored_rows=0; pending_rows=24

### Inputs

- results/human_fidelity_packets/annotation_guide.md
- results/human_fidelity_packets/annotation_template.csv
- results/human_fidelity_packets/*_human_fidelity_packet.md

### Setup

- Send the packet files and annotation guide to independent reviewers.
- Keep blank rows blank; do not convert missing review rows into zero scores.
- Collect reviewer-filled rows in the existing annotation_template.csv schema.

### Commands

```powershell
python scripts\summarize_human_fidelity_annotations.py --strict
python scripts\check_goal_completion.py --strict
```

### Completion Criteria

- results/human_fidelity_packets/annotation_summary.json reports annotation_status=complete.
- All 24 paper-by-criterion rows are scored with no validation errors.
- Reviewer notes and confidence fields are preserved for audit.

### Escalation

Escalate if independent reviewers are unavailable or scoring criteria are ambiguous.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

## aaai_submission_decision

- Status: pending_decision
- Owner: Research Lead
- Goal requirements: aaai_final_submission_ready
- Source evidence: results/reproducibility/aaai_package_report.json; results/reproducibility/submission_review_report.json; research/submission_checklist.md
- Current detail: aaai_package=ready; submission_review=ready

### Inputs

- scripts/generate_aaai_submission_decision.py
- paper/aaai/papertoskill_aaai2027.tex
- results/reproducibility/aaai_package_report.json
- results/reproducibility/submission_review_report.json
- results/aaai_submission_decision/decision.json
- research/submission_checklist.md

### Setup

- Choose whether to submit as a deterministic/offline system paper or wait for external evidence.
- Use scripts/generate_aaai_submission_decision.py after the human research lead selects an option; do not hand-write the record unless the helper is unavailable.
- If waiting, do not mark final submission ready until the chosen evidence rows are complete.
- If submitting a bounded paper, explicitly scope claims to validated local evidence.

### Commands

```powershell
# Pre-decision local gates
python scripts\check_submission_review.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_paper_tables.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_aaai_submission_decision.py --strict
# Select exactly one human decision record command
python scripts\generate_aaai_submission_decision.py --selected-option submit_now_deterministic_offline --decision-owner "<name or role>" --decision-date YYYY-MM-DD --claim-boundary "<accepted bounded claim scope>" --evidence-policy "submit with explicit pending-evidence limitations"
python scripts\generate_aaai_submission_decision.py --selected-option wait_for_external_evidence --decision-owner "<name or role>" --decision-date YYYY-MM-DD --claim-boundary "<claims deferred until named evidence is complete>" --evidence-policy "wait for named external evidence rows"
# Final validation after the selected decision record exists
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
```

### Completion Criteria

- research/aaai_submission_decision.md exists and records the research lead's selected option, claim boundary, and evidence policy.
- scripts/check_aaai_submission_decision.py --strict validates the decision record and reports no failed checks.
- AAAI package, paper-claim, paper-table, and submission-review gates pass after the decision.
- The active-goal completion report no longer has aaai_final_submission_ready pending.

### Escalation

Escalate if evidence strength is insufficient for the intended AAAI claim scope.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

## Checks

| Check | Status | Detail | Evidence |
| --- | --- | --- | --- |
| external_evidence_packets_closure_present | ready | present | results/external_evidence_closure/closure.json |
| external_evidence_packets_match_closure | ready | packets=2; closure_items=2 | results/external_evidence_closure/closure.json |
| external_evidence_packets_have_details | ready | all packets have detail templates | scripts/check_external_evidence_packets.py |
| external_evidence_packets_commands_declared | ready | commands and validation commands declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_completion_criteria_declared | ready | completion criteria declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_boundaries_declared | ready | evidence boundaries declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_no_secret_material | ready | no raw API-key-like strings found | results/external_evidence_packets/packets.json |
