from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT_DIR = HERE / "inputs"
OUTPUT_DIR = HERE / "outputs"
ANALYZER = HERE / "analyze_failure_decomposition.py"
EXTRACTOR = HERE / "extract_failure_evidence.py"
ANALYSIS_OUTPUTS = (
    "failure_decomposition.json",
    "failure_endpoint_summary.csv",
    "failure_final_source_summary.csv",
    "failure_original_class_summary.csv",
    "failure_original_to_endpoint_flow.csv",
    "failure_original_to_source_flow.csv",
    "failure_row_classification.csv",
    "failure_source_to_endpoint_flow.csv",
    "manifest.json",
)
EXTRACTION_OUTPUTS = ("failure_row_evidence_v1.csv", "extraction_manifest.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare_files(expected_dir: Path, actual_dir: Path, names: tuple[str, ...]) -> None:
    mismatches = [
        name
        for name in names
        if (expected_dir / name).read_bytes() != (actual_dir / name).read_bytes()
    ]
    if mismatches:
        raise AssertionError(f"Independent rerun differs for: {mismatches}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_semantics() -> None:
    manifest = json.loads((OUTPUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    if manifest["section"] != "04_failure_decomposition":
        raise AssertionError("Unexpected section identifier.")
    for name, metadata in manifest["outputs"].items():
        if sha256(OUTPUT_DIR / name) != metadata["sha256"]:
            raise AssertionError(f"Output hash mismatch for {name}.")

    result = json.loads(
        (OUTPUT_DIR / "failure_decomposition.json").read_text(encoding="utf-8")
    )
    if result["status"] != "verified_forward_analysis":
        raise AssertionError("Failure decomposition is not marked verified.")
    expected_endpoints = {
        "complete_submission_private_contract_failure": 759,
        "operational_success": 383,
        "submission_or_case_coverage_failure": 154,
    }
    expected_sources = {
        "fg3_retained": 146,
        "fg5_exact_output_direct": 648,
        "integrity_digest_successor": 129,
        "payload_interface_successor": 268,
        "provider_availability_successor": 1,
        "response_format_successor": 104,
    }
    expected_original = {
        "exact_output_contract": 684,
        "experimental_outcome_not_technical_error": 141,
        "integrity_or_digest": 120,
        "operational_success": 5,
        "payload_input_interface": 268,
        "provider_availability": 1,
        "response_format": 77,
    }
    if result["final_endpoint_classes"] != expected_endpoints:
        raise AssertionError("Final endpoint counts changed.")
    if result["final_successor_provenance"] != expected_sources:
        raise AssertionError("Final-source provenance counts changed.")
    if result["original_technical_classes"] != expected_original:
        raise AssertionError("Original routing-class counts changed.")
    if result["score_shortfall_rows"] != 0:
        raise AssertionError("Unexpected score-shortfall rows.")

    rows = read_csv(OUTPUT_DIR / "failure_row_classification.csv")
    if len(rows) != 1296 or len({int(row["global_sequence_index"]) for row in rows}) != 1296:
        raise AssertionError("Row classification does not cover 1,296 unique rows.")
    vector_counts: dict[str, int] = {}
    for row in rows:
        vector_counts[row["hard_contract_vector"]] = (
            vector_counts.get(row["hard_contract_vector"], 0) + 1
        )
    if vector_counts != {"[true,false]": 759, "[true,true]": 383, "[false,false]": 154}:
        raise AssertionError(f"Unexpected scorer-vector counts: {vector_counts}")

    original_to_source = {
        (row["original_technical_class"], row["final_source"]): int(row["rows"])
        for row in read_csv(OUTPUT_DIR / "failure_original_to_source_flow.csv")
    }
    if {
        key: original_to_source[key]
        for key in (
            ("exact_output_contract", "fg5_exact_output_direct"),
            ("exact_output_contract", "integrity_digest_successor"),
            ("exact_output_contract", "response_format_successor"),
        )
    } != {
        ("exact_output_contract", "fg5_exact_output_direct"): 648,
        ("exact_output_contract", "integrity_digest_successor"): 9,
        ("exact_output_contract", "response_format_successor"): 27,
    }:
        raise AssertionError("Exact-output routing-to-source split changed.")


def rerun_analysis() -> None:
    with tempfile.TemporaryDirectory(prefix="effectslice_s04_analysis_") as temp:
        output_dir = Path(temp)
        subprocess.run(
            [sys.executable, str(ANALYZER), "--output-dir", str(output_dir)],
            check=True,
        )
        compare_files(OUTPUT_DIR, output_dir, ANALYSIS_OUTPUTS)


def rerun_extraction() -> None:
    with tempfile.TemporaryDirectory(prefix="effectslice_s04_extract_") as temp:
        output_dir = Path(temp)
        subprocess.run(
            [sys.executable, str(EXTRACTOR), "--output-dir", str(output_dir)],
            check=True,
        )
        compare_files(INPUT_DIR, output_dir, EXTRACTION_OUTPUTS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-source-extraction", action="store_true")
    args = parser.parse_args()
    verify_semantics()
    rerun_analysis()
    if args.require_source_extraction:
        rerun_extraction()
    print("PASS: Section 04 failure decomposition is semantically and byte-for-byte verified.")
    if args.require_source_extraction:
        print("PASS: All 1,296 terminal sources were re-extracted and byte-for-byte matched.")


if __name__ == "__main__":
    main()
