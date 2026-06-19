import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_external_evidence_closure.py"
sys.path.insert(0, str(ROOT / "scripts"))

import check_external_evidence_closure as closure  # noqa: E402


class CheckExternalEvidenceClosureTest(unittest.TestCase):
    def test_current_closure_queue_covers_goal_pending_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "closure.json"
            output_md = Path(tmp) / "closure.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending_external_evidence", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            item_ids = {item["id"] for item in report["items"]}
            self.assertIn("ai_scientist_v2_smoke_completion", item_ids)
            self.assertIn("deepseek_followup_responses", item_ids)
            self.assertIn("human_fidelity_annotation", item_ids)
            self.assertIn("provider_billing_success_per_dollar", item_ids)
            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("ready", checks["external_closure_goal_pending_items_covered"]["status"])
            self.assertTrue(output_md.exists())

    def test_complete_fixture_reports_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {
                "results/reproducibility/goal_completion_report.json": {
                    "checks": [],
                },
                "results/ai_scientist_v2_smoke/run_report.json": {
                    "overall_status": "complete",
                    "status_counts": {"ready": 5, "pending": 0, "fail": 0},
                    "attempted_models": [{"model": "claude-opus-4-8"}],
                },
                "results/ai_scientist_v2_live_run_handoff/handoff.json": {
                    "overall_status": "complete",
                    "completion_dirs": ["experiments/run"],
                    "next_commands": ["python launch_scientist_bfts.py"],
                },
                "results/deepseek_followup_handoff/handoff.json": {
                    "overall_status": "responses_present",
                    "next_commands": ["python scripts\\run_model_ablation_prompts.py"],
                },
                "results/model_ablation_prompts/v0/evaluation.json": {
                    "summary": {"scored_rows": 6, "pending_rows": 0},
                },
                "results/human_fidelity_packets/annotation_summary.json": {
                    "annotation_status": "complete",
                    "scored_rows": 24,
                    "pending_rows": 0,
                },
                "results/provider_billing_evidence/billing_summary.json": {
                    "billing_status": "complete",
                    "measured_rows": 6,
                    "pending_rows": 0,
                    "errors": [],
                },
                "results/reproducibility/aaai_package_report.json": {
                    "overall_status": "ready",
                },
                "results/reproducibility/submission_review_report.json": {
                    "overall_status": "ready",
                },
            }
            for raw_path, payload in paths.items():
                path = root / raw_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload), encoding="utf-8")

            report = closure.build_report(root)
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual(6, report["item_status_counts"]["complete"])

    def test_missing_item_requirement_fails_coverage_check(self):
        original_build_items = closure.build_items

        def broken_build_items(reports):
            items = original_build_items(reports)
            for item in items:
                if item.id == "deepseek_followup_responses":
                    item.goal_requirements = ["deepseek_followup_response_complete"]
            return items

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {
                "results/reproducibility/goal_completion_report.json": {
                    "checks": [
                        {"id": "deepseek_followup_response_complete", "status": "pending"},
                        {"id": "model_ablation_evaluation_complete", "status": "pending"},
                    ],
                },
                "results/ai_scientist_v2_smoke/run_report.json": {"overall_status": "complete"},
                "results/ai_scientist_v2_live_run_handoff/handoff.json": {"overall_status": "complete"},
                "results/deepseek_followup_handoff/handoff.json": {"overall_status": "responses_present"},
                "results/model_ablation_prompts/v0/evaluation.json": {"summary": {"scored_rows": 5, "pending_rows": 1}},
                "results/human_fidelity_packets/annotation_summary.json": {"annotation_status": "complete"},
                "results/provider_billing_evidence/billing_summary.json": {"billing_status": "complete", "errors": []},
                "results/reproducibility/aaai_package_report.json": {"overall_status": "ready"},
                "results/reproducibility/submission_review_report.json": {"overall_status": "ready"},
            }
            for raw_path, payload in paths.items():
                path = root / raw_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload), encoding="utf-8")

            try:
                closure.build_items = broken_build_items
                report = closure.build_report(root)
            finally:
                closure.build_items = original_build_items

            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", checks["external_closure_goal_pending_items_covered"]["status"])
            self.assertIn("model_ablation_evaluation_complete", checks["external_closure_goal_pending_items_covered"]["detail"])


if __name__ == "__main__":
    unittest.main()
