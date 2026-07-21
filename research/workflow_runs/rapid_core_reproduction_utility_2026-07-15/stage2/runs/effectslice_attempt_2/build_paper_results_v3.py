from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
TASK_MACRO_PREFIX = {
    "snap_mfse": "SnapMFSE",
    "toolformer_filter": "ToolformerFilter",
}
INDICATOR_FIELDS = {
    "full_benefit": "FullBenefit",
    "slice_preservation": "SlicePreservation",
    "slice_benefit": "SliceBenefit",
}
CALIBRATION_MACRO_PREFIX = {
    "positive": "CalibrationPositive",
    "negative": "CalibrationNegative",
    "identity": "CalibrationIdentity",
}


def _load(path: Path, *, schema: str) -> dict[str, Any]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected summary schema: {source}")
    if payload.get("statistical_unit") != "independent_agent_run":
        raise ValueError("paper results require independent_agent_run task summaries")
    return payload


def _macro(name: str, value: Any) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def _decision(classification: str) -> str:
    if classification == "task_local_admission_passed":
        return "Admit"
    if classification == "task_local_admission_rejected":
        return "Reject"
    raise ValueError(f"unsupported task classification: {classification}")


def build_paper_results(
    *,
    research_path: Path,
    ablation_path: Path,
    output_tex: Path,
    output_manifest: Path,
) -> dict[str, str]:
    research_file = Path(research_path).resolve()
    ablation_file = Path(ablation_path).resolve()
    research = _load(
        research_file,
        schema="effectslice-stage2-research-summary.v3",
    )
    ablation = _load(
        ablation_file,
        schema="effectslice-stage2-ablation-summary.v3",
    )
    research_rows = {row["task_key"]: row for row in research["task_rows"]}
    ablation_rows = {row["task_key"]: row for row in ablation["task_rows"]}
    if not research_rows or set(research_rows) != set(ablation_rows):
        raise ValueError("paper summaries must contain the same task keys")
    unknown_tasks = set(research_rows) - set(TASK_MACRO_PREFIX)
    if unknown_tasks:
        raise ValueError(f"paper macro mapping is missing tasks: {sorted(unknown_tasks)}")
    denominator = int(ablation["replicate_denominator_per_task"])
    hidden_checks = int(ablation["clustered_hidden_checks_per_run"])
    task_count = len(research_rows)
    real_task_provider_conversations = task_count * denominator * 3
    admission_count = sum(
        row.get("classification") == "task_local_admission_passed"
        for row in research_rows.values()
    )

    research_calibration = research.get("calibration_replication")
    ablation_calibration = ablation.get("calibration_replication")
    if research_calibration != ablation_calibration:
        raise ValueError("paper summaries contain different calibration evidence")
    if not isinstance(research_calibration, dict):
        raise ValueError("paper summaries are missing calibration evidence")
    calibration = research_calibration
    calibration_rows = {
        row["label"]: row for row in calibration.get("label_rows", [])
    }
    if set(calibration_rows) != set(CALIBRATION_MACRO_PREFIX):
        raise ValueError("paper calibration labels are incomplete")
    calibration_provider_conversations = int(
        calibration["registered_condition_run_count"]
    )
    calibration_block_count = int(calibration["registered_schedule_length"])
    total_primary_provider_conversations = (
        real_task_provider_conversations + calibration_provider_conversations
    )

    lines = [
        "% Generated from Stage 2 v3 JSON. Do not edit empirical values by hand.",
        _macro("EffectSliceTaskCount", task_count),
        _macro("EffectSliceReplicatesPerTask", denominator),
        _macro("EffectSliceRealTaskProviderConversations", real_task_provider_conversations),
        _macro("EffectSliceCalibrationProviderConversations", calibration_provider_conversations),
        _macro("EffectSlicePrimaryProviderConversations", total_primary_provider_conversations),
        _macro("EffectSliceHiddenChecksPerRun", hidden_checks),
        _macro("EffectSliceAdmissions", admission_count),
        _macro("CalibrationBlockCount", calibration_block_count),
        _macro(
            "CalibrationInstrumentDecision",
            "Pass" if calibration["instrument_passed"] else "Fail",
        ),
        _macro(
            "CalibrationIntegrityDecision",
            "Pass" if calibration["full_integrity_passed"] else "Fail",
        ),
    ]
    macro_values: dict[str, Any] = {
        "EffectSliceTaskCount": task_count,
        "EffectSliceReplicatesPerTask": denominator,
        "EffectSliceRealTaskProviderConversations": real_task_provider_conversations,
        "EffectSliceCalibrationProviderConversations": calibration_provider_conversations,
        "EffectSlicePrimaryProviderConversations": total_primary_provider_conversations,
        "EffectSliceHiddenChecksPerRun": hidden_checks,
        "EffectSliceAdmissions": admission_count,
        "CalibrationBlockCount": calibration_block_count,
        "CalibrationInstrumentDecision": (
            "Pass" if calibration["instrument_passed"] else "Fail"
        ),
        "CalibrationIntegrityDecision": (
            "Pass" if calibration["full_integrity_passed"] else "Fail"
        ),
    }
    for task_key in research_rows:
        prefix = TASK_MACRO_PREFIX[task_key]
        research_row = research_rows[task_key]
        ablation_row = ablation_rows[task_key]
        condition_counts = ablation_row["condition_successes"]
        for condition in ("B", "F", "S"):
            name = f"{prefix}{condition}Successes"
            value = int(condition_counts[condition])
            lines.append(_macro(name, value))
            macro_values[name] = value
        for field, field_prefix in INDICATOR_FIELDS.items():
            indicator = research_row[field]
            success_name = f"{prefix}{field_prefix}Successes"
            lower_name = f"{prefix}{field_prefix}CPLower"
            successes = int(indicator["successes"])
            lower = f"{float(indicator['one_sided_cp_lower']):.3f}"
            if int(indicator["total"]) != denominator:
                raise ValueError("paper indicator denominator mismatch")
            lines.append(_macro(success_name, successes))
            lines.append(_macro(lower_name, lower))
            macro_values[success_name] = successes
            macro_values[lower_name] = lower
        decision_name = f"{prefix}Decision"
        decision = _decision(str(research_row["classification"]))
        lines.append(_macro(decision_name, decision))
        macro_values[decision_name] = decision

    for label, prefix in CALIBRATION_MACRO_PREFIX.items():
        row = calibration_rows[label]
        event_name = f"{prefix}Events"
        denominator_name = f"{prefix}Blocks"
        events = int(row["primary_event_count"])
        blocks = int(row["registered_blocks"])
        lines.append(_macro(event_name, events))
        lines.append(_macro(denominator_name, blocks))
        macro_values[event_name] = events
        macro_values[denominator_name] = blocks

    false_negative_blocks = calibration.get("false_negative_blocks", [])
    false_negative_ids = ",".join(
        str(row["replicate_id"]) for row in false_negative_blocks
    )
    lines.append(_macro("CalibrationFalseNegativeCount", len(false_negative_blocks)))
    lines.append(_macro("CalibrationFalseNegativeIDs", false_negative_ids or "None"))
    macro_values["CalibrationFalseNegativeCount"] = len(false_negative_blocks)
    macro_values["CalibrationFalseNegativeIDs"] = false_negative_ids or "None"

    tex_path = Path(output_tex).resolve()
    manifest_path = Path(output_manifest).resolve()
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    source_sha256 = {
        research_file.as_posix(): hashlib.sha256(research_file.read_bytes()).hexdigest(),
        ablation_file.as_posix(): hashlib.sha256(ablation_file.read_bytes()).hexdigest(),
    }
    manifest = {
        "schema_version": "effectslice-paper-results-manifest.v3",
        "analysis_units": {
            "real_task": "matched_BFS_replicate",
            "calibration": "registered_interleaved_BFS_block",
        },
        "real_task_replicates_per_task": denominator,
        "real_task_provider_conversations": real_task_provider_conversations,
        "calibration_provider_conversations": calibration_provider_conversations,
        "total_primary_provider_conversations": total_primary_provider_conversations,
        "hidden_checks_per_run": hidden_checks,
        "calibration_instrument_passed": bool(calibration["instrument_passed"]),
        "calibration_independence_verified": bool(
            calibration["independence_verified"]
        ),
        "calibration_preregistration_sha256": calibration[
            "preregistration_sha256"
        ],
        "source_sha256": source_sha256,
        "output_tex": tex_path.as_posix(),
        "output_tex_sha256": hashlib.sha256(tex_path.read_bytes()).hexdigest(),
        "macros": macro_values,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"tex": str(tex_path), "manifest": str(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate traceable V3 LaTeX macros from Stage 2 summaries"
    )
    parser.add_argument(
        "--research-summary",
        type=Path,
        default=RUN_ROOT / "logs" / "research_summary.json",
    )
    parser.add_argument(
        "--ablation-summary",
        type=Path,
        default=RUN_ROOT / "logs" / "ablation_summary.json",
    )
    parser.add_argument(
        "--output-tex",
        type=Path,
        default=PROJECT_ROOT
        / "paper"
        / "effectslice_aaai"
        / "generated_results_v3.tex",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=RUN_ROOT / "manuscript" / "generated_results_manifest_v3.json",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            build_paper_results(
                research_path=args.research_summary,
                ablation_path=args.ablation_summary,
                output_tex=args.output_tex,
                output_manifest=args.output_manifest,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
