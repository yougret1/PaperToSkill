from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROGRESS_SCHEMA = "effectslice-confirmation-v2-progress.v1"
PROVENANCE_SCHEMA = "effectslice-confirmation-v3-historical-view.v1"
STATUSES = ("completed", "failed", "preserved")
TASK_KEY = "toolformer_filter"
EXPECTED_REPLICATE_IDS = [f"r{index:03d}" for index in range(1, 19)]


class HistoricalViewError(ValueError):
    """Raised when the historical progress cannot produce a verified view."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_progress(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        payload = Path(path).read_bytes()
        value = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HistoricalViewError("source progress must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "counts",
        "records",
    }:
        raise HistoricalViewError("source progress fields are invalid")
    if value.get("schema_version") != PROGRESS_SCHEMA:
        raise HistoricalViewError("source progress schema is invalid")
    counts = value.get("counts")
    records = value.get("records")
    if (
        not isinstance(counts, dict)
        or set(counts) != set(STATUSES)
        or any(type(counts[status]) is not int or counts[status] < 0 for status in STATUSES)
        or not isinstance(records, list)
    ):
        raise HistoricalViewError("source progress status data is invalid")
    observed = {status: 0 for status in STATUSES}
    for record in records:
        if not isinstance(record, dict) or record.get("status") not in observed:
            raise HistoricalViewError("source progress contains an invalid record")
        observed[record["status"]] += 1
    if counts != observed:
        raise HistoricalViewError("source progress counts do not match its records")
    return value, payload


def build_view(source_path: Path) -> tuple[bytes, dict[str, Any]]:
    source, source_payload = _load_progress(Path(source_path))
    records = [
        record for record in source["records"] if record.get("task_key") == TASK_KEY
    ]
    if [record.get("replicate_id") for record in records] != EXPECTED_REPLICATE_IDS:
        raise HistoricalViewError("Toolformer historical schedule is missing or reordered")
    counts = {status: 0 for status in STATUSES}
    for record in records:
        counts[record["status"]] += 1
    view = {
        "schema_version": PROGRESS_SCHEMA,
        "counts": counts,
        "records": records,
    }
    view_payload = (
        json.dumps(
            view,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    provenance = {
        "schema_version": PROVENANCE_SCHEMA,
        "source_progress_path": Path(source_path).resolve().as_posix(),
        "source_progress_sha256": _sha256(source_payload),
        "source_record_count": len(source["records"]),
        "selected_task_key": TASK_KEY,
        "selected_record_count": len(records),
        "selected_replicate_ids": EXPECTED_REPLICATE_IDS,
        "view_sha256": _sha256(view_payload),
    }
    return view_payload, provenance


def _write_once(path: Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not destination.is_file() or destination.read_bytes() != payload:
            raise HistoricalViewError(f"existing output differs: {destination}")
        return
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def write_view(source_path: Path, output_path: Path, provenance_path: Path) -> dict[str, Any]:
    source = Path(source_path).resolve()
    output = Path(output_path).resolve()
    provenance_output = Path(provenance_path).resolve()
    if source in {output, provenance_output} or output == provenance_output:
        raise HistoricalViewError("source, view, and provenance paths must be distinct")
    view_payload, provenance = build_view(source)
    provenance = {
        **provenance,
        "view_path": output.as_posix(),
    }
    provenance_payload = (
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    _write_once(output, view_payload)
    _write_once(provenance_output, provenance_payload)
    return provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the Toolformer-only historical V2 progress view for V3 analysis"
    )
    parser.add_argument(
        "--source-progress",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v2"
        / "confirmation_v2_progress.json",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=RUN_ROOT
        / "derived"
        / "confirmation_v3_historical_v2"
        / "toolformer_progress.json",
    )
    parser.add_argument(
        "--provenance-path",
        type=Path,
        default=RUN_ROOT
        / "derived"
        / "confirmation_v3_historical_v2"
        / "toolformer_progress.provenance.json",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = write_view(
        args.source_progress,
        args.output_path,
        args.provenance_path,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
