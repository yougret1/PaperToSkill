#!/usr/bin/env python
"""Check the PaperToSkill AAAI LaTeX package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_AUTHOR_KIT_SHA256 = "E28C6AC9BC6EB3B4E2D849547D2CEFB5162610EE39D0A12E0DC62D1126B44A7D"

REQUIRED_FILES = {
    "readme": "README.md",
    "author_kit_zip": "AuthorKit27.zip",
    "style_file": "aaai2027.sty",
    "bibtex_style": "aaai2027.bst",
    "main_tex": "papertoskill_aaai2027.tex",
    "tables_tex": "papertoskill_tables.tex",
    "refs_bib": "papertoskill_refs.bib",
    "compiled_pdf": "papertoskill_aaai2027.pdf",
    "compiled_log": "papertoskill_aaai2027.log",
    "compiled_bbl": "papertoskill_aaai2027.bbl",
}

LOG_FAILURE_PATTERNS = [
    re.compile(r"LaTeX Warning: Citation .* undefined", re.IGNORECASE),
    re.compile(r"Package natbib Warning: Citation .* undefined", re.IGNORECASE),
    re.compile(r"LaTeX Warning: Reference .* undefined", re.IGNORECASE),
    re.compile(r"There were undefined (references|citations)", re.IGNORECASE),
    re.compile(r"Rerun to get cross-references right", re.IGNORECASE),
    re.compile(r"^! LaTeX Error:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^! Undefined control sequence", re.IGNORECASE | re.MULTILINE),
    re.compile(r"No file .*\.bbl", re.IGNORECASE),
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def evidence_path(aaai_dir: Path, path: Path) -> str:
    relative = path.relative_to(aaai_dir)
    if aaai_dir.name == "aaai" and aaai_dir.parent.name == "paper":
        return (Path("paper") / "aaai" / relative).as_posix()
    return relative.as_posix()


def required_file_checks(aaai_dir: Path) -> list[Check]:
    checks = []
    for check_id, filename in REQUIRED_FILES.items():
        path = aaai_dir / filename
        status = "ready" if path.exists() else "fail"
        detail = "present" if path.exists() else "missing"
        checks.append(Check(f"aaai_{check_id}", status, detail, evidence_path(aaai_dir, path)))
    return checks


def author_kit_sha_check(aaai_dir: Path) -> Check:
    zip_path = aaai_dir / "AuthorKit27.zip"
    if not zip_path.exists():
        return Check("aaai_author_kit_sha256", "fail", "missing AuthorKit27.zip", evidence_path(aaai_dir, zip_path))
    actual = sha256(zip_path)
    status = "ready" if actual == EXPECTED_AUTHOR_KIT_SHA256 else "fail"
    detail = f"sha256={actual}"
    return Check("aaai_author_kit_sha256", status, detail, evidence_path(aaai_dir, zip_path))


def tex_declares_aaai_style_check(aaai_dir: Path) -> Check:
    tex_path = aaai_dir / "papertoskill_aaai2027.tex"
    if not tex_path.exists():
        return Check("aaai_tex_declares_style", "fail", "missing main tex", evidence_path(aaai_dir, tex_path))
    text = tex_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{aaai2027\}")
    status = "ready" if pattern.search(text) else "fail"
    detail = "uses aaai2027 package" if status == "ready" else "missing \\usepackage{aaai2027}"
    return Check("aaai_tex_declares_style", status, detail, evidence_path(aaai_dir, tex_path))


def log_checks(aaai_dir: Path) -> list[Check]:
    log_path = aaai_dir / "papertoskill_aaai2027.log"
    if not log_path.exists():
        return [
            Check("aaai_log_loads_style", "fail", "missing log", evidence_path(aaai_dir, log_path)),
            Check("aaai_log_no_unresolved_items", "fail", "missing log", evidence_path(aaai_dir, log_path)),
            Check("aaai_log_reports_pdf_output", "fail", "missing log", evidence_path(aaai_dir, log_path)),
        ]
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    loads_style = "Package: aaai2027" in text or "Conference Style for AAAI for LaTeX 2e" in text
    output_match = re.search(
        r"Output written on papertoskill_aaai2027\.pdf \((\d+) pages?, ([0-9]+) bytes\)",
        text,
    )
    failures = []
    for pattern in LOG_FAILURE_PATTERNS:
        failures.extend(match.group(0).strip() for match in pattern.finditer(text))

    return [
        Check(
            "aaai_log_loads_style",
            "ready" if loads_style else "fail",
            "aaai2027 loaded" if loads_style else "aaai2027 load marker missing",
            evidence_path(aaai_dir, log_path),
        ),
        Check(
            "aaai_log_no_unresolved_items",
            "ready" if not failures else "fail",
            "no unresolved citation/reference/build markers" if not failures else "; ".join(failures[:5]),
            evidence_path(aaai_dir, log_path),
        ),
        Check(
            "aaai_log_reports_pdf_output",
            "ready" if output_match else "fail",
            (
                f"pages={output_match.group(1)}; bytes={output_match.group(2)}"
                if output_match
                else "missing PDF output marker"
            ),
            evidence_path(aaai_dir, log_path),
        ),
    ]


def freshness_checks(aaai_dir: Path) -> list[Check]:
    tex_inputs = [
        aaai_dir / "papertoskill_aaai2027.tex",
        aaai_dir / "papertoskill_tables.tex",
        aaai_dir / "papertoskill_refs.bib",
    ]
    pdf_path = aaai_dir / "papertoskill_aaai2027.pdf"
    log_path = aaai_dir / "papertoskill_aaai2027.log"
    bbl_path = aaai_dir / "papertoskill_aaai2027.bbl"

    missing = [str(path) for path in [*tex_inputs, pdf_path, log_path, bbl_path] if not path.exists()]
    if missing:
        detail = "missing=" + ",".join(
            evidence_path(aaai_dir, path) for path in [*tex_inputs, pdf_path, log_path, bbl_path] if not path.exists()
        )
        return [
            Check("aaai_pdf_is_fresh", "fail", detail, evidence_path(aaai_dir, pdf_path)),
            Check("aaai_bbl_is_fresh", "fail", detail, evidence_path(aaai_dir, bbl_path)),
        ]

    latest_input_mtime = max(path.stat().st_mtime for path in tex_inputs)
    pdf_fresh = pdf_path.stat().st_mtime >= latest_input_mtime and log_path.stat().st_mtime >= latest_input_mtime
    bbl_fresh = bbl_path.stat().st_mtime >= (aaai_dir / "papertoskill_refs.bib").stat().st_mtime

    return [
        Check(
            "aaai_pdf_is_fresh",
            "ready" if pdf_fresh else "fail",
            "pdf/log newer than tex inputs" if pdf_fresh else "pdf/log older than tex inputs",
            evidence_path(aaai_dir, pdf_path),
        ),
        Check(
            "aaai_bbl_is_fresh",
            "ready" if bbl_fresh else "fail",
            "bbl newer than bibliography" if bbl_fresh else "bbl older than bibliography",
            evidence_path(aaai_dir, bbl_path),
        ),
    ]


def build_report(aaai_dir: Path) -> dict[str, Any]:
    aaai_dir = aaai_dir.resolve()
    checks: list[Check] = []
    checks.extend(required_file_checks(aaai_dir))
    checks.append(author_kit_sha_check(aaai_dir))
    checks.append(tex_declares_aaai_style_check(aaai_dir))
    checks.extend(log_checks(aaai_dir))
    checks.extend(freshness_checks(aaai_dir))

    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    overall = "fail" if status_counts.get("fail", 0) else "ready"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks the local AAAI LaTeX package and build artifacts. A ready report means "
            "the current local package is internally consistent; it is not a submission or acceptance claim."
        ),
        "aaai_dir": str(aaai_dir),
        "overall_status": overall,
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
        "# AAAI Package Report",
        "",
        "Evidence boundary: this report checks the local AAAI LaTeX package and "
        "build artifacts. It does not claim the paper is submission-final.",
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
    parser = argparse.ArgumentParser(description="Check the PaperToSkill AAAI LaTeX package.")
    parser.add_argument("--aaai-dir", type=Path, default=root / "paper" / "aaai")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "aaai_package_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "aaai_package_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any AAAI package check fails.")
    args = parser.parse_args()

    report = build_report(args.aaai_dir)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
