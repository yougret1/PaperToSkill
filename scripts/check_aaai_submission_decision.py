#!/usr/bin/env python
"""Build an AAAI submission-decision preflight report for PaperToSkill."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_REPORTS = {
    "aaai_package": "results/reproducibility/aaai_package_report.json",
    "paper_claims": "results/reproducibility/paper_claim_report.json",
    "paper_tables": "results/reproducibility/paper_table_report.json",
    "usage_examples": "results/reproducibility/usage_example_report.json",
    "submission_review": "results/reproducibility/submission_review_report.json",
    "goal_completion": "results/reproducibility/goal_completion_report.json",
    "reproducibility_package": "results/reproducibility/package_report.json",
    "external_packets": "results/external_evidence_packets/packets.json",
    "ai_scientist_smoke": "results/ai_scientist_v2_smoke/run_report.json",
    "ai_scientist_live_handoff": "results/ai_scientist_v2_live_run_handoff/handoff.json",
    "deepseek_handoff": "results/deepseek_followup_handoff/handoff.json",
    "model_ablation_evaluation": "results/model_ablation_prompts/v0/evaluation.json",
    "human_fidelity": "results/human_fidelity_packets/annotation_summary.json",
    "provider_billing": "results/provider_billing_evidence/billing_summary.json",
}

TEXT_INPUTS = {
    "submission_checklist": "research/submission_checklist.md",
    "review_report": "research/review_report.md",
    "rebuttal_bank": "research/rebuttal_bank.md",
    "aaai_tex": "paper/aaai/papertoskill_aaai2027.tex",
}

LOCAL_READY_REPORTS = {
    "aaai_package",
    "paper_claims",
    "paper_tables",
    "usage_examples",
    "submission_review",
}

EXPECTED_PENDING_REQUIREMENTS = {
    "aaai_final_submission_ready",
    "ai_scientist_v2_live_llm_run_complete",
    "ai_scientist_v2_live_llm_smoke_complete",
    "deepseek_followup_response_complete",
    "human_fidelity_annotation_complete",
    "model_ablation_evaluation_complete",
    "provider_billing_evidence_complete",
}

DECISION_RECORD = "research/aaai_submission_decision.md"

OPTION_IDS = {
    "submit_now_deterministic_offline",
    "wait_for_external_evidence",
}

SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")


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


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def status_counts(checks: list[Check]) -> dict[str, int]:
    counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def pending_goal_requirements(goal: dict[str, Any]) -> set[str]:
    return {
        str(check.get("id", ""))
        for check in goal.get("checks", [])
        if check.get("status") == "pending" and check.get("id") != "active_goal_complete"
    }


def failed_checks(report: dict[str, Any]) -> list[str]:
    return [
        str(check.get("id", ""))
        for check in report.get("checks", [])
        if check.get("status") == "fail"
    ]


def contains_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def parse_decision_record(root: Path) -> dict[str, Any]:
    path = resolve(root, DECISION_RECORD)
    if not path.exists():
        return {
            "path": DECISION_RECORD,
            "status": "missing",
            "selected_option": None,
            "issues": ["decision record is not present"],
        }

    text = read_text(path)
    selected_match = re.search(r"selected option\s*:\s*([A-Za-z0-9_-]+)", text, flags=re.IGNORECASE)
    selected_option = selected_match.group(1).strip() if selected_match else None
    issues = []
    if selected_option not in OPTION_IDS:
        issues.append("selected option must be submit_now_deterministic_offline or wait_for_external_evidence")
    for label in ["decision owner", "decision date", "claim boundary", "evidence policy"]:
        if not re.search(rf"{re.escape(label)}\s*:\s*\S+", text, flags=re.IGNORECASE):
            issues.append(f"missing {label}")
    return {
        "path": DECISION_RECORD,
        "status": "valid" if not issues else "invalid",
        "selected_option": selected_option,
        "issues": issues,
    }


def build_options(reports: dict[str, dict[str, Any]], combined_text: str) -> list[dict[str, Any]]:
    local_ready = all(reports[key].get("overall_status") == "ready" for key in LOCAL_READY_REPORTS)
    pending = pending_goal_requirements(reports["goal_completion"])
    expected_pending_present = EXPECTED_PENDING_REQUIREMENTS <= pending
    boundary_ready = contains_all(
        combined_text,
        [
            "deterministic/offline",
            "do not claim",
            "human validation",
            "provider billing",
            "DeepSeek",
            "AI-Scientist-v2 LLM-client smoke",
        ],
    )

    submit_status = "available_for_human_decision" if local_ready and boundary_ready else "blocked_by_local_gate"
    wait_status = "available_for_human_decision" if expected_pending_present else "blocked_by_missing_pending_map"

    return [
        {
            "id": "submit_now_deterministic_offline",
            "status": submit_status,
            "decision_owner": "Research Lead",
            "when_defensible": (
                "Use only if the human lead accepts a bounded deterministic/offline system paper "
                "whose claims are scoped to local gates, saved-response scoring, and handoff readiness."
            ),
            "required_claim_scope": [
                "Paper-note-to-skill conversion over curated and bounded extracted-text cases.",
                "Deterministic local gates for coverage, source grounding, transfer readiness, and table/claim consistency.",
                "Explicit limitations for human fidelity, provider billing, DeepSeek, and AI-Scientist-v2 live-run evidence.",
            ],
            "must_not_claim": [
                "AAAI acceptance or submission-final status.",
                "Human-validated semantic fidelity.",
                "Completed provider billing or success per dollar.",
                "DeepSeek model-ablation completion.",
                "Completed AI-Scientist-v2 LLM-client smoke or full live/BFTS run.",
            ],
            "validation_commands": [
                "python scripts\\check_aaai_package.py --strict",
                "python scripts\\check_paper_claims.py --strict",
                "python scripts\\check_paper_tables.py --strict",
                "python scripts\\check_usage_examples.py --strict",
                "python scripts\\check_submission_review.py --strict",
                "python scripts\\check_aaai_submission_decision.py --strict",
            ],
        },
        {
            "id": "wait_for_external_evidence",
            "status": wait_status,
            "decision_owner": "Research Lead",
            "when_defensible": (
                "Use if the intended paper claims require semantic fidelity, live AI-Scientist-v2 execution, "
                "DeepSeek comparison, or realized provider economics."
            ),
            "required_claim_scope": [
                "Complete AI-Scientist-v2 smoke before any full live/BFTS run claim.",
                "Collect and score DeepSeek follow-up rows.",
                "Complete independent human-fidelity annotations.",
                "Fill provider billing rows before success-per-dollar claims.",
            ],
            "must_not_claim": [
                "That the local preflight itself completes any external evidence.",
                "That saved-response output-contract scoring proves live task success.",
            ],
            "validation_commands": [
                "python scripts\\check_external_evidence_packets.py --strict",
                "python scripts\\check_goal_completion.py --strict",
                "python scripts\\check_reproducibility_package.py --strict",
            ],
        },
    ]


def required_input_checks(root: Path) -> list[Check]:
    checks = []
    for check_id, raw_path in {**REQUIRED_REPORTS, **TEXT_INPUTS}.items():
        path = resolve(root, raw_path)
        checks.append(
            Check(
                f"aaai_submission_decision_input_{check_id}",
                "ready" if path.exists() else "fail",
                "present" if path.exists() else "missing",
                raw_path,
            )
        )
    return checks


def local_gate_check(reports: dict[str, dict[str, Any]]) -> Check:
    not_ready = [
        report_id
        for report_id in LOCAL_READY_REPORTS
        if reports[report_id].get("overall_status") != "ready"
    ]
    return Check(
        "aaai_submission_decision_local_gates_ready",
        "ready" if not not_ready else "fail",
        "local submission gates ready" if not not_ready else "not_ready=" + ",".join(sorted(not_ready)),
        "; ".join(REQUIRED_REPORTS[key] for key in sorted(LOCAL_READY_REPORTS)),
    )


def pending_state_check(reports: dict[str, dict[str, Any]]) -> Check:
    goal = reports["goal_completion"]
    package = reports["reproducibility_package"]
    pending = pending_goal_requirements(goal)
    missing = sorted(EXPECTED_PENDING_REQUIREMENTS - pending)
    ready = (
        goal.get("overall_status") == "not_complete_pending_external_evidence"
        and package.get("overall_status") == "ready_with_pending_external_evidence"
        and not missing
    )
    return Check(
        "aaai_submission_decision_pending_evidence_state_current",
        "ready" if ready else "fail",
        (
            f"goal={goal.get('overall_status')}; package={package.get('overall_status')}; "
            f"pending={len(pending)}"
            if ready
            else "missing_pending=" + ",".join(missing)
        ),
        f"{REQUIRED_REPORTS['goal_completion']}; {REQUIRED_REPORTS['reproducibility_package']}",
    )


def external_packet_check(reports: dict[str, dict[str, Any]]) -> Check:
    packets = reports["external_packets"]
    packet = next(
        (item for item in packets.get("packets", []) if item.get("id") == "aaai_submission_decision"),
        None,
    )
    failed = failed_checks(packets)
    ready = (
        packets.get("overall_status") == "ready"
        and packet is not None
        and not failed
        and packet.get("completion_criteria")
        and packet.get("run_commands")
    )
    detail = (
        f"packet_status={packet.get('status')}; criteria={len(packet.get('completion_criteria', []))}"
        if packet
        else "aaai_submission_decision packet missing"
    )
    return Check(
        "aaai_submission_decision_external_packet_ready",
        "ready" if ready else "fail",
        detail if ready else detail + f"; failed={len(failed)}",
        REQUIRED_REPORTS["external_packets"],
    )


def boundary_check(combined_text: str) -> Check:
    terms = [
        "Submit now as deterministic/offline system paper",
        "Wait for stronger evidence",
        "Do not claim robust arbitrary-PDF automation",
        "Do not claim live task success",
        "Do not claim human validation",
        "Do not claim provider billing",
        "Do not claim DeepSeek completion",
        "Do not claim AI-Scientist-v2 LLM-client smoke completion",
    ]
    missing = [term for term in terms if term.lower() not in combined_text.lower()]
    return Check(
        "aaai_submission_decision_boundaries_declared",
        "ready" if not missing else "fail",
        "submission options and non-negotiable boundaries declared" if not missing else "missing=" + ",".join(missing),
        "research/submission_checklist.md; research/review_report.md; paper/aaai/papertoskill_aaai2027.tex",
    )


def decision_record_check(decision_record: dict[str, Any]) -> Check:
    if decision_record["status"] == "valid":
        return Check(
            "aaai_submission_decision_human_decision_recorded",
            "ready",
            f"selected_option={decision_record['selected_option']}",
            DECISION_RECORD,
        )
    if decision_record["status"] == "missing":
        return Check(
            "aaai_submission_decision_human_decision_recorded",
            "pending",
            "no human decision record present",
            DECISION_RECORD,
        )
    return Check(
        "aaai_submission_decision_human_decision_recorded",
        "fail",
        "; ".join(decision_record["issues"]),
        DECISION_RECORD,
    )


def no_secret_check(serialized_report: str) -> Check:
    secret_like = sorted(set(SECRET_PATTERN.findall(serialized_report)))
    return Check(
        "aaai_submission_decision_no_secret_material",
        "ready" if not secret_like else "fail",
        "no raw API-key-like strings found" if not secret_like else "matches=" + ",".join(secret_like[:3]),
        "results/aaai_submission_decision/decision.json",
    )


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    reports = {
        report_id: load_json(resolve(root, raw_path))
        for report_id, raw_path in REQUIRED_REPORTS.items()
    }
    combined_text = "\n".join(read_text(resolve(root, raw_path)) for raw_path in TEXT_INPUTS.values())
    decision_record = parse_decision_record(root)
    options = build_options(reports, combined_text)

    checks = required_input_checks(root)
    if all(check.status == "ready" for check in checks):
        option_ids = {option["id"] for option in options}
        checks.extend(
            [
                local_gate_check(reports),
                pending_state_check(reports),
                external_packet_check(reports),
                boundary_check(combined_text),
                Check(
                    "aaai_submission_decision_options_declared",
                    "ready" if option_ids == OPTION_IDS else "fail",
                    "options=" + ",".join(sorted(option_ids)),
                    "results/aaai_submission_decision/decision.json",
                ),
                Check(
                    "aaai_submission_decision_no_default_selection",
                    "ready" if decision_record.get("selected_option") is None else "ready",
                    (
                        "no option selected by the preflight"
                        if decision_record.get("selected_option") is None
                        else f"human-selected option={decision_record.get('selected_option')}"
                    ),
                    DECISION_RECORD,
                ),
                decision_record_check(decision_record),
            ]
        )

    report_without_secret_check = {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local AAAI submission-decision preflight. It distinguishes available submission "
            "paths and required boundaries, but it does not make the human submission decision "
            "or complete pending external evidence."
        ),
        "decision_status": "recorded" if decision_record["status"] == "valid" else "pending_user_decision",
        "selected_option": decision_record.get("selected_option") if decision_record["status"] == "valid" else None,
        "decision_record": decision_record,
        "options": options,
        "checks": [check.as_dict() for check in checks],
    }
    checks.append(no_secret_check(json.dumps(report_without_secret_check, indent=2)))
    counts = status_counts(checks)
    if counts.get("fail", 0):
        overall = "fail"
    elif counts.get("pending", 0):
        overall = "pending_human_decision"
    else:
        overall = "ready"

    return {
        **report_without_secret_check,
        "overall_status": overall,
        "status_counts": counts,
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


def markdown_list(items: list[str]) -> list[str]:
    if not items:
        return ["- n/a"]
    return [f"- {item}" for item in items]


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    counts = report["status_counts"]
    lines = [
        "# AAAI Submission Decision Preflight",
        "",
        "Evidence boundary: this report distinguishes submission choices, but it "
        "does not submit the paper, accept a claim scope, or complete pending "
        "external evidence.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Decision status: {report['decision_status']}",
        f"- Selected option: {report.get('selected_option') or 'n/a'}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Pending checks: {counts.get('pending', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Options",
        "",
    ]
    for option in report["options"]:
        lines.extend(
            [
                f"### {option['id']}",
                "",
                f"- Status: {option['status']}",
                f"- Decision owner: {option['decision_owner']}",
                f"- When defensible: {option['when_defensible']}",
                "",
                "Required claim scope:",
                "",
                *markdown_list(option["required_claim_scope"]),
                "",
                "Must not claim:",
                "",
                *markdown_list(option["must_not_claim"]),
                "",
                "Validation commands:",
                "",
                "```powershell",
                *option["validation_commands"],
                "```",
                "",
            ]
        )

    check_rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines.extend(
        [
            "## Decision Record Template",
            "",
            "Create `research/aaai_submission_decision.md` only after the human lead makes the decision:",
            "",
            "```markdown",
            "# AAAI Submission Decision",
            "",
            "Selected option: submit_now_deterministic_offline",
            "Decision owner: <name or role>",
            "Decision date: YYYY-MM-DD",
            "Claim boundary: <accepted paper claim scope>",
            "Evidence policy: <submit now with limitations, or wait for named evidence>",
            "```",
            "",
            "## Checks",
            "",
            markdown_table(check_rows, ["Check", "Status", "Detail", "Evidence"]),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build an AAAI submission-decision preflight report.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "aaai_submission_decision" / "decision.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "aaai_submission_decision" / "decision.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if preflight checks fail.")
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
