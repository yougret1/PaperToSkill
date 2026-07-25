# Failure Decomposition Report

## Final Endpoints

| Final endpoint | Rows | Share |
| --- | ---: | ---: |
| Operational success | 383 | 29.55% |
| Complete submission, private-contract failure | 759 | 58.56% |
| Submission or case-coverage failure | 154 | 11.88% |
| Score shortfall after all aggregate hard contracts pass | 0 | 0.00% |

The counts cover exactly 1,296 unique registered rows. The three observed rows
sum to 1,296; percentages differ from 100 only through rounding.

## Final Result Provenance

| Final result source | Rows | Successes | Hard-contract failures |
| --- | ---: | ---: | ---: |
| FG3 retained | 146 | 5 | 141 |
| FG5 exact-output direct | 648 | 224 | 424 |
| Response-format successor | 104 | 22 | 82 |
| Integrity/digest successor | 129 | 35 | 94 |
| Payload/interface successor | 268 | 97 | 171 |
| Provider-availability successor | 1 | 0 | 1 |
| **Total** | **1,296** | **383** | **913** |

These provenance rows say where the single terminal result came from. They do
not say that a paper-task passed an ordered sequence of six experimental stages.

## Original Routing Versus Final Outcome

The original `exact_output_contract` class contains 684 rows. Of these, 648 take
their final value directly from FG5, 27 from a response-format successor, and 9
from an integrity/digest successor. Their final endpoints are 236 successes, 435
complete-submission private-contract failures, and 13 incomplete-coverage
failures. This illustrates why the original diagnosis cannot be reported as the
final model result.

Across all rows, the dominant experimental failure is a complete submission
that fails at least one private expected result (759 rows), not transport or
format availability. A further 154 rows have incomplete task-specific case or
executable coverage. The common scorer vector cannot isolate a domain-specific
`no_patch` endpoint, so no such count is reported.
