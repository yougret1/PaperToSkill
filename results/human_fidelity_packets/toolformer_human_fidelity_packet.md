# Human Fidelity Review Packet: Toolformer

Evidence boundary: this packet is an input for human review. It is not a completed annotation.

## Review Instructions

- Review the generated skill against the curated source note and extracted paper text.
- Use source anchors where available, but judge semantic fidelity rather than lexical overlap alone.
- Record one score per criterion and cite the source span or skill section that justifies the score.
- Mark unsupported or inferred transfer guidance explicitly instead of folding it into source-backed fidelity.

## Score Scale

- 0: Missing or contradicts the paper.
- 1: Present but vague, materially incomplete, or weakly grounded.
- 2: Mostly faithful with minor omissions or wording issues.
- 3: Faithful, operationally useful, and source-supported.

## Artifact Summary

- Generated skill: `generated_skills/toolformer/SKILL.md`
- Curated source note: `papers/notes/toolformer_note.md`
- Extracted paper text: `papers/extracted/toolformer.txt`
- Source map: `generated_skills/toolformer/references/source_map.json`
- Source-span report: `results/evaluations/toolformer_source_span_validation_v0.json`
- Deterministic skill coverage: 8.9/10
- Source-span support rate: 1.0
- Invalid source-span ranges: 0
- Source-map entries: 22
- Skill words: 943
- Source note words: 894

## Criteria

| Criterion | Question | Score | Evidence note |
| --- | --- | --- | --- |
| Central contribution fidelity | Does the skill preserve the paper's central contribution without overclaiming? |  |  |
| Operational workflow fidelity | Does the skill preserve the executable workflow, roles, stages, or search policy needed to reuse the method? |  |  |
| Validation and evidence fidelity | Does the skill preserve the paper's validation protocol, evaluation domains, and reported evidence without distorting them? |  |  |
| Failure and limitation fidelity | Does the skill preserve important limitations, failure modes, and stop conditions? |  |  |
| Source grounding | Are source-backed instructions traceable to the cited note or extracted-paper spans? |  |  |
| Transfer boundary discipline | Does the skill separate paper-backed content from inferred transfer guidance and harness-specific adaptation? |  |  |

## Generated Skill

```markdown
---
name: toolformer-paper-skill
description: Use when applying the paper-derived method from Toolformer Language Models Can Teach Themselves to Use Tools as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# Toolformer: Language Models Can Teach Themselves to Use Tools

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/notes/toolformer_note.md`

## Paper Snapshot

Toolformer trains a language model to decide which APIs to call, when to call them, what
arguments to pass, and how to incorporate tool results into future token prediction. It
uses a self-supervised procedure requiring only a handful of demonstrations for each API
and evaluates tools including question answering, calculator, Wikipedia search, machine
translation, and calendar APIs. Source anchors: extracted text lines 22-45.

## Central Contribution

Toolformer trains a language model to decide which APIs to call, when to call them, what
arguments to pass, and how to incorporate tool results into future token prediction.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Represent every API call as text with a tool name, input, and optional result so calls can be inserted into normal language-model sequences without a new interface. Source anchors: lines 86-104.
2. Convert a plain LM dataset into an augmented dataset by using the model to sample potential API calls, executing them, filtering for calls that reduce future-token loss, and interleaving the retained calls with the original text. Source anchors: lines 105-115, 155-173.
3. For each API, write a small prompt with a few demonstrations that encourages the model to annotate text with candidate API calls. Source anchors: lines 123-152, 157-165.
4. Execute each proposed API call using the actual backend for that tool, such as a neural model, Python script, or retrieval system, and require a single text response. Source anchors: lines 123-132.
5. Keep an API call only when providing both the call and result reduces the weighted loss on future tokens by at least a filtering threshold compared with no call or a call without a result. Source anchors: lines 134-171.
6. Fine-tune the language model on the augmented dataset while keeping the original text content unchanged apart from inserted API calls and results. Source anchors: lines 172-204.
7. At inference time, decode normally until the model emits the API-call token, interrupt decoding, execute the selected API, insert the response and closing token, and continue generation. Source anchors: lines 204-208.
8. Treat tools as text-to-text APIs with only two requirements: inputs and outputs can be represented as text, and a few demonstrations of intended use are available. Source anchors: lines 211-221.

## Validation

- The paper investigates whether a model can learn to call tools without further supervision and decide when and how to call available tools in zero-shot settings. Source anchors: lines 211-221, 274-284.
- Toolformer uses five tools: question answering, calculator, Wikipedia search, machine translation, and calendar. Source anchors: lines 211-221, 232-249.
- The authors report that Toolformer with API calls improves over GPT-J and its disabled-tool variant on LAMA subsets, and is competitive with GPT-3 on the tabled results. Source anchors: lines 302-311, 335-340.
- Toolformer more than doubles performance on mathematical reasoning tasks when API calls are enabled and often uses the calculator tool. Source anchors: lines 316-340.
- On question-answering datasets, Toolformer improves over same-size baselines but still lags behind Atlas, and the authors note limitations of interacting with the Wikipedia search API. Source anchors: lines 362-388.
- On temporal datasets, Toolformer outperforms baselines and uses the calendar API heavily, but some improvement is not fully attributable to the calendar tool. Source anchors: lines 417-450.
- The authors check that fine-tuning on API-augmented data does not degrade core language modeling compared with fine-tuning on the same corpus without API calls when API calls are disabled. Source anchors: lines 453-470.

## Failure Cases

- Existing tool-use approaches often rely on large human annotations or task-specific settings; Toolformer targets broader self-supervised tool use but still depends on a few demonstrations for each API. Source anchors: lines 48-63, 98-104.
- Toolformer only supports tools whose inputs and outputs can be represented as text sequences, and tool execution depends on the external backend. Source anchors: lines 86-104, 123-132, 211-221.
- The paper uses heuristics to reduce computational cost when annotating the corpus with API calls. Source anchors: lines 232-237.
- For question answering, Toolformer still lags behind Atlas and is limited by simple interaction with the Wikipedia search API; it cannot reformulate queries or browse multiple top results in the reported setup. Source anchors: lines 374-388.
- Some temporal improvements cannot be fully attributed to the calendar API, because other effects also contribute. Source anchors: lines 429-450.
- The authors do not evaluate perplexity with API calls enabled because computing token probabilities would require marginalizing over possible API calls. Source anchors: lines 467-470.
- Tool use emerges with model scale; smaller models benefit less from the provided APIs. Source anchors: lines 433-496.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
```

## Curated Source Note Excerpt

```markdown
# Toolformer: Language Models Can Teach Themselves to Use Tools

## Source

- Paper ID: `toolformer`
- arXiv: `https://arxiv.org/abs/2302.04761`
- PDF: `papers/raw/toolformer.pdf`
- Extracted text: `papers/extracted/toolformer.txt`
- Render check: `output/pdf/toolformer/page-01.png`
- Extraction notes: PDF has 17 pages. `pdftotext -layout` produced
  `papers/extracted/toolformer.txt`. Page 1 was visually rendered and inspected.

## Abstract

Toolformer trains a language model to decide which APIs to call, when to call
them, what arguments to pass, and how to incorporate tool results into future
token prediction. It uses a self-supervised procedure requiring only a handful
of demonstrations for each API and evaluates tools including question answering,
calculator, Wikipedia search, machine translation, and calendar APIs.

Source anchors: extracted text lines 22-45.

## Methods

1. Represent every API call as text with a tool name, input, and optional result
   so calls can be inserted into normal language-model sequences without a new
   interface. Source anchors: lines 86-104.
2. Convert a plain LM dataset into an augmented dataset by using the model to
   sample potential API calls, executing them, filtering for calls that reduce
   future-token loss, and interleaving the retained calls with the original
   text. Source anchors: lines 105-115, 155-173.
3. For each API, write a small prompt with a few demonstrations that encourages
   the model to annotate text with candidate API calls. Source anchors: lines
   123-152, 157-165.
4. Execute each proposed API call using the actual backend for that tool, such
   as a neural model, Python script, or retrieval system, and require a single
   text response. Source anchors: lines 123-132.
5. Keep an API call only when providing both the call and result reduces the
   weighted loss on future tokens by at least a filtering threshold compared
   with no call or a call without a result. Source anchors: lines 134-171.
6. Fine-tune the language model on the augmented dataset while keeping the
   original text content unchanged apart from inserted API calls and results.
   Source anchors: lines 172-204.
7. At inference time, decode normally until the model emits the API-call token,
   interrupt decoding, execute the selected API, insert the response and closing
   token, and continue generation. Source anchors: lines 204-208.
8. Treat tools as text-to-text APIs with only two requirements: inputs and
   outputs can be represented as text, and a few demonstrations of intended use
   are available. Source anchors: lines 211-221.

## Experiments

- The paper investigates whether a model can learn to call tools without
  further supervision and decide when and how to call available tools in
  zero-shot settings. Source anchors: lines 211-221, 274-284.
- Toolformer uses five tools: question answering, calculator, Wikipedia search,
  machine translation, and calendar. Source anchors: lines 211-221, 232-249.
- The authors report that Toolformer with API calls improves over GPT-J and its
  disabled-tool variant on LAMA subsets, and is competitive with GPT-3 on the
  tabled results. Source anchors: lines 302-311, 335-340.
- Toolformer more than doubles performance on mathematical reasoning tasks when
  API calls are enabled and often uses the calculator tool. Source anchors:
  lines 316-340.
- On question-answering datasets, Toolformer improves over same-size baselines
  but still lags behind Atlas, and the authors note limitations of interacting
  with the Wikipedia search API. Source anchors: lines 362-388.
- On temporal datasets, Toolformer outperforms baselines and uses the calendar
  API heavily, but some improvement is not fully attributable to the calendar
  tool. Source anchors: lines 417-450.
- The authors check that fine-tuning on API-augmented data does not degrade core
  language modeling compared with fine-tuning on the same corpus without API
  calls when API calls are disabled. Source anchors: lines 453-470.

## Limitations

- Existing tool-use approaches often rely on large human annotations or
  task-specific settings; Toolformer targets broader self-supervised tool use
  but still depends on a few demonstrations for each API. Source anchors: lines
  48-63, 98-104.
- Toolformer only supports tools whose inputs and outputs can be represented as
  text sequences, and tool execution depends on the external backend. Source
  anchors: lines 86-104, 123-132, 211-221.
- The paper uses heuristics to reduce computational cost when annotating the
  corpus with API calls. Source anchors: lines 232-237.
- For question answering, Toolformer still lags behind Atlas and is limited by
  simple interaction with the Wikipedia search API; it cannot reformulate
  queries or browse multiple top results in the reported setup. Source anchors:
  lines 374-388.
- Some temporal improvements cannot be fully attributed to the calendar API,
  because other effects also contribute. Source anchors: lines 429-450.
- The authors do not evaluate perplexity with API calls enabled because
  computing token probabilities would require marginalizing over possible API
  calls. Source anchors: lines 467-470.
- Tool use emerges with model scale; smaller models benefit less from the
  provided APIs. Source anchors: lines 433-496.

## Transfer Notes

- A skill derived from Toolformer should preserve the API-call contract:
  text-to-text tools, explicit tool names and inputs, optional results, and
  delimiters or harness-native equivalents.
- The workflow assumes the target harness can safely execute or simulate tool
  calls and can insert returned text back into the model context.
- If a target harness cannot execute tools during generation, use the skill as
  a data-generation or planning protocol and mark live tool-use claims as
  unverified.
```
