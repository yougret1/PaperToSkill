# Toolformer Loss-Filter Slice prefix_04

Evidence boundary: frozen dependency-closed discovery candidate; not a result.

Source atom map SHA-256: `e7b648237861ba1f6c326ca967a2eb891ec99e3d33a441eb413c8d04ce736bba`

## Procedure

1. **Normalize the decreasing future-token weights** (`T01`)
   Let t = j - i, so the first future token uses t = 0. Use raw weight max(0, 1 - 0.2 * t), then divide every raw weight by the sum over offsets.

2. **Compute weighted future-token loss** (`T02`)
   For each conditioning prefix, compute negative weighted log probability over the future tokens using the normalized weights.

3. **Use the stronger counterfactual baseline** (`T03`)
   Let L_empty be the loss with no API call and L_call_only the loss with the call but no result; set L_minus = min(L_empty, L_call_only).

4. **Keep calls that meet the filtering threshold** (`T04`)
   Let L_plus be the loss with the call and result. Compute margin = L_minus - L_plus and keep the call exactly when margin >= tau_filter.
