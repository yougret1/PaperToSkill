from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from targeted_successor import (
    HERE,
    REGISTRATION,
    extended,
    load_json,
    sha256_file,
    verify_registration,
    write_json,
)


DEFAULT_RUN = HERE / "run"
DEFAULT_OUTPUT = HERE / "outputs"


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


def analyze(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    verify_registration()
    registry = load_json(REGISTRATION / "registry.json")
    schedule = load_json(REGISTRATION / "schedule.json")["rows"]
    case_registry = {case["case_id"]: case for case in registry["cases"]}
    results: list[dict[str, Any]] = []
    for registered in schedule:
        path = run_dir / "rows" / f"{registered['execution_id']}.json"
        if not extended(path).is_file():
            raise RuntimeError(
                f"missing terminal result: {registered['execution_id']}"
            )
        row = load_json(path)
        if row["registered_request_sha256"] != registered["request_sha256"]:
            raise RuntimeError(
                f"request binding mismatch: {registered['execution_id']}"
            )
        results.append(row)

    result_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    for case_id in sorted(case_registry):
        case = case_registry[case_id]
        selected = sorted(
            (row for row in results if row["case_id"] == case_id),
            key=lambda row: row["replica"],
        )
        if len(selected) != 2:
            raise RuntimeError(f"expected two replicas for {case_id}")
        for row in selected:
            result_rows.append(
                {
                    "case_id": case_id,
                    "task_id": row["task_id"],
                    "block_id": case["block_id"],
                    "registry_id": row["registry_id"],
                    "replica": row["replica"],
                    "execution_id": row["execution_id"],
                    "terminal_outcome": row["terminal_outcome"],
                    "operational_success": (
                        row["terminal_outcome"] == "operational_success"
                    ),
                    "private_score": row.get("private_score"),
                    "hard_contract_vector": json.dumps(
                        row.get("hard_contract_vector"), separators=(",", ":")
                    ),
                    "transport_attempts": len(row.get("attempts", [])),
                    "total_execution_elapsed_ms": row.get(
                        "total_execution_elapsed_ms"
                    ),
                    "provider_reported_total_tokens": row.get(
                        "provider_reported_total_tokens"
                    ),
                }
            )
        signatures = [
            (
                row["terminal_outcome"],
                row.get("private_score"),
                tuple(row.get("hard_contract_vector") or ()),
            )
            for row in selected
        ]
        successes = [
            row["terminal_outcome"] == "operational_success" for row in selected
        ]
        repeatability = (
            "replicas_agree"
            if signatures[0] == signatures[1]
            else "replicas_disagree"
        )
        if len(set(successes)) == 2:
            source_relation = "reproduces_source_success_discordance"
        elif all(successes):
            source_relation = "both_match_source_success_arm"
        else:
            source_relation = "both_match_source_failure_arm"
        case_rows.append(
            {
                "case_id": case_id,
                "task_id": case["task_id"],
                "block_id": case["block_id"],
                "registry_id": case["registry_id"],
                "final_source": case["final_source"],
                "replica_successes": sum(successes),
                "replica_failures": 2 - sum(successes),
                "repeatability_state": repeatability,
                "source_relation": source_relation,
            }
        )

    counts = Counter(row["terminal_outcome"] for row in results)
    analysis = {
        "schema_version": "effectslice-s06-targeted-analysis.v1",
        "status": "verified_supplementary_repeatability_analysis",
        "scope": {
            "cases": 4,
            "replicas_per_case": 2,
            "terminal_rows": len(results),
            "same_protocol_identity_discordance_only": True,
        },
        "terminal_outcomes": dict(sorted(counts.items())),
        "case_summaries": case_rows,
        "replicas_agree": sum(
            row["repeatability_state"] == "replicas_agree" for row in case_rows
        ),
        "replicas_disagree": sum(
            row["repeatability_state"] == "replicas_disagree"
            for row in case_rows
        ),
        "claim_boundary": (
            "These eight calls are targeted supplementary repeatability evidence. "
            "They do not revise frozen FG3/FG4/FG5 outcomes, repair the registered "
            "controls, or substitute for comprehensive multi-seed evaluation."
        ),
    }
    extended(output_dir).mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "replicate_results.csv",
        list(result_rows[0]),
        result_rows,
    )
    write_csv(
        output_dir / "case_summary.csv",
        list(case_rows[0]),
        case_rows,
    )
    write_json(output_dir / "analysis.json", analysis)
    manifest = {
        "schema_version": "effectslice-s06-targeted-analysis-manifest.v1",
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
            name: sha256_file(output_dir / name)
            for name in (
                "analysis.json",
                "replicate_results.csv",
                "case_summary.csv",
            )
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
