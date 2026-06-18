# AIDE-Style Code Optimization Run Plan

## Run Objective

Execute a local AIDE-inspired code optimization experiment on a small tabular ML task. The run will initialize a solution tree, iteratively draft/debug/improve Python scripts using a stateless objective function (validation accuracy or loss), and select the best-scoring non-buggy solution after a fixed budget of iterations.

---

## Solution Tree Schema

Each node in the solution tree represents a candidate Python script:

```python
{
  "node_id": str,           # Unique identifier
  "code": str,              # Complete Python script content
  "parent_id": str | None,  # Parent node ID (None for root drafts)
  "action": str,            # One of: "draft", "debug", "improve"
  "score": float | None,    # Objective function result (e.g., validation accuracy)
  "buggy": bool,            # True if execution failed or raised errors
  "error_log": str | None,  # Stack trace or error message if buggy
  "selected_base": bool     # True if this node was selected as base for next iteration
}
```

**Tree invariants:**
- Draft nodes have `parent_id = None`.
- Debug nodes inherit from buggy parents and preserve the overall approach.
- Improve nodes inherit from non-buggy parents and introduce one atomic measurable change.

---

## Draft/Debug/Improve Loop

### Search Policy (Hard-coded)

1. **Draft**: If the tree is empty or all existing non-buggy nodes have been exhausted, generate a single-file solution from scratch.
2. **Debug**: If the selected base node is buggy and `debug_depth < MAX_DEBUG_DEPTH`, attempt to fix errors by inspecting logs and traces while preserving the approach.
3. **Improve**: If the selected base node is non-buggy, propose one atomic measurable change (e.g., add feature engineering, tune hyperparameter, change model class).

### Debug-Depth Budget

- `MAX_DEBUG_DEPTH = 3`: After three consecutive debugging attempts on the same buggy lineage, abandon that branch and draft a new solution or select a different base node.

### Atomic Measurable Change Rule

Each `improve` action must:
- Modify exactly one aspect of the solution (feature, hyperparameter, algorithm, preprocessing step).
- Be independently testable via the objective function.
- Avoid bundled changes that make performance attribution unclear.

---

## Context Summary Schema

Before each coding action, construct a concise context summary rather than appending full history:

```python
{
  "best_score": float | None,           # Highest validation score so far
  "best_node_id": str | None,           # Node ID of best solution
  "performance_metrics": {              # Key metrics from recent nodes
    "node_id": {"score": float, "action": str}
  },
  "hyperparameters": dict,              # Extracted from best or selected base node
  "debugging_hints": list[str],         # Recent error patterns or fixes
  "iterations_completed": int,          # Progress tracker
  "budget_remaining": int               # Iterations or time left
}
```

**Summarization operator extracts:**
- Performance metrics: validation accuracy, loss, or task-specific score.
- Hyperparameters: model type, regularization, tree depth, learning rate.
- Debugging hints: common error types (e.g., missing imports, shape mismatches, train/test leaks).

---

## Data Preview Schema

Provide a static data preview to inform coding decisions without requiring full exploratory data analysis:

```python
{
  "dataset_size": {"train": int, "test": int},
  "column_names": list[str],
  "target_column": str,
  "data_splits": {"train": str, "validation": str, "test": str},  # File paths or split ratios
  "target_metric": str,  # e.g., "accuracy", "log_loss", "RMSE"
  "task_type": str       # e.g., "binary_classification", "regression", "multiclass"
}
```

**Example:**
```python
{
  "dataset_size": {"train": 800, "test": 200},
  "column_names": ["feature_1", "feature_2", "feature_3", "target"],
  "target_column": "target",
  "data_splits": {"train": "data/train.csv", "validation": "holdout", "test": "data/test.csv"},
  "target_metric": "accuracy",
  "task_type": "binary_classification"
}
```

---

## Validation Plan

### Objective Function

- **Stateless evaluation**: Each candidate script is executed independently in a clean environment.
- **Metric**: Validation accuracy (or loss) computed on a holdout split separate from training data.
- **Interface**: The script must produce a `submission.csv` or return a validation score via stdout/stderr parsing.

### Local Execution Commands

```bash
# Assume candidate script is saved as candidate_solution.py
python candidate_solution.py --train data/train.csv --test data/test.csv --output submission.csv

# Parse validation score from output or compute from submission.csv
python evaluate.py --submission submission.csv --ground_truth data/validation.csv
```

### Best-Solution Selection

After completing the iteration budget:
1. Filter out all buggy nodes (`buggy == True`).
2. Rank non-buggy nodes by `score` (descending for accuracy, ascending for loss).
3. Select the top-ranked node as the final solution.
4. If no non-buggy nodes exist, report failure and return the least-buggy draft.

### Failure Recording

For each failed execution:
- Record `buggy = True` and capture the full error log in `error_log`.
- Increment the debug-depth counter for that lineage.
- If `debug_depth >= MAX_DEBUG_DEPTH`, mark the lineage as abandoned and exclude from future base selection.

---

## Limitations

### Source-Backed Limitations

1. **Holdout vs. Private Test Set Discrepancy**: Kaggle holdout sets may differ from official private test sets, so percentile scores may not be directly comparable in live competitions. *(Lines 396-398)*
2. **Data Contamination Risk**: LLMs may have seen competition-related data during pretraining; only live competition submissions fully ensure no contamination. *(Lines 398-402)*
3. **Greedy Policy Local Optima**: The hard-coded search policy may converge to local optima on challenging R&D tasks. *(Lines 488-491)*
4. **Limited to Single-File Solutions**: AIDE underperforms in environments requiring larger codebases or multi-step interaction workflows; it may repeat local patches instead of discovering new strategies. *(Lines 494-501)*
5. **Generalization Beyond Tabular ML**: While developed for tabular tasks, third-party experiments suggest the approach can generalize to neural architecture search, Triton kernel optimization, and other AI R&D domains, but this is not source-validated. *(Lines 537-545)*
6. **LLM Inference Cost**: Costs can reach approximately $2.50 USD per task, with most Weco-Kaggle tasks under $1.50 USD using GPT-4 Turbo pricing. *(Lines 744-752)*

### Harness-Specific Limitations

7. **No Live Experimental Run**: This plan is a transfer-adapted specification. No actual code execution, dataset loading, or scoring has been performed. Success metrics are hypothetical.
8. **Missing Dataset**: The run plan assumes a local tabular dataset is available. If no dataset is provided, the experiment cannot proceed.
9. **Unavailable Scoring Infrastructure**: The objective function requires a local Python evaluation script or Kaggle API access. If these are unavailable, the solution tree cannot be scored.
10. **Excessive Cost for Claude Harness**: Running multiple LLM-powered coding iterations in a live Claude Project context may exceed reasonable API cost or token budget. The plan is intended for small-scale local reproduction, not production deployment.

---

## Transfer-Adaptation Note

### What Changed for the Target Harness

The source AIDE paper describes a framework implemented in Python with custom tree-search infrastructure, automated Kaggle submission, and a 24-hour execution budget. This plan adapts the method for a **Claude-style project prompt harness** with the following changes:

1. **Execution Environment**: Replaced Kaggle API and custom Python infrastructure with local file-based execution commands and manual evaluation scripts.
2. **Context Management**: Retained the summarization operator but adapted it to Claude's context-aware prompt compaction and file-reading tools rather than AIDE's internal memory buffer.
3. **Tool Substitution**: Used file-editing tools and terminal commands instead of AIDE's code-generation API wrappers.
4. **Budget**: Reduced iteration budget from 24 hours to a fixed small number of iterations (e.g., 5-10) suitable for a local demonstration.
5. **Dataset Scope**: Narrowed focus to small tabular ML tasks (e.g., <1000 rows) that can be validated locally without cloud compute.
6. **Best-Solution Selection**: Preserved the source paper's ranking-by-score logic but added explicit handling for the all-buggy-nodes failure case.
7. **Limitations Disclosure**: Separated source-backed limitations from harness-specific limitations (no live run, missing dataset, unavailable scoring, cost constraints).

**Source-backed steps** (solution tree, draft/debug/improve, stateless objective, context summarization, data preview) are preserved. **Harness-specific adaptations** (local execution, file tools, reduced budget, failure recording) are marked as inferred equivalents.
