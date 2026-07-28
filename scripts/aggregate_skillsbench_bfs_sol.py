#!/usr/bin/env python3
"""Aggregate SkillsBench B/F/S runs using the official task reward.

The frozen runner schema writes canonical terminal observations to
``run_state.jsonl``.  BenchFlow ``result.json`` files are accepted as a
compatibility fallback, but a runner ``finish`` event takes precedence.
Infrastructure-invalid observations never receive an imputed reward.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


CONDITIONS = ("B", "F", "S")
EFFECTS = (("F-B", "F", "B"), ("S-B", "S", "B"), ("S-F", "S", "F"))
DEFAULT_BOOTSTRAP_SAMPLES = 10_000
DEFAULT_BOOTSTRAP_SEED = 20_260_727
DEFAULT_B_WARNING_THRESHOLD = 0.80
DEFAULT_API_KEY_ENV = "PAPERTOSKILL_GPT_OPENAI_API_KEY"
DEFAULT_BASE_URL_ENV = "PAPERTOSKILL_GPT_OPENAI_BASE_URL"
ERROR_CATEGORY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
GENERIC_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(
        r"(?i)(\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\b\s*[:=]\s*)"
        r"([^\s,;\"']{6,})"
    ),
)
S_CANDIDATE_DESCRIPTION = (
    "an independently generated heuristic candidate inspired by SkillReducer; "
    "it is not the official SkillReducer implementation or artifact, and this is not "
    "an official head-to-head comparison"
)


@dataclass(frozen=True)
class ManifestSpec:
    path: str
    phase: str
    tasks: tuple[str, ...]
    conditions: tuple[str, ...]
    repetitions: int


@dataclass
class Observation:
    execution_id: str
    task_id: str
    condition: str
    phase: str
    repetition: int | None
    status: str
    valid: bool
    official_reward: float | None
    success: bool | None
    invalid_reasons: list[str]
    reward_source: str
    source_path: str
    official_result_path: str | None = None
    event_time: str | None = None

    def schedule_key(self) -> tuple[str, str, str, int | str]:
        repetition: int | str = self.repetition
        if repetition is None:
            repetition = f"execution:{self.execution_id}"
        return (self.phase, self.task_id, self.condition, repetition)

    def schedule_cell(self) -> tuple[str, str, str, int] | None:
        phase = "main" if self.phase in {"main", "main_assumed"} else self.phase
        if (
            phase not in {"pilot", "main"}
            or not self.task_id
            or self.condition not in CONDITIONS
            or self.repetition is None
        ):
            return None
        return (phase, self.task_id, self.condition, self.repetition)


class OutputRedactor:
    """Redact known credential values and common credential-shaped strings."""

    def __init__(self, api_key_env: str, base_url_env: str) -> None:
        values: list[tuple[str, str]] = []
        api_key = os.environ.get(api_key_env, "")
        base_url = os.environ.get(base_url_env, "")
        for value in {api_key, api_key.strip()}:
            if len(value) >= 6:
                values.append((value, "[REDACTED:API_KEY]"))
        for value in {base_url, base_url.rstrip("/"), base_url.strip()}:
            if len(value) >= 8:
                values.append((value, "[REDACTED:BASE_URL]"))
        self._values = sorted(set(values), key=lambda item: len(item[0]), reverse=True)

    def contains_secret(self, text: str) -> bool:
        if any(value in text for value, _ in self._values):
            return True
        return any(pattern.search(text) for pattern in GENERIC_SECRET_PATTERNS)

    def text(self, value: str) -> str:
        redacted = value
        for secret, replacement in self._values:
            redacted = redacted.replace(secret, replacement)
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
            return {self.text(str(key)): self.value(value) for key, value in payload.items()}
        return payload


def secure_summary(
    summary: dict[str, Any], api_key_env: str, base_url_env: str
) -> tuple[dict[str, Any], bool, OutputRedactor]:
    redactor = OutputRedactor(api_key_env, base_url_env)
    serialized = json.dumps(summary, ensure_ascii=False, sort_keys=True)
    reflected = redactor.contains_secret(serialized)
    safe = redactor.value(summary)
    if not isinstance(safe, dict):
        raise TypeError("sanitized summary must remain an object")
    safe["output_security"] = {
        "credential_reflection_detected": reflected,
        "credential_values_recorded": False,
        "error_detail_policy": "categories_only",
    }
    safe_serialized = json.dumps(safe, ensure_ascii=False, sort_keys=True)
    if redactor.contains_secret(safe_serialized):
        raise RuntimeError("credential_redaction_failed")
    return safe, reflected, redactor


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected an object at {path}:{line_number}")
        rows.append((line_number, payload))
    return rows


def nested(payload: dict[str, Any], dotted_path: str) -> Any:
    value: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def first_value(payload: dict[str, Any], paths: Iterable[str]) -> tuple[Any, str]:
    for path in paths:
        value = nested(payload, path)
        if value is not None:
            return value, path
    return None, ""


def category(value: Any, fallback: str) -> str:
    text = str(value or "").strip().lower()
    return text if ERROR_CATEGORY.fullmatch(text) else fallback


def exception_category(exc: BaseException) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return "json_decode_error"
    if isinstance(exc, OSError):
        return "os_error"
    if isinstance(exc, ValueError):
        return "value_error"
    return "parse_error"


def numeric_reward(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def task_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    parsed: list[str] = []
    for item in value:
        if isinstance(item, str):
            parsed.append(item)
        elif isinstance(item, dict):
            task_id, _ = first_value(item, ("task_id", "id", "name"))
            if task_id:
                parsed.append(str(task_id))
    return tuple(dict.fromkeys(parsed))


def resolve_schedule_path(manifest_path: Path, value: Any) -> Path | None:
    if value:
        candidate = Path(str(value))
        if not candidate.is_absolute():
            candidate = manifest_path.parent / candidate
        if candidate.is_file():
            return candidate
    local = manifest_path.parent / "schedule.json"
    return local if local.is_file() else None


def parse_manifest(path: Path) -> list[ManifestSpec]:
    payload = read_json(path)
    tasks = task_ids(payload.get("tasks"))
    if tasks:
        phase = str(payload.get("phase", "")).lower()
        if phase not in {"pilot", "main"}:
            phase = ""
        conditions = tuple(
            condition
            for condition in (str(item).upper() for item in payload.get("conditions", CONDITIONS))
            if condition in CONDITIONS
        )
        repetitions = integer(payload.get("repetitions")) or 0
        if repetitions < 1:
            return []
        return [
            ManifestSpec(
                path=str(path.resolve()),
                phase=phase,
                tasks=tasks,
                conditions=conditions or CONDITIONS,
                repetitions=repetitions,
            )
        ]

    # The frozen runner manifest points to one schedule containing both phases.
    schedule_path = resolve_schedule_path(path, payload.get("schedule_path"))
    if schedule_path is None:
        return []
    schedule = read_json(schedule_path)
    jobs = schedule.get("jobs")
    if not isinstance(jobs, list):
        return []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for job in jobs:
        if not isinstance(job, dict):
            continue
        phase = str(job.get("phase", "")).lower()
        if phase in {"pilot", "main"}:
            grouped[phase].append(job)
    specs: list[ManifestSpec] = []
    for phase, phase_jobs in sorted(grouped.items()):
        phase_tasks = tuple(
            dict.fromkeys(str(job["task_id"]) for job in phase_jobs if job.get("task_id"))
        )
        phase_conditions = tuple(
            condition
            for condition in CONDITIONS
            if any(str(job.get("condition", "")).upper() == condition for job in phase_jobs)
        )
        repetitions = max((integer(job.get("repetition")) or 0 for job in phase_jobs), default=0)
        if phase_tasks and phase_conditions and repetitions > 0:
            specs.append(
                ManifestSpec(
                    path=str(path.resolve()),
                    phase=phase,
                    tasks=phase_tasks,
                    conditions=phase_conditions,
                    repetitions=repetitions,
                )
            )
    return specs


def load_manifests(paths: Iterable[Path]) -> tuple[list[ManifestSpec], list[str]]:
    manifests: list[ManifestSpec] = []
    warnings: list[str] = []
    for path in unique_paths(paths):
        try:
            parsed = parse_manifest(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"Could not parse manifest {path} ({exception_category(exc)}).")
            continue
        if not parsed:
            warnings.append(f"Ignored non-run manifest without tasks/repetitions or schedule: {path}")
            continue
        manifests.extend(parsed)
    return manifests, warnings


def phase_for(task_id: str, explicit_phase: Any, pilot_tasks: set[str], main_tasks: set[str]) -> str:
    # Pilot membership wins so a mislabeled pilot row can never enter a main estimate.
    if task_id in pilot_tasks:
        return "pilot"
    phase = str(explicit_phase or "").lower()
    if phase == "pilot":
        return "pilot"
    if task_id in main_tasks or phase == "main":
        return "main"
    return "main_assumed"


def invalid_flags(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    raw_reasons = payload.get("invalid_reasons", payload.get("invalid_reason", []))
    if isinstance(raw_reasons, str) and raw_reasons:
        reasons.append(category(raw_reasons, "reported_invalid_reason"))
    elif isinstance(raw_reasons, list):
        reasons.extend(category(item, "reported_invalid_reason") for item in raw_reasons if item)
    for field in (
        "infra_error",
        "error",
        "result_error",
        "verifier_error",
        "b_contaminated",
        "credential_reflection_detected",
    ):
        value = payload.get(field)
        if value:
            reasons.append(field)
    return list(dict.fromkeys(reasons))


def parse_finish(
    payload: dict[str, Any],
    source_path: Path,
    pilot_tasks: set[str],
    main_tasks: set[str],
) -> Observation:
    execution_id, _ = first_value(payload, ("execution_id", "run_id", "id"))
    task_id, _ = first_value(payload, ("task_id", "task_name", "task.id"))
    condition, _ = first_value(payload, ("condition", "metadata.condition"))
    reward_value, reward_path = first_value(payload, ("official_reward", "reward"))
    reward = numeric_reward(reward_value)
    status = category(payload.get("status"), "unknown_status")
    reasons = invalid_flags(payload)
    explicitly_invalid = bool(payload.get("invalid", False))
    valid_status = status in {"scored", "completed", "complete", "passed", "failed"}
    valid = valid_status and not explicitly_invalid and not reasons and reward is not None
    if reward is None:
        reasons.append("missing_or_non_numeric_official_reward")
    if not valid_status:
        reasons.append(f"non_scored_status_{status}")
    success = payload.get("success")
    if not isinstance(success, bool):
        success = None
    return Observation(
        execution_id=str(execution_id or f"{source_path}:{payload.get('time', 'finish')}"),
        task_id=str(task_id or ""),
        condition=str(condition or "").upper(),
        phase=phase_for(str(task_id or ""), payload.get("phase"), pilot_tasks, main_tasks),
        repetition=integer(payload.get("repetition")),
        status=status or ("scored" if valid else "invalid"),
        valid=valid,
        official_reward=reward if valid else None,
        success=success if valid else None,
        invalid_reasons=list(dict.fromkeys(reasons)),
        reward_source=f"run_state.finish.{reward_path or 'missing'}",
        source_path=str(source_path.resolve()),
        official_result_path=(
            str(payload.get("official_result_path") or payload.get("result_path"))
            if payload.get("official_result_path") or payload.get("result_path")
            else None
        ),
        event_time=(
            str(payload.get("timestamp") or payload.get("time"))
            if payload.get("timestamp") or payload.get("time")
            else None
        ),
    )


def parse_unfinished_start(
    payload: dict[str, Any],
    source_path: Path,
    pilot_tasks: set[str],
    main_tasks: set[str],
) -> Observation:
    execution_id = str(payload.get("execution_id") or f"{source_path}:unfinished")
    task_id = str(payload.get("task_id") or "")
    return Observation(
        execution_id=execution_id,
        task_id=task_id,
        condition=str(payload.get("condition") or "").upper(),
        phase=phase_for(task_id, payload.get("phase"), pilot_tasks, main_tasks),
        repetition=integer(payload.get("repetition")),
        status="invalid",
        valid=False,
        official_reward=None,
        success=None,
        invalid_reasons=["start_without_finish"],
        reward_source="none",
        source_path=str(source_path.resolve()),
        event_time=(
            str(payload.get("timestamp") or payload.get("time"))
            if payload.get("timestamp") or payload.get("time")
            else None
        ),
    )


def load_run_state(
    paths: Iterable[Path], pilot_tasks: set[str], main_tasks: set[str]
) -> tuple[
    list[Observation],
    set[Path],
    set[tuple[str, str, str, int]],
    list[str],
]:
    events: dict[str, list[tuple[Path, int, dict[str, Any]]]] = defaultdict(list)
    warnings: list[str] = []
    for path in unique_paths(paths):
        try:
            rows = read_jsonl(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"Could not parse run state {path} ({exception_category(exc)}).")
            continue
        for line_number, payload in rows:
            execution_id = str(payload.get("execution_id") or f"{path}:{line_number}")
            events[execution_id].append((path, line_number, payload))

    observations: list[Observation] = []
    referenced_results: set[Path] = set()
    finished_cells: set[tuple[str, str, str, int]] = set()
    for execution_id, rows in sorted(events.items()):
        finishes = [row for row in rows if str(row[2].get("event", "")).lower() == "finish"]
        if finishes:
            path, _, payload = finishes[-1]
            observation = parse_finish(payload, path, pilot_tasks, main_tasks)
            if len(finishes) > 1:
                warnings.append(f"Execution {execution_id} has multiple finish events; the last event was used.")
            if observation.official_result_path:
                result_path = Path(observation.official_result_path)
                if not result_path.is_absolute():
                    result_path = path.parent / result_path
                referenced_results.add(result_path.resolve())
            cell = observation.schedule_cell()
            if cell is not None:
                finished_cells.add(cell)
            observations.append(observation)
            continue
        path, _, payload = rows[-1]
        observations.append(parse_unfinished_start(payload, path, pilot_tasks, main_tasks))
    return observations, referenced_results, finished_cells, warnings


def parse_result_fallback(
    path: Path, pilot_tasks: set[str], main_tasks: set[str]
) -> Observation | None:
    payload = read_json(path)
    task_id, _ = first_value(payload, ("task_id", "task_name", "task.id", "config.task_id"))
    condition, _ = first_value(payload, ("condition", "metadata.condition", "config.condition"))
    if not task_id or str(condition or "").upper() not in CONDITIONS:
        return None
    reward_value, reward_path = first_value(
        payload,
        (
            "official_reward",
            "reward",
            "result.official_reward",
            "result.reward",
            "verifier_result.official_reward",
            "verifier_result.reward",
            "verifier.reward",
            "metrics.reward",
        ),
    )
    reward = numeric_reward(reward_value)
    status_value, _ = first_value(payload, ("status", "result.status", "verifier_result.status"))
    status = category(status_value or "scored", "unknown_status")
    reasons = invalid_flags(payload)
    invalid_status = status in {"invalid", "error", "timeout", "infra_invalid", "runner_error"}
    valid = reward is not None and not invalid_status and not reasons
    if reward is None:
        reasons.append("missing_or_non_numeric_official_reward")
    if invalid_status:
        reasons.append(f"invalid_status_{status}")
    success, _ = first_value(payload, ("success", "result.success"))
    return Observation(
        execution_id=str(payload.get("execution_id") or payload.get("run_id") or path.parent.name),
        task_id=str(task_id),
        condition=str(condition).upper(),
        phase=phase_for(str(task_id), payload.get("phase"), pilot_tasks, main_tasks),
        repetition=integer(payload.get("repetition", payload.get("repeat"))),
        status=status,
        valid=valid,
        official_reward=reward if valid else None,
        success=(success if isinstance(success, bool) and valid else None),
        invalid_reasons=list(dict.fromkeys(reasons)),
        reward_source=f"result.json.{reward_path or 'missing'}",
        source_path=str(path.resolve()),
        official_result_path=str(path.resolve()),
    )


def load_fallback_results(
    paths: Iterable[Path],
    referenced_results: set[Path],
    finished_cells: set[tuple[str, str, str, int]],
    pilot_tasks: set[str],
    main_tasks: set[str],
) -> tuple[list[Observation], list[str]]:
    observations: list[Observation] = []
    warnings: list[str] = []
    for path in unique_paths(paths):
        if path.resolve() in referenced_results:
            continue
        try:
            observation = parse_result_fallback(path, pilot_tasks, main_tasks)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"Could not parse result {path} ({exception_category(exc)}).")
            continue
        if observation is None:
            warnings.append(f"Ignored result without explicit task_id and B/F/S condition: {path}")
            continue
        cell = observation.schedule_cell()
        phase = "main" if observation.phase in {"main", "main_assumed"} else observation.phase
        same_condition_finished = any(
            finished_phase == phase
            and finished_task == observation.task_id
            and finished_condition == observation.condition
            for finished_phase, finished_task, finished_condition, _ in finished_cells
        )
        if cell in finished_cells or (observation.repetition is None and same_condition_finished):
            warnings.append(
                f"Ignored result.json compatibility fallback for canonical schedule cell: {path}"
            )
            continue
        observations.append(observation)
        warnings.append(f"Used result.json compatibility fallback for {path}")
    return observations, warnings


def collapse_schedule_duplicates(
    observations: list[Observation], warnings: list[str]
) -> list[Observation]:
    grouped: dict[tuple[str, str, str, int | str], list[Observation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.schedule_key()].append(observation)
    collapsed: list[Observation] = []
    for key, rows in sorted(grouped.items(), key=lambda item: tuple(map(str, item[0]))):
        if len(rows) == 1:
            collapsed.append(rows[0])
            continue
        execution_ids = sorted({row.execution_id for row in rows})
        warnings.append(
            f"Duplicate schedule cell {key} across executions {execution_ids}; marked protocol-invalid."
        )
        first = rows[0]
        collapsed.append(
            Observation(
                execution_id="duplicate:" + ",".join(execution_ids),
                task_id=first.task_id,
                condition=first.condition,
                phase=first.phase,
                repetition=first.repetition,
                status="invalid",
                valid=False,
                official_reward=None,
                success=None,
                invalid_reasons=["duplicate_schedule_cell"],
                reward_source="none",
                source_path=";".join(sorted({row.source_path for row in rows})),
            )
        )
    return collapsed


def expected_cells(manifests: Iterable[ManifestSpec]) -> set[tuple[str, str, str, int]]:
    expected: set[tuple[str, str, str, int]] = set()
    for manifest in manifests:
        if manifest.phase not in {"pilot", "main"}:
            continue
        for task_id in manifest.tasks:
            for condition in manifest.conditions:
                for repetition in range(1, manifest.repetitions + 1):
                    expected.add((manifest.phase, task_id, condition, repetition))
    return expected


def is_main(phase: str) -> bool:
    return phase in {"main", "main_assumed"}


def condition_counts(
    observations: list[Observation], expected: set[tuple[str, str, str, int]], phase: str
) -> dict[str, dict[str, int]]:
    selected = [row for row in observations if (is_main(row.phase) if phase == "main" else row.phase == phase)]
    observed_keys = {
        ("main" if is_main(row.phase) else row.phase, row.task_id, row.condition, row.repetition)
        for row in selected
        if row.repetition is not None
    }
    counts: dict[str, dict[str, int]] = {}
    for condition in CONDITIONS:
        condition_rows = [row for row in selected if row.condition == condition]
        phase_expected = {cell for cell in expected if cell[0] == phase and cell[2] == condition}
        counts[condition] = {
            "valid": sum(row.valid for row in condition_rows),
            "invalid": sum(not row.valid for row in condition_rows),
            "observed": len(condition_rows),
            "expected": len(phase_expected),
            "missing_scheduled": len(phase_expected - observed_keys),
        }
    return counts


def invalid_reason_counts(rows: Iterable[Observation]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        if not row.valid:
            counter.update(row.invalid_reasons or ["unspecified_invalid"])
    return dict(sorted(counter.items()))


def build_task_condition_rows(
    observations: list[Observation], expected: set[tuple[str, str, str, int]]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    for row in observations:
        if is_main(row.phase) and row.condition in CONDITIONS and row.task_id:
            grouped[(row.task_id, row.condition)].append(row)
    for phase, task_id, condition, _repetition in expected:
        if phase == "main":
            grouped.setdefault((task_id, condition), [])

    output: list[dict[str, Any]] = []
    for (task_id, condition), rows in sorted(grouped.items()):
        valid_rows = [row for row in rows if row.valid and row.official_reward is not None]
        rewards = [float(row.official_reward) for row in valid_rows]
        expected_repetitions = {
            repetition
            for phase, cell_task, cell_condition, repetition in expected
            if phase == "main" and cell_task == task_id and cell_condition == condition
        }
        observed_repetitions = {row.repetition for row in rows if row.repetition is not None}
        output.append(
            {
                "task_id": task_id,
                "condition": condition,
                "mean_official_reward": statistics.fmean(rewards) if rewards else None,
                "n_valid": len(valid_rows),
                "n_invalid": sum(not row.valid for row in rows),
                "n_expected": len(expected_repetitions),
                "n_missing_scheduled": len(expected_repetitions - observed_repetitions),
                "invalid_reasons": invalid_reason_counts(rows),
            }
        )
    return output


def percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("Cannot take a percentile of an empty sequence")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def bootstrap_seed(base_seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{base_seed}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def task_bootstrap(
    differences: list[float], label: str, samples: int, seed: int
) -> tuple[float | None, float | None]:
    if not differences:
        return None, None
    rng = random.Random(bootstrap_seed(seed, label))
    size = len(differences)
    estimates = [
        statistics.fmean(differences[rng.randrange(size)] for _ in range(size))
        for _ in range(samples)
    ]
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def build_effect_rows(
    task_condition_rows: list[dict[str, Any]], samples: int, seed: int
) -> list[dict[str, Any]]:
    means = {
        (row["task_id"], row["condition"]): row["mean_official_reward"]
        for row in task_condition_rows
        if row["mean_official_reward"] is not None
    }
    task_ids = sorted({task_id for task_id, _ in means})
    effects: list[dict[str, Any]] = []
    for label, treatment, reference in EFFECTS:
        paired_tasks = [
            task_id
            for task_id in task_ids
            if (task_id, treatment) in means and (task_id, reference) in means
        ]
        differences = [
            float(means[(task_id, treatment)]) - float(means[(task_id, reference)])
            for task_id in paired_tasks
        ]
        ci_low, ci_high = task_bootstrap(differences, label, samples, seed)
        effects.append(
            {
                "effect": label,
                "treatment": treatment,
                "reference": reference,
                "task_level_paired_mean": statistics.fmean(differences) if differences else None,
                "ci_95_low": ci_low,
                "ci_95_high": ci_high,
                "n_paired_tasks": len(paired_tasks),
                "paired_task_ids": paired_tasks,
                "bootstrap_samples": samples,
                "bootstrap_seed": seed,
            }
        )
    return effects


def baseline_pass_rate(observations: list[Observation], phase: str, success_threshold: float) -> float | None:
    by_task: dict[str, list[float]] = defaultdict(list)
    for row in observations:
        phase_matches = is_main(row.phase) if phase == "main" else row.phase == phase
        if not phase_matches or row.condition != "B" or not row.valid or row.official_reward is None:
            continue
        success = row.success
        if success is None:
            success = row.official_reward >= success_threshold
        by_task[row.task_id].append(float(success))
    task_rates = [statistics.fmean(values) for values in by_task.values() if values]
    return statistics.fmean(task_rates) if task_rates else None


def aggregate(
    manifest_paths: list[Path],
    run_state_paths: list[Path],
    result_paths: list[Path],
    *,
    bootstrap_samples: int,
    bootstrap_seed_value: int,
    b_warning_threshold: float,
    success_threshold: float,
) -> dict[str, Any]:
    manifests, warnings = load_manifests(manifest_paths)
    pilot_tasks = {task for manifest in manifests if manifest.phase == "pilot" for task in manifest.tasks}
    main_tasks = {task for manifest in manifests if manifest.phase == "main" for task in manifest.tasks}
    overlap = sorted(pilot_tasks & main_tasks)
    if overlap:
        warnings.append(f"Tasks appear in both pilot and main manifests; pilot exclusion wins: {overlap}")

    observations, referenced_results, finished_cells, state_warnings = load_run_state(
        run_state_paths, pilot_tasks, main_tasks
    )
    warnings.extend(state_warnings)
    fallback_rows, fallback_warnings = load_fallback_results(
        result_paths, referenced_results, finished_cells, pilot_tasks, main_tasks
    )
    warnings.extend(fallback_warnings)
    observations.extend(fallback_rows)
    observations = collapse_schedule_duplicates(observations, warnings)

    malformed = [
        row
        for row in observations
        if not row.task_id or row.condition not in CONDITIONS
    ]
    if malformed:
        warnings.append(
            f"Excluded {len(malformed)} observations lacking task_id or a B/F/S condition."
        )
    observations = [
        row for row in observations if row.task_id and row.condition in CONDITIONS
    ]
    if not manifests:
        warnings.append(
            "No compatible run manifest was found; unmarked tasks are assumed main and schedule completeness is unknown."
        )

    expected = expected_cells(manifests)
    task_rows = build_task_condition_rows(observations, expected)
    effects = build_effect_rows(task_rows, bootstrap_samples, bootstrap_seed_value)
    main_counts = condition_counts(observations, expected, "main")
    pilot_counts = condition_counts(observations, expected, "pilot")
    for phase in ("pilot", "main"):
        rate = baseline_pass_rate(observations, phase, success_threshold)
        if rate is not None and rate >= b_warning_threshold:
            warnings.append(
                f"High {phase} B pass rate ({rate:.3f} >= {b_warning_threshold:.3f}); "
                "reported as a limitation only. No task was removed or replaced."
            )

    missing_main = sum(item["missing_scheduled"] for item in main_counts.values())
    if missing_main:
        warnings.append(f"Main schedule has {missing_main} missing cells; no reward was imputed.")

    main_rows = [row for row in observations if is_main(row.phase)]
    pilot_rows = [row for row in observations if row.phase == "pilot"]
    return {
        "schema_version": "skillsbench-bfs-aggregate-v1",
        "metric": {
            "primary": "official_reward",
            "unit": "task-level condition mean across valid repetitions",
            "effects": [label for label, _, _ in EFFECTS],
            "uncertainty": "nonparametric percentile bootstrap over paired tasks",
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_seed": bootstrap_seed_value,
        },
        "evidence_boundary": {
            "pilot_excluded_from_main_estimates": True,
            "infra_invalid_imputed_as_zero": False,
            "high_b_rate_changes_task_roster": False,
            "candidate_identity": (
                f"S is {S_CANDIDATE_DESCRIPTION}. The aggregator does not establish provenance; "
                "use the frozen run manifest for the recorded generator identity."
            ),
            "condition_definitions": {
                "B": "no task skill bundle",
                "F": "the official SkillsBench task skill bundle",
                "S": S_CANDIDATE_DESCRIPTION,
            },
        },
        "inputs": {
            "manifests": [str(path.resolve()) for path in unique_paths(manifest_paths)],
            "run_states": [str(path.resolve()) for path in unique_paths(run_state_paths)],
            "result_json": [str(path.resolve()) for path in unique_paths(result_paths)],
        },
        "manifests": [asdict(manifest) for manifest in manifests],
        "counts": {
            "main": main_counts,
            "pilot": pilot_counts,
            "main_invalid_reasons": invalid_reason_counts(main_rows),
            "pilot_invalid_reasons": invalid_reason_counts(pilot_rows),
        },
        "baseline_pass_rate": {
            "main": baseline_pass_rate(observations, "main", success_threshold),
            "pilot": baseline_pass_rate(observations, "pilot", success_threshold),
            "warning_threshold": b_warning_threshold,
            "success_threshold_when_success_missing": success_threshold,
        },
        "task_condition_means": task_rows,
        "effects": effects,
        "observations": [asdict(row) for row in observations],
        "warnings": list(dict.fromkeys(warnings)),
        "parser_assumptions": [
            "Runner finish events are canonical: status=scored, invalid=false, and a numeric official reward define a valid row.",
            "finish.official_reward (or legacy reward) is the normalized BenchFlow verifier reward; result_path is provenance.",
            "A result.json is used only when no finish event references it and it exposes explicit task_id and condition.",
            "A canonical finish event blocks compatibility fallback for the same schedule cell, including older attempts.",
            "Manifest repetitions are interpreted as one-based schedule cells 1..repetitions.",
            "Task means use all valid repetitions. Invalid or missing repetitions are reported and never scored zero.",
        ],
    }


def csv_safe(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: csv_safe(row.get(column)) for column in columns})


def format_number(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"


def markdown_table(columns: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return lines


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# SkillsBench B/F/S Aggregate",
        "",
        "Primary endpoint: official deterministic task reward. Pilot rows are excluded from all main estimates. "
        "Infrastructure-invalid and missing rows are reported but never imputed as zero.",
        f"Condition S is {S_CANDIDATE_DESCRIPTION}.",
        "",
        "## Main Condition Counts",
        "",
    ]
    count_rows = []
    for condition in CONDITIONS:
        item = summary["counts"]["main"][condition]
        count_rows.append(
            [condition, item["valid"], item["invalid"], item["missing_scheduled"], item["expected"]]
        )
    lines.extend(markdown_table(["Condition", "Valid", "Invalid", "Missing", "Expected"], count_rows))
    lines.extend(["", "## Task-Paired Effects", ""])
    effect_rows = [
        [
            row["effect"],
            format_number(row["task_level_paired_mean"]),
            f"[{format_number(row['ci_95_low'])}, {format_number(row['ci_95_high'])}]",
            row["n_paired_tasks"],
        ]
        for row in summary["effects"]
    ]
    lines.extend(markdown_table(["Effect", "Mean", "Task-bootstrap 95% CI", "Paired tasks"], effect_rows))
    lines.extend(["", "## Pilot Diagnostics", ""])
    pilot_rows = []
    for condition in CONDITIONS:
        item = summary["counts"]["pilot"][condition]
        pilot_rows.append([condition, item["valid"], item["invalid"], item["missing_scheduled"]])
    lines.extend(markdown_table(["Condition", "Valid", "Invalid", "Missing"], pilot_rows))
    lines.extend(
        [
            "",
            f"- Main B pass rate: {format_number(summary['baseline_pass_rate']['main'])}",
            f"- Pilot B pass rate: {format_number(summary['baseline_pass_rate']['pilot'])}",
            "- A high B pass rate is diagnostic only; it does not filter, replace, or reweight tasks.",
            "",
            "## Method",
            "",
            "For each task and condition, rewards are averaged over valid repetitions. Each effect is the mean "
            "of paired task-level differences. The percentile interval resamples paired tasks with replacement "
            "using the fixed seed in summary.json, so repetitions remain clustered within task.",
            "",
            "## Warnings",
            "",
        ]
    )
    warnings = summary["warnings"] or ["None."]
    lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["", "## Parser Assumptions", ""])
    lines.extend(f"- {assumption}" for assumption in summary["parser_assumptions"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_outputs(output_dir: Path, summary: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path = output_dir / "summary.md"
    write_markdown(markdown_path, summary)

    observation_columns = [field for field in Observation.__dataclass_fields__]
    observations_path = output_dir / "observations.csv"
    write_csv(observations_path, summary["observations"], observation_columns)
    task_path = output_dir / "task_condition_means.csv"
    write_csv(
        task_path,
        summary["task_condition_means"],
        [
            "task_id",
            "condition",
            "mean_official_reward",
            "n_valid",
            "n_invalid",
            "n_expected",
            "n_missing_scheduled",
            "invalid_reasons",
        ],
    )
    effects_path = output_dir / "effects.csv"
    write_csv(
        effects_path,
        summary["effects"],
        [
            "effect",
            "treatment",
            "reference",
            "task_level_paired_mean",
            "ci_95_low",
            "ci_95_high",
            "n_paired_tasks",
            "paired_task_ids",
            "bootstrap_samples",
            "bootstrap_seed",
        ],
    )
    return {
        "summary_json": summary_path,
        "summary_md": markdown_path,
        "observations_csv": observations_path,
        "task_condition_csv": task_path,
        "effects_csv": effects_path,
    }


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path.resolve())] = path
    return [unique[key] for key in sorted(unique)]


def discover(run_roots: Iterable[Path], filename: str) -> list[Path]:
    paths: list[Path] = []
    for root in run_roots:
        if root.is_file() and root.name == filename:
            paths.append(root)
        elif root.is_dir():
            paths.extend(root.rglob(filename))
    return unique_paths(paths)


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="skillsbench-bfs-aggregate-") as tmp:
        root = Path(tmp)
        manifests: list[Path] = []
        states: list[Path] = []
        for phase, tasks, repetitions in (("pilot", ["p1"], 1), ("main", ["t1", "t2", "t3"], 2)):
            run_root = root / phase
            run_root.mkdir(parents=True)
            manifest = run_root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "skillsbench-bfs-run-manifest-v1",
                        "phase": phase,
                        "tasks": tasks,
                        "conditions": list(CONDITIONS),
                        "repetitions": repetitions,
                    }
                ),
                encoding="utf-8",
            )
            manifests.append(manifest)
            state = run_root / "run_state.jsonl"
            rows: list[dict[str, Any]] = []
            executed_tasks = [task_id for task_id in tasks if task_id != "t3"]
            for task_id in executed_tasks:
                for repetition in range(1, repetitions + 1):
                    rewards = {
                        "p1": {"B": 1.0, "F": 1.0, "S": 1.0},
                        "t1": {"B": 0.0, "F": 1.0, "S": 0.5 if repetition == 1 else 1.0},
                        "t2": {"B": 1.0, "F": 0.5, "S": 1.0},
                    }[task_id]
                    for condition in CONDITIONS:
                        invalid = task_id == "t2" and condition == "F" and repetition == 2
                        rows.append(
                            {
                                "schema_version": "skillsbench-bfs-run-state-v1",
                                "event": "finish",
                                "execution_id": f"{phase}-{task_id}-{condition}-{repetition}",
                                "task_id": task_id,
                                "condition": condition,
                                "phase": phase,
                                "repetition": repetition,
                                "status": "invalid" if invalid else "scored",
                                "invalid": invalid,
                                "invalid_reasons": ["infra_fixture"] if invalid else [],
                                "official_reward": None if invalid else rewards[condition],
                                "success": None if invalid else rewards[condition] >= 1.0,
                            }
                        )
            state.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            states.append(state)

        runner_manifest_root = root / "actual-runner-manifest"
        runner_manifest_root.mkdir()
        schedule_path = runner_manifest_root / "schedule.json"
        schedule_jobs = [
            {
                "task_id": task_id,
                "condition": condition,
                "phase": phase,
                "repetition": repetition,
            }
            for phase, tasks, repetitions in (
                ("pilot", ["p1"], 1),
                ("main", ["t1", "t2", "t3"], 2),
            )
            for task_id in tasks
            for repetition in range(1, repetitions + 1)
            for condition in CONDITIONS
        ]
        schedule_path.write_text(json.dumps({"jobs": schedule_jobs}), encoding="utf-8")
        runner_manifest_path = runner_manifest_root / "manifest.json"
        runner_manifest_path.write_text(
            json.dumps({"schedule_path": str(schedule_path), "planned_jobs": len(schedule_jobs)}),
            encoding="utf-8",
        )
        runner_specs = parse_manifest(runner_manifest_path)
        assert {spec.phase for spec in runner_specs} == {"pilot", "main"}
        assert next(spec for spec in runner_specs if spec.phase == "main").repetitions == 2

        summary = aggregate(
            manifests,
            states,
            [],
            bootstrap_samples=500,
            bootstrap_seed_value=DEFAULT_BOOTSTRAP_SEED,
            b_warning_threshold=DEFAULT_B_WARNING_THRESHOLD,
            success_threshold=1.0,
        )
        effects = {row["effect"]: row for row in summary["effects"]}
        assert math.isclose(effects["F-B"]["task_level_paired_mean"], 0.25)
        assert summary["counts"]["main"]["F"]["valid"] == 3
        assert summary["counts"]["main"]["F"]["invalid"] == 1
        assert summary["counts"]["main"]["F"]["missing_scheduled"] == 2
        assert summary["counts"]["pilot"]["B"]["valid"] == 1
        assert all(row["task_id"] != "p1" for row in summary["task_condition_means"])
        t3_f = next(
            row
            for row in summary["task_condition_means"]
            if row["task_id"] == "t3" and row["condition"] == "F"
        )
        assert t3_f["mean_official_reward"] is None
        assert t3_f["n_missing_scheduled"] == 2

        fallback_path = root / "fallback" / "result.json"
        fallback_path.parent.mkdir()
        fallback_path.write_text(
            json.dumps(
                {
                    "task_id": "fallback-task",
                    "condition": "S",
                    "phase": "main",
                    "repetition": 1,
                    "reward": 0.75,
                    "status": "scored",
                }
            ),
            encoding="utf-8",
        )
        fallback = parse_result_fallback(fallback_path, set(), set())
        assert fallback is not None
        assert fallback.valid and fallback.official_reward == 0.75
        outputs = write_outputs(root / "out", summary)
        assert all(path.is_file() for path in outputs.values())
    print("self-test passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", action="append", type=Path, default=[])
    parser.add_argument("--manifest", action="append", type=Path, default=[])
    parser.add_argument("--run-state", action="append", type=Path, default=[])
    parser.add_argument("--result", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--b-warning-threshold", type=float, default=DEFAULT_B_WARNING_THRESHOLD)
    parser.add_argument("--success-threshold", type=float, default=1.0)
    parser.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--base-url-env", default=DEFAULT_BASE_URL_ENV)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.run_root and not args.run_state and not args.result:
        raise SystemExit("Provide --run-root, --run-state, or --result")
    if args.output_dir is None:
        raise SystemExit("--output-dir is required")
    if args.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be positive")
    if not 0.0 <= args.b_warning_threshold <= 1.0:
        raise SystemExit("--b-warning-threshold must be in [0, 1]")

    manifest_paths = unique_paths([*args.manifest, *discover(args.run_root, "manifest.json")])
    state_paths = unique_paths([*args.run_state, *discover(args.run_root, "run_state.jsonl")])
    result_paths = unique_paths([*args.result, *discover(args.run_root, "result.json")])
    summary = aggregate(
        manifest_paths,
        state_paths,
        result_paths,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed_value=args.bootstrap_seed,
        b_warning_threshold=args.b_warning_threshold,
        success_threshold=args.success_threshold,
    )
    safe_summary, credential_reflection, redactor = secure_summary(
        summary, args.api_key_env, args.base_url_env
    )
    outputs = write_outputs(args.output_dir, safe_summary)
    for path in outputs.values():
        print(redactor.text(str(path)))
    if credential_reflection:
        print("error: credential_reflection_detected", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
