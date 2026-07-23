from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import verify_remote_only_successor as verifier  # noqa: E402


def copied_successor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    destination = tmp_path / "successor"
    shutil.copytree(verifier.SUCCESSOR, destination)
    monkeypatch.setattr(verifier, "SUCCESSOR", destination)
    return destination


def mutate(path: Path, update: object) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    if not callable(update):
        raise TypeError("update must be callable")
    update(value)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def test_remote_only_successor_verifies() -> None:
    result = verifier.verify()
    assert result["status"] == "remote_only_successor_verified"
    assert result["required_remote_rows"] == 1296
    assert result["required_local_rows"] == 0
    assert result["required_model_slots"] == sorted(verifier.REQUIRED_MODEL_SLOTS)


def test_forbidden_local_design_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)
    path = successor / "candidate_matrix.json"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nopen_seed_anchor\n",
        encoding="utf-8",
    )
    with pytest.raises(verifier.SuccessorVerificationError, match="leaked"):
        verifier.verify_no_local_design()


def test_luna_cannot_be_demoted_to_optional(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)

    def demote(value: dict[str, object]) -> None:
        slots = value["model_slots"]
        assert isinstance(slots, list)
        next(row for row in slots if row["slot_id"] == "gpt_5_6_luna")["required"] = False

    mutate(successor / "model_ablation_registry.json", demote)
    with pytest.raises(verifier.SuccessorVerificationError, match="required model"):
        verifier.verify_models()


def test_provider_calls_cannot_precede_successor_anchor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)

    def mark_started(value: dict[str, object]) -> None:
        value["provider_calls_started"] = True

    mutate(successor / "successor_registration.json", mark_started)
    with pytest.raises(verifier.SuccessorVerificationError, match="must not precede"):
        verifier.verify_registration()


def test_generated_token_schema_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)

    def add_token_field(value: dict[str, object]) -> None:
        result = value["result_canonicalization_contract"]
        assert isinstance(result, dict)
        required = result["required_result_row_fields"]
        assert isinstance(required, list)
        required.append("generated_token_ids")

    mutate(successor / "materialization_contract.json", add_token_field)
    with pytest.raises(verifier.SuccessorVerificationError, match="generated token"):
        verifier.verify_contract()


def test_private_registry_overlap_count_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)

    def corrupt_count(value: dict[str, object]) -> None:
        value["parent_overlap_audit"]["source_registry"]["private_case_id"][
            "effectslice_fg1"
        ]["expected_file_count"] = 1

    mutate(successor / "materialization_contract.json", corrupt_count)
    with pytest.raises(verifier.SuccessorVerificationError, match="private-registry"):
        verifier.verify_contract()


def test_bundle_byte_tampering_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    successor = copied_successor(tmp_path, monkeypatch)
    path = successor / "paper_registry.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(verifier.SuccessorVerificationError, match="sha256 mismatch"):
        verifier.verify_bundle()
