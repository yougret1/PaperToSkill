#!/usr/bin/env python
"""Build prompt packets for live PaperToSkill harness-transfer runs."""

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
    return resolved.parent


def resolve_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


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


def slug(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", text.strip()).strip("_").lower()
    return value or "item"


def render_prompt(task: dict, harness: dict, variant: dict, context_text: str) -> str:
    output_contract = "\n".join(f"- {item}" for item in task["output_contract"])
    evaluation_notes = "\n".join(f"- {item}" for item in task.get("evaluation_notes", []))
    if not evaluation_notes:
        evaluation_notes = "- Use the task rubric in the manifest."

    return f"""# PaperToSkill Live Transfer Prompt

## Harness

- Harness ID: `{harness["id"]}`
- Harness label: {harness.get("label", harness["id"])}

## Harness Instructions

{harness["instructions"].strip()}

## Context Variant

- Variant ID: `{variant["id"]}`
- Variant label: {variant.get("label", variant["id"])}
- Source path: `{variant["path"]}`
- Dropped sections: {", ".join(variant.get("drop_sections", [])) or "none"}

## Task

{task["user_prompt"].strip()}

## Required Output Contract

{output_contract}

## Evaluation Notes

{evaluation_notes}

## Context

{context_text.strip()}
"""


def build_prompts(task_path: Path, output_dir: Path) -> dict:
    task = load_json(task_path)
    root = detect_project_root(task_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = []
    for harness in task["target_harnesses"]:
        for variant in task["context_variants"]:
            context_path = resolve_path(root, variant["path"])
            context_text = context_path.read_text(encoding="utf-8")
            context_text = drop_sections(context_text, variant.get("drop_sections", []))
            prompt_text = render_prompt(task, harness, variant, context_text)
            prompt_name = f"{slug(harness['id'])}__{slug(variant['id'])}.md"
            prompt_path = output_dir / prompt_name
            prompt_path.write_text(prompt_text, encoding="utf-8")
            prompts.append(
                {
                    "harness_id": harness["id"],
                    "variant_id": variant["id"],
                    "prompt_path": str(prompt_path),
                    "context_path": str(context_path),
                    "drop_sections": variant.get("drop_sections", []),
                    "expected_response_path": str(output_dir / "responses" / prompt_name),
                }
            )

    index = {
        "task": task["id"],
        "task_path": str(task_path),
        "evidence_boundary": task.get(
            "evidence_boundary",
            "Prompt packet only; live agent responses must be collected separately.",
        ),
        "prompts": prompts,
    }
    (output_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description="Build live harness-transfer prompt packets.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    index = build_prompts(args.task, args.output_dir)
    print(json.dumps(index, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
