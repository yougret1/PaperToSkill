"""Build and verify deterministic, tamper-evident EffectSlice evidence ledgers.

The detached sidecar detects accidental ledger corruption. A trusted external
copy of the ledger SHA-256 (for example, in a preregistration commit or stage
report) is required to detect an actor that can rewrite both files. This module
does not claim tamper-proof storage against an administrator or raw-volume
writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any, Iterable


RUN_ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "effectslice-evidence-ledger-v3.v1"
ALLOWED_PHASES = {"preregistration", "postrun"}
GENESIS_SHA256 = "0" * 64
MAX_LEDGER_BYTES = 16 * 1024 * 1024
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
LEDGER_FIELDS = {
    "schema_version",
    "phase",
    "evidence_boundary",
    "hash_algorithm",
    "source_roots",
    "file_count",
    "total_bytes",
    "genesis_sha256",
    "chain_root_sha256",
    "entries",
    "manifest_core_sha256",
}
ENTRY_FIELDS = {
    "sequence",
    "path",
    "size_bytes",
    "sha256",
    "previous_entry_sha256",
    "entry_sha256",
}


class EvidenceLedgerError(ValueError):
    """Raised when a ledger cannot be built or verified unambiguously."""


def sidecar_path(ledger_path: Path) -> Path:
    path = Path(ledger_path)
    return path.with_name(f"{path.name}.sha256")


def _is_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except (OSError, ValueError):
        return False
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(getattr(metadata, "st_file_attributes", 0) & flag)


def _reject_linked_components(path: Path, label: str) -> None:
    try:
        supplied = Path(path)
        if ".." in supplied.parts:
            raise EvidenceLedgerError(f"{label} must not traverse parents")
        absolute = Path(os.path.abspath(os.fspath(supplied)))
        for component in (*reversed(absolute.parents), absolute):
            if component.is_symlink() or _is_reparse_point(component):
                raise EvidenceLedgerError(f"{label} contains a linked path")
    except EvidenceLedgerError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} path is invalid") from exc


def _root_path(root: Path) -> Path:
    supplied = Path(root)
    if not supplied.is_absolute():
        raise EvidenceLedgerError("ledger root must be absolute")
    _reject_linked_components(supplied, "ledger root")
    try:
        resolved = supplied.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceLedgerError("ledger root cannot be resolved") from exc
    if not resolved.is_dir():
        raise EvidenceLedgerError("ledger root is missing")
    return resolved


def _path_under_root(raw_path: Path | str, root: Path, label: str) -> Path:
    try:
        supplied = Path(raw_path)
    except (TypeError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} path is invalid") from exc
    if not supplied.is_absolute():
        supplied = root / supplied
    _reject_linked_components(supplied, label)
    try:
        resolved = supplied.resolve()
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} escapes the ledger root") from exc
    return resolved


def _contains(parent: Path, child: Path) -> bool:
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EvidenceLedgerError("ledger value is not canonical JSON") from exc


def _pretty_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EvidenceLedgerError("ledger value is not deterministic JSON") from exc


def _file_signature(path: Path, label: str) -> tuple[int, int, int, int]:
    try:
        metadata = os.stat(path, follow_symlinks=False)
    except (OSError, TypeError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} metadata cannot be read") from exc
    if _is_reparse_point(path) or stat.S_ISLNK(metadata.st_mode):
        raise EvidenceLedgerError(f"{label} is a linked file")
    if not stat.S_ISREG(metadata.st_mode):
        raise EvidenceLedgerError(f"{label} is not a regular file")
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
    )


def _snapshot_file(path: Path, label: str) -> tuple[str, int]:
    signature_before = _file_signature(path, label)
    digest = hashlib.sha256()
    observed_bytes = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                observed_bytes += len(chunk)
    except (OSError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} cannot be read") from exc
    if _file_signature(path, label) != signature_before:
        raise EvidenceLedgerError(f"{label} changed while being hashed")
    if observed_bytes != signature_before[2]:
        raise EvidenceLedgerError(f"{label} size changed while being hashed")
    return digest.hexdigest(), observed_bytes


def _relative_posix(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    if not relative.parts:
        return "."
    return relative.as_posix()


def _prepare_sources(
    root: Path,
    sources: Iterable[Path | str],
    ledger_path: Path,
) -> tuple[list[Path], list[str]]:
    resolved = []
    for index, source in enumerate(sources):
        path = _path_under_root(source, root, f"source {index}")
        if not path.exists() or not (path.is_file() or path.is_dir()):
            raise EvidenceLedgerError(f"source {index} is missing")
        resolved.append(path)
    if not resolved:
        raise EvidenceLedgerError("at least one source is required")
    ordered = sorted(resolved, key=lambda path: _relative_posix(path, root))
    for index, first in enumerate(ordered):
        for second in ordered[index + 1 :]:
            if _contains(first, second) or _contains(second, first):
                raise EvidenceLedgerError("registered source roots overlap")
    output_sidecar = sidecar_path(ledger_path)
    for source in ordered:
        if _contains(source, ledger_path) or _contains(source, output_sidecar):
            raise EvidenceLedgerError("ledger output overlaps a registered source")
    return ordered, [_relative_posix(path, root) for path in ordered]


def _enumerate_files(sources: list[Path], root: Path) -> list[Path]:
    files: list[Path] = []
    for source in sources:
        if source.is_file():
            _file_signature(source, f"registered file {_relative_posix(source, root)}")
            files.append(source)
            continue
        if source.is_symlink() or _is_reparse_point(source):
            raise EvidenceLedgerError("registered source is a linked directory")
        for current_root, directory_names, file_names in os.walk(
            source, followlinks=False
        ):
            current = Path(current_root)
            for directory_name in tuple(directory_names):
                directory = current / directory_name
                if directory.is_symlink() or _is_reparse_point(directory):
                    raise EvidenceLedgerError(
                        f"registered source contains a linked directory: {directory}"
                    )
            directory_names.sort()
            for file_name in sorted(file_names):
                path = current / file_name
                _file_signature(path, f"registered file {_relative_posix(path, root)}")
                files.append(path)
    ordered = sorted(files, key=lambda path: _relative_posix(path, root))
    relative_paths = [_relative_posix(path, root) for path in ordered]
    if not ordered:
        raise EvidenceLedgerError("registered sources contain no files")
    if len(relative_paths) != len(set(relative_paths)):
        raise EvidenceLedgerError("registered sources contain duplicate files")
    return ordered


def _entry_payload(
    *,
    sequence: int,
    relative_path: str,
    size_bytes: int,
    digest: str,
    previous: str,
) -> dict[str, Any]:
    entry = {
        "sequence": sequence,
        "path": relative_path,
        "size_bytes": size_bytes,
        "sha256": digest,
        "previous_entry_sha256": previous,
    }
    entry["entry_sha256"] = hashlib.sha256(_canonical_bytes(entry)).hexdigest()
    return entry


def _build_payload(
    *,
    phase: str,
    evidence_boundary: str,
    source_roots: list[str],
    files: list[Path],
    root: Path,
) -> dict[str, Any]:
    entries = []
    previous = GENESIS_SHA256
    total_bytes = 0
    for sequence, path in enumerate(files, start=1):
        relative = _relative_posix(path, root)
        digest, size_bytes = _snapshot_file(path, f"registered file {relative}")
        entry = _entry_payload(
            sequence=sequence,
            relative_path=relative,
            size_bytes=size_bytes,
            digest=digest,
            previous=previous,
        )
        entries.append(entry)
        previous = entry["entry_sha256"]
        total_bytes += size_bytes
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": phase,
        "evidence_boundary": evidence_boundary,
        "hash_algorithm": "sha256",
        "source_roots": source_roots,
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "genesis_sha256": GENESIS_SHA256,
        "chain_root_sha256": previous,
        "entries": entries,
    }
    payload["manifest_core_sha256"] = hashlib.sha256(
        _canonical_bytes(payload)
    ).hexdigest()
    return payload


def _validate_registration(phase: Any, evidence_boundary: Any) -> tuple[str, str]:
    if not isinstance(phase, str) or phase not in ALLOWED_PHASES:
        raise EvidenceLedgerError("ledger phase is not registered")
    if not isinstance(evidence_boundary, str) or not evidence_boundary.strip():
        raise EvidenceLedgerError("evidence boundary must be nonempty")
    return phase, evidence_boundary


def _ledger_destination(path: Path, root: Path) -> Path:
    supplied = Path(path)
    if not supplied.is_absolute():
        raise EvidenceLedgerError("ledger output path must be absolute")
    destination = _path_under_root(supplied, root, "ledger output")
    if destination.suffix.lower() != ".json":
        raise EvidenceLedgerError("ledger output must be a JSON file")
    relative_parts = {part.lower() for part in destination.relative_to(root).parts}
    if "derived" not in relative_parts:
        raise EvidenceLedgerError("ledger output must be below a derived directory")
    return destination


def _write_exclusive(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except (OSError, ValueError) as exc:
        raise EvidenceLedgerError(
            f"ledger package file cannot be written: {path}"
        ) from exc


def build_ledger(
    root: Path,
    sources: Iterable[Path | str],
    ledger_path: Path,
    *,
    phase: str,
    evidence_boundary: str,
) -> dict[str, Any]:
    registered_phase, registered_boundary = _validate_registration(
        phase, evidence_boundary
    )
    resolved_root = _root_path(Path(root))
    destination = _ledger_destination(Path(ledger_path), resolved_root)
    resolved_sources, source_roots = _prepare_sources(
        resolved_root, sources, destination
    )
    package_dir = destination.parent
    if package_dir.exists():
        raise EvidenceLedgerError("ledger output requires a new package directory")
    files = _enumerate_files(resolved_sources, resolved_root)
    payload = _build_payload(
        phase=registered_phase,
        evidence_boundary=registered_boundary,
        source_roots=source_roots,
        files=files,
        root=resolved_root,
    )
    ledger_bytes = _pretty_json_bytes(payload)
    ledger_digest = hashlib.sha256(ledger_bytes).hexdigest()
    sidecar_bytes = f"{ledger_digest}  {destination.name}\n".encode("ascii")
    try:
        package_dir.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        raise EvidenceLedgerError("ledger package parent cannot be created") from exc
    _reject_linked_components(package_dir.parent, "ledger package parent")
    staging = Path(
        tempfile.mkdtemp(prefix=f".{package_dir.name}.staging-", dir=package_dir.parent)
    )
    try:
        staged_ledger = staging / destination.name
        _write_exclusive(staged_ledger, ledger_bytes)
        _write_exclusive(sidecar_path(staged_ledger), sidecar_bytes)
        if package_dir.exists():
            raise EvidenceLedgerError("ledger package directory appeared during build")
        try:
            staging.rename(package_dir)
        except (OSError, ValueError) as exc:
            raise EvidenceLedgerError("ledger package could not be published") from exc
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return payload


def _bounded_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    signature_before = _file_signature(path, label)
    if signature_before[2] > MAX_LEDGER_BYTES:
        raise EvidenceLedgerError(f"{label} exceeds the size limit")
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_LEDGER_BYTES + 1)
    except (OSError, ValueError) as exc:
        raise EvidenceLedgerError(f"{label} cannot be read") from exc
    if len(payload) > MAX_LEDGER_BYTES:
        raise EvidenceLedgerError(f"{label} exceeds the size limit")
    if _file_signature(path, label) != signature_before:
        raise EvidenceLedgerError(f"{label} changed while being read")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceLedgerError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise EvidenceLedgerError(f"{label} must be a JSON object")
    return value, payload


def _validate_sidecar(path: Path, ledger_name: str, actual_digest: str) -> None:
    sidecar = sidecar_path(path)
    _reject_linked_components(sidecar, "ledger sidecar")
    if not sidecar.is_file():
        raise EvidenceLedgerError("ledger sidecar is missing")
    signature_before = _file_signature(sidecar, "ledger sidecar")
    if signature_before[2] > 256:
        raise EvidenceLedgerError("ledger sidecar exceeds the size limit")
    try:
        with sidecar.open("rb") as handle:
            payload = handle.read(257)
    except (OSError, ValueError) as exc:
        raise EvidenceLedgerError("ledger sidecar cannot be read") from exc
    if (
        len(payload) > 256
        or _file_signature(sidecar, "ledger sidecar") != signature_before
    ):
        raise EvidenceLedgerError("ledger sidecar changed while being read")
    expected = f"{actual_digest}  {ledger_name}\n".encode("ascii")
    if payload != expected:
        raise EvidenceLedgerError("ledger sidecar digest does not match")


def _validated_payload_shape(payload: dict[str, Any]) -> None:
    if set(payload) != LEDGER_FIELDS:
        raise EvidenceLedgerError("ledger fields do not match the schema")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EvidenceLedgerError("ledger schema version is invalid")
    _validate_registration(payload.get("phase"), payload.get("evidence_boundary"))
    if payload.get("hash_algorithm") != "sha256":
        raise EvidenceLedgerError("ledger hash algorithm is invalid")
    if payload.get("genesis_sha256") != GENESIS_SHA256:
        raise EvidenceLedgerError("ledger genesis digest is invalid")
    claimed_core = payload.get("manifest_core_sha256")
    if (
        not isinstance(claimed_core, str)
        or SHA256_PATTERN.fullmatch(claimed_core) is None
    ):
        raise EvidenceLedgerError("ledger core digest is invalid")
    core = dict(payload)
    core.pop("manifest_core_sha256")
    actual_core = hashlib.sha256(_canonical_bytes(core)).hexdigest()
    if claimed_core != actual_core:
        raise EvidenceLedgerError("ledger core digest does not match")


def verify_ledger(
    root: Path,
    ledger_path: Path,
    *,
    expected_ledger_sha256: str | None = None,
) -> dict[str, Any]:
    resolved_root = _root_path(Path(root))
    path = _ledger_destination(Path(ledger_path), resolved_root)
    _reject_linked_components(path, "evidence ledger")
    if not path.is_file():
        raise EvidenceLedgerError("evidence ledger is missing")
    payload, ledger_bytes = _bounded_json_object(path, "evidence ledger")
    ledger_digest = hashlib.sha256(ledger_bytes).hexdigest()
    _validate_sidecar(path, path.name, ledger_digest)
    if expected_ledger_sha256 is not None:
        if (
            not isinstance(expected_ledger_sha256, str)
            or SHA256_PATTERN.fullmatch(expected_ledger_sha256) is None
            or expected_ledger_sha256 != ledger_digest
        ):
            raise EvidenceLedgerError("ledger does not match its external anchor")
    _validated_payload_shape(payload)
    raw_source_roots = payload.get("source_roots")
    if (
        not isinstance(raw_source_roots, list)
        or not raw_source_roots
        or any(not isinstance(value, str) or not value for value in raw_source_roots)
    ):
        raise EvidenceLedgerError("ledger source roots are invalid")
    sources, normalized_roots = _prepare_sources(resolved_root, raw_source_roots, path)
    if raw_source_roots != normalized_roots:
        raise EvidenceLedgerError("ledger source roots are not canonical")
    files = _enumerate_files(sources, resolved_root)
    actual_paths = [_relative_posix(file, resolved_root) for file in files]
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise EvidenceLedgerError("ledger entries are invalid")
    registered_paths = [
        entry.get("path") if isinstance(entry, dict) else None for entry in entries
    ]
    if registered_paths != actual_paths:
        raise EvidenceLedgerError("registered evidence file set has changed")
    if type(payload.get("file_count")) is not int or payload["file_count"] != len(
        entries
    ):
        raise EvidenceLedgerError("ledger file count is invalid")
    previous = GENESIS_SHA256
    total_bytes = 0
    for sequence, (entry, file_path) in enumerate(zip(entries, files), start=1):
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise EvidenceLedgerError("ledger entry fields are invalid")
        if (
            type(entry.get("sequence")) is not int
            or type(entry.get("size_bytes")) is not int
            or entry["size_bytes"] < 0
        ):
            raise EvidenceLedgerError("ledger entry integer fields are invalid")
        if (
            not isinstance(entry.get("path"), str)
            or not entry["path"]
            or any(
                not isinstance(entry.get(field), str)
                or SHA256_PATTERN.fullmatch(entry[field]) is None
                for field in (
                    "sha256",
                    "previous_entry_sha256",
                    "entry_sha256",
                )
            )
        ):
            raise EvidenceLedgerError("ledger entry string fields are invalid")
        if entry.get("sequence") != sequence:
            raise EvidenceLedgerError("ledger entry sequence is invalid")
        if entry.get("previous_entry_sha256") != previous:
            raise EvidenceLedgerError("ledger chain predecessor is invalid")
        digest, size_bytes = _snapshot_file(
            file_path, f"registered file {entry['path']}"
        )
        if entry.get("sha256") != digest or entry.get("size_bytes") != size_bytes:
            raise EvidenceLedgerError("registered evidence content has changed")
        unsigned = {key: entry[key] for key in ENTRY_FIELDS - {"entry_sha256"}}
        entry_digest = hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()
        if entry.get("entry_sha256") != entry_digest:
            raise EvidenceLedgerError("ledger entry digest does not match")
        previous = entry_digest
        total_bytes += size_bytes
    if payload.get("chain_root_sha256") != previous:
        raise EvidenceLedgerError("ledger chain root is invalid")
    if (
        type(payload.get("total_bytes")) is not int
        or payload["total_bytes"] != total_bytes
    ):
        raise EvidenceLedgerError("ledger total bytes are invalid")
    return {
        "valid": True,
        "phase": payload["phase"],
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "ledger_sha256": ledger_digest,
        "chain_root_sha256": previous,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or verify a deterministic EffectSlice evidence ledger"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--root", type=Path, default=RUN_ROOT)
    build.add_argument("--source", type=Path, action="append", required=True)
    build.add_argument("--ledger-path", type=Path, required=True)
    build.add_argument("--phase", choices=sorted(ALLOWED_PHASES), required=True)
    build.add_argument("--evidence-boundary", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--root", type=Path, default=RUN_ROOT)
    verify.add_argument("--ledger-path", type=Path, required=True)
    verify.add_argument("--expected-ledger-sha256")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "build":
            payload = build_ledger(
                args.root,
                args.source,
                args.ledger_path,
                phase=args.phase,
                evidence_boundary=args.evidence_boundary,
            )
            result = {
                "built": True,
                "phase": payload["phase"],
                "file_count": payload["file_count"],
                "total_bytes": payload["total_bytes"],
                "chain_root_sha256": payload["chain_root_sha256"],
            }
        else:
            result = verify_ledger(
                args.root,
                args.ledger_path,
                expected_ledger_sha256=args.expected_ledger_sha256,
            )
    except EvidenceLedgerError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
