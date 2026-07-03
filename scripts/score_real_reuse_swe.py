#!/usr/bin/env python
"""Score locked SWE-agent real-reuse patches with `git apply` and tests."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
TASK_IDS = ("SWE-T1", "SWE-T2")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_workspace(workspace: Path, target: Path) -> None:
    if not workspace.exists() or not workspace.is_dir():
        raise ValueError(f"workspace does not exist or is not a directory: {workspace}")
    for item in workspace.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        else:
            shutil.copy2(item, destination)


def read_test_command(command: str | None, command_file: Path | None) -> str:
    if command:
        return command
    if command_file:
        return command_file.read_text(encoding="utf-8").strip()
    raise ValueError("provide --test-command or --test-command-file")


def truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def apply_runtime_shims(workspace: Path) -> list[str]:
    shims: list[str] = []
    astropy_init = workspace / "astropy" / "__init__.py"
    astropy_compiler = workspace / "astropy" / "utils" / "_compiler.py"
    compiled_or_source_compiler = list((workspace / "astropy" / "utils").glob("_compiler.*"))
    if astropy_init.exists() and not compiled_or_source_compiler:
        astropy_compiler.write_text(
            '"""Runtime shim for source-checkout import in locked SWE scoring."""\n',
            encoding="utf-8",
        )
        shims.append("astropy_utils_compiler_stub")
    return shims


def git_apply_command(patch_path: Path) -> list[str]:
    return [
        "git",
        "apply",
        "--recount",
        "--whitespace=nowarn",
        "--ignore-space-change",
        str(patch_path),
    ]


def command_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy()
    source_dir = cwd / "src"
    if source_dir.exists():
        existing = env.get("PYTHONPATH", "")
        entries = [str(source_dir)]
        if existing:
            entries.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(entries)
    return env


def run_command(command: list[str] | str, cwd: Path, timeout_seconds: float, *, shell: bool = False) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=command_env(cwd),
        )
        return {
            "returncode": completed.returncode,
            "stdout": truncate(completed.stdout),
            "stderr": truncate(completed.stderr),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": None,
            "stdout": truncate(exc.stdout or ""),
            "stderr": truncate(exc.stderr or ""),
            "timed_out": True,
            "timeout_seconds": timeout_seconds,
        }


def score_patch(
    *,
    task_id: str,
    patch_path: Path,
    workspace: Path,
    test_command: str,
    timeout_seconds: float,
    test_patch_path: Path | None = None,
) -> dict[str, Any]:
    patch_path = patch_path.resolve()
    workspace = workspace.resolve()
    if test_patch_path is not None:
        test_patch_path = test_patch_path.resolve()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            copy_workspace(workspace, tmp_path)
        except ValueError as exc:
            return failure_result(task_id, patch_path, workspace, test_command, str(exc))

        runtime_shims = apply_runtime_shims(tmp_path)
        run_command(["git", "init", "-q"], tmp_path, timeout_seconds)
        test_patch_result = None
        if test_patch_path is not None:
            test_patch_result = run_command(
                git_apply_command(test_patch_path),
                tmp_path,
                timeout_seconds,
            )
            if test_patch_result["returncode"] != 0:
                return {
                    **base_result(task_id, patch_path, workspace, test_command, test_patch_path, runtime_shims),
                    "task_score": 0.0,
                    "success": False,
                    "patch_applied": False,
                    "test_patch_applied": False,
                    "test_passed": False,
                    "apply_result": None,
                    "test_patch_result": test_patch_result,
                    "test_result": None,
                    "failure_reason": "test_patch_apply_failed",
                }
        apply_result = run_command(git_apply_command(patch_path), tmp_path, timeout_seconds)
        if apply_result["returncode"] != 0:
            return {
                **base_result(task_id, patch_path, workspace, test_command, test_patch_path, runtime_shims),
                "task_score": 0.0,
                "success": False,
                "patch_applied": False,
                "test_patch_applied": test_patch_path is not None,
                "test_passed": False,
                "apply_result": apply_result,
                "test_patch_result": test_patch_result,
                "test_result": None,
                "failure_reason": "patch_apply_failed",
            }

        test_result = run_command(test_command, tmp_path, timeout_seconds, shell=True)
        passed = test_result["returncode"] == 0
        return {
            **base_result(task_id, patch_path, workspace, test_command, test_patch_path, runtime_shims),
            "task_score": 1.0 if passed else 0.0,
            "success": passed,
            "patch_applied": True,
            "test_patch_applied": test_patch_path is not None,
            "test_passed": passed,
            "apply_result": apply_result,
            "test_patch_result": test_patch_result,
            "test_result": test_result,
            "failure_reason": "" if passed else "test_command_failed",
        }


def base_result(
    task_id: str,
    patch_path: Path,
    workspace: Path,
    test_command: str,
    test_patch_path: Path | None = None,
    runtime_shims: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "metric_name": "resolved" if task_id == "SWE-T1" else "tests_passed",
        "patch_path": patch_path.as_posix(),
        "test_patch_path": "" if test_patch_path is None else test_patch_path.as_posix(),
        "workspace": workspace.as_posix(),
        "test_command": test_command,
        "runtime_shims": runtime_shims or [],
        "evidence_boundary": (
            "Objective local patch scoring for one locked SWE output. This "
            "does not compare Summary and PaperToSkill or claim aggregate "
            "downstream effectiveness."
        ),
    }


def failure_result(task_id: str, patch_path: Path, workspace: Path, test_command: str, reason: str) -> dict[str, Any]:
    return {
        **base_result(task_id, patch_path, workspace, test_command),
        "task_score": 0.0,
        "success": False,
        "patch_applied": False,
        "test_patch_applied": False,
        "test_passed": False,
        "apply_result": None,
        "test_patch_result": None,
        "test_result": None,
        "failure_reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score locked SWE real-reuse patch outputs.")
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--test-command")
    parser.add_argument("--test-command-file", type=Path)
    parser.add_argument("--test-patch", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        test_command = read_test_command(args.test_command, args.test_command_file)
        result = score_patch(
            task_id=args.task,
            patch_path=args.patch,
            workspace=args.workspace,
            test_command=test_command,
            timeout_seconds=args.timeout_seconds,
            test_patch_path=args.test_patch,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.output_json:
        write_json(args.output_json, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
