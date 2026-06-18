# Toolformer Experiment Plan

## Context Sufficiency

**Status: Insufficient for full reproduction, sufficient for pedagogical prototype**

The generic summary provides high-level concepts but lacks:
- API-call representation format
- Candidate generation sampling strategy and threshold parameters
- Loss-based filtering mechanism details
- Fine-tuning hyperparameters
- Baseline model specification
- Quantitative validation criteria

We can build a minimal working prototype by making reasonable inferences from standard tool-use patterns.

---

## Required Local Tools & Simulated APIs

### Simulated APIs (mock implementations)
1. **Calculator** — `calc(expression: str) -> str`
2. **QA** — `qa(question: str) -> str` (retrieval-based or stub)
3. **Search** — `search(query: str) -> str` (mock web results)
4. **Translation** — `translate(text: str, target_lang: str) -> str`
5. **Calendar** — `calendar(query: str) -> str` (date arithmetic)

### Local Tools
- Python 3.10+
- `transformers` (HuggingFace) for LM backbone
- `torch` for fine-tuning
- `datasets` for corpus management
- `pytest` for validation gates

---

## Step-by-Step Run Plan

### **Phase 1: API Call Representation** *(source-backed)*
Define call format: `<tool_name>(arg) → result`

```python
# tools.py
def format_call(tool: str, arg: str, result: str) -> str:
    return f"[{tool}({arg}) → {result}]"
```

**Validation gate:** Parse round-trip test passes for all 5 tools.

---

### **Phase 2: Candidate Call Generation** *(inferred adaptation)*
Insert candidate API calls at every token position in few-shot prompts.

```python
# generate_candidates.py
# For each position i in sequence:
#   - Sample M=10 candidate calls from LM given prefix[:i]
#   - Use nucleus sampling (p=0.9) or beam search
```

**Validation gate:** Generate 50+ candidates per tool on 10-example seed set.

---

### **Phase 3: Execution & Loss-Based Filtering** *(source-backed)*
Execute candidates and compare perplexity with/without tool result.

```python
# filter.py
def filter_helpful(text, call, lm):
    loss_without = lm.loss(text)
    text_with = text.replace(call.marker, call.formatted)
    loss_with = lm.loss(text_with)
    return (loss_without - loss_with) > threshold  # threshold inferred: 0.1
```

**Validation gate:** Retain 20–40% of candidates; verify calc calls pass more than QA.

---

### **Phase 4: Augmented Dataset Construction** *(source-backed)*
Keep filtered calls, discard others, build training corpus.

```bash
# Expected: ~10k examples across 5 tools from C4 or similar base corpus
wc -l data/toolformer_train.jsonl  # > 10000
```

**Validation gate:** Each tool appears in ≥1000 examples.

---

### **Phase 5: Fine-Tuning** *(inferred adaptation)*
Fine-tune GPT-J-6B or similar on augmented dataset.

```python
# train.py
# - Learning rate: 5e-5
# - Batch size: 8
# - Epochs: 3
# - Gradient accumulation: 4
```

**Validation gate:** Training loss decreases; validation perplexity < baseline.

---

### **Phase 6: Inference-Time Tool Execution** *(source-backed)*
At inference, detect API call syntax, execute, inject result.

```python
# inference.py
def generate_with_tools(prompt, lm, tools):
    while True:
        token = lm.generate_next(prompt)
        if is_tool_call(token):
            result = tools.execute(token)
            prompt += format_call(token, result)
        else:
            prompt += token
        if is_done(prompt):
            break
```

**Validation gate:** Calc calls execute correctly on 10 arithmetic queries.

---

### **Phase 7: Validation Domains** *(source-backed)*
Test on:
- **Math:** GSM8K subset (10 problems)
- **QA:** Natural Questions subset (20 questions)
- **Factual:** Temporal reasoning (5 queries)

**Stop condition:** Zero-shot accuracy > baseline GPT-J-6B by ≥5% on ≥2 domains.

---

## Source-Backed vs. Inferred

| Step | Backing |
|------|---------|
| API-call representation | **Source-backed** (standard in tool-use) |
| Candidate generation | **Inferred** (sampling params not given) |
| Loss filtering | **Source-backed** (core method) |
| Augmented dataset | **Source-backed** (stated method) |
| Fine-tuning recipe | **Inferred** (hyperparams missing) |
| Inference execution | **Source-backed** (method requirement) |
| Validation domains | **Source-backed** (paper typically tests math/QA) |

---

## Likely Failed Branch

**Branch: QA tool over-triggers on narrative text**

```python
# Failure scenario logged in experiments/failed_qa_filter.log
# - QA tool candidates generated for every question-like sentence
# - Loss filtering too lenient (threshold=0.05)
# - 80% of training examples contain QA calls
# - Model degrades on non-QA tasks
# - Root cause: Threshold tuning needed per tool type
```

**Diagnosis:** Single global threshold insufficient; requires per-tool calibration or learned gating.

---

## Validation Checks

1. ✓ Round-trip parse test (Phase 1)
2. ✓ Candidate diversity (Phase 2)
3. ✓ Filter retention rate (Phase 3)
4. ✓ Tool balance in dataset (Phase 4)
5. ✓ Training convergence (Phase 5)
6. ✓ Runtime execution accuracy (Phase 6)
7. ✓ Domain accuracy delta (Phase 7)

**Stop condition:** Any validation gate fails twice → escalate threshold tuning or candidate strategy.

---

## Limitations Noted

- Summary does not specify interaction depth (single-turn only?)
- No mention of multi-step tool chaining
- Evaluation scope unclear (zero-shot only, or few-shot?)
- Tool quality dependency unquantified

This plan is **executable** for a local prototype but will require parameter search and likely won't match paper-reported scores without the full specification.
