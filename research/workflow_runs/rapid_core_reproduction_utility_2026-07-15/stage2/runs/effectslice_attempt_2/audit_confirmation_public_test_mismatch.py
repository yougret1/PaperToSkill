from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


RUN_ROOT = Path(__file__).resolve().parent
V2_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v2"
V3_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v3_interleaved_calibration_r2"
OUTPUT_PATH = RUN_ROOT / "derived" / "confirmation_v3_public_test_mismatch_audit.json"
UNAVAILABLE_MESSAGE = "private scoring is unavailable before final submission"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def audit_transcript(payload: dict[str, Any]) -> dict[str, Any]:
    turns = payload.get("turns")
    if not isinstance(turns, list):
        raise ValueError("transcript turns must be a list")
    test_turns = [
        turn
        for turn in turns
        if isinstance(turn, dict)
        and isinstance(turn.get("action"), dict)
        and turn["action"].get("action") == "test"
    ]
    unavailable = [
        turn
        for turn in test_turns
        if turn.get("observation_status") == "unavailable"
        and turn.get("observation_message") == UNAVAILABLE_MESSAGE
    ]
    return {
        "turn_count": len(turns),
        "test_action_count": len(test_turns),
        "unavailable_test_count": len(unavailable),
        "affected": bool(unavailable),
    }


def _records(paths: Iterable[Path], component: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted(paths):
        audit = audit_transcript(_json(path))
        relative = path.relative_to(RUN_ROOT).as_posix()
        parts = path.relative_to(
            V2_ROOT if component == "real_task_confirmation" else V3_ROOT
        ).parts
        if component == "real_task_confirmation":
            task, replicate, condition = parts[:3]
            family = task
        else:
            family, replicate, condition = parts[:3]
            task = "toolformer_filter"
        records.append(
            {
                "component": component,
                "task": task,
                "family": family,
                "replicate_id": replicate,
                "condition": condition,
                "transcript_path": relative,
                "transcript_sha256": _sha256(path),
                **audit,
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    v2_paths = V2_ROOT.glob("*/*/*/transcript.json")
    v3_paths = V3_ROOT.glob("*/*/*/transcript.json")
    records = _records(v2_paths, "real_task_confirmation") + _records(
        v3_paths, "interleaved_calibration"
    )
    if not records:
        raise ValueError("no confirmation transcripts found")
    component_counts = Counter(row["component"] for row in records)
    affected_components = Counter(
        row["component"] for row in records if row["affected"]
    )
    condition_counts = Counter(
        f"{row['component']}:{row['condition']}"
        for row in records
        if row["affected"]
    )
    return {
        "schema_version": "effectslice-public-test-mismatch-audit.v1",
        "classification": "task_harness_contract_mismatch",
        "finding": (
            "Locked task prompts required a public test, but the final-only runner "
            "mapped every test action to an unavailable private-score response."
        ),
        "implication": (
            "V2 real-task and V3 calibration outcomes are preserved as historical "
            "evidence but are not clean estimates of the corrected harness."
        ),
        "run_count": len(records),
        "run_with_test_action_count": sum(
            row["test_action_count"] > 0 for row in records
        ),
        "affected_run_count": sum(row["affected"] for row in records),
        "test_action_count": sum(row["test_action_count"] for row in records),
        "unavailable_test_count": sum(
            row["unavailable_test_count"] for row in records
        ),
        "component_run_counts": dict(sorted(component_counts.items())),
        "component_affected_counts": dict(sorted(affected_components.items())),
        "affected_condition_counts": dict(sorted(condition_counts.items())),
        "all_test_actions_rejected_by_mismatch": all(
            row["test_action_count"] == row["unavailable_test_count"]
            for row in records
        ),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the V3 public-test mismatch")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    payload = build_audit()
    destination = args.output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({key: payload[key] for key in (
        "run_count",
        "affected_run_count",
        "run_with_test_action_count",
        "test_action_count",
        "unavailable_test_count",
    )}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
