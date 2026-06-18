# Phase 28 Usage Example Verification Gate

Date: 2026-06-18.

## Question

Can the experiment usage examples be checked as executable local protocols
without waiting for live model availability?

## Actions

- Added `scripts/check_usage_examples.py`.
- Added `tests/test_check_usage_examples.py`.
- Generated:
  - `results/reproducibility/usage_example_report.json`
  - `results/reproducibility/usage_example_report.md`
- Integrated the usage-example report into
  `scripts/check_reproducibility_package.py`.
- Updated runbook, claim/evidence docs, result cards, goal audit, stage log,
  and memory.

## Results

- Usage-example report: `overall_status=ready`.
- Ready checks: `34`.
- Failed checks: `0`.
- The checker validates:
  - usage-example Markdown files;
  - Codex-style Toolformer skill inputs and live-transfer prompt packet;
  - model-ablation task, prompt index, runner, evaluator, model slots, cases,
    prompt files, and six expected response slots;
  - an offline AIDE extracted-text-to-note-to-skill chain in a temporary
    directory.
- Offline example-chain result:
  - selected 6 method windows, 6 experiment windows, and 5 limitation windows;
  - generated a temporary `SKILL.md` and source map;
  - scored the temporary skill 20/20 on `benchmarks/rubric_aide_v0.json`.
- Reproducibility package report after integration:
  `ready_with_pending_external_evidence`, 147 ready checks, 7 pending checks,
  and 0 failed checks.

## Evidence Boundary

This phase supports local usage-example executability and prompt-slot
readiness. It does not execute live Claude/GPT/DeepSeek calls, does not score
model responses, does not prove live cross-harness success, and does not prove
human usability.

## Commands

```powershell
python scripts\check_usage_examples.py `
  --output-json results\reproducibility\usage_example_report.json `
  --output-md results\reproducibility\usage_example_report.md `
  --strict

python scripts\check_reproducibility_package.py `
  --output-json results\reproducibility\package_report.json `
  --output-md results\reproducibility\package_report.md `
  --strict

python -m unittest tests.test_check_usage_examples -v
```
