from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Mapping


RUN_ROOT = Path(__file__).resolve().parent
PREREGISTRATION_PATH = RUN_ROOT / "artifacts" / "confirmation_v5" / "preregistration.json"
DEFAULT_OUTPUT_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v5"
DEFAULT_PROGRESS_PATH = DEFAULT_OUTPUT_ROOT / "confirmation_v5_progress.json"
EVIDENCE_BOUNDARY = "registered_natural_candidate_finite_schedule_confirmation_v5"
PROGRESS_SCHEMA = "effectslice-confirmation-v5-progress.v1"
FAMILY_KEYS = {"toolformer_natural"}
HARNESS_BY_TASK = {
    "snap_mfse": "effectslice-snap-mfse-aci.v3",
    "toolformer_filter": "effectslice-toolformer-filter-aci.v3",
}
CONDITIONS = {"B", "F", "S"}
FAMILY_SPECS = {
    "toolformer_natural": {
        "task_key": "toolformer_filter",
        "candidate_role": "natural_registered_reducer_candidate",
        "replicate_count": 18,
        "schedule_seed": 2026072021,
        "strict_subset": True,
        "admission_decision_applicable": True,
        "expected_admission": True,
        "public_test_file": "test_toolformer_filter_public.py",
    },
}


import sys

sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.evidence_binding import validate_file_bindings  # noqa: E402
from run_snap_mfse_effectslice import run_bundle as run_snap_bundle  # noqa: E402
from run_toolformer_filter_effectslice import (  # noqa: E402
    run_bundle as run_toolformer_bundle,
)


DEFAULT_RUNNERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "snap_mfse": run_snap_bundle,
    "toolformer_filter": run_toolformer_bundle,
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _resolve_registered(raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{label} path must be nonempty")
    path = Path(raw)
    if not path.is_absolute():
        path = RUN_ROOT / path
    return path.resolve()


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _validate_family(
    *, family_key: str, record: Mapping[str, Any]
) -> tuple[Path, dict[str, Any], str]:
    path = _resolve_registered(record.get("path"), f"{family_key} family")
    expected_sha256 = _require_sha256(
        record.get("sha256"), f"{family_key} family digest"
    )
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{family_key} family is missing or unsafe")
    if _sha256_file(path) != expected_sha256:
        raise ValueError(f"{family_key} family digest does not match")
    family = _load_json(path, f"{family_key} family")
    spec = FAMILY_SPECS[family_key]
    expected = {
        "schema_version": "effectslice-confirmation-v5-family.v1",
        "registration_status": "complete",
        "case_block": "confirmation_v5",
        "case_count": 64,
        "conditions": ["B", "F", "S"],
        "private_score_policy": "final_only",
        "public_test_policy": "locked_public_test_visible_private_scorer_terminal",
        "comparison_role": EVIDENCE_BOUNDARY,
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "confirmation_unsealed": False,
        "independence_verified": False,
        "fresh_provider_conversation_per_condition": True,
        "decision_basis": "finite_registered_schedule_without_population_inference",
        "condition_run_unit": "fresh_provider_conversation",
        "analysis_unit": "complete_registered_finite_schedule",
        "run_success_threshold": 0.95,
        "provider_label": "DeepSeek V3.2",
        "base_url": "https://api.deepseek.com",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "timeout_seconds": 240.0,
        "maximum_transport_attempts": 5,
        "retry_delay_seconds": 2.0,
        "direct_connection": True,
        "proxy_policy": "disabled",
        **spec,
    }
    for field, expected_value in expected.items():
        if family.get(field) != expected_value:
            raise ValueError(f"{family_key} family changed registered field {field}")
    task_key = family.get("task_key")
    if task_key not in HARNESS_BY_TASK:
        raise ValueError(f"{family_key} has an unsupported task key")
    schedule = family.get("replicate_schedule")
    if not isinstance(schedule, list) or len(schedule) != record.get("replicate_count"):
        raise ValueError(f"{family_key} schedule length does not match registration")
    seen_ids: set[str] = set()
    for row in schedule:
        replicate_id = row.get("replicate_id")
        order = row.get("condition_order")
        if (
            not isinstance(replicate_id, str)
            or not replicate_id
            or Path(replicate_id).name != replicate_id
            or replicate_id in seen_ids
        ):
            raise ValueError(f"{family_key} replicate IDs are invalid")
        if not isinstance(order, list) or len(order) != 3 or set(order) != CONDITIONS:
            raise ValueError(f"{family_key} condition order is invalid")
        seen_ids.add(replicate_id)
    order_counts = Counter(tuple(row["condition_order"]) for row in schedule)
    if set(order_counts) != set(itertools.permutations(("B", "F", "S"))):
        raise ValueError(f"{family_key} schedule does not cover all B/F/S orders")
    expected_repetitions = family["replicate_count"] // 6
    if set(order_counts.values()) != {expected_repetitions}:
        raise ValueError(f"{family_key} schedule is not balanced")
    verified = validate_file_bindings(family, root=RUN_ROOT)
    required_bindings = {
        "full_artifact",
        "selected_artifact",
        "source_map",
        "slice_registry",
        "case_registry",
        "task_prompt",
        "public_test",
        "scorer",
        "runner",
        "scheduler",
        "analyzer",
        "builder",
        "aci_runner",
        "aci_protocol",
        "evidence_binding",
        "public_test_bridge",
        "case_generator",
        "transport",
        "reducer_source",
        "reducer_registry",
        "prior_v4_summary",
        "crosscheck",
        "confirmation_tests",
        "crosscheck_tests",
    }
    if not required_bindings.issubset(verified):
        raise ValueError(f"{family_key} file bindings are incomplete")
    if Path(verified["scheduler"]["path"]).resolve() != Path(__file__).resolve():
        raise ValueError(f"{family_key} scheduler binding is not this executable")
    if Path(verified["public_test"]["path"]).name != family["public_test_file"]:
        raise ValueError(f"{family_key} public test binding changed")
    return path, family, expected_sha256


def load_and_verify_registration(
    preregistration_path: Path,
    expected_sha256: str,
    *,
    allow_test_registration: bool = False,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], str]:
    expected_sha256 = _require_sha256(expected_sha256, "preregistration digest")
    supplied = Path(preregistration_path)
    if supplied.is_symlink():
        raise ValueError("preregistration path must be a regular file")
    path = supplied.resolve()
    if not allow_test_registration and path != PREREGISTRATION_PATH.resolve():
        raise ValueError("production preregistration path is fixed")
    if not path.is_file() or _sha256_file(path) != expected_sha256:
        raise ValueError("preregistration digest does not match the external anchor")
    registration = _load_json(path, "preregistration")
    expected = {
        "schema_version": "effectslice-confirmation-v5-preregistration.v1",
        "registration_status": "complete",
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "decision_basis": "finite_registered_schedule_without_population_inference",
        "registered_stratum_count": 18,
        "registered_block_count": 18,
        "registered_condition_run_count": 54,
        "maximum_parallel_workers": 2,
        "preserve_registered_failures": True,
    }
    for field, expected_value in expected.items():
        if registration.get(field) != expected_value:
            raise ValueError(f"preregistration changed registered field {field}")
    family_records = registration.get("families")
    if not isinstance(family_records, dict) or set(family_records) != FAMILY_KEYS:
        raise ValueError("preregistration family set is invalid")
    families: dict[str, dict[str, Any]] = {}
    family_paths: dict[str, Path] = {}
    for family_key in sorted(FAMILY_KEYS):
        family_path, family, family_sha256 = _validate_family(
            family_key=family_key, record=family_records[family_key]
        )
        family_paths[family_key] = family_path
        families[family_key] = {
            "path": family_path,
            "sha256": family_sha256,
            "family": family,
        }
    schedule = registration.get("global_interleaved_schedule")
    if not isinstance(schedule, list) or len(schedule) != 18:
        raise ValueError("global registered schedule must contain 18 blocks")
    expected_pairs = {
        (family_key, row["replicate_id"]): row
        for family_key, loaded in families.items()
        for row in loaded["family"]["replicate_schedule"]
    }
    observed_pairs: set[tuple[str, str]] = set()
    for index, row in enumerate(schedule, start=1):
        family_key = row.get("family_key")
        replicate_id = row.get("replicate_id")
        pair = (family_key, replicate_id)
        if row.get("global_order_index") != index or pair not in expected_pairs:
            raise ValueError("global registered schedule contains an unknown block")
        if pair in observed_pairs:
            raise ValueError("global registered schedule duplicates a block")
        if row.get("condition_order") != expected_pairs[pair]["condition_order"]:
            raise ValueError("global schedule condition order changed")
        if row.get("task_key") != families[family_key]["family"]["task_key"]:
            raise ValueError("global schedule task key changed")
        stratum = row.get("stratum")
        if isinstance(stratum, bool) or not isinstance(stratum, int) or not 1 <= stratum <= 18:
            raise ValueError("global schedule stratum is invalid")
        observed_pairs.add(pair)
    if observed_pairs != set(expected_pairs):
        raise ValueError("global registered schedule omits a family block")
    for stratum in range(1, 19):
        observed_families = {
            row["family_key"] for row in schedule if row["stratum"] == stratum
        }
        expected_families = {"toolformer_natural"}
        if observed_families != expected_families:
            raise ValueError("global registered stratum composition changed")
    return registration, families, expected_sha256


def _family_bound_path(family: Mapping[str, Any], prefix: str) -> Path:
    return _resolve_registered(family.get(f"{prefix}_path"), prefix)


def build_run_namespace(
    *,
    family_key: str,
    family_path: Path,
    family: Mapping[str, Any],
    schedule_row: Mapping[str, Any],
    output_root: Path,
) -> argparse.Namespace:
    task_key = family["task_key"]
    replicate_id = schedule_row["replicate_id"]
    order = schedule_row["condition_order"]
    output_dir = Path(output_root).resolve() / family_key / replicate_id
    return argparse.Namespace(
        family_key=family_key,
        condition=list(order),
        pair_id=f"confirmation-v5:{family_key}:{replicate_id}",
        seed_block_id=f"confirmation-v5:{family_key}:{replicate_id}",
        model_family="DeepSeek-family",
        model_alias=family["model_alias"],
        wire_api=family["wire_api"],
        base_url_env="EFFECTSLICE_DEEPSEEK_BASE_URL",
        api_key_env="EFFECTSLICE_DEEPSEEK_API_KEY",
        case_block="confirmation_v5",
        case_registry=_family_bound_path(family, "case_registry"),
        max_tokens=int(family["max_tokens"]),
        harness_protocol_version=HARNESS_BY_TASK[task_key],
        provider_protocol_version="effectslice-deepseek-public-test-final-only.v5",
        timeout_seconds=float(family["timeout_seconds"]),
        max_attempts=int(family["maximum_transport_attempts"]),
        retry_delay_seconds=float(family["retry_delay_seconds"]),
        max_actions=16,
        slice_context=_family_bound_path(family, "selected_artifact"),
        slice_registry=_family_bound_path(family, "slice_registry"),
        slice_candidate_id=family["selected_candidate_id"],
        confirmation_family=Path(family_path).resolve(),
        public_test_file=family["public_test_file"],
        authorization_evidence="user-confirmed trusted endpoint 2026-07-16",
        output_dir=output_dir,
    )


def _base_record(
    row: Mapping[str, Any],
    loaded: Mapping[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    family_key = row["family_key"]
    replicate_id = row["replicate_id"]
    return {
        "global_order_index": row["global_order_index"],
        "stratum": row["stratum"],
        "family_key": family_key,
        "task_key": row["task_key"],
        "replicate_id": replicate_id,
        "condition_execution_order": list(row["condition_order"]),
        "family_path": Path(loaded["path"]).resolve().as_posix(),
        "family_sha256": loaded["sha256"],
        "output_dir": (
            Path(output_root).resolve() / family_key / replicate_id
        ).as_posix(),
    }


def _validate_completed_bundle(base: Mapping[str, Any]) -> dict[str, Any]:
    output_dir = Path(base["output_dir"])
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise ValueError("registered output is not a safe completed directory")
    manifest = _load_json(output_dir / "pair_manifest.json", "pair manifest")
    report = _load_json(output_dir / "run_report.json", "run report")
    pair_id = f"confirmation-v5:{base['family_key']}:{base['replicate_id']}"
    for payload, label in ((manifest, "pair manifest"), (report, "run report")):
        if payload.get("pair_id") != pair_id:
            raise ValueError(f"{label} pair ID does not match registration")
        if payload.get("case_block") != "confirmation_v5":
            raise ValueError(f"{label} case block does not match registration")
        if payload.get("condition_execution_order") != base["condition_execution_order"]:
            raise ValueError(f"{label} condition order does not match registration")
        if set(payload.get("results", {})) != CONDITIONS:
            raise ValueError(f"{label} does not contain B/F/S results")
    if manifest.get("confirmation_family_sha256") != base["family_sha256"]:
        raise ValueError("pair manifest family digest does not match registration")
    for condition in CONDITIONS:
        condition_dir = output_dir / condition
        for name in ("run_result.json", "transcript.json", "candidate.patch"):
            path = condition_dir / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"completed bundle is missing {condition}/{name}")
    return report


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f".{destination.name}.{os.getpid()}.{uuid.uuid4().hex[:12]}.tmp"
    )
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_progress(
    path: Path,
    *,
    preregistration_sha256: str,
    registered_count: int,
    records: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(records.values(), key=lambda row: row["global_order_index"])
    counts = {
        status: sum(row["status"] == status for row in ordered)
        for status in ("completed", "failed", "preserved")
    }
    counts["pending"] = registered_count - len(ordered)
    payload = {
        "schema_version": PROGRESS_SCHEMA,
        "preregistration_sha256": preregistration_sha256,
        "registered_schedule_length": registered_count,
        "counts": counts,
        "records": ordered,
    }
    _atomic_write_json(path, payload)
    return payload


def _load_prior_records(
    path: Path,
    *,
    preregistration_sha256: str,
    expected: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    if not Path(path).exists():
        return {}
    progress = _load_json(path, "progress")
    if progress.get("schema_version") != PROGRESS_SCHEMA:
        raise ValueError("progress schema does not match confirmation V5")
    if progress.get("preregistration_sha256") != preregistration_sha256:
        raise ValueError("progress preregistration digest changed")
    if progress.get("registered_schedule_length") != len(expected):
        raise ValueError("progress registered schedule length changed")
    prior: dict[tuple[str, str], dict[str, Any]] = {}
    for record in progress.get("records", []):
        if not isinstance(record, dict):
            raise ValueError("progress records must be objects")
        key = (record.get("family_key"), record.get("replicate_id"))
        if key in prior or key not in expected:
            raise ValueError("progress contains a duplicate or unregistered block")
        for field, value in expected[key].items():
            if record.get(field) != value:
                raise ValueError(f"progress changed registered field {field}")
        if record.get("status") not in {"completed", "failed", "preserved"}:
            raise ValueError("progress contains an invalid terminal status")
        prior[key] = record
    return prior


@contextmanager
def _exclusive_lock(progress_path: Path):
    lock_path = Path(progress_path).with_name(f".{Path(progress_path).name}.lock")
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
            raise ValueError("confirmation-v5 scheduler is already active") from exc
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


def run_schedule(
    *,
    preregistration_path: Path,
    expected_preregistration_sha256: str,
    output_root: Path | None = None,
    progress_path: Path | None = None,
    max_workers: int = 2,
    runner_by_task: Mapping[
        str, Callable[[argparse.Namespace], dict[str, Any]]
    ]
    | None = None,
    allow_test_injection: bool = False,
) -> dict[str, Any]:
    if (
        isinstance(max_workers, bool)
        or not isinstance(max_workers, int)
        or not 1 <= max_workers <= 2
    ):
        raise ValueError("max_workers must be a non-bool integer in [1, 2]")
    if type(allow_test_injection) is not bool:
        raise ValueError("allow_test_injection must be a bool")
    if runner_by_task is not None and not allow_test_injection:
        raise ValueError("custom runners require explicit test injection")
    registration, families, preregistration_sha256 = load_and_verify_registration(
        preregistration_path,
        expected_preregistration_sha256,
        allow_test_registration=allow_test_injection,
    )
    registered_output_root = _resolve_registered(
        registration["execution"]["output_root"], "execution output root"
    )
    registered_progress_path = _resolve_registered(
        registration["execution"]["progress_path"], "execution progress"
    )
    if not allow_test_injection and (
        registered_output_root != DEFAULT_OUTPUT_ROOT.resolve()
        or registered_progress_path != DEFAULT_PROGRESS_PATH.resolve()
    ):
        raise ValueError("preregistered production execution paths changed")
    root = registered_output_root if output_root is None else Path(output_root).resolve()
    destination = (
        registered_progress_path if progress_path is None else Path(progress_path).resolve()
    )
    if not allow_test_injection and (
        root != registered_output_root or destination != registered_progress_path
    ):
        raise ValueError("production output and progress paths are preregistered")
    if destination.parent != root:
        raise ValueError("progress path must be directly inside the output root")
    if root.is_symlink() or destination.is_symlink():
        raise ValueError("output and progress paths must be regular filesystem paths")
    root.mkdir(parents=True, exist_ok=True)
    runners = DEFAULT_RUNNERS if runner_by_task is None else runner_by_task
    if not isinstance(runners, Mapping):
        raise ValueError("runner_by_task must be a mapping")
    schedule = registration["global_interleaved_schedule"]
    expected: dict[tuple[str, str], dict[str, Any]] = {}
    jobs: dict[tuple[str, str], tuple[argparse.Namespace, Callable]] = {}
    for row in schedule:
        loaded = families[row["family_key"]]
        base = _base_record(row, loaded, root)
        key = (row["family_key"], row["replicate_id"])
        expected[key] = base
        task_key = row["task_key"]
        runner = runners.get(task_key)
        if not callable(runner):
            raise ValueError(f"no runner registered for {task_key}")
        jobs[key] = (
            build_run_namespace(
                family_key=row["family_key"],
                family_path=loaded["path"],
                family=loaded["family"],
                schedule_row=row,
                output_root=root,
            ),
            runner,
        )

    with _exclusive_lock(destination):
        terminal = _load_prior_records(
            destination,
            preregistration_sha256=preregistration_sha256,
            expected=expected,
        )
        for key, base in expected.items():
            previous = terminal.get(key)
            output_dir = Path(base["output_dir"])
            if previous is not None:
                if previous["status"] in {"completed", "preserved"}:
                    _validate_completed_bundle(base)
                continue
            if output_dir.exists():
                try:
                    report = _validate_completed_bundle(base)
                except Exception:
                    terminal[key] = {
                        **base,
                        "status": "failed",
                        "error_type": "IncompleteBundle",
                        "error_message": "registered block failed",
                    }
                else:
                    terminal[key] = {
                        **base,
                        "status": "preserved",
                        "pair_id": report["pair_id"],
                    }
        _write_progress(
            destination,
            preregistration_sha256=preregistration_sha256,
            registered_count=len(expected),
            records=terminal,
        )

        def execute(key: tuple[str, str]) -> dict[str, Any]:
            base = expected[key]
            args, runner = jobs[key]
            try:
                if _sha256_file(Path(base["family_path"])) != base["family_sha256"]:
                    raise ValueError("family changed before registered execution")
                report = runner(args)
                if _sha256_file(Path(base["family_path"])) != base["family_sha256"]:
                    raise ValueError("family changed during registered execution")
                verified_report = _validate_completed_bundle(base)
                if not isinstance(report, dict) or report.get("pair_id") != verified_report.get(
                    "pair_id"
                ):
                    raise ValueError("runner report does not match completed bundle")
                return {
                    **base,
                    "status": "completed",
                    "pair_id": verified_report["pair_id"],
                }
            except Exception as exc:
                error_type = type(exc).__name__
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", error_type) is None:
                    error_type = "RegisteredFailure"
                return {
                    **base,
                    "status": "failed",
                    "error_type": error_type,
                    "error_message": "registered block failed",
                }

        for stratum in range(1, 19):
            stratum_keys = [
                (row["family_key"], row["replicate_id"])
                for row in schedule
                if row["stratum"] == stratum
                and (row["family_key"], row["replicate_id"]) not in terminal
            ]
            if not stratum_keys:
                continue
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                future_to_key = {pool.submit(execute, key): key for key in stratum_keys}
                for future in as_completed(future_to_key):
                    key = future_to_key[future]
                    terminal[key] = future.result()
                    _write_progress(
                        destination,
                        preregistration_sha256=preregistration_sha256,
                        registered_count=len(expected),
                        records=terminal,
                    )
        return _write_progress(
            destination,
            preregistration_sha256=preregistration_sha256,
            registered_count=len(expected),
            records=terminal,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the externally anchored EffectSlice confirmation V5 schedule"
    )
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION_PATH)
    parser.add_argument(
        "--expected-preregistration-sha256",
        default=os.environ.get("EFFECTSLICE_V5_PREREGISTRATION_SHA256", ""),
    )
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--progress-path", type=Path, default=None)
    parser.add_argument("--max-workers", type=int, default=2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.expected_preregistration_sha256:
        raise ValueError(
            "expected preregistration SHA-256 must come from the committed external anchor"
        )
    progress = run_schedule(
        preregistration_path=args.preregistration,
        expected_preregistration_sha256=args.expected_preregistration_sha256,
        output_root=args.output_root,
        progress_path=args.progress_path,
        max_workers=args.max_workers,
    )
    print(json.dumps(progress["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
