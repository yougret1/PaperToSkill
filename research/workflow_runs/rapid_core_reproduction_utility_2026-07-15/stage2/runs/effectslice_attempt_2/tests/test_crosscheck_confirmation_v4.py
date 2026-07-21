from __future__ import annotations

import json
from pathlib import Path

from crosscheck_confirmation_v4 import (
    DEFAULT_PREREGISTRATION,
    DEFAULT_RESULTS,
    DEFAULT_SUMMARY,
    _admission_decision,
    build_crosscheck,
)


def test_crosscheck_recomputes_registered_v4_from_raw_outputs(tmp_path: Path):
    output = tmp_path / "independent_crosscheck.json"
    build_crosscheck(DEFAULT_PREREGISTRATION, DEFAULT_RESULTS, DEFAULT_SUMMARY, output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["registered_blocks"] == 60
    assert payload["registered_condition_runs"] == 180
    assert payload["raw_file_count"] == 660
    assert payload["validation"]["provider_response_id_count"] == 1379
    assert payload["validation"]["minimum_cases_for_operational_success"] == 61
    assert payload["registered_gap_check_is_logically_redundant"] is True
    assert payload["families"]["snap_mfse"]["operational_success_counts"] == {
        "B": 0,
        "F": 15,
        "S": 5,
    }
    assert payload["families"]["toolformer_positive"]["admission_decision"][
        "passed"
    ] is True
    assert payload["families"]["toolformer_identity"]["identity_instrumentation"][
        "passed"
    ] is True
    assert payload["resource_summary"]["extra_transport_attempts"] == 14
    assert payload["expected_summary"]["all_compared_fields_match"] is True


def test_registered_gap_field_is_redundant_at_the_frozen_thresholds():
    contract = {
        "maximum_baseline_successes": 2,
        "minimum_full_successes": 16,
        "minimum_slice_successes": 16,
        "maximum_full_minus_slice_success_gap": 2,
    }
    decision = _admission_decision({"B": 2, "F": 18, "S": 16}, contract)

    assert decision["checks"]["slice_sufficiency"] is True
    assert decision["checks"]["slice_shortfall"] is True
    assert decision["passed"] is True
