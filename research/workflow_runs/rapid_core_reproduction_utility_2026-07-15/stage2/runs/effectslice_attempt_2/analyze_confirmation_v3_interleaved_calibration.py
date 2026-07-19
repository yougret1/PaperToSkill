from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

import analyze_confirmation_v3 as frozen_analyzer
import build_confirmation_v3_interleaved_calibration as registration


RUN_ROOT = Path(__file__).resolve().parent
POSTRUN_ROOT = RUN_ROOT.parent.parent / "postrun" / "derived" / RUN_ROOT.name
OUTPUT_ROOT = POSTRUN_ROOT / "confirmation_v3_interleaved_calibration"
SCHEMA_VERSION = "effectslice-v3-interleaved-calibration-analysis.v1"
PROVENANCE_SCHEMA = "effectslice-v3-interleaved-calibration-analysis-provenance.v1"


class InterleavedAnalysisError(ValueError):
    """Raised when registered calibration evidence cannot be analyzed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InterleavedAnalysisError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise InterleavedAnalysisError(f"{label} must be a JSON object")
    return value


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() == payload:
        return
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _condition(block: dict[str, Any], name: str) -> dict[str, Any]:
    conditions = block.get("condition_results")
    value = conditions.get(name) if isinstance(conditions, dict) else None
    if not isinstance(value, dict):
        raise InterleavedAnalysisError(f"audited block lacks condition {name}")
    success = value.get("success")
    score = value.get("task_score")
    hard = value.get("hard_constraints_passed")
    if type(success) is not bool or not isinstance(score, (int, float)):
        raise InterleavedAnalysisError(f"condition {name} result is invalid")
    if type(hard) is not bool:
        raise InterleavedAnalysisError(f"condition {name} hard status is invalid")
    return {
        "success": success,
        "task_score": float(score),
        "hard_constraints_passed": hard,
    }


def _candidate_centered_event(block: dict[str, Any]) -> dict[str, bool]:
    baseline = _condition(block, "B")
    full = _condition(block, "F")
    selected = _condition(block, "S")
    event = bool(
        not baseline["success"]
        and selected["success"]
        and selected["hard_constraints_passed"]
        and selected["task_score"] >= full["task_score"] - 0.05
    )
    return {
        "event": event,
        "full_succeeded": bool(full["success"]),
        "selected_succeeded": bool(selected["success"]),
    }


def analyze_blocks(
    preregistration: dict[str, Any], blocks: list[dict[str, Any]]
) -> dict[str, Any]:
    if preregistration.get("primary_event") != registration.PRIMARY_EVENT:
        raise InterleavedAnalysisError("registered primary event changed")
    if preregistration.get("registered_block_count") != len(blocks):
        raise InterleavedAnalysisError("registered block count is inconsistent")
    family_specs = preregistration.get("families")
    if not isinstance(family_specs, dict) or set(family_specs) != set(
        registration.LABEL_SPECS
    ):
        raise InterleavedAnalysisError("registered family labels are invalid")

    grouped: dict[str, list[dict[str, Any]]] = {
        label: [row for row in blocks if row.get("label") == label]
        for label in registration.LABEL_SPECS
    }
    if sum(map(len, grouped.values())) != len(blocks):
        raise InterleavedAnalysisError("audited block has an unknown label")

    summaries = {}
    for label, rows in grouped.items():
        spec = family_specs[label]
        if not isinstance(spec, dict) or spec.get("replicate_count") != len(rows):
            raise InterleavedAnalysisError(f"{label} registered count changed")
        primary_events = 0
        joint_events = 0
        reference_only = 0
        selected_successes = 0
        integrity_count = 0
        for row in rows:
            if row.get("integrity_passed") is not True:
                continue
            integrity_count += 1
            result = _candidate_centered_event(row)
            primary_events += int(result["event"])
            selected_successes += int(result["selected_succeeded"])
            joint = row.get("joint_substitution_event") is True
            joint_events += int(joint)
            if result["event"] and not result["full_succeeded"] and not joint:
                reference_only += 1
        summaries[label] = {
            "registered_blocks": len(rows),
            "integrity_passed_blocks": integrity_count,
            "primary_event_count": primary_events,
            "legacy_joint_event_count": joint_events,
            "selected_success_count": selected_successes,
            "reference_failure_only_count": reference_only,
            "required_candidate_centered_events": spec.get(
                "required_candidate_centered_events"
            ),
        }

    positive_required = summaries["positive"]["required_candidate_centered_events"]
    positive_passed = (
        type(positive_required) is int
        and summaries["positive"]["primary_event_count"] == positive_required
        and positive_required == summaries["positive"]["registered_blocks"]
    )
    negative_required = summaries["negative"]["required_candidate_centered_events"]
    negative_passed = bool(
        negative_required == "strictly_less_than_registered_blocks"
        and summaries["negative"]["primary_event_count"]
        < summaries["negative"]["registered_blocks"]
    )
    full_integrity = all(
        row.get("integrity_passed") is True for row in blocks
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_role": "fresh_registered_calibration_replication",
        "primary_event": registration.PRIMARY_EVENT,
        "decision_basis": "finite_registered_schedule",
        "independence_verified": False,
        "full_integrity_passed": full_integrity,
        "labels": summaries,
        "calibration_decision": {
            "preregistered": True,
            "positive_requirement_passed": positive_passed,
            "negative_requirement_passed": negative_passed,
            "instrument_passed": bool(
                full_integrity and positive_passed and negative_passed
            ),
        },
        "scope_guards": {
            "population_guarantee": False,
            "iid_inference_used": False,
            "cross_paper_claim_ready": False,
            "human_benefit_claim_ready": False,
        },
        "blocks": blocks,
    }


def _validate_progress(
    preregistration: dict[str, Any], progress: dict[str, Any]
) -> list[dict[str, Any]]:
    expected_sha = _sha256(registration.PREREGISTRATION_PATH.read_bytes())
    if progress.get("preregistration_sha256") != expected_sha:
        raise InterleavedAnalysisError("progress registration digest mismatch")
    records = progress.get("records")
    if not isinstance(records, list) or len(records) != preregistration.get(
        "registered_block_count"
    ):
        raise InterleavedAnalysisError("progress record count is invalid")
    schedule = preregistration.get("global_schedule")
    for record, registered in zip(records, schedule):
        if not isinstance(record, dict) or not isinstance(registered, dict):
            raise InterleavedAnalysisError("progress schedule row is invalid")
        expected = {
            "global_order_index": registered["global_order_index"],
            "stratum": registered["stratum"],
            "label": registered["label"],
            "control": registered["underlying_control"],
            "replicate_id": registered["replicate_id"],
            "condition_execution_order": registered["condition_order"],
        }
        if any(record.get(key) != value for key, value in expected.items()):
            raise InterleavedAnalysisError("progress schedule differs from registration")
        if record.get("status") not in {"completed", "failed", "preserved"}:
            raise InterleavedAnalysisError("progress schedule is not terminal")
    return records


def audit_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    registration_audit = registration.audit_registration(
        allow_execution_started=True
    )
    preregistration = _json_object(
        registration.PREREGISTRATION_PATH, "preregistration"
    )
    progress = _json_object(registration.PROGRESS_PATH, "progress")
    records = _validate_progress(preregistration, progress)
    schedule_response_ids: set[str] = set()
    schedule_scaffold_sha256: list[str] = []
    blocks = []
    for record in records:
        base = {
            "global_order_index": record["global_order_index"],
            "stratum": record["stratum"],
            "label": record["label"],
            "control": record["control"],
            "replicate_id": record["replicate_id"],
            "registered_status": record["status"],
        }
        if record["status"] == "failed":
            blocks.append(
                {
                    **base,
                    "integrity_passed": False,
                    "integrity_violations": ["registered_runner_failed"],
                    "joint_substitution_event": False,
                    "condition_results": None,
                }
            )
            continue
        family_path = Path(record["family_path"])
        family = _json_object(family_path, f"{record['label']} family")
        if _sha256(family_path.read_bytes()) != record["family_sha256"]:
            blocks.append(
                {
                    **base,
                    "integrity_passed": False,
                    "integrity_violations": ["registered_family_digest_failure"],
                    "joint_substitution_event": False,
                    "condition_results": None,
                }
            )
            continue
        try:
            audited = frozen_analyzer._audit_bundle(
                record,
                family,
                schedule_response_ids=schedule_response_ids,
                schedule_scaffold_sha256=schedule_scaffold_sha256,
            )
        except (frozen_analyzer.AnalysisInputError, OSError, UnicodeError):
            blocks.append(
                {
                    **base,
                    "integrity_passed": False,
                    "integrity_violations": ["registered_bundle_integrity_failure"],
                    "joint_substitution_event": False,
                    "condition_results": None,
                }
            )
        else:
            blocks.append(
                {
                    **base,
                    "integrity_passed": True,
                    "integrity_violations": [],
                    **audited,
                }
            )
    result = analyze_blocks(preregistration, blocks)
    result["registered_schedule_length"] = len(records)
    result["status_counts"] = progress.get("counts")
    result["provider_response_id_count"] = len(schedule_response_ids)
    result["registration_audit"] = registration_audit
    return result, preregistration


def write_analysis(
    output_path: Path, provenance_path: Path
) -> dict[str, Any]:
    result, _ = audit_outputs()
    _write_json_atomic(output_path, result)
    sources = {
        "preregistration": registration.PREREGISTRATION_PATH,
        "anchor": registration.ANCHOR_PATH,
        "progress": registration.PROGRESS_PATH,
        "analyzer": Path(__file__),
        "frozen_bundle_auditor": RUN_ROOT / "analyze_confirmation_v3.py",
    }
    provenance = {
        "schema_version": PROVENANCE_SCHEMA,
        "sources": {
            name: {
                "path": path.resolve().as_posix(),
                "sha256": _sha256(path.read_bytes()),
            }
            for name, path in sources.items()
        },
        "output_path": Path(output_path).resolve().as_posix(),
        "output_sha256": _sha256(Path(output_path).read_bytes()),
        "analysis_role": "fresh_registered_calibration_replication",
        "instrument_passed": result["calibration_decision"]["instrument_passed"],
    }
    _write_json_atomic(provenance_path, provenance)
    return provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit and analyze the V3 interleaved calibration replication"
    )
    parser.add_argument(
        "--output-path", type=Path, default=OUTPUT_ROOT / "analysis.json"
    )
    parser.add_argument(
        "--provenance-path",
        type=Path,
        default=OUTPUT_ROOT / "analysis.provenance.json",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = write_analysis(args.output_path, args.provenance_path)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
