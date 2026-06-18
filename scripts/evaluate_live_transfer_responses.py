#!/usr/bin/env python
"""Score saved PaperToSkill live-transfer response files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


GENERIC_CRITERIA = [
    {
        "id": "source_vs_inferred",
        "keywords": ["source-backed", "inferred", "adaptation"],
    },
    {
        "id": "validation_or_stop",
        "keywords": ["validation", "check", "stop"],
    },
    {
        "id": "failure_branch",
        "keywords": ["failure", "failed branch", "limitation", "unavailable"],
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def contract_keywords(contract_item: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", contract_item.lower())
    stop = {
        "with",
        "from",
        "that",
        "this",
        "into",
        "covering",
        "explaining",
        "copied",
        "adapted",
    }
    return [word for word in words if word not in stop][:5]


def score_keywords(text: str, keywords: list[str]) -> tuple[bool, list[str]]:
    hits = [keyword for keyword in keywords if keyword in text]
    return bool(hits), hits


def score_response(text: str, output_contract: list[str]) -> dict[str, Any]:
    lowered = normalize(text)
    criteria = []
    score = 0
    max_score = 0
    for index, contract_item in enumerate(output_contract, start=1):
        keywords = contract_keywords(contract_item)
        passed, hits = score_keywords(lowered, keywords)
        max_score += 1
        score += 1 if passed else 0
        criteria.append(
            {
                "id": f"contract_{index}",
                "description": contract_item,
                "passed": passed,
                "keywords": keywords,
                "hits": hits,
            }
        )
    for criterion in GENERIC_CRITERIA:
        passed, hits = score_keywords(lowered, criterion["keywords"])
        max_score += 1
        score += 1 if passed else 0
        criteria.append(
            {
                "id": criterion["id"],
                "description": criterion["id"].replace("_", " "),
                "passed": passed,
                "keywords": criterion["keywords"],
                "hits": hits,
            }
        )
    return {
        "score": score,
        "max_score": max_score,
        "normalized_score": round(score / max_score, 3) if max_score else 0.0,
        "word_count": len(re.findall(r"\b\w+\b", text)),
        "criteria": criteria,
    }


def task_contract(root: Path, index: dict[str, Any], index_path: Path) -> list[str]:
    task_path = resolve(root, index.get("task_path", ""))
    if not task_path.exists():
        task_path = resolve(root, index_path.parent / index.get("task_path", ""))
    task = load_json(task_path)
    return [str(item) for item in task.get("output_contract", [])]


def evaluate(root: Path, index_paths: list[Path]) -> dict[str, Any]:
    rows = []
    for raw_index in index_paths:
        index_path = resolve(root, raw_index)
        index = load_json(index_path)
        output_contract = task_contract(root, index, index_path)
        for prompt in index.get("prompts", []):
            response_path = resolve(root, prompt.get("expected_response_path", ""))
            if response_path.exists():
                text = response_path.read_text(encoding="utf-8", errors="ignore")
                result = score_response(text, output_contract)
                status = "scored"
            else:
                result = {
                    "score": 0,
                    "max_score": len(output_contract) + len(GENERIC_CRITERIA),
                    "normalized_score": 0.0,
                    "word_count": 0,
                    "criteria": [],
                }
                status = "pending"
            rows.append(
                {
                    "task": index.get("task", ""),
                    "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                    "harness_id": prompt.get("harness_id", ""),
                    "variant_id": prompt.get("variant_id", ""),
                    "status": status,
                    "response_path": prompt.get("expected_response_path", ""),
                    **result,
                }
            )
    scored = [row for row in rows if row["status"] == "scored"]
    pending = [row for row in rows if row["status"] == "pending"]
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Scores saved live-transfer response files only. Pending rows are not negative evidence "
            "and do not count as completed live cross-harness runs."
        ),
        "summary": {
            "total_rows": len(rows),
            "scored_rows": len(scored),
            "pending_rows": len(pending),
            "average_normalized_score": round(sum(row["normalized_score"] for row in scored) / len(scored), 3) if scored else None,
        },
        "results": rows,
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Harness | Variant | Status | Score | Normalized |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        score = f"{row['score']}/{row['max_score']}" if row["status"] == "scored" else "pending"
        normalized = str(row["normalized_score"]) if row["status"] == "scored" else "pending"
        values = [
            row["task"],
            row["harness_id"],
            row["variant_id"],
            row["status"],
            score,
            normalized,
        ]
        lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Live Transfer Response Evaluation",
        "",
        "Evidence boundary: this scores saved live-transfer response files only; "
        "pending rows are not completed live cross-harness runs.",
        "",
        f"- Total rows: {summary['total_rows']}",
        f"- Scored rows: {summary['scored_rows']}",
        f"- Pending rows: {summary['pending_rows']}",
        f"- Average normalized score: {summary['average_normalized_score']}",
        "",
        markdown_table(report["results"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Evaluate saved live-transfer responses.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--index", action="append", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    args = parser.parse_args()

    report = evaluate(args.root.resolve(), args.index)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
