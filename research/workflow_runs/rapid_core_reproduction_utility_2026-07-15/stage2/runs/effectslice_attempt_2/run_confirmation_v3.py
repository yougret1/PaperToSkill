from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Callable, Mapping


RUN_ROOT = Path(__file__).resolve().parent

from effectslice.confirmation_v3 import balanced_schedule
from run_toolformer_filter_confirmation_v3 import (
    load_and_verify_family as load_toolformer_family,
)
from run_toolformer_filter_confirmation_v3 import run_bundle as run_toolformer_bundle


PROGRESS_SCHEMA = "effectslice-confirmation-v3-progress.v1"
PAIR_SCHEMA = "effectslice-confirmation-v3-pair.v1"
RUN_REPORT_SCHEMA = "effectslice-confirmation-v3-run-report.v1"
JOURNAL_SCHEMA = "effectslice-confirmation-v3-terminal-journal.v1"
REGISTERED_V3 = "registered_final_only_confirmation_v3"
CONDITIONS = ("B", "F", "S")
CONTROL_SPECS = {
    "identity": {
        "schedule_seed": 2026071801,
        "replicate_count": 6,
        "strict_subset": False,
        "calibration_role": "identity_instrumentation_only",
        "admission_rule": "descriptive_only",
        "required_joint_events_for_admission": None,
    },
    "planted": {
        "schedule_seed": 2026071802,
        "replicate_count": 18,
        "strict_subset": True,
        "calibration_role": "planted_redundancy_positive_control",
        "admission_rule": "all_registered_joint_events",
        "required_joint_events_for_admission": 18,
    },
}
DEFAULT_RUNNERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "toolformer_filter": run_toolformer_bundle,
}
DEFAULT_FAMILY_LOADER = load_toolformer_family
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class IncompleteBundle(ValueError):
    """An existing registered output is not a completed write-once bundle."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise ValueError(f"{label} must be {expected!r}")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _resolve_execution_binding(
    family_path: Path,
    family: Mapping[str, Any],
    *,
    name: str,
    actual_path: Path,
) -> None:
    bindings = family.get("bindings")
    if not isinstance(bindings, dict):
        raise ValueError("family bindings must be an object")
    record = bindings.get(name)
    if not isinstance(record, dict):
        raise ValueError(f"{name} binding is missing")
    _require_exact(record.get("status"), "bound", f"{name} binding status")
    raw_path = record.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError(f"{name} binding path must be nonempty")
    expected_digest = _require_sha256(
        record.get("sha256"), f"{name} binding digest"
    )
    source = Path(actual_path).resolve()
    if not source.is_file() or _sha256_file(source) != expected_digest:
        raise ValueError(f"{name} execution binding does not match its source")

    registered = Path(raw_path)
    if registered.is_absolute():
        matches = registered.resolve() == source
    else:
        if ".." in registered.parts:
            raise ValueError(f"{name} binding path must not traverse parents")
        candidates = (family_path.resolve().parent, *family_path.resolve().parents)
        matches = any((candidate / registered).resolve() == source for candidate in candidates)
    if not matches:
        raise ValueError(f"{name} execution binding path does not match its source")

    mirrors = {
        f"{name}_path": raw_path,
        f"{name}_sha256": expected_digest,
        f"{name}_status": "bound",
    }
    for field, expected in mirrors.items():
        if family.get(field) != expected:
            raise ValueError(f"{name} binding metadata does not match {field}")


def _validate_registered_family(
    family_path: Path, family: Mapping[str, Any]
) -> None:
    if not isinstance(family, Mapping):
        raise ValueError("confirmation-v3 family must be an object")
    exact_fields = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": "complete",
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "case_block": "confirmation_v3",
        "case_count": 64,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "run_success_threshold": 0.95,
        "maximum_shortfall": 0.05,
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "fresh_provider_conversation_per_condition": True,
        "comparison_role": REGISTERED_V3,
        "evidence_boundary": REGISTERED_V3,
    }
    for field, expected in exact_fields.items():
        _require_exact(family.get(field), expected, field)

    control = family.get("control")
    if control not in CONTROL_SPECS:
        raise ValueError("control must be identity or planted")
    spec = CONTROL_SPECS[control]
    for field in (
        "schedule_seed",
        "replicate_count",
        "strict_subset",
        "calibration_role",
        "admission_rule",
        "required_joint_events_for_admission",
    ):
        _require_exact(family.get(field), spec[field], field)

    schedule = family.get("replicate_schedule")
    expected_schedule = balanced_schedule(
        seed=spec["schedule_seed"], replicate_count=spec["replicate_count"]
    )
    if schedule != expected_schedule:
        raise ValueError(
            f"{control} replicate schedule does not match the registered schedule"
        )
    for row in schedule:
        order = row.get("condition_order")
        if (
            not isinstance(order, list)
            or len(order) != len(CONDITIONS)
            or set(order) != set(CONDITIONS)
        ):
            raise ValueError("replicate condition order must contain B/F/S exactly once")

    _resolve_execution_binding(
        family_path,
        family,
        name="runner",
        actual_path=Path(run_toolformer_bundle.__code__.co_filename),
    )
    _resolve_execution_binding(
        family_path,
        family,
        name="scheduler",
        actual_path=Path(__file__),
    )


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _load_registered_family(
    family_path: Path,
    family_loader: Callable[[Path, str], Mapping[str, Any]],
) -> tuple[dict[str, Any], str]:
    supplied_path = Path(family_path)
    if supplied_path.is_symlink():
        raise ValueError(f"confirmation-v3 family is missing or unsafe: {supplied_path}")
    path = supplied_path.resolve()
    if not path.is_file():
        raise ValueError(f"confirmation-v3 family is missing or unsafe: {path}")
    try:
        snapshot = path.read_bytes()
        raw = json.loads(snapshot.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("confirmation-v3 family must be valid UTF-8 JSON") from exc
    if not isinstance(raw, dict):
        raise ValueError("confirmation-v3 family must be a JSON object")
    family_sha256 = hashlib.sha256(snapshot).hexdigest()
    _validate_registered_family(path, raw)
    first_replicate_id = raw["replicate_schedule"][0]["replicate_id"]
    verified = family_loader(path, first_replicate_id)
    if not isinstance(verified, Mapping):
        raise ValueError("family loader must return a verified family object")
    _validate_registered_family(path, verified)
    for field in raw:
        if field in verified and verified[field] != raw[field]:
            raise ValueError(f"verified family changed registered field: {field}")
    if _sha256_file(path) != family_sha256:
        raise ValueError("confirmation-v3 family changed during validation")
    return raw, family_sha256


def _safe_output_dir(output_root: Path, replicate_id: str) -> Path:
    if not isinstance(replicate_id, str) or not replicate_id:
        raise ValueError("replicate ID must be nonempty")
    root = Path(output_root).resolve()
    candidate = (root / replicate_id).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("replicate output path escapes its control output root") from exc
    if candidate == root:
        raise ValueError("replicate output path must be below its control output root")
    return candidate


def build_run_namespace(
    *,
    family_path: Path,
    family: Mapping[str, Any],
    replicate: Mapping[str, Any],
    output_root: Path,
) -> argparse.Namespace:
    control = family.get("control")
    if control not in CONTROL_SPECS:
        raise ValueError("control must be identity or planted")
    replicate_id = replicate.get("replicate_id")
    order = replicate.get("condition_order")
    if (
        not isinstance(order, list)
        or len(order) != len(CONDITIONS)
        or set(order) != set(CONDITIONS)
    ):
        raise ValueError("replicate condition order must contain B/F/S exactly once")
    output_dir = _safe_output_dir(Path(output_root), replicate_id)
    return argparse.Namespace(
        family=Path(family_path).resolve(),
        replicate_id=replicate_id,
        condition=list(order),
        control=control,
        pair_id=f"confirmation-v3:{control}:{replicate_id}",
        output_dir=output_dir,
        model_alias=family["model_alias"],
        base_url_env="EFFECTSLICE_DEEPSEEK_BASE_URL",
        api_key_env="EFFECTSLICE_DEEPSEEK_API_KEY",
        timeout_seconds=240.0,
        scorer_timeout_seconds=300.0,
        max_tokens=family["max_tokens"],
        max_attempts=family["maximum_transport_attempts"],
        retry_delay_seconds=2.0,
    )


def _normalize_output_roots(
    output_roots: Mapping[str, Path],
) -> dict[str, Path]:
    if not isinstance(output_roots, Mapping) or set(output_roots) != set(CONTROL_SPECS):
        raise ValueError("output_roots must contain exactly identity and planted")
    try:
        roots = {control: Path(output_roots[control]).resolve() for control in CONTROL_SPECS}
    except (TypeError, ValueError) as exc:
        raise ValueError("control output roots must be filesystem paths") from exc
    identity = roots["identity"]
    planted = roots["planted"]
    if (
        identity == planted
        or identity in planted.parents
        or planted in identity.parents
    ):
        raise ValueError("identity and planted must use separate output roots")
    return roots


def _default_progress_path(output_roots: Mapping[str, Path]) -> Path:
    parents = {root.parent for root in output_roots.values()}
    if len(parents) != 1:
        raise ValueError(
            "progress_path is required when control output roots are not siblings"
        )
    return next(iter(parents)) / "confirmation_v3_progress.json"


def _base_record(
    *,
    family_path: Path,
    family_sha256: str,
    family: Mapping[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "control": family["control"],
        "task_key": family["task_key"],
        "replicate_id": args.replicate_id,
        "condition_execution_order": list(args.condition),
        "family_path": Path(family_path).resolve().as_posix(),
        "family_sha256": family_sha256,
        "output_dir": Path(args.output_dir).as_posix(),
    }


def _validate_completed_bundle(
    base: Mapping[str, Any],
) -> dict[str, Any]:
    output_dir = Path(base["output_dir"])
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise IncompleteBundle("registered output is not a safe directory")
    manifest_path = output_dir / "pair_manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise IncompleteBundle("final pair manifest is missing")
    try:
        manifest = _load_json_object(manifest_path, "final pair manifest")
    except ValueError as exc:
        raise IncompleteBundle("final pair manifest is invalid") from exc
    expected = {
        "schema_version": PAIR_SCHEMA,
        "completion_status": "complete",
        "pair_id": (
            f"confirmation-v3:{base['control']}:{base['replicate_id']}"
        ),
        "control": base["control"],
        "family_path": base["family_path"],
        "family_sha256": base["family_sha256"],
        "replicate_id": base["replicate_id"],
        "condition_execution_order": base["condition_execution_order"],
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            raise IncompleteBundle(f"final pair manifest mismatches {field}")
    return manifest


def _validate_runner_report(
    report: Any, base: Mapping[str, Any]
) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("runner report must be an object")
    expected = {
        "schema_version": RUN_REPORT_SCHEMA,
        "pair_id": f"confirmation-v3:{base['control']}:{base['replicate_id']}",
        "replicate_id": base["replicate_id"],
        "condition_execution_order": base["condition_execution_order"],
    }
    for field, value in expected.items():
        if report.get(field) != value:
            raise ValueError(f"runner report mismatches {field}")
    return report


def _terminal_record(
    base: Mapping[str, Any], status: str, **extra: Any
) -> dict[str, Any]:
    if status not in {"completed", "failed", "preserved"}:
        raise ValueError(f"invalid registered status: {status}")
    return {**base, "status": status, **extra}


def _sanitize_error_type(exc: Exception) -> str:
    name = type(exc).__name__
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name) else "Exception"


def _read_prior_records(
    progress_path: Path,
    registered: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    if not progress_path.exists():
        return {}
    if progress_path.is_symlink() or not progress_path.is_file():
        raise ValueError("progress path must be a regular file")
    payload = _load_json_object(progress_path, "confirmation-v3 progress")
    _require_exact(payload.get("schema_version"), PROGRESS_SCHEMA, "progress schema")
    _require_exact(
        payload.get("registered_schedule_length"),
        len(registered),
        "progress registered_schedule_length",
    )
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != len(registered):
        raise ValueError("progress records must exactly cover the registered schedule")
    counts = payload.get("counts")
    if not isinstance(counts, dict) or set(counts) != {
        "completed",
        "failed",
        "preserved",
    }:
        raise ValueError("progress counts are invalid")
    actual_counts = {
        status: sum(
            isinstance(row, dict) and row.get("status") == status for row in records
        )
        for status in ("completed", "failed", "preserved")
    }
    if counts != actual_counts or sum(actual_counts.values()) != len(registered):
        raise ValueError("progress counts do not equal the registered schedule length")

    expected = {
        (row["control"], row["replicate_id"]): row for row in registered
    }
    prior: dict[tuple[str, str], dict[str, Any]] = {}
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("progress records must be objects")
        key = (row.get("control"), row.get("replicate_id"))
        if key in prior or key not in expected:
            raise ValueError("progress contains a duplicate or unregistered replicate")
        base = expected[key]
        for field, value in base.items():
            if row.get(field) != value:
                raise ValueError(f"progress record changed registered field: {field}")
        status = row.get("status")
        if status not in {"completed", "failed", "preserved"}:
            raise ValueError("progress contains an invalid registered status")
        if status == "failed":
            error_type = row.get("error_type")
            if not isinstance(error_type, str) or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]{0,127}", error_type
            ) is None:
                raise ValueError("failed progress error_type is invalid")
        prior[key] = row
    if set(prior) != set(expected):
        raise ValueError("progress omits a registered replicate")
    return prior


def _journal_directory(progress_path: Path) -> Path:
    destination = Path(progress_path)
    return destination.with_name(f".{destination.name}.j")


def _journal_record_path(
    progress_path: Path, base: Mapping[str, Any]
) -> Path:
    control_prefix = {"identity": "i", "planted": "p"}[base["control"]]
    return _journal_directory(progress_path) / (
        f"{control_prefix}-{base['replicate_id']}.json"
    )


def _write_json_atomic(destination: Path, payload: Mapping[str, Any]) -> None:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f".{destination.name}.{os.getpid()}.{uuid.uuid4().hex[:12]}.tmp"
    )
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_journal_record(
    progress_path: Path, record: Mapping[str, Any]
) -> None:
    directory = _journal_directory(progress_path)
    if directory.exists() and (directory.is_symlink() or not directory.is_dir()):
        raise ValueError("terminal journal path must be a safe directory")
    _write_json_atomic(
        _journal_record_path(progress_path, record),
        {"schema_version": JOURNAL_SCHEMA, "record": dict(record)},
    )


def _read_journal_records(
    progress_path: Path, registered: list[dict[str, Any]]
) -> dict[tuple[str, str], dict[str, Any]]:
    directory = _journal_directory(progress_path)
    if not directory.exists():
        return {}
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("terminal journal path must be a safe directory")
    expected = {
        _journal_record_path(progress_path, row).name: row for row in registered
    }
    recovered: dict[tuple[str, str], dict[str, Any]] = {}
    for path in directory.iterdir():
        if path.name not in expected:
            is_writer_temporary = any(
                re.fullmatch(
                    rf"\.{re.escape(record_name)}\.\d+\.[0-9a-f]{{12}}\.tmp",
                    path.name,
                )
                is not None
                for record_name in expected
            )
            if is_writer_temporary and not path.is_symlink() and path.is_file():
                path.unlink()
                continue
            raise ValueError("terminal journal contains an unsafe or unregistered record")
        if path.is_symlink() or not path.is_file():
            raise ValueError("terminal journal contains an unsafe or unregistered record")
        payload = _load_json_object(path, "terminal journal record")
        _require_exact(
            payload.get("schema_version"), JOURNAL_SCHEMA, "terminal journal schema"
        )
        row = payload.get("record")
        if not isinstance(row, dict):
            raise ValueError("terminal journal record must be an object")
        base = expected[path.name]
        for field, value in base.items():
            if row.get(field) != value:
                raise ValueError(f"terminal journal changed registered field: {field}")
        status = row.get("status")
        if status not in {"completed", "failed"}:
            raise ValueError("terminal journal contains an invalid registered status")
        if status == "failed":
            error_type = row.get("error_type")
            if not isinstance(error_type, str) or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]{0,127}", error_type
            ) is None:
                raise ValueError("terminal journal error_type is invalid")
        else:
            expected_pair_id = (
                f"confirmation-v3:{base['control']}:{base['replicate_id']}"
            )
            if row.get("pair_id") != expected_pair_id:
                raise ValueError("terminal journal pair_id is invalid")
        key = (base["control"], base["replicate_id"])
        if key in recovered:
            raise ValueError("terminal journal duplicates a registered replicate")
        recovered[key] = row
    return recovered


def _write_progress(
    progress_path: Path, records: list[dict[str, Any]]
) -> dict[str, Any]:
    counts = {
        status: sum(row["status"] == status for row in records)
        for status in ("completed", "failed", "preserved")
    }
    if sum(counts.values()) != len(records):
        raise ValueError("terminal progress does not cover the registered schedule")
    payload = {
        "schema_version": PROGRESS_SCHEMA,
        "registered_schedule_length": len(records),
        "counts": counts,
        "records": records,
    }
    destination = Path(progress_path).resolve()
    _write_json_atomic(destination, payload)
    return payload


@contextmanager
def _exclusive_schedule_lock(progress_path: Path):
    lock_path = Path(progress_path).with_name(f".{Path(progress_path).name}.lock")
    if lock_path.is_symlink():
        raise ValueError("scheduler lock path must be a regular file")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    locked = False
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError(
                "confirmation-v3 scheduler is already active for this progress path"
            ) from exc
        locked = True
        yield
    finally:
        if locked:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _run_schedule_locked(
    *,
    family_paths: list[Path],
    output_roots: Mapping[str, Path],
    max_workers: int = 2,
    progress_path: Path | None = None,
    runner_by_task: Mapping[
        str, Callable[[argparse.Namespace], dict[str, Any]]
    ]
    | None = None,
    family_loader: Callable[[Path, str], Mapping[str, Any]] = DEFAULT_FAMILY_LOADER,
    allow_test_injection: bool = False,
) -> dict[str, Any]:
    if (
        isinstance(max_workers, bool)
        or not isinstance(max_workers, int)
        or not 1 <= max_workers <= 2
    ):
        raise ValueError("max_workers must be a non-bool integer in [1, 2]")
    if not isinstance(family_paths, list) or not family_paths:
        raise ValueError("family_paths must be a nonempty list")
    if type(allow_test_injection) is not bool:
        raise ValueError("allow_test_injection must be a bool")
    has_custom_execution = (
        runner_by_task is not None or family_loader is not DEFAULT_FAMILY_LOADER
    )
    if has_custom_execution and not allow_test_injection:
        raise ValueError("custom runner or family loader requires explicit test injection")
    if runner_by_task is None and (
        set(DEFAULT_RUNNERS) != {"toolformer_filter"}
        or DEFAULT_RUNNERS.get("toolformer_filter") is not run_toolformer_bundle
    ):
        raise ValueError("production default runner no longer matches its binding")
    roots = _normalize_output_roots(output_roots)
    if progress_path is None:
        destination = _default_progress_path(roots)
    else:
        supplied_progress_path = Path(progress_path)
        if supplied_progress_path.is_symlink():
            raise ValueError("progress path must be a regular file")
        destination = supplied_progress_path.resolve()
    runners = DEFAULT_RUNNERS if runner_by_task is None else runner_by_task
    if not isinstance(runners, Mapping):
        raise ValueError("runner_by_task must be a mapping")
    if not callable(family_loader):
        raise ValueError("family_loader must be callable")

    seen_paths: set[Path] = set()
    seen_controls: set[str] = set()
    registered: list[dict[str, Any]] = []
    jobs: list[
        tuple[
            dict[str, Any],
            argparse.Namespace,
            Callable[[argparse.Namespace], dict[str, Any]],
        ]
    ] = []
    for raw_family_path in family_paths:
        supplied_family_path = Path(raw_family_path)
        family_path = supplied_family_path.resolve()
        if family_path in seen_paths:
            raise ValueError(f"duplicate confirmation-v3 family path: {family_path}")
        seen_paths.add(family_path)
        family, family_sha256 = _load_registered_family(
            supplied_family_path, family_loader
        )
        control = family["control"]
        if control in seen_controls:
            raise ValueError(f"duplicate confirmation-v3 control family: {control}")
        seen_controls.add(control)
        task_key = family["task_key"]
        runner = runners.get(task_key)
        if not callable(runner):
            raise ValueError(f"no runner registered for {task_key}")
        for replicate in family["replicate_schedule"]:
            args = build_run_namespace(
                family_path=family_path,
                family=family,
                replicate=replicate,
                output_root=roots[control],
            )
            base = _base_record(
                family_path=family_path,
                family_sha256=family_sha256,
                family=family,
                args=args,
            )
            registered.append(base)
            jobs.append((base, args, runner))

    prior = _read_prior_records(destination, registered)
    journal = {} if prior else _read_journal_records(destination, registered)
    terminal: dict[tuple[str, str], dict[str, Any]] = {}
    runnable = []
    for base, args, runner in jobs:
        key = (base["control"], base["replicate_id"])
        previous = prior.get(key)
        if previous is not None:
            if previous["status"] == "failed":
                terminal[key] = _terminal_record(
                    base,
                    "failed",
                    error_type=previous.get("error_type", "RegisteredFailure"),
                    error_message="registered runner failed",
                )
            else:
                manifest = _validate_completed_bundle(base)
                terminal[key] = _terminal_record(
                    base, "preserved", pair_id=manifest["pair_id"]
                )
            continue
        if Path(args.output_dir).exists():
            try:
                manifest = _validate_completed_bundle(base)
            except IncompleteBundle:
                terminal[key] = _terminal_record(
                    base,
                    "failed",
                    error_type="IncompleteBundle",
                    error_message="registered runner failed",
                )
            else:
                terminal[key] = _terminal_record(
                    base, "preserved", pair_id=manifest["pair_id"]
                )
            continue
        recovered = journal.get(key)
        if recovered is not None:
            if recovered["status"] == "completed":
                raise IncompleteBundle(
                    "completed terminal journal record lacks its write-once bundle"
                )
            terminal[key] = _terminal_record(
                base,
                "failed",
                error_type=recovered["error_type"],
                error_message="registered runner failed",
            )
            continue
        runnable.append((base, args, runner))

    def execute(job):
        base, args, runner = job
        try:
            if _sha256_file(args.family) != base["family_sha256"]:
                raise ValueError("confirmation-v3 family changed before execution")
            report = runner(args)
            if _sha256_file(args.family) != base["family_sha256"]:
                raise ValueError("confirmation-v3 family changed during execution")
            _validate_runner_report(report, base)
            manifest = _validate_completed_bundle(base)
            record = _terminal_record(
                base, "completed", pair_id=manifest["pair_id"]
            )
        except Exception as exc:  # Preserve every registered execution failure.
            record = _terminal_record(
                base,
                "failed",
                error_type=_sanitize_error_type(exc),
                error_message="registered runner failed",
            )
        _write_journal_record(destination, record)
        return record

    for base, _args, _runner in runnable:
        _write_journal_record(
            destination,
            _terminal_record(
                base,
                "failed",
                error_type="SchedulerInterrupted",
                error_message="registered runner failed",
            ),
        )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(execute, job): job for job in runnable}
        for future in as_completed(futures):
            base = futures[future][0]
            key = (base["control"], base["replicate_id"])
            terminal[key] = future.result()

    records = [
        terminal[(row["control"], row["replicate_id"])] for row in registered
    ]
    return _write_progress(destination, records)


def run_schedule(
    *,
    family_paths: list[Path],
    output_roots: Mapping[str, Path],
    max_workers: int = 2,
    progress_path: Path | None = None,
    runner_by_task: Mapping[
        str, Callable[[argparse.Namespace], dict[str, Any]]
    ]
    | None = None,
    family_loader: Callable[[Path, str], Mapping[str, Any]] = DEFAULT_FAMILY_LOADER,
    allow_test_injection: bool = False,
) -> dict[str, Any]:
    if (
        isinstance(max_workers, bool)
        or not isinstance(max_workers, int)
        or not 1 <= max_workers <= 2
    ):
        raise ValueError("max_workers must be a non-bool integer in [1, 2]")
    if not isinstance(family_paths, list) or not family_paths:
        raise ValueError("family_paths must be a nonempty list")
    if type(allow_test_injection) is not bool:
        raise ValueError("allow_test_injection must be a bool")
    has_custom_execution = (
        runner_by_task is not None or family_loader is not DEFAULT_FAMILY_LOADER
    )
    if has_custom_execution and not allow_test_injection:
        raise ValueError("custom runner or family loader requires explicit test injection")
    roots = _normalize_output_roots(output_roots)
    if progress_path is None:
        destination = _default_progress_path(roots)
    else:
        supplied_progress_path = Path(progress_path)
        if supplied_progress_path.is_symlink():
            raise ValueError("progress path must be a regular file")
        destination = supplied_progress_path.resolve()
    lock_targets = {destination, *roots.values()}
    with ExitStack() as locks:
        for target in sorted(
            lock_targets, key=lambda path: os.path.normcase(str(path))
        ):
            locks.enter_context(_exclusive_schedule_lock(target))
        return _run_schedule_locked(
            family_paths=family_paths,
            output_roots=output_roots,
            max_workers=max_workers,
            progress_path=progress_path,
            runner_by_task=runner_by_task,
            family_loader=family_loader,
            allow_test_injection=allow_test_injection,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run registered write-once EffectSlice confirmation-v3 controls"
    )
    parser.add_argument("--family", action="append", type=Path, default=[])
    parser.add_argument(
        "--identity-output-root",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "confirmation_v3" / "identity",
    )
    parser.add_argument(
        "--planted-output-root",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "confirmation_v3" / "planted",
    )
    parser.add_argument(
        "--progress-path",
        type=Path,
        default=RUN_ROOT
        / "experiment_results"
        / "confirmation_v3"
        / "confirmation_v3_progress.json",
    )
    parser.add_argument("--max-workers", type=int, default=2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    family_paths = args.family or [
        RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / control
        / "family.json"
        for control in ("identity", "planted")
    ]
    result = run_schedule(
        family_paths=family_paths,
        output_roots={
            "identity": args.identity_output_root,
            "planted": args.planted_output_root,
        },
        max_workers=args.max_workers,
        progress_path=args.progress_path,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
