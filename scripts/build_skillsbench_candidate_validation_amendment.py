#!/usr/bin/env python3
"""Build the one-shot, outcome-blind SEC preserving-candidate amendment."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "skillsbench-candidate-validation-amendment-v1"
SKILLSBENCH_COMMIT = "9a1f4dd5f7659f75707435da3ce854b6e48321d1"
REDUCER_COMMIT = "1c183b5b9f7ea814c40e9c9580a78b83aa71a783"
TASK_ID = "sec-financial-report"
STAGE = 1


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


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
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    process = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    require(process.returncode == 0, f"git {' '.join(arguments)} failed for {root}")
    return process.stdout.strip()


def require_clean_pinned_checkout(root: Path, expected_commit: str, label: str) -> None:
    require(root.is_dir(), f"{label} checkout missing: {root}")
    require(git_output(root, "rev-parse", "HEAD") == expected_commit, f"{label} commit changed")
    require(not git_output(root, "status", "--porcelain"), f"{label} checkout is dirty")


def verify_original_labels(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    require(payload.get("outcome_access") == "prohibited", "original labels accessed outcomes")
    records = [
        row
        for row in payload.get("records") or []
        if isinstance(row, dict) and row.get("task_id") == TASK_ID
    ]
    reviewers = {str(row.get("reviewer_id")) for row in records}
    require(len(reviewers) >= 2, "SEC P1 has fewer than two independent labels")
    require(
        {row.get("P_label") for row in records} == {"destructive"},
        "SEC P1 was not unanimously labelled destructive",
    )
    require(
        {row.get("D_label") for row in records} == {"destructive"},
        "SEC D was not unanimously labelled destructive",
    )
    return {"reviewer_count": len(reviewers), "P": "destructive", "D": "destructive"}


def verify_screen_has_no_candidate_arms(run_root: Path) -> dict[str, Any]:
    schedule_path = run_root / "schedule.json"
    state_path = run_root / "run_state.jsonl"
    require(schedule_path.is_file(), f"screen schedule missing: {schedule_path}")
    require(state_path.is_file(), f"screen state missing: {state_path}")
    schedule = load_json(schedule_path)
    jobs = schedule.get("jobs") or []
    require(isinstance(jobs, list), "screen schedule jobs missing")
    scheduled_conditions = {str(row.get("condition")) for row in jobs if isinstance(row, dict)}
    require(not (scheduled_conditions & {"P", "D"}), "screen schedule contains P/D")
    observed_conditions: set[str] = set()
    for line in state_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("condition") is not None:
            observed_conditions.add(str(row["condition"]))
    require(not (observed_conditions & {"P", "D"}), "screen state contains P/D")
    return {
        "schedule_sha256": sha256_file(schedule_path),
        "run_state_sha256_at_amendment": sha256_file(state_path),
        "scheduled_conditions": sorted(scheduled_conditions),
        "observed_conditions": sorted(observed_conditions),
    }


def overlay_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        target = destination / path.relative_to(source)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def non_skill_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(item for item in root.rglob("*") if item.is_file())
        if path.name.lower() != "skill.md"
    }


def generate_sec_p2(
    *,
    official_skills: Path,
    target_skills: Path,
    reducer_root: Path,
) -> dict[str, Any]:
    sys.path.insert(0, str(reducer_root))
    from skillreducer.config import Config  # type: ignore
    from skillreducer.parser import parse_skill_md  # type: ignore
    from skillreducer.pipeline import reduce_skill  # type: ignore

    config = Config(use_llm=False, tscg_enabled=False)
    rows: list[dict[str, Any]] = []
    original_eager = 0
    candidate_eager = 0
    scratch_root = target_skills.parent / ".scratch"
    for source_dir in sorted(path for path in official_skills.iterdir() if path.is_dir()):
        skill_md = source_dir / "SKILL.md"
        require(skill_md.is_file(), f"official skill lacks SKILL.md: {source_dir}")
        scratch = scratch_root / source_dir.name
        scratch.mkdir(parents=True, exist_ok=True)
        report = reduce_skill(
            skill_md,
            output_dir=scratch,
            config=config,
            stage=STAGE,
            tscg=False,
        )
        target_dir = target_skills / source_dir.name
        shutil.copytree(source_dir, target_dir)
        overlay_tree(report.output, target_dir)

        source_skill = parse_skill_md(skill_md)
        candidate_skill = parse_skill_md(target_dir / "SKILL.md")
        require(candidate_skill.body == source_skill.body, f"{source_dir.name}: P2 body changed")
        require(
            non_skill_hashes(target_dir) == non_skill_hashes(source_dir),
            f"{source_dir.name}: P2 auxiliary assets changed",
        )
        source_eager = report.original_stats.description + report.original_stats.body
        target_eager = report.optimized_stats.description + report.optimized_stats.body
        original_eager += source_eager
        candidate_eager += target_eager
        rows.append(
            {
                "skill": source_dir.name,
                "source_sha256": sha256_tree(source_dir),
                "P2_sha256": sha256_tree(target_dir),
                "source_eager_tokens": source_eager,
                "P2_eager_tokens": target_eager,
                "body_preserved": True,
                "auxiliary_assets_preserved": True,
                "stage_notes": list(report.stage_notes),
            }
        )
    shutil.rmtree(scratch_root, ignore_errors=True)
    require(rows, "SEC official skill bundle is empty")
    require(candidate_eager < original_eager, "SEC P2 does not reduce eager tokens")
    return {
        "skills": rows,
        "source_eager_tokens": original_eager,
        "P2_eager_tokens": candidate_eager,
        "eager_reduction": 1.0 - candidate_eager / original_eager,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    materials = args.materials.resolve()
    output = args.output.resolve()
    skillsbench_root = args.skillsbench_root.resolve()
    reducer_root = args.reducer_root.resolve()
    screen_run = args.screen_run.resolve()
    require(materials.is_dir(), f"base materials missing: {materials}")
    require(not output.exists(), f"amendment output already exists: {output}")
    require(output.parent == (materials / "amendments").resolve(), "output must be under materials/amendments")
    require(output.name == "sec_p2_v1", "amendment output must be named sec_p2_v1")
    require_clean_pinned_checkout(skillsbench_root, SKILLSBENCH_COMMIT, "SkillsBench")
    require_clean_pinned_checkout(reducer_root, REDUCER_COMMIT, "reducer")

    manifest_path = materials / "materials_manifest.json"
    screen_protocol_path = materials / "screen_protocol.json"
    original_labels_path = materials / "blind_labels.json"
    for path in (manifest_path, screen_protocol_path, original_labels_path):
        require(path.is_file(), f"base material missing: {path}")
    manifest = load_json(manifest_path)
    task_row = next(
        (row for row in manifest.get("tasks") or [] if row.get("task_id") == TASK_ID),
        None,
    )
    require(isinstance(task_row, dict), "SEC row missing from base materials manifest")
    original_consensus = verify_original_labels(original_labels_path)
    screen_evidence = verify_screen_has_no_candidate_arms(screen_run)

    official_skills = skillsbench_root / "tasks" / TASK_ID / "environment" / "skills"
    base_p1 = materials / "candidate_pool" / "P" / TASK_ID / "skills"
    base_d = materials / "candidate_pool" / "D" / TASK_ID / "skills"
    require(sha256_tree(official_skills) == task_row.get("official_skills_sha256"), "SEC official tree changed")
    require(sha256_tree(base_p1) == task_row.get("P_skills_sha256"), "SEC P1 tree changed")
    require(sha256_tree(base_d) == task_row.get("D_skills_sha256"), "SEC D tree changed")

    effective_p_root = output / "effective_candidate_pool" / "P"
    output.mkdir(parents=True)
    shutil.copytree(materials / "candidate_pool" / "P", effective_p_root)
    shutil.rmtree(effective_p_root / TASK_ID)
    p2_skills = effective_p_root / TASK_ID / "skills"
    p2_skills.mkdir(parents=True)
    p2_details = generate_sec_p2(
        official_skills=official_skills,
        target_skills=p2_skills,
        reducer_root=reducer_root,
    )

    generator_contract = {
        "identity": "independent SkillReducer implementation",
        "commit": REDUCER_COMMIT,
        "mode": "heuristic/no-llm",
        "stage": STAGE,
        "tscg": False,
        "configuration": {
            "use_llm": False,
            "tscg_enabled": False,
            "short_description_tokens": 40,
            "max_restore_steps": 3,
        },
    }
    contract_path = output / "generator_contract.json"
    atomic_json(contract_path, generator_contract)
    amendment = {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "task_id": TASK_ID,
        "trigger": "unanimous-destructive-specification-label",
        "one_shot": True,
        "no_further_regeneration": True,
        "outcome_access": "prohibited",
        "candidate_outcomes_used": False,
        "selection_effect": "replace P1 with P2 for specification eligibility; retain original B/F screening",
        "base_bindings": {
            "materials_manifest_sha256": sha256_file(manifest_path),
            "screen_protocol_sha256": sha256_file(screen_protocol_path),
            "original_blind_labels_sha256": sha256_file(original_labels_path),
            "original_consensus": original_consensus,
            "screen_evidence": screen_evidence,
        },
        "source": {
            "skillsbench_commit": SKILLSBENCH_COMMIT,
            "official_skills_sha256": sha256_tree(official_skills),
        },
        "generator": generator_contract,
        "generator_contract_sha256": sha256_file(contract_path),
        "candidate": {
            "P1_skills_sha256": sha256_tree(base_p1),
            "P2_skills_sha256": sha256_tree(p2_skills),
            "D_skills_sha256": sha256_tree(base_d),
            "effective_P_pool_sha256": sha256_tree(effective_p_root),
            "P2_details": p2_details,
        },
        "paths": {
            "effective_P_pool": "effective_candidate_pool/P",
            "new_blind_labels": "blind_labels.json",
        },
    }
    amendment_path = output / "amendment.json"
    atomic_json(amendment_path, amendment)
    binding = {
        "schema_version": "skillsbench-candidate-validation-amendment-binding-v1",
        "created_at": utc_now(),
        "amendment": "amendment.json",
        "amendment_sha256": sha256_file(amendment_path),
        "generator_contract": "generator_contract.json",
        "generator_contract_sha256": sha256_file(contract_path),
    }
    atomic_json(output / "binding.json", binding)
    return {**binding, "output": str(output), "P2_skills_sha256": amendment["candidate"]["P2_skills_sha256"]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--materials", type=Path, required=True)
    parser.add_argument("--skillsbench-root", type=Path, required=True)
    parser.add_argument("--reducer-root", type=Path, required=True)
    parser.add_argument("--screen-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    result = build(parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
