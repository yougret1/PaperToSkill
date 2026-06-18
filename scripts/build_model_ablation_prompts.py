#!/usr/bin/env python
"""Build model-ablation prompt packets for PaperToSkill live evaluations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_project_root(task_path: Path) -> Path:
    resolved = task_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if (candidate / "benchmarks").exists() and (candidate / "scripts").exists():
            return candidate
    return resolved.parent


def resolve_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def slug(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", text.strip()).strip("_").lower()
    return value or "item"


def render_prompt(task: dict[str, Any], model: dict[str, Any], case: dict[str, Any], context_text: str) -> str:
    output_contract = "\n".join(f"- {item}" for item in task["output_contract"])
    evaluation_notes = "\n".join(f"- {item}" for item in task.get("evaluation_notes", []))
    run_notes = "\n".join(f"- {item}" for item in model.get("run_notes", []))
    if not run_notes:
        run_notes = "- No model-specific run notes."
    aliases = model.get("model_aliases") or [model["model_alias"]]
    alias_notes = "\n".join(f"- `{alias}`" for alias in aliases)

    return f"""# PaperToSkill Model-Ablation Prompt

## Model Slot

- Model ID: `{model["id"]}`
- Requested or advertised alias: `{model["model_alias"]}`
- Alias candidates:
{alias_notes}
- Provider status: {model.get("provider_status", "pending")}
- Response status: {model.get("response_status", "pending")}

## Model-Specific Notes

{run_notes}

## Context Case

- Case ID: `{case["id"]}`
- Paper: {case["paper"]}
- Context path: `{case["context_path"]}`
- Usage focus: {case["usage_focus"]}

## Task

{task["user_prompt"].strip()}

## Required Output Contract

{output_contract}

## Evaluation Notes

{evaluation_notes}

## Context

{context_text.strip()}
"""


def build_prompts(task_path: Path, output_dir: Path) -> dict[str, Any]:
    task = load_json(task_path)
    root = detect_project_root(task_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = []
    for model in task["model_slots"]:
        for case in task["context_cases"]:
            context_path = resolve_path(root, case["context_path"])
            context_text = context_path.read_text(encoding="utf-8")
            prompt_text = render_prompt(task, model, case, context_text)
            prompt_name = f"{slug(model['id'])}__{slug(case['id'])}.md"
            prompt_path = output_dir / prompt_name
            prompt_path.write_text(prompt_text, encoding="utf-8")
            prompts.append(
                {
                    "model_id": model["id"],
                    "model_alias": model["model_alias"],
                    "model_aliases": model.get("model_aliases") or [model["model_alias"]],
                    "provider_status": model.get("provider_status", "pending"),
                    "response_status": model.get("response_status", "pending"),
                    "case_id": case["id"],
                    "prompt_path": str(prompt_path),
                    "context_path": str(context_path),
                    "expected_response_path": str(output_dir / "responses" / prompt_name),
                }
            )

    index = {
        "schema_version": task.get("schema_version", "0.1"),
        "task": task["id"],
        "task_path": str(task_path),
        "evidence_boundary": task.get(
            "evidence_boundary",
            "Prompt packet only; model responses and scoring must be collected separately.",
        ),
        "prompts": prompts,
    }
    (output_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description="Build model-ablation prompt packets.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    index = build_prompts(args.task, args.output_dir)
    print(json.dumps(index, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
