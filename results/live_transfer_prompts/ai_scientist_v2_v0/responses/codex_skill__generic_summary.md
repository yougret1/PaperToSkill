# PaperToSkill Codex Agent Run Plan

## Run Objective

Implement a **local tree-search experiment manager** inspired by AI Scientist-v2 that:
1. Generates research ideas (code experiments or micro-benchmarks)
2. Executes experiments across multiple nodes with automatic debug/refine branching
3. Replicates successful nodes with multiple random seeds
4. Aggregates metrics and produces visual artifacts (plots, tables)
5. Documents limitations and transfer adaptations

**Scope:** A single research question in a local repository (e.g., "Does learning rate warmup improve convergence on a toy regression task?").

---

## Four-Stage Experiment Plan

| Stage | Description | Artifacts | Success Criteria |
|-------|-------------|-----------|------------------|
| **1. Preliminary Investigation** | Generate 3–5 experiment ideas via LLM prompting; select 1–2 feasible ideas based on dependencies and runtime. | `ideas.json`, `selected_idea.md` | At least 1 idea is executable locally without external APIs or datasets >100MB. |
| **2. Hyperparameter Tuning** | Run coarse grid search or random search over 2–3 hyperparameters; branch on errors. | `hyperparam_search.py`, `tuning_results.csv` | At least 3 successful runs; best config identified. |
| **3. Research Agenda Execution** | Execute main experiment using best config; replicate 3× with different seeds; aggregate metrics (mean, std). | `experiment.py`, `results_{seed}.json`, `aggregated_metrics.csv` | All 3 replications complete; variance within acceptable range. |
| **4. Ablation Studies** | Remove or modify one component (e.g., warmup scheduler); compare to baseline. | `ablation_experiment.py`, `ablation_results.csv`, `comparison_plot.png` | Ablation runs successfully; effect size quantified. |

---

## Node Lifecycle Schema

Each experiment node follows this schema:

```json
{
  "node_id": "exp_001",
  "plan": "Train 2-layer MLP with lr=0.01, warmup_steps=100",
  "code_action": "python experiment.py --lr 0.01 --warmup 100 --seed 42",
  "execution_result": "success | error",
  "error_log": "null | <stderr output>",
  "metrics": {"final_loss": 0.032, "epochs": 50},
  "feedback": "Converged. Metrics look stable.",
  "status": "completed | needs_debug | discarded",
  "next_action": "replicate | refine_code | discard"
}
```

**Key fields:**
- **plan**: Human-readable intent
- **code_action**: Shell command or script invocation
- **execution_result**: Captured exit code + stdout/stderr
- **metrics**: Extracted from logs or output files
- **feedback**: Auto-generated or user-provided diagnosis
- **status**: Terminal or intermediate state
- **next_action**: Branch decision

---

## Debug/Refine Policy

**Source-backed principle:** AI Scientist-v2 uses tree search to explore experiment variants and recovers from bugs by generating fixes.

**Local adaptation:**

1. **Buggy nodes** (exit code ≠ 0, parse errors, missing dependencies):
   - Capture full error log
   - Generate fix candidates (up to 3 attempts):
     - Update imports or dependencies
     - Adjust config syntax
     - Add missing files
   - Create child node for each fix attempt
   - Mark original node as `needs_debug`
   - If all fixes fail after 3 attempts, mark as `discarded`

2. **Non-buggy but low-quality nodes** (e.g., loss NaN, accuracy <50%):
   - Treat as normal node
   - Use replication variance to decide if worth exploring
   - Do not auto-branch unless explicitly requested

3. **Successful nodes**:
   - Proceed to replication stage
   - Mark as `completed`

**Implementation:** `debug_refine.py` reads error logs, prompts LLM for fixes, applies patches, re-runs.

---

## Replication and Aggregation Plan

**Source-backed principle:** AI Scientist-v2 runs multiple seeds to ensure reproducibility.

**Local plan:**

1. **Replication:**
   - For each `completed` node in Stage 3, run 3 replications with seeds [42, 43, 44]
   - Store results in `results/exp_{node_id}_seed_{seed}.json`

2. **Aggregation:**
   - Compute mean and std for each metric across seeds
   - Example:
     ```csv
     node_id,metric,mean,std
     exp_001,final_loss,0.031,0.002
     exp_001,train_time_s,12.3,0.8
     ```
   - Flag high-variance metrics (std > 20% of mean) for investigation

3. **Tools:**
   - `aggregate_metrics.py` reads all `results/*.json`, computes statistics, writes CSV
   - Pandas for aggregation, NumPy for stats

---

## Visual/VLM Review Plan

**Source-backed principle:** AI Scientist-v2 uses a vision-language model to critique and improve figures.

**Local adaptation (no VLM available):**

1. **Manual visual inspection checklist:**
   - [ ] Axis labels present and readable
   - [ ] Legend distinguishes all series
   - [ ] Error bars or confidence intervals shown for multi-seed runs
   - [ ] Title or caption explains what is plotted

2. **Automated plot generation:**
   - `plot_results.py` reads `aggregated_metrics.csv`
   - Generates:
     - Line plot: training loss over epochs (with std shaded region)
     - Bar chart: final metric comparison (baseline vs ablation)
   - Saves to `figures/loss_curve.png`, `figures/ablation_comparison.png`

3. **Limitation note:**
   - No VLM available in local harness → manual review required
   - Future: integrate multimodal LLM API for caption generation

---

## Limitations (Source-Backed + Harness-Specific)

### From AI Scientist-v2 source:
- **Hallucinated citations:** Generated papers may cite non-existent references. (Not applicable to code experiments, but relevant if generating reports.)
- **Insufficient rigor:** Some experiments may lack statistical power or proper controls.
- **Ethical concerns:** Unclear norms for AI-generated scientific artifacts; requires human disclosure.

### Harness-specific additions:
- **No VLM:** Visual review is manual; cannot auto-improve figures.
- **Local compute only:** No distributed execution; long-running experiments may time out.
- **Dependency constraints:** Cannot install packages requiring system-level privileges (e.g., CUDA drivers).
- **No human scoring:** Cannot replicate AI Scientist-v2's human evaluation of generated papers.
- **No live submission:** Cannot submit to conferences/workshops; evaluation is internal only.

---

## Ethics and Disclosure

**Source-backed principles (adapted):**

1. **Transparency:** Any artifacts generated by this system must be labeled as AI-generated.
2. **Human oversight:** A human must review all experimental results before external sharing.
3. **No misrepresentation:** Do not claim AI-generated experiments as human-authored.
4. **Community norms:** Follow emerging standards for AI in research (e.g., conference policies on LLM use).

**Codex harness disclosure:**
- This plan is generated by an LLM agent (Kiro) and executed locally.
- All code, experiments, and results are artifacts of the agent's work.
- Human user supervises execution but does not manually write experimental code.

---

## Transfer-Adaptation Note

### What changed from AI Scientist-v2 source to Codex harness:

| AI Scientist-v2 (source) | Codex Harness (this plan) |
|--------------------------|---------------------------|
| Generates full LaTeX papers with references | Generates code experiments with CSV/plot artifacts |
| Uses vision-language model for figure critique | Manual visual checklist (VLM unavailable) |
| Submits papers to ICLR workshop | Internal evaluation only (no submission) |
| Uses Aider CLI for code editing | Uses Kiro file-editing tools |
| Runs on cloud infrastructure with Docker | Runs locally on user's machine |
| Template-based experiment setup (some domains) | Fully template-free; agent writes experiments from scratch |
| Tree search over experiment variants | Simplified tree search (debug/refine branching only) |
| Human reviewers score generated papers | No human scoring (metrics only) |

### What was preserved:
- Four-stage experiment flow (preliminary, tuning, execution, ablation)
- Node lifecycle schema (plan → execute → feedback → branch)
- Debug/refine branching for buggy nodes
- Multi-seed replication and aggregation
- Emphasis on limitations, ethics, and transparency

### Why these adaptations:
- **Codex harness constraints:** No external APIs, no Docker, no VLM, no conference submission infrastructure.
- **Local execution focus:** Experiments must complete in minutes, not hours.
- **Code-first artifacts:** Prioritize runnable experiments over prose generation.

---

## Execution Checklist

- [ ] Create `experiments/` directory structure
- [ ] Implement `idea_generator.py` (LLM prompt → JSON ideas)
- [ ] Implement `experiment.py` (parameterized training script)
- [ ] Implement `debug_refine.py` (error log → fix prompt → patch)
- [ ] Implement `aggregate_metrics.py` (multi-seed stats)
- [ ] Implement `plot_results.py` (matplotlib charts)
- [ ] Run Stages 1–4 sequentially
- [ ] Review figures manually against checklist
- [ ] Document limitations in `LIMITATIONS.md`
- [ ] Archive all artifacts in `results/` for reproducibility

---

**End of PaperToSkill Live Transfer Output**
