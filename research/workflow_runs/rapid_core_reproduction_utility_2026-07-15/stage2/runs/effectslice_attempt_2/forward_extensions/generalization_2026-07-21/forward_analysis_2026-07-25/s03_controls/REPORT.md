# Registered Controls Audit Report

## Scope

The audit covers four domain-anchor tasks, three registered controls per task,
six paired blocks per control, and two rows per block: 144 terminal rows. Every
row was joined to the frozen schedule by global sequence index, its terminal
source SHA-256 was verified, and its task, condition, registry, score, terminal
outcome, hard-contract vector, and input digests were checked.

## Exact Results

| Registered control | SanityPass | SanityFail | Invalid |
| --- | ---: | ---: | ---: |
| Planted redundancy positive | 1 | 3 | 0 |
| Byte-identical identity | 1 | 3 | 0 |
| Destructive core negative | 0 | 0 | 4 |

The positive control passes only `NLP-LLM-01`. The identity control passes only
`DATA-HDB-01`. Across the other three tasks in each control, valid repeated model
calls disagree too often on success, hard-contract vector, or score tolerance to
pass the frozen sanity gate.

## Binding Audit

Each scorer manifest names four semantic hard contracts, but every observed
scorer vector has only two aggregate entries: `complete` and
`all_private_cases_pass`. The materialized `control_negative` candidate, its
retained atoms, scorer manifest, and scorer implementation contain no
machine-readable destructive-target-to-vector binding. Consequently, the
registered targeted-failure count is not identifiable. The observed six of six
candidate rows with at least one aggregate hard-contract failure in every task
is retained only as a descriptive proxy; it cannot satisfy the registered
targeted gate.

## Interpretation

The controls do not validate a known-positive/known-negative classifier. They
show instead that single-run remote evaluation has substantial repeatability
risk: even byte-identical arms fail the registered agreement gate for three of
four tasks. The positive control is also byte-identical by frozen input digests,
so it does not establish tolerance to removal of genuinely redundant content.
These limitations must accompany any use of the main F/S/B effects.

No confusion matrix or false-admit/false-reject estimate is justified.
