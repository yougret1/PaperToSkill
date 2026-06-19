#!/usr/bin/env python
"""Check submission-review handoff artifacts against current evidence."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TARGET_FILES = {
    "review_report": "research/review_report.md",
    "rebuttal_bank": "research/rebuttal_bank.md",
    "submission_checklist": "research/submission_checklist.md",
}

STALE_PATTERNS = [
    {
        "id": "http_503_live_transfer_pending",
        "pattern": r"HTTP\s+503|endpoint\s+still\s+returns|live prompt packets exist,\s*but endpoint",
        "detail": "Review handoff must not use stale Phase 17 live-transfer HTTP 503 wording.",
    },
    {
        "id": "live_transfer_pending",
        "pattern": r"Live cross-harness execution\s*\|\s*Pending|live response logs remain pending",
        "detail": "Live-transfer saved-response rows are now collected and scored; pending wording must be bounded to real task success or human semantics.",
    },
    {
        "id": "old_toolformer_token_row",
        "pattern": r"Toolformer:\s*1,526\s+vs\s+24,097",
        "detail": "Review handoff must use the current tokenizer-aware cost table values.",
    },
]

FORBIDDEN_POSITIVE_PATTERNS = [
    {
        "id": "final_submission_ready",
        "pattern": r"\b(submission-final|ready for submission|accepted by AAAI|AAAI acceptance|camera-ready)\b",
        "detail": "Do not claim final submission or acceptance readiness.",
    },
    {
        "id": "human_validation_complete",
        "pattern": r"\b(human[- ]validated|expert[- ]validated|human fidelity annotation has been completed|completed human[- ]fidelity)\b",
        "detail": "Do not claim completed human semantic validation.",
    },
    {
        "id": "provider_billing_complete",
        "pattern": r"\b(provider billing is complete|provider bills are complete|success[- ]per[- ]dollar evidence is complete|realized provider bills)\b",
        "detail": "Do not claim provider billing or success-per-dollar completion.",
    },
]

NEGATION_REGEXES = (
    r"\bnot\b",
    r"\bnot\s+yet\b",
    r"\bdoes\s+not\b",
    r"\bdo\s+not\b",
    r"\bno\b",
    r"\bwithout\b",
    r"\bfuture\s+work\b",
    r"\bpending\b",
    r"\bremain(?:s|ed)?\b",
)


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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_bounded(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 120) : min(len(text), end + 100)].lower()
    return any(re.search(pattern, window, flags=re.IGNORECASE) for pattern in NEGATION_REGEXES)


def required_file_checks(root: Path) -> list[Check]:
    checks = []
    for check_id, raw_path in TARGET_FILES.items():
        path = root / raw_path
        checks.append(
            Check(
                f"submission_review_target_{check_id}",
                "ready" if path.exists() else "fail",
                "present" if path.exists() else "missing",
                raw_path,
            )
        )
    return checks


def stale_claim_checks(root: Path, combined_text: str) -> list[Check]:
    checks: list[Check] = []
    for spec in STALE_PATTERNS:
        hits = []
        for match in re.finditer(spec["pattern"], combined_text, flags=re.IGNORECASE | re.DOTALL):
            excerpt = re.sub(r"\s+", " ", match.group(0)).strip()
            hits.append(f"line {line_number(combined_text, match.start())}: {excerpt}")
        checks.append(
            Check(
                f"submission_review_no_stale_{spec['id']}",
                "ready" if not hits else "fail",
                spec["detail"] if not hits else "; ".join(hits[:3]),
                "; ".join(TARGET_FILES.values()),
            )
        )
    return checks


def forbidden_positive_checks(combined_text: str) -> list[Check]:
    checks: list[Check] = []
    for spec in FORBIDDEN_POSITIVE_PATTERNS:
        hits = []
        for match in re.finditer(spec["pattern"], combined_text, flags=re.IGNORECASE | re.DOTALL):
            if is_bounded(combined_text, match.start(), match.end()):
                continue
            excerpt = re.sub(r"\s+", " ", match.group(0)).strip()
            hits.append(f"line {line_number(combined_text, match.start())}: {excerpt}")
        checks.append(
            Check(
                f"submission_review_no_unbounded_{spec['id']}",
                "ready" if not hits else "fail",
                spec["detail"] if not hits else "; ".join(hits[:3]),
                "; ".join(TARGET_FILES.values()),
            )
        )
    return checks


def contains_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def smoke_blocker_detail(smoke: dict[str, Any]) -> str:
    for check in smoke.get("checks", []):
        if check.get("id") == "ai_scientist_v2_llm_error":
            return str(check.get("detail", "")).strip()
    return ""


def evidence_alignment_checks(root: Path, combined_text: str) -> list[Check]:
    live = load_json(root / "results/live_transfer_prompts/evaluation.json").get("summary", {})
    model = load_json(root / "results/model_ablation_prompts/v0/evaluation.json").get("summary", {})
    human = load_json(root / "results/human_fidelity_packets/annotation_summary.json")
    billing = load_json(root / "results/provider_billing_evidence/billing_summary.json")
    smoke = load_json(root / "results/ai_scientist_v2_smoke/run_report.json")
    smoke_detail = smoke_blocker_detail(smoke)
    goal = load_json(root / "results/reproducibility/goal_completion_report.json")
    package = load_json(root / "results/reproducibility/package_report.json")
    goal_counts = goal.get("status_counts", {})
    package_counts = package.get("status_counts", {})

    checks = [
        Check(
            "submission_review_live_transfer_current",
            "ready"
            if int(live.get("total_rows", 0)) == 24
            and int(live.get("scored_rows", 0)) == 24
            and int(live.get("pending_rows", 0)) == 0
            and contains_all(combined_text, ["24", "saved-response", "not", "live task success"])
            else "fail",
            f"live_total={live.get('total_rows')}; scored={live.get('scored_rows')}; pending={live.get('pending_rows')}",
            "results/live_transfer_prompts/evaluation.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_model_ablation_current",
            "ready"
            if int(model.get("scored_rows", 0)) == 4
            and int(model.get("pending_rows", 0)) == 2
            and contains_all(combined_text, ["4 scored", "2 pending", "DeepSeek"])
            else "fail",
            f"scored={model.get('scored_rows')}; pending={model.get('pending_rows')}",
            "results/model_ablation_prompts/v0/evaluation.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_human_fidelity_current",
            "ready"
            if human.get("annotation_status") == "pending"
            and int(human.get("scored_rows", -1)) == 0
            and int(human.get("pending_rows", 0)) == 24
            and contains_all(combined_text, ["0 scored", "24 pending", "human"])
            else "fail",
            f"status={human.get('annotation_status')}; scored={human.get('scored_rows')}; pending={human.get('pending_rows')}",
            "results/human_fidelity_packets/annotation_summary.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_provider_billing_current",
            "ready"
            if billing.get("billing_status") == "pending"
            and int(billing.get("measured_rows", -1)) == 0
            and int(billing.get("pending_rows", 0)) == 6
            and contains_all(combined_text, ["0 measured", "6 pending", "provider"])
            else "fail",
            f"status={billing.get('billing_status')}; measured={billing.get('measured_rows')}; pending={billing.get('pending_rows')}",
            "results/provider_billing_evidence/billing_summary.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_ai_scientist_smoke_current",
            "ready"
            if smoke.get("overall_status") == "blocked_by_provider_or_model_availability"
            and contains_all(combined_text, ["blocked_by_provider_or_model_availability", smoke_detail])
            else "fail",
            f"overall={smoke.get('overall_status')}; detail={smoke_detail}",
            "results/ai_scientist_v2_smoke/run_report.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_goal_package_counts_current",
            "ready"
            if goal_counts.get("fail") == 0
            and package_counts.get("fail") == 0
            and contains_all(
                combined_text,
                [
                    f"{goal_counts.get('ready')} ready",
                    f"{goal_counts.get('pending')} pending",
                    f"{package_counts.get('ready')} ready",
                    f"{package_counts.get('pending')} pending",
                ],
            )
            else "fail",
            (
                f"goal={goal_counts}; "
                f"package={package_counts}"
            ),
            "results/reproducibility/goal_completion_report.json; results/reproducibility/package_report.json; research/submission_checklist.md",
        ),
    ]
    return checks


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    checks = required_file_checks(root)
    combined_text = "\n".join(read_text(root / raw_path) for raw_path in TARGET_FILES.values())
    if all(check.status == "ready" for check in checks):
        checks.extend(stale_claim_checks(root, combined_text))
        checks.extend(forbidden_positive_checks(combined_text))
        checks.extend(evidence_alignment_checks(root, combined_text))

    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks internal review, rebuttal, and submission-checklist handoff artifacts "
            "against current repository evidence. A ready report means the handoff is current; "
            "it is not a final submission or acceptance claim."
        ),
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
        "# Submission Review Handoff Report",
        "",
        "Evidence boundary: this report checks internal review, rebuttal, and "
        "submission-checklist handoff artifacts against current repository evidence. "
        "It does not claim final submission readiness.",
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
    parser = argparse.ArgumentParser(description="Check PaperToSkill submission-review handoff artifacts.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "submission_review_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "submission_review_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any submission-review check fails.")
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
