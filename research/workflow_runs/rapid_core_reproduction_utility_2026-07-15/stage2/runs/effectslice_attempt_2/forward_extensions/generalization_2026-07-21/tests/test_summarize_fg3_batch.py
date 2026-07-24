from __future__ import annotations

import sys
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import summarize_fg3_batch as summary  # noqa: E402


def test_transportless_recovery_is_countable() -> None:
    row = {
        "attempts": [],
        "terminal_outcome": "provider_or_model_unavailable",
        "termination_reason": "not_dispatched",
        "raw_response_path": None,
        "private_score": None,
    }
    assert summary.validated_attempts(row, row["terminal_outcome"]) == []


def test_zero_attempt_semantic_outcome_is_rejected() -> None:
    row = {
        "attempts": [],
        "terminal_outcome": "hard_contract_failure",
        "termination_reason": "provider_stop",
        "raw_response_path": "raw/example.json",
        "private_score": 0.0,
    }
    with pytest.raises(summary.SummaryError, match="outside provider/model unavailability"):
        summary.validated_attempts(row, row["terminal_outcome"])
