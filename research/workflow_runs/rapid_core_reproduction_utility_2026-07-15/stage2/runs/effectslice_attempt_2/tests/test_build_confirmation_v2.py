import hashlib
import itertools
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from build_confirmation_v2 import build_family  # noqa: E402


class BuildConfirmationV2Test(unittest.TestCase):
    def test_builds_digest_bound_balanced_run_level_family_for_each_task(self):
        required_bindings = {
            "selected_artifact",
            "discovery_summary",
            "slice_registry",
            "case_registry",
            "source_map",
            "task_prompt",
            "scorer",
            "runner",
            "scheduler",
            "aci_runner",
            "aci_protocol",
            "evidence_binding",
            "transport",
            "case_generator",
            "family_builder",
            "full_artifact",
        }
        expected_orders = set(itertools.permutations(("B", "F", "S")))

        for task_key in ("snap_mfse", "toolformer_filter"):
            with self.subTest(task=task_key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                case_path = root / f"{task_key}_cases.json"
                family_path = root / f"{task_key}_family.json"

                family = build_family(
                    task_key=task_key,
                    case_registry_output=case_path,
                    family_output=family_path,
                )

                self.assertEqual(
                    family["schema_version"],
                    "effectslice-confirmation-v2-family.v1",
                )
                self.assertEqual(family["case_block"], "confirmation_v2")
                self.assertEqual(family["case_count"], 64)
                self.assertEqual(family["replicate_count"], 18)
                self.assertEqual(family["statistical_unit"], "independent_agent_run")
                self.assertEqual(family["case_role"], "clustered_within_run_checks")
                self.assertEqual(family["private_score_policy"], "final_only")
                self.assertEqual(family["prior_confirmation_status"], "contaminated_development")
                schedule = family["replicate_schedule"]
                self.assertEqual(len(schedule), 18)
                order_counts = Counter(tuple(row["condition_order"]) for row in schedule)
                self.assertEqual(set(order_counts), expected_orders)
                self.assertEqual(set(order_counts.values()), {3})
                self.assertEqual(len({row["replicate_id"] for row in schedule}), 18)

                present_bindings = {
                    key.removesuffix("_path")
                    for key in family
                    if key.endswith("_path")
                    and f"{key.removesuffix('_path')}_sha256" in family
                }
                self.assertTrue(required_bindings.issubset(present_bindings))
                for prefix in required_bindings:
                    path = Path(family[f"{prefix}_path"])
                    if not path.is_absolute():
                        path = RUN_ROOT / path
                    self.assertTrue(path.is_file(), prefix)
                    self.assertEqual(
                        family[f"{prefix}_sha256"],
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                self.assertEqual(
                    json.loads(family_path.read_text(encoding="utf-8")),
                    family,
                )

                with self.assertRaisesRegex(ValueError, "already exists"):
                    build_family(
                        task_key=task_key,
                        case_registry_output=case_path,
                        family_output=family_path,
                    )


if __name__ == "__main__":
    unittest.main()
