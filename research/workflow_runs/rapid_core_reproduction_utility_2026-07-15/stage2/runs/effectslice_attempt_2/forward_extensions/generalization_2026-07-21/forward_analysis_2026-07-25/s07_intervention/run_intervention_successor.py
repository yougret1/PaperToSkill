from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from intervention_successor import (
    GENERALIZATION_ROOT,
    HERE,
    MATERIALIZATION,
    REGISTRATION,
    extended,
    load_json,
    sha256_file,
    verify_registration,
)


RUNNER_PATH = GENERALIZATION_ROOT / "remote_execution_runner.py"
RUN_DIR = HERE / "run"


def load_runner() -> Any:
    name = "effectslice_s07_remote_execution_runner"
    spec = importlib.util.spec_from_file_location(name, extended(RUNNER_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen remote execution runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bound_inputs(runner: Any, row: dict[str, Any]) -> Any:
    materialization = extended(MATERIALIZATION)
    task_dir = materialization / "tasks" / row["task_id"]
    request_path = extended(HERE / row["request_file"])
    payload_path = extended(HERE / row["payload_file"])
    candidate_path = extended(HERE / row["candidate_path"])
    return runner.RowInputs(
        task_dir=task_dir,
        request_path=request_path,
        request_bytes=request_path.read_bytes(),
        payload_path=payload_path,
        fixture_path=materialization / row["fixture_path"],
        scorer_path=materialization / row["scorer_path"],
        candidate_path=candidate_path,
        candidate_tokens=int(row["candidate_tokens"]),
    )


def validate_existing(path: Path, row: dict[str, Any]) -> None:
    result = load_json(path)
    if result.get("execution_id") != row["execution_id"]:
        raise RuntimeError(f"execution ID mismatch in {path.name}")
    if result.get("registered_request_sha256") != row["request_sha256"]:
        raise RuntimeError(f"request binding mismatch in {path.name}")
    for field in ("task_id", "registry_id", "arm_id"):
        if result.get(field) != row[field]:
            raise RuntimeError(f"{field} binding mismatch in {path.name}")


def run(docs_dir: Path) -> dict[str, Any]:
    verification = verify_registration()
    runner = load_runner()
    credentials, metadata = runner.load_credentials(docs_dir.resolve())
    token = credentials["deepseek_primary"]
    schedule = load_json(REGISTRATION / "schedule.json")["rows"]
    run_dir = runner.windows_extended_path(RUN_DIR)
    runner.atomic_json(
        run_dir / "run_manifest.json",
        {
            "schema_version": "effectslice-s07-atom-intervention-run.v1",
            "registration_manifest_sha256": sha256_file(
                REGISTRATION / "manifest.json"
            ),
            "registration_verification": verification,
            "credential_metadata": {
                "deepseek_primary": metadata["deepseek_primary"]
            },
            "semantic_replay_policy": (
                "never replay a row with a terminal result"
            ),
            "transport_attempt_limit": runner.MAXIMUM_TRANSPORT_ATTEMPTS,
            "credential_value_recorded": False,
        },
    )

    for row in schedule:
        execution_id = row["execution_id"]
        row_path = run_dir / "rows" / f"{execution_id}.json"
        started_path = (
            run_dir / "dispatch" / f"{execution_id}.started.json"
        )
        terminal_path = (
            run_dir / "dispatch" / f"{execution_id}.terminal.json"
        )
        if row_path.exists():
            validate_existing(row_path, row)
            continue
        if started_path.exists():
            raise RuntimeError(
                f"ambiguous dispatch without terminal row: {execution_id}; "
                "manual audit required"
            )
        runner.atomic_json(
            started_path,
            {
                "schema_version": "effectslice-s07-dispatch-start.v1",
                "execution_id": execution_id,
                "task_id": row["task_id"],
                "registry_id": row["registry_id"],
                "arm_id": row["arm_id"],
                "registered_request_sha256": row["request_sha256"],
                "semantic_rerun_allowed": False,
                "started_at_utc": runner.utc_now(),
            },
        )
        result = runner.execute_row(
            runner.windows_extended_path(MATERIALIZATION),
            run_dir,
            row,
            bound_inputs(runner, row),
            token,
        )
        result = {
            **result,
            "schema_version": "effectslice-s07-atom-intervention-result.v1",
            "task_id": row["task_id"],
            "domain": row["domain"],
            "registry_id": row["registry_id"],
            "arm_id": row["arm_id"],
            "contrast_role": row["contrast_role"],
            "dependency_closed": row["dependency_closed"],
            "registered_request_sha256": row["request_sha256"],
            "registered_payload_sha256": row["payload_sha256"],
            "source_scope": (
                "four-domain singleton atom necessity and rescue intervention"
            ),
        }
        runner.atomic_json(row_path, result)
        runner.atomic_json(
            terminal_path,
            {
                "schema_version": "effectslice-s07-dispatch-terminal.v1",
                "execution_id": execution_id,
                "terminal_outcome": result["terminal_outcome"],
                "result_row_sha256": runner.sha256_file(row_path),
                "completed_at_utc": runner.utc_now(),
            },
        )
        complete = sum(
            (run_dir / "rows" / f"{item['execution_id']}.json").exists()
            for item in schedule
        )
        print(f"terminal_rows={complete}/{len(schedule)}", flush=True)

    rows = [
        load_json(run_dir / "rows" / f"{row['execution_id']}.json")
        for row in schedule
    ]
    outcomes = sorted({row["terminal_outcome"] for row in rows})
    summary = {
        "schema_version": "effectslice-s07-atom-intervention-run-summary.v1",
        "terminal_rows": len(rows),
        "terminal_outcomes": {
            outcome: sum(row["terminal_outcome"] == outcome for row in rows)
            for outcome in outcomes
        },
        "transport_attempts": sum(
            len(row.get("attempts", [])) for row in rows
        ),
        "credential_value_recorded": False,
    }
    runner.atomic_json(run_dir / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.docs_dir), sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
