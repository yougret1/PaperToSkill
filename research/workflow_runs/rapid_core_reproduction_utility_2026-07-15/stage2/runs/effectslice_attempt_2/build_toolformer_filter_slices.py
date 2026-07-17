from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dependency_closed(atom_ids: list[str], requires: dict[str, list[str]]) -> bool:
    retained = set(atom_ids)
    return all(set(requires[atom_id]).issubset(retained) for atom_id in atom_ids)


def _render_slice(
    candidate_id: str,
    atoms: list[dict[str, Any]],
    *,
    source_map_sha256: str,
) -> str:
    lines = [
        f"# Toolformer Loss-Filter Slice {candidate_id}",
        "",
        "Evidence boundary: frozen dependency-closed discovery candidate; not a result.",
        "",
        f"Source atom map SHA-256: `{source_map_sha256}`",
        "",
        "## Procedure",
        "",
    ]
    for index, atom in enumerate(atoms, start=1):
        lines.extend(
            [
                f"{index}. **{atom['title']}** (`{atom['atom_id']}`)",
                f"   {atom['instruction']}",
                "",
            ]
        )
    return "\n".join(lines)


def build_slice_candidates(atom_map_path: Path, output_dir: Path) -> dict[str, str]:
    source_path = Path(atom_map_path).resolve()
    source_bytes = source_path.read_bytes()
    atom_map = json.loads(source_bytes.decode("utf-8"))
    atoms = atom_map["atoms"]
    requires = atom_map["requires"]
    ordered_ids = [str(atom["atom_id"]) for atom in atoms]
    if len(ordered_ids) < 2 or len(set(ordered_ids)) != len(ordered_ids):
        raise ValueError("source atom map must contain distinct ordered atoms")
    if set(requires) != set(ordered_ids):
        raise ValueError("requires must cover every atom exactly")
    if not _dependency_closed(ordered_ids, requires):
        raise ValueError("full atom sequence is not dependency closed")

    destination = Path(output_dir).resolve()
    candidate_dir = destination / "candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    source_map_sha256 = _sha256_bytes(source_bytes)
    candidates = []
    for retained_count in range(1, len(atoms)):
        retained_atoms = atoms[:retained_count]
        retained_ids = ordered_ids[:retained_count]
        if not _dependency_closed(retained_ids, requires):
            raise ValueError(f"candidate prefix is not dependency closed: {retained_ids}")
        candidate_id = f"prefix_{retained_count:02d}"
        relative_path = Path("candidates") / f"{candidate_id}.md"
        artifact_text = _render_slice(
            candidate_id,
            retained_atoms,
            source_map_sha256=source_map_sha256,
        )
        artifact_path = destination / relative_path
        artifact_path.write_text(artifact_text, encoding="utf-8", newline="\n")
        deletion_neighbors = []
        for removed_index, removed_atom_id in enumerate(retained_ids):
            neighbor_ids = retained_ids[:removed_index]
            if neighbor_ids:
                deletion_neighbors.append(
                    {
                        "removed_atom_id": removed_atom_id,
                        "retained_atom_ids": neighbor_ids,
                        "candidate_id": f"prefix_{len(neighbor_ids):02d}",
                    }
                )
            else:
                deletion_neighbors.append(
                    {
                        "removed_atom_id": removed_atom_id,
                        "retained_atom_ids": [],
                        "condition": "B",
                    }
                )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "artifact_path": relative_path.as_posix(),
                "artifact_sha256": _sha256_bytes(artifact_text.encode("utf-8")),
                "retained_atom_ids": retained_ids,
                "retained_scc_count": retained_count,
                "dependency_closed": True,
                "strict_subset": True,
                "deletion_neighbors": deletion_neighbors,
            }
        )

    registry = {
        "schema_version": "effectslice-toolformer-filter-slice-registry.v1",
        "task_id": "TOOLFORMER-FILTER",
        "source_atom_map_path": source_path.name,
        "source_atom_map_sha256": source_map_sha256,
        "full_atom_ids": ordered_ids,
        "query_budget_Q": 24,
        "branch_cost_per_discovery_candidate": 2,
        "maximum_registered_discovery_branches": 2 * len(candidates),
        "candidate_order": [
            "retained_scc_count_ascending",
            "atom_ids_lexicographic",
        ],
        "candidates": candidates,
        "evidence_boundary": (
            "Frozen before discovery provider runs; contains no model outcomes or scores."
        ),
    }
    registry_path = destination / "slice_registry.json"
    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"registry_path": str(registry_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build frozen TOOLFORMER-FILTER slices")
    parser.add_argument(
        "--atom-map",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "source_atom_map.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter" / "slices",
    )
    args = parser.parse_args()
    print(json.dumps(build_slice_candidates(args.atom_map, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
