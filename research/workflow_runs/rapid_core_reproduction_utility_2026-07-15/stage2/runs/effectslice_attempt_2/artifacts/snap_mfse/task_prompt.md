# SNAP-MFSE Locked Paper-Core Reproduction Task

Task type: paper-method-to-tested-implementation

Implement `matrix_free_spectral_embedding` in `snap_core.py` using NumPy and
SciPy. The input is a finite, nonnegative, two-dimensional cell-by-feature
count matrix. Return the leading `n_components` eigenvalues in descending order
and a `(n_cells, n_components)` matrix whose columns span the corresponding
cell embedding.

Reject nonfinite or negative inputs, all-zero cell rows, and component counts
outside `1 <= n_components < n_cells` with `ValueError`. The implementation
must not materialize an `n_cells x n_cells` similarity or normalized-similarity
matrix. Keep the change focused in `snap_core.py`.

The bounded ACI reports a fixed 16-action horizon and the actions remaining on
every turn. Inspect the starter before editing and use the public test before
submitting.

Verification command:

```powershell
python -m pytest test_snap_core_public.py
```

The public test checks only interface-level behavior. Hidden deterministic
cases check the paper-specific numerical method, invalid inputs, and the
matrix-free resource contract. Do not claim success unless the verification
command passes.
