from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
POSTRUN_ROOT = RUN_ROOT.parent.parent / "postrun" / "derived" / RUN_ROOT.name
SCHEMA_VERSION = "effectslice-confirmation-v3-calibration-analysis.v1"
PROVENANCE_SCHEMA = "effectslice-confirmation-v3-calibration-provenance.v1"
CONDITIONS = ("B", "F", "S")


class CalibrationAnalysisError(ValueError):
    """Raised when calibration inputs are incomplete or inconsistent."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CalibrationAnalysisError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise CalibrationAnalysisError(f"{label} must be a JSON object")
    return value


def _replace_bytes(path: Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
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


def _write_json(path: Path, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    destination = Path(path)
    if destination.exists() and destination.read_bytes() == payload:
        return
    _replace_bytes(destination, payload)


def _condition(row: dict[str, Any], name: str, label: str) -> dict[str, Any]:
    conditions = row.get("condition_results")
    if conditions is None:
        conditions = row.get("conditions")
    value = conditions.get(name) if isinstance(conditions, dict) else None
    if not isinstance(value, dict):
        raise CalibrationAnalysisError(f"{label} lacks condition {name}")
    success = value.get("success")
    score = value.get("task_score")
    hard = value.get("hard_constraints_passed")
    if type(success) is not bool or not isinstance(score, (int, float)):
        raise CalibrationAnalysisError(f"{label} condition {name} is invalid")
    if type(hard) is not bool:
        raise CalibrationAnalysisError(
            f"{label} condition {name} lacks hard-constraint status"
        )
    return {
        "success": success,
        "task_score": float(score),
        "hard_constraints_passed": hard,
    }


def _candidate_centered_event(
    row: dict[str, Any], maximum_shortfall: float, label: str
) -> dict[str, bool]:
    baseline = _condition(row, "B", label)
    full = _condition(row, "F", label)
    selected = _condition(row, "S", label)
    baseline_failed = not baseline["success"]
    selected_succeeded = bool(
        selected["success"] and selected["hard_constraints_passed"]
    )
    selected_noninferior = bool(
        selected["task_score"] >= full["task_score"] - maximum_shortfall
    )
    event = bool(baseline_failed and selected_succeeded and selected_noninferior)
    return {
        "event": event,
        "baseline_failed": baseline_failed,
        "selected_succeeded": selected_succeeded,
        "selected_noninferior": selected_noninferior,
        "full_succeeded": bool(full["success"]),
    }


def _binding_digest(family: dict[str, Any], name: str) -> str:
    bindings = family.get("bindings")
    binding = bindings.get(name) if isinstance(bindings, dict) else None
    digest = binding.get("sha256") if isinstance(binding, dict) else None
    if not isinstance(digest, str) or len(digest) != 64:
        raise CalibrationAnalysisError(f"family {name} binding is invalid")
    return digest


def _summarize_v3_control(
    rows: list[dict[str, Any]], maximum_shortfall: float, control: str
) -> dict[str, Any]:
    events = []
    reference_only = 0
    selected_successes = 0
    for row in rows:
        label = f"V3 {control} {row.get('replicate_id')}"
        result = _candidate_centered_event(row, maximum_shortfall, label)
        events.append(result["event"])
        selected_successes += int(result["selected_succeeded"])
        if (
            result["event"]
            and not result["full_succeeded"]
            and row.get("joint_substitution_event") is False
        ):
            reference_only += 1
    return {
        "events": sum(events),
        "registered_blocks": len(rows),
        "selected_successes": selected_successes,
        "reference_failure_only_count": reference_only,
        "all_registered_events": all(events),
    }


def _summarize_historical(
    historical: dict[str, Any], maximum_shortfall: float
) -> dict[str, Any]:
    if historical.get("integrity_passed") is not True:
        raise CalibrationAnalysisError("historical negative integrity did not pass")
    if historical.get("schedule_complete") is not True:
        raise CalibrationAnalysisError("historical negative schedule is incomplete")
    rows = historical.get("replicates")
    denominator = historical.get("replicate_denominator")
    if not isinstance(rows, list) or denominator != len(rows):
        raise CalibrationAnalysisError("historical negative denominator is invalid")
    events = []
    selected_successes = 0
    reference_only = 0
    for row in rows:
        if not isinstance(row, dict):
            raise CalibrationAnalysisError("historical replicate is invalid")
        if row.get("classification") != "audited":
            raise CalibrationAnalysisError("historical replicate is not audited")
        if row.get("integrity_violations") != []:
            raise CalibrationAnalysisError("historical replicate integrity failed")
        label = f"historical {row.get('replicate_id')}"
        result = _candidate_centered_event(row, maximum_shortfall, label)
        events.append(result["event"])
        selected_successes += int(result["selected_succeeded"])
        if result["event"] and not result["full_succeeded"]:
            reference_only += 1
    return {
        "candidate_id": historical.get("selected_candidate_id"),
        "events": sum(events),
        "registered_blocks": len(rows),
        "selected_successes": selected_successes,
        "reference_failure_only_count": reference_only,
        "all_registered_events": all(events),
        "evidence_role": "real_unstable_negative_control",
    }


def analyze_calibration(
    *,
    analysis: dict[str, Any],
    historical_summary: dict[str, Any],
    progress: dict[str, Any],
    identity_family: dict[str, Any],
    planted_family: dict[str, Any],
) -> dict[str, Any]:
    if analysis.get("schedule_integrity_passed") is not True:
        raise CalibrationAnalysisError("V3 schedule integrity did not pass")
    blocks = analysis.get("blocks")
    schedule_length = analysis.get("registered_schedule_length")
    if not isinstance(blocks, list) or schedule_length != len(blocks):
        raise CalibrationAnalysisError("V3 block schedule is invalid")
    for block in blocks:
        if not isinstance(block, dict) or block.get("integrity_passed") is not True:
            raise CalibrationAnalysisError("V3 block integrity did not pass")
        if type(block.get("joint_substitution_event")) is not bool:
            raise CalibrationAnalysisError("V3 primary event is invalid")

    controls = analysis.get("controls")
    if not isinstance(controls, dict) or set(controls) != {"identity", "planted"}:
        raise CalibrationAnalysisError("V3 controls are invalid")
    grouped = {
        control: [row for row in blocks if row.get("control") == control]
        for control in ("identity", "planted")
    }
    if sum(map(len, grouped.values())) != len(blocks):
        raise CalibrationAnalysisError("V3 block has an unknown control")

    for name, family in (("identity", identity_family), ("planted", planted_family)):
        if family.get("control") != name:
            raise CalibrationAnalysisError(f"{name} family control is invalid")
        maximum_shortfall = family.get("maximum_shortfall")
        if not isinstance(maximum_shortfall, (int, float)) or maximum_shortfall < 0:
            raise CalibrationAnalysisError(f"{name} maximum shortfall is invalid")
        registered = controls[name]
        if not isinstance(registered, dict):
            raise CalibrationAnalysisError(f"{name} registered result is invalid")
        observed_joint = sum(row["joint_substitution_event"] for row in grouped[name])
        if registered.get("joint_event_count") != observed_joint:
            raise CalibrationAnalysisError(f"{name} primary count is inconsistent")
        if registered.get("registered_block_count") != len(grouped[name]):
            raise CalibrationAnalysisError(f"{name} block count is inconsistent")

    identity_selected = _binding_digest(identity_family, "selected_artifact")
    planted_selected = _binding_digest(planted_family, "selected_artifact")
    if identity_selected != planted_selected:
        raise CalibrationAnalysisError(
            "identity and planted selected artifact bindings differ"
        )

    identity_shortfall = float(identity_family["maximum_shortfall"])
    planted_shortfall = float(planted_family["maximum_shortfall"])
    exploratory = {
        "identity": _summarize_v3_control(
            grouped["identity"], identity_shortfall, "identity"
        ),
        "planted": _summarize_v3_control(
            grouped["planted"], planted_shortfall, "planted"
        ),
        "historical_negative": _summarize_historical(
            historical_summary, planted_shortfall
        ),
        "event_definition": {
            "baseline_condition": "B success is false",
            "candidate_condition": "S success and hard constraints are true",
            "noninferiority_condition": "q_S >= q_F - maximum_shortfall",
            "reference_success_required": False,
        },
        "status": "posthoc_exploratory",
    }

    records = progress.get("records")
    if (
        not isinstance(records, list)
        or progress.get("registered_schedule_length") != len(records)
        or len(records) != len(blocks)
    ):
        raise CalibrationAnalysisError("V3 progress schedule is invalid")
    order = [row.get("control") if isinstance(row, dict) else None for row in records]
    if any(control not in {"identity", "planted"} for control in order):
        raise CalibrationAnalysisError("V3 progress control order is invalid")
    groups = 1 + sum(left != right for left, right in zip(order, order[1:])) if order else 0
    control_interleaved = groups > len(set(order))

    primary = {}
    for name in ("identity", "planted"):
        registered = controls[name]
        primary[name] = {
            "events": registered["joint_event_count"],
            "registered_blocks": registered["registered_block_count"],
            "decision": registered["decision"],
        }

    planted_primary_passed = (
        primary["planted"]["events"] == primary["planted"]["registered_blocks"]
    )
    finite_separation = (
        exploratory["planted"]["events"]
        > exploratory["historical_negative"]["events"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_role": "posthoc_event_diagnostic",
        "preregistered_primary": primary,
        "preregistered_strict_subset_admitted": analysis.get(
            "strict_subset_admitted"
        ),
        "exploratory_candidate_centered": exploratory,
        "schedule_diagnostics": {
            "control_order": order,
            "control_order_group_count": groups,
            "control_interleaved": control_interleaved,
            "shared_selected_artifact": True,
            "shared_selected_artifact_sha256": identity_selected,
            "temporal_order_confounded": bool(not control_interleaved),
        },
        "calibration_verdict": {
            "preregistered_rule": (
                "passed_planted_positive_control"
                if planted_primary_passed
                else "failed_planted_positive_control"
            ),
            "candidate_centered_rule": (
                "posthoc_not_admissible_without_fresh_confirmation"
            ),
            "candidate_centered_finite_schedule_separation": finite_separation,
            "fresh_interleaved_confirmation_required": True,
        },
        "scope_guards": {
            "changes_preregistered_decision": False,
            "independence_verified": False,
            "population_guarantee": False,
            "cross_paper_claim_ready": False,
            "human_benefit_claim_ready": False,
        },
    }


def build_analysis(
    *,
    analysis_path: Path,
    analysis_provenance_path: Path,
    historical_summary_path: Path,
    progress_path: Path,
    identity_family_path: Path,
    planted_family_path: Path,
    output_path: Path,
    provenance_path: Path,
) -> dict[str, Any]:
    source_paths = {
        "analysis": Path(analysis_path),
        "analysis_provenance": Path(analysis_provenance_path),
        "historical_summary": Path(historical_summary_path),
        "progress": Path(progress_path),
        "identity_family": Path(identity_family_path),
        "planted_family": Path(planted_family_path),
    }
    values = {name: _json_object(path, name) for name, path in source_paths.items()}
    expected_analysis = values["analysis_provenance"].get("analysis_sha256")
    actual_analysis = _sha256(source_paths["analysis"].read_bytes())
    if expected_analysis != actual_analysis:
        raise CalibrationAnalysisError("analysis provenance digest mismatch")
    result = analyze_calibration(
        analysis=values["analysis"],
        historical_summary=values["historical_summary"],
        progress=values["progress"],
        identity_family=values["identity_family"],
        planted_family=values["planted_family"],
    )
    _write_json(output_path, result)
    provenance = {
        "schema_version": PROVENANCE_SCHEMA,
        "builder_path": Path(__file__).resolve().as_posix(),
        "builder_sha256": _sha256(Path(__file__).read_bytes()),
        "sources": {
            name: {
                "path": path.resolve().as_posix(),
                "sha256": _sha256(path.read_bytes()),
            }
            for name, path in source_paths.items()
        },
        "output_path": Path(output_path).resolve().as_posix(),
        "output_sha256": _sha256(Path(output_path).read_bytes()),
        "analysis_role": "posthoc_event_diagnostic",
        "fresh_confirmation_required": True,
    }
    _write_json(provenance_path, provenance)
    return provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the post-hoc V3 admission-event calibration diagnostic"
    )
    confirmation = POSTRUN_ROOT / "confirmation_v3"
    family_root = RUN_ROOT / "artifacts" / "toolformer_filter" / "confirmation_v3"
    parser.add_argument(
        "--analysis-path", type=Path, default=confirmation / "analysis.json"
    )
    parser.add_argument(
        "--analysis-provenance-path",
        type=Path,
        default=confirmation / "analysis.provenance.json",
    )
    parser.add_argument(
        "--historical-summary-path",
        type=Path,
        default=RUN_ROOT
        / "derived"
        / "confirmation_v2_final"
        / "toolformer_filter_confirmation_v2_summary.json",
    )
    parser.add_argument(
        "--progress-path",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v3"
        / "confirmation_v3_progress.json",
    )
    parser.add_argument(
        "--identity-family-path",
        type=Path,
        default=family_root / "identity" / "family.json",
    )
    parser.add_argument(
        "--planted-family-path",
        type=Path,
        default=family_root / "planted" / "family.json",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=confirmation / "calibration_analysis.json",
    )
    parser.add_argument(
        "--provenance-path",
        type=Path,
        default=confirmation / "calibration_analysis.provenance.json",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = build_analysis(
        analysis_path=args.analysis_path,
        analysis_provenance_path=args.analysis_provenance_path,
        historical_summary_path=args.historical_summary_path,
        progress_path=args.progress_path,
        identity_family_path=args.identity_family_path,
        planted_family_path=args.planted_family_path,
        output_path=args.output_path,
        provenance_path=args.provenance_path,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
