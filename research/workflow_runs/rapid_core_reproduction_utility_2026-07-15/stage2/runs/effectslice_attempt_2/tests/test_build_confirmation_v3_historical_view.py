from __future__ import annotations

import json
from pathlib import Path

import pytest

from build_confirmation_v3_historical_view import (
    HistoricalViewError,
    PROGRESS_SCHEMA,
    build_view,
    write_view,
)


def progress(records):
    counts = {"completed": 0, "failed": 0, "preserved": 0}
    for record in records:
        counts[record["status"]] += 1
    return {
        "schema_version": PROGRESS_SCHEMA,
        "counts": counts,
        "records": records,
    }


def toolformer_records():
    return [
        {
            "task_key": "toolformer_filter",
            "replicate_id": f"r{index:03d}",
            "status": "completed" if index < 18 else "preserved",
            "output_dir": f"D:/raw/toolformer_filter/r{index:03d}",
            "pair_id": f"toolformer_filter:confirmation-v2:r{index:03d}",
        }
        for index in range(1, 19)
    ]


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value) + "\n", encoding="utf-8", newline="\n")


def test_build_view_filters_records_and_recomputes_counts(tmp_path):
    source = tmp_path / "progress.json"
    records = [
        {
            "task_key": "snap_mfse",
            "replicate_id": "r001",
            "status": "completed",
            "output_dir": "D:/raw/snap_mfse/r001",
            "pair_id": "snap_mfse:confirmation-v2:r001",
        },
        *toolformer_records(),
    ]
    write_json(source, progress(records))

    payload, provenance = build_view(source)
    view = json.loads(payload)

    assert [row["replicate_id"] for row in view["records"]] == [
        f"r{index:03d}" for index in range(1, 19)
    ]
    assert view["counts"] == {"completed": 17, "failed": 0, "preserved": 1}
    assert provenance["source_record_count"] == 19
    assert provenance["selected_record_count"] == 18


def test_write_view_is_idempotent_but_refuses_changed_output(tmp_path):
    source = tmp_path / "progress.json"
    output = tmp_path / "derived" / "view.json"
    provenance = tmp_path / "derived" / "provenance.json"
    write_json(source, progress(toolformer_records()))

    first = write_view(source, output, provenance)
    second = write_view(source, output, provenance)

    assert first == second
    output.write_text("{}\n", encoding="utf-8", newline="\n")
    with pytest.raises(HistoricalViewError, match="existing output differs"):
        write_view(source, output, provenance)


def test_build_view_rejects_reordered_or_incomplete_schedule(tmp_path):
    source = tmp_path / "progress.json"
    records = toolformer_records()
    records[-1]["replicate_id"] = "r017"
    write_json(source, progress(records))

    with pytest.raises(HistoricalViewError, match="missing or reordered"):
        build_view(source)
