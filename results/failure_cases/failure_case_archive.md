# Failure Case Archive

Evidence boundary: this archive aggregates paper-reported limitations and project-level failure/fix records. It is not a live reproduction failure study.

- Total cases: 27
- Paper-reported cases: 21
- Project-level cases: 6

## Category Counts

- cost: 2
- ethics: 1
- evaluation_validity: 2
- evaluator_bug: 1
- external_dependency: 1
- extraction_recall_bug: 1
- extractor_bug: 1
- memory_limit: 1
- missing_evidence: 1
- paper_limitation: 9
- quality_limit: 2
- quality_threshold: 2
- search_failure: 2
- source_span_bug: 1

## Cases

| id | scope | paper | phase | category | summary | resolution | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ai_scientist_v2_paper_failure_1 | paper | AI Scientist-v2 | source paper | quality_threshold | The acceptance was workshop-level rather than main-conference-level, and only one of three AI-generated submissions was accepted. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/ai_scientist_v2/references/source_map.json |
| ai_scientist_v2_paper_failure_2 | paper | AI Scientist-v2 | source paper | quality_threshold | The system does not consistently reach workshop-level quality and is not yet at top-tier conference standards. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/ai_scientist_v2/references/source_map.json |
| ai_scientist_v2_paper_failure_3 | paper | AI Scientist-v2 | source paper | quality_limit | The paper identifies remaining challenges in producing genuinely novel, high-impact hypotheses, designing innovative experiments, and rigorously justifying choices with deep domain expertise. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/ai_scientist_v2/references/source_map.json |
| ai_scientist_v2_paper_failure_4 | paper | AI Scientist-v2 | source paper | quality_limit | The authors observed citation inaccuracies and insufficient methodological rigor in generated manuscripts. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/ai_scientist_v2/references/source_map.json |
| ai_scientist_v2_paper_failure_5 | paper | AI Scientist-v2 | source paper | ethics | Ethical handling required IRB approval, reviewer disclosure, organizer coordination, and withdrawal of the accepted AI-generated paper before publication. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/ai_scientist_v2/references/source_map.json |
| reflexion_paper_failure_1 | paper | Reflexion | source paper | search_failure | Reflexion can still get stuck in local minima and has no formal guarantee of success. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/reflexion/references/source_map.json |
| reflexion_paper_failure_2 | paper | Reflexion | source paper | memory_limit | The memory component is limited to a sliding window in the paper, and the authors suggest more advanced structures for future work. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/reflexion/references/source_map.json |
| reflexion_paper_failure_3 | paper | Reflexion | source paper | paper_limitation | Some environments and tasks remain difficult, especially where very creative behavior or richer interaction is required. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/reflexion/references/source_map.json |
| aide_paper_failure_1 | paper | AIDE | source paper | evaluation_validity | Kaggle holdout sets may differ from official private test sets, so percentile scores may not always be directly comparable. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| aide_paper_failure_2 | paper | AIDE | source paper | evaluation_validity | There is possible data contamination because models may have seen competition-related data; the paper says live competition submissions are the only way to fully ensure no contamination. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| aide_paper_failure_3 | paper | AIDE | source paper | search_failure | AIDE can adopt a simple greedy policy that may lead to local optima on challenging R&D tasks. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| aide_paper_failure_4 | paper | AIDE | source paper | paper_limitation | AIDE fell short in environments requiring larger codebases or single improvements with multiple steps of interaction; in Rust CodeContests it repeated local patches instead of discovering new strategies. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| aide_paper_failure_5 | paper | AIDE | source paper | paper_limitation | While AIDE was developed for tabular machine-learning tasks, third-party experiments suggest the approach can generalize to neural architecture search, Triton Kernel optimization, and other AI R&D tasks. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| aide_paper_failure_6 | paper | AIDE | source paper | cost | LLM inference cost can reach approximately 2.50 USD for some tasks, although most Weco-Kaggle tasks stay under 1.50 USD in the reported GPT-4 Turbo pricing setup. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/aide/references/source_map.json |
| toolformer_paper_failure_1 | paper | Toolformer | source paper | paper_limitation | Existing tool-use approaches often rely on large human annotations or task-specific settings; Toolformer targets broader self-supervised tool use but still depends on a few demonstrations for each API. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_2 | paper | Toolformer | source paper | paper_limitation | Toolformer only supports tools whose inputs and outputs can be represented as text sequences, and tool execution depends on the external backend. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_3 | paper | Toolformer | source paper | cost | The paper uses heuristics to reduce computational cost when annotating the corpus with API calls. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_4 | paper | Toolformer | source paper | paper_limitation | For question answering, Toolformer still lags behind Atlas and is limited by simple interaction with the Wikipedia search API; it cannot reformulate queries or browse multiple top results in the reported setup. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_5 | paper | Toolformer | source paper | paper_limitation | Some temporal improvements cannot be fully attributed to the calendar API, because other effects also contribute. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_6 | paper | Toolformer | source paper | paper_limitation | The authors do not evaluate perplexity with API calls enabled because computing token probabilities would require marginalizing over possible API calls. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| toolformer_paper_failure_7 | paper | Toolformer | source paper | paper_limitation | Tool use emerges with model scale; smaller models benefit less from the provided APIs. | Preserve in generated skill failure cases and source maps; do not convert into a success claim. | generated_skills/toolformer/references/source_map.json |
| extractor_multiline_title_bug | project | PaperToSkill | Phase 1 | extractor_bug | Initial extraction split multiline Markdown list items and inferred the title incorrectly as `Methods`. | Merged continuation lines and inferred title from the first H1 or LaTeX title. | research/stage_log.md#Phase-1 |
| source_audit_section_mapping_bug | project | PaperToSkill | Phase 4 | evaluator_bug | The first source-map-aware audit mis-mapped section groups and incorrectly yielded unsupported rate 1.0 for all skills. | Mapped skill sections onto source-note section groups before scoring. | research/stage_log.md#Phase-4 |
| source_span_form_feed_shift | project | PaperToSkill | Phase 6 | source_span_bug | PDF form-feed characters shifted source-span anchors when Python `splitlines()` was used. | Switched source-span counting to newline-delimited lines. | research/stage_log.md#Phase-6 |
| aide_candidate_truncation | project | PaperToSkill | Phase 10 | extraction_recall_bug | AIDE exposed that workflow, validation, and failure candidate limits were too low and dropped data-preview plus LLM-cost content. | Raised candidate limits from 6/5/5 to 8/7/6 and added a regression test. | research/stage_log.md#Phase-10 |
| remote_endpoint_unavailable | project | PaperToSkill | Phases 0, 6, 10, 13, 16 | external_dependency | The OpenAI-compatible endpoint listed models but chat completions repeatedly returned account-pool or HTTP 503 errors, including a Phase 16 retest. | Recorded prompt packets and kept live claims downgraded to offline readiness until provider availability recovers. | memory/short_term_memory.md; research/run_logs/2026-06-17_phase13_human_fidelity_readiness.md; research/run_logs/2026-06-17_phase16_reproducibility_package.md |
| human_fidelity_pending | project | PaperToSkill | Phases 13-14 | missing_evidence | Human-fidelity review packets and annotation summary are prepared, but all 24 score rows remain pending. | Prepared packets, blank annotation template, and summarizer; kept human-validation claims out of the draft. | results/human_fidelity_packets/annotation_summary.md |
