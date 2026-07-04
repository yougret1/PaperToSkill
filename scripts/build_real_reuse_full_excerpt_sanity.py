#!/usr/bin/env python
"""Build the small Full Excerpt sanity-check table for real-reuse tasks."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TABLE_COLUMNS = [
    "Task ID",
    "Source Paper",
    "Metric",
    "Summary Score",
    "PaperToSkill Score",
    "Full Excerpt Score",
    "Summary Tokens",
    "PaperToSkill Tokens",
    "Full Excerpt Tokens",
    "Status",
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


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def paper_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(paper["id"]): paper for paper in spec.get("source_papers", [])}


def task_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(task["id"]): task for task in spec.get("tasks", [])}


def condition_context_path(task_spec: dict[str, Any], condition: str) -> str:
    for item in task_spec.get("conditions", []):
        if item.get("id") == condition:
            return str(item["context_path"])
    raise KeyError(f"missing condition {condition} in {task_spec.get('id')}")


def full_excerpt_path(source_paper_id: str) -> str:
    return f"papers/extracted/{source_paper_id}.txt"


def token_proxy(path: Path) -> int | None:
    if not path.exists():
        return None
    return len(path.read_text(encoding="utf-8").split())


def latest_score_rows(raw_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw_rows:
        if row.get("status") != "scored":
            continue
        key = (str(row.get("task_id", "")), str(row.get("condition", "")))
        latest[key] = row
    return latest


def score_string(row: dict[str, Any] | None) -> str:
    if not row or row.get("status") != "scored" or row.get("task_score") is None:
        return "Pending"
    return f"{float(row['task_score']):.3f}"


def token_string(value: int | None) -> str:
    return "Missing" if value is None else str(value)


def row_status(task_id: str, score_rows: dict[tuple[str, str], dict[str, Any]]) -> str:
    full = score_rows.get((task_id, "full_excerpt"))
    if not full:
        return "Pending full-excerpt run"
    model_family = str(full.get("model_family", "") or "unknown")
    return f"Scored ({model_family})"


def build_rows(root: Path, spec: dict[str, Any], raw_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    papers = paper_by_id(spec)
    tasks = task_by_id(spec)
    score_rows = latest_score_rows(raw_rows)
    rows: list[dict[str, str]] = []
    for task_id in spec.get("full_excerpt_sanity_tasks", []):
        task = tasks[str(task_id)]
        paper = papers[str(task["source_paper_id"])]
        task_spec = load_json(root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json")
        summary_path = resolve(root, condition_context_path(task_spec, "summary"))
        skill_path = resolve(root, condition_context_path(task_spec, "papertoskill"))
        excerpt_path = resolve(root, full_excerpt_path(str(task["source_paper_id"])))
        rows.append(
            {
                "Task ID": str(task_id),
                "Source Paper": str(paper["title"]).split(":")[0],
                "Metric": str(task.get("metric", {}).get("name", "")),
                "Summary Score": score_string(score_rows.get((str(task_id), "summary"))),
                "PaperToSkill Score": score_string(score_rows.get((str(task_id), "papertoskill"))),
                "Full Excerpt Score": score_string(score_rows.get((str(task_id), "full_excerpt"))),
                "Summary Tokens": token_string(token_proxy(summary_path)),
                "PaperToSkill Tokens": token_string(token_proxy(skill_path)),
                "Full Excerpt Tokens": token_string(token_proxy(excerpt_path)),
                "Status": row_status(str(task_id), score_rows),
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
        "# Full Excerpt Sanity Check",
        "",
        "Evidence boundary: this auxiliary table compares the pre-registered "
        "Full Excerpt sanity condition with the same Summary and PaperToSkill "
        "task rows. Token counts are local whitespace context proxies, not "
        "provider bills or output-token costs. Pending Full Excerpt scores are "
        "not negative evidence.",
        "",
        f"- Raw scored rows read: {raw_row_count}",
        "",
        markdown_table(rows, TABLE_COLUMNS),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, rows: list[dict[str, str]], raw_rows: list[dict[str, Any]], root: Path) -> None:
    payload = {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Auxiliary Full Excerpt sanity table. Token counts are local "
            "whitespace context proxies. Pending Full Excerpt score cells are "
            "not downstream task-success evidence."
        ),
        "raw_row_count": len(raw_rows),
        "context_paths": {
            "summary": "baselines/real_reuse/<TASK>_summary.md",
            "papertoskill": "task-specific generated skill context from benchmarks/real_reuse/tasks/<TASK>.json",
            "full_excerpt": "papers/extracted/<source_paper_id>.txt",
        },
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = root_path()
    parser = argparse.ArgumentParser(description="Build the Full Excerpt sanity-check table.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--spec", type=Path, default=root / "benchmarks" / "real_reuse" / "real_reuse_v0.json")
    parser.add_argument("--raw-rows", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "full_excerpt_sanity.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "full_excerpt_sanity.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "full_excerpt_sanity.json",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    spec_path = resolve(root, args.spec)
    raw_rows_path = resolve(root, args.raw_rows)
    raw_rows = load_raw_rows(raw_rows_path)
    rows = build_rows(root, load_json(spec_path), raw_rows)
    write_csv(resolve(root, args.output_csv), rows)
    write_markdown(resolve(root, args.output_md), rows, len(raw_rows))
    write_json(resolve(root, args.output_json), rows, raw_rows, root)
    print(resolve(root, args.output_csv))
    print(resolve(root, args.output_md))
    print(resolve(root, args.output_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
