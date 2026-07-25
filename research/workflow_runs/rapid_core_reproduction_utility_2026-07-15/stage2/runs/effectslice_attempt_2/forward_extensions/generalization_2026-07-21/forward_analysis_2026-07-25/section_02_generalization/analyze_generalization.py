from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ANALYSIS_ROOT = HERE.parent
DEFAULT_INPUT = ANALYSIS_ROOT / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_PAPER_EFFECTS = (
    ANALYSIS_ROOT / "section_01_primary_effects" / "outputs" / "paper_effects.csv"
)
DEFAULT_OUTPUT = HERE / "outputs"
PRIMARY_VARIANT = "primary_dag_ratio_60_v1"
ANCHOR_TASKS = (
    "AGENT-TF-01",
    "DATA-HDB-01",
    "NLP-LLM-01",
    "SE-PE-01",
)
CONTRASTS = (
    ("F_minus_B", "F", "B"),
    ("S_minus_B", "S", "B"),
    ("S_minus_F", "S", "F"),
)
ENDPOINTS = ("operational_success", "private_score")
PROVIDER_FAMILY = {
    "claude_opus_4_7": "anthropic",
    "deepseek_primary": "deepseek",
    "gpt_5_5": "openai",
    "gpt_5_6_luna": "openai",
    "gpt_5_6_sol": "openai",
    "gpt_5_6_terra": "openai",
}
REDUCER_SPECS = (
    ("alternate_reducers", "dag_greedy_ratio_60_v1", "C"),
    ("alternate_reducers", "source_window_ratio_60_v1", "C"),
    ("primary", PRIMARY_VARIANT, "S"),
    ("structural_ladder", "L0_primary_slice", "C"),
    ("structural_ladder", "L1_mid_restore", "C"),
    ("structural_ladder", "L2_near_full_strict", "C"),
)
TOLERANCE = 1e-15


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mean(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        raise ValueError("Cannot average an empty sequence.")
    return float(sum(materialized) / len(materialized))


def sign_counts(values: Iterable[float]) -> dict[str, int]:
    result = {"positive": 0, "negative": 0, "zero": 0}
    for value in values:
        if value > TOLERANCE:
            result["positive"] += 1
        elif value < -TOLERANCE:
            result["negative"] += 1
        else:
            result["zero"] += 1
    return result


def load_overlay(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["records"]
    indices = sorted(int(row["global_sequence_index"]) for row in rows)
    if len(rows) != 1296 or indices != list(range(1, 1297)):
        raise ValueError("Expected unique terminal overlay rows 1..1296.")
    if sum(bool(row["operational_success"]) for row in rows) != 383:
        raise ValueError("Expected 383 operational successes in the terminal overlay.")
    return rows


def condition_mean(rows: list[dict[str, Any]], endpoint: str) -> float:
    values = []
    for row in rows:
        value = row[endpoint]
        if value is None:
            raise ValueError(
                f"Missing {endpoint} for global row {row['global_sequence_index']}."
            )
        values.append(float(bool(value)) if endpoint == "operational_success" else float(value))
    return mean(values)


def heatmap_cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "paper_id",
        "task_id",
        "domain",
        "condition",
        "model_slot_id",
        "execution_family",
        "variant_id",
        "registry_id",
    )
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    output = []
    for group_key in sorted(grouped):
        group = grouped[group_key]
        sources = sorted({str(row["final_source"]) for row in group})
        scores = [float(row["private_score"]) for row in group]
        output.append(
            {
                **dict(zip(keys, group_key, strict=True)),
                "registered_rows": len(group),
                "operational_successes": sum(bool(row["operational_success"]) for row in group),
                "success_rate": mean(float(bool(row["operational_success"])) for row in group),
                "private_score_mean": mean(scores),
                "private_score_min": min(scores),
                "private_score_max": max(scores),
                "final_source_count": len(sources),
                "final_sources": json.dumps(sources, separators=(",", ":")),
            }
        )
    if len(output) != 432 or sum(row["registered_rows"] for row in output) != 1296:
        raise ValueError("Heatmap aggregation must produce 432 cells over 1,296 rows.")
    return output


def model_task_effects(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = [
        row
        for row in rows
        if row["variant_id"] == PRIMARY_VARIANT
        and row["condition"] in {"B", "F", "S"}
        and row["model_slot_id"] in PROVIDER_FAMILY
    ]
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        key = (row["paper_id"], row["task_id"], row["domain"], row["model_slot_id"])
        grouped[key].append(row)

    output = []
    for key in sorted(grouped):
        paper_id, task_id, domain, model = key
        group = grouped[key]
        by_condition = {
            condition: [row for row in group if row["condition"] == condition]
            for condition in ("B", "F", "S")
        }
        if any(len(values) != 6 for values in by_condition.values()):
            raise ValueError(f"Model task cell {key} does not have 6 B/F/S blocks.")
        row: dict[str, Any] = {
            "paper_id": paper_id,
            "task_id": task_id,
            "domain": domain,
            "model_slot_id": model,
            "paired_blocks": 6,
        }
        for endpoint in ENDPOINTS:
            condition_values = {
                condition: condition_mean(by_condition[condition], endpoint)
                for condition in ("B", "F", "S")
            }
            for condition in ("B", "F", "S"):
                row[f"{condition}_{endpoint}"] = condition_values[condition]
            for contrast, left, right in CONTRASTS:
                row[f"{contrast}_{endpoint}"] = (
                    condition_values[left] - condition_values[right]
                )
        output.append(row)

    counts = Counter(row["model_slot_id"] for row in output)
    expected = {model: 4 for model in PROVIDER_FAMILY}
    expected["deepseek_primary"] = 24
    if counts != expected:
        raise ValueError(f"Unexpected model-task coverage: {dict(counts)}")
    return output


def model_summaries(task_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for model in sorted(PROVIDER_FAMILY):
        rows = [
            row
            for row in task_rows
            if row["model_slot_id"] == model and row["task_id"] in ANCHOR_TASKS
        ]
        if len(rows) != 4:
            raise ValueError(f"Expected four anchor tasks for model {model}.")
        result: dict[str, Any] = {
            "model_slot_id": model,
            "provider_family": PROVIDER_FAMILY[model],
            "anchor_paper_n": 4,
            "anchor_task_n": 4,
            "paired_blocks_per_task": 6,
            "anchor_task_ids": json.dumps(list(ANCHOR_TASKS), separators=(",", ":")),
        }
        for contrast, _, _ in CONTRASTS:
            for endpoint in ENDPOINTS:
                key = f"{contrast}_{endpoint}"
                values = [float(row[key]) for row in rows]
                counts = sign_counts(values)
                result[key] = mean(values)
                result[f"{key}_task_positive"] = counts["positive"]
                result[f"{key}_task_negative"] = counts["negative"]
                result[f"{key}_task_zero"] = counts["zero"]
        output.append(result)
    return output


def primary_domain_effects(paper_effects_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with paper_effects_path.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle))
    selected = [
        row for row in all_rows if row["contrast"] in {item[0] for item in CONTRASTS}
    ]
    output = []
    for domain in sorted({row["domain"] for row in selected}):
        result: dict[str, Any] = {"domain": domain, "paper_n": 3, "task_n": 6}
        for contrast, _, _ in CONTRASTS:
            for endpoint in ENDPOINTS:
                values = [
                    float(row["effect"])
                    for row in selected
                    if row["domain"] == domain
                    and row["contrast"] == contrast
                    and row["endpoint"] == endpoint
                ]
                if len(values) != 3:
                    raise ValueError(f"Expected three papers for {domain}, {contrast}, {endpoint}.")
                result[f"{contrast}_{endpoint}"] = mean(values)
        output.append(result)
    return output, selected


def registry_effects(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    primary = [
        row
        for row in rows
        if row["model_slot_id"] == "deepseek_primary"
        and row["variant_id"] == PRIMARY_VARIANT
        and row["execution_family"] == "primary"
    ]
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in primary:
        grouped[(row["paper_id"], row["task_id"], row["domain"], row["registry_id"])].append(row)
    task_rows = []
    for key in sorted(grouped):
        paper_id, task_id, domain, registry_id = key
        group = grouped[key]
        by_condition = {
            condition: [row for row in group if row["condition"] == condition]
            for condition in ("B", "F", "S")
        }
        if any(len(values) != 3 for values in by_condition.values()):
            raise ValueError(f"Registry task cell {key} lacks three blocks per condition.")
        result: dict[str, Any] = {
            "paper_id": paper_id,
            "task_id": task_id,
            "domain": domain,
            "registry_id": registry_id,
            "paired_blocks": 3,
        }
        for endpoint in ENDPOINTS:
            condition_values = {
                condition: condition_mean(by_condition[condition], endpoint)
                for condition in ("B", "F", "S")
            }
            for contrast, left, right in CONTRASTS:
                result[f"{contrast}_{endpoint}"] = (
                    condition_values[left] - condition_values[right]
                )
        task_rows.append(result)
    if len(task_rows) != 48:
        raise ValueError(f"Expected 48 registry-task rows, got {len(task_rows)}.")

    summaries = []
    for registry_id in ("A", "B"):
        selected = [row for row in task_rows if row["registry_id"] == registry_id]
        result: dict[str, Any] = {
            "registry_id": registry_id,
            "paper_n": 12,
            "task_n": 24,
        }
        for contrast, _, _ in CONTRASTS:
            for endpoint in ENDPOINTS:
                key = f"{contrast}_{endpoint}"
                result[key] = mean(float(row[key]) for row in selected)
        summaries.append(result)
    return task_rows, summaries


def reducer_effects(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    task_rows = []
    for family, variant, candidate_condition in REDUCER_SPECS:
        selected = [
            row
            for row in rows
            if row["model_slot_id"] == "deepseek_primary"
            and row["execution_family"] == family
            and row["variant_id"] == variant
            and row["task_id"] in ANCHOR_TASKS
            and row["condition"] in {candidate_condition, "F"}
        ]
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in selected:
            grouped[(row["paper_id"], row["task_id"], row["domain"])].append(row)
        if len(grouped) != 4:
            raise ValueError(f"Reducer {family}/{variant} lacks four anchor tasks.")
        for key in sorted(grouped):
            paper_id, task_id, domain = key
            group = grouped[key]
            candidate = [row for row in group if row["condition"] == candidate_condition]
            full = [row for row in group if row["condition"] == "F"]
            if len(candidate) != 6 or len(full) != 6:
                raise ValueError(f"Reducer task {family}/{variant}/{task_id} is not 6-paired.")
            candidate_success = condition_mean(candidate, "operational_success")
            full_success = condition_mean(full, "operational_success")
            candidate_score = condition_mean(candidate, "private_score")
            full_score = condition_mean(full, "private_score")
            task_rows.append(
                {
                    "paper_id": paper_id,
                    "task_id": task_id,
                    "domain": domain,
                    "execution_family": family,
                    "variant_id": variant,
                    "model_slot_id": "deepseek_primary",
                    "paired_blocks": 6,
                    "candidate_minus_F_operational_success": candidate_success - full_success,
                    "candidate_minus_F_private_score": candidate_score - full_score,
                    "candidate_success_rate": candidate_success,
                    "F_success_rate": full_success,
                    "candidate_score_mean": candidate_score,
                    "F_score_mean": full_score,
                }
            )
    if len(task_rows) != 24:
        raise ValueError(f"Expected 24 reducer-task rows, got {len(task_rows)}.")

    summaries = []
    for family, variant, _ in REDUCER_SPECS:
        selected = [
            row
            for row in task_rows
            if row["execution_family"] == family and row["variant_id"] == variant
        ]
        result: dict[str, Any] = {
            "execution_family": family,
            "variant_id": variant,
            "anchor_paper_n": 4,
            "anchor_task_n": 4,
            "paired_blocks_per_task": 6,
        }
        for key in (
            "candidate_minus_F_operational_success",
            "candidate_minus_F_private_score",
            "candidate_success_rate",
            "F_success_rate",
            "candidate_score_mean",
            "F_score_mean",
        ):
            result[key] = mean(float(row[key]) for row in selected)
        summaries.append(result)
    return task_rows, summaries


def equal_domain_effect(rows: list[dict[str, Any]]) -> float:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["domain"]].append(float(row["effect"]))
    return mean(mean(values) for _, values in sorted(grouped.items()))


def primary_single_driver_diagnostics(paper_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for contrast, _, _ in CONTRASTS:
        for endpoint in ENDPOINTS:
            selected = [
                row
                for row in paper_rows
                if row["contrast"] == contrast and row["endpoint"] == endpoint
            ]
            values = [float(row["effect"]) for row in selected]
            full = equal_domain_effect(selected)
            loo = []
            for omitted in sorted(row["paper_id"] for row in selected):
                kept = [row for row in selected if row["paper_id"] != omitted]
                loo.append(
                    {
                        "omitted_paper_id": omitted,
                        "effect": equal_domain_effect(kept),
                    }
                )
            signs = sign_counts(values)
            output.append(
                {
                    "contrast": contrast,
                    "endpoint": endpoint,
                    "full_effect": full,
                    "largest_absolute_paper_effect": max(abs(value) for value in values),
                    "paper_positive": signs["positive"],
                    "paper_negative": signs["negative"],
                    "paper_zero": signs["zero"],
                    "leave_one_paper_out": loo,
                    "loo_min": min(row["effect"] for row in loo),
                    "loo_max": max(row["effect"] for row in loo),
                    "sign_reversals": sum(
                        1 for row in loo if full * float(row["effect"]) < -TOLERANCE
                    ),
                }
            )
    return output


def anchor_driver_diagnostics(
    model_tasks: list[dict[str, Any]], model_effects: list[dict[str, Any]]
) -> dict[str, Any]:
    model_output = []
    task_output = []
    for contrast, _, _ in CONTRASTS:
        for endpoint in ENDPOINTS:
            key = f"{contrast}_{endpoint}"
            model_values = {
                row["model_slot_id"]: float(row[key]) for row in model_effects
            }
            full_model_mean = mean(model_values.values())
            model_loo = [
                {
                    "omitted_model_slot_id": model,
                    "effect": mean(value for name, value in model_values.items() if name != model),
                }
                for model in sorted(model_values)
            ]
            model_signs = sign_counts(model_values.values())
            model_output.append(
                {
                    "contrast": contrast,
                    "endpoint": endpoint,
                    "equal_model_effect": full_model_mean,
                    "model_positive": model_signs["positive"],
                    "model_negative": model_signs["negative"],
                    "model_zero": model_signs["zero"],
                    "leave_one_model_out": model_loo,
                    "loo_min": min(row["effect"] for row in model_loo),
                    "loo_max": max(row["effect"] for row in model_loo),
                    "sign_reversals": sum(
                        1
                        for row in model_loo
                        if full_model_mean * float(row["effect"]) < -TOLERANCE
                    ),
                }
            )

            by_task: dict[str, list[float]] = defaultdict(list)
            for row in model_tasks:
                if row["task_id"] in ANCHOR_TASKS:
                    by_task[row["task_id"]].append(float(row[key]))
            task_values = {task: mean(values) for task, values in sorted(by_task.items())}
            full_task_mean = mean(task_values.values())
            task_loo = [
                {
                    "omitted_task_id": task,
                    "effect": mean(value for name, value in task_values.items() if name != task),
                }
                for task in sorted(task_values)
            ]
            task_signs = sign_counts(task_values.values())
            task_output.append(
                {
                    "contrast": contrast,
                    "endpoint": endpoint,
                    "equal_anchor_task_effect": full_task_mean,
                    "task_positive": task_signs["positive"],
                    "task_negative": task_signs["negative"],
                    "task_zero": task_signs["zero"],
                    "leave_one_task_out": task_loo,
                    "loo_min": min(row["effect"] for row in task_loo),
                    "loo_max": max(row["effect"] for row in task_loo),
                    "sign_reversals": sum(
                        1
                        for row in task_loo
                        if full_task_mean * float(row["effect"]) < -TOLERANCE
                    ),
                }
            )
    return {
        "model_leave_one_out": model_output,
        "anchor_task_leave_one_out": task_output,
    }


def fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        raise ValueError("Cannot infer fields from empty rows.")
    return list(rows[0])


def relative_reference(path: Path) -> str:
    try:
        return path.resolve().relative_to(ANALYSIS_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def analyze(input_path: Path, paper_effects_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_overlay(input_path)
    cells = heatmap_cells(rows)
    model_tasks = model_task_effects(rows)
    model_effects = model_summaries(model_tasks)
    domain_effects, paper_rows = primary_domain_effects(paper_effects_path)
    registry_tasks, registry_summaries = registry_effects(rows)
    reducer_tasks, reducer_summaries = reducer_effects(rows)
    primary_diagnostics = primary_single_driver_diagnostics(paper_rows)
    anchor_diagnostics = anchor_driver_diagnostics(model_tasks, model_effects)

    named_rows = {
        "heatmap.csv": cells,
        "model_tasks.csv": model_tasks,
        "model_summary.csv": model_effects,
        "domains.csv": domain_effects,
        "primary_papers.csv": paper_rows,
        "registry_tasks.csv": registry_tasks,
        "registry_summary.csv": registry_summaries,
        "reducer_tasks.csv": reducer_tasks,
        "reducer_summary.csv": reducer_summaries,
    }
    for name, csv_rows in named_rows.items():
        write_csv(output_dir / name, fieldnames(csv_rows), csv_rows)

    coverage = {
        "rows": len(rows),
        "papers": len({row["paper_id"] for row in rows}),
        "paper_tasks": len({(row["paper_id"], row["task_id"]) for row in rows}),
        "heatmap_cells": len(cells),
        "conditions": dict(sorted(Counter(row["condition"] for row in rows).items())),
        "domains": dict(sorted(Counter(row["domain"] for row in rows).items())),
        "models": dict(sorted(Counter(row["model_slot_id"] for row in rows).items())),
        "execution_families": dict(
            sorted(Counter(row["execution_family"] for row in rows).items())
        ),
    }
    summary = {
        "schema_version": "effectslice-generalization-interactions.v1",
        "status": "verified_forward_analysis",
        "coverage": coverage,
        "primary_scope": {
            "papers": 12,
            "tasks": 24,
            "model_slot_id": "deepseek_primary",
            "independent_unit": "paper",
        },
        "model_reducer_scope": {
            "anchor_papers": 4,
            "anchor_tasks": 4,
            "models": 6,
            "paired_blocks_per_task": 6,
            "anchor_task_ids": list(ANCHOR_TASKS),
        },
        "model_effects": model_effects,
        "primary_domain_effects": domain_effects,
        "registry_effects": registry_summaries,
        "reducer_effects": reducer_summaries,
        "primary_single_driver_diagnostics": primary_diagnostics,
        "anchor_driver_diagnostics": anchor_diagnostics,
        "claim_diagnostics": {
            "F_minus_B_success_positive_models": sum(
                row["F_minus_B_operational_success"] > TOLERANCE for row in model_effects
            ),
            "S_minus_B_success_positive_models": sum(
                row["S_minus_B_operational_success"] > TOLERANCE for row in model_effects
            ),
            "S_minus_F_success_positive_models": sum(
                row["S_minus_F_operational_success"] > TOLERANCE for row in model_effects
            ),
            "S_minus_F_success_negative_models": sum(
                row["S_minus_F_operational_success"] < -TOLERANCE for row in model_effects
            ),
            "S_minus_F_success_zero_models": sum(
                abs(row["S_minus_F_operational_success"]) <= TOLERANCE
                for row in model_effects
            ),
        },
        "limitations": [
            "Primary inference is registered for DeepSeek across 24 paper-tasks; model and reducer robustness is restricted to four common anchor tasks, one per domain.",
            "Each anchor task has six paired blocks, but only four independent anchor papers support model/reducer comparisons.",
            "Provider-family effects are confounded with model identity and are descriptive.",
            "Leave-one-model and leave-one-anchor-task analyses are sensitivity diagnostics, not population inference.",
        ],
    }
    write_json(output_dir / "summary.json", summary)

    output_names = sorted([*named_rows, "summary.json"])
    manifest = {
        "schema_version": "effectslice-forward-analysis-manifest.v1",
        "section": "02_generalization",
        "runtime": {"python": platform.python_version(), "dependencies": "standard library"},
        "inputs": {
            "terminal_overlay": {
                "path": relative_reference(input_path),
                "sha256": sha256(input_path),
            },
            "primary_paper_effects": {
                "path": relative_reference(paper_effects_path),
                "sha256": sha256(paper_effects_path),
            },
        },
        "outputs": {name: {"sha256": sha256(output_dir / name)} for name in output_names},
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--paper-effects", type=Path, default=DEFAULT_PAPER_EFFECTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.input, args.paper_effects, args.output_dir)


if __name__ == "__main__":
    main()
