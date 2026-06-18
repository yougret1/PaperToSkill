import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_model_ablation_prompts.py"


class BuildModelAblationPromptsTest(unittest.TestCase):
    def test_generates_model_case_prompt_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            context = tmp_path / "skill.md"
            context.write_text("# Skill\n\n## Workflow\n- Keep source-backed steps.\n", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "schema_version": "0.1",
                        "id": "model_ablation_test",
                        "user_prompt": "Use the context.",
                        "output_contract": ["Return source-backed and inferred steps."],
                        "context_cases": [
                            {
                                "id": "case_one",
                                "paper": "Synthetic",
                                "context_path": str(context),
                                "usage_focus": "unit test",
                            }
                        ],
                        "model_slots": [
                            {
                                "id": "claude_slot",
                                "model_alias": "claude-opus-4-8",
                                "provider_status": "pending",
                            },
                            {
                                "id": "gpt_slot",
                                "model_alias": "gpt-5.5",
                                "provider_status": "pending_verification",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_dir = tmp_path / "prompts"

            subprocess.run(
                [sys.executable, str(SCRIPT), "--task", str(task), "--output-dir", str(output_dir)],
                check=True,
                capture_output=True,
                text=True,
            )

            index = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(2, len(index["prompts"]))
            self.assertTrue((output_dir / "claude_slot__case_one.md").exists())
            self.assertTrue((output_dir / "gpt_slot__case_one.md").exists())
            prompt = (output_dir / "gpt_slot__case_one.md").read_text(encoding="utf-8")
            self.assertIn("gpt-5.5", prompt)
            self.assertIn("Keep source-backed steps", prompt)


if __name__ == "__main__":
    unittest.main()
