import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_paper_tables.py"


class BuildRealReusePaperTablesTest(unittest.TestCase):
    def test_cli_builds_main_result_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_csv = Path(tmp) / "main_results_plan.csv"
            output_md = Path(tmp) / "main_results_plan.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(8, len(rows))
            self.assertEqual("AIDE-T1", rows[0]["Task ID"])
            self.assertEqual("Pending", rows[0]["Summary Score"])
            self.assertEqual("Pending", rows[0]["PaperToSkill Score"])
            self.assertEqual("Ready to run", rows[0]["Status"])
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
