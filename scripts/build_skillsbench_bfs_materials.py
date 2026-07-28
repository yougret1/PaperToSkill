#!/usr/bin/env python3
"""Build frozen SkillsBench B/F/S materials without calling a model.

F is the upstream curated SkillsBench bundle. S is produced by the pinned
independent SkillReducer implementation in heuristic mode. The adapter keeps
opaque package assets outside the textual reduction boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


SKILLSBENCH_COMMIT = "9a1f4dd5f7659f75707435da3ce854b6e48321d1"
REDUCER_COMMIT = "1c183b5b9f7ea814c40e9c9580a78b83aa71a783"
SELECTION_SEED = "skillsbench-bfs-sol-2026-07-27-v1"
CATEGORIES = (
    "cybersecurity",
    "finance-economics",
    "industrial-physical-systems",
    "mathematics-or-formal-reasoning",
    "media-content-production",
    "natural-science",
    "office-white-collar",
    "software-engineering",
)
PILOT_CATEGORIES = (
    "finance-economics",
    "media-content-production",
    "natural-science",
    "office-white-collar",
    "software-engineering",
)


@dataclass(frozen=True)
class TaskMetadata:
    task_id: str
    difficulty: str
    category: str
    network_mode: str
    cpus: int
    memory_mb: int
    gpus: int
    timeout_sec: int
    skill_count: int


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def git_head(root: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter: {path}")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Malformed YAML frontmatter: {path}")
    payload = yaml.safe_load(parts[1]) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Frontmatter is not a mapping: {path}")
    return payload


def discover_tasks(skillsbench_root: Path) -> dict[str, TaskMetadata]:
    tasks: dict[str, TaskMetadata] = {}
    for task_md in sorted((skillsbench_root / "tasks").glob("*/task.md")):
        task_id = task_md.parent.name
        payload = parse_frontmatter(task_md)
        metadata = payload.get("metadata") or {}
        sandbox = payload.get("sandbox") or {}
        agent = payload.get("agent") or {}
        skills = sorted((task_md.parent / "environment" / "skills").glob("*/SKILL.md"))
        tasks[task_id] = TaskMetadata(
            task_id=task_id,
            difficulty=str(metadata.get("difficulty", "")),
            category=str(metadata.get("category", "")),
            network_mode=str(sandbox.get("network_mode", "")),
            cpus=int(sandbox.get("cpus", 0)),
            memory_mb=int(sandbox.get("memory_mb", 0)),
            gpus=int(sandbox.get("gpus", 0)),
            timeout_sec=int(float(agent.get("timeout_sec", 0))),
            skill_count=len(skills),
        )
    return tasks


def load_reducer(reducer_root: Path):
    sys.path.insert(0, str(reducer_root))
    from skillreducer.config import Config  # type: ignore
    from skillreducer.pipeline import reduce_skill  # type: ignore

    config = Config(use_llm=False, tscg_enabled=False)
    return reduce_skill, config


def overlay_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        target = destination / path.relative_to(source)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def reduce_task_bundle(
    task_dir: Path,
    candidate_root: Path,
    reduce_skill,
    reducer_config,
) -> dict[str, Any]:
    task_id = task_dir.name
    source_skills = task_dir / "environment" / "skills"
    target_skills = candidate_root / task_id / "skills"
    if target_skills.exists():
        shutil.rmtree(target_skills)
    target_skills.mkdir(parents=True, exist_ok=True)

    skill_rows: list[dict[str, Any]] = []
    original_eager = 0
    reduced_eager = 0
    for skill_dir in sorted(path for path in source_skills.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        scratch_id = hashlib.sha256(f"{task_id}:{skill_dir.name}".encode("utf-8")).hexdigest()[:12]
        scratch = candidate_root / ".s" / scratch_id
        if scratch.exists():
            shutil.rmtree(scratch)
        scratch.mkdir(parents=True, exist_ok=True)
        report = reduce_skill(
            skill_md,
            output_dir=scratch,
            config=reducer_config,
            tscg=False,
        )
        reduced_dir = report.output
        target_dir = target_skills / skill_dir.name
        shutil.copytree(skill_dir, target_dir)
        overlay_tree(reduced_dir, target_dir)
        source_eager = report.original_stats.description + report.original_stats.body
        target_eager = report.optimized_stats.description + report.optimized_stats.body
        original_eager += source_eager
        reduced_eager += target_eager
        skill_rows.append(
            {
                "skill": skill_dir.name,
                "source_sha256": sha256_tree(skill_dir),
                "candidate_sha256": sha256_tree(target_dir),
                "original_eager_tokens": source_eager,
                "candidate_eager_tokens": target_eager,
                "eager_tokens_removed": source_eager - target_eager,
                "description_changed": report.description_changed,
                "stage_notes": list(report.stage_notes),
                "files_written": list(report.files_written),
            }
        )

    shutil.rmtree(candidate_root / ".s", ignore_errors=True)
    reduction = 0.0 if original_eager == 0 else 1.0 - reduced_eager / original_eager
    return {
        "task_id": task_id,
        "source_skills_sha256": sha256_tree(source_skills),
        "candidate_skills_sha256": sha256_tree(target_skills),
        "original_eager_tokens": original_eager,
        "candidate_eager_tokens": reduced_eager,
        "eager_reduction": reduction,
        "eligible": original_eager > reduced_eager,
        "skills": skill_rows,
    }


def rank(seed: str, task_id: str) -> str:
    return hashlib.sha256(f"{seed}:{task_id}".encode("utf-8")).hexdigest()


def resource_eligible(metadata: TaskMetadata) -> bool:
    return (
        metadata.difficulty in {"medium", "hard"}
        and metadata.network_mode != "no-network"
        and metadata.gpus == 0
        and metadata.cpus <= 4
        and metadata.memory_mb <= 8192
        and metadata.timeout_sec <= 3600
    )


def select_main(
    metadata: dict[str, TaskMetadata],
    reduction_rows: dict[str, dict[str, Any]],
) -> list[str]:
    selected: list[str] = []
    for category in CATEGORIES:
        category_rows = [
            row
            for row in metadata.values()
            if row.category == category
            and resource_eligible(row)
            and reduction_rows[row.task_id]["eligible"]
        ]
        for difficulty, count in (("hard", 1), ("medium", 2)):
            pool = [row.task_id for row in category_rows if row.difficulty == difficulty]
            pool.sort(key=lambda task_id: rank(f"{SELECTION_SEED}:{category}:{difficulty}", task_id))
            if len(pool) < count:
                raise ValueError(f"Insufficient {category}/{difficulty} tasks after frozen filters")
            selected.extend(pool[:count])
    return selected


def select_pilot(
    metadata: dict[str, TaskMetadata],
    reduction_rows: dict[str, dict[str, Any]],
    main_tasks: set[str],
) -> list[str]:
    selected: list[str] = []
    for category in PILOT_CATEGORIES:
        pool = [
            row.task_id
            for row in metadata.values()
            if row.category == category
            and row.task_id not in main_tasks
            and row.difficulty in {"easy", "medium"}
            and row.network_mode != "no-network"
            and row.gpus == 0
            and row.cpus <= 4
            and row.memory_mb <= 8192
            and row.timeout_sec <= 1800
            and reduction_rows[row.task_id]["eligible"]
        ]
        pool.sort(key=lambda task_id: rank(f"{SELECTION_SEED}:pilot:{category}", task_id))
        if not pool:
            raise ValueError(f"No pilot task available for {category}")
        selected.append(pool[0])
    return selected


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> dict[str, Any]:
    skillsbench_root = args.skillsbench_root.resolve()
    reducer_root = args.reducer_root.resolve()
    output_root = args.output_root.resolve()
    if git_head(skillsbench_root) != SKILLSBENCH_COMMIT:
        raise SystemExit("SkillsBench checkout does not match the frozen commit")
    if git_head(reducer_root) != REDUCER_COMMIT:
        raise SystemExit("Independent reducer checkout does not match the frozen commit")

    metadata = discover_tasks(skillsbench_root)
    if len(metadata) != 87:
        raise SystemExit(f"Expected 87 SkillsBench tasks, found {len(metadata)}")
    reduce_skill, reducer_config = load_reducer(reducer_root)
    candidate_root = output_root / "candidate_pool"
    candidate_root.mkdir(parents=True, exist_ok=True)

    reduction_rows: dict[str, dict[str, Any]] = {}
    for task_id in sorted(metadata):
        reduction_rows[task_id] = reduce_task_bundle(
            skillsbench_root / "tasks" / task_id,
            candidate_root,
            reduce_skill,
            reducer_config,
        )

    main_tasks = select_main(metadata, reduction_rows)
    pilot_tasks = select_pilot(metadata, reduction_rows, set(main_tasks))
    protocol = {
        "schema_version": "skillsbench-bfs-sol-v0",
        "created_at": utc_now(),
        "selection_seed": SELECTION_SEED,
        "skillsbench": {
            "root": str(skillsbench_root),
            "commit": SKILLSBENCH_COMMIT,
            "task_set": "skillsbench-v1.1",
        },
        "candidate_generator": {
            "root": str(reducer_root),
            "commit": REDUCER_COMMIT,
            "identity": "independent SkillReducer implementation",
            "mode": "heuristic/no-llm",
            "official_artifact": False,
        },
        "executor": {
            "agent": "codex-acp",
            "model": "gpt-5.6-sol",
            "api_protocol": "openai-responses",
            "conditions": ["B", "F", "S"],
        },
        "pilot": {
            "tasks": pilot_tasks,
            "repetitions": 1,
            "purpose": "pipeline-only; excluded from confirmatory estimates",
        },
        "main": {
            "tasks": main_tasks,
            "repetitions": 3,
            "strata": "one hard and two medium tasks per each of eight categories",
        },
        "selection_filters": {
            "candidate_must_reduce_eager_tokens": True,
            "network_mode_excluded": "no-network",
            "max_cpus": 4,
            "max_memory_mb": 8192,
            "max_agent_timeout_sec": 3600,
            "gpus": 0,
        },
        "stopping_rules": {
            "pilot_gate": "all selected rows terminal; official verifier emits reward; no B skill contamination",
            "baseline_ceiling_warning": "warn if pilot B pass rate >= 0.8; do not replace frozen main tasks",
            "protocol_incompatibility": "stop if codex-acp cannot use the Responses endpoint for terminal tools",
        },
        "candidate_pool": str(candidate_root),
    }
    manifest = {
        "schema_version": "skillsbench-bfs-materials-v0",
        "created_at": utc_now(),
        "protocol": protocol,
        "inventory": [asdict(metadata[task_id]) for task_id in sorted(metadata)],
        "candidates": [reduction_rows[task_id] for task_id in sorted(reduction_rows)],
        "counts": {
            "tasks": len(metadata),
            "eligible_candidates": sum(1 for row in reduction_rows.values() if row["eligible"]),
            "pilot_tasks": len(pilot_tasks),
            "main_tasks": len(main_tasks),
        },
    }
    write_json(output_root / "materials_manifest.json", manifest)
    write_json(output_root / "protocol.json", protocol)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skillsbench-root", type=Path, required=True)
    parser.add_argument("--reducer-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    manifest = build(parse_args())
    print(json.dumps(manifest["counts"], indent=2, sort_keys=True))
    print(json.dumps(manifest["protocol"]["pilot"], indent=2, sort_keys=True))
    print(json.dumps(manifest["protocol"]["main"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
