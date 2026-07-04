import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_swe_t1_source_context_followup.py"


class BuildRealReuseSWEFollowupTest(unittest.TestCase):
    def test_cli_builds_followup_table_from_selected_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metrics_dir = tmp_path / "metrics"
            metrics_dir.mkdir()
            write_metric(metrics_dir / "summary_first.json", patch_applied=False, test_passed=False)
            write_metric(metrics_dir / "pts_first.json", patch_applied=False, test_passed=False)
            write_metric(metrics_dir / "summary_followup.json", patch_applied=True, test_passed=False)
            write_metric(metrics_dir / "pts_followup.json", patch_applied=True, test_passed=False)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                "\n".join(
                    [
                        json_line("summary", "phase97_summary", "patch_apply_failed", "metrics/summary_first.json"),
                        json_line(
                            "papertoskill",
                            "phase97_papertoskill",
                            "patch_apply_failed",
                            "metrics/pts_first.json",
                        ),
                        json_line("summary", "phase107_followup", "test_command_failed", "metrics/summary_followup.json"),
                        json_line(
                            "papertoskill",
                            "phase107_followup",
                            "test_command_failed",
                            "metrics/pts_followup.json",
                        ),
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
            output_csv = tmp_path / "swe_t1_source_context_followup.csv"
            output_md = tmp_path / "swe_t1_source_context_followup.md"
            output_json = tmp_path / "swe_t1_source_context_followup.json"

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
                    "--followup-run-id",
                    "phase107_followup",
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
            self.assertEqual("0.000", rows["Summary"]["First-pass Score"])
            self.assertEqual("No", rows["Summary"]["First-pass Patch Applied"])
            self.assertEqual("Yes", rows["Summary"]["Follow-up Patch Applied"])
            self.assertEqual("No", rows["Summary"]["Follow-up Test Passed"])
            self.assertEqual("test_command_failed", rows["PaperToSkill"]["Follow-up Failure"])
            self.assertIn("diagnostic follow-up", output_md.read_text(encoding="utf-8"))
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("SWE-T1", payload["task_id"])
            self.assertEqual(2, len(payload["rows"]))

    def test_current_followup_table_has_expected_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_csv = tmp_path / "swe_t1_source_context_followup.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "swe_t1_source_context_followup.md"),
                    "--output-json",
                    str(tmp_path / "swe_t1_source_context_followup.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Condition"]: row for row in csv.DictReader(handle)}
            self.assertEqual("0.000", rows["Summary"]["Follow-up Score"])
            self.assertEqual("Yes", rows["Summary"]["Follow-up Patch Applied"])
            self.assertEqual("No", rows["Summary"]["Follow-up Test Passed"])
            self.assertEqual("0.000", rows["PaperToSkill"]["Follow-up Score"])
            self.assertEqual("Yes", rows["PaperToSkill"]["Follow-up Patch Applied"])
            self.assertEqual("No", rows["PaperToSkill"]["Follow-up Test Passed"])


def write_metric(path: Path, patch_applied: bool, test_passed: bool) -> None:
    path.write_text(
        json.dumps({"patch_applied": patch_applied, "test_passed": test_passed}),
        encoding="utf-8",
    )


def json_line(condition: str, run_id: str, failure_reason: str, metric_path: str) -> str:
    return json.dumps(
        {
            "run_id": run_id,
            "task_id": "SWE-T1",
            "condition": condition,
            "status": "scored",
            "task_score": 0.0,
            "success": False,
            "failure_reason": failure_reason,
            "metric_path": metric_path,
        }
    )


if __name__ == "__main__":
    unittest.main()
