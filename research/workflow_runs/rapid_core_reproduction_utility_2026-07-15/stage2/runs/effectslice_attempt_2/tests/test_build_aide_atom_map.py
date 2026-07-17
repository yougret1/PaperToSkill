import hashlib
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))

from build_aide_atom_map import (  # noqa: E402
    CANDIDATE_ATOM_IDS,
    MINIMAL_CANDIDATE_ATOM_IDS,
    SINGLETON_CANDIDATE_ATOM_IDS,
    build_artifacts,
    build_candidate_text,
    dependency_closed,
)


class AideAtomMapTest(unittest.TestCase):
    def test_builds_exact_four_way_atoms_and_closed_candidate(self):
        source = PROJECT_ROOT / "generated_skills" / "aide" / "SKILL.md"
        source_bytes = source.read_bytes()
        atom_map, candidate_text = build_artifacts(source)

        self.assertEqual(len(atom_map["atoms"]), 12)
        self.assertEqual(atom_map["dependency_nodes"], [f"A{index:02d}" for index in range(1, 13)])
        self.assertEqual(atom_map["source_sha256"], hashlib.sha256(source_bytes).hexdigest())
        for atom in atom_map["atoms"]:
            span = atom["source_span"]
            extracted = source_bytes[span["byte_start"] : span["byte_end"]].decode("utf-8")
            self.assertEqual(extracted, atom["source_text"])
            self.assertTrue(atom["workflow_step"])
            self.assertTrue(atom["executable_region"]["symbol"])
            self.assertTrue(atom["contract_role"])

        self.assertTrue(dependency_closed(CANDIDATE_ATOM_IDS, atom_map["requires"]))
        self.assertLess(len(CANDIDATE_ATOM_IDS), len(atom_map["atoms"]))
        self.assertEqual(atom_map["candidate_atom_ids"], list(CANDIDATE_ATOM_IDS))
        self.assertIn("submission.csv", candidate_text)
        self.assertNotIn("51.38", candidate_text)
        self.assertNotIn("24-hour", candidate_text)

        minimal_text = build_candidate_text(atom_map["atoms"], MINIMAL_CANDIDATE_ATOM_IDS)
        self.assertTrue(dependency_closed(MINIMAL_CANDIDATE_ATOM_IDS, atom_map["requires"]))
        self.assertLess(len(minimal_text), len(candidate_text))
        self.assertIn("objective function", minimal_text)
        self.assertIn("atomic measurable change", minimal_text)
        self.assertNotIn("submission.csv", minimal_text)

        singleton_text = build_candidate_text(atom_map["atoms"], SINGLETON_CANDIDATE_ATOM_IDS)
        self.assertTrue(dependency_closed(SINGLETON_CANDIDATE_ATOM_IDS, atom_map["requires"]))
        self.assertLess(len(singleton_text), len(minimal_text))
        self.assertIn("objective function", singleton_text)
        self.assertNotIn("atomic measurable change", singleton_text)
        singleton_record = atom_map["development_candidates"]["slice_v2"]
        self.assertEqual(
            singleton_record["artifact_sha256"],
            hashlib.sha256(singleton_text.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            singleton_record["context_sha256"],
            hashlib.sha256(singleton_text.strip().encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
