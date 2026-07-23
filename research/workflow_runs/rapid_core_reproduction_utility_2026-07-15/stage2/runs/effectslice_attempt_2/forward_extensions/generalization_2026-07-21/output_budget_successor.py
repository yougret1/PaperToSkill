from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

import remote_execution_runner as fg1


FORWARD_ROOT = Path(__file__).resolve().parent
DEFAULT_PARENT = FORWARD_ROOT / "materialization_remote_only_2026-07-23"
DEFAULT_SUCCESSOR = FORWARD_ROOT / "output_budget_successor_2026-07-23"
DEFAULT_RUN_DIR = FORWARD_ROOT / "remote_execution_v2_2026-07-23"
INVALID_BATCH_REPORT = (
    FORWARD_ROOT
    / "stage_report_2_3_registered_execution_batch_001_2026_07_23.json"
)
EXPECTED_PARENT_ANCHOR = (
    "1f12dfdba63b1ddc65bd57fa8b1b625ba4259050e93ab4f108786c2023c5ccd7"
)
INVALID_BATCH_COMMIT = "e9bdbeda"
OLD_OUTPUT_BUDGET = 1024
NEW_OUTPUT_BUDGET = 8192
OUTPUT_BUDGET_VERSION = "fg2-output-budget-8192-v1"
PILOT_MARKER = (
    "[OUTPUT-BUDGET PILOT - NOT SCORED]\n"
    "Return the requested submission format. This request is excluded from "
    "all experiment estimates.\n\n"
)
LIMIT_REASONS = frozenset(
    {"length", "max_tokens", "max_output_tokens", "output_limit"}
)


class SuccessorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorError(message)


def utc_now() -> str:
    return fg1.utc_now()


def load_json(path: Path) -> Any:
    return fg1.load_json(path)


def canonical_json(value: object) -> bytes:
    return fg1.canonical_json(value)


def sha256_bytes(value: bytes) -> str:
    return fg1.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(path)


def write_json(path: Path, value: object) -> None:
    fg1.atomic_json(path, value)


def output_budget_key(request: dict[str, Any]) -> str:
    keys = [key for key in ("max_tokens", "max_output_tokens") if key in request]
    require(len(keys) == 1, "request must contain exactly one output-budget field")
    return keys[0]


def transformed_request_bytes(
    parent_bytes: bytes, *, pilot: bool = False
) -> bytes:
    value = json.loads(parent_bytes.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), "parent request must be a JSON object")
    key = output_budget_key(value)
    require(
        value[key] == OLD_OUTPUT_BUDGET,
        "parent request output budget changed",
    )
    value[key] = NEW_OUTPUT_BUDGET
    if pilot:
        if isinstance(value.get("input"), str):
            value["input"] = PILOT_MARKER + value["input"]
        else:
            messages = value.get("messages")
            require(
                isinstance(messages, list) and len(messages) == 1,
                "pilot request must contain one message or one input string",
            )
            message = messages[0]
            require(
                isinstance(message, dict)
                and isinstance(message.get("content"), str),
                "pilot message content is not a string",
            )
            message["content"] = PILOT_MARKER + message["content"]
    return canonical_json(value)


def successor_execution_id(parent_execution_id: str) -> str:
    value = (
        f"{OUTPUT_BUDGET_VERSION}|{parent_execution_id}".encode("utf-8")
    )
    return "fg2-exec-" + hashlib.sha256(value).hexdigest()[:24]


def pilot_execution_id(slot_id: str) -> str:
    value = f"{OUTPUT_BUDGET_VERSION}|pilot|{slot_id}".encode("utf-8")
    return "fg2-pilot-" + hashlib.sha256(value).hexdigest()[:20]


def parent_request_path(parent: Path, row: dict[str, Any]) -> Path:
    return (
        parent
        / "tasks"
        / str(row["task_id"])
        / "requests"
        / f"{row['execution_id']}.json"
    )


def decoding_document(slot_id: str) -> dict[str, Any]:
    return {
        "schema_version": "effectslice-fg2-decoding-overlay.v1",
        "model_slot_id": slot_id,
        "parent_normalized_max_output_tokens": OLD_OUTPUT_BUDGET,
        "normalized_max_output_tokens": NEW_OUTPUT_BUDGET,
        "temperature": 0,
        "top_p": 1.0,
        "only_registered_change": "normalized_max_output_tokens",
    }


def manifest_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name == "successor_manifest.json":
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def manifest_bundle_sha(files: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        canonical_json(
            {
                "schema_version": "effectslice-fg2-successor-binding.v1",
                "parent_anchor_bundle_sha256": EXPECTED_PARENT_ANCHOR,
                "output_budget_version": OUTPUT_BUDGET_VERSION,
                "files": files,
            }
        )
    )


def freeze_successor(parent: Path, successor: Path) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    invalid_batch_report = fg1.windows_extended_path(INVALID_BATCH_REPORT)
    require(
        fg1.EXPECTED_ANCHOR_BUNDLE_SHA256 == EXPECTED_PARENT_ANCHOR,
        "FG1 executor parent binding changed",
    )
    fg1.verify_full_anchor(parent)
    require(invalid_batch_report.is_file(), "invalid FG1 batch report is missing")
    invalid_report = load_json(invalid_batch_report)
    require(invalid_report.get("status") == "invalid", "FG1 batch is not invalid")
    require(
        invalid_report.get("outcomes", {}).get("finish_reason_length") == 72,
        "FG1 invalid-batch evidence changed",
    )
    require(not successor.exists(), "successor directory already exists")
    temporary = successor.with_name(successor.name + ".tmp")
    require(not temporary.exists(), "successor temporary directory already exists")
    temporary.mkdir(parents=True)
    try:
        parent_schedule_doc = load_json(parent / "global_remote_schedule.json")
        parent_rows = parent_schedule_doc["rows"]
        require(len(parent_rows) == 1296, "parent schedule row count changed")

        decoding_hashes: dict[str, str] = {}
        for slot_id in sorted(fg1.PROVIDER_SPECS):
            value = decoding_document(slot_id)
            path = temporary / "decoding" / f"{slot_id}.json"
            write_json(path, value)
            decoding_hashes[slot_id] = sha256_file(path)

        rows: list[dict[str, Any]] = []
        first_by_slot: dict[str, dict[str, Any]] = {}
        for parent_row in parent_rows:
            parent_id = str(parent_row["execution_id"])
            request_path = parent_request_path(parent, parent_row)
            require(request_path.is_file(), f"missing parent request: {parent_id}")
            require(
                sha256_file(request_path)
                == parent_row["serialized_wire_request_sha256"],
                f"parent request SHA changed: {parent_id}",
            )
            new_id = successor_execution_id(parent_id)
            request_bytes = transformed_request_bytes(request_path.read_bytes())
            overlay_path = temporary / "requests" / f"{new_id}.json"
            fg1.atomic_write(overlay_path, request_bytes)

            row = copy.deepcopy(parent_row)
            row["parent_execution_id"] = parent_id
            row["execution_id"] = new_id
            row["output_budget_version"] = OUTPUT_BUDGET_VERSION
            row["serialized_wire_request_sha256"] = sha256_bytes(request_bytes)
            row["decoding_config_sha256"] = decoding_hashes[
                str(row["model_slot_id"])
            ]
            rows.append(row)
            first_by_slot.setdefault(str(row["model_slot_id"]), parent_row)

        require(
            len({row["execution_id"] for row in rows}) == 1296,
            "successor execution IDs are not unique",
        )
        schedule = {
            "schema_version": "effectslice-fg2-remote-schedule.v1",
            "parent_anchor_bundle_sha256": EXPECTED_PARENT_ANCHOR,
            "output_budget_version": OUTPUT_BUDGET_VERSION,
            "registered_rows": len(rows),
            "rows": rows,
        }
        write_json(temporary / "global_remote_schedule.json", schedule)

        pilot_rows: list[dict[str, Any]] = []
        for slot_id in sorted(fg1.PROVIDER_SPECS):
            source = first_by_slot[slot_id]
            source_path = parent_request_path(parent, source)
            pilot_bytes = transformed_request_bytes(
                source_path.read_bytes(), pilot=True
            )
            pilot_id = pilot_execution_id(slot_id)
            pilot_path = temporary / "pilot" / "requests" / f"{slot_id}.json"
            fg1.atomic_write(pilot_path, pilot_bytes)
            pilot_rows.append(
                {
                    "pilot_execution_id": pilot_id,
                    "model_slot_id": slot_id,
                    "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias,
                    "source_parent_execution_id": source["execution_id"],
                    "request_path": f"pilot/requests/{slot_id}.json",
                    "serialized_wire_request_sha256": sha256_bytes(pilot_bytes),
                    "registered_experiment_row": False,
                    "scored": False,
                }
            )
        pilot_manifest = {
            "schema_version": "effectslice-fg2-output-budget-pilot.v1",
            "output_budget": NEW_OUTPUT_BUDGET,
            "pass_rule": (
                "All six exact aliases must return a non-truncated canonical "
                "JSON object containing one nonempty implementation string."
            ),
            "semantic_rerun_of_fg1_terminal_row": False,
            "pilot_marker": PILOT_MARKER,
            "rows": pilot_rows,
        }
        write_json(temporary / "pilot_manifest.json", pilot_manifest)

        registration = {
            "schema_version": "effectslice-fg2-output-budget-successor.v1",
            "created_at_utc": utc_now(),
            "parent_anchor_bundle_sha256": EXPECTED_PARENT_ANCHOR,
            "invalid_parent_batch_report": INVALID_BATCH_REPORT.name,
            "invalid_parent_batch_report_sha256": sha256_file(
                invalid_batch_report
            ),
            "invalid_parent_batch_commit": INVALID_BATCH_COMMIT,
            "invalid_parent_terminal_rows": 72,
            "invalid_parent_rows_pooled_with_fg2": False,
            "output_budget_version": OUTPUT_BUDGET_VERSION,
            "parent_output_budget": OLD_OUTPUT_BUDGET,
            "successor_output_budget": NEW_OUTPUT_BUDGET,
            "allowed_request_mutation": [
                "/max_tokens",
                "/max_output_tokens",
            ],
            "task_candidate_registry_scorer_mutation": False,
            "semantic_rerun_within_fg1": False,
            "fg2_is_new_versioned_execution": True,
            "pilot_required_before_registered_execution": True,
            "registered_rows": 1296,
        }
        write_json(temporary / "registration.json", registration)

        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-fg2-successor-manifest.v1",
            "parent_anchor_bundle_sha256": EXPECTED_PARENT_ANCHOR,
            "output_budget_version": OUTPUT_BUDGET_VERSION,
            "files": files,
            "file_count": len(files),
            "bundle_sha256": manifest_bundle_sha(files),
            "provider_calls_started": False,
        }
        write_json(temporary / "successor_manifest.json", manifest)
        os.replace(temporary, successor)
        return manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_successor(parent: Path, successor: Path) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    invalid_batch_report = fg1.windows_extended_path(INVALID_BATCH_REPORT)
    fg1.verify_full_anchor(parent)
    manifest = load_json(successor / "successor_manifest.json")
    files = manifest_files(successor)
    require(files == manifest["files"], "successor file manifest changed")
    require(
        manifest_bundle_sha(files) == manifest["bundle_sha256"],
        "successor bundle SHA changed",
    )
    require(
        manifest["parent_anchor_bundle_sha256"] == EXPECTED_PARENT_ANCHOR,
        "successor parent binding changed",
    )
    registration = load_json(successor / "registration.json")
    require(
        registration["invalid_parent_batch_report_sha256"]
        == sha256_file(invalid_batch_report),
        "invalid FG1 batch report changed",
    )
    require(
        registration["successor_output_budget"] == NEW_OUTPUT_BUDGET,
        "successor output budget changed",
    )

    parent_rows = load_json(parent / "global_remote_schedule.json")["rows"]
    rows = load_json(successor / "global_remote_schedule.json")["rows"]
    require(len(parent_rows) == len(rows) == 1296, "successor row count changed")
    parent_by_id = {str(row["execution_id"]): row for row in parent_rows}
    require(len(parent_by_id) == 1296, "parent execution IDs are not unique")

    decoding_hashes: dict[str, str] = {}
    for slot_id in sorted(fg1.PROVIDER_SPECS):
        path = successor / "decoding" / f"{slot_id}.json"
        require(load_json(path) == decoding_document(slot_id), "decoding overlay changed")
        decoding_hashes[slot_id] = sha256_file(path)

    seen: set[str] = set()
    for row in rows:
        parent_id = str(row.get("parent_execution_id"))
        require(parent_id in parent_by_id, "unknown successor parent row")
        parent_row = parent_by_id[parent_id]
        new_id = successor_execution_id(parent_id)
        require(row["execution_id"] == new_id, "successor execution ID changed")
        require(new_id not in seen, "duplicate successor execution ID")
        seen.add(new_id)

        parent_path = parent_request_path(parent, parent_row)
        expected_bytes = transformed_request_bytes(parent_path.read_bytes())
        overlay_path = successor / "requests" / f"{new_id}.json"
        require(overlay_path.read_bytes() == expected_bytes, "request overlay changed")
        require(
            row["serialized_wire_request_sha256"] == sha256_bytes(expected_bytes),
            "successor request SHA changed",
        )
        require(
            row["decoding_config_sha256"]
            == decoding_hashes[str(row["model_slot_id"])],
            "successor decoding SHA changed",
        )

        expected_row = copy.deepcopy(parent_row)
        expected_row["parent_execution_id"] = parent_id
        expected_row["execution_id"] = new_id
        expected_row["output_budget_version"] = OUTPUT_BUDGET_VERSION
        expected_row["serialized_wire_request_sha256"] = sha256_bytes(
            expected_bytes
        )
        expected_row["decoding_config_sha256"] = decoding_hashes[
            str(row["model_slot_id"])
        ]
        require(row == expected_row, "successor row changed outside allowed fields")

    pilot = load_json(successor / "pilot_manifest.json")
    require(len(pilot["rows"]) == 6, "pilot row count changed")
    for item in pilot["rows"]:
        slot_id = str(item["model_slot_id"])
        path = successor / str(item["request_path"])
        require(
            sha256_file(path) == item["serialized_wire_request_sha256"],
            "pilot request SHA changed",
        )
        value = json.loads(path.read_text(encoding="utf-8"))
        key = output_budget_key(value)
        require(value[key] == NEW_OUTPUT_BUDGET, "pilot output budget changed")
        visible = value.get("input")
        if visible is None:
            visible = value["messages"][0]["content"]
        require(
            isinstance(visible, str) and visible.startswith(PILOT_MARKER),
            "pilot marker changed",
        )
        require(
            value["model"] == fg1.PROVIDER_SPECS[slot_id].exact_alias,
            "pilot exact alias changed",
        )
    return {
        "status": "passed",
        "bundle_sha256": manifest["bundle_sha256"],
        "registered_rows": len(rows),
        "pilot_rows": len(pilot["rows"]),
        "output_budget": NEW_OUTPUT_BUDGET,
    }


def initialize_run_manifest(
    run_dir: Path,
    successor: Path,
    credential_metadata: dict[str, Any],
) -> dict[str, Any]:
    manifest = load_json(successor / "successor_manifest.json")
    path = run_dir / "run_manifest.json"
    expected = {
        "schema_version": "effectslice-fg2-remote-run.v1",
        "successor_bundle_sha256": manifest["bundle_sha256"],
        "parent_anchor_bundle_sha256": EXPECTED_PARENT_ANCHOR,
        "registered_rows": 1296,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
    }
    if path.exists():
        current = load_json(path)
        for key, value in expected.items():
            require(current.get(key) == value, f"run manifest {key} changed")
        return current
    value = {
        **expected,
        "created_at_utc": utc_now(),
        "provider_calls_started": False,
    }
    write_json(path, value)
    return value


def pilot_status(
    parent: Path,
    slot_id: str,
    dispatch: fg1.DispatchResult,
) -> tuple[str, str | None, Any, str | None]:
    if dispatch.state == "transport_terminal_failure":
        return "transport_terminal_failure", dispatch.failure_class, None, None
    if dispatch.state == "http_terminal_failure":
        status = dispatch.terminal_http_status
        return "request_rejected", f"http_{status}", None, None
    try:
        _, canonical, finish, _, termination = fg1.response_projection(
            parent, slot_id, dispatch.terminal_body or b""
        )
        fg1.strict_submission(canonical.decode("utf-8"))
        if finish in LIMIT_REASONS or termination in LIMIT_REASONS:
            return "output_budget_exhausted", None, finish, termination
        return "available", None, finish, termination
    except Exception as exc:
        return "submission_format_invalid", type(exc).__name__, None, None


def run_pilot(
    parent: Path,
    successor: Path,
    run_dir: Path,
    docs_dir: Path,
) -> dict[str, Any]:
    verify_successor(parent, successor)
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    credentials, metadata = fg1.load_credentials(docs_dir)
    initialize_run_manifest(run_dir, successor, metadata)
    pilot = load_json(successor / "pilot_manifest.json")
    results: list[dict[str, Any]] = []
    for item in pilot["rows"]:
        slot_id = str(item["model_slot_id"])
        pilot_id = str(item["pilot_execution_id"])
        result_path = run_dir / "pilot" / f"{slot_id}.json"
        started_path = run_dir / "pilot" / f"{slot_id}.started.json"
        if result_path.exists():
            value = load_json(result_path)
            require(value["pilot_execution_id"] == pilot_id, "pilot ID changed")
            results.append(value)
            continue
        require(
            not started_path.exists(),
            f"ambiguous pilot dispatch lacks terminal result: {slot_id}",
        )
        write_json(
            started_path,
            {
                "schema_version": "effectslice-fg2-pilot-start.v1",
                "pilot_execution_id": pilot_id,
                "model_slot_id": slot_id,
                "started_at_utc": utc_now(),
                "semantic_rerun_allowed": False,
            },
        )
        request_bytes = (
            successor / str(item["request_path"])
        ).read_bytes()
        require(
            sha256_bytes(request_bytes) == item["serialized_wire_request_sha256"],
            "pilot request changed before dispatch",
        )
        dispatch = fg1.dispatch_request(
            fg1.PROVIDER_SPECS[slot_id],
            credentials[slot_id],
            pilot_id,
            request_bytes,
        )
        fg1.persist_attempts(
            run_dir / "pilot",
            pilot_id,
            dispatch,
            (credentials[slot_id],),
        )
        raw_path: str | None = None
        raw_sha: str | None = None
        if dispatch.terminal_body is not None:
            raw = run_dir / "pilot" / "raw" / f"{slot_id}.json"
            fg1.atomic_write(raw, dispatch.terminal_body)
            raw_path = f"pilot/raw/{slot_id}.json"
            raw_sha = sha256_bytes(dispatch.terminal_body)
        status, reason, finish, termination = pilot_status(
            parent, slot_id, dispatch
        )
        value = {
            "schema_version": "effectslice-fg2-output-budget-pilot-result.v1",
            "pilot_execution_id": pilot_id,
            "model_slot_id": slot_id,
            "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias,
            "status": status,
            "reason": reason,
            "provider_finish_reason": finish,
            "termination_reason": termination,
            "logical_request_count": 1,
            "transport_attempt_count": len(dispatch.attempts),
            "raw_response_path": raw_path,
            "raw_response_sha256": raw_sha,
            "credential_value_recorded": False,
            "completed_at_utc": utc_now(),
        }
        write_json(result_path, value)
        results.append(value)
    summary = {
        "schema_version": "effectslice-fg2-output-budget-pilot-summary.v1",
        "output_budget": NEW_OUTPUT_BUDGET,
        "slots": results,
        "available_slot_count": sum(
            item["status"] == "available" for item in results
        ),
        "all_slots_available": all(
            item["status"] == "available" for item in results
        ),
        "credential_values_recorded": False,
        "registered_experiment_rows_consumed": 0,
        "completed_at_utc": utc_now(),
    }
    write_json(run_dir / "pilot_summary.json", summary)
    manifest = load_json(run_dir / "run_manifest.json")
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    return summary


class OverlayResolver:
    def __init__(self, parent: Path, successor: Path):
        self.parent = fg1.windows_extended_path(parent)
        self.successor = fg1.windows_extended_path(successor)
        self.parent_rows = {
            str(row["execution_id"]): row
            for row in load_json(
                self.parent / "global_remote_schedule.json"
            )["rows"]
        }
        self.parent_resolver = fg1.RowResolver(self.parent)

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        parent_id = str(row["parent_execution_id"])
        require(parent_id in self.parent_rows, "unknown overlay parent row")
        parent_inputs = self.parent_resolver.resolve(self.parent_rows[parent_id])
        request_path = self.successor / "requests" / f"{row['execution_id']}.json"
        request_bytes = request_path.read_bytes()
        require(
            sha256_bytes(request_bytes) == row["serialized_wire_request_sha256"],
            "overlay request SHA changed",
        )
        return fg1.RowInputs(
            task_dir=parent_inputs.task_dir,
            request_path=request_path,
            request_bytes=request_bytes,
            payload_path=parent_inputs.payload_path,
            fixture_path=parent_inputs.fixture_path,
            scorer_path=parent_inputs.scorer_path,
            candidate_path=parent_inputs.candidate_path,
            candidate_tokens=parent_inputs.candidate_tokens,
        )


def progress_summary(
    run_dir: Path, schedule: list[dict[str, Any]]
) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    by_slot: dict[str, int] = {}
    completed = 0
    for row in schedule:
        path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not path.exists():
            continue
        value = load_json(path)
        completed += 1
        outcome = str(value["terminal_outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        slot_id = str(row["model_slot_id"])
        by_slot[slot_id] = by_slot.get(slot_id, 0) + 1
    return {
        "schema_version": "effectslice-fg2-remote-progress.v1",
        "updated_at_utc": utc_now(),
        "registered_rows": len(schedule),
        "terminal_rows": completed,
        "remaining_rows": len(schedule) - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def run_schedule(
    parent: Path,
    successor: Path,
    run_dir: Path,
    docs_dir: Path,
    max_new_rows: int | None,
) -> dict[str, Any]:
    verify_successor(parent, successor)
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    pilot = load_json(run_dir / "pilot_summary.json")
    require(pilot.get("all_slots_available") is True, "FG2 pilot did not pass")
    credentials, metadata = fg1.load_credentials(docs_dir)
    manifest = initialize_run_manifest(run_dir, successor, metadata)
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    schedule = load_json(successor / "global_remote_schedule.json")["rows"]
    resolver = OverlayResolver(parent, successor)
    new_rows = 0
    for row in schedule:
        execution_id = str(row["execution_id"])
        row_path = run_dir / "rows" / f"{execution_id}.json"
        started = run_dir / "dispatch" / f"{execution_id}.started.json"
        terminal = run_dir / "dispatch" / f"{execution_id}.terminal.json"
        if row_path.exists():
            fg1.validate_existing_row(parent, row_path, row)
            continue
        if max_new_rows is not None and new_rows >= max_new_rows:
            break
        require(
            not started.exists(),
            f"ambiguous FG2 dispatch lacks terminal result: {execution_id}",
        )
        inputs = resolver.resolve(row)
        write_json(
            started,
            {
                "schema_version": "effectslice-fg2-dispatch-start.v1",
                "execution_id": execution_id,
                "parent_execution_id": row["parent_execution_id"],
                "model_slot_id": row["model_slot_id"],
                "serialized_wire_request_sha256": row[
                    "serialized_wire_request_sha256"
                ],
                "started_at_utc": utc_now(),
                "semantic_rerun_allowed": False,
                "fg2_is_new_versioned_execution": True,
            },
        )
        result = fg1.execute_row(
            parent,
            run_dir,
            row,
            inputs,
            credentials[str(row["model_slot_id"])],
        )
        fg1.write_row(run_dir, row, result, parent)
        write_json(
            terminal,
            {
                "schema_version": "effectslice-fg2-dispatch-terminal.v1",
                "execution_id": execution_id,
                "terminal_outcome": result["terminal_outcome"],
                "result_row_sha256": sha256_file(row_path),
                "recovered_from_terminal_row": False,
            },
        )
        new_rows += 1
        if new_rows % 5 == 0:
            progress = progress_summary(run_dir, schedule)
            write_json(run_dir / "progress.json", progress)
            print(
                f"terminal_rows={progress['terminal_rows']}/1296",
                flush=True,
            )
    progress = progress_summary(run_dir, schedule)
    write_json(run_dir / "progress.json", progress)
    return progress


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "verify", "pilot", "run"))
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "freeze":
        manifest = freeze_successor(args.parent, args.successor)
        value = {
            "status": "passed",
            "bundle_sha256": manifest["bundle_sha256"],
            "file_count": manifest["file_count"],
            "provider_calls_started": manifest["provider_calls_started"],
        }
    elif args.command == "verify":
        value = verify_successor(args.parent, args.successor)
    elif args.command == "pilot":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = run_pilot(
            args.parent,
            args.successor,
            args.run_dir,
            args.docs_dir.resolve(),
        )
    else:
        require(args.docs_dir is not None, "--docs-dir is required")
        require(
            args.max_new_rows is None or args.max_new_rows > 0,
            "--max-new-rows must be positive",
        )
        value = run_schedule(
            args.parent,
            args.successor,
            args.run_dir,
            args.docs_dir.resolve(),
            args.max_new_rows,
        )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SuccessorError, fg1.ExecutionError, fg1.IntegrityError) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
