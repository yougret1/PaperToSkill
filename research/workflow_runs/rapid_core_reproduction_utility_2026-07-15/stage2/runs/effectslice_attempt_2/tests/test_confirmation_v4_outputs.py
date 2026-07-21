from __future__ import annotations

import json
from pathlib import Path

from build_paper_results_v4 import build_paper_results
from build_stage2_figures_v4 import build_figure
from build_stage2_summaries_v4 import DEFAULT_ANALYSIS, build_summary


def test_builds_traceable_summary_figure_and_final_v3_macros(tmp_path: Path):
    summary_path = tmp_path / "summary.json"
    figure_path = tmp_path / "figure.png"
    report_path = tmp_path / "figure_report.json"
    tex_path = tmp_path / "generated_results_v3.tex"
    manifest_path = tmp_path / "manifest.json"

    build_summary(DEFAULT_ANALYSIS, summary_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["registered_blocks"] == 60
    assert summary["registered_condition_runs"] == 180
    assert summary["real_candidate_admissions"] == 0
    assert summary["calibration"]["passed"] is True
    assert summary["analyzer_disclosure"]["raw_evidence_modified"] is False
    assert summary["sla"]["registered_gap_check_is_logically_redundant"] is True
    assert summary["resource_summary"]["public_test_failures"] == 12
    assert summary["resource_summary"]["extra_transport_attempts"] == 14
    assert summary["families"][0]["paired_success_status"]["matches"] == 6
    assert len(summary["block_scores"]) == 60

    build_figure(summary_path, figure_path, report_path)
    assert figure_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["invented_values"] is False
    assert report["population_inference_shown"] is False

    build_paper_results(summary_path, tex_path, manifest_path)
    tex = tex_path.read_text(encoding="utf-8")
    assert "\\newcommand{\\VFourProviderConversations}{180}" in tex
    assert "\\newcommand{\\SnapRealFSuccesses}{15}" in tex
    assert "\\newcommand{\\ToolformerRealSSuccesses}{8}" in tex
    assert "\\newcommand{\\PlantedPositiveDecision}{Pass}" in tex
    assert "\\newcommand{\\IdentityControlMatches}{5}" in tex
    assert "\\newcommand{\\VFourPublicTestFailures}{12}" in tex
    assert "\\newcommand{\\SnapRealSuccessMatches}{6}" in tex
    assert "\\newcommand{\\IdentityControlDecision}{Instr. Pass}" in tex

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "independent_crosscheck" in manifest["analysis_provenance"]
