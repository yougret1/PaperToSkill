# Phase 19 Auto-Note Scaffold Run Log

Date: 2026-06-17

## Objective

Reduce the curated-note bottleneck by adding a deterministic
extracted-text-to-note scaffold and validating it on Toolformer before the
existing PaperToSkill note-to-skill extractor.

## Commands

```powershell
python -m unittest discover -s tests -p test_papertoskill_note_from_text.py -v
python scripts\papertoskill_note_from_text.py --source papers\extracted\toolformer.txt --output papers\auto_notes\toolformer_auto_note.md --paper-id toolformer_auto --title "Toolformer: Language Models Can Teach Themselves to Use Tools" --report results\evaluations\toolformer_auto_note_scaffold_v0.json
python scripts\papertoskill_extract.py --source papers\auto_notes\toolformer_auto_note.md --output generated_skills\toolformer_auto --name toolformer-auto-paper-skill
python scripts\evaluate_skill.py --skill generated_skills\toolformer_auto\SKILL.md --rubric benchmarks\rubric_toolformer_v0.json --output results\evaluations\toolformer_auto_rubric_v0.json
python scripts\evaluate_context_baselines.py --task benchmarks\tasks\toolformer_auto_research_run.json --output results\evaluations\toolformer_auto_context_baselines_v0.json
python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\toolformer_auto_harness_transfer.json --output results\evaluations\toolformer_auto_harness_transfer_v0.json
python scripts\validate_source_spans.py --task benchmarks\tasks\toolformer_auto_source_span_validation.json --output results\evaluations\toolformer_auto_source_span_validation_v0.json
python scripts\aggregate_results_tables.py --output-dir results\tables
python scripts\check_reproducibility_package.py --output-json results\reproducibility\package_report.json --output-md results\reproducibility\package_report.md --strict
```

## Results

- Auto-note-derived Toolformer skill rubric: `20/20`.
- Context coverage: auto-note-derived skill `9.3/10`, generic summary
  `2.5/10`, abstract-only `1.534/10`.
- Transfer readiness: full auto-note-derived skill `10.0/10`; no-transfer-notes
  variant `7.6/10`; generic summary `1.45/10`.
- Source-span validation: 20 supported claims, 0 invalid ranges, support rate
  `1.0`.
- Compactness: 1,179 words, under the 1,200-word budget.
- Reproducibility package: ready with pending external evidence; no failed local
  checks.

## Failure And Fix Notes

- Initial snippets mixed two-column `pdftotext -layout` output and references.
  Fixed by preserving raw line spacing, splitting likely columns, and selecting
  the keyword-bearing column while preserving original newline line anchors.
- Initial auto-note-derived skill exceeded the compactness budget and missed
  exact rubric signals. Fixed by shortening snippets and making source-backed
  prefixes more explicit.
- Initial limitation anchors passed lexical validation but were not the best
  semantic spans. Fixed by preferring stronger exact phrases and later analysis
  sections for targeted limitation specs.

## Evidence Boundary

This phase supports one deterministic extracted-text-to-note scaffold and a
retained Toolformer auto-note-derived skill. It does not support reliable
arbitrary-PDF-to-skill automation, live agent task success, provider billing
claims, or human semantic fidelity.
