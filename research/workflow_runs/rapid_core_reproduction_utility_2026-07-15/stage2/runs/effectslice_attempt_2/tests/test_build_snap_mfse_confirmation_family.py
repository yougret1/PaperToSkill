import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_snap_mfse_confirmation_family import build_confirmation_family  # noqa: E402


class BuildSnapMFSEConfirmationFamilyTest(unittest.TestCase):
    def setUp(self):
        self.discovery_summary = RUN_ROOT / "derived" / "snap_mfse_discovery_summary.json"
        self.slice_registry = (
            RUN_ROOT / "artifacts" / "snap_mfse" / "slices" / "slice_registry.json"
        )
        self.case_registry = RUN_ROOT / "artifacts" / "snap_mfse" / "case_registry.json"
        self.config = RUN_ROOT / "configs" / "experiment_config.json"

    def test_freezes_selected_candidate_conditions_and_statistical_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "confirmation_family.json"
            build_confirmation_family(
                discovery_summary_path=self.discovery_summary,
                slice_registry_path=self.slice_registry,
                case_registry_path=self.case_registry,
                config_path=self.config,
                output_path=output,
            )
            family = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(family["selected_candidate_id"], "prefix_03")
        self.assertEqual(family["retained_atom_ids"], ["A01", "A02", "A03"])
        self.assertEqual(family["conditions"], ["B", "F", "S"])
        self.assertEqual(family["case_block"], "confirmation")
        self.assertEqual(family["case_count"], 59)
        self.assertEqual(family["alpha"], 0.02)
        self.assertEqual(family["epsilon"], 0.025)
        self.assertEqual(family["maximum_violation_rate"], 0.1)
        self.assertEqual(
            [row["hypothesis_id"] for row in family["hypotheses"]],
            ["H_preserve_F", "H_benefit_over_B", "H_hard_constraints"],
        )
        self.assertFalse(family["confirmation_unsealed"])
        self.assertFalse(family["general_effectslice_claim_ready"])

    def test_family_contains_digests_but_no_confirmation_outcomes(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_output = Path(first) / "family.json"
            second_output = Path(second) / "family.json"
            kwargs = {
                "discovery_summary_path": self.discovery_summary,
                "slice_registry_path": self.slice_registry,
                "case_registry_path": self.case_registry,
                "config_path": self.config,
            }
            build_confirmation_family(output_path=first_output, **kwargs)
            build_confirmation_family(output_path=second_output, **kwargs)
            first_bytes = first_output.read_bytes()
            second_bytes = second_output.read_bytes()
            family = json.loads(first_bytes.decode("utf-8"))

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(len(family["discovery_summary_sha256"]), 64)
        self.assertEqual(len(family["slice_registry_sha256"]), 64)
        self.assertEqual(len(family["case_registry_sha256"]), 64)
        serialized = json.dumps(family).lower()
        self.assertNotIn("case_scores", serialized)
        self.assertNotIn("confirmation_task_score", serialized)


if __name__ == "__main__":
    unittest.main()
