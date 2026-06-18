# Phase 23 DeepSeek Follow-Up Readiness Run Log

Date: 2026-06-18

Evidence boundary: this phase hardens the follow-up process for model ablations
after another Claude/GPT-family availability check. It does not collect model
responses or complete Claude/GPT/DeepSeek ablations.

## Actions

- Re-ran the model-ablation live runner against the provided endpoint for
  `claude_opus_4_8` and `gpt_5_5_or_gpt_family`.
- Updated `scripts/run_model_ablation_prompts.py` so the DeepSeek slot is
  skipped only while its alias is the placeholder `deepseek-to-be-filled`.
- Added tests that distinguish a placeholder DeepSeek slot from a configured
  DeepSeek slot.
- Updated `examples/usage/model_ablation_usage.md` and `research/runbook.md`
  with concrete Claude/GPT runner commands, scorer commands, and DeepSeek
  follow-up steps.

## Latest Availability Result

- `/v1/models` succeeded for `https://coderxiaoc.com/v1`.
- The catalog still listed eight Claude-family model IDs, including
  `claude-opus-4-8`.
- Both Claude rows again selected `claude-opus-4-8` exactly and failed with HTTP
  `503`, `No available accounts: no available accounts`.
- The catalog still did not list `gpt-5.5` or any GPT-family fallback model, so
  GPT-family rows were skipped as unavailable.
- No response files were saved.

## DeepSeek Follow-Up Rule

- If `deepseek_followup_slot.model_alias` remains `deepseek-to-be-filled`, the
  runner skips it by default as a placeholder.
- Once the user replaces that alias with a concrete model ID and sets matching
  `auth_env` / `base_url_env`, the runner treats it like any other model slot.
- The same evaluator scores saved DeepSeek responses, making the later DeepSeek
  addition comparable to Claude/GPT-family rows.

## Claim Impact

Phase 23 supports saying that the DeepSeek follow-up path is mechanically ready
and tested. It does not support completed DeepSeek results, completed
Claude/GPT-family results, or any model-quality comparison.
