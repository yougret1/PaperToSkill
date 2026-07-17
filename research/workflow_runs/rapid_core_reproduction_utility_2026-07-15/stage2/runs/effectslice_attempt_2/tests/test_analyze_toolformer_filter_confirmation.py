import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_toolformer_filter_confirmation import (  # noqa: E402
    analyze_confirmation_bundle,
    one_sided_cp_upper,
)


def condition(case_scores, *, contract=True):
    return {
        "status": "scored",
        "terminal_reason": "submitted",
        "last_action": "submit",
        "last_observation_status": "scored",
        "final_metric": {
            "task_score": sum(case_scores) / len(case_scores),
            "case_scores": list(case_scores),
            "contract_passed": contract,
        },
    }


def bundle(base_scores, full_scores, slice_scores, *, contract=True):
    return {
        "pair_id": "confirmation-joint",
        "case_block": "confirmation",
        "slice_candidate_id": "prefix_03",
        "confirmation_family_sha256": "f" * 64,
        "results": {
            "B": condition(base_scores),
            "F": condition(full_scores),
            "S": condition(slice_scores, contract=contract),
        },
    }


class ToolformerFilterConfirmationAnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.family = {
            "selected_candidate_id": "prefix_03",
            "case_count": 59,
            "alpha": 0.02,
            "epsilon": 0.025,
            "minimum_beneficial_prevalence": 0.8,
            "maximum_violation_rate": 0.1,
        }
        self.base = [0.0] * 59
        self.full = [1.0] * 59

    def test_zero_violation_upper_bound_matches_closed_form(self):
        self.assertAlmostEqual(
            one_sided_cp_upper(0, 59, alpha=0.02),
            1.0 - 0.02 ** (1.0 / 59.0),
        )

    def test_all_registered_cases_confirm_task_local_effect(self):
        row = analyze_confirmation_bundle(
            bundle(self.base, self.full, self.full),
            family=self.family,
            expected_family_sha256="f" * 64,
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "task_local_confirmation_passed")
        self.assertEqual(row["preservation_violations"], 0)
        self.assertEqual(row["beneficial_cases"], 59)
        self.assertLessEqual(row["preservation_cp_upper"], 0.1)
        self.assertGreaterEqual(row["benefit_cp_lower"], 0.8)
        self.assertTrue(row["task_local_confirmation_ready"])
        self.assertFalse(row["general_effectslice_claim_ready"])
        self.assertFalse(row["scientific_claim_ready"])

    def test_any_observed_preservation_mismatch_fails_zero_violation_rule(self):
        row = analyze_confirmation_bundle(
            bundle(self.base, self.full, [1.0] * 58 + [0.0]),
            family=self.family,
            expected_family_sha256="f" * 64,
            delta_min=0.05,
        )

        self.assertEqual(row["preservation_violations"], 1)
        self.assertEqual(row["classification"], "task_local_confirmation_failed")
        self.assertFalse(row["task_local_confirmation_ready"])

    def test_hard_constraint_failure_blocks_confirmation(self):
        row = analyze_confirmation_bundle(
            bundle(self.base, self.full, self.full, contract=False),
            family=self.family,
            expected_family_sha256="f" * 64,
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "task_local_confirmation_failed")
        self.assertFalse(row["hard_constraints_passed"])

    def test_wrong_family_digest_is_rejected(self):
        row = analyze_confirmation_bundle(
            bundle(self.base, self.full, self.full),
            family=self.family,
            expected_family_sha256="a" * 64,
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "confirmation_family_mismatch")
        self.assertFalse(row["task_local_confirmation_ready"])


if __name__ == "__main__":
    unittest.main()
