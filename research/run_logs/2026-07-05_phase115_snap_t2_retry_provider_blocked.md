# 2026-07-05 Phase 115 SNAP-T2 Executable-Candidate Retry

## Action

- Retried SNAP-T2 executable-candidate script generation from the prepared
  prompt packets after phase113 hit provider HTTP 524.
- Loaded the GPT-family base URL and API key from the local Desktop GPT API
  document into shell-only environment variables.
- Ran `scripts\run_real_reuse_snapatac2_executable_candidate_prompts.py` for
  `SNAP-T2` Summary and PaperToSkill with GPT-family `gpt-5.5`, OpenAI
  Responses, run id
  `phase115_gpt_snapatac2_executable_candidate_scripts_t2_retry`,
  `--timeout-seconds 420`, `--max-attempts 7`, `--retry-delay-seconds 8`, and
  `--max-tokens 2400`.
- Used phase-specific output paths:
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase115_t2_retry.md`
  and
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase115_t2_retry.json`.

## Result

- The SNAP-T2 Summary condition returned provider HTTP 524 after seven
  attempts.
- No SNAP-T2 Summary candidate script or response file was saved.
- The PaperToSkill condition did not produce a row in this phase because the
  paired retry was stopped after the Summary-side provider block had already
  made the diagnostic incomplete.
- No candidate scripts were executed, no SNAP-T2 score was produced, and no
  main raw rows were appended.

## Evidence Boundary

- This is provider availability metadata for a SNAP-T2 diagnostic
  script-generation retry.
- It is not model-quality evidence, not a SNAP-T2 task failure, not a
  paper-facing main-row replacement, and not PaperToSkill advantage evidence.
- Future SNAP-T2 executable-candidate evidence still requires paired
  Summary/PaperToSkill scripts generated under the same task, fixture, scorer,
  resource budget, model setting, and no-mid-run-human rule before execution.
