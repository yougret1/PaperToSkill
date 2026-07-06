# 2026-07-06 Phase 118 SNAP-T2 Compact Executable-Candidate Retry

## Action

- Retried SNAP-T2 executable-candidate script generation with the compact prompt
  packets prepared under
  `results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.json`.
- Loaded the GPT-family base URL and API key from the local Desktop GPT API
  document into shell-only environment variables.
- Ran GPT-family `gpt-5.5` with OpenAI Responses, run id
  `phase118_gpt_snapatac2_executable_candidate_scripts_t2_compact`,
  `--timeout-seconds 600`, `--max-attempts 6`,
  `--retry-delay-seconds 10`, and `--max-tokens 2200`.
- Used phase-specific output paths:
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase118_t2_compact.md`
  and
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase118_t2_compact.json`.

## Result

- The SNAP-T2 Summary compact condition returned provider HTTP 524 after six
  attempts.
- No SNAP-T2 Summary candidate script or response file was saved.
- Because the Summary-side script was unavailable, the paired executable
  diagnostic could not proceed. The remaining PaperToSkill-side call was
  stopped after the Summary-side provider block; no PaperToSkill script was
  saved.
- No candidate scripts were executed, no SNAP-T2 score was produced, and no
  main raw rows were appended.

## Evidence Boundary

- This is provider availability metadata for a compact SNAP-T2 diagnostic
  script-generation retry.
- It is not model-quality evidence, not a SNAP-T2 task failure, not a
  paper-facing main-row replacement, and not PaperToSkill advantage evidence.
- Future SNAP-T2 executable-candidate evidence still requires paired
  Summary/PaperToSkill scripts generated under the same task, fixture, scorer,
  resource budget, model setting, and no-mid-run-human rule before execution.
