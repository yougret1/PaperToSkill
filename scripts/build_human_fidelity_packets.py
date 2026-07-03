#!/usr/bin/env python
"""Build human-fidelity review packets for generated PaperToSkill skills."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
            "## Completion Requirements",
            "",
        ]
    )
    packet_lines.extend(f"- {item}" for item in config["completion_requirements"])
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
        "packet_path",
        "criterion_id",
        "criterion_label",
        "score_0_to_3",
        "evidence_locator",
        "evidence_note",
        "confidence_0_to_1",
        "reviewer_id",
        "review_date",
        "needs_discussion",
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
                        "packet_path": packet["packet_path"],
                        "criterion_id": criterion["id"],
                        "criterion_label": criterion["label"],
                        "score_0_to_3": "",
                        "evidence_locator": "",
                        "evidence_note": "",
                        "confidence_0_to_1": "",
                        "reviewer_id": "",
                        "review_date": "",
                        "needs_discussion": "",
                    }
                )


def write_annotation_guide(path: Path, config: dict[str, Any], packet_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Human Fidelity Annotation Guide",
        "",
        "Evidence boundary: this guide prepares independent human review. It does not contain completed annotations.",
        "",
        "## Workflow",
        "",
        "1. Open the packet for one paper and read the generated skill, source-note excerpt, and artifact summary.",
        "2. Score each criterion from 0 to 3 using the protocol scale.",
        "3. Fill `evidence_locator` with a source-note line, source-map entry, generated-skill section, or packet section that supports the judgment.",
        "4. Fill `evidence_note` with the shortest explanation needed to justify the score.",
        "5. Fill `confidence_0_to_1`, `reviewer_id`, `review_date`, and optionally `needs_discussion`.",
        "6. Run `scripts\\summarize_human_fidelity_annotations.py --strict` before using the annotations in any claim.",
        "",
        "## Completion Requirements",
        "",
    ]
    lines.extend(f"- {item}" for item in config["completion_requirements"])
    lines.extend(
        [
            "",
            "## Packets",
            "",
            "| Paper | Packet | Rows |",
            "| --- | --- | --- |",
        ]
    )
    criteria_count = len(config["criteria"])
    for row in packet_rows:
        lines.append(f"| {row['paper']} | `{row['packet_path']}` | {criteria_count} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary(path: Path, packet_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Human Fidelity Review Packets",
        "",
        "Evidence boundary: packets and annotation templates are prepared, but no human annotation has been completed.",
        "",
        "- Annotation guide: `results/human_fidelity_packets/annotation_guide.md`",
        "- Annotation template: `results/human_fidelity_packets/annotation_template.csv`",
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


def write_reviewer_bundle_readme(path: Path, packet_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# PaperToSkill Human Fidelity Reviewer Bundle",
        "",
        "Evidence boundary: this bundle prepares independent review. It does not contain completed human annotations.",
        "",
        "## Files",
        "",
        "- `annotation_guide.md`: scoring protocol and workflow.",
        "- `annotation_template.csv`: file reviewers should fill.",
        "- `*_human_fidelity_packet.md`: one packet per paper.",
        "- `reviewer_bundle_manifest.json`: file list and SHA256 checksums.",
        "",
        "## Review Workflow",
        "",
        "1. Read `annotation_guide.md`.",
        "2. Open each paper packet listed below.",
        "3. Fill every row in `annotation_template.csv` with score/evidence/confidence/reviewer metadata.",
        "4. Leave unreviewed rows blank; do not convert missing review rows into zero scores.",
        "5. Return the filled `annotation_template.csv` to the PaperToSkill repository owner.",
        "",
        "## Paper Packets",
        "",
        "| Paper | Packet |",
        "| --- | --- |",
    ]
    for row in packet_rows:
        lines.append(f"| {row['paper']} | `{Path(row['packet_path']).name}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "PaperToSkill cannot claim human validation until the strict summarizer reports all 24 rows scored with no errors.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_reviewer_bundle(
    root: Path,
    output_dir: Path,
    packet_rows: list[dict[str, Any]],
    annotation_template: Path,
    annotation_guide: Path,
) -> dict[str, Path]:
    readme_path = output_dir / "reviewer_bundle_README.md"
    manifest_path = output_dir / "reviewer_bundle_manifest.json"
    zip_path = output_dir / "human_fidelity_reviewer_bundle.zip"
    write_reviewer_bundle_readme(readme_path, packet_rows)

    bundle_files = [
        ("REVIEWER_README.md", readme_path, "Reviewer-facing quickstart."),
        ("annotation_guide.md", annotation_guide, "Scoring protocol and completion rules."),
        ("annotation_template.csv", annotation_template, "Blank 24-row annotation template to fill."),
    ]
    for row in packet_rows:
        packet_path = root / row["packet_path"]
        bundle_files.append((packet_path.name, packet_path, f"Human-fidelity packet for {row['paper']}."))

    manifest = {
        "schema_version": "0.1",
        "evidence_boundary": "Reviewer bundle readiness only; no completed human annotation is included.",
        "bundle_zip": display_path(root, zip_path),
        "required_annotation_rows": 24,
        "files": [
            {
                "archive_path": f"human_fidelity_review/{archive_name}",
                "source_path": display_path(root, source_path),
                "sha256": sha256_file(source_path),
                "purpose": purpose,
            }
            for archive_name, source_path, purpose in bundle_files
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for archive_name, source_path, _purpose in bundle_files:
            archive.write(source_path, arcname=f"human_fidelity_review/{archive_name}")
        archive.write(manifest_path, arcname="human_fidelity_review/reviewer_bundle_manifest.json")

    return {
        "reviewer_bundle_readme": readme_path,
        "reviewer_bundle_manifest": manifest_path,
        "reviewer_bundle_zip": zip_path,
    }


def build_packets(root: Path, config_path: Path, output_dir: Path) -> dict[str, Path]:
    config = load_json(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_rows = [write_packet(root, output_dir, config, paper) for paper in config["papers"]]

    index_path = output_dir / "index.json"
    annotation_template = output_dir / "annotation_template.csv"
    annotation_guide = output_dir / "annotation_guide.md"
    summary_path = output_dir / "README.md"

    index_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "protocol": str(config_path.relative_to(root)).replace("\\", "/"),
                "evidence_boundary": config["evidence_boundary"],
                "annotation_template": display_path(root, annotation_template),
                "annotation_guide": display_path(root, annotation_guide),
                "paper_count": len(config["papers"]),
                "criteria_count": len(config["criteria"]),
                "required_annotation_rows": len(config["papers"]) * len(config["criteria"]),
                "completion_requirements": config["completion_requirements"],
                "packets": packet_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_annotation_template(annotation_template, config, packet_rows)
    write_annotation_guide(annotation_guide, config, packet_rows)
    write_summary(summary_path, packet_rows)
    bundle_paths = write_reviewer_bundle(root, output_dir, packet_rows, annotation_template, annotation_guide)

    written = {
        "index": index_path,
        "annotation_template": annotation_template,
        "annotation_guide": annotation_guide,
        "summary": summary_path,
        **bundle_paths,
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
