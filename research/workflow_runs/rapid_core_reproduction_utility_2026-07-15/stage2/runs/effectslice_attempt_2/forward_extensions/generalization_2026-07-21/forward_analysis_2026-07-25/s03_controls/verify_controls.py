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
OUTPUT_DIR = HERE / "outputs"
INPUT_DIR = HERE / "inputs"
ANALYZER = HERE / "analyze_controls.py"
EXTRACTOR = HERE / "extract_control_evidence.py"
ANALYSIS_OUTPUTS = (
    "control_analysis.json",
    "control_task_states.csv",
    "destructive_target_binding_audit.csv",
    "manifest.json",
)
EXTRACTION_OUTPUTS = (
    "control_row_evidence_v1.csv",
    "control_binding_evidence_v1.json",
    "extraction_manifest.json",
)


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


def verify_semantics() -> None:
    manifest = json.loads((OUTPUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    if manifest["section"] != "03_controls":
        raise AssertionError("Unexpected analysis section in manifest.")
    for name, metadata in manifest["outputs"].items():
        if sha256(OUTPUT_DIR / name) != metadata["sha256"]:
            raise AssertionError(f"Output hash mismatch for {name}.")

    analysis = json.loads((OUTPUT_DIR / "control_analysis.json").read_text(encoding="utf-8"))
    if analysis["status"] != "verified_forward_analysis":
        raise AssertionError("Controls analysis is not marked verified.")
    expected_counts = {
        "planted_redundancy_positive": {"SanityPass": 1, "SanityFail": 3, "Invalid": 0},
        "byte_identical_identity": {"SanityPass": 1, "SanityFail": 3, "Invalid": 0},
        "destructive_core_negative": {"SanityPass": 0, "SanityFail": 0, "Invalid": 4},
    }
    if analysis["state_counts"] != expected_counts:
        raise AssertionError(f"Unexpected control-state counts: {analysis['state_counts']}")

    rows = analysis["task_results"]
    positive_passes = sorted(
        row["task_id"]
        for row in rows
        if row["variant_id"] == "planted_redundancy_positive"
        and row["state"] == "SanityPass"
    )
    identity_passes = sorted(
        row["task_id"]
        for row in rows
        if row["variant_id"] == "byte_identical_identity"
        and row["state"] == "SanityPass"
    )
    if positive_passes != ["NLP-LLM-01"]:
        raise AssertionError(f"Unexpected positive-control passes: {positive_passes}")
    if identity_passes != ["DATA-HDB-01"]:
        raise AssertionError(f"Unexpected identity-control passes: {identity_passes}")
    if any(
        row["state"] != "Invalid" or row["targeted_hard_contract_failures"] is not None
        for row in rows
        if row["variant_id"] == "destructive_core_negative"
    ):
        raise AssertionError("Destructive controls must remain Invalid without targeted counts.")
    if any(row["target_binding_available"] for row in analysis["destructive_target_binding_audit"]):
        raise AssertionError("A destructive target binding was unexpectedly claimed.")
    if any(
        row["observed_vector_length"] != [2]
        or row["scorer_vector_semantics"] != ["complete", "all_private_cases_pass"]
        for row in analysis["destructive_target_binding_audit"]
    ):
        raise AssertionError("Scorer-vector semantics are not the frozen aggregate two-vector.")
    if "confusion_matrix" not in analysis["interpretation"]:
        raise AssertionError("The no-confusion-matrix boundary is missing.")

    with (OUTPUT_DIR / "control_task_states.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        state_rows = list(csv.DictReader(handle))
    if len(state_rows) != 12:
        raise AssertionError("Control state table must contain twelve task-control rows.")


def rerun_analysis() -> None:
    with tempfile.TemporaryDirectory(prefix="effectslice_s03_analysis_") as temp:
        output_dir = Path(temp)
        subprocess.run(
            [sys.executable, str(ANALYZER), "--output-dir", str(output_dir)],
            check=True,
        )
        compare_files(OUTPUT_DIR, output_dir, ANALYSIS_OUTPUTS)


def rerun_extraction() -> None:
    with tempfile.TemporaryDirectory(prefix="effectslice_s03_extract_") as temp:
        output_dir = Path(temp)
        subprocess.run(
            [sys.executable, str(EXTRACTOR), "--output-dir", str(output_dir)],
            check=True,
        )
        compare_files(INPUT_DIR, output_dir, EXTRACTION_OUTPUTS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-source-extraction",
        action="store_true",
        help="Also re-read and hash-check all 144 raw result sources.",
    )
    args = parser.parse_args()
    verify_semantics()
    rerun_analysis()
    if args.require_source_extraction:
        rerun_extraction()
    print("PASS: Section 03 controls outputs are semantically and byte-for-byte verified.")
    if args.require_source_extraction:
        print("PASS: All 144 source rows were re-extracted and byte-for-byte matched.")


if __name__ == "__main__":
    main()
