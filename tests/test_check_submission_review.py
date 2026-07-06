import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_submission_review.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_submission_review import build_report  # noqa: E402


TEMP_REPORT_FILES = [
    "research/review_report.md",
    "research/rebuttal_bank.md",
    "research/submission_checklist.md",
    "results/live_transfer_prompts/evaluation.json",
    "results/model_ablation_prompts/v0/evaluation.json",
    "results/real_reuse/llm_ablation_summary.json",
    "results/human_fidelity_packets/annotation_summary.json",
    "results/token_accounting/token_accounting_summary.json",
    "results/ai_scientist_v2_smoke/run_report.json",
    "results/ai_scientist_v2_live_run_handoff/handoff.json",
    "results/reproducibility/goal_completion_report.json",
    "results/reproducibility/package_report.json",
    "results/reproducibility/aaai_package_report.json",
    "results/reproducibility/paper_table_report.json",
    "results/reproducibility/usage_example_report.json",
    "results/external_evidence_closure/closure.json",
    "results/external_evidence_packets/packets.json",
    "results/aaai_submission_decision/decision.json",
]


def copy_temp_report_files(tmp_root: Path) -> None:
    for relative in TEMP_REPORT_FILES:
        source = ROOT / relative
        target = tmp_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


class CheckSubmissionReviewTest(unittest.TestCase):
    def test_current_submission_review_handoff_is_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "submission_review_report.json"
            output_md = Path(tmp) / "submission_review_report.md"
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
            self.assertEqual("ready", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("submission_review_live_transfer_current", ready_ids)
            self.assertIn("submission_review_model_ablation_current", ready_ids)
            self.assertIn("submission_review_real_reuse_llm_ablation_current", ready_ids)
            self.assertIn("submission_review_human_fidelity_current", ready_ids)
            self.assertIn("submission_review_token_accounting_current", ready_ids)
            self.assertIn("submission_review_ai_scientist_smoke_current", ready_ids)
            self.assertIn("submission_review_ai_scientist_live_run_current", ready_ids)
            self.assertIn("submission_review_local_gate_counts_current", ready_ids)
            self.assertIn("submission_review_external_evidence_pending_current", ready_ids)
            self.assertTrue(output_md.exists())

    def test_stale_live_transfer_wording_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copy_temp_report_files(tmp_root)

            review = tmp_root / "research" / "review_report.md"
            review.write_text(
                review.read_text(encoding="utf-8")
                + "\n\nLive cross-harness execution | Pending | endpoint still returns HTTP 503.\n",
                encoding="utf-8",
            )

            report = build_report(tmp_root)
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["submission_review_no_stale_http_503_live_transfer_pending"])
            self.assertEqual("fail", statuses["submission_review_no_stale_live_transfer_pending"])

    def test_current_direct_probe_http_503_wording_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copy_temp_report_files(tmp_root)

            review = tmp_root / "research" / "review_report.md"
            review.write_text(
                review.read_text(encoding="utf-8")
                + "\n\nDirect endpoint probe returned HTTP 503 No available accounts.\n",
                encoding="utf-8",
            )

            report = build_report(tmp_root)
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["submission_review_no_stale_http_503_live_transfer_pending"])

    def test_stale_handoff_counts_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copy_temp_report_files(tmp_root)

            for relative in [
                "research/review_report.md",
                "research/rebuttal_bank.md",
                "research/submission_checklist.md",
            ]:
                path = tmp_root / relative
                text = path.read_text(encoding="utf-8")
                text = text.replace("483 ready", "459 ready")
                text = text.replace("343 ready", "316 ready")
                path.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["submission_review_goal_package_counts_current"])
            self.assertEqual("fail", statuses["submission_review_local_gate_counts_current"])

    def test_stale_real_reuse_llm_ablation_text_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copy_temp_report_files(tmp_root)

            for relative in [
                "research/review_report.md",
                "research/rebuttal_bank.md",
                "research/submission_checklist.md",
            ]:
                path = tmp_root / relative
                text = path.read_text(encoding="utf-8")
                text = text.replace("12/18", "18/18")
                path.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["submission_review_real_reuse_llm_ablation_current"])

    def test_stale_external_evidence_pending_text_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copy_temp_report_files(tmp_root)

            for relative in [
                "research/review_report.md",
                "research/rebuttal_bank.md",
                "research/submission_checklist.md",
            ]:
                path = tmp_root / relative
                text = path.read_text(encoding="utf-8")
                text = text.replace("pending_external_evidence", "ready_external_handoff")
                text = text.replace("two pending-external-evidence items", "two local handoff items")
                text = text.replace("2 pending external-evidence items", "2 local handoff items")
                path.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["submission_review_external_evidence_pending_current"])


if __name__ == "__main__":
    unittest.main()
