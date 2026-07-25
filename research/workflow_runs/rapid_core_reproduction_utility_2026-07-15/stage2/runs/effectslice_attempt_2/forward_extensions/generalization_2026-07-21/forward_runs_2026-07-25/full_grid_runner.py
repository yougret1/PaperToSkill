from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import threading
import urllib.parse
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Iterator


EXPERIMENT_ROOT = Path(__file__).resolve().parent
FORWARD_ROOT = EXPERIMENT_ROOT.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))
if str(FORWARD_ROOT) not in sys.path:
    sys.path.insert(0, str(FORWARD_ROOT))

import full_grid_registration as registration  # noqa: E402
import output_contract_successor as fg5  # noqa: E402


fg1 = fg5.fg1

DEFAULT_REGISTRATION = registration.DEFAULT_OUTPUT
DEFAULT_RUNS = EXPERIMENT_ROOT / "runs" / "full_grid"
REPEAT_IDS = registration.REPEAT_IDS
ROWS_PER_REPEAT = registration.ROWS_PER_REPEAT
TOTAL_REPEAT_ROWS = registration.TOTAL_REPEAT_ROWS
SCHEMA_VERSION = "effectslice-full-grid-repetition-runner.v1"


class RunnerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RunnerError(message)


def load_json(path: Path) -> Any:
    return fg1.load_json(fg1.windows_extended_path(path))


def atomic_json(path: Path, value: object) -> None:
    fg1.atomic_json(fg1.windows_extended_path(path), value)


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(fg1.windows_extended_path(path))


def sha256_bytes(value: bytes) -> str:
    return fg1.sha256_bytes(value)


def repeat_schedule(registration_root: Path, repeat_id: str) -> list[dict[str, Any]]:
    registration_root = fg1.windows_extended_path(registration_root)
    doc = load_json(registration_root / repeat_id / "schedule.json")
    require(doc["repeat_id"] == repeat_id, f"repeat registration mismatch: {repeat_id}")
    require(doc["registered_rows"] == ROWS_PER_REPEAT, f"row count mismatch: {repeat_id}")
    return doc["rows"]


def transport_request_id(repeat_id: str, purpose: str, item_id: str) -> str:
    digest = hashlib.sha256(
        (
            f"{SCHEMA_VERSION}|{repeat_id}|{purpose}|{item_id}|"
            f"{registration.EXPECTED_FG5_BUNDLE}"
        ).encode("utf-8")
    ).hexdigest()[:28]
    return f"{repeat_id.lower()}-{purpose}-{digest}"


class RepeatResolver:
    def __init__(self) -> None:
        source_doc = load_json(fg5.DEFAULT_SUCCESSOR / "global_remote_schedule.json")
        self.source_rows = {
            str(row["execution_id"]): row for row in source_doc["rows"]
        }
        require(len(self.source_rows) == ROWS_PER_REPEAT, "FG5 source rows changed")
        self.source_resolver = fg5.OverlayResolver(
            fg5.DEFAULT_PARENT,
            fg5.DEFAULT_FG2,
            fg5.DEFAULT_FG3,
            fg5.DEFAULT_FG4,
            fg5.DEFAULT_SUCCESSOR,
        )

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        source_id = str(row["source_fg5_execution_id"])
        require(source_id in self.source_rows, f"unknown source row: {source_id}")
        source_row = self.source_rows[source_id]
        require(
            source_row["serialized_wire_request_sha256"]
            == row["serialized_wire_request_sha256"],
            f"source request binding changed: {source_id}",
        )
        inputs = self.source_resolver.resolve(source_row)
        require(
            sha256_bytes(inputs.request_bytes) == row["serialized_wire_request_sha256"],
            f"resolved request changed: {source_id}",
        )
        return inputs


def initialize_repeat_manifest(
    registration_root: Path,
    runs_root: Path,
    repeat_id: str,
    credential_metadata: dict[str, Any],
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    runs_root = fg1.windows_extended_path(runs_root)
    run_dir = runs_root / repeat_id
    registration_manifest = load_json(registration_root / "manifest.json")
    expected = {
        "schema_version": SCHEMA_VERSION,
        "repeat_id": repeat_id,
        "registration_bundle_sha256": registration_manifest["bundle_sha256"],
        "source_fg5_bundle_sha256": registration.EXPECTED_FG5_BUNDLE,
        "registered_rows": ROWS_PER_REPEAT,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
        "semantic_rerun_allowed": False,
    }
    path = run_dir / "run_manifest.json"
    if path.exists():
        value = load_json(path)
        for key, expected_value in expected.items():
            require(value.get(key) == expected_value, f"run manifest changed: {repeat_id}:{key}")
        return value
    value = {
        **expected,
        "created_at_utc": fg1.utc_now(),
        "provider_calls_started": False,
    }
    atomic_json(path, value)
    return value


def preflight_id(repeat_id: str, slot_id: str) -> str:
    return transport_request_id(repeat_id, "preflight", slot_id)


def verify_preflight_result(run_dir: Path, repeat_id: str, value: dict[str, Any]) -> None:
    run_dir = fg1.windows_extended_path(run_dir)
    slot_id = str(value.get("model_slot_id"))
    require(slot_id in fg1.PROVIDER_SPECS, "unknown preflight slot")
    require(value.get("repeat_id") == repeat_id, "preflight repeat mismatch")
    require(value.get("exact_alias") == fg1.PROVIDER_SPECS[slot_id].exact_alias, "alias changed")
    require(value.get("logical_request_count") == 1, "preflight request count changed")
    require(value.get("transport_request_id") == preflight_id(repeat_id, slot_id), "preflight ID changed")
    require(value.get("credential_value_recorded") is False, "preflight recorded credential")
    raw_path = value.get("raw_response_path")
    raw_sha = value.get("raw_response_sha256")
    require((raw_path is None) == (raw_sha is None), "preflight raw path/hash mismatch")
    if raw_path is not None:
        path = run_dir / str(raw_path)
        require(path.is_file(), "preflight raw response missing")
        require(sha256_file(path) == raw_sha, "preflight raw response changed")


def run_preflight(
    registration_root: Path,
    runs_root: Path,
    docs_dir: Path,
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    runs_root = fg1.windows_extended_path(runs_root)
    registration.verify(registration_root, require_frozen=True)
    credentials, metadata = fg1.load_credentials(docs_dir.resolve())
    all_results: list[dict[str, Any]] = []
    for repeat_id in REPEAT_IDS:
        run_dir = runs_root / repeat_id
        manifest = initialize_repeat_manifest(
            registration_root, runs_root, repeat_id, metadata
        )
        results: list[dict[str, Any]] = []
        for slot_id, spec in fg1.PROVIDER_SPECS.items():
            final_path = run_dir / "preflight" / f"{slot_id}.json"
            started_path = run_dir / "preflight" / f"{slot_id}.started.json"
            if final_path.exists():
                result = load_json(final_path)
                verify_preflight_result(run_dir, repeat_id, result)
                results.append(result)
                all_results.append(result)
                continue
            require(
                not started_path.exists(),
                f"ambiguous preflight cannot be replayed: {repeat_id}:{slot_id}",
            )
            request_id = preflight_id(repeat_id, slot_id)
            atomic_json(
                started_path,
                {
                    "schema_version": "effectslice-repeat-preflight-start.v1",
                    "repeat_id": repeat_id,
                    "model_slot_id": slot_id,
                    "exact_alias": spec.exact_alias,
                    "transport_request_id": request_id,
                    "started_at_utc": fg1.utc_now(),
                    "maximum_logical_requests": 1,
                    "semantic_rerun_allowed": False,
                },
            )
            manifest["provider_calls_started"] = True
            manifest.setdefault("provider_calls_started_at_utc", fg1.utc_now())
            atomic_json(run_dir / "run_manifest.json", manifest)
            dispatch = fg1.dispatch_request(
                spec,
                credentials[slot_id],
                request_id,
                fg1.preflight_request(spec),
            )
            fg1.persist_attempts(
                run_dir / "preflight",
                f"preflight-{slot_id}",
                dispatch,
                (credentials[slot_id],),
            )
            if dispatch.terminal_body is not None:
                raw_relative = f"preflight/raw/{slot_id}.json"
                fg1.atomic_write(
                    run_dir / "preflight" / "raw" / f"{slot_id}.json",
                    dispatch.terminal_body,
                )
                raw_sha = sha256_bytes(dispatch.terminal_body)
            else:
                raw_relative = None
                raw_sha = None
            status, reason = fg1.preflight_status_from_dispatch(
                fg5.DEFAULT_PARENT, slot_id, dispatch
            )
            result = {
                "schema_version": "effectslice-repeat-live-model-preflight.v1",
                "repeat_id": repeat_id,
                "model_slot_id": slot_id,
                "exact_alias": spec.exact_alias,
                "transport_request_id": request_id,
                "status": status,
                "reason": reason,
                "logical_request_count": 1,
                "transport_attempt_count": len(dispatch.attempts),
                "raw_response_path": raw_relative,
                "raw_response_sha256": raw_sha,
                "credential_value_recorded": False,
                "completed_at_utc": fg1.utc_now(),
            }
            atomic_json(final_path, result)
            verify_preflight_result(run_dir, repeat_id, result)
            results.append(result)
            all_results.append(result)
        summary = {
            "schema_version": "effectslice-repeat-preflight-summary.v1",
            "repeat_id": repeat_id,
            "completed_at_utc": fg1.utc_now(),
            "slots": results,
            "available_slot_count": sum(item["status"] == "available" for item in results),
            "credential_values_recorded": False,
        }
        atomic_json(run_dir / "preflight_summary.json", summary)
    global_summary = {
        "schema_version": "effectslice-three-repeat-preflight-summary.v1",
        "completed_at_utc": fg1.utc_now(),
        "registered_logical_requests": len(REPEAT_IDS) * len(fg1.PROVIDER_SPECS),
        "results": all_results,
        "available_count": sum(item["status"] == "available" for item in all_results),
        "credential_values_recorded": False,
    }
    atomic_json(runs_root / "preflight_summary.json", global_summary)
    return global_summary


def preflight_map(runs_root: Path, repeat_id: str) -> dict[str, str]:
    runs_root = fg1.windows_extended_path(runs_root)
    run_dir = runs_root / repeat_id
    summary = load_json(run_dir / "preflight_summary.json")
    require(summary["repeat_id"] == repeat_id, "preflight summary repeat changed")
    result: dict[str, str] = {}
    for item in summary["slots"]:
        slot_id = str(item["model_slot_id"])
        final = load_json(run_dir / "preflight" / f"{slot_id}.json")
        verify_preflight_result(run_dir, repeat_id, final)
        require(final["status"] == item["status"], "preflight status changed")
        result[slot_id] = str(final["status"])
    require(set(result) == set(fg1.PROVIDER_SPECS), "preflight slots incomplete")
    return result


def progress_summary(
    registration_root: Path, runs_root: Path, repeat_id: str
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    runs_root = fg1.windows_extended_path(runs_root)
    rows = repeat_schedule(registration_root, repeat_id)
    run_dir = runs_root / repeat_id
    outcomes: Counter[str] = Counter()
    by_slot: Counter[str] = Counter()
    completed = 0
    for row in rows:
        path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not path.exists():
            continue
        value = load_json(path)
        fg1.validate_result_row(
            fg5.DEFAULT_PARENT, value, str(row["model_slot_id"])
        )
        require(value["execution_id"] == row["execution_id"], "result ID changed")
        require(value.get("repeat_id") == repeat_id, "result repeat binding changed")
        completed += 1
        outcomes[str(value["terminal_outcome"])] += 1
        by_slot[str(row["model_slot_id"])] += 1
    return {
        "schema_version": "effectslice-full-grid-repeat-progress.v1",
        "updated_at_utc": fg1.utc_now(),
        "repeat_id": repeat_id,
        "registered_rows": ROWS_PER_REPEAT,
        "terminal_rows": completed,
        "remaining_rows": ROWS_PER_REPEAT - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def verify_existing_row(path: Path, row: dict[str, Any]) -> None:
    value = load_json(path)
    require(value.get("execution_id") == row["execution_id"], "resume row ID mismatch")
    require(value.get("source_fg5_execution_id") == row["source_fg5_execution_id"], "source binding changed")
    require(value.get("repeat_id") == row["repeat_id"], "repeat binding changed")
    fg1.validate_result_row(fg5.DEFAULT_PARENT, value, str(row["model_slot_id"]))


@contextlib.contextmanager
def exclusive_run_lock(runs_root: Path) -> Iterator[None]:
    lock_path = runs_root / "global_run.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RunnerError(f"another full-grid runner may be active: {lock_path}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def host_key(slot_id: str) -> str:
    spec = fg1.PROVIDER_SPECS[slot_id]
    return str(urllib.parse.urlparse(spec.endpoint).hostname)


def run(
    registration_root: Path,
    runs_root: Path,
    docs_dir: Path,
    *,
    max_new_rows: int | None,
    workers: int,
    per_host_workers: int,
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    runs_root = fg1.windows_extended_path(runs_root)
    verification = registration.verify(registration_root, require_frozen=True)
    require(1 <= workers <= 6, "workers must be between 1 and 6")
    require(1 <= per_host_workers <= workers, "invalid per-host worker cap")
    if max_new_rows is not None:
        require(max_new_rows > 0, "max-new-rows must be positive")
    credentials, metadata = fg1.load_credentials(docs_dir.resolve())
    manifests = {
        repeat_id: initialize_repeat_manifest(
            registration_root, runs_root, repeat_id, metadata
        )
        for repeat_id in REPEAT_IDS
    }
    preflight = {
        repeat_id: preflight_map(runs_root, repeat_id) for repeat_id in REPEAT_IDS
    }
    schedules = {
        repeat_id: {
            str(row["execution_id"]): row
            for row in repeat_schedule(registration_root, repeat_id)
        }
        for repeat_id in REPEAT_IDS
    }
    dispatch = load_json(registration_root / "global_dispatch_schedule.json")["jobs"]
    resolver = RepeatResolver()
    pending: list[tuple[dict[str, Any], dict[str, Any], fg1.RowInputs]] = []
    for job in dispatch:
        repeat_id = str(job["repeat_id"])
        row = schedules[repeat_id][str(job["execution_id"])]
        run_dir = runs_root / repeat_id
        row_path = run_dir / "rows" / f"{row['execution_id']}.json"
        started_path = run_dir / "dispatch" / f"{row['execution_id']}.started.json"
        terminal_path = run_dir / "dispatch" / f"{row['execution_id']}.terminal.json"
        if row_path.exists():
            verify_existing_row(row_path, row)
            if started_path.exists() and not terminal_path.exists():
                existing = load_json(row_path)
                atomic_json(
                    terminal_path,
                    {
                        "schema_version": "effectslice-repeat-dispatch-terminal.v1",
                        "repeat_id": repeat_id,
                        "execution_id": row["execution_id"],
                        "terminal_outcome": existing["terminal_outcome"],
                        "result_row_sha256": sha256_file(row_path),
                        "recovered_from_terminal_row": True,
                    },
                )
            continue
        if max_new_rows is not None and len(pending) >= max_new_rows:
            break
        require(
            not started_path.exists(),
            f"ambiguous semantic dispatch cannot be replayed: {row['execution_id']}",
        )
        pending.append((job, row, resolver.resolve(row)))

    semaphores = {
        hostname: threading.BoundedSemaphore(per_host_workers)
        for hostname in {host_key(slot) for slot in fg1.PROVIDER_SPECS}
    }

    def execute(
        item: tuple[dict[str, Any], dict[str, Any], fg1.RowInputs]
    ) -> tuple[str, str]:
        job, row, inputs = item
        repeat_id = str(job["repeat_id"])
        execution = str(row["execution_id"])
        slot_id = str(row["model_slot_id"])
        run_dir = runs_root / repeat_id
        row_path = run_dir / "rows" / f"{execution}.json"
        started_path = run_dir / "dispatch" / f"{execution}.started.json"
        terminal_path = run_dir / "dispatch" / f"{execution}.terminal.json"
        # The frozen executor uses row.execution_id for both Idempotency-Key and
        # retry jitter. New repeat-specific execution IDs are therefore also
        # the semantic transport namespace.
        request_id = execution
        atomic_json(
            started_path,
            {
                "schema_version": "effectslice-repeat-dispatch-start.v1",
                "repeat_id": repeat_id,
                "execution_id": execution,
                "source_fg5_execution_id": row["source_fg5_execution_id"],
                "model_slot_id": slot_id,
                "transport_request_id": request_id,
                "serialized_wire_request_sha256": row[
                    "serialized_wire_request_sha256"
                ],
                "started_at_utc": fg1.utc_now(),
                "semantic_rerun_allowed": False,
            },
        )
        if preflight[repeat_id][slot_id] != "available":
            result = fg1.unavailable_row(row, inputs)
        else:
            manifests[repeat_id]["provider_calls_started"] = True
            with semaphores[host_key(slot_id)]:
                result = fg1.execute_row(
                    fg5.DEFAULT_PARENT,
                    run_dir,
                    row,
                    inputs,
                    credentials[slot_id],
                )
        result["repeat_id"] = repeat_id
        result["source_fg5_execution_id"] = row["source_fg5_execution_id"]
        result["logical_cell_id"] = row["logical_cell_id"]
        result["transport_request_id"] = request_id
        result["preflight_status"] = preflight[repeat_id][slot_id]
        result["final_model_visible_text_sha256"] = row[
            "final_model_visible_text_sha256"
        ]
        result["final_model_visible_text_bytes"] = row[
            "final_model_visible_text_bytes"
        ]
        fg1.write_row(run_dir, row, result, fg5.DEFAULT_PARENT)
        atomic_json(
            terminal_path,
            {
                "schema_version": "effectslice-repeat-dispatch-terminal.v1",
                "repeat_id": repeat_id,
                "execution_id": execution,
                "transport_request_id": request_id,
                "terminal_outcome": result["terminal_outcome"],
                "result_row_sha256": sha256_file(row_path),
                "recovered_from_terminal_row": False,
            },
        )
        return repeat_id, execution

    completed = 0
    completed_by_repeat: Counter[str] = Counter()
    errors: list[tuple[str, BaseException]] = []
    with exclusive_run_lock(runs_root):
        for repeat_id in REPEAT_IDS:
            if pending:
                manifests[repeat_id].setdefault("provider_calls_started_at_utc", fg1.utc_now())
            atomic_json(runs_root / repeat_id / "run_manifest.json", manifests[repeat_id])
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures: dict[Future[tuple[str, str]], tuple[dict[str, Any], dict[str, Any], fg1.RowInputs]] = {
                executor.submit(execute, item): item for item in pending
            }
            for future in as_completed(futures):
                _, row, _ = futures[future]
                try:
                    repeat_id, execution = future.result()
                except BaseException as exc:
                    errors.append((str(row["execution_id"]), exc))
                    continue
                completed += 1
                completed_by_repeat[repeat_id] += 1
                if completed % 5 == 0:
                    for rid in REPEAT_IDS:
                        progress = progress_summary(registration_root, runs_root, rid)
                        atomic_json(runs_root / rid / "progress.json", progress)
                    print(
                        f"new_terminal_rows={completed}/{len(pending)} last={repeat_id}:{execution}",
                        flush=True,
                    )
        for repeat_id in REPEAT_IDS:
            progress = progress_summary(registration_root, runs_root, repeat_id)
            progress["new_rows_this_invocation"] = completed_by_repeat[repeat_id]
            progress["global_workers"] = workers
            progress["per_host_workers"] = per_host_workers
            atomic_json(runs_root / repeat_id / "progress.json", progress)
        require(
            not errors,
            "concurrent execution raised after preserving other terminal rows: "
            + "; ".join(
                f"{execution}: {type(exc).__name__}: {exc}"
                for execution, exc in errors
            ),
        )
    final_progress = {
        repeat_id: progress_summary(registration_root, runs_root, repeat_id)
        for repeat_id in REPEAT_IDS
    }
    summary = {
        "schema_version": "effectslice-three-repeat-run-summary.v1",
        "registration_bundle_sha256": verification["registration_bundle_sha256"],
        "new_terminal_rows": completed,
        "repeats": final_progress,
    }
    atomic_json(runs_root / "progress.json", summary)
    return summary


def verify_runs(
    registration_root: Path,
    runs_root: Path,
    *,
    require_complete: bool,
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    runs_root = fg1.windows_extended_path(runs_root)
    reg = registration.verify(registration_root, require_frozen=True)
    repeats: dict[str, Any] = {}
    for repeat_id in REPEAT_IDS:
        progress = progress_summary(registration_root, runs_root, repeat_id)
        if require_complete:
            require(
                progress["terminal_rows"] == ROWS_PER_REPEAT,
                f"repeat is incomplete: {repeat_id}",
            )
        repeats[repeat_id] = progress
    return {
        "status": "passed",
        "registration_bundle_sha256": reg["registration_bundle_sha256"],
        "require_complete": require_complete,
        "repeats": repeats,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "run", "verify"))
    parser.add_argument("--registration", type=Path, default=DEFAULT_REGISTRATION)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--per-host-workers", type=int, default=2)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command in {"preflight", "run"}:
        require(args.docs_dir is not None, "--docs-dir is required")
    if args.command == "preflight":
        value = run_preflight(args.registration, args.runs, args.docs_dir)
    elif args.command == "run":
        value = run(
            args.registration,
            args.runs,
            args.docs_dir,
            max_new_rows=args.max_new_rows,
            workers=args.workers,
            per_host_workers=args.per_host_workers,
        )
    else:
        value = verify_runs(
            args.registration,
            args.runs,
            require_complete=args.require_complete,
        )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RunnerError, registration.RegistrationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
