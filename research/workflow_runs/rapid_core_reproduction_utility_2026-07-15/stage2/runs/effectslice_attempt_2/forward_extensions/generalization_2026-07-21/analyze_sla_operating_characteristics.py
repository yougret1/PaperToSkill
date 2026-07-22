from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "preregistration" / "experiment_plan.json"
OUTPUT_PATH = ROOT / "preregistration" / "sla_operating_characteristics.json"
COUNT_KEYS = ("A_B", "A_F", "A_S", "A_M", "B_B", "B_F", "B_S", "B_M")


def _load_rule() -> tuple[dict[str, int], dict[str, int]]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    sla = plan["scoring"]["admission_sla"]
    return sla["total_six_blocks"], sla["each_three_block_registry"]


def classify(
    counts: dict[str, int], total: dict[str, int], per_registry: dict[str, int]
) -> str:
    f_ok = (
        counts["A_F"] + counts["B_F"] >= total["minimum_F_successes"]
        and counts["A_F"] >= per_registry["minimum_F_successes"]
        and counts["B_F"] >= per_registry["minimum_F_successes"]
    )
    if not f_ok:
        return "full-insufficient"

    baseline_ok = (
        counts["A_B"] + counts["B_B"] <= total["maximum_B_successes"]
        and counts["A_B"] <= per_registry["maximum_B_successes"]
        and counts["B_B"] <= per_registry["maximum_B_successes"]
    )
    if not baseline_ok:
        return "baseline-sensitive"

    s_ok = (
        counts["A_S"] + counts["B_S"] >= total["minimum_S_successes"]
        and counts["A_S"] >= per_registry["minimum_S_successes"]
        and counts["B_S"] >= per_registry["minimum_S_successes"]
    )
    if not s_ok:
        return "slice-insufficient"

    margin_ok = (
        counts["A_M"] + counts["B_M"]
        >= total["minimum_valid_paired_margin_blocks"]
        and counts["A_M"]
        >= per_registry["minimum_valid_paired_margin_blocks"]
        and counts["B_M"]
        >= per_registry["minimum_valid_paired_margin_blocks"]
    )
    if not margin_ok:
        return "margin-shortfall"
    return "Admit"


def analyze() -> dict[str, object]:
    total, per_registry = _load_rule()
    state_rows: list[tuple[dict[str, int], str]] = []
    labels: Counter[str] = Counter()
    for values in itertools.product(range(4), repeat=len(COUNT_KEYS)):
        counts = dict(zip(COUNT_KEYS, values, strict=True))
        label = classify(counts, total, per_registry)
        state_rows.append((counts, label))
        labels[label] += 1

    return {
        "schema_version": "effectslice-fg1-sla-operating-characteristics.v1",
        "source_plan": "preregistration/experiment_plan.json",
        "analysis_type": "deterministic engineering-rule enumeration",
        "count_state_definition": (
            "Eight counts: B/F/S/margin passes in each three-block registry; "
            "every count ranges from 0 to 3."
        ),
        "total_count_states": len(state_rows),
        "classification_counts": dict(sorted(labels.items())),
        "passing_count_states": labels["Admit"],
        "registered_rule": {
            "total_six_blocks": total,
            "each_three_block_registry": per_registry,
        },
        "logical_note": (
            "At the registered 5-of-6 total and 2-of-3 per-registry thresholds, "
            "the per-registry count gates are logically entailed by the total gate. "
            "They remain explicit audit checks for registry materialization and reporting."
        ),
        "probability_model": (
            "None registered. B/F/S success and paired-margin counts are dependent "
            "within blocks, so no factorized admission probability is reported."
        ),
        "invalid_policy": (
            "Invalid rows are not enumerated as failures here; any missing registered "
            "row makes the empirical candidate decision Invalid."
        ),
    }


def main() -> None:
    OUTPUT_PATH.write_text(
        json.dumps(analyze(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
