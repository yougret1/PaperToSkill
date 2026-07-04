import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_failure_analysis.py"


class BuildRealReuseFailureAnalysisTest(unittest.TestCase):
    def test_cli_builds_failure_boundary_table_from_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                "\n".join(
                    [
                        json_line("AIDE-T1", "summary", 0.0, False, "timeout after 60s"),
                        json_line("AIDE-T1", "papertoskill", 0.0, False, "timeout after 60s"),
                        json_line("SWE-T2", "summary", 0.0, False, "patch_apply_failed"),
                        json_line("SWE-T2", "papertoskill", 1.0, True, ""),
                        json_line("REF-T1", "summary", 1.0, True, ""),
                        json_line("REF-T1", "papertoskill", 1.0, True, ""),
                        json_line("SNAP-T1", "summary", 0.0, False, "Extra data: line 1 column 2"),
                        json_line(
                            "SNAP-T1",
                            "papertoskill",
                            0.5,
                            False,
                            "missing_required_artifacts_or_metrics",
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output_csv = tmp_path / "failure_analysis.csv"
            output_md = tmp_path / "failure_analysis.md"
            output_json = tmp_path / "failure_analysis.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(raw_rows),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(output_md),
                    "--output-json",
                    str(output_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Budget timeout", rows["AIDE-T1"]["Boundary Mode"])
            self.assertEqual("0.000; timeout", rows["AIDE-T1"]["Summary Outcome"])
            self.assertEqual("PaperToSkill-only success", rows["SWE-T2"]["Boundary Mode"])
            self.assertEqual("1.000; success", rows["SWE-T2"]["PaperToSkill Outcome"])
            self.assertEqual("Solved by both", rows["REF-T1"]["Boundary Mode"])
            self.assertEqual("Artifact completion", rows["SNAP-T1"]["Boundary Mode"])
            self.assertIn("not add new task success evidence", output_md.read_text(encoding="utf-8"))
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(8, payload["raw_row_count"])

    def test_current_failure_analysis_has_expected_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_csv = Path(tmp) / "failure_analysis.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(Path(tmp) / "failure_analysis.md"),
                    "--output-json",
                    str(Path(tmp) / "failure_analysis.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Solved by both", rows["AIDE-T1"]["Boundary Mode"])
            self.assertEqual("PaperToSkill-only success", rows["AIDE-T2"]["Boundary Mode"])
            self.assertEqual("Patch application", rows["SWE-T1"]["Boundary Mode"])
            self.assertEqual("PaperToSkill-only success", rows["SWE-T2"]["Boundary Mode"])
            self.assertEqual("Solved by both", rows["REF-T1"]["Boundary Mode"])
            self.assertEqual("Solved by both", rows["REF-T2"]["Boundary Mode"])
            self.assertEqual("Artifact completion", rows["SNAP-T1"]["Boundary Mode"])
            self.assertEqual("Artifact completion", rows["SNAP-T2"]["Boundary Mode"])


def json_line(task_id: str, condition: str, task_score: float, success: bool, failure_reason: str) -> str:
    return json.dumps(
        {
            "task_id": task_id,
            "condition": condition,
            "status": "scored",
            "task_score": task_score,
            "success": success,
            "failure_reason": failure_reason,
        }
    )


if __name__ == "__main__":
    unittest.main()
