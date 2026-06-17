# Phase 20 AIDE Auto-Note Profile Run Log

Date: 2026-06-17

Evidence boundary: deterministic extracted-text-to-note scaffold evidence for a
second paper/profile. This is not arbitrary-PDF automation, live agent success,
or human semantic validation.

## Commands

```powershell
python scripts\papertoskill_note_from_text.py --source papers\extracted\aide.txt --output papers\auto_notes\aide_auto_note.md --paper-id aide_auto --title "AIDE: AI-Driven Exploration in the Space of Code" --profile aide --report results\evaluations\aide_auto_note_scaffold_v0.json
python scripts\papertoskill_extract.py --source papers\auto_notes\aide_auto_note.md --output generated_skills\aide_auto --name aide-auto-paper-skill
python scripts\evaluate_skill.py --skill generated_skills\aide_auto\SKILL.md --rubric benchmarks\rubric_aide_v0.json --output results\evaluations\aide_auto_rubric_v0.json
python scripts\evaluate_context_baselines.py --task benchmarks\tasks\aide_auto_research_run.json --output results\evaluations\aide_auto_context_baselines_v0.json
python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\aide_auto_harness_transfer.json --output results\evaluations\aide_auto_harness_transfer_v0.json
python scripts\validate_source_spans.py --task benchmarks\tasks\aide_auto_source_span_validation.json --output results\evaluations\aide_auto_source_span_validation_v0.json
python scripts\aggregate_results_tables.py --output-dir results\tables
python scripts\check_reproducibility_package.py --output-json results\reproducibility\package_report.json --output-md results\reproducibility\package_report.md --strict
```

## Results

- AIDE auto-note-derived rubric score: `20/20`.
- Context baseline:
  - auto-note-derived skill: `8.467/10`
  - generic summary: `1.916/10`
  - abstract-only context: `1.333/10`
- Harness-transfer readiness:
  - full auto-note-derived skill: `9.5/10`
  - no-transfer-notes variant: `7.1/10`
  - generic summary: `1.5/10`
- Source-span validation: 17 supported claims, 0 weak or unsupported claims, 0
  invalid ranges, support rate `1.0`.
- Skill word count: `998`, under the 1,200-word budget.
- Reproducibility package report: `ready_with_pending_external_evidence`, 105
  ready checks, 5 pending checks, and 0 failed checks.

## Failure And Fixes

- The first Toolformer-oriented selector produced poor AIDE semantics: the AIDE
  direct auto run scored only `11.62/20` before adding an AIDE profile.
- The initial AIDE profile pulled several weak limitation/experiment windows
  from figure captions, related work, or generic baseline text. The selector now
  searches the target section first before falling back to full-document search,
  and the AIDE profile uses tighter benchmark, cost, and limitation phrases.
- `papertoskill_extract.py` split an indented `2. AutoGPT.` continuation into a
  new validation bullet. The extractor now recognizes only unindented Markdown
  bullet markers as new bullets, preserving wrapped list text.
- AIDE's data-contamination and live-competition caveats share the same source
  paragraph, so the profile now allows overlap for the specific live-competition
  claim while keeping source anchors auditable.

## Claim Impact

Phase 20 supports saying that deterministic extracted text can seed auditable
note scaffolds for two papers/profiles: Toolformer and AIDE. It does not support
reliable arbitrary-PDF-to-skill automation, completed live cross-harness
execution, provider billing, or completed human-fidelity validation.
