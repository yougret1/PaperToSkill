from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "preregistration" / "bundle_hash_manifest.json"
BOUND_PATHS = [
    "analyze_sla_operating_characteristics.py",
    "build_metadata_evidence_manifest.py",
    "build_preregistration_hash_manifest.py",
    "build_stage_2_2_registration.py",
    "materialization_verifier_v2.py",
    "preregistration/candidate_matrix.json",
    "preregistration/experiment_plan.json",
    "preregistration/experiment_plan.md",
    "preregistration/figure_statistical_plan.json",
    "preregistration/materialization_contract.json",
    "preregistration/metadata_evidence_manifest.json",
    "preregistration/model_ablation_registry.json",
    "preregistration/paper_registry.json",
    "preregistration/sla_operating_characteristics.json",
    "preregistration_verifier_v3.py",
    "tests/test_forward_preregistration.py",
    "tests/test_materialization_semantics.py",
    "tests/test_preregistration_mutations.py",
    "verify_forward_preregistration.py",
    "verify_forward_preregistration_v2.py",
    "verify_stage_2_3_materialization.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> dict[str, object]:
    files: list[dict[str, object]] = []
    canonical_pairs: list[str] = []
    for relative in sorted(BOUND_PATHS):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"hash-bound file is missing: {relative}")
        digest = sha256(path)
        files.append(
            {"path": relative, "bytes": path.stat().st_size, "sha256": digest}
        )
        canonical_pairs.append(f"{relative}\0{digest}")
    bundle = hashlib.sha256("\n".join(canonical_pairs).encode()).hexdigest()
    return {
        "schema_version": "effectslice-fg1-bundle-hashes.v1",
        "hash_algorithm": "sha256",
        "self_hash_excluded": True,
        "canonicalization": "sorted relative_path + NUL + sha256, joined by LF",
        "files": files,
        "bundle_sha256": bundle,
    }


def main() -> None:
    OUTPUT.write_text(
        json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
