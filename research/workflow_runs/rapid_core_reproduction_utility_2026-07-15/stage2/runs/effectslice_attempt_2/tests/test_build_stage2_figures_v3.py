from __future__ import annotations

import json
import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_figures_v3 import (  # noqa: E402
    build_stage2_figures,
    collect_figure_data,
)


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


def _write_summaries(root: Path) -> None:
    logs = root / "logs"
    logs.mkdir(parents=True)
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
    research = {
        "schema_version": "effectslice-stage2-research-summary.v3",
        "statistical_unit": "independent_agent_run",
        "task_rows": [
            {
                "task_key": "snap_mfse",
                "full_benefit": {
                    "successes": 13,
                    "total": 18,
                    "one_sided_cp_lower": 0.454,
                    "minimum_prevalence": 0.8,
                },
                "slice_preservation": {
                    "successes": 3,
                    "total": 18,
                    "one_sided_cp_lower": 0.033,
                    "minimum_prevalence": 0.8,
                },
                "slice_benefit": {
                    "successes": 5,
                    "total": 18,
                    "one_sided_cp_lower": 0.092,
                    "minimum_prevalence": 0.8,
                },
            },
            {
                "task_key": "toolformer_filter",
                "full_benefit": {
                    "successes": 18,
                    "total": 18,
                    "one_sided_cp_lower": 0.805,
                    "minimum_prevalence": 0.8,
                },
                "slice_preservation": {
                    "successes": 6,
                    "total": 18,
                    "one_sided_cp_lower": 0.127,
                    "minimum_prevalence": 0.8,
                },
                "slice_benefit": {
                    "successes": 6,
                    "total": 18,
                    "one_sided_cp_lower": 0.127,
                    "minimum_prevalence": 0.8,
                },
            },
        ],
        "calibration_replication": _calibration(),
    }
    (logs / "ablation_summary.json").write_text(
        json.dumps(ablation), encoding="utf-8"
    )
    (logs / "research_summary.json").write_text(
        json.dumps(research), encoding="utf-8"
    )


def test_collects_real_task_and_calibration_values(tmp_path):
    _write_summaries(tmp_path)

    data = collect_figure_data(tmp_path)

    assert data["condition_successes"]["snap_mfse"] == [0, 13, 5]
    assert data["indicator_successes"]["toolformer_filter"] == [18, 6, 6]
    assert data["calibration"]["event_counts"] == [17, 0, 5]
    assert data["calibration"]["denominators"] == [18, 18, 6]
    assert data["calibration"]["instrument_passed"] is False


def test_builds_v3_png_and_traceability_report(tmp_path):
    _write_summaries(tmp_path)

    outputs = build_stage2_figures(tmp_path, tmp_path / "figures")

    figure = Path(outputs["figure"])
    report = json.loads(Path(outputs["report"]).read_text(encoding="utf-8"))
    assert figure.stat().st_size > 1000
    assert report["schema_version"] == "effectslice-plot-aggregation-report.v3"
    assert report["calibration_analysis_unit"] == "registered_interleaved_BFS_block"
    assert report["calibration_instrument_passed"] is False
    assert report["calibration_preregistration_sha256"] == "a" * 64
    assert report["data_sources"] == [
        "logs/ablation_summary.json",
        "logs/research_summary.json",
    ]
