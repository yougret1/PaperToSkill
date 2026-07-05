#!/usr/bin/env python
"""Build paper-facing real-reuse main-result table scaffolds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


TABLE_COLUMNS = [
    "Task ID",
    "Source Paper",
    "Domain",
    "Original-style Input",
    "Required Output",
    "Metric",
    "Reference",
    "Summary Score",
    "PaperToSkill Score",
    "Status",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def load_row_selection(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None or not path.exists():
        return {}
    payload = load_json(path)
    selected: dict[tuple[str, str], str] = {}
    for item in payload.get("rows", []):
        task_id = str(item.get("task_id", ""))
        condition = str(item.get("condition", ""))
        run_id = str(item.get("run_id", ""))
        if task_id and condition and run_id:
            selected[(task_id, condition)] = run_id
    return selected


def row_selection_summary(path: Path | None, row_selection: dict[tuple[str, str], str]) -> dict[str, Any]:
    return {
        "path": str(path) if path else None,
        "entries": len(row_selection),
        "boundary": (
            "Selected run_id values pin paper-facing main rows so diagnostic "
            "follow-up rows remain auditable without replacing the main table."
            if row_selection
            else "No row-selection file was applied."
        ),
    }


def paper_by_id(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(paper["id"]): paper for paper in spec.get("source_papers", [])}


def short_input(task: dict[str, Any]) -> str:
    task_id = str(task["id"])
    by_task = {
        "AIDE-T1": "Kaggle-style dataset + metric",
        "AIDE-T2": "Weak ML script + feedback",
        "SWE-T1": "Repo issue + tests",
        "SWE-T2": "Failing test + repo",
        "REF-T1": "Multi-hop QA + feedback",
        "REF-T2": "Failed attempt + checker feedback",
        "SNAP-T1": "Small single-cell dataset",
        "SNAP-T2": "Single-cell labels/proxy task",
    }
    return by_task.get(task_id, str(task.get("original_style_input", "")))


def short_output(task: dict[str, Any]) -> str:
    task_id = str(task["id"])
    by_task = {
        "AIDE-T1": "Runnable solution/submission",
        "AIDE-T2": "Improved script + trajectory",
        "SWE-T1": "Patch + test log",
        "SWE-T2": "Focused patch + verification",
        "REF-T1": "Final answer + reflection trace",
        "REF-T2": "Corrected second attempt",
        "SNAP-T1": "Pipeline + embedding artifacts",
        "SNAP-T2": "Clustering/marker artifacts",
    }
    return by_task.get(task_id, str(task.get("required_output", "")))


def reference_label(task: dict[str, Any]) -> str:
    label = str(task.get("paper_reference", {}).get("label", "Reported reference"))
    if "AIDE" in label:
        return "Reported AIDE ref."
    if "SWE-agent" in label:
        return "Reported SWE-agent ref."
    if "Reflexion" in label:
        return "Reported Reflexion ref."
    if "SnapATAC2" in label:
        return "Reported SnapATAC2 ref."
    return "Reported paper ref."


def score_string(row: dict[str, Any] | None) -> str:
    if not row or row.get("status") != "scored" or row.get("task_score") is None:
        return "Pending"
    return f"{float(row['task_score']):.3f}"


def latest_score_rows(
    raw_rows: list[dict[str, Any]],
    row_selection: dict[tuple[str, str], str] | None = None,
) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    row_selection = row_selection or {}
    for row in raw_rows:
        if row.get("status") != "scored":
            continue
        key = (str(row.get("task_id", "")), str(row.get("condition", "")))
        selected_run_id = row_selection.get(key)
        if selected_run_id is not None and row.get("run_id") != selected_run_id:
            continue
        latest[key] = row
    missing = sorted(
        f"{task_id}/{condition}:{run_id}"
        for (task_id, condition), run_id in row_selection.items()
        if (task_id, condition) not in latest
    )
    if missing:
        raise ValueError("row selection references missing scored rows: " + ", ".join(missing))
    return latest


def has_any(status_root: Path, relative_paths: list[str]) -> bool:
    return any((status_root / path).exists() for path in relative_paths)


def unscored_status(task_id: str, status_root: Path) -> str:
    asset_manifest = status_root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"
    if task_id.startswith("AIDE-"):
        scripts_ready = all(
            (status_root / "scripts" / script).exists()
            for script in (
                "prepare_real_reuse_aide_fixture.py",
                "score_real_reuse_aide.py",
                "run_real_reuse_aide.py",
            )
        )
        if asset_manifest.exists():
            return "Ready to run"
        return "Awaiting dataset" if scripts_ready else "Runner pending"

    if task_id.startswith("SWE-"):
        skill_ready = has_any(
            status_root,
            [
                "generated_skills/real_reuse/swe_agent/SKILL.md",
                "generated_skills/swe_agent/SKILL.md",
            ],
        )
        runner_ready = (status_root / "scripts" / "run_real_reuse_swe.py").exists()
        if not skill_ready:
            return "Skill pending"
        if not runner_ready:
            return "Runner pending"
        return "Ready to run" if asset_manifest.exists() else "Fixture pending"

    if task_id.startswith("SNAP-"):
        skill_ready = has_any(
            status_root,
            [
                "generated_skills/real_reuse/snapatac2/SKILL.md",
                "generated_skills/snapatac2/SKILL.md",
                "generated_skills/snap_atac2/SKILL.md",
            ],
        )
        runner_ready = has_any(
            status_root,
            [
                "scripts/run_real_reuse_snapatac2.py",
                "scripts/run_real_reuse_snap.py",
            ],
        )
        if not skill_ready:
            return "Skill pending"
        if not runner_ready:
            return "Runner pending"
        return "Ready to run" if asset_manifest.exists() else "Fixture pending"

    if task_id.startswith("REF-"):
        runner_ready = (status_root / "scripts" / "run_real_reuse_reflexion.py").exists()
        if runner_ready and asset_manifest.exists():
            return "Ready to run"
        return "Fixture pending"

    return "Pending execution"


def row_status(task_id: str, score_rows: dict[tuple[str, str], dict[str, Any]], status_root: Path) -> str:
    summary = score_rows.get((task_id, "summary"))
    papertoskill = score_rows.get((task_id, "papertoskill"))
    scored = [row for row in (summary, papertoskill) if row]
    if len(scored) == 2:
        families = sorted({str(row.get("model_family", "")) for row in scored if row.get("model_family")})
        return "Scored (" + ",".join(families) + ")"
    if scored:
        families = sorted({str(row.get("model_family", "")) for row in scored if row.get("model_family")})
        return "Partial (" + ",".join(families) + ")"
    return unscored_status(task_id, status_root)


def build_rows(
    spec: dict[str, Any],
    raw_rows: list[dict[str, Any]] | None = None,
    *,
    status_root: Path | None = None,
    row_selection: dict[tuple[str, str], str] | None = None,
) -> list[dict[str, str]]:
    papers = paper_by_id(spec)
    score_rows = latest_score_rows(raw_rows or [], row_selection=row_selection)
    status_root = status_root or Path(__file__).resolve().parents[1]
    rows: list[dict[str, str]] = []
    for task in spec.get("tasks", []):
        task_id = str(task["id"])
        paper = papers[str(task["source_paper_id"])]
        summary = score_rows.get((task_id, "summary"))
        papertoskill = score_rows.get((task_id, "papertoskill"))
        rows.append(
            {
                "Task ID": task_id,
                "Source Paper": str(paper["title"]).split(":")[0],
                "Domain": str(task["domain"]),
                "Original-style Input": short_input(task),
                "Required Output": short_output(task),
                "Metric": str(task.get("metric", {}).get("name", "")),
                "Reference": reference_label(task),
                "Summary Score": score_string(summary),
                "PaperToSkill Score": score_string(papertoskill),
                "Status": row_status(task_id, score_rows, status_root),
            }
        )
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [row[column].replace("|", "\\|").replace("\n", " ") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    raw_row_count: int,
    row_selection_info: dict[str, Any],
) -> None:
    lines = [
        "# Real-Reuse Main Results Table",
        "",
        "Evidence boundary: this table defines the main real-reuse experiment "
        "rows for the paper. Score cells are generated from local raw rows "
        "selected by the row-selection file; any Pending scaffold/pre-run "
        "cells mark missing scored raw rows, not downstream task-success "
        "evidence.",
        "",
        f"- Raw scored rows read: {raw_row_count}",
        f"- Row selection file: {row_selection_info['path'] or 'not applied'}",
        f"- Row selection entries: {row_selection_info['entries']}",
        f"- Row selection boundary: {row_selection_info['boundary']}",
        "",
        markdown_table(rows, TABLE_COLUMNS),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(
    path: Path,
    rows: list[dict[str, str]],
    raw_rows: list[dict[str, Any]],
    row_selection_info: dict[str, Any],
) -> None:
    payload = {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Paper-facing real-reuse table. Score cells are generated from "
            "raw_rows.jsonl rows selected by the row-selection file; any "
            "Pending scaffold/pre-run cells mark missing scored raw rows, "
            "not task-success evidence."
        ),
        "raw_row_count": len(raw_rows),
        "row_selection": row_selection_info,
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the real-reuse paper table scaffold.")
    parser.add_argument("--spec", type=Path, default=root / "benchmarks" / "real_reuse" / "real_reuse_v0.json")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "main_results_plan.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "main_results_plan.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "main_results_plan.json",
    )
    parser.add_argument(
        "--raw-rows",
        type=Path,
        default=root / "results" / "real_reuse" / "raw_rows.jsonl",
    )
    parser.add_argument(
        "--row-selection",
        type=Path,
        help=(
            "Optional JSON selecting run_id values for paper-facing rows. "
            "If omitted, the repository default is used only with the default raw rows file."
        ),
    )
    parser.add_argument(
        "--status-root",
        type=Path,
        default=root,
        help="Repository-like root used to infer unscored task readiness status.",
    )
    args = parser.parse_args()

    raw_rows = load_raw_rows(args.raw_rows)
    default_raw_rows = root / "results" / "real_reuse" / "raw_rows.jsonl"
    default_selection = root / "results" / "real_reuse" / "main_run_selection.json"
    row_selection_path = args.row_selection
    if row_selection_path is None and args.raw_rows.resolve() == default_raw_rows.resolve():
        row_selection_path = default_selection
    row_selection = load_row_selection(row_selection_path)
    row_selection_info = row_selection_summary(row_selection_path, row_selection)
    rows = build_rows(
        load_json(args.spec),
        raw_rows,
        status_root=args.status_root,
        row_selection=row_selection,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, len(raw_rows), row_selection_info)
    write_json(args.output_json, rows, raw_rows, row_selection_info)
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
