# Toolformer Loss-Filter Slice prefix_02

Evidence boundary: frozen dependency-closed discovery candidate; not a result.

Source atom map SHA-256: `e7b648237861ba1f6c326ca967a2eb891ec99e3d33a441eb413c8d04ce736bba`

## Procedure

1. **Normalize the decreasing future-token weights** (`T01`)
   Let t = j - i, so the first future token uses t = 0. Use raw weight max(0, 1 - 0.2 * t), then divide every raw weight by the sum over offsets.

2. **Compute weighted future-token loss** (`T02`)
   For each conditioning prefix, compute negative weighted log probability over the future tokens using the normalized weights.
