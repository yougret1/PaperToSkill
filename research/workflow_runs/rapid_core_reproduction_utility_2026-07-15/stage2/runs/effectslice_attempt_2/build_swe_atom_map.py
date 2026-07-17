from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]


ATOM_DEFINITIONS = (
    ("A01", 36, 36, "aci_framing", "interface_contract", ()),
    ("A02", 37, 37, "simple_actions", "action_contract", ("A01",)),
    ("A03", 38, 38, "react_loop", "control_loop", ("A01", "A02")),
    ("A04", 39, 39, "bounded_localization", "search_action", ()),
    ("A05", 40, 40, "bounded_file_view", "inspection_action", ("A04",)),
    ("A06", 41, 41, "focused_edit", "edit_action", ("A05",)),
    ("A07", 42, 42, "edit_guardrail", "guardrail", ("A06",)),
    ("A08", 43, 43, "context_management", "context_control", ("A01", "A02")),
    ("A09", 49, 49, "resolved_cost_budget", "metric_budget_contract", ()),
)

CANDIDATE_ATOM_IDS = ("A04", "A05", "A06", "A07", "A09")


def dependency_closed(candidate_ids: tuple[str, ...], requires: dict[str, list[str]]) -> bool:
    candidate = set(candidate_ids)
    return bool(candidate) and all(
        atom_id in requires and set(requires[atom_id]).issubset(candidate)
        for atom_id in candidate
    )


def closed_deletion(
    candidate_ids: tuple[str, ...],
    removed_atom: str,
    requires: dict[str, list[str]],
) -> tuple[str, ...]:
    if removed_atom not in candidate_ids:
        raise ValueError("removed atom is not retained by the candidate")
    retained = set(candidate_ids)
    retained.remove(removed_atom)
    changed = True
    while changed:
        changed = False
        for atom_id in tuple(retained):
            if not set(requires[atom_id]).issubset(retained):
                retained.remove(atom_id)
                changed = True
    ordered = tuple(atom_id for atom_id in candidate_ids if atom_id in retained)
    if not ordered or not dependency_closed(ordered, requires):
        if not ordered:
            raise ValueError("deletion neighbor would be empty")
        raise ValueError("deletion neighbor is not dependency closed")
    return ordered


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
    *,
    title: str,
) -> str:
    selected = {atom["atom_id"]: atom for atom in atoms}
    if any(atom_id not in selected for atom_id in candidate_ids):
        raise ValueError("candidate contains an unknown atom")
    parts = [f"# {title}"]
    parts.extend(selected[atom_id]["source_text"].strip() for atom_id in candidate_ids)
    return "\n\n".join(parts).strip() + "\n"


def _digest_record(text: str, artifact_path: str) -> dict[str, Any]:
    return {
        "artifact_path": artifact_path,
        "artifact_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "context_sha256": hashlib.sha256(text.strip().encode("utf-8")).hexdigest(),
    }


def build_artifacts(
    source_path: Path,
    source_map_path: Path,
) -> tuple[dict[str, Any], dict[str, str]]:
    source = Path(source_path).resolve()
    source_map = Path(source_map_path).resolve()
    source_bytes = source.read_bytes()
    source_map_bytes = source_map.read_bytes()
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    source_map_digest = hashlib.sha256(source_map_bytes).hexdigest()
    lines, offsets = _line_offsets(source_bytes)
    atoms = []
    requires: dict[str, list[str]] = {}
    previous_byte_end = 0
    for atom_id, line_start, line_end_inclusive, symbol, role, dependencies in ATOM_DEFINITIONS:
        if line_start < 1 or line_end_inclusive < line_start or line_end_inclusive > len(lines):
            raise ValueError(f"invalid source line range for {atom_id}")
        byte_start = offsets[line_start - 1]
        byte_end = offsets[line_end_inclusive]
        if byte_start < previous_byte_end:
            raise ValueError("atom source spans overlap or are not canonical")
        source_text = source_bytes[byte_start:byte_end].decode("utf-8")
        if not source_text.strip():
            raise ValueError(f"empty source span for {atom_id}")
        atoms.append(
            {
                "atom_id": atom_id,
                "workflow_step": source_text.strip(),
                "source_text": source_text,
                "source_span": {
                    "file_digest": source_digest,
                    "byte_start": byte_start,
                    "byte_end": byte_end,
                    "line_start": line_start,
                    "line_end": line_end_inclusive + 1,
                },
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
        previous_byte_end = byte_end

    atom_ids = [atom["atom_id"] for atom in atoms]
    if atom_ids != sorted(atom_ids) or len(atom_ids) != len(set(atom_ids)):
        raise ValueError("atom definitions must be unique and canonical")
    if not dependency_closed(CANDIDATE_ATOM_IDS, requires):
        raise ValueError("candidate is not dependency closed")

    artifacts: dict[str, str] = {}
    candidate_path = "slice_v0.md"
    candidate_text = build_candidate_text(
        atoms,
        CANDIDATE_ATOM_IDS,
        title="SWE-agent Task-Local Procedural Slice",
    )
    artifacts[candidate_path] = candidate_text
    deletion_neighbors: dict[str, dict[str, Any]] = {}
    for removed_atom in CANDIDATE_ATOM_IDS:
        retained = closed_deletion(CANDIDATE_ATOM_IDS, removed_atom, requires)
        neighbor_id = f"minus_{removed_atom}"
        artifact_path = f"deletion_neighbors/slice_v0_{neighbor_id}.md"
        text = build_candidate_text(
            atoms,
            retained,
            title=f"SWE-agent Slice v0 Deletion Neighbor {neighbor_id}",
        )
        artifacts[artifact_path] = text
        deletion_neighbors[neighbor_id] = {
            "removed_atom_id": removed_atom,
            "atom_ids": list(retained),
            **_digest_record(text, artifact_path),
        }

    dependency_edges = [
        {"from": atom_id, "to": dependency}
        for atom_id in atom_ids
        for dependency in requires[atom_id]
    ]
    candidate_record = {
        "atom_ids": list(CANDIDATE_ATOM_IDS),
        "dependency_closed": True,
        **_digest_record(candidate_text, candidate_path),
        "deletion_neighbors": deletion_neighbors,
    }
    atom_map = {
        "schema_version": "effectslice-swe-source-atom-map.v1",
        "paper_id": "swe_agent",
        "task_id": "SWE-T2",
        "source_path": source.as_posix(),
        "source_sha256": source_digest,
        "source_map_path": source_map.as_posix(),
        "source_map_sha256": source_map_digest,
        "atoms": atoms,
        "dependency_nodes": atom_ids,
        "dependency_edges": dependency_edges,
        "requires": requires,
        "development_candidates": {"slice_v0": candidate_record},
        "evidence_boundary": (
            "Development source atomization and candidate neighbors only; "
            "not an EffectSlice admission or effectiveness result."
        ),
    }
    return atom_map, artifacts


def write_artifacts(
    source_path: Path,
    source_map_path: Path,
    output_dir: Path,
) -> dict[str, str]:
    atom_map, artifacts = build_artifacts(source_path, source_map_path)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    written = {}
    for relative_path, text in sorted(artifacts.items()):
        path = output / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written[relative_path] = str(path)
    atom_map_path = output / "source_atom_map.json"
    atom_map_path.write_text(
        json.dumps(atom_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written["source_atom_map.json"] = str(atom_map_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build exact SWE EffectSlice atoms")
    parser.add_argument(
        "--source",
        type=Path,
        default=PROJECT_ROOT / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md",
    )
    parser.add_argument(
        "--source-map",
        type=Path,
        default=PROJECT_ROOT
        / "generated_skills"
        / "real_reuse"
        / "swe_agent"
        / "references"
        / "source_map.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "artifacts" / "swe_t2",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            write_artifacts(args.source, args.source_map, args.output_dir),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
