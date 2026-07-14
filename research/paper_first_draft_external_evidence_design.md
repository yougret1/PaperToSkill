# Paper First Draft and External-Evidence Layout Design

Date: 2026-07-14

## Objective

Produce a first AAAI-format paper draft whose page count already includes the
final intended footprint of two external-evidence tables and their companion
figures. The layout must remain scientifically honest while the external cells
are empty.

## Evidence Boundary

- Preserve every currently validated local result, including the completed
  bounded 24-cell human-fidelity annotation and existing real-reuse evidence.
- Do not invent external measurements, plot synthetic values, or describe an
  uncollected study as completed.
- Render all unavailable numeric cells as `--`.
- Render the row status as `Pending external evidence`.
- Treat the tables as final-size page-budget placeholders: final columns,
  final row counts, final typography, and final float widths.
- Keep the paper body silent about the placeholder state. Do not add planning,
  preregistration, future-work, or protocol discussion solely to explain these
  two tables.
- Use neutral table captions that name the evaluation represented by each
  table. The captions must not claim results.
- Keep the current `wait_for_external_evidence` submission decision unchanged.

## Paper Structure

The existing AAAI manuscript remains the canonical source. The first draft
keeps its current title, abstract, method, validated experiments, results,
limitations, and conclusion, with claim-boundary edits only where required by
the new figures or floats.

The two tables are inserted as final-size main-paper floats without a dedicated
body paragraph explaining their pending state. The abstract and conclusion do
not cite or summarize unavailable values.

## Table 1: Cross-Model Live Real-Reuse

The table uses nine rows: three model families crossed with three existing task
slices.

Model families:

- GPT-family
- Claude-family
- DeepSeek-family

Task slices:

- AIDE-T2
- SWE-T2
- REF-T2

Columns:

- Model family
- Task
- Seeds
- Summary
- PaperToSkill
- Delta
- Status

`Seeds`, `Summary`, `PaperToSkill`, and `Delta` are `--` in the first draft.
Every status cell is `Pending external evidence`.

## Table 2: Expanded Independent Human Study

The table uses the six established fidelity criteria so its eventual values can
replace the placeholders without changing the row count.

Rows:

- Central contribution fidelity
- Operational workflow fidelity
- Validation and evidence fidelity
- Failure and limitation fidelity
- Source grounding
- Transfer boundary discipline

Columns:

- Criterion
- Artifacts
- Raters
- Mean
- Agreement
- 95% CI
- Status

All numeric or sample-count cells are `--` in the first draft. Every status
cell is `Pending external evidence`. This table is distinct from, and does not
erase, the completed bounded 24-cell annotation already reported in the paper.

## Figure 1: Pipeline and Evidence Boundary

Create one full-width conceptual figure showing:

1. Extracted paper and source anchors.
2. Operational note and failure boundaries.
3. Portable skill and deterministic local gates.
4. Live reuse and independent review.

The first three stages use one visual encoding for locally validated artifacts.
The final stage uses a distinct encoding for the external-evidence layer. The
figure contains no empirical marks or numeric results.

## Figure 2: External Evaluation Design

Create one compact two-track conceptual figure:

- Live track: model families by task slices by repeated seeds, producing paired
  Summary and PaperToSkill outcomes.
- Human track: paper artifacts by independent raters, producing criterion
  scores and agreement estimates.

The figure communicates study structure only. It contains no bars, points,
effect estimates, or simulated values.

## Layout

- Figure 1 is a `figure*` spanning both AAAI columns.
- Figure 2 is compact and placed near the two external-evidence tables.
- Both tables are `table*` floats spanning both columns.
- Table typography and row heights are fixed to the intended final footprint.
- Float placement should preserve the AAAI style without forcing manual page
  breaks unless compilation shows an unavoidable layout defect.

## Files

Expected manuscript edits:

- `paper/aaai/papertoskill_aaai2027.tex`
- `paper/aaai/papertoskill_tables.tex` or a dedicated external-evidence table
  include following the repository's current pattern
- `paper/draft.md`
- `paper/outline.md`
- `paper/limitations.md` only if a claim-boundary synchronization is required

Expected figure assets:

- `paper/aaai/figures/papertoskill_pipeline.pdf`
- `paper/aaai/figures/external_evidence_design.pdf`

Source scripts for those figures must live under `scripts/` and generate the
assets deterministically without external downloads.

## Verification

1. Generate both figure assets from local scripts.
2. Compile the AAAI manuscript through the repository's documented build path.
3. Record the page count before and after the new final-size floats.
4. Render the resulting PDF pages to images and inspect all table and figure
   pages for clipping, overlap, unreadable labels, and float-order problems.
5. Run the strict paper-table, paper-claim, AAAI-package, and submission-review
   gates.
6. Run `git diff --check` and the repository raw-key scan.

## Acceptance Criteria

- The PDF compiles successfully.
- Both external-evidence tables are visible in the main paper with the exact
  final row counts and `--` placeholders.
- Every row says `Pending external evidence`.
- The body does not explain the tables as planned or preregistered studies.
- No prose or caption claims that the unavailable measurements are complete.
- Two companion conceptual figures render clearly and contain no invented
  empirical data.
- The final report states the resulting page count and any page-limit risk.
