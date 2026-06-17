#!/usr/bin/env python
"""Aggregate PaperToSkill evaluation JSON into paper-ready tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PAPER_CONFIGS = [
    {
        "id": "ai_scientist_v2",
        "paper": "AI Scientist-v2",
        "context": "ai_scientist_v2_context_baselines_v0.json",
        "transfer": "ai_scientist_v2_harness_transfer_v0.json",
        "source_spans": "ai_scientist_v2_source_span_validation_v0.json",
        "rubric": "ai_scientist_v2_rubric_v0.json",
        "source_audit_id": "ai_scientist_v2",
    },
    {
        "id": "reflexion",
        "paper": "Reflexion",
        "context": "reflexion_context_baselines_v0.json",
        "transfer": "reflexion_harness_transfer_v0.json",
        "source_spans": "reflexion_source_span_validation_v0.json",
        "rubric": "reflexion_rubric_v0.json",
        "source_audit_id": None,
    },
    {
        "id": "aide",
        "paper": "AIDE",
        "context": "aide_context_baselines_v0.json",
        "transfer": "aide_harness_transfer_v0.json",
        "source_spans": "aide_source_span_validation_v0.json",
        "rubric": "aide_rubric_v0.json",
        "source_audit_id": None,
    },
]

TABLE_FILENAMES = {
    "main_results": ("main_results.md", "main_results.csv"),
    "transfer_ablation": ("transfer_ablation.md", "transfer_ablation.csv"),
    "compactness_source_grounding": (
        "compactness_source_grounding.md",
        "compactness_source_grounding.csv",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def criterion(report: dict[str, Any], criterion_id: str) -> dict[str, Any]:
    for item in report.get("criteria", []):
        if item.get("id") == criterion_id:
            return item
    return {}


def status_count(report: dict[str, Any], status: str) -> int:
    return int(report.get("status_counts", {}).get(status, 0))


def format_decimal(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, str):
        return value
    text = f"{float(value):.{digits}f}"
    return text.rstrip("0").rstrip(".")


def format_score(score: Any, max_score: Any) -> str:
    return f"{format_decimal(score)}/{format_decimal(max_score)}"


def format_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return format_decimal(value, 3)


def escape_markdown(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_markdown(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def context_scores(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return by_id(report["results"])


def transfer_scores(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return by_id(report["results"])


def first_result(report: dict[str, Any]) -> dict[str, Any]:
    results = report.get("results", [])
    if not results:
        raise ValueError("Expected at least one result item")
    return results[0]


def source_audit_rates(results_dir: Path) -> dict[str, dict[str, Any]]:
    path = results_dir / "skill_source_audit_v0.json"
    if not path.exists():
        return {}
    report = load_json(path)
    return by_id(report.get("results", []))


def build_main_results(results_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for config in PAPER_CONFIGS:
        context = context_scores(load_json(results_dir / config["context"]))
        transfer = transfer_scores(load_json(results_dir / config["transfer"]))
        spans = first_result(load_json(results_dir / config["source_spans"]))
        rubric = load_json(results_dir / config["rubric"])

        skill = context["skill"]
        generic = context["generic_summary"]
        abstract = context["abstract_only"]
        full_transfer = transfer["full_skill"]

        rows.append(
            {
                "Paper": config["paper"],
                "Skill rubric": format_score(rubric["score"], rubric["max_score"]),
                "Skill coverage": format_score(skill["score"], skill["max_score"]),
                "Generic summary coverage": format_score(generic["score"], generic["max_score"]),
                "Abstract-only coverage": format_score(abstract["score"], abstract["max_score"]),
                "Skill vs generic delta": format_decimal(skill["score"] - generic["score"]),
                "Skill vs abstract delta": format_decimal(skill["score"] - abstract["score"]),
                "Transfer readiness": format_score(full_transfer["average_normalized_score"], 10),
                "Source support rate": format_rate(spans["support_rate"]),
                "Skill words": skill["word_count"],
            }
        )
    return rows


def build_transfer_ablation(results_dir: Path) -> list[dict[str, Any]]:
    rows = []
    variant_labels = {
        "full_skill": "Full skill",
        "skill_without_transfer_notes": "No transfer notes",
        "generic_summary": "Generic summary",
    }
    for config in PAPER_CONFIGS:
        transfer = load_json(results_dir / config["transfer"])
        for result in transfer["results"]:
            harnesses = by_id(result["harnesses"])
            rows.append(
                {
                    "Paper": config["paper"],
                    "Variant": variant_labels.get(result["id"], result["label"]),
                    "Average readiness": format_score(result["average_normalized_score"], 10),
                    "Codex-style readiness": format_score(harnesses["codex_skill"]["normalized_score"], 10),
                    "Claude-style readiness": format_score(
                        harnesses["claude_project_prompt"]["normalized_score"],
                        10,
                    ),
                    "Word count": result["word_count"],
                    "Dropped sections": ", ".join(result.get("drop_sections", [])) or "none",
                }
            )
    return rows


def build_compactness_source_grounding(results_dir: Path) -> list[dict[str, Any]]:
    rows = []
    audits = source_audit_rates(results_dir)
    for config in PAPER_CONFIGS:
        context = context_scores(load_json(results_dir / config["context"]))
        spans = first_result(load_json(results_dir / config["source_spans"]))
        rubric = load_json(results_dir / config["rubric"])
        compactness = criterion(rubric, "compactness")
        source_anchors = criterion(rubric, "source_anchoring")
        audit_id = config.get("source_audit_id")
        audit = audits.get(audit_id) if audit_id else None

        rows.append(
            {
                "Paper": config["paper"],
                "Skill words": context["skill"]["word_count"],
                "Compactness budget": compactness.get("max_words", "n/a"),
                "Compactness score": format_score(compactness.get("points"), compactness.get("max_points")),
                "Source anchors": source_anchors.get("anchor_count", "n/a"),
                "Supported spans": status_count(spans, "supported"),
                "Weak spans": status_count(spans, "weak"),
                "Unsupported spans": status_count(spans, "unsupported"),
                "Invalid ranges": spans.get("invalid_ranges", "n/a"),
                "Source support rate": format_rate(spans.get("support_rate")),
                "Unsupported instruction rate": format_rate(audit.get("unsupported_rate") if audit else None),
            }
        )
    return rows


def write_markdown_table(path: Path, title: str, rows: list[dict[str, Any]], columns: list[str], note: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"# {title}\n\n{note}\n\n{markdown_table(rows, columns)}"
    path.write_text(body, encoding="utf-8")


def write_summary(path: Path, tables: dict[str, tuple[list[dict[str, Any]], list[str]]]) -> None:
    lines = [
        "# Paper-Ready Result Tables",
        "",
        "Evidence boundary: these tables aggregate existing deterministic/offline evaluation JSON. "
        "They are not live cross-harness agent task results.",
        "",
    ]
    for title, (rows, columns) in tables.items():
        lines.extend([f"## {title}", "", markdown_table(rows, columns).strip(), ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def generate_tables(results_dir: Path, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "Main Results": (
            build_main_results(results_dir),
            [
                "Paper",
                "Skill rubric",
                "Skill coverage",
                "Generic summary coverage",
                "Abstract-only coverage",
                "Skill vs generic delta",
                "Skill vs abstract delta",
                "Transfer readiness",
                "Source support rate",
                "Skill words",
            ],
        ),
        "Transfer Ablation": (
            build_transfer_ablation(results_dir),
            [
                "Paper",
                "Variant",
                "Average readiness",
                "Codex-style readiness",
                "Claude-style readiness",
                "Word count",
                "Dropped sections",
            ],
        ),
        "Compactness And Source Grounding": (
            build_compactness_source_grounding(results_dir),
            [
                "Paper",
                "Skill words",
                "Compactness budget",
                "Compactness score",
                "Source anchors",
                "Supported spans",
                "Weak spans",
                "Unsupported spans",
                "Invalid ranges",
                "Source support rate",
                "Unsupported instruction rate",
            ],
        ),
    }

    notes = {
        "Main Results": "Coverage scores are deterministic task-rubric scores; transfer readiness is an offline artifact-readiness metric.",
        "Transfer Ablation": "The no-transfer-notes variant removes only the `Transfer Notes` section from the generated skill.",
        "Compactness And Source Grounding": "Source-span validation checks line-anchor validity and lexical overlap, not human factuality.",
    }

    written: dict[str, Path] = {}
    for key, (md_name, csv_name) in TABLE_FILENAMES.items():
        title = {
            "main_results": "Main Results",
            "transfer_ablation": "Transfer Ablation",
            "compactness_source_grounding": "Compactness And Source Grounding",
        }[key]
        rows, columns = tables[title]
        md_path = output_dir / md_name
        csv_path = output_dir / csv_name
        write_markdown_table(md_path, title, rows, columns, notes[title])
        write_csv(csv_path, rows, columns)
        written[key + "_md"] = md_path
        written[key + "_csv"] = csv_path

    summary_path = output_dir / "paper_ready_summary.md"
    write_summary(summary_path, tables)
    written["summary_md"] = summary_path
    return written


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Aggregate PaperToSkill result JSON into tables.")
    parser.add_argument("--results-dir", type=Path, default=root / "results" / "evaluations")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "tables")
    args = parser.parse_args()

    written = generate_tables(args.results_dir, args.output_dir)
    for path in written.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
