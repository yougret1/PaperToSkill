import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_effectslice_citations import build_citations  # noqa: E402


class BuildEffectSliceCitationsTest(unittest.TestCase):
    def test_builds_19_verified_unique_entries_with_purposes(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            result = build_citations(RUN_ROOT, Path(tmp))
            bib_text = Path(result["bibtex"]).read_text(encoding="utf-8")
            progress = json.loads(
                Path(result["progress"]).read_text(encoding="utf-8")
            )

        self.assertEqual(progress["status"], "complete")
        self.assertEqual(progress["completed_rounds"], 3)
        self.assertEqual(progress["entry_count"], 19)
        self.assertEqual(bib_text.count("\n@"), 19)

        citations = progress["citations"]
        keys = [citation["key"] for citation in citations]
        titles = [citation["title"].casefold() for citation in citations]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(titles), len(set(titles)))
        for citation in citations:
            self.assertTrue(citation["year"])
            self.assertTrue(citation["purpose"])
            self.assertTrue(citation["source"])
            self.assertTrue(citation["identifier"])
            self.assertIn("@", bib_text)
            self.assertIn("{" + citation["key"] + ",", bib_text)

    def test_requires_all_three_retrieval_snapshots_and_exact_arxiv_metadata(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            result = build_citations(RUN_ROOT, Path(tmp))
            progress = json.loads(
                Path(result["progress"]).read_text(encoding="utf-8")
            )

        for relative in progress["retrieval_artifacts"]:
            self.assertTrue((RUN_ROOT / relative).is_file(), relative)
        self.assertIn(
            "citation_search/arxiv_exact.xml", progress["retrieval_artifacts"]
        )


if __name__ == "__main__":
    unittest.main()
