import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_aide_development import load_pairs, summarize_pairs  # noqa: E402


class AideDevelopmentSummaryTest(unittest.TestCase):
    def test_load_pairs_includes_triage_directories_without_pair_in_name(self):
        fixture_root = RUN_ROOT / "tests" / "fixtures" / "aide_development"

        pairs, atom_counts = load_pairs(fixture_root)

        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["pair_id"], "triage")
        self.assertEqual(pairs[0]["candidate_id"], "slice_v2")
        self.assertEqual(atom_counts, {"slice_v2": 1})

    def test_selects_smallest_candidate_with_development_relations(self):
        pairs = [
            {
                "pair_id": "bf",
                "comparison_role": "eligibility",
                "candidate_id": None,
                "scores": {"B": 0.80, "F": 0.82},
                "input_tokens": {"B": 4600, "F": 5900},
            },
            {
                "pair_id": "fs-v1",
                "comparison_role": "preservation",
                "candidate_id": "slice_v1",
                "scores": {"F": 0.83, "S": 0.81},
                "input_tokens": {"F": 5900, "S": 4750},
            },
            {
                "pair_id": "fs-v2",
                "comparison_role": "preservation",
                "candidate_id": "slice_v2",
                "scores": {"F": 0.813, "S": 0.814},
                "input_tokens": {"F": 5900, "S": 4700},
            },
            {
                "pair_id": "bs-v2",
                "comparison_role": "singleton_deletion_neighbor",
                "candidate_id": "slice_v2",
                "scores": {"B": 0.783, "S": 0.809},
                "input_tokens": {"B": 4676, "S": 4707},
            },
        ]

        summary = summarize_pairs(
            pairs,
            candidate_atom_counts={"slice_v1": 2, "slice_v2": 1},
            delta_min=0.01,
            epsilon=0.025,
            delta_delete=0.01,
        )

        self.assertEqual(summary["selected_development_candidate"], "slice_v2")
        self.assertAlmostEqual(summary["eligibility"][0]["effect"], 0.02)
        self.assertTrue(summary["preservation"]["slice_v2"][0]["within_margin"])
        self.assertTrue(summary["deletion_neighbor"]["slice_v2"][0]["witnessed"])
        self.assertFalse(summary["scientific_claim_ready"])

    def test_triage_bundle_contributes_all_three_development_relations(self):
        summary = summarize_pairs(
            [
                {
                    "pair_id": "triage",
                    "comparison_role": "development_triage",
                    "candidate_id": "slice_v2",
                    "scores": {"B": 0.79, "F": 0.82, "S": 0.81},
                    "input_tokens": {"B": 4600, "F": 5900, "S": 4700},
                }
            ],
            candidate_atom_counts={"slice_v2": 1},
            delta_min=0.01,
            epsilon=0.025,
            delta_delete=0.01,
        )

        self.assertEqual(len(summary["eligibility"]), 1)
        self.assertEqual(len(summary["preservation"]["slice_v2"]), 1)
        self.assertEqual(len(summary["deletion_neighbor"]["slice_v2"]), 1)


if __name__ == "__main__":
    unittest.main()
