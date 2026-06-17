# Paper Claim Checklist

Use this file as the gate before promoting a claim into the paper. Prefer the
supported wording. Do not use the unsupported wording until the missing evidence
exists.

| Claim Area | Supported Wording | Unsupported Wording | Evidence | Status |
| --- | --- | --- | --- | --- |
| Conversion | PaperToSkill converts curated paper notes for four real agent/tool-method papers into compact `SKILL.md` artifacts with source maps. | PaperToSkill fully automatically converts arbitrary PDFs into reliable skills. | `generated_skills/ai_scientist_v2/SKILL.md`; `generated_skills/reflexion/SKILL.md`; `generated_skills/aide/SKILL.md`; `generated_skills/toolformer/SKILL.md`; `scripts/papertoskill_extract.py` | Supported |
| Automatic note scaffold | PaperToSkill can generate deterministic, source-anchored note scaffolds from extracted Toolformer and AIDE text and convert them into auditable skills that pass offline gates. | PaperToSkill now reliably converts arbitrary PDFs into final skills without audit. | `scripts/papertoskill_note_from_text.py`; `papers/auto_notes/toolformer_auto_note.md`; `papers/auto_notes/aide_auto_note.md`; `generated_skills/toolformer_auto/SKILL.md`; `generated_skills/aide_auto/SKILL.md`; `results/tables/auto_note_comparison.md` | Supported for two extracted-text scaffolds |
| Structural quality | All four generated skills score 20/20 on deterministic paper-specific rubrics. | The generated skills are human-validated as complete reproductions of the papers. | `results/evaluations/*_rubric_v0.json`; `results/tables/main_results.md` | Supported |
| Summary comparison | Generated skills preserve more deterministic task-relevant operational coverage than generic-summary and abstract-only baselines across four papers. | Skills improve live agent task success over summaries. | `results/evaluations/*_context_baselines_v0.json`; `results/tables/main_results.md` | Supported for deterministic coverage |
| Compactness and cost proxy | Generated skills remain under a 1200-word compactness budget and use only 2.2%, 4.43%, 9.54%, and 6.33% of the full extracted papers' deterministic input-token proxy. | PaperToSkill is cheaper than every summary or guarantees lower provider bills for every model and task. | `results/tables/compactness_source_grounding.md`; `results/tables/context_cost_proxy.md`; `results/tables/context_cost_proxy.json` | Supported for word-count compactness and deterministic token/cost proxy |
| Source grounding | Source-span validation finds zero invalid line ranges and support rates of 0.938, 1.0, 1.0, and 1.0 across the four generated skills. | Every generated instruction is semantically verified by human annotators. | `results/evaluations/*_source_span_validation_v0.json`; `results/tables/compactness_source_grounding.md` | Supported by deterministic span audit |
| Human fidelity readiness | Human-fidelity review protocol, four paper-specific review packets, a blank annotation template, and a pending annotation summary are prepared. | Human fidelity annotation has been completed or the skills are expert-validated. | `benchmarks/human_fidelity_review_v0.json`; `results/human_fidelity_packets/`; `results/human_fidelity_packets/annotation_summary.md` | Prepared, not completed |
| Transfer notes | Removing `Transfer Notes` lowers offline transfer-readiness from 10/10 to 7.6/10 across all four paper cases. | Transfer notes have been proven to improve live Claude/Codex success rates. | `results/evaluations/*_harness_transfer_v0.json`; `results/tables/transfer_ablation.md` | Supported for offline readiness |
| Live transfer | Prompt packets exist for later Codex-style and Claude-style live evaluation. | Live cross-harness execution has completed successfully. | `results/live_transfer_prompts/`; endpoint checks in `memory/short_term_memory.md` | Pending |
| Failure branches | PaperToSkill records 27 paper-reported and project-level failure/limitation cases as a first-class archive. | Failure-branch recording has been shown to improve final user outcomes or live reproduction success. | `benchmarks/failure_case_archive_v0.json`; `results/failure_cases/failure_case_archive.md`; `results/failure_cases/failure_case_archive.json` | Supported as provenance archive, not outcome evidence |
| Reproducibility package | A local package checker reports 105 ready checks, 5 pending external-evidence checks, and 0 failed checks. | The package is submission-complete or all live/human evidence has been collected. | `scripts/check_reproducibility_package.py`; `results/reproducibility/package_report.md`; `results/reproducibility/package_report.json` | Ready with pending external evidence |

## Required Downgrades In Drafting

- Say "curated paper notes" unless the experiment actually starts from raw PDF
  without human curation.
- Say "deterministic extracted-text note scaffold" for Phases 19-20 rather than
  "reliable end-to-end PDF automation."
- Say "deterministic coverage" or "offline readiness" unless live agent runs are
  available.
- Say "source-span support" rather than "factual correctness" unless human
  verification is added.
- Say "human-fidelity packets prepared" rather than "human-validated" until
  annotation rows are filled by independent reviewers and the summary reports
  complete with no errors.
- Say "deterministic token/cost proxy" rather than "provider billing" unless
  tokenizer-exact model prices and live invoices are added.

## Claims Ready For Abstract

1. PaperToSkill converts curated real-paper notes into compact, source-grounded
   skill artifacts.
2. In a four-paper benchmark, generated skills preserve substantially more
   deterministic operational coverage than generic summaries or abstract-only
   contexts.
3. Source anchors are mostly or fully supported by extracted paper spans, with no
   invalid ranges in the current benchmark.
4. Generated skills are compact relative to full extracted papers under both
   word-count and deterministic input-token proxy measurements.
5. Transfer notes improve offline transfer-readiness in a consistent ablation,
   while live cross-harness execution remains future work.
