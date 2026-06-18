# PaperToSkill Live Transfer: AI Scientist-v2 Run Plan

## Run Objective

Execute a **local, single-idea proof-of-concept** that demonstrates the AI Scientist-v2 workflow: generalized idea generation, four-stage experiment management, agentic tree search with node lifecycle tracking, debug/refine branching, replication with aggregation, and visual review. The run will target a **small-scale ML task** (e.g., MNIST classification variant, synthetic regression, or toy RL environment) to validate the workflow structure within available compute and tool constraints.

---

## Four-Stage Experiment Manager

| Stage | Purpose | Stopping Criteria | Output |
|-------|---------|-------------------|--------|
| **1. Preliminary Investigation** | Validate the idea with a minimal working experiment. Test data loading, model instantiation, and training loop. | First non-buggy node with training convergence OR 5 node attempts | Best preliminary node passed to stage 2 |
| **2. Hyperparameter Tuning** | Search learning rate, batch size, architecture width/depth. Use grid or random search within budget. | 3 non-buggy nodes with stable metrics OR 10 node attempts | Best tuned configuration passed to stage 3 |
| **3. Research Agenda Execution** | Run the core experimental variants (e.g., baseline vs. proposed method, ablations of key components). | 2 complete runs per variant with convergence OR 15 node attempts | Best experimental node passed to stage 4 |
| **4. Ablation Studies** | Isolate individual components (e.g., remove regularization, change optimizer, drop augmentation). | 1 ablation per key component with 2 seeds OR 10 node attempts | Final aggregated results and figures |

---

## Node Lifecycle Schema

Each node tracks:

```yaml
node_id: str
parent_id: Optional[str]
stage: str  # prelim | tuning | agenda | ablation
status: str  # planned | running | buggy | non_buggy | selected | pruned

plan:
  hypothesis: str
  experiment_description: str
  expected_outcome: str

code:
  script_path: str
  generated_code: str

execution:
  stdout: str
  stderr: str
  runtime_seconds: float
  exit_code: int

metrics:
  train_loss: List[float]
  val_loss: Optional[List[float]]
  final_metric: Optional[float]  # e.g., accuracy, MSE
  
feedback:
  llm_assessment: str
  suggested_next_action: str

visualization:
  plot_code: str
  figure_paths: List[str]
  vlm_feedback: Optional[str]

next_action: str  # debug | refine | replicate | aggregate | select_for_next_stage
```

---

## Debug/Refine Policy

### Buggy Nodes
- **Trigger**: Non-zero exit code, exception in stderr, or empty metrics.
- **Action**: Extract error message, generate debugging hypothesis, modify code, retry up to 2 times per node.
- **Escalation**: If still buggy after 2 retries, mark as `pruned` and create sibling node with alternative approach.

### Non-Buggy Nodes
- **Trigger**: Successful execution with parseable metrics.
- **Action**: Analyze training dynamics (loss curves, convergence speed). Generate refinement hypothesis (adjust hyperparameter, add regularization, change architecture component).
- **Expansion**: Create child node with refined experiment. Parent remains `selected` if it advances to next stage.

---

## Replication and Aggregation Plan

### Replication
- For each selected experiment in stages 3-4, run **3 replications** with random seeds `[42, 123, 456]`.
- Track per-seed metrics in separate node entries linked to parent experiment node.

### Aggregation
- Compute **mean ± std** for final metrics across seeds.
- Generate aggregated loss curves with shaded confidence intervals.
- Record statistical significance checks (t-test or Wilcoxon) when comparing baseline vs. proposed method.
- Create summary table: `| Method | Mean Acc | Std | Runtime |`

---

## Visual Review Plan

### Figure Generation
For each non-buggy node, generate:
1. **Training curves**: train/val loss over epochs.
2. **Comparison plots**: baseline vs. proposed across seeds.
3. **Ablation bar charts**: final metric per ablated component.

### VLM Review (Simulated)
Since full VLM integration may be unavailable:
- **Fallback**: Use rule-based caption checks:
  - Axis labels present?
  - Legend readable?
  - Title matches experiment?
- **Manual review step**: Present figures to user with prompt: "Do these figures clearly support the claims? Any caption improvements needed?"
- **Iteration**: If user flags issues, regenerate plot code with fixes.

---

## Limitations

### From Source Paper
- Workshop-level acceptance (1/3 submissions), not top-tier conference standard.
- Citation inaccuracies and insufficient methodological rigor observed in generated manuscripts.
- System does not consistently produce genuinely novel, high-impact hypotheses or deep domain-justified experiments.

### Harness-Specific Limitations
- **No GPU cluster**: Restricted to local compute; cannot run large-scale experiments (e.g., ImageNet, multi-day training).
- **No literature search API**: Idea novelty checks must be manual or omitted.
- **No automated manuscript writing**: This run focuses on experiment execution and result aggregation, not paper generation.
- **Limited parallelization**: Tree search runs sequentially due to single-agent constraint; cannot spawn parallel node evaluations.
- **No IRB or venue submission**: This is a local proof-of-concept, not a submitted manuscript.

---

## Ethics and Disclosure

### From Source Paper
- Authors obtained IRB approval, disclosed AI generation to workshop organizers and reviewers, and withdrew the accepted paper before publication.
- Ethical handling required transparency about AI authorship and coordination with venue organizers.

### Harness Adaptation
- This run is a **local demonstration** with no external submission or human deception.
- If results are shared publicly, disclose that experiments were designed and executed by an AI agent following the AI Scientist-v2 workflow.
- Do not claim human-level scientific insight or novelty without manual expert review.
- Flag any generated code that could be unsafe (e.g., file deletion, network requests) before execution.

---

## Transfer Adaptation Note

### What Changed for Claude Project Prompt Harness

1. **Removed manuscript generation**: The source paper includes automated LaTeX writing and citation generation. This run focuses only on experiment execution and result collection, as manuscript generation requires unavailable tools (BibTeX integration, template management).

2. **Sequential node execution**: The paper describes parallelized tree search across multiple nodes. This harness runs nodes sequentially due to single-agent limitations, using best-first selection to prioritize high-quality branches.

3. **Manual VLM review fallback**: Full VLM-based figure feedback may be unavailable. The plan includes rule-based checks and user review prompts as a substitute.

4. **No literature search**: Idea novelty validation via API calls to paper databases is not available. Novelty assessment is either manual or skipped.

5. **Small-scale task constraint**: The paper evaluates on research-grade ML problems. This run targets toy tasks (MNIST, synthetic data) to fit local compute and time budgets.

6. **Explicit user confirmation for destructive actions**: The harness safety guardrails require user confirmation before file deletion, bulk operations, or long-running processes. The paper assumes autonomous execution with post-hoc review.

### What Was Preserved

- **Four-stage structure**: Preliminary → Tuning → Agenda → Ablation with defined stopping criteria.
- **Node lifecycle schema**: Plan, code, execution, metrics, feedback, visualization, status.
- **Debug/refine branching**: Buggy nodes trigger error-based debugging; non-buggy nodes spawn refinement children.
- **Replication with seeds**: Multiple runs per experiment with aggregated statistics.
- **Visual review loop**: Generate figures, collect feedback, iterate.
- **Ethical disclosure**: Transparency about AI authorship and limitations.

---

## Next Steps

1. **User confirms task scope**: Choose a small ML problem (e.g., "Compare SGD vs. Adam on MNIST with 2-layer MLP").
2. **Idea generation**: Produce 3 candidate hypotheses, select 1 for execution.
3. **Stage 1 run**: Write and execute preliminary experiment, validate data pipeline and training loop.
4. **Iterate through stages 2-4**: Track nodes, generate figures, replicate best configuration.
5. **Present results**: Summary table, aggregated plots, limitations, and code artifacts for user review.

**Ready to proceed with a specific task, or would you like me to propose a default small-scale experiment?**
