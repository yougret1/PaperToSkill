# PaperToSkill Live Transfer Plan: AI Scientist-v2 Adaptation

## Run Objective

Implement a local, lightweight version of AI Scientist-v2 that generates a research idea, executes a four-stage experimental workflow with tree-search exploration, produces visualizations with VLM-assisted review, and documents results in a structured report. The system will preserve the core abstractions (idea generation, experiment manager, node lifecycle, debug/refine branching, replication, visual review) while adapting to available local tools and manual review gates.

---

## Four-Stage Experiment Plan

| Stage | Purpose | Key Activities | Success Criteria | Fallback |
|-------|---------|----------------|------------------|----------|
| **1. Preliminary Investigation** | Validate idea feasibility and establish baseline | - Load/prepare dataset<br>- Run baseline model<br>- Confirm metrics pipeline<br>- Document runtime constraints | Baseline metrics recorded, no blocking errors | Manual data inspection if automated load fails |
| **2. Hyperparameter Tuning** | Identify promising configuration space | - Define sweep grid<br>- Run parameter search (tree or grid)<br>- Log performance per config<br>- Select top-k configs | Performance improvement over baseline, configs ranked by validation metric | Use default hyperparameters from literature if search infeasible |
| **3. Research Agenda Execution** | Test core hypothesis with selected configs | - Implement proposed method<br>- Run experiments with replication (3+ seeds)<br>- Compare against baseline<br>- Generate plots and tables | Statistical significance test passed, results reproducible across seeds | Report partial results with disclosed limitations if full replication fails |
| **4. Ablation Studies** | Isolate contribution of each component | - Disable method components individually<br>- Re-run experiments<br>- Measure delta from full method<br>- Visualize component importance | Ablation table complete, clear attribution of gains | Skip ablations if time-constrained, document as limitation |

---

## Node Lifecycle Schema

Each experimental node tracks:

```
Node:
  id: unique identifier
  parent_id: reference to parent node (null for root)
  plan: prose description of what this node will test
  code_or_action: executable script path or command string
  execution_result: stdout/stderr capture or structured log
  error: exception trace if node failed
  metrics: dict of recorded performance measures (accuracy, loss, time, etc.)
  feedback: analysis of result (human or agent-generated)
  status: [planned, running, success, error, abandoned]
  next_action: [refine_code, tune_hyperparameters, branch_alternative, promote_to_report, none]
```

**Lifecycle Flow:**
1. **Plan** → generate hypothesis and experimental design
2. **Code/Action** → write script or command to test hypothesis
3. **Execute** → run code, capture result and metrics
4. **Feedback** → analyze result, decide next action
5. **Branch or Promote** → create child nodes for refinement, or mark complete

---

## Debug/Refine Policy

### For Nodes with Errors (status = error)
- **First failure:** analyze stack trace, check for missing dependencies, file path errors, or syntax issues. Apply targeted fix and retry (max 2 refinement attempts).
- **Second failure:** escalate to human review. Log error and proposed fix for manual inspection.
- **Persistent failure:** mark node as abandoned, document limitation, proceed with alternative branch if available.

### For Nodes without Errors but Poor Metrics
- **Metric below threshold:** create child node with modified hyperparameters or architectural change.
- **No improvement after 3 branches:** accept best result, document as negative finding, move to next stage.

### Buggy vs. Non-Buggy Node Treatment
- **Buggy nodes** block forward progress until resolved or abandoned.
- **Non-buggy low-performing nodes** contribute to exploration but do not block stage advancement.

---

## Replication and Aggregation Plan

**Replication Protocol:**
- Run each final experiment configuration with **3 random seeds** (minimum).
- Record per-seed metrics in structured format (JSON or CSV).
- Compute mean, standard deviation, and confidence intervals (95%) for primary metrics.

**Aggregation:**
- Generate summary table with mean ± std for each method.
- Flag results where std > 10% of mean as high-variance.
- Include seed-level plots in appendix for transparency.

**Seeds Used:** `[42, 123, 999]` (or user-specified)

---

## Visual Review Plan

**Figure Generation:**
1. Auto-generate plots for:
   - Training curves (loss vs. epoch)
   - Validation performance vs. hyperparameter
   - Ablation bar charts
   - Comparison tables (baseline vs. proposed)

2. **VLM-Assisted Review (if available):**
   - Pass rendered figure + caption to vision-language model
   - Request: "Does this figure clearly support the claim in the caption? Suggest improvements."
   - Iterate on axis labels, legends, color schemes based on feedback

3. **Manual Review Gate:**
   - Present figures to user before final report compilation
   - User confirms figure quality or requests revision

**Fallback:** If VLM unavailable, use matplotlib default settings and manual review only.

---

## Limitations (Source-Backed)

From the AI Scientist-v2 evaluation:

1. **Hallucinated Citations:** Generated papers may reference non-existent works. Mitigation: manually verify all citations before publication.

2. **Insufficient Experimental Rigor:** Some generated experiments lack statistical power or proper controls. Mitigation: enforce replication protocol and significance testing.

3. **Template Dependence Reduced but Not Eliminated:** While tree search reduces reliance on templates, some domain-specific structure is still needed.

4. **Quality Gap vs. Top-Tier Venues:** Generated papers received workshop-level scores, not top conference acceptance. This system targets feasibility demonstration, not publication-ready output.

---

## Limitations (Harness-Specific)

1. **No Automated Paper Writing:** This plan focuses on experimental execution. Manuscript generation (LaTeX compilation, bibliography management) requires separate tooling or manual drafting.

2. **Limited Tool Access:** 
   - No specialized ML frameworks assumed (user must provide environment)
   - No cloud compute budget (execution constrained to local resources)
   - No automated code review (human review required for generated scripts)

3. **Manual Review Gates:** Visual review and error escalation require human intervention, breaking full autonomy.

4. **Simplified Tree Search:** Full beam search with branching factor > 3 may exceed context budget. Plan uses depth-limited exploration (max depth = 2).

---

## Ethics and Disclosure

**From Source:**
- AI-generated papers must be clearly disclosed as AI-generated
- Community norms for AI-generated science are still emerging
- Risk of low-quality paper proliferation if not responsibly deployed

**For This Harness:**
- Any report generated by this plan must include "Generated with AI assistance" disclaimer
- User is responsible for verifying correctness before external sharing
- This system is a research tool, not a production publication pipeline

---

## Transfer Adaptation Note

**Changes for Claude Project Prompt Harness:**

1. **Execution Model:** Original AI Scientist-v2 assumes full autonomy with paper submission. This plan introduces manual review gates at:
   - Code generation (user confirms script before execution)
   - Visual review (user approves figures)
   - Error escalation (user resolves persistent bugs)

2. **Tool Availability:** Original assumes access to specialized ML frameworks, LaTeX compilers, and citation databases. This plan treats those as optional and documents workarounds.

3. **Context Budget:** Original may use multiple long-running agent sessions. This plan front-loads the four-stage structure and node lifecycle schema to fit within a single context window, with compaction-aware checkpointing.

4. **No Invented Results:** Unlike a live AI Scientist-v2 run, this plan does not claim experimental success unless actual code is executed and metrics are recorded. All example metrics must be marked as "placeholder pending actual run."

5. **Transparency Over Automation:** The original emphasizes end-to-end automation. This plan prioritizes transparency, reproducibility, and human oversight, reflecting the harness's support-agent role rather than fully autonomous scientist role.

---

**Ready to execute this plan. Awaiting user direction on:**
- Research idea/domain to explore
- Dataset and baseline model
- Available compute resources and time budget
