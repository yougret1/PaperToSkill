#!/usr/bin/env python
"""Audit the active user goal against current repository evidence."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = {
    "memory_long_term": "memory/long_term_memory.md",
    "memory_short_term": "memory/short_term_memory.md",
    "ai_scientist_input": "ai_scientist_inputs/papertoskill.md",
    "ai_scientist_seed_ideas": "ai_scientist_inputs/papertoskill_seed_ideas.json",
    "papertoskill_skill": "skill/SKILL.md",
    "extractor_script": "scripts/papertoskill_extract.py",
    "auto_note_script": "scripts/papertoskill_note_from_text.py",
    "pipeline_script": "scripts/papertoskill_pipeline.py",
    "aaai_tex": "paper/aaai/papertoskill_aaai2027.tex",
    "aaai_style": "paper/aaai/aaai2027.sty",
    "usage_readme": "examples/usage/README.md",
    "model_ablation_task": "benchmarks/model_ablation_v0.json",
    "model_ablation_runner": "scripts/run_model_ablation_prompts.py",
    "model_ablation_evaluator": "scripts/evaluate_model_ablation_responses.py",
    "deepseek_usage": "examples/usage/model_ablation_usage.md",
    "failure_archive": "results/failure_cases/failure_case_archive.json",
    "human_fidelity_summary": "results/human_fidelity_packets/annotation_summary.json",
    "tokenizer_cost_proxy": "results/tables/context_cost_proxy_tokenizer.json",
    "goal_completion_audit": "research/goal_completion_audit.md",
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


def required_file_checks(root: Path) -> list[Check]:
    checks = []
    for check_id, raw_path in REQUIRED_FILES.items():
        path = resolve(root, raw_path)
        checks.append(
            Check(
                check_id,
                "ready" if path.exists() else "fail",
                "present" if path.exists() else "missing",
                raw_path,
            )
        )
    return checks


def report_ready_check(root: Path, check_id: str, report_path: str, expected: str = "ready") -> Check:
    path = resolve(root, report_path)
    report = load_json(path)
    overall = report.get("overall_status")
    status = "ready" if overall == expected else "fail"
    return Check(check_id, status, f"overall_status={overall}", report_path)


def csv_row_count(root: Path, raw_path: str) -> int:
    path = resolve(root, raw_path)
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def memory_checks(root: Path) -> list[Check]:
    long_text = read_text(root / "memory/long_term_memory.md")
    short_text = read_text(root / "memory/short_term_memory.md")
    checks = [
        Check(
            "memory_resume_rule_present",
            "ready" if "Read this file after any context compaction" in long_text and "Read this file after any context compaction" in short_text else "fail",
            "long-term and short-term resume rules present",
            "memory/long_term_memory.md; memory/short_term_memory.md",
        ),
        Check(
            "memory_current_blockers_recorded",
            "ready" if "No available accounts" in short_text and "gpt-5.5" in short_text and "Upstream access forbidden" in short_text else "fail",
            "current model-availability blockers recorded",
            "memory/short_term_memory.md",
        ),
    ]
    return checks


def ai_scientist_checks(root: Path) -> list[Check]:
    short_text = read_text(root / "memory/short_term_memory.md")
    dry_run_ready = "AI-Scientist-v2 dry-run succeeded" in short_text
    provider_blocked = "No available accounts" in short_text or "provider account" in short_text
    return [
        Check(
            "ai_scientist_v2_local_dry_run_recorded",
            "ready" if dry_run_ready else "fail",
            "dry-run recorded in memory" if dry_run_ready else "dry-run evidence missing",
            "memory/short_term_memory.md",
        ),
        Check(
            "ai_scientist_v2_live_llm_run_complete",
            "pending" if provider_blocked else "ready",
            "blocked by provider account availability" if provider_blocked else "no provider blocker recorded",
            "memory/short_term_memory.md",
        ),
    ]


def system_and_experiment_checks(root: Path) -> list[Check]:
    main_rows = csv_row_count(root, "results/tables/main_results.csv")
    transfer_rows = csv_row_count(root, "results/tables/transfer_ablation.csv")
    auto_rows = csv_row_count(root, "results/tables/auto_note_comparison.csv")
    failure = load_json(root / "results/failure_cases/failure_case_archive.json")
    failure_counts = failure.get("scope_counts", {})
    tokenizer = load_json(root / "results/tables/context_cost_proxy_tokenizer.json")
    tokenizer_rows = len(tokenizer.get("context_size", []))
    efficiency_rows = len(tokenizer.get("coverage_efficiency", []))
    return [
        Check(
            "papertoskill_curated_benchmark_ready",
            "ready" if main_rows >= 4 else "fail",
            f"main_result_rows={main_rows}",
            "results/tables/main_results.csv",
        ),
        Check(
            "offline_harness_transfer_ablation_ready",
            "ready" if transfer_rows >= 4 else "fail",
            f"transfer_rows={transfer_rows}",
            "results/tables/transfer_ablation.csv",
        ),
        Check(
            "auto_note_examples_ready",
            "ready" if auto_rows >= 4 else "fail",
            f"auto_note_rows={auto_rows}",
            "results/tables/auto_note_comparison.csv",
        ),
        Check(
            "tokenizer_cost_proxy_ready",
            "ready" if tokenizer_rows >= 20 and efficiency_rows >= 12 else "fail",
            f"context_size_rows={tokenizer_rows}; coverage_efficiency_rows={efficiency_rows}",
            "results/tables/context_cost_proxy_tokenizer.json",
        ),
        Check(
            "provider_billing_evidence_complete",
            "pending",
            "local token proxies exist; provider billing and success-per-dollar evidence remain uncollected",
            "results/tables/context_cost_proxy_tokenizer.json",
        ),
        Check(
            "failure_branch_archive_ready",
            "ready"
            if failure.get("total_cases") == 27 and failure_counts.get("paper") == 21 and failure_counts.get("project") == 6
            else "fail",
            f"total={failure.get('total_cases')}; paper={failure_counts.get('paper')}; project={failure_counts.get('project')}",
            "results/failure_cases/failure_case_archive.json",
        ),
    ]


def paper_package_checks(root: Path) -> list[Check]:
    checks = [
        report_ready_check(root, "aaai_package_gate_ready", "results/reproducibility/aaai_package_report.json"),
        report_ready_check(root, "usage_example_gate_ready", "results/reproducibility/usage_example_report.json"),
        report_ready_check(root, "paper_table_gate_ready", "results/reproducibility/paper_table_report.json"),
        report_ready_check(root, "paper_claim_gate_ready", "results/reproducibility/paper_claim_report.json"),
    ]
    ready = all(check.status == "ready" for check in checks)
    checks.append(
        Check(
            "aaai_final_submission_ready",
            "pending" if ready else "fail",
            "AAAI package is locally verified, but final live/model/human/cost evidence decisions remain pending"
            if ready
            else "one or more paper-package gates failed",
            "paper/aaai/; results/reproducibility/",
        )
    )
    return checks


def model_ablation_checks(root: Path) -> list[Check]:
    index = load_json(root / "results/model_ablation_prompts/v0/index.json")
    run_report = load_json(root / "results/model_ablation_prompts/v0/run_report.json")
    evaluation = load_json(root / "results/model_ablation_prompts/v0/evaluation.json")
    prompts = index.get("prompts", [])
    model_ids = {item.get("model_id") for item in prompts}
    expected_model_ids = {"claude_opus_4_8", "gpt_5_5_or_gpt_family", "deepseek_followup_slot"}
    run_rows = run_report.get("results", [])
    model_catalogs = run_report.get("model_catalogs", [])
    claude_rows = [row for row in run_rows if row.get("model_id") == "claude_opus_4_8"]
    gpt_rows = [row for row in run_rows if row.get("model_id") == "gpt_5_5_or_gpt_family"]
    gpt_catalog_models = [
        model
        for catalog in model_catalogs
        if catalog.get("auth_env") == "PAPERTOSKILL_GPT_OPENAI_API_KEY"
        for model in catalog.get("model_ids", [])
        if str(model).lower().startswith("gpt")
    ]
    summary = evaluation.get("summary", {})
    results = evaluation.get("results", [])
    by_model = {}
    for row in results:
        by_model.setdefault(row.get("model_id"), []).append(row)

    def model_complete(model_id: str) -> bool:
        rows = by_model.get(model_id, [])
        return bool(rows) and all(row.get("status") == "scored" for row in rows)

    def attempted_aliases(rows: list[dict[str, Any]]) -> set[str]:
        aliases = set()
        for row in rows:
            if row.get("alias_used"):
                aliases.add(str(row["alias_used"]))
            for attempt in row.get("attempted_aliases", []):
                if attempt.get("alias"):
                    aliases.add(str(attempt["alias"]))
        return aliases

    deepseek_aliases = {item.get("model_alias") for item in prompts if item.get("model_id") == "deepseek_followup_slot"}
    deepseek_placeholder = "deepseek-to-be-filled" in deepseek_aliases
    claude_attempted = attempted_aliases(claude_rows)
    return [
        Check(
            "model_ablation_protocol_ready",
            "ready" if len(prompts) == 6 and expected_model_ids <= model_ids else "fail",
            f"prompt_packets={len(prompts)}; models={','.join(sorted(model_ids))}",
            "results/model_ablation_prompts/v0/index.json",
        ),
        Check(
            "claude_opus_4_8_ablation_attempted",
            "ready" if claude_rows and any(alias.startswith("claude-opus-4") for alias in claude_attempted) else "fail",
            (
                f"rows={len(claude_rows)}; "
                f"statuses={','.join(sorted({str(row.get('status')) for row in claude_rows}))}; "
                f"attempted_aliases={','.join(sorted(claude_attempted))}"
            ),
            "results/model_ablation_prompts/v0/run_report.json",
        ),
        Check(
            "claude_opus_4_8_ablation_complete",
            "ready" if model_complete("claude_opus_4_8") else "pending",
            "saved and scored responses are required before claiming completion",
            "results/model_ablation_prompts/v0/evaluation.json",
        ),
        Check(
            "gpt_family_ablation_availability_checked",
            "ready" if gpt_rows and gpt_catalog_models else "fail",
            f"rows={len(gpt_rows)}; statuses={','.join(sorted({str(row.get('status')) for row in gpt_rows}))}; catalog_gpt_models={len(gpt_catalog_models)}",
            "results/model_ablation_prompts/v0/run_report.json",
        ),
        Check(
            "gpt_family_ablation_complete",
            "ready" if model_complete("gpt_5_5_or_gpt_family") else "pending",
            "GPT-family catalog is available, but chat completions did not produce saved/scored responses",
            "results/model_ablation_prompts/v0/evaluation.json",
        ),
        Check(
            "deepseek_followup_process_ready",
            "ready" if "deepseek_followup_slot" in model_ids else "fail",
            "DeepSeek slot is present and runner supports configured aliases",
            "benchmarks/model_ablation_v0.json; examples/usage/model_ablation_usage.md",
        ),
        Check(
            "deepseek_followup_response_complete",
            "ready" if model_complete("deepseek_followup_slot") else "pending",
            "placeholder alias still pending user-provided DeepSeek configuration" if deepseek_placeholder else "configured DeepSeek responses are not all scored",
            "results/model_ablation_prompts/v0/evaluation.json",
        ),
        Check(
            "model_ablation_evaluation_complete",
            "ready" if int(summary.get("pending_rows", 0)) == 0 and int(summary.get("scored_rows", 0)) > 0 else "pending",
            f"scored_rows={summary.get('scored_rows')}; pending_rows={summary.get('pending_rows')}",
            "results/model_ablation_prompts/v0/evaluation.json",
        ),
    ]


def live_and_human_checks(root: Path) -> list[Check]:
    package = load_json(root / "results/reproducibility/package_report.json")
    checks = package.get("checks", [])
    pending_live = [
        check
        for check in checks
        if check.get("id", "").endswith("_live_responses") and check.get("status") == "pending"
    ]
    human = load_json(root / "results/human_fidelity_packets/annotation_summary.json")
    human_complete = human.get("annotation_status") == "complete"
    return [
        Check(
            "live_cross_harness_responses_complete",
            "ready" if not pending_live else "pending",
            f"pending_live_response_sets={len(pending_live)}",
            "results/reproducibility/package_report.json",
        ),
        Check(
            "human_fidelity_annotation_complete",
            "ready" if human_complete else "pending",
            f"status={human.get('annotation_status')}; scored_rows={human.get('scored_rows')}; pending_rows={human.get('pending_rows')}",
            "results/human_fidelity_packets/annotation_summary.json",
        ),
    ]


def completion_check(checks: list[Check]) -> Check:
    failed = [check.id for check in checks if check.status == "fail"]
    pending = [check.id for check in checks if check.status == "pending"]
    if failed:
        return Check(
            "active_goal_complete",
            "fail",
            "failed_requirements=" + ",".join(failed[:10]),
            "all goal checks",
        )
    if pending:
        return Check(
            "active_goal_complete",
            "pending",
            "pending_requirements=" + ",".join(pending[:12]),
            "all goal checks",
        )
    return Check("active_goal_complete", "ready", "all requirements verified", "all goal checks")


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    checks: list[Check] = []
    checks.extend(required_file_checks(root))
    checks.extend(memory_checks(root))
    checks.extend(ai_scientist_checks(root))
    checks.extend(system_and_experiment_checks(root))
    checks.extend(paper_package_checks(root))
    checks.extend(model_ablation_checks(root))
    checks.extend(live_and_human_checks(root))
    checks.append(completion_check(checks))

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall = "fail"
    elif status_counts.get("pending", 0):
        overall = "not_complete_pending_external_evidence"
    else:
        overall = "complete"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Audits the active user goal against local repository evidence. Pending checks are explicit "
            "remaining requirements, not negative evidence and not local package failures."
        ),
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
    counts = report["status_counts"]
    rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines = [
        "# Goal Completion Report",
        "",
        "Evidence boundary: this report audits the active user goal against local "
        "repository evidence. Pending checks are remaining requirements, not "
        "negative evidence and not local package failures.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Pending checks: {counts.get('pending', 0)}",
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
    parser = argparse.ArgumentParser(description="Audit active PaperToSkill goal completion.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "goal_completion_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "goal_completion_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if a goal requirement fails.")
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
