#!/usr/bin/env python
"""Check paper-facing text for overclaims and required evidence boundaries."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TARGET_FILES = {
    "aaai_tex": "paper/aaai/papertoskill_aaai2027.tex",
    "draft_md": "paper/draft.md",
}

NEGATION_CUES = (
    "not ",
    "not yet",
    "does not",
    "do not",
    "no ",
    "without",
    "future work",
    "pending",
    "blocked",
    "unavailable",
    "rather than",
    "remain",
    "remains",
)

NEGATION_REGEXES = (
    r"\bnot\b",
    r"\bnot\s+yet\b",
    r"\bdoes\s+not\b",
    r"\bdo\s+not\b",
    r"\bno\b",
    r"\bwithout\b",
    r"\bfuture\s+work\b",
    r"\bpending\b",
    r"\bblocked\b",
    r"\bunavailable\b",
    r"\brather\s+than\b",
    r"\bremain(?:s|ed)?\b",
)

FORBIDDEN_PATTERNS = [
    {
        "id": "full_pdf_automation",
        "pattern": r"\b(fully automatic|reliable|reliably|robust)\b[^.]{0,120}\b(PDF|arbitrary-PDF|arbitrary PDFs?)\b",
        "detail": "Do not claim robust arbitrary-PDF automation without completed evidence.",
    },
    {
        "id": "live_transfer_success",
        "pattern": r"\blive\b[^.]{0,120}\b(cross-harness|transfer|agent)\b[^.]{0,120}\b(completed|successful|success|improves?|proven)\b",
        "detail": "Do not claim completed or successful live transfer.",
    },
    {
        "id": "human_validated",
        "pattern": r"\b(human[- ]validated|expert[- ]validated|human fidelity annotation has been completed|completed human[- ]fidelity)\b",
        "detail": "Do not claim completed human validation.",
    },
    {
        "id": "provider_billing",
        "pattern": r"\b(provider billing|provider-specific prices|live invoices?|success[- ]per[- ]dollar|success per dollar)\b",
        "detail": "Do not claim provider billing or success-per-dollar evidence.",
    },
    {
        "id": "completed_model_ablation",
        "pattern": r"\b(Claude/GPT/DeepSeek ablations have completed|completed (Claude|GPT|DeepSeek)[^.\n]{0,80}ablation|GPT 5\.5 is confirmed)\b",
        "detail": "Do not claim completed Claude/GPT/DeepSeek ablations.",
    },
    {
        "id": "submission_final",
        "pattern": r"\b(submission-final|accepted by AAAI|AAAI acceptance|camera-ready)\b",
        "detail": "Do not claim submission-final or acceptance status.",
    },
]

REQUIRED_BOUNDARIES = [
    {
        "id": "curated_scope",
        "pattern": r"curated[^.\n]{0,80}paper notes?",
        "detail": "Paper text should state the current curated-note scope.",
    },
    {
        "id": "not_pdf_automation",
        "pattern": r"(not presented as[^.\n]{0,80}fully automatic PDF|do not establish[^.\n]{0,80}arbitrary-PDF automation|rather than arbitrary PDFs?)",
        "detail": "Paper text should distinguish the current system from robust arbitrary-PDF automation.",
    },
    {
        "id": "live_transfer_pending",
        "pattern": r"(live cross-harness[^.]{0,80}future\s+work|live cross-harness[^.]{0,80}has\s+not\s+completed|live agent execution[^.]{0,80}not)",
        "detail": "Paper text should keep live cross-harness execution pending.",
    },
    {
        "id": "human_fidelity_pending",
        "pattern": r"(human fidelity[^.\n]{0,80}future work|no independent annotations|human-fidelity[^.\n]{0,80}unscored)",
        "detail": "Paper text should keep human-fidelity annotation pending.",
    },
    {
        "id": "cost_proxy_boundary",
        "pattern": r"(not as provider billing evidence|not by provider-specific prices|not provider bills)",
        "detail": "Paper text should frame cost evidence as local proxy evidence.",
    },
    {
        "id": "model_ablation_partial_boundary",
        "pattern": r"(Claude[^.\n]{0,80}(saved|scored|completed)[^.\n]{0,80}(GPT|DeepSeek)[^.\n]{0,120}pending|GPT[^.\n]{0,80}DeepSeek[^.\n]{0,80}(pending|remain))",
        "detail": "Paper text should classify model ablations as partially completed with GPT/DeepSeek still pending.",
    },
]


@dataclass
class Check:
    id: str
    status: str
    detail: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "status": self.status,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def strip_latex_commands(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = text.replace(r"\texttt{", "").replace("}", "")
    text = text.replace(r"\_", "_")
    text = text.replace("~", " ")
    return text


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_negated_or_bounded(text: str, start: int, end: int) -> bool:
    before = text[max(0, start - 120) : start].lower()
    match_text = text[start:end].lower()
    after = text[end : min(len(text), end + 80)].lower()
    window = before + match_text + after
    return any(cue in window for cue in NEGATION_CUES) or any(
        re.search(pattern, window, flags=re.IGNORECASE) for pattern in NEGATION_REGEXES
    )


def target_texts(root: Path, targets: dict[str, str]) -> dict[str, tuple[Path, str]]:
    loaded: dict[str, tuple[Path, str]] = {}
    for target_id, raw_path in targets.items():
        path = root / raw_path
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".tex":
            text = strip_latex_commands(text)
        loaded[target_id] = (path, text)
    return loaded


def required_file_checks(root: Path, targets: dict[str, str]) -> list[Check]:
    checks = []
    for target_id, raw_path in targets.items():
        path = root / raw_path
        checks.append(
            Check(
                f"paper_claim_target_{target_id}",
                "ready" if path.exists() else "fail",
                "present" if path.exists() else "missing",
                raw_path,
            )
        )
    return checks


def forbidden_claim_checks(root: Path, loaded: dict[str, tuple[Path, str]]) -> list[Check]:
    checks: list[Check] = []
    for target_id, (path, text) in loaded.items():
        for spec in FORBIDDEN_PATTERNS:
            unsupported = []
            for match in re.finditer(spec["pattern"], text, flags=re.IGNORECASE | re.DOTALL):
                if is_negated_or_bounded(text, match.start(), match.end()):
                    continue
                excerpt = re.sub(r"\s+", " ", match.group(0)).strip()
                unsupported.append(f"line {line_number(text, match.start())}: {excerpt}")
            checks.append(
                Check(
                    f"paper_claim_no_{target_id}_{spec['id']}",
                    "ready" if not unsupported else "fail",
                    spec["detail"] if not unsupported else "; ".join(unsupported[:3]),
                    display_path(root, path),
                )
            )
    return checks


def required_boundary_checks(root: Path, loaded: dict[str, tuple[Path, str]]) -> list[Check]:
    combined = "\n".join(text for _, text in loaded.values())
    evidence = ", ".join(display_path(root, path) for path, _ in loaded.values())
    checks: list[Check] = []
    for spec in REQUIRED_BOUNDARIES:
        found = re.search(spec["pattern"], combined, flags=re.IGNORECASE | re.DOTALL)
        checks.append(
            Check(
                f"paper_claim_boundary_{spec['id']}",
                "ready" if found else "fail",
                "present" if found else spec["detail"],
                evidence,
            )
        )
    return checks


def build_report(root: Path, targets: dict[str, str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    targets = targets or TARGET_FILES
    checks = required_file_checks(root, targets)

    missing = [check.evidence for check in checks if check.status == "fail"]
    loaded = {} if missing else target_texts(root, targets)
    if not missing:
        checks.extend(forbidden_claim_checks(root, loaded))
        checks.extend(required_boundary_checks(root, loaded))

    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks paper-facing text for unsupported overclaims and required evidence-boundary statements. "
            "A ready report improves claim discipline; it does not add empirical evidence."
        ),
        "targets": targets,
        "overall_status": "fail" if status_counts.get("fail", 0) else "ready",
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    counts = report["status_counts"]
    lines = [
        "# Paper Claim Discipline Report",
        "",
        "Evidence boundary: this report checks paper-facing text for unsupported "
        "overclaims and required evidence-boundary statements. It does not add "
        "empirical evidence.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check PaperToSkill paper claim discipline.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "paper_claim_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "paper_claim_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any claim check fails.")
    args = parser.parse_args()

    report = build_report(args.root)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
