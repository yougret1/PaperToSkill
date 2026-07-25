from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FORWARD_ROOT = HERE.parent
DEFAULT_OVERLAY = FORWARD_ROOT / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_OUTPUT = HERE / "inputs"
EXPECTED_OVERLAY_SHA256 = "ceb2c4f81c5f5dcaef697a7a40c6f9bfecd264f52cfa959190bcb8b9169a85c1"
FIELDS = (
    "global_sequence_index",
    "hard_contract_vector",
    "result_source_sha256",
    "source_endpoint_verified",
)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Could not locate repository root.")


REPO_ROOT = find_repo_root(HERE)


def extended_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


def read_bytes(path: Path) -> bytes:
    with open(extended_path(path), "rb") as handle:
        return handle.read()


def sha256(path: Path) -> str:
    return hashlib.sha256(read_bytes(path)).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def resolve_result_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def extract(overlay_path: Path, output_dir: Path) -> None:
    overlay_sha = sha256(overlay_path)
    if overlay_sha != EXPECTED_OVERLAY_SHA256:
        raise ValueError("Unexpected terminal-row overlay hash.")
    overlay = json.loads(read_bytes(overlay_path).decode("utf-8-sig"))
    records = overlay["records"]
    indices = [int(row["global_sequence_index"]) for row in records]
    if len(records) != 1296 or sorted(indices) != list(range(1, 1297)):
        raise ValueError("Terminal overlay must contain unique rows 1..1296.")

    evidence: list[dict[str, Any]] = []
    source_pairs: list[dict[str, Any]] = []
    vector_counts: Counter[str] = Counter()
    for row in sorted(records, key=lambda item: int(item["global_sequence_index"])):
        index = int(row["global_sequence_index"])
        result_path = resolve_result_path(row["result_source_path"])
        result_bytes = read_bytes(result_path)
        observed_sha = sha256_bytes(result_bytes)
        if observed_sha != row["result_source_sha256"]:
            raise ValueError(f"Result-source hash mismatch at row {index}.")
        result = json.loads(result_bytes.decode("utf-8-sig"))
        vector = result.get("hard_contract_vector")
        if vector not in ([True, True], [True, False], [False, False]):
            raise ValueError(f"Unexpected hard-contract vector at row {index}: {vector}")
        if float(result["private_score"]) != float(row["private_score"]):
            raise ValueError(f"Private-score mismatch at row {index}.")
        if result["terminal_outcome"] != row["terminal_outcome"]:
            raise ValueError(f"Terminal-outcome mismatch at row {index}.")
        expected_success = vector == [True, True] and float(row["private_score"]) >= 0.90
        if bool(row["operational_success"]) != expected_success:
            raise ValueError(f"Operational-success mismatch at row {index}.")

        vector_text = json.dumps(vector, separators=(",", ":"))
        vector_counts[vector_text] += 1
        evidence.append(
            {
                "global_sequence_index": index,
                "hard_contract_vector": vector_text,
                "result_source_sha256": observed_sha,
                "source_endpoint_verified": True,
            }
        )
        source_pairs.append(
            {"global_sequence_index": index, "result_source_sha256": observed_sha}
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / "failure_row_evidence_v1.csv"
    with evidence_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(evidence)
    aggregate = json.dumps(source_pairs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest = {
        "schema_version": "effectslice-failure-evidence-extraction-manifest.v1",
        "status": "hash_verified_extraction",
        "sources": {"../inputs/terminal_row_overlay_v1.json": overlay_sha},
        "raw_result_sources": {
            "verified_files": 1296,
            "index_and_sha256_aggregate": sha256_bytes(aggregate),
            "final_source_counts": dict(
                sorted(Counter(row["final_source"] for row in records).items())
            ),
        },
        "hard_contract_vector_counts": dict(sorted(vector_counts.items())),
        "outputs": {evidence_path.name: sha256(evidence_path)},
    }
    write_json(output_dir / "extraction_manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    extract(args.overlay, args.output_dir)


if __name__ == "__main__":
    main()
