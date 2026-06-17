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

Human-fidelity review packets, an annotation template, and a summary script have
been prepared, but no independent annotators have scored them yet. The current
annotation summary reports 18 pending rows and 0 scored rows. Source-span
validation reduces hallucination risk, and the packets make expert review
easier to run, but the current benchmark still should not be described as
human-validated.

### Cost Proxy Is Not Full Economic Cost

Generated skills are under a 1200-word budget and have a deterministic
input-token proxy that is much smaller than full extracted paper text. However,
the project has not yet computed tokenizer-exact model costs, provider-specific
prices, live invoices, or success-per-dollar. Cost claims should therefore
remain framed as token/cost proxies until a model-specific pricing experiment is
added.

### Failure Archive Is Not An Outcome Study

The failure-case archive records paper-reported limitations and project-level
failure/fix records, including extractor, evaluator, source-span, endpoint, and
missing-evidence issues. This improves provenance and claim discipline, but it
does not prove that recording failures improves live task outcomes or
reproduction success.

### Reproducibility Package Still Has External Pending Evidence

The reproducibility checker reports that local artifacts, deterministic results,
prompt packets, failure archive, human-fidelity protocol, and secret scan are
ready with zero failed checks. However, the same report still marks live
responses and completed human-fidelity annotation as pending external evidence.
The package should therefore be described as locally ready, not submission-final.

## Future Work

1. Execute live prompt packets once the remote endpoint is available, logging
   model, harness, prompt, response, intervention count, and task outcome.
2. Run the prepared human source-fidelity packets with independent annotators
   and report agreement or adjudication.
3. Extend extraction from curated notes toward raw PDF ingestion with automatic
   section detection, table handling, and citation-aware source maps.
4. Add tokenizer-exact model pricing and success-per-dollar accounting for
   full-paper, summary, and skill contexts.
5. Expand the benchmark with less procedural papers to test failure modes.
6. Preserve negative and failed branches as paper evidence rather than filtering
   them out of the research story.
