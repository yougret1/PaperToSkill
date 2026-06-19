import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_openai_compatible_direct_probe as probe  # noqa: E402


class OpenAICompatibleDirectProbeTest(unittest.TestCase):
    def setUp(self):
        self.original_request_json = probe.request_json

    def tearDown(self):
        probe.request_json = self.original_request_json

    def args(self, tmp_path, **overrides):
        values = {
            "model": "claude-opus-4-8",
            "model_aliases": None,
            "base_url_env": "MISSING_BASE",
            "auth_env": "MISSING_KEY",
            "base_url": "https://example.test/v1",
            "api_key": "test-key",
            "timeout_seconds": 1,
            "max_tokens": 128,
            "system_message": "system",
            "prompt": "prompt",
            "response_output": tmp_path / "response.md",
        }
        values.update(overrides)
        return Namespace(**values)

    def test_direct_probe_saves_contract_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            def fake_request_json(url, api_key, body, timeout_seconds):
                self.assertEqual("https://example.test/v1/chat/completions", url)
                self.assertEqual("test-key", api_key)
                self.assertEqual("claude-opus-4-8", body["model"])
                self.assertEqual(128, body["max_tokens"])
                return 200, {
                    "choices": [
                        {
                            "message": {
                                "content": "PAPERTOSKILL_SMOKE_OK from ai-scientist-v2 for paper-to-skill."
                            }
                        }
                    ]
                }

            probe.request_json = fake_request_json
            report = probe.run(self.args(tmp_path))

            self.assertEqual("complete", report["overall_status"])
            self.assertTrue((tmp_path / "response.md").exists())
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["direct_probe_response_saved"])
            self.assertEqual("ready", statuses["direct_probe_marker_papertoskill_smoke_ok"])
            self.assertEqual("ready", statuses["direct_probe_marker_ai_scientist_v2"])
            self.assertEqual("ready", statuses["direct_probe_marker_paper_to_skill"])
            self.assertEqual(0, probe.exit_code(report, strict=True, require_complete=True))

    def test_direct_probe_error_is_redacted_and_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_secret = "sk-" + "a" * 24

            def fake_request_json(url, api_key, body, timeout_seconds):
                raise RuntimeError(f"bad key {fake_secret}")

            response_path = tmp_path / "response.md"
            response_path.write_text("stale\n", encoding="utf-8")
            probe.request_json = fake_request_json
            report = probe.run(self.args(tmp_path, response_output=response_path))

            encoded = json.dumps(report)
            self.assertEqual("blocked_by_provider_or_model_availability", report["overall_status"])
            self.assertFalse(response_path.exists())
            self.assertIn("sk-REDACTED", encoded)
            self.assertNotIn(fake_secret, encoded)
            self.assertEqual(0, probe.exit_code(report, strict=True, require_complete=False))
            self.assertEqual(1, probe.exit_code(report, strict=True, require_complete=True))

    def test_direct_probe_missing_configuration_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report = probe.run(self.args(tmp_path, base_url=None, api_key=None))

            self.assertEqual("pending_configuration", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("pending", statuses["direct_probe_configuration"])
            self.assertEqual([], report["attempted_models"])

    def test_direct_probe_tries_aliases_until_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            calls = []

            def fake_request_json(url, api_key, body, timeout_seconds):
                calls.append(body["model"])
                if body["model"] == "claude-opus-4-8":
                    raise RuntimeError("capacity failure")
                return 200, {
                    "choices": [
                        {
                            "message": {
                                "content": "PAPERTOSKILL_SMOKE_OK from ai-scientist-v2 for paper-to-skill."
                            }
                        }
                    ]
                }

            probe.request_json = fake_request_json
            report = probe.run(
                self.args(
                    tmp_path,
                    model_aliases=["claude-opus-4-8", "claude-opus-4-7"],
                )
            )

            self.assertEqual("complete", report["overall_status"])
            self.assertEqual(["claude-opus-4-8", "claude-opus-4-7"], calls)
            self.assertEqual(["blocked", "success"], [item["status"] for item in report["attempted_models"]])


if __name__ == "__main__":
    unittest.main()
