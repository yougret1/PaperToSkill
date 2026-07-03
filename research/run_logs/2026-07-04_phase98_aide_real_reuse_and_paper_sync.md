# Phase 98: AIDE Real-Reuse Rows And Paper Sync

- Date: 2026-07-04
- Objective: finish the AIDE slice of the main real-reuse table, then align the
  paper narrative with the first full eight-row GPT-family pass.

## Inputs

- Official Kaggle Spaceship Titanic files supplied under
  `C:\Users\19351\Desktop\tem\real_reuse_assets\spaceship-titanic\`.
- `train.csv` validation: 8,693 rows and SHA256
  `17336D553F49EBDF6ECB266D2B5D3746E5DD308445F7C7864141C4F28D2A88D0`.
- GPT-family base model: `gpt-5.5`.

## Results

- Materialized AIDE-T1 and AIDE-T2 fixtures under
  `benchmarks/real_reuse/assets/`.
- Kaggle-derived CSV fixture files are kept local and ignored by git; the
  committed manifests retain hashes and provenance boundaries.
- Baseline scorer checks passed in
  `results/real_reuse/aide_t1_baseline_metric.json` and
  `results/real_reuse/aide_t2_weak_script_metric.json`; both report about
  `0.4997124784358827`.
- Ran AIDE-T1/T2 Summary and PaperToSkill with run id
  `phase98_gpt_aide_real_reuse`.
- AIDE-T1 Summary/PaperToSkill: `0.000/0.000`, both `timeout after 60s`.
- AIDE-T2 Summary/PaperToSkill: `0.000/0.000`, both `timeout after 60s`.

## Claim Boundary

The first single-run GPT-family pass now covers all eight real-reuse rows:
AIDE-T1/T2, SWE-T1/T2, REF-T1/T2, and SNAP-T1/T2. The result is mixed and
failure-heavy. SWE-T2 is one positive PaperToSkill row; REF ties Summary; AIDE,
SWE-T1, and SNAP expose timeout, patch-application, and artifact-completion
failure boundaries. This does not establish aggregate PaperToSkill advantage
over Summary.

## Paper Sync

- Updated the AAAI abstract, contribution wording, results framing,
  discussion, limitations, conclusion, and real-reuse table caption to reflect
  the completed first-pass table without overclaiming.
- Updated `paper/draft.md`, `paper/outline.md`, memory, and artifact maps to
  keep the current-state narrative consistent.

## Verification

Verification is scheduled immediately after this sync: refresh strict gates,
rebuild the AAAI PDF, run tests, run `git diff --check`, scan for raw keys, then
commit and push the phase backup.
