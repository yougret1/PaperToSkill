from __future__ import annotations

from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]

from crosscheck_confirmation_v5 import _admission_decision, _compare_summary


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
