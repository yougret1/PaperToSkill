#!/usr/bin/env python
"""Check the planned real-reuse benchmark specification."""

from __future__ import annotations

import argparse
import hashlib
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
EXPECTED_FULL_EXCERPT_CONDITION = "full_excerpt"
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
EXPECTED_CANDIDATE_STATUS = "candidate_assets_selected_preparation_pending"
EXPECTED_ASSET_LOCK_STATUS = "asset_lock_ready_preparation_pending"
EXPECTED_PREPARED_ASSET_STATUS = "prepared_assets_ready_for_dry_scoring"
EXPECTED_REFLEXION_PREPARED_ASSET_TASKS = {"REF-T1", "REF-T2"}
EXPECTED_SNAPATAC2_PREPARED_ASSET_TASKS = {"SNAP-T1", "SNAP-T2"}
EXPECTED_PREPARED_ASSET_TASKS = EXPECTED_REFLEXION_PREPARED_ASSET_TASKS | EXPECTED_SNAPATAC2_PREPARED_ASSET_TASKS


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


def expected_task_spec_conditions(task_id: str) -> set[str]:
    conditions = set(EXPECTED_PRIMARY_CONDITIONS)
    if task_id in EXPECTED_SANITY_TASKS:
        conditions.add(EXPECTED_FULL_EXCERPT_CONDITION)
    return conditions


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
    checks.extend(fixture_candidate_checks(root, spec_path, tasks))
    checks.extend(asset_lock_checks(root, spec_path, tasks))
    checks.extend(prepared_asset_checks(root, spec_path, tasks))
    checks.extend(reflexion_runner_checks(root, spec_path))
    checks.extend(aide_runner_checks(root, spec_path))
    checks.extend(swe_agent_skill_checks(root, spec_path))
    checks.extend(swe_runner_checks(root, spec_path))
    checks.extend(snapatac2_skill_checks(root, spec_path))
    checks.extend(snapatac2_runner_checks(root, spec_path))
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
        condition_items = task_spec.get("conditions", [])
        conditions = {condition.get("id") for condition in condition_items}
        condition_by_id = {str(condition.get("id")): condition for condition in condition_items}
        expected_conditions = expected_task_spec_conditions(task_id)
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
                    "ready" if conditions == expected_conditions else "fail",
                    "conditions=" + ",".join(sorted(str(condition) for condition in conditions)),
                    relative(root, task_spec_path),
                ),
                Check(
                    f"{prefix}_task_spec_full_excerpt_scope",
                    "ready"
                    if (
                        task_id not in EXPECTED_SANITY_TASKS
                        and EXPECTED_FULL_EXCERPT_CONDITION not in conditions
                    )
                    or (
                        task_id in EXPECTED_SANITY_TASKS
                        and condition_by_id.get(EXPECTED_FULL_EXCERPT_CONDITION, {}).get("context_kind")
                        == "full_paper_excerpt_sanity"
                        and condition_by_id.get(EXPECTED_FULL_EXCERPT_CONDITION, {}).get("context_path")
                        == f"papers/extracted/{task.get('source_paper_id')}.txt"
                    )
                    else "fail",
                    "full_excerpt="
                    + str(condition_by_id.get(EXPECTED_FULL_EXCERPT_CONDITION, {}).get("context_path", "absent")),
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


def fixture_candidate_checks(root: Path, spec_path: Path, tasks: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    present_fixture_candidates: set[str] = set()
    for task_id in sorted(tasks):
        prefix = task_id.lower().replace("-", "_")
        candidate_path = root / "benchmarks" / "real_reuse" / "fixture_candidates" / f"{task_id}.json"
        task_spec_path = root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json"
        fixture_path = root / "benchmarks" / "real_reuse" / "fixtures" / f"{task_id}.json"
        if not candidate_path.exists():
            checks.append(
                Check(
                    f"{prefix}_fixture_candidate_present",
                    "fail",
                    "missing",
                    relative(root, candidate_path),
                )
            )
            continue
        candidate = load_json(candidate_path)
        present_fixture_candidates.add(task_id)
        task_spec = load_json(task_spec_path) if task_spec_path.exists() else {}
        fixture = load_json(fixture_path) if fixture_path.exists() else {}
        source_urls = candidate.get("source_urls", [])
        source_url_ids = {str(item.get("id", "")) for item in source_urls}
        candidate_assets = candidate.get("candidate_assets", [])
        candidate_asset_slots = {str(item.get("slot", "")) for item in candidate_assets}
        fixture_asset_slots = {str(item.get("id", "")) for item in fixture.get("asset_slots", [])}
        preparation_plan = candidate.get("preparation_plan", {})
        preparation_commands = preparation_plan.get("commands", [])
        scoring_plan = candidate.get("scoring_plan", {})
        boundary = str(candidate.get("evidence_boundary", "")).lower()
        selected = candidate.get("selected_candidate", {})

        checks.extend(
            [
                Check(
                    f"{prefix}_fixture_candidate_present",
                    "ready",
                    "present",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_identity",
                    "ready"
                    if candidate.get("task_id") == task_id
                    and candidate.get("source_paper_id") == tasks[task_id].get("source_paper_id")
                    and candidate.get("task_spec") == f"benchmarks/real_reuse/tasks/{task_id}.json"
                    and candidate.get("fixture_manifest") == f"benchmarks/real_reuse/fixtures/{task_id}.json"
                    else "fail",
                    f"task_id={candidate.get('task_id')}; source_paper_id={candidate.get('source_paper_id')}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_status",
                    "ready" if candidate.get("status") == EXPECTED_CANDIDATE_STATUS else "fail",
                    f"status={candidate.get('status')}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_selected",
                    "ready"
                    if selected.get("id")
                    and selected.get("candidate_status") == "selected_for_preparation"
                    and selected.get("relation_to_source_paper")
                    else "fail",
                    str(selected.get("id", "")) or "missing selected candidate",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_source_urls",
                    "ready"
                    if len(source_urls) >= 3
                    and all(str(item.get("url", "")).startswith("https://") for item in source_urls)
                    and all(item.get("checked_on") for item in source_urls)
                    and all(item.get("source_type") == "primary_source_or_official_distribution" for item in source_urls)
                    else "fail",
                    f"source_urls={len(source_urls)}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_assets_match_slots",
                    "ready"
                    if fixture_asset_slots <= candidate_asset_slots
                    and all(asset.get("source_url_id") in source_url_ids for asset in candidate_assets)
                    else "fail",
                    "asset_slots=" + ",".join(sorted(candidate_asset_slots)),
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_assets_not_downloaded",
                    "ready"
                    if candidate_assets
                    and all(asset.get("materialization_status") == "not_downloaded" for asset in candidate_assets)
                    and all(asset.get("license_status") == "review_required_before_use" for asset in candidate_assets)
                    else "fail",
                    f"candidate_assets={len(candidate_assets)}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_preparation_plan",
                    "ready"
                    if preparation_plan.get("preparation_status") == "not_started"
                    and preparation_plan.get("external_project_root") == "D:/a_work/gitee"
                    and len(preparation_commands) >= 2
                    and any("prepare_real_reuse" in str(command) for command in preparation_commands)
                    and "never commit" in str(preparation_plan.get("credentials_policy", "")).lower()
                    else "fail",
                    f"commands={len(preparation_commands)}; status={preparation_plan.get('preparation_status')}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_scoring_plan",
                    "ready"
                    if scoring_plan.get("scorer_status") == "to_implement_next_phase"
                    and scoring_plan.get("metric_name") == task_spec.get("metric_contract", {}).get("name")
                    and "score_real_reuse" in str(scoring_plan.get("scoring_command_template", ""))
                    else "fail",
                    f"metric={scoring_plan.get('metric_name')}; scorer_status={scoring_plan.get('scorer_status')}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_no_mid_run_human",
                    "ready"
                    if candidate.get("run_controls", {}).get("first_pass_human_intervention") == "none_mid_run"
                    and candidate.get("run_controls", {}).get("same_run_budget_across_conditions") is True
                    else "fail",
                    f"first_pass_human_intervention={candidate.get('run_controls', {}).get('first_pass_human_intervention')}",
                    relative(root, candidate_path),
                ),
                Check(
                    f"{prefix}_fixture_candidate_boundary",
                    "ready"
                    if "does not" in boundary
                    and "execute tasks" in boundary
                    and "downstream task-success results" in boundary
                    else "fail",
                    candidate.get("evidence_boundary", ""),
                    relative(root, candidate_path),
                ),
            ]
        )
    checks.append(
        Check(
            "real_reuse_fixture_candidates_materialized",
            "ready" if present_fixture_candidates == EXPECTED_MAIN_TASKS else "fail",
            "candidates=" + ",".join(sorted(present_fixture_candidates)),
            relative(root, spec_path),
        )
    )
    return checks


def asset_lock_checks(root: Path, spec_path: Path, tasks: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    present_asset_locks: set[str] = set()
    for task_id in sorted(tasks):
        prefix = task_id.lower().replace("-", "_")
        lock_path = root / "benchmarks" / "real_reuse" / "asset_locks" / f"{task_id}.json"
        task_spec_path = root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json"
        fixture_path = root / "benchmarks" / "real_reuse" / "fixtures" / f"{task_id}.json"
        candidate_path = root / "benchmarks" / "real_reuse" / "fixture_candidates" / f"{task_id}.json"
        if not lock_path.exists():
            checks.append(
                Check(
                    f"{prefix}_asset_lock_present",
                    "fail",
                    "missing",
                    relative(root, lock_path),
                )
            )
            continue
        lock = load_json(lock_path)
        present_asset_locks.add(task_id)
        task_spec = load_json(task_spec_path) if task_spec_path.exists() else {}
        fixture = load_json(fixture_path) if fixture_path.exists() else {}
        candidate = load_json(candidate_path) if candidate_path.exists() else {}
        asset_slot_locks = lock.get("asset_slot_locks", [])
        locked_slots = {str(item.get("slot", "")) for item in asset_slot_locks}
        fixture_asset_slots = {str(item.get("id", "")) for item in fixture.get("asset_slots", [])}
        source_revision_locks = lock.get("source_revision_locks", [])
        observed_locks = [item for item in source_revision_locks if item.get("observed_revision")]
        locked_instance = lock.get("locked_task_instance", {})
        preparation_contract = lock.get("preparation_contract", {})
        scoring_lock = lock.get("scoring_lock", {})
        local_targets = lock.get("local_materialization_targets", {})
        boundary = str(lock.get("evidence_boundary", "")).lower()
        hidden_assets = preparation_contract.get("hidden_from_model", [])

        checks.extend(
            [
                Check(
                    f"{prefix}_asset_lock_present",
                    "ready",
                    "present",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_identity",
                    "ready"
                    if lock.get("task_id") == task_id
                    and lock.get("source_paper_id") == tasks[task_id].get("source_paper_id")
                    and lock.get("task_spec") == f"benchmarks/real_reuse/tasks/{task_id}.json"
                    and lock.get("fixture_manifest") == f"benchmarks/real_reuse/fixtures/{task_id}.json"
                    and lock.get("fixture_candidate") == f"benchmarks/real_reuse/fixture_candidates/{task_id}.json"
                    else "fail",
                    f"task_id={lock.get('task_id')}; source_paper_id={lock.get('source_paper_id')}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_status",
                    "ready" if lock.get("status") == EXPECTED_ASSET_LOCK_STATUS else "fail",
                    f"status={lock.get('status')}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_selected_candidate_matches",
                    "ready"
                    if lock.get("selected_candidate_id") == candidate.get("selected_candidate", {}).get("id")
                    else "fail",
                    str(lock.get("selected_candidate_id", "")),
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_instance_locked",
                    "ready"
                    if locked_instance.get("source_kind")
                    and any(
                        key in locked_instance
                        for key in ("local_instance_id", "instance_id", "example_id", "task_id", "dataset_function")
                    )
                    else "fail",
                    str(locked_instance),
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_source_revisions",
                    "ready"
                    if len(source_revision_locks) >= 3
                    and observed_locks
                    and all(item.get("must_reverify_before_materialization") is True for item in source_revision_locks)
                    else "fail",
                    f"source_locks={len(source_revision_locks)}; observed={len(observed_locks)}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_slots_match_fixture",
                    "ready"
                    if fixture_asset_slots <= locked_slots
                    and asset_slot_locks
                    and all(item.get("materialization_status") == "not_materialized" for item in asset_slot_locks)
                    else "fail",
                    "asset_slots=" + ",".join(sorted(locked_slots)),
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_local_targets",
                    "ready"
                    if local_targets.get("asset_dir") == f"benchmarks/real_reuse/assets/{task_id}"
                    and local_targets.get("external_project_root") == "D:/a_work/gitee"
                    and str(local_targets.get("run_dir", "")).startswith(f"results/real_reuse/runs/{task_id}/")
                    else "fail",
                    str(local_targets),
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_preparation_contract",
                    "ready"
                    if preparation_contract.get("status") == "not_started"
                    and str(preparation_contract.get("preparer", "")).startswith("scripts/prepare_real_reuse_")
                    and len(preparation_contract.get("must_complete_before_model_run", [])) >= 4
                    and "Never commit" in str(preparation_contract.get("credential_policy", ""))
                    else "fail",
                    f"preparer={preparation_contract.get('preparer')}; status={preparation_contract.get('status')}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_hidden_assets",
                    "ready" if hidden_assets else "fail",
                    ",".join(str(item) for item in hidden_assets) or "missing hidden asset policy",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_scoring_contract",
                    "ready"
                    if str(scoring_lock.get("scorer", "")).startswith("scripts/score_real_reuse_")
                    and scoring_lock.get("metric_name") == task_spec.get("metric_contract", {}).get("name")
                    and scoring_lock.get("raw_row_schema") == task_spec.get("raw_row_schema")
                    and "must stay out of model-visible context" in str(scoring_lock.get("answer_or_gold_policy", ""))
                    else "fail",
                    f"metric={scoring_lock.get('metric_name')}; scorer={scoring_lock.get('scorer')}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_no_mid_run_human",
                    "ready"
                    if lock.get("run_control_lock", {}).get("first_pass_human_intervention") == "none_mid_run"
                    and lock.get("run_control_lock", {}).get("same_run_budget_across_conditions") is True
                    else "fail",
                    f"first_pass_human_intervention={lock.get('run_control_lock', {}).get('first_pass_human_intervention')}",
                    relative(root, lock_path),
                ),
                Check(
                    f"{prefix}_asset_lock_boundary",
                    "ready"
                    if "does not download assets" in boundary
                    and "score outputs" in boundary
                    and "downstream task-success evidence" in boundary
                    else "fail",
                    lock.get("evidence_boundary", ""),
                    relative(root, lock_path),
                ),
            ]
        )
    checks.append(
        Check(
            "real_reuse_asset_locks_materialized",
            "ready" if present_asset_locks == EXPECTED_MAIN_TASKS else "fail",
            "asset_locks=" + ",".join(sorted(present_asset_locks)),
            relative(root, spec_path),
        )
    )
    return checks


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepared_asset_checks(root: Path, spec_path: Path, tasks: dict[str, dict[str, Any]]) -> list[Check]:
    checks: list[Check] = []
    prepared_tasks: set[str] = set()
    for task_id in sorted(EXPECTED_PREPARED_ASSET_TASKS):
        prefix = task_id.lower().replace("-", "_")
        if task_id not in tasks:
            checks.append(
                Check(
                    f"{prefix}_prepared_asset_task_declared",
                    "fail",
                    "missing task in master spec",
                    relative(root, spec_path),
                )
            )
            continue

        manifest_path = root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"
        if not manifest_path.exists():
            checks.append(
                Check(
                    f"{prefix}_prepared_asset_manifest_present",
                    "fail",
                    "missing",
                    relative(root, manifest_path),
                )
            )
            continue

        manifest = load_json(manifest_path)
        prepared_tasks.add(task_id)
        files = manifest.get("files", [])
        condition_contexts = manifest.get("condition_contexts", [])
        model_visible = [item for item in files if item.get("visibility") == "model_visible"]
        scorer_only = [item for item in files if item.get("visibility") == "scorer_only"]
        condition_slots = {str(item.get("condition", "")) for item in condition_contexts}
        file_paths = [root / str(item.get("path", "")) for item in files]
        context_paths = [root / str(item.get("path", "")) for item in condition_contexts]
        existing_paths = [path for path in file_paths + context_paths if path.exists()]
        sha_mismatches = [
            str(item.get("path", ""))
            for item in files
            if (root / str(item.get("path", ""))).exists()
            and item.get("sha256")
            and sha256_file(root / str(item.get("path", ""))) != item.get("sha256")
        ]
        hidden = set(str(path) for path in manifest.get("hidden_from_model", []))
        scorer_paths = {str(item.get("path", "")) for item in scorer_only}
        boundary = str(manifest.get("evidence_boundary", "")).lower()

        checks.extend(
            [
                Check(
                    f"{prefix}_prepared_asset_manifest_present",
                    "ready",
                    "present",
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_identity",
                    "ready"
                    if manifest.get("task_id") == task_id
                    and manifest.get("source_paper_id") == tasks[task_id].get("source_paper_id")
                    else "fail",
                    f"task_id={manifest.get('task_id')}; source_paper_id={manifest.get('source_paper_id')}",
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_status",
                    "ready" if manifest.get("status") == EXPECTED_PREPARED_ASSET_STATUS else "fail",
                    f"status={manifest.get('status')}",
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_files_exist",
                    "ready" if len(existing_paths) == len(file_paths) + len(context_paths) else "fail",
                    f"files={len(file_paths)}; contexts={len(context_paths)}; existing={len(existing_paths)}",
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_sha256",
                    "ready" if not sha_mismatches and len(files) >= 5 else "fail",
                    "ok" if not sha_mismatches else "mismatch=" + ",".join(sha_mismatches),
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_visibility_split",
                    "ready" if model_visible and scorer_only and scorer_paths <= hidden else "fail",
                    f"model_visible={len(model_visible)}; scorer_only={len(scorer_only)}; hidden={len(hidden)}",
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_condition_contexts",
                    "ready" if condition_slots == EXPECTED_PRIMARY_CONDITIONS else "fail",
                    "conditions=" + ",".join(sorted(condition_slots)),
                    relative(root, manifest_path),
                ),
                Check(
                    f"{prefix}_prepared_asset_boundary",
                    "ready"
                    if "does not run a model" in boundary
                    and "compare summary against papertoskill" in boundary
                    and "claim task success" in boundary
                    else "fail",
                    manifest.get("evidence_boundary", ""),
                    relative(root, manifest_path),
                ),
            ]
        )

    checks.append(
        Check(
            "real_reuse_prepared_assets_reflexion_materialized",
            "ready" if EXPECTED_REFLEXION_PREPARED_ASSET_TASKS <= prepared_tasks else "fail",
            "prepared_tasks=" + ",".join(sorted(prepared_tasks & EXPECTED_REFLEXION_PREPARED_ASSET_TASKS)),
            relative(root, spec_path),
        )
    )
    checks.append(
        Check(
            "real_reuse_prepared_assets_snapatac2_materialized",
            "ready" if EXPECTED_SNAPATAC2_PREPARED_ASSET_TASKS <= prepared_tasks else "fail",
            "prepared_tasks=" + ",".join(sorted(prepared_tasks & EXPECTED_SNAPATAC2_PREPARED_ASSET_TASKS)),
            relative(root, spec_path),
        )
    )
    checks.append(
        Check(
            "real_reuse_prepared_assets_required_materialized",
            "ready" if prepared_tasks == EXPECTED_PREPARED_ASSET_TASKS else "fail",
            "prepared_tasks=" + ",".join(sorted(prepared_tasks)),
            relative(root, spec_path),
        )
    )
    return checks


def reflexion_runner_checks(root: Path, spec_path: Path) -> list[Check]:
    runner_path = root / "scripts" / "run_real_reuse_reflexion.py"
    if not runner_path.exists():
        return [
            Check(
                "real_reuse_reflexion_runner_present",
                "fail",
                "missing",
                relative(root, runner_path),
            )
        ]

    text = runner_path.read_text(encoding="utf-8")
    required_snippets = {
        "--fixture-response-dir",
        "raw_rows.jsonl",
        "provider_or_model_error",
        "score_ref_t1",
        "score_ref_t2",
        "unsupported_errors_status",
        "does not complete the full",
    }
    missing = sorted(snippet for snippet in required_snippets if snippet not in text)
    return [
        Check(
            "real_reuse_reflexion_runner_present",
            "ready",
            "present",
            relative(root, runner_path),
        ),
        Check(
            "real_reuse_reflexion_runner_contract_ready",
            "ready" if not missing else "fail",
            "runner contract snippets present" if not missing else "missing=" + ",".join(missing),
            relative(root, runner_path),
        ),
    ]


def aide_runner_checks(root: Path, spec_path: Path) -> list[Check]:
    preparer_path = root / "scripts" / "prepare_real_reuse_aide_fixture.py"
    scorer_path = root / "scripts" / "score_real_reuse_aide.py"
    runner_path = root / "scripts" / "run_real_reuse_aide.py"
    checks = [
        Check(
            "real_reuse_aide_preparer_present",
            "ready" if preparer_path.exists() else "fail",
            "present" if preparer_path.exists() else "missing",
            relative(root, preparer_path),
        ),
        Check(
            "real_reuse_aide_scorer_present",
            "ready" if scorer_path.exists() else "fail",
            "present" if scorer_path.exists() else "missing",
            relative(root, scorer_path),
        ),
        Check(
            "real_reuse_aide_runner_present",
            "ready" if runner_path.exists() else "fail",
            "present" if runner_path.exists() else "missing",
            relative(root, runner_path),
        ),
    ]
    if not runner_path.exists() or not preparer_path.exists() or not scorer_path.exists():
        checks.append(
            Check(
                "real_reuse_aide_runner_contract_ready",
                "fail",
                "missing AIDE execution-layer script",
                relative(root, runner_path),
            )
        )
        return checks

    runner_text = runner_path.read_text(encoding="utf-8")
    preparer_text = preparer_path.read_text(encoding="utf-8")
    scorer_text = scorer_path.read_text(encoding="utf-8")
    required_snippets = {
        "--fixture-response-dir": runner_text,
        "raw_rows.jsonl": runner_text,
        "score_candidate": runner_text,
        "unsupported_errors_status": runner_text,
        "validation_labels": preparer_text,
        "scorer_only": preparer_text,
        "baseline_score": scorer_text,
        "submission.csv": scorer_text,
    }
    missing = sorted(snippet for snippet, text in required_snippets.items() if snippet not in text)
    checks.append(
        Check(
            "real_reuse_aide_runner_contract_ready",
            "ready" if not missing else "fail",
            "AIDE execution-layer contract snippets present" if not missing else "missing=" + ",".join(missing),
            relative(root, runner_path),
        )
    )
    return checks


def swe_agent_skill_checks(root: Path, spec_path: Path) -> list[Check]:
    skill_path = root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md"
    source_map_path = root / "generated_skills" / "real_reuse" / "swe_agent" / "references" / "source_map.json"
    rubric_path = root / "results" / "evaluations" / "swe_agent_rubric_v0.json"
    source_span_path = root / "results" / "evaluations" / "swe_agent_auto_source_span_validation_v0.json"
    note_report_path = root / "results" / "evaluations" / "swe_agent_auto_note_scaffold_v0.json"
    checks = [
        Check(
            "real_reuse_swe_agent_skill_present",
            "ready" if skill_path.exists() else "fail",
            "present" if skill_path.exists() else "missing",
            relative(root, skill_path),
        ),
        Check(
            "real_reuse_swe_agent_source_map_present",
            "ready" if source_map_path.exists() else "fail",
            "present" if source_map_path.exists() else "missing",
            relative(root, source_map_path),
        ),
        Check(
            "real_reuse_swe_agent_auto_note_report_present",
            "ready" if note_report_path.exists() else "fail",
            "present" if note_report_path.exists() else "missing",
            relative(root, note_report_path),
        ),
    ]
    if skill_path.exists():
        skill_text = skill_path.read_text(encoding="utf-8")
        required_snippets = {
            "agent-computer interface",
            "find_file",
            "search_file",
            "edit command",
            "linter",
            "Docker",
            "Source anchors:",
        }
        missing = sorted(snippet for snippet in required_snippets if snippet not in skill_text)
        checks.append(
            Check(
                "real_reuse_swe_agent_skill_contract_ready",
                "ready" if not missing else "fail",
                "SWE-agent skill contract snippets present" if not missing else "missing=" + ",".join(missing),
                relative(root, skill_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_swe_agent_skill_contract_ready",
                "fail",
                "missing SWE-agent skill",
                relative(root, skill_path),
            )
        )

    if rubric_path.exists():
        rubric = load_json(rubric_path)
        score = float(rubric.get("score", 0))
        max_score = float(rubric.get("max_score", 20))
        checks.append(
            Check(
                "real_reuse_swe_agent_rubric_ready",
                "ready" if score == max_score else "fail",
                f"score={score:g}/{max_score:g}",
                relative(root, rubric_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_swe_agent_rubric_ready",
                "fail",
                "missing",
                relative(root, rubric_path),
            )
        )

    if source_span_path.exists():
        source_span = load_json(source_span_path)
        result = source_span.get("results", [{}])[0]
        support_rate = float(result.get("support_rate", 0))
        invalid_ranges = int(result.get("invalid_ranges", 0))
        checks.append(
            Check(
                "real_reuse_swe_agent_source_span_ready",
                "ready" if support_rate >= 0.9 and invalid_ranges == 0 else "fail",
                f"support_rate={support_rate:g}; invalid_ranges={invalid_ranges}",
                relative(root, source_span_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_swe_agent_source_span_ready",
                "fail",
                "missing",
                relative(root, source_span_path),
            )
        )
    return checks


def swe_runner_checks(root: Path, spec_path: Path) -> list[Check]:
    preparer_path = root / "scripts" / "prepare_real_reuse_swe_fixture.py"
    scorer_path = root / "scripts" / "score_real_reuse_swe.py"
    runner_path = root / "scripts" / "run_real_reuse_swe.py"
    checks = [
        Check(
            "real_reuse_swe_preparer_present",
            "ready" if preparer_path.exists() else "fail",
            "present" if preparer_path.exists() else "missing",
            relative(root, preparer_path),
        ),
        Check(
            "real_reuse_swe_scorer_present",
            "ready" if scorer_path.exists() else "fail",
            "present" if scorer_path.exists() else "missing",
            relative(root, scorer_path),
        ),
        Check(
            "real_reuse_swe_runner_present",
            "ready" if runner_path.exists() else "fail",
            "present" if runner_path.exists() else "missing",
            relative(root, runner_path),
        ),
    ]
    if not runner_path.exists() or not preparer_path.exists() or not scorer_path.exists():
        checks.append(
            Check(
                "real_reuse_swe_runner_contract_ready",
                "fail",
                "missing SWE execution-layer script",
                relative(root, runner_path),
            )
        )
        return checks

    runner_text = runner_path.read_text(encoding="utf-8")
    preparer_text = preparer_path.read_text(encoding="utf-8")
    scorer_text = scorer_path.read_text(encoding="utf-8")
    required_snippets = {
        "--fixture-response-dir": runner_text,
        "raw_rows.jsonl": runner_text,
        "score_patch": runner_text,
        "unsupported_errors_status": runner_text,
        "provider_or_model_error": runner_text,
        "missing_fixture_assets": runner_text,
        "unified diff patch": runner_text,
        "gold_patch": preparer_text,
        "hidden_from_model": preparer_text,
        "target_test_command": preparer_text,
        "git apply": scorer_text,
        "test_command": scorer_text,
        "patch_apply_failed": scorer_text,
    }
    missing = sorted(snippet for snippet, text in required_snippets.items() if snippet not in text)
    checks.append(
        Check(
            "real_reuse_swe_runner_contract_ready",
            "ready" if not missing else "fail",
            "SWE execution-layer contract snippets present" if not missing else "missing=" + ",".join(missing),
            relative(root, runner_path),
        )
    )
    return checks


def snapatac2_skill_checks(root: Path, spec_path: Path) -> list[Check]:
    skill_path = root / "generated_skills" / "real_reuse" / "snapatac2" / "SKILL.md"
    source_map_path = root / "generated_skills" / "real_reuse" / "snapatac2" / "references" / "source_map.json"
    rubric_path = root / "results" / "evaluations" / "snapatac2_rubric_v0.json"
    source_span_path = root / "results" / "evaluations" / "snapatac2_auto_source_span_validation_v0.json"
    note_report_path = root / "results" / "evaluations" / "snapatac2_auto_note_scaffold_v0.json"
    checks = [
        Check(
            "real_reuse_snapatac2_skill_present",
            "ready" if skill_path.exists() else "fail",
            "present" if skill_path.exists() else "missing",
            relative(root, skill_path),
        ),
        Check(
            "real_reuse_snapatac2_source_map_present",
            "ready" if source_map_path.exists() else "fail",
            "present" if source_map_path.exists() else "missing",
            relative(root, source_map_path),
        ),
        Check(
            "real_reuse_snapatac2_auto_note_report_present",
            "ready" if note_report_path.exists() else "fail",
            "present" if note_report_path.exists() else "missing",
            relative(root, note_report_path),
        ),
    ]
    if skill_path.exists():
        skill_text = skill_path.read_text(encoding="utf-8")
        required_snippets = {
            "matrix-free spectral embedding",
            "Lanczos",
            "embedding/clustering",
            "multi-view spectral embedding",
            "ARI",
            "cosine",
            "Source anchors:",
        }
        missing = sorted(snippet for snippet in required_snippets if snippet not in skill_text)
        checks.append(
            Check(
                "real_reuse_snapatac2_skill_contract_ready",
                "ready" if not missing else "fail",
                "SnapATAC2 skill contract snippets present" if not missing else "missing=" + ",".join(missing),
                relative(root, skill_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_snapatac2_skill_contract_ready",
                "fail",
                "missing SnapATAC2 skill",
                relative(root, skill_path),
            )
        )

    if rubric_path.exists():
        rubric = load_json(rubric_path)
        score = float(rubric.get("score", 0))
        max_score = float(rubric.get("max_score", 20))
        checks.append(
            Check(
                "real_reuse_snapatac2_rubric_ready",
                "ready" if score == max_score else "fail",
                f"score={score:g}/{max_score:g}",
                relative(root, rubric_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_snapatac2_rubric_ready",
                "fail",
                "missing",
                relative(root, rubric_path),
            )
        )

    if source_span_path.exists():
        source_span = load_json(source_span_path)
        result = source_span.get("results", [{}])[0]
        support_rate = float(result.get("support_rate", 0))
        invalid_ranges = int(result.get("invalid_ranges", 0))
        checks.append(
            Check(
                "real_reuse_snapatac2_source_span_ready",
                "ready" if support_rate >= 0.9 and invalid_ranges == 0 else "fail",
                f"support_rate={support_rate:g}; invalid_ranges={invalid_ranges}",
                relative(root, source_span_path),
            )
        )
    else:
        checks.append(
            Check(
                "real_reuse_snapatac2_source_span_ready",
                "fail",
                "missing",
                relative(root, source_span_path),
            )
        )
    return checks


def snapatac2_runner_checks(root: Path, spec_path: Path) -> list[Check]:
    preparer_path = root / "scripts" / "prepare_real_reuse_snapatac2_fixture.py"
    scorer_path = root / "scripts" / "score_real_reuse_snapatac2.py"
    runner_path = root / "scripts" / "run_real_reuse_snapatac2.py"
    checks = [
        Check(
            "real_reuse_snapatac2_preparer_present",
            "ready" if preparer_path.exists() else "fail",
            "present" if preparer_path.exists() else "missing",
            relative(root, preparer_path),
        ),
        Check(
            "real_reuse_snapatac2_scorer_present",
            "ready" if scorer_path.exists() else "fail",
            "present" if scorer_path.exists() else "missing",
            relative(root, scorer_path),
        ),
        Check(
            "real_reuse_snapatac2_runner_present",
            "ready" if runner_path.exists() else "fail",
            "present" if runner_path.exists() else "missing",
            relative(root, runner_path),
        ),
    ]
    if not runner_path.exists() or not preparer_path.exists() or not scorer_path.exists():
        checks.append(
            Check(
                "real_reuse_snapatac2_runner_contract_ready",
                "fail",
                "missing SnapATAC2 execution-layer script",
                relative(root, runner_path),
            )
        )
        return checks

    runner_text = runner_path.read_text(encoding="utf-8")
    preparer_text = preparer_path.read_text(encoding="utf-8")
    scorer_text = scorer_path.read_text(encoding="utf-8")
    required_snippets = {
        "--fixture-response-dir": runner_text,
        "raw_rows.jsonl": runner_text,
        "score_artifact": runner_text,
        "unsupported_errors_status": runner_text,
        "provider_or_model_error": runner_text,
        "missing_fixture_assets": runner_text,
        "candidate_output.json": runner_text,
        "reference_labels_or_proxy": preparer_text,
        "hidden_from_model": preparer_text,
        "expected_artifact_schema": preparer_text,
        "resource_budget": preparer_text,
        "adjusted_rand_index": scorer_text,
        "normalized_mutual_info": scorer_text,
        "runtime_memory_quality": scorer_text,
        "ari_nmi_runtime_memory": scorer_text,
    }
    missing = sorted(snippet for snippet, text in required_snippets.items() if snippet not in text)
    checks.append(
        Check(
            "real_reuse_snapatac2_runner_contract_ready",
            "ready" if not missing else "fail",
            "SnapATAC2 execution-layer contract snippets present" if not missing else "missing=" + ",".join(missing),
            relative(root, runner_path),
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
