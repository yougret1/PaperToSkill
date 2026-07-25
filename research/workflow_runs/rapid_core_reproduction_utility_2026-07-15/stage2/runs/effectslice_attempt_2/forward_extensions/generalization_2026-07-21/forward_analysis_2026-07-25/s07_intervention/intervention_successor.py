from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from importlib import metadata
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ANALYSIS_ROOT = HERE.parent
GENERALIZATION_ROOT = ANALYSIS_ROOT.parent
MATERIALIZATION = GENERALIZATION_ROOT / "materialization_remote_only_2026-07-23"
FG5_SUCCESSOR = GENERALIZATION_ROOT / "output_contract_successor_2026-07-24"
REGISTRATION = HERE / "registration"
MAGIC_LINE = "EFFECTSLICE_MODEL_VISIBLE_PAYLOAD_V1\n"

TASK_SPECS = (
    {
        "task_id": "NLP-LLM-01",
        "domain": "nlp",
        "critical_hard_contract_ids": ("no_input_mutation", "stable_tie_break"),
    },
    {
        "task_id": "SE-PE-01",
        "domain": "software_engineering",
        "critical_hard_contract_ids": ("stable_ties",),
    },
    {
        "task_id": "DATA-HDB-01",
        "domain": "data_analysis",
        "critical_hard_contract_ids": ("stable_edge_ties",),
    },
    {
        "task_id": "AGENT-TF-01",
        "domain": "agent_tool_use",
        "critical_hard_contract_ids": ("stable_order",),
    },
)

ARM_ORDER = (
    "F",
    "S",
    "F_drop_critical",
    "F_drop_noncritical",
    "S_restore_critical",
    "S_restore_noncritical",
)

ARM_ROLES = {
    "F": "full_information_baseline",
    "S": "registered_slice_baseline",
    "F_drop_critical": "critical_atom_necessity",
    "F_drop_noncritical": "noncritical_comparator_necessity",
    "S_restore_critical": "critical_atom_rescue",
    "S_restore_noncritical": "noncritical_comparator_rescue",
}

SOURCE_BLOCKS = {"A": 1, "B": 4}


class RegistrationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RegistrationError(message)


def extended(path: Path) -> Path:
    resolved = path.resolve()
    if os.name == "nt" and not str(resolved).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(resolved))
    return resolved


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with extended(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(extended(path).read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    extended(path.parent).mkdir(parents=True, exist_ok=True)
    extended(path).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_bytes(path: Path, value: bytes) -> None:
    extended(path.parent).mkdir(parents=True, exist_ok=True)
    extended(path).write_bytes(value)


def portable(path: Path) -> str:
    return path.resolve().relative_to(HERE.resolve()).as_posix()


def materialization_portable(path: Path) -> str:
    return path.resolve().relative_to(MATERIALIZATION.resolve()).as_posix()


def fg5_portable(path: Path) -> str:
    return path.resolve().relative_to(GENERALIZATION_ROOT.resolve()).as_posix()


def token_encoder() -> Any:
    import tiktoken

    require(metadata.version("tiktoken") == "0.12.0", "tiktoken version drift")
    return tiktoken.get_encoding("cl100k_base")


def render_subset(
    atom_ids: list[str], atom_order: list[str], text_by_id: dict[str, str]
) -> bytes:
    selected = set(atom_ids)
    return "\n\n".join(
        text_by_id[atom_id] for atom_id in atom_order if atom_id in selected
    ).encode("utf-8")


def dependency_closed(
    atom_ids: list[str], dependencies: dict[str, set[str]]
) -> bool:
    selected = set(atom_ids)
    return all(dependencies[atom_id].issubset(selected) for atom_id in atom_ids)


def compose_model_visible_payload(
    task_scaffold: bytes, fixture_payload: bytes, candidate_artifact: bytes
) -> bytes:
    payload = bytearray(MAGIC_LINE.encode("ascii"))
    for label, value in (
        ("task_scaffold", task_scaffold),
        ("fixture_payload", fixture_payload),
        ("candidate_artifact", candidate_artifact),
    ):
        payload.extend(f"{label}:{len(value)}\n".encode("ascii"))
        payload.extend(value)
        payload.extend(b"\n")
    return bytes(payload)


def message_content(request: dict[str, Any]) -> str:
    messages = request.get("messages")
    require(
        isinstance(messages, list) and len(messages) == 1,
        "request must contain exactly one message",
    )
    message = messages[0]
    require(
        isinstance(message, dict) and message.get("role") == "user",
        "request message must be a user message",
    )
    content = message.get("content")
    require(isinstance(content, str), "request content must be a string")
    return content


def validate_request(request_bytes: bytes) -> dict[str, Any]:
    request = json.loads(request_bytes.decode("utf-8", errors="strict"))
    require(isinstance(request, dict), "request must be a JSON object")
    require(request.get("model") == "deepseek-v4-flash", "model alias drift")
    require(request.get("temperature") == 0, "temperature drift")
    require(request.get("top_p") == 1.0, "top_p drift")
    require(request.get("stream") is False, "streaming must be disabled")
    require(request.get("max_tokens") == 8192, "output budget drift")
    require("seed" not in request, "unregistered API seed field is present")
    message_content(request)
    return request


def canonical_request(request: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            request,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def build_task_design(spec: dict[str, Any], encoder: Any) -> dict[str, Any]:
    task_id = str(spec["task_id"])
    task_dir = MATERIALIZATION / "tasks" / task_id
    atom_registry_path = task_dir / "atom_registry.json"
    atom_dag_path = task_dir / "atom_dag.json"
    candidate_manifest_path = task_dir / "candidate_manifest.json"
    scorer_manifest_path = task_dir / "scorer_manifest.json"
    for path in (
        atom_registry_path,
        atom_dag_path,
        candidate_manifest_path,
        scorer_manifest_path,
    ):
        require(extended(path).is_file(), f"missing frozen task input: {path}")

    atom_registry = load_json(atom_registry_path)
    atom_dag = load_json(atom_dag_path)
    candidate_manifest = load_json(candidate_manifest_path)
    scorer_manifest = load_json(scorer_manifest_path)
    atoms = atom_registry["atoms"]
    require(len(atoms) == 12, f"{task_id} atom count is not 12")
    atom_order = [str(atom["atom_id"]) for atom in atoms]
    text_by_id = {
        str(atom["atom_id"]): str(atom["rendered_text"]) for atom in atoms
    }
    dag_rows = atom_dag["atoms"]
    require(
        [str(row["atom_id"]) for row in dag_rows] == atom_order,
        f"{task_id} DAG order differs from atom registry",
    )
    dependencies = {
        str(row["atom_id"]): {str(value) for value in row["dependency_ids"]}
        for row in dag_rows
    }
    for index, atom_id in enumerate(atom_order):
        expected = set() if index == 0 else {atom_order[index - 1]}
        require(
            dependencies[atom_id] == expected,
            f"{task_id} is no longer the registered 12-atom chain",
        )

    candidates = {
        str(row["candidate_id"]): row
        for row in candidate_manifest["candidates"]
    }
    require(
        "F" in candidates and "S_dag_ratio_60_v1" in candidates,
        f"{task_id} missing F/S",
    )
    full_ids = [str(value) for value in candidates["F"]["atom_ids"]]
    slice_ids = [
        str(value) for value in candidates["S_dag_ratio_60_v1"]["atom_ids"]
    ]
    require(full_ids == atom_order, f"{task_id} F is not the full atom order")
    require(
        slice_ids == atom_order[:8],
        f"{task_id} S is not the frozen 8/12 prefix",
    )
    require(
        render_subset(full_ids, atom_order, text_by_id)
        == extended(task_dir / candidates["F"]["artifact_path"]).read_bytes(),
        f"{task_id} rendered F differs from frozen F",
    )
    require(
        render_subset(slice_ids, atom_order, text_by_id)
        == extended(
            task_dir / candidates["S_dag_ratio_60_v1"]["artifact_path"]
        ).read_bytes(),
        f"{task_id} rendered S differs from frozen S",
    )

    noncritical_id = atom_order[8]
    critical_id = atom_order[10]
    require(
        text_by_id[noncritical_id].startswith(
            "Use only quantities present in the case payload."
        ),
        f"{task_id} noncritical comparator text drift",
    )
    require(
        text_by_id[critical_id].startswith("Do not mutate the input."),
        f"{task_id} critical atom text drift",
    )
    hard_contract_ids = {
        str(value) for value in scorer_manifest["hard_contract_ids"]
    }
    critical_targets = {
        str(value) for value in spec["critical_hard_contract_ids"]
    }
    require(
        critical_targets.issubset(hard_contract_ids),
        f"{task_id} critical atom is not bound to the registered hard contracts",
    )
    require(
        not any(
            value in text_by_id[noncritical_id] for value in hard_contract_ids
        ),
        f"{task_id} comparator unexpectedly names a registered hard contract",
    )

    slice_set = set(slice_ids)
    arms = {
        "F": full_ids,
        "S": slice_ids,
        "F_drop_critical": [
            value for value in full_ids if value != critical_id
        ],
        "F_drop_noncritical": [
            value for value in full_ids if value != noncritical_id
        ],
        "S_restore_critical": [
            value for value in full_ids if value in slice_set | {critical_id}
        ],
        "S_restore_noncritical": [
            value for value in full_ids if value in slice_set | {noncritical_id}
        ],
    }
    require(tuple(arms) == ARM_ORDER, f"{task_id} arm order drift")
    require(
        len({tuple(value) for value in arms.values()}) == 6,
        f"{task_id} arms are not unique",
    )

    full_tokens = len(
        encoder.encode(
            render_subset(full_ids, atom_order, text_by_id).decode("utf-8")
        )
    )
    arm_rows: list[dict[str, Any]] = []
    for arm_id in ARM_ORDER:
        atom_ids = arms[arm_id]
        artifact = render_subset(atom_ids, atom_order, text_by_id)
        artifact_path = (
            REGISTRATION / "candidates" / task_id / f"{arm_id}.txt"
        )
        write_bytes(artifact_path, artifact)
        tokens = len(encoder.encode(artifact.decode("utf-8")))
        arm_rows.append(
            {
                "arm_id": arm_id,
                "contrast_role": ARM_ROLES[arm_id],
                "atom_ids": atom_ids,
                "artifact_path": portable(artifact_path),
                "artifact_sha256": sha256_bytes(artifact),
                "artifact_bytes": len(artifact),
                "rendered_token_count": tokens,
                "retained_token_ratio": round(tokens / full_tokens, 12),
                "dependency_closed": dependency_closed(atom_ids, dependencies),
                "singleton_intervention": arm_id not in {"F", "S"},
            }
        )

    return {
        "task_id": task_id,
        "domain": spec["domain"],
        "source_hashes": {
            "atom_registry.json": sha256_file(atom_registry_path),
            "atom_dag.json": sha256_file(atom_dag_path),
            "candidate_manifest.json": sha256_file(candidate_manifest_path),
            "scorer_manifest.json": sha256_file(scorer_manifest_path),
        },
        "atom_count": len(atom_order),
        "registered_slice_atom_count": len(slice_ids),
        "critical_atom": {
            "atom_id": critical_id,
            "index": 10,
            "rendered_text": text_by_id[critical_id],
            "rendered_text_sha256": sha256_bytes(
                text_by_id[critical_id].encode("utf-8")
            ),
            "direct_hard_contract_ids": sorted(critical_targets),
            "selection_basis": (
                "direct operational rule for registered mutation/tie-order hard contracts"
            ),
        },
        "noncritical_comparator_atom": {
            "atom_id": noncritical_id,
            "index": 8,
            "rendered_text": text_by_id[noncritical_id],
            "rendered_text_sha256": sha256_bytes(
                text_by_id[noncritical_id].encode("utf-8")
            ),
            "direct_hard_contract_ids": [],
            "selection_basis": (
                "registered execution-boundary constraint with no direct scorer "
                "hard-contract identifier"
            ),
        },
        "hard_contract_ids": sorted(hard_contract_ids),
        "chain_constraint": {
            "all_atoms_form_one_chain": True,
            "singleton_deletions_may_break_dependency_closure": True,
            "interpretation": (
                "closure-breaking arms are deliberate singleton causal interventions, "
                "not reducer outputs"
            ),
        },
        "arms": arm_rows,
    }


def select_source_row(
    fg5_rows: list[dict[str, Any]], task_id: str, registry_id: str
) -> dict[str, Any]:
    selected = [
        row
        for row in fg5_rows
        if row.get("task_id") == task_id
        and row.get("registry_id") == registry_id
        and int(row.get("block_id")) == SOURCE_BLOCKS[registry_id]
        and row.get("condition") == "F"
        and row.get("candidate_id") == "F"
        and row.get("variant_id") == "primary_dag_ratio_60_v1"
        and row.get("execution_family") == "primary"
        and row.get("model_slot_id") == "deepseek_primary"
    ]
    require(
        len(selected) == 1,
        f"expected one FG5 DeepSeek F source for {task_id}/{registry_id}, got {len(selected)}",
    )
    return selected[0]


def build_registration() -> dict[str, Any]:
    run_dir = HERE / "run"
    if extended(run_dir).exists() and any(extended(run_dir).rglob("*.json")):
        raise RegistrationError(
            "provider execution already exists; registration is immutable"
        )
    if extended(REGISTRATION / "manifest.json").exists():
        raise RegistrationError("frozen registration already exists; use verify")

    encoder = token_encoder()
    fg5_schedule_path = FG5_SUCCESSOR / "global_remote_schedule.json"
    fg5_manifest_path = FG5_SUCCESSOR / "successor_manifest.json"
    fg5_rows = load_json(fg5_schedule_path)["rows"]
    task_designs = [
        build_task_design(dict(spec), encoder) for spec in TASK_SPECS
    ]
    design_by_task = {row["task_id"]: row for row in task_designs}

    schedule: list[dict[str, Any]] = []
    for spec in TASK_SPECS:
        task_id = str(spec["task_id"])
        design = design_by_task[task_id]
        task_dir = MATERIALIZATION / "tasks" / task_id
        task_scaffold_path = task_dir / "task_scaffold.md"
        scorer_path = task_dir / "support" / "scorer.py"
        task_scaffold = extended(task_scaffold_path).read_bytes()
        arms = {row["arm_id"]: row for row in design["arms"]}

        for registry_id in ("A", "B"):
            fixture_path = task_dir / "fixtures" / f"{registry_id}.json"
            fixture = extended(fixture_path).read_bytes()
            source = select_source_row(fg5_rows, task_id, registry_id)
            source_request_path = (
                FG5_SUCCESSOR / "requests" / f"{source['execution_id']}.json"
            )
            source_request_bytes = extended(source_request_path).read_bytes()
            require(
                sha256_bytes(source_request_bytes)
                == source["serialized_wire_request_sha256"],
                f"FG5 source request hash mismatch: {task_id}/{registry_id}",
            )
            source_request = validate_request(source_request_bytes)
            source_content = message_content(source_request)
            require(
                source_content.count(MAGIC_LINE) == 1,
                f"FG5 source payload marker mismatch: {task_id}/{registry_id}",
            )
            prefix = source_content[: source_content.index(MAGIC_LINE)]
            require(
                "[EXPLICIT CASE INTERFACE]" in prefix
                and "[EXACT OUTPUT CONTRACT]" in prefix
                and "[STRICT SUBMISSION ENVELOPE]" in prefix,
                f"corrected protocol prefix incomplete: {task_id}/{registry_id}",
            )

            for arm_id in ARM_ORDER:
                arm = arms[arm_id]
                candidate_path = HERE / arm["artifact_path"]
                candidate = extended(candidate_path).read_bytes()
                canonical_payload = compose_model_visible_payload(
                    task_scaffold, fixture, candidate
                )
                full_content = (
                    prefix
                    + canonical_payload.decode("utf-8", errors="strict")
                )
                request = copy.deepcopy(source_request)
                request["messages"][0]["content"] = full_content
                request_bytes = canonical_request(request)
                validate_request(request_bytes)
                stem = (
                    f"{task_id.lower().replace('-', '_')}_"
                    f"{registry_id.lower()}_{arm_id.lower()}"
                )
                request_path = REGISTRATION / "requests" / f"{stem}.json"
                payload_path = REGISTRATION / "payloads" / f"{stem}.txt"
                write_bytes(request_path, request_bytes)
                write_bytes(payload_path, full_content.encode("utf-8"))
                request_sha = sha256_bytes(request_bytes)
                suffix = sha256_bytes(
                    f"s07|{task_id}|{registry_id}|{arm_id}|{request_sha}".encode(
                        "utf-8"
                    )
                )[:16]
                execution_id = (
                    f"s07-{task_id.lower()}-{registry_id.lower()}-"
                    f"{arm_id.lower().replace('_', '-')}-{suffix}"
                )
                schedule.append(
                    {
                        "execution_id": execution_id,
                        "task_id": task_id,
                        "domain": spec["domain"],
                        "registry_id": registry_id,
                        "source_block_id": SOURCE_BLOCKS[registry_id],
                        "arm_id": arm_id,
                        "condition": arm_id,
                        "candidate_id": f"s07_{arm_id}",
                        "contrast_role": ARM_ROLES[arm_id],
                        "model_slot_id": "deepseek_primary",
                        "model_alias": "deepseek-v4-flash",
                        "temperature": 0,
                        "top_p": 1.0,
                        "api_seed_present": False,
                        "request_file": portable(request_path),
                        "request_sha256": request_sha,
                        "payload_file": portable(payload_path),
                        "payload_sha256": sha256_bytes(
                            full_content.encode("utf-8")
                        ),
                        "canonical_payload_sha256": sha256_bytes(
                            canonical_payload
                        ),
                        "candidate_path": arm["artifact_path"],
                        "candidate_sha256": arm["artifact_sha256"],
                        "candidate_bytes": arm["artifact_bytes"],
                        "candidate_tokens": arm["rendered_token_count"],
                        "candidate_atom_ids": arm["atom_ids"],
                        "dependency_closed": arm["dependency_closed"],
                        "task_scaffold_path": materialization_portable(
                            task_scaffold_path
                        ),
                        "task_scaffold_sha256": sha256_file(task_scaffold_path),
                        "fixture_path": materialization_portable(fixture_path),
                        "fixture_sha256": sha256_file(fixture_path),
                        "scorer_path": materialization_portable(scorer_path),
                        "scorer_sha256": sha256_file(scorer_path),
                        "critical_atom_id": design["critical_atom"]["atom_id"],
                        "noncritical_atom_id": design[
                            "noncritical_comparator_atom"
                        ]["atom_id"],
                        "hard_contract_ids": design["hard_contract_ids"],
                        "source_fg5_execution_id": source["execution_id"],
                        "source_fg5_request_path": fg5_portable(
                            source_request_path
                        ),
                        "source_fg5_request_sha256": sha256_file(
                            source_request_path
                        ),
                    }
                )

    for row in schedule:
        row["order_key"] = sha256_bytes(
            (
                "effectslice-s07-order-v1|"
                + row["task_id"]
                + "|"
                + row["registry_id"]
                + "|"
                + row["arm_id"]
            ).encode("utf-8")
        )
    schedule.sort(key=lambda row: (row["order_key"], row["execution_id"]))
    for index, row in enumerate(schedule, start=1):
        row["execution_order"] = index

    registry_doc = {
        "schema_version": "effectslice-s07-atom-intervention-registry.v1",
        "status": "frozen_before_provider_calls",
        "purpose": (
            "four-domain singleton atom necessity and rescue intervention"
        ),
        "scope": {
            "tasks": 4,
            "domains": 4,
            "registries_per_task": 2,
            "arms_per_task_registry": 6,
            "provider_calls": 48,
            "model_slot_id": "deepseek_primary",
        },
        "design": {
            "necessity_contrasts": [
                "F_vs_F_drop_critical",
                "F_vs_F_drop_noncritical",
            ],
            "rescue_contrasts": [
                "S_restore_critical_vs_S",
                "S_restore_noncritical_vs_S",
            ],
            "closure_policy": (
                "F and S retain registered closure. Singleton causal edits are "
                "allowed to break the chain closure and are never described as "
                "reducer outputs."
            ),
            "technical_retry_policy": (
                "up to five transport attempts; never replay a completed semantic response"
            ),
            "randomization": (
                "deterministic SHA-256 ordering over task, registry, and arm"
            ),
            "api_seed": (
                "unsupported by the registered DeepSeek route; temperature=0 and top_p=1"
            ),
        },
        "frozen_inputs": {
            "materialization_manifest_sha256": sha256_file(
                MATERIALIZATION / "immutable_file_manifest.json"
            ),
            "fg5_schedule_sha256": sha256_file(fg5_schedule_path),
            "fg5_successor_manifest_sha256": sha256_file(fg5_manifest_path),
        },
        "tasks": task_designs,
    }
    schedule_doc = {
        "schema_version": "effectslice-s07-atom-intervention-schedule.v1",
        "status": "frozen_before_provider_calls",
        "rows": schedule,
    }
    write_json(REGISTRATION / "registry.json", registry_doc)
    write_json(REGISTRATION / "schedule.json", schedule_doc)

    tracked = [
        REGISTRATION / "registry.json",
        REGISTRATION / "schedule.json",
    ]
    tracked.extend(sorted((REGISTRATION / "candidates").rglob("*.txt")))
    tracked.extend(sorted((REGISTRATION / "payloads").glob("*.txt")))
    tracked.extend(sorted((REGISTRATION / "requests").glob("*.json")))
    manifest = {
        "schema_version": (
            "effectslice-s07-atom-intervention-freeze-manifest.v1"
        ),
        "status": "frozen_before_provider_calls",
        "source_materialization_manifest_sha256": sha256_file(
            MATERIALIZATION / "immutable_file_manifest.json"
        ),
        "source_fg5_schedule_sha256": sha256_file(fg5_schedule_path),
        "source_fg5_successor_manifest_sha256": sha256_file(fg5_manifest_path),
        "files": {portable(path): sha256_file(path) for path in tracked},
    }
    write_json(REGISTRATION / "manifest.json", manifest)
    return manifest


def verify_registration() -> dict[str, Any]:
    manifest = load_json(REGISTRATION / "manifest.json")
    require(
        manifest["status"] == "frozen_before_provider_calls",
        "registration is not frozen",
    )
    require(
        manifest["source_materialization_manifest_sha256"]
        == sha256_file(MATERIALIZATION / "immutable_file_manifest.json"),
        "materialization source changed",
    )
    require(
        manifest["source_fg5_schedule_sha256"]
        == sha256_file(FG5_SUCCESSOR / "global_remote_schedule.json"),
        "FG5 schedule changed",
    )
    require(
        manifest["source_fg5_successor_manifest_sha256"]
        == sha256_file(FG5_SUCCESSOR / "successor_manifest.json"),
        "FG5 successor manifest changed",
    )
    for name, expected in manifest["files"].items():
        path = HERE / name
        require(extended(path).is_file(), f"missing frozen file: {name}")
        require(
            sha256_file(path) == expected,
            f"frozen file hash mismatch: {name}",
        )

    registry = load_json(REGISTRATION / "registry.json")
    schedule = load_json(REGISTRATION / "schedule.json")
    tasks = registry["tasks"]
    rows = schedule["rows"]
    require(len(tasks) == 4, "task scope is not four")
    require(len(rows) == 48, "schedule scope is not 48 calls")
    require(
        len({row["execution_id"] for row in rows}) == 48,
        "execution IDs are not unique",
    )
    require(
        [row["execution_order"] for row in rows] == list(range(1, 49)),
        "execution order drift",
    )
    require(
        {row["task_id"] for row in rows}
        == {spec["task_id"] for spec in TASK_SPECS},
        "task set drift",
    )
    for arm_id in ARM_ORDER:
        require(
            sum(row["arm_id"] == arm_id for row in rows) == 8,
            f"arm count drift: {arm_id}",
        )

    design_by_task = {row["task_id"]: row for row in tasks}
    for task_id, design in design_by_task.items():
        arm_by_id = {row["arm_id"]: row for row in design["arms"]}
        require(tuple(arm_by_id) == ARM_ORDER, f"arm order drift: {task_id}")
        require(
            arm_by_id["F"]["dependency_closed"] is True,
            f"F closure drift: {task_id}",
        )
        require(
            arm_by_id["S"]["dependency_closed"] is True,
            f"S closure drift: {task_id}",
        )
        for registry_id in ("A", "B"):
            selected = [
                row
                for row in rows
                if row["task_id"] == task_id
                and row["registry_id"] == registry_id
            ]
            require(
                len(selected) == 6,
                f"task/registry arm count drift: {task_id}/{registry_id}",
            )
            require(
                {row["arm_id"] for row in selected} == set(ARM_ORDER),
                f"arm set drift: {task_id}/{registry_id}",
            )
            for row in selected:
                arm = arm_by_id[row["arm_id"]]
                candidate_path = HERE / row["candidate_path"]
                payload_path = HERE / row["payload_file"]
                request_path = HERE / row["request_file"]
                require(
                    sha256_file(candidate_path)
                    == row["candidate_sha256"]
                    == arm["artifact_sha256"],
                    f"candidate hash mismatch: {row['execution_id']}",
                )
                require(
                    extended(candidate_path).stat().st_size
                    == row["candidate_bytes"],
                    f"candidate size mismatch: {row['execution_id']}",
                )
                require(
                    sha256_file(payload_path) == row["payload_sha256"],
                    f"payload hash mismatch: {row['execution_id']}",
                )
                require(
                    sha256_file(request_path) == row["request_sha256"],
                    f"request hash mismatch: {row['execution_id']}",
                )
                request = validate_request(extended(request_path).read_bytes())
                content = message_content(request)
                require(
                    content.encode("utf-8")
                    == extended(payload_path).read_bytes(),
                    f"request/payload mismatch: {row['execution_id']}",
                )
                require(
                    content.count(MAGIC_LINE) == 1,
                    f"payload marker drift: {row['execution_id']}",
                )
                task_scaffold = extended(
                    MATERIALIZATION / row["task_scaffold_path"]
                ).read_bytes()
                fixture = extended(
                    MATERIALIZATION / row["fixture_path"]
                ).read_bytes()
                candidate = extended(candidate_path).read_bytes()
                canonical_payload = compose_model_visible_payload(
                    task_scaffold, fixture, candidate
                )
                require(
                    content[content.index(MAGIC_LINE) :].encode("utf-8")
                    == canonical_payload,
                    f"canonical payload mismatch: {row['execution_id']}",
                )
                require(
                    sha256_bytes(canonical_payload)
                    == row["canonical_payload_sha256"],
                    f"canonical payload hash mismatch: {row['execution_id']}",
                )
                require(
                    sha256_file(MATERIALIZATION / row["fixture_path"])
                    == row["fixture_sha256"],
                    f"fixture changed: {row['execution_id']}",
                )
                require(
                    sha256_file(MATERIALIZATION / row["scorer_path"])
                    == row["scorer_sha256"],
                    f"scorer changed: {row['execution_id']}",
                )
                source_path = (
                    GENERALIZATION_ROOT / row["source_fg5_request_path"]
                )
                require(
                    sha256_file(source_path)
                    == row["source_fg5_request_sha256"],
                    f"FG5 source request changed: {row['execution_id']}",
                )

    return {
        "status": "PASS",
        "tasks": len(tasks),
        "domains": len({row["domain"] for row in rows}),
        "registries": sorted({row["registry_id"] for row in rows}),
        "arms": list(ARM_ORDER),
        "schedule_rows": len(rows),
        "provider_calls": len(rows),
        "api_seed_present": False,
        "frozen_before_provider_calls": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    result = (
        build_registration()
        if args.command == "build"
        else verify_registration()
    )
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
