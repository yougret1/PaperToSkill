from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_OUTPUT = HERE / "outputs"
BOOTSTRAP_SEED = 20260721
BOOTSTRAP_REPLICATES = 10_000
PRIMARY_FILTER = {
    "model_slot_id": "deepseek_primary",
    "variant_id": "primary_dag_ratio_60_v1",
    "execution_family": "primary",
}
CONTRASTS = (
    ("F_minus_B", "F", "B"),
    ("S_minus_B", "S", "B"),
    ("S_minus_F", "S", "F"),
    ("F_minus_S", "F", "S"),
)
ENDPOINTS = ("operational_success", "private_score")
EXPECTED_DOMAINS = (
    "agent_tool_use",
    "data_analysis",
    "nlp",
    "software_engineering",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_primary_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    overlay = json.loads(path.read_text(encoding="utf-8"))
    records = overlay["records"]
    indices = [int(row["global_sequence_index"]) for row in records]
    if len(records) != 1296 or sorted(indices) != list(range(1, 1297)):
        raise ValueError("The analysis overlay must contain unique rows 1..1296.")
    if len(set(indices)) != 1296:
        raise ValueError("Duplicate global sequence indices detected.")
    successes = sum(bool(row["operational_success"]) for row in records)
    if successes != 383:
        raise ValueError(f"Expected 383 operational successes, observed {successes}.")

    primary = [
        row
        for row in records
        if all(row.get(key) == value for key, value in PRIMARY_FILTER.items())
    ]
    if len(primary) != 432:
        raise ValueError(f"Expected 432 primary rows, observed {len(primary)}.")
    if Counter(row["condition"] for row in primary) != {"B": 144, "F": 144, "S": 144}:
        raise ValueError("Primary B/F/S condition counts are not 144 each.")
    return overlay, primary


def validate_design(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cell_counts = Counter(
        (row["paper_id"], row["task_id"], row["block_id"], row["condition"])
        for row in rows
    )
    bad_cells = {key: value for key, value in cell_counts.items() if value != 1}
    if bad_cells:
        raise ValueError(f"Primary paired-cell multiplicity failure: {bad_cells}")

    papers = sorted({row["paper_id"] for row in rows})
    tasks = sorted({row["task_id"] for row in rows})
    domains = sorted({row["domain"] for row in rows})
    if len(papers) != 12 or len(tasks) != 24 or tuple(domains) != EXPECTED_DOMAINS:
        raise ValueError(
            f"Expected 12 papers, 24 tasks, and four domains; got "
            f"{len(papers)}, {len(tasks)}, {domains}."
        )

    paper_tasks: dict[str, set[str]] = defaultdict(set)
    task_blocks: dict[str, set[str]] = defaultdict(set)
    paper_domains: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        paper_tasks[row["paper_id"]].add(row["task_id"])
        task_blocks[row["task_id"]].add(row["block_id"])
        paper_domains[row["paper_id"]].add(row["domain"])
    if any(len(task_ids) != 2 for task_ids in paper_tasks.values()):
        raise ValueError("Every paper must own exactly two nested tasks.")
    if any(len(block_ids) != 6 for block_ids in task_blocks.values()):
        raise ValueError("Every task must own exactly six paired blocks.")
    if any(len(domain_ids) != 1 for domain_ids in paper_domains.values()):
        raise ValueError("Every paper must map to exactly one domain.")

    domain_papers: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        domain_papers[row["domain"]].add(row["paper_id"])
    if {key: len(value) for key, value in domain_papers.items()} != {
        domain: 3 for domain in EXPECTED_DOMAINS
    }:
        raise ValueError("The four domains must contain three papers each.")

    return {
        "paper_count": len(papers),
        "task_count": len(tasks),
        "domain_count": len(domains),
        "papers_per_domain": 3,
        "tasks_per_paper": 2,
        "blocks_per_task": 6,
        "conditions": {"B": 144, "F": 144, "S": 144},
        "paired_cells": len(cell_counts),
    }


def endpoint_value(row: dict[str, Any], endpoint: str) -> float:
    value = row[endpoint]
    if value is None:
        raise ValueError(f"Missing {endpoint} for row {row['global_sequence_index']}.")
    return float(bool(value)) if endpoint == "operational_success" else float(value)


def build_effect_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    indexed: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    task_metadata: dict[str, tuple[str, str]] = {}
    for row in rows:
        key = (row["paper_id"], row["task_id"], row["block_id"], row["condition"])
        indexed[key] = row
        task_metadata[row["task_id"]] = (row["paper_id"], row["domain"])

    task_rows: list[dict[str, Any]] = []
    task_effect_lookup: dict[tuple[str, str, str], float] = {}
    for task_id in sorted(task_metadata):
        paper_id, domain = task_metadata[task_id]
        block_ids = sorted(
            {
                block_id
                for candidate_paper, candidate_task, block_id, _ in indexed
                if candidate_paper == paper_id and candidate_task == task_id
            }
        )
        for contrast, left, right in CONTRASTS:
            for endpoint in ENDPOINTS:
                block_effects = [
                    endpoint_value(indexed[(paper_id, task_id, block_id, left)], endpoint)
                    - endpoint_value(indexed[(paper_id, task_id, block_id, right)], endpoint)
                    for block_id in block_ids
                ]
                effect = float(sum(block_effects) / len(block_effects))
                task_effect_lookup[(task_id, contrast, endpoint)] = effect
                task_rows.append(
                    {
                        "paper_id": paper_id,
                        "domain": domain,
                        "task_id": task_id,
                        "contrast": contrast,
                        "endpoint": endpoint,
                        "effect": effect,
                        "registered_pairs": len(block_ids),
                        "valid_pairs": len(block_effects),
                        "raw_block_min": min(block_effects),
                        "raw_block_max": max(block_effects),
                    }
                )

    paper_to_tasks: dict[str, list[str]] = defaultdict(list)
    paper_to_domain: dict[str, str] = {}
    for task_id, (paper_id, domain) in task_metadata.items():
        paper_to_tasks[paper_id].append(task_id)
        paper_to_domain[paper_id] = domain

    paper_rows: list[dict[str, Any]] = []
    for paper_id in sorted(paper_to_tasks):
        task_ids = sorted(paper_to_tasks[paper_id])
        for contrast, _, _ in CONTRASTS:
            for endpoint in ENDPOINTS:
                task_effects = [
                    task_effect_lookup[(task_id, contrast, endpoint)]
                    for task_id in task_ids
                ]
                paper_rows.append(
                    {
                        "paper_id": paper_id,
                        "domain": paper_to_domain[paper_id],
                        "contrast": contrast,
                        "endpoint": endpoint,
                        "task_ids": json.dumps(task_ids, separators=(",", ":")),
                        "task_effects": json.dumps(task_effects, separators=(",", ":")),
                        "effect": float(sum(task_effects) / len(task_effects)),
                        "registered_pairs": 12,
                        "valid_pairs": 12,
                        "raw_block_min": min(
                            row["raw_block_min"]
                            for row in task_rows
                            if row["paper_id"] == paper_id
                            and row["contrast"] == contrast
                            and row["endpoint"] == endpoint
                        ),
                        "raw_block_max": max(
                            row["raw_block_max"]
                            for row in task_rows
                            if row["paper_id"] == paper_id
                            and row["contrast"] == contrast
                            and row["endpoint"] == endpoint
                        ),
                    }
                )
    return task_rows, paper_rows


def summarize(
    paper_rows: list[dict[str, Any]], contrast: str, endpoint: str
) -> dict[str, Any]:
    selected = [
        row
        for row in paper_rows
        if row["contrast"] == contrast and row["endpoint"] == endpoint
    ]
    by_domain: dict[str, list[float]] = defaultdict(list)
    for row in selected:
        by_domain[row["domain"]].append(float(row["effect"]))
    domain_effects = {
        domain: float(sum(by_domain[domain]) / len(by_domain[domain]))
        for domain in EXPECTED_DOMAINS
    }
    overall = float(sum(domain_effects.values()) / len(domain_effects))

    rng = random.Random(BOOTSTRAP_SEED)
    samples = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    domain_arrays = [np.asarray(by_domain[domain], dtype=float) for domain in EXPECTED_DOMAINS]
    for replicate in range(BOOTSTRAP_REPLICATES):
        sampled_domain_means = []
        for values in domain_arrays:
            indices = [rng.randrange(len(values)) for _ in range(len(values))]
            sampled_domain_means.append(float(values[indices].mean()))
        samples[replicate] = float(np.mean(sampled_domain_means))
    low, high = np.quantile(samples, [0.025, 0.975]).tolist()

    return {
        "contrast": contrast,
        "endpoint": endpoint,
        "paper_n": 12,
        "task_n": 24,
        "registered_pairs": 144,
        "valid_pairs": 144,
        "domain_effects": domain_effects,
        "overall_equal_domain_effect": overall,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_ci95_low": float(low),
        "bootstrap_ci95_high": float(high),
        "bootstrap_interpretation": (
            "registered-benchmark sensitivity interval, not a population confidence interval"
        ),
    }


def analyze(input_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _, primary_rows = load_primary_rows(input_path)
    design = validate_design(primary_rows)
    task_rows, paper_rows = build_effect_rows(primary_rows)

    task_fields = [
        "paper_id",
        "domain",
        "task_id",
        "contrast",
        "endpoint",
        "effect",
        "registered_pairs",
        "valid_pairs",
        "raw_block_min",
        "raw_block_max",
    ]
    paper_fields = [
        "paper_id",
        "domain",
        "contrast",
        "endpoint",
        "task_ids",
        "task_effects",
        "effect",
        "registered_pairs",
        "valid_pairs",
        "raw_block_min",
        "raw_block_max",
    ]
    write_csv(output_dir / "task_effects.csv", task_fields, task_rows)
    write_csv(output_dir / "paper_effects.csv", paper_fields, paper_rows)
    write_csv(output_dir / "forest_data.csv", paper_fields, paper_rows)

    summaries = [
        summarize(paper_rows, contrast, endpoint)
        for contrast, _, _ in CONTRASTS
        for endpoint in ENDPOINTS
    ]
    result = {
        "schema_version": "effectslice-primary-effects.v1",
        "status": "verified_forward_analysis",
        "analysis_contract": {
            "independent_unit": "paper",
            "tasks_nested_per_paper": 2,
            "paired_blocks_per_task": 6,
            "domain_weighting": "equal across four domains",
            "primary_model_slot": PRIMARY_FILTER["model_slot_id"],
            "primary_variant": PRIMARY_FILTER["variant_id"],
            "primary_execution_family": PRIMARY_FILTER["execution_family"],
        },
        "design_verification": design,
        "summaries": summaries,
    }
    write_json(output_dir / "primary_effects.json", result)

    output_names = (
        "forest_data.csv",
        "paper_effects.csv",
        "primary_effects.json",
        "task_effects.csv",
    )
    try:
        input_reference = input_path.resolve().relative_to(HERE.parent.resolve()).as_posix()
    except ValueError:
        input_reference = str(input_path.resolve())
    manifest = {
        "schema_version": "effectslice-forward-analysis-manifest.v1",
        "section": "01_primary_effects",
        "input": {
            "path": input_reference,
            "sha256": sha256(input_path),
            "row_count": 1296,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "parameters": {
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_rng": "python.random.Random reinitialized per summary",
            "quantile_method": "numpy.quantile default linear interpolation",
            "primary_filter": PRIMARY_FILTER,
        },
        "outputs": {
            name: {"sha256": sha256(output_dir / name)} for name in output_names
        },
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.input, args.output_dir)


if __name__ == "__main__":
    main()
