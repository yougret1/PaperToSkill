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
- Rendered artifact: `paper/effectslice_aaai/main_v3.pdf` (8 pages).
- Stages `2.1` through `2.8`: passed.
- Major Stage `2`: passed with `handoff_mode: normal`.
- Forward Stage `2.6`: passed with 33 bibliography entries, 30 main-text
  citations, and 7 DOI-verified AAAI papers.
- Current branch: `codex/effectslice-v3`.

## EffectSlice Evidence State

- The release verifier independently enumerates and rehashes 858 canonical raw
  files and checks 24 directly bound artifacts.
- Final reviewer ratings are 8.5/10, 7/10, and 7/10, all Weak Accept, with no
  unsupported manuscript claims or remaining scientific blocker.
- Focused high-risk tests pass 26/26; the authoritative `tests/` suite passes
  678 tests with 6 skips.
- The latest LaTeX build has no critical log findings, and all 8 rendered pages
  passed visual inspection.
- The user has prohibited workflow-stage rollback. New experiments must be
  forward extensions with new preregistrations and evidence boundaries; the
  accepted V4/V5 records remain immutable parent evidence.

## Forward Generalization Extension

- Root: `research/workflow_runs/rapid_core_reproduction_utility_2026-07-15/stage2/runs/effectslice_attempt_2/forward_extensions/generalization_2026-07-21/`.
- Citation gate: 33 unique bibliography entries, 30 unique main-text citations,
  7 AAAI citations, and 13 official or retrieved metadata records.
- Added admission-risk positioning from SelectiveNet and Conformal Risk Control,
  fine-grained agent-evaluation positioning from AgentBoard, and the ICML 2025
  PaperBench venue record.
- Next forward stage: `2.2`, preregistering a 12-paper by 2-task experiment over
  NLP, software engineering, data analysis, and agent/tool-use domains.

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

## Environment Policy

- The project-local `.venv` is approved for workflow tooling and currently
  contains the idea-spark retrieval/full-text dependencies.
- Independent or dependency-heavy experiment projects may use separately named
  conda environments. Keep conda `base` unchanged and record each environment's
  name, Python version, dependency lock, and reproduction command in Stage 2.
