#!/usr/bin/env python
"""Validate generated skill source anchors against extracted source text lines."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "its",
    "not",
    "of",
    "on",
    "or",
    "the",
    "their",
    "this",
    "to",
    "with",
}


@dataclass
class Section:
    title: str
    body: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_project_root(task_path: Path) -> Path:
    resolved = task_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if (candidate / "benchmarks").exists() and (candidate / "scripts").exists():
            return candidate
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


def tokenize(text: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]+", text.lower()):
        if token not in STOPWORDS and len(token) > 2:
            tokens.add(token)
    return tokens


def parse_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    current_title: str | None = None
    current_body: list[str] = []

    def flush() -> None:
        if current_title is None:
            return
        body = "\n".join(current_body).strip()
        if body:
            sections.append(Section(current_title, body))

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


def split_bullets(section_body: str) -> list[str]:
    bullets: list[str] = []
    current: str | None = None

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        item = normalize(current)
        if item:
            bullets.append(item)
        current = None

    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        match = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if match:
            flush()
            current = match.group(1).strip()
        elif current is not None:
            current = f"{current} {line}"
    flush()
    return bullets


def anchored_claims(skill_text: str, section_names: list[str]) -> list[dict]:
    wanted = {name.lower() for name in section_names}
    claims = []
    for section in parse_sections(skill_text):
        if section.title.lower() not in wanted:
            continue
        for bullet in split_bullets(section.body):
            if "source anchors:" in bullet.lower():
                claims.append({"section": section.title, "claim": bullet})
    return claims


def extract_ranges(claim: str) -> list[tuple[int, int]]:
    anchor_match = re.search(r"source anchors:\s*(.+)$", claim, flags=re.IGNORECASE)
    if not anchor_match:
        return []
    ranges = []
    for start_text, end_text in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", anchor_match.group(1)):
        start = int(start_text)
        end = int(end_text) if end_text else start
        if end < start:
            start, end = end, start
        ranges.append((start, end))
    return ranges


def span_text(source_lines: list[str], ranges: list[tuple[int, int]]) -> tuple[str, list[dict]]:
    pieces = []
    range_results = []
    max_line = len(source_lines)
    for start, end in ranges:
        valid = 1 <= start <= end <= max_line
        text = "\n".join(source_lines[start - 1 : end]) if valid else ""
        pieces.append(text)
        range_results.append({"start": start, "end": end, "valid": valid})
    return "\n".join(pieces), range_results


def score_claim(claim: str, source_lines: list[str], min_overlap: float) -> dict:
    ranges = extract_ranges(claim)
    source_span, range_results = span_text(source_lines, ranges)
    cleaned = normalize(re.sub(r"Source anchors:.*$", "", claim, flags=re.IGNORECASE).strip(" -"))
    claim_tokens = tokenize(cleaned)
    source_tokens = tokenize(source_span)
    overlap = sorted(claim_tokens & source_tokens)

    if not ranges or not source_span:
        score = 0.0
    else:
        denom = max(4, min(len(claim_tokens), 12))
        score = round(min(1.0, len(overlap) / denom), 3)

    if not ranges:
        status = "missing_anchor"
    elif not all(item["valid"] for item in range_results):
        status = "invalid_range"
    elif score >= min_overlap:
        status = "supported"
    elif score > 0:
        status = "weak"
    else:
        status = "unsupported"

    return {
        "claim": claim,
        "status": status,
        "score": score,
        "ranges": range_results,
        "overlap": overlap,
        "claim_token_count": len(claim_tokens),
        "source_token_count": len(source_tokens),
    }


def validate_item(root: Path, task: dict, item: dict) -> dict:
    skill_path = resolve_path(root, item["skill_path"])
    source_text_path = resolve_path(root, item["source_text"])
    skill_text = skill_path.read_text(encoding="utf-8")
    # `pdftotext` page breaks use form-feed characters. Python's splitlines()
    # treats form feed as a line boundary, but rg, PowerShell, and manual line
    # anchors count only newline-delimited lines.
    source_lines = source_text_path.read_text(encoding="utf-8", errors="replace").split("\n")
    claims = anchored_claims(skill_text, task["sections"])
    min_overlap = float(task.get("min_overlap_score", 0.35))
    claim_results = [score_claim(entry["claim"], source_lines, min_overlap) | {"section": entry["section"]} for entry in claims]

    status_counts: dict[str, int] = {}
    for result in claim_results:
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1

    supported = status_counts.get("supported", 0)
    total = len(claim_results)
    support_rate = round(supported / total, 3) if total else 0.0
    invalid_ranges = sum(
        1
        for result in claim_results
        for range_result in result["ranges"]
        if not range_result["valid"]
    )

    return {
        "id": item["id"],
        "skill_path": str(skill_path),
        "source_text": str(source_text_path),
        "total_claims": total,
        "status_counts": status_counts,
        "support_rate": support_rate,
        "invalid_ranges": invalid_ranges,
        "claims": claim_results,
    }


def evaluate(task_path: Path) -> dict:
    task = load_json(task_path)
    root = detect_project_root(task_path)
    results = [validate_item(root, task, item) for item in task["items"]]
    return {
        "task": task["id"],
        "task_path": str(task_path),
        "evidence_boundary": task.get(
            "evidence_boundary",
            "Source-span validation checks line anchors and lexical overlap; it is not human annotation.",
        ),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill source anchors against extracted source text.")
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
