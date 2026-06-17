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
            self.assertGreaterEqual(report["status_counts"]["ready"], 105)
            pending_ids = {check["id"] for check in report["checks"] if check["status"] == "pending"}
            self.assertIn("human_fidelity_annotation_complete", pending_ids)
            self.assertIn("ai_scientist_v2_live_responses", pending_ids)
            self.assertIn("toolformer_live_responses", pending_ids)
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("aide_auto_context_baseline_order", ready_ids)
            self.assertIn("aide_auto_transfer_ablation_order", ready_ids)
            self.assertIn("aide_auto_source_span_support", ready_ids)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
