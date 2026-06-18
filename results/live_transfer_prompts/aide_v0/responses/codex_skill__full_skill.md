# AIDE-Style Code Optimization Run Plan

## Run Objective

Execute a local AIDE-style tree-search optimization on a small tabular ML task. Draft an initial solution, evaluate it against a validation metric, debug errors within a depth budget, and iteratively improve the best non-buggy solution with atomic measurable changes. Return the highest-scoring solution from the tree.

## Solution Tree Schema

```python
# Node structure
{
  "node_id": str,           # unique identifier
  "code": str,              # full Python script content
  "parent_id": str | None,  # parent node ID, None for root
  "action": str,            # "draft" | "debug" | "improve"
  "score": float | None,    # validation metric (e.g., accuracy), None if buggy
  "buggy": bool,            # True if execution failed
  "error_log": str | None,  # captured stderr/exception
  "selected_base": bool     # True if chosen as base for next iteration
}
```

The tree is stored as a list of node dictionaries. Each iteration appends one new node.

## Draft/Debug/Improve Loop

**Search Policy:**
- **Draft:** If tree is empty, generate an initial solution from scratch.
- **Debug:** If the selected base node is buggy and debug depth < 3, generate a fix preserving the approach.
- **Improve:** If the selected base node is non-buggy, generate one atomic measurable change (e.g., tune one hyperparameter, add one feature, switch one algorithm component).

**Debug Depth Budget:** Maximum 3 consecutive debug attempts from the same buggy node before abandoning that branch.

**Atomic Change Constraint:** Each improve action modifies exactly one component: one hyperparameter value, one preprocessing step, or one model choice.

## Context Summary Schema

```python
{
  "performance_metrics": [
    {"node_id": str, "score": float, "action": str}
  ],
  "hyperparameters": {
    "node_id": {"param_name": value, ...}
  },
  "debugging_hints": [
    {"node_id": str, "error_type": str, "attempted_fix": str}
  ]
}
```

Only the last 5 nodes' summaries are retained to keep prompts concise.

## Data Preview Schema

```python
{
  "dataset_name": str,
  "total_rows": int,
  "column_names": [str, ...],
  "target_column": str,
  "train_split_size": int,
  "holdout_split_size": int,
  "task_type": "classification" | "regression",
  "target_metric": "accuracy" | "f1" | "rmse" | "mae"
}
```

Static preview is generated once before the first draft and injected into all coding prompts.

## Validation Plan

**Objective Function:**
- For classification: validation accuracy on holdout split
- For regression: negative RMSE on holdout split (higher is better)

**Local Execution Commands:**
1. Write candidate solution to `solution.py`
2. Execute: `python solution.py --train data/train.csv --test data/holdout.csv --output submission.csv`
3. Capture stdout, stderr, and exit code
4. If exit code != 0, mark node as buggy and record error_log
5. If exit code == 0, parse validation metric from stdout or submission.csv and record score

**Best Solution Selection:**
- After max iterations (default 10) or time budget (default 30 minutes), select the node with the highest non-null score.
- If all nodes are buggy, return the last draft node with a failure record.

**Failure Recording:**
- Each buggy node stores `error_log` with the full stderr trace.
- Debugging hints extract error type (ImportError, ValueError, KeyError, etc.) and attempted fix description.

## Limitations

**Source-Backed (from AIDE paper):**
- Holdout validation scores may not match official test set performance if data distributions differ.
- Possible data contamination if the LLM has seen task-related data during pretraining; live submissions are the only contamination-free validation.
- Greedy search policy can lead to local optima on challenging R&D tasks.
- Limited effectiveness on tasks requiring large multi-file codebases or multi-step interactive workflows.
- LLM inference cost can reach $1.50–$2.50 USD per task depending on iteration count and model pricing.

**Harness-Specific Adaptations:**
- **No live Kaggle submission:** This local plan uses a static train/holdout split, not official competition test sets.
- **No human baseline scores:** The plan does not compute "Exceeds % of Human" or "Above Median" metrics because no human leaderboard is available locally.
- **No automated dataset fetch:** The user must provide `data/train.csv` and `data/holdout.csv` before execution.
- **No cost tracking:** Actual LLM API costs are not measured in this plan; cost estimates remain theoretical.
- **Single-file constraint:** All solutions are single-file Python scripts; multi-file projects are out of scope.

## Transfer Adaptation Note

**What Changed for the Codex Harness:**

The source AIDE paper describes a 24-hour multi-competition Kaggle agent with automated data fetching, official leaderboard submission, and model comparison against human baselines and AutoML tools. This local Codex plan adapts the core tree-search loop (draft/debug/improve, solution tree, context summarization, data preview) to a single-task, single-file, local-validation workflow.

**Key Adaptations:**
1. **Kaggle API replaced with local file I/O:** No `kaggle competitions download`; user provides CSV files.
2. **Official test set replaced with static holdout split:** Validation is computed locally, not submitted to a competition server.
3. **Human percentile metrics dropped:** No "Exceeds % of Human" or "Above Median" calculation.
4. **Time budget reduced:** From 24 hours to 30 minutes default for a single local task.
5. **Single-file constraint enforced:** AIDE's paper examples use single-file solutions; this plan makes that explicit.
6. **No live execution claim:** This is a plan document, not a completed experiment. Actual runs, scores, and costs are not yet available.

All source-backed workflow steps (solution tree, stateless objective function, search policy, summarization, data preview) are preserved. The adaptations address harness-specific tool availability and output expectations without altering the paper's core contribution.
