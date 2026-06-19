#!/usr/bin/env python
"""Build a local closure queue for pending external PaperToSkill evidence."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_REPORTS = {
    "goal_completion": "results/reproducibility/goal_completion_report.json",
    "ai_scientist_smoke": "results/ai_scientist_v2_smoke/run_report.json",
    "ai_scientist_live_run_handoff": "results/ai_scientist_v2_live_run_handoff/handoff.json",
    "deepseek_handoff": "results/deepseek_followup_handoff/handoff.json",
    "model_ablation_evaluation": "results/model_ablation_prompts/v0/evaluation.json",
    "human_fidelity_summary": "results/human_fidelity_packets/annotation_summary.json",
    "provider_billing_summary": "results/provider_billing_evidence/billing_summary.json",
    "aaai_package_report": "results/reproducibility/aaai_package_report.json",
    "submission_review_report": "results/reproducibility/submission_review_report.json",
}

GOAL_REQUIREMENT_TO_ITEM = {
    "ai_scientist_v2_live_llm_smoke_complete": "ai_scientist_v2_smoke_completion",
    "ai_scientist_v2_live_llm_run_complete": "ai_scientist_v2_full_live_run",
    "provider_billing_evidence_complete": "provider_billing_success_per_dollar",
    "aaai_final_submission_ready": "aaai_submission_decision",
    "deepseek_followup_response_complete": "deepseek_followup_responses",
    "model_ablation_evaluation_complete": "deepseek_followup_responses",
    "human_fidelity_annotation_complete": "human_fidelity_annotation",
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


@dataclass
class QueueItem:
    id: str
    status: str
    goal_requirements: list[str]
    detail: str
    evidence: str
    next_action: str
    next_commands: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "goal_requirements": self.goal_requirements,
            "detail": self.detail,
            "evidence": self.evidence,
            "next_action": self.next_action,
            "next_commands": self.next_commands,
        }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def goal_pending_requirements(goal: dict[str, Any]) -> list[str]:
    pending = []
    for check in goal.get("checks", []):
        check_id = str(check.get("id", ""))
        if check.get("status") == "pending" and check_id != "active_goal_complete":
            pending.append(check_id)
    return sorted(pending)


def item_status_counts(items: list[QueueItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.status] = counts.get(item.status, 0) + 1
    return counts


def check_status_counts(checks: list[Check]) -> dict[str, int]:
    counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def build_items(reports: dict[str, dict[str, Any]]) -> list[QueueItem]:
    smoke = reports["ai_scientist_smoke"]
    live_handoff = reports["ai_scientist_live_run_handoff"]
    deepseek = reports["deepseek_handoff"]
    model_eval = reports["model_ablation_evaluation"]
    human = reports["human_fidelity_summary"]
    billing = reports["provider_billing_summary"]
    aaai = reports["aaai_package_report"]
    review = reports["submission_review_report"]

    smoke_complete = smoke.get("overall_status") == "complete"
    live_status = str(live_handoff.get("overall_status", ""))
    deepseek_status = str(deepseek.get("overall_status", ""))
    model_summary = model_eval.get("summary", {})
    human_status = str(human.get("annotation_status", ""))
    billing_status = str(billing.get("billing_status", ""))
    aaai_ready = aaai.get("overall_status") == "ready"
    review_ready = review.get("overall_status") == "ready"

    return [
        QueueItem(
            id="ai_scientist_v2_smoke_completion",
            status="complete" if smoke_complete else "pending_provider",
            goal_requirements=["ai_scientist_v2_live_llm_smoke_complete"],
            detail=(
                f"overall={smoke.get('overall_status')}; "
                f"counts={smoke.get('status_counts')}; "
                f"attempted={','.join(str(row.get('model', '')) for row in smoke.get('attempted_models', []))}"
            ),
            evidence=REQUIRED_REPORTS["ai_scientist_smoke"],
            next_action="Provider must return a smoke response satisfying all marker checks.",
            next_commands=[
                "# Claude-family credential profile",
                "python scripts\\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 30 --max-tokens 128 `",
                "  --model-alias claude-opus-4-8 `",
                "  --model-alias claude-opus-4.8 `",
                "  --model-alias claude-opus-4-7 `",
                "  --model-alias claude-opus-4-6",
                "# GPT-family credential profile",
                "python scripts\\run_ai_scientist_v2_smoke.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 `",
                "  --model-alias gpt-5.5 `",
                "  --model-alias gpt-5.4",
            ],
        ),
        QueueItem(
            id="ai_scientist_v2_full_live_run",
            status="complete" if live_status == "complete" else ("ready_to_run" if live_status == "ready_to_run" else "blocked_by_smoke"),
            goal_requirements=["ai_scientist_v2_live_llm_run_complete"],
            detail=f"handoff={live_status}; completion_dirs={len(live_handoff.get('completion_dirs', []))}",
            evidence=REQUIRED_REPORTS["ai_scientist_live_run_handoff"],
            next_action="Run the bounded full AI-Scientist-v2 task only after the smoke report is complete.",
            next_commands=live_handoff.get("next_commands", []),
        ),
        QueueItem(
            id="deepseek_followup_responses",
            status=(
                "complete"
                if int(model_summary.get("pending_rows", 0)) == 0 and deepseek_status == "responses_present"
                else deepseek_status or "pending"
            ),
            goal_requirements=["deepseek_followup_response_complete", "model_ablation_evaluation_complete"],
            detail=(
                f"handoff={deepseek_status}; scored_rows={model_summary.get('scored_rows')}; "
                f"pending_rows={model_summary.get('pending_rows')}"
            ),
            evidence=f"{REQUIRED_REPORTS['deepseek_handoff']}; {REQUIRED_REPORTS['model_ablation_evaluation']}",
            next_action="User supplies DeepSeek alias/env vars, then run and score the two DeepSeek response rows.",
            next_commands=deepseek.get("next_commands", []),
        ),
        QueueItem(
            id="human_fidelity_annotation",
            status="complete" if human_status == "complete" else "pending_reviewers",
            goal_requirements=["human_fidelity_annotation_complete"],
            detail=f"status={human_status}; scored_rows={human.get('scored_rows')}; pending_rows={human.get('pending_rows')}",
            evidence=REQUIRED_REPORTS["human_fidelity_summary"],
            next_action="Independent reviewers fill the annotation template, then rerun the strict summarizer.",
            next_commands=["python scripts\\summarize_human_fidelity_annotations.py --strict"],
        ),
        QueueItem(
            id="provider_billing_success_per_dollar",
            status="complete" if billing_status == "complete" and not billing.get("errors") else "pending_billing_rows",
            goal_requirements=["provider_billing_evidence_complete"],
            detail=(
                f"status={billing_status}; measured_rows={billing.get('measured_rows')}; "
                f"pending_rows={billing.get('pending_rows')}; errors={len(billing.get('errors', []))}"
            ),
            evidence=REQUIRED_REPORTS["provider_billing_summary"],
            next_action="Fill usage-export or invoice rows, then rerun the strict billing summary.",
            next_commands=["python scripts\\summarize_provider_billing_evidence.py --strict"],
        ),
        QueueItem(
            id="aaai_submission_decision",
            status="complete" if aaai_ready and review_ready and not goal_pending_requirements(reports["goal_completion"]) else "pending_decision",
            goal_requirements=["aaai_final_submission_ready"],
            detail=f"aaai_package={aaai.get('overall_status')}; submission_review={review.get('overall_status')}",
            evidence=f"{REQUIRED_REPORTS['aaai_package_report']}; {REQUIRED_REPORTS['submission_review_report']}; research/submission_checklist.md",
            next_action="Choose whether to submit as a deterministic/offline system paper or wait for the external evidence rows.",
            next_commands=[
                "python scripts\\check_submission_review.py --strict",
                "python scripts\\check_goal_completion.py --strict",
                "python scripts\\check_reproducibility_package.py --strict",
            ],
        ),
    ]


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    missing_reports = [
        report_id
        for report_id, raw_path in REQUIRED_REPORTS.items()
        if not resolve(root, raw_path).exists()
    ]
    reports = {
        report_id: load_json(resolve(root, raw_path))
        for report_id, raw_path in REQUIRED_REPORTS.items()
    }
    items = build_items(reports)
    pending_goal = goal_pending_requirements(reports["goal_completion"])
    covered = sorted({requirement for item in items for requirement in item.goal_requirements})
    uncovered = sorted(
        requirement
        for requirement in pending_goal
        if requirement not in GOAL_REQUIREMENT_TO_ITEM or requirement not in covered
    )
    wrong_item = sorted(
        requirement
        for requirement, item_id in GOAL_REQUIREMENT_TO_ITEM.items()
        if requirement in pending_goal and item_id not in {item.id for item in items}
    )

    checks = [
        Check(
            "external_closure_required_reports_present",
            "ready" if not missing_reports else "fail",
            "present" if not missing_reports else "missing=" + ",".join(missing_reports),
            "; ".join(REQUIRED_REPORTS.values()),
        ),
        Check(
            "external_closure_goal_pending_items_covered",
            "ready" if not uncovered and not wrong_item else "fail",
            (
                f"pending_goal_requirements={len(pending_goal)}; covered={len([item for item in covered if item in pending_goal])}"
                if not uncovered and not wrong_item
                else "uncovered=" + ",".join(uncovered + wrong_item)
            ),
            REQUIRED_REPORTS["goal_completion"],
        ),
        Check(
            "external_closure_queue_items_declared",
            "ready" if len(items) == 6 else "fail",
            f"items={len(items)}",
            "results/external_evidence_closure/closure.json",
        ),
    ]
    counts = check_status_counts(checks)
    item_counts = item_status_counts(items)
    if counts.get("fail", 0):
        overall = "fail"
    elif item_counts.get("complete", 0) == len(items):
        overall = "complete"
    else:
        overall = "pending_external_evidence"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local closure queue for external evidence only. Pending items are "
            "remaining work or external decisions, not local package failures."
        ),
        "overall_status": overall,
        "status_counts": counts,
        "item_status_counts": item_counts,
        "pending_goal_requirements": pending_goal,
        "checks": [check.as_dict() for check in checks],
        "items": [item.as_dict() for item in items],
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
    item_rows = [
        [
            item["id"],
            item["status"],
            ",".join(item["goal_requirements"]),
            item["detail"],
            item["next_action"],
        ]
        for item in report["items"]
    ]
    check_rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines = [
        "# External Evidence Closure Queue",
        "",
        "Evidence boundary: this is a local closure queue. It does not collect "
        "DeepSeek responses, human annotations, provider bills, AI-Scientist-v2 "
        "live-run artifacts, or final submission approval.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Queue item statuses: {report['item_status_counts']}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Pending checks: {report['status_counts'].get('pending', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "## Queue Items",
        "",
        markdown_table(item_rows, ["Item", "Status", "Goal Requirements", "Detail", "Next Action"]),
        "",
        "## Checks",
        "",
        markdown_table(check_rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the PaperToSkill external evidence closure queue.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "external_evidence_closure" / "closure.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "external_evidence_closure" / "closure.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if closure queue checks fail.")
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
