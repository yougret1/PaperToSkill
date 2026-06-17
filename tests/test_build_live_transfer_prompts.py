import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_live_transfer_prompts.py"


class BuildLiveTransferPromptsTest(unittest.TestCase):
    def test_prompt_builder_drops_transfer_notes_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            context = tmp_path / "skill.md"
            context.write_text(
                """# Skill

## Workflow
- Do the work.

## Transfer Notes
- Keep this only in the full variant.
""",
                encoding="utf-8",
            )
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "live_transfer_test",
                        "user_prompt": "Plan the task.",
                        "output_contract": ["Return a plan."],
                        "context_variants": [
                            {"id": "full", "path": str(context)},
                            {"id": "no_transfer", "path": str(context), "drop_sections": ["Transfer Notes"]},
                        ],
                        "target_harnesses": [
                            {"id": "codex", "instructions": "Act like Codex."}
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

            full_prompt = (output_dir / "codex__full.md").read_text(encoding="utf-8")
            no_transfer_prompt = (output_dir / "codex__no_transfer.md").read_text(encoding="utf-8")
            self.assertIn("Keep this only in the full variant", full_prompt)
            self.assertNotIn("Keep this only in the full variant", no_transfer_prompt)
            self.assertTrue((output_dir / "index.json").exists())


if __name__ == "__main__":
    unittest.main()
