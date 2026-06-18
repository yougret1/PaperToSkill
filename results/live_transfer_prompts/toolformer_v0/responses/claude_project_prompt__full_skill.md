# Toolformer-Style Tool-Use Experiment Plan

## Context Sufficiency Assessment

**Yes, the context is sufficient** for planning a local Toolformer-style experiment. The skill document provides:
- Clear representation scheme (text-based API calls)
- Candidate generation and filtering procedure (loss-based)
- Augmented dataset construction steps
- Fine-tuning and inference-time execution flow
- Five concrete tool examples
- Validation domains and known limitations

## Required Local Tools or Simulated APIs

### Core Infrastructure
- **Language model** (GPT-2 or GPT-J scale, ~6B params recommended based on paper's use of GPT-J)
- **Fine-tuning pipeline** (PyTorch/Transformers or JAX/T5X)
- **Loss computation** for filtering candidates (cross-entropy on future tokens)

### Tool APIs (text-to-text)
1. **Calculator**: Python `eval()` or `sympy` for arithmetic expressions
2. **Wikipedia Search**: Wikipedia API wrapper or local Wikipedia dump with search
3. **Question Answering**: Smaller QA model (T5-base fine-tuned on SQuAD) or mock responses
4. **Machine Translation**: MarianMT models or Google Translate API
5. **Calendar**: Python `datetime` library for date queries

### Dataset
- **CCNet or C4 subset** (English web text, as paper used CCNet)
- Target size: ~10k-100k documents for feasibility

---

## Step-by-Step Run Plan

### **Source-Backed Steps**

#### 1. Define API Call Representation
- Format: `[API_NAME(input) → result]`
- Example: `[Calculator(15 * 7) → 105]`
- Special tokens: `<API>`, `</API>`, `<RESULT>`, `</RESULT>`
- Source: Workflow step 1, lines 86-104

#### 2. Write Few-Shot Prompts per API
- Create 3-5 demonstrations for each of the 5 tools
- Format: text with inserted API annotations
- Example for Calculator:
  ```
  The distance is 45 miles at 60 mph, so it takes [Calculator(45/60) → 0.75] hours.
  ```
- Source: Workflow step 3, lines 123-152

#### 3. Sample Candidate API Calls
- For each position in each document:
  - Construct prompt with text up to that position
  - Sample 5-10 continuations that include API calls
  - Parse out API name and arguments
- Heuristic: Only sample at sentence boundaries to reduce cost
- Source: Workflow step 2, lines 105-115; step 3, lines 157-165

#### 4. Execute Candidate Calls
- Route each `(API_NAME, input)` to actual backend
- Collect single text response
- Handle errors as empty responses
- Source: Workflow step 4, lines 123-132

#### 5. Filter by Loss Reduction
- For each candidate call at position *i*:
  - Compute loss *L_∅* on tokens *i+1* to *i+k* (no API call)
  - Compute loss *L_c* with API call but no result
  - Compute loss *L_c→r* with API call and result
  - Keep call if: `weighted_loss(L_c→r) < min(L_∅, L_c) - threshold`
  - Suggested threshold: 0.1 (tune empirically)
  - Suggested *k*: 10 future tokens
- Source: Workflow step 5, lines 134-171

#### 6. Construct Augmented Dataset
- Insert retained API calls and results into original text
- Maintain original text otherwise unchanged
- Save as new training corpus
- Source: Workflow step 2, lines 105-115; step 6, lines 172-204

#### 7. Fine-Tune Model
- Initialize from base GPT-J checkpoint
- Train on augmented dataset for 1-3 epochs
- Standard causal LM objective
- Source: Workflow step 6, lines 172-204

#### 8. Inference with Tool Execution
- Decode until model emits `<API>` token
- Parse API name and arguments
- Execute tool synchronously
- Insert `<RESULT>result</RESULT>` into generated sequence
- Continue decoding
- Source: Workflow step 7, lines 204-208

---

### **Inferred Adaptations**

#### A. Model Selection
- Use GPT-2 Medium (355M) or GPT-J 6B if resources allow
- Fallback: GPT-2 Small (117M) for faster iteration, accepting that tool use emerges with scale (lines 433-496)

#### B. Dataset Sampling Strategy
- Limit candidate call sampling to 1 position per 50 tokens to control compute
- Use parallel execution for API calls

#### C. Loss Computation Window
- Set *k* = 10 future tokens for filtering (paper does not specify exact *k*)
- Weight future tokens equally (uniform weighting)

#### D. Validation Splits
- Hold out 5% of augmented dataset for validation
- Track perplexity on validation set **without API calls** (lines 467-470 note marginalizing over calls is infeasible)

#### E. Tool Backend Choices
- **Calculator**: Use Python `ast.literal_eval` for safety instead of `eval`
- **Wikipedia**: Use `wikipedia-api` Python library
- **QA**: Use `distilbert-base-cased-distilled-squad` from Hugging Face
- **Translation**: Use `Helsinki-NLP/opus-mt-en-de` for English↔German
- **Calendar**: Use Python `datetime.datetime.now()` and arithmetic

---

## Validation Checks and Stop Conditions

### During Candidate Generation
- **Check**: At least 10% of sampled continuations contain valid API calls
- **Stop if**: <1% contain valid calls → prompt demonstrations are insufficient

### During Filtering
- **Check**: At least 5% of executed calls pass the loss-reduction threshold
- **Stop if**: <1% pass → threshold too strict or tools not useful for dataset

### During Fine-Tuning
- **Check**: Training loss decreases and validation perplexity (no API calls) does not degrade >5% vs. baseline fine-tuned on original corpus
- **Stop if**: Validation perplexity degrades >10% → overfitting to API call format

### During Inference
- **Check**: Model uses each tool at least once per 100 test examples in relevant domains
- **Validation domains** (source: lines 302-450):
  - LAMA fact completion (QA tool, Wikipedia)
  - ASDiv, SVAMP, MAWPS math reasoning (Calculator)
  - TempLAMA, TempReason temporal reasoning (Calendar)
  - MLQA cross-lingual QA (Translation)

### Known Limitations to Monitor
- **Tool emergence with scale**: Expect minimal tool use if model <1B params
- **Wikipedia search**: Cannot reformulate queries or browse multiple results (lines 374-388)
- **Temporal improvements**: Some may come from pretraining, not just calendar API (lines 429-450)

---

## Likely Failed Branch

### Branch: Direct Prompting Without Fine-Tuning
**Hypothesis**: Few-shot prompting alone (without fine-tuning on augmented data) will enable tool use.

**Steps**:
1. Use base GPT-J with few-shot prompt containing API call demonstrations
2. Decode and attempt to parse API calls from raw generations
3. Execute parsed calls and insert results

**Expected Failure**:
- Model will generate API-like text but not in consistent parsable format
- API calls will appear in irrelevant contexts (no loss-based filtering)
- No learning signal from tool results

**Root Cause**: The paper's key insight is that **fine-tuning on filtered, executed API calls** teaches the model when and how to use tools. Zero-shot or few-shot prompting lacks the reinforcement from actual tool results during training (lines 48-63, 105-115).

**Diagnostic**: Compare tool-use frequency and accuracy between prompted baseline and fine-tuned model. Expect fine-tuned model to use tools 5-10× more often and with higher precision.

---

## Summary

This plan preserves the paper's core loop: **represent → sample → execute → filter → augment → fine-tune → infer**. It is executable locally with open models and standard APIs. The separation of source-backed steps (1-8) from inferred adaptations (A-E) allows auditing against the original paper. The failed branch documents a common misconception that prompting alone suffices, which the paper explicitly addresses through its self-supervised fine-tuning approach.
