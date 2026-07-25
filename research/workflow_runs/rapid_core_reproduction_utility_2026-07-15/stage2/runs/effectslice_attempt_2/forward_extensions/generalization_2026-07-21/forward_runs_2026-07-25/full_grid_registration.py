from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


EXPERIMENT_ROOT = Path(__file__).resolve().parent
FORWARD_ROOT = EXPERIMENT_ROOT.parent
if str(FORWARD_ROOT) not in sys.path:
    sys.path.insert(0, str(FORWARD_ROOT))

import output_contract_successor as fg5  # noqa: E402


fg4 = fg5.fg4
fg1 = fg5.fg1

PARENT = fg5.DEFAULT_PARENT
FG2_ROOT = fg5.DEFAULT_FG2
FG3_ROOT = fg5.DEFAULT_FG3
FG4_ROOT = fg5.DEFAULT_FG4
FG5_ROOT = fg5.DEFAULT_SUCCESSOR
CONTRACT_REGISTRY = fg5.DEFAULT_CONTRACTS
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "registration" / "full_grid"

EXPECTED_FG5_BUNDLE = (
    "8ec345c120d8aa4ae432ba77e5a120f81c3ce727bca8a7a94800cade934479a6"
)
REPEAT_IDS = ("FG6", "FG7", "FG8")
ROWS_PER_REPEAT = 1296
TOTAL_REPEAT_ROWS = ROWS_PER_REPEAT * len(REPEAT_IDS)
SCHEDULE_SEED = "effectslice-full-grid-three-repeat-interleave-v1"
SCHEMA_VERSION = "effectslice-full-grid-repetition-registration.v1"
BLOCK_SIZE = 216
BLOCK_REPEAT_ORDER = {
    1: ("FG6", "FG7", "FG8"),
    2: ("FG7", "FG8", "FG6"),
    3: ("FG8", "FG6", "FG7"),
    4: ("FG6", "FG8", "FG7"),
    5: ("FG8", "FG7", "FG6"),
    6: ("FG7", "FG6", "FG8"),
}

EXPECTED_FAMILIES = {
    "alternate_reducers": 96,
    "controls": 144,
    "primary": 432,
    "remote_anchor": 96,
    "required_closed_models": 384,
    "structural_ladder": 144,
}
EXPECTED_MODEL_SLOTS = {
    "claude_opus_4_7": 96,
    "deepseek_primary": 816,
    "gpt_5_5": 96,
    "gpt_5_6_luna": 96,
    "gpt_5_6_sol": 96,
    "gpt_5_6_terra": 96,
}


class RegistrationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RegistrationError(message)


def load_json(path: Path) -> Any:
    return fg1.load_json(fg1.windows_extended_path(path))


def canonical_json(value: object) -> bytes:
    return fg1.canonical_json(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(fg1.windows_extended_path(path))


def atomic_json(path: Path, value: object) -> None:
    fg1.atomic_json(fg1.windows_extended_path(path), value)


def source_verification() -> dict[str, Any]:
    result = fg5.verify_successor(
        PARENT,
        FG2_ROOT,
        FG3_ROOT,
        FG4_ROOT,
        CONTRACT_REGISTRY,
        FG5_ROOT,
    )
    require(result["development_frozen"] is True, "FG5 source is not frozen")
    require(result["bundle_sha256"] == EXPECTED_FG5_BUNDLE, "FG5 bundle changed")
    freeze = load_json(FG5_ROOT / "freeze.json")
    require(
        freeze.get("further_provider_calls_allowed") is False,
        "FG5 source freeze no longer forbids additional source calls",
    )
    return result


def visible_text(request_value: dict[str, Any]) -> str:
    kind, target = fg4.visible_request_text(request_value)
    if kind == "input":
        return str(target)
    return str(target["content"])


def execution_id(repeat_id: str, source_execution_id: str) -> str:
    digest = hashlib.sha256(
        (
            f"{SCHEMA_VERSION}|{repeat_id}|{EXPECTED_FG5_BUNDLE}|"
            f"{source_execution_id}"
        ).encode("utf-8")
    ).hexdigest()[:24]
    return f"{repeat_id.lower()}-exec-{digest}"


def logical_cell_id(source_row: dict[str, Any]) -> str:
    source_execution_id = str(source_row["execution_id"])
    digest = hashlib.sha256(
        f"{EXPECTED_FG5_BUNDLE}|{source_execution_id}".encode("utf-8")
    ).hexdigest()[:24]
    return "fg5-cell-" + digest


def request_summary(value: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "model": value.get("model"),
        "stream": value.get("stream"),
        "temperature": value.get("temperature"),
        "top_p": value.get("top_p"),
        "seed_present": "seed" in value,
    }
    if "max_output_tokens" in value:
        summary["output_limit_field"] = "max_output_tokens"
        summary["output_limit"] = value["max_output_tokens"]
    elif "max_tokens" in value:
        summary["output_limit_field"] = "max_tokens"
        summary["output_limit"] = value["max_tokens"]
    else:
        summary["output_limit_field"] = None
        summary["output_limit"] = None
    return summary


def source_rows_and_manifest() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source_verification()
    schedule = load_json(FG5_ROOT / "global_remote_schedule.json")
    rows = schedule["rows"]
    require(len(rows) == ROWS_PER_REPEAT, "FG5 source row count changed")
    require(
        len({str(row["execution_id"]) for row in rows}) == ROWS_PER_REPEAT,
        "FG5 source execution IDs are not unique",
    )
    require(
        Counter(str(row["execution_family"]) for row in rows) == EXPECTED_FAMILIES,
        "FG5 execution-family counts changed",
    )
    require(
        Counter(str(row["model_slot_id"]) for row in rows) == EXPECTED_MODEL_SLOTS,
        "FG5 model-slot counts changed",
    )

    request_manifest: list[dict[str, Any]] = []
    slot_summaries: dict[str, set[bytes]] = defaultdict(set)
    for source_index, row in enumerate(rows, start=1):
        source_id = str(row["execution_id"])
        request_path = FG5_ROOT / "requests" / f"{source_id}.json"
        require(request_path.is_file(), f"missing FG5 request: {source_id}")
        request_bytes = request_path.read_bytes()
        request_sha = sha256_bytes(request_bytes)
        require(
            request_sha == row["serialized_wire_request_sha256"],
            f"FG5 request SHA changed: {source_id}",
        )
        request_value = json.loads(request_bytes.decode("utf-8", errors="strict"))
        require(isinstance(request_value, dict), f"request is not an object: {source_id}")
        slot = str(row["model_slot_id"])
        spec = fg1.PROVIDER_SPECS[slot]
        require(request_value.get("model") == spec.exact_alias, f"alias changed: {source_id}")
        require(request_value.get("stream") is False, f"streaming changed: {source_id}")
        require("seed" not in request_value, f"unexpected API seed field: {source_id}")
        summary = request_summary(request_value)
        require(summary["output_limit"] == 8192, f"output limit changed: {source_id}")
        require(summary["temperature"] == 0, f"temperature changed: {source_id}")
        require(summary["top_p"] == 1.0, f"top_p changed: {source_id}")
        text = visible_text(request_value)
        visible_sha = sha256_bytes(text.encode("utf-8"))
        slot_summaries[slot].add(canonical_json(summary))
        request_manifest.append(
            {
                "source_sequence_index": source_index,
                "source_fg5_execution_id": source_id,
                "logical_cell_id": logical_cell_id(row),
                "execution_family": row["execution_family"],
                "task_id": row["task_id"],
                "condition": row["condition"],
                "model_slot_id": slot,
                "request_bytes": len(request_bytes),
                "serialized_wire_request_sha256": request_sha,
                "final_model_visible_text_bytes": len(text.encode("utf-8")),
                "final_model_visible_text_sha256": visible_sha,
            }
        )
    request_settings = {
        slot: [json.loads(item.decode("utf-8")) for item in sorted(values)]
        for slot, values in sorted(slot_summaries.items())
    }
    require(set(request_settings) == set(EXPECTED_MODEL_SLOTS), "request slots incomplete")
    return rows, request_manifest, request_settings


def derive_repeat_row(
    source_row: dict[str, Any],
    request_record: dict[str, Any],
    repeat_id: str,
) -> dict[str, Any]:
    row = copy.deepcopy(source_row)
    source_id = str(source_row["execution_id"])
    row["source_fg5_execution_id"] = source_id
    row["logical_cell_id"] = request_record["logical_cell_id"]
    row["repeat_id"] = repeat_id
    row["repeat_sequence_index"] = request_record["source_sequence_index"]
    row["execution_id"] = execution_id(repeat_id, source_id)
    row["final_model_visible_text_sha256"] = request_record[
        "final_model_visible_text_sha256"
    ]
    row["final_model_visible_text_bytes"] = request_record[
        "final_model_visible_text_bytes"
    ]
    row["api_seed_present"] = False
    row["repetition_kind"] = "independent_exact_protocol_repetition"
    return row


def derive_repeat_schedules(
    source_rows: list[dict[str, Any]], request_manifest: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    require(len(source_rows) == len(request_manifest) == ROWS_PER_REPEAT, "source mismatch")
    schedules: dict[str, list[dict[str, Any]]] = {}
    for repeat_id in REPEAT_IDS:
        schedules[repeat_id] = [
            derive_repeat_row(source, record, repeat_id)
            for source, record in zip(source_rows, request_manifest, strict=True)
        ]
    return schedules


def interleaved_dispatch(
    schedules: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    global_index = 0
    require(ROWS_PER_REPEAT == BLOCK_SIZE * len(BLOCK_REPEAT_ORDER), "block layout changed")
    rows_by_repeat_and_block = {
        repeat_id: {
            block_id: [
                row for row in schedules[repeat_id] if int(row["block_id"]) == block_id
            ]
            for block_id in BLOCK_REPEAT_ORDER
        }
        for repeat_id in REPEAT_IDS
    }
    for block_id, repeat_order in BLOCK_REPEAT_ORDER.items():
        for wave_position, repeat_id in enumerate(repeat_order, start=1):
            block_rows = rows_by_repeat_and_block[repeat_id][block_id]
            require(len(block_rows) == BLOCK_SIZE, f"block size changed: {block_id}:{repeat_id}")
            for block_row_index, row in enumerate(block_rows, start=1):
                global_index += 1
                jobs.append(
                    {
                        "global_dispatch_index": global_index,
                        "wave_index": (block_id - 1) * len(REPEAT_IDS) + wave_position,
                        "block_id": block_id,
                        "block_wave_position": wave_position,
                        "block_row_index": block_row_index,
                        "repeat_id": repeat_id,
                        "execution_id": row["execution_id"],
                        "logical_cell_id": row["logical_cell_id"],
                        "source_sequence_index": row["repeat_sequence_index"],
                        "model_slot_id": row["model_slot_id"],
                    }
                )
    require(len(jobs) == TOTAL_REPEAT_ROWS, "global dispatch count changed")
    require(
        len({job["execution_id"] for job in jobs}) == TOTAL_REPEAT_ROWS,
        "global dispatch IDs are not unique",
    )
    require(
        Counter(job["repeat_id"] for job in jobs)
        == {repeat_id: ROWS_PER_REPEAT for repeat_id in REPEAT_IDS},
        "global dispatch repeat counts changed",
    )
    return jobs


def manifest_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name in {"manifest.json", "freeze.json"}:
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def registration_bundle(files: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        canonical_json(
            {
                "schema_version": SCHEMA_VERSION,
                "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                "rows_per_repeat": ROWS_PER_REPEAT,
                "repeat_ids": list(REPEAT_IDS),
                "schedule_seed": SCHEDULE_SEED,
                "files": files,
            }
        )
    )


def build(output: Path) -> dict[str, Any]:
    output = fg1.windows_extended_path(output.resolve())
    require(not output.exists(), f"registration already exists: {output}")
    temporary = output.with_name(output.name + ".tmp")
    require(not temporary.exists(), f"temporary registration exists: {temporary}")
    source_rows, request_manifest, settings = source_rows_and_manifest()
    schedules = derive_repeat_schedules(source_rows, request_manifest)
    jobs = interleaved_dispatch(schedules)
    temporary.mkdir(parents=True)
    try:
        atomic_json(
            temporary / "source_requests.json",
            {
                "schema_version": "effectslice-full-grid-source-requests.v1",
                "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                "registered_rows": ROWS_PER_REPEAT,
                "rows": request_manifest,
            },
        )
        atomic_json(
            temporary / "request_settings.json",
            {
                "schema_version": "effectslice-full-grid-request-settings.v1",
                "api_seed_policy": (
                    "No source request contains an API seed field; describe these as "
                    "independent exact-protocol repetitions, not random-seed runs."
                ),
                "settings_by_model_slot": settings,
            },
        )
        for repeat_id in REPEAT_IDS:
            atomic_json(
                temporary / repeat_id / "schedule.json",
                {
                    "schema_version": SCHEMA_VERSION,
                    "repeat_id": repeat_id,
                    "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                    "registered_rows": ROWS_PER_REPEAT,
                    "rows": schedules[repeat_id],
                },
            )
        atomic_json(
            temporary / "global_dispatch_schedule.json",
            {
                "schema_version": "effectslice-three-repeat-interleave.v1",
                "schedule_seed": SCHEDULE_SEED,
                "registered_jobs": TOTAL_REPEAT_ROWS,
                "jobs": jobs,
            },
        )
        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-full-grid-registration-manifest.v1",
            "created_at_utc": fg1.utc_now(),
            "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
            "repeat_ids": list(REPEAT_IDS),
            "rows_per_repeat": ROWS_PER_REPEAT,
            "total_repeat_rows": TOTAL_REPEAT_ROWS,
            "provider_calls_started": False,
            "frozen": False,
            "files": files,
            "bundle_sha256": registration_bundle(files),
        }
        atomic_json(temporary / "manifest.json", manifest)
        os.replace(temporary, output)
        return manifest
    except Exception:
        if temporary.exists() and not output.exists():
            # Leave the temporary directory for forensic inspection.
            pass
        raise


def verify(output: Path, *, require_frozen: bool = False) -> dict[str, Any]:
    output = fg1.windows_extended_path(output.resolve())
    source_rows, request_manifest, settings = source_rows_and_manifest()
    expected_schedules = derive_repeat_schedules(source_rows, request_manifest)
    manifest = load_json(output / "manifest.json")
    files = manifest_files(output)
    require(files == manifest["files"], "registration file manifest changed")
    require(
        registration_bundle(files) == manifest["bundle_sha256"],
        "registration bundle SHA changed",
    )
    require(
        manifest["source_fg5_bundle_sha256"] == EXPECTED_FG5_BUNDLE,
        "registration source binding changed",
    )
    require(manifest["rows_per_repeat"] == ROWS_PER_REPEAT, "row count changed")
    source_doc = load_json(output / "source_requests.json")
    require(source_doc["rows"] == request_manifest, "source request manifest changed")
    settings_doc = load_json(output / "request_settings.json")
    require(settings_doc["settings_by_model_slot"] == settings, "request settings changed")

    seen: set[str] = set()
    for repeat_id in REPEAT_IDS:
        doc = load_json(output / repeat_id / "schedule.json")
        require(doc["repeat_id"] == repeat_id, f"repeat ID changed: {repeat_id}")
        require(doc["registered_rows"] == ROWS_PER_REPEAT, f"row count changed: {repeat_id}")
        require(doc["rows"] == expected_schedules[repeat_id], f"schedule changed: {repeat_id}")
        repeat_ids = {str(row["execution_id"]) for row in doc["rows"]}
        require(len(repeat_ids) == ROWS_PER_REPEAT, f"duplicate IDs: {repeat_id}")
        require(not (seen & repeat_ids), f"cross-repeat execution ID collision: {repeat_id}")
        seen |= repeat_ids
        require(
            Counter(str(row["execution_family"]) for row in doc["rows"])
            == EXPECTED_FAMILIES,
            f"family counts changed: {repeat_id}",
        )
        require(
            Counter(str(row["model_slot_id"]) for row in doc["rows"])
            == EXPECTED_MODEL_SLOTS,
            f"model counts changed: {repeat_id}",
        )
    dispatch = load_json(output / "global_dispatch_schedule.json")
    expected_jobs = interleaved_dispatch(expected_schedules)
    require(dispatch["jobs"] == expected_jobs, "global dispatch schedule changed")
    require(len(seen) == TOTAL_REPEAT_ROWS, "three-repeat coverage changed")

    freeze_path = output / "freeze.json"
    frozen = freeze_path.is_file()
    require(manifest.get("frozen") is frozen, "freeze state mismatch")
    if require_frozen:
        require(frozen, "registration is not frozen")
    if frozen:
        freeze = load_json(freeze_path)
        require(
            freeze["registration_bundle_sha256"] == manifest["bundle_sha256"],
            "freeze bundle binding changed",
        )
        for record in freeze["source_records"]:
            path = EXPERIMENT_ROOT / record["path"]
            require(path.is_file(), f"missing frozen source: {record['path']}")
            require(sha256_file(path) == record["sha256"], f"frozen source changed: {record['path']}")
    return {
        "status": "passed",
        "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
        "registration_bundle_sha256": manifest["bundle_sha256"],
        "rows_per_repeat": ROWS_PER_REPEAT,
        "total_repeat_rows": TOTAL_REPEAT_ROWS,
        "execution_family_counts_per_repeat": EXPECTED_FAMILIES,
        "model_slot_counts_per_repeat": EXPECTED_MODEL_SLOTS,
        "frozen": frozen,
    }


def freeze(output: Path, source_paths: Iterable[Path]) -> dict[str, Any]:
    result = verify(output)
    output = fg1.windows_extended_path(output.resolve())
    manifest_path = output / "manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("frozen") is False, "registration is already frozen")
    records = []
    for path in source_paths:
        resolved = path.resolve()
        require(resolved.is_file(), f"missing freeze source: {resolved}")
        records.append(
            {
                "path": resolved.relative_to(EXPERIMENT_ROOT).as_posix(),
                "sha256": sha256_file(resolved),
            }
        )
    freeze_doc = {
        "schema_version": "effectslice-full-grid-registration-freeze.v1",
        "frozen_at_utc": fg1.utc_now(),
        "registration_bundle_sha256": result["registration_bundle_sha256"],
        "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
        "rows_per_repeat": ROWS_PER_REPEAT,
        "total_repeat_rows": TOTAL_REPEAT_ROWS,
        "provider_calls_started": False,
        "semantic_rerun_allowed": False,
        "transport_policy": {
            "timeout_seconds": fg1.TIMEOUT_SECONDS,
            "maximum_transport_attempts": fg1.MAXIMUM_TRANSPORT_ATTEMPTS,
            "retry_delays_seconds": list(fg1.RETRY_DELAYS_SECONDS),
            "retryable_http_statuses": sorted(fg1.RETRYABLE_HTTP),
        },
        "private_score_threshold": fg1.PRIVATE_SCORE_THRESHOLD,
        "source_records": records,
    }
    atomic_json(output / "freeze.json", freeze_doc)
    manifest["frozen"] = True
    manifest["frozen_at_utc"] = freeze_doc["frozen_at_utc"]
    atomic_json(manifest_path, manifest)
    return verify(output, require_frozen=True)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify", "freeze"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--freeze-source", type=Path, action="append", default=[])
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        value = build(args.output)
    elif args.command == "verify":
        value = verify(args.output)
    else:
        require(args.freeze_source, "freeze requires at least one --freeze-source")
        value = freeze(args.output, args.freeze_source)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RegistrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
