# Section 01 Report: F/S/B Paper-Task Effects

## Scope and verification

- Input snapshot SHA-256:
  `ceb2c4f81c5f5dcaef697a7a40c6f9bfecd264f52cfa959190bcb8b9169aa85c1`.
- The input contains exactly 1,296 unique terminal rows indexed `1..1296`, with
  383 operational successes.
- The primary filter selects exactly 432 rows: 144 each for B, F, and S.
- The design contains 12 papers, 24 nested tasks, four equally weighted domains,
  and six paired blocks per task.
- The independent unit is the paper. Bootstrap sampling is stratified by domain,
  uses 10,000 replicates, and reinitializes Python `random.Random` with seed
  `20260721` for each summary.
- `verify_primary_effects.py` verifies all output hashes, row counts, design
  invariants, point estimates, and interval endpoints.

## Main results

| Contrast | Endpoint | Effect | 95% sensitivity interval |
|---|---|---:|---:|
| F - B | Operational success | +0.1944 | [0.0903, 0.2986] |
| F - B | Private score | +0.1577 | [0.0477, 0.2781] |
| S - B | Operational success | +0.2431 | [0.1042, 0.3889] |
| S - B | Private score | +0.2170 | [0.0922, 0.3558] |
| S - F | Operational success | +0.0486 | [-0.0208, 0.1181] |
| S - F | Private score | +0.0594 | [0.0000, 0.1215] |

These intervals describe sensitivity across the registered benchmark papers; they
are not population confidence intervals.

## Claim boundary

The primary data support that F and S outperform B on both operational success
and private score. They do not support a reliable S-over-F operational-success
claim because that interval crosses zero. The score endpoint is boundary-level
at zero and should not be presented as strong evidence that S dominates F.
