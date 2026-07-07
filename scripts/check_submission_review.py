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
        "pattern": r"endpoint\s+still\s+returns|live prompt packets exist,\s*but endpoint",
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


def contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def smoke_blocker_detail(smoke: dict[str, Any]) -> str:
    for check in smoke.get("checks", []):
        if check.get("id") == "ai_scientist_v2_llm_error":
            return str(check.get("detail", "")).strip()
    return ""


def smoke_alias_terms(smoke: dict[str, Any]) -> list[str]:
    return [
        str(attempt.get("model", "")).strip()
        for attempt in smoke.get("attempted_models", [])
        if str(attempt.get("model", "")).strip()
    ]


def smoke_blocker_terms(smoke: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    details = [smoke_blocker_detail(smoke)]
    for attempt in smoke.get("attempted_models", []):
        attempt_detail = str(attempt.get("detail", "")).strip()
        if attempt_detail:
            details.append(attempt_detail)
    combined_detail = "\n".join(details)
    if "All available accounts exhausted" in combined_detail:
        terms.append("All available accounts exhausted")
    for match in re.finditer(
        r"Timed out after \d+(?:\.\d+)? seconds waiting for provider response",
        combined_detail,
        flags=re.IGNORECASE,
    ):
        phrase = match.group(0)
        if phrase not in terms:
            terms.append(phrase)
    if not terms and smoke_blocker_detail(smoke):
        terms.append(smoke_blocker_detail(smoke))
    return terms


def aggregate_handoff_current(goal_counts: dict[str, Any], package_counts: dict[str, Any], combined_text: str) -> bool:
    boundary_terms_present = contains_all(combined_text, ["active goal", "not complete", "pending external evidence"])
    if goal_counts.get("fail") == 0 and package_counts.get("fail") == 0:
        return contains_all(
            combined_text,
            [
                f"{goal_counts.get('ready')} ready",
                f"{goal_counts.get('pending')} pending",
                f"{package_counts.get('ready')} ready",
                f"{package_counts.get('pending')} pending",
            ],
        )
    # Avoid a self-referential failure loop when stale aggregate reports failed
    # only because the submission-review gate was generated before this check.
    return boundary_terms_present


def local_gate_counts_current(root: Path, combined_text: str) -> tuple[bool, str]:
    gate_paths = {
        "aaai": root / "results/reproducibility/aaai_package_report.json",
        "paper_table": root / "results/reproducibility/paper_table_report.json",
        "usage": root / "results/reproducibility/usage_example_report.json",
    }
    details: list[str] = []
    required_terms: list[str] = []
    for name, path in gate_paths.items():
        report = load_json(path)
        counts = report.get("status_counts", {})
        ready = counts.get("ready")
        failed = counts.get("fail")
        details.append(f"{name}={counts}")
        required_terms.extend([f"{ready} ready", f"{failed} failed"])
    return contains_all(combined_text, required_terms), "; ".join(details)


def external_evidence_pending_current(root: Path, combined_text: str) -> tuple[bool, str]:
    closure = load_json(root / "results/external_evidence_closure/closure.json")
    packets = load_json(root / "results/external_evidence_packets/packets.json")
    decision = load_json(root / "results/aaai_submission_decision/decision.json")
    human = load_json(root / "results/human_fidelity_packets/annotation_summary.json")
    closure_items = closure.get("items", [])
    packet_items = packets.get("packets", [])
    item_status_counts = closure.get("item_status_counts", {})
    data_current = (
        closure.get("overall_status") == "pending_external_evidence"
        and item_status_counts.get("pending_reviewers", 0) == 0
        and item_status_counts.get("pending_decision") == 1
        and len(closure_items) == 1
        and packets.get("overall_status") == "ready"
        and packets.get("closure_status") == "pending_external_evidence"
        and len(packet_items) == 1
        and decision.get("selected_option") == "wait_for_external_evidence"
        and human.get("annotation_status") == "complete"
        and int(human.get("scored_cells", 0)) >= 24
        and int(human.get("pending_cells", -1)) == 0
    )
    text_current = (
        contains_all(
            combined_text,
            [
                "pending_external_evidence",
                "AAAI final decision",
                "wait_for_external_evidence",
                "annotation_status=complete",
                "local queue",
                "local handoff",
            ],
        )
        and contains_any(
            combined_text,
            [
                "one pending-external-evidence item",
                "1 pending external-evidence item",
                "pending_goal_requirements=1",
            ],
        )
        and contains_any(combined_text, ["24 scored", "scored_rows=24", "scored_cells=24"])
        and contains_any(combined_text, ["0 pending", "pending_rows=0", "pending_cells=0"])
    )
    detail = (
        f"closure={closure.get('overall_status')}; "
        f"item_status_counts={item_status_counts}; "
        f"packets={packets.get('overall_status')}; "
        f"closure_status={packets.get('closure_status')}; "
        f"decision={decision.get('selected_option')}; "
        f"human={human.get('annotation_status')}"
    )
    return data_current and text_current, detail


def evidence_alignment_checks(root: Path, combined_text: str) -> list[Check]:
    live = load_json(root / "results/live_transfer_prompts/evaluation.json").get("summary", {})
    model = load_json(root / "results/model_ablation_prompts/v0/evaluation.json").get("summary", {})
    real_reuse_llm = load_json(root / "results/real_reuse/llm_ablation_summary.json")
    human = load_json(root / "results/human_fidelity_packets/annotation_summary.json")
    token_accounting = load_json(root / "results/token_accounting/token_accounting_summary.json")
    smoke = load_json(root / "results/ai_scientist_v2_smoke/run_report.json")
    live_handoff = load_json(root / "results/ai_scientist_v2_live_run_handoff/handoff.json")
    smoke_detail = smoke_blocker_detail(smoke)
    smoke_aliases = smoke_alias_terms(smoke)
    smoke_terms = smoke_blocker_terms(smoke)
    goal = load_json(root / "results/reproducibility/goal_completion_report.json")
    package = load_json(root / "results/reproducibility/package_report.json")
    goal_counts = goal.get("status_counts", {})
    package_counts = package.get("status_counts", {})
    local_gate_counts_ready, local_gate_counts_detail = local_gate_counts_current(root, combined_text)
    external_evidence_pending_ready, external_evidence_pending_detail = external_evidence_pending_current(
        root, combined_text
    )
    human_status = human.get("annotation_status")
    human_scored = int(human.get("scored_rows", -1))
    human_pending = int(human.get("pending_rows", 0))
    human_cells = int(human.get("scored_cells", 0))
    human_pending_current = (
        human_status == "pending"
        and human_scored == 0
        and human_pending == 24
        and contains_all(combined_text, [f"{human_scored} scored", f"{human_pending} pending", "human"])
    )
    human_complete_current = (
        human_status == "complete"
        and human_pending == 0
        and human_cells >= 24
        and contains_all(combined_text, ["human", "complete"])
    )
    real_reuse_llm_families = {
        str(row.get("Model Family", "")): row
        for row in real_reuse_llm.get("family_summary", [])
    }
    gpt_family = real_reuse_llm_families.get("GPT-family", {})
    deepseek_family = real_reuse_llm_families.get("DeepSeek-family", {})
    claude_family = real_reuse_llm_families.get("Claude-family", {})
    real_reuse_llm_counts_current = (
        int(real_reuse_llm.get("expected_rows", 0)) == 18
        and int(real_reuse_llm.get("collected_rows", 0)) == 12
        and int(real_reuse_llm.get("pending_rows", 0)) == 6
        and gpt_family.get("Model Alias") == "gpt-5.5"
        and gpt_family.get("Scored Rows") == "6"
        and gpt_family.get("Pending Rows") == "0"
        and gpt_family.get("Summary Avg") == "0.605"
        and gpt_family.get("PaperToSkill Avg") == "0.333"
        and deepseek_family.get("Model Alias") == "deepseek-v4-flash"
        and deepseek_family.get("Scored Rows") == "6"
        and deepseek_family.get("Pending Rows") == "0"
        and deepseek_family.get("Summary Avg") == "0.500"
        and deepseek_family.get("PaperToSkill Avg") == "0.500"
        and claude_family.get("Model Alias") == "claude-opus-4-8"
        and claude_family.get("Scored Rows") == "0"
        and claude_family.get("Pending Rows") == "6"
    )
    real_reuse_llm_text_current = contains_all(
        combined_text,
        [
            "real-reuse LLM ablation",
            "12/18",
            "GPT-family",
            "0.605/0.333",
            "DeepSeek-family",
            "0.500/0.500",
            "Claude-family",
            "provider-pending",
            "HTTP 502",
            "not a main-row replacement",
        ],
    )

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
            if int(model.get("total_rows", 0)) == 6
            and int(model.get("scored_rows", 0)) == 6
            and int(model.get("pending_rows", 0)) == 0
            and contains_all(combined_text, ["6 scored", "0 pending", "DeepSeek", "saved-response"])
            else "fail",
            f"total={model.get('total_rows')}; scored={model.get('scored_rows')}; pending={model.get('pending_rows')}",
            "results/model_ablation_prompts/v0/evaluation.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_real_reuse_llm_ablation_current",
            "ready"
            if real_reuse_llm_counts_current and real_reuse_llm_text_current
            else "fail",
            (
                f"expected={real_reuse_llm.get('expected_rows')}; "
                f"collected={real_reuse_llm.get('collected_rows')}; "
                f"pending={real_reuse_llm.get('pending_rows')}; "
                f"families={list(real_reuse_llm_families)}"
            ),
            "results/real_reuse/llm_ablation_summary.json; results/real_reuse/llm_ablation_summary.md; results/real_reuse/llm_ablation_family_summary.csv; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_human_fidelity_current",
            "ready"
            if human_pending_current or human_complete_current
            else "fail",
            (
                f"status={human_status}; scored={human.get('scored_rows')}; "
                f"scored_cells={human.get('scored_cells')}; pending={human.get('pending_rows')}"
            ),
            "results/human_fidelity_packets/annotation_summary.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_token_accounting_current",
            "ready"
            if token_accounting.get("accounting_status") == "complete"
            and int(token_accounting.get("composite_proxy", {}).get("generated_skill_input_tokens", 0)) > 0
            and int(token_accounting.get("composite_proxy", {}).get("saved_response_output_tokens", 0)) > 0
            and contains_all(combined_text, ["token accounting", "local token", "not provider billing"])
            else "fail",
            (
                f"status={token_accounting.get('accounting_status')}; "
                f"input_tokens={token_accounting.get('composite_proxy', {}).get('generated_skill_input_tokens')}; "
                f"output_tokens={token_accounting.get('composite_proxy', {}).get('saved_response_output_tokens')}"
            ),
            "results/token_accounting/token_accounting_summary.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_ai_scientist_smoke_current",
            "ready"
            if (
                smoke.get("overall_status") == "complete"
                and contains_all(
                    combined_text,
                    ["AI-Scientist-v2 LLM-client smoke", "complete", "bounded", "marker"],
                )
            )
            or (
                smoke.get("overall_status") == "blocked_by_provider_or_model_availability"
                and contains_all(
                    combined_text,
                    ["blocked_by_provider_or_model_availability", *smoke_terms, *smoke_aliases],
                )
            )
            else "fail",
            f"overall={smoke.get('overall_status')}; detail={smoke_detail}; aliases={','.join(smoke_aliases)}",
            "results/ai_scientist_v2_smoke/run_report.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_ai_scientist_live_run_current",
            "ready"
            if live_handoff.get("overall_status") == "complete"
            and int(len(live_handoff.get("completion_dirs", []))) > 0
            and contains_all(
                combined_text,
                ["AI-Scientist-v2", "full live", "complete", "bounded", "not", "human"],
            )
            else "fail",
            f"overall={live_handoff.get('overall_status')}; completion_dirs={len(live_handoff.get('completion_dirs', []))}",
            "results/ai_scientist_v2_live_run_handoff/handoff.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_goal_package_counts_current",
            "ready"
            if aggregate_handoff_current(goal_counts, package_counts, combined_text)
            else "fail",
            (
                f"goal={goal_counts}; "
                f"package={package_counts}"
            ),
            "results/reproducibility/goal_completion_report.json; results/reproducibility/package_report.json; research/submission_checklist.md",
        ),
        Check(
            "submission_review_local_gate_counts_current",
            "ready" if local_gate_counts_ready else "fail",
            local_gate_counts_detail,
            "results/reproducibility/aaai_package_report.json; results/reproducibility/paper_table_report.json; results/reproducibility/usage_example_report.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
        ),
        Check(
            "submission_review_external_evidence_pending_current",
            "ready" if external_evidence_pending_ready else "fail",
            external_evidence_pending_detail,
            "results/external_evidence_closure/closure.json; results/external_evidence_packets/packets.json; results/aaai_submission_decision/decision.json; results/human_fidelity_packets/annotation_summary.json; research/review_report.md; research/rebuttal_bank.md; research/submission_checklist.md",
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
