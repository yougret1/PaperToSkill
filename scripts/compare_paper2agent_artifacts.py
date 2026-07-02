#!/usr/bin/env python
"""Build a bounded PaperToSkill vs Paper2Agent artifact comparison.

The comparison is source-backed from the local Paper2Agent extracted text and
the current PaperToSkill artifacts. It does not run Paper2Agent or claim an
end-to-end MCP baseline result.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PAPER2AGENT_TEXT = (
    "papers/extracted_text/"
    "Miao 等 - 2025 - Paper2Agent Reimagining Research Papers As Interactive and Reliable AI Agents.txt"
)
DEFAULT_SKILL = "generated_skills/toolformer/SKILL.md"
DEFAULT_PAPERTOSKILL_EVIDENCE = (
    "skill/SKILL.md",
    "generated_skills/toolformer/SKILL.md",
    "generated_skills/toolformer/references/source_map.json",
    "paper/aaai/papertoskill_aaai2027.tex",
    "results/reproducibility/package_report.md",
)


@dataclass(frozen=True)
class Criterion:
    id: str
    label: str
    paper2agent_terms: tuple[str, ...]
    papertoskill_terms: tuple[str, ...]
    paper2agent_expected: str
    papertoskill_expected: str
    interpretation: str


CRITERIA = [
    Criterion(
        id="input_requirements",
        label="Required inputs",
        paper2agent_terms=("paper", "codebase", "public codebase"),
        papertoskill_terms=("source paper", "source note", "references/source_map.json"),
        paper2agent_expected="paper plus associated codebase",
        papertoskill_expected="paper-derived note or extracted text; codebase optional",
        interpretation="Paper2Agent optimizes for executable paper agents, while PaperToSkill can work when only paper text is available.",
    ),
    Criterion(
        id="artifact_type",
        label="Generated artifact",
        paper2agent_terms=("MCP server", "MCP tools", "MCP resources", "MCP prompts"),
        papertoskill_terms=("SKILL.md", "natural-language skill", "Transfer Notes"),
        paper2agent_expected="MCP server with tools, resources, and prompts",
        papertoskill_expected="compact natural-language skill with references and transfer notes",
        interpretation="The two systems expose paper knowledge through different artifact types rather than direct drop-in replacements.",
    ),
    Criterion(
        id="setup_burden",
        label="Setup burden",
        paper2agent_terms=("environment configuration", "deployed remotely", "Hugging Face", "server"),
        papertoskill_terms=("load", "portable", "Codex-style", "harness"),
        paper2agent_expected="configure environment and deploy or connect an MCP server",
        papertoskill_expected="load one skill file plus local reference artifacts into an agent harness",
        interpretation="PaperToSkill has lower setup burden for reading and transfer, but lacks executable MCP tools.",
    ),
    Criterion(
        id="validation_checks",
        label="Validation checks",
        paper2agent_terms=("iteratively generates and runs tests", "validated through iterative testing", "benchmark"),
        papertoskill_terms=("rubric", "source support", "harness transfer", "validation checks"),
        paper2agent_expected="iterative MCP tests and downstream case-study benchmarks",
        papertoskill_expected="deterministic rubric, source-span, transfer-readiness, compactness, and saved-response checks",
        interpretation="Both use validation, but Paper2Agent validates executable tools and PaperToSkill validates source-grounded skill artifacts.",
    ),
    Criterion(
        id="failure_handling",
        label="Failure handling",
        paper2agent_terms=("repeatedly fail", "decorators are removed", "cannot reliably expose"),
        papertoskill_terms=("Failure Modes", "failure cases", "stop condition", "failure branch"),
        paper2agent_expected="remove failing MCP decorators/tools and report codebase limitations",
        papertoskill_expected="record failure branches, stop conditions, and unsupported evidence boundaries",
        interpretation="PaperToSkill's distinctive contribution is making failure branches editable inside the skill artifact.",
    ),
    Criterion(
        id="source_traceability",
        label="Source traceability",
        paper2agent_terms=("traceable link", "original", "recorded for each step"),
        papertoskill_terms=("source_map", "source-backed", "source spans", "references/source_map.json"),
        paper2agent_expected="tool/resource links and recorded workflow traces",
        papertoskill_expected="source map and source-span validation tied to skill sections",
        interpretation="Both care about provenance; PaperToSkill makes source boundaries central to the natural-language artifact.",
    ),
    Criterion(
        id="runtime_dependency",
        label="Runtime dependency",
        paper2agent_terms=("MCP server", "hosted remotely", "external agent", "Claude Code"),
        papertoskill_terms=("without requiring an MCP server", "cross-harness", "human-editable", "portable"),
        paper2agent_expected="MCP runtime plus downstream agent connection",
        papertoskill_expected="text skill usable across compatible agent harnesses",
        interpretation="This is the main positioning gap: server-backed executable agents versus portable skill instructions.",
    ),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def find_evidence(text: str, terms: tuple[str, ...]) -> tuple[bool, str]:
    lowered = text.lower()
    for term in terms:
        index = lowered.find(term.lower())
        if index >= 0:
            start = max(0, index - 140)
            end = min(len(text), index + len(term) + 220)
            return True, normalize(text[start:end])
    return False, ""


def word_count(path: Path) -> int:
    text = read_text(path)
    return len(re.findall(r"\b\S+\b", text))


def build_report(root: Path, paper2agent_text: Path, papertoskill_skill: Path) -> dict[str, Any]:
    paper2agent = read_text(paper2agent_text)
    evidence_paths = [papertoskill_skill]
    for raw_path in DEFAULT_PAPERTOSKILL_EVIDENCE:
        path = root / raw_path
        if path not in evidence_paths:
            evidence_paths.append(path)
    skill = "\n\n".join(read_text(path) for path in evidence_paths)

    rows: list[dict[str, Any]] = []
    for criterion in CRITERIA:
        p2a_present, p2a_evidence = find_evidence(paper2agent, criterion.paper2agent_terms)
        pts_present, pts_evidence = find_evidence(skill, criterion.papertoskill_terms)
        status = "ready" if p2a_present and pts_present else "fail"
        rows.append(
            {
                "criterion_id": criterion.id,
                "criterion": criterion.label,
                "status": status,
                "paper2agent_expected": criterion.paper2agent_expected,
                "papertoskill_expected": criterion.papertoskill_expected,
                "paper2agent_evidence": p2a_evidence,
                "papertoskill_evidence": pts_evidence,
                "interpretation": criterion.interpretation,
            }
        )

    status_counts = {"ready": 0, "fail": 0}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Source-backed artifact/workflow comparison only. It compares Paper2Agent's reported MCP workflow "
            "with current PaperToSkill artifacts and does not run Paper2Agent, deploy an MCP server, or claim "
            "end-to-end baseline performance."
        ),
        "inputs": {
            "paper2agent_text": str(paper2agent_text.relative_to(root)),
            "papertoskill_evidence_paths": [str(path.relative_to(root)) for path in evidence_paths],
        },
        "size_proxy": {
            "paper2agent_extracted_text_words": word_count(paper2agent_text),
            "papertoskill_skill_words": word_count(papertoskill_skill),
        },
        "overall_status": "ready" if status_counts.get("fail", 0) == 0 else "fail",
        "status_counts": status_counts,
        "rows": rows,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "criterion_id",
        "criterion",
        "status",
        "paper2agent_expected",
        "papertoskill_expected",
        "interpretation",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fieldnames})


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_md(path: Path, report: dict[str, Any]) -> None:
    rows = [
        [
            row["criterion"],
            row["status"],
            row["paper2agent_expected"],
            row["papertoskill_expected"],
            row["interpretation"],
        ]
        for row in report["rows"]
    ]
    counts = report["status_counts"]
    size = report["size_proxy"]
    lines = [
        "# Paper2Agent Artifact Comparison",
        "",
        "Evidence boundary: this is a bounded source-backed artifact/workflow comparison. "
        "It does not run Paper2Agent, deploy an MCP server, or claim baseline performance.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready criteria: {counts.get('ready', 0)}",
        f"- Failed criteria: {counts.get('fail', 0)}",
        f"- Paper2Agent extracted text words: {size['paper2agent_extracted_text_words']}",
        f"- PaperToSkill skill words: {size['papertoskill_skill_words']}",
        "",
        "## Comparison",
        "",
        markdown_table(
            rows,
            ["Criterion", "Status", "Paper2Agent", "PaperToSkill", "Interpretation"],
        ),
        "",
        "## Evidence Snippets",
        "",
    ]
    for row in report["rows"]:
        lines.extend(
            [
                f"### {row['criterion']}",
                "",
                f"- Paper2Agent evidence: {row['paper2agent_evidence']}",
                f"- PaperToSkill evidence: {row['papertoskill_evidence']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Compare PaperToSkill artifacts with Paper2Agent-style MCP artifacts.")
    parser.add_argument("--paper2agent-text", type=Path, default=root / DEFAULT_PAPER2AGENT_TEXT)
    parser.add_argument("--papertoskill-skill", type=Path, default=root / DEFAULT_SKILL)
    parser.add_argument("--output-json", type=Path, default=root / "results/tables/paper2agent_artifact_comparison.json")
    parser.add_argument("--output-csv", type=Path, default=root / "results/tables/paper2agent_artifact_comparison.csv")
    parser.add_argument("--output-md", type=Path, default=root / "results/tables/paper2agent_artifact_comparison.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = build_report(root, args.paper2agent_text, args.papertoskill_skill)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(args.output_csv, report["rows"])
    write_md(args.output_md, report)
    print(args.output_json)
    print(args.output_csv)
    print(args.output_md)
    if args.strict and report["overall_status"] != "ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
