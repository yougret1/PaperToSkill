# Controls-v2 and Full-Grid Repetitions Checklist

Date: 2026-07-25

This is the only active checklist for this forward-only phase. It contains
exactly four experiments: Controls-v2, FG6, FG7, and FG8. Earlier FG3-FG5
artifacts and completed forward analyses are immutable inputs. The unrelated
`forward_analysis_2026-07-25/s08/` directory is outside this scope.

An item is complete only when its frozen registration, terminal results,
analysis, verification, chronological log, Git commit, and private push all
succeed. Unfavorable semantic results remain in the registered denominator.

## Shared Pre-call Gate

- [x] Audit all 1,296 rows of the frozen final-protocol grid and reusable
      execution code.
- [x] Audit the old controls and define machine-verifiable successor labels.
- [x] Freeze provider routes, model aliases, decoding, exact-output envelope,
      private scoring, terminal outcomes, and transport-only retry policy.
- [x] Freeze identical logical inputs for FG6, FG7, and FG8.
- [x] Freeze a globally interleaved schedule so repetition ID is not
      confounded with provider time.
- [x] Verify all registrations and write a no-call verification record.
- [x] Commit and privately push the complete pre-call freeze.
- [x] Freeze a forward terminal-row successor after the first live-run writer
      rejected extension metadata. Keep result rows on the original strict
      schema and store repeat/control bindings in hash-bound sidecars.
- [x] Require exactly 1,296 unique terminal rows in each of FG6, FG7, and FG8.
      Locally recovered rows remain part of that count; transport attempts do
      not add or remove semantic rows.
- [x] Treat transient network and retryable HTTP states as transport retries,
      not final experimental outcomes. Continue with the same execution ID and
      idempotency key until a non-network terminal result is available.
- [x] Freeze terminal-row successor v2 after the first successor's patched
      writer recursed through the patched symbol. Bind the additional 10
      Controls-v2 and 10 FG6 nonterminal rows, and call the captured unpatched
      base writer exactly once for every strict terminal row.

## Experiments

1. [x] Controls-v2
   - Deterministic label layer: zero provider calls.
   - Model-mediated layer: 4 domain anchors x 2 registries x 4 arms x 3
     independent repetitions = 96 registered calls.
   - Required machine binding:
     `mutation_id -> atom IDs -> contract ID -> private case IDs -> scorer key`.
   - Report deterministic confusion results separately from model-mediated
     retention, localization, and repeatability.
   - Completed with exactly 96 unique terminal result rows, 96 metadata
     sidecars, and 96 terminal markers; all 96 rows are valid.
   - Terminal outcomes: 23 operational successes, 71 hard-contract failures,
     and 2 malformed/no-submission results.
   - Deterministic layer: all 40 registered cells passed (24 Admit, 8 Reject,
     and 8 Invalid). The exact-contract-removal negative matched its registered
     direction in 24/24 rows and produced 0/24 operational successes.
   - Completion verification passed and confirmed that no retryable transport
     state was persisted as a terminal experimental result.

2. [x] FG6 full-grid independent exact-protocol repetition
   - 1,296 registered calls across all frozen execution families and model
     slots.
   - Execution, completion verification, single-repeat analysis, scoped
     artifact-safety audit, and private Git backup passed. Evidence commit:
     `ac6228a5`.
   - Exact terminal outcomes: 388 operational successes, 668 hard-contract
     failures, 160 integrity/digest failures, and 80 malformed/no-submission
     results.
   - The 24 primary paper-task decisions contain 3 Admit and 21 Reject states.
     Mean effects are F-B 0.263346, S-B 0.311198, and S-F 0.047852.

3. [ ] FG7 full-grid independent exact-protocol repetition
   - 1,296 registered calls across all frozen execution families and model
     slots.
   - Execution, completion verification, single-repeat analysis, and scoped
     artifact-safety audit passed; private Git backup is pending.
   - Exact terminal outcomes: 365 operational successes, 681 hard-contract
     failures, 160 integrity/digest failures, and 90 malformed/no-submission
     results.
   - The 24 primary paper-task decisions contain 6 Admit and 18 Reject states.
     Mean effects are F-B 0.270833, S-B 0.295356, and S-F 0.024523.

4. [ ] FG8 full-grid independent exact-protocol repetition
   - 1,296 registered calls across all frozen execution families and model
     slots.

## Registered Call Accounting

- Controls-v2 model-mediated layer: 96 calls.
- FG6-FG8: 3 x 1,296 = 3,888 calls.
- Total: 3,984 calls before transport retries.
- Completion accounting: Controls-v2 must have 96 unique terminal result rows;
  FG6, FG7, and FG8 must each have exactly 1,296 unique terminal result rows.

## Final Gate

- [ ] Each of the four items has a verifier-passing report and run log.
- [ ] Cross-repetition analysis uses paper-task as the independent unit and
      reports effect stability, decision agreement, technical failures, and
      terminal outcome decomposition without selective deletion.
- [ ] All task artifacts are committed and privately pushed; secrets, caches,
      environments, unrelated changes, and `s08/` are absent from commits.
- [ ] Final report records exact commit IDs, pushed branch, artifact paths,
      limitations, and any unverified residual risk.
