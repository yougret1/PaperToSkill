import sys
import json
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from analyze_confirmation_v2 import (  # noqa: E402
    analyze_replicates,
    load_registered_replicates,
    one_sided_cp_lower,
    write_task_summary,
)


def family(task_key="snap_mfse"):
    return {
        "schema_version": "effectslice-confirmation-v2-family.v1",
        "task_key": task_key,
        "selected_candidate_id": "prefix_03",
        "case_block": "confirmation_v2",
        "case_count": 64,
        "statistical_unit": "independent_agent_run",
        "replicate_count": 18,
        "replicate_schedule": [
            {
                "replicate_id": f"r{index:03d}",
                "condition_order": ["B", "F", "S"],
            }
            for index in range(1, 19)
        ],
        "run_success_threshold": 0.95,
        "maximum_score_gap": 0.05,
        "alpha": 0.02,
        "minimum_prevalence": 0.8,
        "private_score_policy": "final_only",
        "model_alias": "deepseek-v4-flash",
        "workspace_tree_sha256": "w" * 64,
    }


def condition(score, *, task_key="snap_mfse", exposed=False, score_count=1):
    metric = {
        "task_score": score,
        "case_scores": [1.0] * round(64 * score)
        + [0.0] * (64 - round(64 * score)),
        "contract_passed": True,
    }
    if task_key == "snap_mfse":
        metric["matrix_free_guard_passed"] = True
    return {
        "status": "scored",
        "terminal_reason": "submitted",
        "submitted": True,
        "task_score": score,
        "success": score >= 0.95,
        "private_score_policy": "final_only",
        "private_score_count": score_count,
        "private_feedback_exposed": exposed,
        "scorer_metrics": [metric],
        "turns": [
            {
                "observation_status": "scored",
                "observation_message": "final submission accepted",
                "provider_model_id": "deepseek-v4-flash",
                "provider_response_id": "response-1",
                "provider_created": 1784290000,
            }
        ],
    }


def replicate(index, *, task_key="snap_mfse", slice_score=1.0):
    return {
        "replicate_id": f"r{index:03d}",
        "execution_status": "completed",
        "pair_id": f"{task_key}:confirmation-v2:r{index:03d}",
        "case_block": "confirmation_v2",
        "selected_candidate_id": "prefix_03",
        "confirmation_family_sha256": "f" * 64,
        "model_alias": "deepseek-v4-flash",
        "manifest_private_score_policy": "final_only",
        "workspace_tree_sha256": "w" * 64,
        "condition_execution_order": ["B", "F", "S"],
        "results": {
            "B": condition(0.0, task_key=task_key),
            "F": condition(1.0, task_key=task_key),
            "S": condition(slice_score, task_key=task_key),
        },
    }


class ConfirmationV2AnalyzerTest(unittest.TestCase):
    def test_all_eighteen_independent_replicates_admit_task_local_slice(self):
        summary = analyze_replicates(
            family(),
            [replicate(index) for index in range(1, 19)],
            expected_family_sha256="f" * 64,
        )

        self.assertEqual(summary["statistical_unit"], "independent_agent_run")
        self.assertEqual(summary["condition_run_unit"], "independent_provider_conversation")
        self.assertEqual(summary["analysis_unit"], "matched_BFS_replicate")
        self.assertEqual(summary["provider_conversations"], 54)
        self.assertEqual(summary["provider_model_ids"], ["deepseek-v4-flash"])
        self.assertEqual(summary["provider_response_id_count"], 1)
        self.assertEqual(summary["provider_turns_with_identity"], 54)
        self.assertEqual(summary["confirmation_family_sha256"], "f" * 64)
        self.assertEqual(summary["replicate_denominator"], 18)
        self.assertEqual(summary["clustered_hidden_checks_per_run"], 64)
        self.assertTrue(summary["schedule_complete"])
        self.assertTrue(summary["integrity_passed"])
        self.assertTrue(summary["task_local_admission_ready"])
        for hypothesis in summary["hypotheses"].values():
            self.assertEqual(hypothesis["successes"], 18)
            self.assertEqual(hypothesis["total"], 18)
            self.assertGreater(hypothesis["one_sided_cp_lower"], 0.8)

    def test_one_failed_replicate_counts_against_fixed_denominator(self):
        rows = [replicate(index) for index in range(1, 18)]
        rows.append(
            {
                "replicate_id": "r018",
                "execution_status": "failed",
                "error_type": "ProviderFailure",
                "error_message": "retryable_provider_error_exhausted",
            }
        )

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertTrue(summary["schedule_complete"])
        self.assertFalse(summary["task_local_admission_ready"])
        for hypothesis in summary["hypotheses"].values():
            self.assertEqual(hypothesis["successes"], 17)
            self.assertEqual(hypothesis["total"], 18)
            self.assertLess(hypothesis["one_sided_cp_lower"], 0.8)

    def test_private_feedback_exposure_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["results"]["S"] = condition(1.0, exposed=True)

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertFalse(summary["task_local_admission_ready"])
        self.assertIn(
            "private_feedback_exposed",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_multiple_private_scores_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["results"]["F"] = condition(1.0, score_count=2)

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertFalse(summary["task_local_admission_ready"])
        self.assertIn(
            "private_score_count_not_final_only",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_wrong_registered_pair_id_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["pair_id"] = "snap_mfse:confirmation-v2:r999"

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertIn(
            "pair_id_mismatch",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_missing_provider_identity_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["results"]["S"]["turns"][0]["provider_response_id"] = ""

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertIn(
            "missing_provider_response_id",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_workspace_digest_mismatch_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["workspace_tree_sha256"] = "x" * 64

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertIn(
            "workspace_tree_mismatch",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_manifest_model_alias_mismatch_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["model_alias"] = "another-model"

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertIn(
            "model_alias_mismatch",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_manifest_private_score_policy_mismatch_invalidates_integrity(self):
        rows = [replicate(index) for index in range(1, 19)]
        rows[0]["manifest_private_score_policy"] = "interactive"

        summary = analyze_replicates(
            family(),
            rows,
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["integrity_passed"])
        self.assertIn(
            "manifest_private_score_policy_mismatch",
            summary["replicates"][0]["integrity_violations"],
        )

    def test_missing_registered_replicates_is_incomplete_not_a_smaller_sample(self):
        summary = analyze_replicates(
            family(),
            [replicate(index) for index in range(1, 18)],
            expected_family_sha256="f" * 64,
        )

        self.assertFalse(summary["schedule_complete"])
        self.assertEqual(summary["replicate_denominator"], 18)
        self.assertFalse(summary["task_local_admission_ready"])
        self.assertEqual(summary["missing_replicate_ids"], ["r018"])

    def test_case_level_pseudoreplication_is_never_used(self):
        self.assertGreater(one_sided_cp_lower(18, 18, alpha=0.02), 0.8)
        self.assertLess(one_sided_cp_lower(17, 18, alpha=0.02), 0.8)

        summary = analyze_replicates(
            family(),
            [replicate(index) for index in range(1, 19)],
            expected_family_sha256="f" * 64,
        )

        self.assertEqual(
            summary["hypotheses"]["H_slice_benefit_run_level"]["total"],
            18,
        )
        self.assertNotEqual(
            summary["hypotheses"]["H_slice_benefit_run_level"]["total"],
            18 * 64,
        )

    def test_loader_uses_progress_and_confirmation_v2_root_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            family_path = root / "family.json"
            family_payload = family()
            family_path.write_text(json.dumps(family_payload), encoding="utf-8")
            import hashlib

            family_sha256 = hashlib.sha256(family_path.read_bytes()).hexdigest()
            output_root = root / "confirmation_v2"
            bundle_root = output_root / "snap_mfse" / "r001"
            bundle_root.mkdir(parents=True)
            (bundle_root / "pair_manifest.json").write_text(
                json.dumps(
                    {
                        "pair_id": "snap_mfse:confirmation-v2:r001",
                        "case_block": "confirmation_v2",
                        "slice_candidate_id": "prefix_03",
                        "confirmation_family_sha256": family_sha256,
                        "model_alias": "deepseek-v4-flash",
                        "private_score_policy": "final_only",
                        "workspace_state": {"sha256": "w" * 64},
                        "condition_execution_order": ["B", "F", "S"],
                        "results": {"B": {}, "F": {}, "S": {}},
                    }
                ),
                encoding="utf-8",
            )
            for label, score in (("B", 0.0), ("F", 1.0), ("S", 1.0)):
                condition_root = bundle_root / label
                condition_root.mkdir()
                (condition_root / "run_result.json").write_text(
                    json.dumps(condition(score)),
                    encoding="utf-8",
                )
            progress_path = output_root / "confirmation_v2_progress.json"
            progress_path.write_text(
                json.dumps(
                    {
                        "schema_version": "effectslice-confirmation-v2-progress.v1",
                        "counts": {"completed": 1, "failed": 0, "preserved": 0},
                        "records": [
                            {
                                "task_key": "snap_mfse",
                                "replicate_id": "r001",
                                "status": "completed",
                                "output_dir": bundle_root.as_posix(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            contaminated = root / "old_confirmation" / "r999"
            contaminated.mkdir(parents=True)
            (contaminated / "pair_manifest.json").write_text(
                json.dumps({"case_block": "confirmation"}),
                encoding="utf-8",
            )

            loaded_family, loaded_sha256, rows = load_registered_replicates(
                family_path=family_path,
                output_root=output_root,
                progress_path=progress_path,
            )

        self.assertEqual(loaded_family, family_payload)
        self.assertEqual(loaded_sha256, family_sha256)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["replicate_id"], "r001")
        self.assertEqual(set(rows[0]["results"]), {"B", "F", "S"})
        self.assertEqual(rows[0]["case_block"], "confirmation_v2")

    def test_writer_records_run_level_denominator_in_json_and_markdown(self):
        summary = analyze_replicates(
            family(),
            [replicate(index) for index in range(1, 19)],
            expected_family_sha256="f" * 64,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output_json = Path(temporary) / "summary.json"
            output_md = Path(temporary) / "summary.md"

            write_task_summary(summary, output_json=output_json, output_md=output_md)

            saved = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")

        self.assertEqual(saved["replicate_denominator"], 18)
        self.assertIn("18 independent API agent runs", markdown)
        self.assertIn("64 clustered hidden checks per run", markdown)
        self.assertNotIn("1152 independent", markdown)


if __name__ == "__main__":
    unittest.main()
