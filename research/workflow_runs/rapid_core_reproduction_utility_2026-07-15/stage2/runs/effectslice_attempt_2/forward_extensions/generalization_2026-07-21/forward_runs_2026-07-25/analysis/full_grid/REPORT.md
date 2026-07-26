# FG6-FG8 Exact-Protocol Repetition Report

Registration bundle: `0ce5a41ab83289e23b2c3002911cfdb8fb635722cb26edcf7b1142e1863bc94d`

Each repetition contains exactly 1,296 registered terminal rows. The three repetitions total 3,888 rows.

## Repeat Completion

| Repeat | Registered | Valid | Invalid | Operational success |
|---|---:|---:|---:|---:|
| FG6 | 1296 | 1136 | 160 | 388 |
| FG7 | 1296 | 1136 | 160 | 365 |
| FG8 | 1296 | 1228 | 68 | 405 |

## Stability

- Terminal-outcome agreement: 780/1296.
- Condition-success agreement: 919/1296.
- Primary decision agreement: 20/24 paper-task units.

Technical Invalid rows remain in every registered denominator. These are independent exact-protocol repetitions, not API random-seed runs.

## Paper-Task-Averaged Effects

- F_minus_B: 0.262297 (approximate 95% CI [0.142371, 0.382224]).
- S_minus_B: 0.297779 (approximate 95% CI [0.160973, 0.434585]).
- S_minus_F: 0.035482 (approximate 95% CI [-0.000777, 0.071741]).

## Aggregate Terminal Outcomes

- hard_contract_failure: 2074.
- integrity_or_digest_failure: 388.
- malformed_or_no_submission: 268.
- operational_success: 1158.

Effects average repetitions within each paper-task before the 24-unit interval is computed. No API random-seed claim is made.
