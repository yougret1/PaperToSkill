import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_goal_completion.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_goal_completion import build_report, required_file_checks  # noqa: E402


class CheckGoalCompletionTest(unittest.TestCase):
    def test_missing_required_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "memory").mkdir()
            (root / "memory" / "long_term_memory.md").write_text("ok", encoding="utf-8")
            checks = required_file_checks(root)

        statuses = {check.id: check.status for check in checks}
        self.assertEqual("ready", statuses["memory_long_term"])
        self.assertEqual("fail", statuses["memory_short_term"])

    def test_current_goal_is_not_complete_but_has_no_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "goal_completion_report.json"
            output_md = Path(tmp) / "goal_completion_report.md"
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
            self.assertEqual("not_complete_pending_external_evidence", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("pending", statuses["active_goal_complete"])
            self.assertEqual("ready", statuses["aaai_package_gate_ready"])
            self.assertEqual("ready", statuses["usage_example_gate_ready"])
            self.assertEqual("ready", statuses["claude_opus_4_8_ablation_attempted"])
            self.assertEqual("ready", statuses["claude_opus_4_8_ablation_complete"])
            self.assertEqual("ready", statuses["gpt_family_ablation_complete"])
            self.assertEqual("ready", statuses["model_response_output_token_proxy_ready"])
            self.assertEqual("ready", statuses["provider_billing_evidence_handoff_ready"])
            self.assertEqual("pending", statuses["provider_billing_evidence_complete"])
            self.assertEqual("ready", statuses["submission_review_handoff_ready"])
            self.assertEqual("pending", statuses["aaai_final_submission_ready"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_llm_smoke_attempted"])
            self.assertEqual("pending", statuses["ai_scientist_v2_live_llm_smoke_complete"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_run_handoff_ready"])
            self.assertEqual("pending", statuses["ai_scientist_v2_live_llm_run_complete"])
            self.assertEqual("ready", statuses["ai_scientist_v2_live_transfer_responses_complete"])
            self.assertEqual("ready", statuses["reflexion_live_transfer_responses_complete"])
            self.assertEqual("ready", statuses["aide_live_transfer_responses_complete"])
            self.assertEqual("ready", statuses["toolformer_live_transfer_responses_complete"])
            self.assertEqual("ready", statuses["deepseek_followup_process_ready"])
            self.assertEqual("ready", statuses["deepseek_followup_handoff_ready"])
            self.assertEqual("pending", statuses["deepseek_followup_response_complete"])
            self.assertEqual("ready", statuses["live_cross_harness_responses_complete"])
            self.assertEqual("pending", statuses["human_fidelity_annotation_complete"])
            self.assertEqual("ready", statuses["external_evidence_closure_queue_ready"])
            self.assertTrue(output_md.exists())

    def test_current_report_build_has_expected_boundaries(self):
        report = build_report(ROOT)
        checks = {check["id"]: check for check in report["checks"]}
        self.assertIn("provider_billing_evidence_complete", checks)
        self.assertEqual("pending", checks["provider_billing_evidence_complete"]["status"])
        self.assertIn("provider_billing_evidence_handoff_ready", checks)
        self.assertEqual("ready", checks["provider_billing_evidence_handoff_ready"]["status"])
        self.assertIn("submission_review_handoff_ready", checks)
        self.assertEqual("ready", checks["submission_review_handoff_ready"]["status"])
        self.assertEqual("pending", checks["aaai_final_submission_ready"]["status"])
        self.assertIn("live_cross_harness_responses_complete", checks)
        self.assertEqual("ready", checks["live_cross_harness_responses_complete"]["status"])
        self.assertIn("ai_scientist_v2_live_transfer_responses_complete", checks)
        self.assertEqual("ready", checks["ai_scientist_v2_live_transfer_responses_complete"]["status"])
        self.assertIn("ai_scientist_v2_live_llm_smoke_attempted", checks)
        self.assertEqual("ready", checks["ai_scientist_v2_live_llm_smoke_attempted"]["status"])
        self.assertIn("ai_scientist_v2_live_llm_smoke_complete", checks)
        self.assertEqual("pending", checks["ai_scientist_v2_live_llm_smoke_complete"]["status"])
        self.assertIn("ai_scientist_v2_live_run_handoff_ready", checks)
        self.assertEqual("ready", checks["ai_scientist_v2_live_run_handoff_ready"]["status"])
        self.assertIn("ai_scientist_v2_live_llm_run_complete", checks)
        self.assertEqual("pending", checks["ai_scientist_v2_live_llm_run_complete"]["status"])
        self.assertIn("reflexion_live_transfer_responses_complete", checks)
        self.assertEqual("ready", checks["reflexion_live_transfer_responses_complete"]["status"])
        self.assertIn("aide_live_transfer_responses_complete", checks)
        self.assertEqual("ready", checks["aide_live_transfer_responses_complete"]["status"])
        self.assertIn("toolformer_live_transfer_responses_complete", checks)
        self.assertEqual("ready", checks["toolformer_live_transfer_responses_complete"]["status"])
        self.assertIn("external_evidence_closure_queue_ready", checks)
        self.assertEqual("ready", checks["external_evidence_closure_queue_ready"]["status"])


if __name__ == "__main__":
    unittest.main()
