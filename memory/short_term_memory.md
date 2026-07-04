# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume. Also read
`memory/long_term_memory.md` before taking project actions.

Current date: 2026-07-04.

## Latest Resume/Completion Note

- 2026-07-04 Phase 104 Full Excerpt sanity scaffold: re-read long/short memory
  and workflow skills, confirmed `C:\Users\19351\Desktop\tem\ok.txt` absent,
  and closed the current E5.4 scaffold. Added
  `scripts/build_real_reuse_full_excerpt_sanity.py`,
  `tests/test_build_real_reuse_full_excerpt_sanity.py`, and
  `results/real_reuse/full_excerpt_sanity.{csv,md,json}` for AIDE-T1,
  SWE-T1, and SNAP-T1. Added `tab:full-excerpt-sanity` to the AAAI table file
  and a short setup paragraph in the AAAI draft. Extended paper-table and
  reproducibility-package gates, refreshed reports, and updated research docs,
  result cards, stage log, runbook, artifact map, goal audit, review handoff,
  rebuttal bank, claim matrix, long-term memory, and this file. Verification
  passed: focused 6 tests, full unit discovery 164 tests, strict paper-table,
  paper-claim, AAAI package, reproducibility-package, goal, submission-review,
  external-evidence, AAAI-decision, usage, DeepSeek, AI-Scientist-v2 handoff,
  and real-reuse checks; `git diff --check` had only Windows line-ending
  warnings; raw-key scan found no matches. Evidence boundary: Full Excerpt
  score cells remain pending, token counts are local whitespace context
  proxies, and this phase adds no task-success evidence.
- 2026-07-04 discussion sync: user asked whether the current experiment-table
  discussion requires modifying other parts of the original paper. Re-read
  memory and `C:\Users\19351\Desktop\tem\nextStep.md`, confirmed
  `C:\Users\19351\Desktop\tem\ok.txt` absent, and spot-checked the AAAI source
  and table files. Current conclusion: do not make new broad formal-paper
  edits now. The draft already states that the eight-row real-reuse first pass
  is mixed/failure-heavy boundary evidence, distinguishes reported reference
  scores from local reproduced scores, and keeps Full Excerpt as a pending
  sanity scaffold rather than a main baseline. Updated
  `C:\Users\19351\Desktop\tem\nextStep.md` with this answer.
- 2026-07-04 Phase 103 human-fidelity multi-reviewer protocol: re-read
  memory, confirmed `C:\Users\19351\Desktop\tem\ok.txt` absent, and audited
  the human-fidelity annotation path. Fixed a protocol mismatch where the
  handoff allowed 1-2 reviewers but the summarizer judged completion by raw CSV
  rows. `scripts/summarize_human_fidelity_annotations.py` now judges completion
  by 24 paper-by-criterion cells, reports `required_cells`, `scored_cells`, and
  `pending_cells`, allows distinct-reviewer duplicate rows for the same cell,
  rejects duplicate same-reviewer rows, and requires `needs_discussion`
  true/false on scored rows. Updated packet-builder guidance, the protocol
  config, external-evidence packet wording, package/submission-review gates,
  runbook, artifact map, goal audit, long-term memory, and
  `C:\Users\19351\Desktop\tem\toHuman.md`; regenerated human-fidelity packets,
  reviewer bundle, annotation summary, external-evidence packets, package
  report, goal-completion report, and submission-review report. Focused tests
  and strict gates passed. Human fidelity remains pending: 24 required cells,
  0 scored cells, 24 pending cells, 0 validation errors.
- 2026-07-04 Phase 102 submission-review real-reuse sync: re-read long/short
  memory, checked `C:\Users\19351\Desktop\tem\ok.txt` (absent), and reran the
  current goal/package/human-fidelity reports. Human fidelity remains pending
  with 0 scored rows and 24 pending cells; goal completion remains
  `not_complete_pending_external_evidence` with 77 ready / 3 pending / 0
  failed; package remains `ready_with_pending_external_evidence` with 423 ready
  / 1 pending / 0 failed. Synced `research/review_report.md`,
  `research/submission_checklist.md`, and `research/rebuttal_bank.md` so the
  submission-review handoff now reflects the eight-row real-reuse first pass,
  the failure-boundary table, the no-aggregate-effectiveness boundary, and the
  current package counts. Regenerated
  `results/reproducibility/submission_review_report.{json,md}` and added
  `research/run_logs/2026-07-04_phase102_submission_review_real_reuse_sync.md`.
  Strict checks passed for submission review, goal completion, reproducibility
  package, AAAI submission decision, external evidence closure, external
  evidence packets, and paper claims. This phase does not add task-success
  evidence and does not complete human annotation or final submission readiness.
- 2026-07-04 Phase 101 human-fidelity reviewer bundle: re-read memory,
  confirmed `ok.txt` absent, and found the repo aligned with `origin/main`
  except ignored local fixture/build files. Extended
  `scripts/build_human_fidelity_packets.py` so it now writes a reviewer
  quickstart, checksum manifest, and shareable
  `results/human_fidelity_packets/human_fidelity_reviewer_bundle.zip`
  containing the annotation guide, blank template, and four paper packets.
  Added package-gate checks and focused tests for the bundle, regenerated the
  bundle, updated `C:\Users\19351\Desktop\tem\toHuman.md` to point reviewers
  to the zip, and refreshed `scripts/check_reproducibility_package.py --strict`.
  Current package report is `ready_with_pending_external_evidence`, 423 ready,
  1 pending, 0 failed. Human fidelity remains pending: 0 scored rows, 24
  pending cells, no validation errors.
- 2026-07-04 human handoff refresh: after the Phase 100 backup, re-read
  memory, confirmed `ok.txt` absent, and verified the worktree was aligned with
  `origin/main` except ignored local fixture/build files. The existing
  `C:\Users\19351\Desktop\tem\toHuman.md` rendered as mojibake in the terminal,
  so it was rewritten as an ASCII handoff. It now clearly asks independent
  reviewers to fill
  `results/human_fidelity_packets/annotation_template.csv`, points to the
  annotation guide and four packet files, says not to turn unfinished rows into
  zeroes, and instructs the user to create
  `C:\Users\19351\Desktop\tem\ok.txt` when complete. Human fidelity remains
  pending until the strict summarizer reports all 24 paper-by-criterion cells
  scored with no errors.
- 2026-07-04 discussion sync: user asked whether the current discussion
  requires modifying other parts of the original paper. Re-read memory,
  confirmed `ok.txt` absent, inspected the current AAAI text/table/outline
  state, and updated `C:\Users\19351\Desktop\tem\nextStep.md`. Current answer:
  no broad rewrite is needed now. The formal draft already reflects the
  eight-row real-reuse first pass and the new failure-boundary table with
  cautious claims. Future paper edits should stay limited to consistency
  checks, evidence-boundary wording, and table/report synchronization unless
  repeated real-reuse evidence justifies stronger Abstract/Introduction/
  Conclusion claims or exposes a Method schema gap.
- 2026-07-04 Phase 100 real-reuse failure-boundary table: re-read memory,
  checked `ok.txt` (absent), and confirmed `main...origin/main` before edits.
  Added `scripts/build_real_reuse_failure_analysis.py`, generated
  `results/real_reuse/failure_analysis.{csv,md,json}`, and added tests in
  `tests/test_build_real_reuse_failure_analysis.py`. The table derives
  row-level boundary modes from the first eight-row GPT-family raw rows:
  AIDE-T1/T2 budget timeout, SWE-T1 patch application, SWE-T2
  PaperToSkill-only success, REF-T1/T2 solved by both, and SNAP-T1/T2 artifact
  completion. Added the table to `paper/aaai/papertoskill_tables.tex`, linked
  it in the AAAI Results paragraph, expanded `scripts/check_paper_tables.py`
  to verify it against the CSV, and added the new builder/artifacts to
  `check_reproducibility_package.py`. Updated outline/artifact map/claim
  matrix/runbook/rebuttal bank/result cards and rebuilt the AAAI PDF. Focused
  tests, `check_paper_tables.py --strict`, `check_paper_claims.py --strict`,
  `check_aaai_package.py --strict`, and `check_reproducibility_package.py
  --strict` passed before final full verification. Evidence boundary: this is
  explanatory failure-boundary analysis over existing raw rows, not new
  task-success evidence and not aggregate downstream effectiveness.
- 2026-07-04 Phase 99 real-reuse boundary wording cleanup: after the user asked
  whether other paper sections still needed modification, re-read memory,
  checked `C:\Users\19351\Desktop\tem\ok.txt` (absent), and verified
  `git status -sb` was aligned with `origin/main` before edits. Cleaned the
  generated real-reuse results boundary wording in
  `scripts/build_real_reuse_paper_tables.py` so `main_results_plan.md/json`
  no longer describe current unfilled cells as "pending cells" after all eight
  rows have one scored GPT-family pass. The new wording says score cells are
  generated from raw rows when available and future unfilled cells are planning
  placeholders, not task-success evidence. Added regression assertions in
  `tests/test_build_real_reuse_paper_tables.py` and regenerated
  `results/real_reuse/main_results_plan.md/json`. Focused table-builder tests,
  `check_paper_tables.py --strict`, `check_paper_claims.py --strict`, and
  `check_reproducibility_package.py --strict` passed before memory/log updates.
  This is wording/status hygiene only; it does not change scores or evidence
  boundaries.
- 2026-07-04 Phase 98 AIDE real-reuse completion and paper-sync: user
  provided the official Kaggle Spaceship Titanic `train.csv`, `test.csv`, and
  `sample_submission.csv` under
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\`; the
  `train.csv` has 8,693 rows and SHA256
  `17336D553F49EBDF6ECB266D2B5D3746E5DD308445F7C7864141C4F28D2A88D0`.
  AIDE-T1/T2 fixture assets were materialized, baseline scorer checks passed at
  about `0.4997124784358827`, and the GPT-family `gpt-5.5` AIDE run appended
  four scored rows: AIDE-T1 Summary/PaperToSkill `0.000/0.000` and AIDE-T2
  Summary/PaperToSkill `0.000/0.000`, all due `timeout after 60s`. The first
  single-run GPT-family real-reuse pass now covers all eight task rows:
  AIDE-T1/T2 `0.000/0.000`, SWE-T1 `0.000/0.000`, SWE-T2 `0.000/1.000`,
  REF-T1/T2 `1.000/1.000`, SNAP-T1 `0.000/0.500`, and SNAP-T2
  `0.200/0.400`. This is mixed/failure-heavy downstream evidence and does not
  establish aggregate PaperToSkill advantage over Summary. AAAI text, table
  caption, `paper/draft.md`, `paper/outline.md`, memory, result cards, and
  reports were synchronized to this evidence boundary. Strict gates passed,
  the AAAI PDF was rebuilt, full unit discovery passed 158 tests, `git
  diff --check` had only Windows line-ending warnings, and the raw-key scan had
  no matches. Kaggle-derived AIDE CSVs are intentionally ignored by git; hashes
  and manifests were committed. Phase backup commit `6885aaf Complete AIDE
  real reuse first pass` was pushed to `origin/main`; `git status -sb` reports
  `main...origin/main` with only ignored local fixture/cache files.
- 2026-07-04 Phase 97 cleanup/resume: read long-term and short-term memory
  after context continuation, checked `git status -sb`, and checked
  `C:\Users\19351\Desktop\tem\ok.txt`; no new `ok.txt` was present, so AIDE
  remains blocked on the official Kaggle Spaceship Titanic `train.csv` requested
  in `C:\Users\19351\Desktop\tem\toHuman.md`. Began Phase 97 cleanup by
  updating stale current-state docs that still described SWE-T1 as
  fixture-pending or SNAP rows as pending. Current real-reuse status remains:
  AIDE-T1/T2 `Awaiting dataset`; SWE-T1/SWE-T2, REF-T1/T2, and SNAP-T1/T2
  `Scored (GPT-family)`. SWE-T1 is failure-boundary evidence (0.000/0.000
  patch-apply failures), SWE-T2 is one positive single-task row (0.000/1.000),
  REF rows validate the runner/scorer/table path without Summary advantage, and
  SNAP rows are below threshold failure-boundary evidence. Phase 97 cleanup
  verification passed: refreshed strict goal/package/table/claim/real-reuse/
  AAAI/submission/usage/external-evidence/DeepSeek/AI-Scientist-v2 gates; rebuilt
  the AAAI PDF with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`; full unit
  discovery passed 158 tests; `git diff --check` reported only Windows
  line-ending warnings; raw-key scan found no matches. Phase backup committed as
  `26b474d Run SWE-T1 real reuse rows` and pushed successfully to `origin/main`
  (`997fce8..26b474d`). Current blocker remains AIDE-T1/T2 official Kaggle
  `train.csv`.
- 2026-07-03 Phase 97 SWE-T1 live rows: processed the active AIDE human
  handoff first. `ok.txt` existed, but no official Kaggle Spaceship Titanic
  `train.csv`, Kaggle CLI, Python `kaggle` package, `kaggle.json`, or
  `KAGGLE_USERNAME` / `KAGGLE_KEY` env vars were present. Rewrote
  `C:\Users\19351\Desktop\tem\toHuman.md` to ask again for official
  `train.csv` or local user-managed Kaggle setup, then deleted `ok.txt`.
  For SWE-T1, cloned `sqlfluff/sqlfluff` to
  `D:\a_work\gitee\sqlfluff__sqlfluff`, checked out locked base commit
  `14e1a23a3166b9a645a16de96f694c77a5d4abb7`, and created venv
  `D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625` with old-compatible
  SQLFluff dependencies plus editable SQLFluff install for plugin entry
  points. Extended `scripts/prepare_real_reuse_swe_fixture.py` to materialize
  fixtures directly from local SWE-bench parquet via `--swe-bench-parquet` and
  `--instance-id`; extended `scripts/score_real_reuse_swe.py` to add `src/`
  to `PYTHONPATH` and tolerate line-ending/space differences during
  `git apply`; added a parquet-backed preparer regression test. Materialized
  `benchmarks/real_reuse/assets/SWE-T1/` from
  `D:\a_work\gitee\SWE-bench_Lite\data\dev-00000-of-00001.parquet`, keeping
  gold/test patches under `scorer_only`. Gold scorer validation passed in
  `results/real_reuse/swe_t1_gold_metric.json` with `task_score=1.0` and
  hidden target pytest passed. Ran SWE-T1 with GPT-family `gpt-5.5`: first
  Summary attempt timed out twice and appended no raw row; PaperToSkill scored
  `0.000` with `patch_apply_failed`; a one-attempt Summary retry scored
  `0.000` with `patch_apply_failed`. Updated
  `results/real_reuse/main_results_plan.*`, `paper/aaai/papertoskill_tables.tex`,
  `paper/aaai/papertoskill_aaai2027.tex`, `research/claim_evidence_matrix.md`,
  `research/experiment_queue.md`, `research/artifact_map.md`,
  `research/runbook.md`, `paper/outline.md`, `results/result_cards.md`, and
  added `research/run_logs/2026-07-03_phase97_swe_t1_real_reuse_rows.md`.
  Current main real-reuse status: AIDE-T1/T2 `Awaiting dataset`, SWE-T1/SWE-T2
  `Scored (GPT-family)`, REF-T1/T2 `Scored (GPT-family)`, SNAP-T1/T2
  `Scored (GPT-family)` but SNAP remains below threshold. Evidence boundary:
  SWE-T1 is a real failed software-engineering row, not a PaperToSkill success
  and not aggregate SWE-agent effectiveness.
- 2026-07-03 Phase 96 SWE-T2 live rows: cleaned the accidental copied
  `benchmarks/real_reuse/assets/SWE-T2/workspace` directory and rematerialized
  SWE-T2 with `--workspace-mode external` pointing to
  `D:\a_work\gitee\astropy__astropy`. Fixed
  `scripts/score_real_reuse_swe.py` so relative candidate/test patch paths are
  resolved before scoring in the temporary workspace; focused SWE tests passed
  (8 tests). Gold scorer validation passed with `task_score=1.0`,
  `success=true`, hidden test patch applied, and 2/2 Astropy target tests
  passed. Ran `scripts/run_real_reuse_swe.py` with GPT-family `gpt-5.5` for
  SWE-T2 Summary and PaperToSkill. `results/real_reuse/swe_run_report.md`
  reports `complete` with two scored rows: Summary `0.000`
  (`patch_apply_failed`) and PaperToSkill `1.000` (patch applied and tests
  passed). Updated `results/real_reuse/main_results_plan.*`,
  `paper/aaai/papertoskill_tables.tex`, `paper/aaai/papertoskill_aaai2027.tex`,
  `research/claim_evidence_matrix.md`, `research/experiment_queue.md`,
  `research/artifact_map.md`, `research/goal_completion_audit.md`,
  `research/runbook.md`, `paper/outline.md`, `results/result_cards.md`, and
  `research/stage_log.md`; added
  `research/run_logs/2026-07-03_phase96_swe_t2_real_reuse_rows.md`. Current
  main real-reuse status: AIDE-T1/T2 `Awaiting dataset`, SWE-T1
  `Fixture pending`, SWE-T2 `Scored (GPT-family)`, REF-T1/T2
  `Scored (GPT-family)`, SNAP-T1/T2 `Scored (GPT-family)` but SNAP remains
  failure-boundary evidence below success threshold. Final local verification
  passed before commit: focused SWE fixture test passed, full unittest discovery
  passed 157 tests, all refreshed strict gates passed, `git diff --check`
  reported only Windows line-ending warnings, raw-key scan found no matches, and
  the internal SWE-T2 workspace is absent. Remaining phase action: commit and
  push.
- 2026-07-03 discussion sync: user again asked whether the current real-reuse
  experiment-design discussion requires modifying other parts of the original
  paper. Rechecked `paper/aaai/papertoskill_aaai2027.tex`,
  `paper/aaai/papertoskill_tables.tex`, and
  `results/real_reuse/main_results_plan.md`. Current conclusion: no immediate
  full-paper rewrite; only wording/status alignment is appropriate now.
  `Experimental Setup` already lists the eight real-reuse paper-tasks, and
  `Results` correctly treats REF/SNAP as partial GPT-family raw rows rather
  than completed aggregate effectiveness. SNAP remains failure-boundary
  evidence because both scored rows are below threshold. Updated
  `C:\Users\19351\Desktop\tem\nextStep.md` with this confirmation.
- 2026-07-03 discussion sync: user asked whether the current experiment-design
  discussion requires modifying other parts of the existing paper. Current
  answer: do not rewrite the whole AAAI manuscript now. Keep the cautious
  evidence boundary and do only wording/status alignment until more real-reuse
  rows exist. Current real-reuse status is AIDE `Awaiting dataset`, SWE-agent
  `Fixture pending`, REF `Scored (GPT-family)`, and SnapATAC2
  `Scored (GPT-family)`. SNAP-T1/T2 are scored GPT-family miniature-fixture
  rows where PaperToSkill is above Summary but all rows fail the success
  threshold, so they are failure-boundary evidence only. Updated
  `C:\Users\19351\Desktop\tem\nextStep.md` with this correction.
- 2026-07-03 Phase 95 SnapATAC2 live rows: retried `git push origin main` for
  Phase 94 but GitHub port 443 was unreachable. Then ran
  `scripts/run_real_reuse_snapatac2.py` with GPT-family `gpt-5.5` for
  SNAP-T1/SNAP-T2 Summary and PaperToSkill using the local GPT API doc loaded
  into process-local env vars only. `results/real_reuse/snapatac2_run_report.md`
  reports `complete` with four scored rows appended to
  `results/real_reuse/raw_rows.jsonl`. Scores: SNAP-T1 Summary 0.000,
  PaperToSkill 0.500; SNAP-T2 Summary 0.200, PaperToSkill 0.400. All SNAP rows
  failed the pre-registered success threshold due incomplete or malformed
  runtime/memory/quality artifacts. Updated `results/real_reuse/main_results_plan.*`,
  `paper/aaai/papertoskill_tables.tex`, `paper/aaai/papertoskill_aaai2027.tex`,
  claim/queue/audit/outline/artifact-map docs, `research/stage_log.md`, and
  `research/run_logs/2026-07-03_phase95_snapatac2_live_rows.md`. Evidence
  boundary: this is real GPT-family miniature-fixture failure-boundary evidence,
  not full SnapATAC2 paper reproduction or aggregate downstream success. AIDE
  still awaits Kaggle `train.csv`; SWE-agent still awaits fixture assets/raw
  rows.
- 2026-07-03 discussion sync: user asked whether the previously written paper
  sections need more changes under the current experiment-design discussion.
  Current answer: no full AAAI rewrite now. Keep the cautious evidence
  boundary; only do wording/status alignment until more real-reuse raw rows
  exist. The authoritative table statuses are AIDE `Awaiting dataset`,
  SWE-agent `Fixture pending`, Reflexion `Scored (GPT-family)`, and SnapATAC2
  `Ready to run` meaning prepared miniature fixture assets only, not scored
  task success. `C:\Users\19351\Desktop\tem\nextStep.md` was updated with this
  latest correction.
- 2026-07-03 Phase 94 SnapATAC2 fixture materialization is the current local
  phase before final commit/push: extended
  `scripts/prepare_real_reuse_snapatac2_fixture.py` with
  `official_miniature_fixture` mode, materialized SNAP-T1/T2 assets from the
  official local SnapATAC2 checkout at revision
  `7be57442708694217e27c8654ecd38a0de194aa4`, and added scorer-only thresholds
  plus a SNAP-T2 proxy-label policy. New assets live under
  `benchmarks/real_reuse/assets/SNAP-T1/` and
  `benchmarks/real_reuse/assets/SNAP-T2/`; summary contexts live under
  `baselines/real_reuse/SNAP-T1_summary.md` and
  `baselines/real_reuse/SNAP-T2_summary.md`. The copied official miniature
  fragments have SHA256 values
  `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`
  and `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`.
  `results/real_reuse/main_results_plan.{csv,md,json}` and the AAAI table now
  show SNAP-T1/T2 as `Ready to run`, with score cells still `Pending`.
  Current anchors: real-reuse preflight 462 ready / 0 failed; package 415
  ready / 1 pending / 0 failed; AAAI package ready 17 / 0; paper-table ready
  156 / 0. Full unit discovery passed with 155 tests and all strict local
  gates passed. Evidence boundary: this is SnapATAC2 fixture-readiness evidence
  only; no SNAP Summary/PaperToSkill rows were run, no SNAP raw rows were
  appended, and no SNAP task scores were added to the paper.
- 2026-07-03 Phase 93 SnapATAC2 execution layer is the previous local phase:
  added `scripts/prepare_real_reuse_snapatac2_fixture.py`,
  `scripts/score_real_reuse_snapatac2.py`, and
  `scripts/run_real_reuse_snapatac2.py`, plus focused tests and real-reuse /
  package gate integration. SNAP-T1/T2 table rows then showed `Fixture pending`
  with score cells still `Pending`. Historical anchors:
  `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 444 ready / 0 failed; package report reports 396 ready / 1 pending /
  0 failed; `paper/aaai/papertoskill_tables.tex` and the rebuilt AAAI PDF match
  the table source. Verification already passed before documentation cleanup:
  153 unit tests, all strict local gates, `git diff --check` with only Windows
  line-ending warnings, and raw-key scan with no matches. Evidence boundary:
  this is SnapATAC2 execution-layer readiness only; no SNAP fixture assets,
  raw rows, or downstream task-success evidence exist yet.
- 2026-07-03 Phase 92 SnapATAC2 skill gate is a previous verified local phase
  before commit/push: added the `snapatac2` auto-note profile, generated
  `papers/auto_notes/snapatac2_auto_note.md`,
  `generated_skills/real_reuse/snapatac2/SKILL.md`, source map,
  `benchmarks/rubric_snapatac2_v0.json`, source-span task, and evaluation
  reports. Added package/preflight/table integration and tests, normalized
  deterministic text extraction so `Nyström` becomes ASCII `Nystrom`, refreshed
  `results/real_reuse/main_results_plan.*`, updated
  `paper/aaai/papertoskill_tables.tex`, and rebuilt
  `paper/aaai/papertoskill_aaai2027.pdf`. Current anchors:
  `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 440
  ready / 0 failed; package report reports 392 ready / 1 pending / 0 failed;
  SNAP-T1/T2 rows now show `Runner pending` with score cells still `Pending`.
  This is SnapATAC2 skill/readiness evidence only: no SNAP runner, fixture
  assets, raw rows, or downstream task-success evidence exist yet. Full
  verification passed: 143 unit tests, all strict gates, `git diff --check`
  with only Windows line-ending warnings, and raw-key scan with no matches.
- 2026-07-03 discussion/state sync: user asked whether the original paper's
  other sections need changes under the new real-reuse plan. Local AAAI text
  check shows the current manuscript already has the key safety boundaries:
  `Experimental Setup` includes the eight-row real-reuse protocol, `Results`
  says REF-T1/REF-T2 are only one GPT-family partial slice, and it does not
  claim the full benchmark is complete or better than Summary. Current advice:
  do only small status/wording alignment now; do not rewrite `Abstract`,
  `Introduction`, or `Conclusion` into strong real-reuse claims until true
  AIDE/SWE/SNAP/REF raw rows exist. Keep old deterministic/offline experiments
  as quality/grounding/cost/readiness evidence, not downstream effectiveness.
  This conclusion was appended to
  `C:\Users\19351\Desktop\tem\nextStep.md`; the latest correction records
  SWE-agent as `Fixture pending` because its skill gate and execution layer
  exist. Phase 93 supersedes the earlier SnapATAC2 `Runner pending` note:
  SnapATAC2 now also has an execution layer, so its table status is
  `Fixture pending` until fixture assets/raw rows exist.
- 2026-07-03 discussion update: the next-step experiment plan now treats
  "original-style paper-task reuse" as the main future validity evidence. The
  user agreed with an 8-task direction across AIDE, SWE-agent, Reflexion, and
  one non-agent/data-analysis paper, with Toolformer and AI-Scientist-v2 kept as
  sanity/auxiliary cases. `C:\Users\19351\Desktop\tem\nextStep.md` is the live
  discussion record. Do not rewrite the AAAI Results as if these new real-reuse
  experiments are complete; first update planning files, then revise paper text
  after execution.
- 2026-07-03 Phase 90 SWE-agent skill gate is a previous local phase:
  final verification/commit: added the `swe_agent` auto-note profile, generated
  `papers/auto_notes/swe_agent_auto_note.md`,
  `generated_skills/real_reuse/swe_agent/SKILL.md`, and source map, added
  `benchmarks/rubric_swe_agent_v0.json` and
  `benchmarks/tasks/swe_agent_auto_source_span_validation.json`, and integrated
  the SWE-agent skill gate into real-reuse/package checks. Current results:
  rubric 20/20, 1186 words under the 1200-word budget, source-span 20/20
  supported with support_rate=1.0 and invalid_ranges=0. Updated
  `results/real_reuse/main_results_plan.*` reports AIDE rows as
  `Awaiting dataset`, SWE rows as `Runner pending`, REF rows as
  `Scored (GPT-family)`, and SNAP rows as `Skill pending`. This is
  skill/readiness evidence only: no SWE assets, runner, raw rows, or paper
  score cells exist yet. Full verification passed before phase save: 133 unit
  tests, all strict gates, `git diff --check` with only line-ending warnings,
  and raw-key scan with no matches. AIDE `ok.txt` and the real Kaggle
  `train.csv` were still missing during verification.
- 2026-07-03 Phase 88 AIDE real-reuse execution layer is now a previous local
  phase: added `scripts/prepare_real_reuse_aide_fixture.py`,
  `scripts/score_real_reuse_aide.py`, and `scripts/run_real_reuse_aide.py`;
  added AIDE tests for fixture preparation, scorer-only hidden label
  separation, isolated candidate scoring, fixture-response runner execution,
  missing-credential pending behavior, and prompt/hidden-label separation.
  The targeted AIDE/preflight/package test set passed 17 tests; full unit
  discovery passed 131 tests; all strict local gates passed; `git diff --check`
  returned only line-ending warnings; and the raw-key scan produced no matches.
  Strict gates report `results/real_reuse/spec_preflight.md` as
  `ready_to_implement` with 424 ready / 0 failed checks and
  `results/reproducibility/package_report.md` as
  `ready_with_pending_external_evidence` with 376 ready / 1 pending / 0 failed.
  This is execution-layer readiness only: no AIDE fixture assets, raw rows, or
  paper scores exist until the real Kaggle Spaceship Titanic `train.csv` is
  provided. `C:\Users\19351\Desktop\tem\ok.txt` and
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\train.csv`
  were missing in the latest check; the active human request is
  `C:\Users\19351\Desktop\tem\toHuman.md`.
- 2026-07-03 Phase 89 remote save recovered the earlier GitHub HTTPS push
  blocker: `git push origin main` succeeded for the Phase 87/88 stack and the
  follow-up remote-save record was also pushed. `git status -sb` is the
  authoritative check for the latest exact remote alignment. The remote now
  contains Phase 87 REF real-reuse rows, the Phase 87 push-blocker note, and
  the Phase 88 AIDE execution-layer commit.
- 2026-07-03 Phase 87 real-reuse Reflexion runner/execution is now a previous
  local phase: added `scripts/run_real_reuse_reflexion.py`, fixed REF-T1
  yes/no scoring for explanatory final answers, ran REF-T1/REF-T2 Summary and
  PaperToSkill with GPT-family `gpt-5.5`, and saved 4 scored raw rows under
  `results/real_reuse/raw_rows.jsonl`. `results/real_reuse/reflexion_run_report.md`
  reports `complete`; REF-T1 and REF-T2 Summary and PaperToSkill all score
  1.000. `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex` now fill the two REF rows while AIDE,
  SWE-agent, and SnapATAC2 remain pending. This is partial REF-slice evidence
  only: it validates the runner/scorer/table path but does not show
  PaperToSkill advantage over Summary or complete the eight-task benchmark.
- 2026-07-03 Phase 87 local backup was committed as
  `9261bfc feat: run reflexion real reuse rows`; its initial push was blocked
  by GitHub HTTPS connectivity, but Phase 89 later pushed it successfully as
  part of the recovered remote-save stack.
- 2026-07-03 Phase 86 real-reuse Reflexion preparer/scorer is now a previous
  local phase: added `scripts/prepare_real_reuse_reflexion_fixture.py` and
  `scripts/score_real_reuse_reflexion.py`; materialized REF-T1 HotPotQA-style
  assets and REF-T2 HumanEval-style assets under
  `benchmarks/real_reuse/assets/REF-T1` and `REF-T2`; created
  `baselines/real_reuse/REF-T1_summary.md` and `REF-T2_summary.md`; extended
  the real-reuse preflight and package gate. `results/real_reuse/spec_preflight.md`
  reports `ready_to_implement`, 8 tasks, 418 ready checks, 0 failed checks.
  `results/reproducibility/package_report.md` reports 368 ready / 1 pending /
  0 failed. This setup evidence was extended by Phase 87, which added the REF
  runner and created the first REF raw rows.
- 2026-07-03 active-goal update: prioritize the main real-reuse experiment over
  auxiliary experiments. The paper's experiment section should get the main
  table structure first, with TBD/pending numeric cells and explicit evidence
  boundary; after scores are run, update the paper numbers promptly.
- 2026-07-03 Phase 85 asset-lock gate is a previous local phase: added
  `scripts/build_real_reuse_asset_locks.py`, generated all eight
  `benchmarks/real_reuse/asset_locks/*.json` files, corrected the SnapATAC2 API
  candidate URL to `https://scverse.org/SnapATAC2/api/index.html`, extended
  `scripts/check_real_reuse_benchmark.py` and package expectations, and
  validated `results/real_reuse/spec_preflight.md` as `ready_to_implement`
  with 401 ready checks and 0 failed checks. Locked instances include
  Spaceship Titanic split/weak-script seeds for AIDE, SWE-bench Lite
  `sqlfluff__sqlfluff-1625`, SWE-bench Verified `astropy__astropy-12907`,
  HotPotQA example `5a8b57f25542995d1e6f1371`, HumanEval `HumanEval/0`, and
  SnapATAC2 `pbmc5k` / `pbmc10k_multiome`. This phase was setup evidence
  only. Later Phase 86 prepared REF assets/scorers and Phase 87 ran REF rows;
  AIDE, SWE-agent, and SnapATAC2 execution remains pending.
- 2026-07-03 Phase 84 paper-table gate is a previous local phase: added
  `scripts/build_real_reuse_paper_tables.py`, generated
  `results/real_reuse/main_results_plan.{csv,md}`, inserted
  `Table~\ref{tab:real-reuse-main}` into `paper/aaai/papertoskill_tables.tex`,
  updated the AAAI Experimental Setup/Results boundary text, extended
  `scripts/check_paper_tables.py` to validate the real-reuse table against the
  CSV, and rebuilt `paper/aaai/papertoskill_aaai2027.pdf`. This phase was not
  execution evidence; Phase 87 later filled only the REF-T1/REF-T2 cells.
- 2026-07-03 Phase 83 fixture-candidate gate is the previous local phase:
  added `scripts/build_real_reuse_fixture_candidates.py` and generated the eight
  `benchmarks/real_reuse/fixture_candidates/*.json` manifests. Candidate
  sources are MLE-bench/Spaceship Titanic for AIDE-T1/T2, SWE-bench
  Lite/Verified for SWE-T1/T2, HotPotQA and HumanEval for REF-T1/T2, and
  SnapATAC2 official tutorial/API-backed assets for SNAP-T1/T2. The real-reuse
  preflight now reports `ready_to_implement`, 8 tasks, 296 ready checks, and 0
  failed checks; package gate reports 339 ready / 1 pending / 0 failed. This is
  still not execution evidence: assets are not materialized, preparer/scorer
  scripts and runner were not implemented at that phase. Phase 87 later added
  REF raw rows only; AIDE, SWE-agent, and SnapATAC2 remain pending.
- 2026-07-03 Phase 82 fixture-manifest gate is the previous local phase:
  added `scripts/build_real_reuse_fixture_manifests.py` and generated the eight
  `benchmarks/real_reuse/fixtures/*.json` manifests. The real-reuse preflight
  now validates fixture identity, status, asset slots, context conditions,
  metric alignment, no-mid-run-human rule, and license/provenance boundary; it
  reports `ready_to_implement`, 8 tasks, 207 ready checks, and 0 failed checks.
  This was still not execution evidence at that phase. Phase 87 later added
  REF raw rows only; AIDE, SWE-agent, and SnapATAC2 remain pending.
- 2026-07-03 Phase 81 task-spec gate was the previous local phase: added
  `scripts/build_real_reuse_task_specs.py` and generated the eight
  `benchmarks/real_reuse/tasks/*.json` per-task execution-contract specs. The
  real-reuse preflight now validates task-spec identity, conditions, metric
  contracts, raw-row schema, and no-mid-run-human rule; it reports
  `ready_to_implement`, 8 tasks, 142 ready checks, and 0 failed checks. This
  was not execution evidence at that phase. Phase 87 later added REF raw rows
  only; AIDE, SWE-agent, and SnapATAC2 remain pending.
- 2026-07-03 Phase 80 spec gate was committed and pushed as
  `bdd39cc test: add real reuse benchmark preflight`: added
  `benchmarks/real_reuse/real_reuse_v0.json`,
  `scripts/check_real_reuse_benchmark.py`,
  `tests/test_check_real_reuse_benchmark.py`, and
  `results/real_reuse/spec_preflight.{json,md}`. The preflight reports
  `ready_to_implement`, 8 tasks, and initially 85 ready checks before Phase 81
  task-spec validation.
- 2026-07-03 Phase 79 planning sync completed locally: added
  `research/real_reuse_experiment_plan.md`; updated `paper/outline.md`,
  `research/experiment_queue.md`, `research/claim_evidence_matrix.md`,
  `research/goal_completion_audit.md`, `research/runbook.md`,
  `research/artifact_map.md`, `research/stage_log.md`, and
  `research/run_logs/2026-07-03_phase79_real_reuse_planning.md`. This is
  planning only; no `results/real_reuse/` evidence exists yet.
- Phase 79 planning was committed as `cd14dbf docs: plan real reuse
  experiments` and pushed to `origin/main` on 2026-07-03. A first push attempt
  failed because GitHub 443 was unreachable from the sandbox; the approved
  external-network retry succeeded.
- 2026-07-02 Phase 77 final sync completed after reviewing the added papers and
  API docs.
- New-papers decision remains unchanged after verification:
  - Paper2Agent: closest competing work; cite and compare through the bounded
    artifact/workflow table.
  - AgenticSciML: adjacent related work; cite, no immediate experiment.
  - Reasoning Manifolds: future non-procedural stress case; no current main
    experiment.
- API docs at
  `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument` were re-read:
  GPT uses OpenAI Responses (`/v1/responses`), Claude uses Anthropic Messages
  (`/v1/messages`), and DeepSeek uses Chat Completions (`/chat/completions`).
- Corrected stale AAAI decision/claim wording so the project no longer waits
  for AI-Scientist-v2 smoke/full live evidence; that bounded evidence is
  complete but remains only integration/synthetic sensitivity evidence.
- Rebuilt `paper/aaai/papertoskill_aaai2027.pdf` after paper-facing wording
  changes and added LaTeX temporary build files to `.gitignore`.
- Verification passed:
  `python -m unittest discover -s tests -v` (96 tests),
  all strict local gates, `git diff --check`, and repository raw-key scan.
- Current reports:
  - Goal completion: 77 ready / 3 pending / 0 failed.
  - Reproducibility package: 376 ready / 1 pending / 0 failed after adding the
    AIDE real-reuse execution layer.
  - External evidence queue: `human_fidelity_annotation` and
    `aaai_submission_decision`.
  - AAAI decision: ready, selected `wait_for_external_evidence`.
- `C:\Users\19351\Desktop\tem\toHuman.md` currently asks the user for the
  Kaggle Spaceship Titanic `train.csv` needed to materialize AIDE-T1/T2
  fixtures. No `ok.txt` was present in the latest check.
- 2026-07-02 Phase 78 archived the local `ai-scientist-v2` source/config
  adaptations as a PaperToSkill artifact because that checkout's remote is the
  SakanaAI upstream, not the user's PaperToSkill repo. Archive path:
  `external/ai_scientist_v2_patches/2026-07-02_local_coderxiaoc_bfts_adaptation.patch.zip`.
  Archive SHA256:
  `2CEA03F4C8870FFB0F686B12320D413794BF24B983C5DCEA2BA4D96FFC1E7371`;
  decompressed patch SHA256:
  `45523E06C70D33C0F6B2FB769CD26D3701EF397B07D02DFBF781DA85ECEF7AF1`.
  This preserves the local integration state without committing raw API keys,
  `work/` presentation artifacts, or upstream memory files.

## Current Presentation Handoff

- Latest PPT for the doctoral progress report is saved at
  `C:\Users\19351\Desktop\tem\PaperToSkill_博士生阶段进展汇报.pptx`.
- The latest revision directly answers the user's workflow questions:
  - Slide 8 is the real operational workflow. It now states that left-to-right
    is only the main path and shows that failed gates, missing evidence, or
    provider failures return to earlier steps instead of silently passing.
  - Slide 10 is the engineering implementation map. It explains each Slide 8
    step in beginner-friendly language with the local script/action, output,
    and failure check.
- Keep the verbal distinction short in future responses: Slide 8 explains what
  happens to a paper in actual operation; Slide 10 explains which local scripts,
  files, and checks implement that operation.
- Do not describe the real workflow as a one-way pipeline.
- 2026-06-30 verification: both local interface docs in `C:\Users\19351\Desktop\tem`
  are runnable. GPT doc (`gpt-5.5`, `gpt-5.4`) returned HTTP 200 on the first
  attempt via `POST https://coderxiaoc.com/v1/responses`. Claude doc
  (`claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`) returned HTTP 200
  on the first attempt via `POST https://coderxiaoc.com/v1/messages`.
- 2026-07-01 re-test: GPT and DeepSeek docs are currently runnable, while the
  Claude doc did not succeed as direct HTTP this time.
  - GPT doc: `gpt-5.5` returned HTTP 200 on attempt 2 and `gpt-5.4` returned
    HTTP 200 on attempt 1 via `POST https://coderxiaoc.com/v1/responses`.
  - DeepSeek doc: `deepseek-v4-flash` and `deepseek-v4-pro` both returned
    HTTP 200 on attempt 1 via
    `POST https://api.deepseek.com/chat/completions`.
  - Claude doc: `claude-opus-4-8`, `claude-opus-4-7`, and
    `claude-opus-4-6` returned HTTP 502 after five attempts via
    `POST https://coderxiaoc.com/v1/messages` with both the regular doc key
    (`sk-c83d...cad7`) and Desktop token (`sk-6477...000e`). This indicates
    current upstream/direct-request unavailability, not a model-name proof.
- 2026-07-01 same-day Claude-only re-test:
  - Regular Claude doc key (`sk-c83d...cad7`) worked for `claude-opus-4-8`,
    `claude-opus-4-7`, and `claude-opus-4-6` via
    `POST https://coderxiaoc.com/v1/messages`; all returned HTTP 200 on
    attempt 1 and visible `ok`.
  - The same regular key also worked for all three models with the
    Claude Code/Desktop beta header.
  - Desktop token (`sk-6477...000e`) still returned HTTP 502 after five
    attempts for all three models.
  - Current answer: Claude doc is runnable with the regular API key; Desktop
    token is not currently runnable by naked direct HTTP.
- 2026-07-01 update after the latest handoff:
  - Local token accounting now replaces provider-billing evidence for the
    current project state.
  - `results/token_accounting/token_accounting_summary.md` reports 4,322
    generated-skill input tokens, 95,303 full-extracted input tokens, 9,594
    saved-response output tokens, and 13,916 composite local token proxy.
  - The AAAI submission decision has been recorded as
    `wait_for_external_evidence`.

## Current Phase

Phase 94 is the current local phase before final commit/push.
Phase 68 was committed as
`5548070 Refresh memory anchors after remote save` and pushed to `origin/main`
on 2026-06-20. Phase 69 syncs the AAAI submission-decision execution packet
with the validated decision-record helper; no external evidence status is
promoted and no AAAI option is selected. Phase 70 updates the direct provider
diagnostic to match the current coderxiaoc API protocols: Claude uses
Anthropic Messages and GPT uses OpenAI Responses.

Phase 94 evidence:

- `scripts/prepare_real_reuse_snapatac2_fixture.py` supports
  `--materialization-mode official_miniature_fixture` with
  `--snapatac2-root`.
- SNAP-T1 copies official local SnapATAC2
  `tests/test_tools/test_single.tsv.gz` into
  `benchmarks/real_reuse/assets/SNAP-T1/miniature_fragment.tsv.gz`; SHA256 is
  `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`.
- SNAP-T2 copies official local SnapATAC2
  `tests/test_tools/test_clean.tsv.gz` into
  `benchmarks/real_reuse/assets/SNAP-T2/miniature_fragment.tsv.gz`; SHA256 is
  `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`.
- Dataset manifests record SnapATAC2 revision
  `7be57442708694217e27c8654ecd38a0de194aa4`, MIT license provenance,
  official dataset references, tutorial LFS OIDs, copied-file checksums, and
  the boundary that these are miniature smoke fixtures, not full paper-dataset
  reproductions.
- `scripts/score_real_reuse_snapatac2.py` now reads scorer-only
  `scorer_thresholds.json` and applies the hidden success threshold.
- `scripts/check_real_reuse_benchmark.py` validates prepared SNAP assets; the
  preflight reports 462 ready checks and 0 failed checks.
- `results/reproducibility/package_report.md` reports
  `ready_with_pending_external_evidence`, 415 ready checks, 1 pending check,
  and 0 failed checks.
- `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex` now report SNAP-T1/T2 as
  `Ready to run`, with score cells still `Pending`.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after status text/table
  updates.
- Verification passed: 155 unit tests and all strict local gates. Final
  `git diff --check` and raw-key scan still need to run immediately before
  commit.
- This is SnapATAC2 fixture-readiness evidence only; no SNAP Summary or
  PaperToSkill rows were run, no SNAP raw rows were appended, and no SNAP task
  scores were added to the paper.

Phase 93 evidence:

- `scripts/prepare_real_reuse_snapatac2_fixture.py` prepares locked SNAP-T1/T2
  fixture assets from declared SnapATAC2 dataset manifests and expected
  artifact schemas while keeping labels/metric thresholds scorer-only.
- `scripts/score_real_reuse_snapatac2.py` scores candidate analysis artifacts
  against runtime/memory/resource contracts and ARI/NMI-style labels/proxies
  when available.
- `scripts/run_real_reuse_snapatac2.py` runs locked SNAP-T1/T2 Summary and
  PaperToSkill conditions, saves prompts/responses/metrics/raw rows when
  scorable, and records missing fixture assets/provider availability separately
  from model quality.
- Focused SnapATAC2 preparer/scorer/runner tests exist and passed with the
  table/preflight/package test set; full unit discovery passed with 153 tests
  before documentation cleanup.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 444 ready checks, and 0 failed checks after validating the SnapATAC2
  execution-layer contract.
- `results/reproducibility/package_report.md` reports 396 ready / 1 pending /
  0 failed after adding the SnapATAC2 execution-layer artifacts.
- `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex` now report SNAP-T1/T2 as
  `Fixture pending`, with score cells still `Pending`.
- Full verification passed before documentation cleanup: 153 unit tests, all
  strict gates, no raw-key matches, and only Windows line-ending warnings from
  `git diff --check`.
- This is SnapATAC2 execution-layer readiness only; no SnapATAC2 fixture
  assets, raw rows, or downstream task-success evidence exist yet.

Phase 92 evidence:

- `scripts/papertoskill_note_from_text.py` now has a `snapatac2` profile for
  extracting SnapATAC2 matrix-free spectral embedding workflow, benchmarking
  metrics, transfer settings, and limitations from
  `papers/extracted/snapatac2.txt`.
- The auto-note path now uses Unicode normalization before ASCII conversion,
  so extracted names such as `Nyström` become stable ASCII `Nystrom` instead
  of losing the `o`.
- `papers/auto_notes/snapatac2_auto_note.md`,
  `generated_skills/real_reuse/snapatac2/SKILL.md`, and
  `generated_skills/real_reuse/snapatac2/references/source_map.json` exist.
- `results/evaluations/snapatac2_rubric_v0.json` reports 20/20 and 1091
  words under the 1200-word budget.
- `results/evaluations/snapatac2_auto_source_span_validation_v0.json` reports
  18/18 supported claims, support_rate=1.0, and 0 invalid ranges.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 440 ready checks, and 0 failed checks after validating the SnapATAC2
  skill gate.
- `results/reproducibility/package_report.md` reports 392 ready / 1 pending /
  0 failed after adding the SnapATAC2 readiness artifacts.
- `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex` now report SNAP-T1/T2 as
  `Runner pending`, with score cells still `Pending`.
- Full verification passed before phase save: 143 unit tests, all strict
  gates, no raw-key matches, and only Windows line-ending warnings from
  `git diff --check`.
- This is SnapATAC2 skill/readiness evidence only; no SnapATAC2 runner,
  fixture assets, raw rows, or downstream task-success evidence exist yet.
- Phase 93 supersedes the Phase 92 SNAP status by adding the SnapATAC2
  preparer/scorer/runner and moving table rows to `Fixture pending`.

Phase 91 evidence:

- `scripts/prepare_real_reuse_swe_fixture.py` prepares locked SWE-T1/T2
  fixture assets from a local repo snapshot, issue/failing-test context, and a
  locked test command. Any gold patch is scorer-only and hidden from
  model-visible context.
- `scripts/score_real_reuse_swe.py` scores candidate unified diff patches by
  applying them in an isolated temporary workspace and running the locked test
  command.
- `scripts/run_real_reuse_swe.py` runs locked SWE Summary/PaperToSkill
  conditions, supports fixture responses for dry tests, saves scored raw rows
  only when output is scorable, and records missing fixture assets, missing
  credentials, or provider errors as availability state.
- Targeted SWE/table/preflight/package tests passed: 18 tests.
- `results/real_reuse/main_results_plan.{csv,md,json}` and
  `paper/aaai/papertoskill_tables.tex` now report SWE-T1/T2 as
  `Fixture pending` with score cells still `Pending`.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 434 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports 381 ready / 1 pending /
  0 failed.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after the table update.
- This is SWE execution-layer readiness only: no SWE fixture asset manifests,
  no SWE raw rows, and no SWE downstream task-success evidence exist yet.

Phase 90 evidence:

- `scripts/papertoskill_note_from_text.py` now has a `swe_agent` profile for
  extracting SWE-agent's ACI workflow, SWE-bench validation setup, ablation
  details, and limitations from `papers/extracted/swe_agent.txt`.
- `papers/auto_notes/swe_agent_auto_note.md`,
  `generated_skills/real_reuse/swe_agent/SKILL.md`, and
  `generated_skills/real_reuse/swe_agent/references/source_map.json` exist.
- `results/evaluations/swe_agent_rubric_v0.json` reports 20/20 and 1186 words.
- `results/evaluations/swe_agent_auto_source_span_validation_v0.json` reports
  20/20 supported claims, support_rate=1.0, and 0 invalid ranges.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 430 ready checks, and 0 failed checks after validating the SWE-agent
  skill gate.
- `results/reproducibility/package_report.md` reports 377 ready / 1 pending /
  0 failed after adding the SWE-agent readiness artifacts.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after the table status
  update; the AAAI package gate is ready with 17 ready / 0 failed checks.
- Full verification passed before phase save: 133 unit tests, all strict gates,
  no raw-key matches, and only Windows line-ending warnings from
  `git diff --check`.
- This is SWE-agent skill/readiness evidence only; SWE-bench fixture assets,
  scorer, runner, raw rows, and paper scores remain pending.

Phase 89 evidence:

- `git push origin main` succeeded after the earlier GitHub HTTPS blocker.
- Remote save recovered: the Phase 87/88 stack and the follow-up remote-save
  record were pushed to `origin/main`.
- The pushed state contains the Phase 87 REF runner/raw rows, the Phase 87
  push-blocker note, and the Phase 88 AIDE execution-layer commit.
- This is remote-save evidence only; it does not clear the AIDE Kaggle-data
  blocker or complete the eight-task real-reuse benchmark.

Phase 88 evidence:

- `scripts/prepare_real_reuse_aide_fixture.py` prepares locked AIDE-T1/T2
  fixture assets from a real Kaggle-style `train.csv`, writes model-visible
  train/validation feature assets and Summary contexts, and keeps
  `validation_labels.csv` scorer-only.
- `scripts/score_real_reuse_aide.py` scores AIDE submissions or candidate
  scripts against hidden validation labels, including isolated temporary
  workspace execution for candidate scripts.
- `scripts/run_real_reuse_aide.py` runs locked AIDE Summary/PaperToSkill
  conditions, saves prompts/responses/metrics/raw rows when rows are scorable,
  and records missing credentials/provider errors as availability state.
- Targeted AIDE/preflight/package tests passed: 17 tests.
- Full unit discovery passed: 131 tests.
- All strict local gates passed; `git diff --check` returned only line-ending
  warnings, and the raw-key scan produced no matches.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 424 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports 376 ready / 1 pending /
  0 failed.
- AIDE remains data-blocked for real fixture materialization: no Kaggle
  `train.csv`, no AIDE asset manifests, no AIDE raw rows, and no AIDE table
  score cells exist yet.

Phase 87 evidence:

- `scripts/run_real_reuse_reflexion.py` runs locked REF-T1/REF-T2 Summary and
  PaperToSkill conditions, saves prompts/responses/metrics, appends scored raw
  rows, and reports provider/model errors as availability evidence rather than
  model-quality failures.
- REF-T1 and REF-T2 were run once with GPT-family `gpt-5.5` through OpenAI
  Responses using shell-only credentials from the local API docs.
- `results/real_reuse/reflexion_run_report.md` reports `complete` with 4
  scored rows; `results/real_reuse/raw_rows.jsonl` contains the corresponding
  raw rows.
- REF-T1 Summary = 1.000, REF-T1 PaperToSkill = 1.000, REF-T2 Summary = 1.000,
  and REF-T2 PaperToSkill = 1.000.
- `scripts/score_real_reuse_reflexion.py` now treats explanatory yes/no
  final-answer text as correct when the leading normalized label matches the
  hidden answer key; EM/F1 fields are still preserved in the metric JSON.
- `scripts/build_real_reuse_paper_tables.py` now fills
  `results/real_reuse/main_results_plan.{csv,md,json}` from raw rows.
- `paper/aaai/papertoskill_tables.tex` and `paper/aaai/papertoskill_aaai2027.tex`
  now report the REF partial scores and explicitly say the result does not
  complete the eight-task benchmark or establish an advantage over Summary.
- AIDE, SWE-agent, and SnapATAC2 assets/raw rows were pending at Phase 87; Phase
  88 superseded this for AIDE execution-layer scripts only. AIDE data/assets/raw
  rows remain pending.

Phase 86 evidence:

- `scripts/prepare_real_reuse_reflexion_fixture.py` materializes locked REF-T1
  and REF-T2 fixture assets, task prompts, task-specific Summary condition
  contexts, and hidden scorer-only assets.
- `scripts/score_real_reuse_reflexion.py` scores REF-T1 predictions with EM/F1
  against `answer_key.json` and REF-T2 candidates with the hidden HumanEval
  checker.
- REF-T1 assets are under `benchmarks/real_reuse/assets/REF-T1/` and include
  question, retrieval context/tool stub, feedback protocol, task prompt, hidden
  answer key, and `asset_manifest.json`.
- REF-T2 assets are under `benchmarks/real_reuse/assets/REF-T2/` and include
  initial task, failed first attempt, environment feedback, task prompt, hidden
  tests/canonical solution, and `asset_manifest.json`.
- Task-specific Summary contexts exist at
  `baselines/real_reuse/REF-T1_summary.md` and
  `baselines/real_reuse/REF-T2_summary.md`.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 418 ready checks, and 0 failed checks after validating prepared REF
  assets.
- `results/reproducibility/package_report.md` reports 368 ready / 1 pending /
  0 failed after including the REF preparer/scorer and prepared assets.
- At the end of Phase 86 no Summary or PaperToSkill model condition had been
  executed and no raw rows existed; this was superseded by Phase 87, which ran
  the REF rows and filled their table cells.

Phase 85 evidence:

- `scripts/build_real_reuse_asset_locks.py` materializes preparation-time asset
  locks from task specs, fixture manifests, and candidate manifests.
- `benchmarks/real_reuse/asset_locks/AIDE-T1.json`, `AIDE-T2.json`,
  `SWE-T1.json`, `SWE-T2.json`, `REF-T1.json`, `REF-T2.json`,
  `SNAP-T1.json`, and `SNAP-T2.json` exist.
- Locked task instances: Spaceship Titanic local validation split seed
  `20260703`, Spaceship Titanic weak-script seed `20260703`, SWE-bench Lite
  `sqlfluff__sqlfluff-1625`, SWE-bench Verified `astropy__astropy-12907`,
  HotPotQA distractor validation `5a8b57f25542995d1e6f1371`, HumanEval
  `HumanEval/0`, SnapATAC2 `snapatac2.datasets.pbmc5k`, and SnapATAC2
  `snapatac2.datasets.pbmc10k_multiome`.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 401 ready checks, and 0 failed checks after validating asset locks.
- `results/reproducibility/package_report.md` reports 351 ready / 1 pending /
  0 failed after including the asset-lock builder and all eight lock manifests.
- At this phase, no fixture asset had been materialized and no task-specific
  runner/scorer or raw row existed. Phase 86/87 superseded this for REF-T1 and
  REF-T2 only; next implementation should materialize/run AIDE, SWE-agent, or
  SnapATAC2 rows.

Phase 84 evidence:

- `scripts/build_real_reuse_paper_tables.py` materializes the paper-facing
  main real-reuse table scaffold from `benchmarks/real_reuse/real_reuse_v0.json`.
- `results/real_reuse/main_results_plan.csv` and `.md` exist.
- `paper/aaai/papertoskill_tables.tex` includes
  `Table~\ref{tab:real-reuse-main}` with eight task rows and pending
  Summary/PaperToSkill score cells.
- `scripts/check_paper_tables.py` validates the real-reuse table against
  `results/real_reuse/main_results_plan.csv`; the report is ready with 156
  checks and 0 failed checks.
- `paper/aaai/papertoskill_aaai2027.pdf` was rebuilt after the table update.
- `results/reproducibility/package_report.md` reports 342 ready / 1 pending /
  0 failed.
- Next implementation should not expand auxiliary experiments first; materialize
  the main real-reuse assets, implement preparers/scorers and runner, run raw
  rows, then update the pending score cells.

Phase 83 evidence:

- `scripts/build_real_reuse_fixture_candidates.py` materializes all eight
  selected candidate asset/preparation manifests from task specs and fixture
  manifests.
- `benchmarks/real_reuse/fixture_candidates/AIDE-T1.json`, `AIDE-T2.json`,
  `SWE-T1.json`, `SWE-T2.json`, `REF-T1.json`, `REF-T2.json`,
  `SNAP-T1.json`, and `SNAP-T2.json` exist.
- Candidate sources are MLE-bench/Spaceship Titanic for AIDE-T1/T2, SWE-bench
  Lite/Verified for SWE-T1/T2, HotPotQA and HumanEval for REF-T1/T2, and
  SnapATAC2 official tutorial/API-backed assets for SNAP-T1/T2.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 296 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reported 339 ready / 1 pending /
  0 failed after including the candidate builder and all eight manifests.
- No fixture asset has been materialized; no external dataset/repo has been
  downloaded for execution; no preparer/scorer, runner, raw row, or main result
  artifact exists yet. Next implementation should materialize selected assets,
  fix instance IDs, then implement the runner/scorer.

Phase 82 evidence:

- `scripts/build_real_reuse_fixture_manifests.py` materializes all eight
  fixture requirement manifests from the per-task specs.
- `benchmarks/real_reuse/fixtures/AIDE-T1.json`, `AIDE-T2.json`, `SWE-T1.json`,
  `SWE-T2.json`, `REF-T1.json`, `REF-T2.json`, `SNAP-T1.json`, and
  `SNAP-T2.json` exist.
- Each fixture manifest records source alignment, required asset slots,
  Summary/PaperToSkill context assets, execution budget slots, scoring
  contract, license/provenance status, and planned outputs.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 207 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reported 330 ready / 1 pending /
  0 failed after including the fixture builder and all eight manifests.
- At this phase, no concrete fixture asset, scoring command, runner/scorer,
  raw row, or main result artifact existed. Phase 87 superseded this for the
  REF slice only; AIDE, SWE-agent, and SnapATAC2 still need executable assets,
  scorers, runners, and raw rows.

Phase 81 evidence:

- `scripts/build_real_reuse_task_specs.py` materializes all eight per-task
  execution-contract specs from the master spec.
- `benchmarks/real_reuse/tasks/AIDE-T1.json`, `AIDE-T2.json`, `SWE-T1.json`,
  `SWE-T2.json`, `REF-T1.json`, `REF-T2.json`, `SNAP-T1.json`, and
  `SNAP-T2.json` exist.
- Each task spec records input/output contract, Summary and PaperToSkill
  condition paths, metric contract, reference-score policy, run controls,
  workflow checklist, unsupported-error policy, raw-row schema, and artifact
  paths.
- `results/real_reuse/spec_preflight.md` reports `ready_to_implement`, 8
  tasks, 142 ready checks, and 0 failed checks.
- `results/reproducibility/package_report.md` reports 321 ready / 1 pending /
  0 failed after including the task-spec builder and all eight task specs.
- At this phase, fixture manifests, runner/scorer, real-reuse raw rows, and
  main result artifacts did not exist. Later phases created planning fixtures
  for all tasks and ran REF-T1/REF-T2 only; the remaining main-experiment work
  is AIDE, SWE-agent, and SnapATAC2 execution.

Phase 80 evidence:

- Real-reuse benchmark spec exists at
  `benchmarks/real_reuse/real_reuse_v0.json`.
- Preflight checker exists at `scripts/check_real_reuse_benchmark.py`; test
  coverage exists at `tests/test_check_real_reuse_benchmark.py`.
- Initial `results/real_reuse/spec_preflight.md` reported
  `ready_to_implement`, 8 tasks, 85 ready checks, and 0 failed checks before
  task-spec validation was added in Phase 81.
- The aggregate package checker now includes real-reuse spec/preflight checks;
  `results/reproducibility/package_report.md` reports 312 ready / 1 pending /
  0 failed.
- At this phase, no real-reuse task had been executed. This is superseded by
  Phase 87 for REF-T1/REF-T2 only; the full eight-task benchmark is still
  incomplete.

Phase 79 evidence:

- Next-stage validity is now planned as original-style real-reuse tasks, not
  offline coverage alone.
- Main candidate papers/tasks are AIDE-T1/T2, SWE-T1/T2, REF-T1/T2, and
  SNAP-T1/T2. Toolformer and AI Scientist-v2 remain sanity/auxiliary cases.
- Summary is the main baseline. Abstract and main-table Full Excerpt columns
  are dropped; Full Excerpt is only a small sanity check.
- LLM ablation must be attached to the real-reuse tasks, not only the old
  saved-response usage-plan protocol.
- Do not describe the main real-reuse benchmark as complete until all eight
  task rows are executed or a clearly declared subset result is reported.
  Current raw rows cover REF-T1/REF-T2 only.

Phase 76/77 evidence:

- AI-Scientist-v2 bounded LLM-client smoke is complete:
  `results/ai_scientist_v2_smoke/run_report.md` reports `complete`, 6 ready
  checks, 0 pending checks, and 0 failed checks.
- AI-Scientist-v2 bounded full live run is complete:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`,
  16 ready checks, 0 pending checks, 0 failed checks, and one completion
  directory:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
- Stage 1/2 validated an offline synthetic benchmark: skill TSR 0.80, full
  excerpt TSR 0.80, abstract TSR 0.20, generic summary/no context 0.00; skill
  token cost 86.2 versus full excerpt 113.2.
- Stage 3 HF/semantic-data branch is a failed branch only: invalid dataset
  loading/synthetic padding and missing `sentence_transformers`. Do not promote
  those numbers to the main paper.
- Stage 4 retrieval-depth sensitivity reports skill TSR 0.80 for K=1/2/3/5 and
  1.00 for K=all. Treat this as synthetic sensitivity evidence, not a final
  main-paper component ablation.
- Stale external-evidence reports were refreshed in dependency order. Current
  closure queue has two items: `human_fidelity_annotation` and
  `aaai_submission_decision`. Execution packets also have two packets.
- Current generated reports after refresh:
  - Goal completion: 77 ready / 3 pending / 0 failed.
  - Reproducibility package: 305 ready / 1 pending / 0 failed.
  - External evidence closure queue: 2 items, 3 ready checks, 0 failed checks.
  - External evidence execution packets: 2 packets, 7 ready checks, 0 failed
    checks.
- `C:\Users\19351\Desktop\tem\toHuman\needHelp.md` no longer asks for
  AI-Scientist-v2 provider/live-run help. It keeps only human-fidelity
  annotation as the current human-side action.
- Run log:
  `research/run_logs/2026-07-02_phase76_ai_scientist_v2_full_live_run.md`.

Phase 73/74 evidence:

- User added three PDFs under `papers/raw`; extracted text exists under
  `papers/extracted_text`.
- 2026-07-01 human-help signal check: `C:\Users\19351\Desktop\tem\toHuman\ok.txt`
  was present, reviewed, and removed after confirming the handoff. `needHelp.md`
  remains the live escalation log.
- Triage decision:
  - Paper2Agent (`arXiv:2509.06917`) is core related/competing work. It
    converts papers plus codebases into MCP servers and interactive paper
    agents; cite it and use the current bounded artifact/workflow comparison
    for positioning.
  - AgenticSciML (`doi:10.1038/s44387-026-00102-5`, `arXiv:2511.07262`) is
    adjacent agentic-science workflow background; cite it, but do not add an
    immediate experiment.
  - Reasoning Manifolds (`arXiv:2605.08142`) is a future theory-heavy
    non-procedural stress case, not a main experiment now.
- Current citation state:
  - `paper/aaai/papertoskill_aaai2027.tex` already cites Paper2Agent and
    AgenticSciML in Related Work.
  - `paper/aaai/papertoskill_refs.bib` already includes Paper2Agent,
    AgenticSciML, and Reasoning Manifolds entries.
  - No additional main experiment is required for Reasoning Manifolds yet.
- Updated AAAI related work/bib, related-work gap map, claim-source map, and
  `research/new_paper_triage_2026-07-01.md`.
- API docs in `C:\Users\19351\Desktop\论文\SelfPaper\LLMAPIDocument` confirm:
  GPT uses OpenAI Responses at `https://coderxiaoc.com/v1/responses`; Claude
  uses Anthropic Messages at `https://coderxiaoc.com/v1/messages`; DeepSeek
  uses Chat Completions at `https://api.deepseek.com/chat/completions`.
- Current model-ablation protocol state:
  - GPT protocol refresh completed both current rows with `gpt-5.5`.
  - DeepSeek completed both current rows with `deepseek-v4-flash`.
  - Latest Claude protocol refresh used Anthropic Messages but returned
    provider HTTP 502; scored Claude rows come from older saved response files.
  - `results/model_ablation_prompts/v0/evaluation.md` reports 6 total, 6
    scored, 0 pending, average normalized 1.0.
  - `results/tables/model_response_cost_proxy.md` reports 6 measured, 0
    pending, 9,594 `o200k_base` output tokens.
- Evidence boundary: saved-response scoring is not live downstream task
  success, human semantic fidelity, provider billing, success per dollar, or a
  broad model-quality comparison.
- Paper2Agent artifact/workflow comparison:
  - `results/tables/paper2agent_artifact_comparison.md` reports
    `overall_status=ready`, 7 ready criteria, and 0 failed criteria.
  - This is source-backed artifact/workflow positioning only. It does not run
    Paper2Agent, deploy an MCP server, or prove baseline performance.
- Phase 75 generated reports before the Phase 76 live-run refresh:
  - Goal completion: 75 ready / 5 pending / 0 failed.
  - Reproducibility package: 301 ready / 5 pending / 0 failed.
  - Submission review: 15 ready / 0 failed after the latest refresh.
  - AAAI submission decision: ready, recorded
    `selected_option=wait_for_external_evidence`, 27 ready / 0 pending /
    0 failed.
  - External evidence closure queue: 4 items after token-accounting removal
    from the pending-evidence queue.
  - External evidence execution packets: 4 packets, 7 ready / 0 pending /
    0 failed.
  - Superseded by Phase 76 reports: goal 77 ready / 3 pending / 0 failed,
    package 305 ready / 1 pending / 0 failed, closure queue 2 items, packets
    2 items.
- 2026-07-01 Phase 75 sync:
  - Updated tests and `scripts/check_submission_review.py` so current reports
    accept the recorded AAAI wait decision and completed local token accounting
    instead of stale pending-decision/provider-billing assumptions.
  - Re-ran the Claude direct provider probe with the documented Anthropic
    Messages protocol, regular key, `PAPERTOSKILL_CLAUDE_BASE_URL`, and
    `PAPERTOSKILL_CLAUDE_API_KEY`; `claude-opus-4-8`,
    `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 502. This was
    a Phase 75 provider-availability observation, not a model-quality failure;
    it is superseded for the bounded AI-Scientist-v2 evidence path by the
    Phase 76 smoke/full live-run completion artifacts.
  - `python -m unittest discover -s tests -v` passed: 96 tests.

Phase 62 objective:

- Make it easier for the user to add DeepSeek later without manually editing
  JSON or committing secrets.
- Preserve evidence boundaries: configuring a DeepSeek slot is not collecting
  responses, scoring DeepSeek rows, or completing model ablations.

Phase 59 evidence:

- Added `scripts/run_openai_compatible_direct_probe.py`, a diagnostic that
  bypasses `ai_scientist.llm` and calls `/chat/completions` directly with the
  same tiny marker contract.
- Added tests for success, redaction, missing configuration, and alias fallback.
- Ran direct probes with shell-only credentials:
  - Claude-family: `claude-opus-4-8`, `claude-opus-4.8`,
    `claude-opus-4-7`, and `claude-opus-4-6` all returned HTTP 503
    `No available accounts: no available accounts`.
  - GPT-family: `gpt-5.5` and `gpt-5.4` both returned HTTP 502
    `Upstream access forbidden, please contact administrator`.
- Reports are under `results/openai_compatible_direct_probe/`; no direct-probe
  response files exist.
- Added `research/run_logs/2026-06-20_phase59_openai_direct_probe.md`.
- Integrated the direct-probe reports into the reproducibility package gate as
  diagnostic readiness checks only.

Phase 60 evidence:

- `git push origin main` succeeded for Phase 59:
  `2488ade..dc52b06  main -> main`.
- Re-ran direct probes with shell-only credentials:
  - Claude-family remains HTTP 503 `No available accounts: no available accounts`.
  - GPT-family remains HTTP 502 `Upstream access forbidden, please contact
    administrator`.
- Added
  `research/run_logs/2026-06-20_phase60_post_push_provider_recheck.md`.
- Refreshed local gate reports. `results/reproducibility/package_report.md`
  still reports `ready_with_pending_external_evidence`, 281 ready checks, 8
  pending checks, and 0 failed checks. `results/reproducibility/goal_completion_report.md`
  still reports `not_complete_pending_external_evidence`, 70 ready checks, 8
  pending checks, and 0 failed checks.

Phase 61 evidence:

- Updated `scripts/check_external_evidence_packets.py` so
  `ai_scientist_v2_smoke_completion` lists the direct-probe runner and
  Claude/GPT-family reports as inputs and runs direct endpoint probes before
  wrapper smoke commands.
- Added completion criteria that at least one direct probe must return a saved
  marker-contract response before wrapper smoke can be considered resolved.
- Expanded the packet secret scan to include closure-report content as well as
  generated packet content.
- Added regression coverage in `tests/test_check_external_evidence_packets.py`
  for direct-probe-first ordering and alias coverage.
- Added
  `research/run_logs/2026-06-20_phase61_direct_probe_packet_preflight.md`.

Phase 62 evidence:

- Added `scripts/configure_deepseek_followup.py`, which configures only
  non-secret DeepSeek slot metadata: model alias, auth env name, base-url env
  name, and provider status.
- The helper rejects raw API-key-like strings and requires uppercase
  environment-variable names for credential locations.
- Added `tests/test_configure_deepseek_followup.py`.
- Updated `scripts/check_deepseek_followup.py`,
  `scripts/check_external_evidence_packets.py`,
  `examples/usage/model_ablation_usage.md`, `research/runbook.md`, and package
  gates so future DeepSeek setup uses the helper.
- Added
  `research/run_logs/2026-06-20_phase62_deepseek_configuration_helper.md`.
- Current refreshed reproducibility package report is
  `ready_with_pending_external_evidence`, 282 ready checks, 8 pending checks,
  and 0 failed checks.
- Phase 62 was committed locally as
  `0db90e2 Add DeepSeek followup configuration helper`, but push to
  `origin/main` is currently blocked by GitHub HTTPS connectivity. `git push`
  returned `Recv failure: Connection was reset`; `git ls-remote origin main`
  failed to connect to `github.com:443`; `Test-NetConnection github.com -Port
  443` reported ping success but `TcpTestSucceeded=False`. Current local state
  after the failed push is `main...origin/main [ahead 1]`.
- Phase 63 added a push-recovery section to `research/runbook.md` with the
  status, push, `ls-remote`, and GitHub 443 diagnostic commands to run on the
  next resume.

Phase 64 evidence:

- `git push origin main` succeeded and advanced GitHub from `92beb7f` to
  `ad8346b`, saving both local commits:
  `0db90e2 Add DeepSeek followup configuration helper` and
  `ad8346b Record GitHub push connectivity diagnostics`.
- `git status -sb` then reported `main...origin/main`, so local tracking state
  was clean and aligned after the push.
- A follow-up `git ls-remote --heads origin main` still failed with
  `Recv failure: Connection was reset`, so treat GitHub HTTPS access as
  intermittent; do not treat the old Phase 62/63 save as pending.

Phase 65 evidence:

- Re-ran direct OpenAI-compatible probes with shell-only credentials and the
  tiny marker contract.
- Claude-family aliases `claude-opus-4-8`, `claude-opus-4.8`,
  `claude-opus-4-7`, and `claude-opus-4-6` still returned HTTP 503
  `No available accounts: no available accounts`.
- GPT-family aliases `gpt-5.5` and `gpt-5.4` still returned HTTP 502
  `Upstream access forbidden, please contact administrator`.
- Reports under `results/openai_compatible_direct_probe/` remain
  `blocked_by_provider_or_model_availability`; no direct-probe response files
  exist. This is diagnostic only and does not complete AI-Scientist-v2 smoke.

Phase 66 evidence:

- Added `scripts/generate_aaai_submission_decision.py`.
- Added `tests/test_generate_aaai_submission_decision.py`.
- Updated `scripts/check_aaai_submission_decision.py` so the preflight lists
  the helper as an input and shows validated helper commands for both decision
  options.
- Updated `research/runbook.md`, `research/artifact_map.md`, and
  reproducibility package checks to include the helper.
- No `research/aaai_submission_decision.md` decision record was generated; the
  final AAAI submission decision remains pending a human research-lead choice.
- Phase 66 was pushed to `origin/main` as
  `4c020132be895469441489371516e6d14af7d2ef`.

Phase 67 evidence:

- Phase 67 was pushed to `origin/main` as
  `a0d67bc8d64ee7b25f3319817634fbc426bf31e0`.
- `git status -sb` after the Phase 67 push reported `main...origin/main`.

Phase 68 evidence:

- Refreshed long-term memory report counts to match current generated reports:
  reproducibility package `283 ready / 8 pending / 0 failed`, AAAI decision
  preflight `26 ready / 1 pending / 0 failed`, and usage examples `55 ready /
  0 failed`.
- Added `scripts/generate_aaai_submission_decision.py` and the AAAI gate
  recursion fix to the long-term artifact/fix map.
- Current recovery anchor before Phase 68 commit:
  `a0d67bc8d64ee7b25f3319817634fbc426bf31e0`.

Phase 69 evidence:

- Updated `scripts/check_external_evidence_packets.py` so the
  `aaai_submission_decision` packet lists
  `scripts/generate_aaai_submission_decision.py` and
  `results/aaai_submission_decision/decision.json` as inputs.
- The AAAI decision packet now separates pre-decision local gates, exactly one
  human-selected helper command, and final validation after
  `research/aaai_submission_decision.md` exists.
- Added regression assertions in
  `tests/test_check_external_evidence_packets.py`.
- Regenerated `results/external_evidence_packets/packets.{json,md}` and
  refreshed dependent AAAI decision, goal-completion, and package reports.
- Current refreshed report anchors remain:
  - `results/external_evidence_packets/packets.md`: ready, 7 ready checks,
    0 pending checks, 0 failed checks.
  - `results/aaai_submission_decision/decision.md`: pending human decision,
    26 ready checks, 1 pending check, 0 failed checks.
  - `results/reproducibility/goal_completion_report.md`: not complete pending
    external evidence, 70 ready checks, 8 pending checks, 0 failed checks.
  - `results/reproducibility/package_report.md`: ready with pending external
    evidence, 283 ready checks, 8 pending checks, 0 failed checks.
- No `research/aaai_submission_decision.md` decision record was generated; the
  final AAAI submission decision remains pending a human research-lead choice.

Phase 70 evidence:

- Verified local Claude Desktop / CC Switch routing:
  - Claude Desktop config uses `inferenceGatewayBaseUrl=https://coderxiaoc.com`
    and bearer auth.
  - CC Switch current Claude Desktop provider sets
    `ANTHROPIC_BASE_URL=https://coderxiaoc.com` and
    `ANTHROPIC_AUTH_TOKEN` locally.
  - Normal Claude direct request shape is Anthropic Messages:
    `POST https://coderxiaoc.com/v1/messages` with `Authorization: Bearer ...`
    and `anthropic-version: 2023-06-01`.
- Updated `scripts/run_openai_compatible_direct_probe.py` from a fixed
  `/chat/completions` diagnostic into a protocol-aware direct provider probe
  with `--wire-api openai_chat_completions|openai_responses|anthropic_messages`.
- Updated external-evidence closure/packet commands so current direct probes
  use:
  - Claude: `--wire-api anthropic_messages`, base URL `https://coderxiaoc.com`,
    aliases `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`.
  - GPT: `--wire-api openai_responses`, base URL
    `https://coderxiaoc.com/v1`, aliases `gpt-5.5`, `gpt-5.4`.
- Refreshed direct probe reports with shell-only credentials:
  - Claude-family report now has `wire_api=anthropic_messages`, 4 ready checks,
    2 pending checks, 0 failed checks, and all three Claude aliases returned
    HTTP 502 `Upstream service temporarily unavailable`.
  - GPT-family report now has `wire_api=openai_responses`, 3 ready checks,
    2 pending checks, 0 failed checks, and both GPT aliases returned HTTP 502
    `Upstream access forbidden, please contact administrator`.
- Updated `research/runbook.md` and generated external-evidence packets to
  distinguish protocol-specific direct probes from the legacy
  AI-Scientist-v2 wrapper smoke path.
- Local Desktop docs remain outside the repo at:
  - `C:\Users\19351\Desktop\tem\GPT大模型接口说明文档.md`
  - `C:\Users\19351\Desktop\tem\Claude大模型接口说明文档.md`
- No direct-probe response file was produced; AI-Scientist-v2 LLM-client smoke
  and full live/BFTS run remain pending provider availability.

## Current Evidence

- AI-Scientist-v2 dry-run succeeded with the PaperToSkill seed idea at
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- Claude Opus 4.8 and GPT-family model-ablation rows are saved and scored for
  the current two-case protocol. In the GPT-family retry, Toolformer timed out
  on `gpt-5.5` then succeeded with `gpt-5.4`, while AIDE succeeded with
  `gpt-5.5`; call this GPT-family evidence, not pure `gpt-5.5`.
- Status anchor for gates: Claude/GPT-family/DeepSeek rows are now saved and
  scored for the current two-case model-ablation protocol; latest Claude
  protocol refresh is provider-blocked and should not be read as a model-quality
  failure.
- DeepSeek follow-up now reports `responses_present`. `results/deepseek_followup_handoff/handoff.md`
  reports 7 ready checks, 0 pending checks, and 0 failed checks.
- All four live-transfer saved-response sets are complete and scored:
  `results/live_transfer_prompts/evaluation.md` reports 24 total rows, 24
  scored rows, 0 pending rows, and average normalized score 1.0.
- AI-Scientist-v2 LLM-client smoke is complete for the bounded marker contract:
  `results/ai_scientist_v2_smoke/run_report.md` reports `complete`, and
  `results/ai_scientist_v2_smoke/response.md` exists.
- AI-Scientist-v2 bounded full live run is complete:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`
  with one completion directory under
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
  This is bounded integration/synthetic sensitivity evidence, not broad live
  task-success proof.
- Human-fidelity annotation remains pending:
  `results/human_fidelity_packets/annotation_summary.md` reports 0 scored rows
  and 24 pending paper-by-criterion cells.
- Provider billing and success-per-dollar evidence are outside the current
  claim set; local token accounting replaces them for the current package in
  `results/token_accounting/token_accounting_summary.md`.
- External evidence closure queue, execution packets, and AAAI
  submission-decision gate are local handoffs/preflights only, not completed
  external evidence. The AAAI decision record now says
  `wait_for_external_evidence`, but final submission readiness is still
  pending under that policy.

## Boundaries To Preserve

Do not claim:

- Broad BFTS or live research-task success beyond the bounded Phase 76
  AI-Scientist-v2 run.
- Human semantic fidelity or expert validation completed.
- Provider billing, live invoices, realized output-token bills, or
  success-per-dollar evidence as current claims.
- Saved-response model-ablation scoring proves live task success, broad model
  quality, provider billing, or provider economics.
- Reliable arbitrary-PDF automation.
- Saved-response output-contract scoring proves real live task success.
- Submission-final or accepted AAAI paper.
- Final AAAI submission readiness under the recorded wait-for-evidence policy.

Supported:

- The AAAI package, paper-claim, paper-table, usage-example, and
  submission-review gates are locally ready when their checkers pass.
- The AAAI submission-decision gate validates the recorded
  `wait_for_external_evidence` decision.
- `aaai_final_submission_ready` remains pending until the named external
  evidence rows clear under that policy.

## Phase 59 Verification Completed

```powershell
python -m unittest discover -s tests -v
python scripts\check_submission_review.py --strict
python scripts\check_aaai_submission_decision.py --strict
python scripts\check_deepseek_followup.py --strict
python scripts\check_usage_examples.py --strict
python scripts\check_external_evidence_closure.py --strict
python scripts\check_external_evidence_packets.py --strict
python scripts\check_ai_scientist_v2_live_run_handoff.py --strict
python scripts\check_goal_completion.py --strict
python scripts\check_reproducibility_package.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_aaai_package.py --strict
python scripts\check_paper_tables.py --strict
git diff --check
rg -n "sk-[A-Za-z0-9]{20,}" .
```

Results:

- `python -m unittest discover -s tests -v`: 79 tests passed.
- All listed strict checkers passed after direct-probe report and
  submission-review refresh.
- `git diff --check`: no whitespace errors; only line-ending warnings.
- Raw key scan produced no matches.

## Persistent Blockers

- AI-Scientist-v2 bounded smoke/full live-run evidence is complete, but it is
  not human semantic fidelity, not a real-data result, and not a broad live
  research-task success claim.
- Human-fidelity annotation remains pending.
- Local token accounting is complete; provider billing and success-per-dollar
  evidence remain out of scope for the current claim set.
- Final AAAI submission readiness remains pending under the recorded
  `wait_for_external_evidence` policy.
