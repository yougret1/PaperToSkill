import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_snapatac2_executable_candidate_prompts.py"


class BuildSnapATAC2ExecutableCandidatePromptsTest(unittest.TestCase):
    def test_cli_builds_prompt_packets_without_hidden_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "prompts"
            output_json = tmp_path / "plan.json"
            output_md = tmp_path / "plan.md"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            plan = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(4, len(plan["packets"]))
            self.assertEqual("scripts/run_real_reuse_snapatac2_executable_candidate.py", plan["runner"])
            self.assertIn("gpt-5.5", plan["model_default"])
            self.assertTrue(output_md.exists())

            for packet in plan["packets"]:
                prompt_path = ROOT / packet["prompt_path"]
                self.assertTrue(prompt_path.exists())
                prompt = prompt_path.read_text(encoding="utf-8")
                self.assertIn("--task-id", prompt)
                self.assertIn("--artifact-dir", prompt)
                self.assertIn("--result-json", prompt)
                self.assertIn(packet["expected_script_name"], prompt)
                for artifact in packet["required_artifacts"]:
                    self.assertIn(artifact, prompt)
                self.assertNotIn("success_threshold", prompt)
                self.assertNotIn("scorer_thresholds.json\n{", prompt)


if __name__ == "__main__":
    unittest.main()
