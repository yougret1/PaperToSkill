from __future__ import annotations

from collections import Counter
import re

from build_confirmation_v3_interleaved_calibration import (
    LABEL_SPECS,
    artifact_payloads,
    build_interleaved_schedule,
)


def atom_ids(payload: bytes) -> list[str]:
    return re.findall(r"\(`(T\d+)`\)", payload.decode("utf-8"))


def test_interleaved_schedule_is_deterministic_and_stratified():
    first = build_interleaved_schedule()
    second = build_interleaved_schedule()

    assert first == second
    assert len(first) == 42
    assert Counter(row["label"] for row in first) == {
        "identity": 6,
        "positive": 18,
        "negative": 18,
    }
    assert len({row["replicate_id"] for row in first}) == 42
    assert all(set(row["condition_order"]) == {"B", "F", "S"} for row in first)
    assert all(
        {row["label"] for row in first if row["stratum"] == stratum}
        >= {"positive", "negative"}
        for stratum in range(1, 19)
    )
    assert all(
        any(
            row["label"] == "identity" and row["stratum"] == stratum
            for row in first
        )
        for stratum in (1, 4, 7, 10, 13, 16)
    )


def test_artifact_controls_have_registered_truth_relations(tmp_path):
    original = (
        b"# Card\n\n"
        b"1. First (`T01`)\n\n"
        b"2. Second (`T02`)\n\n"
        b"3. Third (`T03`)\n\n"
        b"4. Fourth (`T04`)\n\n"
        b"5. Fifth (`T05`)\n"
    )
    prefix = b"# Card\n\n1. First (`T01`)\n"
    payloads = artifact_payloads(original, prefix)

    assert payloads["identity"]["full"] == payloads["identity"]["selected"]
    assert payloads["positive"]["selected"] == payloads["identity"]["selected"]
    assert set(atom_ids(payloads["positive"]["selected"])) < set(
        atom_ids(payloads["positive"]["full"])
    )
    assert set(atom_ids(payloads["negative"]["selected"])) == {"T01"}
    assert set(atom_ids(payloads["negative"]["selected"])) < set(
        atom_ids(payloads["negative"]["full"])
    )


def test_label_specs_freeze_calibration_roles():
    assert LABEL_SPECS["identity"]["underlying_control"] == "identity"
    assert LABEL_SPECS["positive"]["underlying_control"] == "planted"
    assert LABEL_SPECS["negative"]["underlying_control"] == "planted"
    assert LABEL_SPECS["positive"]["required_candidate_centered_events"] == 18
    assert LABEL_SPECS["negative"]["required_candidate_centered_events"] == (
        "strictly_less_than_registered_blocks"
    )
