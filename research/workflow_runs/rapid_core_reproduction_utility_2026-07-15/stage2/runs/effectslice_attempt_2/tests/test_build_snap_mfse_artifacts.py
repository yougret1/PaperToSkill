import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))

from build_snap_mfse_artifacts import build_artifacts  # noqa: E402


class SnapMFSEArtifactBuilderTest(unittest.TestCase):
    def test_builds_five_source_exact_atoms_and_stable_card(self):
        source_path = PROJECT_ROOT / "papers" / "extracted" / "snapatac2.txt"
        source_bytes = source_path.read_bytes()

        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            first = build_artifacts(PROJECT_ROOT, Path(first_tmp))
            second = build_artifacts(PROJECT_ROOT, Path(second_tmp))

            first_card = Path(first["full_artifact_path"]).read_bytes()
            second_card = Path(second["full_artifact_path"]).read_bytes()
            first_map_bytes = Path(first["atom_map_path"]).read_bytes()
            second_map_bytes = Path(second["atom_map_path"]).read_bytes()
            atom_map = json.loads(first_map_bytes.decode("utf-8"))

        self.assertEqual(first_card, second_card)
        self.assertEqual(first_map_bytes, second_map_bytes)
        self.assertEqual(
            atom_map["source_sha256"], hashlib.sha256(source_bytes).hexdigest()
        )
        self.assertEqual(
            [atom["atom_id"] for atom in atom_map["atoms"]],
            ["A01", "A02", "A03", "A04", "A05"],
        )
        self.assertEqual(
            atom_map["requires"],
            {
                "A01": [],
                "A02": ["A01"],
                "A03": ["A02"],
                "A04": ["A03"],
                "A05": ["A04"],
            },
        )
        for atom in atom_map["atoms"]:
            for span in atom["source_spans"]:
                extracted = source_bytes[span["byte_start"] : span["byte_end"]]
                self.assertEqual(extracted.decode("utf-8"), span["source_text"])
                self.assertGreaterEqual(span["line_start"], 1)
                self.assertGreaterEqual(span["line_end"], span["line_start"])

        card = first_card.decode("utf-8")
        self.assertIn("log(n / (1 + df))", card)
        self.assertIn("X_tilde @ (X_tilde.T @ v) - D_inv * v", card)
        self.assertIn("Do not materialize", card)
        self.assertNotIn("def eigen", card)
        self.assertNotIn("scipy.sparse.linalg", card)
        self.assertEqual(
            atom_map["full_artifact_sha256"], hashlib.sha256(first_card).hexdigest()
        )


if __name__ == "__main__":
    unittest.main()
