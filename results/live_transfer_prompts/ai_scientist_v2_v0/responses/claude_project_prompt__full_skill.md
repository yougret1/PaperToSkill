# PaperToSkill Experiment Plan: AI Scientist-v2 Local Agent Run

## Run Objective

Execute a simplified AI Scientist-v2 workflow on a small machine-learning research task, demonstrating generalized idea generation, four-stage experiment management, agentic tree search with node lifecycle tracking, debug/refine branching, replication with aggregation, and visual review. The goal is to produce an experimental artifact (code, metrics, figures) and a brief research note, not a full manuscript.

---

## Four-Stage Experiment Manager

| Stage | Purpose | Stopping Criteria | Input | Output |
|-------|---------|-------------------|-------|--------|
| **1. Preliminary Investigation** | Explore initial research direction; validate task feasibility; establish baseline metrics | First non-buggy node with valid metrics OR 5 total nodes attempted | High-level idea prompt, available dataset/task description | Best preliminary node (plan, code, metrics, figures) |
| **2. Hyperparameter Tuning** | Search hyperparameter space to improve baseline performance | Best validation metric plateaus over 3 nodes OR 8 nodes attempted | Best node from stage 1 | Best tuned node with improved metrics |
| **3. Research Agenda Execution** | Implement core experimental hypothesis; test main research question | Main hypothesis tested with at least 2 variants OR 10 nodes attempted | Best node from stage 2, research hypothesis from idea | Best research node demonstrating hypothesis outcome |
| **4. Ablation Studies** | Isolate contribution of key components; validate design choices | All planned ablations complete OR 6 nodes attempted | Best node from stage 3, ablation plan | Ablation summary with component-wise metrics |

**Total node budget**: ~29 nodes across all stages (adjustable based on runtime constraints)

---

## Node Lifecycle Schema

Each node in the tree search contains:

```
Node {
  node_id: unique identifier
  stage: 1-4 (preliminary, tuning, research, ablation)
  parent_node_id: reference to parent node or null
  
  plan: text description of experiment intent
  code: generated Python experiment script
  
  execution_result: stdout/stderr trace OR error message
  runtime_seconds: wall-clock execution time
  metrics: dict of logged metrics (e.g., {"val_acc": 0.78, "train_loss": 0.45})
  
  visualization_code: Python script generating figures
  figures: list of output image paths
  
  llm_feedback: text evaluation of metrics and training dynamics
  vlm_feedback: text evaluation of figure quality and clarity (if VLM available)
  
  status: "buggy" | "non-buggy"
  next_action: "debug" | "refine" | "select_best" | "replicate"
}
```

**Node selection policy**: Best-first based on primary metric (e.g., validation accuracy), training stability (low variance), and plot quality score (VLM feedback or heuristic).

---

## Debug/Refine Policy

- **Buggy nodes** (`status == "buggy"`):
  - Record error message and traceback in `execution_result`
  - Set `next_action = "debug"`
  - Generate child node with corrected code (up to 2 debug attempts per parent)
  - If still buggy after 2 attempts, mark branch as exhausted

- **Non-buggy nodes** (`status == "non-buggy"`):
  - Record metrics and figures
  - Set `next_action = "refine"`
  - Generate child node with experiment refinement (e.g., adjusted learning rate, additional logging, improved plotting)
  - Compare child metrics to parent; if child outperforms, continue from child

**Branch exhaustion**: If a branch produces 3 consecutive buggy nodes, terminate that branch and backtrack to the next-best parent.

---

## Replication and Aggregation Plan

After selecting the best node in each stage:

1. **Replication**: Re-run the best node's code with 3 different random seeds (e.g., `random_seed=[42, 123, 456]`)
2. **Metrics aggregation**:
   - Compute mean and standard deviation for each metric across seeds
   - Example: `val_acc: 0.78 ± 0.02`, `train_loss: 0.45 ± 0.03`
3. **Figure aggregation**:
   - Generate overlay plot showing per-seed curves
   - Generate summary figure with mean curve and confidence bands
4. **Record replicated node** with aggregated metrics and combined figures

Replication is applied to the final selected node in stage 3 (research agenda) and optionally to stage 4 (ablations).

---

## Visual Review Plan

For each non-buggy node with generated figures:

1. **Heuristic checks** (always available):
   - Figure file exists and has non-zero size
   - Image dimensions are reasonable (not 1×1 or malformed)
   - File format is valid (PNG, PDF, SVG)

2. **VLM-based review** (if VLM tool available):
   - Pass figure image to VLM with prompt: "Evaluate this research figure for clarity, axis labels, legend completeness, and visual quality. Provide a quality score (1-10) and suggest improvements."
   - Record VLM feedback in `vlm_feedback` field
   - Use quality score as tie-breaker in node selection

3. **Fallback** (if VLM unavailable):
   - Use heuristic scoring: +1 for labeled axes, +1 for legend, +1 for title, +1 for readable font size
   - Record heuristic score in `vlm_feedback` as `"heuristic_score: X/4"`

**Improvement loop**: If VLM identifies missing labels or unclear captions, generate child node with improved visualization code.

---

## Limitations

1. **No human-authored code templates**: This plan assumes the agent generates experiment code from scratch. If the target task requires domain-specific boilerplate (e.g., custom CUDA kernels, proprietary APIs), the agent may need starter examples.

2. **Tool availability**:
   - Assumes Python execution environment with ML libraries (PyTorch/TensorFlow, NumPy, Matplotlib)
   - VLM-based review is optional and degrades gracefully to heuristic scoring
   - Literature search tools (for novelty checking) are not available in this harness; skip novelty validation or rely on user-provided prior work summaries

3. **Scope**: This plan targets small-scale experiments (minutes to hours per node), not large-scale distributed training. Stage budgets and node limits are calibrated for local agent runs.

4. **Acceptance threshold**: The source paper achieved workshop acceptance (6.33/10 average score) for one of three submissions. This plan does not guarantee similar outcomes and focuses on demonstrating the workflow rather than submission-ready quality.

---

## Ethics and Disclosure

- **Source-backed requirements** (from paper):
  - AI-generated research artifacts should be disclosed as AI-generated
  - Human oversight is required before any submission to peer review
  - Ethical review (IRB or equivalent) may be needed if experiments involve human data or have deployment implications
  - Citation accuracy and methodological rigor must be manually verified

- **Harness-specific adaptations**:
  - This local run does not involve peer review submission; disclosure is automatic (user knows this is an AI Scientist-v2 replication)
  - No human data is involved; experiments use public ML benchmark datasets
  - Results are for educational and validation purposes, not publication

- **Manual verification checklist**:
  - [ ] Experiment code is correct and does not contain silent failures
  - [ ] Metrics are logged correctly and match expected ranges
  - [ ] Figures are accurate and not misleading
  - [ ] Research claims (if any) are supported by logged metrics

---

## Transfer-Adaptation Note

**What changed for the Claude-style project prompt harness**:

1. **Removed dependency on workshop submission**: The source paper evaluated AI Scientist-v2 by submitting manuscripts to ICBINB. This harness replaces manuscript generation with a "research note" artifact (markdown summary of findings, figures, and metrics).

2. **Simplified idea generation**: The source paper uses literature search and novelty checking. This harness assumes the user provides a high-level research direction (e.g., "investigate learning rate schedulers for image classification") and skips automated literature search.

3. **Local execution**: The source paper does not specify execution environment details. This harness assumes local Python execution with standard ML libraries. If cluster access or distributed training is needed, the user must provide job submission tools.

4. **VLM review as optional**: The source paper includes VLM-based figure review. This harness treats VLM as optional and provides heuristic fallback scoring.

5. **Node budget calibration**: The source paper does not specify exact node counts. This harness sets stage-specific budgets (5, 8, 10, 6 nodes) to keep total runtime under a few hours for small tasks.

6. **No citation generation**: The source paper generates full manuscripts with references. This harness omits citation generation and focuses on experimental workflow.

**Source-backed claims preserved**:
- Four-stage experiment manager (source lines 211-244)
- Node lifecycle with plan, code, execution, metrics, feedback, status (source lines 244-356)
- Debug/refine branching (source lines 323-354)
- Replication and aggregation (source lines 333-356)
- VLM-based figure review (source lines 358-372)
- Workshop-level acceptance as validation (source lines 429-433)
- Limitations on novelty and rigor (source lines 704-708)

**Missing tools recorded**: Literature search, automated citation generation, workshop submission pipeline, distributed training job scheduler.
