# Phase 62: DeepSeek Configuration Helper

Date: 2026-06-20

## Objective

Make the pending DeepSeek follow-up easier and safer for the user to run later
by adding a helper that configures only non-secret model-slot metadata.

## Changes

- Added `scripts/configure_deepseek_followup.py`.
- The helper updates `deepseek_followup_slot` in
  `benchmarks/model_ablation_v0.json` with a concrete model alias, auth env
  name, base-url env name, and non-secret provider status.
- The helper rejects raw API-key-like strings and requires uppercase
  environment variable names for credential locations.
- Added `tests/test_configure_deepseek_followup.py`.
- Updated `scripts/check_deepseek_followup.py` so the handoff report lists the
  configuration helper before prompt building, running, scoring, and rechecking.
- Updated `scripts/check_external_evidence_packets.py`,
  `examples/usage/model_ablation_usage.md`, `research/runbook.md`, and the
  reproducibility/usage gates to reference the helper.

## Commands

```powershell
python -m unittest tests.test_configure_deepseek_followup tests.test_check_deepseek_followup tests.test_check_external_evidence_packets tests.test_check_usage_examples tests.test_check_reproducibility_package -v
python scripts\check_deepseek_followup.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_reproducibility_package.py --strict
```

## Result

- `results/deepseek_followup_handoff/handoff.md` now includes
  `scripts/configure_deepseek_followup.py` in its next commands.
- `results/external_evidence_packets/packets.md` now tells future operators to
  configure DeepSeek through the helper instead of manually editing the
  benchmark.
- Usage and reproducibility gates check that the helper exists and is wired into
  the DeepSeek handoff path.
- The DeepSeek slot remains `pending_user_configuration` until the user supplies
  a concrete DeepSeek alias and local environment variables.

## Evidence Boundary

This phase prepares DeepSeek configuration only. It does not call DeepSeek,
save DeepSeek responses, complete model ablations, collect provider billing, or
make the AAAI package submission-final.
