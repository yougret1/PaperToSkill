from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
SOURCE_RELATIVE_PATH = Path("papers/extracted/snapatac2.txt")

ATOM_SPECS = (
    {
        "atom_id": "A01",
        "title": "Scale features with the paper IDF",
        "instruction": (
            "For n cells and feature document frequency df, multiply each feature "
            "by log(n / (1 + df)) before row normalization."
        ),
        "line_numbers": (74,),
        "contract_role": "feature_scaling",
    },
    {
        "atom_id": "A02",
        "title": "Normalize rows for cosine similarity",
        "instruction": (
            "After IDF scaling, normalize every nonzero cell row to unit L2 norm; "
            "the resulting matrix X represents cosine similarities through X X^T."
        ),
        "line_numbers": (76,),
        "contract_role": "row_normalization",
    },
    {
        "atom_id": "A03",
        "title": "Remove self-similarity and compute degrees matrix-free",
        "instruction": (
            "Use W = X X^T - I and compute its degree vector as "
            "X @ (X.T @ 1) - 1 without constructing W."
        ),
        "line_numbers": (77,),
        "contract_role": "degree_normalization",
    },
    {
        "atom_id": "A04",
        "title": "Expose the normalized similarity as a linear operator",
        "instruction": (
            "Let X_tilde = D^(-1/2) X and D_inv be the reciprocal degree vector. "
            "For every trial vector v, evaluate "
            "X_tilde @ (X_tilde.T @ v) - D_inv * v."
        ),
        "line_numbers": (79,),
        "contract_role": "matrix_free_operator",
    },
    {
        "atom_id": "A05",
        "title": "Return the leading spectral coordinates under the paper scope",
        "instruction": (
            "Use a Lanczos-style symmetric eigensolver, order the top eigenpairs "
            "from largest to smallest, and keep this exact matrix-free route scoped "
            "to cosine similarity. Do not materialize an n-cell by n-cell matrix."
        ),
        "line_numbers": (73, 75),
        "contract_role": "solver_and_guardrail",
    },
)

REQUIRES = {
    "A01": [],
    "A02": ["A01"],
    "A03": ["A02"],
    "A04": ["A03"],
    "A05": ["A04"],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _line_spans(source_bytes: bytes) -> dict[int, dict[str, Any]]:
    spans: dict[int, dict[str, Any]] = {}
    offset = 0
    for line_number, raw_line in enumerate(source_bytes.splitlines(keepends=True), start=1):
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
        "# SnapATAC2 Matrix-Free Spectral Embedding Execution Card",
        "",
        "Evidence boundary: task-local procedural artifact derived from paper lines 73-79. ",
        "It is not reference code and does not expose scorer cases.",
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
            "## Hard Checks",
            "",
            "- Reject nonfinite or negative count values and rows that cannot be L2-normalized.",
            "- Require positive degrees before applying D^(-1/2).",
            "- Return finite eigenvalues in descending order and one eigenvector column per component.",
            "- Do not materialize the cell-by-cell similarity or normalized similarity matrix.",
            "- Treat the method as cosine-specific; do not claim arbitrary similarity support.",
            "",
            "## Validation",
            "",
            "Validate eigenpair residuals and compare the returned eigenspace with an independent implementation of the paper equations. Eigenvector signs are not identifiable, so compare subspaces rather than raw signs.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifacts(project_root: Path, output_dir: Path) -> dict[str, str]:
    root = Path(project_root).resolve()
    source_path = root / SOURCE_RELATIVE_PATH
    source_bytes = source_path.read_bytes()
    source_sha256 = sha256_bytes(source_bytes)
    spans = _line_spans(source_bytes)
    atoms = []
    for spec in ATOM_SPECS:
        atom_spans = []
        for line_number in spec["line_numbers"]:
            if line_number not in spans:
                raise ValueError(f"SnapATAC2 source line is missing: {line_number}")
            atom_spans.append(dict(spans[line_number]))
        atoms.append(
            {
                "atom_id": spec["atom_id"],
                "title": spec["title"],
                "instruction": spec["instruction"],
                "contract_role": spec["contract_role"],
                "source_spans": atom_spans,
            }
        )

    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    card_path = destination / "full_artifact.md"
    card_text = _render_card(source_sha256)
    card_path.write_text(card_text, encoding="utf-8", newline="\n")
    atom_map = {
        "schema_version": "effectslice-snap-mfse-source-atom-map.v1",
        "paper_id": "snapatac2",
        "task_id": "SNAP-MFSE",
        "source_path": SOURCE_RELATIVE_PATH.as_posix(),
        "source_sha256": source_sha256,
        "full_artifact_path": "full_artifact.md",
        "full_artifact_sha256": sha256_bytes(card_text.encode("utf-8")),
        "atoms": atoms,
        "requires": REQUIRES,
        "dependency_edges": [
            {"from": atom_id, "to": dependency}
            for atom_id, dependencies in REQUIRES.items()
            for dependency in dependencies
        ],
        "evidence_boundary": (
            "Source-grounded development artifact only; not an eligibility or effectiveness result."
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
    parser = argparse.ArgumentParser(description="Build SNAP-MFSE source-grounded artifacts")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUN_ROOT / "artifacts" / "snap_mfse",
    )
    args = parser.parse_args()
    print(json.dumps(build_artifacts(args.project_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
