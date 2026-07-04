import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_swe_t1_issue_aligned_followup.py"


class BuildRealReuseSWEIssueAlignedFollowupTest(unittest.TestCase):
    def test_cli_builds_issue_aligned_followup_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metrics_dir = tmp_path / "metrics"
            metrics_dir.mkdir()
            write_metric(metrics_dir / "summary_phase107.json", test_passed=False, test_patch_applied=True)
            write_metric(metrics_dir / "pts_phase107.json", test_passed=False, test_patch_applied=True)
            write_metric(metrics_dir / "summary_phase110.json", test_passed=True, test_patch_applied=False)
            write_metric(metrics_dir / "pts_phase110.json", test_passed=True, test_patch_applied=False)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                "\n".join(
                    [
                        json_line("summary", "phase97_summary", 0.0, "patch_apply_failed", ""),
                        json_line("papertoskill", "phase97_papertoskill", 0.0, "patch_apply_failed", ""),
                        json_line(
                            "summary",
                            "phase107_followup",
                            0.0,
                            "test_command_failed",
                            "metrics/summary_phase107.json",
                        ),
                        json_line(
                            "papertoskill",
                            "phase107_followup",
                            0.0,
                            "test_command_failed",
                            "metrics/pts_phase107.json",
                        ),
                        json_line("summary", "phase110_followup", 1.0, "", "metrics/summary_phase110.json"),
                        json_line("papertoskill", "phase110_followup", 1.0, "", "metrics/pts_phase110.json"),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            selection = tmp_path / "main_run_selection.json"
            selection.write_text(
                json.dumps(
                    {
                        "rows": [
                            {"task_id": "SWE-T1", "condition": "summary", "run_id": "phase97_summary"},
                            {
                                "task_id": "SWE-T1",
                                "condition": "papertoskill",
                                "run_id": "phase97_papertoskill",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output_csv = tmp_path / "swe_t1_issue_aligned_followup.csv"
            output_md = tmp_path / "swe_t1_issue_aligned_followup.md"
            output_json = tmp_path / "swe_t1_issue_aligned_followup.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(tmp_path),
                    "--raw-rows",
                    str(raw_rows),
                    "--row-selection",
                    str(selection),
                    "--source-context-run-id",
                    "phase107_followup",
                    "--issue-aligned-run-id",
                    "phase110_followup",
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
                rows = {row["Condition"]: row for row in csv.DictReader(handle)}
            self.assertEqual("0.000", rows["Summary"]["Main Score"])
            self.assertEqual("0.000", rows["Summary"]["Phase107 Score"])
            self.assertEqual("No", rows["Summary"]["Phase107 Test Passed"])
            self.assertEqual("1.000", rows["Summary"]["Issue-Aligned Score"])
            self.assertEqual("Yes", rows["PaperToSkill"]["Issue-Aligned Test Passed"])
            self.assertEqual("No", rows["PaperToSkill"]["Issue-Aligned Test Patch"])
            self.assertIn("does not show a PaperToSkill advantage", output_md.read_text(encoding="utf-8"))
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("SWE-T1", payload["task_id"])
            self.assertEqual(2, len(payload["rows"]))

    def test_current_issue_aligned_followup_has_expected_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_csv = tmp_path / "swe_t1_issue_aligned_followup.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "swe_t1_issue_aligned_followup.md"),
                    "--output-json",
                    str(tmp_path / "swe_t1_issue_aligned_followup.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Condition"]: row for row in csv.DictReader(handle)}
            self.assertEqual("1.000", rows["Summary"]["Issue-Aligned Score"])
            self.assertEqual("Yes", rows["Summary"]["Issue-Aligned Test Passed"])
            self.assertEqual("1.000", rows["PaperToSkill"]["Issue-Aligned Score"])
            self.assertEqual("Yes", rows["PaperToSkill"]["Issue-Aligned Test Passed"])
            self.assertIn("no PaperToSkill advantage", rows["Summary"]["Interpretation"])


def write_metric(path: Path, test_passed: bool, test_patch_applied: bool) -> None:
    path.write_text(
        json.dumps({"test_passed": test_passed, "test_patch_applied": test_patch_applied}),
        encoding="utf-8",
    )


def json_line(condition: str, run_id: str, task_score: float, failure_reason: str, metric_path: str) -> str:
    return json.dumps(
        {
            "run_id": run_id,
            "task_id": "SWE-T1",
            "condition": condition,
            "status": "scored",
            "task_score": task_score,
            "success": task_score == 1.0,
            "failure_reason": failure_reason,
            "metric_path": metric_path,
        }
    )


if __name__ == "__main__":
    unittest.main()
