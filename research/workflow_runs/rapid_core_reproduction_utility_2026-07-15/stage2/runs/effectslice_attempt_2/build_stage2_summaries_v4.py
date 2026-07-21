from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
DEFAULT_ANALYSIS = RUN_ROOT / "derived" / "confirmation_v4" / "analysis.json"
DEFAULT_OUTPUT = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
ANALYSIS_SCHEMA = "effectslice-confirmation-v4-analysis.v1"
SUMMARY_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
FAMILY_ORDER = (
    "snap_mfse",
    "toolformer_negative",
    "toolformer_positive",
    "toolformer_identity",
)
DISPLAY_NAMES = {
    "snap_mfse": "SNAP real candidate",
    "toolformer_negative": "Toolformer real candidate",
    "toolformer_positive": "Planted positive control",
    "toolformer_identity": "Identity instrumentation",
}


def _condition_breakdown(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    breakdown: dict[str, dict[str, dict[str, int]]] = {
        family: {
            condition: {
                "condition_runs": 0,
                "invalid_actions": 0,
                "extra_transport_attempts": 0,
                "public_test_requests": 0,
                "public_test_passes": 0,
                "public_test_failures": 0,
                "budget_exhaustions": 0,
            }
            for condition in "BFS"
        }
        for family in FAMILY_ORDER
    }
    for block in blocks:
        family = block["family_key"]
        for condition in "BFS":
            source = block["condition_results"][condition]
            target = breakdown[family][condition]
            requests = int(source["public_test_requests"])
            passes = int(source["public_test_passes"])
            target["condition_runs"] += 1
            target["invalid_actions"] += int(source["action_counts"].get("invalid", 0))
            target["extra_transport_attempts"] += int(source["transport_attempts"]) - int(
                source["actions_used"]
            )
            target["public_test_requests"] += requests
            target["public_test_passes"] += passes
            target["public_test_failures"] += requests - passes
            target["budget_exhaustions"] += int(
                source["terminal_reason"] == "action_budget_exhausted_after_final_score"
            )
    return breakdown


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_analysis(path: Path) -> tuple[Path, dict[str, Any]]:
    source = Path(path).resolve()
    if source.is_symlink() or not source.is_file():
        raise ValueError("confirmation V4 analysis must be a regular file")
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != ANALYSIS_SCHEMA:
        raise ValueError("unexpected confirmation V4 analysis schema")
    if payload.get("analysis_status") != "passed":
        raise ValueError("confirmation V4 analysis did not pass")
    if payload.get("integrity_passed") is not True:
        raise ValueError("confirmation V4 integrity audit did not pass")
    if payload.get("registered_outputs_complete") is not True:
        raise ValueError("confirmation V4 registered outputs are incomplete")
    if payload.get("registered_blocks") != 60:
        raise ValueError("confirmation V4 must contain 60 registered blocks")
    if payload.get("registered_condition_runs") != 180:
        raise ValueError("confirmation V4 must contain 180 condition runs")
    if set(payload.get("family_summaries", {})) != set(FAMILY_ORDER):
        raise ValueError("confirmation V4 family set changed")
    if len(payload.get("blocks", [])) != 60:
        raise ValueError("confirmation V4 block evidence is incomplete")
    return source, payload


def _family_row(key: str, family: dict[str, Any]) -> dict[str, Any]:
    counts = {name: int(family["operational_success_counts"][name]) for name in "BFS"}
    scores = {name: float(family["mean_task_score"][name]) for name in "BFS"}
    blocks = int(family["registered_blocks"])
    if any(not 0 <= value <= blocks for value in counts.values()):
        raise ValueError(f"{key} success count is outside its registered schedule")
    decision = family.get("admission_decision")
    instrumentation = family.get("identity_instrumentation")
    if key == "toolformer_identity":
        if decision is not None or not isinstance(instrumentation, dict):
            raise ValueError("identity family has invalid instrumentation fields")
    elif not isinstance(decision, dict):
        raise ValueError(f"{key} is missing its finite-schedule decision")
    return {
        "family_key": key,
        "display_name": DISPLAY_NAMES[key],
        "candidate_role": family["candidate_role"],
        "registered_blocks": blocks,
        "operational_success_counts": counts,
        "mean_task_score": scores,
        "full_minus_slice_success_gap": counts["F"] - counts["S"],
        "admission_decision": decision,
        "identity_instrumentation": instrumentation,
    }


def build_summary(analysis_path: Path, output_path: Path) -> Path:
    source, analysis = _load_analysis(analysis_path)
    family_rows = [
        _family_row(key, analysis["family_summaries"][key]) for key in FAMILY_ORDER
    ]
    family_by_key = {row["family_key"]: row for row in family_rows}
    calibration = analysis.get("calibration", {})
    if calibration.get("passed") is not True:
        raise ValueError("confirmation V4 control calibration did not pass")
    if family_by_key["toolformer_positive"]["admission_decision"]["passed"] is not True:
        raise ValueError("positive control did not meet its registered decision")
    if family_by_key["toolformer_negative"]["admission_decision"]["passed"] is not False:
        raise ValueError("negative control did not meet its registered decision")
    if family_by_key["toolformer_identity"]["identity_instrumentation"]["passed"] is not True:
        raise ValueError("identity instrumentation did not pass")

    block_scores = []
    for block in analysis["blocks"]:
        conditions = block.get("condition_results", {})
        if set(conditions) != {"B", "F", "S"}:
            raise ValueError("a V4 block does not contain B/F/S evidence")
        block_scores.append(
            {
                "family_key": block["family_key"],
                "replicate_id": block["replicate_id"],
                "global_order_index": int(block["global_order_index"]),
                "stratum": int(block["stratum"]),
                "task_scores": {
                    name: float(conditions[name]["task_score"]) for name in "BFS"
                },
                "operational_success": {
                    name: bool(conditions[name]["operational_success"])
                    for name in "BFS"
                },
            }
        )

    for row in family_rows:
        rows = [block for block in block_scores if block["family_key"] == row["family_key"]]
        row["paired_success_status"] = {
            "matches": sum(
                int(block["operational_success"]["F"] == block["operational_success"]["S"])
                for block in rows
            ),
            "full_success_slice_failure": sum(
                int(block["operational_success"]["F"] and not block["operational_success"]["S"])
                for block in rows
            ),
            "full_failure_slice_success": sum(
                int(not block["operational_success"]["F"] and block["operational_success"]["S"])
                for block in rows
            ),
        }

    resource = dict(analysis["resource_summary"])
    resource["extra_transport_attempts"] = int(resource["transport_attempts"]) - int(
        resource["provider_turns"]
    )
    resource["public_test_failures"] = int(resource["public_test_requests"]) - int(
        resource["public_test_passes"]
    )
    payload = {
        "schema_version": SUMMARY_SCHEMA,
        "evidence_boundary": analysis["evidence_boundary"],
        "decision_basis": "registered_finite_schedule_engineering_sla",
        "inference_scope": analysis["inference_scope"],
        "scope_guards": analysis["scope_guards"],
        "registered_blocks": 60,
        "registered_condition_runs": 180,
        "registered_strata": 18,
        "sla": {
            "maximum_baseline_successes": 2,
            "minimum_full_successes": 16,
            "minimum_slice_successes": 16,
            "maximum_full_minus_slice_success_gap": 2,
            "registered_gap_check_is_logically_redundant": True,
            "effective_decision_scope": "count_level_not_block_level_equivalence",
        },
        "families": family_rows,
        "real_candidate_decisions": analysis["real_candidate_decisions"],
        "real_candidate_admissions": sum(
            bool(analysis["real_candidate_decisions"][task]["passed"])
            for task in ("snap_mfse", "toolformer_filter")
        ),
        "calibration": calibration,
        "resource_summary": resource,
        "resource_by_family_condition": _condition_breakdown(analysis["blocks"]),
        "terminal_reason_counts": analysis["terminal_reason_counts"],
        "block_scores": block_scores,
        "analyzer_disclosure": {
            "bound_analyzer_result": "failed_before_aggregation_on_role_field_semantics",
            "defect": (
                "The bound analyzer compared comparison_role to evidence_boundary; "
                "the runners correctly stored development_triage and the formal V4 "
                "evidence boundary as distinct fields."
            ),
            "posthoc_adapter": "analyze_confirmation_v4_role_repair.py",
            "adapter_scope": "validate_both_raw_fields_then_reuse_all_remaining_bound_checks",
            "raw_evidence_modified": False,
            "preregistered_files_modified": False,
        },
        "claim_status": {
            "finite_schedule_protocol_calibrated": True,
            "real_slices_admitted": False,
            "general_skill_compression_effectiveness": False,
            "cross_paper_effectiveness": False,
            "population_inference": False,
            "human_benefit": False,
        },
        "sources": {
            "analysis": {
                "path": source.as_posix(),
                "sha256": _sha256(source),
            },
            "preregistration": {
                "path": analysis["preregistration_path"],
                "sha256": analysis["preregistration_sha256"],
            },
            "progress": analysis["progress_path"],
        },
    }
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the final V4 Stage 2 summary")
    parser.add_argument("--analysis", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = build_summary(args.analysis, args.output)
    print(json.dumps({"summary": output.as_posix(), "sha256": _sha256(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
