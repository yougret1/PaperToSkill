from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

import analyze_confirmation_v5 as analyzer  # noqa: E402
import build_confirmation_v5 as builder  # noqa: E402
import run_confirmation_v5 as scheduler  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_digest(case: dict) -> str:
    payload = {key: value for key, value in case.items() if key not in {"case_id", "seed"}}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _resolve(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else RUN_ROOT / path


def test_v5_decision_boundaries_are_frozen_from_v4():
    assert builder.finite_schedule_decision({"B": 2, "F": 16, "S": 16})["passed"]
    assert not builder.finite_schedule_decision({"B": 3, "F": 18, "S": 18})[
        "passed"
    ]
    assert not builder.finite_schedule_decision({"B": 0, "F": 15, "S": 18})[
        "passed"
    ]
    assert not builder.finite_schedule_decision({"B": 0, "F": 18, "S": 15})[
        "passed"
    ]


def test_v5_builder_registers_natural_candidate_and_fresh_cases(tmp_path):
    output = tmp_path / "registration"
    registration = builder.build_registration(output)
    preregistration = output / "preregistration.json"
    digest = _sha256(preregistration)

    assert registration["registered_block_count"] == 18
    assert registration["registered_condition_run_count"] == 54
    assert set(registration["families"]) == {"toolformer_natural"}
    assert len(registration["global_interleaved_schedule"]) == 18
    assert {
        row["family_key"] for row in registration["global_interleaved_schedule"]
    } == {"toolformer_natural"}

    family_record = registration["families"]["toolformer_natural"]
    family_path = _resolve(family_record["path"])
    family = json.loads(family_path.read_text(encoding="utf-8"))
    assert _sha256(family_path) == family_record["sha256"]
    assert family["case_block"] == "confirmation_v5"
    assert family["candidate_role"] == "natural_registered_reducer_candidate"
    assert family["candidate_origin"] == (
        "preexisting_dependency_closed_prefix_reducer_output"
    )
    assert family["retained_atom_ids"] == ["T01", "T02", "T03", "T04"]
    assert family["strict_subset"] is True
    assert family["expected_admission"] is True
    assert family["prior_private_results_used_for_v5_selection"] is True
    assert family["v5_private_results_used_for_selection"] is False

    selected = _resolve(family["selected_artifact_path"]).read_text(encoding="utf-8")
    full = _resolve(family["full_artifact_path"]).read_text(encoding="utf-8")
    assert "(`T04`)" in selected and "(`T05`)" not in selected
    assert "(`T05`)" in full
    assert _resolve(family["reducer_source_path"]).is_file()
    assert _resolve(family["reducer_registry_path"]).is_file()
    assert _resolve(family["prior_v4_summary_path"]).is_file()

    registry = json.loads(
        _resolve(family["case_registry_path"]).read_text(encoding="utf-8")
    )
    current = registry["blocks"]["confirmation_v5"]
    earlier = [
        case
        for name, cases in registry["blocks"].items()
        if name != "confirmation_v5"
        for case in cases
    ]
    assert len(current) == 64
    assert not ({case["case_id"] for case in current} & {case["case_id"] for case in earlier})
    assert not ({case["seed"] for case in current} & {case["seed"] for case in earlier})
    assert not ({_payload_digest(case) for case in current} & {_payload_digest(case) for case in earlier})

    loaded_registration, families, loaded_digest = (
        scheduler.load_and_verify_registration(
            preregistration,
            digest,
            allow_test_registration=True,
        )
    )
    assert loaded_registration["registered_condition_run_count"] == 54
    assert set(families) == {"toolformer_natural"}
    assert loaded_digest == digest

    first = loaded_registration["global_interleaved_schedule"][0]
    args = scheduler.build_run_namespace(
        family_key="toolformer_natural",
        family_path=families["toolformer_natural"]["path"],
        family=families["toolformer_natural"]["family"],
        schedule_row=first,
        output_root=tmp_path / "results",
    )
    assert args.case_block == "confirmation_v5"
    assert args.pair_id.startswith("confirmation-v5:toolformer_natural:")
    assert args.slice_candidate_id == "toolformer_prefix_04_v5"
    assert analyzer.DEFAULT_ANALYSIS_PATH.parts[-2:] == (
        "confirmation_v5",
        "analysis.json",
    )

    with pytest.raises(ValueError, match="digest"):
        scheduler.load_and_verify_registration(
            preregistration,
            "0" * 64,
            allow_test_registration=True,
        )
    with pytest.raises(FileExistsError):
        builder.build_registration(output)


def test_v5_scheduler_rejects_excess_parallelism_before_execution(tmp_path):
    with pytest.raises(ValueError, match="max_workers"):
        scheduler.run_schedule(
            preregistration_path=tmp_path / "missing.json",
            expected_preregistration_sha256="0" * 64,
            max_workers=3,
            allow_test_injection=True,
        )
