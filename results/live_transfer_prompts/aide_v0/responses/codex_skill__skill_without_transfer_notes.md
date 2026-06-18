# AIDE-Style Code Optimization Run Plan

## Run Objective

Execute a local AIDE-style iterative tree search to optimize a Python script for a tabular ML task. Start with a draft solution, evaluate with a stateless objective function (validation accuracy or holdout loss), debug buggy nodes within a depth budget, improve the best non-buggy solution with atomic measurable changes, and return the highest-scoring candidate.

---

## Solution Tree Schema

Each node in the solution tree represents a discovered Python script:

```python
{
  "node_id": str,              # Unique identifier
  "code": str,                 # Full Python script content
  "parent_id": str | None,     # Parent node (None for root draft)
  "action": str,               # "draft" | "debug" | "improve"
  "score": float | None,       # Objective function result (None if buggy)
  "buggy": bool,               # True if execution failed
  "error_log": str | None,     # Execution error if buggy
  "selected_as_base": bool     # True if used as base for next iteration
}
```

The tree preserves:
- **Parent edges**: track improvement lineage
- **Score**: comparable metric (e.g., validation accuracy)
- **Buggy status**: execution failure flag
- **Selected base**: policy decision for next iteration

---

## Draft / Debug / Improve Loop

### Search Policy (Hard-Coded)

1. **Draft**: If no non-buggy solutions exist, generate a single-file script from scratch.
2. **Debug**: If the selected base is buggy and debug depth < `MAX_DEBUG_DEPTH` (default: 2), inspect error logs and preserve the approach while fixing bugs.
3. **Improve**: If the selected base is non-buggy, apply one atomic measurable change (e.g., add feature engineering, tune one hyperparameter, change model class).

### Debug Depth Budget

- `MAX_DEBUG_DEPTH = 2`
- Count successive debug attempts from the same buggy lineage.
- After exceeding budget, abandon that branch and select a different base node or draft a new solution.

### Atomic Measurable Change (Improve)

Each improve step must:
- Change exactly one component (feature, hyperparameter, model, preprocessing step)
- Be independently measurable (re-run validation to compare scores)
- Preserve the validated baseline structure

---

## Context Summary Schema

For each iteration, summarize history to keep prompts concise:

```python
{
  "best_score": float,                      # Highest validation score so far
  "best_node_id": str,                      # Node ID of best solution
  "recent_performance": [                   # Last 3 node scores
    {"node_id": str, "action": str, "score": float | None}
  ],
  "hyperparameters": dict,                  # Key hyperparams from best node
  "debugging_hints": [str]                  # Error patterns from buggy nodes
}
```

**Source-backed claim**: AIDE extracts performance metrics, hyperparameters, and debugging hints rather than appending all historical logs. (lines 201-211)

---

## Data Preview Schema

Provide a static data preview to inform coding decisions without full EDA:

```python
{
  "dataset_size": {"train_rows": int, "test_rows": int},
  "columns": [str],                         # Column names
  "target_column": str,
  "splits": {"train": str, "validation": str},  # File paths or split ratio
  "target_metric": str                      # "accuracy" | "rmse" | "f1" | "log_loss"
}
```

**Source-backed claim**: Static data preview with dataset size, column names, or data splits allows validation and hyperparameter decisions without a full EDA pipeline. (lines 213-217)

---

## Validation Plan

### Objective Function

- **Stateless evaluation**: Each candidate script runs independently.
- **Metric**: Validation accuracy, RMSE, F1, or log-loss depending on task.
- **Execution**: Run `python solution.py` in isolated environment, capture stdout/stderr, parse metric from output or saved file.

### Local Execution Commands

```bash
# Create isolated working directory per node
mkdir -p runs/node_{node_id}
cd runs/node_{node_id}

# Copy data and script
cp ../../data/train.csv .
cp ../../data/test.csv .
cp ../../solution_{node_id}.py solution.py

# Execute with timeout and capture output
timeout 600 python solution.py > stdout.log 2> stderr.log

# Parse validation metric from submission.csv or stdout
python ../../parse_metric.py --output stdout.log --metric accuracy
```

### Best Solution Selection

1. Filter nodes where `buggy == False`.
2. Sort by `score` descending.
3. Return `node_id` and `code` of top-ranked solution.
4. If all solutions are buggy, return the draft node with diagnostic message.

### Failure Recording

- **Execution timeout**: Mark `buggy=True`, log "Timeout after 600s".
- **Runtime error**: Mark `buggy=True`, store traceback in `error_log`.
- **Invalid output**: Mark `buggy=True`, log "Submission file missing or malformed".
- **Low score**: Not marked buggy; record score for comparison.

---

## Limitations

### Source-Backed Limitations

1. **Local optima**: AIDE's greedy policy may converge to local optima on challenging R&D tasks. (lines 488-491)
2. **Single-file scope**: AIDE falls short in environments requiring larger codebases or multi-step interactions; may repeat local patches instead of discovering new strategies. (lines 494-501)
3. **Tabular ML focus**: AIDE was developed for tabular ML tasks. Generalization to neural architecture search or kernel optimization is third-party experimental work. (lines 537-545)
4. **Cost**: LLM inference cost can reach ~$2.50 USD per task (GPT-4 Turbo pricing). (lines 744-752)

### Harness-Specific Limitations

5. **No live Kaggle submission**: This local plan uses holdout validation; scores are not official Kaggle percentiles.
6. **No dataset provided**: Requires user to supply `train.csv`, `test.csv`, and target metric definition.
7. **No automated data preview generation**: User must manually construct the data preview schema.
8. **No LLM cost tracking**: This plan does not include token usage monitoring or budget enforcement.
9. **No parallel node evaluation**: Executes one node at a time; no pass@k parallelization.

---

## Transfer Adaptation Note

### Changes for Codex Harness

**Source skill (AIDE paper)** describes a research system with:
- Full Kaggle competition integration
- Automated data preview generation
- Multi-task benchmarking (Weco-Kaggle, MLE-Bench, RE-Bench)
- Pass@k parallel evaluation
- LLM cost tracking and model selection (GPT-4 Turbo, o1-preview)

**This local plan** adapts for a single-task Codex workspace by:
- Replacing Kaggle API with local file execution (`python solution.py`)
- Requiring manual data preview construction
- Using a single validation split instead of competition train/test protocol
- Removing pass@k parallelization (sequential node execution)
- Dropping cost tracking and model comparison
- Preserving core AIDE primitives: solution tree, draft/debug/improve policy, context summarization, stateless objective function, best-solution selection

**What remains source-backed**:
- Solution tree structure (nodes, edges, scores, buggy flags)
- Three-action coding operator (draft, debug, improve)
- Hard-coded search policy with debug-depth budget
- Context summarization schema (performance metrics, hyperparameters, debugging hints)
- Data preview schema (dataset size, columns, splits, target metric)
- Stateless optimization framework

**What is harness-adapted**:
- Local file execution instead of Kaggle submission
- Manual data preparation instead of automated competition data fetching
- Single-task run instead of multi-benchmark evaluation
- No live experimental results (no claim of "AIDE exceeded X% of humans" unless actually executed)
