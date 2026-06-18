import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "papertoskill_pipeline.py"


class PaperToSkillPipelineTest(unittest.TestCase):
    def test_cli_runs_note_to_skill_to_evaluation_pipeline(self):
        source_text = """Example Tool Paper

Abstract
We introduce ExampleTool, a model that teaches itself to use API calls from a handful of demonstrations.

1 Introduction
Existing systems rely on large amounts of human annotations or task-specific settings.

2 Approach
We represent each API call with a tool name, input, and result as a text sequence.
For each API, a prompt with few demonstrations samples candidate API calls.
The system executes API calls using a Python or retrieval backend and records the response.
The filter keeps calls when the result reduces future tokens loss over a threshold.
Model finetuning uses the augmented dataset and the language modeling objective.
Inference interrupts decoding, inserts the response, and continues.

3 Tools
The tools include question answering, calculator, Wikipedia search, calendar, and machine translation.

4 Experiments
We evaluate in zero-shot downstream tasks.
Baselines include GPT-J, OPT, and GPT-3.
The domains include LAMA, math, question answering, and temporal datasets.
We check perplexity for language modeling without API calls.
The analysis varies model size and parameters.

7 Limitations
The API itself may depend entirely on an external retrieval backend.
The heuristics reduce computational cost but are sample-inefficient.
The method lags behind Atlas for some question answering tasks.
Calendar API improvements cannot be attributed to the calendar tool in every setting.
We do not evaluate perplexity with API calls because marginalizing over calls is intractable.
Smaller models do not always benefit; the method depends on model size.
"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "example.txt"
            output_dir = tmp_path / "pipeline"
            source.write_text(source_text, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output-dir",
                    str(output_dir),
                    "--paper-id",
                    "example_tool",
                    "--skill-name",
                    "example-tool-paper-skill",
                    "--rubric",
                    str(ROOT / "benchmarks" / "rubric_toolformer_v0.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads(result.stdout)
            self.assertEqual("example_tool", manifest["paper_id"])
            self.assertEqual("toolformer", manifest["profile"])
            self.assertGreaterEqual(manifest["score"]["value"], 16)
            self.assertIn("not prove human semantic fidelity", manifest["evidence_boundary"])

            for output_path in manifest["outputs"].values():
                self.assertTrue(Path(output_path).exists(), output_path)

            skill = Path(manifest["outputs"]["skill"]).read_text(encoding="utf-8")
            self.assertIn("name: example-tool-paper-skill", skill)
            self.assertIn("Source anchors: lines", skill)

            note_report = json.loads(Path(manifest["outputs"]["note_report"]).read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(note_report["selected"]["methods"]), 4)


if __name__ == "__main__":
    unittest.main()
