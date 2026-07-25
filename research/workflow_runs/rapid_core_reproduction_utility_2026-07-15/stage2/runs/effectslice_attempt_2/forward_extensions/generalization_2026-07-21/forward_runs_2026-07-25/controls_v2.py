from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Iterator


EXPERIMENT_ROOT = Path(__file__).resolve().parent
FORWARD_ROOT = EXPERIMENT_ROOT.parent
if str(FORWARD_ROOT) not in sys.path:
    sys.path.insert(0, str(FORWARD_ROOT))

import output_contract_successor as fg5  # noqa: E402


fg4 = fg5.fg4
fg1 = fg5.fg1

DEFAULT_REGISTRATION = EXPERIMENT_ROOT / "registration" / "controls_v2"
DEFAULT_RUN = EXPERIMENT_ROOT / "runs" / "controls_v2"
DEFAULT_ANALYSIS = EXPERIMENT_ROOT / "analysis" / "controls_v2"
EXPECTED_FG5_BUNDLE = (
    "8ec345c120d8aa4ae432ba77e5a120f81c3ce727bca8a7a94800cade934479a6"
)
SCHEMA_VERSION = "effectslice-controls-v2.v1"
ANCHOR_TASKS = ("AGENT-TF-01", "DATA-HDB-01", "NLP-LLM-01", "SE-PE-01")
REGISTRIES = ("A", "B")
ARMS = (
    "F_reference",
    "F_identity",
    "P_redundancy_removed",
    "N_exact_contract_removed",
)
REPETITIONS = (1, 2, 3)
REGISTERED_ROWS = len(ANCHOR_TASKS) * len(REGISTRIES) * len(ARMS) * len(REPETITIONS)
REDUNDANT_TEXT = (
    "[CONTROLS-V2 REDUNDANT ATOM]\n"
    "The task-specific exact output contract immediately above remains unchanged "
    "and must still be followed exactly.\n"
)


class ControlsError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ControlsError(message)


def load_json(path: Path) -> Any:
    return fg1.load_json(fg1.windows_extended_path(path))


def canonical_json(value: object) -> bytes:
    return fg1.canonical_json(value)


def sha256_bytes(value: bytes) -> str:
    return fg1.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return fg1.sha256_file(fg1.windows_extended_path(path))


def atomic_json(path: Path, value: object) -> None:
    fg1.atomic_json(fg1.windows_extended_path(path), value)


def source_verification() -> dict[str, Any]:
    result = fg5.verify_successor(
        fg5.DEFAULT_PARENT,
        fg5.DEFAULT_FG2,
        fg5.DEFAULT_FG3,
        fg5.DEFAULT_FG4,
        fg5.DEFAULT_CONTRACTS,
        fg5.DEFAULT_SUCCESSOR,
    )
    require(result["development_frozen"] is True, "FG5 source is not frozen")
    require(result["bundle_sha256"] == EXPECTED_FG5_BUNDLE, "FG5 source changed")
    return result


def load_runtime() -> Any:
    materialization = fg1.windows_extended_path(fg5.DEFAULT_PARENT)
    return fg1.load_module(
        materialization / "support" / "task_runtime.py",
        "effectslice_controls_v2_task_runtime",
    )


def expected_registry(runtime: Any, task_id: str, registry_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases, expected = runtime.build_registry(task_id, registry_id)
    require(len(cases) == len(expected) == 64, f"private case count changed: {task_id}:{registry_id}")
    require(
        [item["case_id"] for item in cases] == [item["case_id"] for item in expected],
        f"case/expected ID order changed: {task_id}:{registry_id}",
    )
    return cases, expected


def source_f_rows() -> dict[tuple[str, str], dict[str, Any]]:
    source_verification()
    rows = load_json(fg5.DEFAULT_SUCCESSOR / "global_remote_schedule.json")["rows"]
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if (
            row["execution_family"] == "primary"
            and row["condition"] == "F"
            and row["model_slot_id"] == "deepseek_primary"
            and row["task_id"] in ANCHOR_TASKS
            and row["registry_id"] in REGISTRIES
        ):
            candidates[(str(row["task_id"]), str(row["registry_id"]))].append(row)
    require(set(candidates) == {(task, registry) for task in ANCHOR_TASKS for registry in REGISTRIES}, "anchor F rows incomplete")
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for key, values in candidates.items():
        require(len(values) == 3, f"expected three source blocks: {key}")
        values.sort(key=lambda row: int(row["global_sequence_index"]))
        selected[key] = values[0]
    return selected


def set_visible_text(request_value: dict[str, Any], text: str) -> None:
    kind, target = fg4.visible_request_text(request_value)
    if kind == "input":
        request_value["input"] = text
    else:
        target["content"] = text


def transformed_requests(
    source_row: dict[str, Any], exact_prompt: str
) -> tuple[dict[str, bytes], dict[str, Any]]:
    source_id = str(source_row["execution_id"])
    source_path = fg5.DEFAULT_SUCCESSOR / "requests" / f"{source_id}.json"
    source_bytes = source_path.read_bytes()
    require(
        sha256_bytes(source_bytes) == source_row["serialized_wire_request_sha256"],
        f"source request changed: {source_id}",
    )
    source_value = json.loads(source_bytes.decode("utf-8", errors="strict"))
    _, source_target = fg4.visible_request_text(source_value)
    source_visible = str(source_target if isinstance(source_target, str) else source_target["content"])
    require(source_visible.count(exact_prompt) == 1, f"exact prompt occurrence changed: {source_id}")
    prefix, suffix = source_visible.split(exact_prompt, 1)
    visible = {
        "F_reference": prefix + exact_prompt + REDUNDANT_TEXT + suffix,
        "F_identity": prefix + exact_prompt + REDUNDANT_TEXT + suffix,
        "P_redundancy_removed": source_visible,
        "N_exact_contract_removed": prefix + suffix,
    }
    requests: dict[str, bytes] = {}
    for arm, text in visible.items():
        request_value = copy.deepcopy(source_value)
        set_visible_text(request_value, text)
        requests[arm] = canonical_json(request_value)
    require(
        requests["F_reference"] == requests["F_identity"],
        "reference and identity requests differ",
    )
    require(
        requests["P_redundancy_removed"] == source_bytes,
        "positive arm is not the byte-identical FG5 F source request",
    )
    require(
        len({sha256_bytes(value) for value in requests.values()}) == 3,
        "control request nonidentity pattern changed",
    )
    atoms = {
        "base_atom_id": "ctrl-base-" + sha256_bytes((prefix + suffix).encode("utf-8"))[:16],
        "exact_atom_id": "ctrl-exact-" + sha256_bytes(exact_prompt.encode("utf-8"))[:16],
        "redundant_atom_id": "ctrl-redundant-" + sha256_bytes(REDUNDANT_TEXT.encode("utf-8"))[:16],
        "exact_prompt_sha256": sha256_bytes(exact_prompt.encode("utf-8")),
        "redundant_text_sha256": sha256_bytes(REDUNDANT_TEXT.encode("utf-8")),
        "source_visible_sha256": sha256_bytes(source_visible.encode("utf-8")),
    }
    return requests, atoms


def execution_id(
    task_id: str,
    registry_id: str,
    arm: str,
    repetition: int,
    source_execution_id: str,
) -> str:
    digest = hashlib.sha256(
        (
            f"{SCHEMA_VERSION}|{EXPECTED_FG5_BUNDLE}|{task_id}|{registry_id}|"
            f"{arm}|{repetition}|{source_execution_id}"
        ).encode("utf-8")
    ).hexdigest()[:24]
    return "ctrl2-exec-" + digest


def deterministic_control_state(
    *,
    digest_valid: bool,
    contract_results: dict[str, bool] | None,
) -> str:
    if not digest_valid or contract_results is None:
        return "Invalid"
    require(bool(contract_results), "deterministic control has no case results")
    require(
        all(isinstance(value, bool) for value in contract_results.values()),
        "deterministic control has a non-boolean case result",
    )
    return "Admit" if all(contract_results.values()) else "Reject"


def deterministic_layer(runtime: Any) -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    confusion: Counter[tuple[str, str]] = Counter()
    materialization = fg1.windows_extended_path(fg5.DEFAULT_PARENT)
    for task_id in ANCHOR_TASKS:
        reference_path = materialization / "tasks" / task_id / "support" / "reference.py"
        reference_source = reference_path.read_text(encoding="utf-8")
        positive_source = reference_source + "\n# controls-v2 semantically inert planted redundancy\n"
        require(
            ast.dump(ast.parse(reference_source), include_attributes=False)
            == ast.dump(ast.parse(positive_source), include_attributes=False),
            f"positive AST changed: {task_id}",
        )
        for registry_id in REGISTRIES:
            cases, expected = expected_registry(runtime, task_id, registry_id)
            expected_by_id = {item["case_id"]: item["output"] for item in expected}
            reference_outputs = [
                {
                    "case_id": case["case_id"],
                    "output": runtime.solve(task_id, copy.deepcopy(case["payload"])),
                }
                for case in cases
            ]
            require(
                {item["case_id"]: item["output"] for item in reference_outputs}
                == expected_by_id,
                f"reference oracle mismatch: {task_id}:{registry_id}",
            )
            target_case = str(cases[0]["case_id"])
            states = [
                ("reference_positive", "Admit", True),
                ("identity_positive", "Admit", True),
                ("nonidentical_redundant_positive", "Admit", True),
                ("targeted_case_negative", "Reject", False),
                ("digest_invalid", "Invalid", None),
            ]
            for control_id, expected_class, target_value in states:
                if target_value is None:
                    case_results = None
                    digest_valid = False
                else:
                    case_results = {
                        case_id: (case_id != target_case or target_value)
                        for case_id in expected_by_id
                    }
                    digest_valid = True
                actual_class = deterministic_control_state(
                    digest_valid=digest_valid,
                    contract_results=case_results,
                )
                confusion[(expected_class, actual_class)] += 1
                cells.append(
                    {
                        "task_id": task_id,
                        "registry_id": registry_id,
                        "control_id": control_id,
                        "expected_class": expected_class,
                        "actual_class": actual_class,
                        "digest_valid": digest_valid,
                        "target_case_id": target_case if "targeted" in control_id else None,
                        "contract_results": case_results,
                        "passed": expected_class == actual_class,
                    }
                )
    require(len(cells) == 40, "deterministic control cell count changed")
    require(all(cell["passed"] for cell in cells), "deterministic controls failed")
    matrix = [
        {"expected": expected, "actual": actual, "count": count}
        for (expected, actual), count in sorted(confusion.items())
    ]
    return {
        "schema_version": "effectslice-controls-v2-deterministic-layer.v1",
        "scope": (
            "This layer validates case-level labels, targeted case binding, "
            "nonidentity, and digest Invalid handling without provider calls."
        ),
        "cells": cells,
        "confusion_matrix": matrix,
        "cell_count": len(cells),
        "all_passed": True,
    }


def manifest_files(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.name in {"manifest.json", "freeze.json"}:
            continue
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return records


def bundle_sha(files: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        canonical_json(
            {
                "schema_version": SCHEMA_VERSION,
                "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                "registered_rows": REGISTERED_ROWS,
                "files": files,
            }
        )
    )


def build(output: Path) -> dict[str, Any]:
    output = fg1.windows_extended_path(output.resolve())
    require(not output.exists(), f"Controls-v2 registration exists: {output}")
    temporary = output.with_name(output.name + ".tmp")
    require(not temporary.exists(), f"Controls-v2 temporary exists: {temporary}")
    source_verification()
    runtime = load_runtime()
    source_rows = source_f_rows()
    prompts, registry_sha = fg5.load_contract_registry(fg5.DEFAULT_CONTRACTS)
    rows: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    temporary.mkdir(parents=True)
    (temporary / "requests").mkdir()
    try:
        for task_id in ANCHOR_TASKS:
            for registry_id in REGISTRIES:
                source = source_rows[(task_id, registry_id)]
                requests, atoms = transformed_requests(source, prompts[task_id])
                cases, _ = expected_registry(runtime, task_id, registry_id)
                case_ids = [str(case["case_id"]) for case in cases]
                positive_mutation_id = f"ctrl2-pos-{task_id.lower()}-{registry_id.lower()}"
                negative_mutation_id = f"ctrl2-neg-{task_id.lower()}-{registry_id.lower()}"
                bindings.extend(
                    [
                        {
                            "mutation_id": positive_mutation_id,
                            "task_id": task_id,
                            "registry_id": registry_id,
                            "base_candidate": "F_reference",
                            "candidate": "P_redundancy_removed",
                            "target_atom_ids": [atoms["redundant_atom_id"]],
                            "removed_reverse_dependency_closure": [atoms["redundant_atom_id"]],
                            "contract_id": "semantic_equivalence",
                            "private_case_ids": case_ids,
                            "scorer_keys": [f"case_results.{case_id}.exact_match" for case_id in case_ids],
                            "expected_value": True,
                            "expected_class": "Admit",
                            "dependency_closed": True,
                        },
                        {
                            "mutation_id": negative_mutation_id,
                            "task_id": task_id,
                            "registry_id": registry_id,
                            "base_candidate": "F_reference",
                            "candidate": "N_exact_contract_removed",
                            "target_atom_ids": [atoms["exact_atom_id"]],
                            "removed_reverse_dependency_closure": [
                                atoms["exact_atom_id"],
                                atoms["redundant_atom_id"],
                            ],
                            "contract_id": "task_exact_output_contract",
                            "private_case_ids": case_ids,
                            "scorer_keys": [f"case_results.{case_id}.exact_match" for case_id in case_ids],
                            "expected_value": False,
                            "expected_class": "Reject",
                            "dependency_closed": True,
                        },
                    ]
                )
                arm_order = {
                    1: ARMS,
                    2: ARMS[1:] + ARMS[:1],
                    3: ARMS[2:] + ARMS[:2],
                }
                for repetition in REPETITIONS:
                    for order_position, arm in enumerate(arm_order[repetition], start=1):
                        execution = execution_id(
                            task_id,
                            registry_id,
                            arm,
                            repetition,
                            str(source["execution_id"]),
                        )
                        request_bytes = requests[arm]
                        fg1.atomic_write(
                            fg1.windows_extended_path(
                                temporary / "requests" / f"{execution}.json"
                            ),
                            request_bytes,
                        )
                        row = copy.deepcopy(source)
                        row.update(
                            {
                                "study_id": "EffectSlice-Controls-v2",
                                "execution_family": "controls_v2",
                                "execution_id": execution,
                                "source_fg5_execution_id": source["execution_id"],
                                "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                                "control_arm": arm,
                                "control_repetition": repetition,
                                "control_order_position": order_position,
                                "condition": "C",
                                "candidate_id": f"controls_v2_{arm}",
                                "deterministic_expected_class": (
                                    "Reject"
                                    if arm == "N_exact_contract_removed"
                                    else "Admit"
                                ),
                                "serialized_wire_request_sha256": sha256_bytes(request_bytes),
                                "final_model_visible_text_sha256": sha256_bytes(
                                    (
                                        str(fg4.visible_request_text(json.loads(request_bytes.decode("utf-8")))[1])
                                        if isinstance(fg4.visible_request_text(json.loads(request_bytes.decode("utf-8")))[1], str)
                                        else str(fg4.visible_request_text(json.loads(request_bytes.decode("utf-8")))[1]["content"])
                                    ).encode("utf-8")
                                ),
                                "api_seed_present": False,
                                "mutation_id": (
                                    positive_mutation_id
                                    if arm == "P_redundancy_removed"
                                    else negative_mutation_id
                                    if arm == "N_exact_contract_removed"
                                    else None
                                ),
                            }
                        )
                        rows.append(row)
        require(len(rows) == REGISTERED_ROWS, "Controls-v2 row count changed")
        require(len({row["execution_id"] for row in rows}) == REGISTERED_ROWS, "duplicate Controls-v2 IDs")
        require(Counter(row["control_arm"] for row in rows) == {arm: 24 for arm in ARMS}, "arm balance changed")
        atomic_json(
            temporary / "schedule.json",
            {
                "schema_version": "effectslice-controls-v2-schedule.v1",
                "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
                "output_contract_registry_sha256": registry_sha,
                "registered_rows": REGISTERED_ROWS,
                "rows": rows,
            },
        )
        atomic_json(
            temporary / "mutation_bindings.json",
            {
                "schema_version": "effectslice-controls-v2-mutation-bindings.v1",
                "binding_chain": (
                    "mutation_id -> target_atom_ids -> contract_id -> "
                    "private_case_ids -> scorer_keys -> expected_value"
                ),
                "bindings": bindings,
            },
        )
        atomic_json(temporary / "deterministic_layer.json", deterministic_layer(runtime))
        files = manifest_files(temporary)
        manifest = {
            "schema_version": "effectslice-controls-v2-manifest.v1",
            "created_at_utc": fg1.utc_now(),
            "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
            "registered_rows": REGISTERED_ROWS,
            "provider_calls_started": False,
            "frozen": False,
            "files": files,
            "bundle_sha256": bundle_sha(files),
        }
        atomic_json(temporary / "manifest.json", manifest)
        os.replace(temporary, output)
        return manifest
    except Exception:
        # Preserve the temporary directory for forensic inspection.
        raise


def verify_registration(output: Path, *, require_frozen: bool = False) -> dict[str, Any]:
    output = fg1.windows_extended_path(output.resolve())
    source_verification()
    manifest = load_json(output / "manifest.json")
    files = manifest_files(output)
    require(files == manifest["files"], "Controls-v2 file manifest changed")
    require(bundle_sha(files) == manifest["bundle_sha256"], "Controls-v2 bundle changed")
    schedule = load_json(output / "schedule.json")
    rows = schedule["rows"]
    require(len(rows) == schedule["registered_rows"] == REGISTERED_ROWS, "Controls-v2 row count changed")
    require(len({row["execution_id"] for row in rows}) == REGISTERED_ROWS, "Controls-v2 IDs changed")
    require(Counter(row["control_arm"] for row in rows) == {arm: 24 for arm in ARMS}, "Controls-v2 arm counts changed")
    by_cell: dict[tuple[str, str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        expected_class = (
            "Reject" if row["control_arm"] == "N_exact_contract_removed" else "Admit"
        )
        require(
            row.get("deterministic_expected_class") == expected_class,
            "Controls-v2 deterministic class binding changed",
        )
        path = output / "requests" / f"{row['execution_id']}.json"
        require(path.is_file(), f"missing Controls-v2 request: {row['execution_id']}")
        require(sha256_file(path) == row["serialized_wire_request_sha256"], "Controls-v2 request changed")
        value = json.loads(path.read_text(encoding="utf-8"))
        require(value.get("model") == fg1.PROVIDER_SPECS["deepseek_primary"].exact_alias, "Controls-v2 alias changed")
        require(value.get("temperature") == 0 and value.get("top_p") == 1.0, "Controls-v2 decoding changed")
        require(value.get("stream") is False and value.get("max_tokens") == 8192, "Controls-v2 request limits changed")
        require("seed" not in value, "Controls-v2 gained an API seed")
        key = (str(row["task_id"]), str(row["registry_id"]), int(row["control_repetition"]))
        by_cell[key][str(row["control_arm"])] = row
    require(len(by_cell) == 24, "Controls-v2 factorial cells changed")
    for key, arms in by_cell.items():
        require(set(arms) == set(ARMS), f"Controls-v2 arm coverage changed: {key}")
        require(
            arms["F_reference"]["serialized_wire_request_sha256"]
            == arms["F_identity"]["serialized_wire_request_sha256"],
            f"identity request mismatch: {key}",
        )
        require(
            len({arms[arm]["serialized_wire_request_sha256"] for arm in ARMS}) == 3,
            f"nonidentity request pattern changed: {key}",
        )
    binding_doc = load_json(output / "mutation_bindings.json")
    bindings = binding_doc["bindings"]
    require(len(bindings) == 16, "Controls-v2 binding count changed")
    for binding in bindings:
        for field in (
            "mutation_id",
            "target_atom_ids",
            "contract_id",
            "private_case_ids",
            "scorer_keys",
            "expected_value",
        ):
            require(field in binding, f"missing binding field: {field}")
        require(binding["dependency_closed"] is True, "control mutation is not closure-preserving")
        require(len(binding["private_case_ids"]) == len(binding["scorer_keys"]) == 64, "case/scorer binding changed")
    deterministic = load_json(output / "deterministic_layer.json")
    require(deterministic["cell_count"] == 40 and deterministic["all_passed"] is True, "deterministic controls changed")
    freeze_path = output / "freeze.json"
    frozen = freeze_path.is_file()
    require(manifest.get("frozen") is frozen, "Controls-v2 freeze state mismatch")
    if require_frozen:
        require(frozen, "Controls-v2 is not frozen")
    if frozen:
        freeze_doc = load_json(freeze_path)
        require(freeze_doc["registration_bundle_sha256"] == manifest["bundle_sha256"], "Controls-v2 freeze binding changed")
        for record in freeze_doc["source_records"]:
            path = EXPERIMENT_ROOT / record["path"]
            require(path.is_file(), f"missing frozen control source: {record['path']}")
            require(sha256_file(path) == record["sha256"], f"frozen control source changed: {record['path']}")
    return {
        "status": "passed",
        "registration_bundle_sha256": manifest["bundle_sha256"],
        "registered_rows": REGISTERED_ROWS,
        "deterministic_cells": 40,
        "binding_count": len(bindings),
        "frozen": frozen,
    }


def freeze_registration(output: Path, source_paths: list[Path]) -> dict[str, Any]:
    verified = verify_registration(output)
    output = fg1.windows_extended_path(output.resolve())
    manifest_path = output / "manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("frozen") is False, "Controls-v2 already frozen")
    records = []
    for source_path in source_paths:
        path = source_path.resolve()
        require(path.is_file(), f"missing freeze source: {path}")
        records.append(
            {
                "path": path.relative_to(EXPERIMENT_ROOT).as_posix(),
                "sha256": sha256_file(path),
            }
        )
    freeze_doc = {
        "schema_version": "effectslice-controls-v2-freeze.v1",
        "frozen_at_utc": fg1.utc_now(),
        "registration_bundle_sha256": verified["registration_bundle_sha256"],
        "source_fg5_bundle_sha256": EXPECTED_FG5_BUNDLE,
        "registered_rows": REGISTERED_ROWS,
        "provider_calls_started": False,
        "semantic_rerun_allowed": False,
        "transport_policy": {
            "timeout_seconds": fg1.TIMEOUT_SECONDS,
            "maximum_transport_attempts": fg1.MAXIMUM_TRANSPORT_ATTEMPTS,
            "retry_delays_seconds": list(fg1.RETRY_DELAYS_SECONDS),
            "retryable_http_statuses": sorted(fg1.RETRYABLE_HTTP),
        },
        "source_records": records,
    }
    atomic_json(output / "freeze.json", freeze_doc)
    manifest["frozen"] = True
    manifest["frozen_at_utc"] = freeze_doc["frozen_at_utc"]
    atomic_json(manifest_path, manifest)
    return verify_registration(output, require_frozen=True)


class ControlResolver:
    def __init__(self, registration_root: Path) -> None:
        source_doc = load_json(fg5.DEFAULT_SUCCESSOR / "global_remote_schedule.json")
        self.source_rows = {str(row["execution_id"]): row for row in source_doc["rows"]}
        self.source_resolver = fg5.OverlayResolver(
            fg5.DEFAULT_PARENT,
            fg5.DEFAULT_FG2,
            fg5.DEFAULT_FG3,
            fg5.DEFAULT_FG4,
            fg5.DEFAULT_SUCCESSOR,
        )
        self.registration_root = fg1.windows_extended_path(registration_root)

    def resolve(self, row: dict[str, Any]) -> fg1.RowInputs:
        source_id = str(row["source_fg5_execution_id"])
        require(source_id in self.source_rows, "unknown Controls-v2 source row")
        source_inputs = self.source_resolver.resolve(self.source_rows[source_id])
        request_path = self.registration_root / "requests" / f"{row['execution_id']}.json"
        request_bytes = request_path.read_bytes()
        require(sha256_bytes(request_bytes) == row["serialized_wire_request_sha256"], "Controls-v2 request changed")
        return fg1.RowInputs(
            task_dir=source_inputs.task_dir,
            request_path=request_path,
            request_bytes=request_bytes,
            payload_path=source_inputs.payload_path,
            fixture_path=source_inputs.fixture_path,
            scorer_path=source_inputs.scorer_path,
            candidate_path=source_inputs.candidate_path,
            candidate_tokens=source_inputs.candidate_tokens,
        )


def control_preflight_id(bundle_sha: str) -> str:
    return "ctrl2-preflight-" + hashlib.sha256(
        f"{SCHEMA_VERSION}|{bundle_sha}|deepseek_primary".encode("utf-8")
    ).hexdigest()[:24]


def initialize_run(registration_root: Path, run_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    bundle = load_json(registration_root / "manifest.json")["bundle_sha256"]
    expected = {
        "schema_version": "effectslice-controls-v2-run.v1",
        "registration_bundle_sha256": bundle,
        "registered_rows": REGISTERED_ROWS,
        "credential_sources": metadata,
        "credential_values_recorded": False,
        "semantic_rerun_allowed": False,
    }
    path = run_dir / "run_manifest.json"
    if path.exists():
        current = load_json(path)
        for key, value in expected.items():
            require(current.get(key) == value, f"Controls-v2 run manifest changed: {key}")
        return current
    value = {**expected, "created_at_utc": fg1.utc_now(), "provider_calls_started": False}
    atomic_json(path, value)
    return value


def run_preflight(registration_root: Path, run_dir: Path, docs_dir: Path) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    run_dir = fg1.windows_extended_path(run_dir)
    verified = verify_registration(registration_root, require_frozen=True)
    credentials, metadata = fg1.load_credentials(docs_dir.resolve())
    manifest = initialize_run(registration_root, run_dir, metadata)
    final_path = run_dir / "preflight" / "deepseek_primary.json"
    started_path = run_dir / "preflight" / "deepseek_primary.started.json"
    if final_path.exists():
        return load_json(final_path)
    require(not started_path.exists(), "ambiguous Controls-v2 preflight cannot be replayed")
    request_id = control_preflight_id(verified["registration_bundle_sha256"])
    atomic_json(
        started_path,
        {
            "schema_version": "effectslice-controls-v2-preflight-start.v1",
            "transport_request_id": request_id,
            "started_at_utc": fg1.utc_now(),
            "semantic_rerun_allowed": False,
        },
    )
    manifest["provider_calls_started"] = True
    manifest["provider_calls_started_at_utc"] = fg1.utc_now()
    atomic_json(run_dir / "run_manifest.json", manifest)
    spec = fg1.PROVIDER_SPECS["deepseek_primary"]
    dispatch = fg1.dispatch_request(
        spec,
        credentials["deepseek_primary"],
        request_id,
        fg1.preflight_request(spec),
    )
    fg1.persist_attempts(run_dir / "preflight", "preflight-deepseek_primary", dispatch, (credentials["deepseek_primary"],))
    if dispatch.terminal_body is not None:
        raw_path = run_dir / "preflight" / "raw" / "deepseek_primary.json"
        fg1.atomic_write(raw_path, dispatch.terminal_body)
        raw_relative = "preflight/raw/deepseek_primary.json"
        raw_sha = sha256_bytes(dispatch.terminal_body)
    else:
        raw_relative = None
        raw_sha = None
    status, reason = fg1.preflight_status_from_dispatch(
        fg5.DEFAULT_PARENT, "deepseek_primary", dispatch
    )
    result = {
        "schema_version": "effectslice-controls-v2-preflight.v1",
        "model_slot_id": "deepseek_primary",
        "exact_alias": spec.exact_alias,
        "transport_request_id": request_id,
        "status": status,
        "reason": reason,
        "logical_request_count": 1,
        "transport_attempt_count": len(dispatch.attempts),
        "raw_response_path": raw_relative,
        "raw_response_sha256": raw_sha,
        "credential_value_recorded": False,
        "completed_at_utc": fg1.utc_now(),
    }
    atomic_json(final_path, result)
    return result


def progress(registration_root: Path, run_dir: Path) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    run_dir = fg1.windows_extended_path(run_dir)
    rows = load_json(registration_root / "schedule.json")["rows"]
    outcomes: Counter[str] = Counter()
    completed = 0
    for row in rows:
        path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not path.exists():
            continue
        value = load_json(path)
        fg1.validate_result_row(fg5.DEFAULT_PARENT, value, "deepseek_primary")
        require(value.get("control_arm") == row["control_arm"], "control arm result changed")
        completed += 1
        outcomes[str(value["terminal_outcome"])] += 1
    return {
        "schema_version": "effectslice-controls-v2-progress.v1",
        "updated_at_utc": fg1.utc_now(),
        "registered_rows": REGISTERED_ROWS,
        "terminal_rows": completed,
        "remaining_rows": REGISTERED_ROWS - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
    }


@contextlib.contextmanager
def run_lock(run_dir: Path) -> Iterator[None]:
    path = run_dir / "run.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ControlsError(f"another Controls-v2 runner may be active: {path}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.close(descriptor)
        yield
    finally:
        path.unlink(missing_ok=True)


def run_rows(
    registration_root: Path,
    run_dir: Path,
    docs_dir: Path,
    *,
    workers: int,
) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    run_dir = fg1.windows_extended_path(run_dir)
    verify_registration(registration_root, require_frozen=True)
    require(1 <= workers <= 3, "Controls-v2 workers must be between 1 and 3")
    credentials, metadata = fg1.load_credentials(docs_dir.resolve())
    manifest = initialize_run(registration_root, run_dir, metadata)
    preflight = load_json(run_dir / "preflight" / "deepseek_primary.json")
    rows = load_json(registration_root / "schedule.json")["rows"]
    resolver = ControlResolver(registration_root)
    pending: list[tuple[dict[str, Any], fg1.RowInputs]] = []
    for row in rows:
        execution = str(row["execution_id"])
        row_path = run_dir / "rows" / f"{execution}.json"
        started = run_dir / "dispatch" / f"{execution}.started.json"
        terminal = run_dir / "dispatch" / f"{execution}.terminal.json"
        if row_path.exists():
            value = load_json(row_path)
            fg1.validate_result_row(fg5.DEFAULT_PARENT, value, "deepseek_primary")
            if started.exists() and not terminal.exists():
                atomic_json(
                    terminal,
                    {
                        "schema_version": "effectslice-controls-v2-dispatch-terminal.v1",
                        "execution_id": execution,
                        "terminal_outcome": value["terminal_outcome"],
                        "result_row_sha256": sha256_file(row_path),
                        "recovered_from_terminal_row": True,
                    },
                )
            continue
        require(not started.exists(), f"ambiguous Controls-v2 row cannot be replayed: {execution}")
        pending.append((row, resolver.resolve(row)))

    def execute(item: tuple[dict[str, Any], fg1.RowInputs]) -> str:
        row, inputs = item
        execution = str(row["execution_id"])
        started = run_dir / "dispatch" / f"{execution}.started.json"
        terminal = run_dir / "dispatch" / f"{execution}.terminal.json"
        row_path = run_dir / "rows" / f"{execution}.json"
        atomic_json(
            started,
            {
                "schema_version": "effectslice-controls-v2-dispatch-start.v1",
                "execution_id": execution,
                "control_arm": row["control_arm"],
                "serialized_wire_request_sha256": row["serialized_wire_request_sha256"],
                "transport_request_id": execution,
                "started_at_utc": fg1.utc_now(),
                "semantic_rerun_allowed": False,
            },
        )
        if preflight["status"] != "available":
            result = fg1.unavailable_row(row, inputs)
        else:
            result = fg1.execute_row(
                fg5.DEFAULT_PARENT,
                run_dir,
                row,
                inputs,
                credentials["deepseek_primary"],
            )
        result["control_arm"] = row["control_arm"]
        result["control_repetition"] = row["control_repetition"]
        result["mutation_id"] = row["mutation_id"]
        result["source_fg5_execution_id"] = row["source_fg5_execution_id"]
        result["transport_request_id"] = execution
        result["preflight_status"] = preflight["status"]
        fg1.write_row(run_dir, row, result, fg5.DEFAULT_PARENT)
        atomic_json(
            terminal,
            {
                "schema_version": "effectslice-controls-v2-dispatch-terminal.v1",
                "execution_id": execution,
                "terminal_outcome": result["terminal_outcome"],
                "result_row_sha256": sha256_file(row_path),
                "recovered_from_terminal_row": False,
            },
        )
        return execution

    completed = 0
    errors: list[tuple[str, BaseException]] = []
    with run_lock(run_dir):
        if pending:
            manifest["provider_calls_started"] = True
            manifest.setdefault("provider_calls_started_at_utc", fg1.utc_now())
            atomic_json(run_dir / "run_manifest.json", manifest)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures: dict[Future[str], tuple[dict[str, Any], fg1.RowInputs]] = {
                executor.submit(execute, item): item for item in pending
            }
            for future in as_completed(futures):
                row, _ = futures[future]
                try:
                    execution = future.result()
                except BaseException as exc:
                    errors.append((str(row["execution_id"]), exc))
                    continue
                completed += 1
                if completed % 4 == 0:
                    current = progress(registration_root, run_dir)
                    atomic_json(run_dir / "progress.json", current)
                    print(f"controls_terminal_rows={current['terminal_rows']}/{REGISTERED_ROWS} last={execution}", flush=True)
        current = progress(registration_root, run_dir)
        current["new_rows_this_invocation"] = completed
        current["workers"] = workers
        atomic_json(run_dir / "progress.json", current)
        require(
            not errors,
            "Controls-v2 execution raised after preserving other rows: "
            + "; ".join(f"{execution}: {type(exc).__name__}: {exc}" for execution, exc in errors),
        )
    return progress(registration_root, run_dir)


def verify_run(registration_root: Path, run_dir: Path, *, require_complete: bool) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    run_dir = fg1.windows_extended_path(run_dir)
    verified = verify_registration(registration_root, require_frozen=True)
    current = progress(registration_root, run_dir)
    if require_complete:
        require(current["terminal_rows"] == REGISTERED_ROWS, "Controls-v2 run incomplete")
    return {
        "status": "passed",
        "registration_bundle_sha256": verified["registration_bundle_sha256"],
        "require_complete": require_complete,
        "progress": current,
    }


def analysis(registration_root: Path, run_dir: Path, output: Path) -> dict[str, Any]:
    registration_root = fg1.windows_extended_path(registration_root)
    run_dir = fg1.windows_extended_path(run_dir)
    output = fg1.windows_extended_path(output)
    verify_run(registration_root, run_dir, require_complete=True)
    runtime = load_runtime()
    rows = load_json(registration_root / "schedule.json")["rows"]
    row_results: list[dict[str, Any]] = []
    for row in rows:
        execution = str(row["execution_id"])
        result = load_json(run_dir / "rows" / f"{execution}.json")
        record: dict[str, Any] = {
            "execution_id": execution,
            "task_id": row["task_id"],
            "registry_id": row["registry_id"],
            "control_arm": row["control_arm"],
            "control_repetition": row["control_repetition"],
            "deterministic_expected_class": row["deterministic_expected_class"],
            "row_valid": result["row_valid"],
            "terminal_outcome": result["terminal_outcome"],
            "condition_success": result["condition_success"],
            "private_score": result["private_score"],
            "target_case_failure_count": None,
            "case_results_available": False,
        }
        record["model_behavior_matches_registered_direction"] = (
            result["row_valid"] is True
            and (
                result["condition_success"] is False
                if row["deterministic_expected_class"] == "Reject"
                else result["condition_success"] is True
            )
        )
        scoring_path = run_dir / "scoring" / f"{execution}.json.gz"
        if scoring_path.is_file():
            with gzip.open(scoring_path, "rt", encoding="utf-8") as handle:
                evidence = json.load(handle)
            _, expected = expected_registry(runtime, str(row["task_id"]), str(row["registry_id"]))
            expected_by_id = {item["case_id"]: item["output"] for item in expected}
            supplied = {item["case_id"]: item["output"] for item in evidence["outputs"]}
            case_results = {
                case_id: supplied.get(case_id) == value
                for case_id, value in expected_by_id.items()
            }
            record["case_results_available"] = True
            record["case_pass_count"] = sum(case_results.values())
            record["case_count"] = len(case_results)
            if row["control_arm"] == "N_exact_contract_removed":
                record["target_case_failure_count"] = sum(not value for value in case_results.values())
        row_results.append(record)

    arm_summary: list[dict[str, Any]] = []
    for arm in ARMS:
        subset = [row for row in row_results if row["control_arm"] == arm]
        valid = [row for row in subset if row["row_valid"]]
        arm_summary.append(
            {
                "control_arm": arm,
                "registered_rows": len(subset),
                "valid_rows": len(valid),
                "operational_successes": sum(row["condition_success"] is True for row in subset),
                "success_rate_itt": sum(row["condition_success"] is True for row in subset) / len(subset),
                "registered_direction_matches": sum(
                    row["model_behavior_matches_registered_direction"] is True
                    for row in subset
                ),
                "registered_direction_match_rate_itt": sum(
                    row["model_behavior_matches_registered_direction"] is True
                    for row in subset
                )
                / len(subset),
                "mean_private_score_valid": (
                    sum(float(row["private_score"]) for row in valid) / len(valid)
                    if valid
                    else None
                ),
                "technical_invalid_rows": len(subset) - len(valid),
            }
        )
    repeatability: list[dict[str, Any]] = []
    for task_id in ANCHOR_TASKS:
        for registry_id in REGISTRIES:
            for arm in ARMS:
                subset = [
                    row for row in row_results
                    if row["task_id"] == task_id
                    and row["registry_id"] == registry_id
                    and row["control_arm"] == arm
                ]
                require(len(subset) == 3, "Controls-v2 repeatability cell changed")
                states = [row["condition_success"] for row in subset]
                repeatability.append(
                    {
                        "task_id": task_id,
                        "registry_id": registry_id,
                        "control_arm": arm,
                        "all_three_terminal_states_equal": len(set(map(str, states))) == 1,
                        "success_count": sum(value is True for value in states),
                    }
                )
    deterministic = load_json(registration_root / "deterministic_layer.json")
    value = {
        "schema_version": "effectslice-controls-v2-analysis.v1",
        "registered_rows": REGISTERED_ROWS,
        "deterministic_layer": {
            "cell_count": deterministic["cell_count"],
            "all_passed": deterministic["all_passed"],
            "confusion_matrix": deterministic["confusion_matrix"],
        },
        "model_layer_scope": (
            "Model-mediated rows report retention, targeted omission response, and "
            "repeatability. They do not redefine deterministic ground-truth labels."
        ),
        "arm_summary": arm_summary,
        "repeatability": repeatability,
        "row_results": row_results,
    }
    atomic_json(output / "analysis.json", value)
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("build", "verify-registration", "freeze", "preflight", "run", "verify-run", "analyze"),
    )
    parser.add_argument("--registration", type=Path, default=DEFAULT_REGISTRATION)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--freeze-source", type=Path, action="append", default=[])
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        value = build(args.registration)
    elif args.command == "verify-registration":
        value = verify_registration(args.registration)
    elif args.command == "freeze":
        require(args.freeze_source, "freeze requires --freeze-source")
        value = freeze_registration(args.registration, args.freeze_source)
    elif args.command == "preflight":
        require(args.docs_dir is not None, "preflight requires --docs-dir")
        value = run_preflight(args.registration, args.run_dir, args.docs_dir)
    elif args.command == "run":
        require(args.docs_dir is not None, "run requires --docs-dir")
        value = run_rows(args.registration, args.run_dir, args.docs_dir, workers=args.workers)
    elif args.command == "verify-run":
        value = verify_run(args.registration, args.run_dir, require_complete=args.require_complete)
    else:
        value = analysis(args.registration, args.run_dir, args.output)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ControlsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
