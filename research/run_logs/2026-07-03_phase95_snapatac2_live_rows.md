# Phase 95: SnapATAC2 Live Real-Reuse Rows

Date: 2026-07-03

## Objective

Move the prepared SnapATAC2 real-reuse tasks from fixture-readiness to scored
raw-row evidence, while preserving the boundary that miniature fixture dry
scoring is not a full SnapATAC2 paper reproduction.

## Actions

- Retried the Phase 94 remote save with `git push origin main`; GitHub HTTPS
  access failed because port 443 was unreachable. The Phase 94 local commit
  remains intact.
- Parsed the local GPT API document without printing or committing secrets.
- Ran `scripts/run_real_reuse_snapatac2.py` for SNAP-T1 and SNAP-T2 under both
  `summary` and `papertoskill` conditions with GPT-family `gpt-5.5`.
- Regenerated `results/real_reuse/main_results_plan.{csv,md,json}` from
  `results/real_reuse/raw_rows.jsonl`.
- Updated the AAAI real-reuse table and results narrative to include the SNAP
  scores as failed rows, not positive downstream-effectiveness evidence.

## Command

```powershell
python scripts\run_real_reuse_snapatac2.py `
  --task SNAP-T1 --task SNAP-T2 `
  --condition summary --condition papertoskill `
  --model-family GPT-family `
  --model-alias gpt-5.5 `
  --wire-api openai_responses `
  --max-tokens 1800 `
  --timeout-seconds 120 `
  --max-attempts 2 `
  --retry-delay-seconds 2 `
  --run-id phase95_snapatac2_gpt55_live
```

Credentials were loaded from the local API document into process-local
environment variables only, then removed after the command.

## Results

- `results/real_reuse/snapatac2_run_report.md` reports `complete`.
- Four SNAP raw rows were appended to `results/real_reuse/raw_rows.jsonl`.
- SNAP-T1 Summary scored `0.000` and failed because the candidate output was
  not a single parseable JSON object.
- SNAP-T1 PaperToSkill scored `0.500` and failed because completed runtime and
  memory artifacts were missing.
- SNAP-T2 Summary scored `0.200` and failed because required artifacts and
  metrics were incomplete.
- SNAP-T2 PaperToSkill scored `0.400` and failed because completed runtime,
  memory, and quality artifacts were missing.

## Evidence Boundary

- This is real GPT-family execution and deterministic local scoring over
  prepared official miniature SnapATAC2 fixtures.
- It is not a full pbmc5k or pbmc10k_multiome reproduction and does not prove
  SnapATAC2 paper-level performance.
- The SNAP rows are failure-boundary evidence: PaperToSkill scored higher than
  Summary in this dry scorer, but every SNAP row remained below the
  pre-registered success threshold.
- The full eight-task real-reuse benchmark remains incomplete because AIDE and
  SWE-agent rows are still pending.

