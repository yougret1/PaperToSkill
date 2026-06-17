#!/usr/bin/env python
"""Score PaperToSkill context variants for a downstream task spec."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def score_context(text: str, task: dict) -> dict:
    capability_results = []
    score = 0.0
    for capability in task["required_capabilities"]:
        hits = keyword_hits(text, capability["keywords"])
        points = round(len(hits) / len(capability["keywords"]), 3)
        score += points
        capability_results.append(
            {
                "id": capability["id"],
                "points": points,
                "hits": hits,
                "missing": [k for k in capability["keywords"] if k not in hits],
            }
        )

    max_words = task["compactness"]["max_words"]
    word_count = words(text)
    compactness_points = 1.0 if word_count <= max_words else 0.0
    score += compactness_points

    return {
        "score": round(score, 3),
        "max_score": len(task["required_capabilities"]) + 1,
        "word_count": word_count,
        "compactness_points": compactness_points,
        "capabilities": capability_results,
    }


def evaluate(task_path: Path) -> dict:
    task = read_json(task_path)
    root = task_path.parents[2]
    results = []
    for variant in task["context_variants"]:
        path = root / variant["path"]
        text = path.read_text(encoding="utf-8")
        result = score_context(text, task)
        result.update(
            {
                "id": variant["id"],
                "label": variant["label"],
                "path": variant["path"],
            }
        )
        results.append(result)
    results.sort(key=lambda item: item["score"], reverse=True)
    return {
        "task": task["id"],
        "task_path": str(task_path),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate context baselines for a PaperToSkill downstream task.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = evaluate(args.task)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
