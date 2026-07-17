import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_swe_development import classify_bundle, load_bundles, summarize_bundles  # noqa: E402


def scored_result(score: float, patch_sha256: str) -> dict:
    return {
        "status": "scored",
        "terminal_reason": "submitted",
        "submitted": True,
        "task_score": score,
        "candidate_patch_sha256": patch_sha256,
        "actions": ["search", "open", "edit", "test", "submit"],
        "observation_statuses": ["ok", "ok", "ok", "scored", "scored"],
    }


class SweDevelopmentSummaryTest(unittest.TestCase):
    def test_scored_equal_pair_is_full_artifact_ineligible(self):
        bundle = {
            "pair_id": "scored-equal",
            "model_family": "GPT-family",
            "model_alias": "gpt-test",
            "results": {
                "B": scored_result(1.0, "same-patch"),
                "F": scored_result(1.0, "same-patch"),
            },
        }

        row = classify_bundle(bundle, delta_min=0.01)

        self.assertEqual(row["classification"], "full_artifact_ineligible")
        self.assertEqual(row["eligibility_effect"], 0.0)
        self.assertTrue(row["identical_candidate_patches"])
        self.assertFalse(row["usable_for_scientific_claim"])

    def test_hidden_action_horizon_is_inconclusive_not_model_failure(self):
        exhausted = {
            "status": "failed",
            "terminal_reason": "action_budget_exhausted",
            "submitted": False,
            "task_score": 0.0,
            "candidate_patch_sha256": "empty",
            "actions": ["search", "open", None, "open"],
            "observation_statuses": ["ok", "ok", "invalid_action", "ok"],
        }
        bundle = {
            "pair_id": "deepseek-budget",
            "model_family": "DeepSeek-family",
            "model_alias": "deepseek-test",
            "action_budget_visible_to_model": False,
            "results": {"B": dict(exhausted), "F": dict(exhausted)},
        }

        row = classify_bundle(bundle, delta_min=0.01)

        self.assertEqual(row["classification"], "inconclusive_action_horizon")
        self.assertIsNone(row["eligibility_effect"])
        self.assertNotEqual(row["classification"], "model_failure")
        self.assertFalse(row["usable_for_scientific_claim"])

    def test_last_scored_test_is_normalized_when_submit_step_does_not_fit(self):
        base = {
            "status": "failed",
            "terminal_reason": "action_budget_exhausted",
            "submitted": False,
            "task_score": 0.0,
            "candidate_patch_sha256": "same-patch",
            "actions": ["open", "edit", "test"],
            "observation_statuses": ["ok", "ok", "scored"],
            "last_scorer_task_score": 1.0,
            "last_scorer_success": True,
            "diff_present": True,
        }
        bundle = {
            "pair_id": "normalized-boundary",
            "model_family": "DeepSeek-family",
            "model_alias": "deepseek-test",
            "action_budget_visible_to_model": True,
            "results": {
                "B": base,
                "F": scored_result(1.0, "same-patch"),
            },
        }

        row = classify_bundle(bundle, delta_min=0.01)

        self.assertEqual(row["classification"], "full_artifact_ineligible")
        self.assertEqual(row["eligibility_effect"], 0.0)
        self.assertEqual(row["score_normalization_applied"], ["B"])

    def test_explicit_harness_exclusion_takes_precedence(self):
        bundle = {
            "pair_id": "old-harness",
            "model_family": "GPT-family",
            "model_alias": "gpt-test",
            "results": {
                "B": scored_result(0.0, "empty"),
                "F": scored_result(0.0, "empty"),
            },
        }

        row = classify_bundle(
            bundle,
            delta_min=0.01,
            harness_exclusion={
                "reason": "pre_fix_line_endings",
                "evidence": ["tests/test_aci_workspace.py"],
            },
        )

        self.assertEqual(row["classification"], "harness_failure")
        self.assertEqual(row["classification_reason"], "pre_fix_line_endings")
        self.assertIsNone(row["eligibility_effect"])

    def test_current_run_preserves_all_development_dispositions(self):
        bundles = load_bundles(RUN_ROOT)

        summary = summarize_bundles(bundles, delta_min=0.01)

        by_pair = {row["pair_id"]: row for row in summary["bundles"]}
        self.assertEqual(summary["bundle_count"], 4)
        self.assertEqual(
            by_pair["swe-t2:dev:aci:gpt56:bf:001"]["classification"],
            "harness_failure",
        )
        self.assertEqual(
            by_pair["swe-t2:dev:aci:gpt56:bf:002"]["classification"],
            "full_artifact_ineligible",
        )
        self.assertEqual(
            by_pair["swe-t2:dev:aci:deepseek:bf:001"]["classification"],
            "inconclusive_action_horizon",
        )
        self.assertEqual(
            by_pair["swe-t2:dev:aci:deepseek:bf:002"]["classification"],
            "full_artifact_ineligible",
        )
        self.assertEqual(
            by_pair["swe-t2:dev:aci:deepseek:bf:002"]["score_normalization_applied"],
            ["B"],
        )
        self.assertEqual(summary["task_disposition"], "abstain_full_artifact_ineligible")
        self.assertFalse(summary["scientific_claim_ready"])


if __name__ == "__main__":
    unittest.main()
