---
name: toolformer-auto-paper-skill
description: Use when applying the paper-derived method from Toolformer Language Models Can Teach Themselves to Use Tools as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# Toolformer: Language Models Can Teach Themselves to Use Tools

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/auto_notes/toolformer_auto_note.md`

## Paper Snapshot

... or fac- tual lookup, where much simpler and smaller models excel. In this paper, we
show that LMs can teach themselves to use external tools via simple APIs and achieve the
best of both worlds. We introduce Toolformer, a model trained to decide which APIs to
call, when to call them, what ... Source anchors: lines 10-46.

## Central Contribution

In this paper, we show that LMs can teach themselves to use external tools via simple
APIs and achieve the best of both worlds.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Represent the text-to-text API-call contract with tool name, input, result, and delimiter: ... to use different tools by means of API calls. We require that inputs and outputs for each API can be represented as text sequences. This allows seamless insertion of API calls into any given text .... Source anchors: lines 86-90.
2. Use few demonstrations or prompts to propose candidate actions: ... answering tool: Given an input text x, we first sample a position i and corresponding API call candidates c1i , c2i , . . . , cki . We then execute these API calls and filter out all calls which do not .... Source anchors: lines 74-78.
3. Execute proposed calls or actions with the required backend: ... ability of M to sample a large number of potential API calls. We then execute these API calls and finally check whether the ob- tained responses are helpful for predicting .... Source anchors: lines 108-112.
4. Filter candidates by future-token loss or another source-defined utility threshold: ... this call makes it easier for the model to predict future tokens, compared to not receiving the API call at all, or receiving only its input. Given a filtering threshold f , we .... Source anchors: lines 159-163.
5. Interleave retained calls to build the augmented dataset while preserving the original text: ... results in the new dataset C augmented with API calls. We use this new dataset to finetune M , using a standard language modeling objective. Crucially, apart from inserted API calls the augmented dataset C .... Source anchors: lines 188-192.
6. Fine-tune or train on retained source-backed examples: ... huge language modeling dataset with potential API calls. We then use a self-supervised loss to determine which of these API calls actually help the model in predicting future tokens. Finally, we finetune the .... Source anchors: lines 100-104.
7. At inference time, interrupt generation, insert the response, and continue: Inference When generating text with M after finetuning with our approach, we perform regular decoding until M produces the token, indicat- ing that it next expects the response for an API call. At this point .... Source anchors: lines 201-205.
8. Record the tool set, constraints, and required demonstrations: ... use. Concretely, we explore the fol- lowing five tools: a question answering system, a Wikipedia search engine, a calculator, a calendar, and a machine translation system. Some .... Source anchors: lines 216-220.

## Validation

- Evaluate whether the system works without further supervision in zero-shot settings: ... Toolformer achieves substan- tially improved zero-shot performance across a variety of downstream tasks, often competi- tive with much larger models, without .... Source anchors: lines 40-44.
- Compare against same-size and larger baselines: ... these baseline models, improving upon the best baseline by 11.7, 5.2 and 18.6 points, respec- tively. It also clearly outperforms OPT (66B) and GPT-3 (175B), despite both models being much larger. This .... Source anchors: lines 338-342.
- Track benchmark domains such as LAMA, mathematical reasoning, question answering, and temporal datasets: multilingual aspect of the task. 4.2.5 Temporal Datasets To investigate the calendar APIs utility, we eval- uate all models on T EMP LAMA (Dhingra et al.,. Source anchors: lines 398-402.
- Check whether the added mechanism preserves core language-modeling quality: ... on CCNet leads to We do not evaluate the perplexity of Toolformer with. Source anchors: lines 463-467.
- Run scale or sensitivity analysis when the paper reports model-size effects: ... model (Wang and Komat- suzaki, 2021) with 6.7B parameters, achieves much the existing LMs vocabulary. For reasons of readability, we stronger zero-shot results, clearly outperforming a much larger GPT-3 .... Source anchors: lines 118-122.

## Failure Cases

- Avoid claiming that the method removes the need for large human annotations or task-specific setup: ... However, existing ap- proaches either rely on large amounts of human annotations (Komeili et al., 2022; Thoppilan et al., 2022) or limit tool use to task-specific settings .... Source anchors: lines 50-54.
- Check whether external backend execution is required before transfer: Executing API Calls As a next step, we execute all API calls generated by M to obtain the corre- on the API itself for example, it can involve call- ing another neural network, executing a Python. Source anchors: lines 123-127.
- Treat heuristics and sample efficiency as explicit costs: ... 2021) as our language model M . To reduce the computational cost of annotating C with API calls, we define .... Source anchors: lines 229-233.
- Do not overstate question-answering performance when Atlas or search limitations remain: ... However, Toolformer still lags behind the much larger GPT-3 (175B) model. This is likely due to both the simplicity of our search engine (in many cases, it returns results that are clearly not a .... Source anchors: lines 381-385.
- Audit calendar API or temporal gains before attributing all improvement to the tool: ... on T EMP LAMA can not be attributed to the calendar tool, which is only used for 0.2% of all examples, but mostly .... Source anchors: lines 430-434.
- Do not claim perplexity with live tool calls when the paper says it is not evaluated: ... do not evaluate the perplexity of Toolformer with slightly improved performance on a different CC- x1 , . . . , xt1 ) of token xt given x1 , . . . , xt1 would require Net subset, but it slightly .... Source anchors: lines 467-471.
- Treat model scale or model size as a condition for the method to emerge: ... API calls are not helpful to the smallest models, larger models learn how to make good use of them. Even for bigger models, the gap between model predictions with and without API calls remains .... Source anchors: lines 494-498.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
