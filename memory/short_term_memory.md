# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-06.

## Current Task

- Latest user request: resume after the previous agent, read memory/logs and
  the referenced thread, restate the current task and boundaries, then continue
  the non-blocked work toward `C:\Users\19351\Desktop\tem\nextStep.md`.
  Preserve the existing local-log boundary: do not modify
  `research/run_logs/**` or `research/stage_log.md` during record-sync-only
  work.
- Current local SNAP-T2 prompt-contract continuation: the SNAP
  executable-candidate prompt builder now has a compact mode and generated
  `results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.{md,json}`
  plus four compact packets under
  `results/real_reuse/snapatac2_executable_candidate_compact_prompts/`.
  This is non-network planning/contract work only: it does not call a model,
  score outputs, append raw rows, replace main rows, or alter
  `results/real_reuse/main_run_selection.json`. The compact SNAP-T2 Summary
  prompt is 5,150 bytes versus 7,111 for the full packet, and compact SNAP-T2
  PaperToSkill is 5,553 bytes versus 14,122. The phase is committed and
  independently remote-verified as
  `245c2b276842de657103f89b5227b8fe53fa9f10 refs/heads/main`
  (`245c2b2 Prepare compact SNAP candidate prompts`).
- Follow-up record-sync commit `0a25da3 Record compact prompt checkpoint backup`
  updates memory/runbook/goal-audit records to the verified `245c2b2`
  checkpoint. Its first `git push origin main` failed with `Recv failure:
  Connection was reset`, and the immediate `git ls-remote --heads origin main`
  failed with the same reset. Treat this as GitHub transport metadata only;
  no human `ok.txt` is required for GitHub status.
- Follow-up blocker-record commit `a7a9e3e Record compact checkpoint push
  blocker` is now independently remote-verified:
  `a7a9e3e772883e76404ee217a9ed51278c4c2477 refs/heads/main`. This remote
  HEAD includes the compact prompt checkpoint plus record-sync/blocker
  metadata only; it does not add experiment scores, raw rows, or paper-facing
  main-row changes.
- Follow-up record-sync commit `b770e20 Record verified compact checkpoint
  recovery` is now independently remote-verified:
  `b770e2005bd881c4afa31be2571cfb01d5207971 refs/heads/main`. It records the
  recovered `a7a9e3e` checkpoint state and does not add experiment scores,
  raw rows, or paper-facing main-row changes.
- Follow-up commits `8ac4ddf Refresh Claude availability metadata` and
  `39c4e0f Record Claude availability push blocker` are now independently
  remote-verified:
  `39c4e0ff7a5d500d3250ea7f6dd177a00672fa95 refs/heads/main`. They record a
  2026-07-06 Claude direct availability probe with the local Claude API
  document key, Anthropic Messages, `max_tokens=16`, and a 180-second timeout;
  all three Claude aliases again returned provider HTTP 502. The first `git
  push origin main` and immediate `git ls-remote --heads origin main` failed
  with `Recv failure: Connection was reset`, but a later push and independent
  remote check recovered the backup. Treat this as GitHub transport metadata
  plus provider availability metadata only; no human `ok.txt` is required for
  GitHub or provider status.
- Current pre-submission gate rerun after the checkpoint-record sync passed
  without repository diff drift: full unit discovery reported 211 tests OK, and
  strict submission-review, AAAI submission-decision, external-evidence packet,
  paper-claim, reproducibility-package, AAAI-package, paper-table,
  usage-example, and real-reuse preflight checks all passed. `git diff
  --check` returned only the usual Windows line-ending warnings, and protected
  paths (`research/run_logs/**`, `research/stage_log.md`, and
  `results/real_reuse/main_run_selection.json`) had no diff.
- Current paper-outline evidence-boundary sync: `paper/outline.md` no longer
  says live-transfer prompt packets are waiting to be executed. The saved
  live-transfer and older saved model-ablation rows are already collected and
  scored under output-contract evaluators, while human semantic fidelity,
  provider billing, and live downstream task success remain unsupported by
  those saved responses. The outline now also distinguishes the older 6/6
  saved-response model-ablation protocol from the current real-reuse LLM
  ablation, which is still 12/18 scored with Claude-family rows
  provider-pending.
- Current GitHub backup recovery: the earlier checkpoint-sync commits
  `45ef25b Sync remote checkpoint after LLM handoff guard` and
  `0538ef1 Record checkpoint sync push blocker` first failed to back up because
  GitHub HTTPS transport was unavailable. A later `git push origin main`
  recovered those commits together with `5786d7d Sync outline evidence
  boundary`, and `git ls-remote --heads origin main` verified
  `5786d7d8538a3fd856d98f09619fbc5447c9ebed refs/heads/main`. This is GitHub
  transport metadata only; no human `ok.txt` is required for GitHub status.
- Current submission-review LLM-ablation distinction separates the older
  saved-response model ablation from the auxiliary real-reuse LLM ablation in
  `research/rebuttal_bank.md`, `research/submission_checklist.md`, and
  `research/review_report.md`. `scripts/check_submission_review.py` now checks
  `results/real_reuse/llm_ablation_summary.json` and requires the current
  12/18 scored-row real-reuse slice, GPT-family 0.605/0.333, DeepSeek-family
  0.500/0.500, and Claude-family 0/6 provider-pending HTTP 502 boundary.
  Full unit discovery passed 208/208 tests. Focused
  `tests.test_check_submission_review` and strict submission-review, package,
  goal, paper-claim, AAAI-package, paper-table, real-reuse preflight,
  usage-example, external-evidence packets, external-evidence closure, and
  AAAI submission-decision gates passed. `submission_review_report` is now
  `18 ready / 0 failed`; package remains `474 ready / 1 pending / 0 failed`,
  and goal completion remains `78 ready / 3 pending / 0 failed`. This does not
  change experiment scores, main-row selection, or any paper claim strength.
  The phase was saved and pushed as `905899c Guard real-reuse LLM ablation
  handoff`; `git ls-remote --heads origin main` verified
  `905899cc8d1a5071ac9b26f8c4e927f266445a35 refs/heads/main`.
- Current paper-finalization continuation removed draft/planning wording from
  the AAAI main real-reuse table caption: Table 1 now says scores come from the
  eight locked local raw rows selected by `main_run_selection.json`. The claim
  checker now treats `paper/aaai/papertoskill_tables.tex` as paper-facing text
  and fails on draft language such as "future reruns or additional rows may be
  added", `TBD`, placeholders, or "to be filled". This does not change the
  locked eight main rows or any experiment score. The AAAI PDF was rebuilt and
  remains 8 pages. Local verification passed `python -m unittest
  tests.test_check_paper_claims tests.test_check_paper_tables
  tests.test_check_aaai_package tests.test_check_reproducibility_package -v`,
  `check_paper_claims.py --strict`, `check_paper_tables.py --strict`,
  `check_aaai_package.py --strict`, `check_reproducibility_package.py
  --strict`, `check_usage_examples.py --strict`,
  `check_real_reuse_benchmark.py --strict`, `check_goal_completion.py
  --strict`, `check_submission_review.py --strict`,
  `check_aaai_submission_decision.py --strict`, `git diff --check` with only
  CRLF warnings, a long `sk-...` raw-key scan with no matches, and no diff
  under `research/run_logs/**` or `research/stage_log.md`. Latest refreshed
  report counts: paper claims `56 ready / 0 failed`, package `474 ready / 1 pending /
  0 failed`, AAAI package `20 ready / 0 failed`, paper tables `343 ready / 0
  failed`, submission review `18 ready / 0 failed`, goal completion `78 ready /
  3 pending / 0 failed`. Human-fidelity annotation remains pending; `ok.txt`
  was absent at resume.
- Current limitations-claim gate sync extends `scripts/check_paper_claims.py` to
  cover `paper/limitations.md` in addition to the AAAI body, AAAI table file,
  Markdown draft, and paper outline. `paper_claim_report.md` is now `ready`
  with 51 ready checks and 0 failed checks. It fails on stale limitations
  wording that says the latest Claude-family live recheck completed, and it
  keeps provider-economics claims bounded to local token proxies or future
  measured-cost protocols. This does not change experiment scores, main-row
  selection, or paper claims. Focused claim/package/submission/goal tests,
  related strict gates, protected-log/main-selection scans, raw-key scan, and
  full unit discovery passed; full unit discovery reported 209 tests OK. The
  phase-save commit is `8449799 Guard limitations claim boundary`. Its first
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  the immediate `git ls-remote --heads origin main` failed with `Failed to
  connect to github.com port 443 after 21108 ms`; treat this as GitHub
  transport metadata only. A push retry after the blocker-record commit also
  failed with `Failed to connect to github.com port 443 after 21094 ms`. A
  later push recovered both `8449799` and `6823179` together with the
  follow-up `5aa4195 Sync model response cost boundary` commit, and
  `git ls-remote --heads origin main` verified
  `5aa4195f4636c1d8c5994ee1eb6c4f6949279eb8 refs/heads/main`.
- Historical outline-claim gate sync extended `scripts/check_paper_claims.py` to
  cover `paper/outline.md` in addition to the AAAI body, AAAI table file, and
  Markdown draft. That stage produced the earlier 38-check report
  and 0 failed checks, and it fails on stale outline planning wording such as
  `Planned: LLM real-reuse ablation` or future `results/real_reuse/` language.
  This does not change experiment scores, main-row selection, or paper claims.
  It also keeps the paper-table memory count at 343 ready / 0
  failed. Verification passed `check_paper_claims.py --strict`,
  `check_submission_review.py --strict`, `check_goal_completion.py --strict`,
  `check_reproducibility_package.py --strict`, `check_aaai_package.py
  --strict`, `check_paper_tables.py --strict`, and
  `check_usage_examples.py --strict`. The outline claim gate was pushed as
  `73f4d83`, and the follow-up checkpoint record was pushed as `fe499e5`;
  `git ls-remote --heads origin main` verified
  `fe499e555723786ce8aba63f7bb3c028ba5c91bc refs/heads/main`.
- Current paper finalization audit sync fixes a smaller cost-proxy wording
  drift: paper-facing and result-card records now say the saved-response
  output-token proxy covers six Claude/GPT-family/DeepSeek model-ablation rows
  with 9,594 `o200k_base` output tokens, rather than the earlier
  Claude/GPT-family-only intermediate state. This touches only
  `paper/limitations.md`, `paper/outline.md`, `paper/claim_checklist.md`,
  `results/result_cards.md`, and long memory; it does not change experiments,
  raw rows, `results/real_reuse/main_run_selection.json`, or local logs. Strict
  paper-claim, paper-table, package, goal-completion, and submission-review
  gates passed after the wording sync. The phase was saved and pushed as
  `5aa4195 Sync model response cost boundary`; `git ls-remote --heads origin
  main` verified `5aa4195f4636c1d8c5994ee1eb6c4f6949279eb8`.
- Current follow-up paper-claim regression guard fails if paper-facing text
  reverts to the stale Claude/GPT-family-only model-response cost scope. It
  updates current paper-claim records to 56 ready checks and 0 failed checks,
  and full unit discovery now reports 210 tests OK. This follow-up does not
  change experiment scores, main-row selection,
  `results/real_reuse/main_run_selection.json`, or local logs. The phase was
  saved and pushed as `43f9092 Guard model response cost scope`;
  `git ls-remote --heads origin main` verified
  `43f9092c32a614d882199d5111fe21cc5cb19f8e refs/heads/main`.
- Follow-up record-sync commit `93a2abf Record model cost guard backup`
  updates memory to the verified `43f9092` checkpoint, but its first
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  the immediate `git ls-remote --heads origin main` failed with the same reset
  error. A later `git push origin main` recovered `93a2abf`, `af3ba31`,
  `4a85147`, and `3e18fc5`; `git ls-remote --heads origin main` verified
  `3e18fc5d58ebcf8f791e82c737d3f64457e886e1 refs/heads/main`. This is GitHub
  transport metadata only and does not require human `ok.txt`.
- Follow-up blocker-record commit `af3ba31 Record model cost guard push blocker`
  records that transport failure, but its first push retry also failed with
  `Failed to connect to github.com port 443 after 21063 ms`; the immediate
  `git ls-remote --heads origin main` failed with port-443 connectivity after
  21117 ms. A later push recovered this blocker record; this is GitHub
  transport metadata only.
- Checkpoint-record guard sync checkpoint `3e18fc5 Sync checkpoint record guard`
  updates the short-memory declared
  checkpoint, runbook, goal-completion audit, and generated goal-completion
  report from stale `5786d7d` current-status wording to the verified
  `43f9092 Guard model response cost scope` checkpoint. It also extends
  `scripts/check_goal_completion.py` so the guard accepts the newer "latest
  verified substantive checkpoint" wording. This is record/guard work only; it
  does not change experiments, raw rows,
  `results/real_reuse/main_run_selection.json`, or local logs. The phase was
  pushed and verified at
  `3e18fc5d58ebcf8f791e82c737d3f64457e886e1 refs/heads/main`.
- Follow-up local record-sync commit `4ae3e76 Record recovered checkpoint guard
  backup` saves the recovered checkpoint-record state after reading memory,
  logs, and the referenced Codex thread. `git push origin main` reported
  success and advanced `main` from `3e18fc5` to `4ae3e76`, and local
  `git status -sb` then reported clean against `origin/main`. Two independent
  `git ls-remote --heads origin main` verification attempts failed afterward,
  first with `Recv failure: Connection was reset` and then with
  `Failed to connect to github.com port 443 after 21095 ms`. Treat this as
  GitHub transport metadata only; do not create human `ok.txt` for this status,
  and do not claim `4ae3e76` as independently remote-verified until a later
  `git ls-remote` succeeds.
- Follow-up local blocker-record commit `a72c6d2 Record checkpoint guard
  verification blocker` records those failed independent remote-verification
  checks. Its first `git push origin main` failed with
  `Failed to connect to github.com port 443 after 21060 ms`. Treat this as
  GitHub transport metadata only; do not create human `ok.txt` for GitHub
  status and do not keep retrying GitHub in a tight loop.
- Remote backup later recovered through `bd3fe6e Record pre-submission gate
  rerun`: `git push origin main` advanced `main` from `4ae3e76` to `bd3fe6e`,
  and `git ls-remote --heads origin main` verified
  `bd3fe6e5906411dc23d712d33fabb10a26c6c164 refs/heads/main`. This recovery
  includes `a72c6d2`, `dfd5602`, and `bd3fe6e`; earlier reset and port-443
  failures remain GitHub transport metadata only.
- Current paper-conclusion boundary sync is saved and remote-verified as
  `e57df72 Align paper conclusion with locked-row evidence`; `git push origin
  main` advanced `main` from `bd3fe6e` to `e57df72`, and `git ls-remote --heads
  origin main` verified
  `e57df723bb8bc147626a6769cb2e765311ad6e13 refs/heads/main`. The AAAI
  conclusion and Markdown draft now say the next stage is to stabilize locked
  real-reuse rows with pre-registered paired follow-ups rather than to
  generically repeat/expand real-reuse runs. The AAAI PDF was rebuilt to 8
  pages; strict paper-claim, AAAI-package, paper-table, submission-review,
  package, and goal-completion gates passed.
- A follow-up local record-sync/blocker chain updates memory/runbook/goal-audit/
  goal-completion reports to the verified `e57df72` paper-conclusion boundary
  checkpoint. Its first `git push origin main` failed with `Recv failure:
  Connection was reset`, and the immediate `git ls-remote --heads origin main`
  failed with the same reset error. Treat this as GitHub transport metadata
  only; do not advance the remote-backed baseline beyond `e57df72` until a
  later push/remote check succeeds.
- A later `git push origin main` reported success for that local
  record-sync/blocker/Claude-availability chain and local `origin/main` now
  equals `HEAD`, but two immediate independent `git ls-remote --heads origin
  main` checks both failed with `Recv failure: Connection was reset`. Treat
  this as GitHub verification-transport metadata: the local tracking ref is
  synchronized, but the independently verified remote-backed baseline remains
  `e57df72` until a later `ls-remote` succeeds.
- The follow-up verification-blocker record commit is local-only after its
  first `git push origin main` failed with `Failed to connect to github.com
  port 443 after 21107 ms`. This is GitHub transport metadata only; do not ask
  for human `ok.txt` for GitHub status.
- Pre-submission gate rerun after that local record-sync/blocker chain passed:
  full unit discovery reported 211 tests OK, and strict submission-review,
  AAAI submission-decision, external-evidence packet, external-evidence
  closure, paper-claim, goal-completion, reproducibility-package, AAAI-package,
  paper-table, usage-example, and real-reuse preflight checks all passed.
  `git diff --check` and changed-file raw-key scan had no findings beyond the
  usual CRLF notices, protected paths had no diff, and the tracked working tree
  remained clean with the local branch ahead of `origin/main` by the
  record-sync/blocker chain.
- Current main-results boundary cleanup removes stale "future unfilled cells /
  planning placeholders" wording from `scripts/build_real_reuse_paper_tables.py`
  and regenerated `results/real_reuse/main_results_plan.{md,json}`. It also
  refreshes `results/real_reuse/failure_analysis.{md,json}` from the current
  40-row raw-row ledger while keeping the selected 16 Summary/PaperToSkill main
  entries locked by `results/real_reuse/main_run_selection.json`. The boundary
  now says score cells come from row-selection-selected raw rows, and any
  `Pending` scaffold/pre-run cells indicate missing scored raw rows rather than
  task-success evidence. This does not change the locked eight main rows, any
  score, or `results/real_reuse/main_run_selection.json`. Local commit
  `21009eb Clarify real-reuse main table boundary` records this phase. Its
  first `git push origin main` failed with `Recv failure: Connection was reset`,
  the immediate `git ls-remote --heads origin main` failed with
  `Failed to connect to github.com port 443 after 21115 ms`, and a retry failed
  with `Failed to connect to github.com port 443 after 21067 ms`. A later push
  recovered through `00d32cd Record main table boundary push blocker`, verified
  at `00d32cdab3a35b01ed6cd016de23e21e870b15c7 refs/heads/main`. This is GitHub
  transport metadata only; no human `ok.txt` is required for GitHub status.
- Current pre-submission full-test continuation ran
  `python -m unittest discover -s tests -v`. The first run exposed one stale
  regression-test fixture in `tests/test_check_submission_review.py`: the
  negative test still replaced `467 ready` even though the current package
  report is now `474 ready`, so it no longer simulated stale package counts. The
  fixture now replaces `474 ready` with `459 ready`; focused
  `tests.test_check_submission_review` passes, and the full suite now passes
  206/206 tests. Strict checks also passed after the fix:
  `check_submission_review.py --strict`, `check_goal_completion.py --strict`,
  `check_reproducibility_package.py --strict`,
  `check_external_evidence_packets.py --strict`,
  `check_external_evidence_closure.py --strict`, and
  `check_aaai_submission_decision.py --strict`. The local chain through
  `6c5e6a2 Fix submission review stale count test` was later pushed
  successfully, and `git ls-remote --heads origin main` verified
  `6c5e6a29dfd4ba585101233b41ca819d25b7c17d refs/heads/main`.
- Current auxiliary real-reuse LLM-ablation family-summary continuation
  aggregates existing phase109 evidence into
  `results/real_reuse/llm_ablation_family_summary.csv` and the AAAI
  `tab:real-reuse-llm-ablation` table. GPT-family `gpt-5.5` has 6/6 scored
  rows with Summary/PaperToSkill averages `0.605/0.333`; DeepSeek-family
  `deepseek-v4-flash` has 6/6 scored rows with `0.500/0.500`; Claude-family
  `claude-opus-4-8` remains 0/6 scored and 6 pending because provider HTTP 502
  availability persists. This is auxiliary model-slice evidence only: it does
  not replace the locked eight main rows and does not support aggregate
  PaperToSkill advantage. Local verification passed focused LLM/table/package/
  submission-review unit tests, `check_goal_completion.py --strict`,
  `check_submission_review.py --strict`, `check_usage_examples.py --strict`,
  `check_real_reuse_benchmark.py --strict`, `check_reproducibility_package.py
  --strict`, `check_paper_tables.py --strict`, `check_paper_claims.py
  --strict`, `check_aaai_package.py --strict`, `git diff --check` with only
  CRLF warnings, a changed-file raw-key scan with no matches, and no diff under
  `research/run_logs/**` or `research/stage_log.md`. A later AAAI page-limit
  repair moved the cost-proxy and auto-note tables out of the main PDF into
  `paper/aaai/papertoskill_supporting_tables.tex`, kept them under the
  paper-table drift checker, rebuilt the AAAI PDF to 8 pages, and added an
  AAAI package check that verifies non-reference content ends by page 7.
  At that repair, refreshed counts were: package `468 ready / 1 pending /
  0 failed`, AAAI package `20 ready / 0 failed`, paper tables `343 ready / 0
  failed`, submission review `17 ready / 0 failed`, goal completion `78 ready /
  3 pending / 0 failed`. Its first remote backup attempt failed with
  `Recv failure: Connection was reset`, but a later `git push origin main`
  succeeded and `git ls-remote --heads origin main` verified the recovered
  checkpoint now recorded below.
- Historical record-sync continuation corrected the current remote-checkpoint
  records from the phase114 checkpoint to the verified phase116 provider-block
  checkpoint. `scripts/check_goal_completion.py --strict` now reports
  `current_remote_checkpoint_records` as `declared=96fce87 Record SNAP-T2
  phase116 provider block`, with 78 ready / 3 pending / 0 failed. Verification
  also passed `check_reproducibility_package.py --strict`,
  `check_paper_claims.py --strict`, `check_paper_tables.py --strict`,
  `check_aaai_package.py --strict`, `check_usage_examples.py --strict`,
  `check_submission_review.py --strict`, `git diff --check` with only CRLF
  warnings, a changed-file raw-key scan with no matches, and no diff under
  `research/run_logs/**` or `research/stage_log.md`. The record-sync commit
  `b3441d5` and blocker-note commit `cea43eb` initially followed a GitHub
  reset, but a later push recovered and `git ls-remote --heads origin main`
  verified `96fce87967b207e1cd0a0b9b36ba8fb8795eff33 refs/heads/main`.
- Current claim-checklist sync adds a `Real-reuse first pass` row to
  `paper/claim_checklist.md` and an abstract downgrade bullet that says the
  eight-row real-reuse stress test is mixed boundary evidence, not aggregate
  downstream advantage. It keeps SWE-T1 phase107/phase110 and SNAP
  phase108/phase112 as diagnostic/contract evidence, not paper-facing main-row
  replacements. Local verification passed:
  `python scripts\check_paper_claims.py --strict`,
  `python scripts\check_goal_completion.py --strict`,
  `python scripts\check_reproducibility_package.py --strict`,
  `python scripts\check_submission_review.py --strict`, `git diff --check`
  with only CRLF warnings, a changed-file secret scan with no matches, and no
  diff under `research/run_logs/**` or `research/stage_log.md`.
- Current SNAP-T2 executable-candidate continuation attempted to generate
  paired SNAP-T2 candidate scripts under the pre-registered executable-candidate
  contract with GPT-family `gpt-5.5`, 300-second request timeout, 5 attempts,
  and shell-only credentials loaded from the local GPT API document. The
  Summary condition returned provider HTTP 524 after five attempts and produced
  no script; the PaperToSkill condition was not completed in this phase. The
  default phase112 SNAP-T1 script-generation report was restored with
  `--skip-existing` so the existing paper-facing diagnostic evidence remains
  intact. The partial provider-availability record is saved separately in
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase113_t2_partial.{md,json}`
  and logged at
  `research/run_logs/2026-07-05_phase113_snap_t2_executable_candidate_partial.md`.
  This is provider availability metadata only: it does not execute SNAP-T2,
  append raw rows, replace main rows, or show PaperToSkill advantage.
  The phase-save commit is
  `c030015 Record SNAP-T2 executable candidate availability`; its first
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  the immediate `git ls-remote --heads origin main` failed with
  `Failed to connect to github.com port 443 after 21069 ms`. This is GitHub
  transport metadata only and does not require a human `ok.txt`.
- Current reproducibility-package continuation registers the phase113 SNAP-T2
  partial availability evidence in `scripts/check_reproducibility_package.py`
  and `tests/test_check_reproducibility_package.py`: the two partial reports
  plus the phase113 run log are now package-gated. Package status remains
  `ready_with_pending_external_evidence`; ready count is now
  `453 ready / 1 pending / 0 failed`. This does not change paper-facing main
  rows, execute SNAP-T2, or complete human-fidelity evidence.
- Current SNAP-T2 retry continuation ran phase115 with GPT-family `gpt-5.5`,
  OpenAI Responses, 420-second timeout, 7 attempts, and 8-second retry delay
  from shell-only credentials loaded from the local GPT API document. The
  SNAP-T2 Summary condition still returned provider HTTP 524 after seven
  attempts, no script or response was saved, and the PaperToSkill condition did
  not produce a row after the Summary-side provider block. The phase-specific
  reports are
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase115_t2_retry.{md,json}`;
  the run log is
  `research/run_logs/2026-07-05_phase115_snap_t2_retry_provider_blocked.md`.
  These three artifacts are package-gated; phase116 later raises the current
  package report count further. This is provider availability metadata
  only and does not execute SNAP-T2, append raw rows, replace main rows, or show
  PaperToSkill advantage. The phase-save commit
  `d8d968d Record SNAP-T2 retry provider block` initially hit a GitHub
  transport blocker: `git push origin main` failed with `Recv failure:
  Connection was reset`, and the immediate `git ls-remote --heads origin main`
  failed with the same reset error. The follow-up blocker-record commit
  `583db16 Record SNAP-T2 retry push blocker` was then pushed successfully, and
  `git ls-remote --heads origin main` verified
  `583db16033980f982cda5ee250edf8a0de405ba9 refs/heads/main`. This is GitHub
  transport metadata only and does not require a human `ok.txt`.
- Current SNAP-T2 Summary retry continuation ran phase116 after a temporary
  small GPT-family direct probe returned HTTP 200 in `%TEMP%` but did not pass
  the custom marker check. The real SNAP-T2 Summary executable-candidate
  generation used GPT-family `gpt-5.5`, OpenAI Responses, 600-second timeout,
  10 attempts, 10-second retry delay, and `--max-tokens 2200`. The Summary
  condition still returned provider HTTP 524 after ten attempts, no candidate
  script or response was saved, and PaperToSkill was not run because the paired
  diagnostic cannot proceed without the Summary-side script. The phase-specific
  reports are
  `results/real_reuse/snapatac2_executable_candidate_script_generation_phase116_t2_summary_retry.{md,json}`;
  the run log is
  `research/run_logs/2026-07-05_phase116_snap_t2_summary_retry_provider_blocked.md`.
  These three phase116 artifacts are now package-gated, bringing the package
  report to `459 ready / 1 pending / 0 failed`.
  This is provider availability metadata only and does not execute SNAP-T2,
  append raw rows, replace main rows, or show PaperToSkill advantage.
- Current Claude-family availability continuation rechecked the local Claude
  API document key with Anthropic Messages, aliases `claude-opus-4-8`,
  `claude-opus-4-7`, and `claude-opus-4-6`, 120-second timeout, and
  `max_tokens=16`. All three aliases still returned provider HTTP 502. The
  direct-probe JSON timestamp was refreshed and
  `research/run_logs/2026-07-05_phase114_claude_direct_availability_recheck.md`
  records the command boundary. This is provider availability metadata only;
  do not score the six pending Claude-family real-reuse LLM-ablation rows as
  negative. The phase-save commit
  `a9857b1 Record Claude availability recheck` was pushed, and
  `git ls-remote --heads origin main` verified
  `a9857b1c296c6e866fe41a9aa8422b69e2bb4f0a refs/heads/main`.
- Current non-network continuation after the resume/thread review updates
  `research/real_reuse_experiment_plan.md` Table 6 with existing quality and
  grounding evidence for AIDE, SWE-agent, Reflexion, SnapATAC2, Toolformer
  sanity, and AI Scientist-v2 sanity. All six rows now cite concrete rubric and
  source-span evidence paths, keep invalid source ranges at 0, keep human
  fidelity pending unless annotated, and point package status to the current
  reproducibility package gate. It also clarifies `research/experiment_queue.md`
  E4 as deferred future method work, not a current main-paper priority. This
  does not change `results/real_reuse/main_run_selection.json`, promote any
  diagnostic follow-up, or touch `research/run_logs/**` /
  `research/stage_log.md`. The table-completion commit was initially
  local-only while GitHub transport was unavailable: `git push origin main`
  failed with
  `Recv failure: Connection was reset`, and `git ls-remote --heads origin main`
  then failed with `Failed to connect to github.com port 443 after 21124 ms`.
  A later retry in this continuation failed again with `Recv failure:
  Connection was reset`, followed by `git ls-remote --heads origin main`
  failing with `Failed to connect to github.com port 443 after 21111 ms`.
  Later GitHub recovery verified these commits as remote-backed through
  `bddd900`, pushed the checkpoint record sync as `9cc0683`, and then
  pushed `5d11adc Mark deferred study tables explicitly`; `git ls-remote
  --heads origin main` verified
  `5d11adc7418762e3e416ccda798f30ca4faf041f refs/heads/main`.
  Follow-up record-sync commit
  `591a3f1 Record recovered deferred-table backup` updated memory/runbook/goal
  audit to that recovered checkpoint, but its first `git push origin main`
  failed with `Recv failure: Connection was reset`; the immediate
  `git ls-remote --heads origin main` also failed with `Failed to connect to
  github.com port 443 after 21089 ms`. The local blocker record
  `34542ec Record deferred backup push blocker` was then created. A later
  `git push origin main` recovered and `git ls-remote --heads origin main`
  verified
  `34542eca0fc4a758cae071193f4327870d6f2867 refs/heads/main`. The later
  Claude-probe record-sync chain also recovered through
  `5d2b98c8e2f9f2c3498a11103830ef775257bfdd refs/heads/main`. This is GitHub
  transport metadata only and does not require a human `ok.txt`.
- Current local claim-boundary continuation updates
  `research/claim_source_map.md` so the failure-branch claim no longer says
  "improves reproducibility" as a TBD hypothesis. It now says PaperToSkill
  preserves failure branches as auditable reproducibility-supporting evidence,
  while causal reproducibility improvement remains untested. Supporting files
  are `results/failure_cases/failure_case_archive.md` and
  `results/reproducibility/package_report.md`.
- Current local claim-matrix continuation applies the same boundary to
  `research/claim_evidence_matrix.md`: failure branches are now described as
  provenance and claim-discipline evidence, with no causal reproducibility or
  task-outcome improvement claimed. Local checks passed after the edit:
  `python scripts\check_paper_claims.py --strict`,
  `python scripts\check_goal_completion.py --strict`, and
  `python scripts\check_reproducibility_package.py --strict`. A fresh
  `git push origin main` retry failed with
  `Failed to connect to github.com port 443 after 21083 ms`, and
  `git ls-remote --heads origin main` failed with
  `Failed to connect to github.com port 443 after 21087 ms`. This is GitHub
  transport metadata only, not experiment correctness, and it does not require
  a human `ok.txt`. A later push recovered after local phase commit
  `eab454d Align failure branch claim evidence matrix`, and
  `git ls-remote --heads origin main` verified
  `eab454dfb8699d25636b8c9fafdaa2cb010b5db5 refs/heads/main`. A later
  GitHub retry pushed the follow-up record-sync and Claude availability
  commits, and `git ls-remote --heads origin main` verified
  `bddd9006523a30b152da69a75f002d7948ff0269 refs/heads/main`.
- Current local/remote status override after the Claude availability recovery:
  the latest locally recorded remote checkpoint is
  `39c4e0ff7a5d500d3250ea7f6dd177a00672fa95 refs/heads/main`
  (`39c4e0f Record Claude availability push blocker`). This checkpoint includes
  the recovered checkpoint-sync commits after the real-reuse LLM-ablation handoff
  guard, the outline update that distinguishes collected/scored saved-response
  rows from unsupported human semantic fidelity, provider billing, and live
  downstream task-success claims, the limitations claim gate, the
  paper-facing saved-response cost-boundary sync, and the stale cost-scope
  regression guard with 56 ready paper-claim checks / 0 failures, plus the
  checkpoint-record guard sync, checkpoint blocker records, pre-submission
  gate rerun record, the paper-conclusion boundary sync, the compact SNAP
  executable-candidate prompt contract, and the recovered Claude availability
  metadata/push-blocker commits. Older
  current-status bullets in this file are historical
  checkpoints only; use fresh `git status -sb`, `git log -5 --oneline`, and
  `git ls-remote --heads origin main` before claiming any later remote-backed
  phase.
- Recovered submission-test backup note: `95f1af3 Record recovered submission
  test backup` and `66e4763 Record submission backup push blocker` initially
  remained local-only after GitHub reset/port-443 failures. A later `git push
  origin main` succeeded, and `git ls-remote --heads origin main` verified the
  later checkpoint above. This is GitHub transport metadata only and does
  not require a human `ok.txt`.
- Current non-network paper-outline audit fixed one stale figure/table-plan row
  in `paper/outline.md`: the real-reuse LLM ablation is now described as an
  auxiliary collected/pending slice (`llm_ablation_summary.md` and
  `llm_ablation_family_summary.csv`) rather than as a future planned result.
  This does not change experiment scores, main-row selection, or paper claims.
- Recovered record-sync note: `b3441d5 Sync phase115 checkpoint records`,
  `cea43eb Record checkpoint sync push blocker`, and `96fce87 Record SNAP-T2
  phase116 provider block` are now remote-backed through the verified phase116
  checkpoint.
- Historical local/remote status after the resume check: the then-latest verified
  remote backup is
  `e1709d3bb965df9df8768271c419467266902474 refs/heads/main`
  (`e1709d3 Record SNAP-T2 availability push blocker`). The earlier
  checkpoint-detail/blocker records, grounding-gate evidence sync,
  quality-grounding table completion, blocker record, failure-branch
  claim-source cleanup, claim-evidence-matrix boundary sync, recovered
  checkpoint record, push-blocker record, Claude direct availability recheck,
  recovered Claude backup checkpoint, deferred-study table marking, recovered
  deferred-table backup record, the deferred-backup push-blocker record,
  recovered deferred backup push record, refreshed Claude availability probe
  metadata, Claude-probe push-blocker record, and recovered Claude-probe
  backup record, the real-reuse claim-checklist boundary sync, the SNAP-T2
  executable-candidate availability record, and the SNAP-T2 availability
  push-blocker record are now included in the verified remote chain. Earlier
  `git ls-remote --heads origin main` failures on 2026-07-05 remain historical
  transport metadata; use `git status -sb`, `git log -5 --oneline`, and a fresh
  `git ls-remote --heads origin main` before making any later remote-backed
  claim.
- Historical resume baseline: GitHub backup had recovered and was verified
  through the resume-memory baseline clarification before this continuation's
  record-sync edits. The then-recorded remote checkpoint was:
  `e1709d3bb965df9df8768271c419467266902474 refs/heads/main`
  (`e1709d3 Record SNAP-T2 availability push blocker`). That remote-backed chain
  includes the SNAP executable-candidate prompt packets, phase111/phase112
  diagnostic generation/execution artifacts, the tightened submission-review
  count-check gate, the updated AAAI phase112 SNAP-T1 executable-candidate
  prose/table caption, the rebuilt AAAI PDF/package report, the draft/outline
  SNAP diagnostic sync, the human-fidelity annotation request, and the current
  resume-memory checkpoint/blocker/recovery/baseline records plus the
  checkpoint-record guard commits, the checkpoint-detail and blocker-record
  commits, the grounding-gate evidence sync, the follow-up checkpoint record,
  the quality-grounding table completion, the push-blocker record, the
  failure-branch claim-source cleanup, the claim-evidence-matrix boundary
  sync, the recovered checkpoint record, the push-blocker record, and the
  Claude direct availability recheck, plus the recovered Claude backup
  checkpoint, deferred-study table marking, recovered deferred-table backup
  record, deferred-backup push-blocker record, recovered deferred backup push
  record, refreshed Claude availability probe metadata, Claude-probe
  push-blocker record, recovered Claude-probe backup record, the real-reuse
  claim-checklist boundary sync, the SNAP-T2 executable-candidate availability
  record, and the SNAP-T2 availability push-blocker record. Earlier `Recv failure: Connection was reset` and port-443 failures
  remain historical GitHub transport metadata, not experiment correctness.
  Treat a future successful `git ls-remote` as the authority before claiming
  any new remote-backed phase.
- Current resume verification on 2026-07-05: `ok.txt` is absent, local
  strict gates passed for real-reuse benchmark, paper tables, paper claims,
  usage examples, AAAI package, submission review, reproducibility package,
  goal completion, and AAAI submission decision. The memory-sync commit is
  `4532dd9 Sync resume checkpoint memory`; `git push origin main` then failed
  with `Recv failure: Connection was reset`, and `git ls-remote --heads origin
  main` failed with `Failed to connect to github.com port 443 after 21100 ms`.
  The follow-up commit `bf95213 Record resume memory push blocker` recorded
  that transport failure; later retries pushed and verified `bf95213`,
  `69d23b1 Record recovered resume memory backup`,
  `f1c50d5 Sync resume baseline memory`, and
  `4d2e040 Clarify resume remote memory baseline`, followed by
  `ac3926c Guard current remote checkpoint records` and the guard-baseline fix;
  later push verification now includes the checkpoint-detail/blocker records,
  the grounding-gate evidence sync, the follow-up checkpoint record, the
  quality-grounding table completion, the failure-branch claim-boundary
  cleanup, the claim-evidence-matrix boundary sync, and the Claude direct
  availability recheck through `bddd900`.
  Goal status remains externally blocked on
  human-fidelity annotation and the follow-on AAAI final decision.
- Follow-up record-sync commit `e2f070e Record recovered claim matrix backup`
  records the recovered `eab454d` remote checkpoint in memory/runbook/goal
  reports. Its first push attempt failed with `Recv failure: Connection was
  reset`, but a later GitHub retry pushed `e2f070e`, `e110a03`, and `bddd900`;
  `git ls-remote --heads origin main` verified `bddd9006523a30b152da69a75f002d7948ff0269`.
  The earlier failure remains transport metadata only and does not require a
  human `ok.txt`.
- Current record-sync continuation tightens
  `scripts/check_submission_review.py` so review/rebuttal/submission handoff
  files must carry exact current gate counts for goal/package, AAAI package,
  paper-table, and usage-example reports. It refreshes
  `results/reproducibility/submission_review_report.{json,md}` to
  `17 ready / 0 failed` and
  `results/reproducibility/package_report.{json,md}` to
  `453 ready / 1 pending / 0 failed`, and updates review/rebuttal/checklist,
  runbook, goal audit, and memory wording to include phase112 SNAP
  executable-candidate diagnostic evidence without promoting it into main
  rows. Verification passed locally:
  `python -m unittest tests.test_check_submission_review -v`,
  `python scripts/check_submission_review.py --strict`,
  `python scripts/check_reproducibility_package.py --strict`,
  `python scripts/check_goal_completion.py --strict`,
  `python scripts/check_paper_claims.py --strict`,
  `python scripts/check_paper_tables.py --strict`,
  `python scripts/check_aaai_package.py --strict`, `git diff --check`
  with only CRLF warnings, a changed-file raw-key scan with no matches, and
  `research/run_logs/**` / `research/stage_log.md` unchanged. The phase is
  saved and remote-backed in `2b823f6 Tighten submission review count checks`.
- Current paper-text synchronization after the submission-review save adds an
  explicit AAAI Results paragraph for the phase112 SNAP-T1 model-generated
  executable-candidate diagnostic and clarifies the corresponding table
  caption. The paper now says the phase112 diagnostic reaches 1.000 for both
  Summary and PaperToSkill under the pre-registered executable-candidate
  contract, but it closes the candidate-script artifact contract for both
  conditions rather than replacing main SNAP rows or showing PaperToSkill
  advantage. The AAAI PDF was rebuilt with `pdflatex`, `bibtex`, `pdflatex`,
  `pdflatex`; it remains 8 pages. Verification passed:
  `python scripts/check_paper_claims.py --strict`,
  `python scripts/check_paper_tables.py --strict`,
  `python scripts/check_aaai_package.py --strict`,
  `python scripts/check_usage_examples.py --strict`,
  `python scripts/check_reproducibility_package.py --strict`, and
  `python scripts/check_goal_completion.py --strict`. The phase is saved and
  remote-backed in `b550a26 Clarify SNAP executable candidate results`.
- Current auxiliary paper-record sync updates `paper/draft.md` and
  `paper/outline.md` so they match the AAAI manuscript's phase108/phase112
  SNAP diagnostic boundary: the controlled scaffold and model-generated
  SNAP-T1 executable-candidate scripts close artifact/execution contracts for
  both Summary and PaperToSkill, but do not replace main rows or show
  PaperToSkill advantage. Verification passed:
  `python scripts/check_paper_claims.py --strict`,
  `python scripts/check_reproducibility_package.py --strict`, and
  `python scripts/check_goal_completion.py --strict`.
- Current external-evidence boundary: local paper writing/checking is
  synchronized, but active goal completion still has pending external evidence.
  `C:\Users\19351\Desktop\tem\toHuman.md` now asks for independent
  human-fidelity annotation over the prepared 24 paper-by-criterion cells. When
  the completed annotation CSV is placed and `ok.txt` appears, run
  `python scripts\summarize_human_fidelity_annotations.py --strict`,
  `python scripts\check_goal_completion.py --strict`, and
  `python scripts\check_reproducibility_package.py --strict`, then revisit the
  AAAI submission decision currently recorded as `wait_for_external_evidence`.
- Current external-evidence packet sync makes that human handoff workflow
  machine-checkable: `scripts/check_external_evidence_packets.py` now requires
  the human-fidelity packet to declare
  `C:\Users\19351\Desktop\tem\toHuman.md`,
  `C:\Users\19351\Desktop\tem\ok.txt`, and the agent-side `ok.txt` cleanup
  command after processing completed annotation. The generated
  `results/external_evidence_packets/packets.{json,md}` now report 8 ready
  checks / 0 pending / 0 failed, and
  `results/reproducibility/package_report.{json,md}` reflects that count.
  Follow-up record sync updates `research/submission_checklist.md`,
  `research/runbook.md`, `research/review_report.md`, and
  `results/result_cards.md` from the old 7-ready packet count to 8-ready while
  keeping the evidence pending.
  This does not complete human-fidelity evidence or change the
  `wait_for_external_evidence` AAAI decision. Local verification passed:
  `python -m unittest tests.test_check_external_evidence_packets
  tests.test_check_reproducibility_package tests.test_check_goal_completion -v`,
  `python scripts\check_external_evidence_packets.py --strict`,
  `python scripts\check_reproducibility_package.py --strict`,
  `python scripts\check_goal_completion.py --strict`,
  `python scripts\check_aaai_submission_decision.py --strict`,
  `git diff --check` with only CRLF warnings, a changed-file raw-key scan with
  no matches, and no diff under `research/run_logs/**` or
  `research/stage_log.md`.
- Follow-up record-sync commit `db7a0f4 Sync external packet readiness records`
  updated `research/submission_checklist.md`, `research/runbook.md`,
  `research/review_report.md`, and `results/result_cards.md` to the 8-ready
  external-packet count. Its first `git push origin main` failed with
  `Recv failure: Connection was reset`, and the immediate
  `git ls-remote --heads origin main` failed with the same reset error. A
  follow-up local blocker-record commit captured this state; its first
  `git push origin main` failed with
  `Failed to connect to github.com port 443 after 21085 ms`. A later retry
  pushed `db7a0f4` plus the amended blocker-record commit
  `9749539 Record external packet sync push blocker`; `git ls-remote --heads
  origin main` returned
  `e038930412867996f63f248c4795eee219d2d20a refs/heads/main`
  before that recovery and later returned
  `9749539c7a0e558e0d249aba0af40aaa54290024 refs/heads/main`.
  This is GitHub transport metadata only and does not require `ok.txt`.
- Current record-drift guard continuation adds
  `current_remote_checkpoint_records` to `scripts/check_goal_completion.py`.
  The first implementation compared current-status records directly to the
  local `refs/remotes/origin/main` hash; after the guard commit was pushed,
  that made the checker self-invalidating because the documents could not
  contain the hash of their own just-created commit. The follow-up fix uses the
  short-term-memory declared checkpoint as the consistency baseline for short
  memory, long memory, runbook, and goal audit, and keeps dynamic
  `origin/main` hashes out of tracked regenerated reports. It still fails on stale
  current-status windows such as `b550a26` being presented as the latest
  checkpoint, and it allows clearly historical hashes. Focused unit tests cover
  stale-current detection, declared-checkpoint extraction, historical-hash
  allowance, and the current report boundary. The goal report now has
  `78 ready / 3 pending / 0 failed`; package count remains
  `453 ready / 1 pending / 0 failed`; submission-review remains
  `17 ready / 0 failed`.
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
  warnings, and a raw-key scan with no matches. This phase is saved in
  `ef8cbe0 Prepare SNAP executable candidate prompts` and is remote-backed in
  the current verified chain.
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
  `phase112_gpt_snapatac2_executable_candidate_scripts_v2` now has paired
  revised `SNAP-T1_summary.py` and `SNAP-T1_papertoskill.py` scripts. The
  first long prompt-runner request hung; direct curl retries with a larger
  output budget returned provider HTTP 524; a no-BOM direct Responses request
  with a shorter output budget produced the PaperToSkill script. The
  generation report was rebuilt with both scripts cached. The paired
  executable-candidate diagnostic run
  `phase112_gpt_snapatac2_executable_candidate_t1` scored Summary and
  PaperToSkill 1.000/1.000 under the existing SNAP-T1 scorer. This is
  diagnostic contract-closure evidence for both conditions, not a main-row
  replacement or PaperToSkill advantage. After rebuilding the AAAI PDF/log
  from the updated TeX tables, verification passed:
  `python -m unittest tests.test_check_paper_tables
  tests.test_check_reproducibility_package -v`,
  `python -m py_compile
  results/real_reuse/snapatac2_executable_candidate_scripts/phase112_gpt_snapatac2_executable_candidate_scripts_v2/SNAP-T1_papertoskill.py`,
  `check_aaai_package.py --strict`, `check_paper_tables.py --strict`,
  `check_real_reuse_benchmark.py --strict`,
  `check_paper_claims.py --strict`,
  `check_reproducibility_package.py --strict`,
  `check_goal_completion.py --strict`, `check_usage_examples.py --strict`,
  `check_submission_review.py --strict`,
  `check_aaai_submission_decision.py --strict`, `git diff --check` with only
  CRLF warnings, and a changed-file raw-key scan with no matches. A narrow
  static scan found no actual `resource` imports in the phase112 scripts. This
  completed phase is saved and remote-backed in `b6dc061 Complete SNAP
  executable candidate diagnostic`.
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
- Resume-baseline remote-backup status: GitHub backup is verified through
  `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`
  (`69d23b1 Record recovered resume memory backup`). The previously unbacked
  local commits from `4b216b6` through the SNAP diagnostic record, the
  follow-up remote-status sync, the phase112 completion commit, the
  submission-review count-check save, the AAAI paper-text sync, the
  draft/outline sync, the human-fidelity handoff request, and the
  resume-memory records through `69d23b1` are remote-backed at that baseline.
- The current discussion policy is: stabilize the core eight-row real-reuse
  evidence first; collect auxiliary raw data opportunistically; keep LLM
  ablation auxiliary, component ablation appendix-only, and user study
  last/optional. Provider latency, timeouts, and retry counts are availability
  metadata, not effectiveness metrics.
- `toHuman.md` now asks for independent human-fidelity annotation and records
  the latest remote-backed checkpoint. It lists historical GitHub push /
  remote-check transport errors as transport metadata only. It no longer asks
  the user to create `ok.txt` for GitHub status; `ok.txt` is reserved for
  completed human-fidelity annotation or a concrete placed core real-reuse
  asset.
- The committed chain through `69d23b1 Record recovered resume memory backup` is
  pushed to `origin/main` and verified by `git ls-remote --heads origin main`
  as
  `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`. This includes
  the earlier recovered GitHub backup records, real-reuse boundary tightening,
  SNAP executable-candidate runner, prompt packets, phase111/phase112
  diagnostic artifacts, memory/queue sync, refreshed AAAI diagnostic-table/
  PDF/package reports, tightened submission-review count checks, and the
  phase112 SNAP-T1 executable-candidate paper-text clarification, auxiliary
  draft/outline synchronization, the human-fidelity annotation request, and
  resume-memory recovery records through `69d23b1`.
  Earlier GitHub HTTPS transport failures are availability metadata, not
  experiment-correctness evidence.
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
- `C:\Users\19351\Desktop\tem\toHuman.md` should keep the current human action
  focused on independent human-fidelity annotation. `ok.txt` should only be
  created for completed human-fidelity annotation or a concrete placed core
  asset, not for GitHub status or diagnostic follow-ups.
- Current GitHub transport note: previous 2026-07-05 connection-reset /
  port-443 failures recovered again. The resume-baseline verified remote state
  is `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`. Before
  claiming any later phase save is remote-backed, rerun `git status -sb`,
  `git log -5 --oneline`, and `git ls-remote --heads origin main`; those
  command outputs are authoritative for the latest exact alignment.
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
- Current Claude-family direct availability recheck after the claim-matrix
  sync used the local Claude API document key in shell-only environment
  variables, Anthropic Messages at `https://coderxiaoc.com/v1/messages`,
  aliases `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`,
  `max_tokens=16`, and a 120-second request timeout. All three aliases
  returned provider HTTP 502, so the full real-reuse Claude-family ablation
  rerun remains deferred as provider availability metadata rather than
  method-quality evidence. A same-session opportunistic recheck on 2026-07-05
  reused the local Claude API document key with the same wire API, aliases,
  `max_tokens=16`, and 120-second timeout; all three aliases again returned
  provider HTTP 502, and only the direct-probe JSON timestamp changed. The
  recheck was saved in `54b6780 Refresh Claude availability probe metadata`;
  its first `git push origin main` and immediate `git ls-remote --heads origin
  main` both failed with `Recv failure: Connection was reset`. The follow-up
  blocker record `7a39bfb Record Claude probe push blocker` was then pushed,
  followed by record-sync commit `5d2b98c Record recovered Claude probe
  backup`; `git ls-remote --heads origin main` verified
  `5d2b98c8e2f9f2c3498a11103830ef775257bfdd refs/heads/main`. Report:
  `results/openai_compatible_direct_probe/claude_family/run_report.md`.
- 2026-07-06 opportunistic Claude direct availability recheck after the
  pre-submission gate rerun used the local Claude API document key in
  shell-only `PAPERTOSKILL_CLAUDE_BASE_URL`/`PAPERTOSKILL_CLAUDE_API_KEY`
  variables, Anthropic Messages at `https://coderxiaoc.com/v1/messages`,
  aliases `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`,
  `max_tokens=16`, and a 120-second request timeout. All three aliases again
  returned provider HTTP 502; only the direct-probe JSON timestamp changed.
  This remains provider availability metadata, not method-quality evidence, so
  the full Claude-family real-reuse LLM ablation rows remain deferred.
- 2026-07-06 follow-up Claude direct availability recheck after checkpoint
  recovery used the same local Claude API document key and shell-only
  `PAPERTOSKILL_CLAUDE_BASE_URL`/`PAPERTOSKILL_CLAUDE_API_KEY` variables, the
  same Anthropic Messages endpoint and aliases, `max_tokens=16`, and a
  longer 180-second request timeout. All three aliases again returned provider
  HTTP 502. This is provider availability metadata only; do not run the full
  six Claude-family real-reuse LLM ablation rows until a small direct probe
  returns a usable response.
- Historical remote-backed chain through `0832201`: Claude retry availability, bounded
  summary-comparison claim cleanup, current project record sync, GitHub backup
  recovery, real-reuse record-boundary tightening, the tested SNAP
  executable-candidate runner, push-blocker records, stabilization-queue sync,
  and memory retry sync were remote-backed through `0832201`; later resume
  baseline records are tracked separately above.
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

1. Continue non-network core real-reuse stabilization after the remote-backed
   phase112 save. The SNAP executable-candidate diagnostic is complete and
   must not change paper-facing main rows unless explicitly promoted through
   `results/real_reuse/main_run_selection.json`.
   A compact SNAP executable-candidate prompt contract is now prepared for a
   future paired SNAP-T2 retry when provider large-context availability looks
   healthier; do not use it to replace the locked SNAP main rows without an
   explicit `main_run_selection.json` promotion.
2. Retry Claude-family real-reuse LLM ablation rows only opportunistically when
   provider availability recovers. The current collected scored slices are all
   GPT-family and DeepSeek-family rows for REF-T2, AIDE-T2, and SWE-T2; all
   six Claude-family condition rows were attempted and blocked by provider
   HTTP 502 after 5 attempts per condition. Do not commit raw keys.
3. Keep Summary and PaperToSkill paired under the same task/scorer contract for
   any follow-up. Main SNAP rows remain unchanged unless explicitly promoted.
   Phase112 SNAP-T1 now has paired executable-candidate scripts and a paired
   diagnostic execution with both conditions scoring 1.000; keep it
   diagnostic unless explicitly promoted.
4. During core reruns, collect auxiliary raw data where cheap: provider
   availability, failure reasons, context/token proxies, and raw rows needed
   for real-reuse LLM ablation.
5. Run broader verification gates before the next phase save:
   `check_real_reuse_benchmark.py`, `check_paper_tables.py`,
   `check_reproducibility_package.py`, `check_goal_completion.py`,
   `check_paper_claims.py`, `git diff --check`, and a raw-key scan.
6. Latest remote-backed checkpoint before further edits:
   `39c4e0f Record Claude availability push blocker`, verified at
   `39c4e0ff7a5d500d3250ea7f6dd177a00672fa95 refs/heads/main`. The latest
   substantive content checkpoint inside that chain remains `245c2b2 Prepare
   compact SNAP candidate prompts`: it adds the compact SNAP
   executable-candidate prompt contract and package/checker records, but does
   not call a model, score outputs, append raw rows, or replace main rows.
7. Earlier record-sync/blocker/Claude-availability transport failures recovered
   through the successful push and independent remote verification of
   `39c4e0f`; treat the earlier connection resets as GitHub transport metadata
   only.
8. No experiment-side human action is required for GitHub status right now.
   Continue non-network paper/evidence work and verify remote alignment again
   before claiming any later phase save is remote-backed.

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
