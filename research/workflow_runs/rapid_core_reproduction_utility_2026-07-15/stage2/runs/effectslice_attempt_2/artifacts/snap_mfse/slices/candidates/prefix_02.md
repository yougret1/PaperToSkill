# SnapATAC2 MFSE Slice prefix_02

Evidence boundary: frozen dependency-closed discovery candidate; not a result.

Source atom map SHA-256: `c495f458b2ec182a850d10b06fd843961340947ce5ab7ee11ec16edca42c84d8`

## Procedure

1. **Scale features with the paper IDF** (`A01`)
   For n cells and feature document frequency df, multiply each feature by log(n / (1 + df)) before row normalization.

2. **Normalize rows for cosine similarity** (`A02`)
   After IDF scaling, normalize every nonzero cell row to unit L2 norm; the resulting matrix X represents cosine similarities through X X^T.
