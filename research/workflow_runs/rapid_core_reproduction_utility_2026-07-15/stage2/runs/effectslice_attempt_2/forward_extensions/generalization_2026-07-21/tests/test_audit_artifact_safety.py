from __future__ import annotations

import sys
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

import audit_artifact_safety as safety  # noqa: E402


@pytest.fixture
def credentials(monkeypatch: pytest.MonkeyPatch) -> bytes:
    value = b"credential-value-used-only-by-the-test"
    monkeypatch.setattr(
        safety.runner,
        "load_credentials",
        lambda _: ({"test_slot": value.decode("ascii")}, {}),
    )
    return value


def test_clean_artifacts_pass_complete_enumeration(
    tmp_path: Path, credentials: bytes
) -> None:
    (tmp_path / "clean.txt").write_text("clean artifact", encoding="utf-8")
    result, passed = safety.audit(tmp_path, [tmp_path], minimum_files=1)
    assert passed is True
    assert result["complete_enumeration"] is True
    assert result["credential_values_recorded"] is False


def test_incomplete_enumeration_fails(tmp_path: Path, credentials: bytes) -> None:
    (tmp_path / "only.txt").write_text("one file", encoding="utf-8")
    result, passed = safety.audit(tmp_path, [tmp_path], minimum_files=2)
    assert passed is False
    assert result["complete_enumeration"] is False


@pytest.mark.parametrize(
    ("content", "result_key"),
    (
        (
            b"credential-value-used-only-by-the-test",
            "exact_credential_reflection_count",
        ),
        (b"Authorization: Bearer sk-abcdefghijklmnop", "generic_credential_pattern_match_count"),
        (b"global_local_anchor_schedule", "forbidden_local_model_design_match_count"),
    ),
)
def test_safety_markers_fail_closed(
    tmp_path: Path,
    credentials: bytes,
    content: bytes,
    result_key: str,
) -> None:
    (tmp_path / "artifact.bin").write_bytes(content)
    result, passed = safety.audit(tmp_path, [tmp_path], minimum_files=1)
    assert passed is False
    assert result[result_key] == 1


def test_opaque_response_ciphertext_is_not_a_generic_credential_hit(
    tmp_path: Path, credentials: bytes
) -> None:
    content = b'{"encrypted_content":"sk-' + (b"a" * 64) + b'","output":"clean"}'
    (tmp_path / "response.json").write_bytes(content)

    result, passed = safety.audit(tmp_path, [tmp_path], minimum_files=1)

    assert passed is True
    assert result["generic_credential_pattern_match_count"] == 0


def test_exact_credential_in_opaque_response_field_still_fails(
    tmp_path: Path, credentials: bytes
) -> None:
    content = b'{"encrypted_content":"' + credentials + b'"}'
    (tmp_path / "response.json").write_bytes(content)

    result, passed = safety.audit(tmp_path, [tmp_path], minimum_files=1)

    assert passed is False
    assert result["exact_credential_reflection_count"] == 1
