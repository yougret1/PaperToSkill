import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_model_ablation_prompts.py"
EVALUATOR = ROOT / "scripts" / "evaluate_model_ablation_responses.py"
sys.path.insert(0, str(ROOT / "scripts"))

from run_model_ablation_prompts import model_ids_from_response, select_model_alias  # noqa: E402


class ModelAblationExecutionTest(unittest.TestCase):
    def test_model_ids_accepts_object_and_string_model_lists(self):
        self.assertEqual(
            ["claude-opus-4-8", "gpt-5"],
            model_ids_from_response(
                {"models": ["gpt-5", {"id": "claude-opus-4-8"}]}
            ),
        )

    def test_gpt_slot_falls_back_to_available_gpt_family_model(self):
        alias, reason = select_model_alias(
            {"id": "gpt_5_5_or_gpt_family", "model_alias": "gpt-5.5"},
            ["claude-opus-4-8", "gpt-5", "gpt-4.1"],
        )
        self.assertEqual("gpt-5", alias)
        self.assertEqual("fallback_from_gpt-5.5", reason)

    def test_evaluator_scores_saved_response_and_marks_missing_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            response = tmp_path / "response.md"
            response.write_text(
                """Sufficient context.

Files and commands:
- Use the local tool.

Step-by-step plan:
1. Run the plan.

Source-backed steps:
- Keep the method.

Inferred adaptations:
- Mock external APIs.

Validation checks and stop conditions:
- Stop on failed tests.

Failure branch:
- Log the failed branch.
""",
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "m1",
                                "model_alias": "model-one",
                                "case_id": "case_one",
                                "expected_response_path": str(response),
                            },
                            {
                                "model_id": "m2",
                                "model_alias": "model-two",
                                "case_id": "case_two",
                                "expected_response_path": str(tmp_path / "missing.md"),
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "eval.json"
            output_md = tmp_path / "eval.md"

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
            self.assertEqual(1, report["summary"]["scored_rows"])
            self.assertEqual(1, report["summary"]["pending_rows"])
            self.assertEqual(1.0, report["results"][0]["normalized_score"])
            self.assertEqual("pending", report["results"][1]["status"])

    def test_runner_skips_missing_environment_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "auth_env": "MISSING_KEY",
                                "base_url_env": "MISSING_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "response.md"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "run.json"
            output_md = tmp_path / "run.md"

            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--task",
                    str(task),
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
            self.assertEqual("pending", report["overall_status"])
            self.assertEqual("skipped", report["results"][0]["status"])


if __name__ == "__main__":
    unittest.main()
