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
        analyze(run_dir, reproduced)
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
    return {
        "status": "PASS",
        "verified_outputs": len(EXPECTED),
        "byte_for_byte_reproduction": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=HERE / "run")
    parser.add_argument("--output-dir", type=Path, default=HERE / "outputs")
    args = parser.parse_args()
    print(json.dumps(verify(args.run_dir, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
