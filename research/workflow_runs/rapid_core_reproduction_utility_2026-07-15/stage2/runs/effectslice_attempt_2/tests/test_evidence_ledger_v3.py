import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

import evidence_ledger_v3 as ledger  # noqa: E402


def write_sources(root: Path) -> Path:
    source = root / "registered_inputs"
    (source / "nested").mkdir(parents=True)
    (source / "alpha.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
    (source / "nested" / "beta.json").write_text(
        '{"beta":2}\n', encoding="utf-8", newline="\n"
    )
    return source


def package_path(root: Path, name: str = "package") -> Path:
    return root / "derived" / "evidence_ledger_v3" / name / "ledger.json"


def rewrite_sidecar(path: Path) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    ledger.sidecar_path(path).write_text(
        f"{digest}  {path.name}\n", encoding="ascii", newline="\n"
    )


def rewrite_ledger_with_core(path: Path, payload: dict) -> None:
    core = dict(payload)
    core.pop("manifest_core_sha256")
    payload["manifest_core_sha256"] = hashlib.sha256(
        ledger._canonical_bytes(core)
    ).hexdigest()
    path.write_bytes(ledger._pretty_json_bytes(payload))
    rewrite_sidecar(path)


def build_valid(root: Path, name: str = "package") -> tuple[Path, dict]:
    source = write_sources(root)
    path = package_path(root, name)
    result = ledger.build_ledger(
        root,
        [source],
        path,
        phase="preregistration",
        evidence_boundary="registered_final_only_confirmation_v3",
    )
    return path, result


def test_build_and_verify_ledger_is_deterministic_and_complete(tmp_path):
    root = tmp_path / "run"
    source = write_sources(root)
    first_path = package_path(root, "first")
    second_path = package_path(root, "second")

    first = ledger.build_ledger(
        root,
        [source],
        first_path,
        phase="preregistration",
        evidence_boundary="registered_final_only_confirmation_v3",
    )
    second = ledger.build_ledger(
        root,
        [source],
        second_path,
        phase="preregistration",
        evidence_boundary="registered_final_only_confirmation_v3",
    )

    assert first_path.read_bytes() == second_path.read_bytes()
    assert (
        ledger.sidecar_path(first_path).read_bytes()
        == ledger.sidecar_path(second_path).read_bytes()
    )
    assert first == second
    assert first["file_count"] == 2
    assert first["total_bytes"] == 17
    assert [entry["sequence"] for entry in first["entries"]] == [1, 2]
    assert [entry["path"] for entry in first["entries"]] == [
        "registered_inputs/alpha.txt",
        "registered_inputs/nested/beta.json",
    ]
    verified = ledger.verify_ledger(
        root,
        first_path,
        expected_ledger_sha256=hashlib.sha256(first_path.read_bytes()).hexdigest(),
    )
    assert verified == {
        "valid": True,
        "phase": "preregistration",
        "file_count": 2,
        "total_bytes": 17,
        "ledger_sha256": hashlib.sha256(first_path.read_bytes()).hexdigest(),
        "chain_root_sha256": first["chain_root_sha256"],
    }


@pytest.mark.parametrize("mutation", ["content", "missing", "extra"])
def test_verify_detects_source_file_set_and_content_changes(tmp_path, mutation):
    root = tmp_path / "run"
    path, _ = build_valid(root)
    source = root / "registered_inputs"
    if mutation == "content":
        (source / "alpha.txt").write_text("tampered\n", encoding="utf-8")
    elif mutation == "missing":
        (source / "alpha.txt").unlink()
    else:
        (source / "extra.txt").write_text("extra\n", encoding="utf-8")

    with pytest.raises(ledger.EvidenceLedgerError):
        ledger.verify_ledger(root, path)


@pytest.mark.parametrize("mutation", ["ledger", "sidecar", "schema"])
def test_verify_detects_ledger_and_sidecar_tampering(tmp_path, mutation):
    root = tmp_path / "run"
    path, _ = build_valid(root)
    if mutation == "ledger":
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["entries"][0]["size_bytes"] += 1
        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    elif mutation == "sidecar":
        ledger.sidecar_path(path).write_text(
            f"{'0' * 64}  {path.name}\n", encoding="ascii"
        )
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["unregistered_field"] = True
        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        rewrite_sidecar(path)

    with pytest.raises(ledger.EvidenceLedgerError):
        ledger.verify_ledger(root, path)


def test_verify_requires_matching_external_anchor_when_supplied(tmp_path):
    root = tmp_path / "run"
    path, _ = build_valid(root)

    with pytest.raises(ledger.EvidenceLedgerError, match="external anchor"):
        ledger.verify_ledger(root, path, expected_ledger_sha256="0" * 64)


def test_verify_rejects_boolean_entry_integers_even_if_rechained(tmp_path):
    root = tmp_path / "run"
    source = root / "registered_inputs"
    source.mkdir(parents=True)
    (source / "one-byte.bin").write_bytes(b"x")
    path = package_path(root)
    ledger.build_ledger(
        root,
        [source],
        path,
        phase="preregistration",
        evidence_boundary="registered_final_only_confirmation_v3",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    entry = payload["entries"][0]
    entry["sequence"] = True
    entry["size_bytes"] = True
    unsigned = {key: entry[key] for key in ledger.ENTRY_FIELDS - {"entry_sha256"}}
    entry["entry_sha256"] = hashlib.sha256(
        ledger._canonical_bytes(unsigned)
    ).hexdigest()
    payload["chain_root_sha256"] = entry["entry_sha256"]
    rewrite_ledger_with_core(path, payload)

    with pytest.raises(ledger.EvidenceLedgerError, match="integer fields"):
        ledger.verify_ledger(root, path)


def test_build_rejects_outside_overlapping_and_circular_sources(tmp_path):
    root = tmp_path / "run"
    source = write_sources(root)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")

    with pytest.raises(ledger.EvidenceLedgerError):
        ledger.build_ledger(
            root,
            [outside],
            package_path(root, "outside"),
            phase="preregistration",
            evidence_boundary="registered_final_only_confirmation_v3",
        )
    with pytest.raises(ledger.EvidenceLedgerError, match="overlap"):
        ledger.build_ledger(
            root,
            [source, source / "nested"],
            package_path(root, "overlap"),
            phase="preregistration",
            evidence_boundary="registered_final_only_confirmation_v3",
        )
    with pytest.raises(ledger.EvidenceLedgerError, match="ledger output"):
        ledger.build_ledger(
            root,
            [source],
            source / "ledger_package" / "ledger.json",
            phase="preregistration",
            evidence_boundary="registered_final_only_confirmation_v3",
        )


def test_build_is_write_once_and_requires_a_new_package_directory(tmp_path):
    root = tmp_path / "run"
    source = write_sources(root)
    path = package_path(root)
    path.parent.mkdir(parents=True)

    with pytest.raises(ledger.EvidenceLedgerError, match="new package"):
        ledger.build_ledger(
            root,
            [source],
            path,
            phase="preregistration",
            evidence_boundary="registered_final_only_confirmation_v3",
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows junction semantics")
def test_build_rejects_junctions_in_registered_sources(tmp_path):
    root = tmp_path / "run"
    source = write_sources(root)
    target = root / "junction_target"
    target.mkdir(parents=True)
    (target / "hidden.txt").write_text("hidden\n", encoding="utf-8")
    junction = source / "linked"
    created = subprocess.run(
        ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip(f"junction creation unavailable: {created.stderr.strip()}")
    try:
        assert os.path.samefile(junction, target)
        with pytest.raises(ledger.EvidenceLedgerError, match="linked"):
            ledger.build_ledger(
                root,
                [source],
                package_path(root),
                phase="preregistration",
                evidence_boundary="registered_final_only_confirmation_v3",
            )
    finally:
        junction.rmdir()


@pytest.mark.parametrize("phase", ["", "development", None])
def test_build_rejects_unregistered_phase_and_empty_boundary(tmp_path, phase):
    root = tmp_path / "run"
    source = write_sources(root)
    with pytest.raises(ledger.EvidenceLedgerError):
        ledger.build_ledger(
            root,
            [source],
            package_path(root),
            phase=phase,
            evidence_boundary="registered_final_only_confirmation_v3",
        )
    with pytest.raises(ledger.EvidenceLedgerError):
        ledger.build_ledger(
            root,
            [source],
            package_path(root, "empty-boundary"),
            phase="preregistration",
            evidence_boundary="",
        )
