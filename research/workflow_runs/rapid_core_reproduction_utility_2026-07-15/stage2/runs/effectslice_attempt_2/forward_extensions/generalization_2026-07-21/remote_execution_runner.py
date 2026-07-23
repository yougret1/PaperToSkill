from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import gzip
import hashlib
import http.client
import importlib.util
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


FORWARD_ROOT = Path(__file__).resolve().parent
WORKER_PATH = FORWARD_ROOT / "remote_execution_worker.py"
DEFAULT_MATERIALIZATION = FORWARD_ROOT / "materialization_remote_only_2026-07-23"
DEFAULT_CONTRACT_DIR = FORWARD_ROOT / "remote_execution_contract_2026-07-23"
DEFAULT_RUN_DIR = FORWARD_ROOT / "remote_execution_2026-07-23"
EXPECTED_ANCHOR_BUNDLE_SHA256 = (
    "1f12dfdba63b1ddc65bd57fa8b1b625ba4259050e93ab4f108786c2023c5ccd7"
)
TIMEOUT_SECONDS = 240
MAXIMUM_TRANSPORT_ATTEMPTS = 5
RETRY_DELAYS_SECONDS = (2, 4, 8, 16)
PRIVATE_SCORE_THRESHOLD = 0.99
WORKER_TIMEOUT_SECONDS = 30
SCHEMA_VERSION = "effectslice-fg1-remote-executor.v1"
TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{16,}|[A-Za-z0-9_-]{32,})(?![A-Za-z0-9])"
)
RETRYABLE_HTTP = frozenset({408, 429, 500, 502, 503, 504})
REQUEST_ID_HEADERS = (
    "x-request-id",
    "request-id",
    "openai-request-id",
    "anthropic-request-id",
    "cf-ray",
)


@dataclass(frozen=True)
class ProviderSpec:
    slot_id: str
    exact_alias: str
    endpoint: str
    protocol: str
    anthropic_version: str | None = None


PROVIDER_SPECS: dict[str, ProviderSpec] = {
    "deepseek_primary": ProviderSpec(
        "deepseek_primary",
        "deepseek-v4-flash",
        "https://api.deepseek.com/chat/completions",
        "openai_chat_completions_v1",
    ),
    "gpt_5_5": ProviderSpec(
        "gpt_5_5",
        "gpt-5.5",
        "https://coderxiaoc.com/v1/responses",
        "openai_responses_v1",
    ),
    "gpt_5_6_sol": ProviderSpec(
        "gpt_5_6_sol",
        "gpt-5.6-sol",
        "https://coderxiaoc.com/v1/responses",
        "openai_responses_v1",
    ),
    "gpt_5_6_terra": ProviderSpec(
        "gpt_5_6_terra",
        "gpt-5.6-terra",
        "https://coderxiaoc.com/v1/responses",
        "openai_responses_v1",
    ),
    "claude_opus_4_7": ProviderSpec(
        "claude_opus_4_7",
        "claude-opus-4-7",
        "https://coderxiaoc.com/v1/messages",
        "anthropic_messages_v1",
        "2023-06-01",
    ),
    "gpt_5_6_luna": ProviderSpec(
        "gpt_5_6_luna",
        "gpt-5.6-luna",
        "https://coderxiaoc.com/v1/responses",
        "openai_responses_v1",
    ),
}


class ExecutionError(RuntimeError):
    pass


class IntegrityError(ExecutionError):
    pass


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Any,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        del req, fp, code, msg, headers, newurl
        return None


@dataclass
class DispatchResult:
    state: str
    attempts: list[dict[str, Any]]
    terminal_body: bytes | None
    terminal_http_status: int | None
    terminal_headers: dict[str, str]
    attempt_bodies: list[tuple[int, bytes]]
    total_execution_elapsed_ms: int
    failure_class: str | None

    def row_attempts(self) -> list[dict[str, Any]]:
        return [
            {
                "attempt_index": int(item["attempt_index"]),
                "attempt_status_class": str(item["attempt_status_class"]),
                "attempt_elapsed_ms": int(item["attempt_elapsed_ms"]),
                "retry_sleep_after_attempt_ms": int(
                    item["retry_sleep_after_attempt_ms"]
                ),
            }
            for item in self.attempts
        ]


@dataclass(frozen=True)
class RowInputs:
    task_dir: Path
    request_path: Path
    request_bytes: bytes
    payload_path: Path
    fixture_path: Path
    scorer_path: Path
    candidate_path: Path
    candidate_tokens: int


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_json(path: Path, value: object, pretty: bool = True) -> None:
    if pretty:
        data = (
            json.dumps(
                value,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    else:
        data = canonical_json(value)
    atomic_write(path, data)


def atomic_gzip_json(path: Path, value: object) -> None:
    data = canonical_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(data)
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(temporary, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegrityError(message)


def windows_extended_path(path: Path) -> Path:
    if os.name != "nt":
        return path.resolve()
    value = str(path.absolute())
    if value.startswith("\\\\?\\"):
        return Path(value)
    if value.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + value[2:])
    return Path("\\\\?\\" + value)


def read_document(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ExecutionError(f"cannot decode API documentation: {path.name}")


def credential_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    for match in TOKEN_PATTERN.finditer(text):
        value = match.group(0)
        if value not in seen:
            candidates.append(value)
            seen.add(value)
    return candidates


def credential_for_spec(docs_dir: Path, spec: ProviderSpec) -> tuple[str, dict[str, Any]]:
    matches: list[tuple[Path, str]] = []
    for path in sorted(docs_dir.glob("*.md"), key=lambda item: item.name):
        text = read_document(path)
        if spec.endpoint in text and spec.exact_alias in text:
            matches.append((path, text))
    if len(matches) != 1:
        raise ExecutionError(
            f"expected one API document for {spec.slot_id}, found {len(matches)}"
        )
    path, text = matches[0]
    candidates = credential_candidates(text)
    if not candidates:
        raise ExecutionError(f"no credential candidate found for {spec.slot_id}")
    # The Claude document intentionally lists the regular API key before the
    # desktop-direct key. All other registered documents contain one unique key.
    token = candidates[0]
    metadata = {
        "document_name": path.name,
        "unique_candidate_count": len(candidates),
        "selected_candidate_ordinal": 1,
        "selected_candidate_length": len(token),
        "credential_value_recorded": False,
    }
    return token, metadata


def load_credentials(
    docs_dir: Path,
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    if not docs_dir.is_dir():
        raise ExecutionError(f"API documentation directory does not exist: {docs_dir}")
    values: dict[str, str] = {}
    metadata: dict[str, dict[str, Any]] = {}
    endpoint_tokens: dict[str, str] = {}
    endpoint_metadata: dict[str, dict[str, Any]] = {}
    for slot_id, spec in PROVIDER_SPECS.items():
        if spec.endpoint not in endpoint_tokens:
            token, source = credential_for_spec(docs_dir, spec)
            endpoint_tokens[spec.endpoint] = token
            endpoint_metadata[spec.endpoint] = source
        values[slot_id] = endpoint_tokens[spec.endpoint]
        metadata[slot_id] = dict(endpoint_metadata[spec.endpoint])
    return values, metadata


def provider_headers(spec: ProviderSpec, token: str, execution_id: str) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "Authorization": f"Bearer {token}",
        "Connection": "close",
        "Content-Type": "application/json",
        "User-Agent": "EffectSlice-FG1-RemoteExecutor/1.0",
    }
    if spec.protocol == "openai_responses_v1":
        headers["Idempotency-Key"] = execution_id
    if spec.anthropic_version:
        headers["anthropic-version"] = spec.anthropic_version
    return headers


def safe_response_headers(headers: Any) -> dict[str, str]:
    values: dict[str, str] = {}
    for name in REQUEST_ID_HEADERS:
        value = headers.get(name) if headers is not None else None
        if value:
            values[name] = str(value)[:300]
    return values


def retry_after_seconds(headers: Any, now: Callable[[], float] = time.time) -> float:
    value = headers.get("Retry-After") if headers is not None else None
    if value is None:
        return 0.0
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        try:
            parsed = email.utils.parsedate_to_datetime(str(value))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return max(0.0, parsed.timestamp() - now())
        except (TypeError, ValueError, OverflowError):
            return 0.0


def deterministic_jitter_seconds(execution_id: str, attempt_index: int) -> float:
    digest = hashlib.sha256(f"{execution_id}:{attempt_index}".encode("utf-8")).digest()
    return (int.from_bytes(digest[:4], "big") % 1001) / 1000.0


def classify_url_error(exc: urllib.error.URLError) -> tuple[str, bool]:
    reason = exc.reason
    text = str(reason).lower()
    if isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in text:
        return "read_timeout", True
    if isinstance(reason, ssl.SSLError) or "ssl" in text or "tls" in text:
        return "tls_transport_failure", True
    if isinstance(reason, socket.gaierror) or "name or service" in text or "getaddrinfo" in text:
        return "dns_transport_failure", True
    if isinstance(reason, ConnectionResetError) or "connection reset" in text:
        return "connection_reset", True
    return "transport_failure", True


def dispatch_request(
    spec: ProviderSpec,
    token: str,
    execution_id: str,
    request_bytes: bytes,
    *,
    timeout_seconds: int = TIMEOUT_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    opener_factory: Callable[[], Any] | None = None,
) -> DispatchResult:
    attempts: list[dict[str, Any]] = []
    attempt_bodies: list[tuple[int, bytes]] = []
    start_total = monotonic()
    if opener_factory is None:
        opener_factory = lambda: urllib.request.build_opener(
            urllib.request.ProxyHandler(), NoRedirectHandler()
        )

    terminal_body: bytes | None = None
    terminal_status: int | None = None
    terminal_headers: dict[str, str] = {}
    failure_class: str | None = None
    state = "transport_terminal_failure"

    for attempt_index in range(1, MAXIMUM_TRANSPORT_ATTEMPTS + 1):
        request = urllib.request.Request(
            spec.endpoint,
            data=request_bytes,
            headers=provider_headers(spec, token, execution_id),
            method="POST",
        )
        attempt_start = monotonic()
        status_class = "transport_failure"
        status_code: int | None = None
        body: bytes | None = None
        response_headers: dict[str, str] = {}
        retryable = False
        retry_after = 0.0
        error_type: str | None = None
        try:
            opener = opener_factory()
            with opener.open(request, timeout=timeout_seconds) as response:
                body = response.read()
                status_code = int(response.getcode())
                response_headers = safe_response_headers(response.headers)
            status_class = "completed_body"
            state = "completed_body"
        except urllib.error.HTTPError as exc:
            status_code = int(exc.code)
            body = exc.read()
            response_headers = safe_response_headers(exc.headers)
            status_class = f"http_{status_code}"
            retryable = status_code in RETRYABLE_HTTP
            retry_after = retry_after_seconds(exc.headers)
            error_type = "http_error"
            state = "http_terminal_failure"
        except urllib.error.URLError as exc:
            status_class, retryable = classify_url_error(exc)
            error_type = type(exc.reason).__name__
            state = "transport_terminal_failure"
        except (socket.timeout, TimeoutError) as exc:
            status_class = "read_timeout"
            retryable = True
            error_type = type(exc).__name__
            state = "transport_terminal_failure"
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as exc:
            status_class = "connection_reset"
            retryable = True
            error_type = type(exc).__name__
            state = "transport_terminal_failure"
        except (ssl.SSLError, http.client.RemoteDisconnected) as exc:
            status_class = "tls_or_disconnected_transport_failure"
            retryable = True
            error_type = type(exc).__name__
            state = "transport_terminal_failure"
        elapsed_ms = round((monotonic() - attempt_start) * 1000)
        if body is not None:
            attempt_bodies.append((attempt_index, body))

        should_retry = (
            state != "completed_body"
            and retryable
            and attempt_index < MAXIMUM_TRANSPORT_ATTEMPTS
        )
        sleep_ms = 0
        if should_retry:
            base_delay = float(RETRY_DELAYS_SECONDS[attempt_index - 1])
            delay = max(base_delay, retry_after if status_code == 429 else 0.0)
            delay += deterministic_jitter_seconds(execution_id, attempt_index)
            sleep_start = monotonic()
            sleep(delay)
            sleep_ms = round((monotonic() - sleep_start) * 1000)
        attempts.append(
            {
                "attempt_index": attempt_index,
                "attempt_status_class": status_class,
                "attempt_elapsed_ms": elapsed_ms,
                "retry_sleep_after_attempt_ms": sleep_ms,
                "http_status": status_code,
                "request_ids": response_headers,
                "error_type": error_type,
            }
        )
        if not should_retry:
            terminal_body = body
            terminal_status = status_code
            terminal_headers = response_headers
            if state != "completed_body":
                failure_class = status_class
            break

    total_ms = round((monotonic() - start_total) * 1000)
    return DispatchResult(
        state=state,
        attempts=attempts,
        terminal_body=terminal_body,
        terminal_http_status=terminal_status,
        terminal_headers=terminal_headers,
        attempt_bodies=attempt_bodies,
        total_execution_elapsed_ms=total_ms,
        failure_class=failure_class,
    )


def preflight_request(spec: ProviderSpec) -> bytes:
    prompt = "Return exactly this JSON object: {\"ok\":true}"
    if spec.protocol == "openai_responses_v1":
        value = {
            "input": prompt,
            "max_output_tokens": 32,
            "model": spec.exact_alias,
            "stream": False,
            "temperature": 0,
            "top_p": 1.0,
        }
    else:
        value = {
            "max_tokens": 32,
            "messages": [{"content": prompt, "role": "user"}],
            "model": spec.exact_alias,
            "stream": False,
            "temperature": 0,
            "top_p": 1.0,
        }
    return canonical_json(value)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise IntegrityError(f"cannot load frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_modules(materialization: Path) -> tuple[Any, Any]:
    canonicalizer = load_module(
        materialization / "support" / "result_canonicalizer.py",
        "effectslice_frozen_result_canonicalizer",
    )
    verifier = load_module(
        FORWARD_ROOT / "materialization_verifier_v3.py",
        "effectslice_frozen_materialization_verifier",
    )
    return canonicalizer, verifier


def verify_full_anchor(materialization: Path) -> dict[str, Any]:
    materialization = windows_extended_path(materialization)
    _, verifier = frozen_modules(materialization)
    result = verifier.audit_materialization(materialization)
    require(result.get("status") == "passed", "frozen materialization audit failed")
    require(result.get("rows") == 1296, "frozen schedule row count changed")
    anchor = load_json(materialization / "final_anchor_manifest.json")
    require(
        anchor.get("bundle_sha256") == EXPECTED_ANCHOR_BUNDLE_SHA256,
        "frozen anchor bundle SHA changed",
    )
    return result


def scorer_contract_audit(materialization: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for task_dir in sorted((materialization / "tasks").iterdir(), key=lambda p: p.name):
        if not task_dir.is_dir():
            continue
        manifest = load_json(task_dir / "scorer_manifest.json")
        scorer = load_module(
            task_dir / "support" / "scorer.py",
            f"effectslice_scorer_audit_{task_dir.name.replace('-', '_')}",
        )
        _, expected = scorer.expected_registry("A")
        scored = scorer.score_outputs("A", expected)
        vector = scored.get("hard_contract_vector")
        ids = manifest.get("hard_contract_ids")
        require(isinstance(vector, list), f"scorer vector missing: {task_dir.name}")
        require(isinstance(ids, list), f"hard-contract IDs missing: {task_dir.name}")
        records.append(
            {
                "task_id": task_dir.name,
                "registered_hard_contract_id_count": len(ids),
                "frozen_scorer_vector_length": len(vector),
                "perfect_registry_vector": vector,
                "lengths_agree": len(ids) == len(vector),
            }
        )
    mismatch_count = sum(not record["lengths_agree"] for record in records)
    return {
        "schema_version": "effectslice-fg1-scorer-contract-audit.v1",
        "anchor_bundle_sha256": EXPECTED_ANCHOR_BUNDLE_SHA256,
        "task_count": len(records),
        "length_mismatch_count": mismatch_count,
        "records": records,
        "forward_execution_policy": {
            "frozen_scorer_output_preserved": True,
            "vector_components_relabelled_as_manifest_ids": False,
            "runtime_safety_and_input_mutation_failures_force_both_components_false": True,
            "failure_mode_limitation": (
                "The two frozen scorer components support totality/exactness and F/I "
                "agreement, but are not interpreted as the four named manifest IDs."
            ),
            "admission_impact": (
                "With 64 cases and a 0.99 threshold, one error yields 63/64 < 0.99; "
                "therefore operational success still requires all 64 exact outputs."
            ),
        },
    }


def freeze_contract(materialization: Path, contract_dir: Path) -> dict[str, Any]:
    manifest_path = contract_dir / "contract_manifest.json"
    if manifest_path.exists():
        verify_contract(materialization, contract_dir)
        return load_json(manifest_path)
    if contract_dir.exists() and any(contract_dir.iterdir()):
        raise IntegrityError("nonempty execution contract directory lacks a manifest")
    verify_full_anchor(materialization)
    audit = scorer_contract_audit(materialization)
    schedule_sha = sha256_file(materialization / "global_remote_schedule.json")
    source_records = []
    for path in (Path(__file__).resolve(), WORKER_PATH.resolve()):
        source_records.append(
            {
                "path": path.name,
                "sha256": sha256_file(path),
            }
        )
    test_path = FORWARD_ROOT / "tests" / "test_remote_execution_runner.py"
    if test_path.exists():
        source_records.append(
            {
                "path": f"tests/{test_path.name}",
                "sha256": sha256_file(test_path),
            }
        )
    contract = {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": utc_now(),
        "anchor_bundle_sha256": EXPECTED_ANCHOR_BUNDLE_SHA256,
        "schedule_sha256": schedule_sha,
        "registered_rows": 1296,
        "provider_calls_started": False,
        "source_records": source_records,
        "provider_slots": [
            {
                "model_slot_id": item.slot_id,
                "exact_alias": item.exact_alias,
                "endpoint": item.endpoint,
                "protocol": item.protocol,
            }
            for item in PROVIDER_SPECS.values()
        ],
        "transport_policy": {
            "timeout_seconds": TIMEOUT_SECONDS,
            "maximum_transport_attempts": MAXIMUM_TRANSPORT_ATTEMPTS,
            "retry_delays_seconds": list(RETRY_DELAYS_SECONDS),
            "retryable_http_statuses": sorted(RETRYABLE_HTTP),
            "deterministic_jitter_ms": [0, 1000],
            "semantic_rerun": "forbidden",
        },
        "execution_isolation": {
            "fresh_http_connection_per_attempt": True,
            "fresh_model_conversation_per_row": True,
            "worker_python_isolated_mode": True,
            "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
            "sanitized_worker_environment": True,
            "ast_safety_gate": True,
            "restricted_builtins": True,
            "no_worker_network_or_secret_access": True,
        },
        "credential_policy": {
            "runtime_memory_only": True,
            "source_document_values_never_logged": True,
            "shell_argument_contains_credential": False,
            "tracked_credential_value": False,
        },
        "scorer_contract_audit_path": "scorer_contract_audit.json",
        "scorer_contract_audit_sha256": None,
    }
    contract_dir.mkdir(parents=True, exist_ok=True)
    audit_path = contract_dir / "scorer_contract_audit.json"
    atomic_json(audit_path, audit)
    contract["scorer_contract_audit_sha256"] = sha256_file(audit_path)
    contract_path = contract_dir / "execution_contract.json"
    atomic_json(contract_path, contract)
    manifest = {
        "schema_version": "effectslice-fg1-remote-execution-contract-manifest.v1",
        "anchor_bundle_sha256": EXPECTED_ANCHOR_BUNDLE_SHA256,
        "files": [
            {"path": audit_path.name, "sha256": sha256_file(audit_path)},
            {"path": contract_path.name, "sha256": sha256_file(contract_path)},
        ],
    }
    atomic_json(manifest_path, manifest)
    return manifest


def verify_contract(materialization: Path, contract_dir: Path) -> dict[str, Any]:
    manifest = load_json(contract_dir / "contract_manifest.json")
    require(
        manifest.get("anchor_bundle_sha256") == EXPECTED_ANCHOR_BUNDLE_SHA256,
        "execution contract anchor binding changed",
    )
    for record in manifest.get("files", []):
        path = contract_dir / record["path"]
        require(path.is_file(), f"missing execution contract file: {record['path']}")
        require(
            sha256_file(path) == record["sha256"],
            f"execution contract file changed: {record['path']}",
        )
    contract = load_json(contract_dir / "execution_contract.json")
    require(contract.get("schema_version") == SCHEMA_VERSION, "executor schema changed")
    require(
        contract.get("schedule_sha256")
        == sha256_file(materialization / "global_remote_schedule.json"),
        "schedule changed after executor freeze",
    )
    for record in contract.get("source_records", []):
        path = FORWARD_ROOT / record["path"]
        require(path.is_file(), f"missing frozen executor source: {record['path']}")
        require(
            sha256_file(path) == record["sha256"],
            f"executor source changed after freeze: {record['path']}",
        )
    return contract


class RowResolver:
    def __init__(self, materialization: Path):
        self.materialization = windows_extended_path(materialization)
        self._candidate_cache: dict[str, dict[str, dict[str, Any]]] = {}

    def candidates(self, task_id: str) -> dict[str, dict[str, Any]]:
        if task_id not in self._candidate_cache:
            manifest = load_json(
                self.materialization / "tasks" / task_id / "candidate_manifest.json"
            )
            self._candidate_cache[task_id] = {
                item["candidate_id"]: item for item in manifest["candidates"]
            }
        return self._candidate_cache[task_id]

    def resolve(self, row: dict[str, Any]) -> RowInputs:
        task_id = str(row["task_id"])
        execution_id = str(row["execution_id"])
        slot_id = str(row["model_slot_id"])
        registry_id = str(row["registry_id"])
        task_dir = self.materialization / "tasks" / task_id
        candidate = self.candidates(task_id)[str(row["candidate_id"])]
        paths_and_hashes = [
            (task_dir / "task_scaffold.md", row["task_scaffold_sha256"]),
            (
                task_dir / "public_fixture_manifest.json",
                row["fixture_manifest_sha256"],
            ),
            (task_dir / "fixtures" / f"{registry_id}.json", row["fixture_payload_sha256"]),
            (
                task_dir / f"private_registry_{registry_id}_manifest.json",
                row["private_registry_manifest_sha256"],
            ),
            (task_dir / "scorer_manifest.json", row["scorer_manifest_sha256"]),
            (task_dir / candidate["artifact_path"], row["candidate_artifact_sha256"]),
            (
                task_dir / "payloads" / f"{execution_id}.txt",
                row["canonical_model_visible_payload_sha256"],
            ),
            (
                task_dir / "requests" / f"{execution_id}.json",
                row["serialized_wire_request_sha256"],
            ),
            (task_dir / "decoding" / f"{slot_id}.json", row["decoding_config_sha256"]),
        ]
        for path, expected in paths_and_hashes:
            require(path.is_file(), f"missing frozen row input: {path}")
            require(
                sha256_file(path) == expected,
                f"frozen row input SHA mismatch: {execution_id}:{path.name}",
            )
        request_path = task_dir / "requests" / f"{execution_id}.json"
        request_bytes = request_path.read_bytes()
        request_value = json.loads(request_bytes.decode("utf-8", errors="strict"))
        spec = PROVIDER_SPECS[slot_id]
        require(request_value.get("model") == spec.exact_alias, "request alias mismatch")
        require(request_value.get("stream") is False, "streaming request is forbidden")
        return RowInputs(
            task_dir=task_dir,
            request_path=request_path,
            request_bytes=request_bytes,
            payload_path=task_dir / "payloads" / f"{execution_id}.txt",
            fixture_path=task_dir / "fixtures" / f"{registry_id}.json",
            scorer_path=task_dir / "support" / "scorer.py",
            candidate_path=task_dir / candidate["artifact_path"],
            candidate_tokens=int(candidate["rendered_token_count"]),
        )


def strict_submission(text: str) -> str:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(text, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or set(value) != {"implementation"}:
        raise ValueError("submission must be one JSON object with exactly implementation")
    source = value["implementation"]
    if not isinstance(source, str) or not source.strip():
        raise ValueError("implementation must be a nonempty string")
    return source


def normalize_output(text: str) -> bytes:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", normalized).encode("utf-8")


def run_worker(
    implementation: str,
    cases: list[dict[str, Any]],
    run_dir: Path,
    execution_id: str,
) -> dict[str, Any]:
    del run_dir
    workspace = Path(tempfile.mkdtemp(prefix=f"effectslice-{execution_id[:20]}-"))
    request = canonical_json({"implementation": implementation, "cases": cases})
    environment = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
        "WINDIR": os.environ.get("WINDIR", r"C:\Windows"),
        "TEMP": str(workspace),
        "TMP": str(workspace),
    }
    try:
        completed = subprocess.run(
            [sys.executable, "-I", str(WORKER_PATH)],
            input=request,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
            env=environment,
            timeout=WORKER_TIMEOUT_SECONDS,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except subprocess.TimeoutExpired:
        return {"status": "worker_timeout", "reason": "bounded worker timed out"}
    finally:
        if workspace.exists():
            shutil.rmtree(workspace)
    if completed.returncode != 0:
        return {
            "status": "worker_failure",
            "reason": f"worker exit code {completed.returncode}",
            "stderr_sha256": sha256_bytes(completed.stderr),
        }
    try:
        return json.loads(completed.stdout.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "status": "worker_failure",
            "reason": f"invalid worker output: {type(exc).__name__}",
            "stdout_sha256": sha256_bytes(completed.stdout),
            "stderr_sha256": sha256_bytes(completed.stderr),
        }


def score_worker_result(
    row: dict[str, Any], inputs: RowInputs, worker: dict[str, Any]
) -> tuple[float, list[bool], dict[str, Any]]:
    outputs = worker.get("outputs") if worker.get("status") == "completed" else []
    if not isinstance(outputs, list):
        outputs = []
    scorer = load_module(
        inputs.scorer_path,
        f"effectslice_scorer_{row['execution_id'].replace('-', '_')}",
    )
    scored = scorer.score_outputs(str(row["registry_id"]), outputs)
    private_score = float(scored["private_score"])
    vector = scored["hard_contract_vector"]
    require(
        isinstance(vector, list)
        and len(vector) == 2
        and all(isinstance(value, bool) for value in vector),
        "frozen scorer vector is not the registered executable shape",
    )
    safety_ok = (
        worker.get("status") == "completed"
        and not worker.get("errors")
        and not worker.get("mutated_case_ids")
    )
    effective_vector = [bool(value and safety_ok) for value in vector]
    evidence = {
        "schema_version": "effectslice-fg1-row-scoring-evidence.v1",
        "execution_id": row["execution_id"],
        "task_id": row["task_id"],
        "registry_id": row["registry_id"],
        "worker_status": worker.get("status"),
        "outputs": outputs,
        "errors": worker.get("errors", []),
        "mutated_case_ids": worker.get("mutated_case_ids", []),
        "private_score": private_score,
        "frozen_scorer_vector": vector,
        "effective_safety_vector": effective_vector,
    }
    return private_score, effective_vector, evidence


def response_projection(
    materialization: Path, slot_id: str, raw_body: bytes
) -> tuple[dict[str, Any], bytes, Any, tuple[Any, Any, Any, Any], str]:
    text = raw_body.decode("utf-8", errors="strict")
    response = json.loads(text)
    require(isinstance(response, dict), "provider response must be a JSON object")
    canonicalizer, _ = frozen_modules(materialization)
    output, finish, usage = canonicalizer._response_projection(slot_id, response)
    require(isinstance(output, str), "provider canonical output is not a string")
    termination = canonicalizer._termination(slot_id, finish, "completed_body")
    return response, normalize_output(output), finish, usage, termination


def normalized_usage(
    usage: tuple[Any, Any, Any, Any] | None,
    missing_reason: str,
) -> tuple[int | None, int | None, int | None, int | None, str | None]:
    if usage is None:
        return None, None, None, None, missing_reason
    input_tokens, output_tokens, total_tokens, cached_tokens = usage
    core = (input_tokens, output_tokens, total_tokens)
    valid_core = all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in core
    )
    valid_cached = cached_tokens is None or (
        isinstance(cached_tokens, int)
        and not isinstance(cached_tokens, bool)
        and cached_tokens >= 0
    )
    if valid_core and valid_cached and total_tokens == input_tokens + output_tokens:
        return input_tokens, output_tokens, total_tokens, cached_tokens, None
    if all(value is None for value in core):
        return None, None, None, None, "provider_omitted_usage"
    return None, None, None, None, "malformed_usage_tuple_or_integrity_failure"


def artifact_endpoints(inputs: RowInputs) -> dict[str, int]:
    return {
        "candidate_artifact_bytes": inputs.candidate_path.stat().st_size,
        "candidate_artifact_cl100k_tokens": inputs.candidate_tokens,
        "canonical_model_visible_payload_bytes": inputs.payload_path.stat().st_size,
    }


def unavailable_row(row: dict[str, Any], inputs: RowInputs) -> dict[str, Any]:
    return {
        "execution_id": row["execution_id"],
        "terminal_outcome": "provider_or_model_unavailable",
        "termination_reason": "not_dispatched",
        "provider_finish_reason": None,
        "row_valid": False,
        "condition_success": None,
        "private_score": None,
        "raw_response_path": None,
        "raw_response_sha256": None,
        "canonical_output_path": None,
        "canonical_output_sha256": None,
        "hard_contract_vector": None,
        "attempts": [],
        **artifact_endpoints(inputs),
        "provider_reported_input_tokens": None,
        "provider_reported_output_tokens": None,
        "provider_reported_total_tokens": None,
        "provider_reported_cached_input_tokens": None,
        "provider_usage_missing_reason": "not_dispatched",
        "terminal_attempt_elapsed_ms": None,
        "total_execution_elapsed_ms": None,
        "retry_sleep_elapsed_ms": None,
        "retry_overhead_ms": None,
    }


def dispatched_base(
    row: dict[str, Any], inputs: RowInputs, dispatch: DispatchResult
) -> dict[str, Any]:
    attempts = dispatch.row_attempts()
    terminal_ms = attempts[-1]["attempt_elapsed_ms"]
    total_ms = max(dispatch.total_execution_elapsed_ms, terminal_ms)
    sleep_ms = sum(item["retry_sleep_after_attempt_ms"] for item in attempts)
    return {
        "execution_id": row["execution_id"],
        "attempts": attempts,
        **artifact_endpoints(inputs),
        "terminal_attempt_elapsed_ms": terminal_ms,
        "total_execution_elapsed_ms": total_ms,
        "retry_sleep_elapsed_ms": sleep_ms,
        "retry_overhead_ms": total_ms - terminal_ms,
    }


def transport_failure_row(
    row: dict[str, Any], inputs: RowInputs, dispatch: DispatchResult
) -> dict[str, Any]:
    return {
        **dispatched_base(row, inputs, dispatch),
        "terminal_outcome": "transport_terminal_failure",
        "termination_reason": "transport_failure",
        "provider_finish_reason": None,
        "row_valid": False,
        "condition_success": None,
        "private_score": None,
        "raw_response_path": None,
        "raw_response_sha256": None,
        "canonical_output_path": None,
        "canonical_output_sha256": None,
        "hard_contract_vector": None,
        "provider_reported_input_tokens": None,
        "provider_reported_output_tokens": None,
        "provider_reported_total_tokens": None,
        "provider_reported_cached_input_tokens": None,
        "provider_usage_missing_reason": "transport_failure_no_usage",
    }


def persist_attempts(
    run_dir: Path,
    execution_id: str,
    dispatch: DispatchResult,
    forbidden_values: Iterable[str] = (),
) -> None:
    forbidden_bytes = [value.encode("utf-8") for value in forbidden_values if value]
    for _, body in dispatch.attempt_bodies:
        require(
            not any(secret in body for secret in forbidden_bytes),
            "provider body reflected a credential; refusing to persist it",
        )
    record = {
        "schema_version": "effectslice-fg1-attempt-log.v1",
        "execution_id": execution_id,
        "state": dispatch.state,
        "terminal_http_status": dispatch.terminal_http_status,
        "terminal_request_ids": dispatch.terminal_headers,
        "failure_class": dispatch.failure_class,
        "attempts": dispatch.attempts,
        "credential_value_recorded": False,
    }
    atomic_json(run_dir / "attempts" / f"{execution_id}.json", record)
    for attempt_index, body in dispatch.attempt_bodies:
        atomic_write(
            run_dir / "attempt_bodies" / execution_id / f"attempt_{attempt_index}.bin",
            body,
        )


def validate_result_row(
    materialization: Path, row: dict[str, Any], model_slot_id: str
) -> None:
    contract = load_json(
        windows_extended_path(materialization).parent
        / "preregistration_remote_only_2026-07-22"
        / "materialization_contract.json"
    )
    result_contract = contract["result_canonicalization_contract"]
    _, verifier = frozen_modules(materialization)
    verifier._validate_registered_schema(row, result_contract["result_row_json_schema"])
    verifier._validate_result_row_semantics(row, row["execution_id"], model_slot_id)


def write_row(run_dir: Path, row: dict[str, Any], value: dict[str, Any], materialization: Path) -> None:
    validate_result_row(materialization, value, str(row["model_slot_id"]))
    atomic_json(run_dir / "rows" / f"{row['execution_id']}.json", value, pretty=False)


def execute_row(
    materialization: Path,
    run_dir: Path,
    row: dict[str, Any],
    inputs: RowInputs,
    token: str,
) -> dict[str, Any]:
    execution_id = str(row["execution_id"])
    slot_id = str(row["model_slot_id"])
    spec = PROVIDER_SPECS[slot_id]
    dispatch = dispatch_request(spec, token, execution_id, inputs.request_bytes)
    persist_attempts(run_dir, execution_id, dispatch, (token,))
    if dispatch.state == "transport_terminal_failure":
        return transport_failure_row(row, inputs, dispatch)

    raw_body = dispatch.terminal_body or b""
    raw_path = run_dir / "raw" / f"{execution_id}.json"
    atomic_write(raw_path, raw_body)
    base = dispatched_base(row, inputs, dispatch)
    raw_fields = {
        "raw_response_path": f"raw/{execution_id}.json",
        "raw_response_sha256": sha256_bytes(raw_body),
    }
    if dispatch.state == "http_terminal_failure":
        usage = normalized_usage(None, "malformed_usage_tuple_or_integrity_failure")
        return {
            **base,
            **raw_fields,
            "terminal_outcome": "integrity_or_digest_failure",
            "termination_reason": "provider_stop",
            "provider_finish_reason": None,
            "row_valid": False,
            "condition_success": None,
            "private_score": None,
            "canonical_output_path": None,
            "canonical_output_sha256": None,
            "hard_contract_vector": None,
            "provider_reported_input_tokens": usage[0],
            "provider_reported_output_tokens": usage[1],
            "provider_reported_total_tokens": usage[2],
            "provider_reported_cached_input_tokens": usage[3],
            "provider_usage_missing_reason": usage[4],
        }

    canonical_bytes: bytes | None = None
    finish: Any = None
    usage_tuple: tuple[Any, Any, Any, Any] | None = None
    termination = "provider_stop"
    projection_error: str | None = None
    try:
        _, canonical_bytes, finish, usage_tuple, termination = response_projection(
            materialization, slot_id, raw_body
        )
    except (IntegrityError, KeyError, IndexError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        projection_error = f"{type(exc).__name__}: {str(exc)[:500]}"
    usage = normalized_usage(usage_tuple, "provider_omitted_usage")
    canonical_fields: dict[str, Any]
    if canonical_bytes is None:
        canonical_fields = {
            "canonical_output_path": None,
            "canonical_output_sha256": None,
        }
    else:
        canonical_path = run_dir / "canonical" / f"{execution_id}.txt"
        atomic_write(canonical_path, canonical_bytes)
        canonical_fields = {
            "canonical_output_path": f"canonical/{execution_id}.txt",
            "canonical_output_sha256": sha256_bytes(canonical_bytes),
        }

    if projection_error is not None or canonical_bytes is None:
        atomic_json(
            run_dir / "scoring" / f"{execution_id}.json",
            {
                "schema_version": "effectslice-fg1-row-scoring-evidence.v1",
                "execution_id": execution_id,
                "projection_error": projection_error,
            },
        )
        return {
            **base,
            **raw_fields,
            **canonical_fields,
            "terminal_outcome": "malformed_or_no_submission",
            "termination_reason": termination,
            "provider_finish_reason": finish,
            "row_valid": True,
            "condition_success": False,
            "private_score": 0.0,
            "hard_contract_vector": None,
            "provider_reported_input_tokens": usage[0],
            "provider_reported_output_tokens": usage[1],
            "provider_reported_total_tokens": usage[2],
            "provider_reported_cached_input_tokens": usage[3],
            "provider_usage_missing_reason": usage[4],
        }

    canonical_text = canonical_bytes.decode("utf-8")
    try:
        implementation = strict_submission(canonical_text)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        atomic_json(
            run_dir / "scoring" / f"{execution_id}.json",
            {
                "schema_version": "effectslice-fg1-row-scoring-evidence.v1",
                "execution_id": execution_id,
                "submission_error": f"{type(exc).__name__}: {str(exc)[:500]}",
            },
        )
        return {
            **base,
            **raw_fields,
            **canonical_fields,
            "terminal_outcome": "malformed_or_no_submission",
            "termination_reason": termination,
            "provider_finish_reason": finish,
            "row_valid": True,
            "condition_success": False,
            "private_score": 0.0,
            "hard_contract_vector": None,
            "provider_reported_input_tokens": usage[0],
            "provider_reported_output_tokens": usage[1],
            "provider_reported_total_tokens": usage[2],
            "provider_reported_cached_input_tokens": usage[3],
            "provider_usage_missing_reason": usage[4],
        }

    private_scorer = load_module(
        inputs.scorer_path,
        f"effectslice_private_cases_{execution_id.replace('-', '_')}",
    )
    cases, _ = private_scorer.expected_registry(str(row["registry_id"]))
    require(len(cases) == 64, "frozen private registry must contain 64 cases")
    worker = run_worker(implementation, cases, run_dir, execution_id)
    if worker.get("status") == "invalid_submission":
        atomic_json(
            run_dir / "scoring" / f"{execution_id}.json",
            {
                "schema_version": "effectslice-fg1-row-scoring-evidence.v1",
                "execution_id": execution_id,
                "worker_status": worker.get("status"),
                "reason": worker.get("reason"),
            },
        )
        return {
            **base,
            **raw_fields,
            **canonical_fields,
            "terminal_outcome": "malformed_or_no_submission",
            "termination_reason": termination,
            "provider_finish_reason": finish,
            "row_valid": True,
            "condition_success": False,
            "private_score": 0.0,
            "hard_contract_vector": None,
            "provider_reported_input_tokens": usage[0],
            "provider_reported_output_tokens": usage[1],
            "provider_reported_total_tokens": usage[2],
            "provider_reported_cached_input_tokens": usage[3],
            "provider_usage_missing_reason": usage[4],
        }

    private_score, vector, evidence = score_worker_result(row, inputs, worker)
    atomic_gzip_json(run_dir / "scoring" / f"{execution_id}.json.gz", evidence)
    if not all(vector):
        outcome = "hard_contract_failure"
    elif private_score < PRIVATE_SCORE_THRESHOLD:
        outcome = "score_shortfall"
    else:
        outcome = "operational_success"
    return {
        **base,
        **raw_fields,
        **canonical_fields,
        "terminal_outcome": outcome,
        "termination_reason": termination,
        "provider_finish_reason": finish,
        "row_valid": True,
        "condition_success": outcome == "operational_success",
        "private_score": private_score,
        "hard_contract_vector": vector,
        "provider_reported_input_tokens": usage[0],
        "provider_reported_output_tokens": usage[1],
        "provider_reported_total_tokens": usage[2],
        "provider_reported_cached_input_tokens": usage[3],
        "provider_usage_missing_reason": usage[4],
    }


def preflight_status_from_dispatch(
    materialization: Path, slot_id: str, dispatch: DispatchResult
) -> tuple[str, str | None]:
    if dispatch.state == "transport_terminal_failure":
        return "transport_terminal_failure", dispatch.failure_class
    if dispatch.state == "http_terminal_failure":
        status = dispatch.terminal_http_status
        if status in {401, 403}:
            return "authentication_rejected", f"http_{status}"
        if status in {404, 422}:
            return "provider_or_model_unavailable", f"http_{status}"
        return "request_format_rejected", f"http_{status}"
    try:
        response_projection(materialization, slot_id, dispatch.terminal_body or b"")
    except Exception as exc:
        return "response_format_invalid", type(exc).__name__
    return "available", None


def initialize_run_manifest(
    run_dir: Path, contract_dir: Path, credential_metadata: dict[str, Any]
) -> dict[str, Any]:
    path = run_dir / "run_manifest.json"
    if path.exists():
        value = load_json(path)
        require(
            value.get("anchor_bundle_sha256") == EXPECTED_ANCHOR_BUNDLE_SHA256,
            "run manifest anchor mismatch",
        )
        return value
    value = {
        "schema_version": "effectslice-fg1-remote-run.v1",
        "created_at_utc": utc_now(),
        "anchor_bundle_sha256": EXPECTED_ANCHOR_BUNDLE_SHA256,
        "execution_contract_manifest_sha256": sha256_file(
            contract_dir / "contract_manifest.json"
        ),
        "registered_rows": 1296,
        "provider_calls_started": False,
        "credential_sources": credential_metadata,
        "credential_values_recorded": False,
    }
    atomic_json(path, value)
    return value


def verify_preflight_result(run_dir: Path, value: dict[str, Any]) -> None:
    slot_id = value.get("model_slot_id")
    require(slot_id in PROVIDER_SPECS, "unknown preflight model slot")
    require(
        value.get("exact_alias") == PROVIDER_SPECS[str(slot_id)].exact_alias,
        "preflight exact alias changed",
    )
    require(value.get("logical_request_count") == 1, "preflight logical request count changed")
    require(value.get("credential_value_recorded") is False, "preflight recorded a credential")
    raw_path = value.get("raw_response_path")
    raw_sha = value.get("raw_response_sha256")
    require((raw_path is None) == (raw_sha is None), "preflight raw path/hash mismatch")
    if raw_path is not None:
        path = run_dir / str(raw_path)
        require(path.is_file(), "preflight raw response is missing")
        require(sha256_file(path) == raw_sha, "preflight raw response changed")


def run_preflight(
    materialization: Path,
    contract_dir: Path,
    run_dir: Path,
    docs_dir: Path,
) -> dict[str, Any]:
    verify_contract(materialization, contract_dir)
    verify_full_anchor(materialization)
    credentials, metadata = load_credentials(docs_dir)
    manifest = initialize_run_manifest(run_dir, contract_dir, metadata)
    results: list[dict[str, Any]] = []
    for slot_id, spec in PROVIDER_SPECS.items():
        final_path = run_dir / "preflight" / f"{slot_id}.json"
        started_path = run_dir / "preflight" / f"{slot_id}.started.json"
        if final_path.exists():
            result = load_json(final_path)
            require(result.get("model_slot_id") == slot_id, "preflight slot mismatch")
            verify_preflight_result(run_dir, result)
            results.append(result)
            continue
        if started_path.exists():
            raise ExecutionError(
                f"ambiguous preflight already started for {slot_id}; refusing a second logical request"
            )
        atomic_json(
            started_path,
            {
                "schema_version": "effectslice-fg1-preflight-start.v1",
                "model_slot_id": slot_id,
                "exact_alias": spec.exact_alias,
                "started_at_utc": utc_now(),
                "maximum_logical_requests": 1,
            },
        )
        manifest["provider_calls_started"] = True
        manifest["provider_calls_started_at_utc"] = manifest.get(
            "provider_calls_started_at_utc", utc_now()
        )
        atomic_json(run_dir / "run_manifest.json", manifest)
        dispatch = dispatch_request(
            spec,
            credentials[slot_id],
            f"fg1-preflight-{slot_id}",
            preflight_request(spec),
        )
        persist_attempts(
            run_dir / "preflight",
            f"preflight-{slot_id}",
            dispatch,
            (credentials[slot_id],),
        )
        if dispatch.terminal_body is not None:
            raw_relative = f"preflight/raw/{slot_id}.json"
            atomic_write(run_dir / "preflight" / "raw" / f"{slot_id}.json", dispatch.terminal_body)
            raw_sha = sha256_bytes(dispatch.terminal_body)
        else:
            raw_relative = None
            raw_sha = None
        status, reason = preflight_status_from_dispatch(materialization, slot_id, dispatch)
        result = {
            "schema_version": "effectslice-fg1-live-model-preflight.v1",
            "model_slot_id": slot_id,
            "exact_alias": spec.exact_alias,
            "status": status,
            "reason": reason,
            "logical_request_count": 1,
            "transport_attempt_count": len(dispatch.attempts),
            "raw_response_path": raw_relative,
            "raw_response_sha256": raw_sha,
            "credential_value_recorded": False,
            "completed_at_utc": utc_now(),
        }
        atomic_json(final_path, result)
        verify_preflight_result(run_dir, result)
        results.append(result)
    summary = {
        "schema_version": "effectslice-fg1-live-model-preflight-summary.v1",
        "completed_at_utc": utc_now(),
        "slots": results,
        "available_slot_count": sum(item["status"] == "available" for item in results),
        "credential_values_recorded": False,
    }
    atomic_json(run_dir / "preflight_summary.json", summary)
    return summary


def load_preflight_map(run_dir: Path) -> dict[str, str]:
    summary = load_json(run_dir / "preflight_summary.json")
    result: dict[str, str] = {}
    for item in summary["slots"]:
        slot_id = str(item["model_slot_id"])
        final = load_json(run_dir / "preflight" / f"{slot_id}.json")
        verify_preflight_result(run_dir, final)
        require(final.get("status") == item.get("status"), "preflight summary status changed")
        result[slot_id] = str(item["status"])
    return result


def validate_existing_row(
    materialization: Path, path: Path, scheduled: dict[str, Any]
) -> None:
    value = load_json(path)
    require(value.get("execution_id") == scheduled["execution_id"], "resume row ID mismatch")
    validate_result_row(materialization, value, str(scheduled["model_slot_id"]))


def progress_summary(run_dir: Path, schedule: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    completed = 0
    by_slot: dict[str, int] = {}
    for row in schedule:
        path = run_dir / "rows" / f"{row['execution_id']}.json"
        if not path.exists():
            continue
        value = load_json(path)
        completed += 1
        outcome = str(value["terminal_outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        slot = str(row["model_slot_id"])
        by_slot[slot] = by_slot.get(slot, 0) + 1
    return {
        "schema_version": "effectslice-fg1-remote-progress.v1",
        "updated_at_utc": utc_now(),
        "registered_rows": len(schedule),
        "terminal_rows": completed,
        "remaining_rows": len(schedule) - completed,
        "terminal_outcomes": dict(sorted(outcomes.items())),
        "terminal_rows_by_model_slot": dict(sorted(by_slot.items())),
    }


def run_schedule(
    materialization: Path,
    contract_dir: Path,
    run_dir: Path,
    docs_dir: Path,
    max_new_rows: int | None,
) -> dict[str, Any]:
    verify_contract(materialization, contract_dir)
    verify_full_anchor(materialization)
    credentials, _ = load_credentials(docs_dir)
    preflight = load_preflight_map(run_dir)
    require(set(preflight) == set(PROVIDER_SPECS), "preflight slot set is incomplete")
    schedule_doc = load_json(materialization / "global_remote_schedule.json")
    schedule = schedule_doc["rows"]
    resolver = RowResolver(materialization)
    new_rows = 0
    for row in schedule:
        row_path = run_dir / "rows" / f"{row['execution_id']}.json"
        dispatch_started = run_dir / "dispatch" / f"{row['execution_id']}.started.json"
        dispatch_terminal = run_dir / "dispatch" / f"{row['execution_id']}.terminal.json"
        if row_path.exists():
            validate_existing_row(materialization, row_path, row)
            if dispatch_started.exists() and not dispatch_terminal.exists():
                existing = load_json(row_path)
                atomic_json(
                    dispatch_terminal,
                    {
                        "schema_version": "effectslice-fg1-dispatch-terminal.v1",
                        "execution_id": row["execution_id"],
                        "terminal_outcome": existing["terminal_outcome"],
                        "result_row_sha256": sha256_file(row_path),
                        "recovered_from_terminal_row": True,
                    },
                )
            continue
        if max_new_rows is not None and new_rows >= max_new_rows:
            break
        inputs = resolver.resolve(row)
        if preflight[str(row["model_slot_id"])] != "available":
            result = unavailable_row(row, inputs)
        else:
            if dispatch_started.exists():
                raise ExecutionError(
                    f"ambiguous dispatched row lacks a terminal result: {row['execution_id']}"
                )
            atomic_json(
                dispatch_started,
                {
                    "schema_version": "effectslice-fg1-dispatch-start.v1",
                    "execution_id": row["execution_id"],
                    "model_slot_id": row["model_slot_id"],
                    "serialized_wire_request_sha256": row[
                        "serialized_wire_request_sha256"
                    ],
                    "started_at_utc": utc_now(),
                    "semantic_rerun_allowed": False,
                },
            )
            result = execute_row(
                materialization,
                run_dir,
                row,
                inputs,
                credentials[str(row["model_slot_id"])],
            )
        write_row(run_dir, row, result, materialization)
        if dispatch_started.exists():
            atomic_json(
                dispatch_terminal,
                {
                    "schema_version": "effectslice-fg1-dispatch-terminal.v1",
                    "execution_id": row["execution_id"],
                    "terminal_outcome": result["terminal_outcome"],
                    "result_row_sha256": sha256_file(row_path),
                    "recovered_from_terminal_row": False,
                },
            )
        new_rows += 1
        if new_rows % 5 == 0:
            atomic_json(run_dir / "progress.json", progress_summary(run_dir, schedule))
            print(
                f"terminal_rows={sum(1 for item in schedule if (run_dir / 'rows' / (item['execution_id'] + '.json')).exists())}/1296",
                flush=True,
            )
    progress = progress_summary(run_dir, schedule)
    atomic_json(run_dir / "progress.json", progress)
    return progress


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("audit-credentials", "freeze-contract", "verify", "preflight", "run"),
    )
    parser.add_argument("--materialization", type=Path, default=DEFAULT_MATERIALIZATION)
    parser.add_argument("--contract-dir", type=Path, default=DEFAULT_CONTRACT_DIR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--docs-dir", type=Path)
    parser.add_argument("--max-new-rows", type=int)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    materialization = windows_extended_path(args.materialization)
    contract_dir = windows_extended_path(args.contract_dir)
    run_dir = windows_extended_path(args.run_dir)
    if args.command == "audit-credentials":
        if args.docs_dir is None:
            raise ExecutionError("--docs-dir is required")
        _, metadata = load_credentials(args.docs_dir.resolve())
        print(json.dumps(metadata, sort_keys=True, ensure_ascii=False))
        return 0
    if args.command == "freeze-contract":
        value = freeze_contract(materialization, contract_dir)
    elif args.command == "verify":
        value = {
            "contract": verify_contract(materialization, contract_dir)["schema_version"],
            "anchor": verify_full_anchor(materialization),
        }
    elif args.command == "preflight":
        if args.docs_dir is None:
            raise ExecutionError("--docs-dir is required")
        value = run_preflight(
            materialization, contract_dir, run_dir, args.docs_dir.resolve()
        )
    else:
        if args.docs_dir is None:
            raise ExecutionError("--docs-dir is required")
        if args.max_new_rows is not None and args.max_new_rows <= 0:
            raise ExecutionError("--max-new-rows must be positive")
        value = run_schedule(
            materialization,
            contract_dir,
            run_dir,
            args.docs_dir.resolve(),
            args.max_new_rows,
        )
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExecutionError, IntegrityError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
