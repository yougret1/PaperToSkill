#!/usr/bin/env python
"""Prepare locked SWE-agent real-reuse fixture assets from a local repo snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1"
PREPARED_ON = "2026-07-03"
STATUS = "prepared_assets_ready_for_dry_scoring"
TASK_IDS = ("SWE-T1", "SWE-T2")


SWE_SUMMARY_FALLBACK = """# Real-Reuse Summary Baseline: {task_id}

SWE-agent improves software-engineering agents by shaping the agent-computer
interface. The method gives the language model concise search, navigation,
file-viewing, editing, execution feedback, and context-management tools so the
agent can inspect a repository, localize a bug, edit a focused patch, and verify
the result with tests.

For this locked task, use the issue or failing-test context, inspect files
before editing, produce a minimal unified diff, and verify with the requested
test command. Do not claim that tests passed unless the verification command
actually ran successfully.
"""


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_entry(root: Path, path: Path, slot: str, visibility: str) -> dict[str, str]:
    return {
        "slot": slot,
        "path": relative(root, path),
        "sha256": sha256_file(path),
        "visibility": visibility,
    }


def ignore_snapshot_names(_: str, names: list[str]) -> set[str]:
    ignored = {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "node_modules",
    }
    return {name for name in names if name in ignored}


def copy_repo_snapshot(source: Path, destination: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise ValueError(f"repo source does not exist or is not a directory: {source}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=ignore_snapshot_names)


def read_optional_text(text: str | None, path: Path | None) -> str:
    if path:
        return path.read_text(encoding="utf-8").strip()
    return (text or "").strip()


def load_lock(root: Path, task_id: str) -> dict[str, Any]:
    return load_json(root / "benchmarks" / "real_reuse" / "asset_locks" / f"{task_id}.json")


def load_swe_bench_instance(parquet_path: Path, instance_id: str) -> dict[str, Any]:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised only in missing envs.
        raise ValueError("pandas is required to read --swe-bench-parquet") from exc
    if not parquet_path.exists():
        raise ValueError(f"SWE-bench parquet does not exist: {parquet_path}")
    frame = pd.read_parquet(parquet_path)
    if "instance_id" not in frame.columns:
        raise ValueError(f"SWE-bench parquet is missing instance_id column: {parquet_path}")
    matches = frame[frame["instance_id"] == instance_id]
    if matches.empty:
        raise ValueError(f"instance_id {instance_id!r} not found in {parquet_path}")
    return matches.iloc[0].to_dict()


def default_issue_text(lock: dict[str, Any]) -> str:
    instance = lock.get("locked_task_instance", {})
    tests = "\n".join(f"- {item}" for item in instance.get("fail_to_pass", []))
    return f"""Locked SWE-bench-style instance: {instance.get('instance_id', 'unknown')}

Repository: {instance.get('repo', 'unknown')}
Base commit: {instance.get('base_commit', 'unknown')}

Target tests:
{tests or '- not declared'}

Create a minimal patch that addresses the issue represented by the failing
tests. Preserve unrelated behavior.
"""


def default_test_command(lock: dict[str, Any]) -> str:
    tests = lock.get("locked_task_instance", {}).get("fail_to_pass", [])
    if tests:
        return "python -m pytest " + " ".join(tests)
    return "python -m pytest"


def make_task_prompt(task_id: str, issue_text: str, test_command: str) -> str:
    task_label = "issue-to-patch" if task_id == "SWE-T1" else "failing-test-to-patch"
    return f"""# {task_id} Locked SWE-agent Task Prompt

Task type: {task_label}

You have a local repository snapshot in the starter workspace. The issue or
failing-test context is:

{issue_text}

Verification command:

```powershell
{test_command}
```

Return a single unified diff patch. The patch must apply cleanly from the
workspace root. Keep the change minimal, inspect files before editing, and do
not claim success unless the verification command passes.
"""


def write_summary_context(task_id: str, condition_dir: Path) -> Path:
    path = condition_dir / f"{task_id}_summary.md"
    write_text(path, SWE_SUMMARY_FALLBACK.format(task_id=task_id))
    return path


def source_context_entries(paths: list[Path] | None, labels: list[str] | None) -> list[tuple[str, Path]]:
    if not paths:
        return []
    labels = labels or []
    if labels and len(labels) != len(paths):
        raise ValueError("--source-context-label must be supplied once per --source-context-file")
    entries: list[tuple[str, Path]] = []
    for index, path in enumerate(paths):
        label = labels[index] if labels else path.as_posix()
        entries.append((label, path))
    return entries


def write_source_context(root: Path, output_dir: Path, entries: list[tuple[str, Path]]) -> Path | None:
    if not entries:
        return None
    blocks = [
        "# Model-Visible Source Context",
        "",
        "Evidence boundary: this source slice is model-visible and is provided "
        "equally to all primary conditions for a pre-registered source-context "
        "follow-up. It excludes scorer-only gold patches and hidden test patches.",
    ]
    for label, path in entries:
        resolved = resolve(root, path)
        if not resolved.exists() or not resolved.is_file():
            raise ValueError(f"source context file does not exist: {resolved}")
        blocks.extend(
            [
                "",
                f"## {label}",
                "",
                "```python",
                resolved.read_text(encoding="utf-8").rstrip(),
                "```",
            ]
        )
    source_context_path = output_dir / "source_context.md"
    write_text(source_context_path, "\n".join(blocks))
    return source_context_path


def prepare(args: argparse.Namespace) -> Path:
    root = args.root.resolve()
    task_id = args.task.upper()
    output_dir = resolve(root, args.output_dir)
    condition_dir = resolve(root, args.condition_dir)
    papertoskill_context = resolve(root, args.papertoskill_context)
    repo_source = resolve(root, args.repo_source)
    lock = load_lock(root, task_id)
    locked_instance = lock.get("locked_task_instance", {})
    instance_id = args.instance_id or locked_instance.get("instance_id", "")
    swe_bench_instance = None
    if args.swe_bench_parquet:
        swe_bench_instance = load_swe_bench_instance(resolve(root, args.swe_bench_parquet), instance_id)

    issue_text = (
        read_optional_text(args.issue_text, args.issue_file)
        or (str(swe_bench_instance.get("problem_statement", "")).strip() if swe_bench_instance else "")
        or default_issue_text(lock)
    )
    test_command = args.test_command or default_test_command(lock)

    output_dir.mkdir(parents=True, exist_ok=True)
    if args.workspace_mode == "copy":
        workspace_dir = output_dir / "workspace"
        copy_repo_snapshot(repo_source, workspace_dir)
        readme_path = workspace_dir / "README.papertoskill.md"
    else:
        if not repo_source.exists() or not repo_source.is_dir():
            raise ValueError(f"repo source does not exist or is not a directory: {repo_source}")
        workspace_dir = repo_source
        readme_path = output_dir / "workspace_readme.md"

    instance_path = output_dir / "instance_metadata.json"
    issue_path = output_dir / ("issue_description.md" if task_id == "SWE-T1" else "failing_test.md")
    test_command_path = output_dir / "target_test_command.txt"
    task_prompt_path = output_dir / "task_prompt.md"
    summary_path = write_summary_context(task_id, condition_dir)
    source_context_path = write_source_context(
        root,
        output_dir,
        source_context_entries(args.source_context_file, args.source_context_label),
    )

    instance_payload = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "source_paper_id": "swe_agent",
        "locked_task_instance": locked_instance,
        "selected_candidate_id": lock.get("selected_candidate_id"),
        "repo_source": str(repo_source),
        "swe_bench_parquet": "" if args.swe_bench_parquet is None else str(resolve(root, args.swe_bench_parquet)),
        "swe_bench_instance_id": instance_id,
        "test_command": test_command,
        "evidence_boundary": (
            "Prepared metadata for a local SWE real-reuse fixture. Gold patches "
            "or test patches are scorer-only and must not enter model-visible "
            "context."
        ),
    }
    write_json(instance_path, instance_payload)
    write_text(issue_path, issue_text)
    write_text(test_command_path, test_command)
    write_text(task_prompt_path, make_task_prompt(task_id, issue_text, test_command))
    write_text(
        readme_path,
        f"""# {task_id} Starter Workspace

Apply candidate unified diff patches from this directory. The verification
command is recorded in `../target_test_command.txt`.

Do not expose scorer-only gold patches or hidden test patches to the model.
""",
    )

    files = [
        file_entry(root, instance_path, "instance_metadata", "model_visible"),
        file_entry(root, issue_path, "issue_description" if task_id == "SWE-T1" else "failing_test", "model_visible"),
        file_entry(root, test_command_path, "target_test_command", "model_visible"),
        file_entry(root, task_prompt_path, "task_prompt", "model_visible"),
        file_entry(root, readme_path, "workspace_readme", "model_visible"),
        file_entry(root, summary_path, "summary_context", "condition_context"),
    ]
    if source_context_path is not None:
        files.append(file_entry(root, source_context_path, "source_context", "model_visible"))
    hidden_from_model: list[str] = []
    gold_patch_text = str(swe_bench_instance.get("patch", "")).strip() if swe_bench_instance else ""
    test_patch_text = str(swe_bench_instance.get("test_patch", "")).strip() if swe_bench_instance else ""
    if args.gold_patch or gold_patch_text:
        gold_patch = output_dir / "scorer_only" / "gold.patch"
        gold_patch.parent.mkdir(parents=True, exist_ok=True)
        if args.gold_patch:
            gold_patch_source = resolve(root, args.gold_patch)
            shutil.copy2(gold_patch_source, gold_patch)
        else:
            write_text(gold_patch, gold_patch_text)
        files.append(file_entry(root, gold_patch, "gold_patch", "scorer_only"))
        hidden_from_model.append(relative(root, gold_patch))
    if args.test_patch or test_patch_text:
        test_patch = output_dir / "scorer_only" / "test.patch"
        test_patch.parent.mkdir(parents=True, exist_ok=True)
        if args.test_patch:
            test_patch_source = resolve(root, args.test_patch)
            shutil.copy2(test_patch_source, test_patch)
        else:
            write_text(test_patch, test_patch_text)
        files.append(file_entry(root, test_patch, "test_patch", "scorer_only"))
        hidden_from_model.append(relative(root, test_patch))

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "papertoskill_real_reuse_v0",
        "task_id": task_id,
        "source_paper_id": "swe_agent",
        "status": STATUS,
        "prepared_on": PREPARED_ON,
        "evidence_boundary": (
            "Prepared SWE-agent fixture assets and condition contexts for dry "
            "scoring. This manifest does not run a model, compare Summary "
            "against PaperToSkill, score downstream outputs, or claim task "
            "success."
        ),
        "source_snapshot": {
            "repo_source": str(repo_source),
            "locked_task_instance": locked_instance,
            "swe_bench_parquet": ""
            if args.swe_bench_parquet is None
            else relative(root, resolve(root, args.swe_bench_parquet)),
            "swe_bench_instance_id": instance_id,
        },
        "license_and_provenance": {
            "source_urls": [item.get("url", "") for item in lock.get("source_revision_locks", [])],
            "local_use_scope": "locked local SWE real-reuse fixture for reproducible experiment setup",
            "redistribution_note": "Do not redistribute third-party repository snapshots without checking their licenses.",
        },
        "condition_contexts": [
            {"condition": "summary", "path": relative(root, summary_path), "visibility": "model_visible"},
            {"condition": "papertoskill", "path": relative(root, papertoskill_context), "visibility": "model_visible"},
        ],
        "workspace_dir": relative(root, workspace_dir),
        "hidden_from_model": hidden_from_model,
        "asset_dir": relative(root, output_dir),
        "files": files,
    }
    manifest_path = output_dir / "asset_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare locked SWE real-reuse fixture assets.")
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--repo-source", type=Path, required=True)
    parser.add_argument("--workspace-mode", choices=("copy", "external"), default="copy")
    parser.add_argument("--issue-text")
    parser.add_argument("--issue-file", type=Path)
    parser.add_argument("--test-command")
    parser.add_argument("--gold-patch", type=Path)
    parser.add_argument("--test-patch", type=Path)
    parser.add_argument("--source-context-file", type=Path, action="append")
    parser.add_argument("--source-context-label", action="append")
    parser.add_argument("--swe-bench-parquet", type=Path)
    parser.add_argument("--instance-id")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition-dir", type=Path, default=Path("baselines/real_reuse"))
    parser.add_argument(
        "--papertoskill-context",
        type=Path,
        default=Path("generated_skills/real_reuse/swe_agent/SKILL.md"),
    )
    args = parser.parse_args()

    try:
        manifest_path = prepare(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
