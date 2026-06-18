# Context Cost Proxy

Evidence boundary: Token counts are local tokenizer-aware counts using `o200k_base`. Cost uses a configurable `1.0` dollars per million input-token proxy. These are not provider bills, output-token costs, or success-per-dollar measurements.

Token count method: tiktoken encoding o200k_base.

## Context Size Proxy

| Paper | Variant | Words | Estimated input tokens | Tokens vs full paper | Token reduction vs full paper | Estimated input cost |
| --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | Full extracted paper | 29791 | 45212 | 1 | 0 | 0.045212 |
| AI Scientist-v2 | Curated source note | 820 | 1281 | 0.0283 | 0.9717 | 0.001281 |
| AI Scientist-v2 | Generated skill | 782 | 1079 | 0.0239 | 0.9761 | 0.001079 |
| AI Scientist-v2 | Generic summary | 154 | 193 | 0.0043 | 0.9957 | 0.000193 |
| AI Scientist-v2 | Abstract-only | 99 | 135 | 0.003 | 0.997 | 0.000135 |
| Reflexion | Full extracted paper | 9738 | 16414 | 1 | 0 | 0.016414 |
| Reflexion | Curated source note | 437 | 717 | 0.0437 | 0.9563 | 0.000717 |
| Reflexion | Generated skill | 479 | 703 | 0.0428 | 0.9572 | 0.000703 |
| Reflexion | Generic summary | 111 | 145 | 0.0088 | 0.9912 | 0.000145 |
| Reflexion | Abstract-only | 52 | 77 | 0.0047 | 0.9953 | 0.000077 |
| AIDE | Full extracted paper | 7848 | 13312 | 1 | 0 | 0.013312 |
| AIDE | Curated source note | 899 | 1390 | 0.1044 | 0.8956 | 0.00139 |
| AIDE | Generated skill | 927 | 1285 | 0.0965 | 0.9035 | 0.001285 |
| AIDE | Generic summary | 89 | 123 | 0.0092 | 0.9908 | 0.000123 |
| AIDE | Abstract-only | 51 | 74 | 0.0056 | 0.9944 | 0.000074 |
| Toolformer | Full extracted paper | 12355 | 20365 | 1 | 0 | 0.020365 |
| Toolformer | Curated source note | 894 | 1309 | 0.0643 | 0.9357 | 0.001309 |
| Toolformer | Generated skill | 943 | 1255 | 0.0616 | 0.9384 | 0.001255 |
| Toolformer | Generic summary | 78 | 98 | 0.0048 | 0.9952 | 0.000098 |
| Toolformer | Abstract-only | 40 | 54 | 0.0027 | 0.9973 | 0.000054 |

## Coverage Per Context Budget

Coverage scores are the existing deterministic context-coverage scores. Rows are limited to context variants that were already evaluated.

| Paper | Variant | Coverage score | Normalized coverage | Estimated input tokens | Coverage per 1k tokens | Normalized coverage per 1k tokens |
| --- | --- | --- | --- | --- | --- | --- |
| AI Scientist-v2 | Generated skill | 7.867/9 | 0.8741 | 1079 | 7.291 | 0.81 |
| AI Scientist-v2 | Generic summary | 1.733/9 | 0.1926 | 193 | 8.979 | 0.998 |
| AI Scientist-v2 | Abstract-only | 1.2/9 | 0.1333 | 135 | 8.889 | 0.988 |
| Reflexion | Generated skill | 8.267/9 | 0.9186 | 703 | 11.76 | 1.307 |
| Reflexion | Generic summary | 3.483/9 | 0.387 | 145 | 24.021 | 2.669 |
| Reflexion | Abstract-only | 2.533/9 | 0.2814 | 77 | 32.896 | 3.655 |
| AIDE | Generated skill | 9.1/10 | 0.91 | 1285 | 7.082 | 0.708 |
| AIDE | Generic summary | 1.916/10 | 0.1916 | 123 | 15.577 | 1.558 |
| AIDE | Abstract-only | 1.333/10 | 0.1333 | 74 | 18.014 | 1.801 |
| Toolformer | Generated skill | 8.9/10 | 0.89 | 1255 | 7.092 | 0.709 |
| Toolformer | Generic summary | 2.5/10 | 0.25 | 98 | 25.51 | 2.551 |
| Toolformer | Abstract-only | 1.534/10 | 0.1534 | 54 | 28.407 | 2.841 |
