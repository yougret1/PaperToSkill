# EffectSlice Paper Baseline Cleanup - 2026-07-22

## Scope

This checkpoint cleans and verifies the current EffectSlice manuscript before the
new forward generalization study. It does not revise V4/V5, alter tracked evidence,
or begin provider experiments.

## Cleanup

- Removed eight ignored LaTeX auxiliary/log files from `paper/effectslice_aaai`.
- Removed the ignored `paper/effectslice_aaai/tmp` rendered-page cache.
- Removed no Git-tracked source, bibliography, figure, result, or PDF file.
- Preserved historical tracked manuscript versions in the repository.
- Excluded historical versions from the desktop delivery package so its entrypoint
  is unambiguous: `main_v3.tex`.

## Compile Validation

The manuscript was rebuilt in the isolated directory
`.tmp/effectslice_baseline_compile_20260722_1` with MiKTeX-pdfTeX 4.19:

1. `pdflatex -interaction=nonstopmode -halt-on-error main_v3.tex`
2. `bibtex main_v3`
3. three additional `pdflatex` passes until references converged

All five commands exited with code 0. The final log contains no undefined citation,
undefined reference, Overfull box, fatal error, or emergency stop. It contains 78
Underfull box notices, retained as non-fatal two-column justification diagnostics.

The rebuilt PDF has 8 letter-size pages and 469,555 bytes. PDF metadata makes its
binary hash differ from the tracked PDF, but Poppler extraction from the rebuilt and
tracked PDFs is byte-identical. All eight rebuilt pages were rendered to PNG and
visually inspected; no clipping, overlap, missing figure, unreadable table, black
glyph block, or broken page transition was observed.

## Desktop Delivery

The current minimal complete manuscript package was copied to:

`C:/Users/Z/Desktop/论文/SelfPaper/toSkill/paper`

It contains 11 files: the entrypoint, generated result macros, bibliography and
compiled bibliography, rendered PDF, AAAI style files, and four tracked figures.
Every delivered file matches its repository source by SHA-256; mismatch count is
zero. Exact hashes and sizes are recorded in
`paper_baseline_manifest_20260722.json`.

## Forward Boundary

The next stage remains FG1 experiment configuration and materialization. No API
credential was read into the repository, no provider endpoint appears in the paper
package, and no new provider request was issued at this checkpoint.

## Checkpoint Verification

- All JSON files under the forward-extension directory parse successfully.
- A secret/endpoint scan found no API key, authorization header, or configured
  third-party endpoint in the files selected for Git backup.
- The current preregistration verifier intentionally does not pass this checkpoint:
  `paper_registry.json` says materialization is pending, while the older verifier
  still asserts `frozen_before_provider_calls`. This is a Stage 2.2 design blocker,
  not a paper-cleanup failure. The checkpoint must not be represented as a frozen or
  passed preregistration.
