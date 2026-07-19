# Toolformer API-Call Loss-Filter Execution Card

Evidence boundary: task-local paper procedure derived from Toolformer lines 76-79, 134-171, and 268-272.
It does not expose scorer cases or reference code.

Source SHA-256: `1fa619f443e107690b9fb722a72ab361825cfda5346436c90cb23acb3c7bfbb6`

## Procedure

1. **Normalize the decreasing future-token weights** (`T01`)
   Let t = j - i, so the first future token uses t = 0. Use raw weight max(0, 1 - 0.2 * t), then divide every raw weight by the sum over offsets.

2. **Compute weighted future-token loss** (`T02`)
   For each conditioning prefix, compute negative weighted log probability over the future tokens using the normalized weights.

3. **Use the stronger counterfactual baseline** (`T03`)
   Let L_empty be the loss with no API call and L_call_only the loss with the call but no result; set L_minus = min(L_empty, L_call_only).

4. **Keep calls that meet the filtering threshold** (`T04`)
   Let L_plus be the loss with the call and result. Compute margin = L_minus - L_plus and keep the call exactly when margin >= tau_filter.

5. **Apply the rule to every proposed call in order** (`T05`)
   Evaluate every executed candidate call independently, filter all candidates with the same rule, and preserve candidate order in the output.

## Validation Boundary

- Treat inputs as token log probabilities; lower weighted loss is better.
- Return one Boolean decision and one finite margin per candidate.
- Preserve the inclusive threshold tie and the paper counterfactual minimum.
- Do not infer full Toolformer training or downstream benchmark claims from this task.
