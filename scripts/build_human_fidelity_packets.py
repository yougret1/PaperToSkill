#!/usr/bin/env python
"""Build human-fidelity review packets for generated PaperToSkill skills."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def first_result(report: dict[str, Any]) -> dict[str, Any]:
    results = report.get("results", [])
    if not results:
        return {}
    return results[0]


def context_skill_score(report: dict[str, Any]) -> str:
    for result in report.get("results", []):
        if result.get("id") == "skill":
            return f"{result.get('score')}/{result.get('max_score')}"
    return "n/a"


def source_map_count(path: Path) -> int:
    if not path.exists():
        return 0
    data = load_json(path)
    if isinstance(data, dict):
        grouped_total = sum(
            len(data.get(key, []))
            for key in ["workflow_steps", "validation_checks", "failure_cases"]
            if isinstance(data.get(key), list)
        )
        if grouped_total:
            return grouped_total
        if isinstance(data.get("items"), list):
            return len(data["items"])
        if isinstance(data.get("mappings"), list):
            return len(data["mappings"])
        if isinstance(data.get("source_map"), list):
            return len(data["source_map"])
    if isinstance(data, list):
        return len(data)
    return 0


def text_excerpt(text: str, max_chars: int = 6000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n\n[Excerpt truncated for review packet. See source file for full text.]"


def display_path(root: Path, path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(resolved)


def write_packet(root: Path, output_dir: Path, config: dict[str, Any], paper: dict[str, Any]) -> dict[str, Any]:
    skill_path = root / paper["skill_path"]
    note_path = root / paper["source_note_path"]
    span_report_path = root / paper["source_span_report"]
    context_report_path = root / paper["context_report"]
    source_map_path = root / paper["source_map_path"]

    skill_text = skill_path.read_text(encoding="utf-8")
    note_text = note_path.read_text(encoding="utf-8")
    spans = first_result(load_json(span_report_path))
    context_report = load_json(context_report_path)

    packet_path = output_dir / f"{paper['id']}_human_fidelity_packet.md"
    packet_lines = [
        f"# Human Fidelity Review Packet: {paper['paper']}",
        "",
        "Evidence boundary: this packet is an input for human review. It is not a completed annotation.",
        "",
        "## Review Instructions",
        "",
    ]
    packet_lines.extend(f"- {item}" for item in config["instructions"])
    packet_lines.extend(
        [
            "",
            "## Score Scale",
            "",
        ]
    )
    packet_lines.extend(f"- {item['score']}: {item['meaning']}" for item in config["score_scale"])
    packet_lines.extend(
        [
            "",
            "## Artifact Summary",
            "",
            f"- Generated skill: `{paper['skill_path']}`",
            f"- Curated source note: `{paper['source_note_path']}`",
            f"- Extracted paper text: `{paper['extracted_text_path']}`",
            f"- Source map: `{paper['source_map_path']}`",
            f"- Source-span report: `{paper['source_span_report']}`",
            f"- Deterministic skill coverage: {context_skill_score(context_report)}",
            f"- Source-span support rate: {spans.get('support_rate', 'n/a')}",
            f"- Invalid source-span ranges: {spans.get('invalid_ranges', 'n/a')}",
            f"- Source-map entries: {source_map_count(source_map_path)}",
            f"- Skill words: {words(skill_text)}",
            f"- Source note words: {words(note_text)}",
            "",
            "## Criteria",
            "",
            "| Criterion | Question | Score | Evidence note |",
            "| --- | --- | --- | --- |",
        ]
    )
    for criterion in config["criteria"]:
        packet_lines.append(f"| {criterion['label']} | {criterion['question']} |  |  |")
    packet_lines.extend(
        [
            "",
            "## Generated Skill",
            "",
            "```markdown",
            skill_text.rstrip(),
            "```",
            "",
            "## Curated Source Note Excerpt",
            "",
            "```markdown",
            text_excerpt(note_text),
            "```",
            "",
        ]
    )
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text("\n".join(packet_lines), encoding="utf-8")

    return {
        "paper_id": paper["id"],
        "paper": paper["paper"],
        "packet_path": display_path(root, packet_path),
        "skill_path": paper["skill_path"],
        "source_note_path": paper["source_note_path"],
        "source_span_support_rate": spans.get("support_rate"),
        "invalid_source_span_ranges": spans.get("invalid_ranges"),
        "context_skill_score": context_skill_score(context_report),
        "skill_words": words(skill_text),
        "source_note_words": words(note_text),
        "annotation_status": "pending",
    }


def write_annotation_template(path: Path, config: dict[str, Any], packet_rows: list[dict[str, Any]]) -> None:
    columns = [
        "paper_id",
        "paper",
        "criterion_id",
        "criterion_label",
        "score_0_to_3",
        "evidence_note",
        "reviewer_id",
        "review_date",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for packet in packet_rows:
            for criterion in config["criteria"]:
                writer.writerow(
                    {
                        "paper_id": packet["paper_id"],
                        "paper": packet["paper"],
                        "criterion_id": criterion["id"],
                        "criterion_label": criterion["label"],
                        "score_0_to_3": "",
                        "evidence_note": "",
                        "reviewer_id": "",
                        "review_date": "",
                    }
                )


def write_summary(path: Path, packet_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Human Fidelity Review Packets",
        "",
        "Evidence boundary: packets and annotation templates are prepared, but no human annotation has been completed.",
        "",
        "| Paper | Packet | Source support rate | Invalid ranges | Coverage score | Annotation status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in packet_rows:
        lines.append(
            f"| {row['paper']} | `{row['packet_path']}` | {row['source_span_support_rate']} | "
            f"{row['invalid_source_span_ranges']} | {row['context_skill_score']} | {row['annotation_status']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_packets(root: Path, config_path: Path, output_dir: Path) -> dict[str, Path]:
    config = load_json(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_rows = [write_packet(root, output_dir, config, paper) for paper in config["papers"]]

    index_path = output_dir / "index.json"
    annotation_template = output_dir / "annotation_template.csv"
    summary_path = output_dir / "README.md"

    index_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "protocol": str(config_path.relative_to(root)).replace("\\", "/"),
                "evidence_boundary": config["evidence_boundary"],
                "packets": packet_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_annotation_template(annotation_template, config, packet_rows)
    write_summary(summary_path, packet_rows)

    written = {
        "index": index_path,
        "annotation_template": annotation_template,
        "summary": summary_path,
    }
    for row in packet_rows:
        packet_path = Path(row["packet_path"])
        written[row["paper_id"]] = packet_path if packet_path.is_absolute() else root / packet_path
    return written


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build human-fidelity review packets.")
    parser.add_argument("--config", type=Path, default=root / "benchmarks" / "human_fidelity_review_v0.json")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "human_fidelity_packets")
    args = parser.parse_args()

    written = build_packets(root, args.config, args.output_dir)
    for path in written.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
