from __future__ import annotations

import json
from pathlib import Path

import pytest

import analyze_confirmation_v5 as analyzer
from analyze_confirmation_v5_role_repair import _load_json_with_role_semantics


def _write_payload(path: Path, *, role: str, boundary: str) -> None:
    path.write_text(
        json.dumps(
            {
                "comparison_role": role,
                "evidence_boundary": boundary,
                "results": {"B": {}, "F": {}, "S": {}},
            }
        ),
        encoding="utf-8",
    )


def test_validates_distinct_role_and_boundary_before_normalizing(tmp_path: Path):
    path = tmp_path / "pair_manifest.json"
    _write_payload(
        path,
        role="development_triage",
        boundary=analyzer.EVIDENCE_BOUNDARY,
    )

    payload = _load_json_with_role_semantics(path, "pair manifest")

    assert payload["comparison_role"] == analyzer.EVIDENCE_BOUNDARY
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["comparison_role"] == "development_triage"


@pytest.mark.parametrize(
    ("role", "boundary", "message"),
    [
        ("wrong", analyzer.EVIDENCE_BOUNDARY, "comparison role changed"),
        ("development_triage", "wrong", "evidence boundary changed"),
    ],
)
def test_rejects_invalid_raw_semantics(
    tmp_path: Path,
    role: str,
    boundary: str,
    message: str,
):
    path = tmp_path / "run_report.json"
    _write_payload(path, role=role, boundary=boundary)

    with pytest.raises(analyzer.AnalysisInputError, match=message):
        _load_json_with_role_semantics(path, "run report")


def test_does_not_normalize_unrelated_payloads(tmp_path: Path):
    path = tmp_path / "other.json"
    _write_payload(path, role="development_triage", boundary="other")

    payload = _load_json_with_role_semantics(path, "other")

    assert payload["comparison_role"] == "development_triage"
    assert payload["evidence_boundary"] == "other"
