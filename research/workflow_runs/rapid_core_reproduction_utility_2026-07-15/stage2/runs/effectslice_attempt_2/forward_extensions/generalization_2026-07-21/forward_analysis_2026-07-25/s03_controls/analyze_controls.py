from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_LEDGER = HERE / "inputs" / "control_row_evidence_v1.csv"
DEFAULT_BINDING = HERE / "inputs" / "control_binding_evidence_v1.json"
DEFAULT_EXTRACTION_MANIFEST = HERE / "inputs" / "extraction_manifest.json"
DEFAULT_OUTPUT = HERE / "outputs"
EXPECTED_TASKS = ("AGENT-TF-01", "DATA-HDB-01", "NLP-LLM-01", "SE-PE-01")
EXPECTED_VARIANTS = (
    "byte_identical_identity",
    "destructive_core_negative",
    "planted_redundancy_positive",
)
STATE_FIELDS = [
    "candidate_C_successes",
    "candidate_any_hard_contract_failures",
    "canonical_output_equalities",
    "domain",
    "failed_gates",
    "hard_contract_vector_agreements",
    "input_digest_matches",
    "operational_success_agreements",
    "paper_id",
    "raw_response_equalities",
    "reference_F_successes",
    "registered_pairs",
    "required_rows_valid",
    "score_delta_within_0_05",
    "state",
    "target_binding_available",
    "targeted_hard_contract_failures",
    "task_id",
    "valid_margin_pairs",
    "variant_id",
]
BINDING_FIELDS = [
    "descriptive_proxy_any_hard_contract_failures",
    "observed_vector_length",
    "paper_id",
    "registered_target_count_is_computable",
    "scorer_manifest_hard_contract_ids",
    "scorer_vector_semantics",
    "target_binding_available",
    "target_binding_marker_locations",
    "task_id",
]


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


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
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


def as_bool(value: str) -> bool:
    if value in {"True", "true", "1"}:
        return True
    if value in {"False", "false", "0"}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def load_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row = dict(raw)
            row["block_id"] = int(row["block_id"])
            row["global_sequence_index"] = int(row["global_sequence_index"])
            row["hard_contract_vector"] = json.loads(row["hard_contract_vector"])
            row["operational_success"] = as_bool(row["operational_success"])
            row["private_score"] = float(row["private_score"])
            row["row_valid"] = as_bool(row["row_valid"])
            rows.append(row)
    if len(rows) != 144:
        raise ValueError(f"Expected 144 control rows, observed {len(rows)}.")
    if len({row["global_sequence_index"] for row in rows}) != 144:
        raise ValueError("Control evidence contains duplicate global sequence indices.")
    tasks = tuple(sorted({row["task_id"] for row in rows}))
    variants = tuple(sorted({row["variant_id"] for row in rows}))
    if tasks != EXPECTED_TASKS or variants != tuple(sorted(EXPECTED_VARIANTS)):
        raise ValueError(f"Unexpected controls scope: tasks={tasks}, variants={variants}.")
    return rows


def pair_rows(rows: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    by_block: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_block[row["block_id"]].append(row)
    if set(by_block) != set(range(1, 7)):
        raise ValueError("Each control task-variant cell must cover blocks 1..6.")
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for block_id in sorted(by_block):
        block_rows = by_block[block_id]
        if len(block_rows) != 2 or {row["condition"] for row in block_rows} != {"F", "C"}:
            raise ValueError(f"Block {block_id} is not one registered F/C pair.")
        reference = next(row for row in block_rows if row["condition"] == "F")
        candidate = next(row for row in block_rows if row["condition"] == "C")
        if reference["registry_id"] != candidate["registry_id"]:
            raise ValueError(f"Registry mismatch inside paired block {block_id}.")
        pairs.append((reference, candidate))
    return pairs


def common_metrics(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    return {
        "registered_pairs": len(pairs),
        "required_rows_valid": all(reference["row_valid"] and candidate["row_valid"] for reference, candidate in pairs),
        "input_digest_matches": sum(
            reference["canonical_model_visible_payload_sha256"]
            == candidate["canonical_model_visible_payload_sha256"]
            and reference["candidate_artifact_sha256"] == candidate["candidate_artifact_sha256"]
            for reference, candidate in pairs
        ),
        "operational_success_agreements": sum(
            reference["operational_success"] == candidate["operational_success"]
            for reference, candidate in pairs
        ),
        "hard_contract_vector_agreements": sum(
            reference["hard_contract_vector"] == candidate["hard_contract_vector"]
            for reference, candidate in pairs
        ),
        "score_delta_within_0_05": sum(
            abs(candidate["private_score"] - reference["private_score"]) <= 0.05 + 1e-12
            for reference, candidate in pairs
        ),
        "canonical_output_equalities": sum(
            bool(reference["canonical_output_sha256"])
            and reference["canonical_output_sha256"] == candidate["canonical_output_sha256"]
            for reference, candidate in pairs
        ),
        "raw_response_equalities": sum(
            bool(reference["raw_response_sha256"])
            and reference["raw_response_sha256"] == candidate["raw_response_sha256"]
            for reference, candidate in pairs
        ),
        "reference_F_successes": sum(reference["operational_success"] for reference, _ in pairs),
        "candidate_C_successes": sum(candidate["operational_success"] for _, candidate in pairs),
        "candidate_any_hard_contract_failures": sum(
            not all(candidate["hard_contract_vector"]) for _, candidate in pairs
        ),
    }


def positive_state(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]], metrics: dict[str, Any]
) -> tuple[str, list[str], int]:
    failed: list[str] = []
    valid_margin_pairs = sum(
        candidate["private_score"] >= reference["private_score"] - 0.05 - 1e-12
        for reference, candidate in pairs
    )
    if not metrics["required_rows_valid"] or metrics["input_digest_matches"] != 6:
        return "Invalid", ["required_row_or_input_binding"], valid_margin_pairs
    if metrics["reference_F_successes"] < 5:
        failed.append("total_reference_F_successes")
    if metrics["candidate_C_successes"] < 5:
        failed.append("total_candidate_C_successes")
    if valid_margin_pairs < 5:
        failed.append("total_valid_margin_pairs")
    for registry_id in ("A", "B"):
        selected = [pair for pair in pairs if pair[0]["registry_id"] == registry_id]
        if len(selected) != 3:
            raise ValueError(f"Expected three {registry_id} pairs in each control cell.")
        if sum(reference["operational_success"] for reference, _ in selected) < 2:
            failed.append(f"{registry_id}_reference_F_successes")
        if sum(candidate["operational_success"] for _, candidate in selected) < 2:
            failed.append(f"{registry_id}_candidate_C_successes")
        if sum(
            candidate["private_score"] >= reference["private_score"] - 0.05 - 1e-12
            for reference, candidate in selected
        ) < 2:
            failed.append(f"{registry_id}_valid_margin_pairs")
    return ("SanityPass" if not failed else "SanityFail"), failed, valid_margin_pairs


def identity_state(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    if not metrics["required_rows_valid"] or metrics["input_digest_matches"] != 6:
        return "Invalid", ["required_row_or_input_digest"]
    failed = []
    for field in (
        "operational_success_agreements",
        "hard_contract_vector_agreements",
        "score_delta_within_0_05",
    ):
        if metrics[field] < 5:
            failed.append(f"minimum_{field}")
    return ("SanityPass" if not failed else "SanityFail"), failed


def destructive_state(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    metrics: dict[str, Any],
    target_binding_available: bool,
) -> tuple[str, list[str], int | None]:
    failed: list[str] = []
    if not metrics["required_rows_valid"]:
        failed.append("required_rows_valid")
    if not target_binding_available:
        failed.append("missing_targeted_hard_contract_binding")
    if metrics["reference_F_successes"] < 5:
        failed.append("total_reference_F_successes")
    if not target_binding_available:
        return "Invalid", failed, None

    # This branch is intentionally unreachable for the frozen evidence. It documents
    # the registered rule should a valid target-to-vector binding ever be supplied.
    targeted_failures = sum(not all(candidate["hard_contract_vector"]) for _, candidate in pairs)
    if metrics["candidate_C_successes"] > 1:
        failed.append("total_candidate_C_successes")
    if targeted_failures < 5:
        failed.append("total_targeted_hard_contract_failures")
    for registry_id in ("A", "B"):
        selected = [pair for pair in pairs if pair[0]["registry_id"] == registry_id]
        if sum(reference["operational_success"] for reference, _ in selected) < 2:
            failed.append(f"{registry_id}_reference_F_successes")
        if sum(candidate["operational_success"] for _, candidate in selected) > 1:
            failed.append(f"{registry_id}_candidate_C_successes")
        if sum(not all(candidate["hard_contract_vector"]) for _, candidate in selected) < 2:
            failed.append(f"{registry_id}_targeted_hard_contract_failures")
    return ("SanityPass" if not failed else "SanityFail"), failed, targeted_failures


def analyze(
    ledger_path: Path,
    binding_path: Path,
    extraction_manifest_path: Path,
    output_dir: Path,
) -> None:
    rows = load_ledger(ledger_path)
    binding_evidence = json.loads(binding_path.read_text(encoding="utf-8"))
    extraction_manifest = json.loads(extraction_manifest_path.read_text(encoding="utf-8"))
    if extraction_manifest["status"] != "hash_verified_extraction":
        raise ValueError("Control evidence was not hash-verified during extraction.")
    for name in (ledger_path.name, binding_path.name):
        if extraction_manifest["outputs"][name] != sha256(ledger_path.parent / name):
            raise ValueError(f"Extraction-manifest hash mismatch for {name}.")

    audit_by_task = {row["task_id"]: row for row in binding_evidence["audits"]}
    if tuple(sorted(audit_by_task)) != EXPECTED_TASKS:
        raise ValueError("Binding evidence does not cover the four registered tasks.")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["task_id"], row["variant_id"])].append(row)
    if len(grouped) != 12 or set(map(len, grouped.values())) != {12}:
        raise ValueError("Expected twelve task-control cells with twelve rows each.")

    task_results: list[dict[str, Any]] = []
    paper_by_task: dict[str, str] = {}
    destructive_proxy_by_task: dict[str, int] = {}
    for (task_id, variant_id), selected in sorted(grouped.items()):
        pairs = pair_rows(selected)
        paper_id = selected[0]["paper_id"]
        domain = selected[0]["domain"]
        paper_by_task[task_id] = paper_id
        metrics = common_metrics(pairs)
        target_binding_available = (
            variant_id != "destructive_core_negative"
            or bool(audit_by_task[task_id]["target_binding_available"])
        )
        valid_margin_pairs: int | None = None
        targeted_failures: int | None = None
        if variant_id == "planted_redundancy_positive":
            state, failed, valid_margin_pairs = positive_state(pairs, metrics)
        elif variant_id == "byte_identical_identity":
            state, failed = identity_state(metrics)
        elif variant_id == "destructive_core_negative":
            state, failed, targeted_failures = destructive_state(
                pairs, metrics, target_binding_available
            )
            destructive_proxy_by_task[task_id] = metrics["candidate_any_hard_contract_failures"]
        else:
            raise ValueError(f"Unknown control variant: {variant_id}")
        task_results.append(
            {
                **metrics,
                "domain": domain,
                "failed_gates": failed,
                "paper_id": paper_id,
                "state": state,
                "target_binding_available": target_binding_available,
                "targeted_hard_contract_failures": targeted_failures,
                "task_id": task_id,
                "valid_margin_pairs": valid_margin_pairs,
                "variant_id": variant_id,
            }
        )

    state_counts: dict[str, dict[str, int]] = {}
    for variant_id in EXPECTED_VARIANTS:
        counts = Counter(
            row["state"] for row in task_results if row["variant_id"] == variant_id
        )
        state_counts[variant_id] = {
            state: counts.get(state, 0) for state in ("SanityPass", "SanityFail", "Invalid")
        }

    destructive_audit: list[dict[str, Any]] = []
    for task_id in EXPECTED_TASKS:
        source = audit_by_task[task_id]
        destructive_audit.append(
            {
                "descriptive_proxy_any_hard_contract_failures": destructive_proxy_by_task[task_id],
                "observed_vector_length": source["observed_vector_length"],
                "paper_id": paper_by_task[task_id],
                "registered_target_count_is_computable": source[
                    "registered_target_count_is_computable"
                ],
                "scorer_manifest_hard_contract_ids": source[
                    "scorer_manifest_hard_contract_ids"
                ],
                "scorer_vector_semantics": source["scorer_vector_semantics"],
                "target_binding_available": source["target_binding_available"],
                "target_binding_marker_locations": source["target_binding_marker_locations"],
                "task_id": task_id,
            }
        )

    result = {
        "schema_version": "effectslice-control-analysis.v1",
        "status": "verified_forward_analysis",
        "registered_scope": {
            "anchor_tasks": 4,
            "blocks_per_task_variant": 6,
            "control_variants": 3,
            "rows": 144,
        },
        "state_counts": state_counts,
        "task_results": task_results,
        "destructive_target_binding_audit": destructive_audit,
        "interpretation": {
            "planted_redundancy_positive": (
                "Frozen schedule digests show byte-identical full artifacts in both arms; "
                "this is an identity-like no-harm check, not a nonidentical redundancy test."
            ),
            "byte_identical_identity": (
                "Input digest equality is verified from the frozen schedule; output equality "
                "is descriptive only, as registered."
            ),
            "destructive_core_negative": (
                "The preregistered targeted hard-contract count is not identifiable. Scorers "
                "expose only [complete, all_private_cases_pass], and no machine-readable "
                "destructive target-to-vector binding exists. Any-hard-contract failures are "
                "descriptive proxies only, so all four registered states are Invalid."
            ),
            "confusion_matrix": (
                "Unavailable by design: control states are exact SanityPass/SanityFail/Invalid "
                "outcomes, not admission labels."
            ),
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "control_analysis.json"
    states_path = output_dir / "control_task_states.csv"
    binding_audit_path = output_dir / "destructive_target_binding_audit.csv"
    write_json(json_path, result)
    write_csv(
        states_path,
        STATE_FIELDS,
        [
            {
                field: (
                    json.dumps(row[field], separators=(",", ":"))
                    if field == "failed_gates"
                    else row[field]
                )
                for field in STATE_FIELDS
            }
            for row in task_results
        ],
    )
    write_csv(
        binding_audit_path,
        BINDING_FIELDS,
        [
            {
                field: (
                    json.dumps(row[field], separators=(",", ":"))
                    if isinstance(row[field], list)
                    else row[field]
                )
                for field in BINDING_FIELDS
            }
            for row in destructive_audit
        ],
    )

    output_names = (
        "control_analysis.json",
        "control_task_states.csv",
        "destructive_target_binding_audit.csv",
    )
    manifest = {
        "schema_version": "effectslice-forward-analysis-manifest.v1",
        "section": "03_controls",
        "inputs": {
            portable_reference(ledger_path): sha256(ledger_path),
            portable_reference(binding_path): sha256(binding_path),
            portable_reference(extraction_manifest_path): sha256(extraction_manifest_path),
        },
        "runtime": {"python": platform.python_version()},
        "parameters": {
            "identity_minimum_agreements": 5,
            "score_tolerance": 0.05,
            "positive_total_minimum_successes_per_arm": 5,
            "positive_registry_minimum_successes_per_arm": 2,
            "destructive_target_binding_required": True,
        },
        "outputs": {name: {"sha256": sha256(output_dir / name)} for name in output_names},
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--binding-evidence", type=Path, default=DEFAULT_BINDING)
    parser.add_argument(
        "--extraction-manifest", type=Path, default=DEFAULT_EXTRACTION_MANIFEST
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.ledger, args.binding_evidence, args.extraction_manifest, args.output_dir)


if __name__ == "__main__":
    main()
