import numpy as np

from toolformer_filter import filter_api_calls


def test_returns_ordered_boolean_mask_and_finite_margins():
    with_result = np.array([[-1.0, -1.2, -1.1], [-1.4, -1.2, -1.3]])
    call_only = np.array([[-1.8, -1.7, -1.9], [-1.5, -1.7, -1.6]])
    no_call = np.array([[-2.0, -1.9, -2.1], [-1.8, -1.6, -1.7]])

    keep, margins = filter_api_calls(with_result, call_only, no_call, 0.1)

    assert keep.shape == (with_result.shape[0],)
    assert keep.dtype == np.bool_
    assert margins.shape == (with_result.shape[0],)
    assert np.issubdtype(margins.dtype, np.floating)
    assert np.isfinite(margins).all()
