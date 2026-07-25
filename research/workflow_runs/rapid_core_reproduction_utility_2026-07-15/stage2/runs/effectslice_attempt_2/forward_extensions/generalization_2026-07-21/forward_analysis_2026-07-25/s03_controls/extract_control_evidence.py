from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
FORWARD_ROOT = HERE.parent
GENERALIZATION_ROOT = FORWARD_ROOT.parent
DEFAULT_OVERLAY = FORWARD_ROOT / "inputs" / "terminal_row_overlay_v1.json"
DEFAULT_SCHEDULE = (
    GENERALIZATION_ROOT
    / "materialization_remote_only_2026-07-23"
    / "global_remote_schedule.json"
)
DEFAULT_PREREGISTRATION = (
    GENERALIZATION_ROOT
    / "preregistration_remote_only_2026-07-22"
    / "experiment_plan.json"
)
DEFAULT_TASK_ROOT = GENERALIZATION_ROOT / "materialization_remote_only_2026-07-23" / "tasks"
DEFAULT_OUTPUT = HERE / "inputs"
EXPECTED_OVERLAY_SHA256 = "ceb2c4f81c5f5dcaef697a7a40c6f9bfecd264f52cfa959190bcb8b9169a85c1"
EXPECTED_TASKS = ("AGENT-TF-01", "DATA-HDB-01", "NLP-LLM-01", "SE-PE-01")
EXPECTED_VARIANTS = (
    "byte_identical_identity",
    "destructive_core_negative",
    "planted_redundancy_positive",
)
SCORER_VECTOR_SEMANTICS = ("complete", "all_private_cases_pass")
TARGET_BINDING_KEYS = {
    "destructive_target_hard_contract_id",
    "destructive_target_hard_contract_ids",
    "target_hard_contract_id",
    "target_hard_contract_ids",
    "targeted_hard_contract_id",
    "targeted_hard_contract_ids",
}
LEDGER_FIELDS = [
    "block_id",
    "candidate_artifact_sha256",
    "candidate_id",
    "canonical_model_visible_payload_sha256",
    "canonical_output_sha256",
    "condition",
    "domain",
    "final_source",
    "global_sequence_index",
    "hard_contract_vector",
    "operational_success",
    "paper_id",
    "private_score",
    "raw_response_sha256",
    "registry_id",
    "result_source_sha256",
    "row_valid",
    "task_id",
    "terminal_outcome",
    "variant_id",
]


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Could not locate the repository root.")


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


def read_json(path: Path) -> Any:
    return json.loads(read_bytes(path).decode("utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(read_bytes(path)).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def portable_reference(path: Path) -> str:
    resolved = path.resolve()
    for base, prefix in (
        (FORWARD_ROOT.resolve(), "forward_analysis"),
        (GENERALIZATION_ROOT.resolve(), "generalization"),
        (REPO_ROOT.resolve(), "repository"),
    ):
        try:
            return f"{prefix}/{resolved.relative_to(base).as_posix()}"
        except ValueError:
            continue
    return str(resolved)


def resolve_result_path(value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def nested_target_markers(payload: Any, prefix: str = "") -> list[str]:
    markers: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            location = f"{prefix}.{key}" if prefix else key
            if key.lower() in TARGET_BINDING_KEYS:
                markers.append(location)
            markers.extend(nested_target_markers(value, location))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            markers.extend(nested_target_markers(value, f"{prefix}[{index}]"))
    return markers


def extract_binding_evidence(
    task_root: Path, task_ids: list[str], control_vectors: dict[str, set[tuple[bool, ...]]]
) -> dict[str, Any]:
    audits: list[dict[str, Any]] = []
    source_files: dict[str, str] = {}
    for task_id in task_ids:
        root = task_root / task_id
        scorer_manifest_path = root / "scorer_manifest.json"
        candidate_manifest_path = root / "candidate_manifest.json"
        atom_registry_path = root / "atom_registry.json"
        semantic_audit_path = root / "semantic_audit.json"
        scorer_manifest = read_json(scorer_manifest_path)
        candidate_manifest = read_json(candidate_manifest_path)
        atom_registry = read_json(atom_registry_path)
        semantic_audit = read_json(semantic_audit_path)

        scorer_path = root / scorer_manifest["implementation_path"]
        scorer_source = read_bytes(scorer_path).decode("utf-8")
        if sha256(scorer_path) != scorer_manifest["implementation_sha256"]:
            raise ValueError(f"Scorer implementation hash mismatch for {task_id}.")
        if "[complete, passed == len(expected_by_id)]" not in scorer_source:
            raise ValueError(f"Unexpected scorer-vector implementation for {task_id}.")

        negative_candidates = [
            row for row in candidate_manifest["candidates"] if row["candidate_id"] == "control_negative"
        ]
        if len(negative_candidates) != 1:
            raise ValueError(f"Expected one control_negative candidate for {task_id}.")
        negative_candidate = negative_candidates[0]
        construction_log_path = root / negative_candidate["construction_log_path"]
        construction_log = read_json(construction_log_path)
        if sha256(construction_log_path) != negative_candidate["construction_log_sha256"]:
            raise ValueError(f"Negative-control construction-log hash mismatch for {task_id}.")
        atom_by_id = {row["atom_id"]: row for row in atom_registry["atoms"]}
        retained_atoms = [atom_by_id[atom_id] for atom_id in negative_candidate["atom_ids"]]
        marker_locations = sorted(
            set(
                nested_target_markers(negative_candidate, "candidate_manifest.control_negative")
                + nested_target_markers(construction_log, "construction_log.control_negative")
                + nested_target_markers(retained_atoms, "atom_registry.retained_atoms")
                + nested_target_markers(scorer_manifest, "scorer_manifest")
                + nested_target_markers(semantic_audit, "semantic_audit")
            )
        )
        observed_vectors = sorted(control_vectors[task_id])
        observed_lengths = sorted({len(vector) for vector in observed_vectors})
        source_files.update(
            {
                portable_reference(scorer_manifest_path): sha256(scorer_manifest_path),
                portable_reference(candidate_manifest_path): sha256(candidate_manifest_path),
                portable_reference(atom_registry_path): sha256(atom_registry_path),
                portable_reference(construction_log_path): sha256(construction_log_path),
                portable_reference(semantic_audit_path): sha256(semantic_audit_path),
                portable_reference(scorer_path): sha256(scorer_path),
            }
        )
        audits.append(
            {
                "task_id": task_id,
                "scorer_manifest_hard_contract_ids": scorer_manifest["hard_contract_ids"],
                "scorer_vector_semantics": list(SCORER_VECTOR_SEMANTICS),
                "observed_vector_length": observed_lengths,
                "target_binding_marker_locations": marker_locations,
                "target_binding_available": bool(marker_locations),
                "registered_target_count_is_computable": bool(marker_locations),
            }
        )
    return {
        "schema_version": "effectslice-control-binding-evidence.v1",
        "audit_scope": (
            "control_negative candidate and construction log, its retained atoms, semantic "
            "audit, scorer manifest, and scorer implementation"
        ),
        "audits": audits,
        "source_files": dict(sorted(source_files.items())),
    }


def extract(
    overlay_path: Path,
    schedule_path: Path,
    preregistration_path: Path,
    task_root: Path,
    output_dir: Path,
) -> None:
    if sha256(overlay_path) != EXPECTED_OVERLAY_SHA256:
        raise ValueError("The terminal-row overlay hash is not the frozen analysis input.")
    overlay = read_json(overlay_path)
    schedule = read_json(schedule_path)
    preregistration = read_json(preregistration_path)
    records = overlay["records"]
    schedule_rows = schedule["rows"]
    if len(records) != 1296 or len(schedule_rows) != 1296:
        raise ValueError("Overlay and schedule must each contain 1,296 rows.")

    overlay_by_index = {int(row["global_sequence_index"]): row for row in records}
    schedule_by_index = {int(row["global_sequence_index"]): row for row in schedule_rows}
    expected_indices = set(range(1, 1297))
    if set(overlay_by_index) != expected_indices or set(schedule_by_index) != expected_indices:
        raise ValueError("Overlay and schedule indices must each be unique and cover 1..1296.")

    control_schedule = [row for row in schedule_rows if row["execution_family"] == "controls"]
    if len(control_schedule) != 144:
        raise ValueError(f"Expected 144 registered control rows, observed {len(control_schedule)}.")
    controls_registration = preregistration["secondary_experiments"]["controls"]
    if controls_registration["remote_conversations"] != 144:
        raise ValueError("Preregistered control-row count is not 144.")
    if tuple(sorted(controls_registration["conditions"])) != tuple(sorted(EXPECTED_VARIANTS)):
        raise ValueError("Preregistered control variants do not match the frozen set.")

    ledger: list[dict[str, Any]] = []
    raw_source_pairs: list[dict[str, Any]] = []
    control_vectors: dict[str, set[tuple[bool, ...]]] = defaultdict(set)
    for scheduled in sorted(control_schedule, key=lambda row: int(row["global_sequence_index"])):
        index = int(scheduled["global_sequence_index"])
        final = overlay_by_index[index]
        identity_fields = (
            "block_id",
            "candidate_id",
            "condition",
            "derived_seed",
            "domain",
            "execution_family",
            "model_slot_id",
            "paper_id",
            "registry_id",
            "task_id",
            "variant_id",
        )
        mismatches = [field for field in identity_fields if scheduled.get(field) != final.get(field)]
        if mismatches:
            raise ValueError(f"Schedule/overlay identity mismatch at row {index}: {mismatches}")

        result_path = resolve_result_path(final["result_source_path"])
        result_bytes = read_bytes(result_path)
        observed_result_sha = sha256_bytes(result_bytes)
        if observed_result_sha != final["result_source_sha256"]:
            raise ValueError(f"Final result-source hash mismatch at row {index}.")
        result = json.loads(result_bytes.decode("utf-8-sig"))
        vector = result.get("hard_contract_vector")
        if not isinstance(vector, list) or not vector or not all(isinstance(value, bool) for value in vector):
            raise ValueError(f"Missing or invalid hard-contract vector at row {index}.")
        if float(result["private_score"]) != float(final["private_score"]):
            raise ValueError(f"Private-score mismatch at row {index}.")
        if result["terminal_outcome"] != final["terminal_outcome"]:
            raise ValueError(f"Terminal-outcome mismatch at row {index}.")

        row_valid = result.get("row_valid")
        if row_valid is None:
            row_valid = (
                result.get("terminal_outcome") in {"operational_success", "hard_contract_failure"}
                and result.get("private_score") is not None
                and result.get("canonical_output_sha256") is not None
                and result.get("raw_response_sha256") is not None
            )
        control_vectors[scheduled["task_id"]].add(tuple(vector))
        ledger.append(
            {
                "block_id": int(scheduled["block_id"]),
                "candidate_artifact_sha256": scheduled["candidate_artifact_sha256"],
                "candidate_id": scheduled["candidate_id"],
                "canonical_model_visible_payload_sha256": scheduled[
                    "canonical_model_visible_payload_sha256"
                ],
                "canonical_output_sha256": result.get("canonical_output_sha256"),
                "condition": scheduled["condition"],
                "domain": scheduled["domain"],
                "final_source": final["final_source"],
                "global_sequence_index": index,
                "hard_contract_vector": json.dumps(vector, separators=(",", ":")),
                "operational_success": int(bool(final["operational_success"])),
                "paper_id": scheduled["paper_id"],
                "private_score": float(final["private_score"]),
                "raw_response_sha256": result.get("raw_response_sha256"),
                "registry_id": scheduled["registry_id"],
                "result_source_sha256": observed_result_sha,
                "row_valid": bool(row_valid),
                "task_id": scheduled["task_id"],
                "terminal_outcome": final["terminal_outcome"],
                "variant_id": scheduled["variant_id"],
            }
        )
        raw_source_pairs.append(
            {"global_sequence_index": index, "result_source_sha256": observed_result_sha}
        )

    tasks = sorted({row["task_id"] for row in ledger})
    variants = sorted({row["variant_id"] for row in ledger})
    if tuple(tasks) != EXPECTED_TASKS or tuple(variants) != tuple(sorted(EXPECTED_VARIANTS)):
        raise ValueError(f"Unexpected control scope: tasks={tasks}, variants={variants}.")
    cell_counts = Counter((row["task_id"], row["variant_id"]) for row in ledger)
    if set(cell_counts.values()) != {12} or len(cell_counts) != 12:
        raise ValueError("Every task-control cell must contain 12 rows (six paired blocks).")

    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "control_row_evidence_v1.csv"
    binding_path = output_dir / "control_binding_evidence_v1.json"
    write_csv(ledger_path, LEDGER_FIELDS, ledger)
    binding_evidence = extract_binding_evidence(task_root, tasks, control_vectors)
    write_json(binding_path, binding_evidence)

    source_aggregate = json.dumps(
        raw_source_pairs, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    manifest = {
        "schema_version": "effectslice-control-evidence-extraction-manifest.v1",
        "status": "hash_verified_extraction",
        "design": {
            "rows": 144,
            "tasks": 4,
            "variants": 3,
            "blocks_per_task_variant": 6,
            "rows_per_block": 2,
        },
        "sources": {
            portable_reference(overlay_path): sha256(overlay_path),
            portable_reference(schedule_path): sha256(schedule_path),
            portable_reference(preregistration_path): sha256(preregistration_path),
            **binding_evidence["source_files"],
        },
        "raw_result_sources": {
            "verified_files": len(raw_source_pairs),
            "index_and_sha256_aggregate": sha256_bytes(source_aggregate),
            "final_source_counts": dict(sorted(Counter(row["final_source"] for row in ledger).items())),
        },
        "outputs": {
            ledger_path.name: sha256(ledger_path),
            binding_path.name: sha256(binding_path),
        },
    }
    write_json(output_dir / "extraction_manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--schedule", type=Path, default=DEFAULT_SCHEDULE)
    parser.add_argument("--preregistration", type=Path, default=DEFAULT_PREREGISTRATION)
    parser.add_argument("--task-root", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    extract(args.overlay, args.schedule, args.preregistration, args.task_root, args.output_dir)


if __name__ == "__main__":
    main()
