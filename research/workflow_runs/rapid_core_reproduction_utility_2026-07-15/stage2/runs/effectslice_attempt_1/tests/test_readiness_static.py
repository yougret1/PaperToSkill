import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = RUN_ROOT / "tests" / "fixtures" / "readiness"
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.readiness import audit_project  # noqa: E402


class StaticReadinessAuditTest(unittest.TestCase):
    def test_empty_task_spec_is_an_invalid_format(self):
        root = FIXTURE_ROOT / "aggregate"

        with self.assertRaisesRegex(ValueError, "at least one task"):
            audit_project(root, root / "config_empty.json")

    def test_aggregate_summary_and_skill_rows_are_not_certificate_ready(self):
        root = FIXTURE_ROOT / "aggregate"
        report = audit_project(root, root / "config.json")

        self.assertEqual(report["task_count"], 1)
        self.assertEqual(report["ready_task_count"], 0)
        missing = set(report["tasks"][0]["missing_requirements"])
        self.assertIn("missing_same_scaffold_no_skill_baseline", missing)
        self.assertIn("insufficient_eligibility_pairs", missing)
        self.assertIn("missing_case_level_pairs", missing)
        self.assertIn("missing_cost_conversion", missing)
        self.assertIn("missing_four_way_atoms", missing)
        self.assertIn("missing_dependency_graph", missing)
        self.assertIn("missing_contract_guardrail_predicates", missing)

    def test_shallow_truthy_fields_are_not_certificate_ready(self):
        root = FIXTURE_ROOT / "shallow"
        report = audit_project(root, root / "config.json")

        self.assertEqual(report["ready_task_count"], 0)
        missing = set(report["tasks"][0]["missing_requirements"])
        self.assertIn("missing_case_level_pairs", missing)
        self.assertIn("missing_score_bounds", missing)
        self.assertIn("missing_cost_conversion", missing)
        self.assertIn("missing_contract_guardrail_predicates", missing)
        self.assertIn("missing_four_way_atoms", missing)
        self.assertIn("missing_dependency_graph", missing)
        self.assertIn("missing_complete_neighbor_budget", missing)

    def test_strict_task_adapter_and_paired_rows_are_certificate_ready(self):
        root = FIXTURE_ROOT / "valid"
        report = audit_project(root, root / "config.json")

        self.assertEqual(report["task_count"], 1)
        self.assertEqual(report["ready_task_count"], 1)
        self.assertEqual(report["tasks"][0]["paired_case_count"], 3)
        self.assertEqual(report["tasks"][0]["missing_requirements"], [])


if __name__ == "__main__":
    unittest.main()
