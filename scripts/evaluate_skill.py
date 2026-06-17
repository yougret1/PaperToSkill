#!/usr/bin/env python
"""Evaluate a generated PaperToSkill SKILL.md with a deterministic v0 rubric."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def section_present(text: str, section: str) -> bool:
    return re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE) is not None


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def evaluate(skill_path: Path, rubric_path: Path) -> dict:
    text = skill_path.read_text(encoding="utf-8")
    rubric = load_json(rubric_path)
    criteria_results = []
    total = 0

    for criterion in rubric["criteria"]:
        cid = criterion["id"]
        max_points = criterion["max_points"]
        result = {"id": cid, "max_points": max_points}

        if cid == "structure":
            required = criterion["required_sections"]
            present = [section for section in required if section_present(text, section)]
            points = round(max_points * len(present) / len(required), 2)
            result |= {"present": present, "missing": [s for s in required if s not in present]}
        elif cid == "source_anchoring":
            count = text.count(criterion["anchor_pattern"])
            points = min(max_points, count)
            result |= {"anchor_count": count}
        elif cid in {"workflow_coverage", "failure_coverage"}:
            hits = keyword_hits(text, criterion["keywords"])
            points = round(max_points * len(hits) / len(criterion["keywords"]), 2)
            result |= {"hits": hits, "missing": [k for k in criterion["keywords"] if k not in hits]}
        elif cid == "compactness":
            words = word_count(text)
            points = max_points if words <= criterion["max_words"] else 0
            result |= {"words": words, "max_words": criterion["max_words"]}
        else:
            points = 0
            result |= {"error": f"Unknown criterion: {cid}"}

        result["points"] = points
        total += points
        criteria_results.append(result)

    return {
        "skill": str(skill_path),
        "rubric": str(rubric_path),
        "score": round(total, 2),
        "max_score": rubric["max_score"],
        "criteria": criteria_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a generated PaperToSkill skill.")
    parser.add_argument("--skill", required=True, type=Path)
    parser.add_argument("--rubric", default=Path("benchmarks/rubric_v0.json"), type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = evaluate(args.skill, args.rubric)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
