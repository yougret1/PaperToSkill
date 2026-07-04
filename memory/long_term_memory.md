# PaperToSkill Long-Term Memory

Read this file after any context compaction or session resume before taking new
project actions. Also read `memory/short_term_memory.md`.

This file is intentionally compact. Detailed chronological history lives in
`research/stage_log.md`, `research/run_logs/`, and `results/result_cards.md`.

## Project Identity

- Project: PaperToSkill.
- Goal: turn research papers into compact, human-editable agent skills that
  preserve the paper's reusable method, validation workflow, limitations,
  failure branches, and transfer notes.
- Local repo: `D:\a_work\gitee\PaperToSkill`.
- Remote repo: `https://github.com/yougret1/PaperToSkill.git`.
- Supporting workspace: `D:\a_work\gitee\ai-scientist-v2`.
- Active branch convention: save phase-level progress to `origin/main` unless
  the user asks for a different branch.

## Persistent User Requirements

- Maintain at least two memory files:
  - `memory/long_term_memory.md` for stable project facts.
  - `memory/short_term_memory.md` for current task state and blockers.
- Keep memory useful and short. Move old phase narration into stage logs and
  reports; preserve only facts needed for future action.
- Use `ai-scientist-v2` to refine and develop the idea where useful.
- Final paper artifacts must use an official AAAI TeX template downloaded from
  the web. Current package is AAAI-27 under `paper/aaai/`.
- Experiments must include usage examples.
- Experiment work should prioritize the main real-reuse experiment. Put the
  main experiment table structure into the paper before scores are available,
  then update numeric cells promptly after runs complete. Auxiliary experiments
  are secondary and should not delay the main table/results path.
- Current experiment-design policy: the main experiment is original-paper-style
  real-reuse over locked paper-tasks using the source papers' core objective
  metrics, not a real-user study. Do not keep a separate auxiliary experiment
  for breadth/coverage; coverage breadth is represented by the selected
  main paper-tasks unless the user explicitly reopens it. Put component
  ablation only in an appendix candidate. First complete/stabilize the core
  experiment, collect auxiliary data opportunistically during core runs, then
  run remaining auxiliary analyses; real-user/user-study evidence comes last
  and is only needed for user-efficiency or workflow-improvement claims.
- Third-party LLM service latency, API timeouts, provider retries, and request
  instability are not core effectiveness metrics. Give model calls more time
  and retry budget when needed, and record provider availability separately.
  Only count runtime/resource metrics as core evidence when the selected source
  paper's own core experiment uses local runtime/resource measures; in that
  case rerun locally and report comparable time/resource ratios.
- For the manuscript, real-reuse claims must track evidence state: experiment
  protocols and pending tables may be written before execution, but `Abstract`,
  `Introduction`, `Results`, and `Conclusion` must not claim downstream
  effectiveness until scored raw rows exist. Existing deterministic/offline
  evidence supports quality, grounding, compactness, readiness, and sanity
  claims only.
- The older saved-response Claude/GPT-family/DeepSeek model-ablation protocol
  is complete as supporting output-contract evidence. Real-reuse LLM ablation
  should attach to the real-reuse task protocol; do not treat the older
  saved-response protocol as downstream task-success evidence.
- Do not silently treat unavailable model endpoints as model-quality failures.
  Report provider/model availability problems.
- Record-sync-only work should update planning/handoff/memory records without
  touching local logs (`research/run_logs/**` and `research/stage_log.md`).
  If a network/download problem blocks a core asset or phase save, record the
  concrete command, error, and blocked artifact in
  `C:\Users\19351\Desktop\tem\toHuman.md`, then continue non-blocked work.

## Evidence Boundary

Current supported claims:

- Curated note-to-skill conversion over four papers: AI Scientist-v2,
  Reflexion, AIDE, and Toolformer.
- Deterministic extracted-text-to-note scaffolds for Toolformer and AIDE.
- Offline deterministic evaluations: rubric, context coverage, source-span
  validation, harness-transfer readiness, compactness/token proxy, usage-example
  executability, AAAI package readiness, table consistency, paper claim
  discipline, and active-goal completion auditing.
- Failure-case archive with paper-reported and project-level cases.
- Real-reuse failure-boundary analysis is derived from the same first-pass raw
  rows and is now included in the AAAI table set. It maps row-level outcomes to
  PaperToSkill-only success, patch application, solved-by-both ceiling, and
  artifact completion modes. This is explanatory boundary analysis, not new
  task-success evidence.
- Human-fidelity annotation handoff is ready: review packets, annotation guide,
  reviewer bundle zip, checksum manifest, stricter blank template metadata,
  and strict summarizer validation are present for 24 paper-by-criterion cells;
  completed human annotation remains pending.
- Local token accounting handoff is ready: input-token and saved-response
  output-token proxy summaries are present, and the composite local token
  proxy is ready for reuse.
- Claude Opus 4.8, GPT-family, and DeepSeek model-ablation prompt rows are
  saved and scored for the current two-case protocol. GPT-family protocol
  refresh completed both rows with `gpt-5.5`; DeepSeek completed both rows with
  `deepseek-v4-flash`. The latest Claude protocol refresh used Anthropic
  Messages but was blocked by provider HTTP 502, so scored Claude rows come
  from previously saved response files.
- DeepSeek follow-up handoff now reports `responses_present`: the slot, prompt
  rows, response paths, env names, and saved response files are checked for the
  current two-row protocol.
- Local output-token proxy over saved Claude/GPT-family/DeepSeek
  model-ablation responses: 6 measured rows, 0 pending rows, 9,594
  `o200k_base` output tokens.
- New-paper triage on 2026-07-01: cite Paper2Agent as the closest competing
  paper-to-agent/MCP system; cite AgenticSciML as adjacent agentic-science
  workflow background; keep Reasoning Manifolds as a future non-procedural
  stress-case candidate rather than a main experiment. Paper2Agent and
  AgenticSciML are already cited in the AAAI draft; Reasoning Manifolds is
  kept as a future stress-case citation only.
- Bounded Paper2Agent artifact/workflow comparison is complete in
  `results/tables/paper2agent_artifact_comparison.md`: 7/7 criteria are ready.
  It is source-backed positioning evidence only and does not run Paper2Agent,
  deploy an MCP server, or claim end-to-end baseline performance.
- All four live-transfer response sets are saved and scored for both harness
  prompt styles and all three context variants under the current prompt-packet
  protocol. AI Scientist-v2, Reflexion, and AIDE rows score 11/11; Toolformer
  rows score 9/9 in the saved-response output-contract evaluator.
- Bounded AI-Scientist-v2 LLM-client smoke is complete for the local marker
  contract: `results/ai_scientist_v2_smoke/run_report.md` reports `complete`
  and `results/ai_scientist_v2_smoke/response.md` exists. Earlier provider
  failures remain useful historical diagnostics, not current blockers.
- Bounded AI-Scientist-v2 full live run is complete for the current local gate:
  `results/ai_scientist_v2_live_run_handoff/handoff.md` reports `complete`,
  16 ready checks, 0 pending checks, 0 failed checks, and one completion
  directory under
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-07-02_12-18-28_papertoskill_extractor_attempt_0`.
  The run produced synthetic benchmark/sensitivity evidence: skill TSR 0.80,
  full excerpt TSR 0.80, abstract TSR 0.20, generic summary/no context 0.00,
  and retrieval-depth skill TSR 1.00 only when K=all. The Stage 3 real-data/HF
  branch remains a failed branch due invalid dataset loading/synthetic padding
  and missing `sentence_transformers`.
- External evidence closure queue is ready as a local planning/checking
  artifact: it maps all current pending goal requirements to two next-action
  items, human-fidelity annotation and AAAI submission decision. Provider
  billing and AI-Scientist-v2 smoke/full live-run evidence are no longer pending
  queue items for the current policy.
- External evidence execution packets are ready as a local handoff artifact:
  each closure item has inputs, setup notes, commands, validation commands,
  completion criteria, escalation rules, and evidence boundaries without
  completing any external evidence. The AAAI submission-decision packet uses
  the validated decision-record helper and requires a validated
  `research/aaai_submission_decision.md` record before final goal/package
  checks can clear `aaai_final_submission_ready`.
- AAAI submission decision is recorded as `wait_for_external_evidence` in
  `research/aaai_submission_decision.md`. The local decision gate is ready, but
  final submission readiness remains pending until the named external evidence
  rows clear under that wait policy.
- Phase 77 final-gate sync verified the newly added papers and API docs. The
  decision remains: cite Paper2Agent and AgenticSciML, keep Reasoning Manifolds
  as a future stress case, and do not add a new main experiment yet. All local
  strict gates and 96 unit tests passed after refreshing the AAAI decision
  state and rebuilding the AAAI PDF.
- Phase 78 archived the local `ai-scientist-v2` tracked source/config
  adaptations under `external/ai_scientist_v2_patches/` because the supporting
  checkout's remote is the SakanaAI upstream. The archive backs up the local
  coderxiaoc/BFTS integration patch inside the PaperToSkill GitHub history
  without committing raw API keys or local presentation/build artifacts.
- Phase 79/88 real-reuse planning/task/fixture/candidate/asset-lock/REF-prepared-assets/runner/AIDE-execution-layer gate: the next stronger validity
  target is original-style paper-task reuse over eight planned tasks from AIDE,
  SWE-agent, Reflexion, and SnapATAC2. Toolformer and AI Scientist-v2 remain
  sanity/auxiliary cases. `benchmarks/real_reuse/real_reuse_v0.json` and
  `benchmarks/real_reuse/tasks/*.json` are ready-to-implement planning
  artifacts; `benchmarks/real_reuse/fixtures/*.json` contains fixture
  requirement manifests; `benchmarks/real_reuse/fixture_candidates/*.json`
  records selected candidate datasets/repositories and preparation/scoring
  entry points; `benchmarks/real_reuse/asset_locks/*.json` fixes preparation-
  time source revisions, task instances, local materialization targets, hidden
  scorer assets, and scorer/preparer contracts. Phase 86 materialized REF-T1
  and REF-T2 fixture assets under `benchmarks/real_reuse/assets/`, added
  task-specific Summary contexts under `baselines/real_reuse/`, and implemented
  `scripts/prepare_real_reuse_reflexion_fixture.py` plus
  `scripts/score_real_reuse_reflexion.py`. `results/real_reuse/spec_preflight.md`
  validates the REF prepared assets and runner. Phase 87 added
  `scripts/run_real_reuse_reflexion.py`, ran REF-T1/REF-T2 once through the
  GPT-family `gpt-5.5` Responses profile, and saved four scored raw rows under
  `results/real_reuse/raw_rows.jsonl`: Summary and PaperToSkill both score
  1.000 on both locked REF tasks. This is partial REF-slice execution evidence
  only. Phase 88 added `scripts/prepare_real_reuse_aide_fixture.py`,
  `scripts/score_real_reuse_aide.py`, and `scripts/run_real_reuse_aide.py`;
  131 unit tests, all strict local gates, `git diff --check`, and the raw-key
  scan passed. The preflight validates the AIDE execution-layer contract. AIDE
  fixture materialization and raw rows wait for the real Kaggle Spaceship
  Titanic `train.csv`. Phase 90 added the SWE-agent real-reuse skill gate:
  `papers/auto_notes/swe_agent_auto_note.md`,
  `generated_skills/real_reuse/swe_agent/SKILL.md`, source map,
  `benchmarks/rubric_swe_agent_v0.json`, source-span task, and evaluation
  reports. The SWE-agent skill scores 20/20, stays under the 1200-word budget,
  and has source-span support_rate=1.0 with 0 invalid ranges. Phase 91 added
  `scripts/prepare_real_reuse_swe_fixture.py`,
  `scripts/score_real_reuse_swe.py`, and
  `scripts/run_real_reuse_swe.py`, plus focused tests and gate integration.
  Phase 92 added the SnapATAC2 real-reuse skill gate:
  `papers/auto_notes/snapatac2_auto_note.md`,
  `generated_skills/real_reuse/snapatac2/SKILL.md`, source map,
  `benchmarks/rubric_snapatac2_v0.json`, source-span task, and evaluation
  reports. The SnapATAC2 skill scores 20/20, stays under the 1200-word budget,
  and has source-span support_rate=1.0 with 0 invalid ranges. Phase 93 added
  `scripts/prepare_real_reuse_snapatac2_fixture.py`,
  `scripts/score_real_reuse_snapatac2.py`, and
  `scripts/run_real_reuse_snapatac2.py`, plus focused tests and gate
  integration. Phase 94 materialized official miniature SnapATAC2 fixture
  assets for SNAP-T1/T2 under `benchmarks/real_reuse/assets/`, added
  SNAP-T1/T2 Summary contexts, recorded SnapATAC2 revision
  `7be57442708694217e27c8654ecd38a0de194aa4`, MIT license provenance,
  official dataset references, and copied-fragment SHA256 values
  `c810f5e906de001def93b8fd58397f42a4f31f4a9e500d1245d469a68376c612`
  and `95922648e50db7f47246f588ec38eafe9cbe4b42972d6e3a064916a2689d2251`.
  The miniature fixtures are smoke/fixture-readiness assets only, not full
  pbmc5k/pbmc10k_multiome reproductions. Phase 95 ran SNAP-T1/SNAP-T2 Summary
  and PaperToSkill with GPT-family `gpt-5.5` over these prepared miniature
  fixtures and appended four scored rows to `results/real_reuse/raw_rows.jsonl`.
  SNAP-T1 Summary/PaperToSkill scored 0.000/0.500; SNAP-T2
  Summary/PaperToSkill scored 0.200/0.400. All SNAP rows failed the
  pre-registered success threshold because complete runtime, memory, and
  quality artifacts were missing or malformed. This is failure-boundary
  evidence only, not a full SnapATAC2 reproduction and not non-agent downstream
  success. Phase 96 materialized SWE-T2 as an external-workspace fixture
  against `D:\a_work\gitee\astropy__astropy`, copied gold/test patches into
  `benchmarks/real_reuse/assets/SWE-T2/scorer_only/`, fixed relative patch-path
  scoring, validated the gold scorer, and ran SWE-T2 Summary/PaperToSkill with
  GPT-family `gpt-5.5`. SWE-T2 Summary/PaperToSkill scored 0.000/1.000:
  Summary failed patch application and PaperToSkill applied its patch and
  passed both hidden Astropy target tests. This is one locked SWE-Bench
  Verified-style instance, not a full SWE-agent reproduction. Phase 97
  materialized SWE-T1 as an external-workspace fixture against
  `D:\a_work\gitee\sqlfluff__sqlfluff` at base commit
  `14e1a23a3166b9a645a16de96f694c77a5d4abb7`, using local SWE-bench Lite
  parquet extraction for the problem statement, gold patch, and hidden test
  patch. It created a task-specific venv at
  `D:\a_work\gitee\venvs\sqlfluff__sqlfluff-1625`, validated the gold scorer,
  and ran SWE-T1 Summary/PaperToSkill with GPT-family `gpt-5.5`. SWE-T1
  Summary/PaperToSkill scored 0.000/0.000 because both generated patches failed
  to apply. This is one locked SWE-Bench Lite-style failure-boundary row, not a
  full SWE-agent reproduction. Phase 98 materialized AIDE-T1/T2 from the
  official Kaggle Spaceship Titanic files supplied by the user under
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\`, validated
  the local scorer with baseline/weak-script scores around
  `0.4997124784358827`, and ran AIDE-T1/T2 Summary/PaperToSkill with
  GPT-family `gpt-5.5`. In Phase 98, AIDE-T1 and AIDE-T2 both scored
  0.000/0.000 because all generated scripts exceeded the 60-second scorer
  budget. Phase 106 later reused the same saved model outputs with a
  300-second local scorer budget: AIDE-T1 scored 0.816/0.817 and was solved by
  both conditions; AIDE-T2 scored 0.000/0.826 and became a
  PaperToSkill-only success. The first single-run GPT-family pass covers all
  eight real-reuse rows. It is mixed: AIDE-T2 and SWE-T2 are positive
  PaperToSkill-only rows, AIDE-T1 and REF are solved by both conditions,
  SWE-T1 is a scored patch-apply failure, and SNAP rows remain below success
  threshold. This does not establish aggregate PaperToSkill advantage over
  Summary. Phase 91 targeted verification passed
  for 18 SWE/table/preflight/package tests, refreshed the AAAI PDF/table gates,
  and moved SWE rows to `Fixture pending` without adding scores. Phase 92 full
  verification passed 143 unit tests, all strict local gates, `git diff
  --check` with only Windows line-ending warnings, and the raw-key scan with no
  matches. Phase 93 verification passed 153 unit tests and all strict local
  gates before documentation cleanup. Phase 94 verification passed 155 unit
  tests and all strict local gates before phase save.
- Phase 84 inserted the main real-reuse table scaffold into the AAAI paper, and
  later phases filled AIDE-T1/AIDE-T2, SWE-T1/SWE-T2, REF-T1/REF-T2, and
  SNAP-T1/SNAP-T2 from raw rows:
  `results/real_reuse/main_results_plan.csv`, `.md`, and `.json` are the table
  data source; `paper/aaai/papertoskill_tables.tex` contains
  `tab:real-reuse-main`. Current statuses are all `Scored (GPT-family)`.
  `results/real_reuse/main_run_selection.json` locks the paper-facing main rows
  so later follow-up raw rows, including SWE-T1 phase107, do not silently
  replace the pre-registered main experiment cells.
- Phase 104/105 added and executed the auxiliary Full Excerpt sanity check for
  AIDE-T1, SWE-T1, and SNAP-T1:
  `scripts/build_real_reuse_full_excerpt_sanity.py` writes
  `results/real_reuse/full_excerpt_sanity.{csv,md,json}`, and
  `paper/aaai/papertoskill_tables.tex` contains
  `tab:full-excerpt-sanity`. Phase 105 added bounded runner/spec support for
  `full_excerpt` only on the pre-registered sanity tasks and scored the subset:
  AIDE-T1 Full Excerpt 0.000 (`timeout after 60s`, scored from a saved live
  GPT-family response after fixing AIDE scorer timeout handling), SWE-T1 Full
  Excerpt 0.000 (`patch_apply_failed`, live GPT-family `gpt-5.5`), and
  SNAP-T1 Full Excerpt 0.250 (`missing_required_artifacts_or_metrics`, live
  GPT-family `gpt-5.5`). Token columns are local whitespace context proxies,
  not provider billing or output-token costs. This remains auxiliary sanity
  evidence, not a main baseline or aggregate effectiveness claim.
- Phase 107 executed the SWE-T1 shared-source-context follow-up
  `phase107_gpt_swe_t1_source_context_followup` with GPT-family `gpt-5.5`.
  The follow-up exposed the same locked SQLFluff `L031.py` source slice to both
  Summary and PaperToSkill because the first-pass prompt implied repository
  inspection while the one-shot runner did not provide an inspection tool. Both
  calls succeeded on the first attempt and both generated patches applied, but
  both scored 0.000 because the hidden test failed. The diagnostic boundary is
  that both candidates edited rule logic while the hidden scorer expected the
  specific L031 message-text change. Preserve the first-pass SWE-T1 0.000/0.000
  rows as the paper-facing main rows; report phase107 only as a
  shared-source-context follow-up.
- Latest confirmed GitHub backup includes commit `6424ba6` (`Sync remote
  backup status records`). The earlier HTTPS reset around local commit
  `f54be5b` was recovered by a successful push to `origin/main`. Keep future
  GitHub transport failures separate from experiment correctness and verify
  local/remote alignment before claiming a new phase save. Local commits
  `10ffc10`, `516895a`, and `6c5c360` currently exist beyond that remote
  commit; upload is blocked by GitHub HTTPS reset / port-443 connection
  failure and is recorded in `C:\Users\19351\Desktop\tem\toHuman.md`.
- SNAP artifact-execution follow-up diagnosis is now materialized in
  `results/real_reuse/snapatac2_artifact_followup.{md,json}` with builder
  `scripts/build_real_reuse_snapatac2_artifact_followup.py`: all selected SNAP
  main rows have an execution gap because the current runner collects plan/JSON
  outputs rather than executed artifacts; miniature fixtures are readable;
  `snapatac2` is not importable in the current Python environment. This is a
  pre-registered follow-up contract, not a main-row replacement.
- Phase108 SNAP executable-artifact follow-up is materialized in
  `results/real_reuse/snapatac2_executable_artifact_followup.{csv,md,json}`
  with runner `scripts/run_real_reuse_snapatac2_executable_followup.py`: a
  paired pre-registered controlled scaffold over the same miniature fixtures
  scores 1.000 for Summary and PaperToSkill on SNAP-T1/T2 under the existing
  scorer. It validates the artifact/runtime/memory contract path, does not
  append to `raw_rows.jsonl`, does not replace main SNAP rows, and does not
  show PaperToSkill advantage.
- Phase109 has started the real-reuse LLM ablation only on the pre-registered
  stabilized slices. The current collected pair is REF-T2 / GPT-family /
  `gpt-5.5`: Summary 1.000 and PaperToSkill 1.000, both successful on attempt
  1. `results/real_reuse/llm_ablation_summary.md` reports 2 collected rows and
  16 pending rows out of 18 expected rows. This is ceiling/control auxiliary
  evidence, not a main-row replacement and not PaperToSkill advantage.
- Phase 89 and the 2026-07-04 record-sync push both recovered GitHub HTTPS
  transport interruptions. Use `git status -sb` and a successful remote check
  for the latest exact alignment before each phase-save claim.

Current unsupported claims:

- PaperToSkill improves real original-style task outcomes across AIDE,
  SWE-agent, Reflexion, SnapATAC2, or other domains. The first single-run
  GPT-family pass covers all eight rows, but it is mixed rather than
  confirmatory. AIDE-T1 scores 0.816/0.817 and is solved by both conditions;
  AIDE-T2 scores 0.000/0.826 and is PaperToSkill-only success; SWE-T1 scores
  0.000/0.000 due patch-apply failures; SWE-T2 scores 0.000/1.000 and is a
  PaperToSkill-only success; REF-T1/REF-T2 score 1.000/1.000 and show no
  advantage; and SNAP-T1/T2 score 0.000/0.500 and 0.200/0.400 while failing
  the success threshold. This is downstream stress-test and failure-boundary
  evidence, not broad effectiveness.
- Saved-response model-ablation scoring as proof of live downstream task
  success, broad model quality, provider billing, or provider economics.
- Saved-response output-contract scoring as proof of real live task success.
- Human-validated semantic fidelity.
- Provider billing, realized output-token bills, live invoices, or
  success-per-dollar as current paper claims.
- Reliable arbitrary-PDF-to-skill automation.
- Treating the bounded AI-Scientist-v2 synthetic smoke/full live run as broad
  real-data or live research-task success.
- Submission-final or accepted AAAI paper.
- Final AAAI submission readiness under the recorded wait-for-evidence policy.

## Main Artifact Map

Use these as entry points instead of searching the whole repo first:

- `skill/SKILL.md`: PaperToSkill skill prototype.
- `scripts/papertoskill_extract.py`: source-note-to-skill extractor.
- `scripts/papertoskill_note_from_text.py`: extracted-text-to-note scaffold.
- `scripts/papertoskill_pipeline.py`: local extracted-text-to-note-to-skill
  pipeline manifest command.
- `scripts/run_model_ablation_prompts.py`: OpenAI-compatible live model runner.
- `scripts/evaluate_model_ablation_responses.py`: saved-response scorer.
- `scripts/evaluate_model_response_costs.py`: saved-response output-token proxy.
- `scripts/run_live_transfer_prompts.py`: OpenAI-compatible live-transfer runner.
- `scripts/evaluate_live_transfer_responses.py`: saved live-transfer response
  scorer.
- `scripts/run_ai_scientist_v2_smoke.py`: bounded AI-Scientist-v2 LLM-client
  smoke runner with status-summary output, repeatable `--model-alias`,
  `--timeout-seconds`, `--max-tokens`, and `--require-complete`.
- `scripts/run_openai_compatible_direct_probe.py`: direct provider diagnostic
  for the same tiny marker contract, bypassing `ai_scientist.llm`; this is
  provider-availability evidence only.
- `scripts/check_ai_scientist_v2_live_run_handoff.py`: local full
  AI-Scientist-v2 live/BFTS run handoff and preflight report generator; no
  network calls.
- `scripts/check_reproducibility_package.py`: aggregate local package gate.
- `scripts/check_aaai_package.py`: AAAI package/build gate.
- `scripts/check_usage_examples.py`: usage-example gate.
- `scripts/check_paper_tables.py`: AAAI result-table consistency gate.
- `scripts/check_paper_claims.py`: paper overclaim/boundary gate.
- `scripts/check_submission_review.py`: submission-review handoff freshness
  gate.
- `scripts/check_goal_completion.py`: active-goal completion gate.
- `scripts/check_external_evidence_closure.py`: no-network closure queue for
  pending external evidence and final-decision items.
- `scripts/check_external_evidence_packets.py`: no-network execution packet
  builder for each pending external-evidence item.
- `scripts/check_aaai_submission_decision.py`: no-network AAAI submission
  decision preflight; exposes decision options without selecting one.
- `scripts/generate_aaai_submission_decision.py`: validated helper for writing
  the human AAAI submission-decision record after an explicit option, owner,
  date, claim boundary, and evidence policy are provided.
- `benchmarks/model_ablation_v0.json`: Claude/GPT-family/DeepSeek prompt spec.
- `scripts/check_deepseek_followup.py`: local DeepSeek follow-up handoff and
  preflight report generator; no network calls.
- `research/new_paper_triage_2026-07-01.md`: triage of Paper2Agent,
  AgenticSciML, and Reasoning Manifolds against PaperToSkill.
- `research/real_reuse_experiment_plan.md`: planned next-stage real-reuse
  protocol with eight `paper-task` rows, table layouts, and evidence
  boundaries. It is not a completed result artifact.
- `benchmarks/real_reuse/real_reuse_v0.json`: machine-checkable planned
  real-reuse benchmark spec with eight task rows, Summary/PaperToSkill main
  conditions, Full Excerpt sanity scope, reference-score boundary, and planned
  output paths.
- `scripts/build_real_reuse_task_specs.py`: materializes per-task
  execution-contract specs from the master real-reuse benchmark spec.
- `scripts/build_real_reuse_fixture_manifests.py`: materializes fixture
  requirement manifests from the per-task real-reuse specs.
- `scripts/build_real_reuse_fixture_candidates.py`: materializes selected
  candidate asset/preparation manifests from the task specs and fixture
  manifests.
- `scripts/build_real_reuse_asset_locks.py`: materializes preparation-time
  asset locks from task specs, fixture manifests, and candidate manifests.
- `scripts/build_real_reuse_paper_tables.py`: materializes the paper-facing
  real-reuse main-results table from the benchmark spec and fills existing
  score cells from `results/real_reuse/raw_rows.jsonl`. It can use
  `results/real_reuse/main_run_selection.json` to keep follow-up rows from
  silently replacing paper-facing main cells.
- `scripts/build_real_reuse_failure_analysis.py`: materializes the derived
  real-reuse failure-boundary table and uses the same row-selection policy when
  building paper-facing first-pass boundary analysis.
- `scripts/prepare_real_reuse_reflexion_fixture.py`: materializes locked
  REF-T1 HotPotQA-style and REF-T2 HumanEval-style fixture assets, task prompts,
  Summary condition contexts, and scorer-only hidden assets.
- `scripts/score_real_reuse_reflexion.py`: scores REF-T1 predictions with
  answer-key EM/F1 and REF-T2 candidates with the hidden HumanEval checker.
- `scripts/run_real_reuse_reflexion.py`: runs locked REF-T1/REF-T2 Summary and
  PaperToSkill conditions, saves prompts/responses/metrics, appends raw rows,
  and separates provider availability from model quality.
- `scripts/prepare_real_reuse_aide_fixture.py`: prepares locked AIDE-T1/T2
  Spaceship Titanic fixtures from a human-provided real `train.csv`, while
  keeping `validation_labels.csv` scorer-only.
- `scripts/score_real_reuse_aide.py`: scores AIDE submissions or candidate
  scripts in an isolated workspace against hidden validation labels.
- `scripts/run_real_reuse_aide.py`: runs locked AIDE-T1/T2 Summary and
  PaperToSkill conditions, saves prompts/responses/metrics/raw rows, and
  separates provider/data availability from model quality.
- `scripts/prepare_real_reuse_swe_fixture.py`: prepares locked SWE-T1/T2
  fixture assets from a local repository snapshot or local SWE-bench parquet,
  writes model-visible issue/test context and Summary contexts, and keeps gold
  and hidden test patches scorer-only.
- `scripts/score_real_reuse_swe.py`: scores SWE candidate patches by applying
  unified diffs in an isolated temporary workspace and running the locked test
  command.
- `scripts/run_real_reuse_swe.py`: runs locked SWE-T1/T2 Summary and
  PaperToSkill conditions, saves prompts/responses/metrics/raw rows when
  scorable, and records missing fixture assets/provider availability separately
  from model quality.
- `scripts/check_real_reuse_benchmark.py`: strict local preflight checker for
  the planned real-reuse benchmark spec, per-task specs, fixture manifests,
  candidate asset/preparation manifests, asset locks, REF prepared assets, REF
  runner, AIDE execution-layer script contract, SWE-agent skill gate, and SWE
  execution-layer script contract.
- `benchmarks/real_reuse/tasks/*.json`: eight per-task execution-contract specs
  with input/output contracts, condition paths, metric contracts, run controls,
  workflow checklists, unsupported-error policy, and raw-row schema. They do
  not include fixtures or results.
- `benchmarks/real_reuse/fixtures/*.json`: eight fixture requirement manifests
  with asset slots, context assets, scoring contracts, license/provenance
  status, and planned outputs. They do not select concrete datasets/repos or
  contain results.
- `benchmarks/real_reuse/fixture_candidates/*.json`: eight candidate
  asset/preparation manifests with selected source repositories/datasets,
  preparation commands, scoring entry points, and license/provenance boundaries.
  They do not download or materialize assets and do not contain results.
- `benchmarks/real_reuse/asset_locks/*.json`: eight preparation-time asset
  locks with observed source revisions, fixed task instances, local
  materialization targets, hidden scorer assets, and scorer/preparer contracts.
  They do not download or materialize assets and do not contain results.
- `benchmarks/real_reuse/assets/REF-T1/asset_manifest.json` and
  `benchmarks/real_reuse/assets/REF-T2/asset_manifest.json`: prepared Reflexion
  fixture manifests with sha256 values and model-visible/scorer-only asset
  separation. They are setup evidence; REF model-run results live under
  `results/real_reuse/`.
- `baselines/real_reuse/REF-T1_summary.md` and
  `baselines/real_reuse/REF-T2_summary.md`: task-specific Summary condition
  contexts for the two prepared Reflexion tasks.
- `results/real_reuse/raw_rows.jsonl`: current AIDE-T1/AIDE-T2,
  SWE-T1/SWE-T2, REF-T1/REF-T2, and SNAP-T1/SNAP-T2 GPT-family
  Summary-vs-PaperToSkill raw scored rows; this is the first full eight-row
  single-run pass, but it is mixed/failure-heavy and not aggregate effectiveness
  evidence.
- `results/real_reuse/reflexion_run_report.md`: current REF-T1/REF-T2
  GPT-family run report, complete for 4/4 rows.
- `results/real_reuse/snapatac2_run_report.md`: current SNAP-T1/SNAP-T2
  GPT-family run report, complete for 4/4 rows; all rows failed the success
  threshold, so this is failure-boundary evidence.
- `results/real_reuse/main_results_plan.csv`, `.md`, and `.json`: paper-facing
  real-reuse main table source with all eight rows filled from raw rows.
- `results/real_reuse/main_run_selection.json`: paper-facing row-selection
  manifest that pins the main table to pre-registered rows and leaves follow-up
  rows available for dedicated follow-up analysis.
- `results/real_reuse/failure_analysis.csv`, `.md`, and `.json`: derived
  paper-facing real-reuse failure-boundary table source; it explains first-pass
  boundary modes without adding new task-success evidence.
- `scripts/build_real_reuse_full_excerpt_sanity.py` and
  `results/real_reuse/full_excerpt_sanity.csv`, `.md`, and `.json`: auxiliary
  Full Excerpt sanity check over AIDE-T1, SWE-T1, and SNAP-T1. The current
  table records Summary/PaperToSkill/Full Excerpt scores and local
  context-token proxies; the Full Excerpt scores are 0.000, 0.000, and 0.250.
- `generated_skills/real_reuse/swe_agent/SKILL.md` and
  `generated_skills/real_reuse/swe_agent/references/source_map.json`:
  SWE-agent source-anchored generated skill for the software-engineering
  real-reuse task family. SWE-T1 and SWE-T2 now have one GPT-family scored
  Summary-vs-PaperToSkill run each; SWE-T1 is a failed patch-apply row and
  SWE-T2 is a positive PaperToSkill row.
- `results/evaluations/swe_agent_rubric_v0.json` and
  `results/evaluations/swe_agent_auto_source_span_validation_v0.json`:
  SWE-agent skill quality gates, currently 20/20 rubric and 1.0 source-span
  support rate with 0 invalid ranges.
- `generated_skills/real_reuse/snapatac2/SKILL.md` and
  `generated_skills/real_reuse/snapatac2/references/source_map.json`:
  SnapATAC2 source-anchored generated skill for the single-cell omics
  real-reuse task family. The skill gate, execution layer, miniature fixture
  assets, and one GPT-family Summary-vs-PaperToSkill run are complete for
  SNAP-T1/SNAP-T2. Both rows remain below the pre-registered success threshold,
  so this is failure-boundary evidence rather than full SnapATAC2 reproduction.
- `results/evaluations/snapatac2_rubric_v0.json` and
  `results/evaluations/snapatac2_auto_source_span_validation_v0.json`:
  SnapATAC2 skill quality gates, currently 20/20 rubric and 1.0 source-span
  support rate with 0 invalid ranges.
- `benchmarks/real_reuse/assets/SNAP-T1/asset_manifest.json` and
  `benchmarks/real_reuse/assets/SNAP-T2/asset_manifest.json`: prepared
  SnapATAC2 miniature fixture manifests with model-visible dataset/resource/
  schema/task assets, scorer-only thresholds, SNAP-T2 proxy metric policy, and
  copied official repository test fragments. They were used for the Phase 95
  GPT-family Summary-vs-PaperToSkill dry-run rows; the fixtures are miniature
  failure-boundary assets, not full pbmc5k/pbmc10k_multiome reproductions.
- `baselines/real_reuse/SNAP-T1_summary.md` and
  `baselines/real_reuse/SNAP-T2_summary.md`: task-specific Summary condition
  contexts for the two prepared SnapATAC2 tasks.
- `results/real_reuse/spec_preflight.md`: ready-to-implement preflight report
  for the real-reuse spec/task/fixture/candidate/asset-lock contracts, REF
  runner, AIDE execution-layer contract, SWE-agent skill/execution-layer
  contracts, and SnapATAC2 skill/execution-layer contracts. This is not
  task-success evidence by itself.
- `external/ai_scientist_v2_patches/`: reproducibility backup for local
  AI-Scientist-v2 adaptations used by the bounded Phase 76 integration run.
- `benchmarks/provider_billing_evidence_v0.json`: provider-billing evidence
  slot protocol.
- `scripts/summarize_provider_billing_evidence.py`: billing handoff template
  and summary validator.
- `examples/usage/`: usage examples for skill use, auto-note, and ablations.
- `paper/aaai/`: official AAAI-27 author kit and LaTeX draft.
- `results/reproducibility/`: machine-readable and Markdown readiness reports.
- `research/goal_completion_audit.md`: human-readable requirement audit.
- `research/runbook.md`: reproducible commands.

## Current Reports

- Reproducibility package:
  `results/reproducibility/package_report.md`
  reports `ready_with_pending_external_evidence`, 427 ready checks, 1 pending
  check, and 0 failed checks.
- Active-goal completion:
  `results/reproducibility/goal_completion_report.md`
  reports `not_complete_pending_external_evidence`, 77 ready checks, 3 pending
  checks, and 0 failed checks.
- External evidence closure queue:
  `results/external_evidence_closure/closure.md`
  reports `pending_external_evidence`, 3 ready checks, 0 pending checks, and 0
  failed checks. The two queue items are human-fidelity annotation and AAAI
  final submission readiness under the recorded wait policy.
- External evidence execution packets:
  `results/external_evidence_packets/packets.md`
  reports `ready`, 7 ready checks, 0 pending checks, and 0 failed checks. The
  packets cover the same two queue items and are local handoffs, not completed
  evidence.
- AAAI submission-decision preflight:
  `results/aaai_submission_decision/decision.md`
  reports `ready`, `selected_option=wait_for_external_evidence`, 27 ready
  checks, 0 pending checks, and 0 failed checks. This records the decision to
  wait; it does not complete the external evidence rows.
- AI-Scientist-v2 LLM-client smoke:
  `results/ai_scientist_v2_smoke/run_report.md`
  reports `complete`, 6 ready checks, 0 pending checks, and 0 failed checks.
- Protocol-specific direct provider probes:
  `results/openai_compatible_direct_probe/claude_family/run_report.md` reports
  `wire_api=anthropic_messages`, 4 ready checks, 2 pending checks, and 0 failed
  checks; `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` returned
  HTTP 502 `Upstream service temporarily unavailable`. The GPT-family report
  uses `wire_api=openai_responses`, has 3 ready checks, 2 pending checks, and 0
  failed checks; `gpt-5.5` and `gpt-5.4` returned HTTP 502
  `Upstream access forbidden`.
- AI-Scientist-v2 live-run handoff:
  `results/ai_scientist_v2_live_run_handoff/handoff.md`
  reports `complete`, 16 ready checks, 0 pending checks, 0 failed checks, and
  one completion directory.
- AAAI package:
  `results/reproducibility/aaai_package_report.md`
  reports ready, 17 ready checks, 0 failed checks.
- Usage examples:
  `results/reproducibility/usage_example_report.md`
  reports ready, 55 ready checks, 0 failed checks.
- DeepSeek follow-up handoff:
  `results/deepseek_followup_handoff/handoff.md`
  reports `responses_present`, 7 ready checks, 0 pending checks, and 0 failed
  checks.
- Model ablation response evaluation:
  `results/model_ablation_prompts/v0/evaluation.md`
  reports 6 total rows, 6 scored rows, 0 pending rows, and 1.0 average
  normalized score.
- Model response output-token proxy:
  `results/tables/model_response_cost_proxy.md`
  reports 6 total rows, 6 measured rows, 0 pending rows, 10,381
  character-proxy output tokens, and 9,594 `o200k_base` output tokens.
- Local token accounting evidence:
  `results/token_accounting/token_accounting_summary.md`
  reports 4,322 generated-skill input tokens, 95,303 full-extracted input
  tokens, 9,594 saved-response output tokens, and a 13,916 composite local
  token proxy.
- Live-transfer response evaluation:
  `results/live_transfer_prompts/evaluation.md`
  reports 24 total rows, 24 scored rows, 0 pending rows, and 1.0 average
  normalized score. AI Scientist-v2, Reflexion, and AIDE rows score 11/11;
  Toolformer rows score 9/9.
- Paper tables:
  `results/reproducibility/paper_table_report.md`
  reports ready, 278 ready checks, 0 failed checks after adding the SNAP
  executable-artifact follow-up table consistency checks alongside the
  real-reuse main, failure-boundary, SWE-T1 source-context follow-up, and Full
  Excerpt sanity checks.
- Paper claims:
  `results/reproducibility/paper_claim_report.md`
  reports ready, 20 ready checks, 0 failed checks.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md`
  reports ready, 16 ready checks, 0 failed checks.
- Real-reuse preflight:
  `results/real_reuse/spec_preflight.md`
  reports `ready_to_implement`, 8 tasks, 462 ready checks, and 0 failed checks
  after validating the REF prepared asset/runner layer, AIDE execution-layer
  contract, SWE-agent skill/execution-layer contracts, and SnapATAC2
  skill/execution-layer/prepared-asset contracts.
- Real-reuse first-pass run:
  `results/real_reuse/raw_rows.jsonl` and
  `results/real_reuse/main_results_plan.md` contain one GPT-family `gpt-5.5`
  Summary-vs-PaperToSkill pass for all eight rows. The derived
  `results/real_reuse/failure_analysis.md` maps the first-pass rows to
  boundary modes and follow-up method contracts. Latest main-table scores:
  AIDE-T1 0.816/0.817 (solved by both), AIDE-T2 0.000/0.826
  (PaperToSkill-only success), SWE-T1 0.000/0.000 due patch-apply failures,
  SWE-T2 0.000/1.000, REF-T1/T2 1.000/1.000, SNAP-T1/T2 0.000/0.500 and
  0.200/0.400 while failing the local success threshold. This is mixed
  downstream stress-test evidence and failure-boundary evidence, not aggregate
  effectiveness. AIDE Kaggle-derived CSV fixture files are kept local and
  ignored by git; committed manifests retain hashes and provenance boundaries.
- Current SWE-T1 stabilization boundary: preserve the first-pass SWE-T1
  0.000/0.000 patch-apply result as the paper-facing main-row evidence.
  Phase107 has already run as a paired shared-source-context follow-up and also
  scored 0.000/0.000, but both patches applied and then failed the hidden test.
  This is diagnostic follow-up evidence about task-contract/hidden-objective
  mismatch, not a replacement for the first-pass main row.
- Full Excerpt sanity check:
  `results/real_reuse/full_excerpt_sanity.md` contains AIDE-T1, SWE-T1, and
  SNAP-T1 rows with Summary/PaperToSkill/Full Excerpt scores and local
  whitespace token proxies. It is reviewer-question and cost/context sanity
  evidence only, not a main baseline or aggregate task-success claim.
- SNAP executable-artifact follow-up:
  `results/real_reuse/snapatac2_executable_artifact_followup.md` contains the
  phase108 paired controlled-scaffold diagnostic rows. All four rows score
  1.000, but this is execution-contract evidence only and not a main-row
  replacement.
- Real-reuse LLM ablation plan:
  `benchmarks/real_reuse/llm_ablation_v0.json` and
  `results/real_reuse/llm_ablation_plan.{md,json}` pre-register a stabilized
  AIDE-T2/SWE-T2/REF-T2 pilot over GPT-family `gpt-5.5`, Claude-family
  `claude-opus-4-8`, and DeepSeek-family `deepseek-v4-flash` with 300-second
  timeouts and 5 attempts. Phase109 has collected the GPT-family REF-T2
  ceiling/control pair; AIDE-T2, SWE-T2, Claude-family, and DeepSeek-family
  rows remain pending.
- Real-reuse LLM ablation aggregation:
  `results/real_reuse/llm_ablation_summary.md`,
  `results/real_reuse/llm_ablation_summary.json`, and
  `results/real_reuse/llm_ablation_raw_rows.csv` aggregate only
  pre-registered run IDs; pending rows are not negative evidence.

## Model/API Configuration

Never commit raw API keys to tracked files. Use environment variables or local
shell-only values.

Claude-family profile:

- Direct Claude diagnostics and local Claude Desktop/CC Switch routing use
  Anthropic Messages at base URL `https://coderxiaoc.com`, request path
  `/v1/messages`, and `anthropic-version: 2023-06-01`.
- Current direct-probe aliases: `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6`. The older dotted spelling `claude-opus-4.8` remains in
  historical reports only; do not use it in new direct-probe handoff commands.
- Key source: local environment variable, e.g.
  `AI_SCIENTIST_OPENAI_API_KEY`; never commit raw keys.
- Latest direct provider probe for the AI-Scientist-v2 evidence path used
  `PAPERTOSKILL_CLAUDE_BASE_URL=https://coderxiaoc.com`,
  `PAPERTOSKILL_CLAUDE_API_KEY`, Anthropic Messages, and aliases
  `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`; all returned
  HTTP 502, so no fresh direct-probe response file exists.
- Scored Claude model-ablation rows come from previously saved responses; do
  not describe the latest Claude protocol refresh as a fresh success.

GPT-family profile:

- Direct GPT diagnostics use OpenAI Responses at base URL
  `https://coderxiaoc.com/v1` and request path `/responses`.
- Key source: local environment variable, e.g.
  `PAPERTOSKILL_GPT_OPENAI_API_KEY`.
- Latest catalog evidence with the separate GPT key lists `gpt-5.5`,
  `gpt-5.4`, and other GPT-family models.
- Current protocol-refresh evidence: GPT-family completed both current prompt
  rows with `gpt-5.5` through OpenAI Responses and both saved responses score
  6/6. Older Phase 37 fallback evidence remains historical only.

DeepSeek:

- `deepseek_followup_slot` is currently configured as `deepseek-v4-flash`.
- Current DeepSeek run completed both two-case protocol rows through
  OpenAI-compatible Chat Completions; both saved responses score 6/6.
- The runner skips the slot only if its alias is reset to
  `deepseek-to-be-filled`.
- Use `scripts/check_deepseek_followup.py --strict` before and after future
  edits to verify prompt rows, response paths, env names, and saved responses.

## Engineering/Fix History To Preserve

| Area | Problem Found | Fix / Current Location |
| --- | --- | --- |
| Extractor parsing | Multiline list items split into fragments; title inferred as `Methods`. | Merge continuation lines and infer title from H1/LaTeX title in `scripts/papertoskill_extract.py`; covered by `tests/test_papertoskill_extract.py`. |
| Extractor recall | AIDE exposed truncation of workflow/validation/failure bullets. | Increased candidate limits in `scripts/papertoskill_extract.py`; regression test keeps richer bullets. |
| Numbered continuations | Indented numbered continuations inside wrapped bullets became new bullets. | Treat only unindented list markers as new bullets in `scripts/papertoskill_extract.py`. |
| Source-span anchors | `pdftotext` form-feed characters shifted line anchors. | Use newline-delimited counting in `scripts/validate_source_spans.py`; covered by tests. |
| Source-map audit | First source-map audit mis-mapped section groups and scored all cases badly. | Map skill sections to source-note section groups in `scripts/audit_skill_source_map.py`. |
| Auto-note scaffold | Toolformer auto-note initially mixed two-column PDF text/references and exceeded compactness. | Preserve raw line spacing, split likely columns, prefer keyword-bearing column, shorten snippets in `scripts/papertoskill_note_from_text.py`. |
| AIDE auto-note | Toolformer profile was semantically poor on AIDE; figure captions and related-work snippets leaked in. | Added `--profile aide`, target-section-first selection, overlap exception for shared AIDE caveat. |
| Pipeline ergonomics | The extracted-text-to-note-to-skill workflow required three manual commands. | Added `scripts/papertoskill_pipeline.py` to write note, skill, source map, rubric report, and manifest in one local command. |
| PDF pipeline input | Users needed a smoke-tested direct PDF entry point without claiming robust PDF understanding. | `scripts/papertoskill_pipeline.py` accepts `.pdf` sources through `pdftotext -layout`, records extracted text in the manifest, and remains bounded as local smoke support. |
| Human fidelity | Blank annotation rows could be mistaken for negative scores, and appended second-reviewer rows could make a fully covered review look pending. | `scripts/summarize_human_fidelity_annotations.py` marks blanks as pending and now judges completion by 24 paper-by-criterion cells while allowing distinct-reviewer duplicate rows. |
| Reproducibility | Local package readiness was conflated with external live/human evidence. | `scripts/check_reproducibility_package.py` uses ready/pending/fail statuses. |
| AAAI package | File presence was weaker than checking the actual author kit/build state. | `scripts/check_aaai_package.py` checks SHA256, style use, fresh PDF/log/BibTeX, unresolved markers. |
| Usage examples | Markdown examples could drift from executable paths. | `scripts/check_usage_examples.py` validates files, prompt slots, and offline AIDE example chain. |
| Paper tables | LaTeX table values could drift from CSV results. | `scripts/check_paper_tables.py` compares `paper/aaai/papertoskill_tables.tex` with generated CSVs. |
| Paper claims | Draft/AAAI text could overclaim pending evidence. | `scripts/check_paper_claims.py` checks unsupported positive claims and required boundary statements. |
| Goal completion | Narrative completion audit could stale. | `scripts/check_goal_completion.py` makes the active-goal status machine-checkable. |
| External evidence closure | Pending requirements were spread across multiple reports and docs. | `scripts/check_external_evidence_closure.py` maps current pending goal requirements to concrete queue items without claiming evidence completion. |
| External evidence execution | Closure queue items still required manual interpretation before handoff. | `scripts/check_external_evidence_packets.py` turns each queue item into inputs, commands, completion criteria, and escalation boundaries without claiming evidence completion; the AAAI decision packet now routes final-decision recording through `scripts/generate_aaai_submission_decision.py`. |
| AAAI submission decision | The final submission item was only a checklist row. | `scripts/check_aaai_submission_decision.py` creates a preflight report with submit-now vs wait-for-evidence options while keeping the human decision pending. |
| AAAI decision record | A human decision record could be hand-written with drift, unavailable options, or secret-like fields. | `scripts/generate_aaai_submission_decision.py` writes the record only after an explicit option, owner, date, claim boundary, and evidence policy; it validates option availability and rejects raw API-key-like material. |
| AAAI gate recursion | The decision preflight and goal/package gates can read each other during report refreshes, causing self-referential intermediate failures. | `scripts/check_aaai_submission_decision.py` treats only the known self-referential failure set as pending during its own preflight; regression covered by `tests/test_check_aaai_submission_decision.py`. |
| Model evidence state | GPT retry evidence was saved separately from the older Phase 36 failure report. | `scripts/check_goal_completion.py` reads both `run_report.json` and `gpt_retry_run_report.json` so historical GPT 502 evidence and current GPT-family success both remain visible. |
| Output-token accounting | Cost section had input-token proxies but no saved-response output-token accounting. | `scripts/evaluate_model_response_costs.py` reports local output-token proxies for saved Claude/GPT-family responses while preserving the no-provider-billing boundary. |
| AI-Scientist-v2 smoke boundary | AI-Scientist-v2 dry-run and live-transfer saved responses could be confused with a full live run. | `scripts/run_ai_scientist_v2_smoke.py` records bounded client smoke attempts with alias fallback, script-level timeout, and a tiny-request `--max-tokens` cap; the current marker-contract smoke is complete, but it remains separate from human fidelity and broad live task success. |
| Direct provider diagnosis | AI-Scientist-v2 smoke timeouts could be misread as only a wrapper bug or as only a model-name issue. | `scripts/run_openai_compatible_direct_probe.py` is protocol-aware: Claude-family direct diagnostics use Anthropic Messages (`/v1/messages`) and GPT-family direct diagnostics use OpenAI Responses (`/v1/responses`) with the same marker contract. Historical provider blockers are diagnostics; the bounded smoke/full live-run evidence is now complete. |

## Persistent Rules

- On resume, read both memory files first.
- Use `rg`/`rg --files` for search.
- Use `apply_patch` for manual edits.
- Do not revert user/local changes, especially in `ai-scientist-v2`.
- Keep exploratory notes, active work, and validated claims separate.
- Promote claims only when backed by files, tests, logs, or explicit user
  decisions.
- Before phase saving, run relevant tests/checkers, `git diff --check`, and a
  raw-key scan.

## Model Interface Facts

- GPT provider style follows OpenAI Responses API.
- GPT BaseURL: `https://coderxiaoc.com/v1`.
- GPT models confirmed usable: `gpt-5.5`, `gpt-5.4`.
- Claude provider style follows Anthropic Messages API.
- Claude BaseURL: `https://coderxiaoc.com` with request path `/v1/messages`.
- Claude models confirmed usable: `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`.
- 2026-06-30 verification: the local Desktop docs in `C:\Users\19351\Desktop\tem`
  are runnable. GPT doc returned HTTP 200 on the first attempt for
  `gpt-5.5` and `gpt-5.4` via `POST /v1/responses`. Claude doc returned HTTP 200
  on the first attempt for `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6` via `POST /v1/messages`.
- DeepSeek temporary key verified on 2026-06-30:
  `GET https://api.deepseek.com/models` returned `deepseek-v4-flash` and
  `deepseek-v4-pro`; `POST https://api.deepseek.com/chat/completions`
  succeeded for both models; `deepseek-v4-flash` returned visible content `ok`
  on a slightly larger max-tokens probe.
- 2026-07-01 re-test of the three Desktop API docs: GPT doc still runnable
  (`gpt-5.5` HTTP 200 on attempt 2, `gpt-5.4` HTTP 200 on attempt 1, both
  returned `ok`); DeepSeek doc runnable (`deepseek-v4-flash` and
  `deepseek-v4-pro` both HTTP 200 on attempt 1, returned `ok`); Claude doc did
  not complete as a direct HTTP request in this run (`claude-opus-4-8`,
  `claude-opus-4-7`, and `claude-opus-4-6` returned HTTP 502 after five
  attempts with both the regular doc key and Desktop token). Treat this as
  current upstream/direct-request unavailability, not proof of bad model names.
- 2026-07-01 same-day Claude-only re-test: the regular Claude doc key worked
  for `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6` via
  `POST https://coderxiaoc.com/v1/messages`; all returned HTTP 200 on attempt 1
  with visible `ok`. The same regular key also worked with the Claude
  Code/Desktop beta header. The Desktop direct provider token still returned
  HTTP 502 after five attempts for all three aliases.
