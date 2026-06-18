# Limitations And Future Work

## Current Evidence Boundary

The current PaperToSkill evidence is deterministic and offline. It supports
claims about artifact structure, source-span support, compactness, context
coverage, and transfer readiness. It includes one saved and scored Toolformer
live-transfer response set, but does not yet support claims about complete live
agent task success across all papers, human-rated fidelity, or realized cost
savings.

## Limitations

### Curated Input Notes

The current pipeline converts curated source-anchored paper notes into skills.
Raw PDFs are downloaded and extracted, but the paper notes are still manually
curated. This means the current benchmark validates the paper-note-to-skill
conversion layer more strongly than the full PDF-to-skill pipeline.

Phases 19-20 add deterministic extracted-text-to-note scaffolds and validate
them on Toolformer and AIDE, but that evidence covers two papers and two
extracted-text profiles. They should be described as auditable scaffolds, not as
reliable arbitrary-PDF automation.

### Heuristic Metrics

The rubrics, context coverage, source-span support, and transfer-readiness
metrics are deterministic. They make experiments reproducible, but they remain
sensitive to lexical overlap, section naming, and rubric design. They should be
treated as early gates rather than a substitute for human or live-agent
evaluation.

### Live Cross-Harness Runs Are Partial

Prompt packets have been generated for Codex-style and Claude-style harnesses.
The Toolformer response set is saved and scored across both harness prompt
styles and all three context variants. AI Scientist-v2, Reflexion, and AIDE
response sets remain pending, so full live cross-harness completion and live
success-rate claims remain unsupported.

### Model Ablations Partially Completed

Claude/GPT-family/DeepSeek model-ablation prompt packets, a runner, and a
response evaluator are prepared. The latest live recheck completed both Claude
Opus 4.8 prompt rows, saved response files, and scored both rows 6/6. A later
GPT-family retry with the separate GPT credential profile also saved both
current GPT-family rows: the Toolformer row timed out on `gpt-5.5` and then
succeeded with `gpt-5.4`, while the AIDE row succeeded with `gpt-5.5`. Both
GPT-family rows scored 6/6. DeepSeek remains an unattempted follow-up slot.
The Claude and GPT-family rows are model-response evidence for the current
two-case prompt protocol; the earlier GPT 502 failures are provider
availability history, not GPT model-quality evidence.

### Limited Benchmark Diversity

The current four-paper benchmark focuses on agent, ML-engineering, and
tool-use methods: AI Scientist-v2, Reflexion, AIDE, and Toolformer. These
papers are still naturally procedural, which is favorable for skill extraction.
Future work should include interface papers and theory-heavy papers where
procedural structure is weaker.

### No Human Fidelity Study Yet

Human-fidelity review packets, an annotation template, and a summary script have
been prepared, but no independent annotators have scored them yet. The current
annotation summary reports 24 pending rows and 0 scored rows. Source-span
validation reduces hallucination risk, and the packets make expert review
easier to run, but the current benchmark still should not be described as
human-validated.

### Cost Proxy Is Not Full Economic Cost

Generated skills are under a 1200-word budget and have both a deterministic
character-based input-token proxy and a local `o200k_base` tokenizer-aware proxy
that are much smaller than full extracted paper text. Phase 38 also adds a local
output-token proxy over saved Claude/GPT-family model-ablation responses.
However, the project has not yet computed provider-specific prices, live
invoices, realized provider output bills, or success-per-dollar. Cost claims
should therefore remain framed as local input/output token proxies until a
provider-specific pricing experiment is added.

### Failure Archive Is Not An Outcome Study

The failure-case archive records paper-reported limitations and project-level
failure/fix records, including extractor, evaluator, source-span, endpoint, and
missing-evidence issues. This improves provenance and claim discipline, but it
does not prove that recording failures improves live task outcomes or
reproduction success.

### Reproducibility Package Still Has External Pending Evidence

The reproducibility checker reports that local artifacts, deterministic results,
prompt packets, failure archive, human-fidelity protocol, and secret scan are
ready with zero failed checks. However, the same report still marks the
remaining live responses and completed human-fidelity annotation as pending
external evidence. The package should therefore be described as locally ready,
not submission-final.

## Future Work

1. Execute the remaining AI Scientist-v2, Reflexion, and AIDE live prompt
   packets, logging model, harness, prompt, response, intervention count, and
   task outcome.
2. Add the user's concrete DeepSeek model alias and endpoint profile, then run
   and score the same prompt grid.
3. Run the prepared human source-fidelity packets with independent annotators
   and report agreement or adjudication.
4. Extend extraction from curated notes toward raw PDF ingestion with stronger
   section detection, table handling, citation-aware source maps, and
   multi-paper auto-note validation.
5. Add provider-specific pricing, live invoices, realized output-token bills,
   and success-per-dollar accounting for full-paper, summary, skill, and saved
   response contexts.
6. Expand the benchmark with less procedural papers to test failure modes.
7. Preserve negative and failed branches as paper evidence rather than filtering
   them out of the research story.
