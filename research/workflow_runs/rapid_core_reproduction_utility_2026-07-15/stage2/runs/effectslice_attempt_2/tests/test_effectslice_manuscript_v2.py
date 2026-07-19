import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[7]
PAPER_ROOT = PROJECT_ROOT / "paper" / "effectslice_aaai"


class EffectSliceManuscriptV2Test(unittest.TestCase):
    def test_main_entrypoint_keeps_v3_as_the_final_paper_version(self):
        lines = (PAPER_ROOT / "main.tex").read_text(encoding="utf-8").splitlines()

        self.assertEqual(lines[0], r"\input{main_v3}")
        self.assertEqual(lines[1], r"\endinput")

    def test_v2_uses_generated_results_and_excludes_contaminated_claims(self):
        source = (PAPER_ROOT / "main_v2.tex").read_text(encoding="utf-8")

        self.assertIn(r"\input{generated_results}", source)
        self.assertIn("matched B/F/S replicate blocks", source)
        self.assertIn("final-only private scoring", source)
        self.assertIn("deepseek-v4-flash", source)
        self.assertNotRegex(source, re.compile(r"(?:59/59|44/59|15/59)"))
        self.assertNotRegex(source.lower(), re.compile(r"\b(?:sealed|untouched)\b"))
        self.assertNotIn("case-level Clopper", source)

    def test_no_local_model_is_presented_as_the_experimental_anchor(self):
        source = (PAPER_ROOT / "main_v2.tex").read_text(encoding="utf-8").lower()

        self.assertNotIn("qwen", source)
        self.assertNotIn("local quantized model as", source)
        self.assertIn("trusted vendor api", source)
        self.assertRegex(source, re.compile(r"not used for model\s+inference"))


if __name__ == "__main__":
    unittest.main()
