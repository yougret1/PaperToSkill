from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

import build_confirmation_v3 as legacy
import run_toolformer_filter_confirmation_v3 as bound_runner
from effectslice.confirmation_v3 import balanced_schedule
from run_swe_effectslice import workspace_tree_digest


RUN_ROOT = Path(__file__).resolve().parent
ARTIFACT_ROOT = (
    RUN_ROOT
    / "artifacts"
    / "toolformer_filter"
    / "confirmation_v3_interleaved_calibration_r2"
)
RESULT_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v3_interleaved_calibration_r2"
PREREGISTRATION_PATH = ARTIFACT_ROOT / "preregistration.json"
ANCHOR_PATH = ARTIFACT_ROOT / "preregistration_anchor.json"
PROGRESS_PATH = RESULT_ROOT / "progress.json"
EXECUTION_LOCK_PATH = RESULT_ROOT / "execution_started.json"
SCHEDULE_SEED = 2026072001
IDENTITY_STRATA = (1, 4, 7, 10, 13, 16)
PRIMARY_EVENT = "candidate_centered_substitution_event"
EVIDENCE_BOUNDARY = "registered_final_only_confirmation_v3"
ATOM_PATTERN = re.compile(r"\(`(T\d+)`\)")
LABEL_SPECS: dict[str, dict[str, Any]] = {
    "identity": {
        "underlying_control": "identity",
        "calibration_role": "identity_instrumentation_only",
        "replicate_count": 6,
        "schedule_seed": 2026072003,
        "replicate_prefix": "i",
        "required_candidate_centered_events": None,
    },
    "positive": {
        "underlying_control": "planted",
        "calibration_role": "planted_redundancy_positive_control",
        "replicate_count": 18,
        "schedule_seed": 2026072005,
        "replicate_prefix": "p",
        "required_candidate_centered_events": 18,
    },
    "negative": {
        "underlying_control": "planted",
        "calibration_role": "real_unstable_prefix_01_negative_control",
        "replicate_count": 18,
        "schedule_seed": 2026072007,
        "replicate_prefix": "n",
        "required_candidate_centered_events": (
            "strictly_less_than_registered_blocks"
        ),
    },
}


class InterleavedRegistrationError(ValueError):
    """Raised when the interleaved calibration cannot be registered or audited."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InterleavedRegistrationError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise InterleavedRegistrationError(f"{label} must be a JSON object")
    return value


def _write_exclusive(path: Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        handle.write(payload)


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    _write_exclusive(path, _json_bytes(value))


def _stored_path(path: Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(RUN_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _normalize_lf(payload: bytes) -> bytes:
    text = payload.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return (text.rstrip() + "\n").encode("utf-8")


def artifact_payloads(original: bytes, prefix_01: bytes) -> dict[str, dict[str, bytes]]:
    full = _normalize_lf(original)
    selected_prefix = _normalize_lf(prefix_01)
    positive_full = (
        full.rstrip()
        + b"\n\n"
        + legacy.T06_MARKDOWN.rstrip().encode("utf-8")
        + b"\n"
    )
    return {
        "identity": {"full": full, "selected": full},
        "positive": {"full": positive_full, "selected": full},
        "negative": {"full": full, "selected": selected_prefix},
    }


def _label_schedule(label: str) -> list[dict[str, Any]]:
    spec = LABEL_SPECS[label]
    rows = balanced_schedule(
        seed=spec["schedule_seed"], replicate_count=spec["replicate_count"]
    )
    result = []
    for index, row in enumerate(rows, start=1):
        result.append(
            {
                "label": label,
                "underlying_control": spec["underlying_control"],
                "replicate_id": f"{spec['replicate_prefix']}{index:03d}",
                "condition_order": list(row["condition_order"]),
            }
        )
    return result


def build_interleaved_schedule() -> list[dict[str, Any]]:
    per_label = {label: _label_schedule(label) for label in LABEL_SPECS}
    identity_by_stratum = {
        stratum: per_label["identity"][index]
        for index, stratum in enumerate(IDENTITY_STRATA)
    }
    schedule: list[dict[str, Any]] = []
    for stratum in range(1, 19):
        rows = [
            copy.deepcopy(per_label["positive"][stratum - 1]),
            copy.deepcopy(per_label["negative"][stratum - 1]),
        ]
        if stratum in identity_by_stratum:
            rows.append(copy.deepcopy(identity_by_stratum[stratum]))
        random.Random(SCHEDULE_SEED + stratum).shuffle(rows)
        for row in rows:
            row["stratum"] = stratum
            row["global_order_index"] = len(schedule) + 1
            schedule.append(row)
    return schedule


def _source_map(
    original: dict[str, Any],
    label: str,
    full_path: Path,
    selected_path: Path,
) -> dict[str, Any]:
    control = LABEL_SPECS[label]["underlying_control"]
    builder_control = "planted" if label == "positive" else "identity"
    source_map = legacy._build_source_map(
        original,
        builder_control,
        full_path,
        selected_path,
        registration_status="complete",
        evidence_boundary=EVIDENCE_BOUNDARY,
    )
    source_map["control"] = control
    source_map["calibration_label"] = label
    source_map["calibration_role"] = LABEL_SPECS[label]["calibration_role"]
    return source_map


def _bind_standard(
    family: dict[str, Any], name: str, path: Path, *, digest_path: Path | None = None
) -> None:
    resolved = Path(path).resolve()
    source = Path(digest_path).resolve() if digest_path else resolved
    if not source.is_file():
        raise FileNotFoundError(source)
    record = {
        "path": _stored_path(resolved),
        "sha256": _sha256(source.read_bytes()),
        "status": "bound",
    }
    family["bindings"][name] = record
    family[f"{name}_path"] = record["path"]
    family[f"{name}_sha256"] = record["sha256"]
    family[f"{name}_status"] = "bound"


def _bind_task_prompt(family: dict[str, Any], path: Path) -> None:
    payload = Path(path).read_bytes()
    text = payload.decode("utf-8").strip()
    if "\r" in text:
        raise InterleavedRegistrationError("registered task prompt must use LF")
    record = {
        "path": _stored_path(path),
        "file_sha256": _sha256(payload),
        "canonical_text_sha256": _sha256(text.encode("utf-8")),
        "status": "bound",
    }
    family["bindings"]["task_prompt"] = record
    family["task_prompt_path"] = record["path"]
    family["task_prompt_file_sha256"] = record["file_sha256"]
    family["task_prompt_canonical_text_sha256"] = record[
        "canonical_text_sha256"
    ]
    family["task_prompt_status"] = "bound"


def _build_family(
    *,
    label: str,
    family_dir: Path,
    payloads: dict[str, bytes],
    original_source_map: dict[str, Any],
    case_registry_path: Path,
    task_prompt_path: Path,
    schedules: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    spec = LABEL_SPECS[label]
    control = spec["underlying_control"]
    family_dir.mkdir(parents=True, exist_ok=False)
    full_path = family_dir / "full_artifact.md"
    selected_path = family_dir / "selected_artifact.md"
    source_map_path = family_dir / "source_atom_map.json"
    case_path = family_dir / "case_registry.json"
    family_path = family_dir / "family.json"
    _write_exclusive(full_path, payloads["full"])
    _write_exclusive(selected_path, payloads["selected"])
    source_map = _source_map(
        original_source_map, label, full_path, selected_path
    )
    truth = legacy._validate_artifact_truth(
        control, payloads["full"], payloads["selected"], source_map
    )
    source_map.update(
        {
            "full_artifact_atom_ids": truth["full_atom_ids"],
            "full_artifact_unit_count": len(truth["full_atom_ids"]),
            "full_artifact_scc_count": truth["full_scc_count"],
            "selected_artifact_atom_ids": truth["selected_atom_ids"],
            "selected_artifact_unit_count": len(truth["selected_atom_ids"]),
            "selected_artifact_scc_count": truth["selected_scc_count"],
            "selected_artifact_dependency_closed": True,
            "selected_artifact_strict_subset": truth["strict_subset"],
        }
    )
    _write_json_exclusive(source_map_path, source_map)
    _write_exclusive(case_path, case_registry_path.read_bytes())

    template = _json_object(
        RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / "identity"
        / "family.json",
        "V3 family template",
    )
    family = copy.deepcopy(template)
    family.update(
        {
            "control": control,
            "strict_subset": truth["strict_subset"],
            "calibration_label": label,
            "calibration_role": spec["calibration_role"],
            "calibration_primary_event": PRIMARY_EVENT,
            "retained_atom_ids": truth["selected_atom_ids"],
            "retained_unit_count": len(truth["selected_atom_ids"]),
            "retained_scc_count": truth["selected_scc_count"],
            "replicate_count": spec["replicate_count"],
            "replicate_schedule": [
                {
                    "replicate_id": row["replicate_id"],
                    "condition_order": row["condition_order"],
                }
                for row in schedules[label]
            ],
            "schedule_seed": spec["schedule_seed"],
            "admission_rule": "calibration_manifest_controls_decision",
            "required_joint_events_for_admission": (
                None if control == "identity" else spec["replicate_count"]
            ),
            "required_candidate_centered_events": spec[
                "required_candidate_centered_events"
            ],
            "bindings": {},
        }
    )
    bindings = {
        "full_artifact": full_path,
        "selected_artifact": selected_path,
        "source_map": source_map_path,
        "case_registry": case_path,
        "v2_case_registry": RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "case_registry_v2_r2.json",
        "scorer": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py",
        "runner": RUN_ROOT / "run_toolformer_filter_confirmation_v3.py",
        "scheduler": RUN_ROOT / "run_confirmation_v3_interleaved_calibration.py",
        "analyzer": RUN_ROOT / "analyze_confirmation_v3_interleaved_calibration.py",
        "aci_runner": RUN_ROOT / "src" / "effectslice" / "aci_runner.py",
        "aci_protocol": RUN_ROOT / "src" / "effectslice" / "aci_protocol.py",
        "evidence_binding": RUN_ROOT / "src" / "effectslice" / "evidence_binding.py",
        "transport": RUN_ROOT / "confirmation_transport_v3.py",
        "case_generator": RUN_ROOT
        / "src"
        / "effectslice"
        / "toolformer_filter_cases.py",
    }
    for name, path in bindings.items():
        _bind_standard(family, name, path)
    _bind_task_prompt(family, task_prompt_path)

    workspace = RUN_ROOT / "task_workspaces" / "toolformer_filter_v1"
    state = workspace_tree_digest(workspace)
    family["workspace_path"] = _stored_path(workspace)
    family["workspace_tree_sha256"] = state["sha256"]
    family["workspace_file_count"] = state["file_count"]
    family["workspace_total_bytes"] = state["total_bytes"]
    family["workspace_excluded_directory_names"] = state[
        "excluded_directory_names"
    ]
    if set(family["bindings"]) != set(bound_runner.REQUIRED_BINDINGS):
        raise InterleavedRegistrationError("family binding set is incomplete")
    _write_json_exclusive(family_path, family)
    bound_runner.load_and_verify_family(
        family_path, family["replicate_schedule"][0]["replicate_id"]
    )
    return family


def _execution_binding(path: Path) -> dict[str, str]:
    return {
        "path": _stored_path(path),
        "sha256": _sha256(Path(path).read_bytes()),
    }


def build_registration() -> dict[str, Any]:
    if ARTIFACT_ROOT.exists():
        raise FileExistsError(ARTIFACT_ROOT)
    if RESULT_ROOT.exists():
        raise FileExistsError(RESULT_ROOT)
    required_scripts = (
        Path(__file__),
        RUN_ROOT / "run_toolformer_filter_confirmation_v3.py",
        RUN_ROOT / "run_confirmation_v3_interleaved_calibration.py",
        RUN_ROOT / "analyze_confirmation_v3_interleaved_calibration.py",
    )
    for path in required_scripts:
        if not path.is_file():
            raise FileNotFoundError(path)

    source_root = RUN_ROOT / "artifacts" / "toolformer_filter"
    original_artifact = source_root / "full_artifact.md"
    prefix_01 = source_root / "slices" / "candidates" / "prefix_01.md"
    original_source_map = _json_object(
        source_root / "source_atom_map.json", "source atom map"
    )
    original_prompt = source_root / "task_prompt.md"
    source_case_registry = (
        source_root / "confirmation_v3" / "identity" / "case_registry.json"
    )
    for path in (original_artifact, prefix_01, original_prompt, source_case_registry):
        if not path.is_file():
            raise FileNotFoundError(path)

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=False)
    task_prompt_path = ARTIFACT_ROOT / "task_prompt.md"
    case_registry_path = ARTIFACT_ROOT / "case_registry.json"
    _write_exclusive(task_prompt_path, _normalize_lf(original_prompt.read_bytes()))
    _write_exclusive(case_registry_path, _normalize_lf(source_case_registry.read_bytes()))
    payloads = artifact_payloads(original_artifact.read_bytes(), prefix_01.read_bytes())
    global_schedule = build_interleaved_schedule()
    schedules = {
        label: [row for row in global_schedule if row["label"] == label]
        for label in LABEL_SPECS
    }
    families = {}
    for label in LABEL_SPECS:
        family_dir = ARTIFACT_ROOT / label
        _build_family(
            label=label,
            family_dir=family_dir,
            payloads=payloads[label],
            original_source_map=original_source_map,
            case_registry_path=case_registry_path,
            task_prompt_path=task_prompt_path,
            schedules=schedules,
        )
        family_path = family_dir / "family.json"
        families[label] = {
            "path": _stored_path(family_path),
            "sha256": _sha256(family_path.read_bytes()),
            "underlying_control": LABEL_SPECS[label]["underlying_control"],
            "calibration_role": LABEL_SPECS[label]["calibration_role"],
            "replicate_count": LABEL_SPECS[label]["replicate_count"],
            "required_candidate_centered_events": LABEL_SPECS[label][
                "required_candidate_centered_events"
            ],
        }

    prior_diagnostic = (
        RUN_ROOT.parent.parent
        / "postrun"
        / "derived"
        / RUN_ROOT.name
        / "confirmation_v3"
        / "calibration_analysis.json"
    )
    preregistration = {
        "schema_version": "effectslice-v3-interleaved-calibration-preregistration.v1",
        "registration_status": "complete",
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "analysis_role": "fresh_registered_calibration_replication",
        "task_key": "toolformer_filter",
        "statistical_unit": "registered_matched_block",
        "decision_basis": "finite_registered_schedule",
        "independence_verified": False,
        "population_guarantee": False,
        "primary_event": PRIMARY_EVENT,
        "primary_event_definition": {
            "baseline_condition": "B success is false",
            "candidate_condition": "S success and hard constraints are true",
            "noninferiority_condition": "q_S >= q_F - 0.05",
            "reference_success_required": False,
        },
        "calibration_decision": {
            "positive": "18 of 18 primary events required",
            "negative": "strictly fewer than 18 of 18 primary events required",
            "identity": "descriptive instrumentation only",
            "instrument_pass": "positive and negative requirements both hold",
        },
        "families": families,
        "global_schedule_seed": SCHEDULE_SEED,
        "global_schedule": global_schedule,
        "registered_block_count": len(global_schedule),
        "registered_condition_run_count": len(global_schedule) * 3,
        "conditions": ["B", "F", "S"],
        "private_score_policy": "final_only",
        "no_replacement_replicates": True,
        "preserve_registered_failures": True,
        "maximum_parallel_workers": 2,
        "output_roots": {
            label: _stored_path(RESULT_ROOT / label) for label in LABEL_SPECS
        },
        "progress_path": _stored_path(PROGRESS_PATH),
        "execution_lock_path": _stored_path(EXECUTION_LOCK_PATH),
        "provider": {
            "provider_label": "DeepSeek V3.2",
            "base_url": legacy.REGISTERED_BASE_URL,
            "model_alias": legacy.REGISTERED_MODEL_ALIAS,
            "wire_api": legacy.REGISTERED_WIRE_API,
            "temperature": 0,
            "max_tokens": legacy.REGISTERED_MAX_TOKENS,
            "timeout_seconds": legacy.REGISTERED_TIMEOUT_SECONDS,
            "maximum_transport_attempts": legacy.REGISTERED_MAX_ATTEMPTS,
            "retry_delay_seconds": legacy.REGISTERED_RETRY_DELAY_SECONDS,
            "direct_connection": True,
            "proxy_policy": legacy.REGISTERED_PROXY_POLICY,
        },
        "execution_bindings": {
            "builder": _execution_binding(Path(__file__)),
            "runner": _execution_binding(
                RUN_ROOT / "run_toolformer_filter_confirmation_v3.py"
            ),
            "scheduler": _execution_binding(
                RUN_ROOT / "run_confirmation_v3_interleaved_calibration.py"
            ),
            "analyzer": _execution_binding(
                RUN_ROOT / "analyze_confirmation_v3_interleaved_calibration.py"
            ),
        },
        "design_source": {
            "path": _stored_path(prior_diagnostic),
            "sha256": _sha256(prior_diagnostic.read_bytes()),
            "role": "posthoc_rule_design_only_not_confirmation_evidence",
        },
        "scope_guards": {
            "cross_paper_claim_ready": False,
            "human_benefit_claim_ready": False,
            "provider_population_claim_ready": False,
        },
    }
    _write_json_exclusive(PREREGISTRATION_PATH, preregistration)
    preregistration_sha = _sha256(PREREGISTRATION_PATH.read_bytes())
    anchor = {
        "schema_version": "effectslice-v3-interleaved-calibration-anchor.v1",
        "preregistration_path": _stored_path(PREREGISTRATION_PATH),
        "preregistration_sha256": preregistration_sha,
        "registered_block_count": len(global_schedule),
        "registered_condition_run_count": len(global_schedule) * 3,
        "provider_execution_started": False,
    }
    _write_json_exclusive(ANCHOR_PATH, anchor)
    return audit_registration(allow_execution_started=False)


def _resolve(stored: str) -> Path:
    path = Path(stored)
    return path.resolve() if path.is_absolute() else (RUN_ROOT / path).resolve()


def audit_registration(*, allow_execution_started: bool) -> dict[str, Any]:
    preregistration = _json_object(PREREGISTRATION_PATH, "preregistration")
    anchor = _json_object(ANCHOR_PATH, "preregistration anchor")
    preregistration_sha = _sha256(PREREGISTRATION_PATH.read_bytes())
    if anchor.get("preregistration_sha256") != preregistration_sha:
        raise InterleavedRegistrationError("preregistration anchor digest mismatch")
    if preregistration.get("registration_status") != "complete":
        raise InterleavedRegistrationError("preregistration is incomplete")
    if preregistration.get("global_schedule") != build_interleaved_schedule():
        raise InterleavedRegistrationError("global schedule changed")
    for name, binding in preregistration.get("execution_bindings", {}).items():
        if not isinstance(binding, dict):
            raise InterleavedRegistrationError(f"{name} binding is invalid")
        path = _resolve(binding.get("path", ""))
        if not path.is_file() or _sha256(path.read_bytes()) != binding.get("sha256"):
            raise InterleavedRegistrationError(f"{name} binding changed")
    for label, record in preregistration.get("families", {}).items():
        path = _resolve(record.get("path", ""))
        if not path.is_file() or _sha256(path.read_bytes()) != record.get("sha256"):
            raise InterleavedRegistrationError(f"{label} family changed")
        family = _json_object(path, f"{label} family")
        schedule = [
            {
                "replicate_id": row["replicate_id"],
                "condition_order": row["condition_order"],
            }
            for row in preregistration["global_schedule"]
            if row["label"] == label
        ]
        if family.get("replicate_schedule") != schedule:
            raise InterleavedRegistrationError(f"{label} family schedule changed")
        bound_runner.load_and_verify_family(path, schedule[0]["replicate_id"])
    started = EXECUTION_LOCK_PATH.exists()
    if started and not allow_execution_started:
        raise InterleavedRegistrationError("provider execution already started")
    if not started and RESULT_ROOT.exists():
        raise InterleavedRegistrationError(
            "result root exists without an execution lock"
        )
    return {
        "valid": True,
        "preregistration_sha256": preregistration_sha,
        "anchor_verified": True,
        "registered_block_count": preregistration["registered_block_count"],
        "registered_condition_run_count": preregistration[
            "registered_condition_run_count"
        ],
        "provider_execution_started": started,
        "control_interleaved": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or audit the V3 interleaved calibration registration"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build")
    audit = subparsers.add_parser("audit")
    audit.add_argument("--allow-execution-started", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "build":
        result = build_registration()
    else:
        result = audit_registration(
            allow_execution_started=args.allow_execution_started
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
