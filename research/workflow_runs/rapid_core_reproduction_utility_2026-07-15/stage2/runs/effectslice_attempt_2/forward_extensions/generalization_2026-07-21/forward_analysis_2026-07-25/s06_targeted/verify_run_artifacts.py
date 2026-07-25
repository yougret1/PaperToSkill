from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from targeted_successor import (
    HERE,
    REGISTRATION,
    extended,
    load_json,
    sha256_file,
    verify_registration,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify(run_dir: Path) -> dict[str, Any]:
    verify_registration()
    schedule = load_json(REGISTRATION / "schedule.json")["rows"]
    outcomes: Counter[str] = Counter()
    attempt_counts: Counter[int] = Counter()
    for registered in schedule:
        execution_id = registered["execution_id"]
        row_path = run_dir / "rows" / f"{execution_id}.json"
        started_path = run_dir / "dispatch" / f"{execution_id}.started.json"
        terminal_path = run_dir / "dispatch" / f"{execution_id}.terminal.json"
        attempt_path = run_dir / "attempts" / f"{execution_id}.json"
        for path in (row_path, started_path, terminal_path, attempt_path):
            require(extended(path).is_file(), f"missing run artifact: {path.name}")

        row = load_json(row_path)
        started = load_json(started_path)
        terminal = load_json(terminal_path)
        attempts = load_json(attempt_path)
        require(row["execution_id"] == execution_id, f"row ID mismatch: {execution_id}")
        require(row["case_id"] == registered["case_id"], f"case mismatch: {execution_id}")
        require(row["replica"] == registered["replica"], f"replica mismatch: {execution_id}")
        require(
            row["registered_request_sha256"] == registered["request_sha256"],
            f"request binding mismatch: {execution_id}",
        )
        require(
            started["registered_request_sha256"] == registered["request_sha256"],
            f"dispatch-start binding mismatch: {execution_id}",
        )
        require(started["semantic_rerun_allowed"] is False, f"semantic replay allowed: {execution_id}")
        require(terminal["execution_id"] == execution_id, f"terminal ID mismatch: {execution_id}")
        require(
            terminal["terminal_outcome"] == row["terminal_outcome"],
            f"terminal outcome mismatch: {execution_id}",
        )
        require(
            terminal["result_row_sha256"] == sha256_file(row_path),
            f"terminal row hash mismatch: {execution_id}",
        )
        require(attempts["credential_value_recorded"] is False, f"credential flag invalid: {execution_id}")
        require(attempts["state"] == "completed_body", f"dispatch did not complete: {execution_id}")
        require(1 <= len(attempts["attempts"]) <= 5, f"invalid attempt count: {execution_id}")
        require(len(row["attempts"]) == len(attempts["attempts"]), f"attempt ledger mismatch: {execution_id}")

        for attempt in attempts["attempts"]:
            attempt_index = int(attempt["attempt_index"])
            body = run_dir / "attempt_bodies" / execution_id / f"attempt_{attempt_index}.bin"
            require(extended(body).is_file(), f"missing attempt body: {execution_id}:{attempt_index}")

        raw_path = run_dir / str(row["raw_response_path"])
        canonical_path = run_dir / str(row["canonical_output_path"])
        require(extended(raw_path).is_file(), f"missing raw response: {execution_id}")
        require(extended(canonical_path).is_file(), f"missing canonical output: {execution_id}")
        require(sha256_file(raw_path) == row["raw_response_sha256"], f"raw hash mismatch: {execution_id}")
        require(
            sha256_file(canonical_path) == row["canonical_output_sha256"],
            f"canonical hash mismatch: {execution_id}",
        )
        scoring = run_dir / "scoring" / f"{execution_id}.json.gz"
        require(extended(scoring).is_file(), f"missing private scoring evidence: {execution_id}")
        require(
            row["terminal_outcome"] in {"operational_success", "hard_contract_failure"},
            f"unexpected terminal outcome: {execution_id}",
        )
        require(
            isinstance(row["hard_contract_vector"], list)
            and len(row["hard_contract_vector"]) == 2
            and all(isinstance(value, bool) for value in row["hard_contract_vector"]),
            f"invalid hard-contract vector: {execution_id}",
        )
        outcomes[row["terminal_outcome"]] += 1
        attempt_counts[len(attempts["attempts"])] += 1

    summary = load_json(run_dir / "summary.json")
    require(summary["terminal_rows"] == len(schedule), "run summary row count mismatch")
    require(summary["operational_success"] == outcomes["operational_success"], "run summary success mismatch")
    require(summary["hard_contract_failure"] == outcomes["hard_contract_failure"], "run summary failure mismatch")
    require(summary["other_terminal_outcomes"] == 0, "run summary contains other outcomes")
    return {
        "status": "PASS",
        "terminal_rows": len(schedule),
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "transport_attempt_counts": {str(key): value for key, value in sorted(attempt_counts.items())},
        "incomplete_dispatches": 0,
        "credential_value_recorded": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=HERE / "run")
    args = parser.parse_args()
    print(json.dumps(verify(args.run_dir), sort_keys=True))


if __name__ == "__main__":
    main()
