# Toolformer Experiment Plan

## Context Sufficiency Assessment

**Sufficient:** Yes, the context provides enough detail to plan a Toolformer-style experiment. The core workflow (API-call representation, candidate generation, execution, loss filtering, augmented dataset creation, fine-tuning, and inference-time execution) is fully specified.

**Missing details that require inference:**
- Exact filtering threshold values
- Prompt templates for few-shot demonstrations
- Weighted loss calculation specifics
- Dataset size and composition
- Fine-tuning hyperparameters

---

## Required Local Tools & Simulated APIs

### Core Infrastructure
1. **Language model** (e.g., GPT-2, GPT-J, or similar open model)
2. **Fine-tuning pipeline** (PyTorch/Transformers)
3. **Loss calculation utilities** (per-token cross-entropy)

### Simulated APIs (text-to-text)
1. **Calculator** — Python `eval()` or `sympy` for arithmetic
2. **QA system** — Lightweight model or mock responses
3. **Wikipedia search** — Wikipedia API or local index
4. **Calendar** — Date/time utilities
5. **Translation** — Small translation model or mock

---

## Step-by-Step Run Plan

### Phase 1: Setup (Source-Backed)
**Step 1.1** — Define API-call text representation  
Format: `[API_NAME(input) → result]`  
*Source: lines 86-104*

**Step 1.2** — Write few-shot prompts for each API  
Create 3–5 demonstrations per tool showing when/how to insert calls  
*Source: lines 123-152, 157-165*

**Step 1.3** — Prepare base dataset  
Use a subset of C4, WikiText, or similar (start with 10K–100K examples)  
*Inferred: paper uses "large corpus" but doesn't specify size for replication*

---

### Phase 2: Candidate Generation (Source-Backed)
**Step 2.1** — Sample candidate API calls  
For each text span, use the base LM + few-shot prompt to generate potential API calls at multiple positions  
*Source: lines 105-115, 155-173*

**Step 2.2** — Execute all candidate calls  
Run each proposed API call through its actual backend  
*Source: lines 123-132*

**Step 2.3** — Compute loss deltas  
For each candidate position `i`:
- `L_orig`: loss on tokens `i+1` onward with no API call
- `L_call`: loss with API call but no result
- `L_full`: loss with API call and result

Keep call if `L_full < L_orig - threshold` AND `L_full < L_call`  
*Source: lines 134-171*  
*Inferred: threshold value (paper uses filtering but doesn't specify exact value)*

---

### Phase 3: Dataset Augmentation (Source-Backed)
**Step 3.1** — Filter and insert API calls  
Retain only calls that pass the loss-reduction filter  
*Source: lines 134-171*

**Step 3.2** — Build augmented dataset  
Interleave retained API calls into original text sequences  
Original content remains unchanged except for insertions  
*Source: lines 172-204*

---

### Phase 4: Fine-Tuning (Source-Backed)
**Step 4.1** — Fine-tune on augmented data  
Train the LM on text + API calls using standard language modeling loss  
*Source: lines 172-204*

**Step 4.2** — Create control baseline  
Fine-tune identical model on same corpus without API calls  
*Source: lines 453-470*

---

### Phase 5: Inference (Source-Backed)
**Step 5.1** — Implement interrupt-execute-continue loop  
- Decode until API token appears
- Pause generation
- Execute API call
- Insert result
- Resume decoding  
*Source: lines 204-208*

**Step 5.2** — Run zero-shot evaluation  
Test on unseen tasks requiring tool use  
*Source: lines 211-221, 274-284*

---

### Phase 6: Validation (Source-Backed + Inferred)
**Step 6.1** — Check tool emergence  
Verify model learns to call tools without explicit supervision beyond few-shot prompts  
*Source: lines 211-221*

**Step 6.2** — Compare with disabled-tool baseline  
Measure performance gain from API calls vs. same model with calls disabled  
*Source: lines 302-311*

**Step 6.3** — Verify no language modeling degradation  
Compare perplexity on held-out data (without API calls) between augmented and control models  
*Source: lines 453-470*

**Step 6.4** — Domain-specific checks  
- **Math:** accuracy on arithmetic/reasoning tasks + calculator usage rate *(lines 316-340)*
- **QA:** accuracy on knowledge-intensive questions *(lines 362-388)*
- **Temporal:** date-related query accuracy + calendar API usage *(lines 417-450)*

*Inferred: exact test sets not specified; use LAMA, GSM8K-style tasks, or similar*

---

## Stop Conditions

1. **Success:** Augmented model outperforms disabled-tool baseline by >10% on at least one domain
2. **Partial success:** API calls emerge but provide marginal gains (<5%)
3. **Failure:** Model doesn't learn to generate well-formed API calls
4. **Degradation:** Core language modeling perplexity increases >5% vs. control
5. **Scale failure:** Model too small to benefit from tools *(lines 433-496)*

---

## Validation Checks

| Check | Source-Backed | Inferred Adaptation |
|-------|---------------|---------------------|
| API calls reduce future-token loss | ✓ (lines 134-171) | Need to set threshold value |
| Zero-shot tool use without task-specific training | ✓ (lines 211-221) | Need to define "zero-shot" tasks |
| No degradation vs. control fine-tune | ✓ (lines 453-470) | — |
| Improvement on math with calculator | ✓ (lines 316-340) | Need math benchmark |
| QA improvement with Wikipedia | ✓ (lines 362-388) | Limited by simple search interaction |
| Temporal improvement with calendar | ✓ (lines 417-450) | Some gains not fully attributable |

---

## Likely Failed Branch

**Branch:** Loss filtering is too aggressive  
**Scenario:** Set threshold too high → most candidate API calls rejected → augmented dataset nearly identical to original → fine-tuned model doesn't learn tool use  
**Detection:** Check API call retention rate during Phase 3.1. If <1% of candidates survive, lower threshold  
**Recovery:** Reduce filtering threshold by 50% and re-run augmentation  
*Source context: lines 134-171 describe filtering but don't specify robustness to threshold choice*

---

## Summary

This plan preserves the Toolformer workflow: text-based API representation, self-supervised candidate generation via few-shot prompting, execution-based filtering using future-token loss, augmented dataset construction, fine-tuning, and inference-time tool execution. The experiment is executable locally with open models and simulated APIs. Core steps are source-backed; thresholds, dataset sizes, and exact test sets require inference. The primary risk is failed tool emergence due to model scale or filtering miscalibration.
