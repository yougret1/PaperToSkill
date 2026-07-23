from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
MATERIALIZATION = Path(
    "\\\\?\\" + str(FORWARD_ROOT / "materialization_remote_only_2026-07-23")
)
sys.path.insert(0, str(FORWARD_ROOT))

import build_stage_2_3_materialization as builder  # noqa: E402
import materialization_verifier_v3 as verifier  # noqa: E402
from stage23_result_canonicalizer import canonicalize  # noqa: E402


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_remote_anchor_passes_full_audit() -> None:
    assert verifier.audit_materialization(MATERIALIZATION) == {
        "status": "passed",
        "rows": 1296,
        "family_counts": {
            "primary": 432,
            "controls": 144,
            "structural_ladder": 144,
            "alternate_reducers": 96,
            "required_closed_models": 384,
            "remote_anchor": 96,
        },
    }


def test_anchor_has_one_remote_schedule_and_no_provider_calls() -> None:
    schedule = load_json(MATERIALIZATION / "global_remote_schedule.json")
    anchor = load_json(MATERIALIZATION / "final_anchor_manifest.json")
    assert len(schedule["rows"]) == 1296
    assert not (MATERIALIZATION / "global_local_anchor_schedule.json").exists()
    assert anchor["provider_calls_started"] is False
    remote_anchor = [
        row for row in schedule["rows"] if row["execution_family"] == "remote_anchor"
    ]
    assert len(remote_anchor) == 96
    assert {row["model_slot_id"] for row in remote_anchor} == {"gpt_5_6_luna"}


def test_luna_result_is_remote_only_and_strictly_schema_valid() -> None:
    fixture = {
        "execution_id": "golden-luna",
        "model_slot_id": "gpt_5_6_luna",
        "dispatch_state": "completed_body",
        "provider_response": {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"implementation":"def solve(case):\\n    return {}"}',
                        }
                    ],
                }
            ],
            "status": "completed",
            "incomplete_details": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 8,
                "total_tokens": 20,
                "input_tokens_details": {"cached_tokens": 0},
            },
        },
        "submission_valid": True,
        "private_score": 1.0,
        "scored_outcome": "operational_success",
        "candidate_artifact_bytes": 10,
        "candidate_artifact_cl100k_tokens": 3,
        "canonical_model_visible_payload_bytes": 100,
    }
    row = canonicalize(fixture)
    _, _, _, contract = verifier.preregistrations()
    schema = contract["result_canonicalization_contract"]["result_row_json_schema"]
    verifier._validate_registered_schema(row, schema)
    assert "generated_token_ids" not in row
    row["generated_token_ids"] = []
    with pytest.raises(verifier.MaterializationError, match="additional fields"):
        verifier._validate_registered_schema(row, schema)


def test_bound_path_rejects_parent_traversal() -> None:
    with pytest.raises(verifier.MaterializationError, match="escapes"):
        verifier._safe_bound_path(MATERIALIZATION, "../outside.json")


def test_passing_anchor_cannot_be_replaced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(builder, "MATERIALIZATION", MATERIALIZATION)
    monkeypatch.setattr(
        builder,
        "audit_materialization",
        lambda _: {"status": "passed", "rows": 1296},
    )
    with pytest.raises(RuntimeError, match="passes audit"):
        builder.build(replace_unanchored=False, replace_invalid=True)
