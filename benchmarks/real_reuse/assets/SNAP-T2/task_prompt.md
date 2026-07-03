# SNAP-T2 Locked SnapATAC2 Task Prompt

Objective: Produce dimensionality reduction plus clustering/marker artifacts and objective quality/resource metrics for the declared dataset.

Metric: ari_nmi_runtime_memory

Return one JSON object only. Required top-level fields:

completed, method_steps, clustering_artifacts, quality_metrics, runtime_seconds, peak_memory_mb

Include `predicted_labels` only if the task asks for clustering labels. Do not
claim a completed run unless the output records concrete artifacts and runtime
or memory logs.
