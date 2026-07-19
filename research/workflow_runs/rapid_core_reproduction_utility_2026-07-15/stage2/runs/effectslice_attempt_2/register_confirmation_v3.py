"""Freeze and audit EffectSlice confirmation-v3 preregistration artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

RUN_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN_ROOT / "src"))

import analyze_confirmation_v3 as analyzer
import evidence_ledger_v3 as ledger


BOUNDARY = "registered_final_only_confirmation_v3"
PREREGISTRATION_SCHEMA = "effectslice-confirmation-v3-preregistration.v1"
ANCHOR_SCHEMA = "effectslice-confirmation-v3-preregistration-anchor.v1"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
PREREGISTRATION_FIELDS = {
    "schema_version",
    "registration_status",
    "evidence_boundary",
    "task_key",
    "task_id",
    "conditions",
    "statistical_unit",
    "decision_basis",
    "primary_event",
    "registered_block_count",
    "registered_condition_run_count",
    "controls",
    "provider",
    "private_score_policy",
    "maximum_transport_attempts",
    "maximum_parallel_workers",
    "fresh_provider_conversation_per_condition",
    "no_replacement_replicates",
    "preserve_registered_failures",
    "independence_verified",
    "iid_conditional_reference",
    "provider_execution_started",
    "progress_path",
    "execution_paths",
    "execution_bindings",
    "ledger_plan",
    "manifest_core_sha256",
}
CONTROL_FIELDS = {
    "family_path",
    "family_sha256",
    "replicate_count",
    "strict_subset",
    "calibration_role",
    "admission_rule",
    "required_joint_events_for_admission",
    "schedule_seed",
}
BINDING_FIELDS = {"path", "sha256"}
EXECUTION_PATH_FIELDS = {
    "identity_family_path",
    "planted_family_path",
    "identity_output_root",
    "planted_output_root",
    "progress_path",
}
LEDGER_PLAN_FIELDS = {
    "phase",
    "ledger_path",
    "required_source_roots",
    "external_anchor_path",
}
ANCHOR_FIELDS = {
    "schema_version",
    "registration_status",
    "evidence_boundary",
    "preregistration_path",
    "preregistration_sha256",
    "ledger_path",
    "ledger_sha256",
    "ledger_chain_root_sha256",
    "ledger_file_count",
    "provider_execution_started",
}
EXECUTION_FILES = {
    "builder": "build_confirmation_v3.py",
    "registration": "register_confirmation_v3.py",
    "runner": "run_toolformer_filter_confirmation_v3.py",
    "scheduler": "run_confirmation_v3.py",
    "analyzer": "analyze_confirmation_v3.py",
    "evidence_ledger": "evidence_ledger_v3.py",
    "transport": "confirmation_transport_v3.py",
}
PROVIDER = {
    "provider_label": "DeepSeek V3.2",
    "base_url": "https://api.deepseek.com",
    "model_alias": "deepseek-v4-flash",
    "wire_api": "openai_chat_completions",
    "temperature": 0,
    "max_tokens": 8192,
    "timeout_seconds": 240.0,
    "retry_delay_seconds": 2.0,
    "direct_connection": True,
    "proxy_policy": "disabled",
}


class PreregistrationError(ValueError):
    """Raised when confirmation-v3 cannot be frozen or audited."""


def _root_path(run_root: Path) -> Path:
    try:
        return ledger._root_path(Path(run_root))
    except ledger.EvidenceLedgerError as exc:
        raise PreregistrationError(str(exc)) from exc


def preregistration_path(run_root: Path) -> Path:
    return (
        Path(run_root).resolve()
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / "preregistration.json"
    )


def anchor_path(run_root: Path) -> Path:
    return preregistration_path(run_root).with_name("preregistration_anchor.json")


def ledger_path(run_root: Path) -> Path:
    return (
        Path(run_root).resolve()
        / "derived"
        / "confirmation_v3"
        / "evidence_ledger"
        / "preregistration"
        / "ledger.json"
    )


def progress_path(run_root: Path) -> Path:
    return (
        Path(run_root).resolve()
        / "experiment_results"
        / "confirmation_v3"
        / "confirmation_v3_progress.json"
    )


def execution_root_path(run_root: Path) -> Path:
    return Path(run_root).resolve() / "experiment_results" / "confirmation_v3"


def output_root_path(run_root: Path, control: str) -> Path:
    if control not in {"identity", "planted"}:
        raise PreregistrationError("control must be identity or planted")
    return execution_root_path(run_root) / control


def _family_path(root: Path, control: str) -> Path:
    return (
        root
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / control
        / "family.json"
    )


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except (OSError, RuntimeError, ValueError) as exc:
        raise PreregistrationError("registered path escapes the run root") from exc


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PreregistrationError("preregistration is not canonical JSON") from exc


def _pretty_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PreregistrationError("preregistration is not deterministic JSON") from exc


def _sha256_file(path: Path, label: str) -> str:
    try:
        digest, _ = ledger._snapshot_file(path, label)
    except ledger.EvidenceLedgerError as exc:
        raise PreregistrationError(str(exc)) from exc
    return digest


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value, _ = ledger._bounded_json_object(path, label)
    except ledger.EvidenceLedgerError as exc:
        raise PreregistrationError(str(exc)) from exc
    return value


def _write_new_json(path: Path, payload: dict[str, Any], label: str) -> None:
    destination = Path(path)
    if destination.exists():
        raise PreregistrationError(f"{label} already exists")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        ledger._reject_linked_components(destination.parent, f"{label} parent")
    except (OSError, ValueError, ledger.EvidenceLedgerError) as exc:
        raise PreregistrationError(f"{label} parent is invalid") from exc
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(_pretty_json_bytes(payload))
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_path, destination, follow_symlinks=False)
    except FileExistsError as exc:
        raise PreregistrationError(f"{label} already exists") from exc
    except (OSError, ValueError) as exc:
        raise PreregistrationError(f"{label} could not be published") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _family_record(root: Path, control: str) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _family_path(root, control)
    if not path.is_file():
        raise PreregistrationError(f"{control} family is missing")
    digest = _sha256_file(path, f"{control} family")
    try:
        family = analyzer._validate_family(path, digest)
    except analyzer.AnalysisInputError as exc:
        raise PreregistrationError(f"{control} family is invalid: {exc}") from exc
    if family.get("control") != control:
        raise PreregistrationError(f"{control} family control is inconsistent")
    record = {
        "family_path": _relative(path, root),
        "family_sha256": digest,
        "replicate_count": family["replicate_count"],
        "strict_subset": family["strict_subset"],
        "calibration_role": family["calibration_role"],
        "admission_rule": family["admission_rule"],
        "required_joint_events_for_admission": family[
            "required_joint_events_for_admission"
        ],
        "schedule_seed": family["schedule_seed"],
    }
    return record, family


def _execution_bindings(root: Path) -> dict[str, dict[str, str]]:
    bindings = {}
    for name, relative in EXECUTION_FILES.items():
        path = root / relative
        if not path.is_file():
            raise PreregistrationError(f"execution binding is missing: {name}")
        bindings[name] = {
            "path": relative,
            "sha256": _sha256_file(path, f"{name} execution binding"),
        }
    return bindings


def _required_source_roots(root: Path) -> list[str]:
    paths = [
        _family_path(root, "identity").parent,
        _family_path(root, "planted").parent,
        preregistration_path(root),
    ]
    return sorted(_relative(path, root) for path in paths)


def _ledger_plan(root: Path) -> dict[str, Any]:
    return {
        "phase": "preregistration",
        "ledger_path": _relative(ledger_path(root), root),
        "required_source_roots": _required_source_roots(root),
        "external_anchor_path": _relative(anchor_path(root), root),
    }


def _execution_paths(root: Path) -> dict[str, str]:
    return {
        "identity_family_path": _relative(_family_path(root, "identity"), root),
        "planted_family_path": _relative(_family_path(root, "planted"), root),
        "identity_output_root": _relative(
            output_root_path(root, "identity"), root
        ),
        "planted_output_root": _relative(
            output_root_path(root, "planted"), root
        ),
        "progress_path": _relative(progress_path(root), root),
    }


def _reject_prior_execution(root: Path) -> None:
    if progress_path(root).exists() or execution_root_path(root).exists():
        raise PreregistrationError("provider execution has already started")


def _with_core(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["manifest_core_sha256"] = hashlib.sha256(
        _canonical_bytes(result)
    ).hexdigest()
    return result


def build_preregistration(run_root: Path = RUN_ROOT) -> dict[str, Any]:
    root = _root_path(Path(run_root))
    destination = preregistration_path(root)
    if destination.exists():
        raise PreregistrationError("confirmation-v3 preregistration already exists")
    _reject_prior_execution(root)
    controls = {}
    families = {}
    for control in ("identity", "planted"):
        controls[control], families[control] = _family_record(root, control)
    if (
        families["identity"]["task_prompt_canonical_text_sha256"]
        != families["planted"]["task_prompt_canonical_text_sha256"]
    ):
        raise PreregistrationError("control families do not share a task prompt")
    payload = {
        "schema_version": PREREGISTRATION_SCHEMA,
        "registration_status": "complete",
        "evidence_boundary": BOUNDARY,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "statistical_unit": "registered_matched_block",
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "registered_block_count": 24,
        "registered_condition_run_count": 72,
        "controls": controls,
        "provider": PROVIDER,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "maximum_parallel_workers": 2,
        "fresh_provider_conversation_per_condition": True,
        "no_replacement_replicates": True,
        "preserve_registered_failures": True,
        "independence_verified": False,
        "iid_conditional_reference": {"label": "iid_conditional_only"},
        "provider_execution_started": False,
        "progress_path": _relative(progress_path(root), root),
        "execution_paths": _execution_paths(root),
        "execution_bindings": _execution_bindings(root),
        "ledger_plan": _ledger_plan(root),
    }
    payload = _with_core(payload)
    _write_new_json(destination, payload, "confirmation-v3 preregistration")
    return payload


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise PreregistrationError(f"{label} does not match the registered value")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise PreregistrationError(f"{label} is not a lowercase SHA-256 digest")
    return value


def _validate_core(payload: dict[str, Any]) -> None:
    claimed = _require_sha256(
        payload.get("manifest_core_sha256"), "preregistration core digest"
    )
    core = dict(payload)
    core.pop("manifest_core_sha256", None)
    actual = hashlib.sha256(_canonical_bytes(core)).hexdigest()
    if claimed != actual:
        raise PreregistrationError("preregistration core digest does not match")


def _audit_family_record(root: Path, control: str, record: Any) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != CONTROL_FIELDS:
        raise PreregistrationError(f"{control} control record is invalid")
    expected_path = _family_path(root, control)
    _require_exact(
        record.get("family_path"),
        _relative(expected_path, root),
        f"{control} family path",
    )
    digest = _require_sha256(record.get("family_sha256"), f"{control} family digest")
    actual_digest = _sha256_file(expected_path, f"{control} family")
    _require_exact(actual_digest, digest, f"{control} family digest")
    try:
        family = analyzer._validate_family(expected_path, digest)
    except analyzer.AnalysisInputError as exc:
        raise PreregistrationError(f"{control} family is invalid: {exc}") from exc
    _require_exact(family.get("control"), control, f"{control} family control")
    for field in CONTROL_FIELDS - {"family_path", "family_sha256"}:
        _require_exact(record.get(field), family.get(field), f"{control} {field}")
    return family


def _audit_execution_bindings(root: Path, bindings: Any) -> None:
    if not isinstance(bindings, dict) or set(bindings) != set(EXECUTION_FILES):
        raise PreregistrationError("execution bindings are incomplete")
    for name, relative in EXECUTION_FILES.items():
        binding = bindings.get(name)
        if not isinstance(binding, dict) or set(binding) != BINDING_FIELDS:
            raise PreregistrationError(f"execution binding is invalid: {name}")
        _require_exact(binding.get("path"), relative, f"{name} execution binding path")
        expected = _require_sha256(
            binding.get("sha256"), f"{name} execution binding digest"
        )
        actual = _sha256_file(root / relative, f"{name} execution binding")
        if actual != expected:
            raise PreregistrationError(f"execution binding changed: {name}")


def _validate_preregistration(
    root: Path, *, allow_execution_started: bool = False
) -> dict[str, Any]:
    if type(allow_execution_started) is not bool:
        raise PreregistrationError("allow_execution_started must be a bool")
    path = preregistration_path(root)
    if not path.is_file():
        raise PreregistrationError("confirmation-v3 preregistration is missing")
    payload = _json_object(path, "confirmation-v3 preregistration")
    if set(payload) != PREREGISTRATION_FIELDS:
        raise PreregistrationError("preregistration fields do not match the schema")
    for field, expected in {
        "schema_version": PREREGISTRATION_SCHEMA,
        "registration_status": "complete",
        "evidence_boundary": BOUNDARY,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "statistical_unit": "registered_matched_block",
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "registered_block_count": 24,
        "registered_condition_run_count": 72,
        "provider": PROVIDER,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "maximum_parallel_workers": 2,
        "fresh_provider_conversation_per_condition": True,
        "no_replacement_replicates": True,
        "preserve_registered_failures": True,
        "independence_verified": False,
        "iid_conditional_reference": {"label": "iid_conditional_only"},
        "provider_execution_started": False,
        "progress_path": _relative(progress_path(root), root),
        "execution_paths": _execution_paths(root),
        "ledger_plan": _ledger_plan(root),
    }.items():
        _require_exact(payload.get(field), expected, f"preregistration {field}")
    _validate_core(payload)
    controls = payload.get("controls")
    if not isinstance(controls, dict) or list(controls) != ["identity", "planted"]:
        raise PreregistrationError("preregistration controls are invalid")
    families = {
        control: _audit_family_record(root, control, controls[control])
        for control in ("identity", "planted")
    }
    if (
        families["identity"]["task_prompt_canonical_text_sha256"]
        != families["planted"]["task_prompt_canonical_text_sha256"]
    ):
        raise PreregistrationError("control families do not share a task prompt")
    _audit_execution_bindings(root, payload.get("execution_bindings"))
    paths = payload.get("execution_paths")
    if not isinstance(paths, dict) or set(paths) != EXECUTION_PATH_FIELDS:
        raise PreregistrationError("preregistration execution paths are invalid")
    if not allow_execution_started:
        _reject_prior_execution(root)
    return payload


def _ledger_payload(root: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    path = ledger_path(root)
    if not path.is_file():
        raise PreregistrationError("preregistration ledger is missing")
    digest = _sha256_file(path, "preregistration ledger")
    try:
        verified = ledger.verify_ledger(root, path, expected_ledger_sha256=digest)
        payload, _ = ledger._bounded_json_object(path, "preregistration ledger")
    except ledger.EvidenceLedgerError as exc:
        raise PreregistrationError(f"preregistration ledger is invalid: {exc}") from exc
    if payload.get("source_roots") != _required_source_roots(root):
        raise PreregistrationError("preregistration ledger source roots are invalid")
    _require_exact(payload.get("phase"), "preregistration", "ledger phase")
    _require_exact(payload.get("evidence_boundary"), BOUNDARY, "ledger boundary")
    return payload, verified, digest


def build_anchor(run_root: Path = RUN_ROOT) -> dict[str, Any]:
    root = _root_path(Path(run_root))
    destination = anchor_path(root)
    if destination.exists():
        raise PreregistrationError(
            "confirmation-v3 preregistration anchor already exists"
        )
    preregistration = _validate_preregistration(root)
    ledger_payload, verified, ledger_digest = _ledger_payload(root)
    preregistration_digest = _sha256_file(
        preregistration_path(root), "confirmation-v3 preregistration"
    )
    payload = {
        "schema_version": ANCHOR_SCHEMA,
        "registration_status": preregistration["registration_status"],
        "evidence_boundary": BOUNDARY,
        "preregistration_path": _relative(preregistration_path(root), root),
        "preregistration_sha256": preregistration_digest,
        "ledger_path": _relative(ledger_path(root), root),
        "ledger_sha256": ledger_digest,
        "ledger_chain_root_sha256": ledger_payload["chain_root_sha256"],
        "ledger_file_count": verified["file_count"],
        "provider_execution_started": False,
    }
    _write_new_json(destination, payload, "confirmation-v3 preregistration anchor")
    return payload


def _validate_anchor(root: Path, preregistration: dict[str, Any]) -> dict[str, Any]:
    path = anchor_path(root)
    if not path.is_file():
        raise PreregistrationError("confirmation-v3 preregistration anchor is missing")
    anchor = _json_object(path, "confirmation-v3 preregistration anchor")
    if set(anchor) != ANCHOR_FIELDS:
        raise PreregistrationError("preregistration anchor fields are invalid")
    for field, expected in {
        "schema_version": ANCHOR_SCHEMA,
        "registration_status": "complete",
        "evidence_boundary": BOUNDARY,
        "preregistration_path": _relative(preregistration_path(root), root),
        "ledger_path": _relative(ledger_path(root), root),
        "provider_execution_started": False,
    }.items():
        _require_exact(anchor.get(field), expected, f"anchor {field}")
    preregistration_digest = _sha256_file(
        preregistration_path(root), "confirmation-v3 preregistration"
    )
    _require_exact(
        anchor.get("preregistration_sha256"),
        preregistration_digest,
        "anchor preregistration digest",
    )
    ledger_digest = _require_sha256(anchor.get("ledger_sha256"), "anchor ledger digest")
    try:
        verified = ledger.verify_ledger(
            root,
            ledger_path(root),
            expected_ledger_sha256=ledger_digest,
        )
        ledger_payload, _ = ledger._bounded_json_object(
            ledger_path(root), "preregistration ledger"
        )
    except ledger.EvidenceLedgerError as exc:
        raise PreregistrationError(f"preregistration ledger is invalid: {exc}") from exc
    if (
        ledger_payload.get("source_roots")
        != preregistration["ledger_plan"]["required_source_roots"]
    ):
        raise PreregistrationError("preregistration ledger source roots are invalid")
    _require_exact(
        anchor.get("ledger_chain_root_sha256"),
        verified["chain_root_sha256"],
        "anchor ledger chain root",
    )
    _require_exact(
        anchor.get("ledger_file_count"),
        verified["file_count"],
        "anchor ledger file count",
    )
    return anchor


def audit_preregistration(
    run_root: Path = RUN_ROOT,
    *,
    require_anchor: bool = True,
    allow_execution_started: bool = False,
) -> dict[str, Any]:
    root = _root_path(Path(run_root))
    preregistration = _validate_preregistration(
        root, allow_execution_started=allow_execution_started
    )
    execution_started = (
        execution_root_path(root).exists() or progress_path(root).exists()
    )
    if not require_anchor:
        return {
            "valid": True,
            "registration_status": preregistration["registration_status"],
            "registered_block_count": preregistration["registered_block_count"],
            "registered_condition_run_count": preregistration[
                "registered_condition_run_count"
            ],
            "provider_execution_started": execution_started,
            "anchor_verified": False,
            "ledger_sha256": None,
            "ledger_chain_root_sha256": None,
        }
    anchor = _validate_anchor(root, preregistration)
    return {
        "valid": True,
        "registration_status": preregistration["registration_status"],
        "registered_block_count": preregistration["registered_block_count"],
        "registered_condition_run_count": preregistration[
            "registered_condition_run_count"
        ],
        "provider_execution_started": execution_started,
        "anchor_verified": True,
        "ledger_sha256": anchor["ledger_sha256"],
        "ledger_chain_root_sha256": anchor["ledger_chain_root_sha256"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze and audit EffectSlice confirmation-v3 preregistration"
    )
    parser.add_argument(
        "command", choices=("build-preregistration", "build-anchor", "audit")
    )
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--without-anchor", action="store_true")
    parser.add_argument("--allow-execution-started", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "build-preregistration":
            payload = build_preregistration(args.run_root)
            result = {
                "built": True,
                "artifact": "preregistration",
                "registered_block_count": payload["registered_block_count"],
            }
        elif args.command == "build-anchor":
            payload = build_anchor(args.run_root)
            result = {
                "built": True,
                "artifact": "anchor",
                "ledger_sha256": payload["ledger_sha256"],
            }
        else:
            result = audit_preregistration(
                args.run_root,
                require_anchor=not args.without_anchor,
                allow_execution_started=args.allow_execution_started,
            )
    except PreregistrationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
