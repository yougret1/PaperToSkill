from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_MANIFEST = RUN_ROOT / "manuscript" / "generated_results_manifest_v5.json"
SCHEMA = "effectslice-paper-results-manifest.v5"
BLOCK_EVIDENCE_FILENAMES = frozenset({"pair_manifest.json", "run_report.json"})
CONDITION_EVIDENCE_FILENAMES = frozenset(
    {"candidate.patch", "run_result.json", "transcript.json"}
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_entries(
    node: Any, location: str = "$"
) -> Iterator[tuple[str, dict[str, str]]]:
    if isinstance(node, dict):
        if isinstance(node.get("path"), str) and isinstance(node.get("sha256"), str):
            yield location, node
            return
        for key, value in node.items():
            yield from _artifact_entries(value, f"{location}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _artifact_entries(value, f"{location}[{index}]")


def _resolve_artifact(project_root: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute():
        raise ValueError(f"canonical manifest contains an absolute path: {raw_path}")
    root = project_root.resolve()
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"artifact escapes project root: {raw_path}")
    return resolved


def _verify_raw_output_set(
    version: str, output_set: dict[str, Any], run_root: Path
) -> list[str]:
    inventory = output_set.get("raw_inventory")
    if not isinstance(inventory, list) or not inventory:
        raise ValueError(f"{version} raw evidence inventory is missing")

    raw_root = output_set.get("raw_root")
    if not isinstance(raw_root, str):
        raise ValueError(f"{version} raw evidence root is missing")
    relative_raw_root = Path(raw_root)
    if relative_raw_root.is_absolute():
        raise ValueError(f"{version} raw evidence root is absolute: {raw_root}")

    normalized: list[dict[str, str]] = []
    checked: list[str] = []
    root = run_root.resolve()
    unresolved_source = root / relative_raw_root
    source = unresolved_source.resolve()
    if not source.is_relative_to(root):
        raise ValueError(f"{version} raw evidence root escapes run root: {raw_root}")
    if unresolved_source.is_symlink() or not source.is_dir():
        raise ValueError(f"{version} raw evidence root is missing or linked")

    enumerated: list[str] = []
    for path in source.rglob("*"):
        relative_to_output = path.relative_to(source)
        is_block_file = (
            len(relative_to_output.parts) == 3
            and path.name in BLOCK_EVIDENCE_FILENAMES
        )
        is_condition_file = (
            len(relative_to_output.parts) == 4
            and path.name in CONDITION_EVIDENCE_FILENAMES
        )
        if not is_block_file and not is_condition_file:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{version} canonical raw evidence is missing or linked")
        enumerated.append(path.relative_to(root).as_posix())
    enumerated.sort()

    for index, entry in enumerate(inventory):
        if not isinstance(entry, dict):
            raise ValueError(f"{version} raw evidence entry {index} is malformed")
        raw_path = entry.get("run_relative_path")
        expected = entry.get("sha256")
        if not isinstance(raw_path, str) or not isinstance(expected, str):
            raise ValueError(f"{version} raw evidence entry {index} is malformed")
        relative = Path(raw_path)
        if relative.is_absolute():
            raise ValueError(f"{version} raw evidence path is absolute: {raw_path}")
        unresolved_path = root / relative
        path = unresolved_path.resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"{version} raw evidence escapes run root: {raw_path}")
        if unresolved_path.is_symlink() or not path.is_file():
            raise ValueError(f"{version} raw evidence is missing: {raw_path}")
        observed = _sha256(path)
        if observed != expected:
            raise ValueError(f"{version} raw evidence file digest mismatch: {raw_path}")
        normalized.append({"path": relative.as_posix(), "sha256": expected})
        checked.append(relative.as_posix())

    if len(set(checked)) != len(checked):
        raise ValueError(f"{version} raw evidence inventory contains duplicate paths")
    if checked != sorted(checked):
        raise ValueError(f"{version} raw evidence inventory is not path-sorted")
    if checked != enumerated:
        unexpected = sorted(set(enumerated) - set(checked))
        missing = sorted(set(checked) - set(enumerated))
        raise ValueError(
            f"{version} canonical raw evidence set mismatch: "
            f"unexpected={unexpected[:3]}, missing={missing[:3]}"
        )
    if len(checked) != int(output_set.get("raw_file_count", 0)):
        raise ValueError(f"{version} raw file count mismatch")

    digest_payload = json.dumps(
        normalized, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    observed_digest = hashlib.sha256(digest_payload).hexdigest()
    if observed_digest != output_set.get("raw_evidence_digest"):
        raise ValueError(f"{version} raw evidence digest mismatch")
    return checked


def verify_manifest(manifest_path: Path, project_root: Path) -> dict[str, Any]:
    source = Path(manifest_path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != SCHEMA:
        raise ValueError("unexpected release manifest schema")
    if payload.get("canonical") is not True or payload.get("path_root") != "project_root":
        raise ValueError("release manifest is not marked canonical and relocatable")
    if set(payload.get("pre_run_roots", {})) != {"v4", "v5"}:
        raise ValueError("release manifest must bind both pre-run roots")
    if set(payload.get("output_sets", {})) != {"v4", "v5"}:
        raise ValueError("release manifest must bind both raw output sets")
    if set(payload.get("decisions", {})) != {"v4", "v5"}:
        raise ValueError("release manifest must record both schedule decisions")
    if len(payload.get("supersedes", [])) < 3:
        raise ValueError("release manifest does not identify historical manifests")

    raw_run_root = payload.get("run_root")
    if not isinstance(raw_run_root, str):
        raise ValueError("release manifest does not identify its run root")
    run_root = _resolve_artifact(Path(project_root), raw_run_root)
    if run_root.is_symlink() or not run_root.is_dir():
        raise ValueError("release manifest run root is missing")

    raw_checked: list[str] = []
    for version, output_set in payload["output_sets"].items():
        digest = output_set.get("raw_evidence_digest")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"{version} raw evidence digest is malformed")
        if int(output_set.get("raw_file_count", 0)) <= 0:
            raise ValueError(f"{version} raw file count is missing")
        raw_checked.extend(_verify_raw_output_set(version, output_set, run_root))

    checked: list[str] = []
    for location, artifact in _artifact_entries(payload):
        path = _resolve_artifact(Path(project_root), artifact["path"])
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"artifact is missing or not a regular file: {location}")
        observed = _sha256(path)
        if observed != artifact["sha256"]:
            raise ValueError(f"artifact digest mismatch: {location}")
        checked.append(artifact["path"])

    if len(checked) < 20:
        raise ValueError("release manifest binds too few directly verified artifacts")
    return {
        "schema_version": "effectslice-release-verification.v1",
        "manifest": source.as_posix(),
        "project_root": Path(project_root).resolve().as_posix(),
        "checked_artifacts": len(checked),
        "checked_raw_files": len(raw_checked),
        "status": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the portable EffectSlice release")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    print(json.dumps(verify_manifest(args.manifest, args.project_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
