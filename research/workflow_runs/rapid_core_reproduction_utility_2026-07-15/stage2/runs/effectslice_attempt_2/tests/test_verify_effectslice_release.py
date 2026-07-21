from __future__ import annotations

import json
import hashlib

import pytest

import verify_effectslice_release as verifier


def test_canonical_release_is_relocatable_and_digest_complete():
    result = verifier.verify_manifest(verifier.DEFAULT_MANIFEST, verifier.PROJECT_ROOT)

    assert result["status"] == "passed"
    assert result["checked_artifacts"] >= 20
    assert result["checked_raw_files"] == 858


def test_release_verifier_rejects_a_digest_change(tmp_path):
    payload = json.loads(verifier.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    payload["sources"]["v5_analysis"]["sha256"] = "0" * 64
    changed = tmp_path / "changed_manifest.json"
    changed.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="digest mismatch"):
        verifier.verify_manifest(changed, verifier.PROJECT_ROOT)


def test_release_verifier_rejects_absolute_artifact_paths(tmp_path):
    payload = json.loads(verifier.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    payload["sources"]["v5_analysis"]["path"] = str(
        (verifier.PROJECT_ROOT / "not-portable.json").resolve()
    )
    changed = tmp_path / "absolute_manifest.json"
    changed.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="absolute path"):
        verifier.verify_manifest(changed, verifier.PROJECT_ROOT)


def test_release_verifier_rejects_a_raw_file_change(tmp_path):
    run_root = tmp_path / "run"
    raw_file = run_root / "raw" / "family" / "block" / "B" / "run_result.json"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text('{"score": 1}\n', encoding="utf-8")
    digest = hashlib.sha256(raw_file.read_bytes()).hexdigest()
    inventory = [
        {
            "run_relative_path": "raw/family/block/B/run_result.json",
            "sha256": digest,
        }
    ]
    digest_payload = json.dumps(
        [{"path": "raw/family/block/B/run_result.json", "sha256": digest}],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    output_set = {
        "raw_root": "raw",
        "raw_inventory": inventory,
        "raw_file_count": 1,
        "raw_evidence_digest": hashlib.sha256(digest_payload).hexdigest(),
    }

    assert verifier._verify_raw_output_set("test", output_set, run_root) == [
        "raw/family/block/B/run_result.json"
    ]
    raw_file.write_text('{"score": 0}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="raw evidence file digest mismatch"):
        verifier._verify_raw_output_set("test", output_set, run_root)


def test_release_verifier_rejects_unregistered_canonical_raw_file(tmp_path):
    run_root = tmp_path / "run"
    raw_file = run_root / "raw" / "family" / "block" / "B" / "run_result.json"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text('{"score": 1}\n', encoding="utf-8")
    digest = hashlib.sha256(raw_file.read_bytes()).hexdigest()
    inventory_path = "raw/family/block/B/run_result.json"
    digest_payload = json.dumps(
        [{"path": inventory_path, "sha256": digest}],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    output_set = {
        "raw_root": "raw",
        "raw_inventory": [
            {"run_relative_path": inventory_path, "sha256": digest}
        ],
        "raw_file_count": 1,
        "raw_evidence_digest": hashlib.sha256(digest_payload).hexdigest(),
    }

    unexpected = raw_file.with_name("transcript.json")
    unexpected.write_text('{"messages": []}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="canonical raw evidence set mismatch"):
        verifier._verify_raw_output_set("test", output_set, run_root)
