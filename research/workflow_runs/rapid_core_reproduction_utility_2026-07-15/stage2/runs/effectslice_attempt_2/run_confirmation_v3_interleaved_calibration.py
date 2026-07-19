from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

import build_confirmation_v3_interleaved_calibration as registration
import run_toolformer_filter_confirmation_v3 as bound_runner
from confirmation_transport_v3 import ProviderTransport


RUN_ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "effectslice-v3-interleaved-calibration-progress.v1"
API_KEY_ENV = "EFFECTSLICE_DEEPSEEK_API_KEY"
BASE_URL_ENV = "EFFECTSLICE_DEEPSEEK_BASE_URL"


class InterleavedExecutionError(ValueError):
    """Raised when the registered interleaved schedule cannot be executed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _resolve(stored: str, run_root: Path = RUN_ROOT) -> Path:
    path = Path(stored)
    return path.resolve() if path.is_absolute() else (Path(run_root) / path).resolve()


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InterleavedExecutionError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise InterleavedExecutionError(f"{label} must be a JSON object")
    return value


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
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


def classify_existing_output(output_dir: Path) -> str:
    path = Path(output_dir)
    if not path.exists():
        return "pending"
    if not path.is_dir():
        return "failed"
    manifest = path / "pair_manifest.json"
    if not manifest.is_file():
        return "failed"
    try:
        value = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "failed"
    return "preserved" if value.get("completion_status") == "complete" else "failed"


def build_records(
    preregistration: dict[str, Any], *, run_root: Path = RUN_ROOT
) -> list[dict[str, Any]]:
    families = preregistration.get("families")
    roots = preregistration.get("output_roots")
    schedule = preregistration.get("global_schedule")
    if not all(isinstance(value, dict) for value in (families, roots)):
        raise InterleavedExecutionError("registered family or output roots are invalid")
    if not isinstance(schedule, list):
        raise InterleavedExecutionError("registered schedule is invalid")
    records = []
    for row in schedule:
        if not isinstance(row, dict):
            raise InterleavedExecutionError("registered schedule row is invalid")
        label = row.get("label")
        family = families.get(label)
        root = roots.get(label)
        if not isinstance(family, dict) or not isinstance(root, str):
            raise InterleavedExecutionError("registered schedule label is invalid")
        control = family.get("underlying_control")
        if control != row.get("underlying_control"):
            raise InterleavedExecutionError("registered control label is inconsistent")
        replicate_id = row.get("replicate_id")
        output_dir = _resolve(root, run_root) / str(replicate_id)
        records.append(
            {
                "global_order_index": row["global_order_index"],
                "stratum": row["stratum"],
                "label": label,
                "control": control,
                "replicate_id": replicate_id,
                "condition_execution_order": list(row["condition_order"]),
                "family_path": _resolve(family["path"], run_root).as_posix(),
                "family_sha256": family["sha256"],
                "output_dir": output_dir.as_posix(),
                "pair_id": f"confirmation-v3:{control}:{replicate_id}",
                "status": "pending",
                "failure_classification": None,
            }
        )
    if len(records) != preregistration.get("registered_block_count"):
        raise InterleavedExecutionError("registered block count is inconsistent")
    if len({row["pair_id"] for row in records}) != len(records):
        raise InterleavedExecutionError("registered pair IDs are not unique")
    return records


def progress_payload(
    preregistration_sha256: str, records: list[dict[str, Any]]
) -> dict[str, Any]:
    states = ("completed", "failed", "pending", "preserved", "running")
    counts = {state: sum(row.get("status") == state for row in records) for state in states}
    if sum(counts.values()) != len(records):
        raise InterleavedExecutionError("progress contains an unknown state")
    return {
        "schema_version": SCHEMA_VERSION,
        "preregistration_sha256": preregistration_sha256,
        "registered_schedule_length": len(records),
        "counts": counts,
        "records": records,
    }


def _merge_existing_progress(
    records: list[dict[str, Any]],
    preregistration_sha256: str,
) -> list[dict[str, Any]]:
    by_pair = {row["pair_id"]: row for row in records}
    if registration.PROGRESS_PATH.is_file():
        existing = _json_object(registration.PROGRESS_PATH, "existing progress")
        if existing.get("preregistration_sha256") != preregistration_sha256:
            raise InterleavedExecutionError("existing progress registration differs")
        old_records = existing.get("records")
        if not isinstance(old_records, list):
            raise InterleavedExecutionError("existing progress records are invalid")
        for old in old_records:
            pair_id = old.get("pair_id") if isinstance(old, dict) else None
            if pair_id not in by_pair:
                raise InterleavedExecutionError("existing progress has an extra pair")
            if old.get("status") in {"completed", "failed", "preserved"}:
                current = by_pair[pair_id]
                for field in (
                    "label",
                    "control",
                    "replicate_id",
                    "family_sha256",
                    "output_dir",
                    "condition_execution_order",
                ):
                    if old.get(field) != current.get(field):
                        raise InterleavedExecutionError(
                            "existing progress record differs from registration"
                        )
                current["status"] = old["status"]
                current["failure_classification"] = old.get(
                    "failure_classification"
                )
    for record in records:
        if record["status"] in {"completed", "failed", "preserved"}:
            continue
        existing_state = classify_existing_output(Path(record["output_dir"]))
        if existing_state != "pending":
            record["status"] = existing_state
            record["failure_classification"] = (
                None
                if existing_state == "preserved"
                else "preserved_partial_output"
            )
    return records


def provider_preflight() -> dict[str, Any]:
    base_url = os.environ.get(BASE_URL_ENV, "")
    api_key = os.environ.get(API_KEY_ENV, "")
    if not base_url or not api_key:
        raise InterleavedExecutionError("provider environment is incomplete")
    transport = ProviderTransport(
        base_url=base_url,
        api_key=api_key,
        model_alias=registration.legacy.REGISTERED_MODEL_ALIAS,
        wire_api=registration.legacy.REGISTERED_WIRE_API,
        max_tokens=registration.legacy.REGISTERED_MAX_TOKENS,
        timeout_seconds=registration.legacy.REGISTERED_TIMEOUT_SECONDS,
        max_attempts=registration.legacy.REGISTERED_MAX_ATTEMPTS,
        retry_delay_seconds=registration.legacy.REGISTERED_RETRY_DELAY_SECONDS,
    )
    result = transport(
        prompt='Return exactly one JSON action: {"action":"submit"}.',
        retry_lineage_id="confirmation-v3-interleaved:generic-marker",
        turn_index=1,
    )
    return {
        "status": result.status,
        "attempts": result.attempts,
        "provider_model_id": result.provider_model_id,
        "provider_response_id_present": bool(result.provider_response_id),
        "valid": bool(
            result.status == "ok"
            and result.provider_model_id
            == registration.legacy.REGISTERED_MODEL_ALIAS
            and result.provider_response_id
        ),
    }


def _runner_args(record: dict[str, Any]) -> argparse.Namespace:
    return argparse.Namespace(
        family=Path(record["family_path"]),
        replicate_id=record["replicate_id"],
        output_dir=Path(record["output_dir"]),
        model_alias=registration.legacy.REGISTERED_MODEL_ALIAS,
        base_url_env=BASE_URL_ENV,
        api_key_env=API_KEY_ENV,
        timeout_seconds=registration.legacy.REGISTERED_TIMEOUT_SECONDS,
        scorer_timeout_seconds=300.0,
        max_tokens=registration.legacy.REGISTERED_MAX_TOKENS,
        max_attempts=registration.legacy.REGISTERED_MAX_ATTEMPTS,
        retry_delay_seconds=registration.legacy.REGISTERED_RETRY_DELAY_SECONDS,
    )


def _run_record(record: dict[str, Any]) -> tuple[str, str | None]:
    try:
        result = bound_runner.run_bundle(_runner_args(record))
    except Exception as exc:
        return "failed", type(exc).__name__
    if result.get("pair_id") != record["pair_id"]:
        return "failed", "pair_identity_mismatch"
    return "completed", None


def _write_progress(preregistration_sha256: str, records: list[dict[str, Any]]) -> None:
    _write_json_atomic(
        registration.PROGRESS_PATH,
        progress_payload(preregistration_sha256, copy.deepcopy(records)),
    )


def execute(*, max_workers: int) -> dict[str, Any]:
    if max_workers not in {1, 2}:
        raise InterleavedExecutionError("max_workers must be 1 or 2")
    preregistration = _json_object(
        registration.PREREGISTRATION_PATH, "preregistration"
    )
    preregistration_sha = _sha256(registration.PREREGISTRATION_PATH.read_bytes())
    if registration.EXECUTION_LOCK_PATH.exists():
        registration.audit_registration(allow_execution_started=True)
        lock = _json_object(registration.EXECUTION_LOCK_PATH, "execution lock")
        if lock.get("preregistration_sha256") != preregistration_sha:
            raise InterleavedExecutionError("execution lock registration differs")
    else:
        registration.audit_registration(allow_execution_started=False)
        registration.RESULT_ROOT.mkdir(parents=True, exist_ok=False)
        _write_json_atomic(
            registration.EXECUTION_LOCK_PATH,
            {
                "schema_version": (
                    "effectslice-v3-interleaved-calibration-execution-lock.v1"
                ),
                "preregistration_sha256": preregistration_sha,
                "registered_schedule_sha256": _sha256(
                    json.dumps(
                        preregistration["global_schedule"],
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ),
                "provider_execution_started": True,
                "no_replacement_replicates": True,
            },
        )

    records = _merge_existing_progress(
        build_records(preregistration), preregistration_sha
    )
    _write_progress(preregistration_sha, records)
    pending = iter([row for row in records if row["status"] == "pending"])
    futures: dict[concurrent.futures.Future, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(max_workers):
            try:
                record = next(pending)
            except StopIteration:
                break
            record["status"] = "running"
            _write_progress(preregistration_sha, records)
            futures[executor.submit(_run_record, copy.deepcopy(record))] = record
        while futures:
            done, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in done:
                record = futures.pop(future)
                status, failure = future.result()
                record["status"] = status
                record["failure_classification"] = failure
                _write_progress(preregistration_sha, records)
                try:
                    next_record = next(pending)
                except StopIteration:
                    continue
                next_record["status"] = "running"
                _write_progress(preregistration_sha, records)
                futures[executor.submit(_run_record, copy.deepcopy(next_record))] = (
                    next_record
                )
    final = progress_payload(preregistration_sha, records)
    if final["counts"]["pending"] or final["counts"]["running"]:
        raise InterleavedExecutionError("registered schedule did not terminate")
    return final


def status() -> dict[str, Any]:
    if not registration.PROGRESS_PATH.is_file():
        return {"status": "not_started"}
    progress = _json_object(registration.PROGRESS_PATH, "progress")
    return {
        "status": "started",
        "counts": progress.get("counts"),
        "registered_schedule_length": progress.get("registered_schedule_length"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the registered V3 interleaved calibration schedule"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preflight")
    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--max-workers", type=int, default=2)
    subparsers.add_parser("status")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "preflight":
        result = provider_preflight()
    elif args.command == "execute":
        result = execute(max_workers=args.max_workers)
    else:
        result = status()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
