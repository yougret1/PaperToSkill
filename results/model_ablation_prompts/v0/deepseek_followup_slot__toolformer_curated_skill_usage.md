# PaperToSkill Model-Ablation Prompt

## Model Slot

- Model ID: `deepseek_followup_slot`
- Requested or advertised alias: `deepseek-to-be-filled`
- Provider status: placeholder_for_user_followup
- Response status: pending

## Model-Specific Notes

- This slot is intentionally present for the user's later DeepSeek addition.
- Replace model_alias, auth_env, and base_url_env with the concrete DeepSeek endpoint before running.
- Keep the same prompt grid and scoring protocol to make results comparable.

## Context Case

- Case ID: `toolformer_curated_skill_usage`
- Paper: Toolformer
- Context path: `generated_skills/toolformer/SKILL.md`
- Usage focus: Use a curated-note-derived Toolformer skill to plan a tool-use data-generation experiment.

## Task

Use the provided PaperToSkill context to produce a concise but executable usage plan. The plan should show whether the skill is sufficient, how the target harness should use it, what artifacts or commands are needed, which checks validate success, which steps are source-backed versus inferred adaptations, and at least one likely failure branch.

## Required Output Contract

- State whether the context is sufficient for the requested usage task.
- List required local files, commands, tools, or simulated APIs.
- Give a step-by-step usage or run plan.
- Separate source-backed instructions from inferred adaptations.
- Identify validation checks and stop conditions.
- Record at least one likely failed branch and how it should be logged.
- Do not invent completed live results, human scores, provider bills, or unavailable model aliases.

## Evaluation Notes

- Use these prompts for later live model responses only.
- A response is not a completed ablation until it is saved under the expected response path and scored by the same rubric across model slots.
- The GPT 5.5 alias must be verified against the provider model list before a live run is claimed.
- The DeepSeek slot is included so the user can add it by following the same process after Claude and GPT-family runs.

## Context

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
