# SNAP-T1 Locked SnapATAC2 Task Prompt

Objective: Produce a runnable analysis plan and machine-readable embedding artifact record for the declared small single-cell dataset.

Metric: runtime_memory_quality

Return one JSON object only. Required top-level fields:

completed, method_steps, embedding_artifacts, runtime_seconds, peak_memory_mb

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.
