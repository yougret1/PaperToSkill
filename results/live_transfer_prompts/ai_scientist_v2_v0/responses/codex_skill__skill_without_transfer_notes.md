# PaperToSkill Codex Agent Run Plan

## Run Objective

Execute a local coding experiment inspired by AI Scientist-v2 workflow: generate a research idea for improving a simple ML baseline, design and run experiments across four stages (preliminary investigation, hyperparameter tuning, research agenda execution, ablation studies), manage node lifecycle with debug/refine branching, replicate with multiple seeds, aggregate results, generate and review visualizations, and produce a structured report with limitations and ethics notes.

---

## Four-Stage Experiment Manager

| Stage | Objective | Stop Condition | Output |
|-------|-----------|----------------|--------|
| **Preliminary Investigation** | Validate the baseline can run; collect initial metrics on a toy dataset | First non-buggy node with complete metrics | Selected baseline node |
| **Hyperparameter Tuning** | Explore 2-3 hyperparameter variants (e.g., learning rate, batch size) | Best-performing node by validation metric | Tuned hyperparameter config |
| **Research Agenda Execution** | Implement the generated idea (e.g., add regularization, change architecture) | At least one non-buggy experimental variant that improves or matches baseline | Experimental variant node |
| **Ablation Studies** | Run 3 replications with different random seeds; aggregate metrics | All replications complete with aggregated mean/std | Aggregated result table |

---

## Node Lifecycle Schema

Each experiment node contains:

```
{
  "node_id": "string",
  "plan": "brief description of what this node tests",
  "code_or_action": "path to generated Python script or command",
  "execution_result": "stdout/stderr or error trace",
  "metrics": {
    "train_loss": float,
    "val_loss": float,
    "val_accuracy": float,
    "runtime_seconds": float
  },
  "feedback": "LLM-generated assessment of results",
  "status": "buggy | non-buggy",
  "next_action": "debug | refine | select_for_next_stage | replicate"
}
```

---

## Debug/Refine Policy

- **Buggy nodes**: Record error trace in `execution_result`, set `status: "buggy"`, generate debugging fix in new child node, retry execution.
- **Non-buggy nodes**: Record metrics, generate feedback comparing to parent or baseline, set `status: "non-buggy"`, optionally refine (e.g., increase epochs, adjust learning rate) in child node.
- **Selection**: Use best-first strategy guided by `val_accuracy` (primary) and `train_loss` convergence (secondary).

---

## Replication and Aggregation Plan

1. After selecting the best node from Research Agenda Execution stage, create 3 replication child nodes with seeds `{42, 43, 44}`.
2. Run each replication independently and collect `val_accuracy` and `val_loss`.
3. Aggregate: compute mean and standard deviation for each metric.
4. Store aggregated results in a summary table:

```
| Seed | Val Accuracy | Val Loss |
|------|--------------|----------|
| 42   | 0.xx         | x.xx     |
| 43   | 0.xx         | x.xx     |
| 44   | 0.xx         | x.xx     |
| Mean | 0.xx         | x.xx     |
| Std  | 0.xx         | x.xx     |
```

---

## Visual Review Plan

1. Generate training curves (loss and accuracy vs. epoch) for baseline and experimental variant.
2. Save figures as PNG files in `outputs/figures/`.
3. Use simple matplotlib-based visual inspection (no VLM available in local Codex harness).
4. Record figure paths and brief caption in node metadata.
5. Human review: check for convergence, overfitting, or unexpected trends before finalizing report.

---

## Limitations (Source-Backed + Harness-Specific)

### Source-Backed Limitations
- Workshop-level acceptance, not top-tier conference standards (source: lines 694-704).
- System does not consistently reach workshop-level quality; only 1 of 3 AI-generated submissions accepted (source: lines 696-704).
- Challenges remain in producing genuinely novel hypotheses, innovative experiments, and rigorous justification with deep domain expertise (source: lines 704-708).
- Citation inaccuracies and insufficient methodological rigor observed in generated manuscripts (source: lines 448-452).

### Harness-Specific Limitations
- No literature-search tool available in this Codex harness; novelty checking is skipped.
- No VLM available; visual review is manual inspection of matplotlib figures.
- Limited compute: experiments run locally on CPU or single GPU; no parallelized tree search.
- Node selection is greedy best-first; no full tree exploration budget.
- Experiment scope is toy-scale (small dataset, short training) to fit local runtime constraints.

---

## Ethics and Disclosure (Source-Backed)

- The AI Scientist-v2 workshop experiment required IRB approval, reviewer disclosure, organizer coordination, and withdrawal of the accepted AI-generated paper before publication (source: lines 457-466, 714-721).
- For this local Codex run:
  - No human subjects or external publication.
  - Results are for internal research only.
  - If results are shared externally, disclose that the workflow was AI-assisted and inspired by AI Scientist-v2.
  - Do not claim human-level scientific discovery; label outputs as automated exploration.

---

## Transfer-Adaptation Note

**What changed for the target harness:**

1. **Removed template dependency**: The source paper removes human-authored code templates. In this Codex harness, I will generate baseline code from scratch using a simple ML task (e.g., MNIST classification with a small CNN).
2. **No literature search**: The source uses literature-search tools to check novelty. The Codex harness does not have external search tools, so I skip novelty checking and focus on a known baseline improvement idea (e.g., add dropout or batch normalization).
3. **No VLM-based review**: The source uses VLM feedback for figures and captions. The Codex harness does not have VLM access, so visual review is manual matplotlib inspection.
4. **Single-threaded tree search**: The source runs parallelized agentic tree search. The Codex harness runs experiments sequentially due to local compute constraints.
5. **Toy-scale experiments**: The source targets workshop submissions. This Codex run targets a small local proof-of-concept with short training (5-10 epochs) on a subset of MNIST to fit runtime budgets.
6. **Preserved four-stage structure**: Preliminary investigation, hyperparameter tuning, research agenda execution, and ablation studies are retained as specified in the source (lines 211-244).
7. **Preserved node lifecycle and debug/refine policy**: Node schema and branching logic (buggy vs. non-buggy) are adapted from source (lines 244-356).

---

## Next Steps for Execution

1. Generate baseline MNIST classifier code (stage 1: preliminary investigation).
2. Run baseline, collect metrics, confirm non-buggy status.
3. Generate hyperparameter tuning variants (stage 2).
4. Implement research idea (e.g., add dropout) and run experimental variant (stage 3).
5. Replicate best node with 3 seeds, aggregate results (stage 4).
6. Generate training curves, save figures.
7. Produce structured report with all node metadata, aggregated metrics, and limitations.

**Ready to proceed with stage 1: preliminary investigation.**
