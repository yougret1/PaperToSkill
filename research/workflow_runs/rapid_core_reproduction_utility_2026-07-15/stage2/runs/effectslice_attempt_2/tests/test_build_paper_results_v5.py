from __future__ import annotations

import json

import build_paper_results_v5 as builder


def test_builds_combined_v4_v5_macros_and_manifest(tmp_path):
    output = tmp_path / "generated_results_v3.tex"
    manifest_path = tmp_path / "manifest.json"

    result = builder.build_paper_results(
        builder.DEFAULT_V4_SUMMARY,
        builder.DEFAULT_V5_ANALYSIS,
        builder.DEFAULT_V5_CROSSCHECK,
        output,
        manifest_path,
    )

    assert result["tex"] == output.resolve().as_posix()
    text = output.read_text(encoding="utf-8")
    assert r"\newcommand{\ToolformerNaturalBSuccesses}{0}" in text
    assert r"\newcommand{\ToolformerNaturalFSuccesses}{18}" in text
    assert r"\newcommand{\ToolformerNaturalSSuccesses}{17}" in text
    assert r"\newcommand{\ToolformerNaturalDecision}{Admit}" in text
    assert r"\newcommand{\SnapRealDecision}{Reject}" in text
    assert r"\newcommand{\PlantedPositiveDecision}{Pass}" in text
    assert r"\newcommand{\IdentityControlDecision}{Pass}" in text
    assert r"\newcommand{\AllProviderConversations}{234}" in text
    assert r"\newcommand{\NonPlantedAdmissions}{1}" in text

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "effectslice-paper-results-manifest.v5"
    assert manifest["run_root"].endswith("effectslice_attempt_2")
    assert manifest["macros"]["VFiveRawFileCount"] == 198
    assert manifest["output_sets"]["v4"]["raw_root"] == (
        "experiment_results/confirmation_v4"
    )
    assert manifest["output_sets"]["v5"]["raw_root"] == (
        "experiment_results/confirmation_v5r2"
    )
    assert len(manifest["output_sets"]["v4"]["raw_inventory"]) == 660
    assert len(manifest["output_sets"]["v5"]["raw_inventory"]) == 198
    assert manifest["sources"]["v5_analysis"]["sha256"] == (
        "8b7849590c3a8080f7ed7c06eaea360c16833f0dfec62b855223740cf3e7879a"
    )


def test_default_v5_crosscheck_is_independent_and_complete():
    cross = json.loads(builder.DEFAULT_V5_CROSSCHECK.read_text(encoding="utf-8"))

    assert cross["implementation"]["imports_bound_analyzer"] is False
    assert cross["implementation"]["imports_compatibility_adapter"] is False
    assert cross["validation"]["all_outputs_complete"] is True
    assert cross["validation"]["all_private_score_counts_equal_one"] is True
    assert cross["validation"]["private_feedback_exposed"] is False
    assert cross["validation"]["provider_response_ids_unique"] is True
