import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))

from build_toolformer_filter_artifacts import build_artifacts  # noqa: E402


class BuildToolformerFilterArtifactsTest(unittest.TestCase):
    def test_builds_exact_source_grounded_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_artifacts(PROJECT_ROOT, Path(tmp))
            atom_map = json.loads(Path(result["atom_map_path"]).read_text(encoding="utf-8"))
            card = Path(result["full_artifact_path"]).read_text(encoding="utf-8")

        self.assertEqual(
            [atom["atom_id"] for atom in atom_map["atoms"]],
            ["T01", "T02", "T03", "T04", "T05"],
        )
        self.assertEqual(
            atom_map["requires"],
            {
                "T01": [],
                "T02": ["T01"],
                "T03": ["T02"],
                "T04": ["T03"],
                "T05": ["T04"],
            },
        )
        self.assertEqual(
            [[span["line_start"] for span in atom["source_spans"]] for atom in atom_map["atoms"]],
            [
                [268, 269, 270, 271, 272],
                list(range(134, 146)),
                list(range(146, 159)),
                list(range(159, 172)),
                [76, 77, 78, 79],
            ],
        )
        self.assertIn("max(0, 1 - 0.2 * t)", card)
        self.assertIn("first future token uses t = 0", card)
        self.assertIn("min(L_empty, L_call_only)", card)
        self.assertIn("margin >= tau_filter", card)
        self.assertNotIn("def filter_useful_api_calls", card)
        self.assertNotIn("np.", card)

    def test_source_spans_match_exact_utf8_bytes(self):
        source = (PROJECT_ROOT / "papers" / "extracted" / "toolformer.txt").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            result = build_artifacts(PROJECT_ROOT, Path(tmp))
            atom_map = json.loads(Path(result["atom_map_path"]).read_text(encoding="utf-8"))

        for atom in atom_map["atoms"]:
            for span in atom["source_spans"]:
                extracted = source[span["byte_start"] : span["byte_end"]].decode("utf-8")
                self.assertEqual(extracted, span["source_text"])

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_result = build_artifacts(PROJECT_ROOT, Path(first))
            second_result = build_artifacts(PROJECT_ROOT, Path(second))
            first_card = Path(first_result["full_artifact_path"]).read_bytes()
            second_card = Path(second_result["full_artifact_path"]).read_bytes()
            first_map = Path(first_result["atom_map_path"]).read_bytes()
            second_map = Path(second_result["atom_map_path"]).read_bytes()

        self.assertEqual(first_card, second_card)
        self.assertEqual(first_map, second_map)


if __name__ == "__main__":
    unittest.main()
