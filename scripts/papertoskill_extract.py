#!/usr/bin/env python
"""Deterministic PaperToSkill extraction scaffold.

This script is intentionally simple: it creates a first-pass SKILL.md and source
map from Markdown/plain-text paper notes without requiring an LLM. Later stages
can replace individual heuristics with LLM-assisted extraction while preserving
the same output contract.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    title: str
    body: str
    line: int
    level: int = 1


SECTION_ALIASES = {
    "abstract": ("abstract", "summary"),
    "method": ("method", "methods", "approach", "workflow", "system", "design"),
    "experiment": ("experiment", "experiments", "evaluation", "results"),
    "limitation": ("limitation", "limitations", "risk", "risks", "failure", "conclusion", "future"),
    "related": ("related work", "background", "prior work"),
}


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "paper-derived-skill"


def sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", normalize_space(text))
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip()
    return text


def parse_sections(text: str) -> list[Section]:
    text = strip_frontmatter(text)
    lines = text.splitlines()
    sections: list[Section] = []
    current_title = "Document"
    current_line = 1
    current_body: list[str] = []

    md_heading = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    tex_heading = re.compile(r"^\\(section|subsection|subsubsection)\{(.+?)\}\s*$")
    current_level = 1

    def flush() -> None:
        body = "\n".join(current_body).strip()
        if body:
            sections.append(Section(current_title, body, current_line, current_level))

    for idx, line in enumerate(lines, start=1):
        heading = None
        level = None
        md_match = md_heading.match(line.strip())
        if md_match:
            level = len(md_match.group(1))
            heading = md_match.group(2).strip()
        else:
            tex_match = tex_heading.match(line.strip())
            if tex_match:
                level = {"section": 1, "subsection": 2, "subsubsection": 3}[tex_match.group(1)]
                heading = tex_match.group(2).strip()
        if heading:
            flush()
            current_title = heading
            current_line = idx
            current_level = level or 1
            current_body = []
        else:
            current_body.append(line)
    flush()
    return sections or [Section("Document", text.strip(), 1)]


def find_sections(sections: list[Section], group: str) -> list[Section]:
    aliases = SECTION_ALIASES[group]
    found = []
    for section in sections:
        title = section.title.lower()
        if any(alias in title for alias in aliases):
            found.append(section)
    return found


def first_nonempty(*values: str) -> str:
    for value in values:
        value = value.strip()
        if value:
            return value
    return ""


def infer_title(sections: list[Section], source: Path, explicit_title: str | None) -> str:
    if explicit_title:
        return explicit_title
    for section in sections:
        if section.level == 1 and section.title.lower() not in {"document", "abstract"}:
            return section.title
    for section in sections:
        if section.title.lower() not in {"document", "abstract"}:
            return section.title
    return source.stem.replace("_", " ").replace("-", " ").title()


def infer_document_title(text: str) -> str | None:
    for line in strip_frontmatter(text).splitlines():
        stripped = line.strip()
        md_match = re.match(r"^#\s+(.+?)\s*$", stripped)
        if md_match:
            return md_match.group(1).strip()
        tex_match = re.match(r"^\\title\{(.+?)\}\s*$", stripped)
        if tex_match:
            return tex_match.group(1).strip()
    return None


def infer_abstract(sections: list[Section]) -> str:
    abstract_sections = find_sections(sections, "abstract")
    if abstract_sections:
        return normalize_space(abstract_sections[0].body)
    for section in sections:
        sentences = sentence_split(section.body)
        if sentences:
            return " ".join(sentences[:3])
    return ""


def infer_contribution(abstract: str, title: str) -> str:
    for sentence in sentence_split(abstract):
        if re.search(r"\b(we|this paper|this work|we propose|we introduce|we present)\b", sentence, re.I):
            return sentence
    return first_nonempty(sentence_split(abstract)[0] if sentence_split(abstract) else "", title)


def bullet_candidates(text: str, limit: int = 8) -> list[str]:
    candidates: list[str] = []
    current: str | None = None

    def push_current() -> None:
        nonlocal current
        if current is None:
            return
        item = normalize_space(current)
        if len(item) >= 12 and not item.lower().startswith(("figure ", "table ")):
            if item not in candidates:
                candidates.append(item)
        current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            push_current()
            continue
        bullet_match = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if bullet_match:
            push_current()
            current = bullet_match.group(1).strip()
        elif current is not None:
            current = f"{current} {line}"
        else:
            current = line
        if len(candidates) >= limit:
            continue
    push_current()
    candidates = candidates[:limit]
    if candidates:
        return candidates
    sentences = []
    for sentence in sentence_split(text):
        if len(sentence) >= 20 and sentence not in sentences:
            sentences.append(sentence)
        if len(sentences) >= limit:
            break
    return sentences


def infer_workflow(sections: list[Section], contribution: str) -> list[str]:
    method_text = "\n".join(section.body for section in find_sections(sections, "method"))
    candidates = bullet_candidates(method_text, limit=8)
    if candidates:
        return candidates
    return [
        f"Read the source paper and identify the operational method behind: {contribution}",
        "Separate source-backed method steps from inferred implementation details.",
        "Translate each method step into an agent action with required inputs and outputs.",
        "Add validation checks and stop conditions before using the skill on a real task.",
    ]


def infer_validation(sections: list[Section]) -> list[str]:
    experiment_text = "\n".join(section.body for section in find_sections(sections, "experiment"))
    candidates = bullet_candidates(experiment_text, limit=7)
    if candidates:
        return candidates
    return [
        "Check that every workflow step maps to a source section or is marked as an inference.",
        "Run the skill on a small task before claiming it captures the paper's method.",
        "Record task outcome, missing assumptions, and unsupported instructions.",
    ]


def infer_failure_cases(sections: list[Section]) -> list[str]:
    limitation_text = "\n".join(section.body for section in find_sections(sections, "limitation"))
    candidates = bullet_candidates(limitation_text, limit=6)
    if candidates:
        return candidates
    return [
        "Stop if the paper does not provide enough procedural detail to define an agent workflow.",
        "Warn if the generated skill requires tools, data, or environment access not available to the current harness.",
        "Downgrade claims when validation evidence is absent or only indirectly related.",
    ]


def source_map(sections: list[Section]) -> dict:
    return {
        "sections": [
            {
                "title": section.title,
                "line": section.line,
                "level": section.level,
                "characters": len(section.body),
            }
            for section in sections
        ],
        "selected_groups": {
            group: [section.title for section in find_sections(sections, group)]
            for group in SECTION_ALIASES
        },
    }


def md_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def md_numbers(items: list[str]) -> str:
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def build_skill(
    *,
    source_path: Path,
    title: str,
    name: str,
    abstract: str,
    contribution: str,
    workflow: list[str],
    validation: list[str],
    failure_cases: list[str],
) -> str:
    description = (
        f"Use when applying the paper-derived method from {title} as an agent skill. "
        "Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes."
    )
    description = normalize_space(description)
    description = description.replace(":", "")

    abstract_text = textwrap.fill(abstract or contribution, width=88)
    contribution_text = textwrap.fill(contribution, width=88)

    return f"""---
name: {name}
description: {description}
---

# {title}

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `{source_path.as_posix()}`

## Paper Snapshot

{abstract_text}

## Central Contribution

{contribution_text}

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

{md_numbers(workflow)}

## Validation

{md_bullets(validation)}

## Failure Cases

{md_bullets(failure_cases)}

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.
"""


def write_outputs(source: Path, output: Path, name: str | None, title: str | None) -> dict:
    text = source.read_text(encoding="utf-8")
    sections = parse_sections(text)
    inferred_title = infer_title(sections, source, title or infer_document_title(text))
    skill_name = slugify(name or inferred_title)
    abstract = infer_abstract(sections)
    contribution = infer_contribution(abstract, inferred_title)
    workflow = infer_workflow(sections, contribution)
    validation = infer_validation(sections)
    failure_cases = infer_failure_cases(sections)

    output.mkdir(parents=True, exist_ok=True)
    references = output / "references"
    references.mkdir(exist_ok=True)

    skill_text = build_skill(
        source_path=source,
        title=inferred_title,
        name=skill_name,
        abstract=abstract,
        contribution=contribution,
        workflow=workflow,
        validation=validation,
        failure_cases=failure_cases,
    )
    (output / "SKILL.md").write_text(skill_text, encoding="utf-8")

    report = {
        "source": str(source),
        "output": str(output),
        "name": skill_name,
        "title": inferred_title,
        "central_contribution": contribution,
        "workflow_steps": workflow,
        "validation_checks": validation,
        "failure_cases": failure_cases,
        "source_map": source_map(sections),
    }
    (references / "source_map.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic PaperToSkill scaffold.")
    parser.add_argument("--source", required=True, type=Path, help="Markdown or text source file.")
    parser.add_argument("--output", required=True, type=Path, help="Output skill directory.")
    parser.add_argument("--name", help="Optional skill name. Defaults to a slugified title.")
    parser.add_argument("--title", help="Optional skill title. Defaults to the first heading.")
    args = parser.parse_args()

    if not args.source.exists():
        parser.error(f"Source file not found: {args.source}")

    report = write_outputs(args.source, args.output, args.name, args.title)
    print(json.dumps({"skill": str(args.output / "SKILL.md"), "name": report["name"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
