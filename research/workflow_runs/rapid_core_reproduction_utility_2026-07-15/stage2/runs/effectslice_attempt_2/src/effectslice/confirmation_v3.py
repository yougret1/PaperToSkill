from __future__ import annotations

import hashlib
import itertools
import math
import random
from pathlib import Path
from typing import Any


CONDITIONS = ("B", "F", "S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_canonical_text(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8").strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def balanced_schedule(seed: int, replicate_count: int) -> list[dict[str, Any]]:
    orders = list(itertools.permutations(CONDITIONS))
    if replicate_count <= 0 or replicate_count % len(orders):
        raise ValueError("replicate_count must be a positive multiple of six")
    rows = orders * (replicate_count // len(orders))
    random.Random(seed).shuffle(rows)
    return [
        {"replicate_id": f"r{index:03d}", "condition_order": list(order)}
        for index, order in enumerate(rows, start=1)
    ]


def _unit_interval_number(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    if type(value) is float and not math.isfinite(value):
        return False
    return 0 <= value <= 1


def _condition_valid(row: dict[str, Any], expected_success: bool) -> bool:
    integrity_violations = row.get("integrity_violations")
    return (
        type(row.get("success")) is bool
        and row["success"] is expected_success
        and type(row.get("private_score_count")) is int
        and row["private_score_count"] == 1
        and row.get("private_feedback_exposed") is False
        and row.get("hard_constraints_passed") is True
        and type(integrity_violations) is list
        and integrity_violations == []
        and _unit_interval_number(row.get("task_score"))
    )


def joint_substitution_event(
    baseline: dict[str, Any],
    full: dict[str, Any],
    sliced: dict[str, Any],
    maximum_shortfall: float = 0.05,
) -> bool:
    if not _unit_interval_number(maximum_shortfall):
        raise ValueError("maximum_shortfall must be a finite number within [0, 1]")
    if not all(
        _condition_valid(row, expected_success)
        for row, expected_success in (
            (baseline, False),
            (full, True),
            (sliced, True),
        )
    ):
        return False
    return bool(
        sliced["task_score"] >= full["task_score"] - maximum_shortfall
    )
