import hashlib
import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))

from build_swe_atom_map import (  # noqa: E402
    CANDIDATE_ATOM_IDS,
    build_artifacts,
    build_candidate_text,
    dependency_closed,
)


class SWEAtomMapTest(unittest.TestCase):
    def setUp(self):
        self.source = PROJECT_ROOT / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md"
        self.source_map = self.source.parent / "references" / "source_map.json"

    def test_builds_exact_source_bound_atoms_and_closed_candidate(self):
        source_bytes = self.source.read_bytes()
        source_map_bytes = self.source_map.read_bytes()

        atom_map, artifacts = build_artifacts(self.source, self.source_map)

        self.assertEqual(len(atom_map["atoms"]), 9)
        self.assertEqual(atom_map["dependency_nodes"], [f"A{index:02d}" for index in range(1, 10)])
        self.assertEqual(atom_map["source_sha256"], hashlib.sha256(source_bytes).hexdigest())
        self.assertEqual(atom_map["source_map_sha256"], hashlib.sha256(source_map_bytes).hexdigest())
        spans = []
        for atom in atom_map["atoms"]:
            span = atom["source_span"]
            extracted = source_bytes[span["byte_start"] : span["byte_end"]].decode("utf-8")
            self.assertEqual(extracted, atom["source_text"])
            self.assertEqual(span["file_digest"], atom_map["source_sha256"])
            self.assertTrue(atom["executable_region"]["symbol"])
            self.assertTrue(atom["contract_role"])
            spans.append((span["byte_start"], span["byte_end"]))
        self.assertEqual(spans, sorted(spans))
        for left, right in zip(spans, spans[1:]):
            self.assertLessEqual(left[1], right[0])

        self.assertTrue(dependency_closed(CANDIDATE_ATOM_IDS, atom_map["requires"]))
        self.assertLess(len(CANDIDATE_ATOM_IDS), len(atom_map["atoms"]))
        candidate = artifacts["slice_v0.md"]
        self.assertIn("Localize code", candidate)
        self.assertIn("Inspect code", candidate)
        self.assertIn("focused multiline edits", candidate)
        self.assertIn("editing guardrails", candidate)
        self.assertIn("% Resolved", candidate)
        self.assertNotIn("Context management", candidate)

    def test_generates_complete_closed_deletion_neighbors_with_digests(self):
        atom_map, artifacts = build_artifacts(self.source, self.source_map)
        neighbors = atom_map["development_candidates"]["slice_v0"]["deletion_neighbors"]

        self.assertEqual(set(neighbors), {f"minus_{atom_id}" for atom_id in CANDIDATE_ATOM_IDS})
        for neighbor_id, record in neighbors.items():
            removed_atom = neighbor_id.removeprefix("minus_")
            retained = tuple(record["atom_ids"])
            self.assertNotIn(removed_atom, retained)
            self.assertTrue(retained)
            self.assertTrue(dependency_closed(retained, atom_map["requires"]))
            text = artifacts[record["artifact_path"]]
            self.assertEqual(record["artifact_sha256"], hashlib.sha256(text.encode("utf-8")).hexdigest())
            self.assertEqual(record["context_sha256"], hashlib.sha256(text.strip().encode("utf-8")).hexdigest())

    def test_artifact_generation_is_deterministic_and_rejects_unknown_atoms(self):
        first_map, first_artifacts = build_artifacts(self.source, self.source_map)
        second_map, second_artifacts = build_artifacts(self.source, self.source_map)

        self.assertEqual(first_map, second_map)
        self.assertEqual(first_artifacts, second_artifacts)
        self.assertEqual(
            json.dumps(first_map, sort_keys=True),
            json.dumps(second_map, sort_keys=True),
        )
        with self.assertRaises(ValueError):
            build_candidate_text(first_map["atoms"], ("A99",), title="bad")


if __name__ == "__main__":
    unittest.main()
