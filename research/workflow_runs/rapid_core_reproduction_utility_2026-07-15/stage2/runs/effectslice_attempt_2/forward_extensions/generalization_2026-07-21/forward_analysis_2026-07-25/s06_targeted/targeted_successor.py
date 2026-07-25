from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ANALYSIS_ROOT = HERE.parent
GENERALIZATION_ROOT = ANALYSIS_ROOT.parent
MATERIALIZATION = GENERALIZATION_ROOT / "materialization_remote_only_2026-07-23"
FG5_SUCCESSOR = GENERALIZATION_ROOT / "output_contract_successor_2026-07-24"
OVERLAY = ANALYSIS_ROOT / "inputs" / "terminal_row_overlay_v1.json"
CONTROL_LEDGER = (
    ANALYSIS_ROOT
    / "s03_controls"
    / "inputs"
    / "control_row_evidence_v1.csv"
)
REGISTRATION = HERE / "registration"

PAIR_SPECS = (
    {
        "case_id": "nlp_llm_01_b4",
        "task_id": "NLP-LLM-01",
        "block_id": 4,
        "indices": (463, 464),
        "final_source": "fg5_exact_output_direct",
    },
    {
        "case_id": "se_pe_01_b3",
        "task_id": "SE-PE-01",
        "block_id": 3,
        "indices": (497, 498),
        "final_source": "payload_interface_successor",
    },
    {
        "case_id": "agent_tf_01_b3",
        "task_id": "AGENT-TF-01",
        "block_id": 3,
        "indices": (569, 570),
        "final_source": "fg5_exact_output_direct",
    },
    {
        "case_id": "agent_tf_01_b4",
        "task_id": "AGENT-TF-01",
        "block_id": 4,
        "indices": (571, 572),
        "final_source": "fg5_exact_output_direct",
    },
)


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


def message_content(request: dict[str, Any]) -> str:
    messages = request.get("messages")
    require(
        isinstance(messages, list) and len(messages) == 1,
        "request must contain one message",
    )
    message = messages[0]
    require(
        isinstance(message, dict) and message.get("role") == "user",
        "request message must be user",
    )
    content = message.get("content")
    require(isinstance(content, str), "request content must be a string")
    return content


def validate_request(request_bytes: bytes) -> dict[str, Any]:
    request = json.loads(request_bytes.decode("utf-8", errors="strict"))
    require(isinstance(request, dict), "request must be a JSON object")
    require(
        request.get("model") == "deepseek-v4-flash",
        "unexpected DeepSeek model alias",
    )
    require(request.get("temperature") == 0, "temperature is not frozen at zero")
    require(request.get("top_p") == 1.0, "top_p is not frozen at one")
    require(request.get("stream") is False, "streaming must remain disabled")
    require("seed" not in request, "unregistered API seed field is present")
    message_content(request)
    return request


def source_request_path(record: dict[str, Any]) -> Path:
    execution_id = str(record["final_execution_id"])
    source = str(record["final_source"])
    if source == "fg5_exact_output_direct":
        return FG5_SUCCESSOR / "requests" / f"{execution_id}.json"
    if source == "payload_interface_successor":
        result_path = Path(str(record["result_source_path"]))
        return result_path.parent.parent / "requests" / f"{execution_id}.json"
    raise RegistrationError(f"unsupported source protocol: {source}")


def load_source_evidence() -> tuple[
    dict[int, dict[str, Any]], dict[int, dict[str, str]]
]:
    overlay_doc = load_json(OVERLAY)
    require(
        overlay_doc.get("row_count") == 1296,
        "terminal overlay is not the verified 1,296-row input",
    )
    overlay = {
        int(row["global_sequence_index"]): row for row in overlay_doc["records"]
    }
    require(len(overlay) == 1296, "terminal overlay contains duplicate indices")
    with extended(CONTROL_LEDGER).open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        ledger_rows = list(csv.DictReader(handle))
    ledger = {
        int(row["global_sequence_index"]): row for row in ledger_rows
    }
    require(len(ledger) == 144, "control ledger is not the verified 144-row input")
    return overlay, ledger


def task_inputs(task_id: str, registry_id: str) -> dict[str, Any]:
    task_dir = MATERIALIZATION / "tasks" / task_id
    manifest = load_json(task_dir / "candidate_manifest.json")
    candidate = next(
        (
            item
            for item in manifest["candidates"]
            if item["candidate_id"] == "F"
        ),
        None,
    )
    require(candidate is not None, f"missing F candidate for {task_id}")
    candidate_path = task_dir / str(candidate["artifact_path"])
    fixture_path = task_dir / "fixtures" / f"{registry_id}.json"
    scorer_path = task_dir / "support" / "scorer.py"
    for path in (candidate_path, fixture_path, scorer_path):
        require(extended(path).is_file(), f"missing frozen scoring input: {path}")
    root = MATERIALIZATION.resolve()
    return {
        "candidate_path": candidate_path.resolve().relative_to(root).as_posix(),
        "candidate_sha256": sha256_file(candidate_path),
        "candidate_tokens": int(candidate["rendered_token_count"]),
        "fixture_path": fixture_path.resolve().relative_to(root).as_posix(),
        "fixture_sha256": sha256_file(fixture_path),
        "scorer_path": scorer_path.resolve().relative_to(root).as_posix(),
        "scorer_sha256": sha256_file(scorer_path),
    }


def build_registration() -> dict[str, Any]:
    run_dir = HERE / "run"
    if extended(run_dir).exists() and any(extended(run_dir).rglob("*.json")):
        raise RegistrationError(
            "provider execution already exists; registration is immutable"
        )

    overlay, ledger = load_source_evidence()
    cases: list[dict[str, Any]] = []
    schedule: list[dict[str, Any]] = []

    for spec in PAIR_SPECS:
        records = [overlay[index] for index in spec["indices"]]
        ledger_records = [ledger[index] for index in spec["indices"]]
        case_id = str(spec["case_id"])
        require(
            {row["condition"] for row in records} == {"F", "C"},
            f"{case_id} is not an F/C pair",
        )
        require(
            all(row["task_id"] == spec["task_id"] for row in records),
            f"{case_id} task mismatch",
        )
        require(
            all(int(row["block_id"]) == spec["block_id"] for row in records),
            f"{case_id} block mismatch",
        )
        require(
            all(row["final_source"] == spec["final_source"] for row in records),
            f"{case_id} protocol mismatch",
        )
        require(
            {bool(row["operational_success"]) for row in records} == {False, True},
            f"{case_id} is not discordant",
        )
        require(
            all(row["variant_id"] == "byte_identical_identity" for row in records),
            f"{case_id} is not identity control",
        )
        require(
            len({row["registry_id"] for row in records}) == 1,
            f"{case_id} registry mismatch",
        )
        require(
            all(
                row["variant_id"] == "byte_identical_identity"
                for row in ledger_records
            ),
            f"{case_id} ledger variant mismatch",
        )
        require(
            len(
                {
                    row["canonical_model_visible_payload_sha256"]
                    for row in ledger_records
                }
            )
            == 1
            and len(
                {row["candidate_artifact_sha256"] for row in ledger_records}
            )
            == 1,
            f"{case_id} inputs are not byte-identical",
        )

        request_paths = [source_request_path(row) for row in records]
        request_bytes = [extended(path).read_bytes() for path in request_paths]
        require(request_bytes[0] == request_bytes[1], f"{case_id} wire requests differ")
        request = validate_request(request_bytes[0])
        request_sha = sha256_bytes(request_bytes[0])
        payload_bytes = message_content(request).encode("utf-8")
        payload_sha = sha256_bytes(payload_bytes)
        request_file = REGISTRATION / "requests" / f"{case_id}.json"
        payload_file = REGISTRATION / "payloads" / f"{case_id}.txt"
        write_bytes(request_file, request_bytes[0])
        write_bytes(payload_file, payload_bytes)

        registry_id = str(records[0]["registry_id"])
        frozen_inputs = task_inputs(str(spec["task_id"]), registry_id)
        case = {
            "case_id": case_id,
            "task_id": spec["task_id"],
            "block_id": spec["block_id"],
            "registry_id": registry_id,
            "final_source": spec["final_source"],
            "source_global_sequence_indices": list(spec["indices"]),
            "source_execution_ids": [row["final_execution_id"] for row in records],
            "source_conditions": [row["condition"] for row in records],
            "source_terminal_outcomes": [row["terminal_outcome"] for row in records],
            "source_operational_success": [
                bool(row["operational_success"]) for row in records
            ],
            "source_result_sha256": [row["result_source_sha256"] for row in records],
            "source_request_locators": [str(path) for path in request_paths],
            "request_file": portable(request_file),
            "request_sha256": request_sha,
            "payload_file": portable(payload_file),
            "payload_sha256": payload_sha,
            "model_slot_id": "deepseek_primary",
            "model_alias": "deepseek-v4-flash",
            "temperature": 0,
            "top_p": 1.0,
            "api_seed_present": False,
            **frozen_inputs,
        }
        cases.append(case)

        for replica in (1, 2):
            suffix = sha256_bytes(
                f"{case_id}|{replica}|{request_sha}".encode("utf-8")
            )[:16]
            schedule.append(
                {
                    "case_id": case_id,
                    "replica": replica,
                    "execution_id": (
                        f"s06-{case_id.replace('_', '-')}-r{replica}-{suffix}"
                    ),
                    "task_id": spec["task_id"],
                    "registry_id": registry_id,
                    "candidate_id": "F",
                    "condition": "repeatability_replica",
                    "model_slot_id": "deepseek_primary",
                    "request_file": portable(request_file),
                    "request_sha256": request_sha,
                    "payload_file": portable(payload_file),
                    "payload_sha256": payload_sha,
                    **frozen_inputs,
                }
            )

    registry_doc = {
        "schema_version": "effectslice-s06-targeted-registry.v1",
        "status": "frozen_before_provider_calls",
        "purpose": (
            "supplementary repeatability evidence for same-protocol identity "
            "discordance"
        ),
        "scope": {
            "cases": 4,
            "replicas_per_case": 2,
            "provider_calls": 8,
            "model_slot_id": "deepseek_primary",
        },
        "exclusions": {
            "provider_availability_row_1156": (
                "completed semantic hard-contract failure; no rerun"
            ),
            "cross_protocol_discordance": (
                "excluded because final protocols differ"
            ),
            "frozen_sections": (
                "does not rewrite FG3, FG4, FG5, or Section 03"
            ),
        },
        "cases": cases,
    }
    schedule_doc = {
        "schema_version": "effectslice-s06-targeted-schedule.v1",
        "status": "frozen_before_provider_calls",
        "rows": schedule,
    }
    write_json(REGISTRATION / "registry.json", registry_doc)
    write_json(REGISTRATION / "schedule.json", schedule_doc)

    tracked = [REGISTRATION / "registry.json", REGISTRATION / "schedule.json"]
    tracked.extend(sorted((REGISTRATION / "requests").glob("*.json")))
    tracked.extend(sorted((REGISTRATION / "payloads").glob("*.txt")))
    manifest = {
        "schema_version": "effectslice-s06-targeted-freeze-manifest.v1",
        "status": "frozen_before_provider_calls",
        "source_overlay_sha256": sha256_file(OVERLAY),
        "source_control_ledger_sha256": sha256_file(CONTROL_LEDGER),
        "materialization_manifest_sha256": sha256_file(
            MATERIALIZATION / "immutable_file_manifest.json"
        ),
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
        manifest["source_overlay_sha256"] == sha256_file(OVERLAY),
        "source overlay changed",
    )
    require(
        manifest["source_control_ledger_sha256"] == sha256_file(CONTROL_LEDGER),
        "control ledger changed",
    )
    require(
        manifest["materialization_manifest_sha256"]
        == sha256_file(MATERIALIZATION / "immutable_file_manifest.json"),
        "frozen materialization changed",
    )
    for name, expected in manifest["files"].items():
        path = HERE / name
        require(extended(path).is_file(), f"missing registered file: {name}")
        require(
            sha256_file(path) == expected,
            f"registered file hash mismatch: {name}",
        )

    registry = load_json(REGISTRATION / "registry.json")
    schedule = load_json(REGISTRATION / "schedule.json")
    cases = registry["cases"]
    rows = schedule["rows"]
    require(
        len(cases) == 4 and len(rows) == 8,
        "registered scope is not four cases and eight rows",
    )
    require(
        len({row["execution_id"] for row in rows}) == 8,
        "execution IDs are not unique",
    )
    require(
        {row["replica"] for row in rows} == {1, 2},
        "replica set is incomplete",
    )
    by_case = {case["case_id"]: case for case in cases}
    require(
        set(by_case) == {spec["case_id"] for spec in PAIR_SPECS},
        "case set changed",
    )

    for case_id, case in by_case.items():
        require(
            set(case["source_operational_success"]) == {False, True},
            f"{case_id} is not source-discordant",
        )
        request_path = HERE / case["request_file"]
        payload_path = HERE / case["payload_file"]
        request_bytes = extended(request_path).read_bytes()
        request = validate_request(request_bytes)
        require(
            sha256_bytes(request_bytes) == case["request_sha256"],
            f"{case_id} request hash mismatch",
        )
        payload_bytes = message_content(request).encode("utf-8")
        require(
            extended(payload_path).read_bytes() == payload_bytes,
            f"{case_id} payload is not the request message",
        )
        require(
            sha256_bytes(payload_bytes) == case["payload_sha256"],
            f"{case_id} payload hash mismatch",
        )
        selected = [row for row in rows if row["case_id"] == case_id]
        require(
            len(selected) == 2
            and {row["replica"] for row in selected} == {1, 2},
            f"{case_id} replicas incomplete",
        )
        for row in selected:
            for field in (
                "request_sha256",
                "payload_sha256",
                "candidate_sha256",
                "fixture_sha256",
                "scorer_sha256",
            ):
                require(
                    row[field] == case[field],
                    f"{case_id} schedule binding mismatch: {field}",
                )
            require(
                sha256_file(MATERIALIZATION / row["candidate_path"])
                == row["candidate_sha256"],
                f"{case_id} candidate changed",
            )
            require(
                sha256_file(MATERIALIZATION / row["fixture_path"])
                == row["fixture_sha256"],
                f"{case_id} fixture changed",
            )
            require(
                sha256_file(MATERIALIZATION / row["scorer_path"])
                == row["scorer_sha256"],
                f"{case_id} scorer changed",
            )

    return {
        "status": "PASS",
        "cases": len(cases),
        "schedule_rows": len(rows),
        "provider_calls": len(rows),
        "request_hashes": sorted(
            {case["request_sha256"] for case in cases}
        ),
        "api_seed_present": False,
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
