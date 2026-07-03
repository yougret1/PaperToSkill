#!/usr/bin/env python
"""Build paper-facing real-reuse main-result table scaffolds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TABLE_COLUMNS = [
    "Task ID",
    "Source Paper",
    "Domain",
    "Original-style Input",
    "Required Output",
    "Metric",
    "Reference",
    "Summary Score",
    "PaperToSkill Score",
    "Status",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def paper_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(paper["id"]): paper for paper in spec.get("source_papers", [])}


def short_input(task: dict[str, Any]) -> str:
    task_id = str(task["id"])
    by_task = {
        "AIDE-T1": "Kaggle-style dataset + metric",
        "AIDE-T2": "Weak ML script + feedback",
        "SWE-T1": "Repo issue + tests",
        "SWE-T2": "Failing test + repo",
        "REF-T1": "Multi-hop QA + feedback",
        "REF-T2": "Failed attempt + checker feedback",
        "SNAP-T1": "Small single-cell dataset",
        "SNAP-T2": "Single-cell labels/proxy task",
    }
    return by_task.get(task_id, str(task.get("original_style_input", "")))


def short_output(task: dict[str, Any]) -> str:
    task_id = str(task["id"])
    by_task = {
        "AIDE-T1": "Runnable solution/submission",
        "AIDE-T2": "Improved script + trajectory",
        "SWE-T1": "Patch + test log",
        "SWE-T2": "Focused patch + verification",
        "REF-T1": "Final answer + reflection trace",
        "REF-T2": "Corrected second attempt",
        "SNAP-T1": "Pipeline + embedding artifacts",
        "SNAP-T2": "Clustering/marker artifacts",
    }
    return by_task.get(task_id, str(task.get("required_output", "")))


def reference_label(task: dict[str, Any]) -> str:
    label = str(task.get("paper_reference", {}).get("label", "Reported reference"))
    if "AIDE" in label:
        return "Reported AIDE ref."
    if "SWE-agent" in label:
        return "Reported SWE-agent ref."
    if "Reflexion" in label:
        return "Reported Reflexion ref."
    if "SnapATAC2" in label:
        return "Reported SnapATAC2 ref."
    return "Reported paper ref."


def build_rows(spec: dict[str, Any]) -> list[dict[str, str]]:
    papers = paper_by_id(spec)
    rows: list[dict[str, str]] = []
    for task in spec.get("tasks", []):
        paper = papers[str(task["source_paper_id"])]
        rows.append(
            {
                "Task ID": str(task["id"]),
                "Source Paper": str(paper["title"]).split(":")[0],
                "Domain": str(task["domain"]),
                "Original-style Input": short_input(task),
                "Required Output": short_output(task),
                "Metric": str(task.get("metric", {}).get("name", "")),
                "Reference": reference_label(task),
                "Summary Score": "Pending",
                "PaperToSkill Score": "Pending",
                "Status": "Ready to run",
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


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Real-Reuse Main Results Table Scaffold",
        "",
        "Evidence boundary: this table defines the main real-reuse experiment rows "
        "for the paper. Scores are pending execution and must not be cited as "
        "downstream task-success evidence.",
        "",
        markdown_table(rows, TABLE_COLUMNS),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the real-reuse paper table scaffold.")
    parser.add_argument("--spec", type=Path, default=root / "benchmarks" / "real_reuse" / "real_reuse_v0.json")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "main_results_plan.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "main_results_plan.md",
    )
    args = parser.parse_args()

    rows = build_rows(load_json(args.spec))
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(args.output_csv)
    print(args.output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
