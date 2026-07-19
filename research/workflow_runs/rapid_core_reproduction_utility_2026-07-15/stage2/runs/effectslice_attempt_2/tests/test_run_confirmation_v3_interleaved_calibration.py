from __future__ import annotations

import json
from pathlib import Path

from run_confirmation_v3_interleaved_calibration import (
    build_records,
    classify_existing_output,
    progress_payload,
)


def preregistration(tmp_path: Path) -> dict:
    families = {}
    schedule = []
    for index, (label, control, replicate_id) in enumerate(
        (
            ("identity", "identity", "i001"),
            ("positive", "planted", "p001"),
            ("negative", "planted", "n001"),
        ),
        start=1,
    ):
        family = tmp_path / label / "family.json"
        family.parent.mkdir(parents=True)
        family.write_text("{}\n", encoding="utf-8")
        families[label] = {
            "path": family.as_posix(),
            "sha256": str(index) * 64,
            "underlying_control": control,
        }
        schedule.append(
            {
                "label": label,
                "underlying_control": control,
                "replicate_id": replicate_id,
                "condition_order": ["B", "F", "S"],
                "stratum": index,
                "global_order_index": index,
            }
        )
    return {
        "registered_block_count": 3,
        "registered_condition_run_count": 9,
        "global_schedule": schedule,
        "families": families,
        "output_roots": {
            label: (tmp_path / "results" / label).as_posix()
            for label in families
        },
    }


def test_build_records_preserves_global_order_and_unique_pair_ids(tmp_path):
    prereg = preregistration(tmp_path)

    records = build_records(prereg, run_root=tmp_path)

    assert [row["label"] for row in records] == [
        "identity",
        "positive",
        "negative",
    ]
    assert [row["global_order_index"] for row in records] == [1, 2, 3]
    assert len({row["pair_id"] for row in records}) == 3
    assert records[1]["pair_id"] == "confirmation-v3:planted:p001"
    assert records[2]["pair_id"] == "confirmation-v3:planted:n001"


def test_existing_output_is_never_replaced(tmp_path):
    absent = tmp_path / "absent"
    assert classify_existing_output(absent) == "pending"

    complete = tmp_path / "complete"
    complete.mkdir()
    (complete / "pair_manifest.json").write_text(
        json.dumps({"completion_status": "complete"}) + "\n", encoding="utf-8"
    )
    assert classify_existing_output(complete) == "preserved"

    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / "pair_manifest.pre_run.json").write_text("{}\n", encoding="utf-8")
    assert classify_existing_output(partial) == "failed"


def test_progress_payload_counts_terminal_states(tmp_path):
    records = build_records(preregistration(tmp_path), run_root=tmp_path)
    records[0]["status"] = "completed"
    records[1]["status"] = "preserved"
    records[2]["status"] = "failed"

    progress = progress_payload("a" * 64, records)

    assert progress["counts"] == {
        "completed": 1,
        "failed": 1,
        "pending": 0,
        "preserved": 1,
        "running": 0,
    }
    assert progress["registered_schedule_length"] == 3
