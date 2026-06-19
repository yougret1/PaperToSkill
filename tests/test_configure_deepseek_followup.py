import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_deepseek_followup.py"
sys.path.insert(0, str(ROOT / "scripts"))

import configure_deepseek_followup as configure  # noqa: E402


BASE_TASK = {
    "model_slots": [
        {
            "id": "deepseek_followup_slot",
            "model_alias": "deepseek-to-be-filled",
            "auth_env": "DEEPSEEK_API_KEY",
            "base_url_env": "DEEPSEEK_BASE_URL",
            "provider_status": "placeholder_for_user_followup",
            "run_notes": ["existing note"],
        }
    ]
}


class ConfigureDeepSeekFollowupTest(unittest.TestCase):
    def test_configures_slot_without_secret_material(self):
        task = configure.configure_slot(
            copy.deepcopy(BASE_TASK),
            model_alias="deepseek-reasoner",
            auth_env="PAPERTOSKILL_DEEPSEEK_API_KEY",
            base_url_env="PAPERTOSKILL_DEEPSEEK_BASE_URL",
            provider_status="configured_pending_live_run",
        )

        slot = task["model_slots"][0]
        self.assertEqual("deepseek-reasoner", slot["model_alias"])
        self.assertEqual("PAPERTOSKILL_DEEPSEEK_API_KEY", slot["auth_env"])
        self.assertEqual("PAPERTOSKILL_DEEPSEEK_BASE_URL", slot["base_url_env"])
        self.assertIn("Configured by scripts/configure_deepseek_followup.py", " ".join(slot["run_notes"]))

    def test_rejects_raw_api_key_like_auth_env(self):
        with self.assertRaises(ValueError):
            configure.configure_slot(
                copy.deepcopy(BASE_TASK),
                model_alias="deepseek-reasoner",
                auth_env="sk-" + "1" * 24,
                base_url_env="DEEPSEEK_BASE_URL",
                provider_status="configured_pending_live_run",
            )

    def test_cli_updates_task_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_path = Path(tmp) / "task.json"
            task_path.write_text(json.dumps(copy.deepcopy(BASE_TASK)), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    str(task_path),
                    "--model-alias",
                    "deepseek-chat",
                    "--auth-env",
                    "DEEPSEEK_API_KEY",
                    "--base-url-env",
                    "DEEPSEEK_BASE_URL",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            task = json.loads(task_path.read_text(encoding="utf-8"))
            self.assertEqual("deepseek-chat", task["model_slots"][0]["model_alias"])


if __name__ == "__main__":
    unittest.main()
