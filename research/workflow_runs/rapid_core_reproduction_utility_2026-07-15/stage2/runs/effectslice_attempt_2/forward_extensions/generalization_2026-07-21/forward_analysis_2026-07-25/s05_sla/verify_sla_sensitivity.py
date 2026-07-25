from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "outputs"
ANALYZER = HERE / "analyze_sla_sensitivity.py"
OUTPUTS = (
    "leave_one_block_out.csv",
    "margin_tolerance_sensitivity.csv",
    "registered_decision_summary.csv",
    "registered_task_decisions.csv",
    "sla_registry_oat.csv",
    "sla_sensitivity.json",
    "sla_total_threshold_grid.csv",
    "task_decision_stability.csv",
    "manifest.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUTPUT_DIR / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_semantics() -> None:
    manifest = json.loads((OUTPUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    if manifest["section"] != "05_sla_sensitivity":
        raise AssertionError("Unexpected section identifier.")
    for name, metadata in manifest["outputs"].items():
        if sha256(OUTPUT_DIR / name) != metadata["sha256"]:
            raise AssertionError(f"Output hash mismatch for {name}.")

    summary = json.loads((OUTPUT_DIR / "sla_sensitivity.json").read_text(encoding="utf-8"))
    if summary["status"] != "verified_forward_analysis":
        raise AssertionError("SLA sensitivity is not marked verified.")
    if summary["registered_six_block_decisions"]["state_counts"] != {
        "Admit": 2,
        "Reject": 22,
        "Invalid": 0,
    }:
        raise AssertionError("Registered decision counts changed.")
    if summary["registered_six_block_decisions"]["primary_reject_reason_counts"] != {
        "baseline-sensitive": 2,
        "full-insufficient": 20,
        "none": 2,
    }:
        raise AssertionError("Primary reject-reason counts changed.")
    if summary["registered_engineering_target"] != {
        "minimum_admitted_tasks": 8,
        "minimum_domains": 3,
        "observed_admitted_tasks": 2,
        "observed_domains": 2,
        "admitted_domain_ids": ["data_analysis", "nlp"],
        "achieved": False,
    }:
        raise AssertionError("Registered engineering-target result changed.")
    if summary["total_threshold_grid"] != {
        "profiles": 81,
        "profiles_changing_at_least_one_task": 53,
        "registered_per_registry_gates_held_fixed": True,
        "tasks_changed_in_any_profile": ["DATA-LEI-02", "NLP-LL2-02", "NLP-LLM-02"],
    }:
        raise AssertionError("Total-threshold sensitivity summary changed.")
    if summary["margin_tolerance_sensitivity"]["profiles_changing_at_least_one_task"] != 0:
        raise AssertionError("Margin-tolerance decisions unexpectedly changed.")
    loo = summary["leave_one_block_out"]
    if loo["recomputations"] != 144 or loo["state_counts"] != {
        "Admit": 14,
        "Reject": 130,
        "Invalid": 0,
    }:
        raise AssertionError("Leave-one-block state counts changed.")
    if loo["recomputations_differing_from_registered"] != 2:
        raise AssertionError("Leave-one-block transition count changed.")
    if loo["tasks_with_any_changed_omission"] != ["NLP-LL2-02"]:
        raise AssertionError("Unexpected leave-one-block transition task.")

    registered = read_csv("registered_task_decisions.csv")
    if len(registered) != 24:
        raise AssertionError("Expected 24 registered task decisions.")
    admitted = sorted(row["task_id"] for row in registered if row["state"] == "Admit")
    if admitted != ["DATA-LEI-02", "NLP-LLM-02"]:
        raise AssertionError(f"Unexpected registered admits: {admitted}")

    grid = read_csv("sla_total_threshold_grid.csv")
    if len(grid) != 81 or sum(row["registered_profile"] == "True" for row in grid) != 1:
        raise AssertionError("Total-threshold grid is incomplete or ambiguously registered.")
    registered_grid = next(row for row in grid if row["registered_profile"] == "True")
    if (registered_grid["admit_tasks"], registered_grid["reject_tasks"]) != ("2", "22"):
        raise AssertionError("Registered grid profile does not reproduce frozen decisions.")

    registry_rows = read_csv("sla_registry_oat.csv")
    if len(registry_rows) != 9:
        raise AssertionError("Expected nine registry one-at-a-time profiles.")
    changed_registry = sorted(
        row["profile_id"] for row in registry_rows if int(row["changed_task_count"]) > 0
    )
    if changed_registry != ["registry_b_max_0", "registry_f_min_3"]:
        raise AssertionError(f"Unexpected registry-sensitive profiles: {changed_registry}")

    tolerance_rows = read_csv("margin_tolerance_sensitivity.csv")
    if len(tolerance_rows) != 5 or any(int(row["changed_task_count"]) for row in tolerance_rows):
        raise AssertionError("Margin tolerance should leave all 24 decisions unchanged.")

    loo_rows = read_csv("leave_one_block_out.csv")
    if len(loo_rows) != 144:
        raise AssertionError("Expected 144 leave-one-block recomputations.")
    transitions = [row for row in loo_rows if row["differs_from_registered"] == "True"]
    if sorted((row["task_id"], int(row["omitted_block_id"])) for row in transitions) != [
        ("NLP-LL2-02", 2),
        ("NLP-LL2-02", 4),
    ]:
        raise AssertionError("Unexpected leave-one-block transitions.")


def rerun() -> None:
    with tempfile.TemporaryDirectory(prefix="effectslice_s05_") as temp:
        output_dir = Path(temp)
        subprocess.run(
            [sys.executable, str(ANALYZER), "--output-dir", str(output_dir)],
            check=True,
        )
        mismatches = [
            name
            for name in OUTPUTS
            if (OUTPUT_DIR / name).read_bytes() != (output_dir / name).read_bytes()
        ]
        if mismatches:
            raise AssertionError(f"Independent rerun differs for: {mismatches}")


def main() -> None:
    verify_semantics()
    rerun()
    print("PASS: Section 05 SLA decisions and sensitivity outputs are verified byte for byte.")


if __name__ == "__main__":
    main()
