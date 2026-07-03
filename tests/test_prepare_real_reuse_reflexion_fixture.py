import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_real_reuse_reflexion_fixture.py"


class PrepareRealReuseReflexionFixtureTest(unittest.TestCase):
    def test_prepare_ref_t1_writes_visible_assets_and_hidden_answer_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "REF-T1"
            condition_dir = tmp_path / "conditions"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "REF-T1",
                    "--dataset",
                    "hotpotqa",
                    "--config",
                    "distractor",
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(condition_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("REF-T1", manifest["task_id"])
            self.assertEqual("prepared_assets_ready_for_dry_scoring", manifest["status"])
            files = {row["slot"]: row for row in manifest["files"]}
            self.assertIn("question", files)
            self.assertIn("answer_key", files)
            self.assertEqual("scorer_only", files["answer_key"]["visibility"])
            self.assertTrue((output_dir / "task_prompt.md").exists())
            answer_key = json.loads((output_dir / "answer_key.json").read_text(encoding="utf-8"))
            self.assertEqual("yes", answer_key["answer"])
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Were Scott Derrickson and Ed Wood", prompt)
            self.assertIn("The answer key is hidden", prompt)
            self.assertTrue((condition_dir / "REF-T1_summary.md").exists())

    def test_prepare_ref_t2_writes_humaneval_retry_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "REF-T2"
            condition_dir = tmp_path / "conditions"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "REF-T2",
                    "--dataset",
                    "humaneval",
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(condition_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("REF-T2", manifest["task_id"])
            files = {row["slot"]: row for row in manifest["files"]}
            self.assertEqual("model_visible", files["failed_first_attempt"]["visibility"])
            self.assertEqual("scorer_only", files["objective_checker"]["visibility"])
            tests = json.loads((output_dir / "tests.json").read_text(encoding="utf-8"))
            self.assertEqual("HumanEval/0", tests["humaneval_task_id"])
            self.assertEqual("has_close_elements", tests["entry_point"])
            feedback = (output_dir / "environment_feedback.md").read_text(encoding="utf-8")
            self.assertIn("returned `False`", feedback)
            self.assertTrue((condition_dir / "REF-T2_summary.md").exists())


if __name__ == "__main__":
    unittest.main()
