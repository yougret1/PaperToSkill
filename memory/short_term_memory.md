# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-05.

## Current Task

- Latest user request: save the current phase, upload to GitHub, and continue
  core work toward `C:\Users\19351\Desktop\tem\nextStep.md`. Preserve the
  existing local-log boundary: do not modify `research/run_logs/**` or
  `research/stage_log.md` during record-sync-only work.
- Current save target status: GitHub backup recovered again. The latest
  verified remote checkpoint is
  `db535e7eb344b4aed97f7ba9c3accb266f309d68 refs/heads/main`
  (`db535e7 Record SNAP diagnostic checkpoint`). This remote-backed chain now
  includes the SNAP executable-candidate prompt packets, phase111/phase112
  diagnostic generation/execution artifacts, and memory checkpoint records.
  A later local record-sync commit after `db535e7` is not remote-backed yet:
  `git push origin main` and the follow-up `git ls-remote --heads origin main`
  both failed to connect to github.com port 443 after about 211xx ms.
  Earlier `Recv failure: Connection was reset` failures remain historical
  GitHub transport metadata, not experiment correctness.
- Current local phase commit `77e8ada` implements the SNAP executable-candidate
  runner/checker/test path:
  `scripts/run_real_reuse_snapatac2_executable_candidate.py`,
  `tests/test_run_real_reuse_snapatac2_executable_candidate.py`,
  `scripts/check_real_reuse_benchmark.py`, and
  `tests/test_check_real_reuse_benchmark.py`. Focused verification passed:
  `python -m unittest tests.test_run_real_reuse_snapatac2_executable_candidate
  tests.test_check_real_reuse_benchmark -v` and
  `python scripts\check_real_reuse_benchmark.py --strict`. The runner is
  diagnostic only: it executes candidate scripts, writes runner-owned
  `candidate_output.json`, `artifact_manifest.json`, and
  `resource_record.json`, calls the existing SNAP scorer, does not append to
  main raw rows, and does not replace paper-facing main rows by default.
- Current local SNAP continuation adds executable-candidate prompt packets for
  future paired Summary/PaperToSkill candidate scripts:
  `scripts/build_real_reuse_snapatac2_executable_candidate_prompts.py`,
  `tests/test_build_real_reuse_snapatac2_executable_candidate_prompts.py`,
  `results/real_reuse/snapatac2_executable_candidate_prompt_plan.{md,json}`,
  and four prompt files under
  `results/real_reuse/snapatac2_executable_candidate_prompts/`. The builder is
  local-only: it does not call a model, score outputs, append raw rows, or
  replace main rows. Verification passed for the new prompt-packet test,
  SNAP runner/preflight tests, strict real-reuse/paper-table/paper-claim/usage/
  AAAI/submission/goal/package gates, `git diff --check` with only CRLF
  warnings, and a raw-key scan with no matches. This phase is saved locally as
  `ef8cbe0 Prepare SNAP executable candidate prompts`; GitHub backup failed
  with connection resets and is recorded in `toHuman.md`.
- Current local SNAP executable-candidate live checkpoint is saved in
  substantive phase commit `9829123 Run SNAP executable candidate diagnostics`:
  `scripts/run_real_reuse_snapatac2_executable_candidate_prompts.py` generates
  candidate scripts from the prompt packets and now writes incremental reports
  after each packet so provider stalls preserve partial provenance. Phase111
  GPT-family `gpt-5.5` generation produced paired SNAP-T1 scripts, but both
  candidate scripts imported Windows-incompatible POSIX `resource`; executing
  them with `scripts/run_real_reuse_snapatac2_executable_candidate.py` under
  run id `phase111_gpt_snapatac2_executable_candidate_t1` scored both rows
  0.500 with `missing_required_artifacts_or_metrics` and
  `execution_status=error`. This is diagnostic only and does not replace main
  SNAP rows. The prompt builder was then tightened to require cross-platform
  Python, no `resource`, no network/package installation, and writes only under
  `--artifact-dir` / `--result-json`. Phase112
  `phase112_gpt_snapatac2_executable_candidate_scripts_v2` produced only
  `SNAP-T1_summary.py`; the next provider request did not return after an
  extended wait, so the matching long-running Python process was stopped and
  `results/real_reuse/snapatac2_executable_candidate_script_generation_report.{md,json}`
  records a partial run. Do not execute phase112 as a paired diagnostic until
  the matching PaperToSkill script exists.
  Verification for this uncommitted checkpoint passed: focused SNAP
  prompt/prompt-runner/candidate-runner/repro-package unit tests,
  `check_reproducibility_package.py --strict`,
  `check_real_reuse_benchmark.py --strict`, `check_paper_tables.py --strict`,
  `check_paper_claims.py --strict`, `check_usage_examples.py --strict`,
  `check_aaai_package.py --strict`, `check_submission_review.py --strict`,
  `check_goal_completion.py --strict`, `git diff --check` with only CRLF
  warnings, and a raw-key scan with no matches.
- `research/real_reuse_stabilization_queue.md` now marks the SNAP P1 local
  action as runner-implemented: future SNAP reruns should use the executable
  candidate runner only when paired Summary/PaperToSkill candidate scripts
  exist, and must not fabricate executable evidence from old plan/JSON outputs.
- After the latest GitHub retry failed, local non-network checks were rerun:
  `python scripts\check_paper_tables.py --strict` and
  `python scripts\check_usage_examples.py --strict` both passed without
  producing tracked report changes.
- Row-selection metadata for paper-facing real-reuse outputs is now
  implemented and verified locally: `scripts/build_real_reuse_paper_tables.py`
  and `scripts/build_real_reuse_failure_analysis.py` write row-selection path,
  entry count, and boundary text into Markdown/JSON outputs so follow-up raw
  rows cannot be mistaken for main-table replacements.
- Current execution priority remains the core real-reuse main experiment.
  SWE-T1 source-context reporting, SNAP artifact-execution diagnosis, and the
  phase108 SNAP executable-artifact follow-up are complete and remain
  diagnostic only.
- Local non-network continuation after the row-selection phase added
  `research/real_reuse_stabilization_queue.md`. The first priority is now
  completed locally: the SNAP executable-candidate contract is pre-registered
  in `benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json`,
  summarized in `research/snapatac2_executable_candidate_contract.md`, and
  covered by strict real-reuse preflight checks. This does not replace the SNAP
  main rows.
- SWE-T1 task-contract decision is now completed locally:
  `benchmarks/real_reuse/swe_t1_task_contract_decision_v0.json` and
  `research/swe_t1_task_contract_decision.md` freeze the current SWE-T1 main
  row as boundary evidence, forbid more model calls under the current hidden
  test contract, and require issue-aligned hidden tests before any future
  paired rerun.
- SWE-T1 issue-aligned revised scorer/test contract is now pre-registered and
  validated locally:
  `benchmarks/real_reuse/swe_t1_issue_aligned_contract_v0.json`,
  `benchmarks/real_reuse/assets/SWE-T1/scorer_only/issue_aligned_check.py`,
  `research/swe_t1_issue_aligned_contract.md`, and
  `results/real_reuse/swe_t1_issue_aligned_contract_validation.{md,json}`.
  The base workspace fails the alias no-join check as expected; the phase107
  Summary patch passes; the phase107 PaperToSkill patch fails the join
  regression guard. This is diagnostic contract validation only and not a
  main-row replacement. The contract save is in local commit `cdf67b9`
  (`Pre-register SWE-T1 issue-aligned contract`).
- SWE runner override support is implemented in local commit `0f3a499`
  (`Support SWE scorer override runs`): `scripts/run_real_reuse_swe.py` now
  accepts scorer/test override options, with regression coverage in
  `tests/test_run_real_reuse_swe.py`.
- SWE-T1 issue-aligned paired follow-up has run locally as
  `phase110_gpt_swe_t1_issue_aligned_followup`: Summary scored `1.000` and
  PaperToSkill scored `1.000` under the revised issue-aligned scorer. This
  shows the revised scorer/contract can close for both conditions; it does not
  show PaperToSkill advantage and must not replace the locked first-pass
  SWE-T1 main row unless explicitly promoted later. The dedicated diagnostic
  table is now generated at
  `results/real_reuse/swe_t1_issue_aligned_followup.{csv,md,json}`, included in
  `paper/aaai/papertoskill_tables.tex`, and covered by the paper-table checker.
  Local commit `599382d` (`Add SWE-T1 issue-aligned follow-up table`) now
  contains the appended phase110 raw rows, run artifacts, run report,
  dedicated CSV/MD/JSON table, builder/test, paper table, rebuilt AAAI PDF, and
  table/package checker/report updates.
- Current remote-backup status: GitHub backup is verified through
  `db535e7eb344b4aed97f7ba9c3accb266f309d68 refs/heads/main`
  (`db535e7 Record SNAP diagnostic checkpoint`). The previously unbacked local
  commits from `4b216b6` through the SNAP diagnostic record are now
  remote-backed.
- The current discussion policy is: stabilize the core eight-row real-reuse
  evidence first; collect auxiliary raw data opportunistically; keep LLM
  ablation auxiliary, component ablation appendix-only, and user study
  last/optional. Provider latency, timeouts, and retry counts are availability
  metadata, not effectiveness metrics.
- `toHuman.md` now says no experiment-side human action is required, records
  local commit `599382d` plus later push-status memory records, and lists the
  exact GitHub push / remote-check transport errors. It no longer asks the
  user to create `ok.txt` for GitHub status; `ok.txt` is reserved for completed
  human-fidelity annotation or a concrete placed core real-reuse asset.
- The committed chain through `db535e7 Record SNAP diagnostic checkpoint`
  is pushed to `origin/main` and verified by `git ls-remote --heads origin
  main` as
  `db535e7eb344b4aed97f7ba9c3accb266f309d68 refs/heads/main`. This includes
  the earlier recovered GitHub backup records, real-reuse boundary tightening,
  SNAP executable-candidate runner, prompt packets, phase111/phase112
  diagnostic artifacts, and memory/queue sync. Earlier GitHub HTTPS transport
  failures are availability metadata, not experiment-correctness evidence.
- Verification before the `599382d` phase save passed:
  `python -m unittest tests.test_build_real_reuse_swe_t1_issue_aligned_followup
  tests.test_check_paper_tables tests.test_check_reproducibility_package -v`,
  `check_paper_tables.py --strict`,
  `check_reproducibility_package.py --strict`,
  `check_real_reuse_benchmark.py --strict`, `check_paper_claims.py --strict`,
  `check_goal_completion.py --strict`, `check_submission_review.py --strict`,
  `check_usage_examples.py --strict`, `check_aaai_package.py --strict` after
  rebuilding the AAAI PDF, `git diff --check` with only CRLF warnings, and a
  raw-key scan with no matches.
- `C:\Users\19351\Desktop\tem\toHuman.md` should say no immediate human action
  is required, and `ok.txt` should only be created for completed human-fidelity
  annotation or a concrete placed core asset.
- Current GitHub transport note: previous 2026-07-05 connection-reset /
  port-443 failures recovered again. Current verified remote state is
  `db535e7eb344b4aed97f7ba9c3accb266f309d68 refs/heads/main`. Before claiming
  any later phase save is remote-backed, rerun `git status -sb`,
  `git log -5 --oneline`, and `git ls-remote --heads origin main`.
- Historical Claude-family availability checkpoint: after record-sync commit
  `977b2b9` (`Sync experiment planning records`), Claude-family REF-T2 was
  retried from the local Claude API doc key with the v0 300-second / 5-attempt
  protocol; both Summary and PaperToSkill still returned provider HTTP 502
  after 5 attempts. This is availability metadata only. Commit `7ee44ad`
  (`Track Claude ablation availability metadata`) then updated
  `scripts/build_real_reuse_llm_ablation_results.py` so pending-run
  availability metadata from the latest AIDE/SWE/REF runner reports appears in
  `results/real_reuse/llm_ablation_summary.{md,json}` without changing the
  12/18 scored-row count.
- Current 2026-07-05 Claude-family retry checkpoint: after the remote backup
  recovered, Claude-family AIDE-T2, SWE-T2, and REF-T2 were retried from the
  current local API document path
  `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument\Claude大模型接口说明文档.md`
  using the pre-registered `claude-opus-4-8` slot, 300-second provider
  timeout, 5 attempts per condition, and the same Summary/PaperToSkill pairing.
  All six condition rows again returned provider HTTP 502 after 5 attempts.
  `results/real_reuse/aide_run_report.json`,
  `results/real_reuse/swe_run_report.json`, and
  `results/real_reuse/reflexion_run_report.json` now carry this latest
  availability metadata. `results/real_reuse/llm_ablation_summary.md` remains
  12 collected scored rows / 18 expected rows, with the 6 Claude-family rows
  pending; this is provider availability metadata, not method-quality evidence.
- Latest remote-backed chain: Claude retry availability, bounded
  summary-comparison claim cleanup, current project record sync, GitHub backup
  recovery, real-reuse record-boundary tightening, the tested SNAP
  executable-candidate runner, push-blocker records, stabilization-queue sync,
  and memory retry sync are remote-backed through `0832201`.
- Current non-network claim-boundary cleanup: `research/claim_source_map.md`
  no longer says the broad "PaperToSkill skills outperform generic summaries"
  claim is a TBD hypothesis. It now states the evidence-bounded version:
  PaperToSkill outperforms Summary on selected locked original-style tasks
  (AIDE-T2 and SWE-T2 in the first GPT-family pass), while current evidence
  remains mixed and does not support aggregate superiority.
- Current local core-stabilization change: the real-reuse preflight now treats
  a separate `domain_robustness` planned output as deprecated/forbidden,
  checks current planned output paths (`main_results_plan.*`,
  `failure_analysis.*`, and `llm_ablation_raw_rows.csv`), and checks the
  pre-registered SNAP executable-candidate contract, and checks the SWE-T1
  task-contract decision. This keeps the "no separate breadth experiment"
  decision, SNAP execution-contract boundary, and SWE-T1 rerun boundary
  machine-checkable.
- Current row-selection guard change: regenerated
  `results/real_reuse/main_results_plan.{md,json}` and
  `results/real_reuse/failure_analysis.{md,json}` now report that
  `results/real_reuse/main_run_selection.json` contributed 16 selected rows,
  preserving first-pass main rows while leaving diagnostic follow-ups auditable.

## Latest Record Sync Policy

- Keep the main experiment as eight locked paper-task rows comparing Summary
  with PaperToSkill under source-paper-style objective metrics.
- Do not add a separate breadth/coverage experiment; current breadth is the
  eight main paper-tasks.
- Keep component ablation appendix-only and user study last/optional.
- Treat Full Excerpt as an auxiliary sanity check, not a main baseline.
- Attach LLM ablation to the real-reuse task protocol; do not use older
  saved-response usage-plan scoring as downstream task-success evidence.
- Provider latency, API timeout, and retry counts are availability metadata,
  not core effectiveness metrics. Give third-party LLM calls longer timeout and
  more retries.
- Preserve `results/real_reuse/main_run_selection.json` so follow-up rows such
  as SWE-T1 phase107 do not silently replace paper-facing main-table cells.

## Current Core Experiment State

- Main experiment: `Real-Reuse Main Results`, comparing `Summary` vs
  `PaperToSkill` under the same locked paper-task, input/output, scorer, and
  local run setting.
- This is not a real-user study. The main metrics are source-paper-style
  objective task metrics, not user-experience metrics.
- Provider latency, API timeout, retry count, and third-party service
  instability are not core effectiveness metrics. Give model calls more timeout
  and retry budget, and record provider availability separately.
- Current first GPT-family `gpt-5.5` pass has scored all eight rows:
  AIDE-T1 `0.816/0.817` solved by both; AIDE-T2 `0.000/0.826`
  PaperToSkill-only success; SWE-T1 `0.000/0.000` patch-apply failure;
  SWE-T2 `0.000/1.000` PaperToSkill-only success; REF-T1/T2 `1.000/1.000`;
  SNAP-T1/T2 `0.000/0.500` and `0.200/0.400` below success threshold.
- Evidence boundary: this is mixed first-pass downstream stress-test and
  failure-boundary evidence, not aggregate PaperToSkill superiority over
  Summary.
- SWE-T1 phase107 shared-source-context follow-up is complete locally with
  Summary/PaperToSkill both `0.000/0.000`. Unlike the first-pass row, both
  candidate patches applied; the failure reason is `test_command_failed`
  because the hidden test expected the specific L031 warning-message change
  while both candidates edited rule logic. This is diagnostic follow-up
  evidence, not a main-table replacement.
- SNAP artifact-execution diagnosis is complete in
  `results/real_reuse/snapatac2_artifact_followup.{md,json}`. It found that
  selected SNAP rows are plan/JSON outputs under a non-executing runner, while
  the scorer requires completed artifacts plus runtime/memory records. Fixtures
  are readable; `snapatac2` is not importable in the current Python
  environment. Main SNAP rows remain unchanged.
- Phase108 SNAP executable-artifact follow-up is complete in
  `results/real_reuse/snapatac2_executable_artifact_followup.{csv,md,json}`
  with runner `scripts/run_real_reuse_snapatac2_executable_followup.py`.
  It executes a pre-registered controlled scaffold over the same miniature
  fixtures; all four SNAP-T1/T2 Summary/PaperToSkill rows score 1.000 under
  the existing scorer. It does not append to `raw_rows.jsonl`, does not replace
  main SNAP rows, and does not show PaperToSkill advantage.

## Current Auxiliary Evidence Policy

- Full Excerpt sanity is scored for AIDE-T1, SWE-T1, and SNAP-T1, but it is
  auxiliary sanity/cost/context evidence only, not a main baseline.
- LLM ablation should be attached to the real-reuse task protocol and should
  not rely on the older saved-response usage-plan protocol as downstream task
  evidence.
- A pre-registered real-reuse LLM ablation command plan now exists in
  `benchmarks/real_reuse/llm_ablation_v0.json` and
  `results/real_reuse/llm_ablation_plan.{md,json}`. It selects AIDE-T2,
  SWE-T2, and REF-T2; uses GPT-family `gpt-5.5`, Claude-family
  `claude-opus-4-8`, and DeepSeek-family `deepseek-v4-flash`; and gives each
  provider call 300 seconds, 5 attempts, and 5-second retry delays. Phase109
  has collected all GPT-family and DeepSeek-family rows for REF-T2, AIDE-T2,
  and SWE-T2. GPT-family scores are REF-T2 1.000/1.000, AIDE-T2 0.814/0.000
  with the PaperToSkill candidate timing out under the 300-second local scorer,
  and SWE-T2 0.000/0.000 with both conditions failing `patch_apply_failed`.
  DeepSeek-family scores are REF-T2 1.000/1.000, AIDE-T2 0.500/0.500 below the
  success threshold, and SWE-T2 0.000/0.000 with both conditions failing
  `patch_apply_failed`. Claude-family REF-T2, AIDE-T2, and SWE-T2 were all
  attempted for both Summary and PaperToSkill, but all six condition rows
  returned provider HTTP 502 after 5 attempts per condition. They remain
  pending as scored rows. `results/real_reuse/llm_ablation_summary.md` reports
  12 collected scored rows out of 18 expected rows. This is auxiliary
  model/repetition evidence, not a main-row replacement and not aggregate
  PaperToSkill advantage.
- Human-fidelity annotation supports semantic fidelity and reviewability, not
  main task effectiveness. It remains pending: 0 scored rows and 24 pending
  paper-by-criterion cells.
- Quality/grounding gates remain supporting evidence: rubric, source-span,
  source-map, context coverage, usage examples, token accounting, paper-table
  gates, and claim gates.
- Do not keep a separate domain breadth/coverage auxiliary experiment; the
  selected main paper-tasks provide the current breadth.

## Model And External Evidence State

- GPT protocol refresh completed both current rows with `gpt-5.5`.
- DeepSeek completed both current rows with `deepseek-v4-flash`; the DeepSeek
  handoff reports `responses_present`.
- Latest Claude protocol refresh used Anthropic Messages but was blocked by
  provider HTTP 502. In the real-reuse LLM ablation, all Claude-family
  AIDE-T2/SWE-T2/REF-T2 Summary/PaperToSkill condition rows were attempted and
  all remain unscored for the same provider-availability reason. Treat the 502
  as provider availability, not model quality.
- Local token accounting is complete for the current evidence set and replaces
  provider billing/success-per-dollar claims in the current paper scope.
- AI-Scientist-v2 dry-run succeeded historically. The bounded
  AI-Scientist-v2 LLM-client smoke is now complete, and the bounded full
  live-run handoff is complete with one completion directory. This is bounded
  integration/synthetic sensitivity evidence, not human fidelity, real-data
  validation, or broad live research-task success.
- AAAI decision is recorded as `wait_for_external_evidence`; final submission
  readiness remains pending under that policy.

## Immediate Next Actions

1. Save the current local phase after broader verification: the SNAP
   executable-candidate runner is implemented and focused tests/preflight pass.
   It remains diagnostic and must not change paper-facing main rows unless
   explicitly promoted through `results/real_reuse/main_run_selection.json`.
2. Retry Claude-family real-reuse LLM ablation rows only opportunistically when
   provider availability recovers. The current collected scored slices are all
   GPT-family and DeepSeek-family rows for REF-T2, AIDE-T2, and SWE-T2; all
   six Claude-family condition rows were attempted and blocked by provider
   HTTP 502 after 5 attempts per condition. Do not commit raw keys.
3. Keep Summary and PaperToSkill paired under the same task/scorer contract for
   any follow-up. Main SNAP rows remain unchanged unless explicitly promoted.
   For SNAP executable-candidate reruns, execute/interpret a task only when
   paired Summary/PaperToSkill candidate scripts exist for the same prompt
   generation phase; phase112 currently has only `SNAP-T1_summary.py`.
4. During core reruns, collect auxiliary raw data where cheap: provider
   availability, failure reasons, context/token proxies, and raw rows needed
   for real-reuse LLM ablation.
5. Run broader verification gates before the next phase save:
   `check_real_reuse_benchmark.py`, `check_paper_tables.py`,
   `check_reproducibility_package.py`, `check_goal_completion.py`,
   `check_paper_claims.py`, `git diff --check`, and a raw-key scan.
6. Latest verified remote-backed checkpoint:
   `db535e7 Record SNAP diagnostic checkpoint`, verified at
   `db535e7eb344b4aed97f7ba9c3accb266f309d68 refs/heads/main`.
7. Latest local record-sync commit after `db535e7` is not remote-backed yet due
   GitHub port-443 connection failure. No experiment-side human action is
   required.

## Boundaries

Do not claim:

- Aggregate downstream effectiveness or broad superiority over Summary.
- Human-validated semantic fidelity.
- Provider billing, live invoices, or success-per-dollar evidence.
- Saved-response scoring as proof of live downstream task success.
- Reliable arbitrary-PDF-to-skill automation.
- Final AAAI submission readiness.

Do not modify:

- `research/run_logs/**`
- `research/stage_log.md`
