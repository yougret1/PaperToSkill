from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import shutil
import tempfile
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = RUN_ROOT / "artifacts" / "confirmation_v4"
PREREGISTRATION_PATH = OUTPUT_ROOT / "preregistration.json"
EVIDENCE_BOUNDARY = "registered_public_test_finite_schedule_confirmation_v4"
MODEL_ALIAS = "deepseek-v4-flash"
BASE_URL = "https://api.deepseek.com"
PUBLIC_TEST_FILES = {
    "snap_mfse": "test_snap_core_public.py",
    "toolformer_filter": "test_toolformer_filter_public.py",
}
CONTRACT = {
    "registered_blocks": 18,
    "maximum_baseline_successes": 2,
    "minimum_full_successes": 16,
    "minimum_slice_successes": 16,
    "maximum_full_minus_slice_success_gap": 2,
    "all_registered_outputs_must_be_complete": True,
    "all_integrity_checks_must_pass": True,
}
IDENTITY_CONTRACT = {
    "registered_blocks": 6,
    "minimum_full_slice_success_matches": 5,
    "maximum_full_slice_success_count_gap": 1,
}
T06_MARKDOWN = (
    "6. **Restate the shared selection invariant** (`T06`)\n"
    "   Apply the same inclusive `margin >= tau_filter` rule independently to every\n"
    "   proposed call and preserve the proposals' original order in the returned\n"
    "   decisions. This restates the registered T04/T05 invariant and introduces no\n"
    "   new computation.\n"
)


import sys

sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.confirmation_v3 import balanced_schedule  # noqa: E402
from effectslice.snap_mfse_cases import build_case_registry as build_snap_cases  # noqa: E402
from effectslice.toolformer_filter_cases import (  # noqa: E402
    build_case_registry as build_toolformer_cases,
)
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _stored(path: Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(RUN_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _stored_future(path: Path, staging: Path, destination: Path) -> str:
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(Path(staging).resolve())
    except ValueError:
        return _stored(resolved)
    return _stored(Path(destination).resolve() / relative)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def _write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(value)


def _binding(
    family: dict[str, Any],
    name: str,
    path: Path,
    *,
    staging: Path,
    destination: Path,
) -> None:
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"V4 binding is missing: {resolved}")
    family[f"{name}_path"] = _stored_future(resolved, staging, destination)
    family[f"{name}_sha256"] = _sha256(resolved)


def finite_schedule_decision(
    counts: dict[str, int],
    *,
    outputs_complete: bool = True,
    integrity_passed: bool = True,
) -> dict[str, Any]:
    required = {"B", "F", "S"}
    if set(counts) != required or any(
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > CONTRACT["registered_blocks"]
        for value in counts.values()
    ):
        raise ValueError(
            "condition counts must contain bounded integer B/F/S values"
        )
    if type(outputs_complete) is not bool or type(integrity_passed) is not bool:
        raise ValueError("completion and integrity flags must be bools")
    checks = {
        "baseline_ceiling": counts["B"] <= CONTRACT["maximum_baseline_successes"],
        "full_sufficiency": counts["F"] >= CONTRACT["minimum_full_successes"],
        "slice_sufficiency": counts["S"] >= CONTRACT["minimum_slice_successes"],
        "slice_shortfall": (
            counts["F"] - counts["S"]
            <= CONTRACT["maximum_full_minus_slice_success_gap"]
        ),
        "outputs_complete": outputs_complete,
        "integrity_passed": integrity_passed,
    }
    passed = all(checks.values())
    status = (
        "Invalid"
        if not outputs_complete or not integrity_passed
        else "Admit"
        if passed
        else "Reject"
    )
    return {"checks": checks, "passed": passed, "status": status}


def identity_instrumentation_decision(
    *,
    full_successes: list[bool],
    slice_successes: list[bool],
) -> dict[str, Any]:
    if (
        len(full_successes) != IDENTITY_CONTRACT["registered_blocks"]
        or len(slice_successes) != IDENTITY_CONTRACT["registered_blocks"]
        or any(type(value) is not bool for value in full_successes + slice_successes)
    ):
        raise ValueError("identity instrumentation requires six bool F/S outcomes")
    matches = sum(
        full == sliced for full, sliced in zip(full_successes, slice_successes)
    )
    gap = abs(sum(full_successes) - sum(slice_successes))
    checks = {
        "paired_success_match": (
            matches >= IDENTITY_CONTRACT["minimum_full_slice_success_matches"]
        ),
        "success_count_gap": (
            gap <= IDENTITY_CONTRACT["maximum_full_slice_success_count_gap"]
        ),
    }
    return {
        "checks": checks,
        "full_slice_success_matches": matches,
        "full_slice_success_count_gap": gap,
        "passed": all(checks.values()),
    }


def _schedule(seed: int, count: int, prefix: str) -> list[dict[str, Any]]:
    rows = balanced_schedule(seed=seed, replicate_count=count)
    return [
        {
            "replicate_id": f"{prefix}{index:03d}",
            "condition_order": row["condition_order"],
        }
        for index, row in enumerate(rows, start=1)
    ]


def _global_interleaved_schedule(
    snap: dict[str, Any], toolformer: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rng = random.Random(2026072004)
    identity_strata = {1, 4, 7, 10, 13, 16}
    families = {
        "snap_mfse": snap,
        "toolformer_negative": toolformer["negative"],
        "toolformer_positive": toolformer["positive"],
        "toolformer_identity": toolformer["identity"],
    }
    rows: list[dict[str, Any]] = []
    for stratum in range(1, 19):
        labels = ["snap_mfse", "toolformer_negative", "toolformer_positive"]
        if stratum in identity_strata:
            labels.append("toolformer_identity")
        rng.shuffle(labels)
        for family_key in labels:
            schedule_index = (
                sorted(identity_strata).index(stratum)
                if family_key == "toolformer_identity"
                else stratum - 1
            )
            registered = families[family_key]["replicate_schedule"][schedule_index]
            rows.append(
                {
                    "global_order_index": len(rows) + 1,
                    "stratum": stratum,
                    "family_key": family_key,
                    "task_key": families[family_key]["task_key"],
                    "replicate_id": registered["replicate_id"],
                    "condition_order": registered["condition_order"],
                }
            )
    if len(rows) != 60:
        raise ValueError("global interleaved schedule must contain 60 blocks")
    return rows


def _slice_registry(
    path: Path,
    *,
    candidate_id: str,
    artifact_path: Path,
    retained_atom_ids: list[str],
) -> None:
    payload = {
        "schema_version": "effectslice-confirmation-v4-slice-registry.v1",
        "candidates": [
            {
                "candidate_id": candidate_id,
                "artifact_path": artifact_path.name,
                "artifact_sha256": _sha256(artifact_path),
                "retained_atom_ids": retained_atom_ids,
                "retained_scc_count": len(retained_atom_ids),
                "dependency_closed": True,
            }
        ],
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }
    _write_json(path, payload)


def _base_family(
    *,
    task_key: str,
    task_id: str,
    candidate_id: str,
    retained_atom_ids: list[str],
    replicate_schedule: list[dict[str, Any]],
    schedule_seed: int,
    role: str,
    strict_subset: bool,
    admission_decision_applicable: bool,
    expected_admission: bool | None,
) -> dict[str, Any]:
    return {
        "schema_version": "effectslice-confirmation-v4-family.v1",
        "registration_status": "complete",
        "task_key": task_key,
        "task_id": task_id,
        "candidate_role": role,
        "selected_candidate_id": candidate_id,
        "retained_atom_ids": retained_atom_ids,
        "retained_scc_count": len(retained_atom_ids),
        "strict_subset": strict_subset,
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v4",
        "case_count": 64,
        "case_role": "clustered_within_condition_run",
        "condition_run_unit": "fresh_provider_conversation",
        "analysis_unit": "complete_registered_finite_schedule",
        "schedule_seed": schedule_seed,
        "replicate_count": len(replicate_schedule),
        "replicate_schedule": replicate_schedule,
        "run_success_threshold": 0.95,
        "finite_schedule_contract": copy.deepcopy(CONTRACT),
        "identity_instrumentation_contract": copy.deepcopy(IDENTITY_CONTRACT),
        "admission_decision_applicable": admission_decision_applicable,
        "expected_admission": expected_admission,
        "decision_basis": "finite_registered_schedule_without_population_inference",
        "independence_verified": False,
        "fresh_provider_conversation_per_condition": True,
        "private_score_policy": "final_only",
        "public_test_policy": "locked_public_test_visible_private_scorer_terminal",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "base_url": BASE_URL,
        "model_alias": MODEL_ALIAS,
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "timeout_seconds": 240.0,
        "retry_delay_seconds": 2.0,
        "direct_connection": True,
        "proxy_policy": "disabled",
        "confirmation_unsealed": False,
        "hypotheses": [
            {"hypothesis_id": "C_baseline_ceiling", "rule": "B <= 2 of 18"},
            {"hypothesis_id": "C_full_sufficiency", "rule": "F >= 16 of 18"},
            {"hypothesis_id": "C_slice_sufficiency", "rule": "S >= 16 of 18"},
            {"hypothesis_id": "C_slice_shortfall", "rule": "F - S <= 2"},
            {"hypothesis_id": "C_complete", "rule": "all outputs complete"},
            {"hypothesis_id": "C_integrity", "rule": "all integrity checks pass"},
        ],
        "comparison_role": EVIDENCE_BOUNDARY,
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }


def _source_map_with_paths(
    source_map: dict[str, Any],
    *,
    full_path: Path,
    selected_path: Path,
    role: str,
) -> dict[str, Any]:
    payload = copy.deepcopy(source_map)
    payload["source_schema_version"] = payload.get("schema_version")
    payload["schema_version"] = "effectslice-confirmation-v4-source-map.v1"
    payload["registration_status"] = "complete"
    payload["candidate_role"] = role
    payload["full_artifact_path"] = full_path.name
    payload["full_artifact_sha256"] = _sha256(full_path)
    payload["selected_artifact_path"] = selected_path.name
    payload["selected_artifact_sha256"] = _sha256(selected_path)
    payload["evidence_boundary"] = EVIDENCE_BOUNDARY
    return payload


def _add_t06(source_map: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(source_map)
    by_id = {row["atom_id"]: row for row in payload["atoms"]}
    payload["atoms"].append(
        {
            "atom_id": "T06",
            "title": "Restate the shared selection invariant",
            "instruction": (
                "Apply the same inclusive threshold rule to every proposal and "
                "preserve proposal order; this adds no computation."
            ),
            "contract_role": "registered_redundant_restatement",
            "novel": False,
            "redundancy_status": "registered_redundant",
            "source_spans": copy.deepcopy(
                by_id["T04"]["source_spans"] + by_id["T05"]["source_spans"]
            ),
        }
    )
    payload["requires"]["T06"] = ["T04", "T05"]
    payload["dependency_edges"].extend(
        [{"from": "T06", "to": "T04"}, {"from": "T06", "to": "T05"}]
    )
    return payload


def _validate_source_truth(
    source_map: dict[str, Any],
    *,
    full_path: Path,
    selected_path: Path,
    retained_atom_ids: list[str],
    strict_subset: bool,
) -> None:
    atom_ids = [row.get("atom_id") for row in source_map.get("atoms", [])]
    if not atom_ids or any(
        not isinstance(atom, str) or not atom for atom in atom_ids
    ):
        raise ValueError("source map atom IDs must be nonempty strings")
    if len(set(atom_ids)) != len(atom_ids):
        raise ValueError("source map atom IDs must be unique")
    requires = source_map.get("requires")
    edges = source_map.get("dependency_edges")
    if not isinstance(requires, dict) or set(requires) != set(atom_ids):
        raise ValueError("source map requires must cover every atom")
    required_edges: set[tuple[str, str]] = set()
    for atom, dependencies in requires.items():
        if not isinstance(dependencies, list) or len(dependencies) != len(
            set(dependencies)
        ):
            raise ValueError("source map dependencies must be unique lists")
        for dependency in dependencies:
            if dependency not in atom_ids or dependency == atom:
                raise ValueError(
                    "source map dependency refers to a missing or self atom"
                )
            required_edges.add((atom, dependency))
    if not isinstance(edges, list):
        raise ValueError("source map dependency_edges must be a list")
    edge_pairs = [(row.get("from"), row.get("to")) for row in edges]
    if len(edge_pairs) != len(set(edge_pairs)) or set(edge_pairs) != required_edges:
        raise ValueError("requires and dependency_edges must encode the same graph")
    retained = set(retained_atom_ids)
    if not retained or not retained.issubset(atom_ids):
        raise ValueError("retained atoms must be present in the source map")
    if any(not set(requires[atom]).issubset(retained) for atom in retained):
        raise ValueError("selected artifact is not dependency-closed")
    full_text = full_path.read_text(encoding="utf-8")
    selected_text = selected_path.read_text(encoding="utf-8")
    full_membership = {atom for atom in atom_ids if f"(`{atom}`)" in full_text}
    selected_membership = {
        atom for atom in atom_ids if f"(`{atom}`)" in selected_text
    }
    if full_membership != set(atom_ids) or selected_membership != retained:
        raise ValueError("artifact atom membership does not match source-map truth")
    if strict_subset and not selected_membership < full_membership:
        raise ValueError("registered candidate must be a strict subset")
    if not strict_subset and selected_membership != full_membership:
        raise ValueError("identity candidate must preserve atom membership")


def _case_payload_digest(case: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in case.items()
        if key not in {"case_id", "seed"}
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_case_registry(path: Path) -> None:
    registry = json.loads(Path(path).read_text(encoding="utf-8"))
    blocks = registry.get("blocks")
    if not isinstance(blocks, dict) or len(
        blocks.get("confirmation_v4", [])
    ) != 64:
        raise ValueError("confirmation_v4 case registry must contain 64 cases")
    earlier = [
        case
        for name, cases in blocks.items()
        if name != "confirmation_v4"
        for case in cases
    ]
    current = blocks["confirmation_v4"]
    if {case.get("case_id") for case in current} & {
        case.get("case_id") for case in earlier
    }:
        raise ValueError("confirmation_v4 case IDs overlap prior blocks")
    if {case.get("seed") for case in current} & {
        case.get("seed") for case in earlier
    }:
        raise ValueError("confirmation_v4 seeds overlap prior blocks")
    if {_case_payload_digest(case) for case in current} & {
        _case_payload_digest(case) for case in earlier
    }:
        raise ValueError("confirmation_v4 case payloads overlap prior blocks")


def _bind_common(
    family: dict[str, Any],
    *,
    directory: Path,
    task_key: str,
    case_registry: Path,
    staging: Path,
    destination: Path,
) -> None:
    workspace = RUN_ROOT / "task_workspaces" / (
        "snap_mfse_v1" if task_key == "snap_mfse" else "toolformer_filter_v1"
    )
    task_source = RUN_ROOT / "artifacts" / task_key
    public_test = workspace / PUBLIC_TEST_FILES[task_key]
    scorer = RUN_ROOT / "src" / "effectslice" / (
        "snap_mfse_scorer.py"
        if task_key == "snap_mfse"
        else "toolformer_filter_scorer.py"
    )
    runner = RUN_ROOT / (
        "run_snap_mfse_effectslice.py"
        if task_key == "snap_mfse"
        else "run_toolformer_filter_effectslice.py"
    )
    paths = {
        "full_artifact": directory / "full_artifact.md",
        "selected_artifact": directory / "selected_artifact.md",
        "source_map": directory / "source_atom_map.json",
        "slice_registry": directory / "slice_registry.json",
        "case_registry": case_registry,
        "task_prompt": task_source / "task_prompt.md",
        "public_test": public_test,
        "scorer": scorer,
        "runner": runner,
        "scheduler": RUN_ROOT / "run_confirmation_v4.py",
        "analyzer": RUN_ROOT / "analyze_confirmation_v4.py",
        "builder": RUN_ROOT / "build_confirmation_v4.py",
        "aci_runner": RUN_ROOT / "src" / "effectslice" / "aci_runner.py",
        "aci_protocol": RUN_ROOT / "src" / "effectslice" / "aci_protocol.py",
        "evidence_binding": RUN_ROOT / "src" / "effectslice" / "evidence_binding.py",
        "public_test_bridge": RUN_ROOT
        / "src"
        / "effectslice"
        / "public_test_bridge.py",
        "case_generator": RUN_ROOT / "src" / "effectslice" / (
            "snap_mfse_cases.py"
            if task_key == "snap_mfse"
            else "toolformer_filter_cases.py"
        ),
        "transport": RUN_ROOT / "run_swe_effectslice.py",
    }
    for name, path in paths.items():
        _binding(
            family,
            name,
            path,
            staging=staging,
            destination=destination,
        )
    workspace_state = workspace_tree_digest(workspace)
    family["workspace_path"] = workspace.resolve().as_posix()
    family["workspace_tree_sha256"] = workspace_state["sha256"]
    family["workspace_file_count"] = workspace_state["file_count"]
    family["public_test_file"] = public_test.name


def _build_snap(staging: Path, destination: Path) -> dict[str, Any]:
    directory = staging / "snap_mfse"
    directory.mkdir(parents=True)
    artifact_root = RUN_ROOT / "artifacts" / "snap_mfse"
    full_path = directory / "full_artifact.md"
    selected_path = directory / "selected_artifact.md"
    source_path = directory / "source_atom_map.json"
    registry_path = directory / "slice_registry.json"
    case_path = directory / "case_registry.json"
    _write_bytes(full_path, (artifact_root / "full_artifact.md").read_bytes())
    _write_bytes(
        selected_path,
        (artifact_root / "slices" / "candidates" / "prefix_03.md").read_bytes(),
    )
    source = json.loads((artifact_root / "source_atom_map.json").read_text("utf-8"))
    source_v4 = _source_map_with_paths(
        source,
        full_path=full_path,
        selected_path=selected_path,
        role="real_candidate",
    )
    retained = ["A01", "A02", "A03"]
    _validate_source_truth(
        source_v4,
        full_path=full_path,
        selected_path=selected_path,
        retained_atom_ids=retained,
        strict_subset=True,
    )
    _write_json(source_path, source_v4)
    _slice_registry(
        registry_path,
        candidate_id="snap_prefix_03_v4",
        artifact_path=selected_path,
        retained_atom_ids=retained,
    )
    build_snap_cases(case_path)
    _validate_case_registry(case_path)
    family = _base_family(
        task_key="snap_mfse",
        task_id="SNAP-MFSE",
        candidate_id="snap_prefix_03_v4",
        retained_atom_ids=retained,
        replicate_schedule=_schedule(2026072005, 18, "s"),
        schedule_seed=2026072005,
        role="real_candidate",
        strict_subset=True,
        admission_decision_applicable=True,
        expected_admission=True,
    )
    _bind_common(
        family,
        directory=directory,
        task_key="snap_mfse",
        case_registry=case_path,
        staging=staging,
        destination=destination,
    )
    _write_json(directory / "family.json", family)
    return family


def _build_toolformer(
    staging: Path, destination: Path
) -> dict[str, dict[str, Any]]:
    root = staging / "toolformer_filter"
    root.mkdir(parents=True)
    artifact_root = RUN_ROOT / "artifacts" / "toolformer_filter"
    base_full = (artifact_root / "full_artifact.md").read_bytes()
    base_selected = (
        artifact_root / "slices" / "candidates" / "prefix_01.md"
    ).read_bytes()
    base_map = json.loads((artifact_root / "source_atom_map.json").read_text("utf-8"))
    common_cases = root / "case_registry.json"
    build_toolformer_cases(common_cases)
    _validate_case_registry(common_cases)
    specs = {
        "negative": {
            "full": base_full,
            "selected": base_selected,
            "map": base_map,
            "retained": ["T01"],
            "candidate_id": "toolformer_prefix_01_v4",
            "role": "real_candidate_negative_control",
            "strict_subset": True,
            "count": 18,
            "seed": 2026072006,
            "prefix": "n",
            "admission_applicable": True,
            "expected_admission": False,
        },
        "positive": {
            "full": base_full + b"\n" + T06_MARKDOWN.encode("utf-8"),
            "selected": base_full,
            "map": _add_t06(base_map),
            "retained": ["T01", "T02", "T03", "T04", "T05"],
            "candidate_id": "toolformer_remove_t06_v4",
            "role": "planted_redundancy_positive_control",
            "strict_subset": True,
            "count": 18,
            "seed": 2026072007,
            "prefix": "p",
            "admission_applicable": True,
            "expected_admission": True,
        },
        "identity": {
            "full": base_full,
            "selected": base_full,
            "map": base_map,
            "retained": ["T01", "T02", "T03", "T04", "T05"],
            "candidate_id": "toolformer_identity_v4",
            "role": "identity_instrumentation_only",
            "strict_subset": False,
            "count": 6,
            "seed": 2026072008,
            "prefix": "i",
            "admission_applicable": False,
            "expected_admission": None,
        },
    }
    families = {}
    for label, spec in specs.items():
        directory = root / label
        directory.mkdir()
        full_path = directory / "full_artifact.md"
        selected_path = directory / "selected_artifact.md"
        source_path = directory / "source_atom_map.json"
        registry_path = directory / "slice_registry.json"
        _write_bytes(full_path, spec["full"])
        _write_bytes(selected_path, spec["selected"])
        source_v4 = _source_map_with_paths(
            spec["map"],
            full_path=full_path,
            selected_path=selected_path,
            role=spec["role"],
        )
        _validate_source_truth(
            source_v4,
            full_path=full_path,
            selected_path=selected_path,
            retained_atom_ids=spec["retained"],
            strict_subset=spec["strict_subset"],
        )
        _write_json(source_path, source_v4)
        _slice_registry(
            registry_path,
            candidate_id=spec["candidate_id"],
            artifact_path=selected_path,
            retained_atom_ids=spec["retained"],
        )
        family = _base_family(
            task_key="toolformer_filter",
            task_id="TOOLFORMER-FILTER",
            candidate_id=spec["candidate_id"],
            retained_atom_ids=spec["retained"],
            replicate_schedule=_schedule(spec["seed"], spec["count"], spec["prefix"]),
            schedule_seed=spec["seed"],
            role=spec["role"],
            strict_subset=spec["strict_subset"],
            admission_decision_applicable=spec["admission_applicable"],
            expected_admission=spec["expected_admission"],
        )
        _bind_common(
            family,
            directory=directory,
            task_key="toolformer_filter",
            case_registry=common_cases,
            staging=staging,
            destination=destination,
        )
        _write_json(directory / "family.json", family)
        families[label] = family
    return families


def build_registration(output_root: Path = OUTPUT_ROOT) -> dict[str, Any]:
    destination = Path(output_root).resolve()
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=".confirmation_v4.staging-", dir=destination.parent)
    ).resolve()
    try:
        snap = _build_snap(staging, destination)
        toolformer = _build_toolformer(staging, destination)
        audit_path = (
            RUN_ROOT
            / "derived"
            / "confirmation_v3_public_test_mismatch_audit.json"
        )
        if not audit_path.is_file():
            raise FileNotFoundError(
                f"V3 public-test mismatch audit is missing: {audit_path}"
            )
        registration = {
            "schema_version": "effectslice-confirmation-v4-preregistration.v1",
            "registration_status": "complete",
            "evidence_boundary": EVIDENCE_BOUNDARY,
            "decision_basis": "finite_registered_schedule_without_population_inference",
            "finite_schedule_contract": copy.deepcopy(CONTRACT),
            "identity_instrumentation_contract": copy.deepcopy(IDENTITY_CONTRACT),
            "threshold_rationale": (
                "The operational SLA tolerates at most two failures in eighteen "
                "registered runs. It is not a confidence interval or a population claim."
            ),
            "revision_provenance": {
                "prior_v3_role": "historical_harness-confounded_evidence_only",
                "public_test_mismatch_audit_path": _stored(audit_path),
                "public_test_mismatch_audit_sha256": _sha256(audit_path),
                "new_private_case_block": "confirmation_v4",
                "fresh_provider_sessions_required": True,
            },
            "provider": {
                "provider_label": "DeepSeek V3.2",
                "base_url": BASE_URL,
                "model_alias": MODEL_ALIAS,
                "wire_api": "openai_chat_completions",
                "temperature": 0,
                "max_tokens": 8192,
                "timeout_seconds": 240.0,
                "maximum_transport_attempts": 5,
                "retry_delay_seconds": 2.0,
            },
            "public_test_policy": {
                "visible_channel": "locked public pytest only",
                "private_scorer": "one terminal call after submit or budget exhaustion",
            },
            "families": {
                "snap_mfse": {
                    "path": _stored(destination / "snap_mfse" / "family.json"),
                    "sha256": _sha256(staging / "snap_mfse" / "family.json"),
                    "replicate_count": 18,
                },
                **{
                    f"toolformer_{label}": {
                        "path": _stored(
                            destination
                            / "toolformer_filter"
                            / label
                            / "family.json"
                        ),
                        "sha256": _sha256(
                            staging / "toolformer_filter" / label / "family.json"
                        ),
                        "replicate_count": family["replicate_count"],
                    }
                    for label, family in toolformer.items()
                },
            },
            "global_interleaved_schedule": _global_interleaved_schedule(
                snap, toolformer
            ),
            "registered_stratum_count": 18,
            "registered_block_count": 60,
            "registered_condition_run_count": 180,
            "maximum_parallel_workers": 2,
            "preserve_registered_failures": True,
            "execution": {
                "output_root": _stored(
                    RUN_ROOT / "experiment_results" / "confirmation_v4"
                ),
                "progress_path": _stored(
                    RUN_ROOT
                    / "experiment_results"
                    / "confirmation_v4"
                    / "confirmation_v4_progress.json"
                ),
            },
            "scope_guards": {
                "iid_inference_used": False,
                "population_guarantee": False,
                "cross_paper_claim_ready": False,
                "human_benefit_claim_ready": False,
            },
        }
        _write_json(staging / "preregistration.json", registration)
        staging.rename(destination)
        return registration
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Build write-once EffectSlice V4 inputs")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    registration = build_registration(args.output_root)
    preregistration_path = Path(args.output_root).resolve() / "preregistration.json"
    print(
        json.dumps(
            {
                "registered_block_count": registration["registered_block_count"],
                "registered_condition_run_count": registration[
                    "registered_condition_run_count"
                ],
                "preregistration_sha256": _sha256(preregistration_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
