from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable


RUN_ROOT = Path(__file__).resolve().parent

from run_snap_mfse_effectslice import run_bundle as run_snap_bundle
from run_toolformer_filter_effectslice import run_bundle as run_toolformer_bundle


DEFAULT_RUNNERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "snap_mfse": run_snap_bundle,
    "toolformer_filter": run_toolformer_bundle,
}

HARNESS_BY_TASK = {
    "snap_mfse": "effectslice-snap-mfse-aci.v3",
    "toolformer_filter": "effectslice-toolformer-filter-aci.v3",
}


def _family_path(family: dict[str, Any], prefix: str) -> Path:
    raw = family.get(f"{prefix}_path")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"confirmation-v2 family lacks {prefix}_path")
    path = Path(raw)
    if not path.is_absolute():
        path = RUN_ROOT / path
    return path.resolve()


def build_run_namespace(
    *,
    family_path: Path,
    family: dict[str, Any],
    replicate: dict[str, Any],
    output_root: Path,
) -> argparse.Namespace:
    task_key = family.get("task_key")
    if task_key not in HARNESS_BY_TASK:
        raise ValueError(f"unsupported confirmation-v2 task: {task_key}")
    replicate_id = replicate.get("replicate_id")
    condition_order = replicate.get("condition_order")
    if not isinstance(replicate_id, str) or not replicate_id:
        raise ValueError("replicate ID must be nonempty")
    if sorted(condition_order or []) != ["B", "F", "S"]:
        raise ValueError("replicate condition order must be a B/F/S permutation")
    return argparse.Namespace(
        condition=list(condition_order),
        pair_id=f"{task_key}:confirmation-v2:{replicate_id}",
        seed_block_id=f"confirmation-v2:{task_key}:{replicate_id}",
        model_family="DeepSeek-family",
        model_alias=family["model_alias"],
        wire_api=family["wire_api"],
        base_url_env="EFFECTSLICE_DEEPSEEK_BASE_URL",
        api_key_env="EFFECTSLICE_DEEPSEEK_API_KEY",
        case_block="confirmation_v2",
        case_registry=_family_path(family, "case_registry"),
        max_tokens=int(family["max_tokens"]),
        harness_protocol_version=HARNESS_BY_TASK[task_key],
        provider_protocol_version="effectslice-deepseek-final-only.v3",
        timeout_seconds=240.0,
        max_attempts=int(family["maximum_transport_attempts"]),
        retry_delay_seconds=2.0,
        max_actions=16,
        slice_context=_family_path(family, "selected_artifact"),
        slice_registry=_family_path(family, "slice_registry"),
        slice_candidate_id=family["selected_candidate_id"],
        confirmation_family=Path(family_path).resolve(),
        authorization_evidence="user-confirmed trusted endpoint 2026-07-16",
        output_dir=(Path(output_root).resolve() / task_key / replicate_id),
    )


def _write_progress(output_root: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(records, key=lambda row: (row["task_key"], row["replicate_id"]))
    counts = {
        status: sum(row["status"] == status for row in ordered)
        for status in ("completed", "failed", "preserved")
    }
    payload = {
        "schema_version": "effectslice-confirmation-v2-progress.v1",
        "counts": counts,
        "records": ordered,
    }
    destination = Path(output_root).resolve() / "confirmation_v2_progress.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def run_schedule(
    *,
    family_paths: list[Path],
    output_root: Path,
    max_workers: int = 2,
    replicate_ids: set[str] | None = None,
    runner_by_task: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers < 1:
        raise ValueError("max_workers must be a positive integer")
    runners = DEFAULT_RUNNERS if runner_by_task is None else runner_by_task
    root = Path(output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    jobs: list[tuple[str, str, argparse.Namespace, Callable]] = []
    for raw_family_path in family_paths:
        family_path = Path(raw_family_path).resolve()
        family = json.loads(family_path.read_text(encoding="utf-8"))
        if family.get("schema_version") != "effectslice-confirmation-v2-family.v1":
            raise ValueError(f"invalid confirmation-v2 family: {family_path}")
        task_key = family["task_key"]
        if task_key not in runners:
            raise ValueError(f"no runner registered for {task_key}")
        for replicate in family["replicate_schedule"]:
            replicate_id = replicate["replicate_id"]
            if replicate_ids is not None and replicate_id not in replicate_ids:
                continue
            args = build_run_namespace(
                family_path=family_path,
                family=family,
                replicate=replicate,
                output_root=root,
            )
            if Path(args.output_dir).exists():
                records.append(
                    {
                        "task_key": task_key,
                        "replicate_id": replicate_id,
                        "status": "preserved",
                        "output_dir": Path(args.output_dir).as_posix(),
                    }
                )
                continue
            jobs.append((task_key, replicate_id, args, runners[task_key]))

    def execute(job):
        task_key, replicate_id, args, runner = job
        try:
            report = runner(args)
            return {
                "task_key": task_key,
                "replicate_id": replicate_id,
                "status": "completed",
                "output_dir": Path(args.output_dir).as_posix(),
                "pair_id": report.get("pair_id"),
            }
        except Exception as exc:  # noqa: BLE001 - preserve failed registered runs
            return {
                "task_key": task_key,
                "replicate_id": replicate_id,
                "status": "failed",
                "output_dir": Path(args.output_dir).as_posix(),
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:1000],
            }

    _write_progress(root, records)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            records.append(future.result())
            _write_progress(root, records)
    return _write_progress(root, records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run registered confirmation-v2 families")
    parser.add_argument("--family", action="append", type=Path, default=[])
    parser.add_argument(
        "--output-root",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "confirmation_v2",
    )
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--replicate-id", action="append", default=[])
    args = parser.parse_args()
    families = args.family or [
        RUN_ROOT / "artifacts" / "snap_mfse" / "confirmation_v2_family.json",
        RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v2_family.json",
    ]
    result = run_schedule(
        family_paths=families,
        output_root=args.output_root,
        max_workers=args.max_workers,
        replicate_ids=set(args.replicate_id) or None,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
