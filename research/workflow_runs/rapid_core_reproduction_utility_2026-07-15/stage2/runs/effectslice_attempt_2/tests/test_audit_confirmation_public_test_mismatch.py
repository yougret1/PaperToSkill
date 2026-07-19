from __future__ import annotations

import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from audit_confirmation_public_test_mismatch import (  # noqa: E402
    UNAVAILABLE_MESSAGE,
    audit_transcript,
    build_audit,
)


def test_audit_transcript_counts_only_rejected_test_actions():
    payload = {
        "turns": [
            {"action": {"action": "open"}, "observation_status": "ok"},
            {
                "action": {"action": "test"},
                "observation_status": "unavailable",
                "observation_message": UNAVAILABLE_MESSAGE,
            },
            {
                "action": {"action": "test"},
                "observation_status": "public_tested",
                "observation_message": "1 passed",
            },
        ]
    }

    result = audit_transcript(payload)

    assert result == {
        "turn_count": 3,
        "test_action_count": 2,
        "unavailable_test_count": 1,
        "affected": True,
    }


def test_real_audit_covers_both_primary_components():
    result = build_audit()

    assert result["component_run_counts"] == {
        "interleaved_calibration": 126,
        "real_task_confirmation": 108,
    }
    assert result["run_count"] == 234
    assert result["component_affected_counts"] == {
        "interleaved_calibration": 125,
        "real_task_confirmation": 108,
    }
    assert result["run_with_test_action_count"] == 233
    assert result["affected_run_count"] == 233
    assert result["all_test_actions_rejected_by_mismatch"] is True
