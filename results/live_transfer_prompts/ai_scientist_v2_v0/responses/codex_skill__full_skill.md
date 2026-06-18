# PaperToSkill Codex Experiment Plan

## Run Objective

Execute a small-scale demonstration of the AI Scientist-v2 workflow by running a four-stage experiment manager on a toy machine-learning task. The experiment will generate ideas, implement them as code, execute and debug trials, aggregate metrics across seeds, and produce visualizations for review. The objective is to verify the core workflow components (generalized idea generation, four-stage progression, node lifecycle, debug/refine branching, replication, and visual review) in a local Codex environment, not to produce a novel scientific contribution.

---

## Four-Stage Experiment Table

| Stage | Description | Stopping Criteria | Output to Next Stage |
|-------|-------------|-------------------|---------------------|
| **1. Preliminary Investigation** | Generate a simple research idea and implement a baseline experiment with minimal hyperparameter search. Execute 2-3 candidate nodes. | At least one non-buggy node with recorded metrics | Best-performing non-buggy node (plan, code, metrics, figures) |
| **2. Hyperparameter Tuning** | Spawn child nodes exploring 2-3 hyperparameter variants from the baseline. Execute each variant. | All hyperparameter nodes executed; best configuration identified | Best hyperparameter configuration and associated code |
| **3. Research Agenda Execution** | Implement the core research idea using the tuned hyperparameters. Run 3 replications with different random seeds. | All replications complete; aggregated metrics computed | Aggregated metrics, mean/std curves, replication logs |
| **4. Ablation Studies** | Remove or modify one component of the approach and compare against the full method. Execute 1-2 ablation nodes. | Ablation nodes executed; performance comparison recorded | Final experimental summary with ablation results and figures |

---

## Node Lifecycle Schema

Each experiment node tracks:

```yaml
node_id: unique_identifier
stage: preliminary | hyperparameter | research_agenda | ablation
plan: |
  Natural-language description of the experiment goal, method, and expected outcome.
code: |
  Python script implementing the experiment (training loop, logging, plotting).
execution_result:
  status: success | error
  error_message: null or captured exception
  runtime_seconds: float
metrics:
  train_loss: [...]
  val_accuracy: [...]
  # other task-specific metrics
feedback:
  llm_feedback: "Qualitative assessment of training dynamics and results."
  vlm_feedback: "Qualitative assessment of generated figures and captions."
buggy: false | true
next_action: refine | debug | select_for_next_stage | discard
```

**Lifecycle flow:**
1. **Plan**: Generate experiment description.
2. **Code/Action**: Write Python script.
3. **Execute**: Run script, capture stdout/stderr, metrics, and figures.
4. **Check Status**: If error → set `buggy: true`, `next_action: debug`. If success → set `buggy: false`, compute metrics, generate feedback, `next_action: refine` or `select_for_next_stage`.
5. **Feedback Loop**: Use LLM feedback on metrics/logs and VLM feedback on figures to guide refinement or selection.

---

## Debug/Refine Policy

- **Buggy nodes** (`buggy: true`):
  - Record the error message and traceback.
  - Attempt one automatic debugging pass: parse error, propose code fix, re-execute.
  - If debugging fails after one retry, mark node as `discard` and spawn a new sibling node with a revised plan.
  
- **Non-buggy nodes** (`buggy: false`):
  - Compute metrics and generate feedback.
  - Refine the experiment by adjusting hyperparameters, data augmentation, or model architecture based on feedback.
  - Use best-first selection: rank nodes by primary metric (e.g., validation accuracy) and LLM/VLM feedback scores.
  - Select the top-ranked node for progression to the next stage.

**Source-backed rationale:** The paper describes separate handling for buggy and non-buggy nodes, with debugging branches for errors and refinement branches for performance optimization (lines 323-354).

---

## Replication and Aggregation Plan

- **Replication**: In Stage 3 (Research Agenda Execution), run the selected experiment with 3 different random seeds (e.g., 42, 43, 44).
- **Aggregation**:
  - Collect metrics (train loss, validation accuracy) from all replications.
  - Compute mean and standard deviation across seeds for each epoch/step.
  - Generate aggregated plots showing mean curves with shaded confidence intervals.
  - Store aggregated metrics in a summary JSON file.

**Source-backed rationale:** The paper mentions specialized node types for replications with multiple seeds and aggregation of replicated results (lines 333-356).

---

## Visual Review Plan

After each non-buggy node execution:
1. Generate training curve plots (loss, accuracy vs. epoch).
2. Save plots as PNG files in an `outputs/` directory.
3. Use an LLM-based feedback mechanism to assess plot quality:
   - Check for proper axis labels, legends, and titles.
   - Assess whether training dynamics are as expected (e.g., convergence, overfitting).
4. If a VLM tool is available, invoke it to review figure clarity and caption accuracy.
5. Record feedback in the node's `vlm_feedback` field.
6. Use feedback to decide whether to refine the experiment or accept the node.

**Source-backed rationale:** The paper adds a VLM-based review loop for improving figure, caption, and text quality (lines 49-58, 244-356).

---

## Limitations

1. **No access to full LLM-based idea generation or literature search**: The local Codex environment does not have live access to literature databases or external LLM APIs for novelty checking. Idea generation will be simplified and illustrative rather than research-grade.
2. **No multi-agent parallelization**: The paper describes parallelized agentic tree search; this demo will execute nodes sequentially due to local resource constraints.
3. **No manuscript generation**: The paper's full workflow includes writing complete scientific manuscripts. This demo stops at experimental execution and visual review.
4. **Toy task scope**: The experiment will use a simple, fast-training task (e.g., MNIST classification with a small neural network) to enable rapid iteration within context and time budgets.
5. **No external submission or human review**: The paper validated the system by submitting to a workshop. This demo cannot replicate that validation step.

**Source-backed rationale:** The paper's failure cases note that the system does not consistently reach workshop-level quality and is not yet at top-tier standards (lines 694-708). This demo inherits those limitations and adds harness-specific constraints.

---

## Ethics and Disclosure

- **Source-backed ethical handling**: The original paper required IRB approval, reviewer disclosure, organizer coordination, and withdrawal of the accepted AI-generated paper before publication (lines 457-466, 714-721).
- **Local ethics**: This demo generates code and experiments for illustrative purposes only. No manuscripts will be submitted to conferences or journals. If this workflow were extended to generate scientific work for public dissemination, it must include:
  - Clear disclosure that the work was AI-generated.
  - Human expert review for accuracy, rigor, and ethical compliance.
  - Verification that generated citations are correct and not fabricated.
  - Compliance with target venue policies on AI-generated submissions.

---

## Transfer-Adaptation Note

**What changed for the Codex harness:**

1. **Removed literature-search dependency**: The paper assumes access to tools for checking novelty and identifying prior work (lines 187-204). The Codex environment does not have live literature-search tools, so idea generation will be simplified and based on common machine-learning tasks rather than cutting-edge research directions.

2. **Simplified experiment scope**: The paper describes experiments across multiple machine-learning domains with complex training pipelines. This demo uses a single, fast-training task (MNIST classification) to enable execution within the Codex context and time budget.

3. **Sequential execution instead of parallelized tree search**: The paper's agentic tree search runs nodes in parallel (lines 244-356). This demo executes nodes sequentially due to local resource constraints.

4. **Manual VLM simulation**: The paper uses a VLM-based review loop for figures and captions. If a VLM tool is unavailable in the Codex environment, the demo will simulate visual review using LLM-based heuristics (e.g., checking plot properties programmatically).

5. **No manuscript generation**: The paper's workflow concludes with writing complete manuscripts. This demo stops at experimental execution, metrics aggregation, and visual review, producing a structured experimental log instead of a full manuscript.

6. **No external submission or validation**: The paper validated the system by submitting AI-generated manuscripts to a workshop. This demo cannot replicate that validation step and instead focuses on verifying the workflow mechanics locally.

**Preserved source-backed elements:**
- Generalized idea generation (even if simplified).
- Four-stage experiment manager with stage-specific stopping criteria.
- Node lifecycle schema with plan, code, execution, metrics, feedback, and status.
- Debug/refine branching policy.
- Replication with multiple seeds and aggregation of metrics.
- Visual review plan (LLM-based or VLM-based).
- Ethical disclosure principles adapted for local use.

---

## Next Steps

If you confirm this plan, I will:
1. Create a project directory structure (`experiments/`, `outputs/`, `logs/`).
2. Implement a simple MNIST classification baseline as the preliminary investigation node.
3. Execute the four-stage workflow, generating code, running experiments, collecting metrics, and producing plots.
4. Record the full node lifecycle for each experiment in structured logs.
5. Produce a final summary report with aggregated metrics, ablation comparisons, and visual review feedback.

Confirm to proceed, or request modifications to the plan.
