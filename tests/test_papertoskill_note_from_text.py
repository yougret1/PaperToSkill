import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "papertoskill_note_from_text.py"


class PaperToSkillNoteFromTextTest(unittest.TestCase):
    def test_cli_generates_source_anchored_note(self):
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
            output = tmp_path / "note.md"
            report = tmp_path / "report.json"
            source.write_text(source_text, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                    "--paper-id",
                    "example_tool",
                    "--report",
                    str(report),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["paper_id"], "example_tool")

            note = output.read_text(encoding="utf-8")
            self.assertIn("# Example Tool Paper", note)
            self.assertIn("## Methods", note)
            self.assertIn("Source anchors: lines", note)
            self.assertIn("API-call contract", note)
            self.assertIn("zero-shot", note)
            self.assertIn("perplexity", note)
            self.assertIn("model size", note)

            report_payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(report_payload["paper_id"], "example_tool")
            self.assertGreaterEqual(len(report_payload["selected"]["methods"]), 4)
            self.assertGreaterEqual(len(report_payload["selected"]["experiments"]), 3)
            self.assertGreaterEqual(len(report_payload["selected"]["limitations"]), 3)

    def test_toolformer_text_produces_auditable_scaffold(self):
        if not (ROOT / "papers" / "extracted" / "toolformer.txt").exists():
            self.skipTest("Toolformer extracted text is not available")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "toolformer_auto_note.md"
            report = Path(tmp) / "toolformer_auto_note_report.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(ROOT / "papers" / "extracted" / "toolformer.txt"),
                    "--output",
                    str(output),
                    "--paper-id",
                    "toolformer_auto",
                    "--title",
                    "Toolformer: Language Models Can Teach Themselves to Use Tools",
                    "--report",
                    str(report),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            note = output.read_text(encoding="utf-8")
            self.assertIn("## Abstract", note)
            self.assertIn("## Methods", note)
            self.assertIn("## Experiments", note)
            self.assertIn("## Limitations", note)
            self.assertIn("Source anchors: lines", note)
            self.assertIn("API-call contract", note)
            self.assertIn("zero-shot", note)
            self.assertIn("calendar API", note)

            report_payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(report_payload["paper_id"], "toolformer_auto")
            self.assertEqual(report_payload["profile"], "toolformer")
            self.assertGreaterEqual(len(report_payload["selected"]["methods"]), 5)
            self.assertGreaterEqual(len(report_payload["selected"]["experiments"]), 3)
            self.assertGreaterEqual(len(report_payload["selected"]["limitations"]), 3)

    def test_aide_profile_produces_code_search_scaffold(self):
        if not (ROOT / "papers" / "extracted" / "aide.txt").exists():
            self.skipTest("AIDE extracted text is not available")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "aide_auto_note.md"
            report = Path(tmp) / "aide_auto_note_report.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(ROOT / "papers" / "extracted" / "aide.txt"),
                    "--output",
                    str(output),
                    "--paper-id",
                    "aide_auto",
                    "--title",
                    "AIDE: AI-Driven Exploration in the Space of Code",
                    "--profile",
                    "aide",
                    "--report",
                    str(report),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            note = output.read_text(encoding="utf-8")
            self.assertIn("## Methods", note)
            self.assertIn("solution tree", note)
            self.assertIn("search policy", note)
            self.assertIn("data preview", note)
            self.assertIn("Weco-Kaggle", note)
            self.assertIn("LLM inference cost", note)
            self.assertIn("Source anchors: lines", note)

            report_payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(report_payload["paper_id"], "aide_auto")
            self.assertEqual(report_payload["profile"], "aide")
            self.assertGreaterEqual(len(report_payload["selected"]["methods"]), 5)
            self.assertGreaterEqual(len(report_payload["selected"]["experiments"]), 3)
            self.assertGreaterEqual(len(report_payload["selected"]["limitations"]), 3)


if __name__ == "__main__":
    unittest.main()
