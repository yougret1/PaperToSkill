#!/usr/bin/env python
"""Build a submission-bundle manifest for the PaperToSkill paper package."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BUNDLE_FILES = {
    "aaai_pdf": "paper/aaai/papertoskill_aaai2027.pdf",
    "aaai_tex": "paper/aaai/papertoskill_aaai2027.tex",
    "aaai_tables": "paper/aaai/papertoskill_tables.tex",
    "aaai_supporting_tables": "paper/aaai/papertoskill_supporting_tables.tex",
    "aaai_refs": "paper/aaai/papertoskill_refs.bib",
    "aaai_readme": "paper/aaai/README.md",
    "aaai_style": "paper/aaai/aaai2027.sty",
    "aaai_bst": "paper/aaai/aaai2027.bst",
    "aaai_author_kit": "paper/aaai/AuthorKit27.zip",
    "aaai_package_report": "results/reproducibility/aaai_package_report.json",
    "paper_claim_report": "results/reproducibility/paper_claim_report.json",
    "paper_table_report": "results/reproducibility/paper_table_report.json",
    "submission_review_report": "results/reproducibility/submission_review_report.json",
    "package_report": "results/reproducibility/package_report.json",
    "goal_completion_report": "results/reproducibility/goal_completion_report.json",
    "external_closure_report": "results/external_evidence_closure/closure.json",
    "external_packets_report": "results/external_evidence_packets/packets.json",
    "aaai_submission_decision_report": "results/aaai_submission_decision/decision.json",
    "human_fidelity_summary": "results/human_fidelity_packets/annotation_summary.json",
    "submission_checklist": "research/submission_checklist.md",
    "review_report": "research/review_report.md",
    "rebuttal_bank": "research/rebuttal_bank.md",
}

CORE_REPORT_EXPECTATIONS = {
    "aaai_package_report": {"overall_status": {"ready"}},
    "paper_claim_report": {"overall_status": {"ready"}},
    "paper_table_report": {"overall_status": {"ready"}},
    "submission_review_report": {"overall_status": {"ready"}},
    "package_report": {"overall_status": {"ready_with_pending_external_evidence", "ready"}},
    "goal_completion_report": {"overall_status": {"not_complete_pending_external_evidence", "complete"}},
    "external_closure_report": {"overall_status": {"pending_external_evidence", "complete"}},
    "external_packets_report": {"overall_status": {"ready"}},
    "aaai_submission_decision_report": {"overall_status": {"ready"}},
}


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
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_entry(root: Path, file_id: str, raw_path: str) -> dict[str, Any]:
    path = root / raw_path
    entry: dict[str, Any] = {
        "id": file_id,
        "path": raw_path,
        "present": path.exists(),
    }
    if path.exists():
        entry["bytes"] = path.stat().st_size
        entry["sha256"] = sha256(path)
    return entry


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = [file_entry(root, file_id, raw_path) for file_id, raw_path in BUNDLE_FILES.items()]
    checks: list[Check] = []

    missing = [entry["path"] for entry in files if not entry["present"]]
    checks.append(
        Check(
            "submission_bundle_files_present",
            "ready" if not missing else "fail",
            "all files present" if not missing else "missing=" + ",".join(missing),
            "submission bundle manifest inputs",
        )
    )

    for report_id, expectations in CORE_REPORT_EXPECTATIONS.items():
        raw_path = BUNDLE_FILES[report_id]
        path = root / raw_path
        if not path.exists():
            checks.append(Check(f"submission_bundle_{report_id}_status", "fail", "missing", raw_path))
            continue
        data = read_json(path)
        expected_statuses = expectations["overall_status"]
        actual = data.get("overall_status")
        checks.append(
            Check(
                f"submission_bundle_{report_id}_status",
                "ready" if actual in expected_statuses else "fail",
                f"overall_status={actual}",
                raw_path,
            )
        )

    package = read_json(root / BUNDLE_FILES["package_report"]) if (root / BUNDLE_FILES["package_report"]).exists() else {}
    goal = (
        read_json(root / BUNDLE_FILES["goal_completion_report"])
        if (root / BUNDLE_FILES["goal_completion_report"]).exists()
        else {}
    )
    human = (
        read_json(root / BUNDLE_FILES["human_fidelity_summary"])
        if (root / BUNDLE_FILES["human_fidelity_summary"]).exists()
        else {}
    )
    decision = (
        read_json(root / BUNDLE_FILES["aaai_submission_decision_report"])
        if (root / BUNDLE_FILES["aaai_submission_decision_report"]).exists()
        else {}
    )

    human_status = human.get("annotation_status")
    selected_option = decision.get("selected_option")
    pending_goal = goal.get("overall_status") == "not_complete_pending_external_evidence"
    package_pending = package.get("overall_status") == "ready_with_pending_external_evidence"
    checks.append(
        Check(
            "submission_bundle_external_evidence_boundary_current",
            "ready" if pending_goal and package_pending and human_status == "pending" else "fail",
            (
                "package=ready_with_pending_external_evidence; "
                "goal=not_complete_pending_external_evidence; "
                f"human_fidelity={human_status}; selected_option={selected_option}"
            ),
            "results/reproducibility/package_report.json; results/reproducibility/goal_completion_report.json",
        )
    )

    status_counts: dict[str, int] = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    failed = status_counts.get("fail", 0)
    overall = "fail" if failed else "ready_with_pending_external_evidence"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Submission-bundle manifest for local AAAI paper package and gate reports. "
            "A ready manifest records file hashes and current evidence boundaries; it is not "
            "a submission-final, acceptance, or human-fidelity-complete claim."
        ),
        "overall_status": overall,
        "status_counts": status_counts,
        "files": files,
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


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    counts = report["status_counts"]
    file_rows = [
        [
            entry["id"],
            "yes" if entry["present"] else "no",
            str(entry.get("bytes", "")),
            entry.get("sha256", ""),
            entry["path"],
        ]
        for entry in report["files"]
    ]
    check_rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines = [
        "# Submission Bundle Manifest",
        "",
        "Evidence boundary: this manifest records local package files, hashes, and gate "
        "statuses. It does not claim final submission readiness or completed external evidence.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Files",
        "",
        markdown_table(file_rows, ["ID", "Present", "Bytes", "SHA256", "Path"]),
        "",
        "## Checks",
        "",
        markdown_table(check_rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the PaperToSkill submission-bundle manifest.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "submission_bundle_manifest.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "submission_bundle_manifest.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if manifest checks fail.")
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
