from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from intervention_successor import (
    ARM_ORDER,
    HERE,
    REGISTRATION,
    extended,
    load_json,
    sha256_file,
    verify_registration,
    write_json,
)
from verify_run_artifacts import verify as verify_run_artifacts


DEFAULT_RUN = HERE / "run"
DEFAULT_OUTPUT = HERE / "outputs"

CONTRASTS = (
    {
        "contrast_id": "critical_necessity",
        "positive_arm": "F",
        "negative_arm": "F_drop_critical",
        "interpretation": "positive delta means critical-atom removal harmed the full prompt",
    },
    {
        "contrast_id": "noncritical_necessity",
        "positive_arm": "F",
        "negative_arm": "F_drop_noncritical",
        "interpretation": "positive delta means comparator removal harmed the full prompt",
    },
    {
        "contrast_id": "critical_rescue",
        "positive_arm": "S_restore_critical",
        "negative_arm": "S",
        "interpretation": "positive delta means restoring the critical atom rescued the slice",
    },
    {
        "contrast_id": "noncritical_rescue",
        "positive_arm": "S_restore_noncritical",
        "negative_arm": "S",
        "interpretation": "positive delta means restoring the comparator atom rescued the slice",
    },
)

SEMANTIC_OUTCOMES = {
    "operational_success",
    "hard_contract_failure",
    "score_shortfall",
}


def write_csv(
    path: Path, fieldnames: list[str], rows: list[dict[str, Any]]
) -> None:
    extended(path.parent).mkdir(parents=True, exist_ok=True)
    with extended(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def success(row: dict[str, Any]) -> int:
    return int(row["terminal_outcome"] == "operational_success")


def semantic_valid(row: dict[str, Any]) -> bool:
    return row["terminal_outcome"] in SEMANTIC_OUTCOMES


def safe_mean(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


def sign_test_two_sided(improved: int, worsened: int) -> float | None:
    nonzero = improved + worsened
    if nonzero == 0:
        return None
    tail = min(improved, worsened)
    probability = sum(
        math.comb(nonzero, value) for value in range(tail + 1)
    ) / (2**nonzero)
    return round(min(1.0, 2 * probability), 6)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [
        float(row["private_score"])
        for row in rows
        if row.get("private_score") is not None
    ]
    elapsed = [
        float(row["total_execution_elapsed_ms"])
        for row in rows
        if row.get("total_execution_elapsed_ms") is not None
    ]
    tokens = [
        float(row["provider_reported_total_tokens"])
        for row in rows
        if row.get("provider_reported_total_tokens") is not None
    ]
    vectors = [
        row["hard_contract_vector"]
        for row in rows
        if isinstance(row.get("hard_contract_vector"), list)
    ]
    return {
        "rows": len(rows),
        "operational_success": sum(success(row) for row in rows),
        "hard_contract_failure": sum(
            row["terminal_outcome"] == "hard_contract_failure" for row in rows
        ),
        "score_shortfall": sum(
            row["terminal_outcome"] == "score_shortfall" for row in rows
        ),
        "technical_or_invalid": sum(
            not semantic_valid(row)
            for row in rows
        ),
        "success_rate": round(
            sum(success(row) for row in rows) / len(rows), 6
        ),
        "mean_private_score": safe_mean(scores),
        "hard_vector_0_pass": sum(bool(vector[0]) for vector in vectors),
        "hard_vector_1_pass": sum(bool(vector[1]) for vector in vectors),
        "mean_elapsed_ms": safe_mean(elapsed),
        "mean_provider_total_tokens": safe_mean(tokens),
    }


def analyze(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    verify_registration()
    run_verification = verify_run_artifacts(run_dir)
    schedule = load_json(REGISTRATION / "schedule.json")["rows"]
    results: list[dict[str, Any]] = []
    for registered in schedule:
        path = run_dir / "rows" / f"{registered['execution_id']}.json"
        row = load_json(path)
        if row["registered_request_sha256"] != registered["request_sha256"]:
            raise RuntimeError(
                f"request binding mismatch: {registered['execution_id']}"
            )
        results.append({**registered, **row})

    row_results: list[dict[str, Any]] = []
    for row in sorted(
        results,
        key=lambda value: (
            value["task_id"],
            value["registry_id"],
            ARM_ORDER.index(value["arm_id"]),
        ),
    ):
        vector = row.get("hard_contract_vector")
        row_results.append(
            {
                "task_id": row["task_id"],
                "domain": row["domain"],
                "registry_id": row["registry_id"],
                "arm_id": row["arm_id"],
                "contrast_role": row["contrast_role"],
                "dependency_closed": row["dependency_closed"],
                "candidate_atom_count": len(row["candidate_atom_ids"]),
                "candidate_tokens": row["candidate_tokens"],
                "candidate_bytes": row["candidate_bytes"],
                "execution_order": row["execution_order"],
                "execution_id": row["execution_id"],
                "terminal_outcome": row["terminal_outcome"],
                "semantic_valid": semantic_valid(row),
                "operational_success": bool(success(row)),
                "private_score": row.get("private_score"),
                "hard_vector_0": vector[0] if vector is not None else None,
                "hard_vector_1": vector[1] if vector is not None else None,
                "transport_attempts": len(row.get("attempts", [])),
                "provider_finish_reason": row.get("provider_finish_reason"),
                "termination_reason": row.get("termination_reason"),
                "elapsed_ms": row.get("total_execution_elapsed_ms"),
                "provider_input_tokens": row.get(
                    "provider_reported_input_tokens"
                ),
                "provider_output_tokens": row.get(
                    "provider_reported_output_tokens"
                ),
                "provider_total_tokens": row.get(
                    "provider_reported_total_tokens"
                ),
            }
        )

    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_domain_arm: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_unit_arm: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in results:
        by_arm[row["arm_id"]].append(row)
        by_domain_arm[(row["domain"], row["arm_id"])].append(row)
        key = (row["task_id"], row["registry_id"], row["arm_id"])
        if key in by_unit_arm:
            raise RuntimeError(f"duplicate task-registry-arm result: {key}")
        by_unit_arm[key] = row

    arm_summary = [
        {"arm_id": arm_id, **summarize_rows(by_arm[arm_id])}
        for arm_id in ARM_ORDER
    ]
    domain_arm_summary = [
        {
            "domain": domain,
            "arm_id": arm_id,
            **summarize_rows(by_domain_arm[(domain, arm_id)]),
        }
        for domain in sorted({row["domain"] for row in results})
        for arm_id in ARM_ORDER
    ]

    contrast_units: list[dict[str, Any]] = []
    contrast_summary: list[dict[str, Any]] = []
    contrast_deltas: dict[tuple[str, str, str], float] = {}
    contrast_validity: dict[tuple[str, str, str], bool] = {}
    units = sorted({(row["task_id"], row["registry_id"]) for row in results})
    for contrast in CONTRASTS:
        selected_rows: list[dict[str, Any]] = []
        for task_id, registry_id in units:
            positive = by_unit_arm[
                (task_id, registry_id, contrast["positive_arm"])
            ]
            negative = by_unit_arm[
                (task_id, registry_id, contrast["negative_arm"])
            ]
            delta_success = success(positive) - success(negative)
            positive_score = positive.get("private_score")
            negative_score = negative.get("private_score")
            delta_score = (
                round(float(positive_score) - float(negative_score), 6)
                if positive_score is not None and negative_score is not None
                else None
            )
            positive_vector = positive.get("hard_contract_vector")
            negative_vector = negative.get("hard_contract_vector")
            delta_vector_0 = (
                int(positive_vector[0]) - int(negative_vector[0])
                if positive_vector is not None and negative_vector is not None
                else None
            )
            delta_vector_1 = (
                int(positive_vector[1]) - int(negative_vector[1])
                if positive_vector is not None and negative_vector is not None
                else None
            )
            pair_valid = semantic_valid(positive) and semantic_valid(negative)
            item = {
                "contrast_id": contrast["contrast_id"],
                "task_id": task_id,
                "domain": positive["domain"],
                "registry_id": registry_id,
                "positive_arm": contrast["positive_arm"],
                "negative_arm": contrast["negative_arm"],
                "positive_outcome": positive["terminal_outcome"],
                "negative_outcome": negative["terminal_outcome"],
                "positive_semantic_valid": semantic_valid(positive),
                "negative_semantic_valid": semantic_valid(negative),
                "pair_valid": pair_valid,
                "delta_operational_success": delta_success,
                "delta_private_score": delta_score,
                "delta_hard_vector_0": delta_vector_0,
                "delta_hard_vector_1": delta_vector_1,
            }
            contrast_deltas[
                (contrast["contrast_id"], task_id, registry_id)
            ] = float(delta_success)
            contrast_validity[
                (contrast["contrast_id"], task_id, registry_id)
            ] = pair_valid
            selected_rows.append(item)
            contrast_units.append(item)

        itt_improved = sum(
            row["delta_operational_success"] > 0 for row in selected_rows
        )
        itt_worsened = sum(
            row["delta_operational_success"] < 0 for row in selected_rows
        )
        valid_rows = [row for row in selected_rows if row["pair_valid"]]
        valid_improved = sum(
            row["delta_operational_success"] > 0 for row in valid_rows
        )
        valid_worsened = sum(
            row["delta_operational_success"] < 0 for row in valid_rows
        )
        itt_score_deltas = [
            float(row["delta_private_score"])
            for row in selected_rows
            if row["delta_private_score"] is not None
        ]
        valid_score_deltas = [
            float(row["delta_private_score"])
            for row in valid_rows
            if row["delta_private_score"] is not None
        ]
        itt_mean_delta = round(
            mean(
                row["delta_operational_success"]
                for row in selected_rows
            ),
            6,
        )
        valid_mean_delta = (
            round(
                mean(
                    row["delta_operational_success"]
                    for row in valid_rows
                ),
                6,
            )
            if valid_rows
            else None
        )
        contrast_summary.append(
            {
                "contrast_id": contrast["contrast_id"],
                "positive_arm": contrast["positive_arm"],
                "negative_arm": contrast["negative_arm"],
                "units": len(selected_rows),
                "itt_units": len(selected_rows),
                "valid_units": len(valid_rows),
                "excluded_invalid_units": len(selected_rows) - len(valid_rows),
                "improved_units": itt_improved,
                "worsened_units": itt_worsened,
                "unchanged_units": (
                    len(selected_rows) - itt_improved - itt_worsened
                ),
                "itt_improved_units": itt_improved,
                "itt_worsened_units": itt_worsened,
                "itt_unchanged_units": (
                    len(selected_rows) - itt_improved - itt_worsened
                ),
                "valid_improved_units": valid_improved,
                "valid_worsened_units": valid_worsened,
                "valid_unchanged_units": (
                    len(valid_rows) - valid_improved - valid_worsened
                ),
                "mean_delta_operational_success": itt_mean_delta,
                "itt_mean_delta_operational_success": itt_mean_delta,
                "valid_pair_mean_delta_operational_success": valid_mean_delta,
                "mean_delta_private_score": safe_mean(itt_score_deltas),
                "itt_mean_delta_private_score": safe_mean(itt_score_deltas),
                "valid_pair_mean_delta_private_score": safe_mean(
                    valid_score_deltas
                ),
                "two_sided_exact_sign_p": sign_test_two_sided(
                    itt_improved, itt_worsened
                ),
                "valid_pair_two_sided_exact_sign_p": sign_test_two_sided(
                    valid_improved, valid_worsened
                ),
                "interpretation": contrast["interpretation"],
            }
        )

    selectivity_rows: list[dict[str, Any]] = []
    for task_id, registry_id in units:
        critical_necessity = contrast_deltas[
            ("critical_necessity", task_id, registry_id)
        ]
        noncritical_necessity = contrast_deltas[
            ("noncritical_necessity", task_id, registry_id)
        ]
        critical_rescue = contrast_deltas[
            ("critical_rescue", task_id, registry_id)
        ]
        noncritical_rescue = contrast_deltas[
            ("noncritical_rescue", task_id, registry_id)
        ]
        all_contrasts_valid = all(
            contrast_validity[(contrast_id, task_id, registry_id)]
            for contrast_id in (
                "critical_necessity",
                "noncritical_necessity",
                "critical_rescue",
                "noncritical_rescue",
            )
        )
        domain = by_unit_arm[(task_id, registry_id, "F")]["domain"]
        selectivity_rows.append(
            {
                "task_id": task_id,
                "domain": domain,
                "registry_id": registry_id,
                "all_contrasts_valid": all_contrasts_valid,
                "necessity_delta_of_deltas": (
                    critical_necessity - noncritical_necessity
                ),
                "rescue_delta_of_deltas": critical_rescue - noncritical_rescue,
            }
        )

    token_balance: list[dict[str, Any]] = []
    for task_id in sorted({row["task_id"] for row in results}):
        sample = {
            row["arm_id"]: row
            for row in results
            if row["task_id"] == task_id and row["registry_id"] == "A"
        }
        token_balance.append(
            {
                "task_id": task_id,
                "domain": sample["F"]["domain"],
                "critical_atom_tokens": (
                    sample["F"]["candidate_tokens"]
                    - sample["F_drop_critical"]["candidate_tokens"]
                ),
                "noncritical_atom_tokens": (
                    sample["F"]["candidate_tokens"]
                    - sample["F_drop_noncritical"]["candidate_tokens"]
                ),
                "drop_token_difference_critical_minus_noncritical": (
                    sample["F_drop_noncritical"]["candidate_tokens"]
                    - sample["F_drop_critical"]["candidate_tokens"]
                ),
                "critical_restore_tokens": (
                    sample["S_restore_critical"]["candidate_tokens"]
                    - sample["S"]["candidate_tokens"]
                ),
                "noncritical_restore_tokens": (
                    sample["S_restore_noncritical"]["candidate_tokens"]
                    - sample["S"]["candidate_tokens"]
                ),
            }
        )

    outcome_counts = Counter(row["terminal_outcome"] for row in results)
    technical_or_invalid = sum(
        outcome_counts[outcome]
        for outcome in outcome_counts
        if outcome not in SEMANTIC_OUTCOMES
    )
    technical_invalid_details = []
    for row in results:
        if semantic_valid(row):
            continue
        canonical_path = run_dir / row["canonical_output_path"]
        canonical_bytes = extended(canonical_path).stat().st_size
        technical_invalid_details.append(
            {
                "execution_id": row["execution_id"],
                "task_id": row["task_id"],
                "domain": row["domain"],
                "registry_id": row["registry_id"],
                "arm_id": row["arm_id"],
                "terminal_outcome": row["terminal_outcome"],
                "provider_finish_reason": row.get("provider_finish_reason"),
                "termination_reason": row.get("termination_reason"),
                "provider_output_tokens": row.get(
                    "provider_reported_output_tokens"
                ),
                "canonical_output_bytes": canonical_bytes,
                "response_exhausted_before_submission": (
                    row.get("provider_finish_reason") == "length"
                    and canonical_bytes == 0
                ),
            }
        )
    valid_selectivity_rows = [
        row for row in selectivity_rows if row["all_contrasts_valid"]
    ]
    analysis = {
        "schema_version": "effectslice-s07-atom-intervention-analysis.v2",
        "status": "verified_focused_atom_intervention_analysis",
        "scope": {
            "tasks": 4,
            "domains": 4,
            "task_registry_units": len(units),
            "arms": len(ARM_ORDER),
            "terminal_rows": len(results),
            "model_slot_id": "deepseek_primary",
            "single_semantic_response_per_cell": True,
        },
        "run_verification": run_verification,
        "terminal_outcomes": dict(sorted(outcome_counts.items())),
        "complete_scored_grid": technical_or_invalid == 0,
        "technical_or_invalid_rows": technical_or_invalid,
        "technical_or_invalid_details": technical_invalid_details,
        "arm_summaries": arm_summary,
        "contrast_summaries": contrast_summary,
        "selectivity": {
            "mean_necessity_delta_of_deltas": round(
                mean(
                    row["necessity_delta_of_deltas"]
                    for row in selectivity_rows
                ),
                6,
            ),
            "mean_rescue_delta_of_deltas": round(
                mean(
                    row["rescue_delta_of_deltas"]
                    for row in selectivity_rows
                ),
                6,
            ),
            "valid_complete_contrast_units": len(valid_selectivity_rows),
            "excluded_incomplete_contrast_units": (
                len(selectivity_rows) - len(valid_selectivity_rows)
            ),
            "valid_mean_necessity_delta_of_deltas": (
                round(
                    mean(
                        row["necessity_delta_of_deltas"]
                        for row in valid_selectivity_rows
                    ),
                    6,
                )
                if valid_selectivity_rows
                else None
            ),
            "valid_mean_rescue_delta_of_deltas": (
                round(
                    mean(
                        row["rescue_delta_of_deltas"]
                        for row in valid_selectivity_rows
                    ),
                    6,
                )
                if valid_selectivity_rows
                else None
            ),
            "units": selectivity_rows,
        },
        "claim_boundary": (
            "This is a focused 4-task by 2-registry singleton intervention with "
            "one terminal provider response per cell and no replay of completed "
            "responses. It tests local necessity, "
            "rescue, and selectivity; it does not establish broad multi-seed "
            "repeatability, and closure-breaking singleton arms are not reducer outputs. "
            "Fixed-grid ITT estimates count malformed/no-submission rows as non-success; "
            "valid-pair estimates exclude any contrast whose endpoint is not a semantic "
            "success, hard-contract failure, or score shortfall."
        ),
    }

    extended(output_dir).mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "row_results.csv",
        list(row_results[0]),
        row_results,
    )
    write_csv(
        output_dir / "arm_summary.csv",
        list(arm_summary[0]),
        arm_summary,
    )
    write_csv(
        output_dir / "domain_arm_summary.csv",
        list(domain_arm_summary[0]),
        domain_arm_summary,
    )
    write_csv(
        output_dir / "contrast_units.csv",
        list(contrast_units[0]),
        contrast_units,
    )
    write_csv(
        output_dir / "contrast_summary.csv",
        list(contrast_summary[0]),
        contrast_summary,
    )
    write_csv(
        output_dir / "token_balance.csv",
        list(token_balance[0]),
        token_balance,
    )
    write_json(output_dir / "analysis.json", analysis)
    output_names = (
        "analysis.json",
        "row_results.csv",
        "arm_summary.csv",
        "domain_arm_summary.csv",
        "contrast_units.csv",
        "contrast_summary.csv",
        "token_balance.csv",
    )
    manifest = {
        "schema_version": "effectslice-s07-atom-intervention-analysis-manifest.v2",
        "inputs": {
            "registration/manifest.json": sha256_file(
                REGISTRATION / "manifest.json"
            ),
            **{
                f"run/rows/{row['execution_id']}.json": sha256_file(
                    run_dir / "rows" / f"{row['execution_id']}.json"
                )
                for row in schedule
            },
        },
        "outputs": {
            name: sha256_file(output_dir / name) for name in output_names
        },
    }
    write_json(output_dir / "manifest.json", manifest)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(
        json.dumps(
            analyze(args.run_dir, args.output_dir),
            sort_keys=True,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
