#!/usr/bin/env python
"""Evaluate offline harness-transfer readiness for PaperToSkill contexts.

This evaluator does not call a live agent. It measures whether a context keeps
the operational signals, source discipline, and transfer instructions needed to
move a paper-derived skill between harness styles.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_project_root(task_path: Path) -> Path:
    resolved = task_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if (candidate / "benchmarks").exists() and (candidate / "scripts").exists():
            return candidate
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


def resolve_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


def normalize(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def parse_h2_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_title: str | None = None
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_body
        if current_title is None:
            return
        sections[current_title.lower()] = "\n".join(current_body).strip()
        current_body = []

    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if match:
            flush()
            current_title = match.group(1).strip()
            current_body = []
        elif current_title is not None:
            current_body.append(line)
    flush()
    return sections


def drop_sections(text: str, section_names: list[str]) -> str:
    if not section_names:
        return text

    drop = {name.lower() for name in section_names}
    out: list[str] = []
    skipping = False
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if match:
            skipping = match.group(1).strip().lower() in drop
        if not skipping:
            out.append(line)
    return "\n".join(out).strip() + "\n"


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lowered = normalize(text).lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def score_required_sections(text: str, harness: dict) -> dict:
    required = harness.get("required_sections", [])
    weight = float(harness.get("section_weight", 2.0))
    sections = parse_h2_sections(text)
    present = [section for section in required if section.lower() in sections]
    points = round(weight * len(present) / len(required), 3) if required else weight
    return {
        "points": points,
        "max_points": weight,
        "present": present,
        "missing": [section for section in required if section not in present],
    }


def score_signal_groups(text: str, signal_groups: list[dict]) -> list[dict]:
    results = []
    for group in signal_groups:
        keywords = group.get("keywords", [])
        max_points = float(group.get("max_points", 1.0))
        hits = keyword_hits(text, keywords)
        points = round(max_points * len(hits) / len(keywords), 3) if keywords else max_points
        results.append(
            {
                "id": group["id"],
                "points": points,
                "max_points": max_points,
                "hits": hits,
                "missing": [keyword for keyword in keywords if keyword not in hits],
            }
        )
    return results


def score_transfer_checks(text: str, harness: dict) -> dict:
    keywords = harness.get("transfer_checks", [])
    weight = float(harness.get("transfer_weight", 2.0))
    hits = keyword_hits(text, keywords)
    points = round(weight * len(hits) / len(keywords), 3) if keywords else weight
    return {
        "points": points,
        "max_points": weight,
        "hits": hits,
        "missing": [keyword for keyword in keywords if keyword not in hits],
    }


def score_source_anchors(text: str, harness: dict) -> dict:
    minimum = int(harness.get("source_anchor_min", 0))
    weight = float(harness.get("source_anchor_weight", 1.0))
    count = len(re.findall(r"source anchors:", text, flags=re.IGNORECASE))
    if minimum <= 0:
        points = weight
    else:
        points = round(weight * min(1.0, count / minimum), 3)
    return {
        "points": points,
        "max_points": weight,
        "anchor_count": count,
        "required_min": minimum,
    }


def score_compactness(text: str, harness: dict) -> dict:
    maximum = int(harness.get("max_words", 0))
    weight = float(harness.get("compactness_weight", 1.0))
    words = word_count(text)
    if maximum <= 0:
        points = weight
    else:
        points = weight if words <= maximum else 0.0
    return {
        "points": points,
        "max_points": weight,
        "word_count": words,
        "max_words": maximum,
    }


def score_harness(text: str, task: dict, harness: dict) -> dict:
    signal_groups = task.get("core_signal_groups", []) + harness.get("signal_groups", [])
    section_result = score_required_sections(text, harness)
    signal_results = score_signal_groups(text, signal_groups)
    transfer_result = score_transfer_checks(text, harness)
    source_anchor_result = score_source_anchors(text, harness)
    compactness_result = score_compactness(text, harness)

    score = (
        section_result["points"]
        + sum(result["points"] for result in signal_results)
        + transfer_result["points"]
        + source_anchor_result["points"]
        + compactness_result["points"]
    )
    max_score = (
        section_result["max_points"]
        + sum(result["max_points"] for result in signal_results)
        + transfer_result["max_points"]
        + source_anchor_result["max_points"]
        + compactness_result["max_points"]
    )
    normalized = round(10 * score / max_score, 3) if max_score else 0.0

    return {
        "id": harness["id"],
        "label": harness.get("label", harness["id"]),
        "score": round(score, 3),
        "max_score": round(max_score, 3),
        "normalized_score": normalized,
        "sections": section_result,
        "signals": signal_results,
        "transfer_checks": transfer_result,
        "source_anchors": source_anchor_result,
        "compactness": compactness_result,
    }


def evaluate(task_path: Path) -> dict:
    task = load_json(task_path)
    root = detect_project_root(task_path)
    results = []

    for variant in task["context_variants"]:
        path = resolve_path(root, variant["path"])
        text = path.read_text(encoding="utf-8")
        text = drop_sections(text, variant.get("drop_sections", []))
        harness_results = [score_harness(text, task, harness) for harness in task["target_harnesses"]]
        average = round(
            sum(result["normalized_score"] for result in harness_results) / len(harness_results),
            3,
        )
        results.append(
            {
                "id": variant["id"],
                "label": variant.get("label", variant["id"]),
                "path": variant["path"],
                "drop_sections": variant.get("drop_sections", []),
                "word_count": word_count(text),
                "average_normalized_score": average,
                "harnesses": harness_results,
            }
        )

    results.sort(key=lambda item: item["average_normalized_score"], reverse=True)
    return {
        "task": task["id"],
        "task_path": str(task_path),
        "evidence_boundary": task.get(
            "evidence_boundary",
            "Offline deterministic readiness metric; not a live cross-harness agent run.",
        ),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate PaperToSkill harness-transfer readiness.")
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
