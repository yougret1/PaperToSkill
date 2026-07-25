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

## Experiments

1. [ ] Controls-v2
   - Deterministic label layer: zero provider calls.
   - Model-mediated layer: 4 domain anchors x 2 registries x 4 arms x 3
     independent repetitions = 96 registered calls.
   - Required machine binding:
     `mutation_id -> atom IDs -> contract ID -> private case IDs -> scorer key`.
   - Report deterministic confusion results separately from model-mediated
     retention, localization, and repeatability.

2. [ ] FG6 full-grid independent exact-protocol repetition
   - 1,296 registered calls across all frozen execution families and model
     slots.

3. [ ] FG7 full-grid independent exact-protocol repetition
   - 1,296 registered calls across all frozen execution families and model
     slots.

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
