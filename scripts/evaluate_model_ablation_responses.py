#!/usr/bin/env python
"""Score saved PaperToSkill model-ablation responses."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CRITERIA = [
    {
        "id": "sufficiency_judgment",
        "keywords": ["sufficient", "insufficient", "enough"],
    },
    {
        "id": "required_artifacts",
        "keywords": ["file", "command", "tool"],
    },
    {
        "id": "step_by_step_plan",
        "keywords": ["step", "plan"],
    },
    {
        "id": "source_vs_inferred",
        "keywords": ["source-backed", "inferred"],
    },
    {
        "id": "validation_and_stop",
        "keywords": ["validation", "check", "stop"],
    },
    {
        "id": "failure_branch",
        "keywords": ["failure", "failed branch", "log"],
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def score_response(text: str) -> dict[str, Any]:
    lowered = normalize(text)
    criteria = []
    score = 0
    for criterion in CRITERIA:
        hits = [keyword for keyword in criterion["keywords"] if keyword in lowered]
        passed = bool(hits)
        score += 1 if passed else 0
        criteria.append(
            {
                "id": criterion["id"],
                "passed": passed,
                "hits": hits,
                "missing": [keyword for keyword in criterion["keywords"] if keyword not in hits],
            }
        )
    return {
        "score": score,
        "max_score": len(CRITERIA),
        "normalized_score": round(score / len(CRITERIA), 3),
        "word_count": len(re.findall(r"\b\w+\b", text)),
        "criteria": criteria,
    }


def evaluate(index_path: Path) -> dict[str, Any]:
    index = load_json(index_path)
    rows = []
    for prompt in index["prompts"]:
        response_path = Path(prompt["expected_response_path"])
        if response_path.exists():
            text = response_path.read_text(encoding="utf-8")
            result = score_response(text)
            status = "scored"
        else:
            result = {
                "score": 0,
                "max_score": len(CRITERIA),
                "normalized_score": 0.0,
                "word_count": 0,
                "criteria": [],
            }
            status = "pending"
        rows.append(
            {
                "model_id": prompt["model_id"],
                "model_alias": prompt["model_alias"],
                "case_id": prompt["case_id"],
                "status": status,
                "response_path": prompt["expected_response_path"],
                **result,
            }
        )

    scored = [row for row in rows if row["status"] == "scored"]
    pending = [row for row in rows if row["status"] == "pending"]
    return {
        "schema_version": "0.1",
        "task": index["task"],
        "index_path": str(index_path),
        "evidence_boundary": (
            "Scores saved response files only. Pending rows are not negative evidence "
            "and do not count as completed model ablations."
        ),
        "summary": {
            "total_rows": len(rows),
            "scored_rows": len(scored),
            "pending_rows": len(pending),
            "average_normalized_score": round(
                sum(row["normalized_score"] for row in scored) / len(scored),
                3,
            )
            if scored
            else None,
        },
        "results": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    summary = report["summary"]
    rows = []
    for item in report["results"]:
        score = f"{item['score']}/{item['max_score']}" if item["status"] == "scored" else "pending"
        normalized = str(item["normalized_score"]) if item["status"] == "scored" else "pending"
        rows.append(
            "| "
            + " | ".join(
                [
                    item["model_id"],
                    item["case_id"],
                    item["status"],
                    score,
                    normalized,
                ]
            )
            + " |"
        )
    lines = [
        "# Model Ablation Response Evaluation",
        "",
        "Evidence boundary: this scores saved response files only; pending rows are not completed ablations.",
        "",
        f"- Total rows: {summary['total_rows']}",
        f"- Scored rows: {summary['scored_rows']}",
        f"- Pending rows: {summary['pending_rows']}",
        f"- Average normalized score: {summary['average_normalized_score']}",
        "",
        "| Model | Case | Status | Score | Normalized |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate saved model-ablation responses.")
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    args = parser.parse_args()

    report = evaluate(args.index)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
