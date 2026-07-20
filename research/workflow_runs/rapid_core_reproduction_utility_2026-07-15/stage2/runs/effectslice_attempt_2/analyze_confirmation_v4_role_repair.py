"""Post-hoc compatibility audit for the V4 comparison-role analyzer defect.

The preregistered runners correctly distinguish the comparison role
(`development_triage` for B/F/S) from the formal evidence boundary.  The bound
analyzer accidentally compares both fields to the evidence-boundary value.
This adapter validates both raw fields under their actual schemas and then
normalizes only the in-memory payload consumed by that one erroneous check.
No registered or raw evidence file is modified.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import analyze_confirmation_v4 as analyzer
from run_swe_effectslice import PAIR_ROLE_BY_CONDITIONS


_ORIGINAL_LOAD_JSON = analyzer._load_json
_ROLE_BEARING_LABELS = frozenset({"pair manifest", "run report"})


def _load_json_with_role_semantics(path: Path, label: str) -> dict[str, Any]:
    payload = _ORIGINAL_LOAD_JSON(path, label)
    if label not in _ROLE_BEARING_LABELS:
        return payload

    if payload.get("evidence_boundary") != analyzer.EVIDENCE_BOUNDARY:
        raise analyzer.AnalysisInputError(f"{label} evidence boundary changed")

    results = payload.get("results")
    if not isinstance(results, dict):
        return payload
    conditions = tuple(sorted(results))
    expected_role = PAIR_ROLE_BY_CONDITIONS.get(conditions)
    if expected_role is None:
        return payload
    if payload.get("comparison_role") != expected_role:
        raise analyzer.AnalysisInputError(f"{label} comparison role changed")

    normalized = dict(payload)
    normalized["comparison_role"] = analyzer.EVIDENCE_BOUNDARY
    return normalized


def main() -> int:
    analyzer._load_json = _load_json_with_role_semantics
    try:
        return analyzer.main()
    finally:
        analyzer._load_json = _ORIGINAL_LOAD_JSON


if __name__ == "__main__":
    raise SystemExit(main())
