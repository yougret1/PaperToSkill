from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import aggregate_fg3_results as aggregate  # noqa: E402


@pytest.fixture(scope="module")
def frozen_result() -> dict[str, object]:
    result, _ = aggregate.aggregate(
        aggregate.DEFAULT_SUCCESSOR.resolve(), aggregate.DEFAULT_RUN_DIR.resolve()
    )
    return result


def make_primary_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for condition in ("B", "F", "S"):
        for block in range(1, 7):
            success = condition == "B" and block <= 2
            rows.append(
                {
                    "execution_id": f"{condition}-{block}",
                    "condition": condition,
                    "block_id": block,
                    "row_valid": True,
                    "private_score": 1.0 if success else 0.0,
                    "condition_success": success,
                }
            )
    return rows


def directory_hashes(path: Path) -> dict[str, str]:
    return {
        item.name: aggregate.sha256_path(item)
        for item in sorted(path.iterdir())
        if item.is_file()
    }


def test_exact_1296_row_binding_matches_frozen_schedule() -> None:
    rows, manifest = aggregate.load_rows(
        aggregate.DEFAULT_SUCCESSOR.resolve(), aggregate.DEFAULT_RUN_DIR.resolve()
    )
    schedule = json.loads(
        (aggregate.DEFAULT_SUCCESSOR / "global_remote_schedule.json").read_text(
            encoding="utf-8"
        )
    )["rows"]
    expected = [row["execution_id"] for row in schedule]
    observed = [row["execution_id"] for row in rows]
    assert len(rows) == len(set(observed)) == 1296
    assert observed == expected
    assert manifest["row_count"] == 1296
    assert len(manifest["schedule_sha256"]) == 64
    assert len(manifest["row_hash_manifest_sha256"]) == 64


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        (0.75, 0.25, (0.5, 0.5, 0.5)),
        (0.75, None, (-0.25, 0.75, None)),
        (None, 0.25, (-0.25, 0.75, None)),
        (None, None, (-1.0, 1.0, None)),
    ],
)
def test_registered_partial_identification_bounds(
    x: float | None, y: float | None, expected: tuple[float, float, float | None]
) -> None:
    assert aggregate.identified_block(x, y) == expected


def test_validity_requires_registered_score_and_success_types() -> None:
    base = {
        "row_valid": True,
        "private_score": 0.5,
        "condition_success": False,
    }
    assert aggregate.is_valid(base)
    assert not aggregate.is_valid({**base, "private_score": -0.01})
    assert not aggregate.is_valid({**base, "private_score": 1.01})
    assert not aggregate.is_valid({**base, "private_score": float("nan")})
    assert not aggregate.is_valid({**base, "condition_success": None})


def test_reject_reason_uses_registered_precedence() -> None:
    state = aggregate.decision_state(make_primary_rows())
    assert state["state"] == "Reject"
    assert state["primary_reject_reason"] == "F_insufficient"
    categories = [
        "full" if "F_insufficient" in reason else
        "baseline" if "B_sensitivity" in reason else
        "slice" if "S_insufficient" in reason else
        "margin"
        for reason in state["reasons"]
    ]
    assert categories == sorted(
        categories, key=("full", "baseline", "slice", "margin").index
    )


def test_frozen_primary_counts_and_effects(frozen_result: dict[str, object]) -> None:
    assert frozen_result["registered_rows"] == 1296
    assert frozen_result["primary_state_counts"] == {"Reject": 24}
    assert frozen_result["registered_targets"]["decision_coverage"]["passed"] is True
    assert frozen_result["registered_targets"]["candidate_yield"]["passed"] is False
    for outcome in ("success", "score"):
        for contrast, expected in (
            ("F_minus_B", 0.0),
            ("S_minus_B", 1.0 / 144.0),
            ("S_minus_F", 1.0 / 144.0),
        ):
            overall = frozen_result["effects"][outcome][contrast]["overall"]
            assert overall["observed_papers"] == 12
            assert overall["observed"] == pytest.approx(expected)
            assert overall["lower"] == pytest.approx(expected)
            assert overall["upper"] == pytest.approx(expected)


def test_controls_and_sensitivity_denominators(
    frozen_result: dict[str, object]
) -> None:
    controls = frozen_result["secondary_states"]["controls"]
    assert Counter(row["state"] for row in controls) == {
        "SanityFail": 11,
        "SanityPass": 1,
    }
    assert len(frozen_result["sla_sensitivity"]["grid"]) == 81
    assert len(frozen_result["sla_sensitivity"]["leave_one_block_out"]) == 144


def test_invalid_model_pairs_stay_null(frozen_result: dict[str, object]) -> None:
    for cell in frozen_result["model_states"]:
        score_raw = cell["score_delta"]["raw"]
        for index, score_delta in enumerate(score_raw):
            if score_delta is None:
                for metric in cell["repeatability"].values():
                    assert metric["raw"][index] is None
        assert (
            cell["repeatability"]["input_digest_agreement"]["valid_pairs"]
            == cell["score_delta"]["valid_pairs"]
        )
        assert (
            cell["repeatability"]["operational_success_agreement"]["valid_pairs"]
            == cell["score_delta"]["valid_pairs"]
        )
    assert aggregate.equality_or_null(None, None, True) is None


def test_aggregate_and_written_outputs_are_deterministic(
    tmp_path: Path, frozen_result: dict[str, object]
) -> None:
    repeated, _ = aggregate.aggregate(
        aggregate.DEFAULT_SUCCESSOR.resolve(), aggregate.DEFAULT_RUN_DIR.resolve()
    )
    assert aggregate.canonical_bytes(repeated) == aggregate.canonical_bytes(frozen_result)

    first = tmp_path / "first"
    second = tmp_path / "second"
    assert aggregate.main(["--output-dir", str(first)]) == 0
    assert aggregate.main(["--output-dir", str(second)]) == 0
    assert directory_hashes(first) == directory_hashes(second)
