#!/usr/bin/env python
"""Build execution packets for pending external PaperToSkill evidence."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CLOSURE_REPORT = "results/external_evidence_closure/closure.json"
EXPECTED_PACKET_IDS = {
    "ai_scientist_v2_smoke_completion",
    "ai_scientist_v2_full_live_run",
    "deepseek_followup_responses",
    "human_fidelity_annotation",
    "provider_billing_success_per_dollar",
    "aaai_submission_decision",
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


PACKET_DETAILS: dict[str, dict[str, Any]] = {
    "ai_scientist_v2_smoke_completion": {
        "owner": "Execution/Ops",
        "use_validation_commands_as_run_commands": True,
        "inputs": [
            "scripts/run_openai_compatible_direct_probe.py",
            "results/openai_compatible_direct_probe/claude_family/run_report.json",
            "results/openai_compatible_direct_probe/gpt_family/run_report.json",
            "scripts/run_ai_scientist_v2_smoke.py",
            "results/ai_scientist_v2_smoke/run_report.json",
            "D:\\a_work\\gitee\\ai-scientist-v2",
        ],
        "setup": [
            "Set AI_SCIENTIST_OPENAI_BASE_URL locally.",
            "Set AI_SCIENTIST_OPENAI_API_KEY locally to the Claude-family or GPT-family credential profile.",
            "Set AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE=1 locally.",
            "For the GPT-family profile, map the GPT credential into AI_SCIENTIST_OPENAI_API_KEY for this smoke only.",
            "Run the direct OpenAI-compatible probe first. If it is still blocked, keep the wrapper smoke pending and escalate provider availability instead of treating the wrapper as failed.",
        ],
        "validation_commands": [
            "# Claude-family direct endpoint preflight",
            "python scripts\\run_openai_compatible_direct_probe.py --strict --require-complete --timeout-seconds 30 --max-tokens 128 `",
            "  --model-alias claude-opus-4-8 `",
            "  --model-alias claude-opus-4.8 `",
            "  --model-alias claude-opus-4-7 `",
            "  --model-alias claude-opus-4-6 `",
            "  --output-json results\\openai_compatible_direct_probe\\claude_family\\run_report.json `",
            "  --output-md results\\openai_compatible_direct_probe\\claude_family\\run_report.md `",
            "  --response-output results\\openai_compatible_direct_probe\\claude_family\\response.md",
            "# GPT-family direct endpoint preflight",
            "python scripts\\run_openai_compatible_direct_probe.py --strict --require-complete --timeout-seconds 60 --max-tokens 128 `",
            "  --model-alias gpt-5.5 `",
            "  --model-alias gpt-5.4 `",
            "  --output-json results\\openai_compatible_direct_probe\\gpt_family\\run_report.json `",
            "  --output-md results\\openai_compatible_direct_probe\\gpt_family\\run_report.md `",
            "  --response-output results\\openai_compatible_direct_probe\\gpt_family\\response.md",
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
            "python scripts\\check_goal_completion.py --strict",
        ],
        "completion_criteria": [
            "At least one direct OpenAI-compatible probe report is complete and has a saved response satisfying the marker contract.",
            "results/ai_scientist_v2_smoke/run_report.json reports overall_status=complete.",
            "results/ai_scientist_v2_smoke/response.md exists and satisfies all smoke marker checks.",
            "No provider/model availability timeout, exhausted-account, no-account, or upstream-forbidden status remains in the direct-probe or smoke reports.",
        ],
        "blocker_escalation": "Escalate if every configured Claude-family and GPT-family alias still times out or returns provider/account exhaustion, no available accounts, or upstream access forbidden in the direct probe or wrapper smoke.",
    },
    "ai_scientist_v2_full_live_run": {
        "owner": "Execution/Ops",
        "inputs": [
            "results/ai_scientist_v2_live_run_handoff/handoff.json",
            "ai_scientist_inputs/papertoskill_seed_ideas.json",
            "D:\\a_work\\gitee\\ai-scientist-v2\\launch_scientist_bfts.py",
        ],
        "setup": [
            "Complete the AI-Scientist-v2 smoke packet first.",
            "Use an isolated environment for ai-scientist-v2 dependencies before a long run.",
            "Keep writeup/review disabled for the bounded task unless the user changes scope.",
        ],
        "validation_commands": [
            "python scripts\\check_ai_scientist_v2_live_run_handoff.py --strict",
            "python scripts\\check_goal_completion.py --strict",
        ],
        "completion_criteria": [
            "The bounded full AI-Scientist-v2 run produces a completion directory under ai-scientist-v2/experiments.",
            "results/ai_scientist_v2_live_run_handoff/handoff.json reports overall_status=complete after rerun.",
            "Run logs record the command, environment profile, output directory, and failure or success state.",
        ],
        "blocker_escalation": "Do not start the full run while the smoke report is provider-blocked.",
    },
    "deepseek_followup_responses": {
        "owner": "Execution/Ops",
        "use_validation_commands_as_run_commands": True,
        "inputs": [
            "scripts/configure_deepseek_followup.py",
            "benchmarks/model_ablation_v0.json",
            "results/deepseek_followup_handoff/handoff.json",
            "results/model_ablation_prompts/v0/index.json",
        ],
        "setup": [
            "Use scripts/configure_deepseek_followup.py to replace the deepseek-to-be-filled alias with a real DeepSeek model alias without storing secrets.",
            "Set concrete DeepSeek base-url and API-key environment variable names locally.",
            "Rebuild prompt packets before running the DeepSeek slot.",
        ],
        "validation_commands": [
            "python scripts\\configure_deepseek_followup.py --model-alias <deepseek-model-alias> --auth-env DEEPSEEK_API_KEY --base-url-env DEEPSEEK_BASE_URL",
            "python scripts\\build_model_ablation_prompts.py --task benchmarks\\model_ablation_v0.json --output-dir results\\model_ablation_prompts\\v0",
            "python scripts\\run_model_ablation_prompts.py --task benchmarks\\model_ablation_v0.json --index results\\model_ablation_prompts\\v0\\index.json --output-json results\\model_ablation_prompts\\v0\\deepseek_run_report.json --output-md results\\model_ablation_prompts\\v0\\deepseek_run_report.md --model-id deepseek_followup_slot",
            "python scripts\\check_deepseek_followup.py --strict",
            "python scripts\\evaluate_model_ablation_responses.py --index results\\model_ablation_prompts\\v0\\index.json --output-json results\\model_ablation_prompts\\v0\\evaluation.json --output-md results\\model_ablation_prompts\\v0\\evaluation.md",
        ],
        "completion_criteria": [
            "DeepSeek slot is configured with a concrete non-placeholder alias and non-secret environment variable names.",
            "Both DeepSeek expected_response_path files exist.",
            "results/deepseek_followup_handoff/handoff.json reports responses_present.",
            "results/model_ablation_prompts/v0/evaluation.json reports pending_rows=0 and scored_rows=6.",
        ],
        "blocker_escalation": "Escalate if the user has not supplied a concrete DeepSeek endpoint and model alias.",
    },
    "human_fidelity_annotation": {
        "owner": "Human reviewers",
        "inputs": [
            "results/human_fidelity_packets/annotation_guide.md",
            "results/human_fidelity_packets/annotation_template.csv",
            "results/human_fidelity_packets/*_human_fidelity_packet.md",
        ],
        "setup": [
            "Send the packet files and annotation guide to independent reviewers.",
            "Keep blank rows blank; do not convert missing review rows into zero scores.",
            "Collect reviewer-filled rows in the existing annotation_template.csv schema.",
        ],
        "validation_commands": [
            "python scripts\\summarize_human_fidelity_annotations.py --strict",
            "python scripts\\check_goal_completion.py --strict",
        ],
        "completion_criteria": [
            "results/human_fidelity_packets/annotation_summary.json reports annotation_status=complete.",
            "All 24 paper-by-criterion rows are scored with no validation errors.",
            "Reviewer notes and confidence fields are preserved for audit.",
        ],
        "blocker_escalation": "Escalate if independent reviewers are unavailable or scoring criteria are ambiguous.",
    },
    "provider_billing_success_per_dollar": {
        "owner": "Execution/Ops",
        "inputs": [
            "benchmarks/provider_billing_evidence_v0.json",
            "results/provider_billing_evidence/billing_template.csv",
            "results/provider_billing_evidence/billing_summary.json",
        ],
        "setup": [
            "Export real provider usage or invoice rows for every measured model/provider row.",
            "Fill billing_template.csv without adding raw API keys or secrets.",
            "Keep local token proxies separate from realized provider bills.",
        ],
        "validation_commands": [
            "python scripts\\summarize_provider_billing_evidence.py --strict",
            "python scripts\\check_goal_completion.py --strict",
        ],
        "completion_criteria": [
            "results/provider_billing_evidence/billing_summary.json reports billing_status=complete.",
            "All 6 billing rows are measured and validation errors are empty.",
            "Success-per-dollar can be computed from real billed USD rather than local token proxies.",
        ],
        "blocker_escalation": "Escalate if the provider cannot export usage, invoices, or per-run billing rows.",
    },
    "aaai_submission_decision": {
        "owner": "Research Lead",
        "use_validation_commands_as_run_commands": True,
        "inputs": [
            "scripts/generate_aaai_submission_decision.py",
            "paper/aaai/papertoskill_aaai2027.tex",
            "results/reproducibility/aaai_package_report.json",
            "results/reproducibility/submission_review_report.json",
            "results/aaai_submission_decision/decision.json",
            "research/submission_checklist.md",
        ],
        "setup": [
            "Choose whether to submit as a deterministic/offline system paper or wait for external evidence.",
            "Use scripts/generate_aaai_submission_decision.py after the human research lead selects an option; do not hand-write the record unless the helper is unavailable.",
            "If waiting, do not mark final submission ready until the chosen evidence rows are complete.",
            "If submitting a bounded paper, explicitly scope claims to validated local evidence.",
        ],
        "validation_commands": [
            "# Pre-decision local gates",
            "python scripts\\check_submission_review.py --strict",
            "python scripts\\check_aaai_package.py --strict",
            "python scripts\\check_paper_claims.py --strict",
            "python scripts\\check_paper_tables.py --strict",
            "python scripts\\check_usage_examples.py --strict",
            "python scripts\\check_aaai_submission_decision.py --strict",
            "# Select exactly one human decision record command",
            "python scripts\\generate_aaai_submission_decision.py --selected-option submit_now_deterministic_offline --decision-owner \"<name or role>\" --decision-date YYYY-MM-DD --claim-boundary \"<accepted bounded claim scope>\" --evidence-policy \"submit with explicit pending-evidence limitations\"",
            "python scripts\\generate_aaai_submission_decision.py --selected-option wait_for_external_evidence --decision-owner \"<name or role>\" --decision-date YYYY-MM-DD --claim-boundary \"<claims deferred until named evidence is complete>\" --evidence-policy \"wait for named external evidence rows\"",
            "# Final validation after the selected decision record exists",
            "python scripts\\check_aaai_submission_decision.py --strict",
            "python scripts\\check_goal_completion.py --strict",
            "python scripts\\check_reproducibility_package.py --strict",
        ],
        "completion_criteria": [
            "research/aaai_submission_decision.md exists and records the research lead's selected option, claim boundary, and evidence policy.",
            "scripts/check_aaai_submission_decision.py --strict validates the decision record and reports no failed checks.",
            "AAAI package, paper-claim, paper-table, and submission-review gates pass after the decision.",
            "The active-goal completion report no longer has aaai_final_submission_ready pending.",
        ],
        "blocker_escalation": "Escalate if evidence strength is insufficient for the intended AAAI claim scope.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def status_counts(checks: list[Check]) -> dict[str, int]:
    counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def commands_for_item(item: dict[str, Any], detail: dict[str, Any]) -> list[str]:
    if detail.get("use_validation_commands_as_run_commands"):
        return [str(command) for command in detail.get("validation_commands", []) if str(command).strip()]
    commands = [str(command) for command in item.get("next_commands", []) if str(command).strip()]
    for command in detail.get("validation_commands", []):
        if command not in commands:
            commands.append(command)
    return commands


def build_packets(closure: dict[str, Any]) -> list[dict[str, Any]]:
    packets = []
    for item in closure.get("items", []):
        item_id = str(item.get("id", ""))
        detail = PACKET_DETAILS.get(item_id, {})
        packets.append(
            {
                "id": item_id,
                "status": item.get("status", "pending"),
                "owner": detail.get("owner", "Research Lead"),
                "goal_requirements": item.get("goal_requirements", []),
                "source_closure_evidence": item.get("evidence", ""),
                "current_detail": item.get("detail", ""),
                "inputs": detail.get("inputs", []),
                "setup": detail.get("setup", []),
                "run_commands": commands_for_item(item, detail),
                "validation_commands": detail.get("validation_commands", []),
                "completion_criteria": detail.get("completion_criteria", []),
                "blocker_escalation": detail.get("blocker_escalation", ""),
                "evidence_boundary": (
                    "Execution packet only. This packet does not complete external evidence until "
                    "its completion criteria are satisfied by fresh artifacts."
                ),
            }
        )
    return packets


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    closure_path = resolve(root, CLOSURE_REPORT)
    closure = load_json(closure_path)
    packets = build_packets(closure)
    packet_ids = {packet["id"] for packet in packets}
    closure_ids = {str(item.get("id", "")) for item in closure.get("items", [])}
    serialized_packets = json.dumps(packets, indent=2)
    serialized_closure = json.dumps(closure, indent=2)

    missing_expected = sorted(EXPECTED_PACKET_IDS - packet_ids)
    extra_packets = sorted(packet_ids - EXPECTED_PACKET_IDS)
    missing_detail = sorted(packet_id for packet_id in packet_ids if packet_id not in PACKET_DETAILS)
    commandless = sorted(packet["id"] for packet in packets if not packet.get("run_commands"))
    no_validation = sorted(packet["id"] for packet in packets if not packet.get("validation_commands"))
    no_criteria = sorted(packet["id"] for packet in packets if not packet.get("completion_criteria"))
    no_boundary = sorted(packet["id"] for packet in packets if not packet.get("evidence_boundary"))
    secret_like = sorted(set(SECRET_PATTERN.findall(serialized_packets + "\n" + serialized_closure)))

    checks = [
        Check(
            "external_evidence_packets_closure_present",
            "ready" if closure_path.exists() else "fail",
            "present" if closure_path.exists() else "missing",
            CLOSURE_REPORT,
        ),
        Check(
            "external_evidence_packets_match_closure",
            "ready" if packet_ids == closure_ids == EXPECTED_PACKET_IDS else "fail",
            (
                f"packets={len(packet_ids)}; closure_items={len(closure_ids)}"
                if packet_ids == closure_ids == EXPECTED_PACKET_IDS
                else "missing=" + ",".join(missing_expected) + "; extra=" + ",".join(extra_packets)
            ),
            CLOSURE_REPORT,
        ),
        Check(
            "external_evidence_packets_have_details",
            "ready" if not missing_detail else "fail",
            "all packets have detail templates" if not missing_detail else "missing_detail=" + ",".join(missing_detail),
            "scripts/check_external_evidence_packets.py",
        ),
        Check(
            "external_evidence_packets_commands_declared",
            "ready" if not commandless and not no_validation else "fail",
            (
                "commands and validation commands declared"
                if not commandless and not no_validation
                else "commandless=" + ",".join(commandless) + "; no_validation=" + ",".join(no_validation)
            ),
            "results/external_evidence_packets/packets.json",
        ),
        Check(
            "external_evidence_packets_completion_criteria_declared",
            "ready" if not no_criteria else "fail",
            "completion criteria declared" if not no_criteria else "missing=" + ",".join(no_criteria),
            "results/external_evidence_packets/packets.json",
        ),
        Check(
            "external_evidence_packets_boundaries_declared",
            "ready" if not no_boundary else "fail",
            "evidence boundaries declared" if not no_boundary else "missing=" + ",".join(no_boundary),
            "results/external_evidence_packets/packets.json",
        ),
        Check(
            "external_evidence_packets_no_secret_material",
            "ready" if not secret_like else "fail",
            "no raw API-key-like strings found" if not secret_like else "matches=" + ",".join(secret_like[:3]),
            "results/external_evidence_packets/packets.json",
        ),
    ]
    counts = status_counts(checks)
    overall = "ready" if counts.get("fail", 0) == 0 else "fail"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local execution packets for remaining external evidence. They define inputs, commands, "
            "criteria, and escalation paths without collecting the evidence themselves."
        ),
        "overall_status": overall,
        "status_counts": counts,
        "closure_status": closure.get("overall_status"),
        "packets": packets,
        "checks": [check.as_dict() for check in checks],
    }


def markdown_list(items: list[str]) -> list[str]:
    if not items:
        return ["- n/a"]
    return [f"- {item}" for item in items]


def markdown_commands(commands: list[str]) -> list[str]:
    if not commands:
        return ["```powershell", "# n/a", "```"]
    return ["```powershell", *commands, "```"]


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    counts = report["status_counts"]
    lines = [
        "# External Evidence Execution Packets",
        "",
        "Evidence boundary: these packets define how to finish pending external "
        "evidence. They do not collect DeepSeek responses, human annotations, "
        "provider bills, AI-Scientist-v2 live-run artifacts, or final submission "
        "approval by themselves.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Closure status: {report.get('closure_status')}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Pending checks: {counts.get('pending', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
    ]
    for packet in report["packets"]:
        lines.extend(
            [
                f"## {packet['id']}",
                "",
                f"- Status: {packet['status']}",
                f"- Owner: {packet['owner']}",
                f"- Goal requirements: {', '.join(packet['goal_requirements'])}",
                f"- Source evidence: {packet['source_closure_evidence']}",
                f"- Current detail: {packet['current_detail']}",
                "",
                "### Inputs",
                "",
                *markdown_list(packet["inputs"]),
                "",
                "### Setup",
                "",
                *markdown_list(packet["setup"]),
                "",
                "### Commands",
                "",
                *markdown_commands(packet["run_commands"]),
                "",
                "### Completion Criteria",
                "",
                *markdown_list(packet["completion_criteria"]),
                "",
                "### Escalation",
                "",
                packet["blocker_escalation"],
                "",
                "### Boundary",
                "",
                packet["evidence_boundary"],
                "",
            ]
        )

    check_rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines.extend(["## Checks", "", markdown_table(check_rows, ["Check", "Status", "Detail", "Evidence"]), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


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


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build external-evidence execution packets.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "external_evidence_packets" / "packets.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "external_evidence_packets" / "packets.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if packet checks fail.")
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
