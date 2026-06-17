# Context Cost Proxy

Evidence boundary: token counts are deterministic proxies, estimated as `ceil(characters / 4)`. Cost uses a configurable `1.0` dollars per million input-token proxy. These are not provider bills or tokenizer-exact measurements.

## Context Size Proxy

| Paper | Variant | Words | Estimated input tokens | Tokens vs full paper | Token reduction vs full paper | Estimated input cost |
| --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | Full extracted paper | 29791 | 62041 | 1 | 0 | 0.062041 |
| AI Scientist-v2 | Curated source note | 820 | 1462 | 0.0236 | 0.9764 | 0.001462 |
| AI Scientist-v2 | Generated skill | 782 | 1366 | 0.022 | 0.978 | 0.001366 |
| AI Scientist-v2 | Generic summary | 154 | 262 | 0.0042 | 0.9958 | 0.000262 |
| AI Scientist-v2 | Abstract-only | 99 | 174 | 0.0028 | 0.9972 | 0.000174 |
| Reflexion | Full extracted paper | 9738 | 18559 | 1 | 0 | 0.018559 |
| Reflexion | Curated source note | 437 | 750 | 0.0404 | 0.9596 | 0.00075 |
| Reflexion | Generated skill | 479 | 823 | 0.0443 | 0.9557 | 0.000823 |
| Reflexion | Generic summary | 111 | 186 | 0.01 | 0.99 | 0.000186 |
| Reflexion | Abstract-only | 52 | 94 | 0.0051 | 0.9949 | 0.000094 |
| AIDE | Full extracted paper | 7848 | 15894 | 1 | 0 | 0.015894 |
| AIDE | Curated source note | 899 | 1505 | 0.0947 | 0.9053 | 0.001505 |
| AIDE | Generated skill | 927 | 1517 | 0.0954 | 0.9046 | 0.001517 |
| AIDE | Generic summary | 89 | 152 | 0.0096 | 0.9904 | 0.000152 |
| AIDE | Abstract-only | 51 | 83 | 0.0052 | 0.9948 | 0.000083 |

## Coverage Per Context Budget

Coverage scores are the existing deterministic context-coverage scores. Rows are limited to context variants that were already evaluated.

| Paper | Variant | Coverage score | Normalized coverage | Estimated input tokens | Coverage per 1k tokens | Normalized coverage per 1k tokens |
| --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | Generated skill | 7.867/9 | 0.8741 | 1366 | 5.759 | 0.64 |
| AI Scientist-v2 | Generic summary | 1.733/9 | 0.1926 | 262 | 6.615 | 0.735 |
| AI Scientist-v2 | Abstract-only | 1.2/9 | 0.1333 | 174 | 6.897 | 0.766 |
| Reflexion | Generated skill | 8.267/9 | 0.9186 | 823 | 10.045 | 1.116 |
| Reflexion | Generic summary | 3.483/9 | 0.387 | 186 | 18.726 | 2.081 |
| Reflexion | Abstract-only | 2.533/9 | 0.2814 | 94 | 26.947 | 2.994 |
| AIDE | Generated skill | 9.1/10 | 0.91 | 1517 | 5.999 | 0.6 |
| AIDE | Generic summary | 1.916/10 | 0.1916 | 152 | 12.605 | 1.261 |
| AIDE | Abstract-only | 1.333/10 | 0.1333 | 83 | 16.06 | 1.606 |
