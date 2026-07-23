# PaperToSkill Project Summary

## Stable Goal

Develop PaperToSkill into an evidence-grounded system that helps non-expert
researchers and agent builders extract, verify, adapt, and re-validate a paper's
core research workflow.

## Core Mechanism Under Investigation

- A claim-method-assumption-evidence representation grounded in the paper.
- Explicit supported, inferred, conflicted, and missing states.
- Immutable source evidence plus a separate editable adaptation layer.
- Typed edit deltas that invalidate affected claims or assumptions.
- Concrete re-validation requirements after adaptation.

## Current Workflow Run

- Run: `rapid_core_reproduction_utility_2026-07-15`
- Canonical root:
  `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/`
- Active paper: `EffectSlice: Evidence-Carrying Admission for Paper-Derived
  Procedural Cores`.
- Manuscript source: `paper/effectslice_aaai/main_v3.tex`.
- Current overview figure: V3-derived `SkillAudit_Main_Figure_v3_2`; it is verified
  but not yet inserted into the manuscript source.
- Current verified layout: 8 pages, inspected at 144 DPI.
- Stages `2.1` through `2.8`: passed.
- Major Stage `2`: passed with `handoff_mode: normal`.
- Forward Stage `2.6`: passed with 33 bibliography entries, 30 main-text
  citations, and 7 DOI-verified AAAI papers.
- Frozen parent Stage `2.2`: committed and pushed.
- Remote-only Stage `2.2` successor: committed and pushed at `6262956f`.
- Remote-only Stage `2.3` immutable materialization anchor: passed, committed,
  and privately pushed at `b4a8605f`.
- Current branch: `codex/effectslice-v3`.

## EffectSlice Evidence State

- The release verifier independently enumerates and rehashes 858 canonical raw
  files and checks 24 directly bound artifacts.
- Final reviewer ratings are 8.5/10, 7/10, and 7/10, all Weak Accept, with no
  unsupported manuscript claims or remaining scientific blocker.
- The authoritative frozen parent suite passes 678 tests with 6 skips.
- The latest LaTeX build has no critical log findings, and all 8 rendered pages
  passed visual inspection.
- The user has prohibited workflow-stage rollback. New experiments must be
  forward extensions with new preregistrations and evidence boundaries; the
  accepted V4/V5 records remain immutable parent evidence.

## Forward Generalization Extension

- Root: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/forward_extensions/generalization_2026-07-21/`.
- Stage `2.2` bundle SHA:
  `277bab0fba66a4144346d472ef3deadc010168353d47f939dc812501a2eff9b4`.
- Registered benchmark: 12 papers, 24 nested task decisions, and four domains
  (NLP, software engineering, data analysis, agent/tool-use).
- Frozen parent bundle SHA:
  `277bab0fba66a4144346d472ef3deadc010168353d47f939dc812501a2eff9b4`.
- Remote-only successor bundle SHA:
  `e2615ea65ecc0c1145aa3e0f2fb7a36b8bc91a914bb94821b5cee40be9da99958`.
- Required schedule cap: 1296 remote conversations and zero local executions.
- Required robustness slots are GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra,
  Claude Opus 4.7, and GPT-5.6 Luna. Claude Opus 4.6 remains optional.
- Luna F/I repeats measure observed remote repeatability only; there is no model
  seed-control or deterministic closed-model claim.
- Immutable Stage `2.3` anchor bundle SHA:
  `1f12dfdba63b1ddc65bd57fa8b1b625ba4259050e93ab4f108786c2023c5ccd7`.
- The anchor binds 3,672 files and one 1,296-row remote schedule; its full V3
  audit and complete forward suite pass (`141 passed`).
- The remote executor contract and isolated worker pass focused and full tests;
  the frozen scorer two-component versus four-ID mismatch is preserved and
  explicitly audited.
- The executor checkpoint was privately pushed at `579fc90f`.
- Six exact-alias format preflights passed on their first transport attempts;
  zero registered experiment rows were consumed by preflight.
- FG1 batch 001 executed 72 DeepSeek primary rows, but all exhausted the
  registered 1,024-token output budget and were invalid. The remaining 1,224
  FG1 rows are undispatched.
- FG1 invalid batch 001 was privately pushed at `e9bdbeda`.
- FG2 is a new 1,296-row versioned execution with an 8,192-token output budget;
  its frozen bundle is
  `917fa2d4a722e3b05b3b2fc5d97ebe9f6ee36b888a03844f2a1334e326045411`.
- FG2 was privately pushed at `3ed3a533`; its unscored pilot found all six
  responses nontruncated, but Claude Opus 4.7 and DeepSeek V4 Flash violated the
  bare-JSON submission format. No registered FG2 row was dispatched.
- The invalid FG2 pilot evidence was privately pushed at `13d027ce`.
- FG3 keeps the 8,192-token budget and adds one uniform bare-JSON submission
  instruction. Its frozen bundle SHA is
  `1a5212ee09f43b4e97737f83fc1365e0181942b790bd0a54920609d35b24766d`.
- FG3 contains 1,296 new registered execution IDs and six marked, unscored pilot
  requests. Its verifier, 156-test forward suite, and complete 1,308-file safety
  scan passed before any FG3 provider call started.
- The FG3 successor was privately pushed at `f03d0ce4`. Its six-request unscored
  pilot then passed 6/6 strict submissions with six first-attempt transport
  successes. All 32 evidence files passed the safety scan. The pilot checkpoint
  was privately pushed at `b388845c`.
- FG3 batch 001 then consumed the exact first 72 registered rows: four
  paper-task units with 24 B, 24 F, and 24 S rows. All provider transports
  completed on their first attempt, with no network retry.
- Batch 001 produced 70 hard-contract failures and two malformed/no-submission
  outcomes, zero operational successes, and 72 private scores of 0.0. These are
  valid frozen condition failures rather than Invalid rows and are never rerun.
- The batch summary proves an exact contiguous schedule prefix. Its complete
  611-file safety scan found no credential reflection, generic credential
  pattern, or forbidden local-model design; 1,224 FG3 rows remain undispatched.
- FG3 batch 001 was committed and privately pushed at `eea9cf56` before row 73
  was dispatched.
- FG3 batch 002 consumed rows 73-144, again spanning four paper-task units with
  24 B, 24 F, and 24 S rows. Its 72 logical requests used 75 transports because
  three registered TLS failures were retried; no terminal semantic response was
  rerun.
- Batch 002 produced 66 hard-contract failures, five malformed/no-submission
  outcomes, and one operational success in AGENT-TF-02 under S. The private-score
  sum is 1.0 across 72 rows; this single success is not an early conclusion.
- The complete 1,189-file execution-tree safety scan passed with zero credential
  reflection, generic credential-pattern matches, or forbidden local-model
  design. Cumulative FG3 outcomes across rows 1-144 are 136 hard-contract
  failures, seven malformed/no-submission outcomes, and one operational success;
  1,152 rows remain undispatched.
- FG3 batch 002 was committed and privately pushed at `78b447ca` before row 145
  was dispatched.
- FG3 batch 003 consumed rows 145-216 across AGENT-RF-01, DATA-LEI-01,
  NLP-LL2-01, and SE-CR-01, with 24 B, 24 F, and 24 S rows. All 72 transports
  completed on their first attempt.
- Batch 003 produced 61 hard-contract failures and 11 malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- The complete 1,768-file execution-tree safety scan passed with zero credential
  reflection, generic credential-pattern matches, or forbidden local-model
  design. Cumulative FG3 outcomes across rows 1-216 are 197 hard-contract
  failures, 18 malformed/no-submission outcomes, and one operational success;
  1,080 rows remain undispatched.
- FG3 batch 004 consumed rows 217-288 across AGENT-RF-02, DATA-LEI-02,
  NLP-LL2-02, and SE-CR-02, with 24 B, 24 F, and 24 S rows. All 72 transports
  completed on their first registered attempts.
- Batch 004 produced 68 hard-contract failures and four malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- The complete 2,347-file execution-tree safety scan passed with zero credential
  reflection, generic credential-pattern matches, or forbidden local-model
  design. Cumulative FG3 outcomes across rows 1-288 are 265 hard-contract
  failures, 22 malformed/no-submission outcomes, and one operational success;
  1,008 rows remain undispatched.
- FG3 batch 005 consumed rows 289-360 across AGENT-RA-01, DATA-HDB-01,
  NLP-CSE-01, and SE-PE-01, with 24 B, 24 F, and 24 S rows. All 72 transports
  completed on their first registered attempts.
- Batch 005 produced 62 hard-contract failures and ten malformed/no-submission
  outcomes, zero operational successes, and a private-score sum of 0.0.
- The complete 2,926-file execution-tree safety scan passed with zero credential
  reflection, generic credential-pattern matches, or forbidden local-model
  design. Cumulative FG3 outcomes across rows 1-360 are 327 hard-contract
  failures, 32 malformed/no-submission outcomes, and one operational success;
  936 rows remain undispatched.

## Legacy Evidence Policy

The pre-workflow paper, experiments, memory, and 110 chronological run logs are
preserved as the `legacy_papertoskill_v1` run. They may inform the new design,
but no old metric or manuscript claim automatically transfers to the new
thesis. Reuse requires an explicit Stage 2 evidence audit.

## Known High-Risk Adjacent Work

- Anything2Skill: direct knowledge-to-skill compilation collision.
- Paper2Agent: direct paper-to-agent problem collision.
- SkCC: direct challenge to unverified portability claims.
- SkillWiki: overlap in evidence-linked skill infrastructure.

## Persistent Boundaries

- EffectSlice is an admission protocol, not a slicing or reduction algorithm.
- Treat the current result as a scoped proof of concept, not a population-level
  success estimate or evidence of broad automatic reduction.
- Do not claim faster human reproduction, understanding, or other user benefit
  without a controlled user study.
- Preserve the V4/V5 raw evidence, registration records, and release bindings.
- Do not equate source-span validity with semantic entailment.
- Do not hide manual curation in the main treatment.
- Do not claim arbitrary-PDF understanding from a smoke path.
- Do not claim portability without matched cross-harness evidence.
- Treat provider availability separately from method quality.
- Keep paper as the independent statistical unit and restrict forward inference
  to the purposefully registered, domain-stratified benchmark.
- Do not begin a forward stage until the preceding stage is verified, committed,
  and pushed to the private remote.
- Do not design, download, install, materialize, or run local-model experiments.
  Historical frozen parent records may mention the superseded local anchor, but
  no successor experiment or manuscript claim may rely on it.

## Stage 2.3 Current Gate

- Commit and privately push the complete FG3 batch-005 evidence, summaries,
  audit, report, and memory update before dispatching row 361.
- The frozen plan contains no outcome-driven early-stopping rule. Batch 003's
  zero-success interval and all condition failures remain in the registered
  denominators; neither can trigger a semantic rerun or an in-place protocol
  change.
- Execute only the frozen 1,296-row remote schedule with registered retry
  classification and raw/canonical artifact retention.
- Keep generated token IDs and local runtime evidence out of all successor work.
- Do not treat four controls as a calibrated confusion matrix or error-rate
  estimate.

## Environment Policy

- The project-local `.venv` is approved for workflow tooling and currently
  contains the idea-spark retrieval/full-text dependencies.
- Independent or dependency-heavy experiment projects may use separately named
  conda environments. Keep conda `base` unchanged and record each environment's
  name, Python version, dependency lock, and reproduction command in Stage 2.
- Keep credentials outside source, logs, fixtures, manifests, hashes, manuscript,
  and Git history.
