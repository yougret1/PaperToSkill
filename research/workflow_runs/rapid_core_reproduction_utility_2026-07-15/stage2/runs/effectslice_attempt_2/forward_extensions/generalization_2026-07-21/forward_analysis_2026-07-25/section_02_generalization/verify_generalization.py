from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "outputs"
EXPECTED_MODEL_SUCCESS = {
    "claude_opus_4_7": (0.25, 0.20833333333333334),
    "deepseek_primary": (0.25, 0.04166666666666667),
    "gpt_5_5": (0.5, 0.0),
    "gpt_5_6_luna": (0.4166666666666667, -0.125),
    "gpt_5_6_sol": (0.375, 0.08333333333333331),
    "gpt_5_6_terra": (0.375, 0.041666666666666685),
}
EXPECTED_DOMAIN_FB = {
    "agent_tool_use": 0.13888888888888887,
    "data_analysis": 0.16666666666666666,
    "nlp": 0.3333333333333333,
    "software_engineering": 0.13888888888888887,
}
EXPECTED_REDUCER_SUCCESS = {
    ("alternate_reducers", "dag_greedy_ratio_60_v1"): 0.16666666666666666,
    ("alternate_reducers", "source_window_ratio_60_v1"): 0.20833333333333334,
    ("primary", "primary_dag_ratio_60_v1"): 0.04166666666666667,
    ("structural_ladder", "L0_primary_slice"): 0.20833333333333337,
    ("structural_ladder", "L1_mid_restore"): 0.20833333333333337,
    ("structural_ladder", "L2_near_full_strict"): 0.08333333333333334,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(name: str) -> list[dict[str, str]]:
    with (OUTPUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(observed: float, expected: float) -> bool:
    return math.isclose(float(observed), expected, rel_tol=0.0, abs_tol=1e-12)


def main() -> None:
    manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((OUTPUT / "summary.json").read_text(encoding="utf-8"))
    for name, record in manifest["outputs"].items():
        observed = sha256(OUTPUT / name)
        if observed != record["sha256"]:
            raise AssertionError(f"Hash mismatch for {name}: {observed}")

    expected_rows = {
        "heatmap.csv": 432,
        "model_tasks.csv": 44,
        "model_summary.csv": 6,
        "domains.csv": 4,
        "primary_papers.csv": 72,
        "registry_tasks.csv": 48,
        "registry_summary.csv": 2,
        "reducer_tasks.csv": 24,
        "reducer_summary.csv": 6,
    }
    for name, expected in expected_rows.items():
        observed = len(csv_rows(name))
        if observed != expected:
            raise AssertionError(f"{name}: expected {expected} rows, observed {observed}")

    coverage = summary["coverage"]
    if coverage["rows"] != 1296 or coverage["heatmap_cells"] != 432:
        raise AssertionError("Coverage must bind all 1,296 rows and 432 heatmap cells.")
    if coverage["conditions"] != {"B": 264, "C": 192, "F": 456, "I": 120, "S": 264}:
        raise AssertionError("Condition coverage changed.")

    model_rows = {row["model_slot_id"]: row for row in summary["model_effects"]}
    if set(model_rows) != set(EXPECTED_MODEL_SUCCESS):
        raise AssertionError("Model set changed.")
    for model, (fb, sf) in EXPECTED_MODEL_SUCCESS.items():
        if not close(model_rows[model]["F_minus_B_operational_success"], fb):
            raise AssertionError(f"{model} F-B success changed.")
        if not close(model_rows[model]["S_minus_F_operational_success"], sf):
            raise AssertionError(f"{model} S-F success changed.")

    domains = {row["domain"]: row for row in summary["primary_domain_effects"]}
    for domain, expected in EXPECTED_DOMAIN_FB.items():
        if not close(domains[domain]["F_minus_B_operational_success"], expected):
            raise AssertionError(f"{domain} primary F-B success changed.")

    reducers = {
        (row["execution_family"], row["variant_id"]): row
        for row in summary["reducer_effects"]
    }
    for key, expected in EXPECTED_REDUCER_SUCCESS.items():
        if not close(reducers[key]["candidate_minus_F_operational_success"], expected):
            raise AssertionError(f"Reducer {key} candidate-F success changed.")

    claims = summary["claim_diagnostics"]
    if claims != {
        "F_minus_B_success_positive_models": 6,
        "S_minus_B_success_positive_models": 6,
        "S_minus_F_success_positive_models": 4,
        "S_minus_F_success_negative_models": 1,
        "S_minus_F_success_zero_models": 1,
    }:
        raise AssertionError("Cross-model claim diagnostics changed.")

    primary = {
        (row["contrast"], row["endpoint"]): row
        for row in summary["primary_single_driver_diagnostics"]
    }
    for contrast in ("F_minus_B", "S_minus_B"):
        for endpoint in ("operational_success", "private_score"):
            if primary[(contrast, endpoint)]["sign_reversals"] != 0:
                raise AssertionError(f"Primary {contrast}/{endpoint} reverses under LOO.")
    print("PASS: section 02 coverage, effects, interactions, and hashes verified")


if __name__ == "__main__":
    main()
