# Toolformer Loss-Filter Locked Paper-Core Reproduction Task

Task type: paper-method-to-tested-implementation

Implement `filter_api_calls` in `toolformer_filter.py` using NumPy. Each of the
three inputs is a finite, nonpositive, two-dimensional matrix of token log
probabilities with shape `(n_candidates, future_horizon)`. `tau_filter` is a
finite nonnegative threshold. Return a Boolean keep mask and finite floating
margins, both with shape `(n_candidates,)`, and preserve candidate order.

Reject empty, non-matrix, shape-mismatched, nonfinite, or positive-valued input
matrices and invalid thresholds with `ValueError`.
Boolean values are invalid thresholds. Keep the change focused in
`toolformer_filter.py`.

The bounded ACI reports a fixed 16-action horizon and the actions remaining on
every turn. Inspect the starter before editing and use the public test before
submitting.

Verification command:

```powershell
python -m pytest test_toolformer_filter_public.py
```

The public test checks only interface-level behavior. Hidden deterministic
cases check the paper-specific numerical procedure and invalid inputs. Do not
claim success unless the verification command passes.
