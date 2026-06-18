import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_aaai_package.py"
AAAI_DIR = ROOT / "paper" / "aaai"
sys.path.insert(0, str(ROOT / "scripts"))

from check_aaai_package import build_report  # noqa: E402


class CheckAAAIPackageTest(unittest.TestCase):
    def test_current_aaai_package_is_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "aaai_package_report.json"
            output_md = Path(tmp) / "aaai_package_report.md"
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
            self.assertIn("aaai_author_kit_sha256", ready_ids)
            self.assertIn("aaai_tex_declares_style", ready_ids)
            self.assertIn("aaai_log_no_unresolved_items", ready_ids)
            self.assertIn("aaai_pdf_is_fresh", ready_ids)
            self.assertTrue(output_md.exists())

    def test_unresolved_citation_in_log_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_dir = Path(tmp) / "aaai"
            shutil.copytree(AAAI_DIR, package_dir)
            log_path = package_dir / "papertoskill_aaai2027.log"
            original = log_path.read_text(encoding="utf-8", errors="ignore")
            log_path.write_text(
                original + "\nLaTeX Warning: Citation `missing2026' undefined on input line 12.\n",
                encoding="utf-8",
            )

            report = build_report(package_dir)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["aaai_log_no_unresolved_items"])


if __name__ == "__main__":
    unittest.main()
