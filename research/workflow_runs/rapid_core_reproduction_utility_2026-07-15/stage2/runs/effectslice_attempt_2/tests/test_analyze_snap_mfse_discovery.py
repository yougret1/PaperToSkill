import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_snap_mfse_discovery import summarize_discovery_bundles  # noqa: E402


def condition(case_scores, *, contract=True, guard=True):
    return {
        "status": "scored",
        "terminal_reason": "submitted",
        "last_action": "submit",
        "last_observation_status": "scored",
        "final_metric": {
            "task_score": sum(case_scores) / len(case_scores),
            "case_scores": list(case_scores),
            "contract_passed": contract,
            "matrix_free_guard_passed": guard,
        },
    }


def baseline_bundle(base_scores, full_scores):
    return {
        "pair_id": "discovery-baseline",
        "case_block": "discovery",
        "conditions": ["B", "F"],
        "results": {
            "B": condition(base_scores),
            "F": condition(full_scores),
        },
    }


def slice_bundle(candidate_id, full_scores, slice_scores, *, contract=True, guard=True):
    return {
        "pair_id": f"discovery-{candidate_id}",
        "case_block": "discovery",
        "conditions": ["F", "S"],
        "slice_candidate_id": candidate_id,
        "results": {
            "F": condition(full_scores),
            "S": condition(slice_scores, contract=contract, guard=guard),
        },
    }


class SnapMFSEDiscoveryAnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(
            (
                RUN_ROOT
                / "artifacts"
                / "snap_mfse"
                / "slices"
                / "slice_registry.json"
            ).read_text(encoding="utf-8")
        )
        self.full = [1.0] * 16
        self.base = [0.0] * 16

    def summarize(self, bundles):
        return summarize_discovery_bundles(
            bundles,
            registry=self.registry,
            epsilon=0.025,
            delta_delete=0.05,
        )

    def test_single_case_loss_exceeds_equivalence_band(self):
        summary = self.summarize(
            [
                baseline_bundle(self.base, self.full),
                slice_bundle("prefix_01", self.full, [1.0] * 15 + [0.0]),
            ]
        )

        row = summary["candidate_rows"][0]
        self.assertEqual(row["classification"], "candidate_inferior")
        self.assertEqual(row["effect_gap_F_minus_S"], 0.0625)
        self.assertEqual(summary["task_disposition"], "continue_search")

    def test_shortest_equivalent_prefix_is_locked_when_baseline_degrades(self):
        summary = self.summarize(
            [
                baseline_bundle(self.base, self.full),
                slice_bundle("prefix_01", self.full, self.full),
            ]
        )

        self.assertEqual(summary["selected_candidate_id"], "prefix_01")
        self.assertEqual(summary["task_disposition"], "candidate_locked_for_confirmation")
        self.assertTrue(summary["deletion_audit_complete"])
        self.assertEqual(summary["deletion_rows"][0]["neighbor_id"], "B")
        self.assertTrue(summary["deletion_rows"][0]["deletion_failed"])
        self.assertFalse(summary["scientific_claim_ready"])

    def test_second_prefix_requires_baseline_and_first_prefix_to_fail(self):
        summary = self.summarize(
            [
                baseline_bundle(self.base, self.full),
                slice_bundle("prefix_01", self.full, [1.0] * 15 + [0.0]),
                slice_bundle("prefix_02", self.full, self.full),
            ]
        )

        self.assertEqual(summary["selected_candidate_id"], "prefix_02")
        self.assertTrue(summary["deletion_audit_complete"])
        self.assertEqual(
            [row["neighbor_id"] for row in summary["deletion_rows"]],
            ["B", "prefix_01"],
        )

    def test_hard_constraint_failure_prevents_equivalence(self):
        summary = self.summarize(
            [
                baseline_bundle(self.base, self.full),
                slice_bundle("prefix_01", self.full, self.full, guard=False),
            ]
        )

        self.assertEqual(
            summary["candidate_rows"][0]["classification"],
            "candidate_hard_constraint_failure",
        )
        self.assertEqual(summary["task_disposition"], "continue_search")

    def test_all_registered_candidates_inferior_causes_abstention(self):
        bundles = [baseline_bundle(self.base, self.full)]
        for row in self.registry["candidates"]:
            bundles.append(
                slice_bundle(row["candidate_id"], self.full, [1.0] * 15 + [0.0])
            )

        summary = self.summarize(bundles)

        self.assertEqual(summary["task_disposition"], "abstain_no_equivalent_slice")
        self.assertIsNone(summary["selected_candidate_id"])


if __name__ == "__main__":
    unittest.main()
