from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
GENERALIZATION_ROOT = HERE.parent.parent
DEFAULT_OVERLAY = HERE.parent / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_PREREGISTRATION = (
    GENERALIZATION_ROOT
    / "preregistration_remote_only_2026-07-22"
    / "experiment_plan.json"
)
DEFAULT_OUTPUT = HERE / "outputs"
PRIMARY_FILTER = {
    "execution_family": "primary",
    "model_slot_id": "deepseek_primary",
    "variant_id": "primary_dag_ratio_60_v1",
}
REGISTERED = {
    "total_b_max": 1,
    "total_f_min": 5,
    "total_s_min": 5,
    "total_margin_min": 5,
    "registry_b_max": 1,
    "registry_f_min": 2,
    "registry_s_min": 2,
    "registry_margin_min": 2,
    "margin_tolerance": 0.05,
}
LOO_THRESHOLDS = {
    "total_b_max": 1,
    "total_f_min": 4,
    "total_s_min": 4,
    "total_margin_min": 4,
    "margin_tolerance": 0.05,
}
REASON_PRECEDENCE = (
    "full-insufficient",
    "baseline-sensitive",
    "slice-insufficient",
    "margin-shortfall",
)
REGISTERED_FIELDS = (
    "paper_id",
    "domain",
    "task_id",
    "state",
    "primary_reject_reason",
    "failed_reason_groups",
    "failed_gates",
    "B_successes",
    "F_successes",
    "S_successes",
    "valid_margin_blocks",
    "A_B_successes",
    "A_F_successes",
    "A_S_successes",
    "A_valid_margin_blocks",
    "B_B_successes",
    "B_F_successes",
    "B_S_successes",
    "B_valid_margin_blocks",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, fields: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def portable_reference(path: Path) -> str:
    try:
        return path.resolve().relative_to(HERE.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def load_primary(path: Path) -> list[dict[str, Any]]:
    overlay = json.loads(path.read_text(encoding="utf-8"))
    records = overlay["records"]
    if len(records) != 1296:
        raise ValueError("Expected 1,296 terminal overlay rows.")
    primary = [
        row
        for row in records
        if all(row.get(field) == value for field, value in PRIMARY_FILTER.items())
    ]
    if len(primary) != 432:
        raise ValueError(f"Expected 432 primary rows, observed {len(primary)}.")
    if Counter(row["condition"] for row in primary) != {"B": 144, "F": 144, "S": 144}:
        raise ValueError("Primary B/F/S counts must each equal 144.")
    for row in primary:
        if row["terminal_outcome"] not in {"operational_success", "hard_contract_failure"}:
            raise ValueError(f"Nonterminal primary row {row['global_sequence_index']}.")
        score = float(row["private_score"])
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Out-of-range score at row {row['global_sequence_index']}.")
    return primary


def validate_registration(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    sla = plan["scoring"]["admission_sla"]
    observed = {
        "total_b_max": sla["total_six_blocks"]["maximum_B_successes"],
        "total_f_min": sla["total_six_blocks"]["minimum_F_successes"],
        "total_s_min": sla["total_six_blocks"]["minimum_S_successes"],
        "total_margin_min": sla["total_six_blocks"]["minimum_valid_paired_margin_blocks"],
        "registry_b_max": sla["each_three_block_registry"]["maximum_B_successes"],
        "registry_f_min": sla["each_three_block_registry"]["minimum_F_successes"],
        "registry_s_min": sla["each_three_block_registry"]["minimum_S_successes"],
        "registry_margin_min": sla["each_three_block_registry"][
            "minimum_valid_paired_margin_blocks"
        ],
        "margin_tolerance": 0.05,
    }
    if observed != REGISTERED:
        raise ValueError(f"Registered SLA changed: {observed}")
    if plan["scoring"]["reject_reason_precedence"] != list(REASON_PRECEDENCE):
        raise ValueError("Reject-reason precedence changed.")
    loo_rule = plan["analysis_contract"]["leave_one_block_out"]
    for fragment in ("B<=1", "F>=4", "S>=4", "margin>=4", "per-registry gates are not applied"):
        if fragment not in loo_rule:
            raise ValueError(f"Registered leave-one-block rule is missing {fragment!r}.")
    candidate_yield = plan["success_conditions"]["candidate_yield"]
    if "8/24" not in candidate_yield or "three domains" not in candidate_yield:
        raise ValueError("Registered candidate-yield target changed.")


def index_tasks(rows: list[dict[str, Any]]) -> dict[str, dict[int, dict[str, dict[str, Any]]]]:
    tasks: dict[str, dict[int, dict[str, dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        task_id = row["task_id"]
        block_id = int(row["block_id"])
        condition = row["condition"]
        if condition in tasks[task_id][block_id]:
            raise ValueError(f"Duplicate {task_id}/{block_id}/{condition} row.")
        tasks[task_id][block_id][condition] = row
    if len(tasks) != 24:
        raise ValueError(f"Expected 24 primary tasks, observed {len(tasks)}.")
    for task_id, blocks in tasks.items():
        if set(blocks) != set(range(1, 7)):
            raise ValueError(f"Task {task_id} does not cover blocks 1..6.")
        if any(set(cell) != {"B", "F", "S"} for cell in blocks.values()):
            raise ValueError(f"Task {task_id} contains an incomplete B/F/S block.")
    return tasks


def task_metrics(
    blocks: dict[int, dict[str, dict[str, Any]]],
    block_ids: Iterable[int],
    margin_tolerance: float,
) -> dict[str, Any]:
    selected = [blocks[block_id] for block_id in block_ids]
    metrics: dict[str, Any] = {
        "required_rows_valid": all(
            row["terminal_outcome"] in {"operational_success", "hard_contract_failure"}
            for block in selected
            for row in block.values()
        )
    }
    for condition in ("B", "F", "S"):
        metrics[f"{condition}_successes"] = sum(
            bool(block[condition]["operational_success"]) for block in selected
        )
    metrics["valid_margin_blocks"] = sum(
        float(block["S"]["private_score"])
        >= float(block["F"]["private_score"]) - margin_tolerance - 1e-12
        for block in selected
    )
    for registry_id in ("A", "B"):
        registry_blocks = [
            block for block in selected if block["F"]["registry_id"] == registry_id
        ]
        for block in registry_blocks:
            if any(row["registry_id"] != registry_id for row in block.values()):
                raise ValueError("Registry mismatch inside a B/F/S block.")
        for condition in ("B", "F", "S"):
            metrics[f"{registry_id}_{condition}_successes"] = sum(
                bool(block[condition]["operational_success"]) for block in registry_blocks
            )
        metrics[f"{registry_id}_valid_margin_blocks"] = sum(
            float(block["S"]["private_score"])
            >= float(block["F"]["private_score"]) - margin_tolerance - 1e-12
            for block in registry_blocks
        )
    return metrics


def evaluate(
    metrics: dict[str, Any], thresholds: dict[str, Any], apply_registry: bool
) -> dict[str, Any]:
    if not metrics["required_rows_valid"]:
        return {
            "state": "Invalid",
            "primary_reject_reason": "",
            "failed_reason_groups": [],
            "failed_gates": ["required_rows_valid"],
        }
    failures: list[tuple[str, str]] = []
    total_checks = (
        ("full-insufficient", "F_successes", ">=", thresholds["total_f_min"]),
        ("baseline-sensitive", "B_successes", "<=", thresholds["total_b_max"]),
        ("slice-insufficient", "S_successes", ">=", thresholds["total_s_min"]),
        (
            "margin-shortfall",
            "valid_margin_blocks",
            ">=",
            thresholds["total_margin_min"],
        ),
    )
    for reason, field, operator, limit in total_checks:
        passes = metrics[field] >= limit if operator == ">=" else metrics[field] <= limit
        if not passes:
            failures.append((reason, f"total_{field}_{operator}_{limit}"))
    if apply_registry:
        for registry_id in ("A", "B"):
            registry_checks = (
                (
                    "full-insufficient",
                    f"{registry_id}_F_successes",
                    ">=",
                    thresholds["registry_f_min"],
                ),
                (
                    "baseline-sensitive",
                    f"{registry_id}_B_successes",
                    "<=",
                    thresholds["registry_b_max"],
                ),
                (
                    "slice-insufficient",
                    f"{registry_id}_S_successes",
                    ">=",
                    thresholds["registry_s_min"],
                ),
                (
                    "margin-shortfall",
                    f"{registry_id}_valid_margin_blocks",
                    ">=",
                    thresholds["registry_margin_min"],
                ),
            )
            for reason, field, operator, limit in registry_checks:
                passes = metrics[field] >= limit if operator == ">=" else metrics[field] <= limit
                if not passes:
                    failures.append((reason, f"{field}_{operator}_{limit}"))
    failed_groups = [reason for reason in REASON_PRECEDENCE if any(item[0] == reason for item in failures)]
    return {
        "state": "Admit" if not failures else "Reject",
        "primary_reject_reason": failed_groups[0] if failed_groups else "",
        "failed_reason_groups": failed_groups,
        "failed_gates": [gate for _, gate in failures],
    }


def state_counts(states: dict[str, str]) -> dict[str, int]:
    counts = Counter(states.values())
    return {state: counts.get(state, 0) for state in ("Admit", "Reject", "Invalid")}


def profile_summary(
    profile_id: str,
    thresholds: dict[str, Any],
    task_blocks: dict[str, dict[int, dict[str, dict[str, Any]]]],
    registered_states: dict[str, str],
) -> tuple[dict[str, Any], dict[str, str]]:
    states: dict[str, str] = {}
    for task_id, blocks in task_blocks.items():
        metrics = task_metrics(blocks, range(1, 7), thresholds["margin_tolerance"])
        states[task_id] = evaluate(metrics, thresholds, apply_registry=True)["state"]
    changed = sorted(task_id for task_id, state in states.items() if state != registered_states[task_id])
    counts = state_counts(states)
    return (
        {
            "profile_id": profile_id,
            **thresholds,
            **{f"{state.lower()}_tasks": count for state, count in counts.items()},
            "changed_task_count": len(changed),
            "changed_task_ids": json.dumps(changed, separators=(",", ":")),
        },
        states,
    )


def analyze(overlay_path: Path, preregistration_path: Path, output_dir: Path) -> None:
    validate_registration(preregistration_path)
    primary = load_primary(overlay_path)
    task_blocks = index_tasks(primary)
    task_metadata = {
        task_id: {
            "paper_id": next(iter(blocks.values()))["F"]["paper_id"],
            "domain": next(iter(blocks.values()))["F"]["domain"],
        }
        for task_id, blocks in task_blocks.items()
    }

    registered_rows: list[dict[str, Any]] = []
    registered_states: dict[str, str] = {}
    registered_metrics: dict[str, dict[str, Any]] = {}
    for task_id, blocks in sorted(task_blocks.items()):
        metrics = task_metrics(blocks, range(1, 7), REGISTERED["margin_tolerance"])
        decision = evaluate(metrics, REGISTERED, apply_registry=True)
        registered_states[task_id] = decision["state"]
        registered_metrics[task_id] = metrics
        registered_rows.append(
            {
                **task_metadata[task_id],
                "task_id": task_id,
                "state": decision["state"],
                "primary_reject_reason": decision["primary_reject_reason"],
                "failed_reason_groups": json.dumps(
                    decision["failed_reason_groups"], separators=(",", ":")
                ),
                "failed_gates": json.dumps(decision["failed_gates"], separators=(",", ":")),
                **{field: metrics[field] for field in REGISTERED_FIELDS if field in metrics},
            }
        )

    registered_counts = state_counts(registered_states)
    admitted_domains = sorted(
        {
            task_metadata[task_id]["domain"]
            for task_id, state in registered_states.items()
            if state == "Admit"
        }
    )
    registered_summary_rows = [
        {"state": state, "tasks": count} for state, count in registered_counts.items()
    ]

    total_grid_rows: list[dict[str, Any]] = []
    total_grid_states: dict[str, dict[str, str]] = {}
    for b_max, f_min, s_min, margin_min in itertools.product(
        (0, 1, 2), (4, 5, 6), (4, 5, 6), (4, 5, 6)
    ):
        thresholds = {
            **REGISTERED,
            "total_b_max": b_max,
            "total_f_min": f_min,
            "total_s_min": s_min,
            "total_margin_min": margin_min,
        }
        profile_id = f"B{b_max}_F{f_min}_S{s_min}_M{margin_min}"
        row, states = profile_summary(profile_id, thresholds, task_blocks, registered_states)
        row["registered_profile"] = thresholds == REGISTERED
        total_grid_rows.append(row)
        total_grid_states[profile_id] = states

    registry_profiles: list[tuple[str, dict[str, Any]]] = [("registered", dict(REGISTERED))]
    for field, values in (
        ("registry_b_max", (0, 2)),
        ("registry_f_min", (1, 3)),
        ("registry_s_min", (1, 3)),
        ("registry_margin_min", (1, 3)),
    ):
        for value in values:
            thresholds = dict(REGISTERED)
            thresholds[field] = value
            registry_profiles.append((f"{field}_{value}", thresholds))
    registry_rows: list[dict[str, Any]] = []
    registry_states: dict[str, dict[str, str]] = {}
    for profile_id, thresholds in registry_profiles:
        row, states = profile_summary(profile_id, thresholds, task_blocks, registered_states)
        row["changed_parameter"] = "" if profile_id == "registered" else profile_id.rsplit("_", 1)[0]
        row["changed_value"] = "" if profile_id == "registered" else profile_id.rsplit("_", 1)[1]
        registry_rows.append(row)
        registry_states[profile_id] = states

    tolerance_rows: list[dict[str, Any]] = []
    tolerance_states: dict[str, dict[str, str]] = {}
    for tolerance in (0.0, 0.025, 0.05, 0.075, 0.10):
        thresholds = {**REGISTERED, "margin_tolerance": tolerance}
        profile_id = f"margin_tolerance_{tolerance:.3f}"
        row, states = profile_summary(profile_id, thresholds, task_blocks, registered_states)
        row["registered_profile"] = abs(tolerance - 0.05) < 1e-12
        tolerance_rows.append(row)
        tolerance_states[profile_id] = states

    loo_rows: list[dict[str, Any]] = []
    loo_by_task: dict[str, list[str]] = defaultdict(list)
    for task_id, blocks in sorted(task_blocks.items()):
        for omitted_block in range(1, 7):
            remaining = [block_id for block_id in range(1, 7) if block_id != omitted_block]
            metrics = task_metrics(blocks, remaining, LOO_THRESHOLDS["margin_tolerance"])
            decision = evaluate(metrics, LOO_THRESHOLDS, apply_registry=False)
            loo_by_task[task_id].append(decision["state"])
            loo_rows.append(
                {
                    **task_metadata[task_id],
                    "task_id": task_id,
                    "omitted_block_id": omitted_block,
                    "omitted_registry_id": blocks[omitted_block]["F"]["registry_id"],
                    "registered_six_block_state": registered_states[task_id],
                    "five_block_state": decision["state"],
                    "differs_from_registered": decision["state"] != registered_states[task_id],
                    "primary_reject_reason": decision["primary_reject_reason"],
                    "failed_reason_groups": json.dumps(
                        decision["failed_reason_groups"], separators=(",", ":")
                    ),
                    "failed_gates": json.dumps(decision["failed_gates"], separators=(",", ":")),
                    "B_successes": metrics["B_successes"],
                    "F_successes": metrics["F_successes"],
                    "S_successes": metrics["S_successes"],
                    "valid_margin_blocks": metrics["valid_margin_blocks"],
                }
            )

    stability_rows: list[dict[str, Any]] = []
    for task_id in sorted(task_blocks):
        grid_values = [states[task_id] for states in total_grid_states.values()]
        registry_values = [states[task_id] for states in registry_states.values()]
        tolerance_values = [states[task_id] for states in tolerance_states.values()]
        loo_values = loo_by_task[task_id]
        all_sensitivity = grid_values + registry_values + tolerance_values + loo_values
        stability_rows.append(
            {
                **task_metadata[task_id],
                "task_id": task_id,
                "registered_state": registered_states[task_id],
                "total_grid_admit_profiles": grid_values.count("Admit"),
                "total_grid_profiles": len(grid_values),
                "registry_oat_admit_profiles": registry_values.count("Admit"),
                "registry_oat_profiles": len(registry_values),
                "margin_tolerance_admit_profiles": tolerance_values.count("Admit"),
                "margin_tolerance_profiles": len(tolerance_values),
                "leave_one_block_admit_omissions": loo_values.count("Admit"),
                "leave_one_block_omissions": len(loo_values),
                "all_sensitivity_states_match_registered": all(
                    state == registered_states[task_id] for state in all_sensitivity
                ),
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "registered_task_decisions.csv", REGISTERED_FIELDS, registered_rows)
    write_csv(
        output_dir / "registered_decision_summary.csv",
        ("state", "tasks"),
        registered_summary_rows,
    )
    total_grid_fields = list(total_grid_rows[0])
    registry_fields = list(registry_rows[0])
    tolerance_fields = list(tolerance_rows[0])
    loo_fields = list(loo_rows[0])
    stability_fields = list(stability_rows[0])
    write_csv(output_dir / "sla_total_threshold_grid.csv", total_grid_fields, total_grid_rows)
    write_csv(output_dir / "sla_registry_oat.csv", registry_fields, registry_rows)
    write_csv(output_dir / "margin_tolerance_sensitivity.csv", tolerance_fields, tolerance_rows)
    write_csv(output_dir / "leave_one_block_out.csv", loo_fields, loo_rows)
    write_csv(output_dir / "task_decision_stability.csv", stability_fields, stability_rows)

    loo_state_counts = Counter(row["five_block_state"] for row in loo_rows)
    result = {
        "schema_version": "effectslice-sla-sensitivity.v1",
        "status": "verified_forward_analysis",
        "scope": {
            "primary_tasks": 24,
            "papers": 12,
            "blocks_per_task": 6,
            "primary_rows": 432,
        },
        "registered_six_block_decisions": {
            "thresholds": REGISTERED,
            "state_counts": registered_counts,
            "primary_reject_reason_counts": dict(
                sorted(
                    Counter(
                        row["primary_reject_reason"] or "none" for row in registered_rows
                    ).items()
                )
            ),
        },
        "registered_engineering_target": {
            "minimum_admitted_tasks": 8,
            "minimum_domains": 3,
            "observed_admitted_tasks": registered_counts["Admit"],
            "observed_domains": len(admitted_domains),
            "admitted_domain_ids": admitted_domains,
            "achieved": registered_counts["Admit"] >= 8 and len(admitted_domains) >= 3,
        },
        "total_threshold_grid": {
            "profiles": len(total_grid_rows),
            "registered_per_registry_gates_held_fixed": True,
            "profiles_changing_at_least_one_task": sum(
                int(row["changed_task_count"] > 0) for row in total_grid_rows
            ),
            "tasks_changed_in_any_profile": sorted(
                task_id
                for task_id in task_blocks
                if any(
                    states[task_id] != registered_states[task_id]
                    for states in total_grid_states.values()
                )
            ),
        },
        "registry_one_at_a_time": {
            "profiles": len(registry_rows),
            "registered_total_gates_held_fixed": True,
            "profiles_changing_at_least_one_task": sum(
                int(row["changed_task_count"] > 0) for row in registry_rows
            ),
        },
        "margin_tolerance_sensitivity": {
            "tolerances": [0.0, 0.025, 0.05, 0.075, 0.10],
            "registered_tolerance": 0.05,
            "profiles_changing_at_least_one_task": sum(
                int(row["changed_task_count"] > 0) for row in tolerance_rows
            ),
        },
        "leave_one_block_out": {
            "rule": LOO_THRESHOLDS,
            "recomputations": len(loo_rows),
            "state_counts": {
                state: loo_state_counts.get(state, 0) for state in ("Admit", "Reject", "Invalid")
            },
            "recomputations_differing_from_registered": sum(
                int(row["differs_from_registered"]) for row in loo_rows
            ),
            "tasks_with_any_changed_omission": sorted(
                task_id
                for task_id, states in loo_by_task.items()
                if any(state != registered_states[task_id] for state in states)
            ),
        },
        "claim_boundaries": {
            "registered_decision": (
                "Only registered_task_decisions.csv contains the frozen six-block decisions."
            ),
            "sensitivity": (
                "Threshold grids and five-block omissions are descriptive perturbations and "
                "cannot replace, select, or rescue a registered decision."
            ),
            "coverage": (
                "All sensitivity analyses use the 24-task DeepSeek primary scope only."
            ),
        },
    }
    write_json(output_dir / "sla_sensitivity.json", result)

    output_names = (
        "leave_one_block_out.csv",
        "margin_tolerance_sensitivity.csv",
        "registered_decision_summary.csv",
        "registered_task_decisions.csv",
        "sla_registry_oat.csv",
        "sla_sensitivity.json",
        "sla_total_threshold_grid.csv",
        "task_decision_stability.csv",
    )
    manifest = {
        "schema_version": "effectslice-forward-analysis-manifest.v1",
        "section": "05_sla_sensitivity",
        "inputs": {
            portable_reference(overlay_path): sha256(overlay_path),
            portable_reference(preregistration_path): sha256(preregistration_path),
        },
        "runtime": {"python": platform.python_version()},
        "parameters": {
            "registered_sla": REGISTERED,
            "leave_one_block_out": LOO_THRESHOLDS,
            "total_threshold_grid_values": {
                "total_b_max": [0, 1, 2],
                "total_f_min": [4, 5, 6],
                "total_s_min": [4, 5, 6],
                "total_margin_min": [4, 5, 6],
            },
            "margin_tolerances": [0.0, 0.025, 0.05, 0.075, 0.10],
        },
        "outputs": {name: {"sha256": sha256(output_dir / name)} for name in output_names},
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--preregistration", type=Path, default=DEFAULT_PREREGISTRATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.overlay, args.preregistration, args.output_dir)


if __name__ == "__main__":
    main()
