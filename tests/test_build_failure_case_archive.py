import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_failure_case_archive.py"
CONFIG = ROOT / "benchmarks" / "failure_case_archive_v0.json"


class BuildFailureCaseArchiveTest(unittest.TestCase):
    def test_builds_archive_from_paper_and_project_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "failure_cases"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--config",
                    str(CONFIG),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            archive = json.loads((output_dir / "failure_case_archive.json").read_text(encoding="utf-8"))
            self.assertEqual(20, archive["total_cases"])
            self.assertEqual(14, archive["scope_counts"]["paper"])
            self.assertEqual(6, archive["scope_counts"]["project"])
            self.assertIn("external_dependency", archive["category_counts"])
            self.assertIn("aide_candidate_truncation", {case["id"] for case in archive["cases"]})

            with (output_dir / "failure_case_archive.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(20, len(rows))
            self.assertTrue(any(row["paper"] == "Reflexion" for row in rows))
            self.assertTrue((output_dir / "failure_case_archive.md").exists())


if __name__ == "__main__":
    unittest.main()
