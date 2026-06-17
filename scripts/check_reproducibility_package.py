#!/usr/bin/env python
"""Check the PaperToSkill reproducibility package state."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAPERS = [
    {
        "id": "ai_scientist_v2",
        "name": "AI Scientist-v2",
        "skill": "generated_skills/ai_scientist_v2/SKILL.md",
        "source_map": "generated_skills/ai_scientist_v2/references/source_map.json",
        "rubric": "results/evaluations/ai_scientist_v2_rubric_v0.json",
        "context": "results/evaluations/ai_scientist_v2_context_baselines_v0.json",
        "transfer": "results/evaluations/ai_scientist_v2_harness_transfer_v0.json",
        "source_span": "results/evaluations/ai_scientist_v2_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/ai_scientist_v2_v0/index.json",
    },
    {
        "id": "reflexion",
        "name": "Reflexion",
        "skill": "generated_skills/reflexion/SKILL.md",
        "source_map": "generated_skills/reflexion/references/source_map.json",
        "rubric": "results/evaluations/reflexion_rubric_v0.json",
        "context": "results/evaluations/reflexion_context_baselines_v0.json",
        "transfer": "results/evaluations/reflexion_harness_transfer_v0.json",
        "source_span": "results/evaluations/reflexion_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/reflexion_v0/index.json",
    },
    {
        "id": "aide",
        "name": "AIDE",
        "skill": "generated_skills/aide/SKILL.md",
        "source_map": "generated_skills/aide/references/source_map.json",
        "rubric": "results/evaluations/aide_rubric_v0.json",
        "context": "results/evaluations/aide_context_baselines_v0.json",
        "transfer": "results/evaluations/aide_harness_transfer_v0.json",
        "source_span": "results/evaluations/aide_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/aide_v0/index.json",
    },
]

CORE_FILES = {
    "memory_long_term": "memory/long_term_memory.md",
    "memory_short_term": "memory/short_term_memory.md",
    "paper_draft": "paper/draft.md",
    "paper_outline": "paper/outline.md",
    "claim_checklist": "paper/claim_checklist.md",
    "limitations": "paper/limitations.md",
    "artifact_map": "research/artifact_map.md",
    "claim_evidence_matrix": "research/claim_evidence_matrix.md",
    "stage_log": "research/stage_log.md",
    "result_cards": "results/result_cards.md",
}

TABLE_FILES = {
    "main_results_md": "results/tables/main_results.md",
    "main_results_csv": "results/tables/main_results.csv",
    "transfer_ablation_md": "results/tables/transfer_ablation.md",
    "context_cost_proxy_md": "results/tables/context_cost_proxy.md",
    "context_cost_proxy_json": "results/tables/context_cost_proxy.json",
    "paper_ready_summary": "results/tables/paper_ready_summary.md",
}

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def required_file_checks(root: Path, files: dict[str, str]) -> list[Check]:
    checks = []
    for check_id, raw_path in files.items():
        path = resolve_path(root, raw_path)
        status = "ready" if path.exists() else "fail"
        detail = "present" if path.exists() else "missing"
        checks.append(Check(check_id, status, detail, str(raw_path)))
    return checks


def score_by_id(results: list[dict[str, Any]], result_id: str) -> dict[str, Any]:
    for item in results:
        if item.get("id") == result_id:
            return item
    raise KeyError(result_id)


def paper_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    for paper in PAPERS:
        prefix = paper["id"]
        checks.extend(
            required_file_checks(
                root,
                {
                    f"{prefix}_skill": paper["skill"],
                    f"{prefix}_source_map": paper["source_map"],
                    f"{prefix}_rubric": paper["rubric"],
                    f"{prefix}_context": paper["context"],
                    f"{prefix}_transfer": paper["transfer"],
                    f"{prefix}_source_span": paper["source_span"],
                    f"{prefix}_live_prompt_index": paper["live"],
                },
            )
        )

        rubric_path = root / paper["rubric"]
        if rubric_path.exists():
            rubric = load_json(rubric_path)
            score = float(rubric.get("score", 0))
            max_score = float(rubric.get("max_score", 20))
            status = "ready" if score == max_score else "fail"
            checks.append(
                Check(
                    f"{prefix}_rubric_score",
                    status,
                    f"{score:g}/{max_score:g}",
                    paper["rubric"],
                )
            )

        context_path = root / paper["context"]
        if context_path.exists():
            context = load_json(context_path)
            try:
                skill = score_by_id(context["results"], "skill")
                generic = score_by_id(context["results"], "generic_summary")
                abstract = score_by_id(context["results"], "abstract_only")
                status = "ready" if skill["score"] > generic["score"] and skill["score"] > abstract["score"] else "fail"
                detail = f"skill={skill['score']}; generic={generic['score']}; abstract={abstract['score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected skill/generic_summary/abstract_only rows"
            checks.append(Check(f"{prefix}_context_baseline_order", status, detail, paper["context"]))

        transfer_path = root / paper["transfer"]
        if transfer_path.exists():
            transfer = load_json(transfer_path)
            try:
                full = score_by_id(transfer["results"], "full_skill")
                without = score_by_id(transfer["results"], "skill_without_transfer_notes")
                status = "ready" if full["average_normalized_score"] > without["average_normalized_score"] else "fail"
                detail = f"full={full['average_normalized_score']}; no_transfer={without['average_normalized_score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected full_skill/skill_without_transfer_notes rows"
            checks.append(Check(f"{prefix}_transfer_ablation_order", status, detail, paper["transfer"]))

        source_span_path = root / paper["source_span"]
        if source_span_path.exists():
            source_span = load_json(source_span_path)
            result = source_span.get("results", [{}])[0]
            support_rate = float(result.get("support_rate", 0))
            invalid_ranges = int(result.get("invalid_ranges", 0))
            status = "ready" if support_rate >= 0.9 and invalid_ranges == 0 else "fail"
            detail = f"support_rate={support_rate:g}; invalid_ranges={invalid_ranges}"
            checks.append(Check(f"{prefix}_source_span_support", status, detail, paper["source_span"]))

        live_path = root / paper["live"]
        if live_path.exists():
            live = load_json(live_path)
            prompts = live.get("prompts", [])
            prompt_missing = [
                item["prompt_path"]
                for item in prompts
                if not resolve_path(root, item.get("prompt_path", "")).exists()
            ]
            status = "ready" if len(prompts) == 6 and not prompt_missing else "fail"
            detail = f"prompt_packets={len(prompts)}; missing_prompts={len(prompt_missing)}"
            checks.append(Check(f"{prefix}_live_prompt_packets", status, detail, paper["live"]))

            missing_responses = [
                item.get("expected_response_path", "")
                for item in prompts
                if not resolve_path(root, item.get("expected_response_path", "")).exists()
            ]
            response_status = "ready" if not missing_responses else "pending"
            checks.append(
                Check(
                    f"{prefix}_live_responses",
                    response_status,
                    f"missing_response_files={len(missing_responses)}",
                    paper["live"],
                )
            )
    return checks


def human_fidelity_checks(root: Path) -> list[Check]:
    checks = required_file_checks(
        root,
        {
            "human_fidelity_protocol": "benchmarks/human_fidelity_review_v0.json",
            "human_fidelity_template": "results/human_fidelity_packets/annotation_template.csv",
            "human_fidelity_summary_json": "results/human_fidelity_packets/annotation_summary.json",
            "human_fidelity_summary_md": "results/human_fidelity_packets/annotation_summary.md",
        },
    )
    summary_path = root / "results/human_fidelity_packets/annotation_summary.json"
    if summary_path.exists():
        summary = load_json(summary_path)
        errors = summary.get("errors", [])
        status = "ready" if not errors else "fail"
        checks.append(Check("human_fidelity_summary_valid", status, f"errors={len(errors)}", str(summary_path.relative_to(root))))
        annotation_status = summary.get("annotation_status")
        complete_status = "ready" if annotation_status == "complete" else "pending"
        checks.append(
            Check(
                "human_fidelity_annotation_complete",
                complete_status,
                f"status={annotation_status}; scored_rows={summary.get('scored_rows', 0)}; pending_rows={summary.get('pending_rows', 0)}",
                str(summary_path.relative_to(root)),
            )
        )
    return checks


def failure_archive_checks(root: Path) -> list[Check]:
    checks = required_file_checks(
        root,
        {
            "failure_archive_config": "benchmarks/failure_case_archive_v0.json",
            "failure_archive_json": "results/failure_cases/failure_case_archive.json",
            "failure_archive_md": "results/failure_cases/failure_case_archive.md",
            "failure_archive_csv": "results/failure_cases/failure_case_archive.csv",
        },
    )
    archive_path = root / "results/failure_cases/failure_case_archive.json"
    if archive_path.exists():
        archive = load_json(archive_path)
        scope_counts = archive.get("scope_counts", {})
        status = (
            "ready"
            if archive.get("total_cases") == 20 and scope_counts.get("paper") == 14 and scope_counts.get("project") == 6
            else "fail"
        )
        detail = (
            f"total={archive.get('total_cases')}; "
            f"paper={scope_counts.get('paper')}; project={scope_counts.get('project')}"
        )
        checks.append(Check("failure_archive_counts", status, detail, str(archive_path.relative_to(root))))
    return checks


def secret_scan_check(root: Path) -> Check:
    matches = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if SECRET_PATTERN.search(line):
                matches.append(f"{path.relative_to(root)}:{line_number}")
    status = "ready" if not matches else "fail"
    detail = "no raw API-key-like strings found" if not matches else "; ".join(matches[:10])
    return Check("secret_scan", status, detail, "repository text files")


def build_report(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    checks.extend(required_file_checks(root, CORE_FILES))
    checks.extend(required_file_checks(root, TABLE_FILES))
    checks.extend(paper_checks(root))
    checks.extend(human_fidelity_checks(root))
    checks.extend(failure_archive_checks(root))
    checks.append(secret_scan_check(root))

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall = "fail"
    elif status_counts.get("pending", 0):
        overall = "ready_with_pending_external_evidence"
    else:
        overall = "ready"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks local reproducibility artifacts and evidence gates. Pending live responses or human "
            "annotations are reported as pending external evidence, not local package failures."
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
    rows = [
        [check["id"], check["status"], check["detail"], check["evidence"]]
        for check in report["checks"]
    ]
    counts = report["status_counts"]
    lines = [
        "# Reproducibility Package Report",
        "",
        "Evidence boundary: this report checks local package completeness and separates "
        "pending external evidence from local failures.",
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
    parser = argparse.ArgumentParser(description="Check the PaperToSkill reproducibility package.")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "reproducibility" / "package_report.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "reproducibility" / "package_report.md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any local package check fails.")
    args = parser.parse_args()

    report = build_report(root)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
