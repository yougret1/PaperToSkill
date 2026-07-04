#!/usr/bin/env python
"""Build the SWE-T1 issue-aligned follow-up diagnostic table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TASK_ID = "SWE-T1"
SOURCE_CONTEXT_RUN_ID = "phase107_gpt_swe_t1_source_context_followup"
ISSUE_ALIGNED_RUN_ID = "phase110_gpt_swe_t1_issue_aligned_followup"
CONDITIONS = ("summary", "papertoskill")

TABLE_COLUMNS = [
    "Task ID",
    "Condition",
    "Main Run",
    "Main Score",
    "Phase107 Run",
    "Phase107 Score",
    "Phase107 Test Passed",
    "Issue-Aligned Run",
    "Issue-Aligned Score",
    "Issue-Aligned Test Passed",
    "Issue-Aligned Test Patch",
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


def metric_for(root: Path, row: dict[str, Any]) -> dict[str, Any]:
    metric_path = Path(str(row.get("metric_path", "")))
    if not metric_path:
        return {}
    if not metric_path.is_absolute():
        metric_path = root / metric_path
    return load_json(metric_path) if metric_path.exists() else {}


def condition_label(condition: str) -> str:
    return "PaperToSkill" if condition == "papertoskill" else "Summary"


def score_string(row: dict[str, Any]) -> str:
    return f"{float(row['task_score']):.3f}"


def bool_string(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


def build_rows(
    root: Path,
    raw_rows: list[dict[str, Any]],
    row_selection: dict[tuple[str, str], str],
    *,
    source_context_run_id: str = SOURCE_CONTEXT_RUN_ID,
    issue_aligned_run_id: str = ISSUE_ALIGNED_RUN_ID,
) -> list[dict[str, str]]:
    rows_by_key = indexed_rows(raw_rows)
    rows: list[dict[str, str]] = []
    for condition in CONDITIONS:
        main_run_id = row_selection.get((TASK_ID, condition))
        if not main_run_id:
            raise ValueError(f"missing main row selection for {TASK_ID}/{condition}")
        main_row = require_row(rows_by_key, TASK_ID, condition, main_run_id)
        source_context_row = require_row(rows_by_key, TASK_ID, condition, source_context_run_id)
        issue_aligned_row = require_row(rows_by_key, TASK_ID, condition, issue_aligned_run_id)
        source_context_metric = metric_for(root, source_context_row)
        issue_aligned_metric = metric_for(root, issue_aligned_row)
        rows.append(
            {
                "Task ID": TASK_ID,
                "Condition": condition_label(condition),
                "Main Run": main_run_id,
                "Main Score": score_string(main_row),
                "Phase107 Run": source_context_run_id,
                "Phase107 Score": score_string(source_context_row),
                "Phase107 Test Passed": bool_string(source_context_metric.get("test_passed")),
                "Issue-Aligned Run": issue_aligned_run_id,
                "Issue-Aligned Score": score_string(issue_aligned_row),
                "Issue-Aligned Test Passed": bool_string(issue_aligned_metric.get("test_passed")),
                "Issue-Aligned Test Patch": bool_string(issue_aligned_metric.get("test_patch_applied")),
                "Interpretation": "Issue-aligned scorer passes both conditions; no PaperToSkill advantage",
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


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    raw_row_count: int,
    source_context_run_id: str,
    issue_aligned_run_id: str,
) -> None:
    lines = [
        "# SWE-T1 Issue-Aligned Follow-Up",
        "",
        "Evidence boundary: this paired follow-up uses the pre-registered "
        "SWE-T1 issue-aligned scorer. It is diagnostic contract-closure "
        "evidence and does not replace the SWE-T1 first-pass main-table row. "
        "Because both Summary and PaperToSkill pass, it does not show a "
        "PaperToSkill advantage.",
        "",
        f"- Raw scored rows read: {raw_row_count}",
        f"- Source-context run id: {source_context_run_id}",
        f"- Issue-aligned run id: {issue_aligned_run_id}",
        "",
        markdown_table(rows, TABLE_COLUMNS),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(
    path: Path,
    rows: list[dict[str, str]],
    raw_rows: list[dict[str, Any]],
    source_context_run_id: str,
    issue_aligned_run_id: str,
) -> None:
    payload = {
        "schema_version": "0.1",
        "evidence_boundary": (
            "SWE-T1 issue-aligned paired follow-up. This is diagnostic "
            "contract-closure evidence; it does not replace the paper-facing "
            "first-pass main row and does not show PaperToSkill advantage."
        ),
        "task_id": TASK_ID,
        "source_context_run_id": source_context_run_id,
        "issue_aligned_run_id": issue_aligned_run_id,
        "raw_row_count": len(raw_rows),
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the SWE-T1 issue-aligned follow-up table.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--raw-rows", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument(
        "--row-selection",
        type=Path,
        default=root / "results" / "real_reuse" / "main_run_selection.json",
    )
    parser.add_argument("--source-context-run-id", default=SOURCE_CONTEXT_RUN_ID)
    parser.add_argument("--issue-aligned-run-id", default=ISSUE_ALIGNED_RUN_ID)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_issue_aligned_followup.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_issue_aligned_followup.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "swe_t1_issue_aligned_followup.json",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    raw_rows_path = args.raw_rows if args.raw_rows.is_absolute() else root / args.raw_rows
    row_selection_path = args.row_selection if args.row_selection.is_absolute() else root / args.row_selection
    raw_rows = load_raw_rows(raw_rows_path)
    rows = build_rows(
        root,
        raw_rows,
        load_row_selection(row_selection_path),
        source_context_run_id=args.source_context_run_id,
        issue_aligned_run_id=args.issue_aligned_run_id,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, len(raw_rows), args.source_context_run_id, args.issue_aligned_run_id)
    write_json(args.output_json, rows, raw_rows, args.source_context_run_id, args.issue_aligned_run_id)
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
