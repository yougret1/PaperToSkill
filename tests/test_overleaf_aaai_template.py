import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AAAI_DIR = ROOT / "paper" / "aaai"
MAIN_TEX = AAAI_DIR / "main.tex"


class OverleafAaaiTemplateTest(unittest.TestCase):
    def setUp(self):
        self.main = MAIN_TEX.read_text(encoding="utf-8")

    def test_main_uses_submission_template_once(self):
        self.assertIn(r"\usepackage[submission]{aaai2027}", self.main)
        self.assertEqual(1, len(re.findall(r"\\title\s*\{", self.main)))
        self.assertIn(
            r"\title{PaperToSkill: Turning Research Papers into Portable Agent Skills}",
            self.main,
        )

    def test_main_has_expected_modular_inputs(self):
        expected = [
            "abstract",
            "introduction",
            "related",
            "method",
            "result",
            "conclusion",
        ]
        actual = re.findall(r"\\input\{src/([^}]+)\}", self.main)
        self.assertEqual(expected, actual)
        for name in expected:
            self.assertTrue((AAAI_DIR / "src" / f"{name}.tex").is_file(), name)

    def test_template_contains_only_papertoskill_assets(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in [MAIN_TEX, *(AAAI_DIR / "src").glob("*.tex")]
        )
        self.assertNotIn("Intricate Semantic Typography", combined)
        self.assertNotIn("teaser_small", combined)
        self.assertTrue((AAAI_DIR / "images" / "papertoskill_pipeline.pdf").is_file())
        self.assertTrue(
            (AAAI_DIR / "images" / "external_evidence_design.pdf").is_file()
        )

    def test_bibliography_matches_compatibility_entry(self):
        self.assertIn(r"\bibliography{src/references}", self.main)
        self.assertEqual(
            (AAAI_DIR / "src" / "references.bib").read_bytes(),
            (AAAI_DIR / "papertoskill_refs.bib").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
