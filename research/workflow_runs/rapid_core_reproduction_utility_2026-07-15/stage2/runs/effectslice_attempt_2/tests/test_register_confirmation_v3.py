import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))
sys.path.insert(0, str(RUN_ROOT / "tests"))

import evidence_ledger_v3 as ledger  # noqa: E402
import register_confirmation_v3 as registration  # noqa: E402
from build_confirmation_v3 import build_family  # noqa: E402
from test_build_confirmation_v3 import (  # noqa: E402
    copy_input,
    make_run_root,
    registered_output,
)


BOUNDARY = "registered_final_only_confirmation_v3"


def test_cli_bootstraps_local_source_tree():
    completed = subprocess.run(
        [sys.executable, str(RUN_ROOT / "register_confirmation_v3.py"), "--help"],
        cwd=RUN_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "build-preregistration" in completed.stdout


def prepare_registered_root(tmp_path: Path) -> Path:
    run_root = make_run_root(tmp_path, complete=True)
    for name in (
        "build_confirmation_v3.py",
        "register_confirmation_v3.py",
        "evidence_ledger_v3.py",
    ):
        copy_input(RUN_ROOT / name, run_root / name)
    for control in ("identity", "planted"):
        build_family(
            control,
            registered_output(run_root, control),
            run_root=run_root,
            require_complete_bindings=True,
        )
    return run_root


def build_ledger_and_anchor(run_root: Path) -> tuple[dict, dict]:
    preregistration = registration.build_preregistration(run_root)
    ledger_payload = ledger.build_ledger(
        run_root,
        [
            registered_output(run_root, "identity"),
            registered_output(run_root, "planted"),
            registration.preregistration_path(run_root),
        ],
        registration.ledger_path(run_root),
        phase="preregistration",
        evidence_boundary=BOUNDARY,
    )
    anchor = registration.build_anchor(run_root)
    return {"preregistration": preregistration, "ledger": ledger_payload}, anchor


def rewrite_preregistration(path: Path, payload: dict) -> None:
    core = dict(payload)
    core.pop("manifest_core_sha256")
    payload["manifest_core_sha256"] = hashlib.sha256(
        registration._canonical_bytes(core)
    ).hexdigest()
    path.write_bytes(registration._pretty_json_bytes(payload))


def test_build_anchor_and_audit_complete_registration(tmp_path):
    run_root = prepare_registered_root(tmp_path)

    artifacts, anchor = build_ledger_and_anchor(run_root)
    audit = registration.audit_preregistration(run_root)

    preregistration = artifacts["preregistration"]
    assert preregistration["registration_status"] == "complete"
    assert preregistration["registered_block_count"] == 24
    assert preregistration["registered_condition_run_count"] == 72
    assert preregistration["provider_execution_started"] is False
    assert list(preregistration["controls"]) == ["identity", "planted"]
    assert preregistration["controls"]["identity"]["replicate_count"] == 6
    assert preregistration["controls"]["planted"]["replicate_count"] == 18
    assert preregistration["no_replacement_replicates"] is True
    assert preregistration["maximum_parallel_workers"] == 2
    assert preregistration["provider"] == registration.PROVIDER
    assert preregistration["execution_paths"] == registration._execution_paths(
        run_root
    )
    assert set(preregistration["execution_bindings"]) == set(
        registration.EXECUTION_FILES
    )
    assert (
        anchor["ledger_sha256"]
        == hashlib.sha256(registration.ledger_path(run_root).read_bytes()).hexdigest()
    )
    assert audit == {
        "valid": True,
        "registration_status": "complete",
        "registered_block_count": 24,
        "registered_condition_run_count": 72,
        "provider_execution_started": False,
        "anchor_verified": True,
        "ledger_sha256": anchor["ledger_sha256"],
        "ledger_chain_root_sha256": anchor["ledger_chain_root_sha256"],
    }


def test_preregistration_is_deterministic_across_equivalent_roots(tmp_path):
    first_root = prepare_registered_root(tmp_path / "first")
    second_root = prepare_registered_root(tmp_path / "second")

    registration.build_preregistration(first_root)
    registration.build_preregistration(second_root)

    assert registration.preregistration_path(first_root).read_bytes() == (
        registration.preregistration_path(second_root).read_bytes()
    )


@pytest.mark.parametrize("control", ["identity", "planted"])
def test_audit_rejects_family_mutation(tmp_path, control):
    run_root = prepare_registered_root(tmp_path)
    build_ledger_and_anchor(run_root)
    family_path = registered_output(run_root, control) / "family.json"
    family = json.loads(family_path.read_text(encoding="utf-8"))
    family["schedule_seed"] += 1
    family_path.write_text(json.dumps(family, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(registration.PreregistrationError):
        registration.audit_preregistration(run_root)


def test_audit_rejects_execution_binding_mutation(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    build_ledger_and_anchor(run_root)
    (run_root / "run_confirmation_v3.py").write_text(
        "# changed after preregistration\n", encoding="utf-8"
    )

    with pytest.raises(registration.PreregistrationError, match="execution binding"):
        registration.audit_preregistration(run_root)


def test_build_and_audit_fail_if_provider_progress_exists(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    progress = registration.progress_path(run_root)
    progress.parent.mkdir(parents=True)
    progress.write_text("{}\n", encoding="utf-8")

    with pytest.raises(registration.PreregistrationError, match="already started"):
        registration.build_preregistration(run_root)
    assert not registration.preregistration_path(run_root).exists()

    progress.unlink()
    progress.parent.rmdir()
    build_ledger_and_anchor(run_root)
    progress.parent.mkdir(parents=True)
    progress.write_text("{}\n", encoding="utf-8")
    with pytest.raises(registration.PreregistrationError, match="already started"):
        registration.audit_preregistration(run_root)


def test_build_rejects_any_existing_confirmation_v3_execution_root(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    registration.execution_root_path(run_root).mkdir(parents=True)

    with pytest.raises(registration.PreregistrationError, match="already started"):
        registration.build_preregistration(run_root)
    assert not registration.preregistration_path(run_root).exists()


def test_post_start_audit_requires_explicit_mode_and_preserves_anchor(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    build_ledger_and_anchor(run_root)
    registration.output_root_path(run_root, "identity").mkdir(parents=True)

    with pytest.raises(registration.PreregistrationError, match="already started"):
        registration.audit_preregistration(run_root)
    audit = registration.audit_preregistration(
        run_root, allow_execution_started=True
    )
    assert audit["anchor_verified"] is True
    assert audit["provider_execution_started"] is True


def test_preregistration_and_anchor_are_write_once(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    build_ledger_and_anchor(run_root)

    with pytest.raises(registration.PreregistrationError, match="already exists"):
        registration.build_preregistration(run_root)
    with pytest.raises(registration.PreregistrationError, match="already exists"):
        registration.build_anchor(run_root)


def test_anchor_requires_ledger_to_cover_both_families_and_preregistration(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    registration.build_preregistration(run_root)
    ledger.build_ledger(
        run_root,
        [
            registered_output(run_root, "identity"),
            registered_output(run_root, "planted"),
        ],
        registration.ledger_path(run_root),
        phase="preregistration",
        evidence_boundary=BOUNDARY,
    )

    with pytest.raises(registration.PreregistrationError, match="source roots"):
        registration.build_anchor(run_root)


def test_audit_rejects_control_family_swap_even_with_recomputed_core(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    registration.build_preregistration(run_root)
    path = registration.preregistration_path(run_root)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["controls"]["planted"]["family_path"] = payload["controls"]["identity"][
        "family_path"
    ]
    payload["controls"]["planted"]["family_sha256"] = payload["controls"]["identity"][
        "family_sha256"
    ]
    rewrite_preregistration(path, payload)

    with pytest.raises(registration.PreregistrationError):
        registration.audit_preregistration(run_root, require_anchor=False)


def test_audit_rejects_anchor_or_ledger_mutation(tmp_path):
    run_root = prepare_registered_root(tmp_path)
    _, anchor = build_ledger_and_anchor(run_root)
    anchor_path = registration.anchor_path(run_root)
    payload = json.loads(anchor_path.read_text(encoding="utf-8"))
    payload["ledger_sha256"] = "0" * 64
    anchor_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(registration.PreregistrationError):
        registration.audit_preregistration(run_root)

    anchor_path.write_bytes(registration._pretty_json_bytes(anchor))
    ledger_path = registration.ledger_path(run_root)
    ledger_payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_payload["entries"][0]["size_bytes"] += 1
    ledger_path.write_text(
        json.dumps(ledger_payload, sort_keys=True) + "\n", encoding="utf-8"
    )
    with pytest.raises(registration.PreregistrationError):
        registration.audit_preregistration(run_root)
