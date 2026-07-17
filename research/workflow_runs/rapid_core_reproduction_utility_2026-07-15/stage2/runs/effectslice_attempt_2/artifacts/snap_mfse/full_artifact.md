# SnapATAC2 Matrix-Free Spectral Embedding Execution Card

Evidence boundary: task-local procedural artifact derived from paper lines 73-79. 
It is not reference code and does not expose scorer cases.

Source SHA-256: `34ac99920bd570befad0993bb5f0bf0e66444ef09e4a670fcdc51e58815c56a7`

## Procedure

1. **Scale features with the paper IDF** (`A01`)
   For n cells and feature document frequency df, multiply each feature by log(n / (1 + df)) before row normalization.

2. **Normalize rows for cosine similarity** (`A02`)
   After IDF scaling, normalize every nonzero cell row to unit L2 norm; the resulting matrix X represents cosine similarities through X X^T.

3. **Remove self-similarity and compute degrees matrix-free** (`A03`)
   Use W = X X^T - I and compute its degree vector as X @ (X.T @ 1) - 1 without constructing W.

4. **Expose the normalized similarity as a linear operator** (`A04`)
   Let X_tilde = D^(-1/2) X and D_inv be the reciprocal degree vector. For every trial vector v, evaluate X_tilde @ (X_tilde.T @ v) - D_inv * v.

5. **Return the leading spectral coordinates under the paper scope** (`A05`)
   Use a Lanczos-style symmetric eigensolver, order the top eigenpairs from largest to smallest, and keep this exact matrix-free route scoped to cosine similarity. Do not materialize an n-cell by n-cell matrix.

## Hard Checks

- Reject nonfinite or negative count values and rows that cannot be L2-normalized.
- Require positive degrees before applying D^(-1/2).
- Return finite eigenvalues in descending order and one eigenvector column per component.
- Do not materialize the cell-by-cell similarity or normalized similarity matrix.
- Treat the method as cosine-specific; do not claim arbitrary similarity support.

## Validation

Validate eigenpair residuals and compare the returned eigenspace with an independent implementation of the paper equations. Eigenvector signs are not identifiable, so compare subspaces rather than raw signs.
