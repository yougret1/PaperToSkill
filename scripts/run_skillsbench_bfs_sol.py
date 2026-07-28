#!/usr/bin/env python3
"""Run frozen SkillsBench B/F/S trials with GPT-5.6 Sol through BenchFlow.

The runner consumes materials produced by ``build_skillsbench_bfs_materials.py``.
It never reads credentials from files: the parent process supplies a named API
key and base-URL environment variable, which are mirrored to the names expected
by ``codex-acp`` only in the child environment.

Typical flow::

    python scripts/run_skillsbench_bfs_sol.py prepare --run-root <run>
    python scripts/run_skillsbench_bfs_sol.py run --run-root <run> --phase pilot
    python scripts/run_skillsbench_bfs_sol.py run --run-root <run> --phase main
    python scripts/run_skillsbench_bfs_sol.py audit --run-root <run>
    python scripts/run_skillsbench_bfs_sol.py summarize --run-root <run>

``plan`` and ``--dry-run`` never invoke BenchFlow or a model.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "skillsbench-bfs-sol-runner-v1"
MODEL = "gpt-5.6-sol"
MODEL_ALIAS = MODEL
AGENT = "codex-acp"
BACKEND = "docker"
CONDITIONS = ("B", "F", "S")
SUPPORTED_CONDITIONS = ("B", "F", "S", "P", "D")
PHASES = ("pilot", "main")
FROZEN_EXPECTED_ROWS = {"pilot": 15, "main": 216}
DEFAULT_CONCURRENCY = 2
MAX_CONCURRENCY = 400
DEFAULT_PROCESS_TIMEOUT_SECONDS = 7_200
DEFAULT_API_KEY_ENV = "PAPERTOSKILL_GPT_OPENAI_API_KEY"
DEFAULT_BASE_URL_ENV = "PAPERTOSKILL_GPT_OPENAI_BASE_URL"

TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
}
TRAJECTORY_PATTERNS = (
    "**/trajectory.json",
    "**/trajectory/*.json",
    "**/trajectory/*.jsonl",
    "**/trajectory*.jsonl",
    "**/agent/*.json",
    "**/agent/*.jsonl",
    "**/agent/*.txt",
    "**/codex*.txt",
)
STATIC_SKILL_PATH_MARKERS = (
    "/root/.agents/skills",
    "/root/.codex/skills",
    "/etc/codex/skills",
    "/root/.claude/skills",
    "/root/.gemini/skills",
    "/skills",
)
RUNTIME_CONTAMINATION_PATTERNS = (
    ("skill_xml", re.compile(r"<skills?>|<skill_content", re.IGNORECASE)),
    (
        "skill_base_directory",
        re.compile(r"base directory for this skill", re.IGNORECASE),
    ),
    (
        "codex_skill_path",
        re.compile(r"(?:\.agents|\.codex|/etc/codex)/skills", re.IGNORECASE),
    ),
    ("container_skill_path", re.compile(r"(?:^|[\s\"'])/skills/", re.IGNORECASE)),
    ("skill_file", re.compile(r"(?:^|[/\\])SKILL\.md\b", re.IGNORECASE)),
    ("codex_skill_event", re.compile(r"codex\.skill\.injected", re.IGNORECASE)),
)
INFRA_ERROR_PATTERNS = (
    "No space left on device",
    "Cannot connect to the Docker daemon",
    "Docker compose command failed",
    "docker compose",
    "ImageBuildError",
    "AgentInstallError",
    "NonZeroAgentExitCodeError",
    "RateLimitError",
    "BadRequestError",
    "AgentTimeoutError",
    "VerifierTimeoutError",
    "Could not resolve host",
    "ECONNRESET",
    "ETIMEDOUT",
    "ENOTFOUND",
    "Temporary failure in name resolution",
)
GENERIC_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(
        r"(?i)(\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\b\s*[:=]\s*)"
        r"([^\s,;\"']{6,})"
    ),
)


class RunnerError(RuntimeError):
    """A deterministic experiment-contract violation."""


@dataclass(frozen=True)
class Job:
    execution_id: str
    block_id: str
    phase: str
    repetition: int
    task_id: str
    condition: str
    condition_position: int
    task_position: int
    source_task_dir: str
    mirror_task_dir: str
    skills_dir: str | None
    jobs_dir: str


@dataclass
class RunRecord:
    schema_version: str
    event: str
    timestamp: str
    execution_id: str
    block_id: str
    task_id: str
    condition: str
    phase: str
    repetition: int
    condition_position: int
    attempt_number: int
    status: str
    invalid: bool
    invalid_reasons: list[str]
    official_reward: float | None
    success: bool | None
    return_code: int
    duration_sec: float
    result_path: str | None
    official_result_path: str | None
    official_reward_path: str | None
    trajectory_path: str | None
    jobs_dir: str
    stdout_path: str
    stderr_path: str
    error: str | None
    verifier_error: str | None
    infra_error: bool
    infra_error_markers: list[str]
    b_contaminated: bool
    b_contamination_markers: list[str]
    credential_reflection_detected: bool
    mirror_fingerprint_before: dict[str, Any]
    mirror_fingerprint_after: dict[str, Any]
    platform_repairs_sha256: str
    command: list[str]
    credential_values_recorded: bool


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_materials_root() -> Path:
    return workspace_root() / "research" / "workflow_runs" / "skillsbench_bfs_sol" / "materials_v0"


def default_runs_root() -> Path:
    return workspace_root() / "research" / "workflow_runs" / "skillsbench_bfs_sol" / "runs"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RunnerError(message)


def canonical_json(payload: Any) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, payload: Any) -> None:
    atomic_write(path, canonical_json(payload))


def atomic_text(path: Path, payload: str) -> None:
    atomic_write(path, payload.encode("utf-8"))


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = canonical_json(payload)
    with path.open("ab") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_head(root: Path) -> str:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return process.stdout.strip() if process.returncode == 0 else "unknown"


def stable_id(prefix: str, *parts: object) -> str:
    value = "|".join(str(part) for part in parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(value).hexdigest()[:24]}"


def relative_or_absolute(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


class Redactor:
    """Redact known environment secrets and common credential-shaped strings."""

    def __init__(self, run_env: dict[str, str]) -> None:
        secret_name = re.compile(
            r"(?i)(?:api[_-]?key|token|secret|password|credential|cookie|authorization)"
        )
        values: list[tuple[str, str]] = []
        for name, value in run_env.items():
            if secret_name.search(name) and isinstance(value, str) and len(value) >= 6:
                values.append((value, f"[REDACTED:{name}]"))
        self._values = sorted(set(values), key=lambda item: len(item[0]), reverse=True)

    def contains_secret(self, text: str) -> bool:
        if any(value in text for value, _ in self._values):
            return True
        return any(pattern.search(text) for pattern in GENERIC_SECRET_PATTERNS)

    def text(self, text: str) -> str:
        redacted = text
        for value, replacement in self._values:
            redacted = redacted.replace(value, replacement)
        redacted = GENERIC_SECRET_PATTERNS[0].sub("[REDACTED:API_KEY]", redacted)
        redacted = GENERIC_SECRET_PATTERNS[1].sub("Bearer [REDACTED:TOKEN]", redacted)
        redacted = GENERIC_SECRET_PATTERNS[2].sub(r"\1[REDACTED]", redacted)
        return redacted

    def value(self, payload: Any) -> Any:
        if isinstance(payload, str):
            return self.text(payload)
        if isinstance(payload, list):
            return [self.value(item) for item in payload]
        if isinstance(payload, tuple):
            return [self.value(item) for item in payload]
        if isinstance(payload, dict):
            return {str(key): self.value(value) for key, value in payload.items()}
        return payload


def redact_text_tree(root: Path, redactor: Redactor) -> tuple[int, bool]:
    """Redact BenchFlow-owned text artifacts before this runner parses them."""
    changed = 0
    reflected = False
    if not root.is_dir():
        return changed, reflected
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        had_secret = redactor.contains_secret(text)
        safe = redactor.text(text)
        reflected = reflected or had_secret
        if safe != text:
            atomic_text(path, safe)
            changed += 1
    return changed, reflected


def load_protocol(materials_root: Path) -> tuple[dict[str, Any], Path]:
    path = materials_root / "protocol.json"
    require(path.is_file(), f"missing frozen protocol: {path}")
    protocol = load_json(path)
    require(isinstance(protocol, dict), "protocol must be a JSON object")
    executor = protocol.get("executor") or {}
    require(executor.get("agent") == AGENT, f"protocol agent must be {AGENT}")
    require(executor.get("model") == MODEL_ALIAS, f"protocol model must be {MODEL_ALIAS}")
    conditions = tuple(executor.get("conditions") or ())
    require(conditions, "protocol conditions missing")
    require(len(conditions) == len(set(conditions)), "protocol conditions are not unique")
    require("B" in conditions and "F" in conditions, "protocol must include B and F")
    require(
        set(conditions).issubset(SUPPORTED_CONDITIONS),
        f"unsupported protocol conditions: {sorted(set(conditions) - set(SUPPORTED_CONDITIONS))}",
    )
    for phase in PHASES:
        value = protocol.get(phase) or {}
        tasks = value.get("tasks")
        repetitions = value.get("repetitions")
        require(isinstance(tasks, list) and tasks, f"protocol {phase} tasks missing")
        require(
            isinstance(repetitions, int) and repetitions > 0,
            f"protocol {phase} repetitions invalid",
        )
        require(len(tasks) == len(set(tasks)), f"protocol {phase} tasks are not unique")
    overlap = set(protocol["pilot"]["tasks"]) & set(protocol["main"]["tasks"])
    require(not overlap, f"pilot/main task overlap: {sorted(overlap)}")
    return protocol, path


def protocol_skillsbench_root(protocol: dict[str, Any], override: Path | None) -> Path:
    path = override or Path(str(protocol["skillsbench"]["root"]))
    return path.resolve()


def protocol_candidate_pool(protocol: dict[str, Any], materials_root: Path) -> Path:
    raw = Path(str(protocol["candidate_pool"]))
    path = raw if raw.is_absolute() else materials_root / raw
    return path.resolve()


def protocol_conditions(protocol: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(value) for value in protocol["executor"]["conditions"])


def protocol_candidate_pools(
    protocol: dict[str, Any], materials_root: Path
) -> dict[str, Path]:
    raw_pools = protocol.get("candidate_pools")
    if raw_pools is None:
        raw_pools = {"S": protocol.get("candidate_pool")}
    require(isinstance(raw_pools, dict), "candidate_pools must be an object")
    pools: dict[str, Path] = {}
    for condition in protocol_conditions(protocol):
        if condition in {"B", "F"}:
            continue
        raw = raw_pools.get(condition)
        require(isinstance(raw, str) and raw, f"candidate pool missing for {condition}")
        path = Path(raw)
        pools[condition] = (path if path.is_absolute() else materials_root / path).resolve()
    return pools


def condition_order(
    seed: str,
    phase: str,
    task_id: str,
    repetition: int,
    conditions: Sequence[str] = CONDITIONS,
) -> list[str]:
    permutations = list(itertools.permutations(conditions))
    digest = hashlib.sha256(f"{seed}:{phase}:{task_id}".encode("utf-8")).digest()
    base = list(permutations[int.from_bytes(digest[:4], "big") % len(permutations)])
    offset = (repetition - 1) % len(conditions)
    return base[offset:] + base[:offset]


def build_schedule(
    protocol: dict[str, Any],
    run_root: Path,
    skillsbench_root: Path,
) -> list[Job]:
    seed = str(protocol["selection_seed"])
    conditions = protocol_conditions(protocol)
    jobs: list[Job] = []
    task_position = 0
    for phase in PHASES:
        phase_spec = protocol[phase]
        repetitions = int(phase_spec["repetitions"])
        for repetition in range(1, repetitions + 1):
            for task_id in phase_spec["tasks"]:
                task_position += 1
                block_id = stable_id("sb-block", seed, phase, repetition, task_id)
                for condition_position, condition in enumerate(
                    condition_order(seed, phase, task_id, repetition, conditions), start=1
                ):
                    execution_id = stable_id(
                        "sb-exec", seed, phase, repetition, task_id, condition
                    )
                    mirror = run_root / "work" / condition / task_id
                    skills_dir = (
                        mirror / "environment" / "skills" if condition != "B" else None
                    )
                    jobs_dir = (
                        run_root
                        / "jobs"
                        / phase
                        / f"r{repetition}"
                        / condition
                        / task_id
                    )
                    jobs.append(
                        Job(
                            execution_id=execution_id,
                            block_id=block_id,
                            phase=phase,
                            repetition=repetition,
                            task_id=str(task_id),
                            condition=condition,
                            condition_position=condition_position,
                            task_position=task_position,
                            source_task_dir=str(skillsbench_root / "tasks" / task_id),
                            mirror_task_dir=str(mirror),
                            skills_dir=str(skills_dir) if skills_dir else None,
                            jobs_dir=str(jobs_dir),
                        )
                    )
    return jobs


def selected_jobs(jobs: Sequence[Job], args: argparse.Namespace) -> list[Job]:
    phases = set(args.phase or ["pilot"])
    repetitions = set(args.repetition or [])
    tasks = set(args.task or [])
    available_conditions = {job.condition for job in jobs if job.phase in phases}
    conditions = set(args.condition or available_conditions)
    available_tasks = {job.task_id for job in jobs if job.phase in phases}
    unknown_tasks = sorted(tasks - available_tasks)
    require(not unknown_tasks, f"task(s) outside selected phase: {unknown_tasks}")
    selected = [
        job
        for job in jobs
        if job.phase in phases
        and (not repetitions or job.repetition in repetitions)
        and (not tasks or job.task_id in tasks)
        and job.condition in conditions
    ]
    if repetitions:
        valid_repetitions = {job.repetition for job in jobs if job.phase in phases}
        invalid = sorted(repetitions - valid_repetitions)
        require(not invalid, f"repetition(s) outside selected phase: {invalid}")
    require(selected, "selection produced no jobs")
    return selected


def hardlink_or_copy(source: str, destination: str, *, follow_symlinks: bool = True) -> str:
    try:
        os.link(source, destination, follow_symlinks=follow_symlinks)
    except OSError:
        shutil.copy2(source, destination, follow_symlinks=follow_symlinks)
    return destination


def normalize_shell_scripts(
    task_dir: Path, *, include_skill_scripts: bool = False
) -> list[dict[str, Any]]:
    """Convert CRLF shell scripts in a task mirror using atomic replacement."""
    repaired: list[dict[str, Any]] = []
    if not task_dir.is_dir():
        return repaired
    for path in sorted(item for item in task_dir.rglob("*.sh") if item.is_file()):
        relative = path.relative_to(task_dir)
        parts = relative.parts
        if not include_skill_scripts:
            if len(parts) >= 2 and parts[:2] == ("environment", "skills"):
                continue
            if len(parts) >= 3 and parts[:3] == ("environment", "_deps", "skills"):
                continue
        payload = path.read_bytes()
        crlf_count = payload.count(b"\r\n")
        if crlf_count == 0:
            continue
        normalized = payload.replace(b"\r\n", b"\n")
        before_sha256 = sha256_bytes(payload)
        atomic_write(path, normalized)
        repaired.append(
            {
                "path": relative.as_posix(),
                "crlf_count": crlf_count,
                "before_sha256": before_sha256,
                "after_sha256": sha256_bytes(normalized),
            }
        )
    return repaired


def strip_skill_docker_lines(dockerfile: Path) -> None:
    if not dockerfile.is_file():
        return
    kept: list[str] = []
    for line in dockerfile.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.search(r"^\s*COPY\s+(_deps/)?skills\b", line, flags=re.IGNORECASE):
            continue
        if any(marker.lower() in line.lower() for marker in STATIC_SKILL_PATH_MARKERS):
            continue
        kept.append(line)
    atomic_text(dockerfile, "\n".join(kept).rstrip() + "\n")


def remove_skill_trees(task_dir: Path) -> None:
    for relative in (Path("environment/skills"), Path("environment/_deps/skills")):
        shutil.rmtree(task_dir / relative, ignore_errors=True)
    strip_skill_docker_lines(task_dir / "environment" / "Dockerfile")


def prepare_mirror(
    source_task: Path,
    destination: Path,
    condition: str,
    candidate_skills: Path | None,
    *,
    rebuild: bool,
    include_skill_shells: bool = True,
) -> list[dict[str, Any]]:
    require(source_task.is_dir(), f"source task missing: {source_task}")
    if rebuild:
        shutil.rmtree(destination, ignore_errors=True)
    if destination.exists():
        return normalize_shell_scripts(
            destination,
            include_skill_scripts=include_skill_shells,
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_task,
        destination,
        copy_function=hardlink_or_copy,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
    )
    strip_skill_docker_lines(destination / "environment" / "Dockerfile")
    if condition == "B":
        remove_skill_trees(destination)
    elif condition == "F":
        skills = destination / "environment" / "skills"
        require(skills.is_dir(), f"F skills missing after copy: {skills}")
    elif condition in SUPPORTED_CONDITIONS:
        require(
            candidate_skills is not None and candidate_skills.is_dir(),
            f"{condition} candidate missing: {candidate_skills}",
        )
        remove_skill_trees(destination)
        target = destination / "environment" / "skills"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(candidate_skills, target)
    else:
        raise RunnerError(f"unknown condition: {condition}")
    return normalize_shell_scripts(
        destination,
        include_skill_scripts=include_skill_shells,
    )


def source_skill_names(task_dir: Path) -> list[str]:
    skills_dir = task_dir / "environment" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(path.name for path in skills_dir.iterdir() if path.is_dir())


def audit_b_mirror(task_dir: Path) -> list[str]:
    markers: list[str] = []
    for relative in (Path("environment/skills"), Path("environment/_deps/skills")):
        if (task_dir / relative).exists():
            markers.append(relative.as_posix())
    dockerfile = task_dir / "environment" / "Dockerfile"
    if dockerfile.is_file():
        text = dockerfile.read_text(encoding="utf-8", errors="replace")
        for marker in STATIC_SKILL_PATH_MARKERS:
            if marker.lower() in text.lower():
                markers.append(f"Dockerfile:{marker}")
        if re.search(r"(?im)^\s*COPY\s+(_deps/)?skills\b", text):
            markers.append("Dockerfile:COPY-skills")
    return sorted(set(markers))


def mirror_fingerprint(task_dir: Path) -> dict[str, Any]:
    task_md = task_dir / "task.md"
    dockerfile = task_dir / "environment" / "Dockerfile"
    skills_dir = task_dir / "environment" / "skills"
    return {
        "task_md_sha256": sha256_file(task_md) if task_md.is_file() else None,
        "dockerfile_sha256": sha256_file(dockerfile) if dockerfile.is_file() else None,
        "skills_tree_sha256": sha256_tree(skills_dir),
        "task_tree_sha256": sha256_tree(task_dir),
    }


def validate_current_mirror_fingerprints(
    run_root: Path, manifest: dict[str, Any], jobs: Sequence[Job]
) -> None:
    expected = manifest.get("mirror_fingerprints") or {}
    unique = {
        (job.condition, job.task_id, Path(job.mirror_task_dir).resolve()) for job in jobs
    }
    for condition, task_id, task_dir in unique:
        expected_row = (expected.get(condition) or {}).get(task_id)
        require(isinstance(expected_row, dict), f"missing mirror fingerprint: {condition}/{task_id}")
        require(
            mirror_fingerprint(task_dir) == expected_row,
            f"mirror fingerprint changed: {condition}/{task_id}",
        )


def validate_platform_repairs_binding(run_root: Path, manifest: dict[str, Any]) -> str:
    path_value = manifest.get("platform_repairs_path")
    expected = manifest.get("platform_repairs_sha256")
    require(isinstance(path_value, str) and path_value, "platform repair ledger path missing")
    path = Path(path_value)
    if not path.is_absolute():
        path = run_root / path
    require(path.resolve() == (run_root / "platform_repairs.json").resolve(), "platform repair ledger path changed")
    require(path.is_file(), f"platform repair ledger missing: {path}")
    actual = sha256_file(path)
    require(expected == actual, "platform repair ledger hash changed")
    return actual


def validate_compat_binding(manifest: dict[str, Any]) -> None:
    expected_path = benchflow_compat_entrypoint().resolve()
    recorded_path = manifest.get("benchflow_compat_entrypoint")
    require(isinstance(recorded_path, str) and recorded_path, "compat entrypoint path missing")
    require(Path(recorded_path).resolve() == expected_path, "compat entrypoint path changed")
    require(
        manifest.get("benchflow_compat_sha256") == sha256_file(expected_path),
        "compat entrypoint hash changed; record the change with repair-windows-shells",
    )


def repair_windows_shells(args: argparse.Namespace) -> int:
    run_root = run_root_for(args, create=False)
    manifest, jobs = read_prepared(run_root, allow_compat_drift=True)
    work_root = (run_root / "work").resolve()
    mirrors = sorted(
        {
            (job.condition, job.task_id, Path(job.mirror_task_dir).resolve())
            for job in jobs
            if (not args.condition or job.condition in set(args.condition))
            and (not args.task or job.task_id in set(args.task))
        },
        key=lambda item: (item[0], item[1]),
    )
    require(mirrors, "repair selection produced no mirrors")
    selected_pairs = {(condition, task_id) for condition, task_id, _ in mirrors}
    jobs_by_execution = {job.execution_id: job for job in jobs}
    active_selected = sorted(
        execution_id
        for execution_id in orphan_start_events(run_root)
        if execution_id in jobs_by_execution
        and (jobs_by_execution[execution_id].condition, jobs_by_execution[execution_id].task_id)
        in selected_pairs
    )
    require(
        not active_selected,
        f"cannot repair mirrors with active executions: {active_selected}",
    )
    repairs: list[dict[str, Any]] = []
    fingerprints: dict[str, dict[str, Any]] = defaultdict(dict)
    for condition, task_id, task_dir in mirrors:
        require(
            task_dir.is_relative_to(work_root),
            f"mirror outside run work root: {task_dir}",
        )
        require(task_dir.is_dir(), f"mirror task missing: {task_dir}")
        for repair in normalize_shell_scripts(
            task_dir,
            include_skill_scripts=args.include_skill_shells,
        ):
            repairs.append(
                {
                    "condition": condition,
                    "task_id": task_id,
                    **repair,
                }
            )
        fingerprints[condition][task_id] = mirror_fingerprint(task_dir)

    report_path = run_root / "platform_repairs.json"
    compat_path = benchflow_compat_entrypoint()
    compat_before = manifest.get("benchflow_compat_sha256")
    compat_after = sha256_file(compat_path)
    event = {
        "created_at": utc_now(),
        "include_skill_shells": bool(args.include_skill_shells),
        "checked_mirrors": len(mirrors),
        "selected_conditions": sorted({condition for condition, _, _ in mirrors}),
        "selected_tasks": sorted({task_id for _, task_id, _ in mirrors}),
        "repaired_file_count": len(repairs),
        "repairs": repairs,
    }
    if compat_before != compat_after:
        event["benchflow_compat_change"] = {
            "before_sha256": compat_before,
            "after_sha256": compat_after,
        }
    events: list[dict[str, Any]] = []
    if report_path.is_file():
        previous = load_json(report_path)
        if previous.get("schema_version") == "skillsbench-bfs-platform-repairs-v2":
            events = list(previous.get("events") or [])
        else:
            events = [
                {
                    "created_at": previous.get("created_at"),
                    "include_skill_shells": False,
                    "checked_mirrors": previous.get("checked_mirrors"),
                    "selected_conditions": sorted(
                        {str(row.get("condition")) for row in previous.get("repairs") or []}
                    ),
                    "selected_tasks": sorted(
                        {str(row.get("task_id")) for row in previous.get("repairs") or []}
                    ),
                    "repaired_file_count": previous.get("repaired_file_count", 0),
                    "repairs": previous.get("repairs") or [],
                }
            ]
    events.append(event)
    report = {
        "schema_version": "skillsbench-bfs-platform-repairs-v2",
        "created_at": events[0]["created_at"],
        "scope": "prepared task mirrors; each event records whether skill trees were included",
        "event_count": len(events),
        "repaired_file_count": sum(int(item.get("repaired_file_count", 0)) for item in events),
        "events": events,
    }
    atomic_json(report_path, report)
    merged_fingerprints = dict(manifest.get("mirror_fingerprints") or {})
    for condition, rows in fingerprints.items():
        merged_fingerprints.setdefault(condition, {}).update(rows)
    manifest["mirror_fingerprints"] = {
        condition: dict(sorted(rows.items()))
        for condition, rows in sorted(merged_fingerprints.items())
    }
    manifest["platform_repairs_path"] = str(report_path)
    manifest["platform_repairs_sha256"] = sha256_file(report_path)
    manifest["benchflow_compat_entrypoint"] = str(compat_path)
    manifest["benchflow_compat_sha256"] = compat_after
    atomic_json(run_root / "manifest.json", manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def run_root_for(args: argparse.Namespace, *, create: bool) -> Path:
    if args.run_root:
        root = args.run_root.resolve()
    else:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_id = args.run_id or f"skillsbench-bfs-sol-{stamp}"
        root = (default_runs_root() / run_id).resolve()
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def prepare(args: argparse.Namespace) -> tuple[Path, dict[str, Any], list[Job]]:
    materials_root = args.materials_root.resolve()
    protocol, protocol_path = load_protocol(materials_root)
    skillsbench_root = protocol_skillsbench_root(protocol, args.skillsbench_root)
    conditions = protocol_conditions(protocol)
    candidate_pools = protocol_candidate_pools(protocol, materials_root)
    require(skillsbench_root.is_dir(), f"SkillsBench root missing: {skillsbench_root}")
    for condition, candidate_pool in candidate_pools.items():
        require(candidate_pool.is_dir(), f"{condition} candidate pool missing: {candidate_pool}")
    expected_commit = str(protocol["skillsbench"]["commit"])
    actual_commit = git_head(skillsbench_root)
    require(
        args.allow_checkout_mismatch or actual_commit == expected_commit,
        f"SkillsBench commit mismatch: expected {expected_commit}, got {actual_commit}",
    )

    run_root = run_root_for(args, create=True)
    jobs = build_schedule(protocol, run_root, skillsbench_root)
    tasks = sorted({job.task_id for job in jobs})
    prepare_repairs: list[dict[str, Any]] = []
    for task_id in tasks:
        source = skillsbench_root / "tasks" / task_id
        for condition in conditions:
            candidate_pool = candidate_pools.get(condition)
            candidate = candidate_pool / task_id / "skills" if candidate_pool else None
            repairs = prepare_mirror(
                source,
                run_root / "work" / condition / task_id,
                condition,
                candidate,
                rebuild=args.rebuild_mirrors,
            )
            prepare_repairs.extend(
                {"condition": condition, "task_id": task_id, **repair}
                for repair in repairs
            )

    b_rows: list[dict[str, Any]] = []
    for task_id in tasks:
        markers = audit_b_mirror(run_root / "work" / "B" / task_id)
        b_rows.append(
            {
                "task_id": task_id,
                "contaminated": bool(markers),
                "markers": markers,
            }
        )
    b_report = {
        "schema_version": "skillsbench-bfs-b-static-audit-v1",
        "created_at": utc_now(),
        "contaminated_count": sum(1 for row in b_rows if row["contaminated"]),
        "tasks": b_rows,
    }
    atomic_json(run_root / "b_contamination_static.json", b_report)
    require(b_report["contaminated_count"] == 0, "B mirror contamination detected")

    schedule_payload = {
        "schema_version": "skillsbench-bfs-schedule-v1",
        "selection_seed": protocol["selection_seed"],
        "balance_rule": "task-specific SHA-256 permutation rotated once per repetition",
        "jobs": [asdict(job) for job in jobs],
    }
    atomic_json(run_root / "schedule.json", schedule_payload)
    fingerprints = {
        condition: {
            task_id: mirror_fingerprint(run_root / "work" / condition / task_id)
            for task_id in tasks
        }
        for condition in conditions
    }
    repair_event = {
        "created_at": utc_now(),
        "include_skill_shells": True,
        "checked_mirrors": len(tasks) * len(conditions),
        "selected_conditions": list(conditions),
        "selected_tasks": tasks,
        "repaired_file_count": len(prepare_repairs),
        "repairs": prepare_repairs,
    }
    repair_report = {
        "schema_version": "skillsbench-bfs-platform-repairs-v2",
        "created_at": repair_event["created_at"],
        "scope": "prepared task mirrors; each event records whether skill trees were included",
        "event_count": 1,
        "repaired_file_count": len(prepare_repairs),
        "events": [repair_event],
    }
    repair_report_path = run_root / "platform_repairs.json"
    atomic_json(repair_report_path, repair_report)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "status": "prepared",
        "run_root": str(run_root),
        "materials_root": str(materials_root),
        "protocol_path": str(protocol_path),
        "protocol_sha256": sha256_file(protocol_path),
        "skillsbench_root": str(skillsbench_root),
        "skillsbench_commit_expected": expected_commit,
        "skillsbench_commit_actual": actual_commit,
        "candidate_pools": {
            condition: str(path) for condition, path in sorted(candidate_pools.items())
        },
        "agent": AGENT,
        "model": MODEL,
        "model_alias": MODEL_ALIAS,
        "backend": BACKEND,
        "conditions": list(conditions),
        "planned_jobs": len(jobs),
        "planned_by_phase": dict(Counter(job.phase for job in jobs)),
        "schedule_path": str(run_root / "schedule.json"),
        "schedule_sha256": sha256_file(run_root / "schedule.json"),
        "credential_env_names": {
            "api_key": args.api_key_env,
            "base_url": args.base_url_env,
        },
        "credential_values_recorded": False,
        "stdout_stderr_policy": "complete subprocess streams, redacted before persistence",
        "benchflow_compat_entrypoint": str(benchflow_compat_entrypoint()),
        "benchflow_compat_sha256": sha256_file(benchflow_compat_entrypoint()),
        "mirror_fingerprints": fingerprints,
        "platform_repairs_path": str(repair_report_path),
        "platform_repairs_sha256": sha256_file(repair_report_path),
    }
    atomic_json(run_root / "manifest.json", manifest)
    return run_root, manifest, jobs


def read_prepared(
    run_root: Path, *, allow_compat_drift: bool = False
) -> tuple[dict[str, Any], list[Job]]:
    manifest_path = run_root / "manifest.json"
    schedule_path = run_root / "schedule.json"
    require(manifest_path.is_file(), f"prepared manifest missing: {manifest_path}")
    require(schedule_path.is_file(), f"prepared schedule missing: {schedule_path}")
    manifest = load_json(manifest_path)
    require(manifest.get("schema_version") == SCHEMA_VERSION, "manifest schema changed")
    require(manifest.get("schedule_sha256") == sha256_file(schedule_path), "schedule hash changed")
    schedule = load_json(schedule_path)
    jobs = [Job(**item) for item in schedule["jobs"]]
    require(len(jobs) == int(manifest["planned_jobs"]), "scheduled job count changed")
    validate_platform_repairs_binding(run_root, manifest)
    validate_current_mirror_fingerprints(run_root, manifest, jobs)
    if not allow_compat_drift:
        validate_compat_binding(manifest)
    return manifest, jobs


def resolve_benchflow_python(args: argparse.Namespace, materials_root: Path) -> str:
    if args.benchflow_python:
        candidate = Path(args.benchflow_python)
        if candidate.is_file():
            return str(candidate.resolve())
        located = shutil.which(args.benchflow_python)
        return located or args.benchflow_python
    fallback = materials_root.parent / "skillsbench_venv" / "Scripts" / "python.exe"
    return str(fallback.resolve()) if fallback.is_file() else sys.executable


def benchflow_compat_entrypoint() -> Path:
    path = Path(__file__).resolve().with_name("benchflow_windows_compat.py")
    require(path.is_file(), f"BenchFlow compatibility entrypoint missing: {path}")
    return path


def command_for(
    job: Job,
    args: argparse.Namespace,
    materials_root: Path,
    *,
    jobs_dir: Path | None = None,
) -> list[str]:
    task_dir = Path(job.mirror_task_dir)
    selected_jobs_dir = jobs_dir or Path(job.jobs_dir)
    command = [
        resolve_benchflow_python(args, materials_root),
        str(benchflow_compat_entrypoint()),
        "eval",
        "run",
        "--tasks-dir",
        str(task_dir),
        "--agent",
        AGENT,
        "--model",
        MODEL,
        "--sandbox",
        BACKEND,
        "--jobs-dir",
        str(selected_jobs_dir),
        "--concurrency",
        "1",
        "--skill-mode",
        "no-skill" if job.condition == "B" else "with-skill",
    ]
    if job.condition != "B":
        require(job.skills_dir is not None, f"skills dir missing from {job.execution_id}")
        command.extend(["--skills-dir", job.skills_dir])
    return command


def build_run_env(args: argparse.Namespace) -> tuple[dict[str, str], Redactor]:
    api_key = os.environ.get(args.api_key_env, "")
    base_url = os.environ.get(args.base_url_env, "")
    require(bool(api_key), f"missing credential environment variable: {args.api_key_env}")
    require(bool(base_url), f"missing base URL environment variable: {args.base_url_env}")
    run_env = os.environ.copy()
    run_env["OPENAI_API_KEY"] = api_key
    run_env["OPENAI_BASE_URL"] = base_url.rstrip("/")
    run_env["PYTHONUTF8"] = "1"
    run_env["PYTHONIOENCODING"] = "utf-8"
    return run_env, Redactor(run_env)


def latest_path(root: Path, patterns: Iterable[str]) -> Path | None:
    matches: list[Path] = []
    if root.is_dir():
        for pattern in patterns:
            matches.extend(path for path in root.glob(pattern) if path.is_file())
    return max(matches, key=lambda path: path.stat().st_mtime_ns) if matches else None


def latest_result_json(jobs_dir: Path) -> Path | None:
    return latest_path(jobs_dir, ("**/result.json",))


def latest_reward_file(jobs_dir: Path) -> Path | None:
    return latest_path(jobs_dir, ("**/verifier/reward.txt", "**/reward.txt"))


def latest_trajectory(jobs_dir: Path) -> Path | None:
    return latest_path(jobs_dir, TRAJECTORY_PATTERNS)


def parse_json_object(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"error": f"invalid result JSON: {type(exc).__name__}: {exc}"}
    return value if isinstance(value, dict) else {"error": "result JSON is not an object"}


def parse_reward(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, dict):
        return None
    for key in ("reward", "score"):
        reward = value.get(key)
        if isinstance(reward, (int, float)) and not isinstance(reward, bool):
            return float(reward)
    rewards = value.get("rewards")
    if isinstance(rewards, (int, float)) and not isinstance(rewards, bool):
        return float(rewards)
    if isinstance(rewards, dict):
        reward = rewards.get("reward")
        if isinstance(reward, (int, float)) and not isinstance(reward, bool):
            return float(reward)
    for nested_key in ("verifier_result", "result"):
        nested = parse_reward(value.get(nested_key))
        if nested is not None:
            return nested
    stats = value.get("stats")
    if isinstance(stats, dict):
        evals = stats.get("evals")
        if isinstance(evals, dict):
            for eval_result in evals.values():
                if not isinstance(eval_result, dict):
                    continue
                metrics = eval_result.get("metrics")
                if isinstance(metrics, list):
                    for metric in metrics:
                        if isinstance(metric, dict):
                            mean = metric.get("mean")
                            if isinstance(mean, (int, float)) and not isinstance(mean, bool):
                                return float(mean)
                nested = parse_reward(eval_result.get("reward_stats"))
                if nested is not None:
                    return nested
    for key in ("mean", "value"):
        reward = value.get(key)
        if isinstance(reward, (int, float)) and not isinstance(reward, bool):
            return float(reward)
    return None


def reward_from_file(path: Path | None) -> float | None:
    if path is None:
        return None
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def result_text(result: dict[str, Any], key: str) -> str | None:
    value = result.get(key)
    return value if isinstance(value, str) and value.strip() else None


def result_error_blob(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("error", "verifier_error"):
        value = result.get(key)
        if isinstance(value, str):
            parts.append(value)
    exception = result.get("exception_info")
    if isinstance(exception, dict):
        for key in ("exception_type", "exception_message", "exception_traceback"):
            value = exception.get(key)
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts)


def infra_markers(*texts: str) -> list[str]:
    combined = "\n".join(texts)
    return sorted(marker for marker in INFRA_ERROR_PATTERNS if marker.lower() in combined.lower())


def runtime_b_contamination(jobs_dir: Path, skill_names: Sequence[str]) -> list[str]:
    markers: set[str] = set()
    files: set[Path] = set()
    for pattern in TRAJECTORY_PATTERNS:
        files.update(path for path in jobs_dir.glob(pattern) if path.is_file())
    skill_patterns = [
        (
            name,
            re.compile(
                rf"(?:skills?[/\\:\s]|<skill[^>]*name=[\"']){re.escape(name)}\b",
                re.IGNORECASE,
            ),
        )
        for name in skill_names
    ]
    for path in sorted(files):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for label, pattern in RUNTIME_CONTAMINATION_PATTERNS:
            if pattern.search(text):
                markers.add(f"{path.name}:{label}")
        for name, pattern in skill_patterns:
            if pattern.search(text):
                markers.add(f"{path.name}:task-skill:{name}")
    return sorted(markers)


def state_events(run_root: Path) -> list[dict[str, Any]]:
    path = run_root / "run_state.jsonl"
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RunnerError(f"invalid run_state.jsonl line {line_number}: {exc}") from exc
        require(isinstance(value, dict), f"state line {line_number} is not an object")
        events.append(value)
    return events


def latest_events(run_root: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in state_events(run_root):
        execution_id = event.get("execution_id")
        if isinstance(execution_id, str):
            latest[execution_id] = event
    return latest


def latest_finish_events(run_root: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in state_events(run_root):
        execution_id = event.get("execution_id")
        if isinstance(execution_id, str) and event.get("event") == "finish":
            latest[execution_id] = event
    return latest


def orphan_start_events(run_root: Path) -> dict[str, dict[str, Any]]:
    return {
        execution_id: event
        for execution_id, event in latest_events(run_root).items()
        if event.get("event") == "start"
    }


def terminal_execution_ids(run_root: Path) -> set[str]:
    return {
        execution_id
        for execution_id, event in latest_finish_events(run_root).items()
        if event.get("status") in {"scored", "invalid"}
    }


async def terminate_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    if os.name == "nt" and process.pid:
        await asyncio.create_subprocess_exec(
            "taskkill",
            "/PID",
            str(process.pid),
            "/T",
            "/F",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    else:
        process.kill()
    try:
        await asyncio.wait_for(process.wait(), timeout=30)
    except asyncio.TimeoutError:
        process.kill()


async def run_one(
    job: Job,
    args: argparse.Namespace,
    run_root: Path,
    skillsbench_root: Path,
    materials_root: Path,
    run_env: dict[str, str],
    redactor: Redactor,
    state_lock: asyncio.Lock,
) -> RunRecord:
    prior_attempt_numbers = [
        int(event["attempt_number"])
        for event in state_events(run_root)
        if event.get("execution_id") == job.execution_id
        and isinstance(event.get("attempt_number"), int)
    ]
    attempt_number = max(prior_attempt_numbers, default=0) + 1
    jobs_dir = Path(job.jobs_dir) / f"attempt_{attempt_number:02d}"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    log_dir = run_root / "logs" / job.phase / f"r{job.repetition}" / job.condition
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{job.task_id}.a{attempt_number:02d}.stdout.log"
    stderr_path = log_dir / f"{job.task_id}.a{attempt_number:02d}.stderr.log"
    command = command_for(job, args, materials_root, jobs_dir=jobs_dir)
    source_names = source_skill_names(Path(job.source_task_dir))
    manifest = load_json(run_root / "manifest.json")
    platform_repairs_sha256 = validate_platform_repairs_binding(run_root, manifest)
    expected_fingerprint = (manifest.get("mirror_fingerprints") or {}).get(job.condition, {}).get(
        job.task_id
    )
    require(isinstance(expected_fingerprint, dict), f"missing mirror fingerprint: {job.condition}/{job.task_id}")
    mirror_before = mirror_fingerprint(Path(job.mirror_task_dir))
    require(
        mirror_before == expected_fingerprint,
        f"mirror fingerprint changed before launch: {job.condition}/{job.task_id}",
    )
    start_event = {
        "schema_version": SCHEMA_VERSION,
        "event": "start",
        "timestamp": utc_now(),
        "execution_id": job.execution_id,
        "block_id": job.block_id,
        "task_id": job.task_id,
        "condition": job.condition,
        "phase": job.phase,
        "repetition": job.repetition,
        "condition_position": job.condition_position,
        "status": "running",
        "attempt_number": attempt_number,
        "invalid": None,
        "official_reward": None,
        "mirror_fingerprint": mirror_before,
        "platform_repairs_sha256": platform_repairs_sha256,
        "command": command,
        "credential_values_recorded": False,
    }
    async with state_lock:
        append_jsonl(run_root / "run_state.jsonl", start_event)
        print(
            f"[start] {job.phase}/r{job.repetition} {job.task_id} {job.condition} "
            f"position={job.condition_position}",
            flush=True,
        )

    started = time.monotonic()
    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    timed_out = False
    process: asyncio.subprocess.Process | None = None
    launch_error: str | None = None
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=skillsbench_root,
            env=run_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=creation_flags,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=args.process_timeout_seconds
            )
        except asyncio.TimeoutError:
            timed_out = True
            await terminate_process(process)
            stdout_bytes = b""
            stderr_bytes = f"runner timeout after {args.process_timeout_seconds}s".encode()
    except OSError as exc:
        launch_error = f"{type(exc).__name__}: {exc}"
        stdout_bytes = b""
        stderr_bytes = launch_error.encode("utf-8", errors="replace")
    duration = round(time.monotonic() - started, 3)
    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")
    stream_reflection = redactor.contains_secret(stdout) or redactor.contains_secret(stderr)
    atomic_text(stdout_path, redactor.text(stdout))
    atomic_text(stderr_path, redactor.text(stderr))
    _, tree_reflection = redact_text_tree(jobs_dir, redactor)
    credential_reflection = stream_reflection or tree_reflection

    result_path = latest_result_json(jobs_dir)
    reward_path = latest_reward_file(jobs_dir)
    trajectory_path = latest_trajectory(jobs_dir)
    result = parse_json_object(result_path)
    reward = parse_reward(result)
    if reward is None:
        reward = reward_from_file(reward_path)
    error = result_text(result, "error")
    verifier_error = result_text(result, "verifier_error")
    infra = infra_markers(stdout, stderr, result_error_blob(result))
    b_markers = runtime_b_contamination(jobs_dir, source_names) if job.condition == "B" else []
    invalid_reasons: list[str] = []
    return_code = process.returncode if process is not None and process.returncode is not None else -1
    if launch_error:
        invalid_reasons.append("subprocess_launch_error")
    if timed_out:
        invalid_reasons.append("runner_process_timeout")
    if return_code != 0:
        invalid_reasons.append("nonzero_return_code")
    if result_path is None:
        invalid_reasons.append("missing_result_json")
    if reward is None:
        invalid_reasons.append("missing_official_reward")
    elif not 0.0 <= reward <= 1.0:
        invalid_reasons.append("official_reward_out_of_range")
    if error:
        invalid_reasons.append("benchflow_error")
    if verifier_error:
        invalid_reasons.append("verifier_error")
    if b_markers:
        invalid_reasons.append("b_skill_contamination")
    if credential_reflection:
        invalid_reasons.append("credential_reflection_redacted")
    invalid_reasons = sorted(set(invalid_reasons))
    mirror_after = mirror_fingerprint(Path(job.mirror_task_dir))
    if mirror_after != mirror_before:
        invalid_reasons.append("mirror_changed_during_execution")
    current_manifest = load_json(run_root / "manifest.json")
    current_repairs_sha256 = validate_platform_repairs_binding(run_root, current_manifest)
    if current_repairs_sha256 != platform_repairs_sha256:
        invalid_reasons.append("platform_repairs_changed_during_execution")
    invalid_reasons = sorted(set(invalid_reasons))
    invalid = bool(invalid_reasons)
    status = "invalid" if invalid else "scored"
    record = RunRecord(
        schema_version=SCHEMA_VERSION,
        event="finish",
        timestamp=utc_now(),
        execution_id=job.execution_id,
        block_id=job.block_id,
        task_id=job.task_id,
        condition=job.condition,
        phase=job.phase,
        repetition=job.repetition,
        condition_position=job.condition_position,
        attempt_number=attempt_number,
        status=status,
        invalid=invalid,
        invalid_reasons=invalid_reasons,
        official_reward=reward,
        success=(reward == 1.0) if reward is not None and not invalid else None,
        return_code=return_code,
        duration_sec=duration,
        result_path=relative_or_absolute(run_root, result_path),
        official_result_path=relative_or_absolute(run_root, result_path),
        official_reward_path=relative_or_absolute(run_root, reward_path),
        trajectory_path=relative_or_absolute(run_root, trajectory_path),
        jobs_dir=relative_or_absolute(run_root, jobs_dir) or str(jobs_dir),
        stdout_path=relative_or_absolute(run_root, stdout_path) or str(stdout_path),
        stderr_path=relative_or_absolute(run_root, stderr_path) or str(stderr_path),
        error=redactor.text(error) if error else None,
        verifier_error=redactor.text(verifier_error) if verifier_error else None,
        infra_error=bool(infra) and invalid,
        infra_error_markers=infra,
        b_contaminated=bool(b_markers),
        b_contamination_markers=b_markers,
        credential_reflection_detected=credential_reflection,
        mirror_fingerprint_before=mirror_before,
        mirror_fingerprint_after=mirror_after,
        platform_repairs_sha256=platform_repairs_sha256,
        command=command,
        credential_values_recorded=False,
    )
    async with state_lock:
        append_jsonl(run_root / "run_state.jsonl", redactor.value(asdict(record)))
        print(
            f"[{status}] {job.phase}/r{job.repetition} {job.task_id} {job.condition} "
            f"reward={reward} invalid={invalid_reasons}",
            flush=True,
        )
    return record


async def run_selected(
    jobs: list[Job],
    args: argparse.Namespace,
    run_root: Path,
    skillsbench_root: Path,
    materials_root: Path,
    run_env: dict[str, str],
    redactor: Redactor,
) -> list[RunRecord]:
    finished = terminal_execution_ids(run_root)
    if args.rerun:
        pending = list(jobs)
    elif args.rerun_invalid:
        invalid = {
            execution_id
            for execution_id, event in latest_finish_events(run_root).items()
            if event.get("status") == "invalid"
        }
        pending = [job for job in jobs if job.execution_id in invalid]
    else:
        pending = [job for job in jobs if job.execution_id not in finished]
    atomic_json(run_root / "selected_jobs.json", [asdict(job) for job in pending])
    if not pending:
        print("[skip] no matching jobs selected", flush=True)
    semaphore = asyncio.Semaphore(args.concurrency)
    state_lock = asyncio.Lock()
    grouped: dict[str, list[Job]] = defaultdict(list)
    for job in pending:
        grouped[job.block_id].append(job)

    async def run_block(block_jobs: list[Job]) -> list[RunRecord]:
        rows: list[RunRecord] = []
        for job in sorted(block_jobs, key=lambda item: item.condition_position):
            async with semaphore:
                rows.append(
                    await run_one(
                        job,
                        args,
                        run_root,
                        skillsbench_root,
                        materials_root,
                        run_env,
                        redactor,
                        state_lock,
                    )
                )
        return rows

    blocks = sorted(
        grouped.values(),
        key=lambda rows: (rows[0].phase, rows[0].repetition, rows[0].task_position),
    )
    nested = await asyncio.gather(*(run_block(block) for block in blocks))
    return [record for block in nested for record in block]


def finish_rows(run_root: Path) -> list[dict[str, Any]]:
    return list(latest_finish_events(run_root).values())


def recorded_artifact_path(run_root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = run_root / path
    resolved = path.resolve()
    try:
        resolved.relative_to(run_root.resolve())
    except ValueError:
        return None
    return resolved if resolved.is_file() else None


def numeric_unit_reward(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    reward = float(value)
    return reward if math.isfinite(reward) and 0.0 <= reward <= 1.0 else None


def finish_validation_reasons(
    run_root: Path, row: dict[str, Any], job: Job
) -> list[str]:
    reasons: list[str] = []
    for field, expected in (
        ("execution_id", job.execution_id),
        ("task_id", job.task_id),
        ("condition", job.condition),
        ("phase", job.phase),
        ("repetition", job.repetition),
    ):
        if row.get(field) != expected:
            reasons.append(f"{field}_mismatch")
    if row.get("event") != "finish":
        reasons.append("not_finish_event")
    if row.get("status") != "scored":
        reasons.append("non_scored_status")
    if row.get("invalid") is not False:
        reasons.append("invalid_flag_not_false")
    if row.get("invalid_reasons"):
        reasons.append("invalid_reasons_present")
    if row.get("return_code") != 0:
        reasons.append("nonzero_or_missing_return_code")
    if row.get("infra_error") is not False:
        reasons.append("infra_error_not_cleared")
    if row.get("error") or row.get("verifier_error"):
        reasons.append("runner_or_verifier_error_present")
    if row.get("b_contaminated") is not False:
        reasons.append("b_contamination_not_cleared")
    if row.get("b_contamination_markers"):
        reasons.append("b_contamination_markers_present")
    if row.get("credential_reflection_detected") is not False:
        reasons.append("credential_reflection_not_cleared")
    if row.get("credential_values_recorded") is not False:
        reasons.append("credential_recording_not_cleared")

    reward = numeric_unit_reward(row.get("official_reward"))
    if reward is None:
        reasons.append("invalid_official_reward")

    result_path = recorded_artifact_path(run_root, row.get("official_result_path"))
    result_reward: float | None = None
    if result_path is None or result_path.name != "result.json":
        reasons.append("missing_official_result_provenance")
    else:
        result_reward = numeric_unit_reward(parse_reward(parse_json_object(result_path)))

    reward_path_value = row.get("official_reward_path")
    reward_path = recorded_artifact_path(run_root, reward_path_value)
    file_reward = numeric_unit_reward(reward_from_file(reward_path)) if reward_path else None
    if reward_path_value and reward_path is None:
        reasons.append("invalid_official_reward_path")
    elif reward_path_value and file_reward is None:
        reasons.append("invalid_official_reward_file")

    proven_rewards = [value for value in (result_reward, file_reward) if value is not None]
    if not proven_rewards:
        reasons.append("missing_official_reward_provenance")
    elif reward is not None and any(
        not math.isclose(reward, proven, rel_tol=0.0, abs_tol=1e-12)
        for proven in proven_rewards
    ):
        reasons.append("official_reward_provenance_mismatch")
    return sorted(set(reasons))


def static_b_audit(
    run_root: Path, all_jobs: Sequence[Job], phase: str | None = None
) -> dict[str, Any]:
    task_ids = sorted(
        {
            job.task_id
            for job in all_jobs
            if job.condition == "B" and (phase is None or job.phase == phase)
        }
    )
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        mirror = run_root / "work" / "B" / task_id
        markers = ["missing-task-mirror"] if not mirror.is_dir() else audit_b_mirror(mirror)
        rows.append(
            {
                "task_id": task_id,
                "contaminated": bool(markers),
                "markers": markers,
            }
        )
    contaminated_count = sum(1 for row in rows if row["contaminated"])
    return {
        "phase": phase or "all",
        "status": "passed" if contaminated_count == 0 else "failed",
        "contaminated_count": contaminated_count,
        "tasks": rows,
    }


def protocol_invalid_reasons(run_root: Path) -> list[str]:
    path = run_root / "protocol_status.json"
    if not path.is_file():
        return []
    payload = load_json(path)
    reasons = payload.get("reasons")
    return sorted(str(reason) for reason in reasons) if isinstance(reasons, list) else []


def mark_protocol_invalid(run_root: Path, reason: str) -> dict[str, Any]:
    reasons = sorted(set([*protocol_invalid_reasons(run_root), reason]))
    report = {
        "schema_version": "skillsbench-bfs-protocol-status-v1",
        "updated_at": utc_now(),
        "status": "protocol-invalid",
        "final_reportable": False,
        "reasons": reasons,
    }
    atomic_json(run_root / "protocol_status.json", report)
    return report


def phase_gate(run_root: Path, all_jobs: Sequence[Job], phase: str) -> dict[str, Any]:
    expected_jobs = {job.execution_id: job for job in all_jobs if job.phase == phase}
    finishes = latest_finish_events(run_root)
    rows = {
        execution_id: finishes[execution_id]
        for execution_id in expected_jobs
        if execution_id in finishes
    }
    missing = sorted(set(expected_jobs) - set(rows))
    unexpected = sorted(
        execution_id
        for execution_id, row in finishes.items()
        if row.get("phase") == phase and execution_id not in expected_jobs
    )
    invalid_details = {
        execution_id: reasons
        for execution_id, row in rows.items()
        if (reasons := finish_validation_reasons(run_root, row, expected_jobs[execution_id]))
    }
    contaminated = sorted(
        execution_id for execution_id, row in rows.items() if row.get("b_contaminated") is not False
    )
    credential_reflections = sorted(
        execution_id
        for execution_id, row in rows.items()
        if row.get("credential_reflection_detected") is not False
    )
    static_audit = static_b_audit(run_root, all_jobs, phase)
    manifest_path = run_root / "manifest.json"
    if manifest_path.is_file():
        manifest = load_json(manifest_path)
        required_rows = int((manifest.get("planned_by_phase") or {}).get(phase, 0))
    else:
        required_rows = FROZEN_EXPECTED_ROWS[phase]
    schedule_count_valid = len(expected_jobs) == required_rows
    protocol_reasons = protocol_invalid_reasons(run_root) if phase == "main" else []
    passed = (
        schedule_count_valid
        and not missing
        and not unexpected
        and not invalid_details
        and static_audit["status"] == "passed"
        and not protocol_reasons
    )
    valid_b_rows = [
        row
        for execution_id, row in rows.items()
        if row.get("condition") == "B" and execution_id not in invalid_details
    ]
    b_pass_rate = (
        sum(1 for row in valid_b_rows if row.get("official_reward") == 1.0)
        / len(valid_b_rows)
        if valid_b_rows
        else None
    )
    status = "passed" if passed else "protocol-invalid" if protocol_reasons else "blocked"
    report = {
        "schema_version": f"skillsbench-bfs-{phase}-gate-v2",
        "created_at": utc_now(),
        "phase": phase,
        "status": status,
        "final_reportable": phase == "main" and passed,
        "expected_rows": len(expected_jobs),
        "required_frozen_rows": required_rows,
        "schedule_count_valid": schedule_count_valid,
        "terminal_rows": len(rows),
        "missing_execution_ids": missing,
        "unexpected_execution_ids": unexpected,
        "invalid_execution_ids": sorted(invalid_details),
        "invalid_details": invalid_details,
        "contaminated_execution_ids": contaminated,
        "credential_reflection_execution_ids": credential_reflections,
        "orphan_start_execution_ids": sorted(orphan_start_events(run_root)),
        "static_b_audit": static_audit,
        "protocol_invalid_reasons": protocol_reasons,
        "b_pass_rate": b_pass_rate,
        "baseline_ceiling_warning": b_pass_rate is not None and b_pass_rate >= 0.8,
    }
    atomic_json(run_root / f"{phase}_gate.json", report)
    return report


def pilot_gate(run_root: Path, all_jobs: Sequence[Job]) -> dict[str, Any]:
    return phase_gate(run_root, all_jobs, "pilot")


def main_gate(run_root: Path, all_jobs: Sequence[Job]) -> dict[str, Any]:
    return phase_gate(run_root, all_jobs, "main")


def enforce_main_prerequisites(
    run_root: Path, all_jobs: Sequence[Job], *, allow_without_pilot: bool
) -> dict[str, Any]:
    current_pilot_gate = pilot_gate(run_root, all_jobs)
    current_main_static_audit = static_b_audit(run_root, all_jobs, "main")
    if allow_without_pilot:
        mark_protocol_invalid(run_root, "allow_main_without_pilot_used")
    else:
        require(
            current_pilot_gate.get("status") == "passed",
            "main run blocked by current pilot gate",
        )
    require(
        current_main_static_audit.get("status") == "passed",
        "main run blocked by static B mirror audit",
    )
    return {
        "pilot_gate": current_pilot_gate,
        "main_static_b_audit": current_main_static_audit,
        "allow_main_without_pilot": allow_without_pilot,
        "protocol_invalid": bool(protocol_invalid_reasons(run_root)),
    }


def run_experiment(args: argparse.Namespace) -> int:
    run_root = run_root_for(args, create=True)
    args.run_root = run_root
    if not (run_root / "manifest.json").is_file():
        prepare(args)
    manifest, all_jobs = read_prepared(run_root)
    compat_entrypoint = benchflow_compat_entrypoint()
    manifest["benchflow_compat_entrypoint"] = str(compat_entrypoint)
    manifest["benchflow_compat_sha256"] = sha256_file(compat_entrypoint)
    atomic_json(run_root / "manifest.json", manifest)
    materials_root = Path(manifest["materials_root"])
    skillsbench_root = Path(manifest["skillsbench_root"])
    selected = selected_jobs(all_jobs, args)
    run_env, redactor = build_run_env(args)

    benchflow_python = resolve_benchflow_python(args, materials_root)
    require(
        Path(benchflow_python).is_file() or shutil.which(benchflow_python) is not None,
        f"BenchFlow Python executable not found: {benchflow_python}",
    )
    require(shutil.which("docker") is not None, "docker executable not found")
    require(
        args.concurrency <= MAX_CONCURRENCY,
        f"concurrency exceeds hard ceiling {MAX_CONCURRENCY}",
    )

    selected_phases = [phase for phase in PHASES if any(job.phase == phase for job in selected)]
    all_records: list[RunRecord] = []
    for phase in selected_phases:
        if phase == "main":
            preflight = enforce_main_prerequisites(
                run_root,
                all_jobs,
                allow_without_pilot=args.allow_main_without_pilot,
            )
            atomic_json(run_root / "main_preflight.json", preflight)
        phase_jobs = [job for job in selected if job.phase == phase]
        records = asyncio.run(
            run_selected(
                phase_jobs,
                args,
                run_root,
                skillsbench_root,
                materials_root,
                run_env,
                redactor,
            )
        )
        all_records.extend(records)
        if phase == "pilot":
            gate = pilot_gate(run_root, all_jobs)
            if gate["status"] != "passed" and "main" in selected_phases:
                print("main run held: pilot gate did not pass", file=sys.stderr)
                break
        elif phase == "main":
            main_gate(run_root, all_jobs)

    atomic_json(run_root / "last_run_summary.json", [asdict(record) for record in all_records])
    if protocol_invalid_reasons(run_root):
        return 2
    if any(record.b_contaminated for record in all_records):
        return 2
    return 1 if any(record.invalid for record in all_records) else 0


def audit_run_root(run_root: Path, all_jobs: Sequence[Job]) -> dict[str, Any]:
    static_audit = static_b_audit(run_root, all_jobs)
    static_rows = static_audit["tasks"]
    runtime_rows = [
        {
            "execution_id": row["execution_id"],
            "task_id": row["task_id"],
            "phase": row["phase"],
            "repetition": row["repetition"],
            "contaminated": bool(row.get("b_contaminated")),
            "markers": row.get("b_contamination_markers") or [],
        }
        for row in finish_rows(run_root)
        if row.get("condition") == "B"
    ]
    report = {
        "schema_version": "skillsbench-bfs-b-audit-v1",
        "created_at": utc_now(),
        "static_contaminated_count": sum(1 for row in static_rows if row["contaminated"]),
        "runtime_contaminated_count": sum(1 for row in runtime_rows if row["contaminated"]),
        "static": static_rows,
        "runtime": runtime_rows,
    }
    report["status"] = (
        "passed"
        if report["static_contaminated_count"] == 0 and report["runtime_contaminated_count"] == 0
        else "failed"
    )
    atomic_json(run_root / "b_contamination_report.json", report)
    return report


def audit(args: argparse.Namespace) -> int:
    run_root = run_root_for(args, create=False)
    _, jobs = read_prepared(run_root)
    b_report = audit_run_root(run_root, jobs)
    current_pilot_gate = pilot_gate(run_root, jobs)
    current_main_gate = main_gate(run_root, jobs)
    final_reportable = (
        b_report["status"] == "passed"
        and current_pilot_gate["status"] == "passed"
        and current_main_gate["status"] == "passed"
    )
    report = {
        "schema_version": "skillsbench-bfs-full-audit-v1",
        "created_at": utc_now(),
        "status": "passed" if final_reportable else "failed",
        "final_reportable": final_reportable,
        "b_contamination": b_report,
        "pilot_gate": current_pilot_gate,
        "main_gate": current_main_gate,
        "protocol_invalid_reasons": protocol_invalid_reasons(run_root),
    }
    atomic_json(run_root / "audit_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 2


def status(args: argparse.Namespace) -> int:
    run_root = run_root_for(args, create=False)
    _, jobs = read_prepared(run_root)
    latest = latest_finish_events(run_root)
    orphan_starts = orphan_start_events(run_root)
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for job in jobs:
        event = latest.get(job.execution_id)
        state = str(event.get("status")) if event else "pending"
        counts[f"{job.phase}:{job.condition}"][state] += 1
    payload = {
        "schema_version": "skillsbench-bfs-status-v1",
        "run_root": str(run_root),
        "planned": len(jobs),
        "terminal": len(latest),
        "orphan_start_count": len(orphan_starts),
        "orphan_start_execution_ids": sorted(orphan_starts),
        "by_phase_condition": {key: dict(value) for key, value in sorted(counts.items())},
        "pilot_gate": (
            load_json(run_root / "pilot_gate.json")
            if (run_root / "pilot_gate.json").is_file()
            else None
        ),
        "main_gate": (
            load_json(run_root / "main_gate.json")
            if (run_root / "main_gate.json").is_file()
            else None
        ),
        "protocol_invalid_reasons": protocol_invalid_reasons(run_root),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def summarize(args: argparse.Namespace) -> int:
    run_root = run_root_for(args, create=False)
    _, jobs = read_prepared(run_root)
    rows = finish_rows(run_root)
    jobs_by_execution = {job.execution_id: job for job in jobs}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['phase']}:{row['condition']}"].append(row)
    by_group: dict[str, Any] = {}
    for key, items in sorted(grouped.items()):
        scored = [
            item
            for item in items
            if item.get("execution_id") in jobs_by_execution
            and not finish_validation_reasons(
                run_root,
                item,
                jobs_by_execution[item["execution_id"]],
            )
        ]
        by_group[key] = {
            "terminal": len(items),
            "scored": len(scored),
            "invalid": len(items) - len(scored),
            "successes": sum(1 for item in scored if item.get("official_reward") == 1.0),
            "mean_official_reward": (
                sum(float(item["official_reward"]) for item in scored) / len(scored)
                if scored
                else None
            ),
        }
    b_audit = audit_run_root(run_root, jobs)
    current_pilot_gate = pilot_gate(run_root, jobs)
    current_main_gate = main_gate(run_root, jobs)
    final_reportable = (
        b_audit["status"] == "passed"
        and current_pilot_gate["status"] == "passed"
        and current_main_gate["status"] == "passed"
    )
    report = {
        "schema_version": "skillsbench-bfs-summary-v1",
        "created_at": utc_now(),
        "run_root": str(run_root),
        "planned_rows": len(jobs),
        "terminal_rows": len(rows),
        "scored_rows": sum(item["scored"] for item in by_group.values()),
        "invalid_rows": sum(item["invalid"] for item in by_group.values()),
        "by_phase_condition": by_group,
        "b_contamination": b_audit,
        "pilot_gate": current_pilot_gate,
        "main_gate": current_main_gate,
        "protocol_invalid_reasons": protocol_invalid_reasons(run_root),
        "final_reportable": final_reportable,
        "credential_values_recorded": False,
    }
    atomic_json(run_root / "summary.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if final_reportable else 2


def plan(args: argparse.Namespace) -> int:
    materials_root = args.materials_root.resolve()
    protocol, _ = load_protocol(materials_root)
    skillsbench_root = protocol_skillsbench_root(protocol, args.skillsbench_root)
    run_root = run_root_for(args, create=False)
    jobs = build_schedule(protocol, run_root, skillsbench_root)
    selected = selected_jobs(jobs, args)
    blocks = len({job.block_id for job in selected})
    payload = {
        "schema_version": "skillsbench-bfs-plan-v1",
        "dry_run": True,
        "run_root": str(run_root),
        "materials_root": str(materials_root),
        "skillsbench_root": str(skillsbench_root),
        "agent": AGENT,
        "model": MODEL,
        "backend": BACKEND,
        "jobs": len(selected),
        "blocks": blocks,
        "by_phase": dict(Counter(job.phase for job in selected)),
        "by_condition": dict(Counter(job.condition for job in selected)),
        "credential_env_names": {
            "api_key": args.api_key_env,
            "base_url": args.base_url_env,
        },
        "credential_values_recorded": False,
        "schedule": [
            {
                "execution_id": job.execution_id,
                "block_id": job.block_id,
                "phase": job.phase,
                "repetition": job.repetition,
                "task_id": job.task_id,
                "condition": job.condition,
                "condition_position": job.condition_position,
                "command": command_for(job, args, materials_root),
            }
            for job in selected
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "command",
        choices=(
            "plan",
            "prepare",
            "repair-windows-shells",
            "run",
            "status",
            "audit",
            "summarize",
        ),
    )
    parser.add_argument("--materials-root", type=Path, default=default_materials_root())
    parser.add_argument("--skillsbench-root", type=Path)
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--phase", action="append", choices=PHASES)
    parser.add_argument("--repetition", action="append", type=int)
    parser.add_argument("--task", action="append")
    parser.add_argument("--condition", action="append", choices=SUPPORTED_CONDITIONS)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--process-timeout-seconds", type=int, default=DEFAULT_PROCESS_TIMEOUT_SECONDS)
    parser.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--base-url-env", default=DEFAULT_BASE_URL_ENV)
    parser.add_argument("--benchflow-python")
    parser.add_argument("--rebuild-mirrors", action="store_true")
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument(
        "--rerun-invalid",
        action="store_true",
        help="Rerun only selected cells whose latest terminal event is invalid.",
    )
    parser.add_argument("--allow-main-without-pilot", action="store_true")
    parser.add_argument("--allow-checkout-mismatch", action="store_true")
    parser.add_argument(
        "--include-skill-shells",
        action="store_true",
        help="Also normalize shell scripts inside environment skill trees.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    require(not (args.rerun and args.rerun_invalid), "--rerun and --rerun-invalid are mutually exclusive")
    require(1 <= args.concurrency <= MAX_CONCURRENCY, f"--concurrency must be in [1,{MAX_CONCURRENCY}]")
    require(args.process_timeout_seconds > 0, "--process-timeout-seconds must be positive")
    if args.command in {"repair-windows-shells", "status", "audit", "summarize"}:
        require(args.run_root is not None, f"{args.command} requires --run-root")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.command == "plan" or args.dry_run:
            return plan(args)
        if args.command == "prepare":
            run_root, manifest, _ = prepare(args)
            print(f"run_root={run_root}")
            print(f"planned_jobs={manifest['planned_jobs']}")
            return 0
        if args.command == "repair-windows-shells":
            return repair_windows_shells(args)
        if args.command == "run":
            return run_experiment(args)
        if args.command == "status":
            return status(args)
        if args.command == "audit":
            return audit(args)
        if args.command == "summarize":
            return summarize(args)
        raise AssertionError(args.command)
    except RunnerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
