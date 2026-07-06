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
- AAAI package checks now include the local page-limit guard: total PDF pages
  must stay at or below 9 and non-reference content must end by page 7. The
  cost-proxy and auto-note tables are retained in
  `paper/aaai/papertoskill_supporting_tables.tex` for package/table drift
  checks, but they are not included as main-PDF floats.
- Paper-facing claim discipline includes AAAI table files, not only the main
  TeX body. The main real-reuse caption must keep the eight locked
  `main_run_selection.json` rows as the paper-facing scope and must not use
  draft/planning language such as "future reruns or additional rows may be
  added".
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
- Latest locally recorded remote checkpoint is
  `5063eed45499c204c85b72d15850b9cf7d359fea refs/heads/main`
  (`5063eed Clarify human fidelity study boundary`). It is independently
  remote-verified as of the 2026-07-06 retry. It does not call SNAP-T2,
  append raw rows, replace `main_run_selection.json`, touch local logs,
  complete Claude-family rows, complete human fidelity, or strengthen
  paper-facing effectiveness claims. The recovered backup includes the earlier
  human-boundary record-sync/push-blocker chain plus the paper-facing
  ambiguity cleanup in `paper/draft.md` and the AAAI TeX. The earlier substantive paper/package
  gate checkpoint after the AAAI page-limit,
  paper-finalization, outline-sync recovery, outline claim-drift gate,
  main-results boundary cleanup, real-reuse LLM-ablation handoff guard,
  recovered checkpoint-sync records, outline evidence-boundary sync,
  limitations-claim gate, model-response cost-boundary sync, stale cost-scope
  claim guard, checkpoint-record guard sync, pre-submission gate rerun,
  paper-conclusion boundary sync, compact SNAP executable-candidate prompt
  contract, follow-up record-sync/blocker metadata, recovered Claude
  availability metadata, recovered Claude metadata backup records, and the
  external-evidence handoff-boundary guard is
  `7efa4b72d41c61be8c0b0139e2ae76317fb84413 refs/heads/main`
  (`7efa4b7 Guard external evidence handoff boundary`). The latest
  experiment-facing content checkpoint inside that chain remains
  `245c2b2 Prepare compact SNAP candidate prompts`; it includes the compact
  SNAP prompt plan and package/checker records. The `7efa4b7` phase adds a
  submission-review guard for two pending-external-evidence items and keeps
  the 19-ready review handoff synchronized; it does not call a model, score
  outputs, append raw rows, or replace main rows. The
  earlier `e57df72` checkpoint includes the
  limitations claim gate that covers `paper/limitations.md` with 51 ready
  paper-claim checks / 0 failed checks, the full 209-test verification for
  that gate, and
  the follow-up paper-facing cost-boundary sync that states the saved-response
  output-token proxy covers six Claude/GPT-family/DeepSeek model-ablation rows
  with 9,594 `o200k_base` output tokens. It also includes the follow-up
  stale cost-scope guard with 56 ready paper-claim checks / 0 failed checks,
  full unit discovery at 210 tests OK, and the checkpoint-record guard sync
  that moves current remote-checkpoint reports from stale `5786d7d` wording to
  `43f9092`, plus the recovered checkpoint blocker records, pre-submission
  gate rerun record, and paper-conclusion boundary sync that keeps future-work
  wording aligned with locked real-reuse rows and pre-registered paired
  follow-ups. It also includes the earlier outline
  update that distinguishes collected/scored saved-response rows from
  unsupported human semantic fidelity, provider billing, and live downstream
  task-success claims; the submission-review handoff guard that separates the
  older saved-response model ablation from the auxiliary real-reuse LLM
  ablation; the refreshed submission-review guard that also requires the two
  pending-external-evidence items, human-fidelity pending state, and
  `wait_for_external_evidence` decision; the current `19 ready / 0 failed`
  submission-review report; memory/runbook/result-card synchronization; and the previous recovered
  checkpoint chain through `905899c`, `1a7ae8c`, and `00d32cd`. The earlier
  `00d32cd` checkpoint includes the phase116 SNAP-T2 provider-block chain, the
  auxiliary family summary table, the AAAI page-limit repair, the
  draft-language claim gate over the AAAI table file, submission-record sync,
  the full pre-submission unit-test regression fix, refreshed paper/package/
  submission reports, paper-outline LLM-ablation status sync, the earlier
  38-check paper-outline claim gate, the main-results/failure-analysis raw-row
  provenance refresh to 40 raw rows, and the recovered GitHub transport record
  for `21009eb`.
  Claude-family real-reuse LLM-ablation rows remain
  provider-pending because `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6` all still returned provider HTTP 502 in the latest direct
  availability rechecks. Treat those 502s as provider availability metadata,
  not model-quality evidence or scored real-reuse failures. Older named
  checkpoint notes in this memory are historical recovery checkpoints; the
  earlier failed pushes for `501ffc8`, `48aabac`, `8bdd394`, `95f1af3`,
  `66e4763`, `45ef25b`, and `0538ef1` are historical GitHub transport
  metadata now that later recovery checkpoints are verified remote-backed.
  Verify the exact current local/remote state with `git status -sb`,
  `git log -5 --oneline`, and a successful `git ls-remote --heads origin main`
  before claiming any later phase is remote-backed.
- Follow-up local record-sync commit `cc13abb Record verified human boundary
  backup` updates records to the verified human-boundary backup. Its first
  remote backup and immediate remote check both failed with `Recv failure:
  Connection was reset`. Treat this as GitHub transport metadata only; no
  human `ok.txt` is required for GitHub status.
- Historical follow-up local record-sync commits `a9740f7 Record verified GPT
  probe checkpoint`, `1e32f5f Record GPT checkpoint push blocker`, and
  `51c91bb Record renewed GPT checkpoint push blocker` recorded failed backup
  attempts after the GPT direct-provider metadata checkpoint. Their earlier
  port-443 errors are GitHub transport metadata only, not experiment or
  paper-content failures. The later `98ba943` push recovered that chain; do not
  create human `ok.txt` for GitHub status.
- The earlier human-boundary record-sync and push-blocker commits first hit
  GitHub connection-reset / port-443 transport failures, but the later
  2026-07-06 push and independent remote check recovered the chain through
  `5063eed`. Treat those failures as GitHub transport metadata only; do not
  create human `ok.txt` for GitHub status.
- Recovered outline-guard backup: `fd49a53 Guard outline real-reuse future
  work`, `12f676b Record outline guard push blocker`, and `b20eaa7 Record
  renewed outline guard push blocker` are now remote-backed. `git push origin
  main` advanced `main` from `6cef41e` to `b20eaa7`, and `git ls-remote
  --heads origin main` verified
  `b20eaa7c96003523f41140a5c15a6f8ae91daa41 refs/heads/main`. This is
  paper-outline boundary and GitHub transport/recovery metadata only; it does
  not change experiments, raw rows, `results/real_reuse/main_run_selection.json`,
  local logs, or paper-facing claim strength. Earlier port-443 and
  connection-reset failures are historical GitHub transport metadata only; no
  human `ok.txt` is required for GitHub status.
- Follow-up record-sync commit `a667264 Record recovered outline guard backup`
  records the recovered `b20eaa7` outline-guard backup in repo memory. Its
  `git push origin main` reported success and local `origin/main` now points
  to `a667264`, but two immediate independent `git ls-remote --heads origin
  main` checks failed with port-443 connectivity and then connection reset.
  Treat this as GitHub transport verification metadata only. Follow-up
  verification-blocker commit `f677bb2 Record outline backup verification
  blocker` first failed to push with `Recv failure: Connection was reset`, but
  a later retry recovered the chain: `git push origin main` advanced `main`
  from `a667264` to `f677bb2`, and `git ls-remote --heads origin main`
  verified `f677bb2e2270b5289ace02b6509e13e3ece20e66 refs/heads/main`. No
  human `ok.txt` is required for GitHub status.
- Follow-up record-sync commit `3b0b8a5 Record verified outline backup
  recovery` records the verified `f677bb2` recovery in repo memory. `git push
  origin main` advanced `main` from `f677bb2` to `3b0b8a5`, and `git
  ls-remote --heads origin main` verified
  `3b0b8a50aa032bb68c9cec55ec3acb599c69548c refs/heads/main`. This is
  record-sync/GitHub recovery metadata only and does not change experiment
  scores, raw rows, `results/real_reuse/main_run_selection.json`, local logs,
  or paper-facing claim strength.
- Current local record-sync commit `c09850d Sync verified outline backup
  records` propagates the verified `3b0b8a5` checkpoint into repo runbook and
  goal-audit records. Its first `git push origin main` failed with `Failed to
  connect to github.com port 443 after 21094 ms`, and the immediate
  `git ls-remote --heads origin main` failed with port-443 connectivity after
  21133 ms. Treat this as GitHub transport metadata only; no human `ok.txt` is
  required for GitHub status.
- Follow-up blocker-record commit `259f708 Record verified outline records
  push blocker` is now recovered and remote-verified. A later `git push origin
  main` advanced `main` from `3b0b8a5` to `259f708`, and `git ls-remote
  --heads origin main` verified
  `259f708a8d9ed42e390566f38ca027a748b15e9f refs/heads/main`. This is
  GitHub transport/recovery metadata only and does not change experiments,
  raw rows, `results/real_reuse/main_run_selection.json`, local logs, or
  paper-facing claim strength.
- Follow-up record-sync commit `0a25da3 Record compact prompt checkpoint
  backup` updates checkpoint records to the verified `245c2b2` compact SNAP
  prompt checkpoint. Its first `git push origin main` and immediate
  `git ls-remote --heads origin main` both failed with `Recv failure:
  Connection was reset`. Follow-up blocker-record commit `a7a9e3e Record
  compact checkpoint push blocker` was later pushed and independently verified
  at `a7a9e3e772883e76404ee217a9ed51278c4c2477 refs/heads/main`. Treat the
  earlier failure as GitHub transport metadata only.
- Follow-up record-sync commit `b770e20 Record verified compact checkpoint
  recovery` was pushed and independently verified at
  `b770e2005bd881c4afa31be2571cfb01d5207971 refs/heads/main`. Later commits
  `8ac4ddf Refresh Claude availability metadata` and `39c4e0f Record Claude
  availability push blocker` are now independently remote-verified at
  `39c4e0ff7a5d500d3250ea7f6dd177a00672fa95 refs/heads/main`. `8ac4ddf`
  records a 2026-07-06
  Claude direct availability probe where all three Claude aliases again
  returned provider HTTP 502 with `max_tokens=16` and a 180-second timeout.
  Its first `git push origin main` and immediate `git ls-remote --heads origin
  main` both failed with `Recv failure: Connection was reset`, but the later
  push and independent remote check recovered the backup; treat the earlier
  failure as GitHub transport metadata and the HTTP 502s as provider
  availability metadata only.
- Follow-up local commits `3ee014a Record recovered Claude metadata backup` and
  `91261dd Record Claude metadata backup push blocker` were later pushed and
  independently remote-verified at
  `91261dd145771f3325ed398d5d773d57b791ddb6 refs/heads/main`. They update
  current checkpoint records to the verified `39c4e0f` Claude availability
  metadata checkpoint and record the first failed retry. Their earlier
  `Recv failure: Connection was reset` push failures are GitHub transport
  metadata only.
- Follow-up local record-sync commit
  `3e71736 Record external boundary checkpoint backup` records the verified
  `7efa4b7` checkpoint in memory/runbook/goal-audit reports. Its first
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  the immediate `git ls-remote --heads origin main` failed with
  `Failed to connect to github.com port 443 after 21087 ms`. Treat this as
  GitHub transport metadata only; no human `ok.txt` is required.
- Record-only push recovery after that blocker: `deeb84e Record external
  checkpoint push blocker` was later pushed and `git ls-remote --heads origin
  main` verified
  `deeb84e77d2baa409b369281a0fdc07556a5edcd refs/heads/main`. This recovered
  the `3e71736` backup record and the `deeb84e` blocker record as transport/
  checkpoint metadata only. The declared substantive checkpoint for paper,
  package, and goal gates remains `7efa4b7 Guard external evidence handoff
  boundary`; `deeb84e` does not add experiment scores, raw rows, main-row
  selection changes, model calls, or local-log changes.
- Resume git check on 2026-07-06 before this continuation observed
  `d3f7cb299221923501fa9ccd6897c5f9d664daed refs/heads/main`
  (`d3f7cb2 Record external checkpoint recovery`) on `origin/main`. That
  commit is record-only recovery metadata on top of `deeb84e`; it does not add
  experiment scores, raw rows, main-row selection changes, model calls, or
  local-log changes. Keep `7efa4b7 Guard external evidence handoff boundary`
  as the declared substantive checkpoint for paper/package/goal gates, and
  rerun `git status -sb`, `git log -5 --oneline`, and
  `git ls-remote --heads origin main` before claiming any newer backup state.
- Local phase-save commit `c659519 Record resume checkpoint baseline` records
  the `d3f7cb2` resume baseline while keeping `7efa4b7` as the substantive
  checkpoint. Its first `git push origin main` failed with
  `Failed to connect to github.com port 443 after 21115 ms`; this is GitHub
  transport metadata only and does not require human `ok.txt`.
- A later push recovered `c659519 Record resume checkpoint baseline` and
  `fff973d Record resume checkpoint push blocker`; `git ls-remote --heads
  origin main` verified
  `fff973d72bf88a7ba7b0a57f70c8ece5028d2aae refs/heads/main`. This is
  record-only checkpoint/transport metadata and does not change experiments,
  raw rows, main-row selection, model calls, local logs, or paper-facing claim
  strength.
- Recovered follow-up phase-save checkpoint after the `5786d7d` remote baseline:
  `8449799 Guard limitations claim boundary` extends the paper-claim gate to
  `paper/limitations.md`, refreshes the paper-claim/package/submission-review
  records to 51 ready paper-claim checks and 0 failures, and records full unit
  discovery at 209 tests OK. Its first `git push origin main` failed with
  `Recv failure: Connection was reset`, and the immediate `git ls-remote
  --heads origin main` failed with `Failed to connect to github.com port 443
  after 21108 ms`. A push retry after the blocker-record commit also failed
  with `Failed to connect to github.com port 443 after 21094 ms`. A later
  `git push origin main` recovered `8449799`, `6823179`, and `5aa4195`, and
  `git ls-remote --heads origin main` verified
  `5aa4195f4636c1d8c5994ee1eb6c4f6949279eb8 refs/heads/main`. Treat the
  earlier failures as GitHub transport metadata only.
- Follow-up guard checkpoint `43f9092 Guard model response cost scope` extends
  the paper-claim checker with a stale saved-response cost-scope pattern so
  paper-facing text cannot revert to Claude/GPT-family-only wording for
  evidence that now covers Claude/GPT-family/DeepSeek rows. It refreshes the
  paper-claim/package/submission-review records to 56 ready paper-claim checks
  and 0 failures, and full unit discovery reports 210 tests OK. `git push
  origin main` succeeded, and `git ls-remote --heads origin main` verified
  `43f9092c32a614d882199d5111fe21cc5cb19f8e refs/heads/main`.
- Follow-up record-sync commit `93a2abf Record model cost guard backup`
  updates memory to the verified `43f9092` remote-backed checkpoint. Its first
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  the immediate `git ls-remote --heads origin main` failed with the same reset
  error. A later `git push origin main` recovered this record-sync commit
  together with `af3ba31`, `4a85147`, and `3e18fc5`; `git ls-remote --heads
  origin main` verified
  `3e18fc5d58ebcf8f791e82c737d3f64457e886e1 refs/heads/main`. Treat the
  earlier failure as GitHub transport metadata only; no human `ok.txt` is
  required.
- Follow-up blocker-record commit `af3ba31 Record model cost guard push blocker`
  records that transport failure. Its first push retry failed with
  `Failed to connect to github.com port 443 after 21063 ms`, and the immediate
  `git ls-remote --heads origin main` failed with port-443 connectivity after
  21117 ms. A later push recovered this blocker record; treat the earlier
  failure as GitHub transport metadata only.
- Checkpoint-record guard sync checkpoint `3e18fc5 Sync checkpoint record guard`
  refreshes the short-memory declared
  checkpoint, runbook, goal-completion audit, and generated goal-completion
  report so the current remote checkpoint is `43f9092 Guard model response
  cost scope` rather than stale `5786d7d` wording. It also extends
  `scripts/check_goal_completion.py` to parse the newer "latest verified
  substantive checkpoint" wording. This is record/guard work only and does
  not change experiments, raw rows, `results/real_reuse/main_run_selection.json`,
  or local logs. `git push origin main` succeeded, and `git ls-remote --heads
  origin main` verified
  `3e18fc5d58ebcf8f791e82c737d3f64457e886e1 refs/heads/main`.
- Follow-up record-sync commit `4ae3e76 Record recovered checkpoint guard
  backup` saves the recovered checkpoint-record state after the current resume.
  `git push origin main` reported success and advanced `main` from `3e18fc5`
  to `4ae3e76`, and local status was clean against `origin/main`. Independent
  `git ls-remote --heads origin main` verification failed twice afterward
  with a connection reset and then port-443 connectivity failure after
  21095 ms. Treat this as GitHub transport metadata only; do not create
  human `ok.txt` for GitHub status, and do not claim `4ae3e76` is
  independently remote-verified until a later `ls-remote` succeeds.
- Follow-up blocker-record commit `a72c6d2 Record checkpoint guard verification
  blocker` records the failed independent remote-verification checks after the
  successful `4ae3e76` push. Its first `git push origin main` failed with
  `Failed to connect to github.com port 443 after 21060 ms`. Treat this as
  GitHub transport metadata only and do not create human `ok.txt` for GitHub
  status.
- Remote backup later recovered through `bd3fe6e Record pre-submission gate
  rerun`: `git push origin main` advanced `main` from `4ae3e76` to `bd3fe6e`,
  and `git ls-remote --heads origin main` verified
  `bd3fe6e5906411dc23d712d33fabb10a26c6c164 refs/heads/main`. This recovery
  includes `a72c6d2`, `dfd5602`, and `bd3fe6e`; earlier reset and port-443
  failures remain GitHub transport metadata only.
- Paper-conclusion boundary sync checkpoint `e57df72 Align paper conclusion
  with locked-row evidence` updates the AAAI conclusion, Markdown draft,
  submission checklist, review report, memory, runbook, goal audit, rebuilt
  PDF, and refreshed goal/AAAI reports so future work says to stabilize locked
  rows with pre-registered paired follow-ups rather than generically repeat or
  expand real-reuse runs. `git push origin main` succeeded, and `git ls-remote
  --heads origin main` verified
  `e57df723bb8bc147626a6769cb2e765311ad6e13 refs/heads/main`.
- A follow-up record-sync/blocker chain updates memory, runbook, goal audit, and
  goal-completion report records to the verified `e57df72` paper-conclusion
  boundary checkpoint. Its first `git push origin main` and immediate
  `git ls-remote --heads origin main` both failed with `Recv failure:
  Connection was reset`. Treat this as GitHub transport metadata only; keep the
  remote-backed baseline at `e57df72` until a later push and independent remote
  check succeed.
- A later `git push origin main` reported success for that local
  record-sync/blocker/Claude-availability chain and local `origin/main` equals
  `HEAD`, but two immediate independent `git ls-remote --heads origin main`
  checks both failed with `Recv failure: Connection was reset`. Treat this as
  GitHub verification-transport metadata only; keep `e57df72` as the latest
  independently verified remote-backed baseline until a later remote check
  succeeds.
- Follow-up record-sync commit `45ef25b Sync remote checkpoint after LLM handoff
  guard` and blocker note `0538ef1 Record checkpoint sync push blocker`
  initially failed to back up because GitHub HTTPS transport was unavailable.
  A later push recovered those commits along with `5786d7d Sync outline
  evidence boundary`, and `git ls-remote --heads origin main` verified
  `5786d7d8538a3fd856d98f09619fbc5447c9ebed refs/heads/main`. Treat the
  earlier failures as GitHub transport metadata only.
- Recovered AAAI page-limit backup note: the first push for the page-limit
  repair and its immediate remote check both failed with `Recv failure:
  Connection was reset`, but a later push recovered and verified the current
  remote checkpoint. Treat the earlier reset as GitHub transport metadata; do
  not count it as experiment or paper-content failure.
- Recovered record-only checkpoints after that verification:
  `b3441d5 Sync phase115 checkpoint records` and `cea43eb Record checkpoint
  sync push blocker` initially followed a GitHub reset, but the later phase116
  push recovered and verified `96fce87`. Treat earlier reset errors as GitHub
  transport metadata, not experiment correctness.
- Current resume checkpoint commits are `4532dd9 Sync resume checkpoint
  memory`, `bf95213 Record resume memory push blocker`, `69d23b1 Record
  recovered resume memory backup`, `f1c50d5 Sync resume baseline memory`, and
  `4d2e040 Clarify resume remote memory baseline`. They record the
  current resume verification and a temporary GitHub transport failure:
  `git push origin main` failed with `Recv failure: Connection was reset`, and
  `git ls-remote --heads origin main` failed with `Failed to connect to
  github.com port 443 after 21100 ms`. Later pushes succeeded and the local
  tracking ref later advanced through `bddd900`; the quality-grounding table
  completion, claim-boundary cleanup, blocker-record continuation, and
  claim-evidence-matrix boundary sync, plus the follow-up record-sync and
  Claude direct availability recheck commits, are now verified as
  remote-backed through that checkpoint.
- Follow-up record-sync commit `e2f070e Record recovered claim matrix backup`
  initially remained local-only after `git push origin main` failed with
  `Recv failure: Connection was reset`; a later GitHub retry pushed it along
  with `e110a03` and `bddd900`, verified by `git ls-remote --heads origin
  main` at `bddd9006523a30b152da69a75f002d7948ff0269 refs/heads/main`.

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
  Paper-facing claim records treat this as auditable traceability evidence, not
  proof of a causal reproducibility improvement.
- Real-reuse failure-boundary analysis is derived from the same first-pass raw
  rows and is now included in the AAAI table set. It maps row-level outcomes to
  PaperToSkill-only success, patch application, solved-by-both ceiling, and
  artifact completion modes. This is explanatory boundary analysis, not new
  task-success evidence. The main-table and failure-boundary builders now emit
  row-selection metadata into Markdown/JSON outputs so
  `results/real_reuse/main_run_selection.json` is visible as the source of the
  16 paper-facing row selections.
- Human-fidelity annotation handoff is ready: review packets, annotation guide,
  reviewer bundle zip, checksum manifest, stricter blank template metadata,
  and strict summarizer validation are present for 24 paper-by-criterion cells;
  completed human annotation remains pending.
- Local token accounting handoff is ready: input-token and saved-response
  output-token proxy summaries are present, and the composite local token
  proxy is ready for reuse.
- Claude Opus 4.8, GPT-family, and DeepSeek model-ablation prompt rows are
  saved and scored for the older two-case protocol. GPT-family protocol
  refresh completed both rows with `gpt-5.5`; DeepSeek completed both rows with
  `deepseek-v4-flash`. The latest Claude protocol refresh used Anthropic
  Messages but was blocked by provider HTTP 502, so scored Claude rows in that
  older protocol come from previously saved response files.
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
  queue items for the current policy. The closure queue still reports
  `overall_status=pending_external_evidence` because both next-action items
  remain external evidence, even though the local queue checks are ready.
- External evidence execution packets are ready as a local handoff artifact:
  each closure item has inputs, setup notes, commands, validation commands,
  completion criteria, escalation rules, and evidence boundaries without
  completing any external evidence. The AAAI submission-decision packet uses
  the validated decision-record helper and requires a validated
  `research/aaai_submission_decision.md` record before final goal/package
  checks can clear `aaai_final_submission_ready`. The human-fidelity packet
  must also declare the desktop `toHuman.md` / `ok.txt` workflow and agent-side
  `ok.txt` cleanup after processing completed annotations.
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
- Phase109 substantive experiment and subsequent record-sync evidence was
  saved through the LLM-ablation, row-selection, SNAP contract, SWE-T1
  task-contract, SWE-T1 issue-aligned contract, and SWE runner override-support
  commits. This range includes `e597fcf` (AIDE-T2 GPT-family LLM ablation),
  `1521b72` (AIDE push-blocker record), `200419a` (SWE-T2 GPT-family LLM
  ablation), `cb20cb1` (SWE push-blocker record), `bc9644a`
  (status-hash-churn guard), `ea15664` (DeepSeek-family LLM ablation rows),
  `ea0f016` (memory sync after DeepSeek LLM ablation), `0d4934b`
  (Claude-family availability evidence), `977b2b9` (experiment-planning
  record sync), `7ee44ad` (pending-row availability metadata in the LLM
  ablation summary), `d248878` (core real-reuse stabilization records),
  `f44da1b` (real-reuse planned-output guard), and `641eef0` (memory sync
  after the guard), `4b606f9` (row-selection metadata in real-reuse main and
  failure-boundary outputs), `43bc1a0` (record of the transient push blocker),
  `a170aa6` (push-status sync), `03b7ca4` (core stabilization queue),
  `25017a8` (SNAP executable-candidate contract), `36ae48e` (SWE-T1
  task-contract decision), `ef7dc1b` (memory sync after contract decisions),
  `cdf67b9` (SWE-T1 issue-aligned contract), `0f3a499` (SWE scorer override
  support), `599382d` (SWE-T1 issue-aligned follow-up table), `12e97df`
  (phase110 GitHub push blocker), `24f8029` (phase110 push-status memory
  clarification), `cdeab1f` (phase110 diagnostic paper/memory clarification),
  `c7d55b7` (recovered GitHub backup status), `2a61d42` (Claude-family
  ablation retry availability), `12fab77` (Claude retry push blocker),
  `9888f17` (bounded summary-comparison claim cleanup), `1ab714f` (current
  project record sync), `2b5d9d0` (GitHub backup recovery record), and
  `05b3963` (real-reuse record-boundary tightening), `77e8ada` (SNAP
  executable-candidate runner), `0983fbc` and `c4b4b99` (GitHub push-blocker
  records), `2490a9b` (real-reuse stabilization queue sync), `0832201`
  (memory sync after GitHub retry), `ef8cbe0` (SNAP executable-candidate
  prompt packets), `9829123` (SNAP executable-candidate live diagnostics), and
  `db535e7` (SNAP diagnostic checkpoint record), `fb0baed` (remote-status
  sync), `b6dc061` (phase112 SNAP executable-candidate diagnostic/table/
  package completion), `2b823f6` (tightened submission-review count checks),
  `ef2bcf7` (submission-review push blocker record), `b550a26` (AAAI
  paper-text synchronization for the SNAP executable-candidate diagnostic),
  `1727615` (recovered submission-review backup), `01dfa6e` (draft/outline
  SNAP diagnostic sync), `206fa5c` (human-fidelity annotation request),
  `4532dd9` (resume checkpoint memory sync), and `bf95213` (resume memory
  push-blocker record), and `69d23b1` (recovered resume-memory backup).
  The temporary 2026-07-05 GitHub HTTPS transport blocker recovered again; the
  resume-baseline remote checkpoint for this continuation is
  `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`. Verify exact
  local/remote alignment with
  `git status -sb`, `git log -5 --oneline`, and
  `git ls-remote --heads origin main` before claiming any later remote-backed
  phase save.
- Core real-reuse stabilization guard commit `f44da1b` (`Guard real-reuse
  planned outputs`) is pushed after the record-sync save. It removes the
  deprecated `domain_robustness` planned output from
  `benchmarks/real_reuse/real_reuse_v0.json`, checks current real-reuse output
  paths in `scripts/check_real_reuse_benchmark.py`, and adds a regression test
  so a separate domain-robustness/breadth experiment cannot silently re-enter
  the main spec.
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
- The SNAP executable-candidate contract is now pre-registered in
  `benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json` and
  summarized in `research/snapatac2_executable_candidate_contract.md`. The
  real-reuse preflight checks that it applies to SNAP-T1/T2, keeps
  Summary/PaperToSkill paired, makes the runner own execution/runtime/memory
  and artifact-manifest materialization, uses
  `scripts/score_real_reuse_snapatac2.py`, and leaves current main SNAP rows
  unchanged unless a future paired rerun is explicitly promoted through
  `results/real_reuse/main_run_selection.json`. This is a future-rerun
  contract, not new task-success evidence.
- The SNAP executable-candidate runner is implemented in
  `scripts/run_real_reuse_snapatac2_executable_candidate.py` with focused
  coverage in `tests/test_run_real_reuse_snapatac2_executable_candidate.py`.
  It executes candidate scripts, writes runner-owned `candidate_output.json`,
  `artifact_manifest.json`, and `resource_record.json`, calls the existing
  SNAP scorer, does not append to main raw rows, and does not replace
  paper-facing main rows by default.
- The SWE-T1 issue-aligned revised scorer/test contract is now
  pre-registered in
  `benchmarks/real_reuse/swe_t1_issue_aligned_contract_v0.json`, implemented
  as
  `benchmarks/real_reuse/assets/SWE-T1/scorer_only/issue_aligned_check.py`,
  summarized in `research/swe_t1_issue_aligned_contract.md`, and validated in
  `results/real_reuse/swe_t1_issue_aligned_contract_validation.{md,json}`.
  The validation uses the base SQLFluff workspace and existing phase107
  patches only; it adds no model calls, no raw rows, and no main-row
  replacement.
- Phase110 executed the paired SWE-T1 issue-aligned follow-up with GPT-family
  `gpt-5.5` under the pre-registered revised scorer and runner override
  support. `results/real_reuse/swe_t1_issue_aligned_run_report.{md,json}`
  reports Summary 1.000 and PaperToSkill 1.000; two raw rows were appended to
  `results/real_reuse/raw_rows.jsonl`, with run artifacts under
  `results/real_reuse/runs/SWE-T1/.../phase110_gpt_swe_t1_issue_aligned_followup/`.
  `scripts/build_real_reuse_swe_t1_issue_aligned_followup.py` now generates
  the dedicated diagnostic table
  `results/real_reuse/swe_t1_issue_aligned_followup.{csv,md,json}`, which is
  included in `paper/aaai/papertoskill_tables.tex` and checked by
  `scripts/check_paper_tables.py`. The reproducibility package checker has
  also been updated to require the phase110 builder and outputs.
  This is diagnostic issue-aligned follow-up evidence showing the revised
  scorer/contract can close for both conditions. It does not show a
  PaperToSkill advantage and does not replace the locked first-pass SWE-T1
  main row unless explicitly promoted later. Local commit `599382d` saves this
  table and the rebuilt AAAI PDF locally; follow-up commits `12e97df`,
  `24f8029`, `cdeab1f`, `c7d55b7`, `2a61d42`, `12fab77`, `9888f17`,
  `1ab714f`, `2b5d9d0`, `05b3963`, `77e8ada`, `0983fbc`, `c4b4b99`,
  `2490a9b`, `0832201`, `4b216b6`, `0734bb9`, `ef8cbe0`, `10a3d1d`,
  `c3f9f05`, `9829123`, `db535e7`, `fb0baed`, `b6dc061`, `2b823f6`,
  `ef2bcf7`, `b550a26`, `1727615`, `01dfa6e`, `206fa5c`, `4532dd9`,
  `bf95213`, and `69d23b1` are remote-backed in the resume-baseline checkpoint
  `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`.
- Phase109 has collected scored real-reuse LLM ablation rows only on the
  pre-registered stabilized slices. Current collected GPT-family pairs are
  REF-T2 1.000/1.000,
  AIDE-T2 0.814/0.000 with the PaperToSkill candidate timing out under the
  300-second local scorer, and SWE-T2 0.000/0.000 with both conditions failing
  `patch_apply_failed`. Current collected DeepSeek-family pairs are REF-T2
  1.000/1.000, AIDE-T2 0.500/0.500 below the success threshold, and SWE-T2
  0.000/0.000 with both conditions failing `patch_apply_failed`. Claude-family
  REF-T2, AIDE-T2, and SWE-T2 were all attempted for both Summary and
  PaperToSkill, but all six condition rows returned provider HTTP 502 after
  five attempts per condition and remain pending as scored rows.
  `results/real_reuse/llm_ablation_summary.md` reports 12 collected scored rows
  and 6 pending rows out of 18 expected rows. This is auxiliary
  model/repetition evidence, not a main-row replacement and not PaperToSkill
  advantage.
- Phase 89 and the 2026-07-04/2026-07-05 record-sync pushes recovered GitHub
  HTTPS transport interruptions. Use `git status -sb` and a successful remote
  check for the latest exact alignment before each phase-save claim.
- Resume-baseline substantive checkpoint before this continuation's memory edits:
  `69d23b1 Record recovered resume memory backup`, verified at
  `69d23b1ed7f0bb9e3c3ca4b58fd50796d7f5ab4f refs/heads/main`. Rerun remote
  verification before making later remote-backed claims.

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
  gate; it also guards the distinction between the older saved-response model
  ablation and the auxiliary real-reuse LLM ablation.
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
  reports `ready_with_pending_external_evidence`, 477 ready checks, 1 pending
  check, and 0 failed checks.
- Active-goal completion:
  `results/reproducibility/goal_completion_report.md`
  reports `not_complete_pending_external_evidence`, 78 ready checks, 3 pending
  checks, and 0 failed checks.
- External evidence closure queue:
  `results/external_evidence_closure/closure.md`
  reports `pending_external_evidence`, 3 ready checks, 0 pending checks, and 0
  failed checks. The two queue items are human-fidelity annotation and AAAI
  final submission readiness under the recorded wait policy.
- External evidence execution packets:
  `results/external_evidence_packets/packets.md`
  reports `ready`, 8 ready checks, 0 pending checks, and 0 failed checks. The
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
  uses `wire_api=openai_responses`, model `gpt-5.5`, `timeout_seconds=240.0`,
  and `max_tokens=16`; it is now `overall_status=complete` with 6 ready checks,
  0 pending checks, 0 failed checks, and a saved marker response. This is
  provider availability metadata only, not SNAP-T2, Claude-family, human
  fidelity, or paper-facing effectiveness evidence.
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
  reports ready, 343 ready checks, 0 failed checks after adding the current
  real-reuse main, failure-boundary, SWE-T1 diagnostic, SNAP diagnostic, Full
  Excerpt sanity, LLM-ablation, deterministic/offline, and supporting-table
  consistency checks.
- Paper claims:
  `results/reproducibility/paper_claim_report.md`
  reports ready, 56 ready checks, 0 failed checks. It checks the AAAI body,
  AAAI table file, Markdown draft, paper outline, and limitations text for
  overclaims, required boundaries, draft/planning language, stale
  Claude-family completion wording in limitations, and stale model-response
  cost-scope wording.
- Submission-review handoff:
  `results/reproducibility/submission_review_report.md`
  reports ready, 19 ready checks, 0 failed checks after adding the current
  real-reuse LLM-ablation handoff check and the external-evidence pending
  boundary check.
- Real-reuse preflight:
  `results/real_reuse/spec_preflight.md`
  reports `ready_to_implement`, 8 tasks, 490 ready checks, and 0 failed checks
  after validating the REF prepared asset/runner layer, AIDE execution-layer
  contract, SWE-agent skill/execution-layer contracts, SnapATAC2
  skill/execution-layer/prepared-asset contracts, current real-reuse planned
  output paths, the guard that forbids reintroducing a separate
  `domain_robustness` planned output, the SNAP executable-candidate contract,
  the SNAP executable-candidate runner, the SWE-T1 task-contract decision, and
  the SWE-T1 issue-aligned revised scorer/test contract.
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
  The generated main-table and failure-boundary Markdown/JSON outputs report
  the active row-selection file and entry count, making the boundary between
  first-pass main rows and diagnostic follow-ups explicit in paper-facing
  artifacts.
- Current SWE-T1 stabilization boundary: preserve the first-pass SWE-T1
  0.000/0.000 patch-apply result as the paper-facing main-row evidence.
  Phase107 has already run as a paired shared-source-context follow-up and also
  scored 0.000/0.000, but both patches applied and then failed the hidden test.
  This is diagnostic follow-up evidence about task-contract/hidden-objective
  mismatch, not a replacement for the first-pass main row. The issue-aligned
  revised check is now pre-registered and locally validated: the base workspace
  fails the no-join alias check, the phase107 Summary patch passes, and the
  phase107 PaperToSkill patch fails the join-alias regression guard. Phase110
  then ran a paired issue-aligned follow-up and scored Summary/PaperToSkill
  1.000/1.000 under the revised scorer. This is diagnostic follow-up evidence:
  it closes the issue-aligned contract for both conditions, does not show
  PaperToSkill advantage, and does not replace the first-pass main row unless
  explicitly promoted later.
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
- SNAP executable-candidate contract:
  `benchmarks/real_reuse/snapatac2_executable_candidate_contract_v0.json` and
  `research/snapatac2_executable_candidate_contract.md` define the required
  executable candidate outputs, runner-owned runtime/memory/artifact records,
  scorer components, failure handling, and promotion rule for any future SNAP
  rerun. The strict preflight now guards this contract and the corresponding
  executable-candidate runner. Prompt packets for future paired Summary and
  PaperToSkill executable candidate scripts are generated by
  `scripts/build_real_reuse_snapatac2_executable_candidate_prompts.py` under
  `results/real_reuse/snapatac2_executable_candidate_prompts/`; they are
  planning inputs only and not scored evidence. Compact prompt packets for
  future paired SNAP-T2 retries are also generated under
  `results/real_reuse/snapatac2_executable_candidate_compact_prompts/`, with
  the plan at
  `results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.{md,json}`.
  They summarize context/assets with local paths and hashes after phase113,
  phase115, and phase116 SNAP-T2 Summary generations hit provider HTTP 524;
  they do not call a model, score outputs, append raw rows, or replace main
  rows. Phase118 then attempted the compact SNAP-T2 Summary/PaperToSkill
  generation path with GPT-family `gpt-5.5`, a 600-second timeout, 6 attempts,
  and `max_tokens=2200`; Summary still returned provider HTTP 524 after six
  attempts, no script or response was saved, and the remaining PaperToSkill
  side was stopped because paired execution could not proceed. This remains
  provider availability metadata only. The phase118 provider-block package
  sync and follow-up record synchronization were saved in `6879611 Record
  SNAP-T2 compact provider blocker` and `c43d8b5 Sync phase118 SNAP records`;
  a same-turn remote check confirmed
  `c43d8b5e9c7534bf98479b3357ec9fd2acd59438 refs/heads/main`. Treat that as
  backup/provenance metadata, not new task-success evidence. Local substantive commit
  `9829123 Run SNAP executable candidate diagnostics` records the first live
  script-generation/execution checkpoint: Phase111 generated paired
  SNAP-T1 scripts but both failed execution on Windows because they imported
  POSIX-only `resource`, so the paired diagnostic scored 0.500/0.500 with
  missing artifacts and does not replace main rows. The prompt packets were
  tightened for cross-platform Python; phase112 then produced paired revised
  SNAP-T1 Summary/PaperToSkill scripts after a long hung provider request and
  repeated HTTP 524 responses were treated as availability metadata. The
  paired phase112 executable-candidate diagnostic run scored both Summary and
  PaperToSkill 1.000 under the existing SNAP-T1 scorer, showing contract
  closure for both conditions rather than PaperToSkill advantage. Do not
  execute a SNAP executable-candidate task unless paired Summary/PaperToSkill
  scripts exist for the same generation phase.
- SWE-T1 task-contract decision:
  `benchmarks/real_reuse/swe_t1_task_contract_decision_v0.json` and
  `research/swe_t1_task_contract_decision.md` freeze the current SWE-T1 main
  row as boundary evidence. The decision records that first pass failed at
  patch application, phase107 fixed patch application but failed the hidden
  test, and the current scorer-only hidden test checks a specific L031 warning
  message rather than directly testing the no-join alias false-positive issue.
  Do not spend more SWE-T1 model calls under this hidden-test contract; if a
  stronger SWE-T1 row is needed, use the pre-registered issue-aligned hidden
  test/scorer contract and run a paired Summary/PaperToSkill rerun before any
  possible promotion.
- Real-reuse LLM ablation plan:
  `benchmarks/real_reuse/llm_ablation_v0.json` and
  `results/real_reuse/llm_ablation_plan.{md,json}` pre-register a stabilized
  AIDE-T2/SWE-T2/REF-T2 pilot over GPT-family `gpt-5.5`, Claude-family
  `claude-opus-4-8`, and DeepSeek-family `deepseek-v4-flash` with 300-second
  timeouts and 5 attempts. Phase109 has collected all GPT-family and
  DeepSeek-family scored rows for REF-T2, AIDE-T2, and SWE-T2. Claude-family
  REF-T2, AIDE-T2, and SWE-T2 were all attempted for both Summary and
  PaperToSkill, but every Claude-family condition returned provider HTTP 502
  after five attempts and remains pending as a scored row.
- Real-reuse LLM ablation aggregation:
  `results/real_reuse/llm_ablation_summary.md`,
  `results/real_reuse/llm_ablation_summary.json`, and
  `results/real_reuse/llm_ablation_raw_rows.csv` aggregate only
  pre-registered run IDs; pending rows are not negative evidence. The
  aggregator now also carries latest runner-report provider availability
  metadata for pending rows, so Claude-family HTTP 502 failures remain visible
  without being counted as scored task failures. The paper-facing auxiliary
  family summary is in
  `results/real_reuse/llm_ablation_family_summary.csv` and
  `tab:real-reuse-llm-ablation`: GPT-family `gpt-5.5` reports 6/6 scored rows
  with Summary/PaperToSkill averages `0.605/0.333`, DeepSeek-family
  `deepseek-v4-flash` reports 6/6 scored rows with `0.500/0.500`, and
  Claude-family `claude-opus-4-8` remains 0/6 scored and provider-pending.
  This is auxiliary model-slice evidence, not a main-row replacement and not
  aggregate PaperToSkill advantage.

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
  HTTP 502, so no fresh direct-probe response file exists. The latest
  opportunistic recheck was on 2026-07-06 after checkpoint recovery, with
  `max_tokens=16` and a 180-second timeout; all three aliases again returned
  HTTP 502, and no response file exists.
- Scored Claude model-ablation rows come from previously saved responses; do
  not describe the latest Claude protocol refresh as a fresh success.

GPT-family profile:

- Direct GPT diagnostics use OpenAI Responses at base URL
  `https://coderxiaoc.com/v1` and request path `/responses`.
- Key source for direct probes: local environment variables
  `PAPERTOSKILL_GPT_BASE_URL` and `PAPERTOSKILL_GPT_API_KEY`. Real-reuse
  runners still use their `PAPERTOSKILL_GPT_OPENAI_*` environment profile.
- Latest catalog evidence with the separate GPT key lists `gpt-5.5`,
  `gpt-5.4`, and other GPT-family models.
- Latest direct tiny-marker probe on 2026-07-06 used `gpt-5.5`, OpenAI
  Responses, `max_tokens=16`, and a 240-second timeout; it returned HTTP 200
  with the required PaperToSkill/AI-Scientist-v2 markers. Treat this as
  provider availability metadata only.
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
| Paper future-work wording | The outline conclusion could drift back to "repeat and expand" real-reuse tasks, conflicting with the locked-row stabilization policy. | `paper/outline.md` now matches the AAAI/draft conclusion, and `scripts/check_paper_claims.py` treats stale "repeat and expand the original-style paper tasks" wording as draft/planning language; covered by `tests/test_check_paper_claims.py`. |
| Goal completion | Narrative completion audit could stale. | `scripts/check_goal_completion.py` makes the active-goal status machine-checkable. |
| External evidence closure | Pending requirements were spread across multiple reports and docs. | `scripts/check_external_evidence_closure.py` maps current pending goal requirements to concrete queue items without claiming evidence completion. |
| External evidence execution | Closure queue items still required manual interpretation before handoff, and the human-fidelity packet could drift from the desktop `toHuman.md` / `ok.txt` workflow. | `scripts/check_external_evidence_packets.py` turns each queue item into inputs, commands, completion criteria, and escalation boundaries without claiming evidence completion; the AAAI decision packet now routes final-decision recording through `scripts/generate_aaai_submission_decision.py`; the human-fidelity packet now declares `C:\Users\19351\Desktop\tem\toHuman.md`, `C:\Users\19351\Desktop\tem\ok.txt`, and agent-side `ok.txt` cleanup after annotation processing. |
| AAAI submission decision | The final submission item was only a checklist row. | `scripts/check_aaai_submission_decision.py` creates a preflight report with submit-now vs wait-for-evidence options while keeping the human decision pending. |
| AAAI decision record | A human decision record could be hand-written with drift, unavailable options, or secret-like fields. | `scripts/generate_aaai_submission_decision.py` writes the record only after an explicit option, owner, date, claim boundary, and evidence policy; it validates option availability and rejects raw API-key-like material. |
| AAAI gate recursion | The decision preflight and goal/package gates can read each other during report refreshes, causing self-referential intermediate failures. | `scripts/check_aaai_submission_decision.py` treats only the known self-referential failure set as pending during its own preflight; regression covered by `tests/test_check_aaai_submission_decision.py`. |
| Model evidence state | GPT retry evidence was saved separately from the older Phase 36 failure report. | `scripts/check_goal_completion.py` reads both `run_report.json` and `gpt_retry_run_report.json` so historical GPT 502 evidence and current GPT-family success both remain visible. |
| Remote checkpoint records | Handoff/runbook/memory text could present an older remote checkpoint as current after resume/push recovery; direct comparison to the current commit hash also self-invalidated after a guard commit was pushed. | `scripts/check_goal_completion.py` now checks current checkpoint records in memory, runbook, and goal audit against the short-memory declared checkpoint baseline, keeps dynamic `origin/main` hashes out of tracked regenerated reports, and allows historical hashes. |
| Output-token accounting | Cost section had input-token proxies but no saved-response output-token accounting. | `scripts/evaluate_model_response_costs.py` reports local output-token proxies for saved Claude/GPT-family/DeepSeek responses while preserving the no-provider-billing boundary. |
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
- 2026-07-05 Claude direct availability recheck after the claim-matrix sync:
  using the current local Claude API document key in shell-only environment
  variables, Anthropic Messages at `https://coderxiaoc.com/v1/messages`, and
  aliases `claude-opus-4-8`, `claude-opus-4-7`, and `claude-opus-4-6`, all
  aliases returned provider HTTP 502 with a 120-second timeout and
  `max_tokens=16`. Treat this as provider availability metadata; do not count
  it as model-quality evidence or a real-reuse task failure.
- 2026-07-06 Claude direct availability recheck after checkpoint recovery:
  using the same local Claude API document key, shell-only environment
  variables, Anthropic Messages endpoint, and aliases, all three aliases again
  returned provider HTTP 502 with a 180-second timeout and `max_tokens=16`.
  Treat this as provider availability metadata; do not run the full
  Claude-family real-reuse LLM ablation rows until a small direct probe returns
  a usable response.
- 2026-07-06 phase117 Claude direct availability recheck: using the same local
  Claude API document key, shell-only environment variables, Anthropic Messages
  endpoint, and aliases, all three aliases again returned provider HTTP 502
  with a 240-second timeout and `max_tokens=16`. Treat this as provider
  availability metadata; do not run the full Claude-family real-reuse LLM
  ablation rows until a small direct probe returns a usable response.
- 2026-07-06 continuation Claude direct availability recheck: using the same
  local Claude API document key in shell-only environment variables, Anthropic
  Messages endpoint, aliases `claude-opus-4-8`, `claude-opus-4-7`, and
  `claude-opus-4-6`, `max_tokens=16`, and a 240-second timeout, all three
  aliases again returned provider HTTP 502. Only the direct-probe JSON
  timestamp changed. Treat this as provider availability metadata; do not run
  the full Claude-family real-reuse LLM ablation rows until a small direct
  probe returns a usable response.
