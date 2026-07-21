from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_stage2_summaries_v2 as v2


RUN_ROOT = Path(__file__).resolve().parent
POSTRUN_ROOT = RUN_ROOT.parent.parent / "postrun" / "derived" / RUN_ROOT.name
DEFAULT_CALIBRATION_ANALYSIS = (
    POSTRUN_ROOT
    / "confirmation_v3_interleaved_calibration_r2"
    / "analysis.json"
)
CALIBRATION_SCHEMA = "effectslice-v3-interleaved-calibration-analysis.v1"
LABEL_ORDER = ("positive", "negative", "identity")


def _load_calibration(path: Path) -> dict[str, Any]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != CALIBRATION_SCHEMA:
        raise ValueError(f"invalid interleaved calibration analysis: {source}")
    if payload.get("analysis_role") != "fresh_registered_calibration_replication":
        raise ValueError("calibration analysis role is not the fresh replication")
    if payload.get("full_integrity_passed") is not True:
        raise ValueError("calibration analysis failed the bundle integrity audit")
    registration = payload.get("registration_audit", {})
    if registration.get("valid") is not True:
        raise ValueError("calibration registration audit is invalid")
    if registration.get("control_interleaved") is not True:
        raise ValueError("calibration controls are not interleaved")
    if registration.get("registered_block_count") != payload.get(
        "registered_schedule_length"
    ):
        raise ValueError("calibration block count does not match the registration")
    status_counts = payload.get("status_counts", {})
    if status_counts.get("completed") != payload.get("registered_schedule_length"):
        raise ValueError("calibration schedule is incomplete")
    if any(status_counts.get(name, 0) for name in ("failed", "pending", "running")):
        raise ValueError("calibration schedule contains a non-completed block")
    labels = payload.get("labels", {})
    if set(labels) != set(LABEL_ORDER):
        raise ValueError("calibration labels do not match the registered families")
    payload["_source_path"] = source.as_posix()
    payload["_source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    return payload


def _source(calibration: dict[str, Any]) -> dict[str, str]:
    return {
        "path": calibration["_source_path"],
        "sha256": calibration["_source_sha256"],
    }


def _calibration_summary(calibration: dict[str, Any]) -> dict[str, Any]:
    labels = calibration["labels"]
    label_rows = []
    for label in LABEL_ORDER:
        row = labels[label]
        label_rows.append(
            {
                "label": label,
                "primary_event_count": int(row["primary_event_count"]),
                "registered_blocks": int(row["registered_blocks"]),
                "integrity_passed_blocks": int(row["integrity_passed_blocks"]),
                "selected_success_count": int(row["selected_success_count"]),
                "required_candidate_centered_events": row[
                    "required_candidate_centered_events"
                ],
            }
        )

    false_negative_blocks = []
    for block in calibration.get("blocks", []):
        if block.get("label") != "positive" or block.get(
            "joint_substitution_event"
        ) is True:
            continue
        false_negative_blocks.append(
            {
                "replicate_id": block["replicate_id"],
                "global_order_index": int(block["global_order_index"]),
                "stratum": int(block["stratum"]),
                "condition_results": block["condition_results"],
                "integrity_passed": bool(block["integrity_passed"]),
            }
        )

    decision = calibration["calibration_decision"]
    registered_condition_runs = int(
        calibration["registration_audit"]["registered_condition_run_count"]
    )
    return {
        "analysis_role": calibration["analysis_role"],
        "primary_event": calibration["primary_event"],
        "decision_basis": calibration["decision_basis"],
        "registered_schedule_length": int(
            calibration["registered_schedule_length"]
        ),
        "registered_condition_run_count": registered_condition_runs,
        "instrument_passed": bool(decision["instrument_passed"]),
        "positive_requirement_passed": bool(
            decision["positive_requirement_passed"]
        ),
        "negative_requirement_passed": bool(
            decision["negative_requirement_passed"]
        ),
        "full_integrity_passed": bool(calibration["full_integrity_passed"]),
        "independence_verified": bool(calibration["independence_verified"]),
        "label_rows": label_rows,
        "false_negative_blocks": false_negative_blocks,
        "scope_guards": calibration["scope_guards"],
        "preregistration_sha256": calibration["registration_audit"][
            "preregistration_sha256"
        ],
        "source_analysis": _source(calibration),
    }


def build_summaries(
    task_summary_paths: list[Path],
    calibration_analysis_path: Path,
    output_dir: Path,
) -> dict[str, str]:
    calibration = _load_calibration(calibration_analysis_path)
    paths = v2.build_summaries(task_summary_paths, output_dir)
    baseline = json.loads(Path(paths["baseline"]).read_text(encoding="utf-8"))
    research = json.loads(Path(paths["research"]).read_text(encoding="utf-8"))
    ablation = json.loads(Path(paths["ablation"]).read_text(encoding="utf-8"))
    calibration_summary = _calibration_summary(calibration)

    positive = next(
        row for row in calibration_summary["label_rows"] if row["label"] == "positive"
    )
    negative = next(
        row for row in calibration_summary["label_rows"] if row["label"] == "negative"
    )
    admitted_count = int(research["metric"]["value"])
    task_count = int(research["metric"]["descriptive_denominator"])

    baseline["schema_version"] = "effectslice-stage2-baseline-summary.v3"
    baseline["code"] = (
        "run_confirmation_v2.py, analyze_confirmation_v2.py, and "
        "build_stage2_summaries_v3.py"
    )
    baseline["plot_code"] = "build_stage2_figures_v3.py"

    research["schema_version"] = "effectslice-stage2-research-summary.v3"
    research["analysis"] = (
        f"{admitted_count}/{task_count} task-local slices passed the registered "
        "real-task admission gates. In the fresh interleaved diagnostic "
        f"replication, the candidate-centered event occurred in "
        f"{positive['primary_event_count']}/{positive['registered_blocks']} "
        f"planted-positive blocks and {negative['primary_event_count']}/"
        f"{negative['registered_blocks']} real-negative blocks, but the "
        "preregistered zero-tolerance calibration instrument did not pass. "
        "Neither result is a cross-paper effectiveness estimate."
    )
    research["calibration_replication"] = calibration_summary
    research["diagnostic_event_admission_ready"] = False
    research["general_effectslice_claim_ready"] = False
    research["cross_paper_claim_ready"] = False
    research["human_benefit_claim_ready"] = False
    research["code"] = (
        "analyze_confirmation_v2.py, "
        "analyze_confirmation_v3_interleaved_calibration.py, and "
        "build_stage2_summaries_v3.py"
    )
    research["plot_code"] = "build_stage2_figures_v3.py"
    research["exp_results_data_files"].append(calibration["_source_path"])

    ablation["schema_version"] = "effectslice-stage2-ablation-summary.v3"
    ablation["analysis"] = (
        "Real-task B/F/S condition successes and registered paired indicators "
        "remain separate from the diagnostic calibration families. The fresh "
        "interleaved calibration is reported as fixed-schedule discrimination, "
        "not as an IID population estimate or a passed admission rule."
    )
    ablation["calibration_replication"] = calibration_summary
    ablation["code"] = (
        "run_confirmation_v2.py, analyze_confirmation_v2.py, "
        "run_confirmation_v3_interleaved_calibration.py, and "
        "analyze_confirmation_v3_interleaved_calibration.py"
    )
    ablation["plot_code"] = "build_stage2_figures_v3.py"
    ablation["exp_results_data_files"].append(calibration["_source_path"])

    for name, payload in (
        ("baseline", baseline),
        ("research", research),
        ("ablation", ablation),
    ):
        v2._write(Path(paths[name]), payload)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build final Stage 2 v3 summaries with interleaved calibration"
    )
    parser.add_argument("--task-summary", action="append", type=Path, default=[])
    parser.add_argument(
        "--calibration-analysis",
        type=Path,
        default=DEFAULT_CALIBRATION_ANALYSIS,
    )
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "logs")
    args = parser.parse_args()
    summaries = args.task_summary or [
        RUN_ROOT
        / "derived"
        / "confirmation_v2_final"
        / "snap_mfse_confirmation_v2_summary.json",
        RUN_ROOT
        / "derived"
        / "confirmation_v2_final"
        / "toolformer_filter_confirmation_v2_summary.json",
    ]
    print(
        json.dumps(
            build_summaries(
                summaries,
                args.calibration_analysis,
                args.output_dir,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
