#!/usr/bin/env python
"""Execute SNAP candidate scripts under the pre-registered artifact contract."""

from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import os
import runpy
import sys
import time
import tracemalloc
import traceback
from pathlib import Path
from typing import Any

from score_real_reuse_snapatac2 import score_artifact


SCHEMA_VERSION = "0.1"
RUNNER_ID = "snapatac2_executable_candidate_runner_v0"
TASK_IDS = ("SNAP-T1", "SNAP-T2")
CONDITIONS = ("summary", "papertoskill")
REQUIRED_ARTIFACTS = {
    "SNAP-T1": ("embedding.csv", "cell_features.csv", "fragment_summary.json"),
    "SNAP-T2": ("clusters.csv", "marker_summary.json", "embedding.csv"),
}
ARTIFACT_FIELD = {"SNAP-T1": "embedding_artifacts", "SNAP-T2": "clustering_artifacts"}


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def asset_manifest_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"


def asset_file(manifest: dict[str, Any], slot: str) -> str:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            return str(item["path"])
    raise KeyError(f"missing asset slot {slot}")


def candidate_script_path(candidate_dir: Path, task_id: str, condition: str) -> Path | None:
    names = [
        f"{task_id}_{condition}.py",
        f"{task_id.lower()}_{condition}.py",
        f"{task_id.replace('-', '_').lower()}_{condition}.py",
        f"{condition}.py",
    ]
    for name in names:
        path = candidate_dir / name
        if path.exists():
            return path
    return None


def candidate_worker(script: str, argv: list[str], cwd: str, queue: mp.Queue) -> None:
    old_argv = sys.argv[:]
    old_cwd = os.getcwd()
    status = "success"
    exit_code: int | None = 0
    error = ""
    started = time.perf_counter()
    tracemalloc.start()
    try:
        os.chdir(cwd)
        sys.argv = [script, *argv]
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (0, None):
            status = "error"
            exit_code = int(exc.code) if isinstance(exc.code, int) else 1
            error = str(exc.code)
    except BaseException:
        status = "error"
        exit_code = 1
        error = traceback.format_exc()
    finally:
        runtime = time.perf_counter() - started
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.argv = old_argv
        os.chdir(old_cwd)
    queue.put(
        {
            "status": status,
            "exit_code": exit_code,
            "error": error,
            "runtime_seconds": round(runtime, 6),
            "peak_memory_mb": round(peak_bytes / (1024 * 1024), 6),
        }
    )


def execute_candidate(
    *,
    script: Path,
    fragment_path: Path,
    artifact_dir: Path,
    result_json: Path,
    task_id: str,
    condition: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    result_json.parent.mkdir(parents=True, exist_ok=True)
    argv = [
        "--task-id",
        task_id,
        "--condition",
        condition,
        "--fragment",
        str(fragment_path),
        "--artifact-dir",
        str(artifact_dir),
        "--result-json",
        str(result_json),
    ]
    ctx = mp.get_context("spawn")
    queue: mp.Queue = ctx.Queue()
    process = ctx.Process(target=candidate_worker, args=(str(script), argv, str(script.parent), queue))
    process.start()
    process.join(max(0.1, timeout_seconds))
    if process.is_alive():
        process.terminate()
        process.join(5)
        return {
            "status": "timeout",
            "exit_code": None,
            "error": f"candidate timed out after {timeout_seconds} seconds",
            "runtime_seconds": round(timeout_seconds, 6),
            "peak_memory_mb": 0.0,
        }
    if not queue.empty():
        return dict(queue.get())
    return {
        "status": "error",
        "exit_code": process.exitcode,
        "error": f"candidate process exited without resource record; exitcode={process.exitcode}",
        "runtime_seconds": 0.0,
        "peak_memory_mb": 0.0,
    }


def artifact_manifest(root: Path, artifact_dir: Path) -> dict[str, Any]:
    files = []
    if artifact_dir.exists():
        for path in sorted(item for item in artifact_dir.rglob("*") if item.is_file()):
            files.append(
                {
                    "path": relative(root, path),
                    "name": path.name,
                    "size_bytes": path.stat().st_size,
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "runner_id": RUNNER_ID,
        "artifact_dir": relative(root, artifact_dir),
        "files": files,
    }


def required_artifact_map(root: Path, artifact_dir: Path, task_id: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS[task_id]:
        matches = [path for path in artifact_dir.rglob(name) if path.is_file()]
        if matches:
            result[name] = relative(root, matches[0])
    return result


def load_candidate_result(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = load_json(path)
    except json.JSONDecodeError:
        return {"notes": {"candidate_result_error": "invalid_json"}}
    return payload if isinstance(payload, dict) else {}


def runner_owned_candidate_output(
    *,
    root: Path,
    task_id: str,
    condition: str,
    execution: dict[str, Any],
    candidate_result: dict[str, Any],
    artifacts: dict[str, str],
    resource_record_path: Path,
    artifact_manifest_path: Path,
) -> dict[str, Any]:
    completed = execution.get("status") == "success" and len(artifacts) == len(REQUIRED_ARTIFACTS[task_id])
    method_steps = candidate_result.get("method_steps")
    if not isinstance(method_steps, list) or not method_steps:
        method_steps = [
            "Run a candidate SnapATAC2-style executable over the locked miniature fixture.",
            "Materialize concrete artifacts before invoking the scorer.",
            "Use spectral embedding or clustering outputs when applicable.",
        ]
    output: dict[str, Any] = {
        "completed": completed,
        "method_steps": method_steps,
        ARTIFACT_FIELD[task_id]: artifacts,
        "runtime_seconds": execution.get("runtime_seconds", 0.0),
        "peak_memory_mb": execution.get("peak_memory_mb", 0.0),
        "notes": {
            "runner_id": RUNNER_ID,
            "condition": condition,
            "completed_field_owner": "runner_after_execution",
            "candidate_authored_completed_ignored": candidate_result.get("completed"),
            "resource_record": relative(root, resource_record_path),
            "artifact_manifest": relative(root, artifact_manifest_path),
            "evidence_boundary": (
                "Executable-candidate diagnostic row for SNAP only; not a "
                "main-row replacement unless explicitly promoted."
            ),
        },
    }
    if task_id == "SNAP-T2":
        output["quality_metrics"] = candidate_result.get("quality_metrics", {})
        if "predicted_labels" in candidate_result:
            output["predicted_labels"] = candidate_result["predicted_labels"]
    return output


def run_single(args: argparse.Namespace, task_id: str, condition: str, run_id: str) -> dict[str, Any]:
    root = args.root.resolve()
    manifest_path = asset_manifest_path(root, task_id)
    run_dir = args.output_dir / task_id / condition / run_id
    artifact_dir = run_dir / "artifacts"
    result_json = run_dir / "candidate_result.json"
    candidate_output = run_dir / "candidate_output.json"
    resource_record = run_dir / "resource_record.json"
    manifest_output = run_dir / "artifact_manifest.json"
    metric_path = run_dir / "metric.json"
    run_dir.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists():
        return row(
            root,
            run_id,
            task_id,
            condition,
            "pending",
            "missing_fixture_assets",
            candidate_output,
            metric_path,
            resource_record,
            manifest_output,
        )
    manifest = load_json(manifest_path)
    fragment_path = resolve(root, asset_file(manifest, "miniature_fragment"))
    script = candidate_script_path(args.candidate_dir, task_id, condition)
    if script is None:
        return row(
            root,
            run_id,
            task_id,
            condition,
            "pending",
            "missing_candidate_script",
            candidate_output,
            metric_path,
            resource_record,
            manifest_output,
        )

    execution = execute_candidate(
        script=script,
        fragment_path=fragment_path,
        artifact_dir=artifact_dir,
        result_json=result_json,
        task_id=task_id,
        condition=condition,
        timeout_seconds=args.timeout_seconds,
    )
    write_json(resource_record, {"schema_version": SCHEMA_VERSION, "runner_id": RUNNER_ID, **execution})
    manifest_payload = artifact_manifest(root, artifact_dir)
    write_json(manifest_output, manifest_payload)
    candidate_result = load_candidate_result(result_json)
    artifacts = required_artifact_map(root, artifact_dir, task_id)
    candidate_payload = runner_owned_candidate_output(
        root=root,
        task_id=task_id,
        condition=condition,
        execution=execution,
        candidate_result=candidate_result,
        artifacts=artifacts,
        resource_record_path=resource_record,
        artifact_manifest_path=manifest_output,
    )
    write_json(candidate_output, candidate_payload)
    metric = score_artifact(task_id, run_dir, manifest_path, root)
    write_json(metric_path, metric)
    status = "scored"
    failure_reason = metric.get("failure_reason") or execution.get("error", "")
    result = row(
        root,
        run_id,
        task_id,
        condition,
        status,
        failure_reason,
        candidate_output,
        metric_path,
        resource_record,
        manifest_output,
    )
    result.update(
        {
            "task_score": metric.get("task_score"),
            "success": metric.get("success"),
            "runtime_seconds": candidate_payload["runtime_seconds"],
            "peak_memory_mb": candidate_payload["peak_memory_mb"],
            "execution_status": execution.get("status"),
            "candidate_script": relative(root, script),
        }
    )
    return result


def row(
    root: Path,
    run_id: str,
    task_id: str,
    condition: str,
    status: str,
    failure_reason: str,
    candidate_output: Path,
    metric_path: Path,
    resource_record: Path,
    artifact_manifest_path: Path,
) -> dict[str, Any]:
    return {
        "runner_id": RUNNER_ID,
        "run_id": run_id,
        "task_id": task_id,
        "condition": condition,
        "status": status,
        "task_score": None,
        "success": None,
        "runtime_seconds": None,
        "peak_memory_mb": None,
        "failure_reason": failure_reason,
        "candidate_output": relative(root, candidate_output) if candidate_output.exists() else "",
        "metric_path": relative(root, metric_path) if metric_path.exists() else "",
        "resource_record": relative(root, resource_record) if resource_record.exists() else "",
        "artifact_manifest": relative(root, artifact_manifest_path) if artifact_manifest_path.exists() else "",
        "raw_rows_policy": "not_appended_to_main_raw_rows",
        "evidence_boundary": (
            "SNAP executable-candidate diagnostic row. Main raw rows and "
            "paper-facing main selection remain unchanged."
        ),
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Condition | Status | Score | Success | Failure | Candidate Output |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        values = [
            str(item.get("task_id", "")),
            str(item.get("condition", "")),
            str(item.get("status", "")),
            "" if item.get("task_score") is None else f"{float(item['task_score']):.3f}",
            "" if item.get("success") is None else str(item.get("success")),
            str(item.get("failure_reason", "")),
            str(item.get("candidate_output", "")),
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(lines)


def write_csv_report(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "run_id",
        "task_id",
        "condition",
        "status",
        "task_score",
        "success",
        "runtime_seconds",
        "peak_memory_mb",
        "failure_reason",
        "candidate_output",
        "metric_path",
        "resource_record",
        "artifact_manifest",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in rows:
            writer.writerow({field: item.get(field, "") for field in fields})


def build_report(args: argparse.Namespace, run_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in rows:
        counts[str(item["status"])] = counts.get(str(item["status"]), 0) + 1
    all_scored = bool(rows) and all(item.get("status") == "scored" for item in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "runner_id": RUNNER_ID,
        "run_id": run_id,
        "overall_status": "complete" if all_scored else "partial",
        "status_counts": counts,
        "tasks": list(args.task),
        "conditions": list(args.condition),
        "candidate_dir": str(args.candidate_dir),
        "raw_rows_policy": "not_appended_to_main_raw_rows",
        "main_rows_unchanged": True,
        "evidence_boundary": (
            "This runner executes candidate scripts for SNAP diagnostic reruns "
            "under the executable-candidate contract. It does not append to "
            "main raw rows or replace paper-facing main rows."
        ),
        "rows": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# SnapATAC2 Executable-Candidate Run Report",
        "",
        "Evidence boundary: this diagnostic runner executes candidate scripts "
        "under the pre-registered SNAP executable-candidate contract. It writes "
        "runner-owned `candidate_output.json`, `artifact_manifest.json`, and "
        "`resource_record.json`, then invokes the existing SNAP scorer. It does "
        "not append to main raw rows or replace paper-facing main rows.",
        "",
        f"- Runner ID: `{report['runner_id']}`",
        f"- Run ID: `{report['run_id']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Raw rows policy: `{report['raw_rows_policy']}`",
        f"- Main rows unchanged: {report['main_rows_unchanged']}",
        "",
        markdown_table(report["rows"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = root_path()
    parser = argparse.ArgumentParser(description="Run SNAP executable-candidate diagnostic reruns.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--task", action="append", choices=TASK_IDS, default=[])
    parser.add_argument("--condition", action="append", choices=CONDITIONS, default=[])
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "real_reuse" / "runs")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_executable_candidate_run_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_executable_candidate_run_report.md",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_executable_candidate_run_report.csv",
    )
    args = parser.parse_args()
    if not args.task:
        args.task = list(TASK_IDS)
    if not args.condition:
        args.condition = list(CONDITIONS)
    args.root = args.root.resolve()
    args.candidate_dir = args.candidate_dir.resolve()
    run_id = args.run_id or time.strftime("snap_exec_candidate_%Y%m%d_%H%M%S")

    rows = [run_single(args, task_id, condition, run_id) for task_id in args.task for condition in args.condition]
    report = build_report(args, run_id, rows)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    write_csv_report(args.output_csv, rows)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
