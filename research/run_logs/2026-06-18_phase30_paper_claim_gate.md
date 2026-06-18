# Phase 30 Run Log: Paper Claim Discipline Gate

## Decision Question

Can the paper-facing text be machine-checked so the AAAI manuscript and draft do
not accidentally claim unsupported live, human, model, provider-billing, or
arbitrary-PDF results?

## Actions

- Reran the Claude/GPT-family model-ablation live runner against the provided
  endpoint.
- Added `scripts/check_paper_claims.py`.
- Added `tests/test_check_paper_claims.py`.
- Generated:
  - `results/reproducibility/paper_claim_report.json`
  - `results/reproducibility/paper_claim_report.md`
- Integrated the paper-claim report into
  `scripts/check_reproducibility_package.py`.

## Endpoint Recheck

- `/v1/models` succeeded and still listed eight Claude-family model IDs,
  including `claude-opus-4-8`.
- Both Claude rows selected `claude-opus-4-8` exactly but failed with HTTP 503:
  `No available accounts: no available accounts`.
- The model catalog still did not list `gpt-5.5` or any GPT-family fallback
  model.
- No response files were saved; this remains provider/model availability
  evidence, not model-quality evidence.

## Claim Checks

The checker scans:

- `paper/aaai/papertoskill_aaai2027.tex`
- `paper/draft.md`

It intentionally does not scan `paper/claim_checklist.md`, because that file
contains unsupported wording as negative examples. The checker verifies that
unsupported positive claims are absent and that required boundary statements are
present for curated scope, arbitrary-PDF automation, live transfer, human
fidelity, cost proxy, and model-ablation availability.

## Results

- Paper-claim report status: `ready`.
- Ready checks: `20`.
- Failed checks: `0`.

## Evidence Boundary

This phase improves paper claim discipline and records another provider/model
availability recheck. It does not add new empirical model responses, live
transfer results, human annotations, or provider-billing evidence.

## Verification

- `python scripts\run_model_ablation_prompts.py --task benchmarks\model_ablation_v0.json --index results\model_ablation_prompts\v0\index.json --output-json results\model_ablation_prompts\v0\run_report.json --output-md results\model_ablation_prompts\v0\run_report.md --model-id claude_opus_4_8 --model-id gpt_5_5_or_gpt_family`
- `python scripts\check_paper_claims.py --strict`
- `python -m unittest tests.test_check_paper_claims -v`
