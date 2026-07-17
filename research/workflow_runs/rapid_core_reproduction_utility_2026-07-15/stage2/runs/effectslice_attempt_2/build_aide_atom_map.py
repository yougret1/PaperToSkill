from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]


ATOM_DEFINITIONS = (
    ("A01", 36, 36, "objective_function", "objective", ()),
    ("A02", 37, 37, "iterative_tree_search", "search_loop", ("A01",)),
    ("A03", 38, 38, "solution_tree_state", "state", ("A02",)),
    ("A04", 39, 39, "draft_debug_improve_policy", "policy", ("A03",)),
    ("A05", 40, 40, "focused_coding_actions", "action", ("A01",)),
    ("A06", 41, 41, "compact_history_summary", "context_control", ("A03",)),
    ("A07", 42, 42, "static_data_preview", "task_observation", ("A01",)),
    ("A08", 43, 43, "stateless_integrated_search", "integration", ("A04", "A05", "A06", "A07")),
    ("A09", 49, 49, "submission_metric_contract", "output_metric_contract", ("A01",)),
    ("A10", 57, 60, "failure_boundaries", "failure_boundary", ()),
    ("A11", 66, 67, "harness_compatibility", "execution_contract", ()),
    ("A12", 68, 69, "provenance_and_failure_log", "provenance_contract", ()),
)

CANDIDATE_ATOM_IDS = ("A01", "A05", "A07", "A09", "A11")
MINIMAL_CANDIDATE_ATOM_IDS = ("A01", "A05")
SINGLETON_CANDIDATE_ATOM_IDS = ("A01",)


def dependency_closed(candidate_ids: tuple[str, ...], requires: dict[str, list[str]]) -> bool:
    candidate = set(candidate_ids)
    return bool(candidate) and all(
        atom_id in requires and set(requires[atom_id]).issubset(candidate)
        for atom_id in candidate
    )


def _line_offsets(source_bytes: bytes) -> tuple[list[bytes], list[int]]:
    lines = source_bytes.splitlines(keepends=True)
    offsets = []
    cursor = 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line)
    offsets.append(cursor)
    return lines, offsets


def build_candidate_text(
    atoms: list[dict[str, Any]],
    candidate_ids: tuple[str, ...],
) -> str:
    selected = {atom["atom_id"]: atom for atom in atoms}
    if any(atom_id not in selected for atom_id in candidate_ids):
        raise ValueError("candidate contains an unknown atom")
    parts = [
        "# AIDE Task-Local Procedural Slice",
        *[selected[atom_id]["source_text"].strip() for atom_id in candidate_ids],
    ]
    return "\n\n".join(parts).strip() + "\n"


def build_artifacts(source_path: Path) -> tuple[dict[str, Any], str]:
    source = Path(source_path).resolve()
    source_bytes = source.read_bytes()
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    lines, offsets = _line_offsets(source_bytes)
    atoms = []
    requires: dict[str, list[str]] = {}
    for atom_id, line_start, line_end_inclusive, symbol, role, dependencies in ATOM_DEFINITIONS:
        if line_end_inclusive > len(lines):
            raise ValueError(f"source no longer contains {atom_id} line range")
        byte_start = offsets[line_start - 1]
        byte_end = offsets[line_end_inclusive]
        source_text = source_bytes[byte_start:byte_end].decode("utf-8")
        if not source_text.strip():
            raise ValueError(f"empty source span for {atom_id}")
        span = {
            "file_digest": source_digest,
            "byte_start": byte_start,
            "byte_end": byte_end,
            "line_start": line_start,
            "line_end": line_end_inclusive + 1,
        }
        atoms.append(
            {
                "atom_id": atom_id,
                "workflow_step": source_text.strip(),
                "source_text": source_text,
                "source_span": span,
                "executable_region": {
                    "file_digest": source_digest,
                    "byte_start": byte_start,
                    "byte_end": byte_end,
                    "symbol": symbol,
                },
                "contract_role": role,
            }
        )
        requires[atom_id] = list(dependencies)

    atom_ids = [atom["atom_id"] for atom in atoms]
    if atom_ids != sorted(atom_ids) or len(atom_ids) != len(set(atom_ids)):
        raise ValueError("atom definitions must be unique and canonical")
    if not dependency_closed(CANDIDATE_ATOM_IDS, requires):
        raise ValueError("candidate is not dependency closed")
    dependency_edges = [
        {"from": atom_id, "to": dependency}
        for atom_id in atom_ids
        for dependency in requires[atom_id]
    ]
    candidate_text = build_candidate_text(atoms, CANDIDATE_ATOM_IDS)
    minimal_candidate_text = build_candidate_text(atoms, MINIMAL_CANDIDATE_ATOM_IDS)
    singleton_candidate_text = build_candidate_text(atoms, SINGLETON_CANDIDATE_ATOM_IDS)
    atom_map = {
        "schema_version": "effectslice-source-atom-map.v2",
        "paper_id": "aide",
        "task_id": "AIDE-T2",
        "source_path": source.as_posix(),
        "source_sha256": source_digest,
        "atoms": atoms,
        "dependency_nodes": atom_ids,
        "dependency_edges": dependency_edges,
        "requires": requires,
        "candidate_atom_ids": list(CANDIDATE_ATOM_IDS),
        "candidate_dependency_closed": True,
        "candidate_sha256": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest(),
        "development_candidates": {
            "slice_v0": {
                "atom_ids": list(CANDIDATE_ATOM_IDS),
                "sha256": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest(),
                "artifact_sha256": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest(),
                "context_sha256": hashlib.sha256(candidate_text.strip().encode("utf-8")).hexdigest(),
            },
            "slice_v1": {
                "atom_ids": list(MINIMAL_CANDIDATE_ATOM_IDS),
                "sha256": hashlib.sha256(minimal_candidate_text.encode("utf-8")).hexdigest(),
                "artifact_sha256": hashlib.sha256(minimal_candidate_text.encode("utf-8")).hexdigest(),
                "context_sha256": hashlib.sha256(minimal_candidate_text.strip().encode("utf-8")).hexdigest(),
            },
            "slice_v2": {
                "atom_ids": list(SINGLETON_CANDIDATE_ATOM_IDS),
                "sha256": hashlib.sha256(singleton_candidate_text.encode("utf-8")).hexdigest(),
                "artifact_sha256": hashlib.sha256(singleton_candidate_text.encode("utf-8")).hexdigest(),
                "context_sha256": hashlib.sha256(singleton_candidate_text.strip().encode("utf-8")).hexdigest(),
            },
        },
        "evidence_boundary": (
            "Development atomization and source-preserving candidate only; "
            "not an EffectSlice admission or effectiveness result."
        ),
    }
    return atom_map, candidate_text


def write_artifacts(source_path: Path, output_dir: Path) -> dict[str, str]:
    atom_map, candidate_text = build_artifacts(source_path)
    minimal_candidate_text = build_candidate_text(
        atom_map["atoms"],
        MINIMAL_CANDIDATE_ATOM_IDS,
    )
    singleton_candidate_text = build_candidate_text(
        atom_map["atoms"],
        SINGLETON_CANDIDATE_ATOM_IDS,
    )
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    atom_map_path = output / "source_atom_map.json"
    candidate_path = output / "slice_v0.md"
    minimal_candidate_path = output / "slice_v1.md"
    singleton_candidate_path = output / "slice_v2.md"
    atom_map_path.write_text(
        json.dumps(atom_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    candidate_path.write_text(candidate_text, encoding="utf-8")
    minimal_candidate_path.write_text(minimal_candidate_text, encoding="utf-8")
    singleton_candidate_path.write_text(singleton_candidate_text, encoding="utf-8")
    return {
        "source_atom_map": str(atom_map_path),
        "candidate_slice": str(candidate_path),
        "minimal_candidate_slice": str(minimal_candidate_path),
        "singleton_candidate_slice": str(singleton_candidate_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build exact AIDE EffectSlice atoms and slice v0")
    parser.add_argument(
        "--source",
        type=Path,
        default=PROJECT_ROOT / "generated_skills" / "aide" / "SKILL.md",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "artifacts" / "aide_t2",
    )
    args = parser.parse_args()
    print(json.dumps(write_artifacts(args.source, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
