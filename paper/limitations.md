# Limitations And Future Work

## Current Evidence Boundary

The current PaperToSkill evidence is deterministic and offline. It supports
claims about artifact structure, source-span support, compactness, context
coverage, and transfer readiness. It includes saved and scored live-transfer
responses for all four paper packets under a deterministic output-contract
evaluator, but does not yet support claims about live agent task success,
human-rated fidelity, or realized cost savings.

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

### Saved Live-Transfer Responses Are Not Task Success

Prompt packets have been generated for Codex-style and Claude-style harnesses.
All four paper response sets are saved and scored across both harness prompt
styles and all three context variants. This completes saved-response coverage
for the current prompt-packet protocol. However, the scorer is deterministic and
contract-based, so live task success-rate claims and human semantic-fidelity
claims remain unsupported.

### AI-Scientist-v2 Integration Is Bounded

The AI-Scientist-v2 marker smoke and one bounded full live run are complete for
the current local gate. The run is useful integration evidence and produced a
synthetic sensitivity result, but it should not be described as human semantic
fidelity, real-data validation, or broad live research-task success. The
HF/semantic-data branch remains a failed branch because dataset loading was
invalid and `sentence_transformers` was missing.

### Model Ablations Partially Completed

Claude/GPT-family/DeepSeek model-ablation prompt packets, a runner, and a
response evaluator are prepared. The latest live recheck completed both Claude
Opus 4.8 prompt rows, saved response files, and scored both rows 6/6. A later
GPT-family protocol refresh saved both rows with `gpt-5.5`, and DeepSeek saved
both rows with `deepseek-v4-flash`; all six saved rows score 6/6. The latest
Claude protocol refresh used Anthropic Messages but was blocked by provider
HTTP 502, so the scored Claude rows come from earlier saved response files.
These rows are saved-response evidence for the current two-case prompt
protocol; provider errors are availability history, not model-quality evidence.

### Limited Benchmark Diversity

The current four-paper benchmark focuses on agent, ML-engineering, and
tool-use methods: AI Scientist-v2, Reflexion, AIDE, and Toolformer. These
papers are still naturally procedural, which is favorable for skill extraction.
Future work should include interface papers and theory-heavy papers where
procedural structure is weaker.

### No Human Fidelity Study Yet

Human-fidelity review packets, an annotation guide, a stricter blank annotation
template, and a summary script have been prepared, but no independent
annotators have scored them yet. The current annotation summary reports 24
pending rows and 0 scored rows. Source-span validation reduces hallucination
risk, and the packets make expert review easier to run, but the current
benchmark still should not be described as human-validated.

### Cost Proxy Is Not Full Economic Cost

Generated skills are under a 1200-word budget and have both a deterministic
character-based input-token proxy and a local `o200k_base` tokenizer-aware proxy
that are much smaller than full extracted paper text. Phase 38 also adds a local
output-token proxy over saved Claude/GPT-family model-ablation responses.
However, the project has not computed provider-specific prices, live invoices,
realized provider output bills, or success-per-dollar. Cost claims should
therefore remain framed as local input/output token proxies. Provider billing
and success-per-dollar are outside the current claim set unless a separate
future evidence policy explicitly reopens them.

### Failure Archive Is Not An Outcome Study

The failure-case archive records paper-reported limitations and project-level
failure/fix records, including extractor, evaluator, source-span, endpoint, and
missing-evidence issues. This improves provenance and claim discipline, but it
does not prove that recording failures improves live task outcomes or
reproduction success.

### Reproducibility Package Still Has External Pending Evidence

The reproducibility checker reports that local artifacts, deterministic results,
prompt packets, saved live-transfer responses, failure archive, human-fidelity
protocol, and secret scan are ready with zero failed checks. However, the same
report still marks completed human-fidelity annotation as pending external
evidence. The AAAI decision is recorded as `wait_for_external_evidence`, so the
package should therefore be described as locally ready, not submission-final.

## Future Work

1. Run the prepared human source-fidelity packets with independent annotators
   and report agreement or adjudication.
2. Extend extraction from curated notes toward raw PDF ingestion with stronger
   section detection, table handling, citation-aware source maps, and
   multi-paper auto-note validation.
3. If future economics claims are desired, define a separate billing protocol
   with provider-specific prices, live invoices, realized output-token bills,
   and success-per-dollar accounting before making those claims.
4. Extend the bounded Paper2Agent artifact/workflow comparison into a real
   executable MCP baseline if Paper2Agent setup resources are available.
5. Expand the benchmark with less procedural papers to test failure modes.
6. Preserve negative and failed branches as paper evidence rather than filtering
   them out of the research story.
