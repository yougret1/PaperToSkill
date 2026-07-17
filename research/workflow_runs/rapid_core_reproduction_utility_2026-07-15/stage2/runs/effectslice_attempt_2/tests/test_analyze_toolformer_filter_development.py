import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_toolformer_filter_development import classify_bundle, summarize_bundles  # noqa: E402


def scored(score: float, patch: str) -> dict:
    return {
        "status": "scored",
        "terminal_reason": "submitted",
        "task_score": score,
        "candidate_patch_sha256": patch,
        "last_scorer_task_score": score,
        "last_action": "submit",
        "last_observation_status": "scored",
        "diff_present": True,
    }


class ToolformerFilterDevelopmentAnalyzerTest(unittest.TestCase):
    def test_positive_full_artifact_signal_proceeds_only_to_eligibility(self):
        row = classify_bundle(
            {
                "pair_id": "positive",
                "model_family": "DeepSeek-family",
                "model_alias": "deepseek-test",
                "results": {"B": scored(0.25, "b"), "F": scored(1.0, "f")},
            },
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "positive_development_signal")
        self.assertEqual(row["eligibility_effect"], 0.75)
        self.assertTrue(row["proceed_to_frozen_eligibility"])
        self.assertFalse(row["usable_for_scientific_claim"])

    def test_equal_scored_pair_is_full_artifact_ineligible(self):
        row = classify_bundle(
            {
                "pair_id": "equal",
                "model_family": "GPT-family",
                "model_alias": "gpt-test",
                "results": {"B": scored(1.0, "same"), "F": scored(1.0, "same")},
            },
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "full_artifact_ineligible")
        self.assertTrue(row["identical_candidate_patches"])
        self.assertFalse(row["proceed_to_frozen_eligibility"])

    def test_final_scored_test_is_normalized_without_submit(self):
        boundary = {
            "status": "failed",
            "terminal_reason": "action_budget_exhausted",
            "task_score": 0.0,
            "candidate_patch_sha256": "same",
            "last_scorer_task_score": 1.0,
            "last_action": "test",
            "last_observation_status": "scored",
            "diff_present": True,
        }
        row = classify_bundle(
            {
                "pair_id": "boundary",
                "model_family": "DeepSeek-family",
                "model_alias": "deepseek-test",
                "results": {"B": boundary, "F": scored(1.0, "same")},
            },
            delta_min=0.05,
        )

        self.assertEqual(row["classification"], "full_artifact_ineligible")
        self.assertEqual(row["score_normalization_applied"], ["B"])

    def test_provider_failure_and_harness_exclusion_are_not_model_failures(self):
        provider = classify_bundle(
            {
                "pair_id": "provider",
                "model_family": "DeepSeek-family",
                "model_alias": "deepseek-test",
                "results": {
                    "B": {"status": "error", "terminal_reason": "provider_error"},
                    "F": {"status": "error", "terminal_reason": "provider_error"},
                },
            },
            delta_min=0.05,
        )
        harness = classify_bundle(
            {
                "pair_id": "harness",
                "model_family": "GPT-family",
                "model_alias": "gpt-test",
                "results": {"B": scored(0.0, "a"), "F": scored(0.0, "b")},
            },
            delta_min=0.05,
            harness_exclusion={"reason": "known_fixture_bug", "evidence": ["test"]},
        )

        self.assertEqual(provider["classification"], "provider_failure")
        self.assertEqual(harness["classification"], "harness_failure")
        self.assertNotEqual(provider["classification"], "model_failure")

    def test_summary_stays_development_only(self):
        summary = summarize_bundles(
            [
                {
                    "pair_id": "positive",
                    "model_family": "DeepSeek-family",
                    "model_alias": "deepseek-test",
                    "results": {"B": scored(0.0, "b"), "F": scored(1.0, "f")},
                },
                {
                    "pair_id": "equal",
                    "model_family": "GPT-family",
                    "model_alias": "gpt-test",
                    "results": {"B": scored(1.0, "x"), "F": scored(1.0, "x")},
                },
            ],
            delta_min=0.05,
        )

        self.assertEqual(summary["task_disposition"], "proceed_to_frozen_eligibility")
        self.assertFalse(summary["scientific_claim_ready"])
        self.assertEqual(summary["selected_development_model_family"], "DeepSeek-family")

    def test_robustness_signal_does_not_replace_missing_primary_signal(self):
        summary = summarize_bundles(
            [
                {
                    "pair_id": "primary-provider-failure",
                    "model_family": "DeepSeek-family",
                    "model_alias": "deepseek-test",
                    "results": {
                        "B": {"status": "error", "terminal_reason": "provider_error"},
                        "F": {"status": "error", "terminal_reason": "provider_error"},
                    },
                },
                {
                    "pair_id": "robustness-positive",
                    "model_family": "GPT-family",
                    "model_alias": "gpt-test",
                    "results": {"B": scored(0.0, "b"), "F": scored(1.0, "f")},
                },
            ],
            delta_min=0.05,
        )

        self.assertEqual(
            summary["task_disposition"],
            "inconclusive_primary_no_valid_scored_pair",
        )
        self.assertIsNone(summary["selected_development_model_family"])
        self.assertEqual(summary["robustness_positive_model_families"], ["GPT-family"])
        robustness_row = next(
            row for row in summary["bundles"] if row["model_family"] == "GPT-family"
        )
        self.assertTrue(robustness_row["robustness_signal_only"])
        self.assertFalse(robustness_row["proceed_to_frozen_eligibility"])

    def test_ambiguous_v1_bundle_is_excluded_as_task_contract_failure(self):
        summary = summarize_bundles(
            [
                {
                    "pair_id": "toolformer-filter:development:deepseek:bf:001",
                    "model_family": "DeepSeek-family",
                    "model_alias": "deepseek-v4-flash",
                    "results": {"B": scored(0.0, "b"), "F": scored(0.0, "f")},
                }
            ],
            delta_min=0.05,
        )

        self.assertEqual(
            summary["bundles"][0]["classification"], "task_contract_failure"
        )
        self.assertEqual(
            summary["task_disposition"],
            "inconclusive_primary_no_valid_scored_pair",
        )


if __name__ == "__main__":
    unittest.main()
