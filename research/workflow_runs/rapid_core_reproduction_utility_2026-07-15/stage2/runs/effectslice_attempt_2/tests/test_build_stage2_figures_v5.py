from __future__ import annotations

import json

import matplotlib.image as mpimg

import build_stage2_figures_v5 as builder


def test_builds_combined_v4_v5_figure_from_registered_data(tmp_path):
    output = tmp_path / "combined.png"
    report_path = tmp_path / "report.json"

    result = builder.build_figure(
        builder.DEFAULT_V4_SUMMARY,
        builder.DEFAULT_V5_ANALYSIS,
        output,
        report_path,
    )

    assert result["figure"] == output.resolve().as_posix()
    assert output.stat().st_size > 50_000
    image = mpimg.imread(output)
    assert image.shape[0] >= 900
    assert image.shape[1] >= 2500

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == "effectslice-plot-aggregation-report.v5"
    assert report["invented_values"] is False
    assert report["population_inference_shown"] is False
    assert report["v5_selected_after_v4_disclosed"] is True
    assert set(report["sources"]) == {"v4_summary", "v5_analysis"}
