import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_usage_examples.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_usage_examples import build_report  # noqa: E402


class CheckUsageExamplesTest(unittest.TestCase):
    def test_current_usage_examples_are_ready(self):
        report = build_report(ROOT, run_examples=True)

        self.assertEqual("ready", report["overall_status"])
        self.assertEqual(0, report["status_counts"]["fail"])
        ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
        self.assertIn("codex_toolformer_prompt", ready_ids)
        self.assertIn("usage_model_ablation_prompt_grid", ready_ids)
        self.assertIn("usage_model_ablation_response_slots", ready_ids)
        self.assertIn("usage_auto_note_example_rubric_score", ready_ids)
        sample = report["auto_note_example_sample"]
        self.assertEqual("aide", sample["note_report"]["profile"])
        self.assertEqual(20, sample["rubric"]["score"])

    def test_cli_can_skip_running_example_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "usage_example_report.json"
            output_md = Path(tmp) / "usage_example_report.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--skip-run",
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("ready", report["overall_status"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("usage_model_ablation_model_slots", ready_ids)
            self.assertIsNone(report["auto_note_example_sample"])
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
