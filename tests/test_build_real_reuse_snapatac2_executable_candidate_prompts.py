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
                self.assertIn("cross-platform Python", prompt)
                self.assertIn("do not import POSIX-only modules such as `resource`", prompt)
                self.assertIn("Do not import `resource`", prompt)
                self.assertIn("Do not use network access", prompt)
                self.assertIn(packet["expected_script_name"], prompt)
                for artifact in packet["required_artifacts"]:
                    self.assertIn(artifact, prompt)
                self.assertNotIn("success_threshold", prompt)
                self.assertNotIn("scorer_thresholds.json\n{", prompt)

    def test_compact_cli_builds_shorter_prompt_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            full_dir = tmp_path / "full_prompts"
            compact_dir = tmp_path / "compact_prompts"
            full_json = tmp_path / "full_plan.json"
            compact_json = tmp_path / "compact_plan.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(full_dir),
                    "--output-json",
                    str(full_json),
                    "--output-md",
                    str(tmp_path / "full_plan.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "compact",
                    "--output-dir",
                    str(compact_dir),
                    "--output-json",
                    str(compact_json),
                    "--output-md",
                    str(tmp_path / "compact_plan.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            full_plan = json.loads(full_json.read_text(encoding="utf-8"))
            compact_plan = json.loads(compact_json.read_text(encoding="utf-8"))
            self.assertEqual("full", full_plan["prompt_mode"])
            self.assertEqual("compact", compact_plan["prompt_mode"])
            self.assertEqual(4, len(compact_plan["packets"]))

            full_total = sum((full_dir / Path(row["prompt_path"]).name).stat().st_size for row in full_plan["packets"])
            compact_total = sum(
                (compact_dir / Path(row["prompt_path"]).name).stat().st_size for row in compact_plan["packets"]
            )
            self.assertLess(compact_total, full_total * 0.7)

            for packet in compact_plan["packets"]:
                prompt = (compact_dir / Path(packet["prompt_path"]).name).read_text(encoding="utf-8")
                prompt_lower = prompt.lower()
                self.assertIn("Compact Condition Context", prompt)
                self.assertIn("Compact Model-Visible Locked Assets", prompt)
                self.assertIn("--task-id", prompt)
                self.assertIn("--condition", prompt)
                self.assertIn("--fragment", prompt)
                self.assertIn("--artifact-dir", prompt)
                self.assertIn("--result-json", prompt)
                self.assertIn("do not import `resource`", prompt_lower)
                self.assertIn("No network", prompt)
                self.assertIn("main_run_selection.json", prompt)
                for artifact in packet["required_artifacts"]:
                    self.assertIn(artifact, prompt)
                self.assertNotIn("scorer_thresholds.json", prompt)
                self.assertNotIn("reference_labels_or_proxy.json", prompt)
                self.assertNotIn("success_threshold", prompt)


if __name__ == "__main__":
    unittest.main()
