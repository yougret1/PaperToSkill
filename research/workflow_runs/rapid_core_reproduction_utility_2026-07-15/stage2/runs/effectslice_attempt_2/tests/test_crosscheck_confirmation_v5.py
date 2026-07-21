from __future__ import annotations

import json
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]

from crosscheck_confirmation_v5 import (
    DEFAULT_OUTPUT,
    DEFAULT_PREREGISTRATION,
    DEFAULT_RESULTS,
    DEFAULT_SUMMARY,
    _admission_decision,
    _compare_summary,
    _success_flags,
    build_crosscheck,
)


def test_v5_crosscheck_is_independent_of_bound_analyzer_and_adapter():
    source = (RUN_ROOT / "crosscheck_confirmation_v5.py").read_text(encoding="utf-8")
    assert "import analyze_confirmation" not in source
    assert "import analyze_confirmation_v4_role_repair" not in source
    assert "from analyze_confirmation" not in source


def test_v5_crosscheck_recomputes_frozen_decision_and_matches_analysis():
    contract = {
        "registered_blocks": 18,
        "maximum_baseline_successes": 2,
        "minimum_full_successes": 16,
        "minimum_slice_successes": 16,
        "maximum_full_minus_slice_success_gap": 2,
    }
    decision = _admission_decision({"B": 0, "F": 17, "S": 16}, contract)
    assert decision["passed"] is True

    resources = {
        "actions_used": 100,
        "provider_turns": 100,
        "transport_attempts": 101,
        "input_tokens": 200,
        "output_tokens": 300,
        "public_test_requests": 20,
        "public_test_passes": 19,
        "action_counts": {"submit": 54},
    }
    family = {
        "operational_success_counts": {"B": 0, "F": 17, "S": 16},
        "mean_task_score": {"B": 0.0, "F": 0.96, "S": 0.95},
        "admission_decision": decision,
    }
    crosscheck = {
        "registered_blocks": 18,
        "registered_condition_runs": 54,
        "families": {"toolformer_natural": family},
        "natural_candidate_admitted": True,
        "resource_summary": resources,
    }
    analysis = {
        "registered_blocks": 18,
        "registered_condition_runs": 54,
        "family_summaries": {"toolformer_natural": family},
        "natural_candidate_decision": decision,
        "resource_summary": resources,
    }
    _compare_summary(crosscheck, analysis)

    changed = dict(analysis)
    changed["natural_candidate_decision"] = {"passed": False}
    with pytest.raises(ValueError, match="natural-candidate"):
        _compare_summary(crosscheck, changed)


def test_exact_scorer_and_operational_success_have_distinct_semantics():
    metric = {"contract_passed": True, "patch_applied": True}
    case_scores = [1] * 61 + [0] * 3

    exact_scorer_success, operational_success = _success_flags(
        metric, 61 / 64, case_scores
    )

    assert exact_scorer_success is False
    assert operational_success is True


def test_default_crosscheck_rebuilds_the_actual_198_file_bundle(tmp_path):
    output = tmp_path / "independent_crosscheck.json"
    build_crosscheck(
        DEFAULT_PREREGISTRATION,
        DEFAULT_RESULTS,
        DEFAULT_SUMMARY,
        output,
    )

    rebuilt = json.loads(output.read_text(encoding="utf-8"))
    canonical = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    assert rebuilt["raw_file_count"] == 198
    assert rebuilt["raw_evidence_digest"] == canonical["raw_evidence_digest"]
    assert rebuilt["families"] == canonical["families"]
    assert rebuilt["natural_candidate_admitted"] is True
