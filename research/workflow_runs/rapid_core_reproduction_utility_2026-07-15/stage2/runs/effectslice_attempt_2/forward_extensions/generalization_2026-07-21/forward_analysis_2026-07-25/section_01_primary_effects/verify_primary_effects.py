from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "outputs"
EXPECTED = {
    ("F_minus_B", "operational_success"): (0.19444444444444442, 0.09027777777777776, 0.2986111111111111),
    ("F_minus_B", "private_score"): (0.15766059027777776, 0.04774305555555555, 0.2781032986111111),
    ("S_minus_B", "operational_success"): (0.24305555555555555, 0.10416666666666666, 0.3888888888888889),
    ("S_minus_B", "private_score"): (0.2170138888888889, 0.09223090277777778, 0.3557942708333333),
    ("S_minus_F", "operational_success"): (0.048611111111111105, -0.020833333333333332, 0.11805555555555555),
    ("S_minus_F", "private_score"): (0.05935329861111111, 0.0, 0.12153591579861099),
    ("F_minus_S", "operational_success"): (-0.048611111111111105, -0.11805555555555555, 0.020833333333333332),
    ("F_minus_S", "private_score"): (-0.05935329861111111, -0.1215359157986111, 0.0),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    result = json.loads((OUTPUT / "primary_effects.json").read_text(encoding="utf-8"))
    for name, record in manifest["outputs"].items():
        observed = sha256(OUTPUT / name)
        if observed != record["sha256"]:
            raise AssertionError(f"Hash mismatch for {name}: {observed}")

    with (OUTPUT / "task_effects.csv").open(encoding="utf-8", newline="") as handle:
        task_rows = list(csv.DictReader(handle))
    with (OUTPUT / "paper_effects.csv").open(encoding="utf-8", newline="") as handle:
        paper_rows = list(csv.DictReader(handle))
    if len(task_rows) != 192 or len(paper_rows) != 96:
        raise AssertionError(
            f"Expected 192 task rows and 96 paper rows; got {len(task_rows)}, {len(paper_rows)}."
        )

    summaries = {
        (row["contrast"], row["endpoint"]): row for row in result["summaries"]
    }
    if set(summaries) != set(EXPECTED):
        raise AssertionError("Unexpected summary contrast/endpoint set.")
    for key, (effect, low, high) in EXPECTED.items():
        observed = summaries[key]
        for field, expected in (
            ("overall_equal_domain_effect", effect),
            ("bootstrap_ci95_low", low),
            ("bootstrap_ci95_high", high),
        ):
            if not math.isclose(float(observed[field]), expected, abs_tol=1e-12):
                raise AssertionError(
                    f"{key} {field}: expected {expected}, observed {observed[field]}"
                )

    if result["design_verification"] != {
        "paper_count": 12,
        "task_count": 24,
        "domain_count": 4,
        "papers_per_domain": 3,
        "tasks_per_paper": 2,
        "blocks_per_task": 6,
        "conditions": {"B": 144, "F": 144, "S": 144},
        "paired_cells": 432,
    }:
        raise AssertionError("Primary design verification payload changed.")
    print("PASS: section 01 primary effects and hashes verified")


if __name__ == "__main__":
    main()
