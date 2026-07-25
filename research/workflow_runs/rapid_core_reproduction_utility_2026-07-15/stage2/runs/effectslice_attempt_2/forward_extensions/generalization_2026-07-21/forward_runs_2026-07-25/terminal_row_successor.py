from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator

import controls_v2 as controls
import full_grid_runner as grid


fg1 = grid.fg1
fg5 = grid.fg5

ROOT = Path(__file__).resolve().parent
DEFAULT_FREEZE = ROOT / "terminal_row_successor_freeze.json"
DEFAULT_RECOVERY_REPORT = ROOT / "terminal_row_successor_recovery.json"
SUCCESSOR_TEST = ROOT / "tests" / "test_terminal_row_successor.py"
EXPECTED_JOINT_FREEZE_SHA256 = (
    "da5148475835251551e9ad5075d24c4c97bde2282b08bf3dfe074fbe92174ee1"
)
SCHEMA_VERSION = "effectslice-terminal-row-successor.v1"
RESULT_FIELDS = (
    "execution_id",
    "terminal_outcome",
    "termination_reason",
    "provider_finish_reason",
    "row_valid",
    "condition_success",
    "private_score",
    "raw_response_path",
    "raw_response_sha256",
    "canonical_output_path",
    "canonical_output_sha256",
    "hard_contract_vector",
    "attempts",
    "candidate_artifact_bytes",
    "candidate_artifact_cl100k_tokens",
    "canonical_model_visible_payload_bytes",
    "provider_reported_input_tokens",
    "provider_reported_output_tokens",
    "provider_reported_total_tokens",
    "provider_reported_cached_input_tokens",
    "provider_usage_missing_reason",
    "terminal_attempt_elapsed_ms",
    "total_execution_elapsed_ms",
    "retry_sleep_elapsed_ms",
    "retry_overhead_ms",
)
CONTROL_BINDINGS = (
    "control_arm",
    "control_repetition",
    "mutation_id",
    "source_fg5_execution_id",
)
GRID_BINDINGS = (
    "repeat_id",
    "source_fg5_execution_id",
    "logical_cell_id",
    "final_model_visible_text_sha256",
    "final_model_visible_text_bytes",
)
RUNNER_EXTRAS = set(CONTROL_BINDINGS) | set(GRID_BINDINGS) | {
    "transport_request_id",
    "preflight_status",
}
MAX_TRANSPORT_CYCLES_PER_INVOCATION = 3


class SuccessorError(RuntimeError):
    pass


class DeferredTransportError(SuccessorError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorError(message)


def xpath(path: Path) -> Path:
    return fg1.windows_extended_path(path)


def load_json(path: Path) -> Any:
    return fg1.load_json(xpath(path))


def atomic_json(path: Path, value: object) -> None:
    fg1.atomic_json(xpath(path), value)


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(xpath(path))


def utc_now() -> str:
    return fg1.utc_now()


def schedule_maps() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    control_rows = load_json(controls.DEFAULT_REGISTRATION / "schedule.json")["rows"]
    controls_by_id = {str(row["execution_id"]): row for row in control_rows}
    grid_by_id: dict[str, dict[str, Any]] = {}
    for repeat_id in grid.REPEAT_IDS:
        for row in grid.repeat_schedule(grid.DEFAULT_REGISTRATION, repeat_id):
            grid_by_id[str(row["execution_id"])] = row
    require(len(controls_by_id) == controls.REGISTERED_ROWS == 96, "control schedule changed")
    require(len(grid_by_id) == grid.TOTAL_REPEAT_ROWS == 3 * 1296, "grid schedule changed")
    return controls_by_id, grid_by_id


def run_dir_for(row: dict[str, Any]) -> Path:
    if "repeat_id" in row:
        return grid.DEFAULT_RUNS / str(row["repeat_id"])
    return controls.DEFAULT_RUN


def started_ids(run_dir: Path) -> list[str]:
    dispatch_dir = xpath(run_dir / "dispatch")
    if not dispatch_dir.exists():
        return []
    return sorted(
        path.name.removesuffix(".started.json")
        for path in dispatch_dir.glob("*.started.json")
    )


def artifact_manifest(run_dir: Path, execution_id: str) -> dict[str, str]:
    run_dir = xpath(run_dir)
    candidates = [
        run_dir / "attempts" / f"{execution_id}.json",
        run_dir / "raw" / f"{execution_id}.json",
        run_dir / "canonical" / f"{execution_id}.txt",
        run_dir / "scoring" / f"{execution_id}.json",
        run_dir / "scoring" / f"{execution_id}.json.gz",
    ]
    body_dir = run_dir / "attempt_bodies" / execution_id
    if body_dir.exists():
        candidates.extend(sorted(body_dir.glob("attempt_*.bin")))
    result: dict[str, str] = {}
    for path in candidates:
        if path.exists():
            relative = path.relative_to(run_dir).as_posix()
            result[relative] = sha256_file(path)
    return dict(sorted(result.items()))


def classify_started_row(run_dir: Path, execution_id: str) -> str:
    artifacts = artifact_manifest(run_dir, execution_id)
    if f"attempts/{execution_id}.json" in artifacts:
        required_prefixes = (
            f"raw/{execution_id}.json",
            f"canonical/{execution_id}.txt",
        )
        require(all(key in artifacts for key in required_prefixes), f"partial persisted response: {execution_id}")
        require(
            any(key.startswith(f"scoring/{execution_id}.json") for key in artifacts),
            f"missing scoring evidence: {execution_id}",
        )
        return "persisted_response"
    require(not artifacts, f"unclassified partial artifacts: {execution_id}")
    return "started_marker_only"


def build_freeze(path: Path = DEFAULT_FREEZE) -> dict[str, Any]:
    require(not path.exists(), f"successor freeze already exists: {path}")
    require(sha256_file(ROOT / "joint_freeze.json") == EXPECTED_JOINT_FREEZE_SHA256, "joint freeze changed")
    controls_by_id, grid_by_id = schedule_maps()
    affected: list[dict[str, Any]] = []
    for label, rows, run_dir in (
        ("Controls-v2", controls_by_id, controls.DEFAULT_RUN),
        ("FG6", grid_by_id, grid.DEFAULT_RUNS / "FG6"),
        ("FG7", grid_by_id, grid.DEFAULT_RUNS / "FG7"),
        ("FG8", grid_by_id, grid.DEFAULT_RUNS / "FG8"),
    ):
        for execution_id in started_ids(run_dir):
            require(execution_id in rows, f"started ID is not registered: {execution_id}")
            row_path = xpath(run_dir / "rows" / f"{execution_id}.json")
            terminal_path = xpath(run_dir / "dispatch" / f"{execution_id}.terminal.json")
            require(not row_path.exists(), f"row already terminal before successor freeze: {execution_id}")
            require(not terminal_path.exists(), f"terminal marker exists without row: {execution_id}")
            affected.append(
                {
                    "experiment": label,
                    "execution_id": execution_id,
                    "recovery_class": classify_started_row(run_dir, execution_id),
                    "started_marker_sha256": sha256_file(
                        run_dir / "dispatch" / f"{execution_id}.started.json"
                    ),
                    "persisted_artifacts": artifact_manifest(run_dir, execution_id),
                }
            )
    counts = Counter(item["experiment"] for item in affected)
    classes = Counter(item["recovery_class"] for item in affected)
    require(counts == {"Controls-v2": 12, "FG6": 18}, f"unexpected affected rows: {dict(counts)}")
    require(classes == {"persisted_response": 26, "started_marker_only": 4}, f"unexpected recovery classes: {dict(classes)}")
    document = {
        "schema_version": "effectslice-terminal-row-successor-freeze.v1",
        "created_at_utc": utc_now(),
        "forward_only": True,
        "no_semantic_replay_of_started_rows": True,
        "joint_freeze_sha256": EXPECTED_JOINT_FREEZE_SHA256,
        "successor_source_sha256": sha256_file(Path(__file__).resolve()),
        "successor_test_sha256": sha256_file(SUCCESSOR_TEST),
        "registered_rows": {
            "Controls-v2": 96,
            "FG6": 1296,
            "FG7": 1296,
            "FG8": 1296,
        },
        "affected_row_counts": dict(sorted(counts.items())),
        "recovery_class_counts": dict(sorted(classes.items())),
        "affected_rows": sorted(affected, key=lambda item: (item["experiment"], item["execution_id"])),
    }
    atomic_json(path, document)
    return document


def verify_freeze(path: Path = DEFAULT_FREEZE) -> dict[str, Any]:
    freeze = load_json(path)
    require(freeze["schema_version"] == "effectslice-terminal-row-successor-freeze.v1", "freeze schema changed")
    require(freeze["joint_freeze_sha256"] == EXPECTED_JOINT_FREEZE_SHA256, "freeze parent binding changed")
    require(sha256_file(ROOT / "joint_freeze.json") == EXPECTED_JOINT_FREEZE_SHA256, "joint freeze changed")
    require(freeze["successor_source_sha256"] == sha256_file(Path(__file__).resolve()), "successor source changed after freeze")
    require(freeze["successor_test_sha256"] == sha256_file(SUCCESSOR_TEST), "successor tests changed after freeze")
    controls_by_id, grid_by_id = schedule_maps()
    for item in freeze["affected_rows"]:
        execution_id = str(item["execution_id"])
        row = controls_by_id.get(execution_id) or grid_by_id.get(execution_id)
        require(row is not None, f"frozen affected ID disappeared: {execution_id}")
        run_dir = run_dir_for(row)
        require(
            sha256_file(run_dir / "dispatch" / f"{execution_id}.started.json")
            == item["started_marker_sha256"],
            f"started marker changed: {execution_id}",
        )
        current_artifacts = artifact_manifest(run_dir, execution_id)
        if item["recovery_class"] == "persisted_response":
            require(
                current_artifacts == item["persisted_artifacts"],
                f"persisted response artifacts changed: {execution_id}",
            )
        else:
            # A started-marker-only row may acquire transport-attempt evidence
            # while retaining the same semantic execution and idempotency key.
            require(
                all(
                    current_artifacts.get(name) == digest
                    for name, digest in item["persisted_artifacts"].items()
                ),
                f"frozen started-row evidence changed: {execution_id}",
            )
    return {
        "status": "passed",
        "freeze_sha256": sha256_file(path),
        "affected_rows": len(freeze["affected_rows"]),
        "registered_rows_per_repeat": 1296,
    }


def core_result(value: dict[str, Any]) -> dict[str, Any]:
    missing = set(RESULT_FIELDS) - set(value)
    unexpected = set(value) - set(RESULT_FIELDS) - RUNNER_EXTRAS
    require(not missing, f"result is missing frozen fields: {sorted(missing)}")
    require(not unexpected, f"result has unknown extension fields: {sorted(unexpected)}")
    return {key: value[key] for key in RESULT_FIELDS}


def metadata_document(
    row: dict[str, Any],
    core: dict[str, Any],
    *,
    preflight_status: str,
    recovery: dict[str, Any] | None,
) -> dict[str, Any]:
    bindings = GRID_BINDINGS if "repeat_id" in row else CONTROL_BINDINGS
    return {
        "schema_version": "effectslice-terminal-row-metadata.v1",
        "experiment": str(row.get("repeat_id", "Controls-v2")),
        "execution_id": row["execution_id"],
        "transport_request_id": row["execution_id"],
        "preflight_status": preflight_status,
        "schedule_bindings": {key: row[key] for key in bindings},
        "result_row_sha256": fg1.sha256_bytes(fg1.canonical_json(core)),
        "recovery": recovery,
    }


def write_core_and_metadata(
    run_dir: Path,
    row: dict[str, Any],
    value: dict[str, Any],
    *,
    preflight_status: str,
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    core = core_result(value)
    fg1.validate_result_row(fg5.DEFAULT_PARENT, core, str(row["model_slot_id"]))
    fg1.write_row(xpath(run_dir), row, core, fg5.DEFAULT_PARENT)
    row_path = run_dir / "rows" / f"{row['execution_id']}.json"
    metadata = metadata_document(
        row,
        core,
        preflight_status=preflight_status,
        recovery=recovery,
    )
    metadata["result_row_sha256"] = sha256_file(row_path)
    atomic_json(run_dir / "metadata" / f"{row['execution_id']}.json", metadata)
    return core


def verify_result_binding(run_dir: Path, row: dict[str, Any]) -> dict[str, Any]:
    execution_id = str(row["execution_id"])
    row_path = run_dir / "rows" / f"{execution_id}.json"
    metadata_path = run_dir / "metadata" / f"{execution_id}.json"
    require(xpath(row_path).exists(), f"missing result row: {execution_id}")
    require(xpath(metadata_path).exists(), f"missing result metadata: {execution_id}")
    value = load_json(row_path)
    require(set(value) == set(RESULT_FIELDS), f"result schema surface changed: {execution_id}")
    fg1.validate_result_row(fg5.DEFAULT_PARENT, value, str(row["model_slot_id"]))
    metadata = load_json(metadata_path)
    require(metadata["execution_id"] == execution_id, "metadata execution binding changed")
    require(metadata["result_row_sha256"] == sha256_file(row_path), "metadata result hash changed")
    bindings = GRID_BINDINGS if "repeat_id" in row else CONTROL_BINDINGS
    require(metadata["schedule_bindings"] == {key: row[key] for key in bindings}, "metadata schedule binding changed")
    return value


def load_persisted_dispatch(run_dir: Path, execution_id: str) -> Any:
    record = load_json(run_dir / "attempts" / f"{execution_id}.json")
    attempts = list(record["attempts"])
    bodies: list[tuple[int, bytes]] = []
    for attempt in attempts:
        index = int(attempt["attempt_index"])
        path = xpath(run_dir / "attempt_bodies" / execution_id / f"attempt_{index}.bin")
        if path.exists():
            bodies.append((index, path.read_bytes()))
    terminal_body = bodies[-1][1] if bodies else None
    if record["state"] in {"completed_body", "http_terminal_failure"}:
        require(terminal_body is not None, f"terminal body missing: {execution_id}")
        raw = xpath(run_dir / "raw" / f"{execution_id}.json").read_bytes()
        require(raw == terminal_body, f"raw response differs from terminal attempt: {execution_id}")
    elapsed = sum(
        int(item["attempt_elapsed_ms"]) + int(item["retry_sleep_after_attempt_ms"])
        for item in attempts
    )
    return fg1.DispatchResult(
        state=str(record["state"]),
        attempts=attempts,
        terminal_body=terminal_body,
        terminal_http_status=record["terminal_http_status"],
        terminal_headers=dict(record["terminal_request_ids"]),
        attempt_bodies=bodies,
        total_execution_elapsed_ms=elapsed,
        failure_class=record["failure_class"],
    )


def retryable_dispatch_failure(dispatch: Any) -> bool:
    if dispatch.state == "transport_terminal_failure":
        return True
    return (
        dispatch.state == "http_terminal_failure"
        and dispatch.terminal_http_status in fg1.RETRYABLE_HTTP
    )


def resilient_dispatch(
    original_dispatch: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    all_attempts: list[dict[str, Any]] = []
    all_bodies: list[tuple[int, bytes]] = []
    total_elapsed = 0
    final: Any = None
    for _ in range(MAX_TRANSPORT_CYCLES_PER_INVOCATION):
        current = original_dispatch(*args, **kwargs)
        offset = len(all_attempts)
        for attempt in current.attempts:
            copied = dict(attempt)
            copied["attempt_index"] = offset + int(attempt["attempt_index"])
            all_attempts.append(copied)
        for attempt_index, body in current.attempt_bodies:
            all_bodies.append((offset + int(attempt_index), body))
        total_elapsed += int(current.total_execution_elapsed_ms)
        final = current
        if not retryable_dispatch_failure(current):
            break
    require(final is not None, "resilient dispatch produced no transport cycle")
    return fg1.DispatchResult(
        state=final.state,
        attempts=all_attempts,
        terminal_body=final.terminal_body,
        terminal_http_status=final.terminal_http_status,
        terminal_headers=final.terminal_headers,
        attempt_bodies=all_bodies,
        total_execution_elapsed_ms=total_elapsed,
        failure_class=final.failure_class,
    )


def retryable_result(value: dict[str, Any]) -> bool:
    if value["terminal_outcome"] == "transport_terminal_failure":
        return True
    attempts = value.get("attempts") or []
    if not attempts:
        return False
    status_class = str(attempts[-1]["attempt_status_class"])
    if not status_class.startswith("http_"):
        return False
    try:
        status = int(status_class.removeprefix("http_"))
    except ValueError:
        return False
    return status in fg1.RETRYABLE_HTTP


def execute_live_resume(
    row: dict[str, Any],
    run_dir: Path,
    inputs: Any,
    token: str,
) -> dict[str, Any]:
    original_dispatch = fg1.dispatch_request

    def retrying_dispatch(*args: Any, **kwargs: Any) -> Any:
        return resilient_dispatch(original_dispatch, *args, **kwargs)

    try:
        fg1.dispatch_request = retrying_dispatch
        value = fg1.execute_row(
            fg5.DEFAULT_PARENT,
            xpath(run_dir),
            row,
            inputs,
            token,
        )
    finally:
        fg1.dispatch_request = original_dispatch
    if retryable_result(value):
        raise DeferredTransportError(
            f"retryable transport state retained for continuation: {row['execution_id']}"
        )
    return value


def reproject_persisted_response(
    row: dict[str, Any], run_dir: Path, inputs: Any
) -> tuple[dict[str, Any], dict[str, str]]:
    execution_id = str(row["execution_id"])
    before = artifact_manifest(run_dir, execution_id)
    dispatch = load_persisted_dispatch(run_dir, execution_id)
    calls = 0

    def local_dispatch(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        del args, kwargs
        calls += 1
        return dispatch

    original = fg1.dispatch_request
    try:
        fg1.dispatch_request = local_dispatch
        with tempfile.TemporaryDirectory(prefix="pts_terminal_recovery_", dir=Path.cwd()) as temporary:
            temporary_run = Path(temporary) / "run"
            result = fg1.execute_row(
                fg5.DEFAULT_PARENT,
                temporary_run,
                row,
                inputs,
                "",
            )
            regenerated = artifact_manifest(temporary_run, execution_id)
    finally:
        fg1.dispatch_request = original
    require(calls == 1, f"local projection dispatch count changed: {execution_id}")
    require(regenerated == before, f"local reprojection changed persisted evidence: {execution_id}")
    require(artifact_manifest(run_dir, execution_id) == before, f"source evidence changed during reprojection: {execution_id}")
    return result, before


def terminal_marker(
    run_dir: Path,
    row: dict[str, Any],
    core: dict[str, Any],
    recovery_class: str,
) -> None:
    execution_id = str(row["execution_id"])
    schema = (
        "effectslice-repeat-dispatch-terminal.v1"
        if "repeat_id" in row
        else "effectslice-controls-v2-dispatch-terminal.v1"
    )
    value = {
        "schema_version": schema,
        "execution_id": execution_id,
        "transport_request_id": execution_id,
        "terminal_outcome": core["terminal_outcome"],
        "result_row_sha256": sha256_file(run_dir / "rows" / f"{execution_id}.json"),
        "recovered_from_persisted_evidence": recovery_class == "persisted_response",
        "recovery_class": recovery_class,
    }
    if "repeat_id" in row:
        value["repeat_id"] = row["repeat_id"]
    atomic_json(run_dir / "dispatch" / f"{execution_id}.terminal.json", value)


def resume_nonterminal_rows(
    rows: Iterable[dict[str, Any]],
    resolver: Any,
    docs_dir: Path,
) -> dict[str, Any]:
    credentials, _ = fg1.load_credentials(docs_dir.resolve())
    completed: list[str] = []
    deferred: list[str] = []
    for row in rows:
        execution_id = str(row["execution_id"])
        run_dir = run_dir_for(row)
        started = xpath(run_dir / "dispatch" / f"{execution_id}.started.json")
        row_path = xpath(run_dir / "rows" / f"{execution_id}.json")
        if row_path.exists():
            verify_result_binding(run_dir, row)
            continue
        if not started.exists():
            continue
        inputs = resolver.resolve(row)
        attempts_path = xpath(run_dir / "attempts" / f"{execution_id}.json")
        recovery_class = "same_id_transport_continuation"
        if attempts_path.exists():
            attempt_record = load_json(attempts_path)
            retryable = (
                attempt_record["state"] == "transport_terminal_failure"
                or (
                    attempt_record["state"] == "http_terminal_failure"
                    and attempt_record["terminal_http_status"] in fg1.RETRYABLE_HTTP
                )
            )
        else:
            retryable = True
        try:
            if retryable:
                value = execute_live_resume(
                    row,
                    run_dir,
                    inputs,
                    credentials[str(row["model_slot_id"])],
                )
            else:
                value, _ = reproject_persisted_response(row, run_dir, inputs)
                recovery_class = "persisted_response_local_reprojection"
        except DeferredTransportError:
            deferred.append(execution_id)
            continue
        preflight_status = (
            grid.preflight_map(grid.DEFAULT_RUNS, str(row["repeat_id"]))[
                str(row["model_slot_id"])
            ]
            if "repeat_id" in row
            else str(
                load_json(
                    controls.DEFAULT_RUN / "preflight" / "deepseek_primary.json"
                )["status"]
            )
        )
        core = write_core_and_metadata(
            run_dir,
            row,
            value,
            preflight_status=preflight_status,
            recovery={
                "class": recovery_class,
                "recorded_as_network_terminal": False,
            },
        )
        terminal_marker(run_dir, row, core, recovery_class)
        completed.append(execution_id)
    return {
        "completed": completed,
        "deferred": deferred,
    }


def recover(docs_dir: Path, path: Path = DEFAULT_FREEZE) -> dict[str, Any]:
    verification = verify_freeze(path)
    freeze = load_json(path)
    controls_by_id, grid_by_id = schedule_maps()
    control_resolver = controls.ControlResolver(controls.DEFAULT_REGISTRATION)
    grid_resolver = grid.RepeatResolver()
    credentials, _ = fg1.load_credentials(docs_dir.resolve())
    recovered: list[dict[str, Any]] = []
    deferred: list[str] = []
    for item in freeze["affected_rows"]:
        execution_id = str(item["execution_id"])
        row = controls_by_id.get(execution_id) or grid_by_id[execution_id]
        run_dir = run_dir_for(row)
        row_path = xpath(run_dir / "rows" / f"{execution_id}.json")
        if row_path.exists():
            value = verify_result_binding(run_dir, row)
            recovered.append(
                {
                    "execution_id": execution_id,
                    "experiment": item["experiment"],
                    "recovery_class": item["recovery_class"],
                    "terminal_outcome": value["terminal_outcome"],
                    "result_row_sha256": sha256_file(row_path),
                    "resume_verified": True,
                }
            )
            continue
        inputs = (
            grid_resolver.resolve(row)
            if "repeat_id" in row
            else control_resolver.resolve(row)
        )
        if item["recovery_class"] == "persisted_response":
            value, evidence = reproject_persisted_response(row, run_dir, inputs)
            recovery = {
                "class": "persisted_response_local_reprojection",
                "http_calls": 0,
                "source_artifact_hashes": evidence,
                "total_elapsed_reconstruction": "sum_of_persisted_attempt_and_sleep_ms",
            }
        else:
            try:
                value = execute_live_resume(
                    row,
                    run_dir,
                    inputs,
                    credentials[str(row["model_slot_id"])],
                )
            except DeferredTransportError:
                deferred.append(execution_id)
                continue
            recovery = {
                "class": "started_marker_only_same_id_transport_continuation",
                "maximum_transport_cycles_this_invocation": MAX_TRANSPORT_CYCLES_PER_INVOCATION,
                "recorded_as_network_terminal": False,
            }
        preflight_status = (
            grid.preflight_map(grid.DEFAULT_RUNS, str(row["repeat_id"]))[
                str(row["model_slot_id"])
            ]
            if "repeat_id" in row
            else str(load_json(controls.DEFAULT_RUN / "preflight" / "deepseek_primary.json")["status"])
        )
        core = write_core_and_metadata(
            run_dir,
            row,
            value,
            preflight_status=preflight_status,
            recovery=recovery,
        )
        terminal_marker(run_dir, row, core, str(item["recovery_class"]))
        recovered.append(
            {
                "execution_id": execution_id,
                "experiment": item["experiment"],
                "recovery_class": item["recovery_class"],
                "terminal_outcome": core["terminal_outcome"],
                "result_row_sha256": sha256_file(row_path),
                "resume_verified": False,
            }
        )
    result = {
        "schema_version": "effectslice-terminal-row-recovery-report.v1",
        "created_at_utc": utc_now(),
        "freeze_sha256": verification["freeze_sha256"],
        "local_only_reprojections": sum(
            row["recovery_class"] == "persisted_response" for row in recovered
        ),
        "recovered_rows": len(recovered),
        "deferred_transport_rows": deferred,
        "complete": len(recovered) == len(freeze["affected_rows"]),
        "recovery_class_counts": dict(sorted(Counter(row["recovery_class"] for row in recovered).items())),
        "terminal_outcomes": dict(sorted(Counter(row["terminal_outcome"] for row in recovered).items())),
        "rows": recovered,
    }
    atomic_json(DEFAULT_RECOVERY_REPORT, result)
    return result


def grid_progress(
    registration_root: Path, runs_root: Path, repeat_id: str
) -> dict[str, Any]:
    rows = grid.repeat_schedule(registration_root, repeat_id)
    outcomes: Counter[str] = Counter()
    by_slot: Counter[str] = Counter()
    completed = 0
    run_dir = runs_root / repeat_id
    for row in rows:
        row_path = xpath(run_dir / "rows" / f"{row['execution_id']}.json")
        if not row_path.exists():
            continue
        value = verify_result_binding(run_dir, row)
        completed += 1
        outcomes[str(value["terminal_outcome"])] += 1
        by_slot[str(row["model_slot_id"])] += 1
    return {
        "schema_version": "effectslice-full-grid-repeat-progress.v2",
        "updated_at_utc": utc_now(),
        "repeat_id": repeat_id,
        "registered_rows": 1296,
        "terminal_rows": completed,
        "remaining_rows": 1296 - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def controls_progress(registration_root: Path, run_dir: Path) -> dict[str, Any]:
    rows = load_json(registration_root / "schedule.json")["rows"]
    outcomes: Counter[str] = Counter()
    completed = 0
    for row in rows:
        row_path = xpath(run_dir / "rows" / f"{row['execution_id']}.json")
        if not row_path.exists():
            continue
        value = verify_result_binding(run_dir, row)
        completed += 1
        outcomes[str(value["terminal_outcome"])] += 1
    return {
        "schema_version": "effectslice-controls-v2-progress.v2",
        "updated_at_utc": utc_now(),
        "registered_rows": 96,
        "terminal_rows": completed,
        "remaining_rows": 96 - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
    }


@contextlib.contextmanager
def patched_runner_schema() -> Iterator[None]:
    original_write = fg1.write_row
    original_dispatch = fg1.dispatch_request
    original_grid_progress = grid.progress_summary
    original_grid_verify = grid.verify_existing_row
    original_controls_progress = controls.progress

    def patched_write(
        run_dir: Path,
        row: dict[str, Any],
        value: dict[str, Any],
        materialization: Path,
    ) -> None:
        require(materialization == fg5.DEFAULT_PARENT, "materialization binding changed")
        if retryable_result(value):
            raise DeferredTransportError(
                f"retryable transport state is not a terminal experiment row: {row['execution_id']}"
            )
        preflight_status = str(value.get("preflight_status", "unknown"))
        write_core_and_metadata(
            run_dir,
            row,
            value,
            preflight_status=preflight_status,
        )

    def patched_grid_verify(path: Path, row: dict[str, Any]) -> None:
        del path
        verify_result_binding(grid.DEFAULT_RUNS / str(row["repeat_id"]), row)

    def patched_dispatch(*args: Any, **kwargs: Any) -> Any:
        return resilient_dispatch(original_dispatch, *args, **kwargs)

    try:
        fg1.write_row = patched_write
        fg1.dispatch_request = patched_dispatch
        grid.progress_summary = grid_progress
        grid.verify_existing_row = patched_grid_verify
        controls.progress = controls_progress
        yield
    finally:
        fg1.write_row = original_write
        fg1.dispatch_request = original_dispatch
        grid.progress_summary = original_grid_progress
        grid.verify_existing_row = original_grid_verify
        controls.progress = original_controls_progress


def run_controls(docs_dir: Path, workers: int) -> dict[str, Any]:
    verify_freeze()
    rows = load_json(controls.DEFAULT_REGISTRATION / "schedule.json")["rows"]
    resumed = resume_nonterminal_rows(
        rows,
        controls.ControlResolver(controls.DEFAULT_REGISTRATION),
        docs_dir,
    )
    require(not resumed["deferred"], f"Controls-v2 transport rows remain deferred: {resumed['deferred']}")
    with patched_runner_schema():
        return controls.run_rows(
            controls.DEFAULT_REGISTRATION,
            controls.DEFAULT_RUN,
            docs_dir,
            workers=workers,
        )


def run_grid(
    docs_dir: Path,
    *,
    max_new_rows: int | None,
    workers: int,
    per_host_workers: int,
) -> dict[str, Any]:
    verify_freeze()
    resolver = grid.RepeatResolver()
    rows = [
        row
        for repeat_id in grid.REPEAT_IDS
        for row in grid.repeat_schedule(grid.DEFAULT_REGISTRATION, repeat_id)
    ]
    resumed = resume_nonterminal_rows(rows, resolver, docs_dir)
    require(not resumed["deferred"], f"full-grid transport rows remain deferred: {resumed['deferred']}")
    with patched_runner_schema():
        return grid.run(
            grid.DEFAULT_REGISTRATION,
            grid.DEFAULT_RUNS,
            docs_dir,
            max_new_rows=max_new_rows,
            workers=workers,
            per_host_workers=per_host_workers,
        )


def verify_all(require_complete: bool) -> dict[str, Any]:
    freeze = verify_freeze()
    controls_registration = controls.verify_registration(
        controls.DEFAULT_REGISTRATION, require_frozen=True
    )
    grid_registration = grid.registration.verify(
        grid.DEFAULT_REGISTRATION, require_frozen=True
    )
    control_status = controls_progress(controls.DEFAULT_REGISTRATION, controls.DEFAULT_RUN)
    repeats = {
        repeat_id: grid_progress(grid.DEFAULT_REGISTRATION, grid.DEFAULT_RUNS, repeat_id)
        for repeat_id in grid.REPEAT_IDS
    }
    if require_complete:
        require(control_status["terminal_rows"] == 96, "Controls-v2 is incomplete")
        for repeat_id, status in repeats.items():
            require(status["terminal_rows"] == 1296, f"{repeat_id} is incomplete")
    return {
        "status": "passed",
        "require_complete": require_complete,
        "freeze": freeze,
        "controls_registration_bundle_sha256": controls_registration[
            "registration_bundle_sha256"
        ],
        "grid_registration_bundle_sha256": grid_registration[
            "registration_bundle_sha256"
        ],
        "controls": control_status,
        "repeats": repeats,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=(
            "freeze",
            "verify-freeze",
            "recover",
            "run-controls",
            "run-grid",
            "verify",
        ),
    )
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--per-host-workers", type=int, default=2)
    parser.add_argument("--max-new-rows", type=int)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "freeze":
        value = build_freeze()
    elif args.command == "verify-freeze":
        value = verify_freeze()
    elif args.command == "recover":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = recover(args.docs_dir)
    elif args.command == "run-controls":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = run_controls(args.docs_dir, args.workers or 1)
    elif args.command == "run-grid":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = run_grid(
            args.docs_dir,
            max_new_rows=args.max_new_rows,
            workers=args.workers or 3,
            per_host_workers=args.per_host_workers,
        )
    else:
        value = verify_all(args.require_complete)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SuccessorError,
        controls.ControlsError,
        grid.RunnerError,
        grid.registration.RegistrationError,
    ) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
