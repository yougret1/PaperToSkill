from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row {line_number} is not an object")
        rows.append(value)
    return rows


def _is_finite_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _is_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_interval(value: Any, *, line_interval: bool = False) -> bool:
    if not isinstance(value, dict) or not _is_digest(value.get("file_digest")):
        return False
    start = value.get("line_start" if line_interval else "byte_start")
    end = value.get("line_end" if line_interval else "byte_end")
    minimum = 1 if line_interval else 0
    return (
        isinstance(start, int)
        and not isinstance(start, bool)
        and isinstance(end, int)
        and not isinstance(end, bool)
        and minimum <= start < end
    )


def _four_way_atom_ids(source_map: dict[str, Any]) -> tuple[str, ...] | None:
    atoms = source_map.get("atoms") or source_map.get("atom_inventory")
    if not isinstance(atoms, list) or not atoms:
        return None
    atom_ids = []
    for atom in atoms:
        if not isinstance(atom, dict):
            return None
        atom_id = atom.get("atom_id")
        workflow_step = atom.get("workflow_step")
        source_span = atom.get("source_span")
        executable_region = atom.get("executable_region")
        contract_role = atom.get("contract_role")
        if not isinstance(atom_id, str) or not atom_id:
            return None
        if not isinstance(workflow_step, str) or not workflow_step:
            return None
        if not _valid_interval(source_span) or not _valid_interval(
            source_span, line_interval=True
        ):
            return None
        if not _valid_interval(executable_region):
            return None
        if not isinstance(executable_region.get("symbol"), str) or not executable_region["symbol"]:
            return None
        if not isinstance(contract_role, str) or not contract_role:
            return None
        atom_ids.append(atom_id)
    if len(set(atom_ids)) != len(atom_ids) or atom_ids != sorted(atom_ids):
        return None
    return tuple(atom_ids)


def _valid_dependency_graph(source_map: dict[str, Any], atom_ids: tuple[str, ...]) -> bool:
    nodes = source_map.get("dependency_nodes")
    edges = source_map.get("dependency_edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return False
    if tuple(nodes) != atom_ids:
        return False
    edge_keys = []
    for edge in edges:
        if not isinstance(edge, dict):
            return False
        source = edge.get("from")
        target = edge.get("to")
        if source not in atom_ids or target not in atom_ids or source == target:
            return False
        edge_keys.append((source, target))
    return len(set(edge_keys)) == len(edge_keys)


def _paired_identifiers(
    full_rows: list[dict[str, Any]], baseline_rows: list[dict[str, Any]]
) -> set[tuple[str, str, str]]:
    def valid_keys(rows: list[dict[str, Any]]) -> Counter[tuple[str, str, str]]:
        keys: Counter[tuple[str, str, str]] = Counter()
        for row in rows:
            identifiers = (row.get("pair_id"), row.get("case_id"), row.get("seed_block_id"))
            if not all(isinstance(value, str) and value for value in identifiers):
                continue
            if str(row.get("status", "")).lower() not in {"completed", "success", "ok"}:
                continue
            if not _is_finite_number(row.get("task_score")):
                continue
            keys[identifiers] += 1
        return keys

    full_keys = valid_keys(full_rows)
    baseline_keys = valid_keys(baseline_rows)
    return {
        key
        for key in full_keys.keys() & baseline_keys.keys()
        if full_keys[key] == 1 and baseline_keys[key] == 1
    }


def _valid_score_bounds(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(_is_finite_number(item) for item in value)
        and value[0] < value[1]
    )


def _valid_cost_weights(value: Any) -> bool:
    expected = {"api", "compute", "guardrail", "labor"}
    return (
        isinstance(value, dict)
        and set(value) == expected
        and all(_is_finite_number(weight) and weight >= 0 for weight in value.values())
        and math.isclose(sum(value.values()), 1.0, rel_tol=0.0, abs_tol=1e-12)
    )


def _valid_predicates(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    required = {"id", "callable", "digest", "missing_value_policy"}
    identifiers = []
    for predicate in value:
        if not isinstance(predicate, dict) or not required.issubset(predicate):
            return False
        if not all(isinstance(predicate[field], str) and predicate[field] for field in ("id", "callable")):
            return False
        if not _is_digest(predicate["digest"]):
            return False
        if predicate["missing_value_policy"] not in {"fail", "abstain"}:
            return False
        identifiers.append(predicate["id"])
    return len(set(identifiers)) == len(identifiers)


def _valid_query_budget(value: Any, atom_count: int) -> bool:
    if not isinstance(value, dict) or set(value) != {"Q", "N"}:
        return False
    q = value["Q"]
    n = value["N"]
    if any(isinstance(item, bool) or not isinstance(item, int) for item in (q, n)):
        return False
    return q > 0 and n > 0 and q >= n and n == atom_count


def audit_project(project_root: Path, config_path: Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    config = _load_json(Path(config_path).resolve())
    if not isinstance(config, dict):
        raise ValueError("experiment config must be an object")
    for field in ("task_spec", "main_row_selection", "raw_rows"):
        if not isinstance(config.get(field), str) or not config[field]:
            raise ValueError(f"experiment config requires path field: {field}")
    task_spec = _load_json(root / config["task_spec"])
    selection = _load_json(root / config["main_row_selection"])
    raw_rows = _load_jsonl(root / config["raw_rows"])
    if not isinstance(task_spec, dict) or not isinstance(task_spec.get("tasks"), list):
        raise ValueError("task spec must contain a tasks list")
    tasks = task_spec["tasks"]
    if not tasks:
        raise ValueError("task spec must contain at least one task")
    if not isinstance(selection, dict) or not isinstance(selection.get("rows"), list):
        raise ValueError("main row selection must contain a rows list")
    selection_rows = selection["rows"]
    if any(
        not isinstance(row, dict)
        or not all(isinstance(row.get(field), str) and row[field] for field in ("task_id", "condition", "run_id"))
        for row in selection_rows
    ):
        raise ValueError("main row selection contains an invalid row")
    selected_keys = {
        (row["task_id"], row["condition"], row["run_id"])
        for row in selection_rows
    }
    selected_rows = [
        row
        for row in raw_rows
        if (row.get("task_id"), row.get("condition"), row.get("run_id")) in selected_keys
    ]
    minimum_pairs = config.get("statistics", {}).get("minimum_eligibility_pairs", 3)
    if isinstance(minimum_pairs, bool) or not isinstance(minimum_pairs, int) or minimum_pairs < 1:
        raise ValueError("minimum_eligibility_pairs must be a positive integer")
    adapters = config.get("task_adapters", {})
    source_paths = config.get("source_maps", {})
    if not isinstance(adapters, dict) or not isinstance(source_paths, dict):
        raise ValueError("task_adapters and source_maps must be objects")
    task_reports = []
    blocker_counts: Counter[str] = Counter()

    seen_task_ids = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("task spec contains a non-object task")
        if not all(
            isinstance(task.get(field), str) and task[field]
            for field in ("id", "source_paper_id")
        ):
            raise ValueError("task requires nonempty id and source_paper_id")
        if not isinstance(task.get("conditions"), list) or not all(
            isinstance(condition, str) and condition for condition in task["conditions"]
        ):
            raise ValueError("task conditions must be nonempty strings")
        task_id = task["id"]
        if task_id in seen_task_ids:
            raise ValueError(f"duplicate task id: {task_id}")
        seen_task_ids.add(task_id)
        paper_id = task["source_paper_id"]
        conditions = set(task.get("conditions", []))
        rows = [row for row in selected_rows if row.get("task_id") == task_id]
        f_rows = [row for row in rows if row.get("condition") == "papertoskill"]
        b_rows = [
            row
            for row in rows
            if str(row.get("condition", "")).lower() in {"b", "baseline", "no_skill"}
        ]
        missing = []

        if not ({"b", "baseline", "no_skill"} & {value.lower() for value in conditions}):
            missing.append("missing_same_scaffold_no_skill_baseline")
        paired = _paired_identifiers(f_rows, b_rows)
        if len(paired) < minimum_pairs:
            missing.append("insufficient_eligibility_pairs")
        if not paired:
            missing.append("missing_case_level_pairs")

        adapter = adapters.get(task_id, {})
        if not isinstance(adapter, dict):
            adapter = {}
        if not _valid_score_bounds(adapter.get("score_bounds")):
            missing.append("missing_score_bounds")
        if not _valid_cost_weights(adapter.get("cost_weights")):
            missing.append("missing_cost_conversion")
        if not _valid_predicates(adapter.get("contracts")) or not _valid_predicates(
            adapter.get("guardrails")
        ):
            missing.append("missing_contract_guardrail_predicates")

        source_path = source_paths.get(paper_id)
        source_map = None
        if source_path and (root / source_path).exists():
            source_map = _load_json(root / source_path)
        if source_map is None:
            missing.append("missing_source_map")
            atom_ids = None
        else:
            if not isinstance(source_map, dict):
                atom_ids = None
            else:
                atom_ids = _four_way_atom_ids(source_map)
            if atom_ids is None:
                missing.append("missing_four_way_atoms")
            if atom_ids is None or not _valid_dependency_graph(source_map, atom_ids):
                missing.append("missing_dependency_graph")

        if atom_ids is None or not _valid_query_budget(
            adapter.get("query_budget"), len(atom_ids)
        ):
            missing.append("missing_complete_neighbor_budget")

        missing = sorted(set(missing))
        blocker_counts.update(missing)
        task_reports.append(
            {
                "task_id": task_id,
                "source_paper_id": paper_id,
                "selected_row_count": len(rows),
                "selected_full_artifact_rows": len(f_rows),
                "selected_no_skill_rows": len(b_rows),
                "paired_case_count": len(paired),
                "ready": not missing,
                "missing_requirements": missing,
            }
        )

    ready_count = sum(1 for task in task_reports if task["ready"])
    return {
        "schema_version": "effectslice-readiness-report.v1",
        "evidence_boundary": (
            "Read-only development readiness audit; this is not EffectSlice effectiveness evidence. "
            "Aggregate task scores are not treated as paired observations."
        ),
        "task_count": len(task_reports),
        "ready_task_count": ready_count,
        "not_ready_task_count": len(task_reports) - ready_count,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "tasks": task_reports,
    }
