#!/usr/bin/env python
"""Summarize human-fidelity annotation CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "paper_id",
    "paper",
    "criterion_id",
    "criterion_label",
    "score_0_to_3",
    "evidence_note",
    "reviewer_id",
    "review_date",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required annotation columns: {', '.join(missing)}")
        return list(reader)


def parse_score(value: str, row_number: int) -> int | None:
    value = value.strip()
    if value == "":
        return None
    try:
        score = int(value)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: score_0_to_3 must be an integer 0-3 or blank") from exc
    if score < 0 or score > 3:
        raise ValueError(f"Row {row_number}: score_0_to_3 must be between 0 and 3")
    return score


def format_decimal(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    text = f"{value:.{digits}f}"
    return text.rstrip("0").rstrip(".")


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    total_rows = len(rows)
    scored_rows = 0
    errors: list[str] = []
    by_paper: dict[str, dict[str, Any]] = {}
    by_criterion: dict[str, dict[str, Any]] = {}
    paper_scores: dict[str, list[int]] = defaultdict(list)
    criterion_scores: dict[str, list[int]] = defaultdict(list)
    paper_labels: dict[str, str] = {}
    criterion_labels: dict[str, str] = {}

    for index, row in enumerate(rows, start=2):
        score = parse_score(row["score_0_to_3"], index)
        paper_id = row["paper_id"].strip()
        criterion_id = row["criterion_id"].strip()
        paper_labels[paper_id] = row["paper"].strip()
        criterion_labels[criterion_id] = row["criterion_label"].strip()
        if score is None:
            continue
        scored_rows += 1
        if not row["evidence_note"].strip():
            errors.append(f"Row {index}: scored annotation requires evidence_note")
        if not row["reviewer_id"].strip():
            errors.append(f"Row {index}: scored annotation requires reviewer_id")
        paper_scores[paper_id].append(score)
        criterion_scores[criterion_id].append(score)

    for paper_id, label in paper_labels.items():
        scores = paper_scores.get(paper_id, [])
        by_paper[paper_id] = {
            "paper": label,
            "scored_rows": len(scores),
            "average_score": round(sum(scores) / len(scores), 3) if scores else None,
            "max_score": 3,
            "status": "complete" if len(scores) == 6 else "pending",
        }

    for criterion_id, label in criterion_labels.items():
        scores = criterion_scores.get(criterion_id, [])
        by_criterion[criterion_id] = {
            "criterion": label,
            "scored_rows": len(scores),
            "average_score": round(sum(scores) / len(scores), 3) if scores else None,
            "max_score": 3,
            "status": "complete" if len(scores) == len(paper_labels) else "pending",
        }

    return {
        "schema_version": "0.1",
        "evidence_boundary": "Summarizes human-fidelity annotation rows. Blank score rows are pending, not negative evidence.",
        "total_rows": total_rows,
        "scored_rows": scored_rows,
        "pending_rows": total_rows - scored_rows,
        "annotation_status": "complete" if total_rows > 0 and scored_rows == total_rows else "pending",
        "errors": errors,
        "by_paper": by_paper,
        "by_criterion": by_criterion,
    }


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    paper_rows = []
    for item in summary["by_paper"].values():
        paper_rows.append(
            [
                item["paper"],
                str(item["scored_rows"]),
                format_decimal(item["average_score"]),
                item["status"],
            ]
        )
    criterion_rows = []
    for item in summary["by_criterion"].values():
        criterion_rows.append(
            [
                item["criterion"],
                str(item["scored_rows"]),
                format_decimal(item["average_score"]),
                item["status"],
            ]
        )
    lines = [
        "# Human Fidelity Annotation Summary",
        "",
        "Evidence boundary: blank score rows are pending, not negative evidence. "
        "Do not claim human validation unless `annotation_status` is `complete` and errors are empty.",
        "",
        f"- Annotation status: {summary['annotation_status']}",
        f"- Total rows: {summary['total_rows']}",
        f"- Scored rows: {summary['scored_rows']}",
        f"- Pending rows: {summary['pending_rows']}",
        f"- Errors: {len(summary['errors'])}",
        "",
        "## By Paper",
        "",
        markdown_table(paper_rows, ["Paper", "Scored rows", "Average score", "Status"]),
        "",
        "## By Criterion",
        "",
        markdown_table(criterion_rows, ["Criterion", "Scored rows", "Average score", "Status"]),
        "",
    ]
    if summary["errors"]:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in summary["errors"])
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Summarize PaperToSkill human-fidelity annotations.")
    parser.add_argument(
        "--annotations",
        type=Path,
        default=root / "results" / "human_fidelity_packets" / "annotation_template.csv",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "human_fidelity_packets" / "annotation_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "human_fidelity_packets" / "annotation_summary.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if scored rows have validation errors.")
    args = parser.parse_args()

    summary = summarize(load_rows(args.annotations))
    write_json(args.output_json, summary)
    write_markdown(args.output_md, summary)
    print(args.output_json)
    print(args.output_md)
    if args.strict and summary["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
