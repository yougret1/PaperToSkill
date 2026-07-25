from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_OVERLAY = HERE.parent / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_EVIDENCE = HERE / "inputs" / "failure_row_evidence_v1.csv"
DEFAULT_EXTRACTION_MANIFEST = HERE / "inputs" / "extraction_manifest.json"
DEFAULT_OUTPUT = HERE / "outputs"
ROW_FIELDS = (
    "condition",
    "domain",
    "execution_family",
    "final_endpoint_class",
    "final_source",
    "global_sequence_index",
    "hard_contract_vector",
    "model_slot_id",
    "original_technical_class",
    "paper_id",
    "private_score",
    "result_source_sha256",
    "task_id",
    "terminal_outcome",
    "variant_id",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def portable_reference(path: Path) -> str:
    try:
        return path.resolve().relative_to(HERE.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def classify(vector: list[bool], private_score: float) -> str:
    if vector == [True, True]:
        if private_score >= 0.90:
            return "operational_success"
        return "score_shortfall"
    if vector == [True, False]:
        return "complete_submission_private_contract_failure"
    if vector == [False, False]:
        return "submission_or_case_coverage_failure"
    raise ValueError(f"Unsupported hard-contract vector: {vector}")


def counter_rows(counter: Counter[Any], names: tuple[str, ...]) -> list[dict[str, Any]]:
    return [dict(zip(names, key if isinstance(key, tuple) else (key,)), rows=count) for key, count in sorted(counter.items())]


def analyze(
    overlay_path: Path,
    evidence_path: Path,
    extraction_manifest_path: Path,
    output_dir: Path,
) -> None:
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    records = overlay["records"]
    if len(records) != 1296:
        raise ValueError("Expected 1,296 overlay records.")
    extraction_manifest = json.loads(
        extraction_manifest_path.read_text(encoding="utf-8")
    )
    if extraction_manifest["status"] != "hash_verified_extraction":
        raise ValueError("Failure evidence is not hash-verified.")
    if extraction_manifest["outputs"][evidence_path.name] != sha256(evidence_path):
        raise ValueError("Failure-evidence hash mismatch.")

    evidence_by_index: dict[int, dict[str, Any]] = {}
    with evidence_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            index = int(row["global_sequence_index"])
            evidence_by_index[index] = {
                "hard_contract_vector": json.loads(row["hard_contract_vector"]),
                "result_source_sha256": row["result_source_sha256"],
                "source_endpoint_verified": row["source_endpoint_verified"] == "True",
            }
    if len(evidence_by_index) != 1296 or set(evidence_by_index) != set(range(1, 1297)):
        raise ValueError("Failure evidence must cover unique rows 1..1296.")

    classified: list[dict[str, Any]] = []
    for row in sorted(records, key=lambda item: int(item["global_sequence_index"])):
        index = int(row["global_sequence_index"])
        evidence = evidence_by_index[index]
        if not evidence["source_endpoint_verified"]:
            raise ValueError(f"Unverified source endpoint at row {index}.")
        if evidence["result_source_sha256"] != row["result_source_sha256"]:
            raise ValueError(f"Overlay/evidence source-hash mismatch at row {index}.")
        endpoint = classify(evidence["hard_contract_vector"], float(row["private_score"]))
        expected_success = endpoint == "operational_success"
        if bool(row["operational_success"]) != expected_success:
            raise ValueError(f"Endpoint/success mismatch at row {index}.")
        classified.append(
            {
                "condition": row["condition"],
                "domain": row["domain"],
                "execution_family": row["execution_family"],
                "final_endpoint_class": endpoint,
                "final_source": row["final_source"],
                "global_sequence_index": index,
                "hard_contract_vector": json.dumps(
                    evidence["hard_contract_vector"], separators=(",", ":")
                ),
                "model_slot_id": row["model_slot_id"],
                "original_technical_class": row["technical_classification"],
                "paper_id": row["paper_id"],
                "private_score": float(row["private_score"]),
                "result_source_sha256": row["result_source_sha256"],
                "task_id": row["task_id"],
                "terminal_outcome": row["terminal_outcome"],
                "variant_id": row["variant_id"],
            }
        )

    endpoint_counts = Counter(row["final_endpoint_class"] for row in classified)
    source_counts = Counter(row["final_source"] for row in classified)
    original_counts = Counter(row["original_technical_class"] for row in classified)
    original_to_endpoint = Counter(
        (row["original_technical_class"], row["final_endpoint_class"])
        for row in classified
    )
    original_to_source = Counter(
        (row["original_technical_class"], row["final_source"]) for row in classified
    )
    source_to_endpoint = Counter(
        (row["final_source"], row["final_endpoint_class"]) for row in classified
    )
    if endpoint_counts.get("score_shortfall", 0) != 0:
        raise ValueError("Observed a score-shortfall row contrary to frozen evidence.")
    if endpoint_counts != {
        "complete_submission_private_contract_failure": 759,
        "operational_success": 383,
        "submission_or_case_coverage_failure": 154,
    }:
        raise ValueError(f"Unexpected final endpoint counts: {endpoint_counts}")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "failure_row_classification.csv", ROW_FIELDS, classified)
    write_csv(
        output_dir / "failure_endpoint_summary.csv",
        ("final_endpoint_class", "rows"),
        counter_rows(endpoint_counts, ("final_endpoint_class",)),
    )
    write_csv(
        output_dir / "failure_final_source_summary.csv",
        ("final_source", "rows"),
        counter_rows(source_counts, ("final_source",)),
    )
    write_csv(
        output_dir / "failure_original_class_summary.csv",
        ("original_technical_class", "rows"),
        counter_rows(original_counts, ("original_technical_class",)),
    )
    write_csv(
        output_dir / "failure_original_to_endpoint_flow.csv",
        ("final_endpoint_class", "original_technical_class", "rows"),
        [
            {
                "final_endpoint_class": endpoint,
                "original_technical_class": original,
                "rows": count,
            }
            for (original, endpoint), count in sorted(original_to_endpoint.items())
        ],
    )
    write_csv(
        output_dir / "failure_original_to_source_flow.csv",
        ("final_source", "original_technical_class", "rows"),
        [
            {
                "final_source": source,
                "original_technical_class": original,
                "rows": count,
            }
            for (original, source), count in sorted(original_to_source.items())
        ],
    )
    write_csv(
        output_dir / "failure_source_to_endpoint_flow.csv",
        ("final_endpoint_class", "final_source", "rows"),
        [
            {"final_endpoint_class": endpoint, "final_source": source, "rows": count}
            for (source, endpoint), count in sorted(source_to_endpoint.items())
        ],
    )

    result = {
        "schema_version": "effectslice-failure-decomposition.v1",
        "status": "verified_forward_analysis",
        "registered_rows": 1296,
        "original_technical_classes": dict(sorted(original_counts.items())),
        "final_successor_provenance": dict(sorted(source_counts.items())),
        "final_endpoint_classes": dict(sorted(endpoint_counts.items())),
        "score_shortfall_rows": 0,
        "flow_tables": {
            "original_to_endpoint": "failure_original_to_endpoint_flow.csv",
            "original_to_source": "failure_original_to_source_flow.csv",
            "source_to_endpoint": "failure_source_to_endpoint_flow.csv",
        },
        "definitions": {
            "original_technical_class": (
                "The diagnosis that routed the frozen FG3 row; it is not the final model outcome."
            ),
            "final_source": (
                "The retained or forward-successor record supplying the single terminal result."
            ),
            "operational_success": (
                "Both aggregate scorer-vector entries are true and private score is at least 0.90."
            ),
            "complete_submission_private_contract_failure": (
                "Final scorer vector is [true,false]: complete case coverage, but at least one "
                "private expected result fails."
            ),
            "submission_or_case_coverage_failure": (
                "Final scorer vector is [false,false]: the task-specific case set or executable "
                "coverage is incomplete. This is broader than no-patch."
            ),
            "score_shortfall": (
                "All aggregate hard-contract entries pass but private score is below 0.90; "
                "the observed count is zero."
            ),
            "no_patch": (
                "Not a cross-domain registered endpoint and not separately identifiable from "
                "the common aggregate scorer vector; no count is reported."
            ),
        },
        "interpretation": (
            "Response-format, integrity/digest, payload/interface, provider-availability, and "
            "exact-output are original routing or final-source provenance classes. After forward "
            "repairs, final outcomes are 383 operational successes, 154 incomplete-coverage "
            "failures, and 759 complete-submission private-contract failures."
        ),
    }
    write_json(output_dir / "failure_decomposition.json", result)

    output_names = (
        "failure_decomposition.json",
        "failure_endpoint_summary.csv",
        "failure_final_source_summary.csv",
        "failure_original_class_summary.csv",
        "failure_original_to_endpoint_flow.csv",
        "failure_original_to_source_flow.csv",
        "failure_row_classification.csv",
        "failure_source_to_endpoint_flow.csv",
    )
    manifest = {
        "schema_version": "effectslice-forward-analysis-manifest.v1",
        "section": "04_failure_decomposition",
        "inputs": {
            portable_reference(overlay_path): sha256(overlay_path),
            portable_reference(evidence_path): sha256(evidence_path),
            portable_reference(extraction_manifest_path): sha256(extraction_manifest_path),
        },
        "runtime": {"python": platform.python_version()},
        "parameters": {
            "success_threshold": 0.90,
            "endpoint_vector_semantics": ["complete", "all_private_cases_pass"],
            "no_patch_is_not_identifiable": True,
        },
        "outputs": {name: {"sha256": sha256(output_dir / name)} for name in output_names},
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument(
        "--extraction-manifest", type=Path, default=DEFAULT_EXTRACTION_MANIFEST
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.overlay, args.evidence, args.extraction_manifest, args.output_dir)


if __name__ == "__main__":
    main()
