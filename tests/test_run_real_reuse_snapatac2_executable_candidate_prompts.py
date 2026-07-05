import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_real_reuse_snapatac2_executable_candidate_prompts.py"
PLAN = ROOT / "results" / "real_reuse" / "snapatac2_executable_candidate_prompt_plan.json"


SCRIPT_TEMPLATE = """```python
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--task-id')
parser.add_argument('--condition')
parser.add_argument('--fragment')
parser.add_argument('--artifact-dir')
parser.add_argument('--result-json')
args = parser.parse_args()
Path(args.result_json).write_text(json.dumps({'method_steps': ['fixture generated script']}), encoding='utf-8')
```
"""


class RunSnapATAC2ExecutableCandidatePromptsTest(unittest.TestCase):
    def test_fixture_responses_generate_candidate_scripts_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture_dir = tmp_path / "fixture_responses"
            script_dir = tmp_path / "candidate_scripts"
            response_dir = tmp_path / "responses"
            report_json = tmp_path / "report.json"
            report_md = tmp_path / "report.md"
            fixture_dir.mkdir()
            plan = json.loads(PLAN.read_text(encoding="utf-8"))
            for packet in plan["packets"]:
                (fixture_dir / packet["expected_script_name"]).write_text(SCRIPT_TEMPLATE, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan-json",
                    str(PLAN),
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--script-dir",
                    str(script_dir),
                    "--response-dir",
                    str(response_dir),
                    "--output-json",
                    str(report_json),
                    "--output-md",
                    str(report_md),
                    "--run-id",
                    "unit_fixture_generation",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual(4, report["selected_packet_count"])
            self.assertEqual(4, report["recorded_row_count"])
            self.assertEqual("not_appended_to_main_raw_rows", report["raw_rows_policy"])
            self.assertIn("does not execute candidates", report["evidence_boundary"])
            for packet in plan["packets"]:
                script_path = script_dir / packet["expected_script_name"]
                self.assertTrue(script_path.exists())
                script_text = script_path.read_text(encoding="utf-8")
                self.assertIn("argparse.ArgumentParser", script_text)
                self.assertNotIn("```", script_text)
            self.assertTrue(report_md.exists())

    def test_missing_env_is_recorded_as_pending_not_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report_json = tmp_path / "report.json"
            env = {}
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan-json",
                    str(PLAN),
                    "--script-dir",
                    str(tmp_path / "candidate_scripts"),
                    "--response-dir",
                    str(tmp_path / "responses"),
                    "--output-json",
                    str(report_json),
                    "--output-md",
                    str(tmp_path / "report.md"),
                    "--base-url-env",
                    "PAPERTOSKILL_TEST_MISSING_BASE_URL",
                    "--api-key-env",
                    "PAPERTOSKILL_TEST_MISSING_API_KEY",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertEqual(4, report["selected_packet_count"])
            self.assertEqual(4, report["recorded_row_count"])
            self.assertEqual({"skipped": 4}, report["status_counts"])
            for row in report["rows"]:
                self.assertEqual("missing_base_url_or_api_key_env", row["call_status"]["selection_reason"])

    def test_can_filter_and_skip_existing_candidate_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script_dir = tmp_path / "candidate_scripts"
            response_dir = tmp_path / "responses"
            script_dir.mkdir()
            existing = script_dir / "SNAP-T1_summary.py"
            existing.write_text("print('already here')\n", encoding="utf-8")
            report_json = tmp_path / "report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan-json",
                    str(PLAN),
                    "--task",
                    "SNAP-T1",
                    "--condition",
                    "summary",
                    "--skip-existing",
                    "--script-dir",
                    str(script_dir),
                    "--response-dir",
                    str(response_dir),
                    "--output-json",
                    str(report_json),
                    "--output-md",
                    str(tmp_path / "report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual(1, report["selected_packet_count"])
            self.assertEqual(1, report["recorded_row_count"])
            self.assertEqual({"cached": 1}, report["status_counts"])
            self.assertEqual("SNAP-T1", report["rows"][0]["task_id"])
            self.assertEqual("summary", report["rows"][0]["condition"])


if __name__ == "__main__":
    unittest.main()
