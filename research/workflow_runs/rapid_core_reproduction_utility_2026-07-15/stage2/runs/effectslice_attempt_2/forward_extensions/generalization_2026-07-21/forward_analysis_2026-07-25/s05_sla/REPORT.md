# SLA Sensitivity Report

## Registered Six-Block Result

The frozen SLA admits 2 of 24 primary tasks, rejects 22, and marks none Invalid.
The admitted tasks are `DATA-LEI-02` and `NLP-LLM-02`, spanning two domains.
Primary reject reasons are full-insufficient for 20 tasks and
baseline-sensitive for 2 (`AGENT-TF-02` and `NLP-LL2-01`).

The preregistered engineering target required at least 8 of 24 admitted tasks
across at least three domains. The observed result, 2 of 24 across two domains,
does not meet that target. This failure cannot be rescued by effect estimates or
descriptive sensitivity analyses.

## Threshold Sensitivity

The 81-profile total-gate grid varies total `B` maximum and total `F`, `S`, and
margin minima while holding the registered per-registry gates fixed. Fifty-three
profiles change at least one task relative to the registered decision, but only
three tasks ever change: `DATA-LEI-02`, `NLP-LL2-02`, and `NLP-LLM-02`. The other
21 task decisions are unchanged throughout this grid.

Per-registry one-at-a-time perturbations change decisions only when the registry
`B` maximum is tightened from 1 to 0 or the registry `F` minimum is tightened
from 2 to 3; each change turns the two registered admits into rejects. Relaxing
the tested registry gates does not rescue another task because the registered
total gates remain binding.

Changing the paired-score margin tolerance across 0.000, 0.025, 0.050, 0.075,
and 0.100 changes no task decision.

## Leave-One-Block-Out

The registered five-block descriptive rule yields 14 Admit and 130 Reject states
across 144 omissions, with no Invalid state. Only two recomputations differ from
their six-block decision: omitting block 2 or block 4 of `NLP-LL2-02` produces a
five-block Admit. The other 142 omissions retain the registered label.

These two omissions are sensitivity signals, not recovered registered admits.
The six-block decision remains Reject. Per-registry gates are intentionally not
applied after an unbalanced omission, exactly as registered.

## Claim Boundary

The sensitivity result is locally concentrated: 21 of 24 task decisions match
the registered state across every tested total-grid, registry, margin, and block
omission perturbation. However, the primary engineering yield target fails, and
the two admitted tasks are vulnerable to stricter registry thresholds. Any paper
claim must report both facts.
