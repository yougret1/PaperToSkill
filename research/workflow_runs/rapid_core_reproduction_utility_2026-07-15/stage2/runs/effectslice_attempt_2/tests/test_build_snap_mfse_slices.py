import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_snap_mfse_slices import build_slice_candidates  # noqa: E402


class BuildSnapMFSESlicesTest(unittest.TestCase):
    def setUp(self):
        self.atom_map_path = RUN_ROOT / "artifacts" / "snap_mfse" / "source_atom_map.json"

    def test_builds_all_strict_dependency_closed_prefixes_in_frozen_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_slice_candidates(self.atom_map_path, Path(tmp))
            registry = json.loads(Path(result["registry_path"]).read_text(encoding="utf-8"))
            rendered = {
                row["candidate_id"]: (Path(tmp) / row["artifact_path"]).read_text(
                    encoding="utf-8"
                )
                for row in registry["candidates"]
            }

        self.assertEqual(registry["query_budget_Q"], 24)
        self.assertEqual(
            [row["candidate_id"] for row in registry["candidates"]],
            ["prefix_01", "prefix_02", "prefix_03", "prefix_04"],
        )
        self.assertEqual(
            [row["retained_atom_ids"] for row in registry["candidates"]],
            [
                ["A01"],
                ["A01", "A02"],
                ["A01", "A02", "A03"],
                ["A01", "A02", "A03", "A04"],
            ],
        )
        self.assertTrue(all(row["dependency_closed"] for row in registry["candidates"]))
        self.assertTrue(all(row["strict_subset"] for row in registry["candidates"]))
        self.assertNotIn("A02", rendered["prefix_01"])
        self.assertIn("A04", rendered["prefix_04"])
        self.assertNotIn("A05", rendered["prefix_04"])

    def test_registers_each_single_deletion_closure_without_model_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build_slice_candidates(self.atom_map_path, Path(tmp))
            registry = json.loads(Path(result["registry_path"]).read_text(encoding="utf-8"))

        prefix_04 = registry["candidates"][-1]
        self.assertEqual(
            prefix_04["deletion_neighbors"],
            [
                {"removed_atom_id": "A01", "retained_atom_ids": [], "condition": "B"},
                {
                    "removed_atom_id": "A02",
                    "retained_atom_ids": ["A01"],
                    "candidate_id": "prefix_01",
                },
                {
                    "removed_atom_id": "A03",
                    "retained_atom_ids": ["A01", "A02"],
                    "candidate_id": "prefix_02",
                },
                {
                    "removed_atom_id": "A04",
                    "retained_atom_ids": ["A01", "A02", "A03"],
                    "candidate_id": "prefix_03",
                },
            ],
        )
        serialized = json.dumps(registry).lower()
        self.assertNotIn("task_score", serialized)
        self.assertNotIn("case_scores", serialized)
        self.assertNotIn("selected_candidate", serialized)

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_result = build_slice_candidates(self.atom_map_path, Path(first))
            second_result = build_slice_candidates(self.atom_map_path, Path(second))
            first_registry = Path(first_result["registry_path"]).read_bytes()
            second_registry = Path(second_result["registry_path"]).read_bytes()

        self.assertEqual(first_registry, second_registry)


if __name__ == "__main__":
    unittest.main()
