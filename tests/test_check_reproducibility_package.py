import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_reproducibility_package.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_reproducibility_package import required_file_checks  # noqa: E402


class CheckReproducibilityPackageTest(unittest.TestCase):
    def test_missing_required_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "present.md").write_text("ok", encoding="utf-8")
            checks = required_file_checks(root, {"present": "present.md", "missing": "missing.md"})

        statuses = {check.id: check.status for check in checks}
        self.assertEqual("ready", statuses["present"])
        self.assertEqual("fail", statuses["missing"])

    def test_current_package_is_ready_with_pending_external_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "package_report.json"
            output_md = Path(tmp) / "package_report.md"
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
            self.assertEqual("ready_with_pending_external_evidence", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            self.assertGreaterEqual(report["status_counts"]["ready"], 164)
            pending_ids = {check["id"] for check in report["checks"] if check["status"] == "pending"}
            self.assertIn("human_fidelity_annotation_complete", pending_ids)
            self.assertIn("provider_billing_evidence_complete", pending_ids)
            self.assertIn("ai_scientist_v2_llm_smoke_complete", pending_ids)
            self.assertIn("ai_scientist_v2_llm_smoke_response", pending_ids)
            self.assertIn("ai_scientist_v2_llm_smoke_contract_ready", pending_ids)
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("human_fidelity_guide", ready_ids)
            self.assertIn("human_fidelity_annotation_handoff_ready", ready_ids)
            self.assertIn("provider_billing_summary_valid", ready_ids)
            self.assertIn("provider_billing_evidence_handoff_ready", ready_ids)
            self.assertIn("ai_scientist_smoke_runner", ready_ids)
            self.assertIn("ai_scientist_smoke_report_json", ready_ids)
            self.assertIn("ai_scientist_smoke_report_md", ready_ids)
            self.assertIn("phase50_ai_scientist_v2_smoke_timeout_recheck_run_log", ready_ids)
            self.assertIn("ai_scientist_live_run_handoff_checker", ready_ids)
            self.assertIn("ai_scientist_live_run_handoff_json", ready_ids)
            self.assertIn("ai_scientist_live_run_handoff_md", ready_ids)
            self.assertIn("ai_scientist_v2_live_run_handoff_report_ready", ready_ids)
            self.assertIn("ai_scientist_v2_live_run_handoff_core_checks_ready", ready_ids)
            self.assertIn("ai_scientist_v2_live_run_completion", pending_ids)
            self.assertIn("deepseek_followup_checker", ready_ids)
            self.assertIn("deepseek_followup_handoff_json", ready_ids)
            self.assertIn("deepseek_followup_handoff_md", ready_ids)
            self.assertIn("deepseek_followup_handoff_report_ready", ready_ids)
            self.assertIn("deepseek_followup_handoff_core_checks_ready", ready_ids)
            self.assertIn("ai_scientist_v2_smoke_cli_status_summary", ready_ids)
            smoke_cli = {
                check["id"]: check
                for check in report["checks"]
                if check["id"] == "ai_scientist_v2_smoke_cli_status_summary"
            }["ai_scientist_v2_smoke_cli_status_summary"]
            self.assertIn("alias_fallback=True", smoke_cli["detail"])
            self.assertIn("ai_scientist_v2_live_responses", ready_ids)
            self.assertIn("reflexion_live_responses", ready_ids)
            self.assertIn("aide_live_responses", ready_ids)
            self.assertIn("toolformer_live_responses", ready_ids)
            self.assertIn("ai_scientist_v2_live_transfer_responses_scored", ready_ids)
            self.assertIn("reflexion_live_transfer_responses_scored", ready_ids)
            self.assertIn("aide_live_transfer_responses_scored", ready_ids)
            self.assertIn("toolformer_live_transfer_responses_scored", ready_ids)
            self.assertIn("ai_scientist_v2_live_run_report_complete", ready_ids)
            self.assertIn("reflexion_live_run_report_complete", ready_ids)
            self.assertIn("aide_live_run_report_complete", ready_ids)
            self.assertIn("toolformer_live_run_report_complete", ready_ids)
            self.assertIn("live_transfer_all_responses_scored", ready_ids)
            self.assertIn("live_transfer_evaluation_valid", ready_ids)
            self.assertIn("aide_auto_context_baseline_order", ready_ids)
            self.assertIn("aide_auto_transfer_ablation_order", ready_ids)
            self.assertIn("aide_auto_source_span_support", ready_ids)
            self.assertIn("aaai_package_report_ready", ready_ids)
            self.assertIn("aaai_package_core_checks_ready", ready_ids)
            self.assertIn("paper_table_report_ready", ready_ids)
            self.assertIn("paper_table_core_checks_ready", ready_ids)
            self.assertIn("paper_claim_report_ready", ready_ids)
            self.assertIn("paper_claim_core_checks_ready", ready_ids)
            self.assertIn("submission_review_report_ready", ready_ids)
            self.assertIn("submission_review_core_checks_ready", ready_ids)
            self.assertIn("goal_completion_report_ready", ready_ids)
            self.assertIn("goal_completion_core_checks_ready", ready_ids)
            self.assertIn("external_closure_checker", ready_ids)
            self.assertIn("external_closure_report_json", ready_ids)
            self.assertIn("external_closure_report_md", ready_ids)
            self.assertIn("phase51_external_evidence_closure_queue_run_log", ready_ids)
            self.assertIn("external_evidence_closure_report_ready", ready_ids)
            self.assertIn("external_evidence_closure_core_checks_ready", ready_ids)
            self.assertIn("external_evidence_closure_queue_items_ready", ready_ids)
            self.assertIn("usage_example_report_ready", ready_ids)
            self.assertIn("usage_example_core_checks_ready", ready_ids)
            self.assertIn("model_response_output_token_proxy", ready_ids)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
