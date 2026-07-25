# Forward Analysis Completion Checklist

Date: 2026-07-25

This checklist is forward-only. Frozen FG3, FG4, and FG5 artifacts are inputs and
must not be mutated or reinterpreted. A section is complete only after its
artifacts, verification record, log, commit, and private push all succeed.

## Active Work

1. [x] F/S/B paper-task effects
   - Status: independently rerun, hash-verified, committed as `582bba5c`, and privately pushed through `e547d1fc`.
   - Deliver paper-level effects, paper-stratified intervals, task effects, and forest-plot data.
2. [x] Generalization and interactions
   - Status: independently rerun, hash-verified, committed as `e547d1fc`, and privately pushed.
   - Separate the 24-task DeepSeek primary analysis from the four-anchor, six-model analysis.
   - Report domain, model, task, registry, and reducer effects without overstating coverage.
3. [ ] Registered controls audit
   - Status: scratch audit exists; repository migration and independent rerun pending.
   - Report exact SanityPass/SanityFail/Invalid states and destructive-target binding validity.
4. [ ] Failure decomposition
   - Status: scratch results exist; repository migration and independent rerun pending.
   - Separate original routing class, final result source, and final experimental endpoint.
5. [ ] SLA sensitivity and leave-one-block-out
   - Apply the frozen six-block and registered block-omission rules.
   - Report threshold sensitivity separately from registered decisions.
6. [ ] Targeted anomaly review and reruns
   - Identify ambiguous transport failures and repeatability anomalies.
   - Rerun only cases whose cause remains ambiguous, under a frozen successor registry.
7. [ ] Focused Atom restore/drop intervention
   - Use one representative task per domain.
   - Compare critical-atom drop, noncritical-atom drop, and incremental restore arms.
   - Freeze and privately push the successor before any provider call.
8. [ ] Figure-design evidence and manuscript-owner handoff
   - Find relevant published figure designs for forest, sensitivity, failure, and intervention results.
   - Deliver claim boundaries, plot/table specifications, source data, and a concise handoff report.

## Deferred And Not Executed

Note: 准备时间多的话再去做. These items were retained for traceability but are
outside the current execution scope and must not be run in this goal.

9. [ ] Additional compression points and Pareto analysis
10. [ ] Additional publication-figure implementation and visual polishing
11. [ ] FG6 comprehensive multi-seed experiment (must remain last)
