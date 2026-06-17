#!/usr/bin/env python
"""Audit generated PaperToSkill skills against their source notes.

The audit is source-map-aware: it reads each skill's `references/source_map.json`,
loads the linked source note, and scores actionable bullets using section-aware
token overlap plus explicit source-anchor presence.
"""

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
    "before",
    "by",
    "can",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "the",
    "their",
    "this",
    "to",
    "with",
    "within",
    "when",
    "while",
    "using",
    "use",
    "used",
    "via",
}

SECTION_MAP = {
    "workflow": ["method"],
    "validation": ["experiment"],
    "failure cases": ["limitation"],
    "transfer notes": ["transfer notes", "method", "limitation"],
}

ACTIONABLE_SECTIONS = set(SECTION_MAP)


@dataclass
class Section:
    title: str
    body: str


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
    lines = text.splitlines()
    sections: list[Section] = []
    current_title = "Document"
    current_body: list[str] = []

    def flush() -> None:
        body = "\n".join(current_body).strip()
        if body:
            sections.append(Section(current_title, body))

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if match:
            flush()
            current_title = match.group(2).strip()
            current_body = []
        else:
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def source_sections_from_map(source_map: dict, source_text: str) -> dict[str, str]:
    sections = parse_sections(source_text)
    section_lookup = {section.title.lower(): section.body for section in sections}
    selected = source_map.get("selected_groups", {})
    out = {}
    for group, titles in selected.items():
        bodies = [section_lookup.get(title.lower(), "") for title in titles]
        out[group] = "\n\n".join(body for body in bodies if body)
    return out


def source_body_for_category(source_sections: dict[str, str], category: str) -> str:
    groups = SECTION_MAP.get(category, [category])
    return "\n\n".join(source_sections.get(group, "") for group in groups).strip()


def score_bullet(bullet: str, source_text: str, source_sections: dict[str, str], category: str) -> dict:
    raw = bullet
    anchor_present = "source anchors:" in raw.lower()
    cleaned = normalize(re.sub(r"Source anchors:.*$", "", raw, flags=re.IGNORECASE).strip(" -"))
    bullet_tokens = tokenize(cleaned)
    source_body = source_body_for_category(source_sections, category)
    source_tokens = tokenize(source_body)

    overlap = sorted(bullet_tokens & source_tokens)
    if not source_body:
        content_score = 0.0
    else:
        denom = max(4, min(len(bullet_tokens), 12))
        content_score = min(1.0, len(overlap) / denom)

    anchor_score = 1.0 if anchor_present else 0.0
    score = round(0.4 * anchor_score + 0.6 * content_score, 3)
    if score >= 0.7:
        status = "supported"
    elif score >= 0.35:
        status = "weak"
    else:
        status = "unsupported"

    if not source_body:
        status = "unsupported"
        score = 0.0

    return {
        "bullet": raw,
        "status": status,
        "score": score,
        "anchor_present": anchor_present,
        "overlap": overlap,
        "bullet_tokens": sorted(bullet_tokens),
        "source_token_count": len(source_tokens),
    }


def audit_skill(skill_dir: Path) -> dict:
    skill_path = skill_dir / "SKILL.md"
    source_map_path = skill_dir / "references" / "source_map.json"
    skill_text = load_markdown(skill_path)
    source_map = load_json(source_map_path)
    source_path = Path(source_map["source"])
    source_text = load_markdown(source_path)
    source_sections = source_sections_from_map(source_map["source_map"], source_text)

    skill_sections = parse_sections(skill_text)
    section_results = []
    total = 0
    supported = 0
    weak = 0
    unsupported = 0

    for section in skill_sections:
        title = section.title.strip().lower()
        if title not in ACTIONABLE_SECTIONS:
            continue
        bullets = split_bullets(section.body)
        section_key = title
        section_source = source_body_for_category(source_sections, section_key)
        bullet_results = []
        for bullet in bullets:
            if not bullet:
                continue
            total += 1
            result = score_bullet(bullet, source_text, source_sections, section_key)
            bullet_results.append(result)
            if result["status"] == "supported":
                supported += 1
            elif result["status"] == "weak":
                weak += 1
            else:
                unsupported += 1

        section_results.append(
            {
                "section": section.title,
                "source_section_present": bool(section_source),
                "bullets": bullet_results,
            }
        )

    unsupported_rate = round(unsupported / total, 3) if total else 0.0
    return {
        "skill_dir": str(skill_dir),
        "skill_path": str(skill_path),
        "source_note": str(source_path),
        "total_bullets": total,
        "supported": supported,
        "weak": weak,
        "unsupported": unsupported,
        "unsupported_rate": unsupported_rate,
        "section_results": section_results,
    }


def evaluate(task_path: Path) -> dict:
    task = load_json(task_path)
    root = task_path.parents[2]
    results = []
    for item in task["skills"]:
        skill_dir = root / item["path"]
        result = audit_skill(skill_dir)
        result["id"] = item["id"]
        results.append(result)
    results.sort(key=lambda x: (x["unsupported_rate"], -x["supported"]))
    return {
        "task": task["id"],
        "task_path": str(task_path),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit generated PaperToSkill skills against their source notes.")
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
