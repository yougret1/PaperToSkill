# PaperToSkill: Turning Research Papers into Portable Agent Skills

## Abstract

Many LLM and agent papers introduce workflows that could help ordinary users and
agent builders, but those workflows are usually described for human reading
rather than direct reuse. Summaries compress the idea, but often discard the
procedural details, validation checks, assumptions, and failure branches needed
to apply the method. We introduce PaperToSkill, a paper-to-skill conversion
workflow that turns source-anchored paper notes into compact, human-editable
agent skills. Each skill records the paper's contribution, use conditions,
workflow, validation checks, failure cases, transfer notes, and source anchors.
In a four-paper benchmark over AI Scientist-v2, Reflexion, AIDE, and Toolformer,
PaperToSkill generates skills that score 20/20 on deterministic structural
rubrics, preserve more deterministic operational coverage than generic-summary
and abstract-only baselines, remain under a 1200-word compactness budget, and
use only 2.2%, 4.43%, 9.54%, and 6.33% of the full extracted papers'
deterministic input-token proxy. The generated skills also achieve high
source-span support with zero invalid line ranges. Removing transfer notes
consistently lowers
offline transfer-readiness from 10/10 to 7.6/10. These results support
PaperToSkill as a reproducible conversion layer from curated paper notes to
portable skills, while live cross-harness agent execution and human fidelity
studies remain future work.

## 1. Introduction

Using LLMs is becoming a practical skill for researchers, builders, and
non-expert users. At the same time, many of the best ways to use LLM agents are
introduced in papers whose methods are difficult to operationalize. A paper may
describe a search policy, memory loop, validation stage, or interface contract,
but a user who wants to reuse the contribution must translate prose into an
agent workflow by hand.

PaperToSkill studies a simple hypothesis: papers can be converted into compact,
editable skills that preserve enough procedural knowledge for agents and users
to reuse the main contribution. We use "skill" to mean a natural-language
operational artifact with an entry-point `SKILL.md`, similar to the format used
by agent harnesses that load task-specific instructions. Unlike a summary, a
skill is not only explanatory. It should specify when to use the method, which
inputs are required, which steps to execute, how to validate progress, which
failures to watch for, and how to adapt the instructions across harnesses.

This paper takes an artifact-first view. PaperToSkill is not presented as a
fully automatic PDF understanding system. The current implementation converts
curated, source-anchored paper notes into skills and source maps. This narrow
scope is intentional: it lets us evaluate whether the conversion layer preserves
operational knowledge before claiming end-to-end PDF automation.

We also introduce deterministic extracted-text-to-note scaffolds. These
scaffolds select source-anchored line windows from extracted paper text and
emit auditable Markdown notes before skill extraction. We evaluate them
separately from the curated-note main benchmark so they reduce the curation gap
without becoming an unsupported arbitrary-PDF automation claim.

The current contributions are:

1. a paper-to-skill schema for operationalizing research contributions;
2. a deterministic extraction scaffold that emits `SKILL.md` plus source maps;
3. deterministic extracted-text-to-note scaffolds evaluated on Toolformer and
   AIDE;
4. a four-paper benchmark using AI Scientist-v2, Reflexion, AIDE, and
   Toolformer;
5. deterministic/offline evaluations for structure, context coverage,
   compactness, source grounding, and transfer readiness;
6. a claim discipline that separates validated evidence from pending live-agent
   claims, including a first-class archive of paper-reported and project-level
   failure cases.

## 2. Related Work

PaperToSkill is motivated by several lines of agent research. Automated research
systems such as AI Scientist-v2 and Agent Laboratory show how agents can plan,
execute, analyze, write, and review research workflows. Code and experiment
search systems such as AIDE frame ML engineering as a search problem over code
solutions, debug loops, and performance records. Skill-library systems such as
Voyager show how reusable skills can support open-ended exploration. Reflection
methods such as Reflexion demonstrate that verbal feedback and episodic memory
can improve later attempts without weight updates. Tool and interface papers
such as Toolformer and SWE-agent show that agent behavior often depends on
explicit tool contracts and interface design.

These papers each contribute reusable procedures, but the procedures remain
inside the paper or the original system. PaperToSkill targets the conversion
layer: extracting operational knowledge from papers into compact skills with
validation checks, failure branches, and transfer notes.

## 3. Method

PaperToSkill represents each converted paper as a skill package. The main file is
`SKILL.md`; optional references include a source map that links generated skill
bullets to source note sections and line spans.

The schema contains:

- identity and central contribution;
- when the skill should be used;
- required inputs and artifacts;
- workflow steps an agent can execute;
- validation checks;
- failure cases and limitations;
- transfer notes for adapting the skill to another harness;
- source notes that distinguish source-backed material from inferred guidance.

The deterministic extractor reads a source-anchored paper note, normalizes
Markdown sections and list items, collects candidates from abstract, methods,
experiments, limitations, and transfer sections, then emits a compact skill.
Candidate limits keep the artifact within a practical context budget while
preserving method, validation, and failure coverage. The extractor also writes a
`references/source_map.json` file so later audits can inspect which source
section supports each generated instruction.

The text-to-note scaffold is an earlier pre-processing step. It operates on
newline-numbered extracted text, detects broad paper regions, selects line
windows for methods, experiments, and limitations, and preserves line anchors.
For two-column extracted text, it keeps raw line spacing and selects the
keyword-bearing column while retaining the original source line range. The
output is explicitly marked as an audit scaffold.

## 4. Experimental Setup

We evaluate four real agent-method papers:

- AI Scientist-v2, representing an automated research workflow with agentic tree
  search and multi-stage experiment management;
- Reflexion, representing verbal reflection, retry policy, and episodic memory;
- AIDE, representing code-space tree search for ML engineering;
- Toolformer, representing self-supervised tool-use data generation, API-call
  filtering, and inference-time tool execution.

For each paper, we create a curated source-anchored note from the extracted paper
text, generate a PaperToSkill skill, and compare it against two context
baselines: a generic summary and an abstract-only context. For transfer
ablation, we compare the full skill against the same skill with `Transfer Notes`
removed and against the generic summary.

The metrics are deterministic:

- skill rubric score, checking required sections, source anchors, workflow
  coverage, failure coverage, and compactness;
- context coverage, checking whether a context preserves task-relevant
  operational elements for a downstream planning task;
- source-span validation, checking whether line-anchored claims point to valid
  supporting spans;
- offline transfer-readiness, checking whether a context contains harness
  adaptation, source/inference separation, validation, and failure-recording
  signals;
- word count under a 1200-word compactness budget;
- deterministic input-token and cost proxy, estimated as `ceil(characters / 4)`
  and reported with a configurable price per million input-token proxy.

These metrics are reproducible gates. They do not replace live agent execution
or completed human fidelity annotation. To support later human review, we also
prepare a six-criterion fidelity protocol and paper-specific review packets, but
those packets remain unscored until independent annotators fill them. The
annotation summarizer currently reports 24 pending rows and no completed
scores.

We also prepare model-ablation prompt packets, a runner, and a response
evaluator for Claude Opus 4.8, a GPT-family slot requested as GPT 5.5, and a
DeepSeek follow-up slot. The current live attempt records provider/model
availability rather than model quality: the endpoint lists `claude-opus-4-8`,
but Claude prompt calls returned HTTP 503 because no provider accounts were
available, and no GPT-family alias was listed.

## 5. Results

Table 1 in `results/tables/main_results.md` summarizes the current benchmark.
All four generated skills score 20/20 on the deterministic skill rubrics. On
context coverage, the generated skills score 7.867/9 for AI Scientist-v2,
8.267/9 for Reflexion, 9.1/10 for AIDE, and 8.9/10 for Toolformer. The
generic-summary baselines score 1.733/9, 3.483/9, 1.916/10, and 2.5/10
respectively; abstract-only baselines score 1.2/9, 2.533/9, 1.333/10, and
1.534/10.

The generated skills remain compact: 782 words for AI Scientist-v2, 479 words
for Reflexion, 927 words for AIDE, and 943 words for Toolformer, all under the
1200-word budget. Source validation finds support rates of 0.938, 1.0, 1.0,
and 1.0 with zero invalid line ranges. The one weak AI Scientist-v2 span is
recorded as a boundary case rather than treated as fully verified.

The context cost proxy shows the same compactness pattern relative to full paper
contexts. Generated skills use 1,366 estimated input tokens for AI Scientist-v2
compared with 62,041 for the full extracted paper, 823 versus 18,559 for
Reflexion, 1,517 versus 15,894 for AIDE, and 1,526 versus 24,097 for
Toolformer. This corresponds to token-proxy reductions of 97.8%, 95.57%,
90.46%, and 93.67% relative to full extracted paper text. The summary and
abstract baselines are smaller, but their deterministic coverage scores are
much lower. We therefore interpret PaperToSkill's economic signal as a
coverage-preserving compression relative to full-paper context, not as a claim
that skills are the shortest possible context.

Transfer-note ablations show a consistent offline readiness pattern. Full skills
score 10/10 on the readiness metric across all four papers. Removing
`Transfer Notes` lowers readiness to 7.6/10 in all four cases, while generic
summaries score between 1.2/10 and 2.25/10. This supports the narrower claim
that transfer notes encode artifact-readiness signals. It does not yet prove
improved live cross-harness success.

The failure-case archive records 27 cases: 21 paper-reported limitations or
failure branches from the four source maps and 6 project-level failure/fix
records from the PaperToSkill development process. This archive supports the
claim that failed branches are preserved as inspectable provenance. It is not
evidence that failure recording improves live task outcomes.

The reproducibility package checker reports 128 ready checks, 7 pending
external-evidence checks, and 0 failed checks. The pending checks correspond to
the four live transfer response sets, human-fidelity annotation status,
model-ablation response files, and completed model-ablation evaluation. This
supports a local artifact-readiness claim, not a claim of completed live, model,
or human evaluation.

The model-ablation runner/evaluator is executable, but the current evidence is
blocked rather than scored. The latest run report records two Claude errors
with `claude-opus-4-8`, two skipped GPT-family rows because no GPT aliases were
available, zero saved response files, and six pending evaluation rows across
Claude, GPT-family, and DeepSeek slots. These rows should not be interpreted as
negative quality evidence for any model.

Phases 19-20 evaluate the automatic note scaffold separately on Toolformer and
AIDE. The Toolformer auto-note-derived skill scores 20/20 on the deterministic
rubric, 9.3/10 on context coverage, 10/10 on offline transfer readiness, and
1.0 source-span support with zero invalid ranges. The AIDE auto-note-derived
skill scores 20/20, 8.467/10 on context coverage, 9.5/10 on offline transfer
readiness, and 1.0 source-span support with zero invalid ranges. These skills
are 1,179 and 998 words respectively, both under the 1,200-word compactness
budget. The result supports the narrower claim that extracted text can seed
auditable note scaffolds; it does not establish robust arbitrary-PDF
automation.

## 6. Discussion

The main result is not that PaperToSkill "understands" papers in the broadest
sense. The result is that a structured paper-note-to-skill pipeline can preserve
operational knowledge that summaries discard. The skills include workflow
steps, validation checks, failure cases, and source anchors, which are exactly
the parts needed when a user wants an agent to apply a paper rather than merely
explain it.

The benchmark also reveals useful failure modes. During the AIDE case, the
initial extractor capped workflow, validation, and failure candidates too
aggressively, which dropped data-preview and LLM-cost content. Earlier phases
also exposed title parsing, source-audit mapping, and source-span line-counting
bugs. These records are the type of failure branches PaperToSkill should
preserve: not just final successes, but the ways extraction, evaluation, or
external dependencies can lose important operational content.

The auto-note scaffold adds another failure mode: raw `pdftotext` output can mix
two-column paper text, figures, and references into one line. The final scaffold
therefore keeps source anchors auditable and treats automatic snippets as draft
evidence that must be reviewed before live use.

## 7. Limitations

The current work has several important limits. First, the main benchmark
converts curated notes rather than arbitrary PDFs; automatic note scaffolds have
only been retained on Toolformer and AIDE extracted text. Second, the metrics are
deterministic and partly lexical, so they can over-credit exact matches or
under-credit valid paraphrases. Third, live cross-harness execution has not
completed because the provided remote endpoint returned service errors during
chat-completion tests. Fourth, model ablations were attempted but not completed
because Claude account capacity was unavailable and the endpoint did not list a
GPT-family model. Fifth, human-fidelity packets, a blank annotation template,
and a summary script are prepared, but no independent annotations have been
completed. Sixth, compactness is measured by word count and deterministic
input-token proxy, not by tokenizer-exact model price, provider billing, or live
success per dollar. Seventh, the failure-case archive is an evidence and
provenance artifact rather than a controlled outcome study. Eighth, the
reproducibility package is locally ready but still has pending external evidence
for live responses, model responses, and human annotations.

These limits shape the correct claim: PaperToSkill currently provides
reproducible evidence for compact, source-grounded skill artifacts and offline
coverage/readiness improvements. It does not yet establish live deployment
success.

## 8. Conclusion

PaperToSkill turns paper-derived procedural knowledge into portable,
human-editable skills. In a four-paper benchmark, generated skills are compact,
source-grounded, structurally valid, and more operationally complete than short
summary baselines under deterministic evaluation. The next stage is to re-run
the prepared live prompt packets when provider capacity and GPT-family aliases
are available, add the user's DeepSeek slot, run human fidelity review, compute
token and price costs, and test papers whose contributions are less naturally
procedural.

## Reproducibility Pointers

- Extraction: `scripts/papertoskill_extract.py`
- Skill evaluation: `scripts/evaluate_skill.py`
- Context baselines: `scripts/evaluate_context_baselines.py`
- Transfer readiness: `scripts/evaluate_harness_transfer.py`
- Source-span validation: `scripts/validate_source_spans.py`
- Table aggregation: `scripts/aggregate_results_tables.py`
- Context cost proxy: `scripts/evaluate_context_costs.py`
- Human-fidelity packets: `scripts/build_human_fidelity_packets.py`
- Human-fidelity annotation summary:
  `scripts/summarize_human_fidelity_annotations.py`
- Failure-case archive: `scripts/build_failure_case_archive.py`
- Reproducibility package check:
  `scripts/check_reproducibility_package.py`
- Model-ablation runner and evaluator:
  `scripts/run_model_ablation_prompts.py`;
  `scripts/evaluate_model_ablation_responses.py`
- Review report and rebuttal bank: `research/review_report.md`;
  `research/rebuttal_bank.md`
- Result tables: `results/tables/`
- Live prompt packets: `results/live_transfer_prompts/`
