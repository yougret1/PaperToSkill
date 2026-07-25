from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


EXPERIMENT_ROOT = Path(__file__).resolve().parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

import controls_v2  # noqa: E402
import full_grid_analysis  # noqa: E402,F401
import full_grid_registration  # noqa: E402
import full_grid_runner  # noqa: E402,F401


JOINT_FREEZE = EXPERIMENT_ROOT / "joint_freeze.json"
NO_CALL_RECORD = EXPERIMENT_ROOT / "no_call_verification.json"
FULL_GRID_REGISTRATION = full_grid_registration.DEFAULT_OUTPUT
CONTROLS_REGISTRATION = controls_v2.DEFAULT_REGISTRATION
SCHEMA_VERSION = "effectslice-forward-four-experiment-joint-freeze.v1"
SOURCE_PATHS = (
    EXPERIMENT_ROOT / "full_grid_registration.py",
    EXPERIMENT_ROOT / "full_grid_runner.py",
    EXPERIMENT_ROOT / "full_grid_analysis.py",
    EXPERIMENT_ROOT / "controls_v2.py",
    EXPERIMENT_ROOT / "protocol_freeze.py",
    EXPERIMENT_ROOT / "tests" / "test_forward_protocol.py",
)


class FreezeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def load_json(path: Path) -> Any:
    return full_grid_registration.load_json(path)


def atomic_json(path: Path, value: object) -> None:
    full_grid_registration.atomic_json(path, value)


def sha256_file(path: Path) -> str:
    return full_grid_registration.sha256_file(path)


def build() -> dict[str, Any]:
    require(not JOINT_FREEZE.exists(), "joint freeze already exists")
    full_manifest = full_grid_registration.build(FULL_GRID_REGISTRATION)
    controls_manifest = controls_v2.build(CONTROLS_REGISTRATION)
    return {
        "status": "built",
        "provider_calls_started": False,
        "full_grid_registration_bundle_sha256": full_manifest["bundle_sha256"],
        "controls_v2_registration_bundle_sha256": controls_manifest["bundle_sha256"],
        "rows_per_full_grid_repeat": full_grid_registration.ROWS_PER_REPEAT,
        "full_grid_rows": full_grid_registration.TOTAL_REPEAT_ROWS,
        "controls_v2_rows": controls_v2.REGISTERED_ROWS,
        "total_registered_rows": full_grid_registration.TOTAL_REPEAT_ROWS
        + controls_v2.REGISTERED_ROWS,
    }


def freeze() -> dict[str, Any]:
    require(not JOINT_FREEZE.exists(), "joint freeze already exists")
    for path in SOURCE_PATHS:
        require(path.is_file(), f"missing freeze source: {path}")
    full_grid_registration.verify(FULL_GRID_REGISTRATION)
    controls_v2.verify_registration(CONTROLS_REGISTRATION)
    full = full_grid_registration.freeze(FULL_GRID_REGISTRATION, SOURCE_PATHS)
    controls = controls_v2.freeze_registration(CONTROLS_REGISTRATION, list(SOURCE_PATHS))
    source_records = [
        {
            "path": path.relative_to(EXPERIMENT_ROOT).as_posix(),
            "sha256": sha256_file(path),
        }
        for path in SOURCE_PATHS
    ]
    value = {
        "schema_version": SCHEMA_VERSION,
        "frozen_at_utc": full_grid_registration.fg1.utc_now(),
        "provider_calls_started": False,
        "semantic_rerun_allowed": False,
        "source_fg5_bundle_sha256": full_grid_registration.EXPECTED_FG5_BUNDLE,
        "experiments": {
            "Controls-v2": {
                "registered_rows": controls_v2.REGISTERED_ROWS,
                "registration_bundle_sha256": controls[
                    "registration_bundle_sha256"
                ],
                "freeze_sha256": sha256_file(CONTROLS_REGISTRATION / "freeze.json"),
            },
            "FG6": {
                "registered_rows": full_grid_registration.ROWS_PER_REPEAT,
                "registration_bundle_sha256": full[
                    "registration_bundle_sha256"
                ],
            },
            "FG7": {
                "registered_rows": full_grid_registration.ROWS_PER_REPEAT,
                "registration_bundle_sha256": full[
                    "registration_bundle_sha256"
                ],
            },
            "FG8": {
                "registered_rows": full_grid_registration.ROWS_PER_REPEAT,
                "registration_bundle_sha256": full[
                    "registration_bundle_sha256"
                ],
            },
        },
        "full_grid_freeze_sha256": sha256_file(
            FULL_GRID_REGISTRATION / "freeze.json"
        ),
        "registered_accounting": {
            "rows_per_full_grid_repeat": full_grid_registration.ROWS_PER_REPEAT,
            "full_grid_repeat_count": len(full_grid_registration.REPEAT_IDS),
            "full_grid_rows": full_grid_registration.TOTAL_REPEAT_ROWS,
            "controls_v2_rows": controls_v2.REGISTERED_ROWS,
            "total_registered_rows": full_grid_registration.TOTAL_REPEAT_ROWS
            + controls_v2.REGISTERED_ROWS,
            "operational_preflight_requests_excluded": True,
        },
        "source_records": source_records,
    }
    atomic_json(JOINT_FREEZE, value)
    return verify(record=True)


def verify(*, record: bool) -> dict[str, Any]:
    require(JOINT_FREEZE.is_file(), "joint freeze is missing")
    full = full_grid_registration.verify(FULL_GRID_REGISTRATION, require_frozen=True)
    controls = controls_v2.verify_registration(
        CONTROLS_REGISTRATION, require_frozen=True
    )
    joint = load_json(JOINT_FREEZE)
    accounting = joint["registered_accounting"]
    require(accounting["rows_per_full_grid_repeat"] == 1296, "per-repeat count changed")
    require(accounting["full_grid_rows"] == 3888, "full-grid total changed")
    require(accounting["controls_v2_rows"] == 96, "Controls-v2 count changed")
    require(accounting["total_registered_rows"] == 3984, "registered total changed")
    require(joint["provider_calls_started"] is False, "pre-call freeze state changed")
    require(
        joint["full_grid_freeze_sha256"]
        == sha256_file(FULL_GRID_REGISTRATION / "freeze.json"),
        "full-grid freeze changed",
    )
    require(
        joint["experiments"]["Controls-v2"]["freeze_sha256"]
        == sha256_file(CONTROLS_REGISTRATION / "freeze.json"),
        "Controls-v2 freeze changed",
    )
    for repeat_id in full_grid_registration.REPEAT_IDS:
        experiment = joint["experiments"][repeat_id]
        require(experiment["registered_rows"] == 1296, f"row count changed: {repeat_id}")
        require(
            experiment["registration_bundle_sha256"]
            == full["registration_bundle_sha256"],
            f"registration binding changed: {repeat_id}",
        )
    require(
        joint["experiments"]["Controls-v2"]["registration_bundle_sha256"]
        == controls["registration_bundle_sha256"],
        "Controls-v2 registration binding changed",
    )
    for source in joint["source_records"]:
        path = EXPERIMENT_ROOT / source["path"]
        require(path.is_file(), f"missing frozen source: {source['path']}")
        require(sha256_file(path) == source["sha256"], f"frozen source changed: {source['path']}")
    value = {
        "schema_version": "effectslice-forward-four-experiment-no-call-verification.v1",
        "verified_at_utc": full_grid_registration.fg1.utc_now(),
        "status": "passed",
        "provider_calls_started": False,
        "joint_freeze_sha256": sha256_file(JOINT_FREEZE),
        "source_fg5_bundle_sha256": full_grid_registration.EXPECTED_FG5_BUNDLE,
        "full_grid_registration_bundle_sha256": full[
            "registration_bundle_sha256"
        ],
        "controls_v2_registration_bundle_sha256": controls[
            "registration_bundle_sha256"
        ],
        "rows_per_full_grid_repeat": 1296,
        "full_grid_rows": 3888,
        "controls_v2_rows": 96,
        "total_registered_rows": 3984,
    }
    if record:
        atomic_json(NO_CALL_RECORD, value)
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "freeze", "verify"))
    parser.add_argument("--record", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        value = build()
    elif args.command == "freeze":
        value = freeze()
    else:
        value = verify(record=args.record)
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        FreezeError,
        full_grid_registration.RegistrationError,
        controls_v2.ControlsError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
