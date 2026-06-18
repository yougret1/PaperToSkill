# Toolformer Experiment Plan

## Context Sufficiency

**Yes, the context is sufficient** for a Toolformer-style run. The skill provides:
- Clear API-call representation format
- Candidate generation via prompted sampling
- Execution and loss-based filtering procedure
- Augmented dataset construction
- Fine-tuning and inference-time execution workflow
- Validation domains and reported limitations

## Required Local Tools & Simulated APIs

### Tools to Implement or Simulate

1. **Calculator API** – Python `eval()` for arithmetic (primary validation tool)
2. **Wikipedia Search API** – Simulated with local corpus or mock responses
3. **Question Answering API** – Stub returning fixed answers or small QA model
4. **Calendar API** – Python `datetime` for date queries
5. **Machine Translation API** – Mock or lightweight model (e.g., MarianMT)

### Infrastructure

- Base LM: GPT-2 small (124M) or similar for fast iteration
- Dataset: CCNet subset or comparable unlabeled corpus (~1M tokens)
- Compute: Single GPU for fine-tuning
- Loss computation: Cross-entropy on future tokens with/without API calls

---

## Step-by-Step Run Plan

### Phase 1: API Call Representation (Source-Backed)

**Step 1.1** – Define text format for API calls:
```
<API>tool_name(input_text)</API> → result_text </API>
```
Source: lines 86-104.

**Step 1.2** – Write few-shot prompts (3–5 examples per API) demonstrating intended use.  
Source: lines 123-152, 157-165.

---

### Phase 2: Candidate Generation (Source-Backed)

**Step 2.1** – Sample ~50K sequences from base LM using few-shot prompts.  
Source: lines 123-152.

**Step 2.2** – For each sequence, identify positions where model could insert API calls (use heuristic: after question marks, before numeric expressions, etc.).  
Source: lines 232-237 (heuristics to reduce cost).

**Step 2.3** – Generate candidate API calls at identified positions using prompted base LM.

---

### Phase 3: Execution & Filtering (Source-Backed)

**Step 3.1** – Execute each candidate call via actual tool backend (calculator, Wikipedia stub, etc.).  
Source: lines 123-132.

**Step 3.2** – Compute weighted future-token loss in three conditions:
- **L₀**: No API call
- **L₁**: API call only (no result)
- **L₂**: API call + result

Source: lines 134-171.

**Step 3.3** – Keep call+result if:
```
L₀ - L₂ > τ  AND  L₁ - L₂ > τ
```
where τ is filtering threshold (paper uses τ > 0).  
Source: lines 134-171.

**Validation Check**: Measure retention rate. Expect ~5–15% of candidate calls to pass filter.

---

### Phase 4: Augmented Dataset Construction (Source-Backed)

**Step 4.1** – Insert retained API calls and results into original text sequences.  
Source: lines 172-204.

**Step 4.2** – Verify original content remains unchanged except for API insertions.  
Source: lines 172-204.

**Stop Condition**: If <1% of sequences contain API calls after filtering, revisit candidate generation or filtering threshold.

---

### Phase 5: Fine-Tuning (Source-Backed)

**Step 5.1** – Fine-tune base LM on augmented dataset for 3–5 epochs.  
Source: lines 172-204.

**Step 5.2** – Monitor cross-entropy loss on held-out augmented set.

**Validation Check**: Fine-tuned model should predict API call tokens without new supervision.

---

### Phase 6: Inference-Time Execution (Source-Backed)

**Step 6.1** – Decode until model emits `<API>` token.  
Source: lines 204-208.

**Step 6.2** – Parse tool name and input, execute API, insert result + `</API>`, resume generation.  
Source: lines 204-208.

**Validation Check**: Run on held-out math problems (e.g., "What is 17 * 23?"). Expect model to invoke calculator.

---

### Phase 7: Validation Domains (Source-Backed)

**Test 1: Mathematical Reasoning**  
- Dataset: ASDiv or GSM8K subset  
- Expected: >2x improvement with calculator enabled  
- Source: lines 316-340

**Test 2: Question Answering**  
- Dataset: NaturalQuestions or TriviaQA subset  
- Expected: Improvement over base but lag behind retrieval-heavy baselines  
- Source: lines 362-388

**Test 3: Temporal Queries**  
- Dataset: TempLAMA subset  
- Expected: Heavy calendar API use  
- Source: lines 417-450

**Test 4: Core LM Integrity**  
- Measure perplexity on standard LM eval (WikiText) with APIs disabled  
- Expected: No degradation vs. base model  
- Source: lines 453-470

---

## Source-Backed vs. Inferred Adaptations

### Source-Backed Steps
- API call text format (lines 86-104)
- Few-shot prompting for candidate generation (lines 123-152)
- Three-way loss comparison for filtering (lines 134-171)
- Fine-tuning on augmented data (lines 172-204)
- Inference-time API execution (lines 204-208)
- Five validation tools and domains (lines 211-221, 232-249)

### Inferred Adaptations
- Choice of GPT-2 small as base model (paper uses GPT-J)
- Specific retention rate threshold (paper states τ > 0 but does not report exact value)
- Candidate position heuristics (paper mentions heuristics but doesn't detail them)
- Mock Wikipedia/QA APIs (paper uses real backends)

---

## Likely Failed Branch

**Branch: Filtering Threshold Too Strict**

**Scenario**: Set τ = 0.5 (high threshold to ensure only high-confidence calls pass).

**Expected Failure**:
- Retention rate drops to <0.1%
- Augmented dataset has insufficient API examples
- Fine-tuned model rarely emits `<API>` tokens at inference
- Math and QA performance shows no improvement

**Root Cause**: Loss improvements from simple tool calls (e.g., basic arithmetic) may be small but still beneficial. High threshold discards them.

**Recovery**: Lower threshold to τ = 0.01 and re-filter. Source: lines 134-171 suggest positive threshold but do not specify magnitude.

---

## Stop Conditions

1. **Candidate generation**: If base LM cannot produce plausible API calls after 5 prompt iterations, tool demonstrations are insufficient.
2. **Filtering**: If <1% retention after trying τ ∈ {0.01, 0.1, 0.5}, revisit execution correctness or candidate quality.
3. **Fine-tuning**: If training loss does not decrease after 2 epochs, check dataset construction.
4. **Validation**: If calculator-enabled model shows <10% improvement on math tasks, tool-use has not emerged (expected for small models per lines 433-496).

---

## Summary

This plan preserves the paper's self-supervised tool-use workflow: API-call text representation, prompted candidate generation, execution-based filtering via loss comparison, augmented dataset fine-tuning, and inference-time tool execution. All core steps are source-backed. The likely failed branch (overly strict filtering) reflects the paper's acknowledgment of heuristic choices. Validation checks target mathematical reasoning, QA, temporal queries, and LM integrity as reported in the source.
