#!/usr/bin/env python
"""Build the SWE-T1 shared-source-context follow-up table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TASK_ID = "SWE-T1"
FOLLOWUP_RUN_ID = "phase107_gpt_swe_t1_source_context_followup"
CONDITIONS = ("summary", "papertoskill")

TABLE_COLUMNS = [
    "Task ID",
    "Condition",
    "First-pass Run",
    "First-pass Score",
    "First-pass Failure",
    "First-pass Patch Applied",
    "Follow-up Run",
    "Follow-up Score",
    "Follow-up Patch Applied",
    "Follow-up Test Passed",
    "Follow-up Failure",
    "Interpretation",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_row_selection(path: Path) -> dict[tuple[str, str], str]:
    payload = load_json(path)
    selected: dict[tuple[str, str], str] = {}
    for item in payload.get("rows", []):
        task_id = str(item.get("task_id", ""))
        condition = str(item.get("condition", ""))
        run_id = str(item.get("run_id", ""))
        if task_id and condition and run_id:
            selected[(task_id, condition)] = run_id
    return selected


def indexed_rows(raw_rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in raw_rows:
        if row.get("status") != "scored":
            continue
        key = (
            str(row.get("task_id", "")),
            str(row.get("condition", "")),
            str(row.get("run_id", "")),
        )
        rows[key] = row
    return rows


def score_string(row: dict[str, Any]) -> str:
    return f"{float(row['task_score']):.3f}"


def bool_string(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


def condition_label(condition: str) -> str:
    return "PaperToSkill" if condition == "papertoskill" else "Summary"


def metric_for(root: Path, row: dict[str, Any]) -> dict[str, Any]:
    metric_path = Path(str(row.get("metric_path", "")))
    if not metric_path:
        return {}
    if not metric_path.is_absolute():
        metric_path = root / metric_path
    return load_json(metric_path) if metric_path.exists() else {}


def require_row(
    rows_by_key: dict[tuple[str, str, str], dict[str, Any]],
    task_id: str,
    condition: str,
    run_id: str,
) -> dict[str, Any]:
    key = (task_id, condition, run_id)
    if key not in rows_by_key:
        raise ValueError(f"missing scored raw row: {task_id}/{condition}:{run_id}")
    return rows_by_key[key]


def build_rows(
    root: Path,
    raw_rows: list[dict[str, Any]],
    row_selection: dict[tuple[str, str], str],
    followup_run_id: str = FOLLOWUP_RUN_ID,
) -> list[dict[str, str]]:
    rows_by_key = indexed_rows(raw_rows)
    rows: list[dict[str, str]] = []
    for condition in CONDITIONS:
        first_run_id = row_selection.get((TASK_ID, condition))
        if not first_run_id:
            raise ValueError(f"missing main row selection for {TASK_ID}/{condition}")
        first_row = require_row(rows_by_key, TASK_ID, condition, first_run_id)
        followup_row = require_row(rows_by_key, TASK_ID, condition, followup_run_id)
        first_metric = metric_for(root, first_row)
        followup_metric = metric_for(root, followup_row)
        rows.append(
            {
                "Task ID": TASK_ID,
                "Condition": condition_label(condition),
                "First-pass Run": first_run_id,
                "First-pass Score": score_string(first_row),
                "First-pass Failure": str(first_row.get("failure_reason", "")),
                "First-pass Patch Applied": bool_string(first_metric.get("patch_applied")),
                "Follow-up Run": followup_run_id,
                "Follow-up Score": score_string(followup_row),
                "Follow-up Patch Applied": bool_string(followup_metric.get("patch_applied")),
                "Follow-up Test Passed": bool_string(followup_metric.get("test_passed")),
                "Follow-up Failure": str(followup_row.get("failure_reason", "")),
                "Interpretation": "Source context fixed patch application; hidden test still failed",
            }
        )
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [row[column].replace("|", "\\|").replace("\n", " ") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]], raw_row_count: int) -> None:
    lines = [
        "# SWE-T1 Source-Context Follow-Up",
        "",
        "Evidence boundary: this paired follow-up exposes the same locked SQLFluff "
        "source slice to Summary and PaperToSkill. It is diagnostic follow-up "
        "evidence and does not replace the SWE-T1 first-pass main-table row.",
        "",
        f"- Raw scored rows read: {raw_row_count}",
        f"- Follow-up run id: {FOLLOWUP_RUN_ID}",
        "",
        markdown_table(rows, TABLE_COLUMNS),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, rows: list[dict[str, str]], raw_rows: list[dict[str, Any]]) -> None:
    payload = {
        "schema_version": "0.1",
        "evidence_boundary": (
            "SWE-T1 shared-source-context follow-up. This does not replace the "
            "paper-facing first-pass main row."
        ),
        "task_id": TASK_ID,
        "followup_run_id": FOLLOWUP_RUN_ID,
        "raw_row_count": len(raw_rows),
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the SWE-T1 source-context follow-up table.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--raw-rows", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument(
        "--row-selection",
        type=Path,
        default=root / "results" / "real_reuse" / "main_run_selection.json",
    )
    parser.add_argument("--followup-run-id", default=FOLLOWUP_RUN_ID)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_source_context_followup.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_source_context_followup.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_source_context_followup.json",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    raw_rows_path = args.raw_rows if args.raw_rows.is_absolute() else root / args.raw_rows
    row_selection_path = args.row_selection if args.row_selection.is_absolute() else root / args.row_selection
    raw_rows = load_raw_rows(raw_rows_path)
    rows = build_rows(root, raw_rows, load_row_selection(row_selection_path), args.followup_run_id)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, len(raw_rows))
    write_json(args.output_json, rows, raw_rows)
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
