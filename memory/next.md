# Next Actions

The accepted Stage `2` remains complete. The active work is a separate,
forward-only generalization extension required by the user.

## Immediate Gate

1. Inspect the remote executor contract diff and Git boundary.
2. Commit and push the executor contract checkpoint after anchor commit
   `b4a8605f`.
3. Do not call a provider unless this private push succeeds.

## Stage 2.3 Materialization

1. The complete materialization anchor is generated, verified, committed, and
   privately pushed.
2. The executor contract is frozen and verified; API documentation was parsed
   at runtime without persisting credential values.
3. After the executor checkpoint push, run at most one format-only preflight per
   exact alias and preserve redacted
   request/response evidence.
4. Dispatch the frozen schedule with classified retries, raw responses,
   canonical outputs, scoring artifacts, and resumable progress.

## Preservation Rules

- Keep the 858-file parent raw set, all 24 bound artifacts, and V4/V5 records
  immutable.
- Use `python -m pytest tests` from the EffectSlice attempt directory as the
  authoritative suite scope; repository-wide discovery also collects archived
  duplicate snapshots and is not a valid release signal.
- Keep paper as the independent unit and restrict FG1 inference to the purposeful,
  registered, domain-stratified benchmark.
- Report controls as exact task tables, not calibrated error rates or a confusion
  matrix.
- Keep usage, latency, and conditional cost descriptive rather than method-quality
  evidence.
- Do not mutate, supersede, or reinterpret V4/V5 preregistrations, raw outputs,
  or accepted stage reports; every new artifact lives under `forward_extensions`.
- Do not design or run local-model experiments. The remote-only successor has
  1296 remote rows and zero local rows.
