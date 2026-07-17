from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping


def validate_file_bindings(
    record: Mapping[str, Any],
    *,
    root: Path,
) -> dict[str, dict[str, str]]:
    binding_root = Path(root).resolve()
    prefixes = sorted(
        key.removesuffix("_path")
        for key in record
        if key.endswith("_path")
        and f"{key.removesuffix('_path')}_sha256" in record
    )
    verified: dict[str, dict[str, str]] = {}
    for prefix in prefixes:
        raw_path = record[f"{prefix}_path"]
        expected = record[f"{prefix}_sha256"]
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"{prefix} path must be nonempty")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"{prefix} digest must be a SHA-256 hex string")
        path = Path(raw_path)
        if not path.is_absolute():
            path = binding_root / path
        path = path.resolve()
        if not path.is_file():
            raise ValueError(f"{prefix} file is missing: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"{prefix} digest does not match the registered file")
        verified[prefix] = {"path": path.as_posix(), "sha256": actual}
    return verified


def require_new_output_dir(path: Path) -> Path:
    output = Path(path).resolve()
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ValueError(f"output directory already exists: {output}") from exc
    return output


def normalize_condition_order(values: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    execution_order = tuple(dict.fromkeys(values))
    if not execution_order or any(value not in {"B", "F", "S"} for value in execution_order):
        raise ValueError("conditions must be a nonempty sequence drawn from B/F/S")
    return execution_order, tuple(sorted(execution_order))
