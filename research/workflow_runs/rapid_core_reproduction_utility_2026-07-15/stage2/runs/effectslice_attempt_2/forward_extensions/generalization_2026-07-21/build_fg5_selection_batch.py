from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

import remote_execution_runner as runner


FORWARD_ROOT = Path(__file__).resolve().parent
DEVELOPMENT_ROOT = FORWARD_ROOT / "fg5_development_2026-07-24"
DEFAULT_SOURCE = DEVELOPMENT_ROOT / "exact_output_contract_all_rows.json"
DEFAULT_RUN = FORWARD_ROOT / "remote_execution_v5_development_2026-07-24"


class BatchSelectionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BatchSelectionError(message)


def build_batch(
    source_path: Path,
    run_dir: Path,
    *,
    limit: int,
    batch_name: str,
) -> dict[str, Any]:
    require(limit > 0, "batch limit must be positive")
    source_path = runner.windows_extended_path(source_path)
    run_dir = runner.windows_extended_path(run_dir)
    source = runner.load_json(source_path)
    source_rows = {str(row["execution_id"]): row for row in source["rows"]}
    pending = [
        execution_id
        for execution_id in map(str, source["execution_ids"])
        if not (run_dir / "rows" / f"{execution_id}.json").is_file()
    ]
    selected_ids = pending[:limit]
    require(selected_ids, "source selection has no pending rows")
    rows = [source_rows[execution_id] for execution_id in selected_ids]
    return {
        "schema_version": "effectslice-fg5-selection.v1",
        "selection_name": batch_name,
        "source_selection_name": source["selection_name"],
        "source_row_count": source["row_count"],
        "pending_before_batch": len(pending),
        "row_count": len(rows),
        "execution_ids": selected_ids,
        "rows": rows,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build",))
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--batch-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    value = build_batch(
        args.source,
        args.run_dir,
        limit=args.limit,
        batch_name=args.batch_name,
    )
    runner.atomic_json(args.output, value)
    print(
        json.dumps(
            {
                "status": "passed",
                "selection_name": value["selection_name"],
                "row_count": value["row_count"],
                "pending_before_batch": value["pending_before_batch"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BatchSelectionError as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        raise SystemExit(2)
