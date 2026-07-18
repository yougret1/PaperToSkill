import hashlib
import itertools
import sys
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.confirmation_v3 import (  # noqa: E402
    CONDITIONS,
    balanced_schedule,
    joint_substitution_event,
    sha256_canonical_text,
    sha256_file,
)


def condition(success: bool, score: float, hard: bool = True) -> dict:
    return {
        "success": success,
        "task_score": score,
        "hard_constraints_passed": hard,
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "integrity_violations": [],
    }


def test_joint_event_accepts_successful_noninferior_slice():
    assert joint_substitution_event(
        condition(False, 0.0), condition(True, 0.98), condition(True, 0.96)
    )


def test_joint_event_accepts_slice_better_than_full():
    assert joint_substitution_event(
        condition(False, 0.0), condition(True, 0.95), condition(True, 1.0)
    )


def test_joint_event_rejects_common_full_and_slice_failure():
    assert not joint_substitution_event(
        condition(False, 0.0), condition(False, 0.1), condition(False, 0.1)
    )


def test_joint_event_rejects_slice_beyond_maximum_shortfall():
    assert not joint_substitution_event(
        condition(False, 0.0), condition(True, 1.0), condition(True, 0.94)
    )


def test_joint_event_rejects_hard_contract_failure():
    assert not joint_substitution_event(
        condition(False, 0.0), condition(True, 1.0), condition(True, 1.0, hard=False)
    )


@pytest.mark.parametrize("replicate_count", [-6, 0, 1, 5, 7])
def test_balanced_schedule_rejects_nonpositive_or_unbalanced_counts(replicate_count):
    with pytest.raises(ValueError, match="positive multiple of six"):
        balanced_schedule(seed=2026071801, replicate_count=replicate_count)


def test_balanced_schedule_uses_all_orders_equally():
    identity = balanced_schedule(seed=2026071801, replicate_count=6)
    planted = balanced_schedule(seed=2026071802, replicate_count=18)
    expected_orders = set(itertools.permutations(CONDITIONS))

    assert [row["replicate_id"] for row in identity] == [
        f"r{index:03d}" for index in range(1, 7)
    ]
    assert {tuple(row["condition_order"]) for row in identity} == expected_orders

    planted_counts = {
        order: sum(tuple(row["condition_order"]) == order for row in planted)
        for order in expected_orders
    }
    assert set(planted_counts.values()) == {3}


def test_file_and_canonical_text_hashes_use_exact_bytes_and_stripped_text():
    path = Path(__file__)
    file_bytes = path.read_bytes()
    expected_file_hash = hashlib.sha256(file_bytes).hexdigest()
    canonical_text = path.read_text(encoding="utf-8").strip().encode("utf-8")
    expected_text_hash = hashlib.sha256(canonical_text).hexdigest()

    assert sha256_file(path) == expected_file_hash
    assert sha256_canonical_text(path) == expected_text_hash
    assert expected_file_hash != expected_text_hash
