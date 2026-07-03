#!/usr/bin/env python
"""Check the planned real-reuse benchmark specification."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_MAIN_TASKS = {
    "AIDE-T1",
    "AIDE-T2",
    "SWE-T1",
    "SWE-T2",
    "REF-T1",
    "REF-T2",
    "SNAP-T1",
    "SNAP-T2",
}
EXPECTED_MAIN_PAPERS = {"aide", "swe_agent", "reflexion", "snapatac2"}
EXPECTED_PRIMARY_CONDITIONS = {"summary", "papertoskill"}
FORBIDDEN_MAIN_CONDITIONS = {"abstract", "full_excerpt"}
EXPECTED_SANITY_TASKS = {"AIDE-T1", "SWE-T1", "SNAP-T1"}
EXPECTED_MODEL_FAMILIES = {"Claude-family", "GPT-family", "DeepSeek-family"}
EXPECTED_RAW_ROW_FIELDS = {
    "run_id",
    "task_id",
    "source_paper_id",
    "condition",
    "model_family",
    "model_alias",
    "task_score",
    "success",
    "workflow_score",
    "unsupported_errors",
    "tokens",
    "time_seconds",
    "failure_reason",
    "output_path",
}
EXPECTED_FIXTURE_STATUS = "fixture_manifest_ready_assets_pending"


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


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def task_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(task.get("id")): task for task in spec.get("tasks", [])}


def paper_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(paper.get("id")): paper for paper in spec.get("source_papers", [])}


def build_report(root: Path, spec_path: Path) -> dict[str, Any]:
    root = root.resolve()
    spec_path = spec_path if spec_path.is_absolute() else root / spec_path
    checks: list[Check] = []
    if not spec_path.exists():
        checks.append(
            Check(
                "real_reuse_spec_file",
                "fail",
                "missing",
                relative(root, spec_path),
            )
        )
        return report_from_checks(root, spec_path, {}, checks)

    spec = load_json(spec_path)
    tasks = task_by_id(spec)
    papers = paper_by_id(spec)
    task_ids = set(tasks)
    main_paper_ids = {paper_id for paper_id, paper in papers.items() if str(paper.get("role", "")).startswith("main")}
    main_conditions = set(spec.get("main_conditions", []))
    excluded_main_conditions = set(spec.get("excluded_main_conditions", []))
    sanity_tasks = set(spec.get("full_excerpt_sanity_tasks", []))

    checks.extend(
        [
            Check(
                "real_reuse_spec_file",
                "ready",
                "present",
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_status_planned",
                "ready" if spec.get("status") == "planned" else "fail",
                f"status={spec.get('status')}",
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_main_task_count",
                "ready" if len(tasks) == 8 else "fail",
                f"tasks={len(tasks)}",
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_expected_task_ids",
                "ready" if task_ids == EXPECTED_MAIN_TASKS else "fail",
                "tasks=" + ",".join(sorted(task_ids)),
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_main_papers",
                "ready" if EXPECTED_MAIN_PAPERS <= main_paper_ids else "fail",
                "main_papers=" + ",".join(sorted(main_paper_ids)),
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_main_conditions",
                "ready" if main_conditions == EXPECTED_PRIMARY_CONDITIONS else "fail",
                "conditions=" + ",".join(sorted(main_conditions)),
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_no_abstract_or_full_excerpt_main",
                "ready"
                if not (main_conditions & FORBIDDEN_MAIN_CONDITIONS)
                and FORBIDDEN_MAIN_CONDITIONS <= excluded_main_conditions
                else "fail",
                "excluded=" + ",".join(sorted(excluded_main_conditions)),
                relative(root, spec_path),
            ),
            Check(
                "real_reuse_full_excerpt_sanity_scope",
                "ready" if sanity_tasks == EXPECTED_SANITY_TASKS else "fail",
                "sanity_tasks=" + ",".join(sorted(sanity_tasks)),
                relative(root, spec_path),
            ),
        ]
    )

    checks.extend(task_checks(root, spec_path, tasks, papers))
    checks.extend(source_paper_checks(root, spec_path, papers))
    checks.extend(llm_ablation_checks(root, spec_path, spec))
    checks.extend(planned_output_checks(root, spec_path, spec))
    checks.extend(task_spec_file_checks(root, spec_path, tasks))
    checks.extend(fixture_manifest_checks(root, spec_path, tasks))
    return report_from_checks(root, spec_path, spec, checks)


def task_checks(
    root: Path,
    spec_path: Path,
    tasks: dict[str, dict[str, Any]],
    papers: dict[str, dict[str, Any]],
) -> list[Check]:
    checks: list[Check] = []
    for task_id in sorted(tasks):
        task = tasks[task_id]
        paper_id = str(task.get("source_paper_id", ""))
        conditions = set(task.get("conditions", []))
        metric = task.get("metric", {})
        reference = task.get("paper_reference", {})
        artifacts = task.get("planned_artifacts", {})
        checklist = task.get("workflow_checklist", [])
        task_prefix = task_id.lower().replace("-", "_")

        checks.append(
            Check(
                f"{task_prefix}_source_paper_known",
                "ready" if paper_id in papers else "fail",
                f"source_paper_id={paper_id}",
                relative(root, spec_path),
            )
        )
        checks.append(
            Check(
                f"{task_prefix}_planned_status",
                "ready" if task.get("status") == "planned" else "fail",
                f"status={task.get('status')}",
                relative(root, spec_path),
            )
        )
        checks.append(
            Check(
                f"{task_prefix}_conditions_are_primary_only",
                "ready" if conditions == EXPECTED_PRIMARY_CONDITIONS else "fail",
                "conditions=" + ",".join(sorted(conditions)),
                relative(root, spec_path),
            )
        )
        checks.append(
            Check(
                f"{task_prefix}_automated_metric",
                "ready" if metric.get("automated") is True and metric.get("name") else "fail",
                f"metric={metric.get('name')}; automated={metric.get('automated')}",
                relative(root, spec_path),
            )
        )
        comparability = str(reference.get("comparability", ""))
        checks.append(
            Check(
                f"{task_prefix}_reference_boundary",
                "ready" if comparability == "reported_reference_only_until_local_reproduction" else "fail",
                comparability or "missing comparability",
                relative(root, spec_path),
            )
        )
        output_paths = " ".join(str(value) for value in artifacts.values())
        checks.append(
            Check(
                f"{task_prefix}_planned_artifacts_declared",
                "ready"
                if "benchmarks/real_reuse/tasks/" in output_paths
                and "results/real_reuse/" in output_paths
                else "fail",
                output_paths or "missing planned artifacts",
                relative(root, spec_path),
            )
        )
        checks.append(
            Check(
                f"{task_prefix}_workflow_checklist_preregistered",
                "ready" if len(checklist) >= 4 else "fail",
                f"items={len(checklist)}",
                relative(root, spec_path),
            )
        )
    return checks


def source_paper_checks(root: Path, spec_path: Path, papers: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    for paper_id, paper in sorted(papers.items()):
        prefix = paper_id.lower()
        checks.append(
            Check(
                f"{prefix}_paper_url_declared",
                "ready" if str(paper.get("paper_url", "")).startswith("https://") else "fail",
                str(paper.get("paper_url", "")),
                relative(root, spec_path),
            )
        )
        checks.append(
            Check(
                f"{prefix}_resource_status_declared",
                "ready" if paper.get("resource_status") else "fail",
                str(paper.get("resource_status", "")),
                relative(root, spec_path),
            )
        )
        if str(paper.get("role", "")).startswith("main"):
            checks.append(
                Check(
                    f"{prefix}_code_url_declared",
                    "ready" if str(paper.get("code_url", "")).startswith("https://") else "fail",
                    str(paper.get("code_url", "")),
                    relative(root, spec_path),
                )
            )
    return checks


def llm_ablation_checks(root: Path, spec_path: Path, spec: dict[str, Any]) -> list[Check]:
    ablation = spec.get("llm_ablation", {})
    families = set(ablation.get("model_families", []))
    conditions = set(ablation.get("conditions", []))
    return [
        Check(
            "real_reuse_llm_ablation_linked_to_tasks",
            "ready" if ablation.get("linked_to_real_reuse_tasks") is True else "fail",
            f"linked={ablation.get('linked_to_real_reuse_tasks')}",
            relative(root, spec_path),
        ),
        Check(
            "real_reuse_llm_ablation_model_families",
            "ready" if EXPECTED_MODEL_FAMILIES <= families else "fail",
            "families=" + ",".join(sorted(families)),
            relative(root, spec_path),
        ),
        Check(
            "real_reuse_llm_ablation_conditions",
            "ready" if conditions == EXPECTED_PRIMARY_CONDITIONS else "fail",
            "conditions=" + ",".join(sorted(conditions)),
            relative(root, spec_path),
        ),
    ]


def planned_output_checks(root: Path, spec_path: Path, spec: dict[str, Any]) -> list[Check]:
    outputs = spec.get("planned_outputs", {})
    required = {
        "spec_preflight_json",
        "spec_preflight_md",
        "raw_rows",
        "main_results",
        "domain_robustness",
        "llm_ablation_raw",
    }
    missing = sorted(required - set(outputs))
    results_paths = [str(value) for value in outputs.values() if str(value).startswith("results/real_reuse/")]
    return [
        Check(
            "real_reuse_planned_outputs_complete",
            "ready" if not missing else "fail",
            "missing=" + ",".join(missing) if missing else f"outputs={len(outputs)}",
            relative(root, spec_path),
        ),
        Check(
            "real_reuse_planned_outputs_under_results_real_reuse",
            "ready" if len(results_paths) >= len(required) else "fail",
            f"results_real_reuse_paths={len(results_paths)}",
            relative(root, spec_path),
        ),
    ]


def task_spec_file_checks(root: Path, spec_path: Path, tasks: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    present_task_specs: set[str] = set()
    for task_id in sorted(tasks):
        task = tasks[task_id]
        declared = task.get("planned_artifacts", {}).get("task_spec", "")
        task_spec_path = root / str(declared)
        prefix = task_id.lower().replace("-", "_")
        if not declared:
            checks.append(
                Check(
                    f"{prefix}_task_spec_path_declared",
                    "fail",
                    "missing task_spec planned artifact",
                    relative(root, spec_path),
                )
            )
            continue
        if not task_spec_path.exists():
            checks.append(
                Check(
                    f"{prefix}_task_spec_file_present",
                    "fail",
                    "missing",
                    relative(root, task_spec_path),
                )
            )
            continue
        task_spec = load_json(task_spec_path)
        present_task_specs.add(task_id)
        conditions = {condition.get("id") for condition in task_spec.get("conditions", [])}
        raw_fields = set(task_spec.get("raw_row_schema", []))
        checks.extend(
            [
                Check(
                    f"{prefix}_task_spec_file_present",
                    "ready",
                    "present",
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_identity",
                    "ready"
                    if task_spec.get("id") == task_id
                    and task_spec.get("source_paper_id") == task.get("source_paper_id")
                    else "fail",
                    f"id={task_spec.get('id')}; source_paper_id={task_spec.get('source_paper_id')}",
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_status",
                    "ready" if task_spec.get("status") == "spec_ready_assets_pending" else "fail",
                    f"status={task_spec.get('status')}",
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_conditions",
                    "ready" if conditions == EXPECTED_PRIMARY_CONDITIONS else "fail",
                    "conditions=" + ",".join(sorted(str(condition) for condition in conditions)),
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_metric_matches",
                    "ready"
                    if task_spec.get("metric_contract", {}).get("name") == task.get("metric", {}).get("name")
                    else "fail",
                    f"metric={task_spec.get('metric_contract', {}).get('name')}",
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_raw_row_schema",
                    "ready" if EXPECTED_RAW_ROW_FIELDS <= raw_fields else "fail",
                    "fields=" + ",".join(sorted(raw_fields)),
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_no_mid_run_human",
                    "ready"
                    if task_spec.get("run_controls", {}).get("first_pass_human_intervention")
                    == "none_mid_run"
                    else "fail",
                    f"first_pass_human_intervention={task_spec.get('run_controls', {}).get('first_pass_human_intervention')}",
                    relative(root, task_spec_path),
                ),
            ]
        )
    checks.append(
        Check(
            "real_reuse_task_specs_materialized",
            "ready" if present_task_specs == EXPECTED_MAIN_TASKS else "fail",
            "task_specs=" + ",".join(sorted(present_task_specs)),
            relative(root, spec_path),
        )
    )
    return checks


def fixture_manifest_checks(root: Path, spec_path: Path, tasks: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    present_fixture_manifests: set[str] = set()
    for task_id in sorted(tasks):
        prefix = task_id.lower().replace("-", "_")
        fixture_path = root / "benchmarks" / "real_reuse" / "fixtures" / f"{task_id}.json"
        task_spec_path = root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json"
        if not fixture_path.exists():
            checks.append(
                Check(
                    f"{prefix}_fixture_manifest_present",
                    "fail",
                    "missing",
                    relative(root, fixture_path),
                )
            )
            continue
        fixture = load_json(fixture_path)
        present_fixture_manifests.add(task_id)
        task_spec = load_json(task_spec_path) if task_spec_path.exists() else {}
        asset_slots = fixture.get("asset_slots", [])
        context_conditions = {asset.get("condition") for asset in fixture.get("context_assets", [])}
        checks.extend(
            [
                Check(
                    f"{prefix}_fixture_manifest_present",
                    "ready",
                    "present",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_identity",
                    "ready"
                    if fixture.get("task_id") == task_id
                    and fixture.get("source_paper_id") == tasks[task_id].get("source_paper_id")
                    else "fail",
                    f"task_id={fixture.get('task_id')}; source_paper_id={fixture.get('source_paper_id')}",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_status",
                    "ready" if fixture.get("status") == EXPECTED_FIXTURE_STATUS else "fail",
                    f"status={fixture.get('status')}",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_asset_slots_declared",
                    "ready" if len(asset_slots) >= 3 else "fail",
                    f"asset_slots={len(asset_slots)}",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_context_conditions",
                    "ready" if context_conditions == EXPECTED_PRIMARY_CONDITIONS else "fail",
                    "conditions=" + ",".join(sorted(str(condition) for condition in context_conditions)),
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_metric_matches_task",
                    "ready"
                    if fixture.get("scoring_contract", {}).get("metric_name")
                    == task_spec.get("metric_contract", {}).get("name")
                    else "fail",
                    f"metric={fixture.get('scoring_contract', {}).get('metric_name')}",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_no_mid_run_human",
                    "ready"
                    if fixture.get("execution_budget", {}).get("first_pass_human_intervention")
                    == "none_mid_run"
                    else "fail",
                    f"first_pass_human_intervention={fixture.get('execution_budget', {}).get('first_pass_human_intervention')}",
                    relative(root, fixture_path),
                ),
                Check(
                    f"{prefix}_fixture_license_review_pending",
                    "ready"
                    if "required" in str(fixture.get("provenance_and_license", {}).get("license_review", ""))
                    and fixture.get("provenance_and_license", {}).get("download_or_clone_status") == "not_started"
                    else "fail",
                    str(fixture.get("provenance_and_license", {})),
                    relative(root, fixture_path),
                ),
            ]
        )
    checks.append(
        Check(
            "real_reuse_fixture_manifests_materialized",
            "ready" if present_fixture_manifests == EXPECTED_MAIN_TASKS else "fail",
            "fixtures=" + ",".join(sorted(present_fixture_manifests)),
            relative(root, spec_path),
        )
    )
    return checks


def report_from_checks(
    root: Path,
    spec_path: Path,
    spec: dict[str, Any],
    checks: list[Check],
) -> dict[str, Any]:
    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    overall = "fail" if status_counts.get("fail", 0) else "ready_to_implement"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local preflight for the planned real-reuse benchmark. It checks "
            "task definitions, conditions, reference-score boundaries, source "
            "links, and planned artifact paths. It does not execute real tasks "
            "or claim downstream success."
        ),
        "overall_status": overall,
        "spec_path": relative(root, spec_path),
        "task_count": len(spec.get("tasks", [])) if spec else 0,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    lines = [
        "# Real-Reuse Benchmark Spec Preflight",
        "",
        "Evidence boundary: this is a local preflight for the planned "
        "real-reuse benchmark. It does not run any paper-task and does not "
        "claim downstream task success.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Spec path: {report['spec_path']}",
        f"- Task count: {report['task_count']}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check the planned real-reuse benchmark spec.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--spec", type=Path, default=Path("benchmarks/real_reuse/real_reuse_v0.json"))
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "spec_preflight.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "spec_preflight.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if the local spec preflight fails.")
    args = parser.parse_args()

    report = build_report(args.root, args.spec)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
