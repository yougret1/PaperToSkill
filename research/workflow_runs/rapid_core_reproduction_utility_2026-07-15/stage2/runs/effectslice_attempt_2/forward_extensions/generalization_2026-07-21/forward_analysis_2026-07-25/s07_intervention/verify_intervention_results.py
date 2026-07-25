from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from analyze_intervention_successor import analyze
from intervention_successor import HERE, extended, sha256_file


EXPECTED = (
    "analysis.json",
    "row_results.csv",
    "arm_summary.csv",
    "domain_arm_summary.csv",
    "contrast_units.csv",
    "contrast_summary.csv",
    "token_balance.csv",
    "manifest.json",
)


def verify(run_dir: Path, output_dir: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="effectslice-s07-verify-") as temp:
        reproduced = Path(temp)
        analysis = analyze(run_dir, reproduced)
        mismatches = [
            name
            for name in EXPECTED
            if not extended(output_dir / name).is_file()
            or sha256_file(reproduced / name) != sha256_file(output_dir / name)
        ]
    if mismatches:
        raise RuntimeError(
            f"independent reproduction mismatch: {mismatches}"
        )
    expected_outcomes = {
        "hard_contract_failure": 23,
        "malformed_or_no_submission": 2,
        "operational_success": 23,
    }
    if analysis["terminal_outcomes"] != expected_outcomes:
        raise RuntimeError(
            f"terminal outcome mismatch: {analysis['terminal_outcomes']}"
        )
    invalid_details = analysis["technical_or_invalid_details"]
    if len(invalid_details) != 2 or any(
        row["provider_finish_reason"] != "length"
        or row["canonical_output_bytes"] != 0
        or not row["response_exhausted_before_submission"]
        for row in invalid_details
    ):
        raise RuntimeError(
            f"unexpected technical/invalid detail: {invalid_details}"
        )
    valid_units = {
        row["contrast_id"]: row["valid_units"]
        for row in analysis["contrast_summaries"]
    }
    expected_valid_units = {
        "critical_necessity": 7,
        "noncritical_necessity": 7,
        "critical_rescue": 8,
        "noncritical_rescue": 8,
    }
    if valid_units != expected_valid_units:
        raise RuntimeError(f"valid-pair unit mismatch: {valid_units}")
    return {
        "status": "PASS",
        "verified_outputs": len(EXPECTED),
        "byte_for_byte_reproduction": True,
        "terminal_rows": sum(expected_outcomes.values()),
        "technical_or_invalid_rows": len(invalid_details),
        "itt_and_valid_pair_contract": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=HERE / "run")
    parser.add_argument("--output-dir", type=Path, default=HERE / "outputs")
    args = parser.parse_args()
    print(json.dumps(verify(args.run_dir, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
