from __future__ import annotations

import json
import re
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parent
AAAI_KEYS = {
    "gao2024confucius",
    "hao2025citi",
    "ma2025reusabletoolsets",
    "liskavets2025contextcompression",
    "guo2026mcpagentbench",
    "jia2026autotool",
    "wang2026beyondaccuracy",
}

FORWARD_RETRIEVALS = (
    "stage1/retrieval/effectslice-selectivenet.json",
    "stage1/retrieval/effectslice-conformal-risk-control.json",
    "stage1/retrieval/effectslice-agentboard.json",
    "stage1/retrieval/effectslice-paperbench-dblp.json",
)


def _repo_root() -> Path:
    for candidate in (FORWARD_ROOT, *FORWARD_ROOT.parents):
        if (candidate / "paper" / "effectslice_aaai" / "main_v3.tex").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def _bib_keys(text: str) -> list[str]:
    return re.findall(r"^@\w+\{([^,]+),", text, flags=re.MULTILINE)


def _cited_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\\cite\w*\{([^}]+)\}", text):
        keys.update(part.strip() for part in group.split(",") if part.strip())
    return keys


def audit() -> dict[str, object]:
    repo = _repo_root()
    paper_dir = repo / "paper" / "effectslice_aaai"
    run_root = (
        repo
        / "research"
        / "workflow_runs"
        / "rapid_core_reproduction_utility_2026-07-15"
        / "stage2"
        / "runs"
        / "effectslice_attempt_2"
    )
    paper_bib = (paper_dir / "effectslice_refs.bib").read_text(encoding="utf-8")
    cached_bib = (run_root / "cached_citations.bib").read_text(encoding="utf-8")
    manuscript = (paper_dir / "main_v3.tex").read_text(encoding="utf-8")
    matrix = json.loads(
        (FORWARD_ROOT / "citation_search" / "citation_matrix.json").read_text(
            encoding="utf-8"
        )
    )
    metadata = json.loads(
        (FORWARD_ROOT / "citation_search" / "official_metadata.json").read_text(
            encoding="utf-8"
        )
    )

    paper_keys = _bib_keys(paper_bib)
    cached_keys = _bib_keys(cached_bib)
    cited_keys = _cited_keys(manuscript)
    matrix_keys = [entry["key"] for entry in matrix["entries"]]
    official_keys = {entry["key"] for entry in metadata["records"]}

    assert paper_bib == cached_bib, "paper and cached bibliographies diverge"
    assert len(paper_keys) == 33 == len(set(paper_keys)), "expected 33 unique entries"
    assert paper_keys == cached_keys, "bibliography key order differs"
    assert set(matrix_keys) == set(paper_keys), "citation matrix is incomplete"
    assert len(cited_keys) >= 25, "fewer than 25 unique works are cited in main text"
    assert cited_keys <= set(paper_keys), "manuscript contains unknown citation keys"
    assert AAAI_KEYS <= cited_keys, "not every selected AAAI paper is cited"
    assert AAAI_KEYS <= official_keys, "AAAI official metadata is incomplete"
    assert {
        "geifman2019selectivenet",
        "angelopoulos2022conformalriskcontrol",
        "ma2024agentboard",
    } <= cited_keys, "risk-control and fine-grained evaluation citations are missing"
    for relative_path in FORWARD_RETRIEVALS:
        assert (FORWARD_ROOT / relative_path).is_file(), f"missing retrieval: {relative_path}"
    assert all(
        entry.get("doi", "").startswith("10.1609/aaai.")
        for entry in metadata["records"]
        if entry["key"] in AAAI_KEYS
    ), "AAAI DOI verification failed"
    assert "Advances in Neural Information Processing Systems 36" in paper_bib
    assert "10.18653/v1/2023.emnlp-main.825" in paper_bib
    assert "Proceedings of the 42nd International Conference on Machine Learning" in paper_bib

    return {
        "status": "passed",
        "bibliography_entries": len(paper_keys),
        "main_text_unique_citations": len(cited_keys),
        "aaai_citations": len(AAAI_KEYS & cited_keys),
        "official_metadata_records": len(metadata["records"]),
        "uncited_bibliography_entries": sorted(set(paper_keys) - cited_keys),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
