"""Starter module for the locked SNAP-MFSE reproduction task."""

from __future__ import annotations

import numpy as np


def matrix_free_spectral_embedding(
    counts: np.ndarray,
    n_components: int,
    random_state: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return leading spectral coordinates for a cell-by-feature count matrix."""

    raise NotImplementedError("implement the paper-core reproduction task")
