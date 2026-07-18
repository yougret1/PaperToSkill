from __future__ import annotations

import hashlib
import itertools
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


def _condition_valid(row: dict[str, Any]) -> bool:
    return (
        row.get("private_score_count") == 1
        and row.get("private_feedback_exposed") is False
        and row.get("hard_constraints_passed") is True
        and not row.get("integrity_violations")
    )


def joint_substitution_event(
    baseline: dict[str, Any],
    full: dict[str, Any],
    sliced: dict[str, Any],
    maximum_shortfall: float = 0.05,
) -> bool:
    if not all(_condition_valid(row) for row in (baseline, full, sliced)):
        return False
    return bool(
        not baseline.get("success")
        and full.get("success")
        and sliced.get("success")
        and float(sliced["task_score"])
        >= float(full["task_score"]) - maximum_shortfall
    )
