#!/usr/bin/env python3
"""Package verified SkillsBench candidate-validation evidence for dataDetail.

The raw, attempt-level run remains under ``research/workflow_runs``.  This
script creates a compact, path-neutral report package after independently
checking the hash bindings emitted by the screening and confirmatory analyses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "skillsbench-candidate-validation-report-package-v1"
DEFER_STATES = {"baseline-inconclusive", "full-inconclusive", "evidence-inconclusive"}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"required JSON file is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(text.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


def hash_binding(actual_path: Path, expected: str, label: str) -> str:
    actual = sha256_file(actual_path)
    require(actual == expected, f"{label} hash mismatch")
    return actual


def sha256_value(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


def amendment_reference(
    payload: dict[str, Any], *, source: Path, label: str
) -> tuple[Path, str] | None:
    value = payload.get("candidate_amendment")
    if value is None:
        return None
    if isinstance(value, str):
        path_value = value
        digest = sha256_value(payload, "candidate_amendment_sha256", "amendment_sha256")
    else:
        require(isinstance(value, dict), f"{label} candidate_amendment must be a path or object")
        path_value = value.get("path") or value.get("file")
        digest = sha256_value(value, "sha256", "candidate_amendment_sha256")
    require(isinstance(path_value, str) and path_value, f"{label} amendment path is missing")
    require(
        isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest) is not None,
        f"{label} amendment SHA-256 is invalid",
    )
    path = Path(path_value)
    if not path.is_absolute():
        path = source.parent / path
    return path.resolve(), digest


def candidate_tree_hashes(amendment: dict[str, Any]) -> tuple[str | None, str | None]:
    old_hash = sha256_value(
        amendment,
        "old_candidate_tree_sha256",
        "old_tree_sha256",
        "previous_candidate_tree_sha256",
    )
    new_hash = sha256_value(
        amendment,
        "new_candidate_tree_sha256",
        "new_tree_sha256",
        "amended_candidate_tree_sha256",
    )
    hashes = amendment.get("candidate_tree_sha256")
    if isinstance(hashes, dict):
        old_hash = old_hash or sha256_value(hashes, "old", "before")
        new_hash = new_hash or sha256_value(hashes, "new", "after")
    candidate = amendment.get("candidate")
    if isinstance(candidate, dict):
        old_hash = old_hash or sha256_value(candidate, "P1_skills_sha256")
        new_hash = new_hash or sha256_value(candidate, "P2_skills_sha256")
    return old_hash, new_hash


def validate_candidate_amendment(amendment: dict[str, Any]) -> None:
    require(
        amendment.get("schema_version")
        == "skillsbench-candidate-validation-amendment-v1",
        "candidate amendment schema changed",
    )
    require(
        isinstance(amendment.get("task_id"), str) and amendment["task_id"],
        "candidate amendment task is missing",
    )
    require(
        amendment.get("outcome_access") == "prohibited",
        "candidate amendment accessed outcomes",
    )
    require(
        amendment.get("candidate_outcomes_used") is False,
        "candidate amendment used P/D outcomes",
    )
    generator = amendment.get("generator")
    require(
        isinstance(generator, dict) or generator is None,
        "candidate amendment generator is invalid",
    )
    generator = generator or amendment
    require(generator.get("mode") == "heuristic/no-llm", "candidate amendment mode changed")
    require(
        type(generator.get("stage")) is int and generator["stage"] == 1,
        "candidate amendment stage must be 1",
    )
    require(generator.get("tscg") is False, "candidate amendment must disable TSCG")
    old_hash, new_hash = candidate_tree_hashes(amendment)
    require(
        isinstance(old_hash, str) and SHA256_PATTERN.fullmatch(old_hash) is not None,
        "candidate amendment old tree SHA-256 is invalid",
    )
    require(
        isinstance(new_hash, str) and SHA256_PATTERN.fullmatch(new_hash) is not None,
        "candidate amendment new tree SHA-256 is invalid",
    )
    require(old_hash != new_hash, "candidate amendment old and new tree hashes are identical")


def screen_label(row: dict[str, Any], candidate: str) -> str:
    consensus = row.get("blind_label_consensus") or {}
    value = consensus.get(candidate)
    return str(value) if value is not None else "unavailable"


def build_summary(
    *,
    final_report: dict[str, Any],
    selection: dict[str, Any],
    screen_protocol: dict[str, Any],
    confirm_protocol: dict[str, Any],
) -> dict[str, Any]:
    screen_tasks = list((screen_protocol.get("main") or {}).get("tasks") or [])
    screen_repetitions = int((screen_protocol.get("main") or {}).get("repetitions") or 0)
    screen_arms = list((screen_protocol.get("executor") or {}).get("conditions") or [])
    screen_pilot_tasks = list((screen_protocol.get("pilot") or {}).get("tasks") or [])
    screen_pilot_repetitions = int(
        (screen_protocol.get("pilot") or {}).get("repetitions") or 0
    )
    confirm_tasks = list(final_report.get("confirmatory_tasks") or [])
    confirm_repetitions = int(final_report.get("repetitions_per_arm") or 0)
    confirm_arms = list((confirm_protocol.get("executor") or {}).get("conditions") or [])
    confirm_pilot_tasks = list((confirm_protocol.get("pilot") or {}).get("tasks") or [])
    confirm_pilot_repetitions = int(
        (confirm_protocol.get("pilot") or {}).get("repetitions") or 0
    )

    screen_rows = []
    for row in selection.get("task_results") or []:
        arms = row.get("arms") or {}
        screen_rows.append(
            {
                "task_id": row.get("task_id"),
                "B_successes": (arms.get("B") or {}).get("successes"),
                "F_successes": (arms.get("F") or {}).get("successes"),
                "B_rows": (arms.get("B") or {}).get("rows"),
                "F_rows": (arms.get("F") or {}).get("rows"),
                "B_valid": (arms.get("B") or {}).get("valid"),
                "F_valid": (arms.get("F") or {}).get("valid"),
                "B_mean_reward": (arms.get("B") or {}).get("mean_reward"),
                "F_mean_reward": (arms.get("F") or {}).get("mean_reward"),
                "repetitions_per_arm": screen_repetitions,
                "P_blind_consensus": screen_label(row, "P"),
                "D_blind_consensus": screen_label(row, "D"),
                "label_eligible": bool(row.get("label_eligible")),
                "eligible": bool(row.get("eligible")),
                "selected": row.get("task_id") in confirm_tasks,
            }
        )

    decision_counts = Counter(str(row.get("state")) for row in final_report.get("decisions") or [])
    preserving = [
        row
        for row in final_report.get("decisions") or []
        if row.get("expected_class") == "intended-preserving"
    ]
    destructive = [
        row
        for row in final_report.get("decisions") or []
        if row.get("expected_class") == "destructive"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "complete",
        "primary_executor": "GPT-5.6 Sol",
        "purpose": (
            "Minimum effective public-benchmark validation of candidate-level "
            "behavioral admission and official verifier compatibility."
        ),
        "screening": {
            "tasks": screen_tasks,
            "conditions": screen_arms,
            "repetitions_per_arm": screen_repetitions,
            "registered_main_rows": len(screen_tasks) * len(screen_arms) * screen_repetitions,
            "pilot_tasks": screen_pilot_tasks,
            "pilot_repetitions_per_arm": screen_pilot_repetitions,
            "registered_pilot_rows": (
                len(screen_pilot_tasks) * len(screen_arms) * screen_pilot_repetitions
            ),
            "candidate_outcomes_used_for_selection": False,
            "task_results": screen_rows,
            "selected_tasks": confirm_tasks,
        },
        "confirmation": {
            "tasks": confirm_tasks,
            "conditions": confirm_arms,
            "repetitions_per_arm": confirm_repetitions,
            "registered_main_rows": len(confirm_tasks) * len(confirm_arms) * confirm_repetitions,
            "pilot_tasks": confirm_pilot_tasks,
            "pilot_repetitions_per_arm": confirm_pilot_repetitions,
            "registered_pilot_rows": (
                len(confirm_pilot_tasks) * len(confirm_arms) * confirm_pilot_repetitions
            ),
            "task_results": final_report.get("task_results") or [],
            "decisions": final_report.get("decisions") or [],
            "decision_counts": dict(sorted(decision_counts.items())),
            "preserving_candidates": {
                "total": len(preserving),
                "accepted": sum(row.get("state") == "Accept" for row in preserving),
                "rejected": sum(row.get("state") == "RejectCandidate" for row in preserving),
                "deferred": sum(row.get("state") in DEFER_STATES for row in preserving),
            },
            "destructive_candidates": {
                "total": len(destructive),
                "accepted": sum(row.get("state") == "Accept" for row in destructive),
                "rejected": sum(row.get("state") == "RejectCandidate" for row in destructive),
                "deferred": sum(row.get("state") in DEFER_STATES for row in destructive),
            },
            "unsafe_accepts": int(final_report.get("unsafe_accepts") or 0),
            "false_rejects": int(final_report.get("false_rejects") or 0),
            "deferrals": int(final_report.get("deferrals") or 0),
        },
        "candidate_construction": {
            "P": "Independent heuristic reducer output; not the official SkillReducer artifact.",
            "D": "Uniform automatic body-drop negative control retaining unchanged YAML frontmatter.",
        },
        "evidence_boundary": final_report.get("boundary") or {},
    }


def summarize_blind_labels(
    blind_labels: dict[str, Any], selection_summary: dict[str, Any]
) -> dict[str, Any]:
    records = blind_labels.get("records") or []
    reviewers = sorted(
        {
            str(row.get("reviewer_id"))
            for row in records
            if isinstance(row, dict) and row.get("reviewer_id")
        }
    )
    tasks = []
    for row in selection_summary["task_results"]:
        tasks.append(
            {
                "task_id": row["task_id"],
                "P_consensus": row["P_blind_consensus"],
                "D_consensus": row["D_blind_consensus"],
                "unanimous_candidate_pair": row["label_eligible"],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "outcome_access": blind_labels.get("outcome_access"),
        "reviewer_count": len(reviewers),
        "reviewer_ids": reviewers,
        "annotation_rows": len(records),
        "task_consensus": tasks,
        "rationales_packaged": False,
    }


def terminal_attestation(
    gate: dict[str, Any],
    *,
    expected_rows: int,
    source_hashes: dict[str, str],
    audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": gate.get("status"),
        "final_reportable": gate.get("final_reportable"),
        "expected_rows": int(gate.get("expected_rows", expected_rows)),
        "terminal_rows": int(gate.get("terminal_rows", expected_rows)),
        "schedule_count_valid": gate.get("schedule_count_valid", True),
        "missing_rows": len(gate.get("missing_execution_ids") or []),
        "unexpected_rows": len(gate.get("unexpected_execution_ids") or []),
        "invalid_rows": len(gate.get("invalid_execution_ids") or []),
        "contaminated_rows": len(gate.get("contaminated_execution_ids") or []),
        "credential_reflection_rows": len(
            gate.get("credential_reflection_execution_ids") or []
        ),
        "protocol_invalid_reasons": gate.get("protocol_invalid_reasons") or [],
        "audit_status": audit.get("status") if audit else "not-required-for-screening",
        "audit_final_reportable": (
            audit.get("final_reportable") if audit else "not-required-for-screening"
        ),
        "source_sha256": source_hashes,
    }


def fmt_count(value: Any, n: Any) -> str:
    return f"{value}/{n}"


def render_report(summary: dict[str, Any]) -> str:
    screening = summary["screening"]
    confirmation = summary["confirmation"]
    preserving = confirmation["preserving_candidates"]
    destructive = confirmation["destructive_candidates"]
    lines = [
        "# SkillsBench Candidate-Level Validation Report",
        "",
        "## Question and design",
        "",
        "This minimum-effective-scale experiment asks whether the frozen behavioral admission "
        "policy can preserve useful candidates while rejecting destructive candidates on public "
        "SkillsBench tasks. GPT-5.6 Sol is the primary executor.",
        "",
        f"The diagnostic screen used {len(screening['tasks'])} tasks, B/F arms, and "
        f"{screening['repetitions_per_arm']} repetitions per arm "
        f"({screening['registered_main_rows']} registered screening rows), preceded by "
        f"{screening['registered_pilot_rows']} integrity-only pilot rows. Task selection used "
        "only B/F outcomes and pre-outcome blind candidate labels. It did not use P/D outcomes.",
        "",
        f"The confirmation used {len(confirmation['tasks'])} selected tasks, B/F/P/D arms, and "
        f"{confirmation['repetitions_per_arm']} repetitions per arm "
        f"({confirmation['registered_main_rows']} registered confirmatory rows), preceded by "
        f"{confirmation['registered_pilot_rows']} integrity-only pilot rows. "
        "B is the no-skill baseline, F is the official full skill bundle, P is an independently "
        "generated intended-preserving reduction, and D is an automatic body-drop negative control.",
        "",
        "## Screening and frozen selection",
        "",
        "| Task | B | F | P blind label | D blind label | Diagnostic | Selected |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in screening["task_results"]:
        n = row["repetitions_per_arm"]
        lines.append(
            f"| {row['task_id']} | {fmt_count(row['B_successes'], n)} | "
            f"{fmt_count(row['F_successes'], n)} | {row['P_blind_consensus']} | "
            f"{row['D_blind_consensus']} | {'yes' if row['eligible'] else 'no'} | "
            f"{'yes' if row['selected'] else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Confirmatory results",
            "",
            "| Task | Candidate | Expected | B | F | Candidate | Effect [95% CI] | Decision |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in confirmation["decisions"]:
        interval = f"{row['effect']:.3f} [{row['ci_low']:.3f}, {row['ci_high']:.3f}]"
        lines.append(
            f"| {row['task_id']} | {row['candidate']} | {row['expected_class']} | "
            f"{fmt_count(row['k_B'], row['n'])} | {fmt_count(row['k_F'], row['n'])} | "
            f"{fmt_count(row['k_S'], row['n'])} | {interval} | {row['state']} |"
        )

    lines.extend(
        [
            "",
            "## What the experiment shows",
            "",
            f"The policy accepted {preserving['accepted']}/{preserving['total']} independently "
            f"labeled preserving candidates and rejected {destructive['rejected']}/"
            f"{destructive['total']} destructive controls. It produced "
            f"{confirmation['unsafe_accepts']} unsafe destructive-candidate accepts, "
            f"{confirmation['false_rejects']} preserving-candidate false rejects, and "
            f"{confirmation['deferrals']} deferred decisions.",
            "",
        ]
    )
    if (
        preserving["accepted"] == preserving["total"]
        and destructive["rejected"] == destructive["total"]
        and preserving["total"] > 0
        and destructive["total"] > 0
    ):
        lines.append(
            "Within these selected tasks, the frozen policy cleanly separated the preserving and "
            "destructive candidates. This is direct evidence that the decision layer can retain "
            "useful reductions and block severe behavioral damage under official verifiers."
        )
    else:
        lines.append(
            "The result should be read by decision state: accepts demonstrate retained utility, "
            "rejections demonstrate detected damage, and inconclusive states demonstrate "
            "withholding rather than a positive or negative classification."
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "This is a deliberately small public-benchmark validation. It supports the behavioral "
            "decision layer and compatibility with official SkillsBench verifiers on the selected "
            "tasks. It does not establish population-wide generalization, paper source-span "
            "fidelity, or end-to-end equivalence between the independent P generator and the "
            "paper's full reduction pipeline. P is an independent heuristic reducer artifact, not "
            "the official SkillReducer output. Screening observations are excluded from the "
            "confirmatory estimates.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SkillsBench Candidate Validation Evidence",
            "",
            "This directory contains the compact report package for the minimum-effective-scale "
            "SkillsBench candidate-level validation. The primary executor is GPT-5.6 Sol.",
            "",
            "Raw prompts, model responses, attempt-level logs, working directories, and run-state "
            "records remain in the git-ignored `research/workflow_runs/skillsbench_candidate_validation_sol` "
            "tree. They are intentionally not duplicated here.",
            "",
            "Files:",
            "",
            "- `REPORT.md`: design, screening, confirmatory results, interpretation, and claim boundary.",
            "- `SUMMARY.json`: path-neutral machine-readable overview.",
            "- `protocol/`, `analysis/`, `annotations/`, and `attestations/`: focused evidence summaries.",
            "- `outputs/final_report.json`: verified analysis output used to generate the report.",
            "- `outputs/binding_manifest.json`: SHA-256 bindings to the source evidence.",
            "- `PACKAGE_MANIFEST.sha256` and `verify_package.py`: offline package-integrity check.",
            "- `scripts/`: the frozen analysis and packaging programs.",
            "",
            "This package records experiment evidence only and does not modify the manuscript.",
            "",
        ]
    )


def package(args: argparse.Namespace) -> dict[str, Any]:
    final_report_path = args.analysis_output / "final_report.json"
    selection_path = args.selection_output / "selection.json"
    confirm_protocol_path = args.selection_output / "confirm_materials" / "protocol.json"
    screen_protocol_path = args.materials / "screen_protocol.json"

    final_report = load_json(final_report_path)
    selection = load_json(selection_path)
    confirm_protocol = load_json(confirm_protocol_path)
    screen_protocol = load_json(screen_protocol_path)
    blind_labels_value = confirm_protocol.get("blind_labels")
    if isinstance(blind_labels_value, str) and blind_labels_value:
        blind_labels_path = Path(blind_labels_value)
        if not blind_labels_path.is_absolute():
            blind_labels_path = confirm_protocol_path.parent / blind_labels_path
        blind_labels_path = blind_labels_path.resolve()
    else:
        blind_labels_path = args.materials / "blind_labels.json"
    blind_labels = load_json(blind_labels_path)
    require(final_report.get("status") == "complete", "final analysis is not complete")
    require(selection.get("status") == "passed", "screening selection did not pass")
    require(
        selection.get("selected_tasks") == final_report.get("confirmatory_tasks"),
        "selected and confirmatory tasks differ",
    )

    selection_amendment = amendment_reference(
        selection, source=selection_path, label="selection"
    )
    protocol_amendment = amendment_reference(
        confirm_protocol, source=confirm_protocol_path, label="confirmatory protocol"
    )
    require(
        (selection_amendment is None) == (protocol_amendment is None),
        "selection and confirmatory protocol amendment declarations differ",
    )
    candidate_amendment_path: Path | None = None
    candidate_amendment_sha256: str | None = None
    candidate_amendment: dict[str, Any] | None = None
    if selection_amendment is not None and protocol_amendment is not None:
        selection_path_value, selection_digest = selection_amendment
        protocol_path_value, protocol_digest = protocol_amendment
        require(selection_digest == protocol_digest, "candidate amendment hashes differ")
        require(selection_path_value == protocol_path_value, "candidate amendment paths differ")
        candidate_amendment_path = selection_path_value
        candidate_amendment_sha256 = selection_digest
        require(candidate_amendment_path.is_file(), "candidate amendment is missing")
        hash_binding(
            candidate_amendment_path,
            candidate_amendment_sha256,
            "candidate amendment",
        )
        final_digest = sha256_value(
            final_report, "candidate_amendment_sha256", "amendment_sha256"
        )
        if final_digest is not None:
            require(final_digest == candidate_amendment_sha256, "final amendment hash differs")
        candidate_amendment = load_json(candidate_amendment_path)
        validate_candidate_amendment(candidate_amendment)
        _, new_candidate_hash = candidate_tree_hashes(candidate_amendment)
        task_id = str(candidate_amendment["task_id"])
        task_material_hashes = (
            (final_report.get("candidate_material_hashes") or {}).get(task_id) or {}
        )
        final_candidate_hash = (task_material_hashes.get("P") or {}).get(
            "frozen_source_sha256"
        )
        require(
            final_candidate_hash == new_candidate_hash,
            "candidate amendment new tree hash differs from confirmatory materials",
        )
    else:
        require(
            sha256_value(
                final_report, "candidate_amendment_sha256", "amendment_sha256"
            )
            is None,
            "final report declares an amendment without protocol bindings",
        )

    source_paths = {
        "final_report": final_report_path,
        "selection": selection_path,
        "screen_protocol": screen_protocol_path,
        "confirm_protocol": confirm_protocol_path,
        "blind_labels": blind_labels_path,
        "screen_manifest": args.screen_run / "manifest.json",
        "screen_schedule": args.screen_run / "schedule.json",
        "screen_main_gate": args.screen_run / "main_gate.json",
        "screen_run_state": args.screen_run / "run_state.jsonl",
        "screen_platform_repairs": args.screen_run / "platform_repairs.json",
        "confirm_manifest": args.confirm_run / "manifest.json",
        "confirm_schedule": args.confirm_run / "schedule.json",
        "confirm_main_gate": args.confirm_run / "main_gate.json",
        "confirm_audit": args.confirm_run / "audit_report.json",
        "confirm_run_state": args.confirm_run / "run_state.jsonl",
        "confirm_platform_repairs": args.confirm_run / "platform_repairs.json",
    }
    if candidate_amendment_path is not None:
        source_paths["candidate_amendment"] = candidate_amendment_path
    for label, path in source_paths.items():
        require(path.is_file(), f"{label} is missing: {path}")

    expected_bindings = {
        "selection": final_report["selection_sha256"],
        "confirm_protocol": final_report["protocol_sha256"],
        "blind_labels": final_report["blind_labels_sha256"],
        "confirm_manifest": final_report["manifest_sha256"],
        "confirm_schedule": final_report["schedule_sha256"],
        "confirm_main_gate": final_report["main_gate_sha256"],
        "confirm_audit": final_report["audit_sha256"],
        "confirm_run_state": final_report["run_state_sha256"],
        "screen_protocol": selection["screen_protocol_sha256"],
        "screen_manifest": selection["screen_manifest_sha256"],
        "screen_schedule": selection["screen_schedule_sha256"],
        "screen_main_gate": selection["screen_main_gate_sha256"],
        "screen_run_state": selection["screen_run_state_sha256"],
        "screen_platform_repairs": selection["screen_platform_repairs_sha256"],
        "confirm_platform_repairs": final_report["platform_repairs_sha256"],
    }
    if candidate_amendment_sha256 is not None:
        expected_bindings["candidate_amendment"] = candidate_amendment_sha256
    source_hashes = {label: sha256_file(path) for label, path in source_paths.items()}
    for label, expected in expected_bindings.items():
        require(source_hashes[label] == expected, f"{label} hash mismatch")

    confirm_audit = load_json(source_paths["confirm_audit"])
    confirm_gate = load_json(source_paths["confirm_main_gate"])
    screen_gate = load_json(source_paths["screen_main_gate"])
    require(confirm_audit.get("status") == "passed", "confirmatory audit did not pass")
    require(confirm_audit.get("final_reportable") is True, "confirmatory audit is not reportable")
    require(confirm_gate.get("status") == "passed", "confirmatory main gate did not pass")
    require(confirm_gate.get("final_reportable") is True, "confirmatory main gate is not reportable")
    require(screen_gate.get("status") == "passed", "screening main gate did not pass")
    require(screen_gate.get("final_reportable") is True, "screening main gate is not reportable")

    summary = build_summary(
        final_report=final_report,
        selection=selection,
        screen_protocol=screen_protocol,
        confirm_protocol=confirm_protocol,
    )
    amendment_summary: dict[str, Any] | None = None
    if candidate_amendment is not None and candidate_amendment_sha256 is not None:
        old_hash, new_hash = candidate_tree_hashes(candidate_amendment)
        generator = candidate_amendment.get("generator")
        if not isinstance(generator, dict):
            generator = candidate_amendment
        amendment_summary = {
            "present": True,
            "sha256": candidate_amendment_sha256,
            "candidate_outcomes_used": False,
            "mode": generator["mode"],
            "stage": generator["stage"],
            "tscg": generator["tscg"],
            "old_candidate_tree_sha256": old_hash,
            "new_candidate_tree_sha256": new_hash,
        }
        summary["candidate_amendment"] = amendment_summary
    design_summary = {
        "schema_version": SCHEMA_VERSION,
        "status": "frozen-and-complete",
        "primary_executor": summary["primary_executor"],
        "screening": {
            key: summary["screening"][key]
            for key in (
                "tasks",
                "conditions",
                "repetitions_per_arm",
                "registered_main_rows",
                "pilot_tasks",
                "pilot_repetitions_per_arm",
                "registered_pilot_rows",
            )
        },
        "confirmation": {
            key: summary["confirmation"][key]
            for key in (
                "tasks",
                "conditions",
                "repetitions_per_arm",
                "registered_main_rows",
                "pilot_tasks",
                "pilot_repetitions_per_arm",
                "registered_pilot_rows",
            )
        },
        "decision_policy": confirm_protocol.get("decision_policy") or {},
        "candidate_construction": summary["candidate_construction"],
        "evidence_boundary": summary["evidence_boundary"],
    }
    if amendment_summary is not None:
        design_summary["candidate_amendment"] = amendment_summary
    selection_summary = {
        "schema_version": SCHEMA_VERSION,
        "status": selection["status"],
        **summary["screening"],
    }
    if amendment_summary is not None:
        selection_summary["candidate_amendment"] = amendment_summary
    decision_summary = {
        "schema_version": SCHEMA_VERSION,
        "status": final_report["status"],
        **summary["confirmation"],
    }
    blind_summary = summarize_blind_labels(blind_labels, selection_summary)
    screen_attestation = terminal_attestation(
        screen_gate,
        expected_rows=summary["screening"]["registered_main_rows"],
        source_hashes={
            key: source_hashes[key]
            for key in (
                "screen_protocol",
                "screen_manifest",
                "screen_schedule",
                "screen_main_gate",
                "screen_run_state",
                "screen_platform_repairs",
            )
        },
    )
    confirm_attestation = terminal_attestation(
        confirm_gate,
        expected_rows=summary["confirmation"]["registered_main_rows"],
        source_hashes={
            key: source_hashes[key]
            for key in (
                "confirm_protocol",
                "confirm_manifest",
                "confirm_schedule",
                "confirm_main_gate",
                "confirm_audit",
                "confirm_run_state",
                "confirm_platform_repairs",
            )
        },
        audit=confirm_audit,
    )
    binding_manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "verified",
        "source_evidence_sha256": source_hashes,
        "analysis_expected_bindings": expected_bindings,
        "candidate_material_hashes": final_report.get("candidate_material_hashes") or {},
        "raw_evidence_packaged": False,
        "paper_modified": False,
    }

    require(not args.output.exists(), f"output already exists: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = args.output.parent / f".{args.output.name}.{uuid.uuid4().hex}.tmp"
    try:
        atomic_text(staging / "README.md", render_readme(summary))
        atomic_text(staging / "REPORT.md", render_report(summary))
        atomic_json(staging / "SUMMARY.json", summary)
        atomic_json(staging / "protocol" / "design_summary.json", design_summary)
        atomic_json(staging / "analysis" / "selection_summary.json", selection_summary)
        atomic_json(staging / "analysis" / "decision_summary.json", decision_summary)
        atomic_json(staging / "annotations" / "blind_label_summary.json", blind_summary)
        atomic_json(staging / "attestations" / "screen_terminal.json", screen_attestation)
        atomic_json(
            staging / "attestations" / "confirmatory_terminal.json", confirm_attestation
        )
        atomic_json(staging / "outputs" / "binding_manifest.json", binding_manifest)
        shutil.copy2(final_report_path, staging / "outputs" / "final_report.json")
        if candidate_amendment_path is not None:
            shutil.copy2(
                candidate_amendment_path,
                staging / "protocol" / "candidate_amendment.json",
            )
        shutil.copy2(
            source_paths["screen_platform_repairs"],
            staging / "attestations" / "screen_platform_repairs.json",
        )
        shutil.copy2(
            source_paths["confirm_platform_repairs"],
            staging / "attestations" / "confirmatory_platform_repairs.json",
        )
        (staging / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.analysis_script, staging / "scripts" / args.analysis_script.name)
        shutil.copy2(Path(__file__), staging / "scripts" / Path(__file__).name)
        verifier_source = Path(__file__).with_name(
            "verify_skillsbench_candidate_validation_package.py"
        )
        require(verifier_source.is_file(), f"package verifier is missing: {verifier_source}")
        shutil.copy2(verifier_source, staging / "verify_package.py")

        package_files = sorted(
            (
                path
                for path in staging.rglob("*")
                if path.is_file() and path.name != "PACKAGE_MANIFEST.sha256"
            ),
            key=lambda path: path.relative_to(staging).as_posix(),
        )
        manifest_text = "\n".join(
            f"{sha256_file(path)}  {path.relative_to(staging).as_posix()}"
            for path in package_files
        )
        atomic_text(staging / "PACKAGE_MANIFEST.sha256", manifest_text)
        verification = subprocess.run(
            [sys.executable, str(staging / "verify_package.py"), str(staging)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        require(
            verification.returncode == 0,
            "generated package failed offline verification: "
            + (verification.stderr.strip() or verification.stdout.strip()),
        )
        staging.replace(args.output)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return {
        "status": "complete",
        "output": str(args.output.resolve()),
        "tasks": summary["confirmation"]["tasks"],
        "confirmatory_rows": summary["confirmation"]["registered_main_rows"],
        "unsafe_accepts": summary["confirmation"]["unsafe_accepts"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-output", type=Path, required=True)
    parser.add_argument("--selection-output", type=Path, required=True)
    parser.add_argument("--materials", type=Path, required=True)
    parser.add_argument("--screen-run", type=Path, required=True)
    parser.add_argument("--confirm-run", type=Path, required=True)
    parser.add_argument("--analysis-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    result = package(parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
