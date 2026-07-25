from __future__ import annotations

import argparse
import contextlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator

import terminal_row_successor as v1


fg1 = v1.fg1
fg5 = v1.fg5
controls = v1.controls
grid = v1.grid

ROOT = Path(__file__).resolve().parent
DEFAULT_FREEZE = ROOT / "terminal_row_successor_v2_freeze.json"
DEFAULT_RECOVERY_REPORT = ROOT / "terminal_row_successor_v2_recovery.json"
SUCCESSOR_TEST = ROOT / "tests" / "test_terminal_row_successor_v2.py"
EXPECTED_V1_FREEZE_SHA256 = (
    "a6b4d581968e098693ba3ef94fd3d359f2e28347c239fe85670ce44ce7809bd6"
)
SCHEMA_VERSION = "effectslice-terminal-row-successor.v2"


class SuccessorV2Error(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorV2Error(message)


def classify_nonterminal(run_dir: Path, execution_id: str) -> str:
    attempts_path = v1.xpath(run_dir / "attempts" / f"{execution_id}.json")
    if not attempts_path.exists():
        return "started_marker_only"
    record = v1.load_json(attempts_path)
    retryable = (
        record["state"] == "transport_terminal_failure"
        or (
            record["state"] == "http_terminal_failure"
            and record["terminal_http_status"] in fg1.RETRYABLE_HTTP
        )
    )
    return "retryable_transport" if retryable else "persisted_response"


def current_nonterminal_rows() -> list[tuple[str, dict[str, Any], Path]]:
    controls_by_id, grid_by_id = v1.schedule_maps()
    result: list[tuple[str, dict[str, Any], Path]] = []
    for label, rows, run_dir in (
        ("Controls-v2", controls_by_id, controls.DEFAULT_RUN),
        ("FG6", grid_by_id, grid.DEFAULT_RUNS / "FG6"),
        ("FG7", grid_by_id, grid.DEFAULT_RUNS / "FG7"),
        ("FG8", grid_by_id, grid.DEFAULT_RUNS / "FG8"),
    ):
        for execution_id in v1.started_ids(run_dir):
            row_path = v1.xpath(run_dir / "rows" / f"{execution_id}.json")
            terminal_path = v1.xpath(
                run_dir / "dispatch" / f"{execution_id}.terminal.json"
            )
            if row_path.exists():
                continue
            require(execution_id in rows, f"unregistered nonterminal row: {execution_id}")
            require(
                not terminal_path.exists(),
                f"terminal marker exists without result row: {execution_id}",
            )
            result.append((label, rows[execution_id], run_dir))
    return result


def build_freeze(path: Path = DEFAULT_FREEZE) -> dict[str, Any]:
    require(not path.exists(), f"v2 freeze already exists: {path}")
    v1_verification = v1.verify_freeze()
    require(
        v1_verification["freeze_sha256"] == EXPECTED_V1_FREEZE_SHA256,
        "v1 freeze binding changed",
    )
    affected: list[dict[str, Any]] = []
    for label, row, run_dir in current_nonterminal_rows():
        execution_id = str(row["execution_id"])
        affected.append(
            {
                "experiment": label,
                "execution_id": execution_id,
                "recovery_class": classify_nonterminal(run_dir, execution_id),
                "started_marker_sha256": v1.sha256_file(
                    run_dir / "dispatch" / f"{execution_id}.started.json"
                ),
                "persisted_artifacts": v1.artifact_manifest(run_dir, execution_id),
            }
        )
    counts = Counter(item["experiment"] for item in affected)
    require(
        counts == {"Controls-v2": 10, "FG6": 10},
        f"unexpected v2 affected rows: {dict(counts)}",
    )
    document = {
        "schema_version": "effectslice-terminal-row-successor-v2-freeze.v1",
        "created_at_utc": v1.utc_now(),
        "forward_only": True,
        "root_cause": "patched_writer_recursed_through_patched_symbol",
        "fix": "capture_and_call_unpatched_base_writer",
        "network_states_are_not_final_results": True,
        "v1_freeze_sha256": EXPECTED_V1_FREEZE_SHA256,
        "v1_source_sha256": v1.sha256_file(ROOT / "terminal_row_successor.py"),
        "v2_source_sha256": v1.sha256_file(Path(__file__).resolve()),
        "v2_test_sha256": v1.sha256_file(SUCCESSOR_TEST),
        "registered_rows": {
            "Controls-v2": 96,
            "FG6": 1296,
            "FG7": 1296,
            "FG8": 1296,
        },
        "affected_row_counts": dict(sorted(counts.items())),
        "recovery_class_counts": dict(
            sorted(Counter(item["recovery_class"] for item in affected).items())
        ),
        "affected_rows": sorted(
            affected, key=lambda item: (item["experiment"], item["execution_id"])
        ),
    }
    v1.atomic_json(path, document)
    return document


def verify_freeze(path: Path = DEFAULT_FREEZE) -> dict[str, Any]:
    freeze = v1.load_json(path)
    require(
        freeze["schema_version"]
        == "effectslice-terminal-row-successor-v2-freeze.v1",
        "v2 freeze schema changed",
    )
    require(
        v1.sha256_file(v1.DEFAULT_FREEZE) == EXPECTED_V1_FREEZE_SHA256,
        "v1 freeze file changed",
    )
    require(
        freeze["v1_source_sha256"]
        == v1.sha256_file(ROOT / "terminal_row_successor.py"),
        "v1 source changed",
    )
    require(
        freeze["v2_source_sha256"] == v1.sha256_file(Path(__file__).resolve()),
        "v2 source changed after freeze",
    )
    require(
        freeze["v2_test_sha256"] == v1.sha256_file(SUCCESSOR_TEST),
        "v2 tests changed after freeze",
    )
    controls_by_id, grid_by_id = v1.schedule_maps()
    for item in freeze["affected_rows"]:
        execution_id = str(item["execution_id"])
        row = controls_by_id.get(execution_id) or grid_by_id.get(execution_id)
        require(row is not None, f"v2 affected row disappeared: {execution_id}")
        run_dir = v1.run_dir_for(row)
        require(
            v1.sha256_file(
                run_dir / "dispatch" / f"{execution_id}.started.json"
            )
            == item["started_marker_sha256"],
            f"v2 started marker changed: {execution_id}",
        )
        current = v1.artifact_manifest(run_dir, execution_id)
        if item["recovery_class"] == "persisted_response":
            require(
                current == item["persisted_artifacts"],
                f"v2 persisted evidence changed: {execution_id}",
            )
        else:
            require(
                all(
                    current.get(name) == digest
                    for name, digest in item["persisted_artifacts"].items()
                ),
                f"v2 retry evidence prefix changed: {execution_id}",
            )
    return {
        "status": "passed",
        "freeze_sha256": v1.sha256_file(path),
        "affected_rows": len(freeze["affected_rows"]),
        "registered_rows_per_repeat": 1296,
    }


def write_core_and_metadata(
    base_write: Any,
    run_dir: Path,
    row: dict[str, Any],
    value: dict[str, Any],
    *,
    preflight_status: str,
) -> dict[str, Any]:
    core = v1.core_result(value)
    fg1.validate_result_row(fg5.DEFAULT_PARENT, core, str(row["model_slot_id"]))
    base_write(v1.xpath(run_dir), row, core, fg5.DEFAULT_PARENT)
    row_path = run_dir / "rows" / f"{row['execution_id']}.json"
    metadata = v1.metadata_document(
        row,
        core,
        preflight_status=preflight_status,
        recovery=None,
    )
    metadata["writer_successor"] = SCHEMA_VERSION
    metadata["result_row_sha256"] = v1.sha256_file(row_path)
    v1.atomic_json(run_dir / "metadata" / f"{row['execution_id']}.json", metadata)
    return core


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
        require(materialization == fg5.DEFAULT_PARENT, "materialization changed")
        if v1.retryable_result(value):
            raise v1.DeferredTransportError(
                f"retryable transport state is not final: {row['execution_id']}"
            )
        write_core_and_metadata(
            original_write,
            run_dir,
            row,
            value,
            preflight_status=str(value.get("preflight_status", "unknown")),
        )

    def patched_dispatch(*args: Any, **kwargs: Any) -> Any:
        return v1.resilient_dispatch(original_dispatch, *args, **kwargs)

    def patched_grid_verify(path: Path, row: dict[str, Any]) -> None:
        del path
        v1.verify_result_binding(
            grid.DEFAULT_RUNS / str(row["repeat_id"]), row
        )

    try:
        fg1.write_row = patched_write
        fg1.dispatch_request = patched_dispatch
        grid.progress_summary = v1.grid_progress
        grid.verify_existing_row = patched_grid_verify
        controls.progress = v1.controls_progress
        yield
    finally:
        fg1.write_row = original_write
        fg1.dispatch_request = original_dispatch
        grid.progress_summary = original_grid_progress
        grid.verify_existing_row = original_grid_verify
        controls.progress = original_controls_progress


def recover_nonterminal(docs_dir: Path) -> dict[str, Any]:
    freeze = verify_freeze()
    control_rows = v1.load_json(
        controls.DEFAULT_REGISTRATION / "schedule.json"
    )["rows"]
    grid_rows = [
        row
        for repeat_id in grid.REPEAT_IDS
        for row in grid.repeat_schedule(grid.DEFAULT_REGISTRATION, repeat_id)
    ]
    control_result = v1.resume_nonterminal_rows(
        control_rows,
        controls.ControlResolver(controls.DEFAULT_REGISTRATION),
        docs_dir,
    )
    grid_result = v1.resume_nonterminal_rows(
        grid_rows,
        grid.RepeatResolver(),
        docs_dir,
    )
    completed = control_result["completed"] + grid_result["completed"]
    deferred = control_result["deferred"] + grid_result["deferred"]
    result = {
        "schema_version": "effectslice-terminal-row-successor-v2-recovery.v1",
        "created_at_utc": v1.utc_now(),
        "freeze_sha256": freeze["freeze_sha256"],
        "completed_rows": completed,
        "completed_count": len(completed),
        "deferred_transport_rows": deferred,
        "network_states_recorded_as_final": False,
        "controls_progress": v1.controls_progress(
            controls.DEFAULT_REGISTRATION, controls.DEFAULT_RUN
        ),
        "repeat_progress": {
            repeat_id: v1.grid_progress(
                grid.DEFAULT_REGISTRATION, grid.DEFAULT_RUNS, repeat_id
            )
            for repeat_id in grid.REPEAT_IDS
        },
    }
    v1.atomic_json(DEFAULT_RECOVERY_REPORT, result)
    return result


def run_controls(docs_dir: Path, workers: int) -> dict[str, Any]:
    recovery = recover_nonterminal(docs_dir)
    require(
        not recovery["deferred_transport_rows"],
        f"Controls/full-grid rows remain deferred: {recovery['deferred_transport_rows']}",
    )
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
    recovery = recover_nonterminal(docs_dir)
    require(
        not recovery["deferred_transport_rows"],
        f"Controls/full-grid rows remain deferred: {recovery['deferred_transport_rows']}",
    )
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
    v2_freeze = verify_freeze()
    result = v1.verify_all(require_complete)
    result["terminal_row_successor_v2_freeze"] = v2_freeze
    return result


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
        value = recover_nonterminal(args.docs_dir)
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
        SuccessorV2Error,
        v1.SuccessorError,
        controls.ControlsError,
        grid.RunnerError,
        grid.registration.RegistrationError,
    ) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
