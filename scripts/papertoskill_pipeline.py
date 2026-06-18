#!/usr/bin/env python
"""Run the local PaperToSkill text-to-skill pipeline.

This command composes the deterministic extracted-text note scaffold, skill
extraction, and rubric evaluation steps. It is intentionally local and
auditable; it does not claim arbitrary-PDF semantic fidelity.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import evaluate_skill
import papertoskill_extract
import papertoskill_note_from_text


def default_paths(output_dir: Path, paper_id: str) -> dict[str, Path]:
    return {
        "extracted_text": output_dir / "extracted_text" / f"{paper_id}.txt",
        "note": output_dir / "notes" / f"{paper_id}_auto_note.md",
        "note_report": output_dir / "reports" / f"{paper_id}_note_scaffold.json",
        "skill_dir": output_dir / "skills" / paper_id,
        "evaluation": output_dir / "reports" / f"{paper_id}_rubric.json",
        "manifest": output_dir / "manifest.json",
    }


def prepare_source(source: Path, paths: dict[str, Path]) -> tuple[Path, dict[str, Any]]:
    if source.suffix.lower() != ".pdf":
        return source, {"input_type": "text", "original_source": str(source), "text_source": str(source)}

    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise RuntimeError("pdftotext is required for PDF input but was not found on PATH")

    text_path = paths["extracted_text"]
    text_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [pdftotext, "-layout", str(source), str(text_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return text_path, {
        "input_type": "pdf",
        "original_source": str(source),
        "text_source": str(text_path),
        "text_extractor": "pdftotext -layout",
    }


def run_pipeline(
    *,
    source: Path,
    output_dir: Path,
    paper_id: str | None,
    title: str | None,
    profile: str,
    skill_name: str | None,
    rubric: Path,
) -> dict[str, Any]:
    inferred_paper_id = paper_id or source.stem
    paths = default_paths(output_dir, inferred_paper_id)
    text_source, source_info = prepare_source(source, paths)

    note_report = papertoskill_note_from_text.write_outputs(
        text_source,
        paths["note"],
        inferred_paper_id,
        title,
        paths["note_report"],
        profile,
    )
    skill_report = papertoskill_extract.write_outputs(
        paths["note"],
        paths["skill_dir"],
        skill_name,
        title,
    )
    evaluation = evaluate_skill.evaluate(paths["skill_dir"] / "SKILL.md", rubric)
    paths["evaluation"].parent.mkdir(parents=True, exist_ok=True)
    paths["evaluation"].write_text(json.dumps(evaluation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": "0.1",
        "source": str(source),
        "source_info": source_info,
        "paper_id": inferred_paper_id,
        "title": note_report["title"],
        "profile": profile,
        "rubric": str(rubric),
        "outputs": {
            "extracted_text": str(paths["extracted_text"]) if source_info["input_type"] == "pdf" else None,
            "note": str(paths["note"]),
            "note_report": str(paths["note_report"]),
            "skill": str(paths["skill_dir"] / "SKILL.md"),
            "source_map": str(paths["skill_dir"] / "references" / "source_map.json"),
            "evaluation": str(paths["evaluation"]),
        },
        "score": {
            "value": evaluation["score"],
            "max_score": evaluation["max_score"],
        },
        "evidence_boundary": (
            "Composes deterministic local scaffold steps. The manifest proves "
            "the pipeline executed and produced auditable artifacts; it does "
            "not prove human semantic fidelity or reliable arbitrary-PDF "
            "automation."
        ),
        "note_selection": {
            "line_count": note_report["line_count"],
            "selected_counts": {
                "methods": len(note_report["selected"]["methods"]),
                "experiments": len(note_report["selected"]["experiments"]),
                "limitations": len(note_report["selected"]["limitations"]),
            },
        },
        "skill": {
            "name": skill_report["name"],
            "title": skill_report["title"],
        },
    }
    paths["manifest"].parent.mkdir(parents=True, exist_ok=True)
    paths["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local PaperToSkill text-to-skill pipeline.")
    parser.add_argument("--source", required=True, type=Path, help="Extracted paper text path, or a PDF when pdftotext is available.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for note, skill, reports, and manifest.")
    parser.add_argument("--paper-id", help="Optional paper identifier. Defaults to source stem.")
    parser.add_argument("--title", help="Optional paper title.")
    parser.add_argument(
        "--profile",
        choices=sorted(papertoskill_note_from_text.PROFILE_SPECS),
        default="toolformer",
        help="Source-selection profile for the note scaffold.",
    )
    parser.add_argument("--skill-name", help="Optional skill manifest name.")
    parser.add_argument("--rubric", default=Path("benchmarks/rubric_v0.json"), type=Path)
    args = parser.parse_args()

    if not args.source.exists():
        parser.error(f"Source file not found: {args.source}")
    if not args.rubric.exists():
        parser.error(f"Rubric file not found: {args.rubric}")

    try:
        manifest = run_pipeline(
            source=args.source,
            output_dir=args.output_dir,
            paper_id=args.paper_id,
            title=args.title,
            profile=args.profile,
            skill_name=args.skill_name,
            rubric=args.rubric,
        )
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
