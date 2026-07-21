from __future__ import annotations

import sys
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

from verify_forward_citations import AAAI_KEYS, audit  # noqa: E402


def test_forward_citation_gate_passes() -> None:
    result = audit()
    assert result["status"] == "passed"
    assert result["bibliography_entries"] == 33
    assert result["main_text_unique_citations"] >= 25


def test_more_than_three_verified_aaai_papers_are_cited() -> None:
    result = audit()
    assert len(AAAI_KEYS) == 7
    assert result["aaai_citations"] == 7
