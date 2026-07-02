# Paper Claim Checklist

Use this file as the gate before promoting a claim into the paper. Prefer the
supported wording. Do not use the unsupported wording until the missing evidence
exists.

| Claim Area | Supported Wording | Unsupported Wording | Evidence | Status |
| --- | --- | --- | --- | --- |
| Conversion | PaperToSkill converts curated paper notes for four real agent/tool-method papers into compact `SKILL.md` artifacts with source maps. | PaperToSkill fully automatically converts arbitrary PDFs into reliable skills. | `generated_skills/ai_scientist_v2/SKILL.md`; `generated_skills/reflexion/SKILL.md`; `generated_skills/aide/SKILL.md`; `generated_skills/toolformer/SKILL.md`; `scripts/papertoskill_extract.py` | Supported |
| Automatic note scaffold | PaperToSkill can generate deterministic, source-anchored note scaffolds from extracted Toolformer and AIDE text and convert them into auditable skills that pass offline gates; the local pipeline command composes this path into a manifest, note, skill, source map, and rubric report, and it can also smoke-test a direct PDF input through `pdftotext -layout` when that command is available. | PaperToSkill now reliably converts arbitrary PDFs into final skills without audit. | `scripts/papertoskill_note_from_text.py`; `scripts/papertoskill_pipeline.py`; `papers/auto_notes/toolformer_auto_note.md`; `papers/auto_notes/aide_auto_note.md`; `generated_skills/toolformer_auto/SKILL.md`; `generated_skills/aide_auto/SKILL.md`; `results/tables/auto_note_comparison.md`; `results/reproducibility/usage_example_report.md`; `research/run_logs/2026-06-19_phase35_pdf_pipeline_input.md` | Supported for two extracted-text scaffolds and local PDF smoke input |
| Structural quality | All four generated skills score 20/20 on deterministic paper-specific rubrics. | The generated skills are human-validated as complete reproductions of the papers. | `results/evaluations/*_rubric_v0.json`; `results/tables/main_results.md` | Supported |
| Summary comparison | Generated skills preserve more deterministic task-relevant operational coverage than generic-summary and abstract-only baselines across four papers. | Skills improve live agent task success over summaries. | `results/evaluations/*_context_baselines_v0.json`; `results/tables/main_results.md` | Supported for deterministic coverage |
| Compactness and cost proxy | Generated skills remain under a 1200-word compactness budget and use only 2.39%, 4.28%, 9.65%, and 6.16% of the full extracted papers' `o200k_base` tokenizer-aware input-token proxy. The six saved Claude/GPT-family/DeepSeek model-ablation responses total 9,594 local `o200k_base` output tokens. The local token-accounting summary combines generated-skill input tokens and saved-response output tokens for the current evidence set. The earlier character proxy remains available as a sensitivity check. | PaperToSkill is cheaper than every summary or guarantees lower provider bills for every model and task. | `results/tables/compactness_source_grounding.md`; `results/tables/context_cost_proxy.md`; `results/tables/context_cost_proxy.json`; `results/tables/context_cost_proxy_tokenizer.md`; `results/tables/context_cost_proxy_tokenizer.json`; `scripts/evaluate_model_response_costs.py`; `results/tables/model_response_cost_proxy.md`; `results/tables/model_response_cost_proxy.json`; `results/token_accounting/token_accounting_summary.md` | Supported for word-count compactness and local input/output token proxies; not provider billing |
| Source grounding | Source-span validation finds zero invalid line ranges and support rates of 0.938, 1.0, 1.0, and 1.0 across the four generated skills. | Every generated instruction is semantically verified by human annotators. | `results/evaluations/*_source_span_validation_v0.json`; `results/tables/compactness_source_grounding.md` | Supported by deterministic span audit |
| Human fidelity readiness | Human-fidelity review protocol, four paper-specific review packets, reviewer handoff guide, stricter blank annotation template, and a pending annotation summary are prepared. | Human fidelity annotation has been completed or the skills are expert-validated. | `benchmarks/human_fidelity_review_v0.json`; `results/human_fidelity_packets/`; `results/human_fidelity_packets/annotation_guide.md`; `results/human_fidelity_packets/annotation_summary.md` | Prepared, not completed |
| Transfer notes | Removing `Transfer Notes` lowers offline transfer-readiness from 10/10 to 7.6/10 across all four paper cases. | Transfer notes have been proven to improve live Claude/Codex success rates. | `results/evaluations/*_harness_transfer_v0.json`; `results/tables/transfer_ablation.md` | Supported for offline readiness |
| Live transfer | Prompt packets exist for Codex-style and Claude-style live evaluation; all four paper response sets are saved and deterministically scored under the current output-contract evaluator. This is saved-response evidence, not human semantic fidelity or real live task success. | Live agent task execution has succeeded for all papers, saved-response scoring proves semantic correctness, or output-contract scoring proves user-facing task success. | `results/live_transfer_prompts/`; `results/live_transfer_prompts/ai_scientist_v2_v0/run_report.md`; `results/live_transfer_prompts/reflexion_v0/run_report.md`; `results/live_transfer_prompts/aide_v0/run_report.md`; `results/live_transfer_prompts/toolformer_v0/run_report.md`; `results/live_transfer_prompts/evaluation.md`; `research/run_logs/2026-06-19_phase40_all_live_transfer_responses.md` | Saved-response coverage complete; live task success and human fidelity pending |
| Model ablations | Claude Opus 4.8, GPT-family, and DeepSeek each have two saved/scored rows in the current protocol. GPT-family refreshed both rows through Responses with `gpt-5.5`; DeepSeek used `deepseek-v4-flash`; latest Claude protocol refresh was provider-blocked by HTTP 502, so scored Claude rows are older saved files. | Saved-response model-ablation scoring proves live task success, provider economics, or broad model quality; provider errors are negative model-quality evidence. | `benchmarks/model_ablation_v0.json`; `results/model_ablation_prompts/v0/`; `results/model_ablation_prompts/v0/responses/`; `scripts/run_model_ablation_prompts.py`; `scripts/evaluate_model_ablation_responses.py`; `results/model_ablation_prompts/v0/run_report.md`; `results/model_ablation_prompts/v0/gpt_protocol_run_report.md`; `results/model_ablation_prompts/v0/deepseek_run_report.md`; `results/model_ablation_prompts/v0/claude_protocol_run_report.md`; `results/model_ablation_prompts/v0/evaluation.md`; `examples/usage/model_ablation_usage.md` | Saved-response scoring complete for current protocol; live task success and provider economics remain unproven |
| Usage examples | Usage examples exist and pass a local usage-example checker that validates files, model-ablation prompt/response slots, an offline auto-note-to-skill example chain, a one-command AIDE pipeline run, and a direct-PDF pipeline smoke run. | Usage examples prove live Claude/GPT/DeepSeek success or human usability. | `examples/usage/`; `scripts/check_usage_examples.py`; `scripts/papertoskill_pipeline.py`; `results/reproducibility/usage_example_report.md`; `research/run_logs/2026-06-19_phase35_pdf_pipeline_input.md` | Prepared and locally verified |
| AAAI paper package | The paper has an AAAI-27 LaTeX draft package using the official downloaded author kit, and the current local build artifacts, result tables, and claim boundaries pass local checkers. | The paper is submission-final or accepted by AAAI. | `paper/aaai/README.md`; `paper/aaai/papertoskill_aaai2027.tex`; `paper/aaai/aaai2027.sty`; `scripts/check_aaai_package.py`; `scripts/check_paper_tables.py`; `scripts/check_paper_claims.py`; `results/reproducibility/aaai_package_report.md`; `results/reproducibility/paper_table_report.md`; `results/reproducibility/paper_claim_report.md` | Prepared and locally verified |
| Failure branches | PaperToSkill records 27 paper-reported and project-level failure/limitation cases as a first-class archive. | Failure-branch recording has been shown to improve final user outcomes or live reproduction success. | `benchmarks/failure_case_archive_v0.json`; `results/failure_cases/failure_case_archive.md`; `results/failure_cases/failure_case_archive.json` | Supported as provenance archive, not outcome evidence |
| Paper2Agent comparison | PaperToSkill includes a bounded source-backed artifact/workflow comparison against Paper2Agent over required inputs, generated artifact type, setup burden, validation checks, failure handling, source traceability, and runtime dependency. | PaperToSkill has beaten Paper2Agent in an end-to-end MCP baseline or runtime benchmark. | `scripts/compare_paper2agent_artifacts.py`; `results/tables/paper2agent_artifact_comparison.md`; `results/tables/paper2agent_artifact_comparison.json` | Supported as artifact/workflow positioning; not executable baseline performance |
| Reproducibility package | A local package checker reports local readiness while separating completed bounded AI-Scientist-v2 integration evidence from pending human-fidelity annotation and final submission-policy evidence. | The package is submission-complete or all live/human/model/economic evidence has been collected. | `scripts/check_reproducibility_package.py`; `results/reproducibility/package_report.md`; `results/reproducibility/package_report.json`; `results/reproducibility/paper_claim_report.md`; `results/ai_scientist_v2_smoke/run_report.md`; `results/ai_scientist_v2_live_run_handoff/handoff.md` | Ready with pending external evidence |

## Required Downgrades In Drafting

- Say "curated paper notes" unless the experiment actually starts from raw PDF
  without human curation.
- Say "deterministic extracted-text note scaffold" for Phases 19-20 and "local
  PDF smoke input" for Phase 35 rather than "reliable end-to-end PDF
  automation."
- Say "deterministic coverage" or "offline readiness" unless live agent runs are
  available.
- Say "source-span support" rather than "factual correctness" unless human
  verification is added.
- Say "human-fidelity packets prepared" rather than "human-validated" until
  annotation rows are filled by independent reviewers and the summary reports
  complete with no errors.
- Say "local input/output token proxy" or "`o200k_base` tokenizer-aware proxy"
  rather than "provider billing" unless provider-specific prices, realized
  output bills, and live invoices are added.
- Say "Claude/GPT-family/DeepSeek saved-response rows are scored under the
  current two-case protocol" rather than implying live task success, broad
  model quality, or provider economics.
- Say "bounded Paper2Agent artifact/workflow comparison" rather than
  "Paper2Agent baseline" unless an MCP server is actually run.

## Claims Ready For Abstract

1. PaperToSkill converts curated real-paper notes into compact, source-grounded
   skill artifacts.
2. In a four-paper benchmark, generated skills preserve substantially more
   deterministic operational coverage than generic summaries or abstract-only
   contexts.
3. Source anchors are mostly or fully supported by extracted paper spans, with no
   invalid ranges in the current benchmark.
4. Generated skills are compact relative to full extracted papers under word
   count, character-proxy, and local tokenizer-aware measurements; saved
   Claude/GPT-family responses also have local output-token proxy accounting.
5. Transfer notes improve offline transfer-readiness in a consistent ablation;
   all four live-transfer saved-response sets are collected and scored under a
   deterministic output-contract evaluator, while human semantic fidelity and
   real live task success remain future work.
