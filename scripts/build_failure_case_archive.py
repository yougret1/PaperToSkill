#!/usr/bin/env python
"""Build a failure-case archive from PaperToSkill source maps and project records."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_failure(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["cost", "usd", "expensive"]):
        return "cost"
    if any(token in lowered for token in ["ethical", "irb", "disclosure", "withdraw"]):
        return "ethics"
    if any(token in lowered for token in ["contamination", "overlap", "holdout", "private test"]):
        return "evaluation_validity"
    if any(token in lowered for token in ["local optima", "greedy", "stuck"]):
        return "search_failure"
    if any(token in lowered for token in ["citation", "methodological", "rigor", "justify", "novel"]):
        return "quality_limit"
    if any(token in lowered for token in ["top-tier", "workshop", "accepted", "not accepted"]):
        return "quality_threshold"
    if any(token in lowered for token in ["memory", "sliding window"]):
        return "memory_limit"
    return "paper_limitation"


def source_anchor(text: str) -> str:
    match = re.search(r"Source anchors?:\s*(.+?)(?:\.?$)", text)
    return match.group(1).strip() if match else "n/a"


def clean_summary(text: str) -> str:
    return re.sub(r"\s*Source anchors?:\s*.+?\.?$", "", text).strip()


def paper_failure_rows(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in config["paper_sources"]:
        data = load_json(root / source["source_map_path"])
        for index, failure in enumerate(data.get("failure_cases", []), start=1):
            rows.append(
                {
                    "id": f"{source['paper_id']}_paper_failure_{index}",
                    "scope": "paper",
                    "paper": source["paper"],
                    "phase": "source paper",
                    "category": classify_failure(failure),
                    "summary": clean_summary(failure),
                    "impact": "Defines a limitation or failure branch that generated skills should preserve.",
                    "resolution": "Preserve in generated skill failure cases and source maps; do not convert into a success claim.",
                    "evidence": source["source_map_path"],
                    "source_anchor": source_anchor(failure),
                }
            )
    return rows


def project_failure_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in config["project_failures"]:
        rows.append(
            {
                "id": item["id"],
                "scope": "project",
                "paper": "PaperToSkill",
                "phase": item["phase"],
                "category": item["category"],
                "summary": item["summary"],
                "impact": item["impact"],
                "resolution": item["resolution"],
                "evidence": item["evidence"],
                "source_anchor": "n/a",
            }
        )
    return rows


def archive_rows(root: Path, config_path: Path) -> list[dict[str, Any]]:
    config = load_json(config_path)
    return paper_failure_rows(root, config) + project_failure_rows(config)


def counts_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|").replace("\n", " ") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    columns = ["id", "scope", "paper", "phase", "category", "summary", "resolution", "evidence"]
    lines = [
        "# Failure Case Archive",
        "",
        "Evidence boundary: this archive aggregates paper-reported limitations and project-level failure/fix records. It is not a live reproduction failure study.",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Paper-reported cases: {summary['scope_counts'].get('paper', 0)}",
        f"- Project-level cases: {summary['scope_counts'].get('project', 0)}",
        "",
        "## Category Counts",
        "",
    ]
    for category, count in summary["category_counts"].items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Cases", "", markdown_table(rows, columns), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_archive(root: Path, config_path: Path, output_dir: Path) -> dict[str, Path]:
    rows = archive_rows(root, config_path)
    summary = {
        "schema_version": "0.1",
        "evidence_boundary": "Aggregates paper-reported limitations and project-level failure/fix records. Not a live reproduction failure study.",
        "total_cases": len(rows),
        "scope_counts": counts_by(rows, "scope"),
        "category_counts": counts_by(rows, "category"),
        "cases": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "failure_case_archive.json"
    md_path = output_dir / "failure_case_archive.md"
    csv_path = output_dir / "failure_case_archive.csv"
    columns = ["id", "scope", "paper", "phase", "category", "summary", "impact", "resolution", "evidence", "source_anchor"]
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, rows, columns)
    write_markdown(md_path, rows, summary)
    return {"json": json_path, "md": md_path, "csv": csv_path}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the PaperToSkill failure-case archive.")
    parser.add_argument("--config", type=Path, default=root / "benchmarks" / "failure_case_archive_v0.json")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "failure_cases")
    args = parser.parse_args()
    written = build_archive(root, args.config, args.output_dir)
    for path in written.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
