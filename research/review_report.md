# PaperToSkill Review Report

Date: 2026-06-17

Evidence boundary: this is an internal adversarial review of the current
PaperToSkill draft and artifact package. It does not add new empirical results.

## Overall Assessment

PaperToSkill has a coherent system-paper shape: a clear conversion artifact,
four real agent/tool-method cases, deterministic/offline comparisons, source
grounding, compactness/cost proxy, failure archive, human-fidelity readiness,
and a reproducibility package gate.

The draft should not be positioned as a completed live-agent or fully automatic
PDF-to-skill system yet. The strongest current framing is:

> PaperToSkill converts curated, source-anchored paper notes into compact,
> source-grounded skills and shows deterministic/offline evidence that these
> skills preserve more operational detail than summary baselines.

## Major Risks

| ID | Risk | Severity | Current Evidence | Required Response |
| --- | --- | --- | --- | --- |
| R1 | Reviewers may call PaperToSkill "just summarization." | High | Generated skills beat generic-summary and abstract-only baselines on deterministic operational coverage across four papers. | Emphasize workflow, validation, failure cases, source maps, and transfer notes; avoid claiming live task improvement until response logs exist. |
| R2 | Reviewers may reject deterministic metrics as too lexical. | High | Source-span validation, context coverage, and transfer readiness are reproducible but lexical/section-based. | Present metrics as early gates; keep human-fidelity annotation and live execution as future work or pending evidence. |
| R3 | Curated notes weaken the automation claim. | High | The draft explicitly says curated source-anchored notes; raw PDFs are extracted but notes are manually curated. | Keep "curated paper-note-to-skill" in title/abstract claims unless automatic PDF sectioning is added. |
| R4 | Four papers may still be too narrow and all are naturally procedural. | Medium | Benchmark includes AI Scientist-v2, Reflexion, AIDE, and Toolformer, covering agent, ML-engineering, and tool-use methods. | Describe this as a focused first benchmark; plan stress cases on interface-heavy and theory-heavy papers. |
| R5 | Cross-harness transfer is only offline readiness. | High | Live prompt packets exist, but endpoint still returns HTTP 503. | Use "offline transfer readiness"; do not claim live Codex-to-Claude success. |
| R6 | Human fidelity is prepared but unscored. | High | Annotation template has 24 rows, 0 scored, 24 pending, 0 errors. | Say "human-fidelity protocol prepared" and "annotation pending"; never say "human-validated." |
| R7 | Cost/economic claims can be overread. | Medium | Cost uses `ceil(characters / 4)` and a configurable price proxy, not provider billing. | Call it deterministic context-size/cost proxy; avoid real savings or success-per-dollar claims. |
| R8 | Failure archive could sound like an outcome study. | Medium | Archive records 27 cases but does not test user outcomes. | Frame as provenance and claim discipline, not as proof of better final results. |

## Claim Tightening Recommendations

| Location | Current Pressure | Safer Wording |
| --- | --- | --- |
| Abstract | "conversion workflow" may imply end-to-end PDF automation. | "workflow that turns source-anchored paper notes into compact, human-editable agent skills" |
| Introduction | "preserve enough procedural knowledge" can sound broad. | "preserve enough procedural knowledge under deterministic/offline gates" |
| Results | "economic signal" can sound like real cost savings. | "coverage-preserving compression relative to full extracted paper context under a deterministic token proxy" |
| Transfer | "transfer readiness" can be mistaken for live success. | "offline transfer-readiness score; live response logs remain pending" |
| Failure archive | "first-class evidence" can sound causal. | "first-class provenance artifact" |

## Submission Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Claim-evidence consistency | Pass with caveats | `paper/claim_checklist.md`; `research/claim_evidence_matrix.md` |
| Reproducibility package | Pass locally, external evidence pending | `results/reproducibility/package_report.md` |
| Live cross-harness execution | Pending | `results/live_transfer_prompts/`; endpoint HTTP 503 |
| Human fidelity | Pending | `results/human_fidelity_packets/annotation_summary.md` |
| Cost accounting | Partial | `results/tables/context_cost_proxy.md` |
| Benchmark diversity | Partial | Four agent/tool-method papers only |

## Recommended Next Experiments

1. Execute the prepared live prompt packets once the endpoint returns chat
   completions.
2. Fill the 24-row human-fidelity annotation template with independent reviewer
   scores and evidence notes.
3. Add one less-procedural or theory-heavy stress case to test whether the extractor fails
   gracefully.
4. Add tokenizer-exact or provider-specific cost accounting only after choosing
   the target model family and pricing source.

## Decision

Do not mark the project as complete. The current package is ready for internal
review, but not for claims of live agent success, expert validation, or realized
economic savings.
