from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

import format_conformance_successor as fg3
import output_budget_successor as fg2
import remote_execution_runner as fg1


FORWARD_ROOT = Path(__file__).resolve().parent
DEFAULT_PARENT = FORWARD_ROOT / "materialization_remote_only_2026-07-23"
DEFAULT_FG2 = FORWARD_ROOT / "output_budget_successor_2026-07-23"
DEFAULT_FG3 = FORWARD_ROOT / "format_conformance_successor_2026-07-23"
DEFAULT_SUCCESSOR = FORWARD_ROOT / "interface_contract_successor_2026-07-24"
DEFAULT_RUN_DIR = FORWARD_ROOT / "remote_execution_v4_2026-07-24"
EXPECTED_FG3_BUNDLE = "1a5212ee09f43b4e97737f83fc1365e0181942b790bd0a54920609d35b24766d"
FORMAT_VERSION = "fg4-explicit-payload-interface-v1"
INTERFACE_INSTRUCTION = (
    "[EXPLICIT CASE INTERFACE]\n"
    "The evaluator invokes solve(case) once for each fixture row. The argument "
    "is exactly the inner object stored in that row's payload field. Do not "
    "expect case_id, seed, or any outer fixture-row keys; use only fields present "
    "in the payload object. Return the result for that payload.\n\n"
)
PILOT_MARKER = "[INTERFACE-CONTRACT PILOT - NOT SCORED]\nThis request is excluded from every experiment estimate.\n\n"


class InterfaceSuccessorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InterfaceSuccessorError(message)


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


def visible_request_text(value: dict[str, Any]) -> tuple[str, Any]:
    if isinstance(value.get("input"), str):
        return "input", value["input"]
    messages = value.get("messages")
    require(isinstance(messages, list) and len(messages) == 1, "request must contain one message or one input string")
    message = messages[0]
    require(isinstance(message, dict) and isinstance(message.get("content"), str), "message content is not a string")
    return "message", message


def transformed_request_bytes(fg3_request_bytes: bytes, *, pilot: bool = False) -> bytes:
    value = json.loads(fg3_request_bytes.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), "FG3 request must be a JSON object")
    budget_key = fg2.output_budget_key(value)
    require(value[budget_key] == fg2.NEW_OUTPUT_BUDGET, "FG3 output budget changed")
    kind, target = visible_request_text(value)
    current = str(target if kind == "input" else target["content"])
    if pilot:
        require(current.startswith(fg3.PILOT_MARKER + fg3.FORMAT_INSTRUCTION), "FG3 pilot prefix changed")
        prefix = PILOT_MARKER + INTERFACE_INSTRUCTION
    else:
        require(current.startswith(fg3.FORMAT_INSTRUCTION), "FG3 request format prefix changed")
        prefix = INTERFACE_INSTRUCTION
    visible = prefix + current
    if kind == "input":
        value["input"] = visible
    else:
        target["content"] = visible
    return canonical_json(value)


def execution_id(fg3_execution_id: str) -> str:
    digest = hashlib.sha256(f"{FORMAT_VERSION}|{fg3_execution_id}".encode("utf-8")).hexdigest()[:24]
    return "fg4-exec-" + digest


def pilot_execution_id(slot_id: str) -> str:
    digest = hashlib.sha256(f"{FORMAT_VERSION}|pilot|{slot_id}".encode("utf-8")).hexdigest()[:20]
    return "fg4-pilot-" + digest


def fg3_request_path(fg3_root: Path, row: dict[str, Any]) -> Path:
    return fg3_root / "requests" / f"{row['execution_id']}.json"


def manifest_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name == "successor_manifest.json":
            continue
        files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return files


def bundle_sha(files: list[dict[str, Any]]) -> str:
    return sha256_bytes(canonical_json({
        "schema_version": "effectslice-fg4-successor-binding.v1",
        "fg3_successor_bundle_sha256": EXPECTED_FG3_BUNDLE,
        "format_contract_version": FORMAT_VERSION,
        "files": files,
    }))


def freeze_successor(parent: Path, fg2_root: Path, fg3_root: Path, successor: Path) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    fg3_root = fg1.windows_extended_path(fg3_root)
    successor = fg1.windows_extended_path(successor)
    fg3_result = fg3.verify_successor(parent, fg2_root, fg3_root)
    require(fg3_result["bundle_sha256"] == EXPECTED_FG3_BUNDLE, "FG3 bundle binding changed")
    require(not successor.exists(), "FG4 successor directory already exists")
    temporary = successor.with_name(successor.name + ".tmp")
    require(not temporary.exists(), "FG4 temporary directory already exists")
    temporary.mkdir(parents=True)
    try:
        fg3_rows = load_json(fg3_root / "global_remote_schedule.json")["rows"]
        require(len(fg3_rows) == 1296, "FG3 schedule row count changed")
        rows: list[dict[str, Any]] = []
        for fg3_row in fg3_rows:
            fg3_id = str(fg3_row["execution_id"])
            request_path = fg3_request_path(fg3_root, fg3_row)
            require(sha256_file(request_path) == fg3_row["serialized_wire_request_sha256"], f"FG3 request SHA changed: {fg3_id}")
            new_id = execution_id(fg3_id)
            request_bytes = transformed_request_bytes(request_path.read_bytes())
            fg1.atomic_write(temporary / "requests" / f"{new_id}.json", request_bytes)
            row = copy.deepcopy(fg3_row)
            row["fg2_execution_id"] = fg3_row["parent_execution_id"]
            row["fg3_execution_id"] = fg3_id
            row["parent_execution_id"] = fg3_id
            row["execution_id"] = new_id
            row["interface_contract_version"] = FORMAT_VERSION
            row["serialized_wire_request_sha256"] = sha256_bytes(request_bytes)
            rows.append(row)
        require(len({row["execution_id"] for row in rows}) == 1296, "FG4 execution IDs are not unique")
        write_json(temporary / "global_remote_schedule.json", {
            "schema_version": "effectslice-fg4-remote-schedule.v1",
            "fg3_successor_bundle_sha256": EXPECTED_FG3_BUNDLE,
            "interface_contract_version": FORMAT_VERSION,
            "registered_rows": 1296,
            "rows": rows,
        })

        fg3_pilot = load_json(fg3_root / "pilot_manifest.json")
        pilot_rows: list[dict[str, Any]] = []
        for item in fg3_pilot["rows"]:
            slot_id = str(item["model_slot_id"])
            source = fg3_root / str(item["request_path"])
            request_bytes = transformed_request_bytes(source.read_bytes(), pilot=True)
            path = temporary / "pilot" / "requests" / f"{slot_id}.json"
            fg1.atomic_write(path, request_bytes)
            pilot_rows.append({
                "pilot_execution_id": pilot_execution_id(slot_id),
                "model_slot_id": slot_id,
                "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias,
                "source_fg3_pilot_execution_id": item["pilot_execution_id"],
                "request_path": f"pilot/requests/{slot_id}.json",
                "serialized_wire_request_sha256": sha256_bytes(request_bytes),
                "registered_experiment_row": False,
                "scored": False,
            })
        write_json(temporary / "pilot_manifest.json", {
            "schema_version": "effectslice-fg4-interface-pilot.v1",
            "output_budget": fg2.NEW_OUTPUT_BUDGET,
            "interface_contract_version": FORMAT_VERSION,
            "interface_instruction": INTERFACE_INSTRUCTION,
            "pilot_marker": PILOT_MARKER,
            "pass_rule": "All six exact aliases must return a non-truncated bare JSON object containing exactly one nonempty implementation string.",
            "registered_experiment_rows_consumed": 0,
            "rows": pilot_rows,
        })
        write_json(temporary / "registration.json", {
            "schema_version": "effectslice-fg4-interface-successor.v1",
            "created_at_utc": fg1.utc_now(),
            "fg3_successor_bundle_sha256": EXPECTED_FG3_BUNDLE,
            "fg3_or_earlier_rows_pooled_with_fg4": False,
            "output_budget": fg2.NEW_OUTPUT_BUDGET,
            "interface_contract_version": FORMAT_VERSION,
            "allowed_request_mutation": "prepend one uniform explicit payload-interface instruction",
            "task_candidate_registry_scorer_mutation": False,
            "model_alias_or_endpoint_mutation": False,
            "registered_rows": 1296,
            "pilot_required_before_registered_execution": True,
            "solve_case_argument": "fixture row payload field contents",
        })
        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-fg4-successor-manifest.v1",
            "fg3_successor_bundle_sha256": EXPECTED_FG3_BUNDLE,
            "interface_contract_version": FORMAT_VERSION,
            "files": files,
            "file_count": len(files),
            "bundle_sha256": bundle_sha(files),
            "provider_calls_started": False,
        }
        write_json(temporary / "successor_manifest.json", manifest)
        os.replace(temporary, successor)
        return manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_successor(parent: Path, fg2_root: Path, fg3_root: Path, successor: Path) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    fg3_root = fg1.windows_extended_path(fg3_root)
    successor = fg1.windows_extended_path(successor)
    fg3_result = fg3.verify_successor(parent, fg2_root, fg3_root)
    require(fg3_result["bundle_sha256"] == EXPECTED_FG3_BUNDLE, "FG3 bundle changed")
    manifest = load_json(successor / "successor_manifest.json")
    files = manifest_files(successor)
    require(files == manifest["files"], "FG4 file manifest changed")
    require(bundle_sha(files) == manifest["bundle_sha256"], "FG4 bundle SHA changed")
    registration = load_json(successor / "registration.json")
    require(registration["fg3_successor_bundle_sha256"] == EXPECTED_FG3_BUNDLE, "FG3 registration binding changed")
    fg3_rows = load_json(fg3_root / "global_remote_schedule.json")["rows"]
    rows = load_json(successor / "global_remote_schedule.json")["rows"]
    require(len(fg3_rows) == len(rows) == 1296, "FG4 row count changed")
    fg3_by_id = {str(row["execution_id"]): row for row in fg3_rows}
    seen: set[str] = set()
    for row in rows:
        fg3_id = str(row["fg3_execution_id"])
        require(fg3_id in fg3_by_id, "unknown FG3 parent row")
        source_row = fg3_by_id[fg3_id]
        new_id = execution_id(fg3_id)
        require(row["execution_id"] == new_id and row["parent_execution_id"] == fg3_id, "FG4 execution lineage changed")
        require(new_id not in seen, "duplicate FG4 execution ID")
        seen.add(new_id)
        source = fg3_request_path(fg3_root, source_row)
        expected_bytes = transformed_request_bytes(source.read_bytes())
        request_path = successor / "requests" / f"{new_id}.json"
        require(request_path.read_bytes() == expected_bytes, "FG4 request changed")
        require(row["serialized_wire_request_sha256"] == sha256_bytes(expected_bytes), "FG4 request SHA changed")
        expected_row = copy.deepcopy(source_row)
        expected_row["fg2_execution_id"] = source_row["parent_execution_id"]
        expected_row["fg3_execution_id"] = fg3_id
        expected_row["parent_execution_id"] = fg3_id
        expected_row["execution_id"] = new_id
        expected_row["interface_contract_version"] = FORMAT_VERSION
        expected_row["serialized_wire_request_sha256"] = sha256_bytes(expected_bytes)
        require(row == expected_row, "FG4 row changed outside allowed fields")
    pilot = load_json(successor / "pilot_manifest.json")
    require(len(pilot["rows"]) == len(fg1.PROVIDER_SPECS) == 6, "FG4 pilot row count changed")
    for item in pilot["rows"]:
        slot_id = str(item["model_slot_id"])
        path = successor / str(item["request_path"])
        require(sha256_file(path) == item["serialized_wire_request_sha256"], "FG4 pilot request SHA changed")
        value = load_json(path)
        budget_key = fg2.output_budget_key(value)
        require(value[budget_key] == fg2.NEW_OUTPUT_BUDGET, "FG4 pilot budget changed")
        kind, target = visible_request_text(value)
        visible = target if kind == "input" else target["content"]
        require(visible.startswith(PILOT_MARKER + INTERFACE_INSTRUCTION + fg3.PILOT_MARKER + fg3.FORMAT_INSTRUCTION), "FG4 pilot prefix changed")
        require(value["model"] == fg1.PROVIDER_SPECS[slot_id].exact_alias, "FG4 pilot alias changed")
    return {
        "status": "passed",
        "bundle_sha256": manifest["bundle_sha256"],
        "registered_rows": 1296,
        "pilot_rows": 6,
        "output_budget": fg2.NEW_OUTPUT_BUDGET,
        "interface_contract_version": FORMAT_VERSION,
    }


def initialize_run_manifest(run_dir: Path, successor: Path, credential_metadata: dict[str, Any]) -> dict[str, Any]:
    successor_manifest = load_json(successor / "successor_manifest.json")
    path = run_dir / "run_manifest.json"
    expected = {
        "schema_version": "effectslice-fg4-remote-run.v1",
        "successor_bundle_sha256": successor_manifest["bundle_sha256"],
        "fg3_successor_bundle_sha256": EXPECTED_FG3_BUNDLE,
        "interface_contract_version": FORMAT_VERSION,
        "registered_rows": 1296,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
    }
    if path.exists():
        current = load_json(path)
        for key, value in expected.items():
            require(current.get(key) == value, f"FG4 run manifest {key} changed")
        return current
    value = {**expected, "created_at_utc": fg1.utc_now(), "provider_calls_started": False}
    write_json(path, value)
    return value


def run_pilot(parent: Path, fg2_root: Path, fg3_root: Path, successor: Path, run_dir: Path, docs_dir: Path) -> dict[str, Any]:
    verify_successor(parent, fg2_root, fg3_root, successor)
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
            require(value["pilot_execution_id"] == pilot_id, "FG4 pilot ID changed")
            results.append(value)
            continue
        require(not started_path.exists(), f"ambiguous FG4 pilot dispatch lacks terminal result: {slot_id}")
        write_json(started_path, {"schema_version": "effectslice-fg4-pilot-start.v1", "pilot_execution_id": pilot_id, "model_slot_id": slot_id, "started_at_utc": fg1.utc_now(), "semantic_rerun_allowed": False})
        request_bytes = (successor / str(item["request_path"])).read_bytes()
        require(sha256_bytes(request_bytes) == item["serialized_wire_request_sha256"], "FG4 pilot request changed before dispatch")
        dispatch = fg1.dispatch_request(fg1.PROVIDER_SPECS[slot_id], credentials[slot_id], pilot_id, request_bytes)
        fg1.persist_attempts(run_dir / "pilot", pilot_id, dispatch, (credentials[slot_id],))
        raw_path: str | None = None
        raw_sha: str | None = None
        if dispatch.terminal_body is not None:
            raw = run_dir / "pilot" / "raw" / f"{slot_id}.json"
            fg1.atomic_write(raw, dispatch.terminal_body)
            raw_path, raw_sha = f"pilot/raw/{slot_id}.json", sha256_bytes(dispatch.terminal_body)
        status, reason, finish, termination = fg2.pilot_status(parent, slot_id, dispatch)
        value = {"schema_version": "effectslice-fg4-interface-pilot-result.v1", "pilot_execution_id": pilot_id, "model_slot_id": slot_id, "exact_alias": fg1.PROVIDER_SPECS[slot_id].exact_alias, "status": status, "reason": reason, "provider_finish_reason": finish, "termination_reason": termination, "logical_request_count": 1, "transport_attempt_count": len(dispatch.attempts), "raw_response_path": raw_path, "raw_response_sha256": raw_sha, "credential_value_recorded": False, "completed_at_utc": fg1.utc_now()}
        write_json(result_path, value)
        results.append(value)
    summary = {"schema_version": "effectslice-fg4-interface-pilot-summary.v1", "interface_contract_version": FORMAT_VERSION, "output_budget": fg2.NEW_OUTPUT_BUDGET, "slots": results, "available_slot_count": sum(item["status"] == "available" for item in results), "all_slots_available": all(item["status"] == "available" for item in results), "credential_values_recorded": False, "registered_experiment_rows_consumed": 0, "completed_at_utc": fg1.utc_now()}
    write_json(run_dir / "pilot_summary.json", summary)
    manifest = load_json(run_dir / "run_manifest.json")
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    return summary


class OverlayResolver:
    def __init__(self, parent: Path, fg2_root: Path, fg3_root: Path, successor: Path):
        self.parent = fg1.windows_extended_path(parent)
        self.fg2_root = fg1.windows_extended_path(fg2_root)
        self.fg3_root = fg1.windows_extended_path(fg3_root)
        self.successor = fg1.windows_extended_path(successor)
        self.fg3_rows = {str(row["execution_id"]): row for row in load_json(self.fg3_root / "global_remote_schedule.json")["rows"]}
        self.fg3_resolver = fg3.OverlayResolver(self.parent, self.fg2_root, self.fg3_root)

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        parent_id = str(row["parent_execution_id"])
        require(parent_id in self.fg3_rows, "unknown FG4 parent row")
        parent_inputs = self.fg3_resolver.resolve(self.fg3_rows[parent_id])
        request_path = self.successor / "requests" / f"{row['execution_id']}.json"
        request_bytes = request_path.read_bytes()
        require(sha256_bytes(request_bytes) == row["serialized_wire_request_sha256"], "FG4 request SHA changed")
        return fg1.RowInputs(task_dir=parent_inputs.task_dir, request_path=request_path, request_bytes=request_bytes, payload_path=parent_inputs.payload_path, fixture_path=parent_inputs.fixture_path, scorer_path=parent_inputs.scorer_path, candidate_path=parent_inputs.candidate_path, candidate_tokens=parent_inputs.candidate_tokens)


def progress_summary(run_dir: Path, schedule: list[dict[str, Any]]) -> dict[str, Any]:
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
    return {"schema_version": "effectslice-fg4-remote-progress.v1", "updated_at_utc": fg1.utc_now(), "registered_rows": len(schedule), "terminal_rows": completed, "remaining_rows": len(schedule) - completed, "terminal_outcomes": dict(sorted(outcomes.items())), "terminal_rows_by_model_slot": dict(sorted(by_slot.items()))}


def run_schedule(parent: Path, fg2_root: Path, fg3_root: Path, successor: Path, run_dir: Path, docs_dir: Path, max_new_rows: int | None) -> dict[str, Any]:
    verify_successor(parent, fg2_root, fg3_root, successor)
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    pilot = load_json(run_dir / "pilot_summary.json")
    require(pilot.get("all_slots_available") is True, "FG4 pilot did not pass")
    credentials, metadata = fg1.load_credentials(docs_dir)
    manifest = initialize_run_manifest(run_dir, successor, metadata)
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    schedule = load_json(successor / "global_remote_schedule.json")["rows"]
    resolver = OverlayResolver(parent, fg2_root, fg3_root, successor)
    new_rows = 0
    for row in schedule:
        execution = str(row["execution_id"])
        row_path = run_dir / "rows" / f"{execution}.json"
        started = run_dir / "dispatch" / f"{execution}.started.json"
        terminal = run_dir / "dispatch" / f"{execution}.terminal.json"
        if row_path.exists():
            fg1.validate_existing_row(parent, row_path, row)
            continue
        if max_new_rows is not None and new_rows >= max_new_rows:
            break
        require(not started.exists(), f"ambiguous FG4 dispatch lacks terminal result: {execution}")
        inputs = resolver.resolve(row)
        write_json(started, {"schema_version": "effectslice-fg4-dispatch-start.v1", "execution_id": execution, "parent_execution_id": row["parent_execution_id"], "model_slot_id": row["model_slot_id"], "serialized_wire_request_sha256": row["serialized_wire_request_sha256"], "started_at_utc": fg1.utc_now(), "semantic_rerun_allowed": False, "fg4_is_new_versioned_execution": True, "interface_contract_version": FORMAT_VERSION})
        result = fg1.execute_row(parent, run_dir, row, inputs, credentials[str(row["model_slot_id"])])
        fg1.write_row(run_dir, row, result, parent)
        write_json(terminal, {"schema_version": "effectslice-fg4-dispatch-terminal.v1", "execution_id": execution, "terminal_outcome": result["terminal_outcome"], "result_row_sha256": sha256_file(row_path), "recovered_from_terminal_row": False})
        new_rows += 1
        if new_rows % 5 == 0:
            progress = progress_summary(run_dir, schedule)
            write_json(run_dir / "progress.json", progress)
            print(f"terminal_rows={progress['terminal_rows']}/1296", flush=True)
    progress = progress_summary(run_dir, schedule)
    write_json(run_dir / "progress.json", progress)
    return progress


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "verify", "pilot", "run"))
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--fg2", type=Path, default=DEFAULT_FG2)
    parser.add_argument("--fg3", type=Path, default=DEFAULT_FG3)
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "freeze":
        manifest = freeze_successor(args.parent, args.fg2, args.fg3, args.successor)
        value = {"status": "passed", "bundle_sha256": manifest["bundle_sha256"], "file_count": manifest["file_count"], "provider_calls_started": manifest["provider_calls_started"]}
    elif args.command == "verify":
        value = verify_successor(args.parent, args.fg2, args.fg3, args.successor)
    elif args.command == "pilot":
        require(args.docs_dir is not None, "--docs-dir is required")
        value = run_pilot(args.parent, args.fg2, args.fg3, args.successor, args.run_dir, args.docs_dir.resolve())
    else:
        require(args.docs_dir is not None, "--docs-dir is required")
        require(args.max_new_rows is None or args.max_new_rows > 0, "--max-new-rows must be positive")
        value = run_schedule(args.parent, args.fg2, args.fg3, args.successor, args.run_dir, args.docs_dir.resolve(), args.max_new_rows)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InterfaceSuccessorError, fg3.FormatSuccessorError, fg2.SuccessorError, fg1.ExecutionError, fg1.IntegrityError) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
