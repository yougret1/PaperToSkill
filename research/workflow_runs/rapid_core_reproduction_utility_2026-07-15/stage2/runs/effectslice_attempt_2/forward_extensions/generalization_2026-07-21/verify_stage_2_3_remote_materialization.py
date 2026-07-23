from __future__ import annotations

import json
from pathlib import Path

from materialization_verifier_v3 import (
    MaterializationError,
    audit_materialization,
    build_validation_fixture_rows,
    expected_row_specs,
    validate_schedule_rows,
    validate_task_artifacts,
)


ROOT = Path(__file__).resolve().parent

__all__ = [
    "MaterializationError",
    "audit_materialization",
    "build_validation_fixture_rows",
    "expected_row_specs",
    "validate_schedule_rows",
    "validate_task_artifacts",
]


if __name__ == "__main__":
    print(
        json.dumps(
            audit_materialization(ROOT / "materialization_remote_only_2026-07-23"),
            indent=2,
            sort_keys=True,
        )
    )
