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


MISSING = object()
ROW_NAMES = ("baseline", "full", "sliced")


def condition(success: bool, score: float, hard: bool = True) -> dict:
    return {
        "success": success,
        "task_score": score,
        "hard_constraints_passed": hard,
        "private_score_count": 1,
        "private_feedback_exposed": False,
        "integrity_violations": [],
    }


def valid_rows() -> dict[str, dict]:
    return {
        "baseline": condition(False, 0.0),
        "full": condition(True, 0.98),
        "sliced": condition(True, 0.96),
    }


def event_with_mutation(row_name: str, field: str, value=MISSING) -> bool:
    rows = valid_rows()
    if value is MISSING:
        rows[row_name].pop(field)
    else:
        rows[row_name][field] = value
    return joint_substitution_event(
        rows["baseline"], rows["full"], rows["sliced"]
    )


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


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(False, id="false"),
        pytest.param(0, id="zero"),
        pytest.param("", id="empty-string"),
        pytest.param({}, id="empty-dict"),
    ],
)
def test_joint_event_requires_integrity_violations_to_be_an_explicit_empty_list(
    row_name, value
):
    assert not event_with_mutation(row_name, "integrity_violations", value)


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(0, id="zero-int"),
        pytest.param(1, id="one-int"),
        pytest.param("False", id="false-string"),
        pytest.param("True", id="true-string"),
    ],
)
def test_joint_event_rejects_non_boolean_success_metadata(row_name, value):
    assert not event_with_mutation(row_name, "success", value)


@pytest.mark.parametrize(
    ("row_name", "wrong_success"),
    [("baseline", True), ("full", False), ("sliced", False)],
)
def test_joint_event_requires_condition_specific_boolean_success(
    row_name, wrong_success
):
    assert not event_with_mutation(row_name, "success", wrong_success)


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(False, id="false-bool"),
        pytest.param(True, id="true-bool"),
        pytest.param(1.0, id="float"),
        pytest.param("1", id="string"),
    ],
)
def test_joint_event_requires_exact_integer_private_score_count(row_name, value):
    assert not event_with_mutation(row_name, "private_score_count", value)


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(0, id="zero-int"),
        pytest.param("False", id="string"),
        pytest.param(True, id="true-bool"),
    ],
)
def test_joint_event_requires_exact_false_private_feedback_flag(row_name, value):
    assert not event_with_mutation(row_name, "private_feedback_exposed", value)


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(1, id="one-int"),
        pytest.param("True", id="string"),
        pytest.param(False, id="false-bool"),
    ],
)
def test_joint_event_requires_exact_true_hard_constraints_flag(row_name, value):
    assert not event_with_mutation(row_name, "hard_constraints_passed", value)


@pytest.mark.parametrize("row_name", ROW_NAMES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="none"),
        pytest.param(False, id="false-bool"),
        pytest.param(True, id="true-bool"),
        pytest.param("0.5", id="string"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param(-0.01, id="below-zero"),
        pytest.param(1.01, id="above-one"),
    ],
)
def test_joint_event_rejects_invalid_task_scores_for_every_condition(row_name, value):
    assert not event_with_mutation(row_name, "task_score", value)


@pytest.mark.parametrize(
    "maximum_shortfall",
    [
        pytest.param(None, id="none"),
        pytest.param(False, id="false-bool"),
        pytest.param(True, id="true-bool"),
        pytest.param("0.05", id="string"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param(-0.01, id="below-zero"),
        pytest.param(1.01, id="above-one"),
    ],
)
def test_joint_event_rejects_invalid_maximum_shortfall_argument(maximum_shortfall):
    rows = valid_rows()
    with pytest.raises(ValueError, match="maximum_shortfall"):
        joint_substitution_event(
            rows["baseline"],
            rows["full"],
            rows["sliced"],
            maximum_shortfall=maximum_shortfall,
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


def test_balanced_schedule_is_repeatable_for_the_same_seed():
    first = balanced_schedule(seed=2026071803, replicate_count=18)
    second = balanced_schedule(seed=2026071803, replicate_count=18)

    assert first == second


def test_file_and_canonical_text_hashes_use_exact_bytes_and_stripped_text():
    path = Path(__file__)
    file_bytes = path.read_bytes()
    expected_file_hash = hashlib.sha256(file_bytes).hexdigest()
    canonical_text = path.read_text(encoding="utf-8").strip().encode("utf-8")
    expected_text_hash = hashlib.sha256(canonical_text).hexdigest()

    assert sha256_file(path) == expected_file_hash
    assert sha256_canonical_text(path) == expected_text_hash
    assert expected_file_hash != expected_text_hash
