# Phase 35 Run Log: PDF Input Smoke Path

## Decision Question

Can the local PaperToSkill pipeline accept a PDF source directly while keeping
the evidence boundary separate from reliable arbitrary-PDF automation?

## Actions

- Updated `scripts/papertoskill_pipeline.py` so `.pdf` sources are converted to
  extracted text with `pdftotext -layout` when the command is available on
  `PATH`.
- Added `source_info` and `outputs.extracted_text` fields to the pipeline
  manifest so a user can audit the original source, generated text source, and
  extraction command.
- Added a PDF smoke test to `tests/test_papertoskill_pipeline.py` using the
  local AAAI PDF package when both the PDF and `pdftotext` are available.
- Updated `scripts/check_usage_examples.py` so the usage gate runs a temporary
  PDF pipeline example and checks that the manifest records PDF extraction.
- Updated the auto-note usage example and runbook with the direct-PDF command.

## Results

- The text-source pipeline test still passes.
- The PDF-source pipeline test extracts text from
  `paper/aaai/papertoskill_aaai2027.pdf`, records `pdftotext -layout` in the
  manifest, and creates the expected pipeline artifacts.
- The usage-example report now reports 42 ready checks and 0 failed checks,
  including `usage_pdf_pipeline_example_manifest_created` and
  `usage_pdf_pipeline_example_text_extracted`.

## Evidence Boundary

This phase supports a local PDF-input smoke path for already-available PDFs.
It does not prove robust arbitrary-PDF understanding, semantic fidelity without
human audit, live harness success, or provider-model quality.

## Verification

- `python -m unittest tests.test_papertoskill_pipeline -v`
- `python -m unittest discover -s tests -v`
- `python scripts\check_usage_examples.py --strict`
