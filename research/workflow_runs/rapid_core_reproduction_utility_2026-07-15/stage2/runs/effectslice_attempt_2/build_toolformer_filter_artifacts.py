from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
SOURCE_RELATIVE_PATH = Path("papers/extracted/toolformer.txt")

ATOM_SPECS = (
    {
        "atom_id": "T01",
        "title": "Normalize the decreasing future-token weights",
        "instruction": (
            "Let t = j - i, so the first future token uses t = 0. Use raw "
            "weight max(0, 1 - 0.2 * t), then divide every raw weight by the "
            "sum over offsets."
        ),
        "line_numbers": tuple(range(268, 273)),
        "contract_role": "paper_weight_schedule",
    },
    {
        "atom_id": "T02",
        "title": "Compute weighted future-token loss",
        "instruction": (
            "For each conditioning prefix, compute negative weighted log "
            "probability over the future tokens using the normalized weights."
        ),
        "line_numbers": tuple(range(134, 146)),
        "contract_role": "weighted_cross_entropy",
    },
    {
        "atom_id": "T03",
        "title": "Use the stronger counterfactual baseline",
        "instruction": (
            "Let L_empty be the loss with no API call and L_call_only the loss "
            "with the call but no result; set L_minus = min(L_empty, L_call_only)."
        ),
        "line_numbers": tuple(range(146, 159)),
        "contract_role": "counterfactual_comparator",
    },
    {
        "atom_id": "T04",
        "title": "Keep calls that meet the filtering threshold",
        "instruction": (
            "Let L_plus be the loss with the call and result. Compute margin = "
            "L_minus - L_plus and keep the call exactly when margin >= tau_filter."
        ),
        "line_numbers": tuple(range(159, 172)),
        "contract_role": "inclusive_filter_decision",
    },
    {
        "atom_id": "T05",
        "title": "Apply the rule to every proposed call in order",
        "instruction": (
            "Evaluate every executed candidate call independently, filter all "
            "candidates with the same rule, and preserve candidate order in the output."
        ),
        "line_numbers": (76, 77, 78, 79),
        "contract_role": "batched_candidate_filtering",
    },
)

REQUIRES = {
    "T01": [],
    "T02": ["T01"],
    "T03": ["T02"],
    "T04": ["T03"],
    "T05": ["T04"],
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _line_spans(source: bytes) -> dict[int, dict[str, Any]]:
    spans: dict[int, dict[str, Any]] = {}
    offset = 0
    for line_number, raw_line in enumerate(source.splitlines(keepends=True), start=1):
        end = offset + len(raw_line)
        spans[line_number] = {
            "byte_start": offset,
            "byte_end": end,
            "line_start": line_number,
            "line_end": line_number,
            "source_text": raw_line.decode("utf-8"),
        }
        offset = end
    return spans


def _render_card(source_sha256: str) -> str:
    lines = [
        "# Toolformer API-Call Loss-Filter Execution Card",
        "",
        "Evidence boundary: task-local paper procedure derived from Toolformer lines 76-79, 134-171, and 268-272.",
        "It does not expose scorer cases or reference code.",
        "",
        f"Source SHA-256: `{source_sha256}`",
        "",
        "## Procedure",
        "",
    ]
    for index, atom in enumerate(ATOM_SPECS, start=1):
        lines.extend(
            [
                f"{index}. **{atom['title']}** (`{atom['atom_id']}`)",
                f"   {atom['instruction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Validation Boundary",
            "",
            "- Treat inputs as token log probabilities; lower weighted loss is better.",
            "- Return one Boolean decision and one finite margin per candidate.",
            "- Preserve the inclusive threshold tie and the paper counterfactual minimum.",
            "- Do not infer full Toolformer training or downstream benchmark claims from this task.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifacts(project_root: Path, output_dir: Path) -> dict[str, str]:
    root = Path(project_root).resolve()
    source_path = root / SOURCE_RELATIVE_PATH
    source = source_path.read_bytes()
    spans = _line_spans(source)
    source_sha256 = _sha256(source)
    atoms = []
    for spec in ATOM_SPECS:
        source_spans = []
        for line_number in spec["line_numbers"]:
            if line_number not in spans:
                raise ValueError(f"Toolformer source line is missing: {line_number}")
            source_spans.append(dict(spans[line_number]))
        atoms.append(
            {
                "atom_id": spec["atom_id"],
                "title": spec["title"],
                "instruction": spec["instruction"],
                "contract_role": spec["contract_role"],
                "source_spans": source_spans,
            }
        )
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    card_text = _render_card(source_sha256)
    card_path = destination / "full_artifact.md"
    card_path.write_text(card_text, encoding="utf-8", newline="\n")
    atom_map = {
        "schema_version": "effectslice-toolformer-filter-source-atom-map.v1",
        "paper_id": "toolformer",
        "task_id": "TOOLFORMER-FILTER",
        "source_path": SOURCE_RELATIVE_PATH.as_posix(),
        "source_sha256": source_sha256,
        "full_artifact_path": "full_artifact.md",
        "full_artifact_sha256": _sha256(card_text.encode("utf-8")),
        "atoms": atoms,
        "requires": REQUIRES,
        "dependency_edges": [
            {"from": atom_id, "to": dependency}
            for atom_id, dependencies in REQUIRES.items()
            for dependency in dependencies
        ],
        "evidence_boundary": (
            "Source-grounded task artifact only; not eligibility or effectiveness evidence."
        ),
    }
    atom_map_path = destination / "source_atom_map.json"
    atom_map_path.write_text(
        json.dumps(atom_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "full_artifact_path": str(card_path),
        "atom_map_path": str(atom_map_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Toolformer filter artifacts")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "artifacts" / "toolformer_filter",
    )
    args = parser.parse_args()
    print(json.dumps(build_artifacts(args.project_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
