"""Starter module for the locked Toolformer loss-filter task."""

from __future__ import annotations

import numpy as np


def filter_api_calls(
    logp_with_result: np.ndarray,
    logp_call_only: np.ndarray,
    logp_no_call: np.ndarray,
    tau_filter: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return an ordered keep mask and one finite margin per proposed call."""

    raise NotImplementedError("implement the paper-core reproduction task")
