from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import terminal_row_successor_v2 as v2


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "verification"
EXPECTED_ROWS = {
    "Controls-v2": 96,
    "FG6": 1296,
    "FG7": 1296,
    "FG8": 1296,
}
SCHEMA_VERSION = "effectslice-forward-completion-verification.v1"


class CompletionVerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CompletionVerificationError(message)


def registered_rows(experiment: str) -> tuple[list[dict[str, Any]], Path, str]:
    if experiment == "Controls-v2":
        registration = v2.controls.verify_registration(
            v2.controls.DEFAULT_REGISTRATION, require_frozen=True
        )
        rows = v2.v1.load_json(
            v2.controls.DEFAULT_REGISTRATION / "schedule.json"
        )["rows"]
        return (
            rows,
            v2.controls.DEFAULT_RUN,
            str(registration["registration_bundle_sha256"]),
        )

    registration = v2.grid.registration.verify(
        v2.grid.DEFAULT_REGISTRATION, require_frozen=True
    )
    return (
        v2.grid.repeat_schedule(v2.grid.DEFAULT_REGISTRATION, experiment),
        v2.grid.DEFAULT_RUNS / experiment,
        str(registration["registration_bundle_sha256"]),
    )


def directory_ids(path: Path, suffix: str) -> set[str]:
    if not v2.v1.xpath(path).exists():
        return set()
    return {
        item.name.removesuffix(suffix)
        for item in v2.v1.xpath(path).iterdir()
        if item.is_file() and item.name.endswith(suffix)
    }


def verify_experiment(experiment: str, output_dir: Path) -> dict[str, Any]:
    require(experiment in EXPECTED_ROWS, f"unknown experiment: {experiment}")
    freeze = v2.verify_freeze()
    rows, run_dir, registration_sha = registered_rows(experiment)
    expected = EXPECTED_ROWS[experiment]
    execution_ids = [str(row["execution_id"]) for row in rows]
    require(len(rows) == expected, f"registered row count changed: {experiment}")
    require(
        len(set(execution_ids)) == expected,
        f"registered execution IDs are not unique: {experiment}",
    )

    row_ids = directory_ids(run_dir / "rows", ".json")
    metadata_ids = directory_ids(run_dir / "metadata", ".json")
    terminal_ids = directory_ids(run_dir / "dispatch", ".terminal.json")
    expected_ids = set(execution_ids)
    require(row_ids == expected_ids, f"result row set is not exact: {experiment}")
    require(
        metadata_ids == expected_ids,
        f"metadata sidecar set is not exact: {experiment}",
    )
    require(
        terminal_ids == expected_ids,
        f"terminal marker set is not exact: {experiment}",
    )

    terminal_outcomes: Counter[str] = Counter()
    validity: Counter[str] = Counter()
    condition_success: Counter[str] = Counter()
    for row in rows:
        execution_id = str(row["execution_id"])
        value = v2.v1.verify_result_binding(run_dir, row)
        require(
            value["execution_id"] == execution_id,
            f"result execution binding changed: {execution_id}",
        )
        require(
            not v2.v1.retryable_result(value),
            f"retryable transport state became terminal: {execution_id}",
        )
        marker = v2.v1.load_json(
            run_dir / "dispatch" / f"{execution_id}.terminal.json"
        )
        require(
            marker["execution_id"] == execution_id,
            f"terminal marker binding changed: {execution_id}",
        )
        terminal_outcomes[str(value["terminal_outcome"])] += 1
        validity[str(value["row_valid"])] += 1
        condition_success[str(value["condition_success"])] += 1

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": v2.v1.utc_now(),
        "status": "passed",
        "experiment": experiment,
        "expected_rows": expected,
        "registered_rows": len(rows),
        "unique_terminal_result_rows": len(row_ids),
        "unique_metadata_sidecars": len(metadata_ids),
        "unique_terminal_markers": len(terminal_ids),
        "registration_bundle_sha256": registration_sha,
        "terminal_row_successor_v2_freeze_sha256": freeze["freeze_sha256"],
        "terminal_outcomes": dict(sorted(terminal_outcomes.items())),
        "row_valid": dict(sorted(validity.items())),
        "condition_success": dict(sorted(condition_success.items())),
        "network_states_recorded_as_final": False,
        "strict_result_schema_and_metadata_bindings_verified": True,
    }
    if experiment == "Controls-v2":
        analysis_path = v2.controls.DEFAULT_ANALYSIS / "analysis.json"
        require(v2.v1.xpath(analysis_path).exists(), "Controls-v2 analysis missing")
        report["analysis_path"] = str(analysis_path.relative_to(ROOT))
        report["analysis_sha256"] = v2.v1.sha256_file(analysis_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{experiment.lower().replace('-', '_')}.json"
    v2.v1.atomic_json(output, report)
    return report


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", choices=tuple(EXPECTED_ROWS))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    report = verify_experiment(args.experiment, args.output_dir)
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CompletionVerificationError, v2.SuccessorV2Error) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
