# PaperToSkill Rebuttal Bank

Date: 2026-06-17

Use this file to answer likely reviewer objections without exceeding the current
evidence boundary.

## Q1: Is PaperToSkill just another summarizer?

Short answer: No, but current evidence is deterministic/offline.

Evidence to cite:

- `results/tables/main_results.md`: generated skills outperform generic-summary
  and abstract-only baselines on deterministic operational coverage across AI
  Scientist-v2, Reflexion, AIDE, and Toolformer.
- `generated_skills/*/SKILL.md`: generated artifacts include workflow,
  validation, failure cases, transfer notes, and source anchors.
- `results/tables/transfer_ablation.md`: removing `Transfer Notes` lowers
  offline readiness from 10/10 to 7.6/10 across all four cases.

Do not say:

- "Skills improve live agent success over summaries."
- "The generated skills are semantically complete."

## Q2: How do you prevent hallucinated instructions?

Short answer: PaperToSkill uses source maps and source-span validation as local
guards, but human semantic validation is pending.

Evidence to cite:

- `generated_skills/*/references/source_map.json`
- `results/tables/compactness_source_grounding.md`
- Source-span support rates: 0.938, 1.0, 1.0, and 1.0 with zero invalid ranges.
- `results/human_fidelity_packets/annotation_summary.md`: human annotation is
  prepared but pending.

Do not say:

- "All instructions are human-verified."
- "Source-span support proves factual correctness."

## Q3: Why are the inputs curated notes instead of raw PDFs?

Short answer: This paper isolates the paper-note-to-skill conversion layer first
so fidelity, compactness, and transfer readiness can be measured before claiming
full PDF automation. Phases 19-20 add deterministic extracted-text-to-note
scaffolds for Toolformer and AIDE, but they remain auditable scaffolds rather
than a general arbitrary-PDF solution.

Evidence to cite:

- `papers/raw/` and `papers/extracted/` show PDFs were collected and extracted.
- `papers/notes/` contains curated source-anchored notes used as scaffold input.
- `scripts/papertoskill_note_from_text.py` and
  `results/tables/auto_note_comparison.md` show the Toolformer and AIDE
  extracted-text scaffold results.
- `paper/limitations.md` explicitly states the curated-note boundary.

Do not say:

- "PaperToSkill fully automatically converts arbitrary PDFs."
- "The Toolformer and AIDE auto-note results prove robust PDF automation."

## Q4: Are the metrics too heuristic?

Short answer: Yes, they are deterministic gates rather than final semantic or
live-agent evidence; the paper is explicit about that boundary.

Evidence to cite:

- `paper/limitations.md`: heuristic metric limitation.
- `results/reproducibility/package_report.md`: local package readiness and
  pending external evidence are separated.
- `results/human_fidelity_packets/`: prepared protocol for later human scoring.

Do not say:

- "The metrics replace human review."
- "The deterministic score proves real-world usability."

## Q5: Does transfer readiness prove Codex-to-Claude transfer?

Short answer: Not yet. It proves only that the artifact contains offline
readiness signals for target-harness adaptation.

Evidence to cite:

- `results/tables/transfer_ablation.md`
- `results/live_transfer_prompts/`: prompt packets are prepared.
- `research/run_logs/2026-06-17_phase16_reproducibility_package.md`: endpoint
  retest returned HTTP 503 for chat completions.

Do not say:

- "Codex-to-Claude transfer succeeded."
- "Transfer notes improve live success rate."

## Q6: What is the economic claim?

Short answer: Generated skills compress full extracted paper context under both
a deterministic character proxy and a local `o200k_base` tokenizer-aware proxy
while preserving more operational coverage than short summaries.

Evidence to cite:

- `results/tables/context_cost_proxy.md`
- `results/tables/context_cost_proxy_tokenizer.md`
- AI Scientist-v2: 1,079 `o200k_base` tokens vs 45,212 for full extracted paper.
- Reflexion: 703 vs 16,414.
- AIDE: 1,285 vs 13,312.
- Toolformer: 1,255 vs 20,365.
- Toolformer: 1,526 vs 24,097.

Do not say:

- "PaperToSkill guarantees lower provider bills."
- "The system improves success per dollar."

## Q7: Why archive failures?

Short answer: The archive preserves limitations and project-level failure/fix
records as provenance so the paper does not become a success-only narrative.

Evidence to cite:

- `results/failure_cases/failure_case_archive.md`: 27 cases, 21 paper-reported
  and 6 project-level.
- `paper/limitations.md`: failure archive is not an outcome study.

Do not say:

- "Failure recording has been shown to improve final user outcomes."

## Q8: What must be done before a stronger submission?

Short answer: Complete live response collection, independent human-fidelity
annotation, and either a less-procedural stress case or stronger PDF automation.

Evidence to cite:

- `results/reproducibility/package_report.md`: 7 pending external-evidence
  checks and 0 failed local checks.
- `results/model_ablation_prompts/v0/run_report.md`: current Claude/GPT-family
  attempt is blocked by provider account availability and missing GPT-family
  aliases, not completed model evidence.
- `research/review_report.md`: submission gate status.

Do not say:

- "The package is final."
- "All validation is complete."
