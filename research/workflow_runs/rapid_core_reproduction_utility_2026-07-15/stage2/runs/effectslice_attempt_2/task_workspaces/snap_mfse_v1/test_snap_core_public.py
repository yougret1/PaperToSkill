import numpy as np

from snap_core import matrix_free_spectral_embedding


def test_returns_finite_descending_embedding_with_expected_shape():
    counts = np.array(
        [
            [2.0, 1.0, 0.0, 0.0, 1.0],
            [1.0, 3.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 3.0, 1.0],
            [1.0, 0.0, 0.0, 1.0, 2.0],
            [2.0, 0.0, 0.0, 0.0, 1.0],
        ]
    )

    values, vectors = matrix_free_spectral_embedding(counts, 2, random_state=7)

    assert values.shape == (2,)
    assert vectors.shape == (counts.shape[0], 2)
    assert np.isfinite(values).all()
    assert np.isfinite(vectors).all()
    assert np.all(values[:-1] >= values[1:])
