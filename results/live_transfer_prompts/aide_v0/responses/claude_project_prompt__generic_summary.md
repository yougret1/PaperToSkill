# AIDE-Style Code Optimization Run Plan for Claude Project Harness

## Run Objective

Execute a local AIDE-style iterative code optimization experiment on a machine learning task. The agent will draft initial solution code, debug execution failures, and iteratively improve model performance through small atomic changes, maintaining a solution tree to track explored variants and selecting the best-performing solution based on a stateless objective function.

## Solution Tree Schema

Each node in the solution tree contains:

- **node_id**: Unique identifier (e.g., `node_0`, `node_1_debug_0`, `node_1_improve_0`)
- **code**: Complete executable Python script for the ML solution
- **parent_id**: Reference to parent node (null for root)
- **edge_type**: Action that created this node (`draft`, `debug`, `improve`)
- **score**: Numeric evaluation metric (e.g., accuracy, F1, RMSE) or null if execution failed
- **buggy**: Boolean indicating whether code executed successfully
- **is_selected_base**: Boolean marking whether this node was selected as base for next improvement iteration

## Draft/Debug/Improve Loop

1. **Draft**: Generate initial solution code from task description and data preview
2. **Debug**: If execution fails (buggy=true), fix errors with maximum debug depth of 3 attempts per node
3. **Improve**: From best non-buggy node, make one atomic measurable change:
   - Add/modify a single feature engineering step
   - Change one hyperparameter
   - Swap one model component
   - Adjust one preprocessing step
4. **Select Base**: After each improve iteration, select the highest-scoring non-buggy node as the new base
5. **Terminate**: Stop after 10 improve iterations or when score improvement < 0.01 for 3 consecutive iterations

## Context Summary Schema

Maintained across iterations and compacted as needed:

- **performance_history**: List of (node_id, score, iteration) tuples for all non-buggy nodes
- **best_score_so_far**: Current highest validation metric
- **hyperparameters_explored**: Set of hyperparameter configurations already tried
- **debugging_hints**: Common error patterns encountered (import errors, shape mismatches, missing columns)
- **feature_engineering_log**: Features added/removed in improve steps
- **current_iteration**: Integer tracking improve step count

## Data Preview Schema

Before drafting initial solution:

- **dataset_path**: Local file path to training/test data
- **dataset_size**: Row and column counts (train/test splits)
- **column_names**: List of feature column names
- **target_column**: Name of prediction target
- **data_splits**: Train/validation/test split specification
- **target_metric**: Evaluation metric for objective function (e.g., "accuracy", "rmse", "f1_macro")
- **sample_rows**: First 5 rows of training data for type/distribution inspection

## Validation Plan

### Objective Function
- **Stateless**: Each solution evaluated independently by running its code against validation data
- **Metric extraction**: Parse printed output or saved predictions file to extract single numeric score
- **Execution command**: `python solution_node_{id}.py --mode validate --data {dataset_path}`

### Local Execution
1. Write node code to temporary file `solution_node_{id}.py`
2. Execute in isolated subprocess with 5-minute timeout
3. Capture stdout/stderr for score extraction or error diagnosis
4. Record execution success (buggy=false) or failure (buggy=true)
5. If successful, parse validation metric from output

### Best Solution Selection
- After all iterations complete, select node with highest score among all non-buggy nodes
- Re-run best solution on held-out test set for final evaluation
- Save best solution code to `best_solution.py`

### Failure Recording
- Log all buggy nodes with (node_id, error_type, error_message)
- Track debug attempts per node
- Record abandoned branches (nodes that could not be debugged within budget)

## Limitations

**Source-backed limitations from AIDE research:**
- Possible benchmark contamination: LLM training data may include similar Kaggle problems, inflating measured performance
- Public/private leaderboard mismatch: Validation metrics may not reflect final test performance due to overfitting
- Local optima: Tree search may converge to suboptimal solutions without exploring alternative approaches
- Cost from repeated LLM calls: Each draft/debug/improve step requires API calls, accumulating expense on large iteration counts

**Harness-specific adaptations for Claude project environment:**
- **Missing live dataset**: This plan requires a local ML dataset (CSV/parquet) that is not provided in current context. User must supply dataset path before execution.
- **No actual code execution available**: Claude cannot directly execute Python subprocesses for objective function evaluation. User must run generated solution scripts manually and report scores back.
- **No automated scoring**: Validation metric extraction requires user to parse script output and input scores into the agent workflow.
- **Context compaction impact**: Solution tree may be summarized after compaction, losing detailed debugging hints from early iterations.
- **Human-in-loop required**: Each improve iteration needs user confirmation of execution results before proceeding to next step.

## Transfer Adaptation Note

The original AIDE system operates autonomously with direct code execution, subprocess management, and automated metric extraction. This Claude harness adaptation introduces **human-in-the-loop validation** where:

1. Agent generates solution code as file content
2. User manually executes code locally
3. User reports back execution success/failure and numeric score
4. Agent updates solution tree and proceeds with next iteration

This preserves AIDE's core tree-search logic and stateless objective function while adapting execution to Claude's file-editing and conversational interface rather than autonomous subprocess control. The agent will guide the user through each step but cannot claim experimental success without user-confirmed execution results.
