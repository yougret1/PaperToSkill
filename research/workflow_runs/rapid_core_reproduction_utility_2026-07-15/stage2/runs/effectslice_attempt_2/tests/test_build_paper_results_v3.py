from __future__ import annotations

import json
import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_paper_results_v3 import build_paper_results  # noqa: E402


def _calibration() -> dict:
    return {
        "registered_schedule_length": 42,
        "registered_condition_run_count": 126,
        "instrument_passed": False,
        "positive_requirement_passed": False,
        "negative_requirement_passed": True,
        "full_integrity_passed": True,
        "independence_verified": False,
        "preregistration_sha256": "a" * 64,
        "false_negative_blocks": [{"replicate_id": "p015"}],
        "label_rows": [
            {
                "label": "positive",
                "primary_event_count": 17,
                "registered_blocks": 18,
            },
            {
                "label": "negative",
                "primary_event_count": 0,
                "registered_blocks": 18,
            },
            {
                "label": "identity",
                "primary_event_count": 5,
                "registered_blocks": 6,
            },
        ],
    }


def _indicator(successes: int, lower: float) -> dict:
    return {
        "successes": successes,
        "total": 18,
        "one_sided_cp_lower": lower,
    }


def _write_summaries(root: Path) -> tuple[Path, Path]:
    research = {
        "schema_version": "effectslice-stage2-research-summary.v3",
        "statistical_unit": "independent_agent_run",
        "task_rows": [
            {
                "task_key": "snap_mfse",
                "classification": "task_local_admission_rejected",
                "full_benefit": _indicator(13, 0.454269),
                "slice_preservation": _indicator(3, 0.032857),
                "slice_benefit": _indicator(5, 0.091598),
            },
            {
                "task_key": "toolformer_filter",
                "classification": "task_local_admission_rejected",
                "full_benefit": _indicator(18, 0.804661),
                "slice_preservation": _indicator(6, 0.127037),
                "slice_benefit": _indicator(6, 0.127037),
            },
        ],
        "calibration_replication": _calibration(),
    }
    ablation = {
        "schema_version": "effectslice-stage2-ablation-summary.v3",
        "statistical_unit": "independent_agent_run",
        "replicate_denominator_per_task": 18,
        "clustered_hidden_checks_per_run": 64,
        "task_rows": [
            {
                "task_key": "snap_mfse",
                "condition_successes": {"B": 0, "F": 13, "S": 5},
            },
            {
                "task_key": "toolformer_filter",
                "condition_successes": {"B": 0, "F": 18, "S": 6},
            },
        ],
        "calibration_replication": _calibration(),
    }
    research_path = root / "research.json"
    ablation_path = root / "ablation.json"
    research_path.write_text(json.dumps(research), encoding="utf-8")
    ablation_path.write_text(json.dumps(ablation), encoding="utf-8")
    return research_path, ablation_path


def test_generates_v3_real_task_and_calibration_macros(tmp_path):
    research_path, ablation_path = _write_summaries(tmp_path)
    output_tex = tmp_path / "generated_results_v3.tex"
    output_manifest = tmp_path / "generated_results_manifest_v3.json"

    build_paper_results(
        research_path=research_path,
        ablation_path=ablation_path,
        output_tex=output_tex,
        output_manifest=output_manifest,
    )

    latex = output_tex.read_text(encoding="utf-8")
    manifest = json.loads(output_manifest.read_text(encoding="utf-8"))
    assert r"\newcommand{\EffectSliceRealTaskProviderConversations}{108}" in latex
    assert r"\newcommand{\EffectSliceCalibrationProviderConversations}{126}" in latex
    assert r"\newcommand{\EffectSlicePrimaryProviderConversations}{234}" in latex
    assert r"\newcommand{\EffectSliceAdmissions}{0}" in latex
    assert r"\newcommand{\CalibrationPositiveEvents}{17}" in latex
    assert r"\newcommand{\CalibrationNegativeEvents}{0}" in latex
    assert r"\newcommand{\CalibrationIdentityEvents}{5}" in latex
    assert r"\newcommand{\CalibrationInstrumentDecision}{Fail}" in latex
    assert r"\newcommand{\CalibrationFalseNegativeIDs}{p015}" in latex
    assert manifest["schema_version"] == "effectslice-paper-results-manifest.v3"
    assert manifest["total_primary_provider_conversations"] == 234
    assert manifest["calibration_instrument_passed"] is False
    assert manifest["calibration_independence_verified"] is False
    assert len(manifest["source_sha256"]) == 2


def test_rejects_disagreeing_calibration_summaries(tmp_path):
    research_path, ablation_path = _write_summaries(tmp_path)
    ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
    ablation["calibration_replication"]["instrument_passed"] = True
    ablation_path.write_text(json.dumps(ablation), encoding="utf-8")

    try:
        build_paper_results(
            research_path=research_path,
            ablation_path=ablation_path,
            output_tex=tmp_path / "result.tex",
            output_manifest=tmp_path / "result.json",
        )
    except ValueError as error:
        assert "different calibration" in str(error)
    else:
        raise AssertionError("divergent calibration summaries should be rejected")
