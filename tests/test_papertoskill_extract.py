import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "papertoskill_extract.py"


class PaperToSkillExtractTest(unittest.TestCase):
    def test_cli_generates_skill_and_source_map(self):
        source_text = """# Example Paper

## Abstract

We introduce ExampleFlow, a workflow that turns failed coding attempts into
validated reusable repair steps.

## Methods

1. Collect the failed attempt and traceback.
2. Reflect on the root cause.
3. Apply the smallest repair.

## Experiments

- Compare retry without reflection against retry with reflection.
- Measure task success and token cost.

## Limitations

- Stop when the traceback is unavailable.
"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "example.md"
            output = tmp_path / "generated"
            source.write_text(source_text, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                    "--name",
                    "example-flow",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["name"], "example-flow")

            skill = (output / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: example-flow", skill)
            self.assertIn("# Example Paper", skill)
            self.assertIn("## Workflow", skill)
            self.assertIn("Collect the failed attempt", skill)
            self.assertIn("## Validation", skill)
            self.assertIn("## Failure Cases", skill)

            source_map = json.loads((output / "references" / "source_map.json").read_text(encoding="utf-8"))
            self.assertEqual(source_map["name"], "example-flow")
            self.assertIn("Methods", source_map["source_map"]["selected_groups"]["method"])


if __name__ == "__main__":
    unittest.main()
