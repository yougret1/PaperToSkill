#!/usr/bin/env python
"""Build a SnapATAC2 artifact-execution follow-up diagnosis."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
TASK_IDS = ("SNAP-T1", "SNAP-T2")
CONDITIONS = ("summary", "papertoskill")
FOLLOWUP_ID = "snapatac2_artifact_execution_followup_v0"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_row_selection(path: Path) -> dict[tuple[str, str], str]:
    if not path.exists():
        return {}
    payload = load_json(path)
    selected: dict[tuple[str, str], str] = {}
    for row in payload.get("rows", []):
        task_id = str(row.get("task_id", ""))
        condition = str(row.get("condition", ""))
        run_id = str(row.get("run_id", ""))
        if task_id in TASK_IDS and condition in CONDITIONS and run_id:
            selected[(task_id, condition)] = run_id
    return selected


def selected_rows(raw_rows: list[dict[str, Any]], selection: dict[tuple[str, str], str]) -> list[dict[str, Any]]:
    rows_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    latest_by_condition: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw_rows:
        task_id = str(row.get("task_id", ""))
        condition = str(row.get("condition", ""))
        run_id = str(row.get("run_id", ""))
        if task_id not in TASK_IDS or condition not in CONDITIONS or row.get("status") != "scored":
            continue
        rows_by_key[(task_id, condition, run_id)] = row
        latest_by_condition[(task_id, condition)] = row

    selected: list[dict[str, Any]] = []
    for task_id in TASK_IDS:
        for condition in CONDITIONS:
            run_id = selection.get((task_id, condition))
            row = rows_by_key.get((task_id, condition, run_id)) if run_id else latest_by_condition.get((task_id, condition))
            if row:
                selected.append(row)
    return selected


def candidate_probe(root: Path, row: dict[str, Any]) -> dict[str, Any]:
    output_path = str(row.get("output_path", ""))
    if not output_path:
        return {"status": "missing_output_path"}
    path = resolve(root, output_path)
    if not path.exists():
        return {"status": "missing_candidate_output", "path": relative(root, path)}
    text = path.read_text(encoding="utf-8")
    try:
        candidate = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid_json",
            "path": relative(root, path),
            "error": str(exc),
            "starts_with_command_probe": text.lstrip().startswith('{"cmd"'),
        }
    task_id = str(row.get("task_id", ""))
    artifact_key = "embedding_artifacts" if task_id == "SNAP-T1" else "clustering_artifacts"
    artifacts = candidate.get(artifact_key)
    if isinstance(artifacts, list):
        artifact_count = len(artifacts)
        artifact_present = artifact_count > 0
    elif isinstance(artifacts, dict):
        artifact_count = len(artifacts)
        artifact_present = bool(artifacts)
    else:
        artifact_count = 0
        artifact_present = bool(artifacts)
    runtime = candidate.get("runtime_seconds")
    memory = candidate.get("peak_memory_mb")
    commands = candidate.get("commands", [])
    return {
        "status": "parsed",
        "path": relative(root, path),
        "completed": candidate.get("completed") is True,
        "artifact_key": artifact_key,
        "artifact_present": artifact_present,
        "artifact_count": artifact_count,
        "runtime_recorded": isinstance(runtime, (int, float)),
        "memory_recorded": isinstance(memory, (int, float)),
        "commands_count": len(commands) if isinstance(commands, list) else 0,
        "execution_gap": not (
            candidate.get("completed") is True
            and artifact_present
            and isinstance(runtime, (int, float))
            and isinstance(memory, (int, float))
        ),
    }


def asset_file(manifest: dict[str, Any], slot: str) -> str | None:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            return str(item.get("path", ""))
    return None


def fixture_probe(root: Path, task_id: str) -> dict[str, Any]:
    manifest_path = root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"
    if not manifest_path.exists():
        return {"task_id": task_id, "status": "missing_manifest", "manifest": relative(root, manifest_path)}
    manifest = load_json(manifest_path)
    miniature = asset_file(manifest, "miniature_fragment")
    if not miniature:
        return {"task_id": task_id, "status": "missing_miniature_slot", "manifest": relative(root, manifest_path)}
    path = resolve(root, miniature)
    if not path.exists():
        return {"task_id": task_id, "status": "missing_miniature_file", "path": relative(root, path)}
    sample_lines: list[str] = []
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for _ in range(3):
                line = handle.readline()
                if not line:
                    break
                sample_lines.append(line.rstrip("\n"))
    except OSError as exc:
        return {
            "task_id": task_id,
            "status": "unreadable_gzip",
            "path": relative(root, path),
            "error": str(exc),
        }
    field_counts = [len(line.split("\t")) for line in sample_lines]
    return {
        "task_id": task_id,
        "status": "readable",
        "path": relative(root, path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "sample_line_count": len(sample_lines),
        "sample_field_counts": field_counts,
    }


def run_git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return f"unavailable: {exc}"
    return result.stdout.strip()


def environment_probe(root: Path) -> dict[str, Any]:
    repo = Path("D:/a_work/gitee/SnapATAC2")
    return {
        "snapatac2_importable": importlib.util.find_spec("snapatac2") is not None,
        "local_repository": {
            "path": repo.as_posix(),
            "exists": repo.exists(),
            "revision": run_git(repo, "rev-parse", "HEAD") if repo.exists() else "",
            "status_short": run_git(repo, "status", "--short") if repo.exists() else "",
        },
        "fixture_probes": [fixture_probe(root, task_id) for task_id in TASK_IDS],
    }


def row_diagnosis(root: Path, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    diagnosed: list[dict[str, Any]] = []
    for row in rows:
        probe = candidate_probe(root, row)
        diagnosed.append(
            {
                "task_id": row.get("task_id"),
                "condition": row.get("condition"),
                "run_id": row.get("run_id"),
                "score": row.get("task_score"),
                "success": row.get("success"),
                "failure_reason": row.get("failure_reason"),
                "candidate_probe": probe,
            }
        )
    return diagnosed


def build_report(root: Path, raw_rows: Path, row_selection: Path) -> dict[str, Any]:
    rows = selected_rows(load_jsonl(raw_rows), load_row_selection(row_selection))
    diagnosed = row_diagnosis(root, rows)
    execution_gaps = [
        row
        for row in diagnosed
        if row.get("candidate_probe", {}).get("status") != "parsed"
        or row.get("candidate_probe", {}).get("execution_gap") is True
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "followup_id": FOLLOWUP_ID,
        "overall_status": "pre_registered_followup_needed" if execution_gaps else "no_followup_needed",
        "evidence_boundary": (
            "SNAP artifact-execution diagnosis and follow-up contract. This "
            "does not replace the paper-facing main SNAP rows and does not add "
            "new task-success evidence."
        ),
        "raw_rows": relative(root, raw_rows),
        "row_selection": relative(root, row_selection),
        "selected_row_count": len(rows),
        "environment": environment_probe(root),
        "rows": diagnosed,
        "diagnosis": [
            "Current SNAP rows ask the model for a JSON artifact record but the runner does not execute candidate scripts or commands.",
            "The scorer requires completed=true plus concrete artifacts and runtime/memory records, so plan-only outputs cannot reach the pre-registered success threshold.",
            "The local miniature fixtures are readable, but the Python package `snapatac2` is not importable in the current environment.",
        ],
        "followup_contract": {
            "main_rows_unchanged": True,
            "conditions": list(CONDITIONS),
            "paired_conditions_required": True,
            "base_model": "gpt-5.5 unless explicitly running LLM ablation",
            "provider_policy": "Use longer timeout/retry budgets; record provider availability separately from task metrics.",
            "execution_requirement": (
                "A follow-up runner must execute a controlled candidate script "
                "or a pre-registered scaffold that materializes artifacts and "
                "measures runtime/memory before setting completed=true."
            ),
            "scoring_requirement": (
                "Use the same locked fixture, resource budget, hidden labels/"
                "proxy policy, and scorer for Summary and PaperToSkill."
            ),
            "human_intervention": "none_mid_run",
            "blocked_if": (
                "SnapATAC2 installation or required data download fails; record "
                "the command, error, and blocked artifact in toHuman.md and "
                "continue other non-blocked work."
            ),
        },
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Condition | Run | Score | Success | Candidate Status | Execution Gap | Failure |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        probe = row.get("candidate_probe", {})
        values = [
            str(row.get("task_id", "")),
            str(row.get("condition", "")),
            str(row.get("run_id", "")),
            "" if row.get("score") is None else f"{float(row.get('score')):.3f}",
            str(row.get("success", "")),
            str(probe.get("status", "")),
            str(probe.get("execution_gap", probe.get("status") != "parsed")),
            str(row.get("failure_reason", "")),
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    env = report["environment"]
    lines = [
        "# SnapATAC2 Artifact-Execution Follow-Up Plan",
        "",
        "Evidence boundary: this is a diagnosis and pre-registered follow-up "
        "contract for SNAP artifact execution. It does not replace the main "
        "SNAP rows or add new task-success evidence.",
        "",
        f"- Follow-up ID: `{report['followup_id']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Selected SNAP rows inspected: {report['selected_row_count']}",
        f"- `snapatac2` importable: {env['snapatac2_importable']}",
        f"- Local SnapATAC2 repo exists: {env['local_repository']['exists']}",
        f"- Local SnapATAC2 revision: `{env['local_repository']['revision']}`",
        "",
        "## Current Rows",
        "",
        markdown_table(report["rows"]),
        "",
        "## Fixture Probe",
        "",
        "| Task | Status | Path | Size Bytes | Sample Lines | Field Counts |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for probe in env["fixture_probes"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(probe.get("task_id", "")),
                    str(probe.get("status", "")),
                    str(probe.get("path", "")),
                    str(probe.get("size_bytes", "")),
                    str(probe.get("sample_line_count", "")),
                    ",".join(str(value) for value in probe.get("sample_field_counts", [])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Diagnosis",
            "",
        ]
    )
    for item in report["diagnosis"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Follow-Up Contract",
            "",
        ]
    )
    for key, value in report["followup_contract"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build SNAP artifact-execution follow-up diagnosis.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--raw-rows", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument(
        "--row-selection",
        type=Path,
        default=root / "results" / "real_reuse" / "main_run_selection.json",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_artifact_followup.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_artifact_followup.md",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    raw_rows = args.raw_rows if args.raw_rows.is_absolute() else root / args.raw_rows
    row_selection = args.row_selection if args.row_selection.is_absolute() else root / args.row_selection
    report = build_report(root, raw_rows, row_selection)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
