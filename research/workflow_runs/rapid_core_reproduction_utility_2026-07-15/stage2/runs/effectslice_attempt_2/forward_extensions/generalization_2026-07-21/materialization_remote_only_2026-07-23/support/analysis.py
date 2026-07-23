from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from typing import Any


RESOURCE_FIELDS = [
    "candidate_artifact_bytes",
    "candidate_artifact_cl100k_tokens",
    "canonical_model_visible_payload_bytes",
    "provider_reported_input_tokens",
    "provider_reported_output_tokens",
    "provider_reported_total_tokens",
    "terminal_attempt_elapsed_ms",
    "retry_overhead_ms",
]


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _summary(values: list[float | int | None]) -> dict[str, Any]:
    observed = [float(value) for value in values if value is not None]
    if not observed:
        return {"non_null": 0, "registered": len(values), "median": None, "minimum": None, "maximum": None, "sum": None}
    return {
        "non_null": len(observed),
        "registered": len(values),
        "median": statistics.median(observed),
        "minimum": min(observed),
        "maximum": max(observed),
        "sum": sum(observed),
    }


def _valid(row: dict[str, Any]) -> bool:
    return row.get("row_valid") is True and row.get("private_score") is not None


def _primary_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_condition[str(row["condition"])].append(row)
    if set(by_condition) != {"B", "F", "S"} or any(len(by_condition[key]) != 6 for key in ("B", "F", "S")):
        return {"state": "Invalid", "reasons": ["incomplete_schedule"]}
    if any(not _valid(row) for values in by_condition.values() for row in values):
        return {"state": "Invalid", "reasons": ["invalid_terminal_row"]}
    success = {key: sum(row["condition_success"] is True for row in values) for key, values in by_condition.items()}
    margins = 0
    per_block = {}
    for block in range(1, 7):
        f_row = next(row for row in by_condition["F"] if row["block_id"] == block)
        s_row = next(row for row in by_condition["S"] if row["block_id"] == block)
        passed = float(s_row["private_score"]) >= float(f_row["private_score"]) - 0.05
        margins += passed
        per_block[str(block)] = passed
    reasons = []
    if success["B"] > 1:
        reasons.append("B_sensitivity")
    if success["F"] < 5:
        reasons.append("F_insufficient")
    if success["S"] < 5:
        reasons.append("S_insufficient")
    if margins < 5:
        reasons.append("paired_margin")
    for registry, blocks in (("A", {1, 2, 3}), ("B", {4, 5, 6})):
        local = {condition: [row for row in values if row["block_id"] in blocks] for condition, values in by_condition.items()}
        if sum(row["condition_success"] is True for row in local["B"]) > 1:
            reasons.append(f"{registry}_B_sensitivity")
        if sum(row["condition_success"] is True for row in local["F"]) < 2:
            reasons.append(f"{registry}_F_insufficient")
        if sum(row["condition_success"] is True for row in local["S"]) < 2:
            reasons.append(f"{registry}_S_insufficient")
        if sum(per_block[str(block)] for block in blocks) < 2:
            reasons.append(f"{registry}_paired_margin")
    return {"state": "Admit" if not reasons else "Reject", "reasons": reasons, "successes": success, "valid_margin_blocks": margins}


def analyze(document: dict[str, Any]) -> dict[str, Any]:
    rows = document["rows"]
    allowlist = list(document["allowed_execution_ids"])
    ids = [str(row["execution_id"]) for row in rows]
    if ids != allowlist or len(ids) != len(set(ids)):
        raise ValueError("analysis rows must exactly match the frozen execution allowlist")
    family_counts = dict(sorted(Counter(str(row["execution_family"]) for row in rows).items()))
    terminal_counts = dict(sorted(Counter(str(row["terminal_outcome"]) for row in rows).items()))
    cells: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        cells[(str(row["task_id"]), str(row["model_slot_id"]), str(row["candidate_id"]))].append(row)
    cell_rows = []
    for (task, model, candidate), values in sorted(cells.items()):
        resource = {field: _summary([row.get(field) for row in values]) for field in RESOURCE_FIELDS}
        cell_rows.append({
            "task_id": task,
            "model_slot_id": model,
            "candidate_id": candidate,
            "registered": len(values),
            "valid": sum(_valid(row) for row in values),
            "operational_successes": sum(row.get("condition_success") is True for row in values),
            "scores": [row.get("private_score") for row in values],
            "terminal_outcomes": dict(sorted(Counter(str(row["terminal_outcome"]) for row in values).items())),
            "resources": resource,
        })
    primary_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["execution_family"] == "primary":
            primary_groups[str(row["task_id"])].append(row)
    task_states = [{"task_id": task, **_primary_state(values)} for task, values in sorted(primary_groups.items())]
    pair_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        pair_groups[str(row["pair_id"])].append(row)
    pair_rows = []
    for pair_id, values in sorted(pair_groups.items()):
        by_condition = {str(row["condition"]): row for row in values}
        deltas = {}
        for left, right in (("S", "F"), ("F", "B"), ("S", "B"), ("C", "F")):
            if left in by_condition and right in by_condition and _valid(by_condition[left]) and _valid(by_condition[right]):
                deltas[f"{left}_minus_{right}"] = float(by_condition[left]["private_score"]) - float(by_condition[right]["private_score"])
        pair_rows.append({"pair_id": pair_id, "task_id": values[0]["task_id"], "family": values[0]["execution_family"], "block_id": values[0]["block_id"], "deltas": deltas})
    return {
        "schema_version": "effectslice-fg1-analysis-result.v1",
        "row_count": len(rows),
        "family_counts": family_counts,
        "terminal_outcome_counts": terminal_counts,
        "task_states": task_states,
        "cells": cell_rows,
        "pairs": pair_rows,
    }


def main() -> None:
    document = json.load(sys.stdin)
    sys.stdout.buffer.write(_canonical(analyze(document)))


if __name__ == "__main__":
    main()
