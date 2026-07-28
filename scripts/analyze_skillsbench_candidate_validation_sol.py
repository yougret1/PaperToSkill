#!/usr/bin/env python3
"""Select diagnostic tasks and analyze the minimal SkillsBench validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "skillsbench-candidate-validation-analysis-v1"
ARMS = ("B", "F", "P", "D")
BLIND_LABELS = {"intended-preserving", "destructive", "unclear"}
AMENDMENT_SCHEMA = "skillsbench-candidate-validation-amendment-v1"
DEFER_STATES = {
    "baseline-inconclusive",
    "full-inconclusive",
    "evidence-inconclusive",
}
Z_975 = 1.959963984540054


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


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree_contents(root: Path, *, normalize_shells: bool = False) -> str | None:
    """Hash a tree using the materials-builder's canonical byte-level format."""
    if not root.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        if normalize_shells and path.suffix.lower() == ".sh":
            payload = payload.replace(b"\r\n", b"\n")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def runner_tree_sha256(root: Path) -> str | None:
    if not root.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def runner_mirror_fingerprint(task_dir: Path) -> dict[str, Any]:
    task_md = task_dir / "task.md"
    dockerfile = task_dir / "environment" / "Dockerfile"
    skills_dir = task_dir / "environment" / "skills"
    return {
        "task_md_sha256": sha256_file(task_md) if task_md.is_file() else None,
        "dockerfile_sha256": sha256_file(dockerfile) if dockerfile.is_file() else None,
        "skills_tree_sha256": runner_tree_sha256(skills_dir),
        "task_tree_sha256": runner_tree_sha256(task_dir),
    }


def parse_timestamp(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value, f"{label}: timestamp missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError(f"{label}: invalid timestamp") from exc
    require(parsed.tzinfo is not None, f"{label}: timestamp lacks timezone")
    return parsed.astimezone(UTC)


def state_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        require(isinstance(payload, dict), f"line {number}: run-state row must be an object")
        rows.append(payload)
    return rows


def validate_platform_integrity(
    *,
    run_root: Path,
    manifest: dict[str, Any],
    scheduled_rows: list[dict[str, Any]],
    main_finishes: dict[str, dict[str, Any]],
    run_state_path: Path,
) -> str:
    ledger_path = run_root / "platform_repairs.json"
    require(ledger_path.is_file(), f"platform repair ledger missing: {ledger_path}")
    recorded_path = manifest.get("platform_repairs_path")
    require(isinstance(recorded_path, str) and recorded_path, "platform repair path missing")
    require(Path(recorded_path).resolve() == ledger_path.resolve(), "platform repair path changed")
    ledger_sha256 = sha256_file(ledger_path)
    require(
        manifest.get("platform_repairs_sha256") == ledger_sha256,
        "platform repair ledger hash mismatch",
    )
    ledger = required_json(ledger_path, "platform repair ledger")
    require(
        ledger.get("schema_version") == "skillsbench-bfs-platform-repairs-v2",
        "platform repair ledger schema changed",
    )
    events = ledger.get("events")
    require(isinstance(events, list) and events, "platform repair events missing")
    require(int(ledger.get("event_count", -1)) == len(events), "platform repair event count changed")
    compat_path_value = manifest.get("benchflow_compat_entrypoint")
    require(isinstance(compat_path_value, str) and compat_path_value, "compat entrypoint missing")
    compat_path = Path(compat_path_value)
    require(compat_path.is_file(), f"compat entrypoint missing: {compat_path}")
    compat_sha256 = sha256_file(compat_path)
    require(
        manifest.get("benchflow_compat_sha256") == compat_sha256,
        "compat entrypoint hash mismatch",
    )

    expected_fingerprints = manifest.get("mirror_fingerprints") or {}
    mirrors: dict[tuple[str, str], Path] = {}
    for row in scheduled_rows:
        key = (str(row["condition"]), str(row["task_id"]))
        task_dir = Path(str(row["mirror_task_dir"]))
        prior = mirrors.setdefault(key, task_dir)
        require(prior.resolve() == task_dir.resolve(), f"{key}: scheduled mirror path changed")
    for (condition, task), task_dir in mirrors.items():
        expected = (expected_fingerprints.get(condition) or {}).get(task)
        require(isinstance(expected, dict), f"{task}/{condition}: mirror fingerprint missing")
        require(
            runner_mirror_fingerprint(task_dir) == expected,
            f"{task}/{condition}: current mirror fingerprint mismatch",
        )

    repair_times: list[tuple[datetime, set[tuple[str, str]]]] = []
    latest_repairs: dict[tuple[str, str, str], dict[str, Any]] = {}
    repair_count = 0
    compat_changes: list[dict[str, Any]] = []
    for event_number, event in enumerate(events, 1):
        require(isinstance(event, dict), f"platform event {event_number} must be an object")
        repairs = event.get("repairs")
        require(isinstance(repairs, list), f"platform event {event_number} repairs missing")
        require(
            int(event.get("repaired_file_count", -1)) == len(repairs),
            f"platform event {event_number} repair count changed",
        )
        repair_count += len(repairs)
        compat_change = event.get("benchflow_compat_change")
        if compat_change is not None:
            require(isinstance(compat_change, dict), "compat change record must be an object")
            for field in ("before_sha256", "after_sha256"):
                value = compat_change.get(field)
                require(
                    value is None or (isinstance(value, str) and len(value) == 64),
                    f"compat change {field} is invalid",
                )
            compat_changes.append(compat_change)
        affected: set[tuple[str, str]] = set()
        for repair in repairs:
            require(isinstance(repair, dict), "platform repair row must be an object")
            condition = str(repair.get("condition"))
            task = str(repair.get("task_id"))
            relative = str(repair.get("path"))
            require((condition, task) in mirrors, f"unexpected repaired mirror: {task}/{condition}")
            require(relative and not Path(relative).is_absolute(), "platform repair path is not relative")
            affected.add((condition, task))
            latest_repairs[(condition, task, relative)] = repair
        if affected:
            repair_times.append(
                (parse_timestamp(event.get("created_at"), f"platform event {event_number}"), affected)
            )
    require(
        int(ledger.get("repaired_file_count", -1)) == repair_count,
        "platform repair total changed",
    )
    for previous, current in zip(compat_changes, compat_changes[1:]):
        require(
            previous.get("after_sha256") == current.get("before_sha256"),
            "compatibility repair hash chain is broken",
        )
    if compat_changes:
        require(
            compat_changes[-1].get("after_sha256") == compat_sha256,
            "compatibility repair does not bind the current entrypoint",
        )
    for (condition, task, relative), repair in latest_repairs.items():
        target = (mirrors[(condition, task)] / relative).resolve()
        require(target.is_relative_to(mirrors[(condition, task)].resolve()), "repair path escapes mirror")
        require(target.is_file(), f"repaired file missing: {task}/{condition}/{relative}")
        require(sha256_file(target) == repair.get("after_sha256"), "repaired file hash changed")

    starts: dict[tuple[str, int], dict[str, Any]] = {}
    for row in state_rows(run_state_path):
        if row.get("event") == "start" and isinstance(row.get("attempt_number"), int):
            starts[(str(row.get("execution_id")), int(row["attempt_number"]))] = row
    for execution_id, finish in main_finishes.items():
        attempt = finish.get("attempt_number")
        require(isinstance(attempt, int), f"{execution_id}: finish attempt missing")
        start = starts.get((execution_id, attempt))
        require(start is not None, f"{execution_id}: matching start event missing")
        start_time = parse_timestamp(start.get("timestamp"), f"{execution_id} start")
        finish_time = parse_timestamp(finish.get("timestamp"), f"{execution_id} finish")
        key = (str(finish.get("condition")), str(finish.get("task_id")))
        for repair_time, affected in repair_times:
            require(
                key not in affected or not (start_time <= repair_time <= finish_time),
                f"{execution_id}: canonical attempt overlapped a mirror repair",
            )
    return ledger_sha256


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def latest_finishes(path: Path) -> dict[str, dict[str, Any]]:
    finishes: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return finishes
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("event") != "finish":
            continue
        execution_id = payload.get("execution_id")
        require(isinstance(execution_id, str) and execution_id, f"line {number}: missing execution_id")
        finishes[execution_id] = payload
    return finishes


def valid_reward(row: dict[str, Any]) -> float | None:
    reward = row.get("official_reward")
    if (
        row.get("status") != "scored"
        or row.get("invalid") is not False
        or isinstance(reward, bool)
        or not isinstance(reward, (int, float))
        or not 0 <= float(reward) <= 1
    ):
        return None
    return float(reward)


def rows_for(
    finishes: Iterable[dict[str, Any]], *, phase: str, task: str, condition: str
) -> list[dict[str, Any]]:
    return sorted(
        (
            row
            for row in finishes
            if row.get("phase") == phase
            and row.get("task_id") == task
            and row.get("condition") == condition
        ),
        key=lambda row: int(row.get("repetition") or 0),
    )


def required_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {label}: {path}")
    payload = load_json(path)
    require(isinstance(payload, dict), f"{label} must be a JSON object")
    return payload


def validate_blind_labels(path: Path, tasks: list[str]) -> dict[str, dict[str, str]]:
    payload = required_json(path, "blind labels")
    require(payload.get("outcome_access") == "prohibited", "blind labels must prohibit outcome access")
    records = payload.get("records")
    require(isinstance(records, list), "blind-label records missing")
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    reviewer_tasks: set[tuple[str, str]] = set()
    for row in records:
        require(isinstance(row, dict), "blind-label record must be an object")
        if row.get("task_id") not in tasks:
            continue
        task = str(row["task_id"])
        reviewer = row.get("reviewer_id")
        require(isinstance(reviewer, str) and reviewer.strip(), f"{task}: blank reviewer_id")
        key = (reviewer, task)
        require(key not in reviewer_tasks, f"{task}: duplicate label from {reviewer}")
        reviewer_tasks.add(key)
        for candidate in ("P", "D"):
            label = row.get(f"{candidate}_label")
            require(label in BLIND_LABELS, f"{task}: invalid {candidate} label from {reviewer}")
        by_task[task].append(row)
    consensus: dict[str, dict[str, str]] = {}
    for task in tasks:
        task_rows = by_task.get(task, [])
        reviewers = {str(row.get("reviewer_id")) for row in task_rows}
        require(len(reviewers) >= 2, f"{task}: fewer than two independent reviewers")
        p_labels = {str(row.get("P_label")) for row in task_rows}
        d_labels = {str(row.get("D_label")) for row in task_rows}
        consensus[task] = {
            "P": next(iter(p_labels)) if len(p_labels) == 1 else "disagreement",
            "D": next(iter(d_labels)) if len(d_labels) == 1 else "disagreement",
        }
    return consensus


def blind_label_reviewer_ids(path: Path, task: str) -> set[str]:
    payload = required_json(path, "blind labels")
    records = payload.get("records") or []
    return {
        str(row.get("reviewer_id"))
        for row in records
        if isinstance(row, dict) and row.get("task_id") == task and row.get("reviewer_id")
    }


def amendment_path(value: Path) -> Path:
    return value / "amendment.json" if value.is_dir() else value


def validate_amendment_document(path: Path) -> dict[str, Any]:
    payload = required_json(path, "candidate amendment")
    require(payload.get("schema_version") == AMENDMENT_SCHEMA, "candidate amendment schema changed")
    require(payload.get("task_id") == "sec-financial-report", "candidate amendment task changed")
    require(payload.get("trigger") == "unanimous-destructive-specification-label", "candidate amendment trigger changed")
    require(payload.get("one_shot") is True, "candidate amendment is not one-shot")
    require(payload.get("no_further_regeneration") is True, "candidate amendment permits further regeneration")
    require(payload.get("outcome_access") == "prohibited", "candidate amendment accessed outcomes")
    require(payload.get("candidate_outcomes_used") is False, "candidate amendment used P/D outcomes")
    generator = payload.get("generator") or {}
    require(generator.get("mode") == "heuristic/no-llm", "candidate amendment is not no-LLM")
    require(int(generator.get("stage", -1)) == 1, "candidate amendment is not stage 1")
    require(generator.get("tscg") is False, "candidate amendment enabled TSCG")
    candidate = payload.get("candidate") or {}
    for key in ("P1_skills_sha256", "P2_skills_sha256", "D_skills_sha256", "effective_P_pool_sha256"):
        value = candidate.get(key)
        require(isinstance(value, str) and len(value) == 64, f"candidate amendment lacks {key}")
    require(
        candidate["P1_skills_sha256"] != candidate["P2_skills_sha256"],
        "candidate amendment did not change P1",
    )
    contract_path = path.parent / "generator_contract.json"
    require(contract_path.is_file(), "candidate amendment generator contract missing")
    require(
        payload.get("generator_contract_sha256") == sha256_file(contract_path),
        "candidate amendment generator contract hash mismatch",
    )
    require(required_json(contract_path, "generator contract") == generator, "candidate amendment generator contract changed")
    return payload


def validate_selection_amendment(
    *,
    amendment_value: Path,
    materials_root: Path,
    materials: dict[str, Any],
    blind_labels_path: Path,
    screen_protocol_path: Path,
) -> dict[str, Any]:
    path = amendment_path(amendment_value.resolve())
    payload = validate_amendment_document(path)
    task = str(payload["task_id"])
    bindings = payload.get("base_bindings") or {}
    manifest_path = materials_root / "materials_manifest.json"
    original_labels_path = materials_root / "blind_labels.json"
    require(
        bindings.get("materials_manifest_sha256") == sha256_file(manifest_path),
        "candidate amendment base materials hash mismatch",
    )
    require(
        bindings.get("screen_protocol_sha256") == sha256_file(screen_protocol_path),
        "candidate amendment screen protocol hash mismatch",
    )
    require(
        bindings.get("original_blind_labels_sha256") == sha256_file(original_labels_path),
        "candidate amendment original-label hash mismatch",
    )
    original_consensus = validate_blind_labels(original_labels_path, [task])
    require(
        original_consensus[task] == {"P": "destructive", "D": "destructive"},
        "candidate amendment lacks unanimous destructive P1 trigger",
    )
    require(
        blind_label_reviewer_ids(original_labels_path, task).isdisjoint(
            blind_label_reviewer_ids(blind_labels_path, task)
        ),
        "candidate amendment reused an original SEC reviewer",
    )

    rows = materials.get("tasks") or []
    by_task = {str(row.get("task_id")): dict(row) for row in rows if isinstance(row, dict)}
    require(task in by_task, "candidate amendment task absent from materials")
    base_row = by_task[task]
    candidate = payload["candidate"]
    source = payload.get("source") or {}
    require(base_row.get("official_skills_sha256") == source.get("official_skills_sha256"), "candidate amendment official hash changed")
    require(base_row.get("P_skills_sha256") == candidate.get("P1_skills_sha256"), "candidate amendment P1 hash changed")
    require(base_row.get("D_skills_sha256") == candidate.get("D_skills_sha256"), "candidate amendment D hash changed")

    relative_pool = (payload.get("paths") or {}).get("effective_P_pool")
    require(isinstance(relative_pool, str) and relative_pool, "candidate amendment effective P path missing")
    effective_pool = (path.parent / relative_pool).resolve()
    require(
        sha256_tree_contents(effective_pool) == candidate.get("effective_P_pool_sha256"),
        "candidate amendment effective P pool hash mismatch",
    )
    for row_task, row in by_task.items():
        effective_hash = sha256_tree_contents(effective_pool / row_task / "skills")
        expected = candidate["P2_skills_sha256"] if row_task == task else row.get("P_skills_sha256")
        require(effective_hash == expected, f"{row_task}: effective P candidate changed")
    expected_labels = (payload.get("paths") or {}).get("new_blind_labels")
    require(isinstance(expected_labels, str) and expected_labels, "candidate amendment label path missing")
    require(
        blind_labels_path.resolve() == (path.parent / expected_labels).resolve(),
        "selection did not use the amendment's new blind labels",
    )

    new_labels = required_json(blind_labels_path, "amendment blind labels")
    input_bindings = new_labels.get("input_bindings") or {}
    p_binding = input_bindings.get("effective_P_pool") or {}
    require(
        p_binding.get("tree_sha256") == candidate.get("effective_P_pool_sha256"),
        "amendment blind labels used a different effective P pool",
    )
    p_task_hashes = p_binding.get("task_skills_sha256") or {}
    d_task_hashes = ((input_bindings.get("D_pool") or {}).get("task_skills_sha256") or {})
    official_hashes = (
        (input_bindings.get("skillsbench_public_inputs") or {}).get("official_skills_sha256")
        or {}
    )
    screen_tasks = list((required_json(screen_protocol_path, "screen protocol").get("main") or {}).get("tasks") or [])
    require(
        set(input_bindings.get("tasks") or []) == set(screen_tasks),
        "amendment blind-label task set differs from screening",
    )
    for row_task in screen_tasks:
        require(row_task in by_task, f"{row_task}: blind-label task absent from materials")
        row = by_task[row_task]
        require(
            p_task_hashes.get(row_task)
            == sha256_tree_contents(effective_pool / row_task / "skills"),
            f"{row_task}: blind labels used a different P candidate",
        )
        require(
            d_task_hashes.get(row_task) == row.get("D_skills_sha256"),
            f"{row_task}: blind labels used a different D candidate",
        )
        require(
            official_hashes.get(row_task) == row.get("official_skills_sha256"),
            f"{row_task}: blind labels used different official skills",
        )

    by_task[task]["P_skills_sha256"] = candidate["P2_skills_sha256"]
    return {
        "path": path,
        "sha256": sha256_file(path),
        "payload": payload,
        "effective_P_pool": effective_pool,
        "effective_candidate_rows": [by_task[str(row["task_id"])] for row in rows],
    }


def validate_confirmatory_amendment(
    protocol: dict[str, Any], selection: dict[str, Any], blind_labels_path: Path
) -> dict[str, Any] | None:
    binding = protocol.get("candidate_amendment")
    selection_binding = selection.get("candidate_amendment")
    if binding is None and selection_binding is None:
        return None
    require(isinstance(binding, dict) and binding == selection_binding, "selection/protocol amendment binding differs")
    path_value = binding.get("path")
    require(isinstance(path_value, str) and path_value, "candidate amendment path missing")
    path = Path(path_value)
    require(path.is_file(), f"candidate amendment missing: {path}")
    require(binding.get("sha256") == sha256_file(path), "candidate amendment hash mismatch")
    payload = validate_amendment_document(path)
    expected_labels = (payload.get("paths") or {}).get("new_blind_labels")
    require(
        blind_labels_path.resolve() == (path.parent / str(expected_labels)).resolve(),
        "confirmatory protocol did not bind amendment labels",
    )
    pools = protocol.get("candidate_pools") or {}
    effective_pool = Path(str(pools.get("P", "")))
    require(
        effective_pool.resolve() == (path.parent / str((payload.get("paths") or {}).get("effective_P_pool"))).resolve(),
        "confirmatory protocol did not bind the effective P pool",
    )
    require(
        sha256_tree_contents(effective_pool) == (payload.get("candidate") or {}).get("effective_P_pool_sha256"),
        "confirmatory effective P pool hash mismatch",
    )
    return {"path": path, "sha256": sha256_file(path), "payload": payload}


def expected_cells(
    tasks: list[str], conditions: tuple[str, ...], repetitions: int
) -> set[tuple[str, str, int]]:
    return {
        (task, condition, repetition)
        for task in tasks
        for condition in conditions
        for repetition in range(1, repetitions + 1)
    }


def row_cell(row: dict[str, Any], label: str) -> tuple[str, str, int]:
    task = row.get("task_id")
    condition = row.get("condition")
    repetition = row.get("repetition")
    require(isinstance(task, str) and task, f"{label}: missing task_id")
    require(isinstance(condition, str) and condition, f"{label}: missing condition")
    require(
        isinstance(repetition, int) and not isinstance(repetition, bool),
        f"{label}: invalid repetition",
    )
    return task, condition, repetition


def validate_main_evidence(
    *,
    run_root: Path,
    protocol_path: Path,
    tasks: list[str],
    conditions: tuple[str, ...],
    repetitions: int,
    require_audit: bool,
) -> dict[str, Any]:
    require(tasks and len(tasks) == len(set(tasks)), "main tasks must be nonempty and unique")
    require(repetitions > 0, "main repetitions must be positive")
    expected = expected_cells(tasks, conditions, repetitions)
    protocol_sha256 = sha256_file(protocol_path)

    manifest_path = run_root / "manifest.json"
    manifest = required_json(manifest_path, "run manifest")
    require(
        manifest.get("protocol_sha256") == protocol_sha256,
        "run manifest protocol hash does not match the analyzed protocol",
    )
    require(tuple(manifest.get("conditions") or ()) == conditions, "run conditions changed")
    require(manifest.get("credential_values_recorded") is False, "run manifest records credentials")
    require(
        int((manifest.get("planned_by_phase") or {}).get("main", -1)) == len(expected),
        "run manifest main-row count changed",
    )

    schedule_path = run_root / "schedule.json"
    schedule = required_json(schedule_path, "run schedule")
    require(
        manifest.get("schedule_sha256") == sha256_file(schedule_path),
        "run schedule hash does not match the manifest",
    )
    jobs = schedule.get("jobs")
    require(isinstance(jobs, list), "run schedule jobs missing")
    scheduled_main = [row for row in jobs if isinstance(row, dict) and row.get("phase") == "main"]
    schedule_cells = [row_cell(row, "scheduled main row") for row in scheduled_main]
    require(len(schedule_cells) == len(set(schedule_cells)), "run schedule has duplicate main cells")
    require(set(schedule_cells) == expected, "run schedule does not match the frozen main grid")
    schedule_by_execution: dict[str, tuple[str, str, int]] = {}
    for row, cell in zip(scheduled_main, schedule_cells, strict=True):
        execution_id = row.get("execution_id")
        require(
            isinstance(execution_id, str) and execution_id,
            "scheduled main row lacks execution_id",
        )
        require(execution_id not in schedule_by_execution, "duplicate scheduled execution_id")
        schedule_by_execution[execution_id] = cell

    gate_path = run_root / "main_gate.json"
    gate = required_json(gate_path, "main gate")
    require(gate.get("status") == "passed", "main gate did not pass")
    require(gate.get("final_reportable") is True, "main gate is not final-reportable")
    require(gate.get("schedule_count_valid") is True, "main gate schedule count is invalid")
    require(int(gate.get("expected_rows", -1)) == len(expected), "main gate row count changed")
    require(int(gate.get("terminal_rows", -1)) == len(expected), "main gate is not terminal")
    for field in (
        "missing_execution_ids",
        "unexpected_execution_ids",
        "invalid_execution_ids",
        "contaminated_execution_ids",
        "credential_reflection_execution_ids",
        "protocol_invalid_reasons",
    ):
        require(not gate.get(field), f"main gate contains {field}")

    audit_path = run_root / "audit_report.json"
    audit: dict[str, Any] | None = None
    if require_audit:
        audit = required_json(audit_path, "audit report")
        require(audit.get("status") == "passed", "run audit did not pass")
        require(audit.get("final_reportable") is True, "run audit is not final-reportable")
        require(not audit.get("protocol_invalid_reasons"), "run audit reports protocol invalidity")
        audit_main = audit.get("main_gate") or {}
        require(audit_main.get("status") == "passed", "audit main gate did not pass")
        require(
            audit_main.get("final_reportable") is True,
            "audit main gate is not final-reportable",
        )

    run_state = run_root / "run_state.jsonl"
    require(run_state.is_file(), f"missing run state: {run_state}")
    finishes_by_execution = latest_finishes(run_state)
    main_finishes = {
        execution_id: row
        for execution_id, row in finishes_by_execution.items()
        if row.get("phase") == "main"
    }
    require(
        set(main_finishes) == set(schedule_by_execution),
        "terminal main execution IDs do not match the frozen schedule",
    )
    actual_cells: list[tuple[str, str, int]] = []
    for execution_id, row in main_finishes.items():
        cell = row_cell(row, f"terminal row {execution_id}")
        require(cell == schedule_by_execution[execution_id], f"{execution_id}: scheduled cell changed")
        actual_cells.append(cell)
    require(len(actual_cells) == len(set(actual_cells)), "terminal main rows duplicate a repetition cell")
    require(set(actual_cells) == expected, "terminal main rows do not cover repetitions 1..n exactly")
    platform_repairs_sha256 = validate_platform_integrity(
        run_root=run_root,
        manifest=manifest,
        scheduled_rows=jobs,
        main_finishes=main_finishes,
        run_state_path=run_state,
    )

    return {
        "finishes": list(main_finishes.values()),
        "manifest_sha256": sha256_file(manifest_path),
        "schedule_sha256": sha256_file(schedule_path),
        "main_gate_sha256": sha256_file(gate_path),
        "audit_sha256": sha256_file(audit_path) if audit is not None else None,
        "run_state_sha256": sha256_file(run_state),
        "platform_repairs_sha256": platform_repairs_sha256,
    }


def validate_candidate_materials(
    protocol: dict[str, Any], confirm_run: Path, tasks: list[str]
) -> dict[str, dict[str, dict[str, str]]]:
    skillsbench_root = Path(protocol["skillsbench"]["root"])
    pools = protocol.get("candidate_pools") or {}
    require(set(pools) == {"P", "D"}, "candidate pools must be exactly P/D")
    pool_paths = {condition: Path(pools[condition]) for condition in ("P", "D")}

    raw_hashes = protocol.get("candidate_hashes")
    require(isinstance(raw_hashes, list), "candidate hashes missing")
    by_task: dict[str, dict[str, Any]] = {}
    for row in raw_hashes:
        require(isinstance(row, dict), "candidate hash row must be an object")
        task = row.get("task_id")
        require(isinstance(task, str) and task, "candidate hash row lacks task_id")
        require(task not in by_task, f"duplicate candidate hash row: {task}")
        by_task[task] = row

    verified: dict[str, dict[str, dict[str, str]]] = {}
    for task in tasks:
        require(task in by_task, f"{task}: frozen candidate hashes missing")
        row = by_task[task]
        sources = {
            "F": skillsbench_root / "tasks" / task / "environment" / "skills",
            "P": pool_paths["P"] / task / "skills",
            "D": pool_paths["D"] / task / "skills",
        }
        expected_keys = {
            "F": "official_skills_sha256",
            "P": "P_skills_sha256",
            "D": "D_skills_sha256",
        }
        task_hashes: dict[str, dict[str, str]] = {}
        for condition, source in sources.items():
            source_hash = sha256_tree_contents(source)
            require(source_hash is not None, f"{task}/{condition}: source skills missing")
            require(
                row.get(expected_keys[condition]) == source_hash,
                f"{task}/{condition}: frozen source hash mismatch",
            )
            mirror = confirm_run / "work" / condition / task / "environment" / "skills"
            mirror_hash = sha256_tree_contents(mirror)
            require(mirror_hash is not None, f"{task}/{condition}: run mirror skills missing")
            execution_hash = sha256_tree_contents(source, normalize_shells=True)
            require(execution_hash is not None, f"{task}/{condition}: execution hash missing")
            require(
                mirror_hash == execution_hash,
                f"{task}/{condition}: run mirror differs from deterministic LF execution form",
            )
            task_hashes[condition] = {
                "frozen_source_sha256": source_hash,
                "execution_sha256": execution_hash,
            }
        verified[task] = task_hashes
    return verified


def seeded_tie(seed: str, task: str) -> str:
    return hashlib.sha256(f"{seed}:{task}".encode("utf-8")).hexdigest()


def select_tasks(args: argparse.Namespace) -> dict[str, Any]:
    require(not args.output.exists(), f"selection output already exists: {args.output}")
    materials = required_json(args.materials / "materials_manifest.json", "materials manifest")
    screen_protocol_path = args.materials / "screen_protocol.json"
    protocol = required_json(screen_protocol_path, "screen protocol")
    tasks = list(protocol["main"]["tasks"])
    repetitions = int(protocol["main"]["repetitions"])
    require(
        tuple((protocol.get("executor") or {}).get("conditions") or ()) == ("B", "F"),
        "screen protocol conditions must be exactly B/F",
    )
    consensus = validate_blind_labels(args.blind_labels, tasks)
    amendment_info = None
    amendment_value = getattr(args, "amendment", None)
    if amendment_value is not None:
        amendment_info = validate_selection_amendment(
            amendment_value=Path(amendment_value),
            materials_root=args.materials,
            materials=materials,
            blind_labels_path=args.blind_labels,
            screen_protocol_path=screen_protocol_path,
        )
    evidence = validate_main_evidence(
        run_root=args.screen_run,
        protocol_path=screen_protocol_path,
        tasks=tasks,
        conditions=("B", "F"),
        repetitions=repetitions,
        require_audit=False,
    )
    finishes = evidence["finishes"]
    forbidden = [row for row in finishes if row.get("condition") in {"P", "D"}]
    require(not forbidden, "screening run contains forbidden P/D outcomes")

    task_rows: list[dict[str, Any]] = []
    for task in tasks:
        arms: dict[str, dict[str, Any]] = {}
        valid = True
        for condition in ("B", "F"):
            rows = rows_for(finishes, phase="main", task=task, condition=condition)
            rewards = [valid_reward(row) for row in rows]
            arm_valid = len(rows) == repetitions and all(value is not None for value in rewards)
            valid = valid and arm_valid
            arms[condition] = {
                "rows": len(rows),
                "valid": arm_valid,
                "successes": sum(value == 1.0 for value in rewards if value is not None),
                "mean_reward": (
                    sum(value for value in rewards if value is not None) / len(rewards)
                    if arm_valid
                    else None
                ),
            }
        k_b = arms["B"]["successes"]
        k_f = arms["F"]["successes"]
        label_eligible = consensus[task] == {"P": "intended-preserving", "D": "destructive"}
        eligible = bool(valid and label_eligible and k_b <= 1 and k_f >= 2 and k_f > k_b)
        task_rows.append(
            {
                "task_id": task,
                "arms": arms,
                "eligible": eligible,
                "label_eligible": label_eligible,
                "rank_key": [-(k_f - k_b), -k_f, k_b, seeded_tie(protocol["selection_seed"], task)],
                "blind_label_consensus": consensus[task],
            }
        )
    eligible = sorted((row for row in task_rows if row["eligible"]), key=lambda row: row["rank_key"])
    selected = [row["task_id"] for row in eligible[:2]]
    status = "passed" if len(selected) == 2 else "blocked"
    confirm_protocol_path = args.output / "confirm_materials" / "protocol.json"
    selection = {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "status": status,
        "screen_protocol_sha256": sha256_file(screen_protocol_path),
        "screen_manifest_sha256": evidence["manifest_sha256"],
        "screen_schedule_sha256": evidence["schedule_sha256"],
        "screen_main_gate_sha256": evidence["main_gate_sha256"],
        "screen_run_state_sha256": evidence["run_state_sha256"],
        "screen_platform_repairs_sha256": evidence["platform_repairs_sha256"],
        "blind_labels_sha256": sha256_file(args.blind_labels),
        "candidate_outcomes_used": False,
        "task_results": task_rows,
        "selected_tasks": selected,
    }
    if amendment_info is not None:
        selection["candidate_amendment"] = {
            "path": str(amendment_info["path"].resolve()),
            "sha256": amendment_info["sha256"],
        }
        selection["post_screen_outcome_blind_amendment"] = True
        selection["effective_P_pool_sha256"] = amendment_info["payload"]["candidate"][
            "effective_P_pool_sha256"
        ]
    if status == "passed":
        selection["confirm_protocol"] = str(confirm_protocol_path.resolve())
    selection_path = args.output / "selection.json"
    atomic_json(selection_path, selection)
    if status != "passed":
        return selection

    effective_rows = (
        amendment_info["effective_candidate_rows"]
        if amendment_info is not None
        else materials["tasks"]
    )
    effective_p_pool = (
        amendment_info["effective_P_pool"]
        if amendment_info is not None
        else args.materials / "candidate_pool" / "P"
    )
    protocol_out = {
        "schema_version": "skillsbench-candidate-validation-protocol-v1",
        "created_at": utc_now(),
        "selection_seed": "skillsbench-candidate-confirmatory-2026-07-27-v1",
        "skillsbench": protocol["skillsbench"],
        "executor": {"agent": "codex-acp", "model": "gpt-5.6-sol", "conditions": list(ARMS)},
        "candidate_pools": {
            "P": str(effective_p_pool.resolve()),
            "D": str((args.materials / "candidate_pool" / "D").resolve()),
        },
        "pilot": {"tasks": [materials["pilot_task"]], "repetitions": 1},
        "main": {
            "tasks": selected,
            "repetitions": int(materials["confirmatory_repetitions_per_arm"]),
        },
        "selection_record": str(selection_path.resolve()),
        "selection_record_sha256": sha256_file(selection_path),
        "blind_labels": str(args.blind_labels.resolve()),
        "blind_labels_sha256": sha256_file(args.blind_labels),
        "candidate_hashes": [
            row for row in effective_rows if row["task_id"] in {*selected, materials["pilot_task"]}
        ],
        "decision_policy": materials["decision_policy"],
        "evidence_boundary": {
            "screening_rows_excluded": True,
            "confirmatory_selection_uses_only_B_F": True,
            "candidate_outcomes_used_for_selection": False,
            "source_binding": "official SkillsBench skill artifacts, not paper source spans",
            "P": "independent heuristic reducer; not official SkillReducer",
            "D": "uniform body-drop negative control",
        },
    }
    if amendment_info is not None:
        protocol_out["candidate_amendment"] = selection["candidate_amendment"]
        protocol_out["evidence_boundary"]["post_screen_outcome_blind_amendment"] = True
        protocol_out["evidence_boundary"]["candidate_frozen_before_confirmatory"] = True
        protocol_out["evidence_boundary"]["candidate_frozen_before_screening"] = False
    atomic_json(confirm_protocol_path, protocol_out)
    atomic_json(
        args.output / "bundle_manifest.json",
        {
            "schema_version": "skillsbench-candidate-validation-bundle-v1",
            "created_at": utc_now(),
            "selection": str(selection_path.resolve()),
            "selection_sha256": sha256_file(selection_path),
            "protocol": str(confirm_protocol_path.resolve()),
            "protocol_sha256": sha256_file(confirm_protocol_path),
            **(
                {"candidate_amendment": selection["candidate_amendment"]}
                if amendment_info is not None
                else {}
            ),
        },
    )
    return selection


def wilson(k: int, n: int) -> tuple[float, float]:
    p = k / n
    z2 = Z_975**2
    denominator = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denominator
    radius = Z_975 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def newcombe(k_s: int, n_s: int, k_f: int, n_f: int) -> tuple[float, float]:
    p_s, p_f = k_s / n_s, k_f / n_f
    l_s, u_s = wilson(k_s, n_s)
    l_f, u_f = wilson(k_f, n_f)
    lower = (p_s - p_f) - math.sqrt((p_s - l_s) ** 2 + (u_f - p_f) ** 2)
    upper = (p_s - p_f) + math.sqrt((u_s - p_s) ** 2 + (p_f - l_f) ** 2)
    return max(-1.0, lower), min(1.0, upper)


def decide(k_b: int, k_f: int, k_s: int, n: int, policy: dict[str, Any]) -> dict[str, Any]:
    lower, upper = newcombe(k_s, n, k_f, n)
    margin = float(policy["noninferiority_margin"])
    if k_b > int(policy["b_max"]):
        state = "baseline-inconclusive"
    elif k_f < int(policy["f_min"]):
        state = "full-inconclusive"
    elif k_s < int(policy["s_min"]) or upper < -margin:
        state = "RejectCandidate"
    elif lower >= -margin:
        state = "Accept"
    else:
        state = "evidence-inconclusive"
    return {"state": state, "ci_low": lower, "ci_high": upper, "effect": k_s / n - k_f / n}


def analyze_confirmatory(args: argparse.Namespace) -> dict[str, Any]:
    protocol = required_json(args.protocol, "confirmatory protocol")
    require(
        tuple((protocol.get("executor") or {}).get("conditions") or ()) == ARMS,
        "confirmatory protocol conditions must be exactly B/F/P/D",
    )
    tasks = list((protocol.get("main") or {}).get("tasks") or [])
    require(tasks and len(tasks) == len(set(tasks)), "confirmatory tasks must be nonempty and unique")
    n = int(protocol["main"]["repetitions"])
    require(n > 0, "confirmatory repetitions must be positive")

    selection_path = Path(protocol["selection_record"])
    selection = required_json(selection_path, "selection record")
    require(
        protocol.get("selection_record_sha256") == sha256_file(selection_path),
        "selection record hash does not match the confirmatory protocol",
    )
    require(selection.get("status") == "passed", "selection record did not pass")
    require(selection.get("candidate_outcomes_used") is False, "selection used candidate outcomes")
    require(selection.get("selected_tasks") == tasks, "selection and protocol tasks differ")

    blind_labels_path = Path(protocol["blind_labels"])
    require(
        protocol.get("blind_labels_sha256") == sha256_file(blind_labels_path),
        "blind-label hash does not match the confirmatory protocol",
    )
    labels = validate_blind_labels(blind_labels_path, tasks)
    for task, task_labels in labels.items():
        require(
            task_labels == {"P": "intended-preserving", "D": "destructive"},
            f"{task}: confirmatory labels are not unanimous",
        )

    amendment_info = validate_confirmatory_amendment(protocol, selection, blind_labels_path)

    candidate_materials = validate_candidate_materials(protocol, args.confirm_run, tasks)
    evidence = validate_main_evidence(
        run_root=args.confirm_run,
        protocol_path=args.protocol,
        tasks=tasks,
        conditions=ARMS,
        repetitions=n,
        require_audit=True,
    )
    finishes = evidence["finishes"]
    policy = protocol["decision_policy"]
    task_results: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for task in tasks:
        counts: dict[str, int] = {}
        means: dict[str, float | None] = {}
        for arm in ARMS:
            rows = rows_for(finishes, phase="main", task=task, condition=arm)
            rewards = [valid_reward(row) for row in rows]
            arm_valid = len(rows) == n and all(value is not None for value in rewards)
            require(arm_valid, f"{task}/{arm}: invalid confirmatory rewards")
            counts[arm] = sum(value == 1.0 for value in rewards if value is not None)
            means[arm] = (
                sum(value for value in rewards if value is not None) / len(rewards)
                if arm_valid
                else None
            )
        task_results.append({"task_id": task, "successes": counts, "mean_rewards": means})
        if all(means[arm] is not None for arm in ARMS):
            for candidate in ("P", "D"):
                decision = decide(counts["B"], counts["F"], counts[candidate], n, policy)
                expected = labels[task][candidate]
                decision.update(
                    {
                        "task_id": task,
                        "candidate": candidate,
                        "expected_class": expected,
                        "k_B": counts["B"],
                        "k_F": counts["F"],
                        "k_S": counts[candidate],
                        "n": n,
                        "unsafe_accept": expected == "destructive" and decision["state"] == "Accept",
                        "false_reject": expected == "intended-preserving" and decision["state"] == "RejectCandidate",
                        "deferred": decision["state"] in DEFER_STATES,
                    }
                )
                decisions.append(decision)

    report = {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "status": "complete",
        "protocol_sha256": sha256_file(args.protocol),
        "selection_sha256": sha256_file(selection_path),
        "blind_labels_sha256": sha256_file(blind_labels_path),
        "manifest_sha256": evidence["manifest_sha256"],
        "schedule_sha256": evidence["schedule_sha256"],
        "main_gate_sha256": evidence["main_gate_sha256"],
        "audit_sha256": evidence["audit_sha256"],
        "run_state_sha256": evidence["run_state_sha256"],
        "platform_repairs_sha256": evidence["platform_repairs_sha256"],
        "candidate_material_hashes": candidate_materials,
        "screening_rows_excluded": True,
        "confirmatory_tasks": tasks,
        "repetitions_per_arm": n,
        "task_results": task_results,
        "decisions": decisions,
        "decision_counts": dict(Counter(row["state"] for row in decisions)),
        "unsafe_accepts": sum(row["unsafe_accept"] for row in decisions),
        "false_rejects": sum(row["false_reject"] for row in decisions),
        "deferrals": sum(row["deferred"] for row in decisions),
        "boundary": protocol["evidence_boundary"],
    }
    if amendment_info is not None:
        report["candidate_amendment_sha256"] = amendment_info["sha256"]
        report["candidate_amendment_task"] = amendment_info["payload"]["task_id"]
    atomic_json(args.output / "final_report.json", report)
    atomic_text(args.output / "REPORT.md", render_report(report))
    return report


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Minimal SkillsBench Candidate-Level Validation",
        "",
        f"Status: **{report['status']}**.",
        "",
        "## Confirmatory design",
        "",
        f"- Tasks: {', '.join(report['confirmatory_tasks'])}",
        f"- Repetitions per arm: {report['repetitions_per_arm']}",
        "- Arms: B, official full skill F, independent reducer candidate P, and body-drop negative control D.",
        "- Screening rows were excluded; task selection used only B/F screening outcomes.",
        "",
        "## Decisions",
        "",
        "| Task | Candidate | Expected | B | F | Candidate | Effect [95% CI] | Decision |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in report["decisions"]:
        interval = f"{row['effect']:.3f} [{row['ci_low']:.3f}, {row['ci_high']:.3f}]"
        lines.append(
            f"| {row['task_id']} | {row['candidate']} | {row['expected_class']} | "
            f"{row['k_B']}/{row['n']} | {row['k_F']}/{row['n']} | {row['k_S']}/{row['n']} | "
            f"{interval} | {row['state']} |"
        )
    lines.extend(
        [
            "",
            "## Safety summary",
            "",
            f"- Unsafe destructive-candidate accepts: {report['unsafe_accepts']}",
            f"- Preserving-candidate false rejects: {report['false_rejects']}",
            f"- Deferred candidate decisions: {report['deferrals']}",
            f"- Decision counts: {json.dumps(report['decision_counts'], sort_keys=True)}",
            "",
            "## Evidence boundary",
            "",
            "This public benchmark validates the behavioral B/F/candidate decision layer with official SkillsBench verifiers. It does not validate paper source-span fidelity, and the independent reducer is not the official SkillReducer artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    select = subparsers.add_parser("select")
    select.add_argument("--materials", type=Path, required=True)
    select.add_argument("--screen-run", type=Path, required=True)
    select.add_argument("--blind-labels", type=Path, required=True)
    select.add_argument(
        "--amendment",
        type=Path,
        default=None,
        help="Optional outcome-blind candidate amendment directory or amendment.json",
    )
    select.add_argument("--output", type=Path, required=True)
    final = subparsers.add_parser("final")
    final.add_argument("--protocol", type=Path, required=True)
    final.add_argument("--confirm-run", type=Path, required=True)
    final.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = select_tasks(args) if args.command == "select" else analyze_confirmatory(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("status") in {"passed", "complete"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
