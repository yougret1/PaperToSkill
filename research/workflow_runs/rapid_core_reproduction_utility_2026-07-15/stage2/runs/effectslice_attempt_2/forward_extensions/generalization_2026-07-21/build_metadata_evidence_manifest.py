from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREREG = ROOT / "preregistration"
OUTPUT = PREREG / "metadata_evidence_manifest.json"


def repo_root() -> Path:
    for candidate in (ROOT, *ROOT.parents):
        if (candidate / "paper" / "effectslice_aaai" / "main_v3.tex").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(repo: Path, relative: str) -> tuple[str, Path]:
    if relative.startswith(("paper/", "papers/", "research/")):
        return "repository", repo / relative
    return "forward_extension", ROOT / relative


def build() -> dict[str, object]:
    repo = repo_root()
    registry = json.loads(
        (PREREG / "paper_registry.json").read_text(encoding="utf-8")
    )
    entries: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for paper in registry["papers"]:
        for relative in paper["metadata_evidence"]:
            scope, path = resolve(repo, relative)
            key = (scope, relative)
            if key in seen:
                continue
            seen.add(key)
            if not path.is_file():
                raise FileNotFoundError(f"metadata evidence missing: {relative}")
            entries.append(
                {
                    "scope": scope,
                    "path": relative,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "paper_ids": sorted(
                        item["paper_id"]
                        for item in registry["papers"]
                        if relative in item["metadata_evidence"]
                    ),
                }
            )
    stage_report = ROOT / "stage_report_2_6.json"
    entries.append(
        {
            "scope": "forward_extension",
            "path": "stage_report_2_6.json",
            "bytes": stage_report.stat().st_size,
            "sha256": sha256(stage_report),
            "paper_ids": [],
        }
    )
    return {
        "schema_version": "effectslice-fg1-metadata-evidence-hashes.v1",
        "hash_algorithm": "sha256",
        "entries": sorted(entries, key=lambda item: (item["scope"], item["path"])),
    }


def main() -> None:
    OUTPUT.write_text(
        json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
