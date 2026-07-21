# Next Actions

The accepted Stage `2` remains complete. The active work is a separate,
forward-only generalization extension required by the user.

## Required Forward Work

1. Commit and push the passed forward Stage `2.6` citation package.
2. Write Stage `2.2` preregistration for 12 papers by 2 tasks, stratified across
   NLP, software engineering, data analysis, and agent/tool-use.
3. Freeze paper-selection criteria, task and atom contracts, six execution blocks
   per paper-task, B/F/S conditions, controls, retry policy, provider identities,
   SLA thresholds, and cluster-aware statistical analysis before private runs.
4. Require a fixed-seed open-model reproducibility anchor. Closed-model ablations
   use a frozen four-paper-task subset and do not replace cross-paper coverage.
5. Build and validate method diagrams from the preregistered structure; empirical
   forest, heatmap, calibration, sensitivity, Pareto, and restore/drop plots must
   wait for real forward results.

## Preservation Rules

- Keep the 858-file canonical raw set, all 24 bound artifacts, V4/V5 manifests,
  review records, and stage reports immutable.
- Use `python -m pytest tests` from the EffectSlice attempt directory as the
  authoritative suite scope; repository-wide discovery also collects archived
  duplicate snapshots and is not a valid release signal.
- Do not present the local admission result as a broad reduction, portability,
  population-rate, or human-benefit claim.
- Do not mutate, supersede, or reinterpret V4/V5 preregistrations, raw outputs,
  or accepted stage reports; every new artifact lives under `forward_extensions`.
