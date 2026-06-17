# Paper Claim Checklist

Use this file as the gate before promoting a claim into the paper. Prefer the
supported wording. Do not use the unsupported wording until the missing evidence
exists.

| Claim Area | Supported Wording | Unsupported Wording | Evidence | Status |
| --- | --- | --- | --- | --- |
| Conversion | PaperToSkill converts curated paper notes for three real agent-method papers into compact `SKILL.md` artifacts with source maps. | PaperToSkill fully automatically converts arbitrary PDFs into reliable skills. | `generated_skills/ai_scientist_v2/SKILL.md`; `generated_skills/reflexion/SKILL.md`; `generated_skills/aide/SKILL.md`; `scripts/papertoskill_extract.py` | Supported |
| Structural quality | All three generated skills score 20/20 on deterministic paper-specific rubrics. | The generated skills are human-validated as complete reproductions of the papers. | `results/evaluations/*_rubric_v0.json`; `results/tables/main_results.md` | Supported |
| Summary comparison | Generated skills preserve more deterministic task-relevant operational coverage than generic-summary and abstract-only baselines across three papers. | Skills improve live agent task success over summaries. | `results/evaluations/*_context_baselines_v0.json`; `results/tables/main_results.md` | Supported for deterministic coverage |
| Compactness and cost proxy | Generated skills remain under a 1200-word compactness budget and use only 2.2%, 4.43%, and 9.54% of the full extracted papers' deterministic input-token proxy. | PaperToSkill is cheaper than every summary or guarantees lower provider bills for every model and task. | `results/tables/compactness_source_grounding.md`; `results/tables/context_cost_proxy.md`; `results/tables/context_cost_proxy.json` | Supported for word-count compactness and deterministic token/cost proxy |
| Source grounding | Source-span validation finds zero invalid line ranges and support rates of 0.938, 1.0, and 1.0 across the three generated skills. | Every generated instruction is semantically verified by human annotators. | `results/evaluations/*_source_span_validation_v0.json`; `results/tables/compactness_source_grounding.md` | Supported by deterministic span audit |
| Transfer notes | Removing `Transfer Notes` lowers offline transfer-readiness from 10/10 to 7.6/10 across all three paper cases. | Transfer notes have been proven to improve live Claude/Codex success rates. | `results/evaluations/*_harness_transfer_v0.json`; `results/tables/transfer_ablation.md` | Supported for offline readiness |
| Live transfer | Prompt packets exist for later Codex-style and Claude-style live evaluation. | Live cross-harness execution has completed successfully. | `results/live_transfer_prompts/`; endpoint checks in `memory/short_term_memory.md` | Pending |
| Failure branches | PaperToSkill records failure cases and source-audit risks as first-class artifacts. | Failure-branch recording has been shown to improve final user outcomes. | `results/result_cards.md`; `results/evaluations/skill_source_audit_v0.json` | Partially supported |

## Required Downgrades In Drafting

- Say "curated paper notes" unless the experiment actually starts from raw PDF
  without human curation.
- Say "deterministic coverage" or "offline readiness" unless live agent runs are
  available.
- Say "source-span support" rather than "factual correctness" unless human
  verification is added.
- Say "deterministic token/cost proxy" rather than "provider billing" unless
  tokenizer-exact model prices and live invoices are added.

## Claims Ready For Abstract

1. PaperToSkill converts curated real-paper notes into compact, source-grounded
   skill artifacts.
2. In a three-paper benchmark, generated skills preserve substantially more
   deterministic operational coverage than generic summaries or abstract-only
   contexts.
3. Source anchors are mostly or fully supported by extracted paper spans, with no
   invalid ranges in the current benchmark.
4. Generated skills are compact relative to full extracted papers under both
   word-count and deterministic input-token proxy measurements.
5. Transfer notes improve offline transfer-readiness in a consistent ablation,
   while live cross-harness execution remains future work.
