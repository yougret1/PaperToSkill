import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_live_transfer_prompts.py"
EVALUATOR = ROOT / "scripts" / "evaluate_live_transfer_responses.py"


class LiveTransferExecutionTest(unittest.TestCase):
    def write_task_and_index(self, tmp_path: Path, response_path: Path | None = None):
        prompt = tmp_path / "prompt.md"
        prompt.write_text("Prompt with source-backed and inferred adaptation requirements.", encoding="utf-8")
        task = tmp_path / "task.json"
        task.write_text(
            json.dumps(
                {
                    "id": "live_transfer_test",
                    "output_contract": [
                        "State whether the context is sufficient.",
                        "List required local tools.",
                        "Give a step-by-step run plan.",
                    ],
                }
            ),
            encoding="utf-8",
        )
        index = tmp_path / "index.json"
        index.write_text(
            json.dumps(
                {
                    "task": "live_transfer_test",
                    "task_path": str(task),
                    "prompts": [
                        {
                            "harness_id": "codex_skill",
                            "variant_id": "full_skill",
                            "prompt_path": str(prompt),
                            "expected_response_path": str(response_path or (tmp_path / "response.md")),
                        },
                        {
                            "harness_id": "claude_project_prompt",
                            "variant_id": "generic_summary",
                            "prompt_path": str(prompt),
                            "expected_response_path": str(tmp_path / "missing.md"),
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        return index

    def test_runner_skips_when_env_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            index = self.write_task_and_index(tmp_path)
            output_json = tmp_path / "run.json"
            output_md = tmp_path / "run.md"

            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--base-url-env",
                    "MISSING_LIVE_BASE",
                    "--api-key-env",
                    "MISSING_LIVE_KEY",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertEqual(2, report["status_counts"]["skipped"])
            self.assertEqual("missing_base_url_or_api_key", report["results"][0]["selection_reason"])

    def test_evaluator_scores_saved_response_and_marks_missing_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            response = tmp_path / "response.md"
            response.write_text(
                """The context is sufficient.

Required local tools:
- Python.

Step-by-step run plan:
1. Execute the plan.

Source-backed steps:
- Keep the method.

Inferred adaptation:
- Mock unavailable services.

Validation checks and stop conditions:
- Stop on failed checks.

Failure branch:
- Log unavailable tools as a limitation.
""",
                encoding="utf-8",
            )
            index = self.write_task_and_index(tmp_path, response)
            output_json = tmp_path / "evaluation.json"
            output_md = tmp_path / "evaluation.md"

            subprocess.run(
                [
                    sys.executable,
                    str(EVALUATOR),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(2, report["summary"]["total_rows"])
            self.assertEqual(1, report["summary"]["scored_rows"])
            self.assertEqual(1, report["summary"]["pending_rows"])
            self.assertEqual(1.0, report["results"][0]["normalized_score"])
            self.assertEqual("pending", report["results"][1]["status"])


if __name__ == "__main__":
    unittest.main()
