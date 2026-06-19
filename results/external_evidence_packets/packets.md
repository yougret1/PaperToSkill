# External Evidence Execution Packets

Evidence boundary: these packets define how to finish pending external evidence. They do not collect DeepSeek responses, human annotations, provider bills, AI-Scientist-v2 live-run artifacts, or final submission approval by themselves.

- Overall status: ready
- Closure status: pending_external_evidence
- Ready checks: 7
- Pending checks: 0
- Failed checks: 0

## ai_scientist_v2_smoke_completion

- Status: pending_provider
- Owner: Execution/Ops
- Goal requirements: ai_scientist_v2_live_llm_smoke_complete
- Source evidence: results/ai_scientist_v2_smoke/run_report.json
- Current detail: overall=blocked_by_provider_or_model_availability; counts={'ready': 5, 'pending': 2, 'fail': 0}; attempted=claude-opus-4-8,claude-opus-4.8,claude-opus-4-7,claude-opus-4-6

### Inputs

- scripts/run_ai_scientist_v2_smoke.py
- results/ai_scientist_v2_smoke/run_report.json
- D:\a_work\gitee\ai-scientist-v2

### Setup

- Set AI_SCIENTIST_OPENAI_BASE_URL locally.
- Set AI_SCIENTIST_OPENAI_API_KEY locally.
- Set AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE=1 locally.

### Commands

```powershell
python scripts\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 30 `
  --model-alias claude-opus-4-8 `
  --model-alias claude-opus-4.8 `
  --model-alias claude-opus-4-7 `
  --model-alias claude-opus-4-6
python scripts\check_goal_completion.py --strict
```

### Completion Criteria

- results/ai_scientist_v2_smoke/run_report.json reports overall_status=complete.
- results/ai_scientist_v2_smoke/response.md exists and satisfies all smoke marker checks.
- No provider/model availability timeout or exhausted-account status remains in the smoke report.

### Escalation

Escalate if every configured alias still times out or returns provider/account exhaustion.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

## ai_scientist_v2_full_live_run

- Status: blocked_by_smoke
- Owner: Execution/Ops
- Goal requirements: ai_scientist_v2_live_llm_run_complete
- Source evidence: results/ai_scientist_v2_live_run_handoff/handoff.json
- Current detail: handoff=blocked_by_provider_smoke; completion_dirs=0

### Inputs

- results/ai_scientist_v2_live_run_handoff/handoff.json
- ai_scientist_inputs/papertoskill_seed_ideas.json
- D:\a_work\gitee\ai-scientist-v2\launch_scientist_bfts.py

### Setup

- Complete the AI-Scientist-v2 smoke packet first.
- Use an isolated environment for ai-scientist-v2 dependencies before a long run.
- Keep writeup/review disabled for the bounded task unless the user changes scope.

### Commands

```powershell
cd D:\a_work\gitee\ai-scientist-v2
$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'
$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'
$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'
python launch_scientist_bfts.py `
  --load_ideas D:\a_work\gitee\PaperToSkill\ai_scientist_inputs\papertoskill_seed_ideas.json `
  --idea_idx 0 `
  --skip_writeup `
  --skip_review
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_goal_completion.py --strict
```

### Completion Criteria

- The bounded full AI-Scientist-v2 run produces a completion directory under ai-scientist-v2/experiments.
- results/ai_scientist_v2_live_run_handoff/handoff.json reports overall_status=complete after rerun.
- Run logs record the command, environment profile, output directory, and failure or success state.

### Escalation

Do not start the full run while the smoke report is provider-blocked.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

## deepseek_followup_responses

- Status: pending_user_configuration
- Owner: Execution/Ops
- Goal requirements: deepseek_followup_response_complete, model_ablation_evaluation_complete
- Source evidence: results/deepseek_followup_handoff/handoff.json; results/model_ablation_prompts/v0/evaluation.json
- Current detail: handoff=pending_user_configuration; scored_rows=4; pending_rows=2

### Inputs

- benchmarks/model_ablation_v0.json
- results/deepseek_followup_handoff/handoff.json
- results/model_ablation_prompts/v0/index.json

### Setup

- Replace the deepseek-to-be-filled alias with a real DeepSeek model alias.
- Set concrete DeepSeek base-url and API-key environment variable names locally.
- Rebuild prompt packets before running the DeepSeek slot.

### Commands

```powershell
python scripts\build_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --output-dir results\model_ablation_prompts\v0
python scripts\run_model_ablation_prompts.py `
  --task benchmarks\model_ablation_v0.json `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\deepseek_run_report.json `
  --output-md results\model_ablation_prompts\v0\deepseek_run_report.md `
  --model-id deepseek_followup_slot
python scripts\evaluate_model_ablation_responses.py `
  --index results\model_ablation_prompts\v0\index.json `
  --output-json results\model_ablation_prompts\v0\evaluation.json `
  --output-md results\model_ablation_prompts\v0\evaluation.md
python scripts\check_deepseek_followup.py --strict
python scripts\evaluate_model_ablation_responses.py --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\evaluation.json --output-md results\model_ablation_prompts\v0\evaluation.md
```

### Completion Criteria

- Both DeepSeek expected_response_path files exist.
- results/deepseek_followup_handoff/handoff.json reports responses_present.
- results/model_ablation_prompts/v0/evaluation.json reports pending_rows=0 and scored_rows=6.

### Escalation

Escalate if the user has not supplied a concrete DeepSeek endpoint and model alias.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

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

## provider_billing_success_per_dollar

- Status: pending_billing_rows
- Owner: Execution/Ops
- Goal requirements: provider_billing_evidence_complete
- Source evidence: results/provider_billing_evidence/billing_summary.json
- Current detail: status=pending; measured_rows=0; pending_rows=6; errors=0

### Inputs

- benchmarks/provider_billing_evidence_v0.json
- results/provider_billing_evidence/billing_template.csv
- results/provider_billing_evidence/billing_summary.json

### Setup

- Export real provider usage or invoice rows for every measured model/provider row.
- Fill billing_template.csv without adding raw API keys or secrets.
- Keep local token proxies separate from realized provider bills.

### Commands

```powershell
python scripts\summarize_provider_billing_evidence.py --strict
python scripts\check_goal_completion.py --strict
```

### Completion Criteria

- results/provider_billing_evidence/billing_summary.json reports billing_status=complete.
- All 6 billing rows are measured and validation errors are empty.
- Success-per-dollar can be computed from real billed USD rather than local token proxies.

### Escalation

Escalate if the provider cannot export usage, invoices, or per-run billing rows.

### Boundary

Execution packet only. This packet does not complete external evidence until its completion criteria are satisfied by fresh artifacts.

## aaai_submission_decision

- Status: pending_decision
- Owner: Research Lead
- Goal requirements: aaai_final_submission_ready
- Source evidence: results/reproducibility/aaai_package_report.json; results/reproducibility/submission_review_report.json; research/submission_checklist.md
- Current detail: aaai_package=ready; submission_review=ready

### Inputs

- paper/aaai/papertoskill_aaai2027.tex
- results/reproducibility/aaai_package_report.json
- results/reproducibility/submission_review_report.json
- research/submission_checklist.md

### Setup

- Choose whether to submit as a deterministic/offline system paper or wait for external evidence.
- If waiting, do not mark final submission ready until the chosen evidence rows are complete.
- If submitting a bounded paper, explicitly scope claims to validated local evidence.

### Commands

```powershell
python scripts\check_submission_review.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_claims.py --strict
```

### Completion Criteria

- The research lead records the submission decision and claim boundary.
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
| external_evidence_packets_match_closure | ready | packets=6; closure_items=6 | results/external_evidence_closure/closure.json |
| external_evidence_packets_have_details | ready | all packets have detail templates | scripts/check_external_evidence_packets.py |
| external_evidence_packets_commands_declared | ready | commands and validation commands declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_completion_criteria_declared | ready | completion criteria declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_boundaries_declared | ready | evidence boundaries declared | results/external_evidence_packets/packets.json |
| external_evidence_packets_no_secret_material | ready | no raw API-key-like strings found | results/external_evidence_packets/packets.json |
