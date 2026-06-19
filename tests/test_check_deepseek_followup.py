import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_deepseek_followup.py"
sys.path.insert(0, str(ROOT / "scripts"))

from check_deepseek_followup import build_report  # noqa: E402


class CheckDeepSeekFollowupTest(unittest.TestCase):
    def test_current_handoff_is_pending_user_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "handoff.json"
            output_md = Path(tmp) / "handoff.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending_user_configuration", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["deepseek_followup_slot_present"])
            self.assertEqual("pending", statuses["deepseek_followup_alias_configured"])
            self.assertEqual("pending", statuses["deepseek_followup_responses_saved"])
            self.assertTrue(output_md.exists())

    def test_configured_slot_is_ready_to_run_until_responses_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt_one = tmp_path / "p1.md"
            prompt_two = tmp_path / "p2.md"
            prompt_one.write_text("prompt one", encoding="utf-8")
            prompt_two.write_text("prompt two", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "context_cases": [{"id": "c1"}, {"id": "c2"}],
                        "model_slots": [
                            {
                                "id": "deepseek_followup_slot",
                                "model_alias": "deepseek-reasoner",
                                "auth_env": "DEEPSEEK_API_KEY",
                                "base_url_env": "DEEPSEEK_BASE_URL",
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
                        "prompts": [
                            {
                                "model_id": "deepseek_followup_slot",
                                "case_id": "c1",
                                "prompt_path": str(prompt_one),
                                "expected_response_path": str(tmp_path / "r1.md"),
                            },
                            {
                                "model_id": "deepseek_followup_slot",
                                "case_id": "c2",
                                "prompt_path": str(prompt_two),
                                "expected_response_path": str(tmp_path / "r2.md"),
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = build_report(tmp_path, task, index)
            self.assertEqual("ready_to_run", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["deepseek_followup_alias_configured"])
            self.assertEqual("pending", statuses["deepseek_followup_responses_saved"])


if __name__ == "__main__":
    unittest.main()
