from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import run_confirmation_v3_analysis as replay
from run_confirmation_v3_analysis import (
    AnalysisReplayError,
    corrected_task_prompt_canonicalization,
    historical_eol_replay,
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def build_historical_view(tmp_path: Path, payload: bytes, expected: str) -> tuple[Path, Path]:
    run_root = tmp_path / "run"
    source = run_root / "src" / "bound.py"
    source.parent.mkdir(parents=True)
    source.write_bytes(payload)
    output = run_root / "experiment_results" / "confirmation_v2" / "r001"
    output.mkdir(parents=True)
    manifest = {
        "verified_family_inputs": {
            "runner": {"path": source.resolve().as_posix(), "sha256": expected}
        }
    }
    (output / "pair_manifest.json").write_text(
        json.dumps(manifest) + "\n", encoding="utf-8", newline="\n"
    )
    progress = {
        "schema_version": "effectslice-confirmation-v2-progress.v1",
        "counts": {"completed": 1, "failed": 0, "preserved": 0},
        "records": [
            {
                "task_key": "toolformer_filter",
                "replicate_id": "r001",
                "status": "completed",
                "output_dir": output.resolve().as_posix(),
                "pair_id": "toolformer_filter:confirmation-v2:r001",
            }
        ],
    }
    progress_path = run_root / "derived" / "historical" / "progress.json"
    progress_path.parent.mkdir(parents=True)
    progress_path.write_text(
        json.dumps(progress) + "\n", encoding="utf-8", newline="\n"
    )
    return progress_path, source


def test_historical_eol_replay_normalizes_and_restores(tmp_path):
    original = b"line one\r\nline two\r\n"
    replay = b"line one\nline two\n"
    progress, source = build_historical_view(tmp_path, original, sha256(replay))

    with historical_eol_replay(progress, progress.parents[2]) as changed:
        assert source.read_bytes() == replay
        assert len(changed) == 1
        assert changed[0]["replay_sha256"] == sha256(replay)

    assert source.read_bytes() == original


def test_historical_eol_replay_rejects_non_newline_change(tmp_path):
    original = b"different content\r\n"
    progress, source = build_historical_view(
        tmp_path, original, sha256(b"registered content\n")
    )

    with pytest.raises(AnalysisReplayError, match="differs beyond newline"):
        with historical_eol_replay(progress, progress.parents[2]):
            pass

    assert source.read_bytes() == original


def test_corrected_prompt_decode_preserves_raw_verification_and_restores(monkeypatch):
    original = replay.frozen_analyzer._snapshot_bytes
    calls = []

    def fake_snapshot(path, expected_sha256, label):
        calls.append((path, expected_sha256, label))
        return b"line one\r\nline two\r\n"

    monkeypatch.setattr(replay.frozen_analyzer, "_snapshot_bytes", fake_snapshot)
    try:
        with corrected_task_prompt_canonicalization():
            prompt = replay.frozen_analyzer._snapshot_bytes(
                Path("prompt.md"), "a" * 64, "task prompt snapshot"
            )
            other = replay.frozen_analyzer._snapshot_bytes(
                Path("other.md"), "b" * 64, "full artifact snapshot"
            )
            assert bytes(prompt) == b"line one\r\nline two\r\n"
            assert prompt.decode("utf-8") == "line one\nline two\n"
            assert other.decode("utf-8") == "line one\r\nline two\r\n"
        assert replay.frozen_analyzer._snapshot_bytes is fake_snapshot
        assert len(calls) == 2
    finally:
        monkeypatch.setattr(replay.frozen_analyzer, "_snapshot_bytes", original)


def test_corrected_prompt_digest_revalidates_registered_bytes(monkeypatch, tmp_path):
    prompt = tmp_path / "verified_inputs" / "task_prompt.md"
    prompt.parent.mkdir(parents=True)
    payload = b"line one\r\nline two\r\n"
    prompt.write_bytes(payload)
    canonical = b"line one\nline two"
    legacy = b"line one\r\nline two"
    family = {
        "task_prompt_file_sha256": sha256(payload),
        "task_prompt_canonical_text_sha256": sha256(canonical),
    }
    original = replay.frozen_analyzer._audit_condition
    observed = []

    def fake_audit_condition(**kwargs):
        observed.append(kwargs["family"]["task_prompt_canonical_text_sha256"])
        return {"success": True}

    monkeypatch.setattr(
        replay.frozen_analyzer, "_audit_condition", fake_audit_condition
    )
    try:
        with corrected_task_prompt_canonicalization():
            result = replay.frozen_analyzer._audit_condition(
                output_dir=tmp_path,
                family=family,
            )
        assert result == {"success": True}
        assert observed == [sha256(legacy)]
        assert family["task_prompt_canonical_text_sha256"] == sha256(canonical)
        assert replay.frozen_analyzer._audit_condition is fake_audit_condition
    finally:
        monkeypatch.setattr(replay.frozen_analyzer, "_audit_condition", original)


def test_corrected_prompt_digest_rejects_unregistered_bytes(monkeypatch, tmp_path):
    prompt = tmp_path / "verified_inputs" / "task_prompt.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_bytes(b"changed\r\n")
    family = {
        "task_prompt_file_sha256": sha256(b"registered\r\n"),
        "task_prompt_canonical_text_sha256": sha256(b"registered"),
    }

    monkeypatch.setattr(
        replay.frozen_analyzer,
        "_audit_condition",
        lambda **kwargs: {"success": True},
    )
    with corrected_task_prompt_canonicalization():
        with pytest.raises(
            replay.frozen_analyzer.AnalysisInputError,
            match="task prompt snapshot digest mismatch",
        ):
            replay.frozen_analyzer._audit_condition(
                output_dir=tmp_path,
                family=family,
            )
