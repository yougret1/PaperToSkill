from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable


TASK_ROOT_FILES = (
    "adapter_manifest.json",
    "atom_dag.json",
    "atom_registry.json",
    "candidate_manifest.json",
    "differential_test_report.json",
    "private_registry_A_manifest.json",
    "private_registry_B_manifest.json",
    "public_fixture_manifest.json",
    "reducer_enumeration_manifest.json",
    "reducer_input_manifest.json",
    "reducer_runtime_manifest.json",
    "reference_implementation_manifest.json",
    "scorer_manifest.json",
    "semantic_audit.json",
    "source_manifest.json",
    "task_scaffold.md",
    "task_to_span_matrix.json",
)

TASK_SUBFILES = (
    "artifacts/B_empty_artifact.txt",
    "artifacts/F.txt",
    "artifacts/S_dag_ratio_60_v1.txt",
    "fixtures/A.json",
    "fixtures/B.json",
    "fixtures/public.json",
    "logs/B_empty_artifact.json",
    "logs/F.json",
    "logs/S_dag_ratio_60_v1.json",
    "runtime/reducer.py",
    "runtime/renderer.py",
    "runtime/tokenizer_fingerprint.json",
    "sources/paper_evidence.txt",
    "support/adapter.py",
    "support/reference.py",
    "support/scorer.py",
)

PROSPECTIVE_REQUIRED_FROZEN_PATHS = frozenset(
    {
        "README.md",
        "RUNNER_INTEGRATION.md",
        "analyze.py",
        "build_registration.py",
        "preregistration/design.json",
        "preregistration/policy.json",
        "preregistration/review_gate.json",
        "preregistration/source_grounding.json",
        "prospective_lib.py",
        "registration/confirmatory/schedule.json",
        "registration/manifest.json",
        "registration/pilot/schedule.json",
        "registration/runtime_jobs.jsonl",
        "registration/truth/review_packet.json",
        "runner.py",
        "truth_audit.py",
    }
)

PROSPECTIVE_SUPPLEMENTAL_FILES = (
    "registration/LAUNCHED",
    "runs/results.jsonl.manifest.json",
    "runs/pilot/phase-terminal.json",
    "runs/pilot/pilot_gate_pass.json",
    "runs/confirmatory/phase-terminal.json",
    "analysis/pilot_summary.json",
    "analysis/blinded_decisions.json",
    "analysis/truth_comparison.json",
)

PROSPECTIVE_RESULT_FIELDS = (
    "actual_model_identifier",
    "condition_success",
    "credential_value_recorded",
    "digest_ok",
    "hard_contract_vector",
    "lineage_ok",
    "private_score",
    "provider_finish_reason",
    "provider_reported_cached_input_tokens",
    "provider_reported_input_tokens",
    "provider_reported_output_tokens",
    "provider_reported_total_tokens",
    "row_valid",
    "scorer_interpretation_present",
    "terminal_outcome",
    "terminal_result_present",
    "termination_reason",
)

WINDOWS_ABSOLUTE_PATH = re.compile(
    r"(?i)(?:(?<![a-z0-9+._-])[a-z]:[\\/]|"
    r"\\\\[a-z0-9][a-z0-9._-]+[\\/])"
)
POSIX_HOME_PATH = re.compile(r"/(?:home|Users)/[^/\s]+/")
FORBIDDEN_OPERATIONAL_TEXT = re.compile(
    r"(?i)(?:third[_ -]?party|http[_ -]?(?:429|500|502)|read[_ -]?timeout|"
    r"connection[_ -]?failure|transport[_ -]?health)"
)
KNOWN_LOCAL_IDENTITY = re.compile(
    r"(?i)(?:c:[\\/]+users[\\/]+z(?:[\\/]|$)|d:[\\/]+a_work(?:[\\/]|$)|"
    r"current[_ -]?third[_ -]?party[_ -]?proxy)"
)
CREDENTIAL_TOKEN = re.compile(
    r"(?i)(?<![a-z0-9])sk-[a-z0-9_-]{16,}(?![a-z0-9])"
)
FORBIDDEN_PROVIDER_IDENTITY = re.compile(r"(?i)coderxiaoc\.com")


class BundleError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"cannot load JSON: {path}: {exc}") from exc


def filesystem_path(path: Path) -> Path:
    resolved = path.resolve()
    text = str(resolved)
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        return Path("\\\\?\\" + text)
    return resolved


def require_file(path: Path) -> Path:
    usable = filesystem_path(path)
    if not usable.is_file():
        raise BundleError(f"required file is missing: {path}")
    return usable


def replace_known_roots(text: str, roots: dict[Path, str]) -> str:
    result = text
    for root, logical in sorted(
        roots.items(), key=lambda item: len(str(item[0])), reverse=True
    ):
        variants = {
            str(root.resolve()),
            str(root.resolve()).replace("\\", "/"),
        }
        for variant in sorted(variants, key=len, reverse=True):
            result = re.sub(re.escape(variant), logical, result, flags=re.IGNORECASE)
    return result


def validate_anonymous_text(
    text: str, logical_path: str, *, check_generic_paths: bool = True
) -> None:
    if check_generic_paths and (
        WINDOWS_ABSOLUTE_PATH.search(text) or POSIX_HOME_PATH.search(text)
    ):
        raise BundleError(f"absolute local path remains in {logical_path}")
    identity = KNOWN_LOCAL_IDENTITY.search(text)
    if identity:
        raise BundleError(
            f"known local identity remains in {logical_path}: {identity.group(0)}"
        )
    match = FORBIDDEN_OPERATIONAL_TEXT.search(text)
    if match:
        raise BundleError(
            f"operational-only metadata remains in {logical_path}: {match.group(0)}"
        )
    if CREDENTIAL_TOKEN.search(text):
        raise BundleError(f"credential-shaped token remains in {logical_path}")
    if FORBIDDEN_PROVIDER_IDENTITY.search(text):
        raise BundleError(f"provider identity remains in {logical_path}")


def validate_anonymous_value(
    value: Any, logical_path: str, *, check_generic_paths: bool = True
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            validate_anonymous_text(
                str(key), logical_path, check_generic_paths=check_generic_paths
            )
            validate_anonymous_value(
                item, logical_path, check_generic_paths=check_generic_paths
            )
    elif isinstance(value, list):
        for item in value:
            validate_anonymous_value(
                item, logical_path, check_generic_paths=check_generic_paths
            )
    elif isinstance(value, str):
        validate_anonymous_text(
            value, logical_path, check_generic_paths=check_generic_paths
        )


def sanitize_value(value: Any, roots: dict[Path, str]) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_value(item, roots) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_value(item, roots) for item in value]
    if isinstance(value, str):
        return replace_known_roots(value, roots)
    return value


def normalized_bytes(
    path: Path,
    roots: dict[Path, str],
    logical_path: str,
    *,
    check_generic_paths: bool = True,
) -> bytes:
    if path.suffix.lower() == ".json":
        value = sanitize_value(load_json(path), roots)
        validate_anonymous_value(
            value, logical_path, check_generic_paths=check_generic_paths
        )
        data = canonical_json(value)
    else:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BundleError(f"cannot read text file: {path}: {exc}") from exc
        data = replace_known_roots(text, roots).replace("\r\n", "\n").encode("utf-8")
    if path.suffix.lower() != ".json":
        validate_anonymous_text(
            data.decode("utf-8"), logical_path, check_generic_paths=check_generic_paths
        )
    return data


def normalized_json_value(
    value: Any,
    roots: dict[Path, str],
    logical_path: str,
    *,
    check_generic_paths: bool = True,
) -> bytes:
    clean = sanitize_value(value, roots)
    validate_anonymous_value(
        clean, logical_path, check_generic_paths=check_generic_paths
    )
    return canonical_json(clean)


def write_bytes(root: Path, relative: str, data: bytes) -> None:
    target = root / Path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def path_allows_generic_test_literals(logical_path: str) -> bool:
    return logical_path.startswith("prospective/frozen/tests/")


def validate_artifact_bytes(data: bytes, logical_path: str) -> None:
    suffix = Path(logical_path).suffix.lower()
    check_generic_paths = not (
        logical_path.startswith("responses/")
        or logical_path.startswith("prospective/responses/")
        or path_allows_generic_test_literals(logical_path)
    )
    if suffix == ".json":
        try:
            value = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BundleError(f"invalid JSON in {logical_path}: {exc}") from exc
        validate_anonymous_value(
            value, logical_path, check_generic_paths=check_generic_paths
        )
    elif suffix in {".jsonl", ".md", ".py", ".txt", ".csv"} or not suffix:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BundleError(f"non-UTF-8 text in {logical_path}: {exc}") from exc
        validate_anonymous_text(
            text, logical_path, check_generic_paths=check_generic_paths
        )


def contained_path(root: Path, relative: str, label: str) -> Path:
    root = root.resolve()
    path = (root / Path(relative)).resolve()
    if not path.is_relative_to(root):
        raise BundleError(f"{label} escapes its root: {relative}")
    return require_file(path)


def safe_schedule_row(row: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "execution_id",
        "logical_cell_id",
        "task_id",
        "paper_id",
        "domain",
        "registry_id",
        "block_id",
        "pair_id",
        "condition",
        "candidate_id",
        "variant_id",
        "order_code",
        "order_position",
        "repeat_id",
        "repeat_sequence_index",
        "model_slot_id",
        "candidate_artifact_sha256",
        "canonical_model_visible_payload_sha256",
        "serialized_wire_request_sha256",
        "private_registry_manifest_sha256",
        "scorer_manifest_sha256",
        "task_scaffold_sha256",
        "fixture_manifest_sha256",
        "fixture_payload_sha256",
        "decoding_config_sha256",
    )
    result = {field: row[field] for field in fields if field in row}
    result["request_file"] = f"requests/{row['logical_cell_id']}.json"
    return result


def safe_evidence_row(
    schedule_row: dict[str, Any], result: dict[str, Any], response_path: str
) -> dict[str, Any]:
    result_fields = (
        "actual_model_identifier",
        "condition_success",
        "hard_contract_vector",
        "private_score",
        "row_valid",
        "terminal_outcome",
        "provider_finish_reason",
        "provider_reported_cached_input_tokens",
        "provider_reported_input_tokens",
        "provider_reported_output_tokens",
        "provider_reported_total_tokens",
        "termination_reason",
    )
    evidence = safe_schedule_row(schedule_row)
    evidence.update(
        {field: result[field] for field in result_fields if field in result}
    )
    evidence["canonical_response_file"] = response_path
    evidence["canonical_response_sha256"] = result["canonical_output_sha256"]
    evidence["registered_request_sha256"] = result["registered_request_sha256"]
    evidence["evidence_scope"] = (
        "complete canonical model-visible response plus frozen request, registry, "
        "scorer, contract vector, and terminal outcome"
    )
    return evidence


def task_ids(task_root: Path) -> list[str]:
    return sorted(
        path.name
        for path in task_root.iterdir()
        if path.is_dir() and (path / "atom_registry.json").is_file()
    )


def add_task_packages(
    staging: Path, task_root: Path, roots: dict[Path, str]
) -> list[str]:
    ids = task_ids(task_root)
    for task_id in ids:
        source = task_root / task_id
        for relative in (*TASK_ROOT_FILES, *TASK_SUBFILES):
            path = require_file(source / Path(relative))
            logical = f"tasks/{task_id}/{Path(relative).as_posix()}"
            write_bytes(staging, logical, normalized_bytes(path, roots, logical))
    return ids


def add_source_scope(staging: Path, task_root: Path, ids: list[str]) -> None:
    rows: list[dict[str, Any]] = []
    for task_id in ids:
        source = task_root / task_id
        source_manifest = load_json(source / "source_manifest.json")
        atom_registry = load_json(source / "atom_registry.json")
        span_matrix = load_json(source / "task_to_span_matrix.json")

        sources = source_manifest.get("sources")
        if not isinstance(sources, list) or len(sources) != 1:
            raise BundleError(f"{task_id} must register exactly one bounded source summary")
        source_record = sources[0]
        source_path = require_file(source / str(source_record.get("path", "")))
        local_summary_sha256 = sha256_file(source_path)
        if local_summary_sha256 != source_record.get("sha256"):
            raise BundleError(f"{task_id} bounded source summary digest changed")

        atoms = atom_registry.get("atoms")
        if not isinstance(atoms, list) or not atoms:
            raise BundleError(f"{task_id} atom registry is empty")
        locator_documents = {
            str(atom.get("source_locator", {}).get("document_sha256", ""))
            for atom in atoms
        }
        if locator_documents != {local_summary_sha256}:
            raise BundleError(
                f"{task_id} atom locators do not exclusively target the bounded source summary"
            )

        spans = span_matrix.get("central_spans")
        if not isinstance(spans, list) or not spans:
            raise BundleError(f"{task_id} source-span matrix is empty")
        rows.append(
            {
                "task_id": task_id,
                "locator_target": "builder-authored bounded source summary",
                "local_summary_sha256": local_summary_sha256,
                "upstream_document_sha256": source_record.get("upstream_sha256"),
                "upstream_url": source_record.get("upstream_url"),
                "source_transformation": source_record.get("transformation"),
                "atom_count": len(atoms),
                "unique_source_spans": len(
                    {
                        (
                            str(span.get("document_sha256", "")),
                            int(span.get("byte_start", -1)),
                            int(span.get("byte_end", -1)),
                        )
                        for span in spans
                    }
                ),
                "independent_original_paper_fidelity_review": "not included",
            }
        )

    write_bytes(
        staging,
        "SOURCE_SCOPE.json",
        canonical_json(
            {
                "schema_version": "skillaudit-anonymous-source-scope.v1",
                "scope_statement": (
                    "Atom locators bind to builder-authored bounded source summaries, "
                    "not directly to the upstream paper PDFs."
                ),
                "tasks": rows,
            }
        ),
    )


def add_primary_evidence(
    staging: Path, primary_root: Path, roots: dict[Path, str]
) -> tuple[int, int]:
    evidence_index: list[dict[str, Any]] = []
    copied_requests: set[str] = set()
    for repeat_id in ("SOL1", "SOL2", "SOL3"):
        schedule_path = require_file(
            primary_root / "registration" / "full_grid" / repeat_id / "schedule.json"
        )
        schedule = load_json(schedule_path)
        rows = [
            row for row in schedule["rows"] if row.get("execution_family") == "primary"
        ]
        rows.sort(key=lambda row: (int(row["global_sequence_index"]), row["execution_id"]))
        safe_rows = [safe_schedule_row(row) for row in rows]
        write_bytes(
            staging,
            f"schedules/{repeat_id}.json",
            canonical_json(
                {
                    "schema_version": "skillaudit-anonymous-primary-schedule.v1",
                    "repeat_id": repeat_id,
                    "registered_rows": len(safe_rows),
                    "rows": safe_rows,
                }
            ),
        )

        run_root = primary_root / "runs" / "full_grid" / repeat_id
        for row in rows:
            request_name = f"{row['logical_cell_id']}.json"
            request_logical = f"requests/{request_name}"
            if request_logical not in copied_requests:
                request_source = require_file(
                    primary_root
                    / "registration"
                    / "full_grid"
                    / "requests"
                    / request_name
                )
                request_data = normalized_bytes(
                    request_source, roots, request_logical
                )
                expected = row["serialized_wire_request_sha256"]
                if sha256_bytes(request_source.read_bytes()) != expected:
                    raise BundleError(f"registered request hash changed: {request_source}")
                write_bytes(staging, request_logical, request_data)
                copied_requests.add(request_logical)

            execution_id = row["execution_id"]
            result_path = require_file(run_root / "rows" / f"{execution_id}.json")
            result = load_json(result_path)
            if result.get("execution_id") != execution_id:
                raise BundleError(f"result execution mismatch: {result_path}")
            response_source = require_file(
                run_root / str(result["canonical_output_path"])
            )
            if sha256_file(response_source) != result["canonical_output_sha256"]:
                raise BundleError(f"canonical response hash changed: {response_source}")
            response_logical = f"responses/{repeat_id}/{execution_id}.txt"
            response_data = normalized_bytes(
                response_source,
                roots,
                response_logical,
                check_generic_paths=False,
            )
            write_bytes(staging, response_logical, response_data)
            evidence = safe_evidence_row(row, result, response_logical)
            evidence_logical = f"evidence/{repeat_id}/{execution_id}.json"
            data = canonical_json(evidence)
            validate_anonymous_text(data.decode("utf-8"), evidence_logical)
            write_bytes(staging, evidence_logical, data)
            evidence_index.append(
                {
                    "execution_id": execution_id,
                    "repeat_id": repeat_id,
                    "evidence_file": evidence_logical,
                    "evidence_sha256": sha256_bytes(data),
                    "response_file": response_logical,
                    "response_sha256": sha256_bytes(response_data),
                }
            )

    write_bytes(
        staging,
        "EVIDENCE_INDEX.json",
        canonical_json(
            {
                "schema_version": "skillaudit-anonymous-evidence-index.v1",
                "rows": evidence_index,
            }
        ),
    )
    return len(evidence_index), len(copied_requests)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BundleError(f"invalid JSONL row {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise BundleError(f"JSONL row is not an object: {path}:{line_number}")
        rows.append(value)
    return rows


def add_frozen_prospective_package(
    staging: Path, prospective_root: Path
) -> str:
    freeze_path = require_file(prospective_root / "registration" / "freeze.json")
    freeze = load_json(freeze_path)
    bundle_sha256 = str(freeze.get("bundle_sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", bundle_sha256):
        raise BundleError("prospective registration bundle digest is invalid")
    records = freeze.get("files")
    if not isinstance(records, list) or not records:
        raise BundleError("prospective freeze file list is empty")
    registered_paths = {str(record.get("path", "")) for record in records}
    missing = sorted(PROSPECTIVE_REQUIRED_FROZEN_PATHS - registered_paths)
    if missing:
        raise BundleError(f"prospective freeze omits required files: {missing}")

    seen: set[str] = set()
    for record in records:
        relative = str(record.get("path", ""))
        if not relative or relative in seen:
            raise BundleError(f"invalid or duplicate prospective freeze path: {relative}")
        seen.add(relative)
        source = contained_path(prospective_root, relative, "prospective freeze path")
        data = source.read_bytes()
        if len(data) != int(record.get("bytes", -1)):
            raise BundleError(f"prospective frozen size changed: {relative}")
        if sha256_bytes(data) != str(record.get("sha256", "")):
            raise BundleError(f"prospective frozen digest changed: {relative}")
        logical = f"prospective/frozen/{Path(relative).as_posix()}"
        validate_artifact_bytes(data, logical)
        write_bytes(staging, logical, data)

    freeze_data = normalized_bytes(
        freeze_path,
        {prospective_root: "source://prospective-six-state"},
        "prospective/registration/freeze.json",
    )
    write_bytes(staging, "prospective/registration/freeze.json", freeze_data)
    return bundle_sha256


def add_prospective_supplemental_files(
    staging: Path, prospective_root: Path, roots: dict[Path, str]
) -> tuple[str, str]:
    for relative in PROSPECTIVE_SUPPLEMENTAL_FILES:
        source = contained_path(prospective_root, relative, "prospective evidence path")
        logical = f"prospective/{Path(relative).as_posix()}"
        write_bytes(staging, logical, normalized_bytes(source, roots, logical))

    completed = prospective_root / "registration" / "truth" / "completed"
    reviewer_a = require_file(completed / "reviewer_a.json")
    reviewer_b = require_file(completed / "reviewer_b.json")
    for source in sorted(path for path in completed.rglob("*") if path.is_file()):
        relative = source.relative_to(prospective_root).as_posix()
        logical = f"prospective/{relative}"
        write_bytes(staging, logical, normalized_bytes(source, roots, logical))

    return sha256_file(reviewer_a), sha256_file(reviewer_b)


def safe_prospective_evidence_row(
    job: dict[str, Any],
    result: dict[str, Any],
    transport: dict[str, Any],
    response_logical: str,
) -> dict[str, Any]:
    evidence = {
        "schema_version": "skillaudit-anonymous-prospective-terminal-evidence.v1",
        "phase": result["phase"],
        "execution_id": result["execution_id"],
        "condition_id": result["condition_id"],
        "task_id": job["task_id"],
        "registry_id": job["registry_id"],
        "repetition_id": job["repetition_id"],
        "block_id": job["block_id"],
        "request_file": f"prospective/frozen/{Path(job['request_file']).as_posix()}",
        "request_sha256": job["request_sha256"],
        "candidate_file": f"prospective/frozen/{Path(job['candidate_file']).as_posix()}",
        "candidate_sha256": job["candidate_sha256"],
        "canonical_response_file": response_logical,
        "canonical_response_sha256": result["canonical_output_sha256"],
        "registration_bundle_sha256": result["registration_bundle_sha256"],
        "response_reported_temperature": transport.get(
            "response_reported_temperature"
        ),
        "response_reported_top_p": transport.get("response_reported_top_p"),
        "decoding_config_match": transport.get("decoding_config_match"),
        "evidence_scope": (
            "registered request and candidate, canonical model output, frozen scorer "
            "result, and response-reported decoding metadata"
        ),
    }
    evidence.update(
        {field: result[field] for field in PROSPECTIVE_RESULT_FIELDS if field in result}
    )
    return evidence


def add_prospective_terminal_evidence(
    staging: Path,
    prospective_root: Path,
    roots: dict[Path, str],
    expected_rows: int,
    expected_bundle_sha256: str,
) -> tuple[int, int, int]:
    runtime_path = require_file(
        prospective_root / "registration" / "runtime_jobs.jsonl"
    )
    jobs = load_jsonl(runtime_path)
    jobs_by_execution = {str(row.get("execution_id", "")): row for row in jobs}
    if len(jobs_by_execution) != len(jobs):
        raise BundleError("prospective runtime execution IDs are not unique")

    results_path = require_file(prospective_root / "runs" / "results.jsonl")
    results = load_jsonl(results_path)
    if len(results) != expected_rows:
        raise BundleError(
            f"prospective evidence count changed: expected {expected_rows}, found {len(results)}"
        )
    if len(jobs) != expected_rows:
        raise BundleError(
            f"prospective runtime count changed: expected {expected_rows}, found {len(jobs)}"
        )

    evidence_index: list[dict[str, Any]] = []
    request_files: set[str] = set()
    candidate_files: set[str] = set()
    seen_results: set[str] = set()
    for result in results:
        execution_id = str(result.get("execution_id", ""))
        if not execution_id or execution_id in seen_results:
            raise BundleError(f"duplicate prospective result: {execution_id}")
        seen_results.add(execution_id)
        job = jobs_by_execution.get(execution_id)
        if job is None:
            raise BundleError(f"prospective result lacks a runtime job: {execution_id}")
        phase = str(result.get("phase", ""))
        if phase != job.get("phase") or phase not in {"pilot", "confirmatory"}:
            raise BundleError(f"prospective phase binding changed: {execution_id}")
        if result.get("condition_id") != job.get("condition_id"):
            raise BundleError(f"prospective condition binding changed: {execution_id}")
        if result.get("registered_request_sha256") != job.get("request_sha256"):
            raise BundleError(f"prospective request binding changed: {execution_id}")
        if result.get("registered_candidate_sha256") != job.get("candidate_sha256"):
            raise BundleError(f"prospective candidate binding changed: {execution_id}")
        if result.get("registration_bundle_sha256") != expected_bundle_sha256:
            raise BundleError(f"prospective registration binding changed: {execution_id}")

        request_source = contained_path(
            prospective_root, str(job["request_file"]), "prospective request"
        )
        candidate_source = contained_path(
            prospective_root, str(job["candidate_file"]), "prospective candidate"
        )
        if sha256_file(request_source) != job.get("request_sha256"):
            raise BundleError(f"prospective request digest changed: {execution_id}")
        if sha256_file(candidate_source) != job.get("candidate_sha256"):
            raise BundleError(f"prospective candidate digest changed: {execution_id}")
        request_files.add(str(job["request_file"]))
        candidate_files.add(str(job["candidate_file"]))

        run_root = prospective_root / "runs" / phase
        response_source = contained_path(
            run_root,
            str(result.get("canonical_output_path", "")),
            "prospective canonical response",
        )
        if sha256_file(response_source) != result.get("canonical_output_sha256"):
            raise BundleError(f"prospective response digest changed: {execution_id}")
        response_logical = f"prospective/responses/{phase}/{execution_id}.txt"
        response_data = normalized_bytes(
            response_source,
            roots,
            response_logical,
            check_generic_paths=False,
        )
        write_bytes(staging, response_logical, response_data)

        transport_path = require_file(
            run_root / "transport" / f"{execution_id}.json"
        )
        transport = load_json(transport_path)
        if transport.get("execution_id") != execution_id:
            raise BundleError(f"prospective transport binding changed: {execution_id}")
        if transport.get("decoding_config_match") is not True:
            raise BundleError(f"prospective decoding evidence failed: {execution_id}")

        evidence = safe_prospective_evidence_row(
            job, result, transport, response_logical
        )
        evidence_logical = f"prospective/evidence/{phase}/{execution_id}.json"
        evidence_data = normalized_json_value(
            evidence, roots, evidence_logical
        )
        write_bytes(staging, evidence_logical, evidence_data)
        evidence_index.append(
            {
                "phase": phase,
                "execution_id": execution_id,
                "evidence_file": evidence_logical,
                "evidence_sha256": sha256_bytes(evidence_data),
                "response_file": response_logical,
                "response_sha256": sha256_bytes(response_data),
            }
        )

    write_bytes(
        staging,
        "PROSPECTIVE_EVIDENCE_INDEX.json",
        canonical_json(
            {
                "schema_version": "skillaudit-anonymous-prospective-evidence-index.v1",
                "registration_bundle_sha256": expected_bundle_sha256,
                "rows": evidence_index,
            }
        ),
    )
    return len(evidence_index), len(request_files), len(candidate_files)


def add_prospective_evidence(
    staging: Path,
    prospective_root: Path,
    roots: dict[Path, str],
    expected_rows: int,
) -> dict[str, Any]:
    bundle_sha256 = add_frozen_prospective_package(staging, prospective_root)
    reviewer_a_sha256, reviewer_b_sha256 = add_prospective_supplemental_files(
        staging, prospective_root, roots
    )
    rows, requests, candidates = add_prospective_terminal_evidence(
        staging,
        prospective_root,
        roots,
        expected_rows,
        bundle_sha256,
    )
    truth_comparison = load_json(prospective_root / "analysis" / "truth_comparison.json")
    gate = truth_comparison.get("review_gate", {})
    if gate.get("launch_authorized") is not True or gate.get(
        "truth_join_authorized"
    ) is not True:
        raise BundleError("prospective truth gate is not authorized")
    if gate.get("registration_bundle_sha256") != bundle_sha256:
        raise BundleError("prospective truth gate bundle binding changed")
    if gate.get("reviewer_a_sha256") != reviewer_a_sha256:
        raise BundleError("prospective reviewer A binding changed")
    if gate.get("reviewer_b_sha256") != reviewer_b_sha256:
        raise BundleError("prospective reviewer B binding changed")
    return {
        "bundle_sha256": bundle_sha256,
        "evidence_rows": rows,
        "unique_requests": requests,
        "unique_candidates": candidates,
    }


def add_readme(
    staging: Path,
    task_count: int,
    row_count: int,
    request_count: int,
    prospective: dict[str, Any] | None,
) -> None:
    prospective_text = ""
    if prospective is not None:
        prospective_text = f"""

The prospective section preserves the complete hash-frozen registration package,
independent truth-review records, pilot and confirmatory terminal attestations,
blinded decisions, truth comparison, canonical model outputs, and sanitized
field-level evidence. Raw provider bodies and transport-attempt logs are excluded.

- prospective terminal evidence rows: {prospective['evidence_rows']}
- prospective unique requests: {prospective['unique_requests']}
- prospective unique candidates: {prospective['unique_candidates']}
- prospective registration bundle: {prospective['bundle_sha256']}
"""
    text = f"""# SkillAudit Anonymous Audit Objects

This bundle exposes the source summaries and locators, atom registries, dependency
graphs, rendered full and simplified specifications, task scaffolds, public and
private fixtures, scorers, frozen primary schedules, registered requests, complete
canonical model-visible responses, and field-level terminal evidence used by the
primary GPT-5.6 Sol analysis.

The task packages are builder-authored operationalizations linked to bounded source
summaries. Their registered dependency edges and task/scorer contracts are package
declarations: including them makes the experimental boundary inspectable, but does
not independently establish fidelity to the original papers.

- task packages: {task_count}
- primary terminal evidence rows: {row_count}
- unique registered primary requests: {request_count}
{prospective_text}

Canonical response text and its retained source digest are included for every
primary row. All package paths are relative and the ZIP is deterministic.
"""
    validate_anonymous_text(text, "README.md")
    write_bytes(staging, "README.md", text.encode("utf-8"))


def add_manifest(staging: Path) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in staging.rglob("*") if item.is_file()):
        relative = path.relative_to(staging).as_posix()
        if relative == "MANIFEST.json":
            continue
        data = path.read_bytes()
        validate_artifact_bytes(data, relative)
        files.append(
            {"path": relative, "bytes": len(data), "sha256": sha256_bytes(data)}
        )
    manifest = {
        "schema_version": "skillaudit-anonymous-audit-bundle.v1",
        "file_count": len(files),
        "files": files,
    }
    write_bytes(staging, "MANIFEST.json", canonical_json(manifest))
    return manifest


def deterministic_zip(staging: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(item for item in staging.rglob("*") if item.is_file()):
            relative = path.relative_to(staging).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def verify_bundle(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise BundleError("ZIP contains duplicate entry names")
        if "MANIFEST.json" not in names:
            raise BundleError("ZIP is missing MANIFEST.json")
        manifest = json.loads(archive.read("MANIFEST.json"))
        records = manifest.get("files")
        if not isinstance(records, list):
            raise BundleError("manifest files field is invalid")
        expected = {str(record["path"]) for record in records} | {"MANIFEST.json"}
        if set(names) != expected:
            missing = sorted(expected - set(names))
            extra = sorted(set(names) - expected)
            raise BundleError(f"ZIP/manifest entry mismatch: missing={missing}, extra={extra}")
        for info in infos:
            if info.date_time != (1980, 1, 1, 0, 0, 0):
                raise BundleError(f"nondeterministic ZIP timestamp: {info.filename}")
        for record in records:
            name = str(record["path"])
            data = archive.read(name)
            if len(data) != int(record["bytes"]):
                raise BundleError(f"manifest byte count mismatch: {name}")
            if sha256_bytes(data) != str(record["sha256"]):
                raise BundleError(f"manifest digest mismatch: {name}")
            validate_artifact_bytes(data, name)
        evidence = json.loads(archive.read("EVIDENCE_INDEX.json"))["rows"]
        for row in evidence:
            if row["evidence_file"] not in expected:
                raise BundleError(f"indexed evidence is missing: {row['evidence_file']}")
            if row["response_file"] not in expected:
                raise BundleError(f"indexed response is missing: {row['response_file']}")
            if sha256_bytes(archive.read(row["evidence_file"])) != row["evidence_sha256"]:
                raise BundleError(f"indexed evidence digest mismatch: {row['evidence_file']}")
            if sha256_bytes(archive.read(row["response_file"])) != row["response_sha256"]:
                raise BundleError(f"indexed response digest mismatch: {row['response_file']}")
        prospective_evidence: list[dict[str, Any]] = []
        if "PROSPECTIVE_EVIDENCE_INDEX.json" in names:
            prospective_evidence = json.loads(
                archive.read("PROSPECTIVE_EVIDENCE_INDEX.json")
            )["rows"]
            for row in prospective_evidence:
                if row["evidence_file"] not in expected:
                    raise BundleError(
                        f"indexed prospective evidence is missing: {row['evidence_file']}"
                    )
                if row["response_file"] not in expected:
                    raise BundleError(
                        f"indexed prospective response is missing: {row['response_file']}"
                    )
                if sha256_bytes(archive.read(row["evidence_file"])) != row[
                    "evidence_sha256"
                ]:
                    raise BundleError(
                        f"indexed prospective evidence digest mismatch: {row['evidence_file']}"
                    )
                if sha256_bytes(archive.read(row["response_file"])) != row[
                    "response_sha256"
                ]:
                    raise BundleError(
                        f"indexed prospective response digest mismatch: {row['response_file']}"
                    )
    return {
        "status": "passed",
        "zip_sha256": sha256_file(path),
        "entries": len(names),
        "manifest_files": len(records),
        "evidence_rows": len(evidence),
        "prospective_evidence_rows": len(prospective_evidence),
    }


def build_bundle(
    task_root: Path,
    primary_root: Path,
    output: Path,
    expected_tasks: int = 24,
    expected_rows: int = 1296,
    prospective_root: Path | None = None,
    expected_prospective_rows: int = 434,
) -> dict[str, Any]:
    task_root = task_root.resolve()
    primary_root = primary_root.resolve()
    roots = {
        task_root: "source://task-materialization",
        primary_root: "source://gpt-5.6-sol-primary",
    }
    if prospective_root is not None:
        prospective_root = prospective_root.resolve()
        roots[prospective_root] = "source://prospective-six-state"
    with tempfile.TemporaryDirectory(prefix="skillaudit-audit-bundle-") as temp:
        staging = Path(temp)
        ids = add_task_packages(staging, task_root, roots)
        if len(ids) != expected_tasks:
            raise BundleError(
                f"task count changed: expected {expected_tasks}, found {len(ids)}"
            )
        add_source_scope(staging, task_root, ids)
        row_count, request_count = add_primary_evidence(staging, primary_root, roots)
        if row_count != expected_rows:
            raise BundleError(
                f"primary evidence count changed: expected {expected_rows}, found {row_count}"
            )
        prospective = (
            add_prospective_evidence(
                staging,
                prospective_root,
                roots,
                expected_prospective_rows,
            )
            if prospective_root is not None
            else None
        )
        add_readme(staging, len(ids), row_count, request_count, prospective)
        manifest = add_manifest(staging)
        deterministic_zip(staging, output)
    return {
        "status": "complete",
        "output": str(output.resolve()),
        "output_sha256": sha256_file(output),
        "task_count": len(ids),
        "evidence_rows": row_count,
        "unique_requests": request_count,
        "prospective_evidence_rows": (
            0 if prospective is None else prospective["evidence_rows"]
        ),
        "manifest_files": manifest["file_count"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--primary-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prospective-root", type=Path)
    parser.add_argument("--expected-tasks", type=int, default=24)
    parser.add_argument("--expected-rows", type=int, default=1296)
    parser.add_argument("--expected-prospective-rows", type=int, default=434)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_bundle(
        args.task_root,
        args.primary_root,
        args.output,
        expected_tasks=args.expected_tasks,
        expected_rows=args.expected_rows,
        prospective_root=args.prospective_root,
        expected_prospective_rows=args.expected_prospective_rows,
    )
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
