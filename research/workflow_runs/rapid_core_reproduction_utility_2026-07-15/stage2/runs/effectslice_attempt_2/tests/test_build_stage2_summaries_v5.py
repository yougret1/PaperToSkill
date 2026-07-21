from __future__ import annotations

import json

import build_stage2_summaries_v5 as builder


def test_builds_final_finite_schedule_summaries(tmp_path):
    result = builder.build_summaries(
        builder.DEFAULT_V4,
        builder.DEFAULT_V5_ANALYSIS,
        builder.DEFAULT_V5_CROSSCHECK,
        tmp_path,
    )

    baseline = json.loads((tmp_path / "baseline_summary.json").read_text())
    research = json.loads((tmp_path / "research_summary.json").read_text())
    ablation = json.loads((tmp_path / "ablation_summary.json").read_text())
    v5 = json.loads((tmp_path / "confirmation_v5_summary.json").read_text())

    assert set(result) == {"baseline", "research", "ablation", "confirmation_v5"}
    assert baseline["metric"] == {
        "name": "full_artifact_operational_successes",
        "value": 50,
        "direction": "higher_is_better",
        "descriptive_denominator": 54,
    }
    assert research["metric"]["value"] == 1
    assert research["metric"]["descriptive_denominator"] == 3
    assert research["candidate_rows"][2]["selected_after_v4"] is True
    assert ablation["identity_instrumentation"]["identity_instrumentation"]["passed"] is True
    assert v5["family"]["operational_success_counts"] == {"B": 0, "F": 18, "S": 17}
    assert v5["validation"]["private_feedback_exposed"] is False
    assert v5["selection_disclosure"]["selected_after_v4_analysis"] is True

    combined = json.dumps([baseline, research, ablation, v5]).lower()
    for forbidden in ("clopper", "independent_agent_run", "population_guarantee\": true"):
        assert forbidden not in combined
