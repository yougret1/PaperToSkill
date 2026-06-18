# AIDE-Style Code Optimization Run Plan

## Run Objective

Execute a local AIDE-style tree-search code optimization experiment on a small tabular ML task. Generate candidate Python scripts through draft/debug/improve actions, evaluate each with a validation accuracy objective function, maintain a solution tree with parent edges and scores, and select the best-scoring non-buggy solution after completing the search budget.

## Solution Tree Schema

Each node in the solution tree contains:

- **Node ID**: Unique identifier (e.g., `node_0`, `node_1`)
- **Code**: Complete Python script as string
- **Parent Edge**: Reference to parent node ID and action type (`draft`, `debug`, or `improve`). Root node has `null` parent.
- **Score**: Float value from objective function (e.g., validation accuracy 0.0–1.0, or `null` if buggy)
- **Buggy Status**: Boolean indicating whether execution raised errors
- **Selected Base Node**: Boolean marking whether this node was chosen as base for next iteration

Example structure:
```python
{
  "node_id": "node_3",
  "code": "import pandas as pd\n...",
  "parent": {"node_id": "node_1", "action": "improve"},
  "score": 0.847,
  "buggy": False,
  "selected_base": True
}
```

## Draft/Debug/Improve Loop

**Search Policy (hard-coded):**

1. **Draft**: When no valid solutions exist, generate a single-file program from scratch using data preview and task description.
2. **Debug**: When the selected base node is buggy and debug depth < 3, fix errors by inspecting logs and traces while preserving the original approach.
3. **Improve**: When the selected base node is valid, make one atomic measurable change (e.g., add feature engineering, tune single hyperparameter, switch model class).

**Debug-Depth Budget**: Maximum 3 consecutive debugging attempts per branch before abandoning and drafting a new solution.

**Atomic Improvement Rule**: Each improve action changes exactly one component (one feature transform, one hyperparameter, one model swap) to isolate impact on the objective function.

## Context Summary Schema

Extracted for each coding prompt to avoid unbounded history growth:

- **Performance Metrics**: Best score so far, score distribution across valid nodes, number of buggy vs. valid solutions
- **Hyperparameters**: Model type, key hyperparameters (e.g., `max_depth=5`, `learning_rate=0.01`)
- **Debugging Hints**: Most recent error type and line number if debugging, or performance bottleneck if improving

Example:
```
Best score: 0.863 | Valid nodes: 4 | Buggy nodes: 2
Current model: RandomForestClassifier(n_estimators=100, max_depth=5)
Last error: KeyError at line 23 (missing column 'feature_x')
```

## Data Preview Schema

Provided statically at experiment start to inform coding decisions without running full EDA:

- **Dataset Size**: Number of rows and columns (e.g., 5000 rows × 12 columns)
- **Column Names**: List of feature names and target variable
- **Data Splits**: Train/validation split sizes (e.g., 4000 train, 1000 validation)
- **Target Metric**: Validation accuracy, F1, RMSE, or competition-specific metric

Example:
```
Dataset: 5000 rows × 12 columns
Columns: ['age', 'income', 'education', ..., 'target']
Split: 4000 train, 1000 validation
Metric: Validation accuracy
```

## Validation Plan

**Objective Function**: Stateless Python function that accepts a candidate script path, executes it in an isolated subprocess, captures `validation_score` from stdout or a designated output file, and returns a float score or `null` if execution fails.

**Local Execution Commands**:
```bash
# Run candidate script
python candidate_solution.py > output.log 2>&1

# Parse validation score from output.log or submission.csv
grep "validation_score" output.log | awk '{print $2}'
```

**Best-Solution Selection**: After search budget exhausted (e.g., 10 iterations or 1-hour wall time), return the node with the highest non-null score among all valid (non-buggy) nodes in the solution tree.

**Failure Recording**: If a candidate script raises exceptions, record `buggy=True`, `score=null`, and append error traceback to the node metadata for debugging context.

## Limitations

1. **Holdout Mismatch**: Local validation splits may differ from official test distributions, so reported scores may not reflect final leaderboard performance. (Source: lines 396-398)

2. **Data Contamination Risk**: If using publicly available datasets, the underlying LLM may have seen related examples during pretraining, inflating perceived novelty. Live competition submissions are the only way to ensure no contamination. (Source: lines 398-402)

3. **Greedy Local Optima**: The hard-coded search policy (draft → debug → improve) is greedy and may converge to suboptimal solutions on complex tasks requiring exploration of fundamentally different approaches. (Source: lines 488-491)

4. **Single-File Constraint**: AIDE's design targets single-script solutions. Tasks requiring modular codebases, multi-step pipelines, or interactive debugging sessions may exceed the framework's scope. (Source: lines 494-501)

5. **Cost**: LLM inference costs can reach ~$2.50 USD per task for complex problems, with most simple tabular tasks staying under $1.50 USD at reported GPT-4 Turbo pricing. (Source: lines 744-752)

6. **Harness-Specific Limitations**:
   - No live code execution available in this transfer context
   - No actual dataset provided for validation
   - No real objective function to compute scores
   - Cannot report experimental success without running the plan

## Transfer Adaptation Note

**Original Context**: AIDE was developed for 24-hour Kaggle competitions with tabular ML tasks, using GPT-4 Turbo or o1-preview, and evaluated across Weco-Kaggle, MLE-Bench, and RE-Bench with automated submission systems and official leaderboards.

**Target Harness**: Claude-style project prompt harness, which provides conversational assistance but lacks integrated dataset loading, automatic code execution, or competition submission infrastructure.

**Key Adaptations**:

1. **Removed Live Execution Claims**: The original skill assumed AIDE could execute candidate scripts and retrieve validation scores automatically. In this harness, we explicitly state that code execution, dataset access, and scoring are unavailable, and record this as a limitation.

2. **Preserved Solution Tree Structure**: The core tree-search schema (nodes with code, parent edges, scores, buggy flags) is harness-neutral and reusable for any agent implementing AIDE's method.

3. **Clarified Stateless Objective**: The plan emphasizes that the objective function must be stateless (each script evaluated independently) to match AIDE's design, even though the harness cannot provide a working implementation.

4. **Added Harness Limitation**: Explicitly documented that this transfer cannot demonstrate experimental success, compute real scores, or validate the workflow without external execution infrastructure.

5. **Kept Source-Backed Validation**: All performance claims (Kaggle results, MLE-Bench metrics, RE-Bench timings) are attributed to the source paper and separated from harness-specific adaptations.
