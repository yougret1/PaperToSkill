#!/usr/bin/env python
"""Build a paper-facing failure-boundary table from real-reuse raw rows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TABLE_COLUMNS = [
    "Task ID",
    "Summary Outcome",
    "PaperToSkill Outcome",
    "Boundary Mode",
    "Contract Implication",
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


def latest_score_rows(raw_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw_rows:
        if row.get("status") != "scored":
            continue
        key = (str(row.get("task_id", "")), str(row.get("condition", "")))
        latest[key] = row
    return latest


def score_string(row: dict[str, Any] | None) -> str:
    if not row or row.get("task_score") is None:
        return "Pending"
    return f"{float(row['task_score']):.3f}"


def reason_label(reason: str) -> str:
    text = reason.strip()
    lower = text.lower()
    if not text:
        return "success"
    if "timeout" in lower:
        return "timeout"
    if "patch_apply_failed" in lower or "patch apply" in lower:
        return "patch apply failed"
    if "missing_required_artifacts_or_metrics" in lower:
        return "artifact incomplete"
    if "extra data" in lower:
        return "artifact parse failed"
    return text.replace("_", " ")


def outcome(row: dict[str, Any] | None) -> str:
    if not row:
        return "Pending"
    status = "success" if row.get("success") is True else reason_label(str(row.get("failure_reason", "")))
    return f"{score_string(row)}; {status}"


def task_boundary(summary: dict[str, Any] | None, papertoskill: dict[str, Any] | None) -> tuple[str, str]:
    if not summary or not papertoskill:
        return ("Incomplete row", "rerun until both conditions are scored")

    summary_success = summary.get("success") is True
    pts_success = papertoskill.get("success") is True
    reasons = " ".join(
        str(row.get("failure_reason", "")).lower()
        for row in (summary, papertoskill)
        if row and row.get("failure_reason")
    )

    if summary_success and pts_success:
        return ("Solved by both", "harder task slice or stricter scorer")
    if not summary_success and pts_success:
        return ("PaperToSkill-only success", "preserve patch/tool-use constraints")
    if summary_success and not pts_success:
        return ("PaperToSkill regression", "inspect skill guidance against summary")
    if "timeout" in reasons:
        return ("Budget timeout", "runtime budget and fallback contract")
    if "patch_apply_failed" in reasons or "patch apply" in reasons:
        return ("Patch application", "patch-format and apply-check contract")
    if "missing_required_artifacts_or_metrics" in reasons or "extra data" in reasons:
        return ("Artifact completion", "required artifact and metric manifest")
    return ("Scored failure", "task-specific recovery contract")


def build_rows(spec: dict[str, Any], raw_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    scores = latest_score_rows(raw_rows)
    rows: list[dict[str, str]] = []
    for task in spec.get("tasks", []):
        task_id = str(task["id"])
        summary = scores.get((task_id, "summary"))
        papertoskill = scores.get((task_id, "papertoskill"))
        mode, contract = task_boundary(summary, papertoskill)
        rows.append(
            {
                "Task ID": task_id,
                "Summary Outcome": outcome(summary),
                "PaperToSkill Outcome": outcome(papertoskill),
                "Boundary Mode": mode,
                "Contract Implication": contract,
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
        "# Real-Reuse Failure-Boundary Analysis",
        "",
        "Evidence boundary: this table is derived from scored raw rows and "
        "summarizes first-pass boundary modes. It does not add new task "
        "success evidence or support aggregate downstream effectiveness.",
        "",
        f"- Raw scored rows read: {raw_row_count}",
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
            "Paper-facing real-reuse failure-boundary analysis derived from "
            "raw_rows.jsonl. It does not add new task-success evidence."
        ),
        "raw_row_count": len(raw_rows),
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build real-reuse failure-boundary analysis tables.")
    parser.add_argument("--spec", type=Path, default=root / "benchmarks" / "real_reuse" / "real_reuse_v0.json")
    parser.add_argument("--raw-rows", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "failure_analysis.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "failure_analysis.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "failure_analysis.json",
    )
    args = parser.parse_args()

    raw_rows = load_raw_rows(args.raw_rows)
    rows = build_rows(load_json(args.spec), raw_rows)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, len(raw_rows))
    write_json(args.output_json, rows, raw_rows)
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
