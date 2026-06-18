# Toolformer-Style Tool-Use Experiment Plan

## Context Sufficiency Assessment

**Sufficient for a local Toolformer-style run:** Yes, with adaptations.

The context provides the complete workflow: API-call representation, candidate generation via prompted LM, execution, loss-based filtering, augmented dataset construction, fine-tuning, and inference-time execution. The paper's validation domains and limitations are documented.

**Gaps requiring adaptation:**
- No specific model checkpoint or size recommendation beyond "GPT-J scale"
- No exact filtering threshold value (paper uses weighted loss reduction; we'll need to tune)
- No corpus specification (paper uses CCNet; we'll use a smaller public corpus)
- API backend implementations are harness-specific

---

## Required Local Tools & Simulated APIs

### Core Infrastructure
- **Language model:** GPT-2 or GPT-Neo (1.3B+) for candidate generation and fine-tuning
- **Training framework:** PyTorch + Hugging Face Transformers
- **Compute:** GPU with ≥16GB VRAM for fine-tuning

### Simulated Tool APIs (text-in, text-out)
1. **Calculator:** Python `eval()` wrapper for arithmetic expressions
2. **Wikipedia Search:** Sentence-level retrieval using `wikipedia-api` library (top-1 snippet)
3. **Calendar:** Return current date/day-of-week from system clock
4. **QA System:** Lightweight extractive QA model (e.g., DistilBERT SQuAD)
5. **Translation:** `transformers` Helsinki-NLP model for EN↔DE

### Validation Tools
- Perplexity measurement with API calls disabled
- LAMA-style fact probes (subset)
- Arithmetic reasoning samples (GSM8K-style, small subset)
- Temporal question samples

---

## Step-by-Step Run Plan

### Phase 1: API Call Representation (Source-Backed)
**Source anchor:** Lines 86-104

1. Define text templates:
   ```
   <API>tool_name(input_text) → result_text</API>
   ```
2. Tokenize special tokens: `<API>`, `</API>`, `→`
3. Verify model can encode/decode these markers without vocabulary expansion

**Validation gate:** Model reconstructs annotated examples with ≤1% token error rate.

---

### Phase 2: Candidate Generation Prompts (Source-Backed)
**Source anchor:** Lines 123-152, 157-165

4. Write 3-5 demonstrations per API:
   - Calculator: "The result of 45 * 17 is <API>Calculator(45 * 17) → 765</API>."
   - Wikipedia: "Paris is the capital of <API>WikiSearch(France capital) → Paris</API> France."
   - Calendar: "Today is <API>Calendar() → 2024-01-15, Wednesday</API>."

5. Construct sampling prompts:
   ```
   Your task is to decide which API calls, if any, to make, and to replace "..." by the actual API calls.
   
   [demonstrations]
   
   Input: {sentence_from_corpus}
   Output:
   ```

6. Sample K=5 candidate annotations per position per sentence using nucleus sampling (p=0.95, T=1.0)

**Validation gate:** At least 2 candidate calls generated per 100 corpus sentences.

---

### Phase 3: API Execution (Source-Backed)
**Source anchor:** Lines 123-132

7. Parse each candidate call to extract `(tool_name, input_text)`
8. Route to corresponding backend:
   ```python
   def execute_api(tool, input_text):
       if tool == "Calculator":
           return str(eval(input_text))  # sandboxed
       elif tool == "WikiSearch":
           return wikipedia.summary(input_text, sentences=1)
       # ... etc
   ```
9. Catch execution failures (malformed input, API timeout) and discard those candidates

**Validation gate:** ≥80% of well-formed calls return non-empty text responses.

---

### Phase 4: Loss-Based Filtering (Source-Backed)
**Source anchor:** Lines 134-171

10. For each candidate call at position i in sequence x:
    - Compute L₁: cross-entropy loss on tokens [i+1:i+1+k] given x[:i] (no call)
    - Compute L₂: loss on tokens [i+1:i+1+k] given x[:i] + `<API>call`  (call without result)
    - Compute L₃: loss on tokens [i+1:i+1+k] given x[:i] + `<API>call → result</API>` (call with result)
    
11. Keep call if:
    ```
    min(L₁, L₂) - L₃ ≥ τ
    ```
    where τ is the filtering threshold (start with τ=0.1, tune based on retention rate)

12. Weight future tokens exponentially: w_j = 1.5^(-j) for j=0..k-1, k=5

**Validation gate:** Retention rate between 5-20% (too low = no learning signal; too high = noise).

**Known failure branch:** If τ is too high, no calls pass filtering and the augmented dataset equals the original. If τ=0, all calls pass and many will be spurious. Requires empirical tuning.

---

### Phase 5: Augmented Dataset Construction (Source-Backed)
**Source anchor:** Lines 105-115, 172-204

13. For each corpus sentence:
    - Insert retained API calls at their original positions
    - Preserve original text otherwise
    - Result: `{text_prefix} <API>tool(input) → result</API> {text_suffix}`

14. Merge augmented sentences back into corpus order
15. Save as training shards (HDF5 or Arrow format)

**Validation gate:** Augmented corpus size within 5-15% of original token count.

---

### Phase 6: Fine-Tuning (Source-Backed)
**Source anchor:** Lines 172-204

16. Fine-tune the base LM on augmented dataset:
    - AdamW optimizer, learning rate 5e-5
    - Batch size 8-16 (gradient accumulation if needed)
    - 1-3 epochs over augmented data
    - Standard causal language modeling loss

17. Checkpoint every 10% of training
18. Monitor validation perplexity on held-out augmented data

**Validation gate:** Training loss converges; validation perplexity does not degrade vs. baseline trained on non-augmented data.

---

### Phase 7: Inference-Time Execution (Source-Backed)
**Source anchor:** Lines 204-208

19. Decode token-by-token until `<API>` token is emitted
20. Continue decoding to capture `tool_name(input_text)`
21. Interrupt, execute API, insert `→ result</API>` into context
22. Resume decoding from extended context

**Validation gate:** Model completes ≥90% of sampled API calls without hanging or malformed syntax.

---

### Phase 8: Validation Domains (Source-Backed)
**Source anchor:** Lines 302-340, 362-388, 417-450

20. **LAMA fact probes:** Measure accuracy on "The capital of France is ___" style cloze tasks
21. **Arithmetic reasoning:** Test on "If John has 15 apples and buys 23 more, he has ___" samples
22. **Temporal questions:** "What day of the week is today?" with date context
23. **Baseline comparison:** Run same validation with API calls disabled at inference

**Validation gate:** Tool-enabled model outperforms tool-disabled variant by ≥10% absolute on arithmetic, ≥5% on temporal.

---

### Phase 9: Ablations & Diagnostics

24. Count API call frequency by type in validation outputs
25. Check whether calculator is used on math problems, calendar on temporal questions
26. Verify core LM capability is preserved: measure perplexity on standard corpus with API calls disabled

**Stop conditions:**
- Filtering threshold tuning converges (retention rate stable across 3 runs)
- Validation improvement plateaus or regresses
- Inference-time execution failure rate >10%

---

## Source-Backed vs. Inferred Steps

### Source-Backed (Direct from Paper)
- Steps 1-3: API call representation (lines 86-104)
- Steps 4-6: Candidate generation prompts (lines 123-152)
- Steps 7-9: API execution (lines 123-132)
- Steps 10-12: Loss-based filtering (lines 134-171)
- Steps 13-15: Augmented dataset construction (lines 105-115, 172-204)
- Steps 16-18: Fine-tuning (lines 172-204)
- Steps 19-22: Inference-time execution (lines 204-208)
- Steps 20-23: Validation domains (lines 302-450)

### Inferred Adaptations
- Model choice (GPT-2/GPT-Neo instead of GPT-J; compute constraints)
- Corpus choice (paper uses CCNet; we'll use OpenWebText or similar)
- Exact filtering threshold value (paper implies tuning; starting point τ=0.1)
- API backend implementations (Wikipedia library, eval() for calculator)
- Hyperparameters (learning rate, batch size) estimated from standard fine-tuning practice

---

## Likely Failed Branch

**Branch:** Setting filtering threshold τ=0.0 (keep all candidate calls)

**Expected failure:**
1. All sampled API calls pass filtering, including spurious ones
2. Model learns to insert calls everywhere, degrading fluency
3. Validation perplexity with API calls disabled increases (core LM ability damaged)
4. Arithmetic accuracy does not improve because spurious calculator calls outnumber helpful ones
5. Inference becomes slow due to excessive API execution

**Recovery:** Increase τ incrementally (0.05, 0.1, 0.2) until retention rate drops to 5-20% and validation metrics improve.

This branch is documented in source anchors lines 134-171 (filtering methodology) and lines 232-237 (heuristics to reduce computational cost).

---

## Summary

This plan is **executable** in a local environment with open models and simulated APIs. All core steps are grounded in the paper's workflow. The main engineering work is:
- Implementing the loss-based filtering loop (step 10-12)
- Building inference-time API call interception (step 19-22)
- Tuning the filtering threshold empirically

The plan preserves the paper's self-supervised approach and avoids inventing results or tools not described in the source.
