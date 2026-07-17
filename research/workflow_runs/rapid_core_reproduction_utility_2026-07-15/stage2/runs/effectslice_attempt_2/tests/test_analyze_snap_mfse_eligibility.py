import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_snap_mfse_eligibility import (  # noqa: E402
    classify_eligibility_bundle,
    one_sided_cp_lower,
    summarize_eligibility_bundles,
)


def condition(
    case_scores,
    *,
    status="scored",
    terminal_reason="submitted",
    last_action="submit",
    observation_status="scored",
):
    return {
        "status": status,
        "terminal_reason": terminal_reason,
        "last_action": last_action,
        "last_observation_status": observation_status,
        "diff_present": True,
        "final_metric": {
            "task_score": sum(case_scores) / len(case_scores),
            "case_scores": list(case_scores),
            "contract_passed": True,
            "matrix_free_guard_passed": True,
        },
    }


def bundle(base_scores, full_scores, *, harness="effectslice-snap-mfse-aci.v2"):
    return {
        "pair_id": "eligibility-pair",
        "model_family": "DeepSeek-family",
        "case_block": "eligibility",
        "harness_protocol_version": harness,
        "results": {
            "B": condition(base_scores),
            "F": condition(full_scores),
        },
    }


class SnapMFSEEligibilityAnalyzerTest(unittest.TestCase):
    def test_exact_lower_bound_for_zero_and_all_successes(self):
        self.assertEqual(one_sided_cp_lower(0, 21, alpha=0.01), 0.0)
        self.assertAlmostEqual(
            one_sided_cp_lower(21, 21, alpha=0.01),
            0.01 ** (1.0 / 21.0),
        )

    def test_all_21_beneficial_cases_pass_the_frozen_gate(self):
        row = classify_eligibility_bundle(
            bundle([0.0] * 21, [1.0] * 21),
            delta_min=0.05,
            alpha=0.01,
            minimum_prevalence=0.8,
            minimum_pairs=21,
        )

        self.assertEqual(row["classification"], "eligible_full_artifact")
        self.assertEqual(row["beneficial_cases"], 21)
        self.assertGreaterEqual(row["one_sided_cp_lower"], 0.8)
        self.assertTrue(row["proceed_to_discovery"])
        self.assertFalse(row["usable_for_scientific_claim"])

    def test_one_nonbeneficial_case_fails_the_frozen_gate(self):
        row = classify_eligibility_bundle(
            bundle([0.0] * 21, [1.0] * 20 + [0.0]),
            delta_min=0.05,
            alpha=0.01,
            minimum_prevalence=0.8,
            minimum_pairs=21,
        )

        self.assertEqual(row["classification"], "ineligible_full_artifact")
        self.assertEqual(row["beneficial_cases"], 20)
        self.assertLess(row["one_sided_cp_lower"], 0.8)
        self.assertFalse(row["proceed_to_discovery"])

    def test_v1_final_edit_without_terminal_score_is_excluded(self):
        candidate = bundle(
            [0.0] * 21,
            [1.0] * 21,
            harness="effectslice-snap-mfse-aci.v1",
        )
        candidate["results"]["B"] = condition(
            [0.0] * 21,
            status="failed",
            terminal_reason="action_budget_exhausted",
            last_action="edit",
            observation_status="ok",
        )

        row = classify_eligibility_bundle(
            candidate,
            delta_min=0.05,
            alpha=0.01,
            minimum_prevalence=0.8,
            minimum_pairs=21,
        )

        self.assertEqual(row["classification"], "unscored_final_state")
        self.assertFalse(row["proceed_to_discovery"])

    def test_summary_uses_valid_bundle_and_retains_exclusion(self):
        excluded = bundle(
            [0.0] * 21,
            [1.0] * 21,
            harness="effectslice-snap-mfse-aci.v1",
        )
        excluded["pair_id"] = "excluded"
        excluded["results"]["B"] = condition(
            [0.0] * 21,
            status="failed",
            terminal_reason="action_budget_exhausted",
            last_action="edit",
            observation_status="ok",
        )
        accepted = bundle([0.0] * 21, [1.0] * 21)
        accepted["pair_id"] = "accepted"

        summary = summarize_eligibility_bundles(
            [excluded, accepted],
            delta_min=0.05,
            alpha=0.01,
            minimum_prevalence=0.8,
            minimum_pairs=21,
        )

        self.assertEqual(summary["task_disposition"], "proceed_to_discovery")
        self.assertEqual(summary["selected_eligibility_pair_id"], "accepted")
        self.assertEqual(summary["classification_counts"]["unscored_final_state"], 1)
        self.assertFalse(summary["scientific_claim_ready"])


if __name__ == "__main__":
    unittest.main()
