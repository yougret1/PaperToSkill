# AIDE-style PaperToSkill Code Optimization Run Plan

## Run Objective

Execute an iterative code optimization experiment that mirrors AIDE's ML engineering workflow: maintain a solution tree, apply draft/debug/improve actions, summarize context after each iteration, validate with an objective function, and select the best solution from the explored tree.

**Target domain:** Simple algorithmic or data processing task (e.g., optimize a sorting function, improve a feature extraction pipeline, or refine a basic model training script) where validation can be measured locally without external APIs or large datasets.

---

## Solution Tree Schema

Each node in the solution tree represents a distinct code variant.

```python
{
  "node_id": "string",           # Unique identifier (e.g., "node_0", "node_1a")
  "code": "string",              # Complete executable code for this solution
  "parent_id": "string | null",  # ID of parent node (null for root)
  "action": "draft | debug | improve",  # Action that produced this node
  "score": "float | null",       # Objective function result (null if buggy or not evaluated)
  "buggy": "boolean",            # True if code failed to execute or raised errors
  "selected_as_base": "boolean", # True if this node was chosen for the next improve step
  "metadata": {
    "iteration": "int",          # Iteration number when created
    "error_log": "string | null" # Error message if buggy
  }
}
```

**Tree rules:**
- Root node is always a draft.
- Debug children fix bugs in their parent.
- Improve children make one atomic measurable change to a non-buggy parent.
- Selected base node is the best-scoring non-buggy node at the end of each iteration.

---

## Draft/Debug/Improve Loop

### Loop Structure

1. **Draft** (iteration 0): Generate initial working solution from task description.
2. **Debug** (if buggy): Fix execution errors with bounded retry depth (max 3 debug attempts per branch).
3. **Improve** (if non-buggy): Generate one atomic change to improve the objective metric.
4. **Evaluate**: Run objective function on all new non-buggy nodes.
5. **Select base**: Choose highest-scoring node for next iteration's improve step.
6. **Repeat**: Continue until max iterations (e.g., 5) or no improvement for 2 consecutive iterations.

### Debug Depth Budget

- Max 3 debug attempts per buggy node.
- If still buggy after 3 attempts, mark node as terminal failure and prune branch.

### Atomic Improve Changes

Each improve action makes **one measurable change**:
- Algorithmic: Change data structure (list → set), algorithm choice (quicksort → mergesort).
- Performance: Add caching, vectorize loop, precompute values.
- Model (if ML task): Adjust one hyperparameter, add one feature, change one layer.

**Anti-pattern:** Bundling multiple unrelated changes in one improve step.

---

## Context Summary Schema

After each iteration, summarize the current state to guide the next action.

```python
{
  "iteration": "int",
  "best_score": "float",
  "best_node_id": "string",
  "performance_metrics": {
    "execution_time_ms": "float",
    "memory_usage_mb": "float | null",
    "custom_metric": "float | null"  # e.g., accuracy, F1, throughput
  },
  "hyperparameters": {
    # Key parameters from best solution (e.g., {"batch_size": 32, "lr": 0.01})
  },
  "debugging_hints": [
    "string"  # Lessons from recent failures (e.g., "IndexError on empty input")
  ],
  "exploration_status": {
    "total_nodes": "int",
    "buggy_nodes": "int",
    "viable_branches": "int"
  }
}
```

---

## Data Preview Schema

Define the task's data characteristics upfront (even for non-ML tasks, describe input/output).

```python
{
  "dataset_size": {
    "train": "int | null",
    "validation": "int | null",
    "test": "int | null"
  },
  "input_schema": {
    "columns": ["string"],      # or "parameters" for algorithmic tasks
    "types": ["string"]
  },
  "output_schema": {
    "target": "string",         # Target variable or output description
    "type": "string"            # e.g., "continuous", "categorical", "array"
  },
  "splits": {
    "train_validation_test": "string"  # e.g., "70/15/15" or "N/A for synthetic"
  },
  "target_metric": "string"     # e.g., "execution_time", "accuracy", "throughput"
}
```

---

## Validation Plan

### Objective Function

**Signature:**
```python
def objective_function(code: str, test_inputs: list) -> dict:
    """
    Execute code against test inputs and return score + metadata.
    Returns: {
        "score": float,        # Higher is better
        "buggy": bool,
        "error": str | None,
        "execution_time_ms": float,
        "custom_metrics": dict
    }
    """
```

**Implementation:**
- Write code to temporary file.
- Execute in isolated subprocess with timeout (e.g., 30s).
- Capture stdout, stderr, exit code.
- Compute score from task-specific metric (e.g., `-execution_time` for speed optimization, `accuracy` for ML).

### Local Execution Commands

```bash
# Example: Python optimization task
python validate.py --node_id node_1a --timeout 30

# Example: ML training task
python train.py --config configs/node_2b.yaml --data_path ./data --output_path ./results
python evaluate.py --model_path ./results/model.pkl --test_path ./data/test.csv
```

### Best Solution Selection

At the end of all iterations:
1. Filter to non-buggy nodes.
2. Rank by `score` descending.
3. Select top node as final solution.
4. If all nodes buggy, report failure and return best pre-failure node.

### Failure Recording

Log failures in solution tree metadata:
```python
{
  "node_id": "node_3c",
  "buggy": true,
  "metadata": {
    "error_log": "IndexError: list index out of range at line 42",
    "debug_attempts": 2,
    "pruned": false
  }
}
```

---

## Limitations (Source-Backed + Adapted)

### From AIDE Source Context

1. **Benchmark contamination risk:** If using public datasets (Kaggle, MLE-Bench), training data may have leaked into LLM pretraining.
2. **Evaluation mismatch:** Local validation scores may not align with held-out test sets or private leaderboards.
3. **Local optima:** Tree search may converge to suboptimal solutions if improve actions explore narrow neighborhoods.
4. **LLM call cost:** Repeated code generation and debugging incurs token usage and latency.

### Harness-Specific Adaptations

5. **No live Kaggle submission:** This local harness cannot submit to external leaderboards; validation is offline only.
6. **Missing datasets:** If the task references unavailable data (e.g., proprietary benchmarks), use synthetic or placeholder data with noted limitations.
7. **No human scoring:** All evaluation is automated via objective function; no human judgment of code quality or creativity.
8. **Execution environment constraints:** Local runs may differ from original AIDE infrastructure (different OS, Python version, library versions).
9. **Simplification for demo:** Real AIDE runs may use more sophisticated node selection (e.g., UCT, Bayesian optimization); this plan uses greedy best-score selection.

---

## Transfer Adaptation Note

**What changed for the Codex harness:**

- **Execution model:** AIDE ran on cloud infrastructure with Kaggle API integration. This plan uses local file-based code execution with subprocess isolation.
- **Objective function:** AIDE evaluated ML models on benchmark metrics (accuracy, F1, RMSE). This plan generalizes to any measurable code property (runtime, correctness, throughput) and requires the user to implement the objective function for their task.
- **Solution tree persistence:** AIDE's tree was managed in-memory or via experiment tracking. This plan outputs tree state to JSON after each iteration for reproducibility and debugging.
- **Context summarization:** AIDE's context was implicit in agent prompts. This plan explicitly serializes context summaries to guide LLM actions and enable stateless iteration.
- **Data preview:** AIDE worked with known Kaggle datasets. This plan requires upfront data schema definition or uses synthetic data for algorithmic tasks.
- **Debug depth budget:** Explicit 3-attempt limit adapted from source mentions of "fix bugs" without specified retry policy.
- **No claim of live success:** This is a *plan*, not an executed experiment. Actual scores, runtimes, and tree shapes are unknown until run.

**Preserved from source:**
- Tree-structured solution exploration.
- Draft → Debug → Improve action taxonomy.
- Stateless objective function for reproducibility.
- Best-solution selection from explored nodes.
- Recognition of local optima and cost limitations.
