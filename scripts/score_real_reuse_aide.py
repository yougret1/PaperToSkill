#!/usr/bin/env python
"""Score locked AIDE real-reuse outputs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
ID_COLUMN = "PassengerId"
TARGET_COLUMN = "Transported"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return fieldnames, rows


def normalize_bool(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return "True"
    if text in {"false", "0", "no", "n"}:
        return "False"
    raise ValueError(f"unsupported boolean label: {value!r}")


def load_baseline_score(path: Path | None, labels_path: Path | None = None) -> float | None:
    candidates: list[Path] = []
    if path is not None:
        candidates.append(path)
    if labels_path is not None:
        candidates.append(labels_path.parent / "baseline_score.json")
    for candidate in candidates:
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            value = data.get("baseline_score")
            return float(value) if value is not None else None
    return None


def validate_submission(submission_path: Path, labels_path: Path) -> tuple[float, str]:
    submission_fields, submission_rows = read_csv(submission_path)
    label_fields, label_rows = read_csv(labels_path)
    if {ID_COLUMN, TARGET_COLUMN} - set(label_fields):
        raise ValueError("labels file missing PassengerId/Transported columns")
    if {ID_COLUMN, TARGET_COLUMN} - set(submission_fields):
        raise ValueError("submission file missing PassengerId/Transported columns")
    labels = {row[ID_COLUMN]: normalize_bool(row[TARGET_COLUMN]) for row in label_rows}
    predictions: dict[str, str] = {}
    for row in submission_rows:
        passenger_id = row.get(ID_COLUMN, "")
        if passenger_id in predictions:
            raise ValueError(f"duplicate prediction id: {passenger_id}")
        predictions[passenger_id] = normalize_bool(row.get(TARGET_COLUMN, ""))
    missing = sorted(set(labels) - set(predictions))
    extra = sorted(set(predictions) - set(labels))
    if missing or extra:
        detail = []
        if missing:
            detail.append("missing=" + ",".join(missing[:5]))
        if extra:
            detail.append("extra=" + ",".join(extra[:5]))
        raise ValueError("submission ids do not match validation labels: " + "; ".join(detail))
    correct = sum(1 for passenger_id, answer in labels.items() if predictions[passenger_id] == answer)
    return correct / len(labels), ""


def score_submission(
    *,
    task_id: str,
    submission_path: Path,
    labels_path: Path,
    baseline_score: float | None,
) -> dict[str, Any]:
    try:
        score, failure_reason = validate_submission(submission_path, labels_path)
        valid = True
    except (OSError, ValueError) as exc:
        score = 0.0
        failure_reason = str(exc)
        valid = False
    success = bool(valid and (baseline_score is None or score > baseline_score))
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "metric_name": "validation_score" if task_id == "AIDE-T1" else "best_node_score",
        "task_score": score,
        "success": success,
        "valid_submission": valid,
        "baseline_score": baseline_score,
        "improved_over_baseline": None if baseline_score is None else score > baseline_score,
        "submission_path": submission_path.as_posix(),
        "labels_path": labels_path.as_posix(),
        "failure_reason": failure_reason,
        "evidence_boundary": (
            "Objective local validation scoring for one locked AIDE output. "
            "This does not compare Summary and PaperToSkill or claim aggregate "
            "downstream effectiveness."
        ),
    }


def copy_workspace(workspace: Path, target: Path) -> None:
    if not workspace.exists():
        raise ValueError(f"workspace does not exist: {workspace}")
    for item in workspace.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            text=True,
        )
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def run_python_script(script_name: str, cwd: Path, timeout_seconds: float) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, script_name]
    kwargs: dict[str, Any] = {
        "cwd": cwd,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=stdout, stderr=stderr) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_candidate(
    candidate_script: Path,
    workspace: Path,
    timeout_seconds: float,
) -> tuple[Path | None, subprocess.CompletedProcess[str] | None, str]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        copy_workspace(workspace, tmp_path)
        script_path = tmp_path / "candidate_solution.py"
        shutil.copy2(candidate_script, script_path)
        try:
            completed = run_python_script(script_path.name, tmp_path, timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            return None, None, f"timeout after {timeout_seconds:g}s"
        submission_path = tmp_path / "submission.csv"
        if not submission_path.exists():
            stderr = completed.stderr.strip().splitlines()
            reason = stderr[-1] if stderr else f"candidate did not create submission.csv; returncode={completed.returncode}"
            return None, completed, reason
        persisted = candidate_script.parent / "submission.csv"
        shutil.copy2(submission_path, persisted)
        return persisted, completed, ""


def score_candidate(
    *,
    task_id: str,
    candidate_script: Path,
    workspace: Path,
    labels_path: Path,
    baseline_score: float | None,
    timeout_seconds: float,
) -> dict[str, Any]:
    try:
        submission_path, completed, run_failure = run_candidate(candidate_script, workspace, timeout_seconds)
    except ValueError as exc:
        submission_path = None
        completed = None
        run_failure = str(exc)
    if submission_path is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "metric_name": "validation_score" if task_id == "AIDE-T1" else "best_node_score",
            "task_score": 0.0,
            "success": False,
            "valid_submission": False,
            "baseline_score": baseline_score,
            "improved_over_baseline": False if baseline_score is not None else None,
            "candidate_script": candidate_script.as_posix(),
            "workspace": workspace.as_posix(),
            "labels_path": labels_path.as_posix(),
            "returncode": None if completed is None else completed.returncode,
            "stdout": "" if completed is None else completed.stdout[-2000:],
            "stderr": "" if completed is None else completed.stderr[-2000:],
            "failure_reason": run_failure,
            "evidence_boundary": (
                "Objective local validation scoring for one locked AIDE "
                "candidate script. No aggregate downstream claim is implied."
            ),
        }
    result = score_submission(
        task_id=task_id,
        submission_path=submission_path,
        labels_path=labels_path,
        baseline_score=baseline_score,
    )
    result.update(
        {
            "candidate_script": candidate_script.as_posix(),
            "workspace": workspace.as_posix(),
            "returncode": None if completed is None else completed.returncode,
            "stdout": "" if completed is None else completed.stdout[-2000:],
            "stderr": "" if completed is None else completed.stderr[-2000:],
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Score locked AIDE real-reuse outputs.")
    parser.add_argument("--task", choices=["AIDE-T1", "AIDE-T2"], required=True)
    parser.add_argument("--submission", type=Path)
    parser.add_argument("--candidate-script", type=Path)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--baseline-score-json", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    baseline_score = load_baseline_score(args.baseline_score_json, args.labels)
    if args.candidate_script:
        if not args.workspace:
            parser.error("--candidate-script requires --workspace")
        result = score_candidate(
            task_id=args.task,
            candidate_script=args.candidate_script,
            workspace=args.workspace,
            labels_path=args.labels,
            baseline_score=baseline_score,
            timeout_seconds=args.timeout_seconds,
        )
    elif args.submission:
        result = score_submission(
            task_id=args.task,
            submission_path=args.submission,
            labels_path=args.labels,
            baseline_score=baseline_score,
        )
    else:
        parser.error("provide --submission or --candidate-script")

    if args.output_json:
        write_json(args.output_json, result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
