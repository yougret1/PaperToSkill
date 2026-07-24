from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import build_fg5_output_contracts as contracts
import interface_contract_successor as fg4


fg3 = fg4.fg3
fg2 = fg4.fg2
fg1 = fg4.fg1

FORWARD_ROOT = Path(__file__).resolve().parent
DEFAULT_PARENT = fg4.DEFAULT_PARENT
DEFAULT_FG2 = fg4.DEFAULT_FG2
DEFAULT_FG3 = fg4.DEFAULT_FG3
DEFAULT_FG4 = fg4.DEFAULT_SUCCESSOR
DEFAULT_FG4_RUN = fg4.DEFAULT_RUN_DIR
DEFAULT_CONTRACTS = contracts.DEFAULT_OUTPUT
DEFAULT_SUCCESSOR = FORWARD_ROOT / "output_contract_successor_2026-07-24"
DEFAULT_RUN_DIR = FORWARD_ROOT / "remote_execution_v5_development_2026-07-24"
DEFAULT_FINAL_REPORT = (
    FORWARD_ROOT
    / "fg5_development_2026-07-24"
    / "exact_output_contract_final_report.json"
)
EXPECTED_FG4_BUNDLE = (
    "223f73a98c258c5340b812a8529a802e12b5162c741dff332115996ca2b3024a"
)
FORMAT_VERSION = "fg5-task-output-contract-v1"


class OutputContractSuccessorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OutputContractSuccessorError(message)


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


def load_contract_registry(path: Path) -> tuple[dict[str, str], str]:
    verification = contracts.verify_registry(path)
    value = load_json(path)
    prompts = {str(row["task_id"]): str(row["prompt"]) for row in value["tasks"]}
    require(len(prompts) == value["task_count"] == 24, "output contract task count changed")
    return prompts, str(verification["registry_sha256"])


def transformed_request_bytes(
    fg4_request_bytes: bytes,
    *,
    task_id: str,
    prompt: str,
) -> bytes:
    value = json.loads(fg4_request_bytes.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), "FG4 request must be a JSON object")
    kind, target = fg4.visible_request_text(value)
    current = str(target if kind == "input" else target["content"])
    required_prefix = fg4.INTERFACE_INSTRUCTION + fg3.FORMAT_INSTRUCTION
    require(current.startswith(required_prefix), "FG4 visible prefix changed")
    require(prompt.startswith("[EXACT OUTPUT CONTRACT]\n"), "invalid output contract prompt")
    require(f"For task {task_id}," in prompt, "task/output contract mismatch")
    visible = fg4.INTERFACE_INSTRUCTION + prompt + current[len(fg4.INTERFACE_INSTRUCTION) :]
    if kind == "input":
        value["input"] = visible
    else:
        target["content"] = visible
    return canonical_json(value)


def execution_id(fg4_execution_id: str, registry_sha256: str) -> str:
    digest = hashlib.sha256(
        f"{FORMAT_VERSION}|{registry_sha256}|{fg4_execution_id}".encode("utf-8")
    ).hexdigest()[:24]
    return "fg5-exec-" + digest


def manifest_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name in {
            "successor_manifest.json",
            "freeze.json",
        }:
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def bundle_sha(files: list[dict[str, Any]], registry_sha256: str) -> str:
    return sha256_bytes(
        canonical_json(
            {
                "schema_version": "effectslice-fg5-successor-binding.v1",
                "fg4_successor_bundle_sha256": EXPECTED_FG4_BUNDLE,
                "output_contract_registry_sha256": registry_sha256,
                "format_contract_version": FORMAT_VERSION,
                "files": files,
            }
        )
    )


def _install_development(
    temporary: Path,
    successor: Path,
    run_dir: Path,
    *,
    replace: bool,
) -> None:
    if not successor.exists():
        os.replace(temporary, successor)
        return
    require(replace, "FG5 development successor already exists; use rebuild")
    require(not (successor / "freeze.json").exists(), "frozen FG5 successor cannot be rebuilt")
    successor_backup = successor.with_name(successor.name + ".replaced")
    run_backup = run_dir.with_name(run_dir.name + ".replaced")
    require(not successor_backup.exists(), "stale FG5 successor replacement backup exists")
    require(not run_backup.exists(), "stale FG5 run replacement backup exists")
    os.replace(successor, successor_backup)
    run_moved = False
    try:
        if run_dir.exists():
            os.replace(run_dir, run_backup)
            run_moved = True
        os.replace(temporary, successor)
    except Exception:
        if run_moved and run_backup.exists():
            os.replace(run_backup, run_dir)
        if successor_backup.exists():
            os.replace(successor_backup, successor)
        raise
    shutil.rmtree(successor_backup)
    if run_moved:
        shutil.rmtree(run_backup)


def build_successor(
    parent: Path,
    fg2_root: Path,
    fg3_root: Path,
    fg4_root: Path,
    contract_path: Path,
    successor: Path,
    run_dir: Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    fg3_root = fg1.windows_extended_path(fg3_root)
    fg4_root = fg1.windows_extended_path(fg4_root)
    contract_path = fg1.windows_extended_path(contract_path)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    fg4_result = fg4.verify_successor(parent, fg2_root, fg3_root, fg4_root)
    require(fg4_result["bundle_sha256"] == EXPECTED_FG4_BUNDLE, "FG4 bundle binding changed")
    prompts, registry_sha256 = load_contract_registry(contract_path)
    temporary = successor.with_name(successor.name + ".tmp")
    require(not temporary.exists(), "FG5 temporary directory already exists")
    temporary.mkdir(parents=True)
    try:
        fg4_rows = load_json(fg4_root / "global_remote_schedule.json")["rows"]
        require(len(fg4_rows) == 1296, "FG4 schedule row count changed")
        rows: list[dict[str, Any]] = []
        for fg4_row in fg4_rows:
            fg4_id = str(fg4_row["execution_id"])
            task_id = str(fg4_row["task_id"])
            require(task_id in prompts, f"missing output contract: {task_id}")
            source = fg4_root / "requests" / f"{fg4_id}.json"
            require(
                sha256_file(source) == fg4_row["serialized_wire_request_sha256"],
                f"FG4 request SHA changed: {fg4_id}",
            )
            new_id = execution_id(fg4_id, registry_sha256)
            request_bytes = transformed_request_bytes(
                source.read_bytes(),
                task_id=task_id,
                prompt=prompts[task_id],
            )
            fg1.atomic_write(temporary / "requests" / f"{new_id}.json", request_bytes)
            row = copy.deepcopy(fg4_row)
            row["fg4_execution_id"] = fg4_id
            row["parent_execution_id"] = fg4_id
            row["execution_id"] = new_id
            row["output_contract_version"] = FORMAT_VERSION
            row["output_contract_prompt_sha256"] = sha256_bytes(
                prompts[task_id].encode("utf-8")
            )
            row["output_contract_registry_sha256"] = registry_sha256
            row["serialized_wire_request_sha256"] = sha256_bytes(request_bytes)
            rows.append(row)
        require(len({row["execution_id"] for row in rows}) == 1296, "FG5 execution IDs are not unique")
        write_json(
            temporary / "global_remote_schedule.json",
            {
                "schema_version": "effectslice-fg5-remote-schedule.v1",
                "fg4_successor_bundle_sha256": EXPECTED_FG4_BUNDLE,
                "output_contract_registry_sha256": registry_sha256,
                "output_contract_version": FORMAT_VERSION,
                "registered_rows": 1296,
                "rows": rows,
            },
        )
        write_json(
            temporary / "registration.json",
            {
                "schema_version": "effectslice-fg5-output-contract-successor.v1",
                "created_at_utc": fg1.utc_now(),
                "development_state": "mutable_until_class_validation_passes",
                "fg4_successor_bundle_sha256": EXPECTED_FG4_BUNDLE,
                "output_contract_registry_sha256": registry_sha256,
                "output_contract_version": FORMAT_VERSION,
                "allowed_request_mutation": "insert one task-specific public structural output contract",
                "task_candidate_registry_scorer_mutation": False,
                "model_alias_endpoint_budget_seed_mutation": False,
                "private_expected_outputs_persisted": False,
                "registered_rows": 1296,
                "direct_unbounded_run_disabled": True,
            },
        )
        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-fg5-development-manifest.v1",
            "fg4_successor_bundle_sha256": EXPECTED_FG4_BUNDLE,
            "output_contract_registry_sha256": registry_sha256,
            "output_contract_version": FORMAT_VERSION,
            "files": files,
            "file_count": len(files),
            "bundle_sha256": bundle_sha(files, registry_sha256),
            "provider_calls_started": False,
            "development_frozen": False,
        }
        write_json(temporary / "successor_manifest.json", manifest)
        _install_development(temporary, successor, run_dir, replace=replace)
        return manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_successor(
    parent: Path,
    fg2_root: Path,
    fg3_root: Path,
    fg4_root: Path,
    contract_path: Path,
    successor: Path,
) -> dict[str, Any]:
    parent = fg1.windows_extended_path(parent)
    fg2_root = fg1.windows_extended_path(fg2_root)
    fg3_root = fg1.windows_extended_path(fg3_root)
    fg4_root = fg1.windows_extended_path(fg4_root)
    contract_path = fg1.windows_extended_path(contract_path)
    successor = fg1.windows_extended_path(successor)
    fg4_result = fg4.verify_successor(parent, fg2_root, fg3_root, fg4_root)
    require(fg4_result["bundle_sha256"] == EXPECTED_FG4_BUNDLE, "FG4 bundle changed")
    prompts, registry_sha256 = load_contract_registry(contract_path)
    manifest = load_json(successor / "successor_manifest.json")
    files = manifest_files(successor)
    require(files == manifest["files"], "FG5 file manifest changed")
    require(bundle_sha(files, registry_sha256) == manifest["bundle_sha256"], "FG5 bundle SHA changed")
    frozen = manifest.get("development_frozen") is True
    freeze_path = successor / "freeze.json"
    if frozen:
        require(freeze_path.is_file(), "frozen FG5 successor lacks freeze record")
        freeze = load_json(freeze_path)
        require(
            freeze.get("schema_version") == "effectslice-fg5-development-freeze.v1",
            "FG5 freeze schema changed",
        )
        require(
            freeze.get("successor_bundle_sha256") == manifest["bundle_sha256"],
            "FG5 freeze bundle binding changed",
        )
        require(
            freeze.get("output_contract_registry_sha256") == registry_sha256,
            "FG5 freeze registry binding changed",
        )
        require(
            freeze.get("class_validation_passed") is True,
            "FG5 freeze lacks a passed class validation",
        )
    else:
        require(not freeze_path.exists(), "mutable FG5 successor has freeze record")
    fg4_rows = load_json(fg4_root / "global_remote_schedule.json")["rows"]
    rows = load_json(successor / "global_remote_schedule.json")["rows"]
    require(len(fg4_rows) == len(rows) == 1296, "FG5 row count changed")
    fg4_by_id = {str(row["execution_id"]): row for row in fg4_rows}
    seen: set[str] = set()
    for row in rows:
        fg4_id = str(row["parent_execution_id"])
        require(fg4_id in fg4_by_id, "unknown FG4 parent row")
        source_row = fg4_by_id[fg4_id]
        task_id = str(source_row["task_id"])
        new_id = execution_id(fg4_id, registry_sha256)
        require(row["execution_id"] == new_id and new_id not in seen, "FG5 execution lineage changed")
        seen.add(new_id)
        source = fg4_root / "requests" / f"{fg4_id}.json"
        expected_bytes = transformed_request_bytes(
            source.read_bytes(), task_id=task_id, prompt=prompts[task_id]
        )
        request_path = successor / "requests" / f"{new_id}.json"
        require(request_path.read_bytes() == expected_bytes, "FG5 request changed")
        expected_row = copy.deepcopy(source_row)
        expected_row["fg4_execution_id"] = fg4_id
        expected_row["parent_execution_id"] = fg4_id
        expected_row["execution_id"] = new_id
        expected_row["output_contract_version"] = FORMAT_VERSION
        expected_row["output_contract_prompt_sha256"] = sha256_bytes(
            prompts[task_id].encode("utf-8")
        )
        expected_row["output_contract_registry_sha256"] = registry_sha256
        expected_row["serialized_wire_request_sha256"] = sha256_bytes(expected_bytes)
        require(row == expected_row, "FG5 row changed outside allowed fields")
    return {
        "status": "passed",
        "bundle_sha256": manifest["bundle_sha256"],
        "output_contract_registry_sha256": registry_sha256,
        "registered_rows": 1296,
        "output_contract_version": FORMAT_VERSION,
        "development_frozen": frozen,
    }


def freeze_successor(
    parent: Path,
    fg2_root: Path,
    fg3_root: Path,
    fg4_root: Path,
    contract_path: Path,
    successor: Path,
    run_dir: Path,
    final_report_path: Path,
) -> dict[str, Any]:
    verification = verify_successor(
        parent, fg2_root, fg3_root, fg4_root, contract_path, successor
    )
    require(
        verification["development_frozen"] is False,
        "FG5 successor is already frozen",
    )
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    final_report_path = fg1.windows_extended_path(final_report_path)
    report = load_json(final_report_path)
    require(
        report.get("schema_version")
        == "effectslice-fg5-output-contract-final-report.v1",
        "FG5 final report schema changed",
    )
    require(
        report.get("class_name") == "exact_output_contract"
        and report.get("status") == "completed"
        and report.get("class_validation_passed") is True,
        "FG5 exact-output class validation did not pass",
    )
    require(
        report.get("selected_fg3_rows") == 684
        and report.get("terminal_fg5_rows") == 684
        and report.get("affected_tasks") == 24,
        "FG5 final report coverage changed",
    )
    progress_path = run_dir / "progress.json"
    run_manifest_path = run_dir / "run_manifest.json"
    progress = load_json(progress_path)
    run_manifest = load_json(run_manifest_path)
    require(progress.get("terminal_rows", 0) >= 684, "FG5 run coverage is incomplete")
    require(
        run_manifest.get("successor_bundle_sha256")
        == verification["bundle_sha256"],
        "FG5 run/successor binding changed",
    )
    frozen_at = fg1.utc_now()
    freeze = {
        "schema_version": "effectslice-fg5-development-freeze.v1",
        "frozen_at_utc": frozen_at,
        "successor_bundle_sha256": verification["bundle_sha256"],
        "output_contract_registry_sha256": verification[
            "output_contract_registry_sha256"
        ],
        "output_contract_version": FORMAT_VERSION,
        "class_name": "exact_output_contract",
        "class_validation_passed": True,
        "final_report_sha256": sha256_file(final_report_path),
        "run_manifest_sha256_before_freeze": sha256_file(run_manifest_path),
        "terminal_rows_at_freeze": progress["terminal_rows"],
        "request_bundle_changed_by_freeze": False,
        "further_provider_calls_allowed": False,
    }
    write_json(successor / "freeze.json", freeze)
    manifest_path = successor / "successor_manifest.json"
    manifest = load_json(manifest_path)
    manifest["development_frozen"] = True
    manifest["frozen_at_utc"] = frozen_at
    write_json(manifest_path, manifest)
    run_manifest["development_record_overwrite_allowed_before_freeze"] = False
    run_manifest["development_frozen"] = True
    run_manifest["frozen_at_utc"] = frozen_at
    run_manifest["freeze_record_sha256"] = sha256_file(successor / "freeze.json")
    write_json(run_manifest_path, run_manifest)
    verified = verify_successor(
        parent, fg2_root, fg3_root, fg4_root, contract_path, successor
    )
    require(verified["development_frozen"] is True, "FG5 freeze verification failed")
    return {
        **verified,
        "freeze_record_sha256": sha256_file(successor / "freeze.json"),
        "final_report_sha256": freeze["final_report_sha256"],
    }


class OverlayResolver:
    def __init__(
        self,
        parent: Path,
        fg2_root: Path,
        fg3_root: Path,
        fg4_root: Path,
        successor: Path,
    ):
        self.parent = fg1.windows_extended_path(parent)
        self.fg2_root = fg1.windows_extended_path(fg2_root)
        self.fg3_root = fg1.windows_extended_path(fg3_root)
        self.fg4_root = fg1.windows_extended_path(fg4_root)
        self.successor = fg1.windows_extended_path(successor)
        self.fg4_rows = {
            str(row["execution_id"]): row
            for row in load_json(self.fg4_root / "global_remote_schedule.json")["rows"]
        }
        self.fg4_resolver = fg4.OverlayResolver(
            self.parent, self.fg2_root, self.fg3_root, self.fg4_root
        )

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        parent_id = str(row["parent_execution_id"])
        require(parent_id in self.fg4_rows, "unknown FG5 parent row")
        parent_inputs = self.fg4_resolver.resolve(self.fg4_rows[parent_id])
        request_path = self.successor / "requests" / f"{row['execution_id']}.json"
        request_bytes = request_path.read_bytes()
        require(
            sha256_bytes(request_bytes) == row["serialized_wire_request_sha256"],
            "FG5 request SHA changed",
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


def initialize_run_manifest(
    run_dir: Path,
    successor: Path,
    credential_metadata: dict[str, Any],
) -> dict[str, Any]:
    successor_manifest = load_json(successor / "successor_manifest.json")
    path = run_dir / "run_manifest.json"
    expected = {
        "schema_version": "effectslice-fg5-development-run.v1",
        "successor_bundle_sha256": successor_manifest["bundle_sha256"],
        "fg4_successor_bundle_sha256": EXPECTED_FG4_BUNDLE,
        "output_contract_registry_sha256": successor_manifest[
            "output_contract_registry_sha256"
        ],
        "output_contract_version": FORMAT_VERSION,
        "registered_rows": 1296,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
        "development_record_overwrite_allowed_before_freeze": True,
    }
    if path.exists():
        current = load_json(path)
        for key, value in expected.items():
            require(current.get(key) == value, f"FG5 run manifest {key} changed")
        return current
    value = {
        **expected,
        "created_at_utc": fg1.utc_now(),
        "provider_calls_started": False,
    }
    write_json(path, value)
    return value


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
    return {
        "schema_version": "effectslice-fg5-development-progress.v1",
        "updated_at_utc": fg1.utc_now(),
        "registered_rows": len(schedule),
        "terminal_rows": completed,
        "remaining_rows": len(schedule) - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def _load_selection(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    value = load_json(path)
    execution_ids = value.get("execution_ids") if isinstance(value, dict) else value
    require(isinstance(execution_ids, list) and execution_ids, "selection manifest is empty")
    selected = {str(item) for item in execution_ids}
    require(len(selected) == len(execution_ids), "selection manifest has duplicates")
    return selected


def run_schedule(
    parent: Path,
    fg2_root: Path,
    fg3_root: Path,
    fg4_root: Path,
    fg4_run: Path,
    contract_path: Path,
    successor: Path,
    run_dir: Path,
    docs_dir: Path,
    max_new_rows: int,
    selection_path: Path | None = None,
    workers: int = 1,
) -> dict[str, Any]:
    successor_verification = verify_successor(
        parent, fg2_root, fg3_root, fg4_root, contract_path, successor
    )
    require(
        successor_verification["development_frozen"] is False,
        "frozen FG5 successor cannot execute additional rows",
    )
    require(max_new_rows > 0, "--max-new-rows must be positive")
    require(1 <= workers <= 6, "--workers must be between 1 and 6")
    parent = fg1.windows_extended_path(parent)
    successor = fg1.windows_extended_path(successor)
    run_dir = fg1.windows_extended_path(run_dir)
    fg4_run = fg1.windows_extended_path(fg4_run)
    pilot = load_json(fg4_run / "pilot_summary.json")
    require(pilot.get("all_slots_available") is True, "frozen FG4 pilot did not pass")
    credentials, metadata = fg1.load_credentials(docs_dir)
    manifest = initialize_run_manifest(run_dir, successor, metadata)
    manifest["provider_calls_started"] = True
    write_json(run_dir / "run_manifest.json", manifest)
    schedule = load_json(successor / "global_remote_schedule.json")["rows"]
    selected = _load_selection(selection_path)
    if selected is not None:
        known = {str(row["execution_id"]) for row in schedule}
        require(selected <= known, "selection manifest contains unknown FG5 IDs")
    resolver = OverlayResolver(parent, fg2_root, fg3_root, fg4_root, successor)
    pending: list[tuple[dict[str, Any], fg1.RowInputs, Path, Path, Path]] = []
    for row in schedule:
        execution = str(row["execution_id"])
        if selected is not None and execution not in selected:
            continue
        row_path = run_dir / "rows" / f"{execution}.json"
        started = run_dir / "dispatch" / f"{execution}.started.json"
        terminal = run_dir / "dispatch" / f"{execution}.terminal.json"
        if row_path.exists():
            fg1.validate_existing_row(parent, row_path, row)
            continue
        if len(pending) >= max_new_rows:
            break
        require(not started.exists(), f"ambiguous FG5 dispatch lacks terminal result: {execution}")
        inputs = resolver.resolve(row)
        pending.append((row, inputs, row_path, started, terminal))

    def execute_pending(
        item: tuple[dict[str, Any], fg1.RowInputs, Path, Path, Path]
    ) -> tuple[tuple[dict[str, Any], fg1.RowInputs, Path, Path, Path], dict[str, Any]]:
        local_row, local_inputs, _, local_started, _ = item
        write_json(
            local_started,
            {
                "schema_version": "effectslice-fg5-development-dispatch-start.v1",
                "execution_id": local_row["execution_id"],
                "parent_execution_id": local_row["parent_execution_id"],
                "model_slot_id": local_row["model_slot_id"],
                "serialized_wire_request_sha256": local_row[
                    "serialized_wire_request_sha256"
                ],
                "started_at_utc": fg1.utc_now(),
                "semantic_rerun_allowed": False,
                "fg5_is_new_versioned_execution": True,
                "output_contract_version": FORMAT_VERSION,
            },
        )
        result = fg1.execute_row(
            parent,
            run_dir,
            local_row,
            local_inputs,
            credentials[str(local_row["model_slot_id"])],
        )
        return item, result

    completed_new_rows = 0
    errors: list[tuple[str, BaseException]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_rows = {executor.submit(execute_pending, item): item for item in pending}
        for future in as_completed(future_rows):
            item = future_rows[future]
            row, _, row_path, _, terminal = item
            execution = str(row["execution_id"])
            try:
                _, result = future.result()
            except BaseException as exc:  # preserve other in-flight terminal evidence
                errors.append((execution, exc))
                continue
            fg1.write_row(run_dir, row, result, parent)
            write_json(
                terminal,
                {
                    "schema_version": "effectslice-fg5-development-dispatch-terminal.v1",
                    "execution_id": execution,
                    "terminal_outcome": result["terminal_outcome"],
                    "result_row_sha256": sha256_file(row_path),
                    "recovered_from_terminal_row": False,
                },
            )
            completed_new_rows += 1
            progress = progress_summary(run_dir, schedule)
            write_json(run_dir / "progress.json", progress)
            print(f"terminal_rows={progress['terminal_rows']}/1296", flush=True)
    require(
        not errors,
        "FG5 concurrent execution raised: "
        + "; ".join(f"{execution}: {type(exc).__name__}: {exc}" for execution, exc in errors),
    )
    progress = progress_summary(run_dir, schedule)
    progress["new_rows_this_invocation"] = completed_new_rows
    progress["workers"] = workers
    progress["selection_manifest_used"] = selection_path is not None
    write_json(run_dir / "progress.json", progress)
    return progress


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("build", "rebuild", "verify", "run", "freeze")
    )
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--fg2", type=Path, default=DEFAULT_FG2)
    parser.add_argument("--fg3", type=Path, default=DEFAULT_FG3)
    parser.add_argument("--fg4", type=Path, default=DEFAULT_FG4)
    parser.add_argument("--fg4-run", type=Path, default=DEFAULT_FG4_RUN)
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--final-report", type=Path, default=DEFAULT_FINAL_REPORT)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    parser.add_argument("--selection-manifest", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command in {"build", "rebuild"}:
        manifest = build_successor(
            args.parent,
            args.fg2,
            args.fg3,
            args.fg4,
            args.contracts,
            args.successor,
            args.run_dir,
            replace=args.command == "rebuild",
        )
        value = {
            "status": "passed",
            "bundle_sha256": manifest["bundle_sha256"],
            "file_count": manifest["file_count"],
            "development_frozen": manifest["development_frozen"],
        }
    elif args.command == "verify":
        value = verify_successor(
            args.parent,
            args.fg2,
            args.fg3,
            args.fg4,
            args.contracts,
            args.successor,
        )
    elif args.command == "freeze":
        value = freeze_successor(
            args.parent,
            args.fg2,
            args.fg3,
            args.fg4,
            args.contracts,
            args.successor,
            args.run_dir,
            args.final_report,
        )
    else:
        require(args.docs_dir is not None, "--docs-dir is required")
        require(args.max_new_rows is not None, "bounded --max-new-rows is required")
        value = run_schedule(
            args.parent,
            args.fg2,
            args.fg3,
            args.fg4,
            args.fg4_run,
            args.contracts,
            args.successor,
            args.run_dir,
            args.docs_dir.resolve(),
            args.max_new_rows,
            args.selection_manifest,
            args.workers,
        )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OutputContractSuccessorError,
        contracts.ContractRegistryError,
        fg4.InterfaceSuccessorError,
        fg3.FormatSuccessorError,
        fg2.SuccessorError,
        fg1.ExecutionError,
        fg1.IntegrityError,
    ) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
