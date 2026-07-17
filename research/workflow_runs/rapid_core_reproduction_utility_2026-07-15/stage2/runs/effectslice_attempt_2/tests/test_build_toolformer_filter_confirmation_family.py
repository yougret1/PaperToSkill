import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_toolformer_filter_confirmation_family import (  # noqa: E402
    build_confirmation_family,
)
from build_toolformer_filter_slices import build_slice_candidates  # noqa: E402


class BuildToolformerFilterConfirmationFamilyTest(unittest.TestCase):
    def setUp(self):
        self.atom_map = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        )
        self.case_registry = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry.json"
        )
        self.config = RUN_ROOT / "configs" / "experiment_config.json"

    @staticmethod
    def write_discovery(path: Path, *, deletion_complete: bool = True) -> None:
        path.write_text(
            json.dumps(
                {
                    "task_disposition": "candidate_locked_for_confirmation",
                    "deletion_audit_complete": deletion_complete,
                    "selected_candidate_id": "prefix_03",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def build_in(self, root: Path) -> Path:
        slices = root / "slices"
        build_slice_candidates(self.atom_map, slices)
        discovery = root / "discovery.json"
        self.write_discovery(discovery)
        output = root / "confirmation_family.json"
        build_confirmation_family(
            discovery_summary_path=discovery,
            slice_registry_path=slices / "slice_registry.json",
            case_registry_path=self.case_registry,
            config_path=self.config,
            output_path=output,
        )
        return output

    def test_freezes_selected_candidate_conditions_and_statistical_family(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            family = json.loads(self.build_in(Path(tmp)).read_text(encoding="utf-8"))

        self.assertEqual(family["task_id"], "TOOLFORMER-FILTER")
        self.assertEqual(family["selected_candidate_id"], "prefix_03")
        self.assertEqual(family["retained_atom_ids"], ["T01", "T02", "T03"])
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
        self.assertEqual(
            family["hypotheses"][-1]["metric"], "S_contract_passed"
        )
        self.assertFalse(family["confirmation_unsealed"])
        self.assertFalse(family["general_effectslice_claim_ready"])

    def test_rejects_incomplete_deletion_audit(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            root = Path(tmp)
            slices = root / "slices"
            build_slice_candidates(self.atom_map, slices)
            discovery = root / "discovery.json"
            self.write_discovery(discovery, deletion_complete=False)
            with self.assertRaises(ValueError):
                build_confirmation_family(
                    discovery_summary_path=discovery,
                    slice_registry_path=slices / "slice_registry.json",
                    case_registry_path=self.case_registry,
                    config_path=self.config,
                    output_path=root / "family.json",
                )

    def test_family_rebuild_is_byte_identical_and_contains_no_outcomes(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            root = Path(tmp)
            slices = root / "slices"
            build_slice_candidates(self.atom_map, slices)
            discovery = root / "discovery.json"
            self.write_discovery(discovery)
            kwargs = {
                "discovery_summary_path": discovery,
                "slice_registry_path": slices / "slice_registry.json",
                "case_registry_path": self.case_registry,
                "config_path": self.config,
            }
            first_output = root / "family_first.json"
            second_output = root / "family_second.json"
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
