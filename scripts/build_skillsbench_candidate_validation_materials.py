#!/usr/bin/env python3
"""Build frozen materials for the minimal SkillsBench candidate validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "skillsbench-candidate-validation-materials-v1"
TASKS = (
    "flink-query",
    "lab-unit-harmonization",
    "sec-financial-report",
    "organize-messy-files",
)
PILOT_TASK = "threejs-to-obj"
SCREEN_REPETITIONS = 3
CONFIRM_REPETITIONS = 48
MODEL = "gpt-5.6-sol"
SELECTION_SEED = "skillsbench-candidate-validation-2026-07-27-v1"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str | None:
    if not root.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def frontmatter_only(text: str) -> str:
    lines = text.splitlines()
    require(lines and lines[0].strip() == "---", "SKILL.md lacks YAML frontmatter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[: index + 1]) + "\n"
    raise RuntimeError("SKILL.md has unterminated YAML frontmatter")


def copy_preserving_candidate(source: Path, destination: Path) -> None:
    require(source.is_dir(), f"preserving candidate missing: {source}")
    shutil.copytree(source, destination)


def build_body_drop_candidate(source: Path, destination: Path) -> dict[str, Any]:
    require(source.is_dir(), f"official skill directory missing: {source}")
    rows: list[dict[str, Any]] = []
    for skill_dir in sorted(item for item in source.iterdir() if item.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        require(skill_md.is_file(), f"official skill lacks SKILL.md: {skill_dir}")
        target = destination / skill_dir.name
        target.mkdir(parents=True, exist_ok=True)
        original = skill_md.read_text(encoding="utf-8")
        reduced = frontmatter_only(original)
        (target / "SKILL.md").write_text(reduced, encoding="utf-8")
        rows.append(
            {
                "skill": skill_dir.name,
                "source_sha256": sha256_file(skill_md),
                "candidate_sha256": sha256_file(target / "SKILL.md"),
                "source_bytes": len(original.encode("utf-8")),
                "candidate_bytes": len(reduced.encode("utf-8")),
                "rule": "retain byte-identical YAML frontmatter; remove all procedural body and auxiliary resources",
            }
        )
    require(rows, f"no skills found under {source}")
    return {"skills": rows}


def protocol(
    *,
    skillsbench_root: Path,
    candidate_pools: dict[str, Path],
    main_tasks: list[str],
    main_repetitions: int,
    conditions: list[str],
    phase: str,
) -> dict[str, Any]:
    return {
        "schema_version": "skillsbench-candidate-validation-protocol-v1",
        "created_at": utc_now(),
        "selection_seed": f"{SELECTION_SEED}:{phase}",
        "skillsbench": {
            "root": str(skillsbench_root.resolve()),
            "commit": "9a1f4dd5f7659f75707435da3ce854b6e48321d1",
            "task_set": "skillsbench-v1.1",
        },
        "executor": {
            "agent": "codex-acp",
            "model": MODEL,
            "conditions": conditions,
        },
        "candidate_pools": {
            key: str(value.resolve()) for key, value in sorted(candidate_pools.items())
        },
        "pilot": {"tasks": [PILOT_TASK], "repetitions": 1},
        "main": {"tasks": main_tasks, "repetitions": main_repetitions},
        "evidence_boundary": {
            "benchmark": "public official task and deterministic verifier",
            "source_binding": "official SkillsBench skill artifacts, not paper source spans",
            "P": "independent SkillReducer heuristic output; not the official SkillReducer artifact",
            "D": "uniform deterministic body-drop negative control",
            "candidate_outcomes_used_for_selection": False,
        },
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    require(not output.exists(), f"output already exists: {output}")
    skillsbench_root = args.skillsbench_root.resolve()
    bfs_materials = args.bfs_materials.resolve()
    require(skillsbench_root.is_dir(), f"SkillsBench root missing: {skillsbench_root}")
    require(bfs_materials.is_dir(), f"B/F/S materials missing: {bfs_materials}")

    p_pool = output / "candidate_pool" / "P"
    d_pool = output / "candidate_pool" / "D"
    task_rows: list[dict[str, Any]] = []
    for task_id in (*TASKS, PILOT_TASK):
        official = skillsbench_root / "tasks" / task_id / "environment" / "skills"
        preserving = bfs_materials / "candidate_pool" / task_id / "skills"
        p_target = p_pool / task_id / "skills"
        d_target = d_pool / task_id / "skills"
        p_target.parent.mkdir(parents=True, exist_ok=True)
        d_target.parent.mkdir(parents=True, exist_ok=True)
        copy_preserving_candidate(preserving, p_target)
        destructive = build_body_drop_candidate(official, d_target)
        task_rows.append(
            {
                "task_id": task_id,
                "official_skills_sha256": sha256_tree(official),
                "P_skills_sha256": sha256_tree(p_target),
                "D_skills_sha256": sha256_tree(d_target),
                "D_details": destructive,
            }
        )

    screening = protocol(
        skillsbench_root=skillsbench_root,
        candidate_pools={},
        main_tasks=list(TASKS),
        main_repetitions=SCREEN_REPETITIONS,
        conditions=["B", "F"],
        phase="screen",
    )
    screening["selection_rule"] = {
        "uses_conditions": ["B", "F"],
        "forbidden_conditions": ["P", "D"],
        "eligible": "all six B/F rows valid, k_B <= 1, k_F >= 2, and k_F > k_B",
        "ranking": ["descending k_F-k_B", "descending k_F", "ascending k_B", "SHA-256 seeded tie break"],
        "confirmatory_task_count": 2,
        "pilot_rows_excluded": True,
        "screening_rows_excluded": True,
    }
    screening["candidate_hashes_frozen_before_screening"] = task_rows
    atomic_json(output / "screen_protocol.json", screening)

    labels = {
        "schema_version": "skillsbench-candidate-blind-labels-v1",
        "created_at": utc_now(),
        "outcome_access": "prohibited",
        "reviewer_fields": [
            "reviewer_id",
            "task_id",
            "P_label",
            "D_label",
            "P_rationale",
            "D_rationale",
            "reviewed_at",
        ],
        "allowed_labels": ["intended-preserving", "destructive", "unclear"],
        "records": [],
    }
    atomic_json(output / "blind_label_template.json", labels)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "tasks": task_rows,
        "screen_tasks": list(TASKS),
        "pilot_task": PILOT_TASK,
        "screen_protocol_sha256": sha256_file(output / "screen_protocol.json"),
        "blind_label_template_sha256": sha256_file(output / "blind_label_template.json"),
        "P_pool_sha256": sha256_tree(p_pool),
        "D_pool_sha256": sha256_tree(d_pool),
        "confirmatory_repetitions_per_arm": CONFIRM_REPETITIONS,
        "decision_policy": {
            "b_max": 5,
            "f_min": 43,
            "s_min": 43,
            "noninferiority_margin": 2 / 18,
            "interval": "two-sided 95% Newcombe hybrid-score",
            "success": "official_reward == 1.0",
        },
    }
    atomic_json(output / "materials_manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skillsbench-root", type=Path, default=Path(r"D:\a_work\gitee\skillsbench")
    )
    parser.add_argument(
        "--bfs-materials",
        type=Path,
        default=Path("research/workflow_runs/skillsbench_bfs_sol/materials_v0"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/workflow_runs/skillsbench_candidate_validation_sol/materials_v1"),
    )
    return parser.parse_args()


def main() -> int:
    manifest = build(parse_args())
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
