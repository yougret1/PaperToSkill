from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from stage23_analysis import analyze as frozen_analyze


ROOT = Path(__file__).resolve().parent
DEFAULT_SUCCESSOR = ROOT / "format_conformance_successor_2026-07-23"
DEFAULT_RUN_DIR = ROOT / "remote_execution_v3_2026-07-23"
DEFAULT_OUTPUT_DIR = ROOT / "analysis_v1_2026-07-24"
CONTRASTS = {
    "F_minus_B": ("F", "B"),
    "S_minus_B": ("S", "B"),
    "S_minus_F": ("S", "F"),
}
PRIMARY_THRESHOLDS = {
    "maximum_B_successes": 1,
    "minimum_F_successes": 5,
    "minimum_S_successes": 5,
    "minimum_margin_blocks": 5,
}
REGISTRY_THRESHOLDS = {
    "maximum_B_successes": 1,
    "minimum_F_successes": 2,
    "minimum_S_successes": 2,
    "minimum_margin_blocks": 2,
}


class AggregateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AggregateError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_bytes(value) + b"\n")
    temporary.replace(path)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    temporary.replace(path)


def mean(values: Iterable[float]) -> float:
    materialized = list(values)
    require(bool(materialized), "cannot average an empty sequence")
    return sum(materialized) / len(materialized)


def percentile(values: list[float], probability: float) -> float:
    require(bool(values), "cannot take percentile of an empty sequence")
    require(0.0 <= probability <= 1.0, "invalid percentile probability")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def is_valid(row: dict[str, Any]) -> bool:
    score = row.get("private_score")
    return (
        row.get("row_valid") is True
        and isinstance(score, (int, float))
        and not isinstance(score, bool)
        and math.isfinite(float(score))
        and 0.0 <= float(score) <= 1.0
        and isinstance(row.get("condition_success"), bool)
    )


def group_by_condition(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["condition"])].append(row)
    for values in grouped.values():
        values.sort(key=lambda item: int(item["block_id"]))
    return grouped


def block_map(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    mapped = {int(row["block_id"]): row for row in rows}
    require(len(mapped) == len(rows), "duplicate block within condition")
    return mapped


def decision_state(
    rows: list[dict[str, Any]],
    *,
    thresholds: dict[str, int] | None = None,
    margin_tolerance: float = 0.05,
    apply_registry_gates: bool = True,
) -> dict[str, Any]:
    thresholds = thresholds or PRIMARY_THRESHOLDS
    grouped = group_by_condition(rows)
    if set(grouped) != {"B", "F", "S"} or any(
        len(grouped[key]) != 6 for key in ("B", "F", "S")
    ):
        return {"state": "Invalid", "reasons": ["incomplete_schedule"]}
    if any(not is_valid(row) for values in grouped.values() for row in values):
        invalid = [
            str(row["execution_id"])
            for values in grouped.values()
            for row in values
            if not is_valid(row)
        ]
        return {
            "state": "Invalid",
            "reasons": ["invalid_terminal_row"],
            "invalid_execution_ids": invalid,
        }
    successes = {
        key: sum(row["condition_success"] is True for row in grouped[key])
        for key in ("B", "F", "S")
    }
    by_block = {key: block_map(grouped[key]) for key in ("B", "F", "S")}
    margins = {
        block: float(by_block["S"][block]["private_score"])
        >= float(by_block["F"][block]["private_score"]) - margin_tolerance
        for block in range(1, 7)
    }
    reason_buckets: dict[str, list[str]] = {
        "full": [],
        "baseline": [],
        "slice": [],
        "margin": [],
    }
    if successes["B"] > thresholds["maximum_B_successes"]:
        reason_buckets["baseline"].append("B_sensitivity")
    if successes["F"] < thresholds["minimum_F_successes"]:
        reason_buckets["full"].append("F_insufficient")
    if successes["S"] < thresholds["minimum_S_successes"]:
        reason_buckets["slice"].append("S_insufficient")
    if sum(margins.values()) < thresholds["minimum_margin_blocks"]:
        reason_buckets["margin"].append("paired_margin")
    if apply_registry_gates:
        for registry, blocks in (("A", (1, 2, 3)), ("B", (4, 5, 6))):
            local = {
                condition: sum(
                    by_block[condition][block]["condition_success"] is True
                    for block in blocks
                )
                for condition in ("B", "F", "S")
            }
            if local["B"] > REGISTRY_THRESHOLDS["maximum_B_successes"]:
                reason_buckets["baseline"].append(f"{registry}_B_sensitivity")
            if local["F"] < REGISTRY_THRESHOLDS["minimum_F_successes"]:
                reason_buckets["full"].append(f"{registry}_F_insufficient")
            if local["S"] < REGISTRY_THRESHOLDS["minimum_S_successes"]:
                reason_buckets["slice"].append(f"{registry}_S_insufficient")
            if sum(margins[block] for block in blocks) < REGISTRY_THRESHOLDS[
                "minimum_margin_blocks"
            ]:
                reason_buckets["margin"].append(f"{registry}_paired_margin")
    reasons = [
        reason
        for category in ("full", "baseline", "slice", "margin")
        for reason in reason_buckets[category]
    ]
    return {
        "state": "Admit" if not reasons else "Reject",
        "reasons": reasons,
        "primary_reject_reason": reasons[0] if reasons else None,
        "successes": successes,
        "margin_blocks": sum(margins.values()),
        "margin_by_block": {str(key): value for key, value in margins.items()},
    }


def pair_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped = group_by_condition(rows)
    if set(grouped) != {"F", "C"} or any(
        len(grouped[key]) != 6 for key in ("F", "C")
    ):
        return {"state": "Invalid", "reasons": ["incomplete_schedule"]}
    if any(not is_valid(row) for values in grouped.values() for row in values):
        return {"state": "Invalid", "reasons": ["invalid_terminal_row"]}
    mapped = {key: block_map(grouped[key]) for key in ("F", "C")}
    successes = {
        key: sum(row["condition_success"] is True for row in grouped[key])
        for key in ("F", "C")
    }
    margins = {
        block: float(mapped["C"][block]["private_score"])
        >= float(mapped["F"][block]["private_score"]) - 0.05
        for block in range(1, 7)
    }
    reasons: list[str] = []
    if successes["F"] < 5:
        reasons.append("F_insufficient")
    if successes["C"] < 5:
        reasons.append("candidate_insufficient")
    if sum(margins.values()) < 5:
        reasons.append("paired_margin")
    for registry, blocks in (("A", (1, 2, 3)), ("B", (4, 5, 6))):
        if sum(mapped["F"][block]["condition_success"] is True for block in blocks) < 2:
            reasons.append(f"{registry}_F_insufficient")
        if sum(mapped["C"][block]["condition_success"] is True for block in blocks) < 2:
            reasons.append(f"{registry}_candidate_insufficient")
        if sum(margins[block] for block in blocks) < 2:
            reasons.append(f"{registry}_paired_margin")
    return {
        "state": "PairPass" if not reasons else "PairFail",
        "reasons": reasons,
        "successes": successes,
        "margin_blocks": sum(margins.values()),
    }


def load_rows(successor: Path, run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    schedule_path = successor / "global_remote_schedule.json"
    schedule_document = load_json(schedule_path)
    schedule = schedule_document["rows"]
    require(len(schedule) == 1296, "registered schedule row count changed")
    row_dir = run_dir / "rows"
    row_files = {path.stem: path for path in row_dir.glob("*.json")}
    expected_ids = [str(row["execution_id"]) for row in schedule]
    require(len(row_files) == 1296, "terminal row count is not 1296")
    require(set(row_files) == set(expected_ids), "terminal rows do not match schedule")
    merged: list[dict[str, Any]] = []
    row_hashes: list[dict[str, str]] = []
    for schedule_row in schedule:
        execution_id = str(schedule_row["execution_id"])
        result_path = row_files[execution_id]
        result = load_json(result_path)
        require(result.get("execution_id") == execution_id, "row execution ID changed")
        merged.append({**schedule_row, **result})
        row_hashes.append({"execution_id": execution_id, "sha256": sha256_path(result_path)})
    manifest = {
        "schedule_sha256": sha256_path(schedule_path),
        "run_manifest_sha256": sha256_path(run_dir / "run_manifest.json"),
        "row_hash_manifest_sha256": hashlib.sha256(canonical_bytes(row_hashes)).hexdigest(),
        "row_count": len(merged),
    }
    return merged, manifest


def endpoint(row: dict[str, Any], outcome: str) -> float | None:
    if not is_valid(row):
        return None
    if outcome == "success":
        return 1.0 if row["condition_success"] is True else 0.0
    if outcome == "score":
        return float(row["private_score"])
    raise AggregateError(f"unknown outcome: {outcome}")


def identified_block(x: float | None, y: float | None) -> tuple[float, float, float | None]:
    if x is not None and y is not None:
        difference = x - y
        return difference, difference, difference
    if x is not None:
        return x - 1.0, x, None
    if y is not None:
        return -y, 1.0 - y, None
    return -1.0, 1.0, None


def task_effect(
    rows: list[dict[str, Any]], outcome: str, contrast: str
) -> dict[str, Any]:
    left, right = CONTRASTS[contrast]
    grouped = group_by_condition(rows)
    require(left in grouped and right in grouped, "missing primary contrast condition")
    left_rows = block_map(grouped[left])
    right_rows = block_map(grouped[right])
    blocks: list[dict[str, Any]] = []
    for block in range(1, 7):
        x = endpoint(left_rows[block], outcome)
        y = endpoint(right_rows[block], outcome)
        lower, upper, observed = identified_block(x, y)
        blocks.append(
            {
                "block_id": block,
                "left": x,
                "right": y,
                "observed": observed,
                "lower": lower,
                "upper": upper,
            }
        )
    observed_values = [float(item["observed"]) for item in blocks if item["observed"] is not None]
    return {
        "valid_pairs": len(observed_values),
        "registered_pairs": 6,
        "observed": mean(observed_values) if observed_values else None,
        "observed_median": statistics.median(observed_values) if observed_values else None,
        "observed_minimum": min(observed_values) if observed_values else None,
        "observed_maximum": max(observed_values) if observed_values else None,
        "lower": mean(float(item["lower"]) for item in blocks),
        "upper": mean(float(item["upper"]) for item in blocks),
        "blocks": blocks,
    }


def aggregate_effects(primary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    task_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in primary_rows:
        task_groups[str(row["task_id"])].append(row)
    paper_tasks: dict[str, list[str]] = defaultdict(list)
    paper_domain: dict[str, str] = {}
    for task_id, rows in task_groups.items():
        paper_id = str(rows[0]["paper_id"])
        paper_tasks[paper_id].append(task_id)
        paper_domain[paper_id] = str(rows[0]["domain"])
    require(len(task_groups) == 24, "primary task count changed")
    require(len(paper_tasks) == 12, "primary paper count changed")
    require(all(len(tasks) == 2 for tasks in paper_tasks.values()), "paper task nesting changed")

    output: dict[str, Any] = {}
    for outcome in ("success", "score"):
        outcome_result: dict[str, Any] = {}
        for contrast in CONTRASTS:
            tasks = {
                task_id: task_effect(rows, outcome, contrast)
                for task_id, rows in sorted(task_groups.items())
            }
            papers: dict[str, dict[str, Any]] = {}
            for paper_id, task_ids in sorted(paper_tasks.items()):
                values = [tasks[task_id] for task_id in sorted(task_ids)]
                observed = (
                    mean(float(value["observed"]) for value in values)
                    if all(value["observed"] is not None for value in values)
                    else None
                )
                papers[paper_id] = {
                    "domain": paper_domain[paper_id],
                    "task_ids": sorted(task_ids),
                    "observed": observed,
                    "lower": mean(float(value["lower"]) for value in values),
                    "upper": mean(float(value["upper"]) for value in values),
                    "valid_pairs": sum(int(value["valid_pairs"]) for value in values),
                    "registered_pairs": 12,
                }
            by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for value in papers.values():
                by_domain[str(value["domain"])].append(value)
            require(set(by_domain) == {"nlp", "software_engineering", "data_analysis", "agent_tool_use"}, "domain registry changed")
            require(all(len(values) == 3 for values in by_domain.values()), "domain paper counts changed")
            domains = {
                domain: {
                    "papers": len(values),
                    "lower": mean(float(value["lower"]) for value in values),
                    "upper": mean(float(value["upper"]) for value in values),
                }
                for domain, values in sorted(by_domain.items())
            }
            defined = [float(value["observed"]) for value in papers.values() if value["observed"] is not None]
            overall = {
                "observed": mean(defined) if defined else None,
                "observed_papers": len(defined),
                "registered_papers": 12,
                "lower": mean(float(value["lower"]) for value in domains.values()),
                "upper": mean(float(value["upper"]) for value in domains.values()),
            }

            rng = random.Random(20260721)
            bootstrap_lower: list[float] = []
            bootstrap_upper: list[float] = []
            for _ in range(10000):
                domain_bounds: list[tuple[float, float]] = []
                for domain in sorted(by_domain):
                    values = by_domain[domain]
                    sampled = [values[rng.randrange(len(values))] for _ in values]
                    domain_bounds.append(
                        (
                            mean(float(value["lower"]) for value in sampled),
                            mean(float(value["upper"]) for value in sampled),
                        )
                    )
                bootstrap_lower.append(mean(value[0] for value in domain_bounds))
                bootstrap_upper.append(mean(value[1] for value in domain_bounds))
            bootstrap = {
                "seed": 20260721,
                "replicates": 10000,
                "lower_endpoint_percentile_95": [
                    percentile(bootstrap_lower, 0.025),
                    percentile(bootstrap_lower, 0.975),
                ],
                "upper_endpoint_percentile_95": [
                    percentile(bootstrap_upper, 0.025),
                    percentile(bootstrap_upper, 0.975),
                ],
                "scope": "registered-benchmark sensitivity; not a population confidence interval",
            }
            leave_one_out: list[dict[str, Any]] = []
            for omitted in sorted(papers):
                remaining_domains: list[tuple[float, float]] = []
                for domain in sorted(by_domain):
                    values = [
                        value
                        for paper_id, value in papers.items()
                        if value["domain"] == domain and paper_id != omitted
                    ]
                    remaining_domains.append(
                        (
                            mean(float(value["lower"]) for value in values),
                            mean(float(value["upper"]) for value in values),
                        )
                    )
                leave_one_out.append(
                    {
                        "omitted_paper_id": omitted,
                        "lower": mean(value[0] for value in remaining_domains),
                        "upper": mean(value[1] for value in remaining_domains),
                    }
                )
            outcome_result[contrast] = {
                "tasks": tasks,
                "papers": papers,
                "domains": domains,
                "overall": overall,
                "bootstrap": bootstrap,
                "leave_one_paper_out": leave_one_out,
            }
        output[outcome] = outcome_result
    return output


def primary_states(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in primary_rows:
        groups[str(row["task_id"])].append(row)
    states: list[dict[str, Any]] = []
    for task_id, rows in sorted(groups.items()):
        state = decision_state(rows)
        grouped = group_by_condition(rows)
        token_values = {
            condition: sorted({int(row["candidate_artifact_cl100k_tokens"]) for row in values})
            for condition, values in grouped.items()
        }
        require(all(len(values) == 1 for values in token_values.values()), "candidate token count changed across blocks")
        full_tokens = token_values["F"][0]
        slice_tokens = token_values["S"][0]
        states.append(
            {
                "domain": str(rows[0]["domain"]),
                "paper_id": str(rows[0]["paper_id"]),
                "task_id": task_id,
                **state,
                "B_valid": sum(is_valid(row) for row in grouped["B"]),
                "F_valid": sum(is_valid(row) for row in grouped["F"]),
                "S_valid": sum(is_valid(row) for row in grouped["S"]),
                "full_tokens": full_tokens,
                "slice_tokens": slice_tokens,
                "slice_token_ratio": slice_tokens / full_tokens,
            }
        )
    return states


def sla_sensitivity(primary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in primary_rows:
        groups[str(row["task_id"])].append(row)
    grid: list[dict[str, Any]] = []
    for maximum_b in (0, 1, 2):
        for minimum_f in (4, 5, 6):
            for minimum_s in (4, 5, 6):
                for margin in (0.0, 0.05, 0.1):
                    counts: Counter[str] = Counter()
                    task_values: dict[str, str] = {}
                    for task_id, rows in sorted(groups.items()):
                        state = decision_state(
                            rows,
                            thresholds={
                                "maximum_B_successes": maximum_b,
                                "minimum_F_successes": minimum_f,
                                "minimum_S_successes": minimum_s,
                                "minimum_margin_blocks": 5,
                            },
                            margin_tolerance=margin,
                            apply_registry_gates=True,
                        )["state"]
                        counts[state] += 1
                        task_values[task_id] = state
                    grid.append(
                        {
                            "maximum_B_successes": maximum_b,
                            "minimum_F_successes": minimum_f,
                            "minimum_S_successes": minimum_s,
                            "paired_margin": margin,
                            "state_counts": dict(sorted(counts.items())),
                            "task_states": task_values,
                        }
                    )
    leave_one_block: list[dict[str, Any]] = []
    for task_id, rows in sorted(groups.items()):
        full_invalid = sum(not is_valid(row) for row in rows)
        for omitted in range(1, 7):
            remaining = [row for row in rows if int(row["block_id"]) != omitted]
            grouped = group_by_condition(remaining)
            if any(not is_valid(row) for values in grouped.values() for row in values):
                state = "Invalid"
            else:
                mapped = {key: block_map(grouped[key]) for key in ("B", "F", "S")}
                blocks = sorted(mapped["B"])
                successes = {
                    condition: sum(mapped[condition][block]["condition_success"] is True for block in blocks)
                    for condition in ("B", "F", "S")
                }
                margins = sum(
                    float(mapped["S"][block]["private_score"])
                    >= float(mapped["F"][block]["private_score"]) - 0.05
                    for block in blocks
                )
                passed = successes["B"] <= 1 and successes["F"] >= 4 and successes["S"] >= 4 and margins >= 4
                state = "Admit" if passed else "Reject"
            omitted_invalid = any(
                not is_valid(row) and int(row["block_id"]) == omitted for row in rows
            )
            leave_one_block.append(
                {
                    "task_id": task_id,
                    "omitted_block": omitted,
                    "state": state,
                    "recovered_sensitivity": bool(full_invalid and omitted_invalid and state != "Invalid"),
                }
            )
    return {"grid": grid, "leave_one_block_out": leave_one_block}


def secondary_states(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    pairs: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        family = str(row["execution_family"])
        if family == "controls":
            controls[(str(row["task_id"]), str(row["variant_id"]))].append(row)
        elif family in {"structural_ladder", "alternate_reducers"}:
            pairs[(family, str(row["task_id"]), str(row["variant_id"]))].append(row)
    control_rows: list[dict[str, Any]] = []
    for (task_id, variant), values in sorted(controls.items()):
        grouped = group_by_condition(values)
        if variant == "planted_redundancy_positive":
            pair = pair_state(values)
            mapping = {"PairPass": "SanityPass", "PairFail": "SanityFail", "Invalid": "Invalid"}
            result = {**pair, "state": mapping[pair["state"]]}
        elif variant == "destructive_core_negative":
            if set(grouped) != {"F", "C"} or any(len(grouped[key]) != 6 for key in ("F", "C")):
                result = {"state": "Invalid", "reasons": ["incomplete_schedule"]}
            elif any(not is_valid(row) for item in grouped.values() for row in item):
                result = {"state": "Invalid", "reasons": ["invalid_terminal_row"]}
            else:
                mapped = {key: block_map(grouped[key]) for key in ("F", "C")}
                reference_success = sum(row["condition_success"] is True for row in grouped["F"])
                candidate_success = sum(row["condition_success"] is True for row in grouped["C"])
                targeted_failures = sum(
                    isinstance(row.get("hard_contract_vector"), list)
                    and not all(row["hard_contract_vector"])
                    for row in grouped["C"]
                )
                reasons: list[str] = []
                if reference_success < 5:
                    reasons.append("F_insufficient")
                if candidate_success > 1:
                    reasons.append("candidate_not_destructive")
                if targeted_failures < 5:
                    reasons.append("targeted_failure_insufficient")
                for registry, blocks in (("A", (1, 2, 3)), ("B", (4, 5, 6))):
                    if sum(mapped["F"][block]["condition_success"] is True for block in blocks) < 2:
                        reasons.append(f"{registry}_F_insufficient")
                    if sum(mapped["C"][block]["condition_success"] is True for block in blocks) > 1:
                        reasons.append(f"{registry}_candidate_not_destructive")
                    if sum(
                        isinstance(mapped["C"][block].get("hard_contract_vector"), list)
                        and not all(mapped["C"][block]["hard_contract_vector"])
                        for block in blocks
                    ) < 2:
                        reasons.append(f"{registry}_targeted_failure_insufficient")
                result = {
                    "state": "SanityPass" if not reasons else "SanityFail",
                    "reasons": reasons,
                    "reference_successes": reference_success,
                    "candidate_successes": candidate_success,
                    "targeted_hard_contract_failures": targeted_failures,
                }
        elif variant == "byte_identical_identity":
            if set(grouped) != {"F", "C"} or any(len(grouped[key]) != 6 for key in ("F", "C")):
                result = {"state": "Invalid", "reasons": ["incomplete_schedule"]}
            else:
                mapped = {key: block_map(grouped[key]) for key in ("F", "C")}
                digest_matches = 0
                valid_pairs = 0
                success_agreements = 0
                vector_agreements = 0
                score_within = 0
                raw_agreements = 0
                canonical_agreements = 0
                for block in range(1, 7):
                    reference = mapped["F"][block]
                    candidate = mapped["C"][block]
                    digest_matches += reference["canonical_model_visible_payload_sha256"] == candidate["canonical_model_visible_payload_sha256"]
                    if not (is_valid(reference) and is_valid(candidate)):
                        continue
                    valid_pairs += 1
                    success_agreements += reference["condition_success"] == candidate["condition_success"]
                    vector_agreements += (
                        equality_or_null(
                            reference.get("hard_contract_vector"),
                            candidate.get("hard_contract_vector"),
                            True,
                        )
                        is True
                    )
                    score_within += abs(float(reference["private_score"]) - float(candidate["private_score"])) <= 0.05
                    raw_agreements += (
                        equality_or_null(
                            reference.get("raw_response_sha256"),
                            candidate.get("raw_response_sha256"),
                            True,
                        )
                        is True
                    )
                    canonical_agreements += (
                        equality_or_null(
                            reference.get("canonical_output_sha256"),
                            candidate.get("canonical_output_sha256"),
                            True,
                        )
                        is True
                    )
                reasons = []
                if digest_matches != 6:
                    reasons.append("input_digest_mismatch")
                if valid_pairs < 5:
                    reasons.append("valid_pairs_insufficient")
                if success_agreements < 5:
                    reasons.append("success_agreement_insufficient")
                if vector_agreements < 5:
                    reasons.append("hard_vector_agreement_insufficient")
                if score_within < 5:
                    reasons.append("score_agreement_insufficient")
                result = {
                    "state": "SanityPass" if not reasons else "SanityFail",
                    "reasons": reasons,
                    "input_digest_matches": digest_matches,
                    "valid_pairs": valid_pairs,
                    "operational_success_agreements": success_agreements,
                    "hard_contract_vector_agreements": vector_agreements,
                    "score_delta_within_0_05": score_within,
                    "raw_response_sha256_agreements": raw_agreements,
                    "canonical_output_sha256_agreements": canonical_agreements,
                }
        else:
            raise AggregateError(f"unknown control variant: {variant}")
        control_rows.append({"task_id": task_id, "variant_id": variant, **result})

    pair_rows: list[dict[str, Any]] = []
    for (family, task_id, variant), values in sorted(pairs.items()):
        pair_rows.append(
            {
                "family": family,
                "task_id": task_id,
                "variant_id": variant,
                **pair_state(values),
            }
        )
    return {"controls": control_rows, "two_arm_pairs": pair_rows}


def equality_or_null(left: Any, right: Any, valid: bool) -> bool | None:
    if not valid or left is None or right is None:
        return None
    return left == right


def model_states(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["execution_family"] in {"required_closed_models", "remote_anchor"}:
            groups[(str(row["task_id"]), str(row["model_slot_id"]))].append(row)
    require(len(groups) == 20, "sentinel task-model cell count changed")
    output: list[dict[str, Any]] = []
    for (task_id, model), values in sorted(groups.items()):
        grouped = group_by_condition(values)
        require(set(grouped) == {"B", "F", "S", "I"}, "model cell conditions changed")
        candidate = decision_state(grouped["B"] + grouped["F"] + grouped["S"])
        f_rows = block_map(grouped["F"])
        i_rows = block_map(grouped["I"])
        raw_metrics: dict[str, list[Any]] = {
            "input_digest_agreement": [],
            "operational_success_agreement": [],
            "hard_contract_vector_agreement": [],
            "canonical_output_sha256_agreement": [],
            "raw_response_sha256_agreement": [],
            "absolute_private_score_delta": [],
        }
        for block in range(1, 7):
            f_row, i_row = f_rows[block], i_rows[block]
            pair_valid = is_valid(f_row) and is_valid(i_row)
            raw_metrics["input_digest_agreement"].append(
                equality_or_null(
                    f_row.get("canonical_model_visible_payload_sha256"),
                    i_row.get("canonical_model_visible_payload_sha256"),
                    pair_valid,
                )
            )
            raw_metrics["operational_success_agreement"].append(
                equality_or_null(f_row.get("condition_success"), i_row.get("condition_success"), pair_valid)
            )
            raw_metrics["hard_contract_vector_agreement"].append(
                equality_or_null(f_row.get("hard_contract_vector"), i_row.get("hard_contract_vector"), pair_valid)
            )
            raw_metrics["canonical_output_sha256_agreement"].append(
                equality_or_null(f_row.get("canonical_output_sha256"), i_row.get("canonical_output_sha256"), pair_valid)
            )
            raw_metrics["raw_response_sha256_agreement"].append(
                equality_or_null(f_row.get("raw_response_sha256"), i_row.get("raw_response_sha256"), pair_valid)
            )
            raw_metrics["absolute_private_score_delta"].append(
                abs(float(f_row["private_score"]) - float(i_row["private_score"]))
                if pair_valid
                else None
            )
        boolean_summary = {}
        for metric in (
            "input_digest_agreement",
            "operational_success_agreement",
            "hard_contract_vector_agreement",
            "canonical_output_sha256_agreement",
            "raw_response_sha256_agreement",
        ):
            observed = [value for value in raw_metrics[metric] if value is not None]
            agreements = sum(value is True for value in observed)
            boolean_summary[metric] = {
                "raw": raw_metrics[metric],
                "valid_pairs": len(observed),
                "registered_pairs": 6,
                "agreement_count": agreements,
                "agreement_rate_registered": agreements / 6,
                "agreement_rate_valid": agreements / len(observed) if observed else None,
            }
        deltas = [float(value) for value in raw_metrics["absolute_private_score_delta"] if value is not None]
        output.append(
            {
                "task_id": task_id,
                "model_slot_id": model,
                "candidate_state": candidate["state"],
                "candidate_reasons": candidate.get("reasons", []),
                "repeatability": boolean_summary,
                "score_delta": {
                    "raw": raw_metrics["absolute_private_score_delta"],
                    "valid_pairs": len(deltas),
                    "registered_pairs": 6,
                    "median": statistics.median(deltas) if deltas else None,
                    "maximum": max(deltas) if deltas else None,
                },
            }
        )
    return output


def failure_decomposition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    attempt_statuses: Counter[str] = Counter()
    retries = 0
    for row in rows:
        attempts = row.get("attempts", [])
        retries += max(0, len(attempts) - 1)
        for attempt in attempts:
            attempt_statuses[str(attempt.get("attempt_status_class"))] += 1
    return {
        "terminal_outcomes": dict(sorted(Counter(str(row["terminal_outcome"]) for row in rows).items())),
        "termination_reasons": dict(sorted(Counter(str(row["termination_reason"]) for row in rows).items())),
        "length_cap_terminations": sum(row.get("termination_reason") == "length" for row in rows),
        "attempt_statuses": dict(sorted(attempt_statuses.items())),
        "transport_retries": retries,
        "by_model": {
            model: dict(sorted(Counter(str(row["terminal_outcome"]) for row in values).items()))
            for model, values in sorted(group_rows(rows, "model_slot_id").items())
        },
        "by_family": {
            family: dict(sorted(Counter(str(row["terminal_outcome"]) for row in values).items()))
            for family, values in sorted(group_rows(rows, "execution_family").items())
        },
    }


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    return grouped


def flatten_outputs(result: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    primary_csv: list[dict[str, Any]] = []
    for row in result["primary_states"]:
        primary_csv.append(
            {
                **row,
                "reasons": ";".join(row.get("reasons", [])),
                "primary_reject_reason": row.get("primary_reject_reason"),
                "B_successes": row.get("successes", {}).get("B"),
                "F_successes": row.get("successes", {}).get("F"),
                "S_successes": row.get("successes", {}).get("S"),
                "margin_blocks": row.get("margin_blocks"),
            }
        )
    paper_csv: list[dict[str, Any]] = []
    for outcome, outcome_values in result["effects"].items():
        for contrast, contrast_values in outcome_values.items():
            for paper_id, value in contrast_values["papers"].items():
                paper_csv.append(
                    {
                        "outcome": outcome,
                        "contrast": contrast,
                        "domain": value["domain"],
                        "paper_id": paper_id,
                        "observed": value["observed"],
                        "lower": value["lower"],
                        "upper": value["upper"],
                        "valid_pairs": value["valid_pairs"],
                        "registered_pairs": value["registered_pairs"],
                    }
                )
    secondary_csv = []
    for kind, values in result["secondary_states"].items():
        for row in values:
            secondary_csv.append(
                {
                    "kind": kind,
                    **row,
                    "reasons": ";".join(row.get("reasons", [])),
                }
            )
    model_csv = []
    for row in result["model_states"]:
        model_csv.append(
            {
                "task_id": row["task_id"],
                "model_slot_id": row["model_slot_id"],
                "candidate_state": row["candidate_state"],
                "candidate_reasons": ";".join(row["candidate_reasons"]),
                "fi_valid_pairs": row["score_delta"]["valid_pairs"],
                "fi_score_median_delta": row["score_delta"]["median"],
                "fi_score_maximum_delta": row["score_delta"]["maximum"],
                "fi_success_agreements": row["repeatability"]["operational_success_agreement"]["agreement_count"],
                "fi_hard_vector_agreements": row["repeatability"]["hard_contract_vector_agreement"]["agreement_count"],
            }
        )
    failure_csv = [
        {"terminal_outcome": key, "count": value}
        for key, value in result["failures"]["terminal_outcomes"].items()
    ]
    return {
        "primary_task_states.csv": primary_csv,
        "paper_effects.csv": paper_csv,
        "secondary_states.csv": secondary_csv,
        "model_sentinel_states.csv": model_csv,
        "failure_decomposition.csv": failure_csv,
    }


def aggregate(successor: Path, run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    rows, input_manifest = load_rows(successor, run_dir)
    frozen = frozen_analyze(
        {
            "allowed_execution_ids": [row["execution_id"] for row in rows],
            "rows": rows,
        }
    )
    primary = [row for row in rows if row["execution_family"] == "primary"]
    states = primary_states(primary)
    effects = aggregate_effects(primary)
    secondary = secondary_states(rows)
    models = model_states(rows)
    failures = failure_decomposition(rows)
    state_counts = Counter(row["state"] for row in states)
    admission_domains = sorted({row["domain"] for row in states if row["state"] == "Admit"})
    control_counts = Counter(row["state"] for row in secondary["controls"])
    result = {
        "schema_version": "effectslice-fg3-aggregate-analysis.v1",
        "registered_rows": len(rows),
        "primary_registered_tasks": len(states),
        "primary_registered_papers": len({row["paper_id"] for row in states}),
        "primary_state_counts": dict(sorted(state_counts.items())),
        "primary_states": states,
        "effects": effects,
        "secondary_states": secondary,
        "model_states": models,
        "sla_sensitivity": sla_sensitivity(primary),
        "failures": failures,
        "frozen_analysis_result": frozen,
        "registered_targets": {
            "decision_coverage": {
                "observed_valid_tasks": state_counts["Admit"] + state_counts["Reject"],
                "required_valid_tasks": 20,
                "passed": state_counts["Admit"] + state_counts["Reject"] >= 20,
            },
            "candidate_yield": {
                "observed_admissions": state_counts["Admit"],
                "required_admissions": 8,
                "observed_admission_domains": len(admission_domains),
                "required_admission_domains": 3,
                "passed": state_counts["Admit"] >= 8 and len(admission_domains) >= 3,
            },
            "control_sanity": {
                "state_counts": dict(sorted(control_counts.items())),
                "passed": all(row["state"] == "SanityPass" for row in secondary["controls"]),
            },
        },
        "interpretation_guardrails": [
            "The registered benchmark is purposeful rather than a random population sample.",
            "Paper is the independent aggregate unit; tasks and blocks are nested.",
            "Invalid rows remain in registered denominators and are bounded, never deleted or imputed.",
            "Availability, integrity, contract conformance, and method quality are separate outcomes.",
            "Only five of 1,296 rows are operational successes, so broad method-effectiveness claims are unsupported.",
            "Controls are exact sanity states, not a confusion matrix or calibration estimate.",
            "Model and resource analyses are descriptive and do not rank providers.",
        ],
        "credential_values_recorded": False,
    }
    manifest = {
        "schema_version": "effectslice-fg3-analysis-manifest.v1",
        **input_manifest,
        "analysis_code_sha256": sha256_path(Path(__file__).resolve()),
        "frozen_analysis_code_sha256": sha256_path(ROOT / "stage23_analysis.py"),
        "successor_bundle_sha256": load_json(run_dir / "run_manifest.json")["successor_bundle_sha256"],
        "bootstrap_seed": 20260721,
        "bootstrap_replicates": 10000,
        "credential_values_recorded": False,
    }
    return result, manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--successor", type=Path, default=DEFAULT_SUCCESSOR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result, manifest = aggregate(args.successor.resolve(), args.run_dir.resolve())
    output_dir = args.output_dir.resolve()
    atomic_json(output_dir / "aggregate_results.json", result)
    atomic_json(output_dir / "analysis_manifest.json", manifest)
    csv_outputs = flatten_outputs(result)
    field_map = {
        "primary_task_states.csv": [
            "domain", "paper_id", "task_id", "state", "primary_reject_reason", "reasons", "B_valid",
            "F_valid", "S_valid", "B_successes", "F_successes", "S_successes",
            "margin_blocks", "full_tokens", "slice_tokens", "slice_token_ratio",
        ],
        "paper_effects.csv": [
            "outcome", "contrast", "domain", "paper_id", "observed", "lower",
            "upper", "valid_pairs", "registered_pairs",
        ],
        "secondary_states.csv": ["kind", "family", "task_id", "variant_id", "state", "reasons"],
        "model_sentinel_states.csv": [
            "task_id", "model_slot_id", "candidate_state", "candidate_reasons",
            "fi_valid_pairs", "fi_score_median_delta", "fi_score_maximum_delta",
            "fi_success_agreements", "fi_hard_vector_agreements",
        ],
        "failure_decomposition.csv": ["terminal_outcome", "count"],
    }
    for name, rows in csv_outputs.items():
        write_csv(output_dir / name, rows, field_map[name])
    output_hashes = {
        path.name: sha256_path(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file() and path.name != "output_hashes.json"
    }
    atomic_json(output_dir / "output_hashes.json", output_hashes)
    print(
        json.dumps(
            {
                "status": "passed",
                "rows": result["registered_rows"],
                "primary_state_counts": result["primary_state_counts"],
                "registered_targets": result["registered_targets"],
                "output_dir": str(output_dir),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AggregateError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
