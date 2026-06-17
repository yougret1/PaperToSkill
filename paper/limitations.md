# Limitations And Future Work

## Current Evidence Boundary

The current PaperToSkill evidence is deterministic and offline. It supports
claims about artifact structure, source-span support, compactness, context
coverage, and transfer readiness. It does not yet support claims about live
agent task success, human-rated fidelity, or realized cost savings.

## Limitations

### Curated Input Notes

The current pipeline converts curated source-anchored paper notes into skills.
Raw PDFs are downloaded and extracted, but the paper notes are still manually
curated. This means the current benchmark validates the paper-note-to-skill
conversion layer more strongly than the full PDF-to-skill pipeline.

### Heuristic Metrics

The rubrics, context coverage, source-span support, and transfer-readiness
metrics are deterministic. They make experiments reproducible, but they remain
sensitive to lexical overlap, section naming, and rubric design. They should be
treated as early gates rather than a substitute for human or live-agent
evaluation.

### No Completed Live Cross-Harness Runs

Prompt packets have been generated for Codex-style and Claude-style harnesses,
but the remote chat-completion endpoint returned service errors during the
latest checks. As a result, transfer results are currently offline readiness
scores, not live success rates.

### Limited Benchmark Diversity

The current three-paper benchmark focuses on agent and ML-engineering methods:
AI Scientist-v2, Reflexion, and AIDE. These papers are naturally procedural,
which is favorable for skill extraction. Future work should include tool-use
papers, interface papers, and theory-heavy papers where procedural structure is
weaker.

### No Human Fidelity Study Yet

No independent annotators have judged whether each generated skill preserves the
paper's intended contribution. Source-span validation reduces hallucination
risk, but it is not equivalent to expert fidelity review.

### Compactness Is Not Full Economic Cost

Generated skills are under a 1200-word budget, but the project has not yet
computed token-level cost, model-specific pricing, or success-per-dollar. Cost
claims should therefore remain framed as compactness claims until a pricing
experiment is added.

## Future Work

1. Execute live prompt packets once the remote endpoint is available, logging
   model, harness, prompt, response, intervention count, and task outcome.
2. Add human source-fidelity annotation for generated skills and summaries.
3. Extend extraction from curated notes toward raw PDF ingestion with automatic
   section detection, table handling, and citation-aware source maps.
4. Add token and price accounting for full-paper, summary, and skill contexts.
5. Expand the benchmark with less procedural papers to test failure modes.
6. Preserve negative and failed branches as paper evidence rather than filtering
   them out of the research story.
