Context sufficiency: **sufficient for a usage plan**, but **not sufficient to claim a completed model ablation**. The context provides the Toolformer workflow, validation ideas, and failure cases. It does not provide live provider verification, completed runs, scores, bills, or evidence that `gpt-5.5` is available.

Model metadata for this response:

```yaml
model_slot: gpt_5_5_or_gpt_family
requested_alias: gpt-5.5
actual_model_alias_used: not_verified_in_this_response
provider_path_required: /v1/responses
response_status: planning_only
```

**Required Local Files / Tools**

Required files:

- `generated_skills/toolformer/SKILL.md`
- `papers/notes/toolformer_note.md`
- A target corpus or small text sample for API-call annotation
- Few-shot prompt files per tool, for example:
  - `prompts/toolformer/calculator.md`
  - `prompts/toolformer/qa.md`
  - `prompts/toolformer/wiki_search.md`
  - `prompts/toolformer/calendar.md`
  - `prompts/toolformer/translation.md`
- Output directory for generated artifacts, for example:
  - `runs/toolformer_data_generation/`

Required tools or simulated APIs:

- LM candidate annotator using OpenAI Responses `/v1/responses`
- Provider model-list check before claiming `gpt-5.5`
- Calculator API or deterministic local calculator
- QA API or simulated QA backend
- Wikipedia/search API or local retrieval stub
- Calendar/date API
- Translation API or simulated translation backend
- Scorer that computes future-token loss deltas, or a documented proxy if full LM loss is unavailable

Useful commands, adapted to the local harness:

```bash
# Verify available GPT-family aliases before live run
python scripts/list_openai_models.py --profile gpt_family

# Generate candidate API-call annotations
python scripts/toolformer/generate_candidates.py \
  --model ACTUAL_VERIFIED_GPT_ALIAS \
  --input data/toolformer/sample_corpus.jsonl \
  --prompts prompts/toolformer \
  --output runs/toolformer_data_generation/candidates.jsonl

# Execute proposed API calls
python scripts/toolformer/execute_calls.py \
  --input runs/toolformer_data_generation/candidates.jsonl \
  --tools-config configs/toolformer_tools.yaml \
  --output runs/toolformer_data_generation/executed_calls.jsonl

# Filter calls by loss improvement
python scripts/toolformer/filter_by_loss.py \
  --input runs/toolformer_data_generation/executed_calls.jsonl \
  --threshold FILTER_THRESHOLD \
  --output runs/toolformer_data_generation/filtered_augmented.jsonl

# Validate generated dataset
python scripts/toolformer/validate_augmented_data.py \
  --input runs/toolformer_data_generation/filtered_augmented.jsonl
```

These command names are inferred placeholders unless they already exist in the repo.

**Step-by-Step Usage Plan**

1. Verify the GPT-family model alias.
   - Query the provider model list using the separate GPT-family credential profile.
   - Prefer `gpt-5.5` if present.
   - If unavailable, check `gpt-5.4`.
   - Record the actual alias used in response metadata.
   - Stop if no approved GPT-family candidate is available.

2. Load the Toolformer skill context.
   - Read `generated_skills/toolformer/SKILL.md`.
   - Use `papers/notes/toolformer_note.md` only as audit support, not as evidence of completed execution.

3. Define the target experiment.
   - Input: a plain text corpus or curated sample.
   - Output: an augmented dataset where useful API calls and results are interleaved into the original text.
   - Constraint: original text content should remain unchanged except for inserted API calls and API results.

4. Define API-call text format.
   - Use a consistent textual representation such as:

```text
[API_CALL tool="calculator" input="23 * 47"] [API_RESULT 1081]
```

   - Require every tool to accept text input and return a single text output.

5. Prepare few-shot prompts per tool.
   - Each prompt should demonstrate when to insert a candidate API call.
   - Include examples for calculator, QA, Wikipedia search, translation, and calendar if those tools are available.
   - If fewer tools are available, run the experiment only on supported text-to-text tools and log the reduction in scope.

6. Generate candidate API calls.
   - For each corpus segment, ask the verified GPT-family model to annotate possible API calls.
   - Save raw candidates, including model alias, prompt ID, source document ID, and timestamp.
   - Do not execute calls during this stage unless the harness intentionally combines generation and execution.

7. Execute proposed API calls.
   - Route each candidate to the corresponding backend.
   - Normalize each tool output to a single text response.
   - Log execution errors without dropping the original candidate record.

8. Score and filter candidates.
   - Compare future-token loss under at least these conditions:
     - Original text without API call.
     - Text with API call but without result.
     - Text with API call and result.
   - Retain a call only if the call plus result reduces weighted future-token loss by at least the configured threshold.
   - If exact LM loss is unavailable, stop or explicitly mark the run as using an inferred proxy rather than a Toolformer-faithful filter.

9. Build the augmented dataset.
   - Insert retained API calls and results into the original text.
   - Preserve original text order and content.
   - Emit machine-readable records containing:
     - original text
     - augmented text
     - retained calls
     - rejected calls
     - tool outputs
     - scoring values
     - model alias used
     - prompt file used

10. Validate the generated artifacts.
   - Confirm every retained call has a tool name, input, output, and score.
   - Confirm all inserted calls correspond to executable tool results.
   - Confirm original text was not otherwise rewritten.
   - Confirm filtering threshold was applied consistently.
   - Confirm failed candidates are logged with reason codes.

11. Optional downstream step.
   - Fine-tune or simulate fine-tuning on the augmented dataset.
   - At inference, decode until the model emits an API-call marker, execute the tool, insert the result, and continue generation.
   - This is source-backed as a Toolformer method, but actual fine-tuning is outside the data-generation plan unless explicitly run.

**Source-Backed Instructions**

The following come directly from the provided Toolformer skill:

- Represent API calls as text with tool name, input, and optional result.
- Generate candidate API calls from a plain LM corpus.
- Use a few demonstrations per API to prompt candidate annotations.
- Execute proposed calls against actual tool backends.
- Keep calls only when the call plus result reduces future-token loss beyond a threshold.
- Interleave retained calls and results into the original text.
- Fine-tune on the augmented dataset while keeping original text unchanged apart from inserted calls.
- At inference, interrupt decoding when an API-call token is emitted, execute the tool, insert the response, and continue.
- Restrict tools to text-to-text APIs with a few demonstrations of intended use.

**Inferred Adaptations**

The following are local harness adaptations, not completed evidence from the paper:

- Specific script names under `scripts/toolformer/`.
- JSONL artifact layout.
- Use of `configs/toolformer_tools.yaml`.
- Use of OpenAI Responses `/v1/responses` for the GPT-family slot.
- Provider alias fallback from `gpt-5.5` to `gpt-5.4`.
- Any simulated API backend.
- Any proxy loss scorer if exact future-token loss is unavailable.
- Any directory such as `runs/toolformer_data_generation/`.

**Validation Checks**

Minimum checks before considering the usage plan successful:

- GPT-family alias was verified before live generation.
- Actual model alias used is recorded.
- All prompt files used are versioned or copied into the run directory.
- Every retained API call has:
  - source document ID
  - tool name
  - text input
  - text output
  - score or loss delta
  - filtering decision
- The augmented text preserves the original text except inserted calls/results.
- Retained calls pass the configured loss-improvement threshold.
- Rejected calls remain available for audit.
- Tool execution failures are logged separately from model-generation failures.
- The run output is saved under the expected response or experiment path before scoring.
- The same scorer/rubric is used across model slots.

Stop conditions:

- Stop if `gpt-5.5` and allowed fallback GPT-family aliases are unavailable.
- Stop if credentials for the GPT-family profile are missing.
- Stop if the harness cannot execute or simulate the required tools.
- Stop if no valid future-token loss scorer or approved proxy is available.
- Stop if generated annotations rewrite the source text rather than only inserting API calls.
- Stop if retained calls cannot be traced back to their prompts, model alias, and tool outputs.

**Likely Failed Branch**

Failure branch: `gpt-5.5` is not present in the provider model list.

Expected handling:

```yaml
event: model_alias_unavailable
requested_alias: gpt-5.5
fallback_candidates:
  - gpt-5.4
action:
  - check_fallback_aliases
  - use_verified_fallback_if_available
  - record_actual_model_alias_used
  - mark_requested_alias_as_unavailable
stop_condition: no_allowed_gpt_family_alias_available
```

Failure branch: candidate API calls are generated, but the loss filter keeps none.

Expected handling:

```yaml
event: no_calls_retained
stage: filter_by_loss
possible_causes:
  - threshold_too_high
  - weak few-shot prompts
  - tool outputs not useful for future-token prediction
  - scorer mismatch
action:
  - save rejected candidates
  - save loss deltas
  - log prompt IDs and model alias
  - do not claim successful Toolformer-style augmentation
```

Failure branch: tool backend returns malformed or multi-field output.

Expected handling:

```yaml
event: tool_execution_invalid_output
stage: execute_calls
action:
  - mark candidate as execution_failed
  - preserve raw tool response
  - exclude from retained augmented dataset
  - continue processing unrelated candidates
```

This is an executable planning response only. It does not claim a completed ablation, live GPT-5.5 availability, generated artifacts, scores, or provider costs.
